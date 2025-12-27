import sqlite3
import hashlib

DB_NAME = "users.db"

def init_db():
    """Initialize the database with the users and notes tables."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            gmail TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            rpi_enabled INTEGER DEFAULT 0,
            rpi_ip TEXT,
            rpi_user TEXT,
            rpi_pass TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()
    migrate_legacy_notes()

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, username, gmail, password, rpi_enabled=0, rpi_ip=None, rpi_user=None, rpi_pass=None):
    """Register a new user. Returns True if successful, False if username exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        password_hash = hash_password(password)
        cursor.execute("INSERT INTO users (name, username, gmail, password_hash, rpi_enabled, rpi_ip, rpi_user, rpi_pass) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                       (name, username, gmail, password_hash, int(rpi_enabled), rpi_ip, rpi_user, rpi_pass))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def user_exists(username):
    """Check if a username already exists in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def update_user_rpi_info(username, rpi_ip, rpi_user, rpi_pass):
    """Update RPI credentials for a user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET rpi_ip = ?, rpi_user = ?, rpi_pass = ? WHERE username = ?", 
                       (rpi_ip, rpi_user, rpi_pass, username))
        conn.commit()
        return True
    except Exception as e:
        print(f"Update RPI info error: {e}")
        return False
    finally:
        conn.close()

def login_user(username, password):
    """Verify user credentials. Returns user info dict if valid, None otherwise."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    password_hash = hash_password(password)
    cursor.execute("SELECT name, username, gmail, rpi_enabled, rpi_ip, rpi_user, rpi_pass FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "name": user[0],
            "username": user[1],
            "gmail": user[2],
            "rpi_enabled": bool(user[3]),
            "rpi_ip": user[4],
            "rpi_user": user[5],
            "rpi_pass": user[6]
        }
    return None

def migrate_legacy_notes():
    """Migrate data from old 'notes' table to 'user_notes' if it exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Check if old table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
    if cursor.fetchone():
        try:
            cursor.execute("SELECT username, content FROM notes")
            old_notes = cursor.fetchall()
            
            for username, content in old_notes:
                if content:
                    # Check if already migrated (avoid duplicates if run multiple times)
                    cursor.execute("SELECT id FROM user_notes WHERE username = ? AND title = 'General'", (username,))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO user_notes (username, title, content) VALUES (?, 'General', ?)", (username, content))
            
            conn.commit()
            # Optionally drop old table, but keeping it for safety for now
            # cursor.execute("DROP TABLE notes") 
        except Exception as e:
            print(f"Migration error: {e}")
            
    conn.close()

# --- Section Based Notes API ---

def get_sections(username):
    """Get all note sections for a user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, updated_at FROM user_notes WHERE username = ? ORDER BY updated_at DESC", (username,))
    sections = cursor.fetchall()
    conn.close()
    return sections

def create_section(username, title):
    """Create a new note section."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_notes (username, title, content) VALUES (?, ?, '')", (username, title))
    conn.commit()
    conn.close()

def delete_section(section_id):
    """Delete a note section."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_notes WHERE id = ?", (section_id,))
    conn.commit()
    conn.close()

def delete_all_sections(username):
    """Delete all note sections for a user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_notes WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def get_section_content(section_id):
    """Get content of a specific section."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM user_notes WHERE id = ?", (section_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else ""

def save_section_content(section_id, content):
    """Save content to a section and update timestamp."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE user_notes SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (content, section_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
