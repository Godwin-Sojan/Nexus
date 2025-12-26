import customtkinter as ctk
from tkinter import messagebox
import database
from config import *
from email_validator import validate_email, EmailNotValidError
from rpi_utils import NetworkScanner, SSHClient
from email_utils import EmailVerifier
import threading

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, login_callback):
        super().__init__(master)
        self.login_callback = login_callback
        self.master = master

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.frame = ctk.CTkFrame(self, width=300, height=380, corner_radius=20, fg_color=COLOR_CARD)
        self.frame.grid(row=1, column=0, sticky="ns")
        self.frame.grid_propagate(False)

        self.label = ctk.CTkLabel(self.frame, text="Welcome Back", font=FONT_HEADER)
        self.label.pack(pady=(50, 30))

        self.username_entry = ctk.CTkEntry(self.frame, placeholder_text="Username", width=220, height=40, font=FONT_BODY)
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.frame, placeholder_text="Password", show="*", width=220, height=40, font=FONT_BODY)
        self.password_entry.pack(pady=10)

        self.login_button = ctk.CTkButton(self.frame, text="Login", width=220, height=40, font=FONT_BODY,
                                          command=self.login_event, fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY)
        self.login_button.pack(pady=30)

        self.register_link = ctk.CTkLabel(self.frame, text="Create Account", font=("Roboto", 12, "underline"), text_color="gray70", cursor="hand2")
        self.register_link.pack(pady=5)
        self.register_link.bind("<Button-1>", lambda e: master.show_register())

    def login_event(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        user_info = database.login_user(username, password)
        if user_info:
            self.login_callback(user_info)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, master, back_callback):
        super().__init__(master)
        self.back_callback = back_callback
        self.master = master
        self.scanner = NetworkScanner()
        
        # Email verification is now console-based
        self.email_verifier = EmailVerifier()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame = ctk.CTkFrame(self, width=400, height=600, corner_radius=20, fg_color=COLOR_CARD)
        self.frame.grid(row=0, column=0, sticky="ns", pady=20)
        self.frame.grid_propagate(False)

        self.step = 1
        self.rpi_data = {}
        
        self.setup_step1_ui()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def setup_step1_ui(self):
        self.clear_frame()
        
        ctk.CTkLabel(self.frame, text="Create Account", font=FONT_HEADER).pack(pady=(30, 20))

        self.name_entry = ctk.CTkEntry(self.frame, placeholder_text="Full Name", width=280, height=40, font=FONT_BODY)
        self.name_entry.pack(pady=10)

        self.username_entry = ctk.CTkEntry(self.frame, placeholder_text="Username", width=280, height=40, font=FONT_BODY)
        self.username_entry.pack(pady=10)

        self.gmail_entry = ctk.CTkEntry(self.frame, placeholder_text="Gmail", width=280, height=40, font=FONT_BODY)
        self.gmail_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.frame, placeholder_text="Password", show="*", width=280, height=40, font=FONT_BODY)
        self.password_entry.pack(pady=10)

        self.rpi_var = ctk.StringVar(value="No")
        self.rpi_switch = ctk.CTkSwitch(self.frame, text="Enable RPi Integration", variable=self.rpi_var, onvalue="Yes", offvalue="No", font=FONT_BODY)
        self.rpi_switch.pack(pady=20)

        ctk.CTkButton(self.frame, text="Next", width=280, height=40, font=FONT_BODY,
                      command=self.step1_next, fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY).pack(pady=20)

        login_link = ctk.CTkLabel(self.frame, text="Back to Login", font=("Roboto", 12, "underline"), text_color="gray70", cursor="hand2")
        login_link.pack(pady=5)
        login_link.bind("<Button-1>", lambda e: self.back_callback())

    def step1_next(self):
        name = self.name_entry.get()
        username = self.username_entry.get()
        gmail = self.gmail_entry.get()
        password = self.password_entry.get()
        
        if not all([name, username, gmail, password]):
             messagebox.showerror("Error", "Please fill all fields")
             return

        try:
            valid = validate_email(gmail, check_deliverability=False) # Faster check
            gmail = valid.normalized
        except EmailNotValidError as e:
            messagebox.showerror("Invalid Email", str(e))
            return

        # Check if username exists
        if database.user_exists(username):
            messagebox.showerror("Error", "Username already exists")
            return
        
        self.user_data = {
            "name": name,
            "username": username,
            "gmail": gmail,
            "password": password,
            "rpi_enabled": self.rpi_var.get() == "Yes"
        }

        if self.user_data["rpi_enabled"]:
            self.setup_step2_rpi_ui()
        else:
            self.setup_step3_email_ui()

    def setup_step2_rpi_ui(self):
        self.clear_frame()
        ctk.CTkLabel(self.frame, text="RPi Setup", font=FONT_HEADER).pack(pady=(30, 10))
        
        # Container for device list (will be created only if devices found)
        self.device_list_container = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.device_list_container.pack(pady=10, fill="both", expand=True)
        
        self.device_list = None  # Will be created if devices are found
        
        # Manual IP Entry
        self.manual_ip = ctk.CTkEntry(self.frame, placeholder_text="Enter RPi IP Address", width=280, height=40, font=FONT_BODY)
        self.manual_ip.pack(pady=5)

        # Creds
        self.rpi_user = ctk.CTkEntry(self.frame, placeholder_text="RPi Username (e.g. pi)", width=280, height=40, font=FONT_BODY)
        self.rpi_user.pack(pady=5)
        self.rpi_pass = ctk.CTkEntry(self.frame, placeholder_text="RPi Password", show="*", width=280, height=40, font=FONT_BODY)
        self.rpi_pass.pack(pady=5)

        self.connect_btn = ctk.CTkButton(self.frame, text="Connect & Sync", width=280, height=40, font=FONT_BODY,
                                         command=self.connect_rpi, state="disabled",
                                         fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY)
        self.connect_btn.pack(pady=15)
        
        # Status label at the bottom
        self.status_label = ctk.CTkLabel(self.frame, text="🔍 Scanning network for RPi devices...", 
                                         font=FONT_BODY, text_color="gray70")
        self.status_label.pack(pady=(5, 20))
        
        # Start scan in background
        threading.Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        devices = self.scanner.scan_network()
        self.master.after(0, lambda: self.update_device_list(devices))

    def update_device_list(self, devices):
        self.connect_btn.configure(state="normal")
        
        if len(devices) > 0:
            # Devices found - show scrollable list
            self.status_label.configure(text=f"✅ Found {len(devices)} device(s) with SSH", text_color="green")
            
            # Create scrollable frame for devices
            self.device_list = ctk.CTkScrollableFrame(self.device_list_container, width=280, height=120,
                                                     fg_color=COLOR_BG, corner_radius=10)
            self.device_list.pack(pady=5, fill="both", expand=True)
            
            ctk.CTkLabel(self.device_list_container, text="Select a device:", 
                        font=("Roboto", 12, "bold"), text_color="gray70").pack(anchor="w", padx=10, pady=(0, 5))
            
            for dev in devices:
                btn = ctk.CTkButton(self.device_list, text=f"🖥️  {dev['hostname']} ({dev['ip']})", 
                                    command=lambda ip=dev['ip']: self.select_device(ip),
                                    fg_color=COLOR_CARD, hover_color=COLOR_PRIMARY,
                                    border_width=2, border_color="gray30",
                                    anchor="w", font=FONT_BODY)
                btn.pack(fill="x", pady=3, padx=5)
        else:
            # No devices found - show clean message
            self.status_label.configure(text="ℹ️  No RPi devices found. Enter IP manually below.", 
                                       text_color="orange")
            
            # Show a helpful message in the container
            info_frame = ctk.CTkFrame(self.device_list_container, fg_color=COLOR_CARD, corner_radius=10)
            info_frame.pack(pady=10, padx=20, fill="x")
            
            ctk.CTkLabel(info_frame, text="💡 Tip", font=("Roboto", 14, "bold"), 
                        text_color=COLOR_PRIMARY).pack(pady=(15, 5))
            ctk.CTkLabel(info_frame, text="Make sure your RPi is:", 
                        font=FONT_BODY, text_color="gray70").pack(pady=2)
            ctk.CTkLabel(info_frame, text="• Connected to the same network", 
                        font=("Roboto", 11), text_color="gray60", anchor="w").pack(pady=1, padx=30, anchor="w")
            ctk.CTkLabel(info_frame, text="• SSH is enabled", 
                        font=("Roboto", 11), text_color="gray60", anchor="w").pack(pady=1, padx=30, anchor="w")
            ctk.CTkLabel(info_frame, text="• Powered on and accessible", 
                        font=("Roboto", 11), text_color="gray60", anchor="w").pack(pady=1, padx=30, anchor="w")
            ctk.CTkLabel(info_frame, text="", font=("Roboto", 5)).pack(pady=5)  # Spacer

    def select_device(self, ip):
        self.manual_ip.delete(0, "end")
        self.manual_ip.insert(0, ip)

    def connect_rpi(self):
        ip = self.manual_ip.get()
        user = self.rpi_user.get()
        pwd = self.rpi_pass.get()
        
        if not all([ip, user, pwd]):
            messagebox.showerror("Error", "Please provide IP, Username and Password")
            return
            
        self.status_label.configure(text="Connecting...", text_color="yellow")
        self.connect_btn.configure(state="disabled")
        
        threading.Thread(target=self.perform_ssh_sync, args=(ip, user, pwd), daemon=True).start()

    def perform_ssh_sync(self, ip, user, pwd):
        client = SSHClient(ip, user, pwd)
        if client.connect():
            self.master.after(0, lambda: self.status_label.configure(text="Syncing code...", text_color="blue"))
            # Sync current directory
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if client.sync_code(current_dir):
                 self.master.after(0, self.rpi_success)
            else:
                 self.master.after(0, lambda: self.rpi_fail("Sync failed"))
            client.close()
        else:
            self.master.after(0, lambda: self.rpi_fail("Connection failed"))

    def rpi_success(self):
        messagebox.showinfo("Success", "RPi Connected and Synced!")
        self.setup_step3_email_ui()

    def rpi_fail(self, msg):
        self.status_label.configure(text=msg, text_color="red")
        self.connect_btn.configure(state="normal")
        messagebox.showerror("Error", msg)

    def setup_step3_email_ui(self):
        self.clear_frame()
        ctk.CTkLabel(self.frame, text="Email Verification", font=FONT_HEADER).pack(pady=(30, 20))
        
        ctk.CTkLabel(self.frame, text=f"Code sent to {self.user_data['gmail']}", font=FONT_BODY).pack(pady=10)
        
        self.code_entry = ctk.CTkEntry(self.frame, placeholder_text="6-Digit Code", width=280, height=40, font=FONT_HEADER, justify="center")
        self.code_entry.pack(pady=20)
        
        ctk.CTkButton(self.frame, text="Verify & Register", width=280, height=40, font=FONT_BODY,
                      command=self.verify_and_register, fg_color=COLOR_SUCCESS, hover_color="green").pack(pady=20)

        # Send email
        threading.Thread(target=self.send_email, daemon=True).start()

    def send_email(self):
        if not self.email_verifier.send_verification_code(self.user_data['gmail']):
            self.master.after(0, lambda: messagebox.showerror("Error", "Failed to send email"))

    def verify_and_register(self):
        code = self.code_entry.get()
        if self.email_verifier.verify_code(self.user_data['gmail'], code):
            # Register in DB
            if database.register_user(self.user_data['name'], self.user_data['username'], 
                                      self.user_data['gmail'], self.user_data['password'], 
                                      self.user_data['rpi_enabled']):
                messagebox.showinfo("Success", "Account created successfully!")
                self.back_callback()
            else:
                messagebox.showerror("Error", "Username already exists")
                self.back_callback() # Or go back to step 1?
        else:
            messagebox.showerror("Error", "Invalid Code")
