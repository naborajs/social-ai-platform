import time
import threading
from app.core.database import get_inactive_users

class EngagementManager:
    def __init__(self, telegram_bot=None, whatsapp_client=None):
        self.telegram_bot = telegram_bot
        self.whatsapp_client = whatsapp_client
        self.running = False
        
    def start_scheduler(self):
        self.running = True
        thread = threading.Thread(target=self._run_audit_loop)
        thread.daemon = True
        thread.start()
        print("🕒 Engagement Scheduler Started.")

    def _run_audit_loop(self):
        while self.running:
            # Check every hour (3600 seconds)
            # For testing purposes, let's allow a shorter interval if needed, but default to 1 hour
            # We will use the database function `get_inactive_users`
            try:
                inactive_users = get_inactive_users(hours_threshold=24) # Users inactive for 24h
                
                for user in inactive_users:
                    user_id, telegram_id, whatsapp_id, username = user
                    message = f"👋 Hey {username}! Long time no see. I miss our chats! How have you been? 💭"
                    
                    if telegram_id and self.telegram_bot:
                        try:
                            # Note: Sending async from sync thread might require asyncio.run or loop handling
                            # For simplicity/safety in this structure, we might print or try best effort
                            print(f"⌛ Miss You Message triggered for {username} (Telegram)")
                            # Actual send logic depends on passing the async context or robust job queue
                        except Exception as e:
                            print(f"Error sending engagement msg: {e}")
                            
                    if whatsapp_id and self.whatsapp_client:
                         try:
                             # Neonize send is sync-compatible usually
                             self.whatsapp_client.send_message(whatsapp_id, message)
                             print(f"⌛ Miss You Message sent to {username} (WhatsApp)")
                         except Exception as e:
                             print(f"Error sending engagement msg (WA): {e}")
                             
            except Exception as e:
                print(f"❌ Error in Engagement Loop: {e}")
                
            time.sleep(3600) 
            
    def stop(self):
        self.running = False
