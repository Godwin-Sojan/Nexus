# Nexus `v1.0`

> [!NOTE]
> **Status:** Work in Progress 🛠️

Nexus is a powerful, all-in-one desktop utility designed to streamline your workflow by combining AI assistance, comprehensive system monitoring, and remote hardware control into a single, sleek interface.

## What is Nexus?

Nexus is built to be the central hub for your computing needs. Whether you're a developer, a power user, or someone who just wants better control over their system, Nexus provides the tools you need in a modern, intuitive environment.

## Key Features

- 🤖 **AI Assistant:** Integrated with Google Gemini for intelligent chat and task assistance.
- 📊 **System Monitor:** Real-time tracking of CPU, RAM, GPU, and Disk usage with beautiful visualizations.
- 🌐 **Raspberry Pi Control:** Remote management and monitoring of your RPi devices.
- 📝 **Smart Notes:** A built-in note-taking application to keep your thoughts organized.
- 🔐 **Secure Auth:** A robust user authentication system with email verification.
- 🎨 **Modern UI:** Built with CustomTkinter for a premium, responsive look and feel.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Godwin-Sojan/Nexus.git
   cd Nexus
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration:**
   - Create a `.env` file based on the provided template.
   - Add your Gemini API key as `GEMINI_API_KEY=KEY`

## Usage

Run the application using:
```bash
python main.py
```

---
*Developed with ❤️ by Godwin*
