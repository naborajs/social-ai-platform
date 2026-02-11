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
    print(f"{Fore.YELLOW}🚀 Starting Unified Bot System v3.4...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}="*50)

    # Communication Queues for Cross-Platform Messaging
    # We use separate queues to avoid "put it back" cycling logic
    queues = {
        "whatsapp": multiprocessing.Queue(),
        "telegram": multiprocessing.Queue()
    }

    # processes
    p_whatsapp = multiprocessing.Process(target=start_whatsapp, args=(queues,), name="WhatsAppBot")
    p_telegram = multiprocessing.Process(target=start_telegram, args=(queues,), name="TelegramBot")

    processes = []

    try:
        print(f"{Fore.GREEN}Starting WhatsApp Bot...{Style.RESET_ALL}")
        p_whatsapp.start()
        processes.append(p_whatsapp)
        
        print(f"{Fore.GREEN}Starting Telegram Bot...{Style.RESET_ALL}")
        p_telegram.start()
        processes.append(p_telegram)

        print(f"\n{Fore.WHITE}✅ Both bots are connected via IPC Queues.")
        print(f"Press {Fore.YELLOW}Ctrl+C{Fore.WHITE} to stop the system.\n")

        while True:
            time.sleep(1)
            # Check if processes are alive
            if not p_whatsapp.is_alive():
                print(f"{Fore.RED}⚠️ WhatsApp Bot process ended unexpectedly.{Style.RESET_ALL}")
            if not p_telegram.is_alive():
                print(f"{Fore.RED}⚠️ Telegram Bot process ended unexpectedly.{Style.RESET_ALL}")
            
            if not p_whatsapp.is_alive() and not p_telegram.is_alive():
                print(f"{Fore.RED}❌ All bots have stopped. Exiting.{Style.RESET_ALL}")
                break

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Shutting down system...{Style.RESET_ALL}")
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join()
        print(f"{Fore.GREEN}👋 System shutdown complete.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
