# Social AI Platform 🤖

> **Advanced Multi-Platform AI Companion with Personalized Personas**  
> Built by [Naboraj Sarkar](https://github.com/naborajs) | [@NSGAMMING699](https://twitter.com/NSGAMMING699)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-Supported-25D366?logo=whatsapp)](https://www.whatsapp.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Supported-26A5E4?logo=telegram)](https://telegram.org/)

An intelligent, production-ready AI social platform that brings personalized chatbot experiences to WhatsApp and Telegram. Each user gets a unique identity with customizable AI personalities, making conversations feel truly human.
## 🔄 Recent Updates
- **Version**: v3.6 (QR & Secure Sharing)
- **Status**: Stable / Production Ready
- **v3.4**: WhatsApp Pairing Code (OTP) Activation 🔑
- **v3.4**: OTP-based Login System (`/otp_login`, `/verify`) 🔐
- **v3.3**: Hardened Security & Prompt Injection Detection 🛡️
- **v3.3**: Graceful Error Handling & Privacy Guards
- **v3.2**: AI Emotions & Personalized Memory System 🧠
- **v3.2**: Real-time Cross-Platform Memory (WhatsApp ↔️ Telegram sync)
- **v3.2**: Automatic Gender Adaptation & Mood Controls (`/mood`, `/gender`)
- **v3.2**: Integrated Problem Reporting System (`/report`)
- **v3.1**: Advanced Private Messaging (`/msg`, `/chat`, `/exit`)

## 🔗 Quick Links
- [Technical Architecture](app/docs/system_architecture.md)
- [Documentation Wiki](https://github.com/naborajs/social-ai-platform/wiki)
- [Report a Bug](https://github.com/naborajs/social-ai-platform/issues)

## 🌟 Key Features

### 🎭 **Personalized AI Personas**
Choose how your AI companion talks to you:
- 🤗 **Best Friend** - Supportive and enthusiastic
- 🔥 **Roast Master** - Sarcastic and witty
- 👔 **Professional** - Formal executive assistant
- 🧙‍♂️ **Wizard** - Mystical and mysterious

### 🚀 **Interactive Onboarding**
No complex commands! Registration is conversational:
1. Choose a username
2. Enter your email
3. Set a password
4. Pick your avatar (4 unique options)
5. Select your AI's personality

### 🔐 **Privacy-First Architecture**
- **Per-User API Keys**: Set your own Gemini API key
- **Encrypted Passwords**: bcrypt hashing
- **Account Recovery**: Unique backup keys
- **Session Management**: Secure authentication flow

### 🌐 **Multi-Platform Support**
- ✅ WhatsApp (via Neonize)
- ✅ Telegram (via python-telegram-bot)
- 📱 Unified backend for both platforms

### 👥 **Social Features**
- **Friend System**: `/add_friend`, `/friends`, `/accept`
- **Group Chats**: `/create_group`, `/join`
- **Unified Profiles**: Cross-platform identity synchronization

### 🎨 **Social-Ready Features**
- Unique user profiles with avatars
- Email & username uniqueness
- Conversation history logging
- Activity tracking (last seen)
- **Technical Documentation**: [System Architecture](app/docs/system_architecture.md)

---

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [User Guide](#-user-guide)
- [Configuration](#-configuration)
- [Development](#-development)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- WhatsApp account (for WhatsApp bot)
- Telegram Bot Token (for Telegram bot)
- Google Gemini API Key

### Step 1: Clone the Repository
```bash
git clone https://github.com/naborajs/social-ai-platform.git
cd social-ai-platform
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DB_NAME=whatsapp_bot.db
BOT_WHATSAPP_NUMBER=+1234567890
```

**Note:** Users can also set their own Gemini API keys after registration using `/set_key`.

---

## 🚀 Quick Start

### Launch the Platform
```bash
python main.py
```

This starts both WhatsApp and Telegram bots simultaneously.

### WhatsApp Setup
1.  Set `BOT_WHATSAPP_NUMBER` in your `.env` file (Optional).
2.  Run `python main.py`.
3.  **Login Choice**: The system will prompt you to choose between:
    - **1. Pairing Code**: Enter your number if not set in `.env`, and link via code.
    - **2. QR Code**: Scan the QR code directly.
4.  On your phone (WhatsApp) -> Settings -> Linked Devices -> Link a Device.
5.  Follow the terminal instructions for the chosen method.
6.  The bot is now connected!

### Telegram Setup
1. Get a bot token from [@BotFather](https://t.me/botfather)
2. Add it to your `.env` file
3. Run `python main.py`
4. Start chatting with your bot on Telegram

### ⚙️ Persistence & Reliability
This version introduces a **Self-Healing** architecture:
- **Auto-Restarter**: The `main.py` controller monitors background processes and automatically restarts them if they fail.
- **SQLite WAL Mode**: Prevents database corruption and improves concurrent performance.
- **Centralized Data**: All stateful files are kept in the `./data` folder for easy backup.
- **Persistent Pairing**: Sessions are saved locally, so you only need to pair once.

---

## 🏗️ Architecture

### Project Structure
```
social-ai-platform/
├── main.py                    # Unified entry point
├── cli_chatbot.py            # Standalone CLI chatbot
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── data/                     # PERSISTENT STORAGE [NEW]
│   ├── whatsapp_bot.db      # Users, Friends, Stats
│   └── whatsapp_session.sqlite3 # Logged-in Session
│
├── app/
│   ├── core/
│   │   ├── bot_core.py       # Unified bot logic
│   │   ├── chatbot.py        # ChatBot class
│   │   ├── database.py       # Database operations
│   │   ├── user_flow.py      # Conversation state machine
│   │   └── config.py         # Configuration loader
│   │
│   ├── bots/
│   │   ├── whatsapp_bot.py   # WhatsApp integration
│   │   └── telegram_bot.py   # Telegram integration
│   │
│   └── features/
│       ├── llm_handler.py    # Gemini API integration
│       ├── love_calculator.py # Fun feature
│       ├── media_handler.py  # Image/Video processing
│       └── engagement.py     # User engagement (optional)
```

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    whatsapp_id TEXT,
    telegram_id TEXT,
    gemini_api_key TEXT,
    system_prompt TEXT,
    avatar_url TEXT,
    bio TEXT,
    recovery_key TEXT,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### User States Table (Conversation Flow)
```sql
CREATE TABLE user_states (
    platform_id TEXT PRIMARY KEY,
    platform TEXT,
    state TEXT,
    data TEXT
);
```

#### Conversations Table
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

### How It Works

#### 1. **Unified Entry Point** (`main.py`)
Uses `multiprocessing` to run WhatsApp and Telegram bots in parallel processes.

#### 2. **State Machine** (`user_flow.py`)
Manages interactive registration flow:
- `STATE_REG_USERNAME` → `STATE_REG_EMAIL` → `STATE_REG_PASSWORD` → `STATE_REG_AVATAR` → `STATE_REG_PERSONA`

#### 3. **Bot Core** (`bot_core.py`)
- Checks conversation state first
- Routes to appropriate handler (registration flow vs. chat)
- Passes user-specific API key and system prompt to LLM

#### 4. **LLM Handler** (`llm_handler.py`)
- Configures Gemini model with custom system instructions
- Supports per-user API keys
- Maintains chat history (stateless for custom personas)

---

## 📖 User Guide

### Registration (Interactive)
```
User: /register
Bot: 👋 Welcome! Let's get you set up.
     First, choose a unique Username:

User: john_doe
Bot: 📧 Great! Now, what is your Email Address?

User: john@example.com
Bot: 🔐 Secure your account. Create a Password:

User: mypassword123
Bot: 🎨 Choose your Identity (Avatar):
     1️⃣ Adventurer Felix
     2️⃣ Adventurer Aneka
     3️⃣ Midnight Warrior
     4️⃣ Retro Bot

User: 1
Bot: 🧠 Final Step! Choose my Personality:
     1️⃣ 🤗 Best Friend (Supportive)
     2️⃣ 🔥 Roast Master (Sarcastic)
     3️⃣ 👔 Professional (Formal)
     4️⃣ 🧙‍♂️ Wizard (Mystical)

User: 2
Bot: ✅ Registration successful!
     Email: john@example.com
     🔑 Backup Key: `a3f8d9e2c1b4`
     (Save this! Use `/recover <key> <new_pass>` if you forget your password.)
     
     🎉 Setup Complete!
```

### Commands

#### Authentication
- `/register` - Start interactive registration
- `/login <username> <password>` - Login to existing account
- `/otp_login <username>` - Request a login OTP on WhatsApp 🔐
- `/verify <otp>` - Verify OTP and log in
- `/recover <backup_key> <new_password>` - Recover account
- `/help` - Show detailed menu with all commands 🌟
- `/about` - Developer info and project mission 👨‍💻

#### Account Management
- `/set_key <your_api_key>` - Set your personal Gemini API key
- `/my_key` - Check if API key is set
- `/change_password <new_password>` - Update password
- `/change_username <new_username>` - Update username

#### Fun Features
- `love <name1> and <name2>` - Love compatibility calculator
- Send a photo → Get a sticker
- Send a video → Get a GIF
- `/qr <text>` - Generate a standard QR code 🖼️
- `/secure_qr <text>` - Generate an encrypted QR code 🔒

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Default Gemini API key | Optional* |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather | Yes (for Telegram) |
| `DB_NAME` | SQLite database filename | No (default: `whatsapp_bot.db`) |
| `BOT_WHATSAPP_NUMBER` | WhatsApp number for terminal linking | No (triggers QR if missing) |

*Users can set their own API keys via `/set_key`

### Customizing Personas

Edit `app/core/user_flow.py`:
```python
PERSONAS = {
    "1": "Your custom persona instruction here",
    "2": "Another persona...",
    # Add more personas
}
```

### Customizing Avatars

Edit `app/core/user_flow.py`:
```python
AVATARS = {
    "1": "https://your-avatar-url.com/avatar1.png",
    "2": "https://your-avatar-url.com/avatar2.png",
    # Add more avatars
}
```

---

## 🔧 Development

### Running Individual Bots

**WhatsApp Only:**
```bash
python app/bots/whatsapp_bot.py
```

**Telegram Only:**
```bash
python app/bots/telegram_bot.py
```

**CLI Chatbot (No Platform):**
```bash
python cli_chatbot.py
```

### Database Migrations

The database auto-migrates on startup. To reset:
```bash
rm whatsapp_bot.db
python main.py
```

### Adding New Features

1. **Create a new module** in `app/features/`
2. **Import in `bot_core.py`**
3. **Add command handler** in `handle_message()`

Example:
```python
# app/features/my_feature.py
def my_function(user_input):
    return "Feature response"

# app/core/bot_core.py
from app.features.my_feature import my_function

# In handle_message():
if command == "/mycommand":
    return my_function(message)
```

---

## 📚 API Reference

### Core Classes

#### `UnifiedBot` (bot_core.py)
Main bot controller.

**Methods:**
- `handle_message(message, platform, platform_id)` - Process incoming messages

#### `ConversationManager` (user_flow.py)
Manages registration flow.

**Methods:**
- `start_registration(platform_id, platform)` - Begin registration
- `handle_input(platform_id, platform, text)` - Process state-based input

#### `GeminiHandler` (llm_handler.py)
Gemini API integration.

**Methods:**
- `generate_response(user_input, user_api_key=None, system_instruction=None)` - Generate AI response

### Database Functions

```python
# User Management
register_user(username, email, password, platform, platform_id, avatar_url, bio)
verify_user(username, password)
get_user_by_platform(platform, platform_id)

# API Keys
set_api_key(user_id, api_key)
get_user_api_key(user_id)

# Personas
update_system_prompt(user_id, system_prompt)
get_user_system_prompt(user_id)

# State Management
set_state(platform_id, platform, state, data)
get_state(platform_id)
clear_state(platform_id)
```

---

## 🐛 Troubleshooting

### WhatsApp QR Code Not Showing
- Ensure terminal supports UTF-8
- Try running in a different terminal
- Check `neonize` installation: `pip install --upgrade neonize`

### Telegram Bot Not Responding
- Verify `TELEGRAM_BOT_TOKEN` in `.env`
- Check bot token with [@BotFather](https://t.me/botfather)
- Ensure bot is not already running elsewhere

### Database Errors
```bash
# Reset database
rm whatsapp_bot.db
python main.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Gemini API Errors
- Verify API key is valid
- Check quota at [Google AI Studio](https://aistudio.google.com/)
- Users can set their own keys with `/set_key`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to functions
- Update README for new features
- Test on both WhatsApp and Telegram

---

## 📞 Contact & Support

**Developer:** Naboraj Sarkar

- 📧 Email: [nishant.ns.business@gmail.com](mailto:nishant.ns.business@gmail.com)
- 🐦 Twitter/X: [@NSGAMMING699](https://twitter.com/NSGAMMING699)
- 📷 Instagram: [@naborajs](https://instagram.com/naborajs)
- 💬 Telegram: [@Nishantsarkar10k](https://t.me/Nishantsarkar10k)
- 🎮 YouTube: [NS GAMMiNG](https://youtube.com/@NSGAMMING)
- 💻 GitHub: [@naborajs](https://github.com/naborajs)

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** - AI model
- **Neonize** - WhatsApp integration
- **python-telegram-bot** - Telegram integration
- **DiceBear** - Avatar generation API

---

## 🗺️ Roadmap

- [ ] Web dashboard for user management
- [x] Group chat support
- [x] **Secure QR Generation**: Create standard and encrypted QR codes for data sharing.
- [x] **Multimedia Messaging**: Bot support for sending images and documents across platforms.
- [x] **High Availability**: Automatic process restarter for WhatsApp and Telegram.
- [x] **One-Time Pairing**: Logged-in WhatsApp sessions persist even after server reboots.
- [ ] Voice message processing
- [ ] Multi-language support
- [x] User-to-user messaging (social features)
- [ ] Analytics dashboard
- [x] Custom persona training
- [ ] Mobile app integration

---

<div align="center">

**Made with ❤️ by Naboraj Sarkar**

⭐ Star this repo if you find it useful!

[Report Bug](https://github.com/naborajs/social-ai-platform/issues) · [Request Feature](https://github.com/naborajs/social-ai-platform/issues)

</div>