import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_WHATSAPP_NUMBER = os.getenv("BOT_WHATSAPP_NUMBER")

# Database & Session Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DB_NAME = os.path.join(DATA_DIR, os.getenv("DB_NAME", "whatsapp_bot.db"))
WHATSAPP_SESSION = os.path.join(DATA_DIR, "whatsapp_session.sqlite3")
