import os
import signal
import sys
import time
from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv, PairStatusEv
from neonize.types import MessageServerID
from app.core.bot_core import UnifiedBot
from app.core.config import BOT_WHATSAPP_NUMBER
from dotenv import load_dotenv

load_dotenv()

import threading

def run_whatsapp_bot(outbox_queue):
    print("🚀 Starting WhatsApp Bot (Unified)...")
    
    # Initialize Unified Bot with Queue for IPC
    bot_core = UnifiedBot(outbox_queue)

    # Initialize Neonize Client
    client = NewClient("whatsapp_session.sqlite3")

    def queue_listener():
        """Thread to listen for cross-platform messages destined for WhatsApp."""
        while True:
            try:
                # We check the queue for messages
                if not outbox_queue.empty():
                    item = outbox_queue.get()
                    if item.get("platform") == "whatsapp":
                        target = item.get("target")
                        text = item.get("text")
                        if target and text:
                            print(f"📥 IPC -> WhatsApp: Sending to {target}")
                            client.send_message(target, text)
                    else:
                        # Put it back if not for us, wait a bit
                        outbox_queue.put(item)
                        time.sleep(0.5)
                time.sleep(1)
            except Exception as e:
                print(f"❌ WhatsApp Queue Listener Error: {e}")
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

    print("📱 Please scan the QR code if prompted.")
    
    if BOT_WHATSAPP_NUMBER and not os.path.exists("whatsapp_session.sqlite3"):
        print(f"🔑 Generating Pairing Code for: {BOT_WHATSAPP_NUMBER}")
        # We need to connect first to trigger the pairing process or use pair_code
        # In neonize, it's often handled via an event or direct call before connect
        # But wait, neonize-python's current version often handles it like this:
        try:
             # This will show the pairing code in the terminal
             code = client.pair_code(BOT_WHATSAPP_NUMBER, show=True)
             print(f"\n🚀 PAIRING CODE: {code}\n")
             print("Please enter this code on your phone in WhatsApp 'Link a Device'.")
        except Exception as e:
             print(f"⚠️ Could not generate pairing code: {e}")

    client.connect()

if __name__ == "__main__":
    run_whatsapp_bot()

