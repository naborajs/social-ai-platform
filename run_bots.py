import multiprocessing
import os
import time

def run_whatsapp():
    os.system("python whatsapp_bot.py")

def run_telegram():
    os.system("python telegram_bot.py")

if __name__ == "__main__":
    print("🚀 Starting Unified Bot System...")
    
    p1 = multiprocessing.Process(target=run_whatsapp)
    p2 = multiprocessing.Process(target=run_telegram)
    
    # Engagement Scheduler needs to run in a separate process or thread that has access to send messages
    # Since neonize and telegram-bot are blocking in their own processes, we might need a different approach for the scheduler
    # to communicate. For simplicity in this architecture, we will append the scheduler start to each individual bot process 
    # OR run it as a standalone process that checks DB and prints logs (actual sending requires active client instances).
    
    # Better approach given the architecture:
    # We will modify whatsapp_bot.py and telegram_bot.py to start their own internal schedulers or checks.
    # So run_bots.py just launches them.
    
    p1.start()
    p2.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down bots...")
        p1.terminate()
        p2.terminate()
        p1.join()
        p2.join()
