#PAC Extractor
#coded by James

import re
import sys, os
from struct import *
import time

time_start = time.time()
gotta_go_deep = 0

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

#gets all the offsets from the header
def getFiles(str):
	num_files = unpack("<I", str[4:8])[0] #how many files
	offset = 8
	offsets = []
	
	#for how many files, get each pointer
	for i in range(num_files):
		file = unpack("<I", str[offset:offset+4])[0]
		if file != 0 and file not in offsets:
			offsets.append(file)
		offset += 4
	return offsets

#get the type of file, just add more to this for more file types
#double tested because I was having errors without it
def getType(str):
	try:
		if str[:4].encode("hex").upper() == "4D4F4420" or str[:3] == "MOD":
			suf = "mod"
		elif str[:4].encode("hex").upper() == "44445320" or str[:3] == "DDS":
			suf = "dds"
		elif str[:4].encode("hex").upper() == "53485720" or str[:3] == "SHW":
			suf = "shw"
		elif str[:3] == "MOT" or str[:8].encode("hex").upper() == "500000004D4F5400":
			suf = "mot"
		elif str[:3] == "PAC" or str[:4] == "PNST":
			suf = "pac"
		elif str[:4].encode("hex").upper() == "4F676753" or str[:3] == "Ogg":
			suf = "ogg"
		elif str[:4].encode("hex").upper() == "424D3600" or str[:3] == "BM6":
			suf = "bm6"
		elif str[:4].encode("hex").upper() == "000001BA":
			suf = "mpg"
		elif str[:4] == "LIG2":
			suf = "lig"
		elif str[:3] == "SEF":
			suf = "sef"
		elif str[:3] == "CAM":
			suf = "cam"
		elif str[:3] == "EVE":
			suf = "eve"
		elif str[:3] == "POS":
			suf = "pos"
		elif str[:4].encode("hex").upper() == "EFBBBF23":
			suf = "txt"
		elif str[:4].encode("hex").upper() == "00000000":
			suf = "bd"
		elif str[:4].encode("hex").upper() == "00000100":
			suf = "ico"
		elif str[:4].encode("hex").upper() == "64627354" or str[:4] == "dbsT":
			suf = "tsb"
		elif str[:2] == "# ":
			suf = "txt"
		elif str[:4] == "ff&A":
			suf = "ff"
		elif str[:1] == ";":
			suf = "txt"
		elif (str[:2].encode("hex").upper() == "0600" and str[2:4] != "0000") or str[1:5].encode("hex").upper() == "00656301":
			suf = "so"
		elif str[:3] == "SCM":
			suf = "scm"
		elif str[:3] == "EFM":
			suf = "efm"
		elif str[:8].encode("hex").upper() == "300000004D4F5400":
			suf = "mot2"
		elif str[:8].encode("hex").upper() == "6000000043414D00":
			suf = "cam"
		elif str[:8].encode("hex").upper() == "3000000048494400":
			suf = "hid3"
		elif str[:8].encode("hex").upper() == "9000000048494400":
			suf = "hid1"
		elif str[:8].encode("hex").upper() == "2000000048494400":
			suf = "hid2"
		elif str[:8].encode("hex").upper() == "8000000048494400":
			suf = "hid4"
		elif str[:8].encode("hex").upper() == "4000000048494400":
			suf = "hid5"
		elif str[:8].encode("hex").upper() == "6000000048494400":
			suf = "hid6"
		elif str[:8].encode("hex").upper() == "1000000048494400":
			suf = "hid7"
		elif str[:8].encode("hex").upper() == "A000000048494400":
			suf = "hid8"
		elif str[:8].encode("hex").upper() == "7000000048494400":
			suf = "hid"
		elif str[:8].encode("hex").upper() == "E00000004D4F5400":
			suf = "mot1"
		elif str[:8].encode("hex").upper() == "600000004D4F5400":
			suf = "mot3"
		elif str[:8].encode("hex").upper() == "400000004D4F5400":
			suf = "mot4"
		elif str[:8].encode("hex").upper() == "700000004D4F5400":
			suf = "mot5"
		elif str[:8].encode("hex").upper() == "800000004D4F5400":
			suf = "mot6"
		elif str[:8].encode("hex").upper() == "100100004D4F5400":
			suf = "mot7"
		elif str[:8].encode("hex").upper() == "200000004D4F5400":
			suf = "mot8"
		elif str[:8].encode("hex").upper() == "100000004D4F5400":
			suf = "mot9"
		elif str[:4].encode("hex").upper() == "2E545343":
			suf = "tsc"
		elif "# End" in str:
			suf = "txt"
		elif str[:4].encode("hex").upper() == "6970756D":
			suf = "ipum"

		#last chance, if the first three values are ASCII, use em.
		elif (unpack("B", str[:1]) >= 65 and unpack("B", str[:1]) <= 90 and  unpack("B", str[1:2]) >= 65 and unpack("B", str[1:2]) <= 90 and unpack("B", str[2:3]) >= 65 and unpack("B", str[2:3]) <= 90) or (unpack("B", str[:1]) >= 97 and unpack("B", str[:1]) <= 122 and unpack("B", str[1:2]) >= 97 and unpack("B", str[1:2]) <= 122 and unpack("B", str[2:3]) >= 97 and unpack("B", str[2:3]) <= 122):
			suf = str[:3]
		else: suf = "ukn"
	except:
		suf = "ukn"
	return suf

def IPUM(str, ipum_name, pac_name):
	offs = 16
	num_files = unpack("<I", str[12:16])[0]
	try:
		os.mkdir("%s\\%s" % (pac_name, ipum_name))
	except WindowsError:
		""
	index_file = open("%s\\%s\\%s.index" % (pac_name, ipum_name, ipum_name), "w")
	for i in range(num_files):
		file_len = unpack("<I", str[offs+4:offs+8])[0]
		offs +=8
		file_str = str[offs:offs+file_len]
		offs += file_len
		index_file.write("%s_%.3d.dds\n" % (ipum_name, i))
		try:
			file_open = open("%s\\%s\\%s_%.3d.dds" % (pac_name, ipum_name, ipum_name, i), "wb")
			file_open.write(file_str)
			file_open.close()
		except:
			print "\tError Writing %s_%.3d.dds" % (ipum_name, i)
	
	return 0
	
#PTX extractor
def PTX(str, ptx_name, pac_name):
	time_1 = time.time()
	print "PTX Archive: %s.ptx" % ptx_name
	num_files = unpack("<I", str[:4])[0] #number of files
	offsets = []
	last = 0
	tex_len = []
	
	#too lazy to properly write it, just searched
	for i in range(num_files):
		offsets.append(str.find("DDS |", last))
		last = str.find("DDS |", last)+4
		tex_len.append(unpack("<I", str[offsets[i]-12:offsets[i]-8])[0])
		
	#make another sub directory
	try:
		os.mkdir("%s\\%s" % (pac_name, ptx_name))
	except WindowsError:
		""
	index_file = open("%s\\%s\\%s.index" % (pac_name, ptx_name, ptx_name), "w")
	#for how many files, write each file
	for i in range(num_files):
		try:
			file_str = str[offsets[i]:offsets[i] + tex_len[i]]
		except IndexError:
			file_str = str[offsets[i]:]
		#index files, and writing contents
		index_file.write("%s_%.3d.dds\n" % (ptx_name, i))
		#print "\tWriting: %s_%.3d.dds" % (ptx_name, i)
		try:
			file_open = open("%s\\%s\\%s_%.3d.dds" % (pac_name, ptx_name, ptx_name, i), "wb")
			file_open.write(file_str)
			file_open.close()
		except:
			print "\tError Writing %s_%.3d.dds" % (ptx_name, i)
			
	#print "\n	//Finished in %.4f sec\n" % (time.time() - time_1)
	return 0

def PTX2(str, ptx_name):
	time_1 = time.time()
	print "PTX Archive: %s.ptx" % ptx_name
	num_files = unpack("<I", str[:4])[0] #number of files
	offsets = []
	last = 0
	tex_len = []
	
	#too lazy to properly write it, just searched
	for i in range(num_files):
		offsets.append(str.find("DDS", last))
		last = str.find("DDS", last)+4
		tex_len.append(unpack("<I", str[offsets[i]-12:offsets[i]-8])[0])
		
	#make another sub directory
	try:
		os.mkdir(ptx_name)
	except WindowsError:
		""
	index_file = open("%s\\%s.index" % (ptx_name, ptx_name), "w")
	#for how many files, write each file
	for i in range(num_files):
		try:
			file_str = str[offsets[i]:offsets[i] + tex_len[i]]
		except IndexError:
			file_str = str[offsets[i]:]
		#index files, and writing contents
		index_file.write("%s_%.3d.dds\n" % (ptx_name, i))
		#print "\tWriting: %s_%.3d.dds" % (ptx_name, i)
		try:
			file_open = open("%s\\%s_%.3d.dds" % (ptx_name, ptx_name, i), "wb")
			file_open.write(file_str)
			file_open.close()
		except:
			print "\tError Writing %s_%.3d.dds" % (ptx_name, i)
			
	#print "\n	//Finished in %.4f sec\n" % (time.time() - time_1)
	return 0

def walkdir(dirname):
	for root, dirs, files in os.walk(dirname):
		dirs.sort(key=natural_keys)
		files.sort(key=natural_keys)
		path = os.path.abspath(root)
		for filename in files:
			filename = os.path.basename(filename)
			if ".pac" in filename[-4:]:
				pac_file = filename
				Unpack(path, pac_file)
			else:
				continue
				

def Unpack(path, pac_file):
	pac_name = pac_file[:pac_file.find(".")]	#the name of the folder
	try:
		os.chdir(path)
	except:
		print "nope"
		return -1

	#if can't open, exit
	#print "Opening: %s" % pac_file
	try:
		pac_open = open(pac_file, "rb")
	except:
		print "Error Opening %s" % pac_file
		return -1
	
	#if can't read, exit
	print "Reading: %s" % pac_file
	try:
		pac_str = pac_open.read()
	except:
		print "Error Reading %s" % pac_file
		return -1
	pac_open.close()
	
	#if the header is corrupt, exit
	try:
		offsets = getFiles(pac_str)
		print "\nNumber of Files: %d\n" % len(offsets)
	except:
		print "Error Getting Contents of %s" % pac_file
		return -1
	
	#make directory
	try:
		os.mkdir(pac_name)
	except:
		""
	
	#write all the files
	index_file = open("%s\\%s.index" % (pac_name, pac_name), "w")
	if "PNST" in pac_str[:4]:
		index_file.write("PNST\n")
	for i in range(len(offsets)):
		try:
			file_str = pac_str[offsets[i]:offsets[i+1]]
		except IndexError:
			file_str = pac_str[offsets[i]:]
		
		if "ipum" in file_str[:5]:
			IPUM(file_str, "%s_%.3d" % (pac_name, i), pac_name)
			index_file.write("%s vid\n" % ("%s_%.3d"% (pac_name, i)))
			
		elif "DDS |" in file_str[4:] and "PAC." not in file_str[:5] and "PNST" not in file_str[:5] and "ipum" not in file_str[:5]:
			if "DDS |" in file_str[112:117] :
				index_file.write("%s_%.3d.dds\n" % (pac_name, i))
				#print "Writing: %s_%.3d.dds" % (pac_name, i)
				try:
					file_open = open("%s\\%s_%.3d.dds" % (pac_name,pac_name, i), "wb")
					file_open.write(file_str[112:])
					file_open.close()
				except:
					print "Error Writing %s" % ("%s_%.3i.dds" % (pac_name, i))
			else:
				#print "%X" % offsets[i]
				PTX(file_str, "%s_%.3d" % (pac_name, i), pac_name)
				index_file.write("%s folder\n" % ("%s_%.3d"% (pac_name, i)))
		else:
			index_file.write("%s_%.3d.%s\n" % (pac_name, i,getType(file_str)))
			#print "Writing: %s_%3d.%s" % (pac_name, i,getType(file_str))
			try:
				file_open = open("%s\\%s_%.3d.%s" % (pac_name,pac_name, i,getType(file_str)), "wb")
				file_open.write(file_str)
				file_open.close()
			except:
				print "Error Writing %s" % ("%s_%.3i.%s" % (pac_name, i,getType(file_str)))
		
	index_file.close()

	if gotta_go_deep:
		walkdir(pac_name)
	return 0

def main():
	global gotta_go_deep
	#greetings
	print "\n=================================\nDevil May Cry 3 \nPac extractor\nv1.8\nCoded by James aka Jamesuminator updated by Che\n=================================\n---------------------------------\n"

	if len(sys.argv) < 2:
		gotta_go_deep = 1
		for root, dirs, files in os.walk("."):
			files.sort(key=natural_keys)
			path = os.path.abspath(root)
			for filename in files:
				filename = os.path.basename(filename)
				if ".pac" in filename[-4:]:
					pac_file = filename
					time_2 = time.time()
					Unpack(path, pac_file)
					#print "\n//Unpacked in %.4f sec\n" % (time.time() - time_2)

	elif len(sys.argv) == 3:
		gotta_go_deep = 1
		if sys.argv[2] == "all":
			pac_file = sys.argv[1]
			gotta_go_deep = 1
			path = os.path.abspath(".")
			time_2 = time.time()
			Unpack(path, pac_file)
			#print "\n//Unpacked in %.4f sec\n" % (time.time() - time_2)
		else:
			break_while = False
			break_loop = False
			for root, dirs, files in os.walk("."):
				dirs.sort(key=natural_keys)
				if break_loop == True:
					break
				files.sort(key=natural_keys)
				path = os.path.abspath(".")
				for filename in files:
					if filename != sys.argv[1] and break_while != True:
						continue
					else:
						break_while = True
						if ".pac" in filename[-4:]:
							pac_file = filename
							#time_2 = time.time()
							Unpack(path, filename)
							#print "\n//Unpacked in %.4f sec\n" % (time.time() - time_2)
					if filename == sys.argv[2]:
						break_loop = True
						break 
				
		
	elif sys.argv[1].endswith(".ptx"):
		ptx_file = sys.argv[1]
		ptx_open = open(ptx_file, "rb")
		ptx_str = ptx_open.read()
		PTX2(ptx_str, ptx_file[:-4])
		
	elif sys.argv[1].endswith(".tm2"):
		read_str = open(sys.argv[1], "rb")
		file_str = read_str.read()
		write_str = open("%sdds" % (sys.argv[1][:-3]), "wb")
		write_str.write(file_str[112:])
		read_str.close()
		write_str.close()
		
	else:
		pac_file = sys.argv[1]
		path = os.path.abspath(".")
		time_2 = time.time()
		Unpack(path, pac_file)
		#print "\n//Unpacked in %.4f sec\n" % (time.time() - time_2)

	print "\nAll Done! %.4f sec" % (time.time() - time_start)
	return 0
main()
	

	