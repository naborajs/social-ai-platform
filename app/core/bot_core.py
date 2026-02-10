from app.core.chatbot import ChatBot
from app.core.database import get_user_by_platform, register_user, verify_user, update_platform_id, log_conversation, set_api_key
from app.core.user_flow import ConversationManager
from app.features.love_calculator import LoveCalculator
from app.features.llm_handler import GeminiHandler
from app.core.config import GOOGLE_API_KEY

class UnifiedBot:
    def __init__(self):
        self.chatbot = ChatBot()
        # Override chatbot name/version if needed
        self.chatbot.name = "TrueFriend"
        self.chatbot.version = "3.0"
        self.conv_manager = ConversationManager()
        
    def handle_message(self, message, platform, platform_id):
        # 1. Check Active Conversation State First
        response, options, is_complete = self.conv_manager.handle_input(platform_id, platform, message)
        if response:
            return response # Return immediate response from flow
            
        user_data = get_user_by_platform(platform, platform_id)
        
        # Authentication Logic
        message_parts = message.strip().split()
        command = message_parts[0].lower() if message_parts else ""
        
        if command == "/register" or command == "/start":
            if user_data:
                return "✅ You are already registered! Just start chatting."
            # Start Interactive Flow
            return self.conv_manager.start_registration(platform_id, platform)
            
        elif command == "/login":
            if len(message_parts) < 3:
                return "❌ Usage: `/login <username> <password>`"
            user_id = verify_user(message_parts[1], message_parts[2])
            if user_id:
                update_platform_id(user_id, platform, platform_id)
                from app.core.database import update_last_seen
                update_last_seen(user_id)
                return f"✅ Login successful! Welcome back, {message_parts[1]}. 👋\n\n💡 **Tip**: Set your own Gemini API Key for privacy using:\n`/set_key <your_api_key>`"
            else:
                return "❌ Invalid username or password."

        elif command == "/recover":
            if len(message_parts) < 3:
                 return "❌ Usage: `/recover <key> <new_password>`"
            from app.core.database import recover_account
            success, msg = recover_account(message_parts[1], message_parts[2])
            return msg

        if not user_data:
            return "🔒 **Authentication Required**\n\nPlease log in or register to chat:\n\n🆕 `/register` (Interactive Setup)\n🔑 `/login <username> <password>`"
        
        # Authenticated User Logic
        # user_data structure: (id, username, gemini_api_key, system_prompt)
        user_id = user_data[0]
        username = user_data[1]
        user_api_key = user_data[2]
        system_prompt = user_data[3]
        
        # System Commands
        if command == "/set_key":
             if len(message_parts) < 2:
                  return "❌ Usage: `/set_key <your_gemini_api_key>`"
             success, msg = set_api_key(user_id, message_parts[1])
             return msg

        if command == "/my_key":
             if user_api_key:
                 return f"🔑 Your API Key is set: `...{user_api_key[-4:]}`"
             else:
                 return "❌ You haven't set a custom API Key yet."

        if command == "/change_password":
             if len(message_parts) < 2:
                  return "❌ Usage: `/change_password <new_password>`"
             from app.core.database import change_password
             change_password(user_id, message_parts[1])
             return "✅ Password updated successfully!"
             
        if command == "/change_username":
             if len(message_parts) < 2:
                  return "❌ Usage: `/change_username <new_username>`"
             from app.core.database import change_username
             success, msg = change_username(user_id, message_parts[1])
             if success: 
                  username = message_parts[1] # Update local context
             return msg
        
        # --- Social Controls ---
        
        if command == "/add_friend":
            if len(message_parts) < 2:
                return "❌ Usage: `/add_friend <username>`"
            from app.core.database import send_friend_request
            success, msg = send_friend_request(user_id, message_parts[1])
            return msg

        if command == "/friend_requests":
            from app.core.database import get_friend_requests
            requests = get_friend_requests(user_id)
            if not requests:
                return "📩 No pending friend requests."
            return "📩 **Pending Friend Requests**:\n" + "\n".join([f"• {r}" for r in requests]) + "\n\nUse `/accept <username>` to become friends."

        if command == "/accept":
            if len(message_parts) < 2:
                return "❌ Usage: `/accept <username>`"
            from app.core.database import accept_friend_request
            success, msg = accept_friend_request(user_id, message_parts[1])
            return msg

        if command == "/friends":
            from app.core.database import get_friends
            friends = get_friends(user_id)
            if not friends:
                return "👥 You haven't added any friends yet. Try `/add_friend <username>`!"
            return "👥 **Your Friends**:\n" + "\n".join([f"• {f}" for f in friends])

        if command == "/create_group":
            if len(message_parts) < 2:
                return "❌ Usage: `/create_group <group_name>`"
            from app.core.database import create_group
            name = " ".join(message_parts[1:])
            g_id = create_group(name, user_id)
            return f"🎨 Group **{name}** created! Invite others with ID: `{g_id}`\n\nUse `/join <group_id>` to enter."

        if command == "/join":
            if len(message_parts) < 2:
                return "❌ Usage: `/join <group_id>`"
            from app.core.database import join_group
            success, msg = join_group(message_parts[1], user_id)
            return msg

        # Update Activity
        from app.core.database import update_last_seen
        update_last_seen(user_id)
        
        self.chatbot.user_name = username # Set context for the chatbot
        
        # Pass user_api_key and system_prompt to generate_response
        response = self.chatbot.generate_response(message, user_api_key=user_api_key, system_instruction=system_prompt)
        
        # Log conversation
        log_conversation(user_id, message, response)
        
        return response
