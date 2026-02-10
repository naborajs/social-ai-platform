import sqlite3
import bcrypt
import json
from app.core.config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    whatsapp_id TEXT,
                    telegram_id TEXT,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    recovery_key TEXT,
                    gemini_api_key TEXT,
                    display_name TEXT,
                    avatar_url TEXT,
                    bio TEXT
                )''')
    
    # Conversations table (linked to user)
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')

    # User States table (for conversational flow)
    c.execute('''CREATE TABLE IF NOT EXISTS user_states (
                    platform_id TEXT PRIMARY KEY,
                    platform TEXT,
                    state TEXT,
                    data TEXT
                )''')
    
    # Migrations
    columns = [
        ("last_seen", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
        ("recovery_key", "TEXT"),
        ("email", "TEXT UNIQUE"),
        ("gemini_api_key", "TEXT"),
        ("display_name", "TEXT"),
        ("avatar_url", "TEXT"),
        ("bio", "TEXT"),
        ("system_prompt", "TEXT")
    ]
    
    for col_name, col_type in columns:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass # Column likely exists

    conn.commit()
    conn.close()

def register_user(username, email, password, platform=None, platform_id=None, avatar_url=None, bio=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    import secrets
    recovery_key = secrets.token_hex(8)
    
    try:
        hashed = bcrypt.hash(password)
        c.execute("INSERT INTO users (username, email, password_hash, recovery_key, avatar_url, bio) VALUES (?, ?, ?, ?, ?, ?)", 
                  (username, email, hashed, recovery_key, avatar_url, bio))
        user_id = c.lastrowid
        
        if platform == "whatsapp":
             c.execute("UPDATE users SET whatsapp_id = ? WHERE id = ?", (platform_id, user_id))
        elif platform == "telegram":
             c.execute("UPDATE users SET telegram_id = ? WHERE id = ?", (platform_id, user_id))
             
        conn.commit()
        return True, f"✅ Registration successful!\nEmail: {email}\n🔑 **Backup Key**: `{recovery_key}`\n(Save this! Use `/recover <key> <new_pass>` if you forget your password.)"
    except sqlite3.IntegrityError as e:
        if "users.username" in str(e):
             return False, "❌ Username already exists."
        elif "users.email" in str(e):
             return False, "❌ Email already registered."
        return False, f"❌ Registration failed: Duplicate entry."
    except Exception as e:
        return False, f"❌ Error: {e}"
    finally:
        conn.close()

def update_system_prompt(user_id, system_prompt):
    """Update the user's custom system prompt (persona)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("UPDATE users SET system_prompt = ? WHERE id = ?", (system_prompt, user_id))
        conn.commit()
        return True, "✅ Persona updated successfully!"
    except Exception as e:
        return False, f"❌ Error updating persona: {e}"
    finally:
        conn.close()

def get_user_system_prompt(user_id):
    """Retrieve the user's custom system prompt."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT system_prompt FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Updated get_user_by_platform to return system_prompt
def get_user_by_platform(platform, platform_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if platform == "whatsapp":
        c.execute("SELECT id, username, gemini_api_key, system_prompt FROM users WHERE whatsapp_id = ?", (platform_id,))
    elif platform == "telegram":
        c.execute("SELECT id, username, gemini_api_key, system_prompt FROM users WHERE telegram_id = ?", (platform_id,))
    user = c.fetchone()
    conn.close()
    return user # Returns (id, username, gemini_api_key, system_prompt)

def verify_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user and bcrypt.verify(password, user[1]):
        return user[0] # Return user_id
    return None

def update_platform_id(user_id, platform, platform_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if platform == "whatsapp":
        c.execute("UPDATE users SET whatsapp_id = ? WHERE id = ?", (platform_id, user_id))
    elif platform == "telegram":
        c.execute("UPDATE users SET telegram_id = ? WHERE id = ?", (platform_id, user_id))
    conn.commit()
    conn.close()

def set_api_key(user_id, api_key):
    """Set the user's personal Gemini API key."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("UPDATE users SET gemini_api_key = ? WHERE id = ?", (api_key, user_id))
        conn.commit()
        return True, "✅ API Key set successfully!"
    except Exception as e:
        return False, f"❌ Error setting API key: {e}"
    finally:
        conn.close()

def get_user_api_key(user_id):
    """Retrieve the user's personal Gemini API key."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT gemini_api_key FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_by_platform(platform, platform_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if platform == "whatsapp":
        c.execute("SELECT id, username, gemini_api_key FROM users WHERE whatsapp_id = ?", (platform_id,))
    elif platform == "telegram":
        c.execute("SELECT id, username, gemini_api_key FROM users WHERE telegram_id = ?", (platform_id,))
    user = c.fetchone()
    conn.close()
    return user # Returns (id, username, gemini_api_key)

def log_conversation(user_id, message, response):
     conn = sqlite3.connect(DB_NAME)
     c = conn.cursor()
     c.execute("INSERT INTO conversations (user_id, message, response) VALUES (?, ?, ?)", (user_id, message, response))
     conn.commit()
     conn.close()

# --- State Management Functions ---

def set_state(platform_id, platform, state, data=None):
    """Set or update the conversation state for a user (by platform ID)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    data_json = json.dumps(data) if data else "{}"
    c.execute('''INSERT INTO user_states (platform_id, platform, state, data) 
                 VALUES (?, ?, ?, ?) 
                 ON CONFLICT(platform_id) DO UPDATE SET state=?, data=?''', 
              (platform_id, platform, state, data_json, state, data_json))
    conn.commit()
    conn.close()

def get_state(platform_id):
    """Get the current state and data for a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT state, data FROM user_states WHERE platform_id = ?", (platform_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0], json.loads(result[1])
    return None, {}

def clear_state(platform_id):
    """Clear the conversation state."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM user_states WHERE platform_id = ?", (platform_id,))
    conn.commit()
    conn.close()

# Initialize on import
init_db()
