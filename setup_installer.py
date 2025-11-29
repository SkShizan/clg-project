import os
import sys
import time
import zipfile
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# --- CONFIGURATION ---
INSTALL_FOLDER_NAME = "AttendanceSystem_App"
EXE_NAME = "AttendanceSystem.exe"

def get_resource_path(relative_path):
    """Get path to the bundled zip file"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def find_exe_and_launch(install_root):
    """
    RECURSIVE SEARCH: Finds the .exe even if it's inside extra folders.
    """
    target_exe = None
    
    # Walk through all folders to find the specific EXE file
    for root_dir, dirs, files in os.walk(install_root):
        if EXE_NAME in files:
            target_exe = os.path.join(root_dir, EXE_NAME)
            break
    
    if not target_exe:
        messagebox.showerror("Error", f"Could not find '{EXE_NAME}' inside the installation folder.\n\nFolder: {install_root}")
        sys.exit()
        return

    # Launch the found EXE and close this installer
    try:
        # cwd=os.path.dirname(target_exe) ensures the app finds its own internal files
        subprocess.Popen([target_exe], cwd=os.path.dirname(target_exe))
        sys.exit() 
    except Exception as e:
        messagebox.showerror("Launch Error", f"Found app but failed to start:\n{e}")
        sys.exit()

def install_and_run():
    # Determine where to install (Next to the Setup.exe)
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
    install_path = os.path.join(base_dir, INSTALL_FOLDER_NAME)

    # --- SCENARIO 1: ALREADY INSTALLED ---
    if os.path.exists(install_path):
        status_label.config(text="Launching...")
        root.update()
        # Check if we can find the exe inside
        root.after(500, lambda: find_exe_and_launch(install_path))
        return

    # --- SCENARIO 2: FRESH INSTALL ---
    status_label.config(text="First Time Setup: Extracting...")
    root.update()
    
    try:
        zip_path = get_resource_path("payload.zip")
        
        if not os.path.exists(zip_path):
            status_label.config(text="Error: Missing Payload")
            messagebox.showerror("Error", "Installer is corrupt. 'payload.zip' is missing.")
            return

        # Extract Zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            total = len(file_list)
            
            for i, file in enumerate(file_list):
                zip_ref.extract(file, install_path)
                
                # Update UI every 5 files to be fast
                if i % 5 == 0: 
                    percent = (i / total) * 100
                    progress_bar['value'] = percent
                    root.update()
        
        # Extraction Done
        progress_bar['value'] = 100
        status_label.config(text="Starting Application...")
        root.update()
        
        # Launch immediately using the Smart Search
        root.after(1000, lambda: find_exe_and_launch(install_path))

    except Exception as e:
        status_label.config(text="Installation Failed")
        messagebox.showerror("Critical Error", str(e))

# --- GUI SETUP ---
root = tk.Tk()
root.title("Setup")
root.overrideredirect(True) # Remove window borders
root.geometry("400x150")

# Center the window
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws/2) - (400/2)
y = (hs/2) - (150/2)
root.geometry(f'400x150+{int(x)}+{int(y)}')

root.configure(bg="#ecf0f1")

tk.Label(root, text="Attendance System", font=("Segoe UI", 14, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=(20, 5))
status_label = tk.Label(root, text="Checking System...", font=("Segoe UI", 10), bg="#ecf0f1", fg="#7f8c8d")
status_label.pack(pady=5)

style = ttk.Style()
style.theme_use('default')
style.configure("TProgressbar", thickness=10, background="#27ae60")
progress_bar = ttk.Progressbar(root, length=300, mode="determinate", style="TProgressbar")
progress_bar.pack(pady=15)

# Run logic automatically
root.after(100, install_and_run)
root.mainloop()