import customtkinter as ctk
from tkinter import messagebox
import database
from config import *
from frames.rpi_management import RPIManagementWindow

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, logout_callback, system_frame, notes_frame):
        super().__init__(master, fg_color="transparent")
        self.logout_callback = logout_callback
        self.system_frame = system_frame
        self.notes_frame = notes_frame
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, width=600, height=500, corner_radius=20, fg_color=COLOR_CARD)
        self.container.grid(row=0, column=0)
        self.container.grid_propagate(False)

        self.header = ctk.CTkLabel(self.container, text="Settings", font=FONT_HEADER)
        self.header.pack(pady=(30, 20))

        self.sys_lbl = ctk.CTkLabel(self.container, text="System Info Refresh Rate", font=FONT_SUBHEADER)
        self.sys_lbl.pack(pady=(10, 5))
        
        self.refresh_val = ctk.CTkLabel(self.container, text="1.0s", font=FONT_BODY, text_color=COLOR_ACCENT_1)
        self.refresh_val.pack(pady=0)

        self.refresh_slider = ctk.CTkSlider(self.container, from_=0.5, to=5.0, number_of_steps=9, width=300, command=self.update_refresh_rate)
        self.refresh_slider.set(1.0)
        self.refresh_slider.pack(pady=10)

        self.rpi_lbl = ctk.CTkLabel(self.container, text="Manage RPI", font=FONT_SUBHEADER)
        self.rpi_lbl.pack(pady=(20, 10))

        self.manage_rpi_btn = ctk.CTkButton(self.container, text="Open RPI Settings", width=250, height=45, font=FONT_BODY,
                                            fg_color=COLOR_PRIMARY, text_color=COLOR_BG, hover_color=COLOR_SECONDARY,
                                            command=self.open_rpi_management)
        self.manage_rpi_btn.pack(pady=10)

        self.data_lbl = ctk.CTkLabel(self.container, text="Data Management", font=FONT_SUBHEADER)
        self.data_lbl.pack(pady=(20, 10))

        self.clear_notes_btn = ctk.CTkButton(self.container, text="Clear My Notes", width=200, height=35, font=FONT_BODY,
                                             fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
                                             command=self.clear_notes)
        self.clear_notes_btn.pack(pady=5)

        self.logout_btn = ctk.CTkButton(self.container, text="Logout", width=200, height=35, font=FONT_BODY,
                                        fg_color=COLOR_DANGER, hover_color="#8a1f15",
                                        command=self.logout_callback)
        self.logout_btn.pack(pady=(20, 10))
        
        self.about_lbl = ctk.CTkLabel(self.container, text="v1.1 | Developed by Godwin", font=FONT_SMALL, text_color="gray60")
        self.about_lbl.pack(side="bottom", pady=10)

        self.username = None
        self.rpi_update_callback = None

    def set_user_info(self, user_info, rpi_update_callback):
        self.username = user_info.get("username")
        self.rpi_update_callback = rpi_update_callback
        self.user_info = user_info # Store for later use in management window

    def open_rpi_management(self):
        if not self.username:
            return
            
        RPIManagementWindow(
            self, 
            self.username,
            self.user_info.get("rpi_ip") or "",
            self.user_info.get("rpi_user") or "",
            self.user_info.get("rpi_pass") or "",
            self.user_info.get("rpi_port") or 5000,
            self.rpi_update_callback
        )


    def update_refresh_rate(self, value):
        self.refresh_val.configure(text=f"{value:.1f}s")
        if self.system_frame:
            self.system_frame.set_refresh_rate(value)

    def clear_notes(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all your notes? This cannot be undone."):
            if self.notes_frame and self.notes_frame.username:
                database.delete_all_sections(self.notes_frame.username)
                self.notes_frame.load_sections() # Reload to update UI
                messagebox.showinfo("Success", "Notes cleared.")
