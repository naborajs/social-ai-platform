from app.core.database import set_state, get_state, clear_state, register_user
import re

class ConversationManager:
    """
    Handles interactive user flows (Registration, Onboarding).
    Uses a state machine approach backed by the database.
    """
    
    # States
    STATE_NONE = None
    STATE_REG_USERNAME = "REG_USERNAME"
    STATE_REG_EMAIL = "REG_EMAIL"
    STATE_REG_PASSWORD = "REG_PASSWORD"
    STATE_REG_AVATAR = "REG_AVATAR"
    STATE_REG_PERSONA = "REG_PERSONA"
    
    # Avatar Options (URLs or File IDs - using placeholders for now)
    AVATARS = {
        "1": "https://api.dicebear.com/7.x/adventurer/png?seed=Felix",
        "2": "https://api.dicebear.com/7.x/adventurer/png?seed=Aneka",
        "3": "https://api.dicebear.com/7.x/adventurer/png?seed=Midnight",
        "4": "https://api.dicebear.com/7.x/bottts/png?seed=123"
    }

    # Personas
    PERSONAS = {
        "1": "You are a supportive, enthusiastic best friend. You use emojis, give compliments, and encourage the user.",
        "2": "You are a sarcastic roast master. You make fun of the user playfully, you are witty, and you don't hold back.",
        "3": "You are a professional, highly efficient executive assistant. You are polite, concise, and formal.",
        "4": "You are a mystical wizard. You speak in riddles, use archaic language, and reference magic."
    }

    def __init__(self):
        pass

    def handle_input(self, platform_id, platform, text):
        """
        Main entry point for handling input based on current state.
        Returns: (response_text, media_url_or_options, is_flow_complete)
        """
        state, data = get_state(platform_id)
        
        if not state:
            return None, None, False

        text = text.strip()
        
        # --- Registration Flow ---
        
        if state == self.STATE_REG_USERNAME:
            # Validate Username (Simple check)
            if len(text) < 3:
                return "❌ Username must be at least 3 characters. Try again:", None, False
            
            # Save username, move to next step
            data['username'] = text
            set_state(platform_id, platform, self.STATE_REG_EMAIL, data)
            return "📧 Great! Now, what is your **Email Address**?", None, False

        elif state == self.STATE_REG_EMAIL:
            # Validate Email
            if "@" not in text or "." not in text:
                return "❌ That doesn't look like a valid email. Please try again:", None, False
                
            data['email'] = text
            set_state(platform_id, platform, self.STATE_REG_PASSWORD, data)
            return "🔐 Secure your account. Create a **Password**:", None, False

        elif state == self.STATE_REG_PASSWORD:
            if len(text) < 6:
                return "❌ Password must be at least 6 characters. Try again:", None, False
                
            data['password'] = text
            set_state(platform_id, platform, self.STATE_REG_AVATAR, data)
            
            # Show Avatar Options
            msg = "🎨 Choose your **Identity (Avatar)**:\n\n"
            msg += "1️⃣ Adventurer Felix\n2️⃣ Adventurer Aneka\n3️⃣ Midnight Warrior\n4️⃣ Retro Bot\n\nReply with the number (1-4) or type a custom URL."
            return msg, self.AVATARS, False # Return avatars dict for UI handling

        elif state == self.STATE_REG_AVATAR:
            avatar_url = text
            if text in self.AVATARS:
                avatar_url = self.AVATARS[text]
            
            data['avatar_url'] = avatar_url
            set_state(platform_id, platform, self.STATE_REG_PERSONA, data)
            
            msg = "🧠 **Final Step!** Choose my **Personality**:\n\n"
            msg += "1️⃣ 🤗 Best Friend (Supportive)\n2️⃣ 🔥 Roast Master (Sarcastic)\n3️⃣ 👔 Professional (Formal)\n4️⃣ 🧙‍♂️ Wizard (Mystical)\n\nReply with the number (1-4)."
            return msg, None, False

        elif state == self.STATE_REG_PERSONA:
            system_prompt = self.PERSONAS.get("1") # Default
            if text in self.PERSONAS:
                system_prompt = self.PERSONAS[text]
            
            from app.core.database import update_system_prompt
            
            # Finalize Registration
            success, msg = register_user(
                data['username'], 
                data['email'], 
                data['password'], 
                platform, 
                platform_id,
                avatar_url=data.get('avatar_url'),
                bio="New User"
            )
            
            # Update system prompt after registration (we could have passed it to register_user but simpler to update here or update register_user signature again. 
            # Ideally register_user should take it. But I didn't update register_user signature in DB step? 
            # Wait, I did update the DB *schema* but did I update `register_user` python function? 
            # I checked previous tool call: I updated `register_user` to take `avatar_url` and `bio`. 
            # I did NOT update it to take `system_prompt`.
            # So I should use `update_system_prompt` here.
            
            # Need to get user_id not returned by register_user directly (it returns msg).
            # But register_user returns (success, msg). 
            # We can use update_system_prompt if we can get the ID.
            # OR we can update register_user again.
            # Let's use `update_system_prompt` but we need `user_id`. `register_user` doesn't return `user_id`.
            # We can get user by platform_id immediately.
            
            from app.core.database import get_user_by_platform
            user = get_user_by_platform(platform, platform_id)
            if user:
                update_system_prompt(user[0], system_prompt)
            
            clear_state(platform_id)
            return msg + "\n\n🎉 Setup Complete! backend updated.", None, True

        return None, None, False

    def start_registration(self, platform_id, platform):
        """Start the registration flow."""
        set_state(platform_id, platform, self.STATE_REG_USERNAME, {})
        return "👋 Welcome! Let's get you set up.\n\nFirst, choose a unique **Username**:"
