import os
import sys
import time
import shutil
import threading
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
from django.core.management import execute_from_command_line

# --- 1. LOGGING SETUP ---
if getattr(sys, 'frozen', False):
    app_path = os.path.dirname(sys.executable)
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

log_path = os.path.join(app_path, 'debug.log')

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(log_path, "a")
    def write(self, message):
        try: self.log.write(message); self.log.flush()
        except: pass
    def flush(self):
        try: self.log.flush()
        except: pass

sys.stdout = Logger()
sys.stderr = Logger()

# --- GLOBAL VARIABLES ---
splash_root = None
progress_bar = None
status_label = None
webview_lib = None 

# --- 2. BACKEND LOGIC (CLOUD MODE) ---

def check_cloud_and_load():
    """Connects to Cloud DB, Auto-Migrates if needed, then Launches."""
    try:
        # A. Load Webview
        global webview_lib
        update_ui("Loading Interface...", 20)
        import webview
        webview_lib = webview
        
        # B. Load Django
        update_ui("Connecting to Cloud Database...", 40)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
        import django
        django.setup()
        
        # C. Check/Run Migrations (Auto-Setup Cloud Tables)
        update_ui("Verifying Cloud Tables...", 60)
        from django.db import connection
        from django.db.utils import OperationalError, ProgrammingError
        from django.core.management import call_command
        
        try:
            # Try a simple query to see if tables exist
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM auth_user")
        except (OperationalError, ProgrammingError):
            # Tables don't exist (First run on new Cloud DB)
            update_ui("First Run: Creating Cloud Tables...", 80)
            call_command('migrate', interactive=False)
        
        # D. Launch App Directly (Admin Check Removed)
        # We assume you created the Superuser via the Supabase Dashboard
        finish_loading()

    except Exception as e:
        # Show connection errors clearly
        error_message = f"Could not connect to Cloud DB.\n\n1. Check internet connection.\n2. Check database password.\n\nDetails: {e}"
        splash_root.after(0, lambda: messagebox.showerror("Connection Error", error_message))

def finish_loading():
    update_ui("Starting Server...", 90)
    t = threading.Thread(target=run_django_server)
    t.daemon = True
    t.start()
    
    update_ui("Launching...", 100)
    time.sleep(0.5)
    splash_root.after(0, splash_root.destroy)

def run_django_server():
    try:
        from django.core.management import execute_from_command_line
        sys.argv = ['manage.py', 'runserver', '8000', '--noreload', '--insecure']
        execute_from_command_line(sys.argv)
    except Exception as e:
        print(f"Server Error: {e}")

# --- 3. FRONTEND UI ---

def update_ui(text, percent):
    if splash_root:
        splash_root.after(0, lambda: _do_update(text, percent))

def _do_update(text, percent):
    if status_label: status_label.config(text=text)
    if progress_bar: progress_bar['value'] = percent

def center_window(root, width=500, height=350):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

# --- 4. MAIN ENTRY POINT ---
if __name__ == '__main__':
    splash_root = tk.Tk()
    splash_root.title("Attendance System")
    splash_root.overrideredirect(False)
    splash_root.attributes('-topmost', True)
    splash_root.focus_force()
    
    center_window(splash_root, 450, 250)
    splash_root.configure(bg="#f4f7f6")
    
    tk.Label(splash_root, text="Attendance System", font=("Segoe UI", 16, "bold"), bg="#f4f7f6", fg="#2c3e50").pack(pady=(40, 10))
    status_label = tk.Label(splash_root, text="Initializing...", bg="#f4f7f6", font=("Segoe UI", 10))
    status_label.pack(pady=5)
    
    style = ttk.Style()
    style.theme_use('default')
    style.configure("TProgressbar", thickness=10, background="#3498db")
    progress_bar = ttk.Progressbar(splash_root, length=350, mode="determinate", style="TProgressbar")
    progress_bar.pack(pady=20)
    
    t = threading.Thread(target=check_cloud_and_load)
    t.daemon = True
    t.start()
    
    splash_root.mainloop()
    
    if webview_lib:
        try:
            webview_lib.create_window("Attendance Management System", "http://127.0.0.1:8000", width=1200, height=800, resizable=True)
            webview_lib.start()
        except Exception as e:
            ctypes.windll.user32.MessageBoxW(0, f"Crash: {e}", "Error", 0x10)