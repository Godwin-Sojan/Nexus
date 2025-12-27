import customtkinter as ctk
from tkinter import messagebox
import database
from config import *

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

        # --- System Monitor Settings ---
        self.sys_lbl = ctk.CTkLabel(self.container, text="System Info Refresh Rate", font=FONT_SUBHEADER)
        self.sys_lbl.pack(pady=(10, 5))
        
        self.refresh_val = ctk.CTkLabel(self.container, text="1.0s", font=FONT_BODY, text_color=COLOR_ACCENT_1)
        self.refresh_val.pack(pady=0)

        self.refresh_slider = ctk.CTkSlider(self.container, from_=0.5, to=5.0, number_of_steps=9, width=300, command=self.update_refresh_rate)
        self.refresh_slider.set(1.0)
        self.refresh_slider.pack(pady=10)

        # --- Manage RPI ---
        self.rpi_lbl = ctk.CTkLabel(self.container, text="Manage RPI", font=FONT_SUBHEADER)
        self.rpi_lbl.pack(pady=(20, 10))

        self.rpi_ip_entry = ctk.CTkEntry(self.container, placeholder_text="RPI IP Address", width=300, height=35, font=FONT_BODY)
        self.rpi_ip_entry.pack(pady=5)

        self.rpi_user_entry = ctk.CTkEntry(self.container, placeholder_text="RPI Username", width=300, height=35, font=FONT_BODY)
        self.rpi_user_entry.pack(pady=5)

        self.rpi_pass_entry = ctk.CTkEntry(self.container, placeholder_text="RPI Password", show="*", width=300, height=35, font=FONT_BODY)
        self.rpi_pass_entry.pack(pady=5)

        self.save_rpi_btn = ctk.CTkButton(self.container, text="Save RPI Config", width=200, height=35, font=FONT_BODY,
                                          fg_color=COLOR_PRIMARY, text_color=COLOR_BG, hover_color=COLOR_SECONDARY,
                                          command=self.save_rpi_config)
        self.save_rpi_btn.pack(pady=10)

        # --- Data Management ---
        self.data_lbl = ctk.CTkLabel(self.container, text="Data Management", font=FONT_SUBHEADER)
        self.data_lbl.pack(pady=(20, 10))

        self.clear_notes_btn = ctk.CTkButton(self.container, text="Clear My Notes", width=200, height=35, font=FONT_BODY,
                                             fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
                                             command=self.clear_notes)
        self.clear_notes_btn.pack(pady=5)

        # --- Account ---
        self.logout_btn = ctk.CTkButton(self.container, text="Logout", width=200, height=35, font=FONT_BODY,
                                        fg_color=COLOR_DANGER, hover_color="#8a1f15",
                                        command=self.logout_callback)
        self.logout_btn.pack(pady=(20, 10))
        
        # --- About ---
        self.about_lbl = ctk.CTkLabel(self.container, text="v1.1 | Developed by Godwin", font=FONT_SMALL, text_color="gray60")
        self.about_lbl.pack(side="bottom", pady=10)

        self.username = None
        self.rpi_update_callback = None

    def set_user_info(self, user_info, rpi_update_callback):
        self.username = user_info.get("username")
        self.rpi_update_callback = rpi_update_callback
        
        self.rpi_ip_entry.delete(0, "end")
        self.rpi_ip_entry.insert(0, user_info.get("rpi_ip") or "")
        
        self.rpi_user_entry.delete(0, "end")
        self.rpi_user_entry.insert(0, user_info.get("rpi_user") or "")
        
        self.rpi_pass_entry.delete(0, "end")
        self.rpi_pass_entry.insert(0, user_info.get("rpi_pass") or "")

    def save_rpi_config(self):
        ip = self.rpi_ip_entry.get()
        user = self.rpi_user_entry.get()
        pwd = self.rpi_pass_entry.get()
        
        if not all([ip, user, pwd]):
            messagebox.showerror("Error", "Please fill all RPI fields")
            return
            
        if database.update_user_rpi_info(self.username, ip, user, pwd):
            messagebox.showinfo("Success", "RPI configuration updated!")
            if self.rpi_update_callback:
                self.rpi_update_callback(ip, user, pwd)
        else:
            messagebox.showerror("Error", "Failed to update RPI configuration")

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
