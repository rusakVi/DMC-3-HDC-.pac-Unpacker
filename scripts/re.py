#Pac Repacker
#Coded by James

import re
import sys, os
from struct import pack
import time

time_start = time.time()
gotta_go_deep = 0

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

#creates a header before texture
def texHeader(bin_str):
	res1 = bin_str[12:14]
	res2 = bin_str[16:18]
	bin_str = ("00000000".decode("hex"))*4 + res2 + res1 + ("00000000".decode("hex"))*3 + "40000000".decode("hex") + ("00000000".decode("hex"))*9 + ("0000803b".decode("hex")) + ("0000003c".decode("hex")) + ("00000000".decode("hex"))*5 + pack("<I", len(bin_str)) + "08000000".decode("hex") + "00000000".decode("hex") + bin_str
	return bin_str

#get the files from the index
def getFiles(index_file, folder):
	line = index_file.readline().strip()
	files = []
	while line != "":
		#if there's a sub PTX archive, repack it first
		#then add a ptx file to the files array
		#if line[:4] == "PNST":
		#	line = index_file.readline().strip()
		if line[-3:] == "vid":
			IPUM(line[:-4], folder)
			files.append("%s.ipum" % line[:-4])
		elif line[-6:] == "folder":
			PTX(line[:-7], folder)
			files.append("%s.ptx" % line[:-7])
		elif line != "PNST":
			#print "%s" % line
			files.append(line)
		line = index_file.readline().strip()
	return files  #this value is an array of all the filenames

#Another version of getFiles, for PTX usage
def getFilesPTX(index_file):
	line = index_file.readline().strip()
	files = []
	while line != "":
		#print "\t%s" % line
		files.append(line)
		line = index_file.readline().strip()
	return files

def IPUM(file, folder):
	try:
		index_file = open("%s\\%s\\%s.index" % (folder, file, file), "r")
	except:
		print "Error Reading %s.index from IPUM folder %s" % (file, file)
	
	files = getFilesPTX(index_file)
	num_files = len(files)
	body = ""
	outfile = open("%s\\%s.ipum" % (folder, file), "wb")

	for i in range(num_files):
		bin_open = open("%s\\%s\\%s" % (folder, file, files[i]), "rb")
		bin_str = bin_open.read()
		body += ("frmj" + pack("<I", len(bin_str)) + bin_str)
	
	res1 = bin_str[12:14]
	res2 = bin_str[16:18]
	header = ("ipum" + "00000100".decode("hex") + res1 + res2 + pack("<I", num_files))
	
	outfile.write(header+body)

	return 0

#repacks a PTX archive
def PTX(file, folder):
	time_1 = time.time()
	print "\nRepacking PTX Archive: %s" % file
	try:
		index_file = open("%s\\%s\\%s.index" % (folder, file, file), "r")
	except:
		print "Error Reading %s.index from PTX folder %s" % (file, file)
	
	files = getFilesPTX(index_file)
	num_files = len(files)
	header = pack("<I", num_files)
	body = ""
	outfile = open("%s\\%s.ptx" % (folder, file), "wb")

	for i in range(num_files):
		bin_open = open("%s\\%s\\%s" % (folder, file, files[i]), "rb")
		bin_str = bin_open.read()
		bin_str = texHeader(bin_str) 	
		while len(bin_str)%2048:
			bin_str += "00".decode("hex")
		header += pack("<I", len(bin_str)/1024/2)
		body += bin_str

	header += ("00000000".decode("hex"))*(511-num_files)  #trailer #cushion
	outfile.write(header+body)

	print "\n	//Finished in %.4f sec\n" % (time.time() - time_1)
	return 0

def PTX2(file, folder):
	time_1 = time.time()
	print "\nRepacking PTX Archive: %s" % file
	try:
		index_file = open("%s\\%s.index" % (folder, file), "r")
	except:
		print "Error Reading %s.index from PTX folder %s" % (file, file)
	
	files = getFilesPTX(index_file)
	num_files = len(files)
	header = pack("<I", num_files)
	body = ""
	outfile = open("%s.ptx" % (file), "wb")

	for i in range(num_files):
		bin_open = open("%s\\%s" % (folder, files[i]), "rb")
		bin_str = bin_open.read()
		bin_str = texHeader(bin_str) 	
		while len(bin_str)%2048:
			bin_str += "00".decode("hex")
		header += pack("<I", len(bin_str)/1024/2)
		body += bin_str

	header += ("00000000".decode("hex"))*(511-num_files)  #trailer #cushion
	outfile.write(header+body)

	print "\n	//Finished in %.4f sec\n" % (time.time() - time_1)
	return 0

#make the body of the pac file
def MakeBody(files, folder):
	index_file = open("%s\\%s.index" % (folder, folder), "r")
	line = index_file.readline().strip()
	if line [:4] == "PNST":
		header = "PNST"
	else:
		header = "PAC" + "00".decode("hex")  #default
	body = ""
	num_files = len(files)
	pointers = [0]	#starting position
	#print files
	for i in range(num_files):
		file_open = open("%s\\%s" % (folder, files[i]), "rb")
		file_str = file_open.read()
		if "DDS |" in file_str[:5]:
			file_str = texHeader(file_str) 
			body += file_str
		else:
			body += file_str
		pointers.append(len(body))
	del pointers[-1]	#delete file size marker
	
	header_len = (num_files * 4) + 8
	
	while header_len%16:  #if header isn't divisible by 16, make it
		header_len += 4
	
	for i in range((header_len-8)/4):
		try:
			pointers[i] = pointers[i] + header_len   #correct the pointers
		except IndexError:
			pointers.append(0)
	
	#odd rule
	if pointers[-1] == 0 and pointers[-2] == 0 and pointers[-3] == 0:
		pointers[-3] = pointers[0]
	
	#another odd rule, size can't be 20
	if len(pointers) == 42:
		pointers.append(0)
		pointers.append(0)
		pointers.append(pointers[0])
		pointers.append(0)
		num_files += 2
	
	for i in range(len(pointers)):
		pointers[i] = pointers[i] + ((len(pointers)*4)-(header_len-8)) if pointers[i] else 0#correct the pointers
	
	header += pack("<I", num_files)
	for point in pointers:
		header += pack("<I", point)
	return header+body
	
#traversing subfolders
def walkdir(files, dirname):
	for root, dirs, files2 in os.walk(dirname):
		files.sort(key=natural_keys)
		path = os.path.abspath(root)
		for filename in files:
			filename = os.path.basename(filename)
			if ".pac" in filename[-4:] and os.path.exists("%s\\%s" % (path, filename[:-4])):
				folder = filename[:-4]
				pac_file = filename
				repack(path, folder, pac_file)

#repacking
def repack(path, folder, pac_file):
	time_3 = time.time()
	try:
		os.chdir(path)

	except:
		print "nope"
		return -1
	cwd = os.getcwd()

	#if can't open, exit
	#print "Opening: %s.index" % folder
	try:
		index_file = open("%s\\%s.index" % (folder, folder), "r")
	except:
		print "\nError Opening %s.index" % folder
		return -1
	
	#if can't read, exit
	#print "\nReading: %s.index\n" % folder
	try:
		files = getFiles(index_file, folder)
	except:
		print "\nError Reading %s.index" % folder
		return -1

	if gotta_go_deep == 1:
		num_files = len(files)
		for i in range(num_files):
			if ".pac" in files[i]:
				walkdir(files, folder)
		
	os.chdir(path)
	dr = os.getcwd()

	#contents
	if len(files) != 0:
		#contents
		pac = MakeBody(files, folder)

		#if can't open output, exit
		#print "\nOpening: %s" % pac_file
		try:
			pac_open = open(pac_file, "wb")
		except:
			print "\nError Opening %s" % pac_file
			return -1

		#if can't write output, exit
		print "\nWriting: %s" % pac_file
		try:
			pac_open.write(pac)
		except:
			print "\nError Writing %s" % pac_file
			return -1
	#print "\nRepacked in %.4f sec\n" % (time.time() - time_3)
	return 0
	
def main():
	#greetings
	print "\n=================================\nDevil May Cry 3 \nPac Repacker\n1.8\nCoded by James aka Jamesuminator updated by Che\n=================================\n---------------------------------\n"
	global gotta_go_deep
	
	if len(sys.argv) < 2:
		for root, dirs, files in os.walk("."):
			files.sort(key=natural_keys)
			path = os.path.abspath(".")
			for filename in files:
				filename = os.path.basename(filename)
				if ".pac" in filename[-4:] and os.path.exists("%s\\%s" % (path, filename[:-4])):
					os.chdir(path)
					folder = filename[:-4]
					cwd = os.getcwd()
					pac_file = filename
					index_file = open("%s\\%s.index" % (folder, folder), "r")
					files = getFiles(index_file, folder)
					time_2 = time.time()
					gotta_go_deep = 1
					walkdir(files, folder)
					gotta_go_deep = 0
					#print "\n//Traversed directory in %.4f sec\n" % (time.time() - time_2)
					repack(path, folder, pac_file)
					print "\n//Repacked in %.4f sec\n" % (time.time() - time_2)
					
	elif len(sys.argv) == 3:
		if sys.argv[2] != "all":
			break_while = False
			for root, dirs, files in os.walk("."):
				files.sort(key=natural_keys)
				path = os.path.abspath(".")
				for filename in files:
					filename = os.path.basename(filename)
					while filename[:-4] != sys.argv[1] and break_while != True:
						break
					else:
						break_while = True
						if ".pac" in filename[-4:] and os.path.exists("%s\\%s" % (path, filename[:-4])):
							folder = filename[:-4]
							os.chdir(path)
							cwd = os.getcwd()
							pac_file = filename
							index_file = open("%s\\%s.index" % (folder, folder), "r")
							files = getFiles(index_file, folder)
							time_2 = time.time()
							gotta_go_deep = 1
							walkdir(files, folder)
							gotta_go_deep = 0
							#print "\n//Traversed directory in %.4f sec\n" % (time.time() - time_2)
							repack(path, folder, pac_file)
							print "\n//Repacked in %.4f sec\n" % (time.time() - time_2)
					if filename[:-4] == sys.argv[2]:
						break
		else:
			folder = sys.argv[1]   #folder
			pac_file = "%s.pac" % folder
			path = os.path.abspath(".")
			index_file = open("%s\\%s.index" % (folder, folder), "r")
			files = getFiles(index_file, folder)
			time_2 = time.time()
			gotta_go_deep = 1
			walkdir(files, folder)
			gotta_go_deep = 0
			#print "\n//Traversed directory in %.4f sec\n" % (time.time() - time_2)
			repack(path, folder, pac_file)
			print "\n//Repacked in %.4f sec\n" % (time.time() - time_2)
	
	elif sys.argv[1].endswith(".ptx"):
		file = sys.argv[1][:-4]
		PTX2(file, file)
		
	elif sys.argv[1].endswith(".dds"):
		read_str = open(sys.argv[1], "rb")
		file_str = read_str.read()
		file_str = texHeader(file_str)
		write_str = open("%stm2" % (sys.argv[1][:-3]), "wb")
		write_str.write(file_str)
		read_str.close()
		write_str.close()
		
	else:
		folder = sys.argv[1]   #folder
		pac_file = "%s.pac" % folder
		path = os.path.abspath(".")
		time_2 = time.time()
		repack(path, folder, pac_file)
		print "\n//Repacked in %.4f sec\n" % (time.time() - time_2)
		
	#all done!
	print "\nAll Done! %.4f sec" % (time.time() - time_start)
	return 0
main()