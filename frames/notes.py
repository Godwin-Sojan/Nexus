import customtkinter as ctk
from tkinter import messagebox
import database
from config import *

import json

class NotesFrame(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master, fg_color="transparent")
        self.app_instance = app_instance
        self.username = None
        self.current_section_id = None
        self.dirty = False
        self.current_font_size = "14"
        
        # Grid Layout: Left Sidebar (Sections) | Right Main (Editor)
        self.grid_columnconfigure(0, weight=1) # Sidebar
        self.grid_columnconfigure(1, weight=3) # Main
        self.grid_rowconfigure(0, weight=1)

        # --- Left Sidebar: Sections ---
        self.left_panel = ctk.CTkFrame(self, corner_radius=20, fg_color=COLOR_SIDEBAR)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)

        self.sections_label = ctk.CTkLabel(self.left_panel, text="Sections", font=FONT_SUBHEADER)
        self.sections_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.sections_scroll = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.sections_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.add_section_btn = ctk.CTkButton(self.left_panel, text="+ Add Section", height=40, font=FONT_BODY,
                                             fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY,
                                             text_color=COLOR_BG,
                                             command=self.add_section_dialog)
        self.add_section_btn.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        # --- Right Main: Editor ---
        self.right_panel = ctk.CTkFrame(self, corner_radius=20, fg_color=COLOR_CARD)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        # Header Area
        self.header_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        self.note_title = ctk.CTkLabel(self.header_frame, text="Select a Section", font=FONT_HEADER, anchor="w")
        self.note_title.pack(side="left", fill="x", expand=True)
        
        self.last_updated = ctk.CTkLabel(self.header_frame, text="", font=FONT_SMALL, text_color="gray60")
        self.last_updated.pack(side="right")

        # Editor
        self.textbox = ctk.CTkTextbox(self.right_panel, font=FONT_BODY, corner_radius=15, fg_color=COLOR_BG)
        self.textbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.textbox.bind("<<Modified>>", self.on_modify)
        self.textbox.bind("<Key>", self.on_key_press)
        
        # Initialize font tags
        self.font_sizes = ["12", "14", "16", "18", "20", "24", "32"]
        for size in self.font_sizes:
            self.textbox._textbox.tag_config(f"font_{size}", font=("Roboto", int(size)))

        # Toolbar (Bottom)
        self.toolbar = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.toolbar.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        
        self.font_size_lbl = ctk.CTkLabel(self.toolbar, text="Font Size:", font=FONT_SMALL)
        self.font_size_lbl.pack(side="left", padx=(0, 10))
        
        self.font_combo = ctk.CTkComboBox(self.toolbar, values=self.font_sizes, width=80, command=self.change_font_size)
        self.font_combo.set("14")
        self.font_combo.pack(side="left")
        
        self.delete_section_btn = ctk.CTkButton(self.toolbar, text="Delete Section", width=120, height=30, font=FONT_SMALL,
                                                fg_color=COLOR_DANGER, hover_color="#c93c4e",
                                                command=self.delete_current_section)
        self.delete_section_btn.pack(side="right")
        
        # Save button removed for auto-save

    def set_user(self, username):
        self.username = username
        self.load_sections()

    def load_sections(self):
        # Clear existing buttons
        for widget in self.sections_scroll.winfo_children():
            widget.destroy()
            
        if not self.username:
            return

        sections = database.get_sections(self.username)
        
        if not sections:
            # Create default if none exist
            database.create_section(self.username, "General")
            sections = database.get_sections(self.username)

        for sec_id, title, updated in sections:
            btn = ctk.CTkButton(self.sections_scroll, text=title, height=40, corner_radius=10,
                                fg_color="transparent", hover_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD,
                                anchor="w", command=lambda i=sec_id, t=title, u=updated: self.load_note_content(i, t, u))
            btn.pack(fill="x", pady=5)
            
        # Load first section by default if nothing selected
        if sections and not self.current_section_id:
            self.load_note_content(sections[0][0], sections[0][1], sections[0][2])

    def load_note_content(self, section_id, title, updated_at):
        if self.dirty:
            self.save_state()
            
        self.current_section_id = section_id
        self.note_title.configure(text=title)
        self.last_updated.configure(text=f"Last Updated: {updated_at}")
        
        content = database.get_section_content(section_id)
        self.textbox.delete("0.0", "end")
        
        # Try to deserialize as JSON (Rich Text)
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "content" in data and "tags" in data:
                self.textbox.insert("0.0", data["content"])
                # Apply tags
                for tag_name, ranges in data["tags"].items():
                    for start, end in ranges:
                        self.textbox._textbox.tag_add(tag_name, start, end)
            else:
                # Fallback for plain text or legacy format
                self.textbox.insert("0.0", content)
        except (json.JSONDecodeError, TypeError):
            # Not JSON, treat as plain text
            self.textbox.insert("0.0", content)
            
        self.textbox.edit_modified(False)
        self.dirty = False
        
        # Highlight active section button
        for widget in self.sections_scroll.winfo_children():
            if widget.cget("text") == title:
                widget.configure(fg_color=COLOR_PRIMARY, text_color=COLOR_BG)
            else:
                widget.configure(fg_color="transparent", text_color=COLOR_TEXT)

    def add_section_dialog(self):
        if self.dirty:
            self.save_state()
        dialog = ctk.CTkInputDialog(text="Enter Section Name:", title="New Section")
        name = dialog.get_input()
        if name:
            database.create_section(self.username, name)
            self.load_sections()

    def delete_current_section(self):
        if not self.current_section_id:
            return
            
        if messagebox.askyesno("Delete Section", "Are you sure? This will delete the section and all its contents."):
            database.delete_section(self.current_section_id)
            self.current_section_id = None
            self.load_sections()

    def change_font_size(self, value):
        self.current_font_size = value
        
        # Check if text is selected
        try:
            if self.textbox._textbox.tag_ranges("sel"):
                # Apply tag to selection
                self.textbox._textbox.tag_add(f"font_{value}", "sel.first", "sel.last")
                # Remove other font tags from selection to avoid conflicts
                for size in self.font_sizes:
                    if size != value:
                        self.textbox._textbox.tag_remove(f"font_{size}", "sel.first", "sel.last")
            
            # Also trigger dirty state
            self.dirty = True
        except Exception:
            pass
            
        # Set focus back to textbox so typing continues with new font
        self.textbox.focus_set()

    def on_key_press(self, event):
        self.after(1, self.apply_font_to_last_char)

    def apply_font_to_last_char(self):
        # Apply current font tag to the character before 'insert'
        try:
            self.textbox._textbox.tag_add(f"font_{self.current_font_size}", "insert-1c", "insert")
            
            # Remove conflicting tags
            for size in self.font_sizes:
                if size != self.current_font_size:
                    self.textbox._textbox.tag_remove(f"font_{size}", "insert-1c", "insert")
        except Exception:
            pass

    def on_modify(self, event=None):
        if self.textbox.edit_modified():
            self.dirty = True
            self.textbox.edit_modified(False)

    def is_dirty(self):
        return self.dirty

    def save_state(self):
        """Auto-save the current note state."""
        if self.username and self.current_section_id and self.dirty:
            # Serialize content and tags
            text_content = self.textbox.get("0.0", "end-1c") # -1c to remove trailing newline added by Text widget
            tags_data = {}
            
            for size in self.font_sizes:
                tag_name = f"font_{size}"
                ranges = self.textbox._textbox.tag_ranges(tag_name)
                # ranges is a flat tuple (start1, end1, start2, end2, ...)
                # Convert to list of pairs
                if ranges:
                    pairs = []
                    for i in range(0, len(ranges), 2):
                        pairs.append((str(ranges[i]), str(ranges[i+1])))
                    tags_data[tag_name] = pairs
            
            data = {
                "content": text_content,
                "tags": tags_data
            }
            
            serialized_content = json.dumps(data)
            database.save_section_content(self.current_section_id, serialized_content)
            self.dirty = False
            
            # Update timestamp in UI
            import datetime
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_updated.configure(text=f"Last Updated: {now}")

    def load_notes(self):
        # Wrapper for compatibility with dashboard call
        self.load_sections()
