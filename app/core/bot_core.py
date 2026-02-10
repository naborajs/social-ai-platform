from app.core.chatbot import ChatBot
from app.core.database import get_user_by_platform, register_user, verify_user, update_platform_id, log_conversation, set_api_key
from app.core.user_flow import ConversationManager
from app.features.love_calculator import LoveCalculator
from app.features.llm_handler import GeminiHandler
from app.core.config import GOOGLE_API_KEY

class UnifiedBot:
    def __init__(self, outbox_queue=None):
        self.chatbot = ChatBot()
        # Override chatbot name/version if needed
        self.chatbot.name = "TrueFriend"
        self.chatbot.version = "3.1"
        self.conv_manager = ConversationManager()
        self.outbox_queue = outbox_queue
        
    def handle_message(self, message, platform, platform_id):
        # 1. Check Active Conversation State First (Registration/Onboarding)
        response, options, is_complete = self.conv_manager.handle_input(platform_id, platform, message)
        if response:
            return response 
            
        user_data = get_user_by_platform(platform, platform_id)
        
        # Authentication Logic
        message_parts = message.strip().split()
        command = message_parts[0].lower() if message_parts else ""
        
        if command == "/register" or command == "/start":
            if user_data:
                return "✅ You are already registered! Just start chatting."
            return self.conv_manager.start_registration(platform_id, platform)
            
        elif command == "/login":
            if len(message_parts) < 3:
                return "❌ Usage: `/login <username> <password>`"
            user_id = verify_user(message_parts[1], message_parts[2])
            if user_id:
                update_platform_id(user_id, platform, platform_id)
                from app.core.database import update_last_seen
                update_last_seen(user_id)
                return f"✅ Login successful! Welcome back, {message_parts[1]}. 👋"
            else:
                return "❌ Invalid username or password."

        if not user_data:
            return "🔒 **Authentication Required**\n\nPlease `/register` or `/login` to start."
        
        # Authenticated User Logic
        user_id = user_data[0]
        username = user_data[1]
        user_api_key = user_data[2]
        system_prompt = user_data[3]
        
        from app.core.database import update_last_seen, get_active_chat, set_active_chat, is_blocked, get_user_contact_info, log_private_message
        update_last_seen(user_id)

        # --- Active Chat Context (Tunneling) ---
        active_chat_id = get_active_chat(user_id)
        if active_chat_id and command != "/exit":
            # Check if still friends and not blocked
            # tunnel message to active_chat_id
            from app.core.database import get_user_by_id
            target_user = get_user_by_id(active_chat_id) # Need to implement this
            if target_user:
                 t_username = target_user['username']
                 self._send_private_msg(user_id, username, active_chat_id, t_username, message)
                 return None # Silent return as message is dispatched

        # --- Commands ---
        
        if command == "/msg":
            if len(message_parts) < 3:
                return "❌ Usage: `/msg <username> <message>`"
            target_username = message_parts[1]
            content = " ".join(message_parts[2:])
            target_info = get_user_contact_info(target_username)
            if not target_info:
                return f"❌ User '{target_username}' not found."
            
            return self._send_private_msg(user_id, username, target_info['id'], target_username, content)

        if command == "/chat":
            if len(message_parts) < 2:
                return "❌ Usage: `/chat <username>`"
            target_username = message_parts[1]
            target_info = get_user_contact_info(target_username)
            if not target_info:
                return f"❌ User '{target_username}' not found."
            
            set_active_chat(user_id, target_info['id'])
            return f"🤝 **Chat Started with {target_username}**\nAI is now offline. Only {target_username} will see your messages.\n\nType `/exit` to return to AI mode."

        if command == "/exit":
            set_active_chat(user_id, None)
            return "🤖 **AI Mode Reactivated**\nWelcome back! How can I help you today?"

        if command == "/block":
            if len(message_parts) < 2: return "❌ Usage: `/block <username>`"
            from app.core.database import block_user
            success, msg = block_user(user_id, message_parts[1])
            return msg

        if command == "/unblock":
            if len(message_parts) < 2: return "❌ Usage: `/unblock <username>`"
            from app.core.database import unblock_user
            success, msg = unblock_user(user_id, message_parts[1])
            return msg

        if command == "/set_notify":
             if len(message_parts) < 2 or message_parts[1].lower() not in ["wa", "tg", "whatsapp", "telegram"]:
                 return "❌ Usage: `/set_notify <wa|tg>`"
             plat = "whatsapp" if message_parts[1].lower() in ["wa", "whatsapp"] else "telegram"
             from app.core.database import set_preferred_platform
             set_preferred_platform(user_id, plat)
             return f"✅ Notifications will now be sent to your **{plat.title()}** account."

        # Re-use existing friend/group commands
        if command == "/add_friend":
            from app.core.database import send_friend_request
            success, msg = send_friend_request(user_id, message_parts[1] if len(message_parts)>1 else "")
            return msg

        if command == "/friends":
            from app.core.database import get_friends
            friends = get_friends(user_id)
            return "👥 **Friends**:\n" + "\n".join([f"• {f}" for f in friends]) if friends else "👥 No friends yet."

        if command == "/accept":
            from app.core.database import accept_friend_request
            success, msg = accept_friend_request(user_id, message_parts[1] if len(message_parts)>1 else "")
            return msg
        
        # Default AI Response
        self.chatbot.user_name = username
        response = self.chatbot.generate_response(message, user_api_key=user_api_key, system_instruction=system_prompt)
        from app.core.database import log_conversation
        log_conversation(user_id, message, response)
        
        return response

    def _send_private_msg(self, from_id, from_username, to_id, to_username, content):
        from app.core.database import is_blocked, get_user_contact_info, log_private_message, get_friends
        
        # Permission checks
        if is_blocked(from_id, to_id):
            return "❌ You are blocked by this user."
        
        friends = get_friends(from_id)
        if to_username not in friends:
            return "❌ You can only message your friends."

        target_info = get_user_contact_info(to_username)
        pref_plat = target_info['preferred_platform']
        plat_id = target_info['whatsapp_id'] if pref_plat == 'whatsapp' else target_info['telegram_id']
        
        if not plat_id:
            # Fallback to other platform if preferred not linked
            pref_plat = 'telegram' if pref_plat == 'whatsapp' else 'whatsapp'
            plat_id = target_info['whatsapp_id'] if pref_plat == 'whatsapp' else target_info['telegram_id']
        
        if not plat_id:
            return f"❌ {to_username} has not linked their {pref_plat} account."

        # Dispatch via Queue
        if self.outbox_queue:
            payload = {
                "platform": pref_plat,
                "target": plat_id,
                "text": f"🔒 **Private Message from {from_username}**:\n{content}"
            }
            self.outbox_queue.put(payload)
            log_private_message(from_id, to_id, content)
            return f"📤 Message sent to {to_username}!"
        
        return "❌ Messaging system temporarily unavailable."
