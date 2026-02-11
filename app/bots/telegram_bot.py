import os
import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from app.core.bot_core import UnifiedBot
from dotenv import load_dotenv

load_dotenv()

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

import threading
import asyncio

def run_telegram_bot(queues):
    print("🚀 Starting Telegram Bot...")
    
    # Initialize Unified Bot with Queues for IPC
    bot_core = UnifiedBot(queues)
    
    # Initialize Application
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env")
        return
        
    application = ApplicationBuilder().token(telegram_token).build()

    def queue_listener():
        """Thread to listen for cross-platform messages destined for Telegram."""
        if not queues or "telegram" not in queues:
            return
            
        tg_queue = queues["telegram"]
        bot = application.bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while True:
            try:
                # Get message from our specific queue
                item = tg_queue.get()
                target = item.get("target")
                text = item.get("text")
                image_path = item.get("image_path")
                
                if target and text:
                    print(f"📥 IPC -> Telegram: Sending to {target}")
                    if image_path and os.path.exists(image_path):
                        with open(image_path, 'rb') as photo:
                            loop.run_until_complete(bot.send_photo(chat_id=target, photo=photo, caption=text, parse_mode='Markdown'))
                    else:
                        loop.run_until_complete(bot.send_message(chat_id=target, text=text, parse_mode='Markdown'))
            except Exception as e:
                print(f"❌ Telegram Queue Listener Error: {e}")
                time.sleep(2)

    # Start Queue Listener Thread
    listener_thread = threading.Thread(target=queue_listener, daemon=True)
    listener_thread.start()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="👋 **Welcome to TrueFriend!** \n\nI'm your AI companion. Please authenticate to start chatting!",
            parse_mode='Markdown'
        )

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        sender_id = str(update.effective_user.id)
        text = update.message.text
        if not text: return

        response = bot_core.handle_message(text, "telegram", sender_id)
        
        if response:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=response,
                parse_mode='Markdown'
            )

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO) & (~filters.COMMAND), handle_message)
    command_handler = MessageHandler(filters.COMMAND, handle_message)

    application.add_handler(start_handler)
    application.add_handler(message_handler)
    application.add_handler(command_handler)
    
    application.run_polling()

if __name__ == '__main__':
    run_telegram_bot(None) # For local test only

