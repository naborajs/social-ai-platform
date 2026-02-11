import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_WHATSAPP_NUMBER = os.getenv("BOT_WHATSAPP_NUMBER")

# Database Configuration
# Use absolute path for DB to avoid issues when running from different directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_NAME = os.path.join(BASE_DIR, os.getenv("DB_NAME", "whatsapp_bot.db"))
