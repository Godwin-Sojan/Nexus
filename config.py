import customtkinter as ctk
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    
    # Get the directory where this config.py file is located
    BASE_DIR = Path(__file__).resolve().parent
    ENV_FILE = BASE_DIR / '.env'
    
    # Load .env file
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
        print("✅ Environment variables loaded successfully")
    else:
        print("⚠️  WARNING: .env file not found!")
        print(f"   Expected location: {ENV_FILE}")
        print("   Please copy .env.example to .env and add your credentials")
except ImportError:
    print("⚠️  WARNING: python-dotenv not installed!")
    print("   Install it with: pip install python-dotenv")

# --- Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("./theme.json")

# Custom Colors
COLOR_PRIMARY = "#B4BEFE" # Lavender/Soft Blue
COLOR_SECONDARY = "#CBA6F7" # Mauve
COLOR_BG = "#1E1E2E" # Dark Base
COLOR_CARD = "#313244" # Surface
COLOR_SIDEBAR = "#11111B" # Darker Sidebar
COLOR_TEXT = "#CDD6F4" # Text
COLOR_DANGER = "#F38BA8" # Soft Red
COLOR_SUCCESS = "#A6E3A1" # Soft Green
COLOR_ACCENT_1 = "#F38BA8" # CPU - Soft Red
COLOR_ACCENT_2 = "#FAB387" # RAM - Peach
COLOR_ACCENT_3 = "#89DCEB" # Disk - Sky Blue
COLOR_ACCENT_4 = "#A6E3A1" # GPU - Soft Green

# Fonts
FONT_HEADER = ("Poppins Medium", 24)
FONT_SUBHEADER = ("Poppins Medium", 18)
FONT_BODY = ("Poppins", 14)
FONT_MONO = ("Roboto Mono", 13) # Keep Mono for RPi/Code
FONT_SMALL = ("Poppins", 12)

# Optional: Gemini API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
