import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, Toplevel
from tkinter.ttk import Combobox
import pygame
import sys
import threading
import io
import subprocess
import os


pygame_running = False
current_file_path = None  # Şu anki kaydedilmiş dosyanın yolu

class RedirectOutput(io.StringIO):
    def __init__(self, output_widget):
        super().__init__()
        self.output_widget = output_widget

    def write(self, text):
        self.output_widget.insert(tk.END, text)
        self.output_widget.see(tk.END)

def start_pygame_code():
    global pygame_running
    if pygame_running:
        return

    code = code_editor.get("1.0", tk.END)

    def run_pygame():
        global pygame_running
        pygame_running = True
        redirect_output = RedirectOutput(debug_text)
        sys.stdout = redirect_output

        try:
            pygame.init()
            screen_width = int(width_entry.get())
            screen_height = int(height_entry.get())
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)

            clock = pygame.time.Clock()
            exec(code)

        except Exception as e:
            print(f"Hata: {str(e)}")
        finally:
            sys.stdout = sys.__stdout__
            pygame.quit()
            pygame_running = False

    pygame_thread = threading.Thread(target=run_pygame)
    pygame_thread.start()

def stop_pygame():
    global pygame_running
    pygame_running = False
    pygame.quit()
    print("Project Stopped")

def run_python_file():
    if current_file_path:
        subprocess.run(["python", current_file_path])
    else:
        messagebox.showwarning("Warning", "Please save the file before running it.")

def open_file():
    global current_file_path
    current_file_path = filedialog.askopenfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
    if current_file_path:
        with open(current_file_path, "r") as file:
            code_editor.delete("1.0", tk.END)
            code_editor.insert(tk.END, file.read())

def save_file():
    global current_file_path
    if not current_file_path:
        current_file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
    if current_file_path:
        with open(current_file_path, "w") as file:
            file.write(code_editor.get("1.0", tk.END))

def save_as_file():
    global current_file_path
    current_file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
    if current_file_path:
        with open(current_file_path, "w") as file:
            file.write(code_editor.get("1.0", tk.END))

def export_to_exe():
    def export():
        nonlocal exe_name, icon_path
        export_dir = filedialog.askdirectory()
        if export_dir and current_file_path:
            command = ["pyinstaller", "--onefile", current_file_path]
            if exe_name.get():
                command += ["--name", exe_name.get()]
            if icon_path.get():
                command += ["--icon", icon_path.get()]
            subprocess.run(command)
            messagebox.showinfo("Export", f"Game Exported : '{export_dir}' ENJOY !.")

    export_window = Toplevel(root)
    export_window.title("Export to .exe")
    export_window.geometry("400x200")

    tk.Label(export_window, text="Name (Optinal):").pack(pady=5)
    exe_name = tk.Entry(export_window, width=30)
    exe_name.pack(pady=5)

    tk.Label(export_window, text="Icon (Optional):").pack(pady=5)
    icon_path = tk.Entry(export_window, width=30)
    icon_path.pack(pady=5)

    tk.Button(export_window, text="Browse Icon", command=lambda: icon_path.insert(0, filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico")])), width=10).pack(pady=5)

    tk.Button(export_window, text="Export", command=export, width=10).pack(pady=10)

# Ana Tkinter pencere oluştur
root = tk.Tk()
root.title("K Engine")
root.geometry("1000x600")
root.configure(bg="#2E2E2E")

# Menüyü oluştur
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_as_file)
menu_bar.add_cascade(label="File", menu=file_menu)

export_menu = tk.Menu(menu_bar, tearoff=0)
export_menu.add_command(label="Export to .exe", command=export_to_exe)
menu_bar.add_cascade(label="Export", menu=export_menu)

root.config(menu=menu_bar)

# Kod editörü
code_editor = scrolledtext.ScrolledText(root, width=50, height=30, font=("Courier", 12), bg="#2E2E2E", fg="#FFFFFF", insertbackground='white')
code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Debug alanı
debug_text = scrolledtext.ScrolledText(root, width=50, height=10, font=("Courier", 10), bg="#2E2E2E", fg="blue", insertbackground='white')
debug_text.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Boyut ve pozisyon ayarları için giriş alanları
frame = tk.Frame(root, bg="#2E2E2E")
frame.pack(side=tk.RIGHT, fill=tk.Y)

tk.Label(frame, text="Width:", bg="#2E2E2E", fg="#FFFFFF").pack(pady=5)
width_entry = tk.Entry(frame, bg="#444444", fg="#FFFFFF", insertbackground='white')
width_entry.insert(0, "500")
width_entry.pack(pady=5)

tk.Label(frame, text="Height:", bg="#2E2E2E", fg="#FFFFFF").pack(pady=5)
height_entry = tk.Entry(frame, bg="#444444", fg="#FFFFFF", insertbackground='white')
height_entry.insert(0, "400")
height_entry.pack(pady=5)

# Seçim listesi oluştur
mode_label = tk.Label(frame, text="Mode:", bg="#2E2E2E", fg="#FFFFFF")
mode_label.pack(pady=5)
mode_combobox = Combobox(frame, values=["Run File", "Editor"])
mode_combobox.current(1)  # Varsayılan olarak 'Editor' seçili
mode_combobox.pack(pady=5)

# Çalıştır butonu
run_button = tk.Button(frame, text="Run", command=lambda: run_python_file() if current_file_path and mode_combobox.get() == "Run File" else start_pygame_code(), bg="#007BFF", fg="#FFFFFF")
run_button.pack(pady=5)

# Durdur butonu
stop_button = tk.Button(frame, text="Stop", command=stop_pygame, bg="#FF4C4C", fg="#FFFFFF")
stop_button.pack(pady=5)

# K logosu eklemek için Canvas widgetı
canvas = tk.Canvas(frame, width=50, height=50, bg="#2E2E2E", highlightthickness=0)
canvas.pack(pady=10)
canvas.create_text(25, 25, text="K", font=("Arial", 24), fill="#FFFFFF")



root.mainloop()
