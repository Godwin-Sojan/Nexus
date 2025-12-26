import google.generativeai as ai
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
        
        self.api_key = GEMINI_API_KEY
        self.is_processing = False
        self.loading_bubble = None
        self.stop_requested = False

        if self.api_key:
            # Configure the API
            ai.configure(api_key=self.api_key)
            # Create a new model
            self.model = ai.GenerativeModel("gemini-2.5-flash")
            self.chat = self.model.start_chat()
            # Initialize conversation history
            self.history = []
        else:
            self.append_message("System", "Please set GEMINI_API_KEY environment variable to use the chatbot.")

    def send_message(self, event=None):
        if self.is_processing:
            return # Block sending while processing
            
        message = self.entry.get()
        if not message or not message.strip():
            return
            
        self.append_message("You", message)
        self.entry.delete(0, "end")
        
        if hasattr(self, 'chat'):
            self.start_loading()
            threading.Thread(target=self.get_response, args=(message,), daemon=True).start()
        else:
            self.append_message("System", "Chatbot not configured (missing API key).")

    def start_loading(self):
        self.is_processing = True
        self.stop_requested = False
        self.send_btn.configure(text="Stop", fg_color=COLOR_DANGER, hover_color="#c93c4e", command=self.stop_processing)
        self.loading_bubble = self.append_message("Gemini", "...")

    def stop_loading(self):
        self.is_processing = False
        self.send_btn.configure(text="Send", fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY, command=self.send_message)
        if self.loading_bubble:
            self.loading_bubble.destroy()
            self.loading_bubble = None

    def stop_processing(self):
        self.stop_requested = True
        self.stop_loading()
        self.append_message("System", "Response stopped by user.")

    def get_response(self, message):
        try:
            # Add user message to conversation history
            self.history.append(f"User: {message}")
            
            # Send the full conversation history to the model
            response = self.chat.send_message('\n'.join(self.history))
            
            if not self.stop_requested:
                # Add AI response to conversation history
                self.history.append(f"Chatbot: {response.text}")
                self.master.after(0, self.finalize_response, response.text)
        except Exception as e:
            if not self.stop_requested:
                self.master.after(0, self.handle_error, str(e))

    def finalize_response(self, text):
        self.stop_loading()
        self.append_message("Gemini", text)

    def handle_error(self, error_text):
        self.stop_loading()
        self.append_message("Error", error_text)

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
        elif sender == "System" or sender == "Error":
            # Center aligned
            color = COLOR_DANGER if sender == "Error" else "gray40"
            bubble = ctk.CTkLabel(bubble_frame, text=text, font=FONT_SMALL, 
                                  fg_color=color, text_color="white",
                                  corner_radius=10, padx=10, pady=5)
            bubble.pack(side="top", pady=5)
        else:
            # Left aligned, Card Color
            bubble = ctk.CTkLabel(bubble_frame, text=text, font=FONT_BODY, 
                                  fg_color=COLOR_ACCENT_3, text_color=COLOR_BG,
                                  corner_radius=15, padx=15, pady=10, wraplength=400, justify="left")
            bubble.pack(side="left", padx=(10, 50))
            
        # Scroll to bottom
        self.chat_scroll.update_idletasks()
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
        
        return bubble_frame # Return frame so it can be destroyed (for loading bubble)

    def scroll_to_bottom(self):
        """Programmatically scroll the chat to the bottom."""
        self.chat_scroll.update_idletasks()
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
