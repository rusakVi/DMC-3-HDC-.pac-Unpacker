import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

PYTHON_27 = r"C:\Python27\python.exe"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
EX_SCRIPT = os.path.join(SCRIPTS_DIR, "ex.py")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DMC3 PAC Unpacker")
        self.root.geometry("540x240")

        tk.Label(root, text="DMC3 PAC Unpacker", font=("Arial", 14, "bold")).pack(pady=12)

        tk.Button(root, text="🔎 Перевірити систему", font=("Arial", 11), command=self.check).pack(pady=6)
        tk.Button(root, text="🔓 Розпакувати .pac", font=("Arial", 12), command=self.unpack).pack(pady=10)

        self.status = tk.Label(root, text="", fg="black", wraplength=520, justify="left")
        self.status.pack(pady=10)

        self.check()

    def check(self):
        problems = []
        if not os.path.exists(PYTHON_27):
            problems.append(f"Не знайдено Python 2.7: {PYTHON_27}")
        if not os.path.exists(SCRIPTS_DIR):
            problems.append(f"Не знайдено папку scripts: {SCRIPTS_DIR}")
        if not os.path.exists(EX_SCRIPT):
            problems.append(f"Не знайдено ex.py: {EX_SCRIPT}")

        if problems:
            self.status.config(text="Проблеми:\n- " + "\n- ".join(problems), fg="red")
            return False

        self.status.config(text="OK: Python 2.7 і ex.py знайдені. Можна запускати.", fg="green")
        return True

    def unpack(self):
        if not self.check():
            messagebox.showerror("Помилка", "Виправ проблеми (дивись червоний текст).")
            return

        pac_path = filedialog.askopenfilename(
            title="Оберіть .pac файл",
            filetypes=[("PAC files", "*.pac"), ("All files", "*.*")]
        )
        if not pac_path:
            return

        pac_dir = os.path.dirname(pac_path)
        pac_name = os.path.basename(pac_path)
        pac_base = os.path.splitext(pac_name)[0]
        out_dir = pac_base + "_extracted"

        # створюємо BAT поряд із .pac (так найпростіше з правами/шляхами)
        bat_path = os.path.join(pac_dir, f"__run_ex_{pac_base}.bat")

        # ВАЖЛИВО: тільки ASCII в bat, щоб не було проблем з кодуванням
        bat_text = "\r\n".join([
            "@echo off",
            f'cd /d "{pac_dir}"',
            "echo Running:",
            f'echo {PYTHON_27} "{EX_SCRIPT}" "{pac_name}" "{out_dir}"',
            f'"{PYTHON_27}" "{EX_SCRIPT}" "{pac_name}" "{out_dir}"',
            "echo.",
            "echo ===== DONE =====",
            f'echo Expected folder: "{pac_dir}\\{out_dir}"',
            "pause"
        ]) + "\r\n"

        try:
            with open(bat_path, "w", encoding="ascii", errors="ignore") as f:
                f.write(bat_text)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося створити .bat:\n{e}")
            return

        try:
            # Відкриваємо нову консоль і запускаємо .bat
            subprocess.Popen(
                ["cmd.exe", "/k", bat_path],
                cwd=pac_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити консоль:\n{e}")
            return

        self.status.config(
            text=f"Запущено. Очікувана папка: {os.path.join(pac_dir, out_dir)}",
            fg="green"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
