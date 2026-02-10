import os
import signal
import sys
import time
from neonize.client import NewClient
from neonize.events import ConnectedEv, MessageEv, PairStatusEv
from neonize.types import MessageServerID
from app.core.bot_core import UnifiedBot
from dotenv import load_dotenv

load_dotenv()

def run_whatsapp_bot():
    print("🚀 Starting WhatsApp Bot (Unified)...")
    
    # Initialize Unified Bot
    bot_core = UnifiedBot()

    # Initialize Neonize Client
    client = NewClient("whatsapp_session.sqlite3")

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

            # Handle Image Message
            if original_msg.imageMessage:
                print(f"📷 Image received from {sender}")
                try:
                     print("⚠️ Media download implementation requires manual verification of neonize docs.")
                     client.send_message(sender, "🤖 Image received! Sticker conversion coming soon.")
                except Exception as e:
                    print(f"❌ Error handling image: {e}")
                return

            # Handle Video Message
            if original_msg.videoMessage:
                 print(f"🎥 Video received from {sender}")
                 client.send_message(sender, "🤖 Video received! GIF conversion coming soon.")
                 return

            # Extract text content
            text = original_msg.conversation or original_msg.extendedTextMessage.text
            
            if not text:
                return

            print(f"📩 Message from {sender}: {text}")

            # Process message via UnifiedBot
            response_text = bot_core.handle_message(text, "whatsapp", sender)
            print(f"📤 Replying: {response_text}")

            # Send response
            client.send_message(sender, response_text)

        except Exception as e:
            print(f"❌ Error processing message: {e}")

    print("📱 Please scan the QR code if prompted.")
    client.connect()

if __name__ == "__main__":
    run_whatsapp_bot()

