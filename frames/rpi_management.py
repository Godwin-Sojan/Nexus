import customtkinter as ctk
from tkinter import messagebox
import database
import socket
from config import *

class RPIManagementWindow(ctk.CTkToplevel):
    def __init__(self, master, username, current_ip, current_user, current_pass, current_port, update_callback):
        super().__init__(master)
        self.title("Manage RPI")
        self.geometry("500x600")
        self.attributes("-topmost", True)
        
        self.username = username
        self.update_callback = update_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.container = ctk.CTkFrame(self, corner_radius=20, fg_color=COLOR_CARD)
        self.container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkLabel(self.container, text="RPI Configuration", font=FONT_HEADER)
        self.header.pack(pady=(30, 20))

        self.ip_entry = self.create_entry("IP Address", current_ip)
        self.port_entry = self.create_entry("Port (Default: 5000)", str(current_port or 5000))
        self.user_entry = self.create_entry("Username", current_user)
        self.pass_entry = self.create_entry("Password", current_pass, show="*")
        
        self.btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.btn_frame.pack(pady=(30, 20))

        self.test_btn = ctk.CTkButton(self.btn_frame, text="Test Connection", width=150, height=35, font=FONT_BODY,
                                      fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
                                      command=self.test_connection)
        self.test_btn.pack(side="left", padx=10)

        self.save_btn = ctk.CTkButton(self.btn_frame, text="Save Changes", width=150, height=35, font=FONT_BODY,
                                      fg_color=COLOR_PRIMARY, text_color=COLOR_BG, hover_color=COLOR_SECONDARY,
                                      command=self.save_config)
        self.save_btn.pack(side="left", padx=10)

        # Center the window
        self.after(100, self.center_window)

    def create_entry(self, placeholder, initial_value, show=None):
        entry = ctk.CTkEntry(self.container, placeholder_text=placeholder, width=350, height=40, font=FONT_BODY, show=show)
        entry.pack(pady=5)
        if initial_value:
            entry.insert(0, initial_value)
        return entry

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def test_connection(self):
        ip = self.ip_entry.get()
        port_str = self.port_entry.get()
        
        if not ip:
            messagebox.showwarning("Warning", "Please enter an IP address.")
            return
        
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid port number.")
            return

        # Disable button during test
        self.test_btn.configure(state="disabled", text="Testing...")
        self.update_idletasks()

        def run_test():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    self.after(0, lambda: messagebox.showinfo("Success", f"Successfully reached {ip}:{port}!"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", f"Could not reach {ip}:{port}.\nError code: {result}"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Connection test failed: {e}"))
            finally:
                self.after(0, lambda: self.test_btn.configure(state="normal", text="Test Connection"))

        import threading
        threading.Thread(target=run_test, daemon=True).start()

    def save_config(self):
        ip = self.ip_entry.get()
        port_str = self.port_entry.get()
        user = self.user_entry.get()
        pwd = self.pass_entry.get()
        
        if not all([ip, port_str, user, pwd]):
            messagebox.showerror("Error", "Please fill all connection fields")
            return
            
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid port number.")
            return

        if database.update_user_rpi_info(self.username, ip, user, pwd, port):
            messagebox.showinfo("Success", "RPI configuration updated!")
            if self.update_callback:
                self.update_callback(ip, user, pwd, port)
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to update RPI configuration")
