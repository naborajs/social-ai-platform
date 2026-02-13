import os
import signal
import sys
import time
from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv, PairStatusEv
from neonize.types import MessageServerID
from app.core.bot_core import UnifiedBot
from app.core.config import BOT_WHATSAPP_NUMBER, WHATSAPP_SESSION
from app.core.database import get_inactive_users
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()

import threading

def run_whatsapp_bot(queues, login_info=None):
    print("🚀 Starting WhatsApp Bot (Unified)...")
    
    # Initialize Unified Bot with Queues for IPC
    bot_core = UnifiedBot(queues)

    # Initialize Neonize Client
    client = NewClient(WHATSAPP_SESSION)
    
    # ... (rest of the listeners and events) ...

    def queue_listener():
        """Robust thread to listen for cross-platform messages destined for WhatsApp."""
        if not queues or "whatsapp" not in queues:
            return
        
        wa_queue = queues["whatsapp"]
        print("📲 WhatsApp IPC Listener [ACTIVE]")
        
        while True:
            try:
                # Get message from our specific queue
                item = wa_queue.get()
                if not item: continue
                
                target = item.get("target")
                text = item.get("text", "")
                image_path = item.get("image_path")
                
                if target:
                    if image_path and os.path.exists(image_path):
                        try:
                            client.send_image(target, image_path, caption=text)
                            print(f"🖼️ IPC -> WhatsApp: Sent Image to {target}")
                        except Exception as e:
                            # Fallback if send_image fails/not available
                            client.send_message(target, f"{text}\n\n📎 [Attachment]: {image_path}")
                            print(f"📥 IPC -> WhatsApp: Sent Message (Image Fallback) to {target}: {e}")
                    elif text:
                        client.send_message(target, text)
                        print(f"💬 IPC -> WhatsApp: Sent Message to {target}")
                        
            except Exception as e:
                print(f"⚠️ WhatsApp IPC Listener Warning: {e}")
                time.sleep(2)

    # Start Queue Listener Thread
    listener_thread = threading.Thread(target=queue_listener, daemon=True)
    listener_thread.start()

    # Initialize Engagement Scheduler
    # We import here to avoid circular dependencies if any, or just to keep scope clean
    # assuming engagement.py is in the same folder or reachable
    # Adjust import based on file structure: app/bots/engagement.py??
    # The list_dir showed 'engagement.py' is NOT in 'app/bots'. 
    # Let's check where 'EngagementManager' is.
    # It was imported as 'from engagement import EngagementManager' in line 20 of original file.
    # But list_dir of app/bots only showed whatsapp_bot.py and telegram_bot.py.
    # list_dir of app/features showed (implied) it might be there?
    # Original code had: "from engagement import EngagementManager" which implies it expected it in the same dir
    # BUT list_dir of d:/code/test-whatsapp-bot/app/bots returned ONLY telegram_bot.py and whatsapp_bot.py. 
    # So "from engagement import ..." would have FAILED if run from bots dir unless it's in pythonpath.
    # Use absolute import: from app.features.engagement import EngagementManager (guessing location)

    try:
        from app.features.engagement import EngagementManager
        engagement_manager = EngagementManager(whatsapp_client=client)
        engagement_manager.start_scheduler()
    except ImportError:
        print("⚠️ EngagementManager not found or failed to load. Continuing without it.")
        pass

    def interrupt_handler(signum, frame):
        print("🔴 Interrupt received, shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, interrupt_handler)

    @client.event(ConnectedEv)
    def on_connected(event: ConnectedEv):
        print("✅ WhatsApp Connected!")

    @client.event(PairStatusEv)
    def on_pair_status(event: PairStatusEv):
        print(f"🔗 Pair Status: {event}")

    @client.event(MessageEv)
    def on_message(client: NewClient, message: MessageEv):
        try:
            # Check if message is text and not from self
            original_msg = message.Message
            chat_info = message.Info
            if chat_info.IsFromMe:
                return

            sender = chat_info.RemoteJid

            # Handle Media
            if original_msg.imageMessage:
                client.send_message(sender, "🤖 Image received!")
                return
            if original_msg.videoMessage:
                 client.send_message(sender, "🤖 Video received!")
                 return

            # Extract text content
            text = original_msg.conversation or original_msg.extendedTextMessage.text
            
            if not text:
                return

            print(f"📩 Message from {sender}: {text}")

            # Process message via UnifiedBot
            response_text = bot_core.handle_message(text, "whatsapp", sender)
            
            if response_text:
                print(f"📤 Replying: {response_text}")
                client.send_message(sender, response_text)

        except Exception as e:
            print(f"❌ Error processing message: {e}")

    if login_info and not os.path.exists(WHATSAPP_SESSION):
        method = login_info.get("method")
        
        if method == "pairing":
            target_number = login_info.get("number")
            if target_number:
                print(f"🔑 Generating Pairing Code for: {target_number}")
                try:
                     code = client.pair_code(target_number, show=True)
                     print(f"\n🚀 PAIRING CODE: {Fore.GREEN}{code}{Style.RESET_ALL}\n")
                     print("Please enter this code on your phone in WhatsApp 'Link a Device' -> 'Link with phone number instead'.")
                except Exception as e:
                     print(f"⚠️ Could not generate pairing code: {e}. Falling back to QR...")
        else:
            print("📱 Please scan the QR code below when it appears.")

    print(f"{Fore.WHITE}Connecting to WhatsApp...{Style.RESET_ALL}")
    client.connect()

if __name__ == "__main__":
    run_whatsapp_bot()

