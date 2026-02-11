import multiprocessing
import time
import sys
import os
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

def start_whatsapp(queue):
    """Function to run WhatsApp bot in a separate process."""
    try:
        from app.bots.whatsapp_bot import run_whatsapp_bot
        run_whatsapp_bot(queue)
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
    print(f"{Fore.CYAN}="*50)
    print(f"{Fore.YELLOW}🚀 Starting Unified Bot System v3.5 (Resilient)...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}="*50)

    # Communication Queues for Cross-Platform Messaging
    queues = {
        "whatsapp": multiprocessing.Queue(),
        "telegram": multiprocessing.Queue()
    }

    def create_process(name, target, args):
        p = multiprocessing.Process(target=target, args=args, name=name)
        p.start()
        return p

    # Initial start
    p_whatsapp = create_process("WhatsAppBot", start_whatsapp, (queues,))
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
