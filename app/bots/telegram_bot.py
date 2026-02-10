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

def run_telegram_bot(outbox_queue):
    print("🚀 Starting Telegram Bot...")
    
    # Initialize Unified Bot with Queue for IPC
    bot_core = UnifiedBot(outbox_queue)
    
    # Initialize Application
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env")
        return
        
    application = ApplicationBuilder().token(telegram_token).build()

    def queue_listener():
        """Thread to listen for cross-platform messages destined for Telegram."""
        # We need a reference to the bot object which is in the application
        # but the application is not fully started yet. 
        # Application.run_polling is blocking.
        # We can use the bot object directly from the application after it's built.
        bot = application.bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while True:
            try:
                if not outbox_queue.empty():
                    item = outbox_queue.get()
                    if item.get("platform") == "telegram":
                        target = item.get("target")
                        text = item.get("text")
                        if target and text:
                            print(f"📥 IPC -> Telegram: Sending to {target}")
                            loop.run_until_complete(bot.send_message(chat_id=target, text=text, parse_mode='Markdown'))
                    else:
                        # Put it back if not for us
                        outbox_queue.put(item)
                        time.sleep(0.5)
                time.sleep(1)
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

