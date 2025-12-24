import customtkinter as ctk
import os
from google import genai
import threading
from config import *

class ChatbotFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Chat History (Scrollable Frame for Bubbles)
        self.chat_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_scroll.grid(row=0, column=0, padx=20, pady=(20, 20), sticky="nsew")
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=40, pady=(0, 40), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Ask Gemini something...", height=50, font=FONT_BODY, corner_radius=25)
        self.entry.grid(row=0, column=0, padx=(0, 15), sticky="ew")
        self.entry.bind("<Return>", self.send_message)

        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", width=120, height=50, corner_radius=25, font=FONT_BODY,
                                      fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY,
                                      command=self.send_message)
        self.send_btn.grid(row=0, column=1)
        
        self.api_key = os.getenv("GOOGLE_API_KEY") 
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.chat = self.client.chats.create(model='gemini-2.0-flash')
        else:
            self.append_message("System", "Please set GOOGLE_API_KEY environment variable to use the chatbot.")

    def send_message(self, event=None):
        message = self.entry.get()
        if not message or not message.strip():
            return
        self.append_message("You", message)
        self.entry.delete(0, "end")
        if hasattr(self, 'chat'):
            threading.Thread(target=self.get_response, args=(message,)).start()
        else:
            self.append_message("System", "Chatbot not configured (missing API key).")

    def get_response(self, message):
        try:
            response = self.chat.send_message(message)
            self.master.after(0, self.append_message, "Gemini", response.text)
        except Exception as e:
            self.master.after(0, self.append_message, "Error", str(e))

    def append_message(self, sender, text):
        # Create Bubble Frame
        bubble_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        bubble_frame.pack(fill="x", pady=5)
        
        if sender == "You":
            # Right aligned, Primary Color
            bubble = ctk.CTkLabel(bubble_frame, text=text, font=FONT_BODY, 
                                  fg_color=COLOR_PRIMARY, text_color=COLOR_BG,
                                  corner_radius=15, padx=15, pady=10, wraplength=400, justify="left")
            bubble.pack(side="right", padx=(50, 10))
        else:
            # Left aligned, Card Color
            bubble = ctk.CTkLabel(bubble_frame, text=text, font=FONT_BODY, 
                                  fg_color=COLOR_ACCENT_3, text_color=COLOR_BG,
                                  corner_radius=15, padx=15, pady=10, wraplength=400, justify="left")
            bubble.pack(side="left", padx=(10, 50))
            
        # Scroll to bottom
        # We need to update idletasks to ensure the frame size is calculated
        self.chat_scroll.update_idletasks()
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
