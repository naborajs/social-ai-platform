import multiprocessing
import time
import sys
import os
import io
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Load environment variables
load_dotenv()

# Initialize colorama
init(autoreset=True)

# Force UTF-8 encoding for stdout to handle emojis
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def start_whatsapp(queue, login_info=None):
    """Function to run WhatsApp bot in a separate process."""
    try:
        from app.bots.whatsapp_bot import run_whatsapp_bot
        run_whatsapp_bot(queue, login_info)
    except Exception as e:
        print(f"{Fore.RED}❌ WhatsApp Bot Crashed: {e}{Style.RESET_ALL}")

def start_telegram(queue):
    """Function to run Telegram bot in a separate process."""
    try:
        from app.bots.telegram_bot import run_telegram_bot
        run_telegram_bot(queue)
    except Exception as e:
        print(f"{Fore.RED}❌ Telegram Bot Crashed: {e}{Style.RESET_ALL}")

def main():
    """Main entry point for the Multi-Bot system."""
    queues = {
        "whatsapp": multiprocessing.Queue(),
        "telegram": multiprocessing.Queue()
    }

    # Initial check for WhatsApp setup
    from app.core.config import WHATSAPP_SESSION, BOT_WHATSAPP_NUMBER
    login_info = None
    
    if not os.path.exists(WHATSAPP_SESSION):
        print(f"\n{Fore.CYAN}--- WhatsApp Login Setup ---{Style.RESET_ALL}")
        print("1. 🔑 **Link with Phone Number** (Pairing Code)")
        print("2. 📱 **Scan QR Code**")
        
        choice = input(f"{Fore.YELLOW}Select option (1 or 2): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            target_number = BOT_WHATSAPP_NUMBER
            if not target_number:
                target_number = input(f"{Fore.YELLOW}Enter your WhatsApp number (with country code, e.g., 919876543210): {Style.RESET_ALL}").strip()
            
            if target_number:
                login_info = {"method": "pairing", "number": target_number}
            else:
                print("⚠️ No number provided. Falling back to QR...")
                login_info = {"method": "qr"}
        else:
            login_info = {"method": "qr"}

    def create_process(name, target, args):
        p = multiprocessing.Process(target=target, args=args, name=name)
        p.start()
        return p

    # Initial start
    p_whatsapp = create_process("WhatsAppBot", start_whatsapp, (queues, login_info))
    p_telegram = create_process("TelegramBot", start_telegram, (queues,))

    print(f"\n{Fore.WHITE}✅ Both bots are connected via IPC Queues.")
    print(f"Press {Fore.YELLOW}Ctrl+C{Fore.WHITE} to stop the system.\n")

    try:
        while True:
            time.sleep(5)
            # Monitor and restart WhatsApp Bot
            if not p_whatsapp.is_alive():
                print(f"{Fore.RED}⚠️ WhatsApp Bot stopped. Restarting...{Style.RESET_ALL}")
                p_whatsapp = create_process("WhatsAppBot", start_whatsapp, (queues,))
            
            # Monitor and restart Telegram Bot
            if not p_telegram.is_alive():
                print(f"{Fore.RED}⚠️ Telegram Bot stopped. Restarting...{Style.RESET_ALL}")
                p_telegram = create_process("TelegramBot", start_telegram, (queues,))
                
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Shutting down system...{Style.RESET_ALL}")
        if p_whatsapp.is_alive(): p_whatsapp.terminate()
        if p_telegram.is_alive(): p_telegram.terminate()
        p_whatsapp.join()
        p_telegram.join()
        print(f"{Fore.GREEN}👋 System shutdown complete.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
