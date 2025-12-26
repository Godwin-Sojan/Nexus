# 🚀 Nexus AI Assistant

A powerful AI-powered system control and monitoring application built with Python and CustomTkinter.

## 🔒 Security Setup (IMPORTANT!)

This project uses environment variables to keep your credentials secure. **Never commit your `.env` file to GitHub!**

### First-Time Setup

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your credentials:**
   ```bash
   nano .env  # or use any text editor
   ```

3. **Get a Gmail App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Enable 2-Step Verification (required)
   - Create a new App Password for "Mail"
   - Copy the 16-character password (remove spaces)
   - Paste it in your `.env` file

4. **Your `.env` should look like:**
   ```env
   GMAIL_SENDER_EMAIL=your_email@gmail.com
   GMAIL_APP_PASSWORD=abcdefghijklmnop
   ```

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd nexus
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (see Security Setup above)

5. **Run the application:**
   ```bash
   python main.py
   ```

## ✨ Features

- 🔐 **Secure Authentication** - Email verification with beautiful HTML emails
- 🤖 **AI Chatbot** - Powered by Google Gemini
- 🖥️ **System Monitor** - Real-time CPU, RAM, GPU, and disk monitoring
- 📝 **Notes** - Organized note-taking with sections
- 🔧 **RPi Integration** - Connect and sync with Raspberry Pi devices
- ⚙️ **Settings** - Customizable preferences

## 📁 Project Structure

```
nexus/
├── main.py              # Application entry point
├── auth.py              # Authentication & registration
├── dashboard.py         # Main dashboard
├── config.py            # Configuration & environment loading
├── database.py          # SQLite database operations
├── email_utils.py       # Email verification system
├── rpi_utils.py         # Raspberry Pi utilities
├── frames/              # UI frames
│   ├── chatbot.py
│   ├── notes.py
│   ├── rpi.py
│   ├── settings.py
│   └── system.py
├── .env                 # YOUR CREDENTIALS (NOT in git)
├── .env.example         # Template for .env
├── .gitignore           # Protects sensitive files
└── requirements.txt     # Python dependencies
```

## 🛡️ Security Features

- ✅ Environment variables for sensitive data
- ✅ `.gitignore` protects `.env` file
- ✅ Gmail App Password support
- ✅ No hardcoded credentials in source code
- ✅ Secure password hashing (bcrypt)
- ✅ One-time verification codes

## 🤝 Contributing

When contributing:
1. **NEVER** commit your `.env` file
2. **NEVER** hardcode credentials
3. Always use environment variables for sensitive data
4. Update `.env.example` if adding new environment variables

## 📝 License

This project is for educational purposes.

---

**⚠️ SECURITY REMINDER:** Always keep your `.env` file private and never share your Gmail App Password!
