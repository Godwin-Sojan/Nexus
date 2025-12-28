import customtkinter as ctk
from tkinter import messagebox
from config import *
from frames.chatbot import ChatbotFrame
from frames.rpi import RPIFrame
from frames.notes import NotesFrame
from frames.system import SystemFrame
from frames.settings import SettingsFrame

class MainView(ctk.CTkFrame):
    def __init__(self, master, logout_callback):
        super().__init__(master)
        self.logout_callback = logout_callback

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="AI CONTROL", font=FONT_HEADER)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(40, 30))

        self.chatbot_btn = self.create_nav_btn("CHATBOT", self.show_chatbot, 1)
        self.rpi_btn = self.create_nav_btn("RPI CONTROL", self.show_rpi, 2)
        self.notes_btn = self.create_nav_btn("MY NOTES", self.show_notes, 3)
        self.system_btn = self.create_nav_btn("SYSTEM INFO", self.show_system, 4)
        self.settings_btn = self.create_nav_btn("SETTINGS", self.show_settings, 5)

        # Account Section
        self.account_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.account_frame.grid(row=7, column=0, padx=20, pady=30, sticky="s")
        
        self.account_icon = ctk.CTkLabel(self.account_frame, text="👤", font=("Arial", 36))
        self.account_icon.pack()
        
        self.account_name = ctk.CTkLabel(self.account_frame, text="User", font=FONT_SUBHEADER)
        self.account_name.pack(pady=5)

        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.chatbot_frame = ChatbotFrame(self.content_area)
        self.rpi_frame = RPIFrame(self.content_area)
        self.notes_frame = NotesFrame(self.content_area, self.master)
        self.system_frame = SystemFrame(self.content_area)
        self.settings_frame = SettingsFrame(self.content_area, self.logout_callback, self.system_frame, self.notes_frame)

        self.frames = [self.chatbot_frame, self.rpi_frame, self.notes_frame, self.system_frame, self.settings_frame]
        self.buttons = [self.chatbot_btn, self.rpi_btn, self.notes_btn, self.system_btn, self.settings_btn]

        self.current_frame = None
        self.show_chatbot()

    def create_nav_btn(self, text, command, row):
        btn = ctk.CTkButton(self.sidebar, text=text, height=50, corner_radius=20, font=FONT_BODY,
                            fg_color="transparent", hover_color=COLOR_SECONDARY,
                            anchor="w", command=command)
        btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
        return btn

    def set_user(self, user_info):
        # user_info is a dict: {"name": ..., "username": ..., "gmail": ..., "rpi_enabled": ...}
        username = user_info.get("username", "User")
        self.account_name.configure(text=username)
        self.notes_frame.set_user(username)
        self.settings_frame.set_user_info(user_info, self.update_rpi_info)
        
        if not user_info.get("rpi_enabled", False):
            self.rpi_btn.configure(state="disabled", fg_color="transparent", text_color="gray50")
        else:
            self.rpi_btn.configure(state="normal", text_color=COLOR_TEXT)
            self.rpi_frame.set_rpi_info(
                user_info.get("rpi_ip"),
                user_info.get("rpi_user"),
                user_info.get("rpi_pass"),
                user_info.get("rpi_port")
            )

    def update_rpi_info(self, ip, user, pwd, port):
        """Callback from settings to update RPI info in the current session."""
        self.rpi_frame.set_rpi_info(ip, user, pwd, port)

    def switch_frame(self, frame_to_show, active_btn):
        # Auto-save previous frame if supported
        if self.current_frame and hasattr(self.current_frame, 'save_state'):
            self.current_frame.save_state()

        if self.current_frame == frame_to_show:
            return

        # Update buttons
        for btn in self.buttons:
            btn.configure(fg_color="transparent", text_color=COLOR_TEXT)
        active_btn.configure(fg_color=COLOR_PRIMARY, text_color=COLOR_BG)

        # Animation Setup
        # 1. Remove old frame immediately (or keep for overlap, but immediate is safer for performance)
        if self.current_frame:
            self.current_frame.place_forget() # Use place_forget since we are switching to place()
            self.current_frame.grid_forget() # Just in case mixed

        self.current_frame = frame_to_show
        self.content_area.grid_propagate(False) 
        self.animate_slide_in(frame_to_show, 1.0)

    def animate_slide_in(self, frame, relx):
        if relx <= 0:
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            return
            
        # Move frame
        frame.place(relx=relx, rely=0, relwidth=1, relheight=1)
        
        # Next step (Linear interpolation)
        # Decrease relx. Speed depends on step size.
        # 0.08 is fast enough.
        new_relx = relx - 0.05
        
        if new_relx < 0:
            new_relx = 0
            
        self.after(10, self.animate_slide_in, frame, new_relx)

    def show_chatbot(self):
        self.switch_frame(self.chatbot_frame, self.chatbot_btn)
        self.chatbot_frame.scroll_to_bottom()

    def show_rpi(self):
        self.switch_frame(self.rpi_frame, self.rpi_btn)

    def show_notes(self):
        self.switch_frame(self.notes_frame, self.notes_btn)
        self.notes_frame.load_notes()

    def show_system(self):
        self.switch_frame(self.system_frame, self.system_btn)

    def show_settings(self):
        self.switch_frame(self.settings_frame, self.settings_btn)
