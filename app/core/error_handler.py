import logging
import traceback
import sys
from colorama import Fore, Style

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("system_errors.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class ErrorHandler:
    """Centralized error handling for the Social AI Platform."""
    
    def __init__(self):
        self.logger = logging.getLogger("TrueFriend_ErrorHandler")

    def handle_exception(self, e, platform=None, platform_id=None, context=None):
        """Handle a general exception and return a user-friendly message."""
        error_type = type(e).__name__
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        
        # Log the full error for the owner
        log_msg = f"ERROR on {platform or 'UNKNOWN'}: {error_type}: {error_msg}\nContext: {context}\nID: {platform_id}\n{stack_trace}"
        self.logger.error(log_msg)
        
        # System-side alert (Terminal)
        print(f"{Fore.RED}🚨 SYSTEM ERROR: {error_type} in {context or 'processing'}{Style.RESET_ALL}")
        
        # Return a graceful, friend-like error message to the user
        friendly_messages = [
            "Oops, I got a bit tangled up in my own thoughts there! 😅 What were we saying?",
            "I seem to have hit a small bump in the road. 🚧 Could you try saying that again?",
            "My apologies! I missed that. 🤖 Something went slightly wrong on my end, but I'm back now!",
            "Whoops! I got a bit lost. 🧭 Let's try that again?"
        ]
        
        # If it's a known error type, we can be more specific
        if "API" in error_msg or "Gemini" in error_msg:
            return "☁️ My connection to the 'cloud' is a bit shaky right now. Give me a moment to catch my breath!"
        
        import random
        return random.choice(friendly_messages)

# Singleton instance
error_handler = ErrorHandler()
