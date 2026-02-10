import json
import re
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Import ChatBot from shared module
try:
    from app.core.chatbot import ChatBot
except ImportError:
    # Fallback if specific import path needed or local development
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'core'))
        from chatbot import ChatBot
    except:
        print("❌ Could not import ChatBot class!")
        pass

# Initialize colorama
init(autoreset=True)

load_dotenv()
try:
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def main():
    """Main entry point for the chatbot application."""
    try:
        chatbot = ChatBot()
        chatbot.chat()
    except KeyboardInterrupt:
        print("\n\n🛑 Program terminated by user.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

print ("Starting ChatBot application... 🚀")
if __name__ == "__main__":
    main()