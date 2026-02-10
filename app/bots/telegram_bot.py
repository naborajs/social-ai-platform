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

def run_telegram_bot():
    print("🚀 Starting Telegram Bot...")
    
    # Initialize Unified Bot
    bot_core = UnifiedBot()
    
    # Initialize Engagement Manager
    try:
        from app.features.engagement import EngagementManager
        engagement_manager = None
    except ImportError:
         print("⚠️ EngagementManager not found in expected path.")

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("📝 Register", callback_data='help_register'),
                InlineKeyboardButton("🔑 Login", callback_data='help_login'),
            ],
            [InlineKeyboardButton("❓ Help", callback_data='help_general')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="👋 **Welcome to TrueFriend!** \n\nI'm your AI companion. Please authenticate to start chatting!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == 'help_register':
            await query.edit_message_text(text="📝 **To Register:**\nType: `/register <username> <email> <password>`\n\nExample:\n`/register john john@email.com secret123`", parse_mode='Markdown')
        elif query.data == 'help_login':
            await query.edit_message_text(text="🔑 **To Login:**\nType: `/login <username> <password>`\n\nExample:\n`/login john secret123`", parse_mode='Markdown')
        elif query.data == 'help_general':
             await query.edit_message_text(text="📚 **Help Menu**\n• `/set_key <key>` - Set your own API key\n• `love <name> and <name>` - Love Calculator\n• Send Photo -> Sticker\n• Send Video -> GIF", parse_mode='Markdown')

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        # Handle Photo
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            file_path = f"temp_{int(time.time())}.jpg"
            await file.download_to_drive(file_path)
            
            try:
                from app.features.media_handler import create_sticker
                sticker_path = create_sticker(file_path)
                
                if sticker_path:
                    await context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=open(sticker_path, 'rb'))
                    os.remove(sticker_path)
            except ImportError:
                 print("⚠️ MediaHandler not found.")
                 await context.bot.send_message(chat_id=update.effective_chat.id, text="[Media Processing Unavailable]")
                 
            if os.path.exists(file_path): os.remove(file_path)
            return

        # Handle Video
        elif update.message.video:
            file = await update.message.video.get_file()
            file_path = f"temp_{int(time.time())}.mp4"
            await file.download_to_drive(file_path)
            
            try:
                from app.features.media_handler import create_gif
                gif_path = create_gif(file_path)
                
                if gif_path:
                    await context.bot.send_animation(chat_id=update.effective_chat.id, animation=open(gif_path, 'rb'))
                    os.remove(gif_path)
            except ImportError:
                 print("⚠️ MediaHandler not found.")
                 await context.bot.send_message(chat_id=update.effective_chat.id, text="[Media Processing Unavailable]")

            if os.path.exists(file_path): os.remove(file_path)
            return

        text = update.message.text
        if not text: return

        response = bot_core.handle_message(text, "telegram", str(user_id))
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response,
            parse_mode='Markdown'
        )

    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env")
        return
        
    application = ApplicationBuilder().token(telegram_token).build()
    
    start_handler = CommandHandler('start', start)
    button_handler_obj = CallbackQueryHandler(button_handler)
    message_handler = MessageHandler((filters.TEXT | filters.PHOTO | filters.VIDEO) & (~filters.COMMAND), handle_message)
    command_handler = MessageHandler(filters.COMMAND, handle_message)

    application.add_handler(start_handler)
    application.add_handler(button_handler_obj)
    application.add_handler(message_handler)
    application.add_handler(command_handler)
    
    # Start Engagement Scheduler
    try:
        from app.features.engagement import EngagementManager
        engagement_manager = EngagementManager(telegram_bot=application.bot)
        engagement_manager.start_scheduler()
    except Exception as e:
        print(f"⚠️ Could not start engagement scheduler: {e}")
    
    application.run_polling()

if __name__ == '__main__':
    run_telegram_bot()

