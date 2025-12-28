import customtkinter as ctk
from config import *
import socket
import threading
import time

class RPIFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Expand row 1 (Chat Scroll), not row 0 (Header)

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(self.header_frame, text="Control your RPI here", font=FONT_HEADER)
        self.header_label.grid(row=0, column=0, padx=(140, 0))
        
        self.connection_btn = ctk.CTkButton(self.header_frame, text="Connecting...", width=140, height=30, 
                                            fg_color=COLOR_CARD, hover_color=COLOR_PRIMARY,
                                            command=self.toggle_connection, state="disabled")
        self.connection_btn.grid(row=0, column=1, padx=20)
        
        self.chat_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_scroll.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=40, pady=(0, 40), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Enter command...", height=50, font=FONT_MONO, corner_radius=25)
        self.entry.grid(row=0, column=0, padx=(0, 15), sticky="ew")
        self.entry.bind("<Return>", self.send_message)

        self.send_btn = ctk.CTkButton(self.input_frame, text="Execute", width=120, height=50, corner_radius=25, font=FONT_BODY,
                                      fg_color=COLOR_SUCCESS, hover_color="#1e5c29",
                                      command=self.send_message)
        self.send_btn.grid(row=0, column=1)

        self.rpi_ip = None
        self.rpi_user = None
        self.rpi_pass = None
        self.rpi_port = 5000
        self.socket = None
        self.connected = False
        
    def set_rpi_info(self, ip, user=None, pwd=None, port=5000):
        """Set RPI info and attempt connection if not already connected."""
        if not ip:
            return
            
        self.rpi_ip = ip
        self.rpi_user = user
        self.rpi_pass = pwd
        self.rpi_port = port or 5000

        if self.connected:
            return # Already connected
            
        # Start connection in a separate thread
        threading.Thread(target=self.connect_to_rpi, daemon=True).start()

    def toggle_connection(self):
        if self.connected:
            self.show_disconnect_popup()
        else:
            self.append_message("System", "Connecting...")
            threading.Thread(target=self.connect_to_rpi, daemon=True).start()

    def show_disconnect_popup(self):
        self.popup = ctk.CTkToplevel(self)
        self.popup.title("Confirm Disconnect")
        self.popup.geometry("400x200")
        self.popup.attributes("-topmost", True)
        self.popup.wait_visibility()
        self.popup.grab_set()
        
        self.popup.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (self.popup.winfo_width() // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (self.popup.winfo_height() // 2)
        self.popup.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(self.popup, text="Are you sure you want to disconnect?", font=FONT_SUBHEADER)
        label.pack(pady=30)

        btn_frame = ctk.CTkFrame(self.popup, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.confirm_btn = ctk.CTkButton(btn_frame, text="YES (5)", width=100, state="disabled",
                                         fg_color=COLOR_DANGER, hover_color="#8a1f15",
                                         command=self.confirm_disconnect)
        self.confirm_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(btn_frame, text="NO", width=100,
                                   fg_color=COLOR_CARD, hover_color=COLOR_PRIMARY,
                                   command=self.popup.destroy)
        cancel_btn.pack(side="left", padx=10)

        self.countdown = 5
        self.update_countdown()

    def update_countdown(self):
        if not self.popup.winfo_exists():
            return
            
        if self.countdown > 0:
            self.confirm_btn.configure(text=f"YES ({self.countdown})")
            self.countdown -= 1
            self.after(1000, self.update_countdown)
        else:
            self.confirm_btn.configure(text="YES", state="normal")

    def confirm_disconnect(self):
        self.popup.destroy()
        self.disconnect_rpi()

    def disconnect_rpi(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        self.socket = None
        self.update_ui_state()
        self.append_message("System", "Disconnected from RPi.")

    def update_ui_state(self):
        if self.connected:
            self.connection_btn.configure(text="Disconnect", fg_color=COLOR_DANGER, state="normal")
            self.entry.configure(state="normal", placeholder_text="Enter command...")
            self.send_btn.configure(state="normal")
        else:
            self.connection_btn.configure(text="Connect", fg_color=COLOR_SUCCESS, state="normal")
            self.entry.configure(state="disabled", placeholder_text="Disconnected - Click Connect to start")
            self.send_btn.configure(state="disabled")

    def connect_to_rpi(self):
        self.master.after(0, lambda: self.connection_btn.configure(state="disabled", text="Connecting..."))
        self.append_message("System", f"Connecting to {self.rpi_ip}:{self.rpi_port}...")
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.rpi_ip, self.rpi_port))
            self.socket.settimeout(None) # Remove timeout after connection
            self.connected = True
            self.master.after(0, self.append_message, "System", "Connected to RPi!")
            self.master.after(0, self.update_ui_state)
            
            # Start listening thread
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.master.after(0, self.append_message, "Error", f"Connection failed: {e}")
            self.connected = False
            self.master.after(0, self.update_ui_state)

    def receive_messages(self):
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                self.master.after(0, self.append_message, "RPi", data)
            except Exception as e:
                if self.connected: # Only show error if we didn't manually disconnect
                    self.master.after(0, self.append_message, "Error", f"Connection lost: {e}")
                    self.connected = False
                    self.master.after(0, self.update_ui_state)
                break

    def send_message(self, event=None):
        message = self.entry.get()
        if not message or not message.strip():
            return
            
        self.append_message("User", message)
        self.entry.delete(0, "end")
        
        if self.connected and self.socket:
            try:
                self.socket.send(message.encode('utf-8'))
            except Exception as e:
                self.append_message("Error", f"Failed to send: {e}")
        else:
            self.append_message("System", "Not connected to RPi.")

    def append_message(self, sender, text):
        bubble_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        bubble_frame.pack(fill="x", pady=5)
        
        if sender == "User":
            bubble = ctk.CTkLabel(bubble_frame, text=text, font=FONT_MONO, 
                                  fg_color=COLOR_PRIMARY, text_color=COLOR_BG,
                                  corner_radius=15, padx=15, pady=10, wraplength=400, justify="left")
            bubble.pack(side="right", padx=(50, 10))
        elif sender == "System" or sender == "Error":
            color = "#e74c3c" if sender == "Error" else "#95a5a6"
            bubble = ctk.CTkLabel(bubble_frame, text=text, font=FONT_BODY, 
                                  fg_color=color, text_color="white",
                                  corner_radius=10, padx=10, pady=5, wraplength=400, justify="center")
            bubble.pack(side="top", pady=5)
        else:
            bubble = ctk.CTkLabel(bubble_frame, text=text, font=FONT_MONO, 
                                  fg_color=COLOR_ACCENT_3, text_color=COLOR_BG,
                                  corner_radius=15, padx=15, pady=10, wraplength=400, justify="left")
            bubble.pack(side="left", padx=(10, 50))
            
        self.chat_scroll.update_idletasks()
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
