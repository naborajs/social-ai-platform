import sqlite3
import json
import bcrypt
from app.core.config import DB_NAME
from app.core.security import security_manager

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
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

    # Friends table
    c.execute('''CREATE TABLE IF NOT EXISTS friends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER,
                    user2_id INTEGER,
                    status TEXT, -- 'pending', 'accepted'
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user1_id) REFERENCES users(id),
                    FOREIGN KEY(user2_id) REFERENCES users(id)
                )''')

    # Groups table
    c.execute('''CREATE TABLE IF NOT EXISTS groups (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    created_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(created_by) REFERENCES users(id)
                )''')

    # Group Members table
    c.execute('''CREATE TABLE IF NOT EXISTS group_members (
                    group_id TEXT,
                    user_id INTEGER,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(group_id, user_id),
                    FOREIGN KEY(group_id) REFERENCES groups(id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')

    # Blocked Users table
    c.execute('''CREATE TABLE IF NOT EXISTS blocked_users (
                    user_id INTEGER,
                    blocked_user_id INTEGER,
                    PRIMARY KEY(user_id, blocked_user_id),
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(blocked_user_id) REFERENCES users(id)
                )''')

    # Private Messages table
    c.execute('''CREATE TABLE IF NOT EXISTS private_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_id INTEGER,
                    to_id INTEGER,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_read INTEGER DEFAULT 0,
                    FOREIGN KEY(from_id) REFERENCES users(id),
                    FOREIGN KEY(to_id) REFERENCES users(id)
                )''')

    # Posts table (v4.0)
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    content TEXT,
                    image_url TEXT,
                    is_public INTEGER DEFAULT 1,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')

    # Stories table (v4.0 - Expiring)
    c.execute('''CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    content TEXT,
                    image_url TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')

    # Reactions table (v4.0)
    c.execute('''CREATE TABLE IF NOT EXISTS reactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER,
                    story_id INTEGER,
                    user_id INTEGER,
                    type TEXT DEFAULT 'like',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(post_id) REFERENCES posts(id),
                    FOREIGN KEY(story_id) REFERENCES stories(id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')

    # Achievements table (v4.0)
    c.execute('''CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    badge_name TEXT,
                    achieved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')

    # Follows table (v5.0)
    c.execute('''CREATE TABLE IF NOT EXISTS follows (
                    follower_id INTEGER,
                    followed_id INTEGER,
                    receive_notifications INTEGER DEFAULT 1,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(follower_id, followed_id),
                    FOREIGN KEY(follower_id) REFERENCES users(id),
                    FOREIGN KEY(followed_id) REFERENCES users(id)
                )''')

    # Post Analytics / Views table (v5.0)
    c.execute('''CREATE TABLE IF NOT EXISTS post_views (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER,
                    viewer_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(post_id) REFERENCES posts(id),
                    FOREIGN KEY(viewer_id) REFERENCES users(id)
                )''')

    # Reports table
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    description TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )''')
    
    # Migrations
    columns = [
        ("last_seen", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
        ("recovery_key", "TEXT"),
        ("email", "TEXT"),
        ("gemini_api_key", "TEXT"),
        ("display_name", "TEXT"),
        ("avatar_url", "TEXT"),
        ("bio", "TEXT"),
        ("system_prompt", "TEXT"),
        ("uuid", "TEXT"),
        ("preferred_platform", "TEXT DEFAULT 'whatsapp'"),
        ("active_chat_id", "INTEGER"), # For context-based chatting
        ("gender", "TEXT"), # user's gender
        ("ai_gender", "TEXT"), # AI's preferred gender
        ("ai_mood", "TEXT DEFAULT 'supportive'"), # current AI mood
        ("is_verified", "INTEGER DEFAULT 0"), # v4.0 Diamond logic
        ("level", "INTEGER DEFAULT 1"),
        ("account_type", "TEXT DEFAULT 'personal'"), # v5.0 Creator Edition
        ("is_professional", "INTEGER DEFAULT 0")
    ]
    
    for col_name, col_type in columns:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            conn.commit() # Commit each column add
        except sqlite3.OperationalError:
            pass # Column likely exists
            
    # Posts Table Migrations (v5.0)
    post_columns = [
        ("visibility", "TEXT DEFAULT 'public'"), # public/private/archive
        ("post_type", "TEXT DEFAULT 'post'") # post/story
    ]
    for col_name, col_type in post_columns:
        try:
            c.execute(f"ALTER TABLE posts ADD COLUMN {col_name} {col_type}")
            conn.commit() # Commit each column add
        except sqlite3.OperationalError:
            pass # Column likely exists

    # Ensure UUIDs exist for all users
    import uuid
    c.execute("SELECT id FROM users WHERE uuid IS NULL")
    users_without_uuid = c.fetchall()
    for (u_id,) in users_without_uuid:
        c.execute("UPDATE users SET uuid = ? WHERE id = ?", (str(uuid.uuid4()), u_id))

    conn.commit()
    conn.close()

def register_user(username, email, password, platform=None, platform_id=None, avatar_url=None, bio=None):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    c = conn.cursor()
    
    import secrets
    recovery_key = secrets.token_hex(8)
    
    try:
        # PII Encryption (v6.0 Cyber-Secure)
        enc_email = security_manager.encrypt(email)
        enc_bio = security_manager.encrypt(bio) if bio else None
        
        enc_recovery = security_manager.encrypt(recovery_key)
        c.execute("INSERT INTO users (username, email, password_hash, recovery_key, avatar_url, bio) VALUES (?, ?, ?, ?, ?, ?)", 
                  (username, enc_email, hashed, enc_recovery, avatar_url, enc_bio))
        user_id = c.lastrowid
        
        if platform == "whatsapp":
             c.execute("UPDATE users SET whatsapp_id = ? WHERE id = ?", (platform_id, user_id))
        elif platform == "telegram":
             c.execute("UPDATE users SET telegram_id = ? WHERE id = ?", (platform_id, user_id))
             
        conn.commit()
        return True, f"Registration successful!\nEmail: {email}\nBackup Key: {recovery_key}"
    except sqlite3.IntegrityError as e:
        if "users.username" in str(e):
             return False, "Username already exists."
        elif "users.email" in str(e):
             return False, "Email already registered."
        return False, f"Registration failed: Duplicate entry."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def update_system_prompt(user_id, system_prompt):
    """Update the user's custom system prompt (persona)."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    c = conn.cursor()
    try:
        enc_prompt = security_manager.encrypt(system_prompt)
        c.execute("UPDATE users SET system_prompt = ? WHERE id = ?", (enc_prompt, user_id))
        conn.commit()
        return True, "✅ Persona updated successfully!"
    except Exception as e:
        return False, f"Error updating persona: {e}"
    finally:
        conn.close()

def get_user_system_prompt(user_id):
    """Retrieve the user's custom system prompt."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT system_prompt FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result and result[0]:
        return security_manager.decrypt(result[0])
    return None

# Updated get_user_by_platform to return system_prompt
def get_user_by_platform(platform, platform_id):
    """Retrieve user with decrypted API key and system prompt."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    c = conn.cursor()
    if platform == "whatsapp":
        c.execute("SELECT id, username, gemini_api_key, system_prompt, is_verified, level FROM users WHERE whatsapp_id = ?", (platform_id,))
    elif platform == "telegram":
        c.execute("SELECT id, username, gemini_api_key, system_prompt, is_verified, level FROM users WHERE telegram_id = ?", (platform_id,))
    user = c.fetchone()
    conn.close()
    if user:
        u_list = list(user)
        u_list[2] = security_manager.decrypt(u_list[2]) # Gemini Key
        u_list[3] = security_manager.decrypt(u_list[3]) # System Prompt
        return tuple(u_list)
    return user

def get_user_by_username(username):
    """Retrieve user info by username (Decrypted PII)."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, username, display_name, bio, avatar_url, last_seen, is_verified, level, whatsapp_id, telegram_id, preferred_platform FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user:
        u_dict = dict(user)
        u_dict['bio'] = security_manager.decrypt(u_dict.get('bio'))
        u_dict['display_name'] = security_manager.decrypt(u_dict.get('display_name'))
        return u_dict
    return None

def verify_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user:
        # Direct bcrypt verification
        if bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
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

def update_last_seen(user_id):
    """Update the user's last activity timestamp."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def change_password(user_id, new_password):
    """Securely update the user's password."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, user_id))
    conn.commit()
    conn.close()

def change_username(user_id, new_username):
    """Update the user's username if unique."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))
        conn.commit()
        return True, "✅ Username updated successfully!"
    except sqlite3.IntegrityError:
        return False, "❌ Username already exists."
    finally:
        conn.close()

def recover_account(recovery_key, new_password):
    """Recover account using encrypted recovery key."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # We need to find the user by their decrypted recovery key.
    # Since we can't search encrypted fields efficiently, we iterate or use a deterministic hash (Omitted for simplicity, we'll try to match exact ciphertext if it's deterministic which it isn't with Fernet).
    # Correct way: fetch all and decrypt, or use a separate hash for lookup.
    # For now, we'll fetch all recovery keys and match.
    c.execute("SELECT id, recovery_key FROM users")
    users = c.fetchall()
    
    for u_id, enc_key in users:
        if security_manager.decrypt(enc_key) == recovery_key:
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, u_id))
            conn.commit()
            conn.close()
            return True, "✅ Account recovered and password updated successfully!"
    
    conn.close()
    return False, "❌ Invalid recovery key."

def set_api_key(user_id, api_key):
    """Set the user's personal Gemini API key (encrypted)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        encrypted_key = security_manager.encrypt(api_key)
        c.execute("UPDATE users SET gemini_api_key = ? WHERE id = ?", (encrypted_key, user_id))
        conn.commit()
        return True, "✅ API Key set successfully!"
    except Exception as e:
        return False, f"❌ Error setting API key: {e}"
    finally:
        conn.close()

def get_user_api_key(user_id):
    """Retrieve the user's personal Gemini API key (decrypted)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT gemini_api_key FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result and result[0]:
        return security_manager.decrypt(result[0])
    return None

def get_user_by_id(user_id):
    """Retrieve basic user info by internal ID."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, username, whatsapp_id, telegram_id, preferred_platform, is_verified, level FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None


def log_conversation(user_id, message, response):
    """Log a conversation with encrypted content."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    c = conn.cursor()
    enc_msg = security_manager.encrypt(message)
    enc_res = security_manager.encrypt(response)
    c.execute("INSERT INTO conversations (user_id, message, response) VALUES (?, ?, ?)", (user_id, enc_msg, enc_res))
    conn.commit()
    conn.close()

# --- State Management Functions ---
def set_state(platform_id, platform, state, data=None):
    """Set or update the conversation state for a user (by platform ID)."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
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

# --- Social Functions ---

def send_friend_request(from_id, to_username):
    """Send a friend request by username."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (to_username,))
    to_user = c.fetchone()
    if not to_user:
        return False, "❌ User not found."
    to_id = to_user[0]
    if from_id == to_id:
        return False, "❌ You cannot friend yourself."
    
    try:
        c.execute("INSERT INTO friends (user1_id, user2_id, status) VALUES (?, ?, 'pending')", (from_id, to_id))
        conn.commit()
        return True, f"✅ Friend request sent to {to_username}!"
    except Exception as e:
        return False, f"❌ Error: {e}"
    finally:
        conn.close()

def get_friend_requests(user_id):
    """List pending friend requests."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT users.username FROM friends 
                 JOIN users ON friends.user1_id = users.id 
                 WHERE friends.user2_id = ? AND friends.status = 'pending' ''', (user_id,))
    requests = [r[0] for r in c.fetchall()]
    conn.close()
    return requests

def accept_friend_request(user_id, from_username):
    """Accept a pending friend request."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (from_username,))
    from_user = c.fetchone()
    if not from_user:
        return False, "❌ User not found."
    from_id = from_user[0]
    
    c.execute("UPDATE friends SET status = 'accepted' WHERE user1_id = ? AND user2_id = ? AND status = 'pending'", (from_id, user_id))
    if c.rowcount > 0:
        conn.commit()
        conn.close()
        return True, f"✅ You are now friends with {from_username}!"
    conn.close()
    return False, "❌ No pending request from that user."

def get_friends(user_id):
    """List all accepted friends."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT username FROM users WHERE id IN (
                    SELECT user2_id FROM friends WHERE user1_id = ? AND status = 'accepted'
                    UNION
                    SELECT user1_id FROM friends WHERE user2_id = ? AND status = 'accepted'
                 )''', (user_id, user_id))
    friends = [f[0] for f in c.fetchall()]
    conn.close()
    return friends

def create_group(name, creator_id):
    """Create a new group."""
    import uuid
    group_id = str(uuid.uuid4())[:8]
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    c = conn.cursor()
    c.execute("INSERT INTO groups (id, name, created_by) VALUES (?, ?, ?)", (group_id, name, creator_id))
    c.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, creator_id))
    conn.commit()
    conn.close()
    return group_id

def join_group(group_id, user_id):
    """Join an existing group."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name FROM groups WHERE id = ?", (group_id,))
    group = c.fetchone()
    if not group:
        return False, "❌ Group not found."
    try:
        c.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, user_id))
        conn.commit()
        return True, f"✅ Joined group: {group[0]}"
    except sqlite3.IntegrityError:
        return False, "❌ You are already a member of this group."
    finally:
        conn.close()

def set_user_personalization(user_id, gender=None, ai_gender=None, mood=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if gender:
        c.execute("UPDATE users SET gender = ? WHERE id = ?", (gender, user_id))
    if ai_gender:
        c.execute("UPDATE users SET ai_gender = ? WHERE id = ?", (ai_gender, user_id))
    if mood:
        c.execute("UPDATE users SET ai_mood = ? WHERE id = ?", (mood, user_id))
    conn.commit()
    conn.close()

def get_user_personalization(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT gender, ai_gender, ai_mood FROM users WHERE id = ?", (user_id,))
    res = c.fetchone()
    conn.close()
    if res:
        return {"gender": res[0], "ai_gender": res[1], "mood": res[2]}
    return {"gender": None, "ai_gender": None, "mood": "supportive"}

def submit_report(user_id, report_type, description):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO reports (user_id, type, description) VALUES (?, ?, ?)", (user_id, report_type, description))
    conn.commit()
    conn.close()

def get_chat_history(user_id, limit=15):
    """Retrieve and decrypt recent conversation history."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT message, response FROM conversations 
                 WHERE user_id = ? 
                 ORDER BY timestamp DESC LIMIT ?''', (user_id, limit))
    history = c.fetchall()
    conn.close()
    
    decrypted_history = []
    for msg, res in history:
        decrypted_history.append((
            security_manager.decrypt(msg),
            security_manager.decrypt(res)
        ))
    
    return decrypted_history[::-1]

# Initialize on import
init_db()

def block_user(user_id, target_username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (target_username,))
    target = c.fetchone()
    if not target:
        conn.close()
        return False, "User not found."
    try:
        c.execute("INSERT INTO blocked_users (user_id, blocked_user_id) VALUES (?, ?)", (user_id, target[0]))
        conn.commit()
        return True, f"User {target_username} blocked."
    except sqlite3.IntegrityError:
        return False, "User already blocked."
    finally:
        conn.close()

def unblock_user(user_id, target_username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (target_username,))
    target = c.fetchone()
    if target:
        c.execute("DELETE FROM blocked_users WHERE user_id = ? AND blocked_user_id = ?", (user_id, target[0]))
        conn.commit()
        conn.close()
        return True, f"User {target_username} unblocked."
    conn.close()
    return False, "User not found."

def is_blocked(user_id, target_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT 1 FROM blocked_users WHERE user_id = ? AND blocked_user_id = ?", (target_id, user_id))
    blocked = c.fetchone() is not None
    conn.close()
    return blocked

def set_preferred_platform(user_id, platform):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET preferred_platform = ? WHERE id = ?", (platform, user_id))
    conn.commit()
    conn.close()

def get_user_contact_info(username):
    """Retrieve platform IDs and preferred platform for messaging."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, whatsapp_id, telegram_id, preferred_platform FROM users WHERE username = ?", (username,))
    res = c.fetchone()
    conn.close()
    if res:
        return {"id": res[0], "whatsapp_id": res[1], "telegram_id": res[2], "preferred_platform": res[3]}
    return None

def log_private_message(from_id, to_id, content):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA journal_mode=WAL;")
    c = conn.cursor()
    c.execute("INSERT INTO private_messages (from_id, to_id, content) VALUES (?, ?, ?)", (from_id, to_id, content))
    conn.commit()
    conn.close()

def set_active_chat(user_id, target_user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET active_chat_id = ? WHERE id = ?", (target_user_id, user_id))
    conn.commit()
    conn.close()

def get_active_chat(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT active_chat_id FROM users WHERE id = ?", (user_id,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else None

def remove_friend(user_id, friend_username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (friend_username,))
    friend = c.fetchone()
    if friend:
        f_id = friend[0]
        c.execute("DELETE FROM friends WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)", 
                  (user_id, f_id, f_id, user_id))
        conn.commit()
        conn.close()
        return True, f"Friendship with {friend_username} removed."
    conn.close()
    return False, "Friend not found."
def create_post(user_id, content, image_url=None, visibility='public', post_type='post'):
    """Create a new social post with visibility controls."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO posts (user_id, content, image_url, visibility, post_type) VALUES (?, ?, ?, ?, ?)", 
              (user_id, content, image_url, visibility, post_type))
    post_id = c.lastrowid
    conn.commit()
    conn.close()
    return post_id

def create_story(user_id, content, image_url=None, hours=24):
    """Create an expiring story."""
    from datetime import datetime, timedelta
    expires_at = (datetime.now() + timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO stories (user_id, content, image_url, expires_at) VALUES (?, ?, ?, ?)", 
              (user_id, content, image_url, expires_at))
    conn.commit()
    conn.close()
    return True

def send_private_message(from_id, to_username, content):
    """Send an encrypted private message."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, preferred_platform, whatsapp_id, telegram_id FROM users WHERE username = ?", (to_username,))
    to_user = c.fetchone()
    if to_user:
        to_id = to_user[0]
        enc_content = security_manager.encrypt(content)
        c.execute("INSERT INTO private_messages (from_id, to_id, content) VALUES (?, ?, ?)", (from_id, to_id, enc_content))
        conn.commit()
        conn.close()
        return True, to_user
    conn.close()
    return False, None

def get_private_messages(user_id, limit=20):
    """Fetch and decrypt recent private messages."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT pm.*, users.username as from_username FROM private_messages pm
                 JOIN users ON pm.from_id = users.id
                 WHERE pm.to_id = ? 
                 ORDER BY pm.timestamp DESC LIMIT ?''', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    
    messages = []
    for row in rows:
        d = dict(row)
        d['content'] = security_manager.decrypt(d['content'])
        messages.append(d)
    return messages

def get_social_feed(limit=20):
    """Fetch global public feed with usernames."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT posts.*, users.username, users.is_verified FROM posts 
                 JOIN users ON posts.user_id = users.id 
                 WHERE posts.visibility = 'public' AND posts.post_type = 'post'
                 ORDER BY posts.timestamp DESC LIMIT ?''', (limit,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def get_active_stories():
    """Fetch current stories that haven't expired."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT stories.*, users.username FROM stories 
                 JOIN users ON stories.user_id = users.id 
                 WHERE stories.expires_at > CURRENT_TIMESTAMP 
                 ORDER BY stories.created_at DESC''')
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def react_to_content(user_id, post_id=None, story_id=None, reaction_type='like'):
    """Add a reaction to a post or story."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO reactions (user_id, post_id, story_id, type) VALUES (?, ?, ?, ?)", 
              (user_id, post_id, story_id, reaction_type))
    conn.commit()
    conn.close()
    return True

def get_reactions_count(post_id=None, story_id=None):
    """Get count of reactions for a specific content."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if post_id:
        c.execute("SELECT COUNT(*) FROM reactions WHERE post_id = ?", (post_id,))
    else:
        c.execute("SELECT COUNT(*) FROM reactions WHERE story_id = ?", (story_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def set_verified_status(user_id, status=1):
    """Mark a user as verified (💎 Diamond status)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET is_verified = ? WHERE id = ?", (status, user_id))
    conn.commit()
    conn.close()

def get_all_users_for_broadcast():
    """Retrieve all users with linked platform IDs for owner broadcasts."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT whatsapp_id, telegram_id, preferred_platform FROM users")
    users = c.fetchall()
    conn.close()
    return users
def search_users(query, limit=10):
    """Search for users by username or display name."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    search_query = f"%{query}%"
    c.execute("SELECT username, display_name, bio FROM users WHERE username LIKE ? OR display_name LIKE ? LIMIT ?", 
              (search_query, search_query, limit))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results

def get_mutual_friends_count(user1_id, user2_id):
    """Calculate the number of mutual friends between two users."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM (
                    SELECT user2_id as friend_id FROM friends WHERE user1_id = ? AND status = 'accepted'
                    UNION SELECT user1_id FROM friends WHERE user2_id = ? AND status = 'accepted'
                 ) AS u1
                 INTERSECT
                 SELECT friend_id FROM (
                    SELECT user2_id as friend_id FROM friends WHERE user1_id = ? AND status = 'accepted'
                    UNION SELECT user1_id FROM friends WHERE user2_id = ? AND status = 'accepted'
                 ) AS u2''', (user1_id, user1_id, user2_id, user2_id))
    count = c.fetchone()[0]
    conn.close()
    return count

def follow_user(follower_id, followed_username):
    """Follow a user by their username."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (followed_username,))
    followed = c.fetchone()
    if not followed:
        conn.close()
        return False, "User not found."
    
    followed_id = followed[0]
    if follower_id == followed_id:
        conn.close()
        return False, "You cannot follow yourself."
        
    try:
        c.execute("INSERT INTO follows (follower_id, followed_id) VALUES (?, ?)", (follower_id, followed_id))
        conn.commit()
        res = True, f"You are now following {followed_username}!"
    except sqlite3.IntegrityError:
        res = False, f"You are already following {followed_username}."
    
    conn.close()
    return res

def unfollow_user(follower_id, followed_username):
    """Unfollow a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (followed_username,))
    followed = c.fetchone()
    if not followed:
        conn.close()
        return False, "User not found."
    
    c.execute("DELETE FROM follows WHERE follower_id = ? AND followed_id = ?", (follower_id, followed[0]))
    conn.commit()
    conn.close()
    return True, f"Unfollowed {followed_username}."

def get_follow_status(follower_id, followed_id):
    """Check if a user follows another."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT receive_notifications FROM follows WHERE follower_id = ? AND followed_id = ?", (follower_id, followed_id))
    res = c.fetchone()
    conn.close()
    return res if res else (None,)

def set_professional_account(user_id, is_prof=1):
    """Upgrade account to professional/creator status."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET is_professional = ?, account_type = ? WHERE id = ?", (is_prof, 'professional' if is_prof else 'personal', user_id))
    conn.commit()
    conn.close()

def log_post_view(post_id, viewer_id):
    """Log a view for analytics (Diamond/Creator feature)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Check if already viewed to prevent duplicate counting in stats
    c.execute("SELECT id FROM post_views WHERE post_id = ? AND viewer_id = ?", (post_id, viewer_id))
    if not c.fetchone():
        c.execute("INSERT INTO post_views (post_id, viewer_id) VALUES (?, ?)", (post_id, viewer_id))
        conn.commit()
    conn.close()

def get_post_analytics(post_id):
    """Retrieve detailed analytics for a post."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM post_views WHERE post_id = ?", (post_id,))
    views = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM reactions WHERE post_id = ?", (post_id,))
    likes = c.fetchone()[0]
    conn.close()
    return {"views": views, "likes": likes}

def get_follower_ids(user_id):
    """Get IDs of everyone following this user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT follower_id FROM follows WHERE followed_id = ? AND receive_notifications = 1", (user_id,))
    ids = [r[0] for r in c.fetchall()]
    conn.close()
    return ids

def update_post_visibility(post_id, user_id, visibility):
    """Update visibility of a post (Creator control)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE posts SET visibility = ? WHERE id = ? AND user_id = ?", (visibility, post_id, user_id))
    conn.commit()
    conn.close()
    return True
