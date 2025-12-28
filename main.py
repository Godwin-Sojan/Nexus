import customtkinter as ctk
import database
from config import *
from auth import LoginFrame, RegisterFrame
from dashboard import MainView

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        database.init_db()

        try:
            ctk.FontManager.load_font("assets/fonts/Poppins-Regular.ttf")
            ctk.FontManager.load_font("assets/fonts/Poppins-Bold.ttf")
            ctk.FontManager.load_font("assets/fonts/Poppins-Medium.ttf")
        except Exception as e:
            print(f"Error loading fonts: {e}")

        self.title("AI Assistant & System Control")
        self.geometry("1100x700")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.current_user = None

        self.login_frame = LoginFrame(self, self.login_success)
        self.register_frame = RegisterFrame(self, self.show_login)
        self.main_view = MainView(self, self.logout)

        self.show_login()

    def show_login(self):
        self.register_frame.grid_forget()
        self.main_view.grid_forget()
        self.login_frame.grid(row=0, column=0, sticky="nsew")

    def show_register(self):
        self.login_frame.grid_forget()
        self.register_frame.grid(row=0, column=0, sticky="nsew")

    def login_success(self, user_info):
        self.current_user = user_info
        self.login_frame.grid_forget()
        self.main_view.set_user(user_info)
        self.main_view.grid(row=0, column=0, sticky="nsew")

    def logout(self):
        self.current_user = None
        self.main_view.grid_forget()
        self.show_login()

if __name__ == "__main__":
    app = App()
    app.mainloop()
