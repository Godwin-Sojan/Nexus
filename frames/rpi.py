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

        # Chat History (Scrollable Frame for Bubbles)
        self.header_label = ctk.CTkLabel(self, text="Control your RPI here", font=FONT_HEADER)
        self.header_label.grid(row=0, column=0, pady=(20, 10))
        
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

        # RPi Connection
        self.rpi_ip = "192.168.31.230"
        self.rpi_port = 5000
        self.socket = None
        self.connected = False
        
        # Start connection in a separate thread to not block UI
        threading.Thread(target=self.connect_to_rpi, daemon=True).start()

    def connect_to_rpi(self):
        self.append_message("System", f"Connecting to {self.rpi_ip}:{self.rpi_port}...")
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.rpi_ip, self.rpi_port))
            self.connected = True
            self.master.after(0, self.append_message, "System", "Connected to RPi!")
            
            # Start listening thread
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            self.master.after(0, self.append_message, "Error", f"Connection failed: {e}")
            self.connected = False

    def receive_messages(self):
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                self.master.after(0, self.append_message, "RPi", data)
            except Exception as e:
                self.master.after(0, self.append_message, "Error", f"Connection lost: {e}")
                self.connected = False
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
        # Create Bubble Frame
        bubble_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        bubble_frame.pack(fill="x", pady=5)
        
        if sender == "User":
            # Right aligned, Primary Color
            bubble = ctk.CTkLabel(bubble_frame, text=text, font=FONT_MONO, 
                                  fg_color=COLOR_PRIMARY, text_color=COLOR_BG,
                                  corner_radius=15, padx=15, pady=10, wraplength=400, justify="left")
            bubble.pack(side="right", padx=(50, 10))
        elif sender == "System" or sender == "Error":
             # Center aligned, Gray/Red
            color = "#e74c3c" if sender == "Error" else "#95a5a6"
            bubble = ctk.CTkLabel(bubble_frame, text=text, font=FONT_BODY, 
                                  fg_color=color, text_color="white",
                                  corner_radius=10, padx=10, pady=5, wraplength=400, justify="center")
            bubble.pack(side="top", pady=5)
        else:
            # Left aligned, Card Color, Monospace
            bubble = ctk.CTkLabel(bubble_frame, text=text, font=FONT_MONO, 
                                  fg_color=COLOR_ACCENT_3, text_color=COLOR_BG,
                                  corner_radius=15, padx=15, pady=10, wraplength=400, justify="left")
            bubble.pack(side="left", padx=(10, 50))
            
        # Scroll to bottom
        self.chat_scroll.update_idletasks()
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
