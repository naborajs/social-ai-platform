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
    STATE_REG_ACCOUNT_TYPE = "REG_ACCOUNT_TYPE"
    STATE_REG_EMAIL = "REG_EMAIL"
    STATE_REG_PASSWORD = "REG_PASSWORD"
    STATE_REG_GENDER = "REG_GENDER"
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
        "1": "You are a supportive, enthusiastic best friend. You use emojis, give compliments, and encourage the user with a warm, caring vibe.",
        "2": "You are a sarcastic roast master. You make fun of the user playfully, you are witty, sassy, and never hold back on the humor.",
        "3": "You are a professional, highly efficient executive assistant. You are polite, concise, formal, and focused on excellence.",
        "4": "You are a mystical wizard. You speak in riddles, use archaic language, and reference ancient magic and hidden wisdom."
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
                return "⚠️ *Username must be at least 3 characters.* Try again:", None, False
            
            from app.core.database import get_user_by_username
            if get_user_by_username(text):
                return f"❌ *The username '{text}' is already taken.* Please choose another one:", None, False

            # Save username, move to next step
            data['username'] = text
            set_state(platform_id, platform, self.STATE_REG_ACCOUNT_TYPE, data)
            return (
                "👑 [Step 2/7] **Choose your Path!**\n\n"
                "What kind of account would you like?\n"
                "1️⃣ **Personal** (Casual AI friendship)\n"
                "2️⃣ **Professional** (Creator tools & Analytics)\n\n"
                "_Reply with **1 or 2** to select._"
            ), None, False

        elif state == self.STATE_REG_ACCOUNT_TYPE:
            acc_type = "professional" if text == "2" else "personal"
            data['account_type'] = acc_type
            data['is_professional'] = 1 if acc_type == "professional" else 0
            
            set_state(platform_id, platform, self.STATE_REG_EMAIL, data)
            return "✨ [Step 3/7] **Great choice!**\n\nWhat is your **Email Address**?\n\n_This helps us secure your account and recover it if you ever forget your password._", None, False

        elif state == self.STATE_REG_EMAIL:
            # Validate Email
            if "@" not in text or "." not in text:
                return "⚠️ *That doesn't look like a valid email.* Please try again:", None, False
                
            data['email'] = text
            set_state(platform_id, platform, self.STATE_REG_PASSWORD, data)
            return "🔐 [Step 4/7] **Let's keep it secure!**\n\nCreate a **Strong Password**:\n\n_Tip: Use a mix of letters and numbers for maximum safety._", None, False

        elif state == self.STATE_REG_PASSWORD:
            if len(text) < 6:
                return "⚠️ *Your password should be at least 6 characters.* Try again:", None, False
                
            data['password'] = text
            set_state(platform_id, platform, self.STATE_REG_GENDER, data)
            return "👤 [Step 5/7] **Tell me about yourself.**\n\nWhat is your **Gender**? (he/she)\n\n_I'll use this to tailor my tone and how I address you!_", None, False

        elif state == self.STATE_REG_GENDER:
            gender = "she" if "she" in text.lower() else "he"
            data['gender'] = gender
            # Auto-align AI gender with user gender
            data['ai_gender'] = "she" if gender == "he" else "he" # Typical companion default
            
            set_state(platform_id, platform, self.STATE_REG_AVATAR, data)
            
            # Show Avatar Options
            msg = "🎨 [Step 6/7] **Let's pick an Identity!**\n\nChoose your **Avatar**:\n\n"
            msg += "1️⃣ **Adventurer Felix** (Bold & Dynamic)\n"
            msg += "2️⃣ **Adventurer Aneka** (Wise & Swift)\n"
            msg += "3️⃣ **Midnight Warrior** (Sleek & Mysterious)\n"
            msg += "4️⃣ **Retro Bot** (Classic & Techie)\n\n"
            msg += "_Reply with **1, 2, 3, or 4** to select your look._"
            return msg, self.AVATARS, False 

        elif state == self.STATE_REG_AVATAR:
            avatar_url = text
            if text in self.AVATARS:
                avatar_url = self.AVATARS[text]
            
            data['avatar_url'] = avatar_url
            set_state(platform_id, platform, self.STATE_REG_PERSONA, data)
            
            msg = "🧠 [Step 7/7] **The Final Touch!**\n\nHow should I act around you? Choose my **Personality**:\n\n"
            msg += "1️⃣ 🤗 **Best Friend** (Always here for you)\n"
            msg += "2️⃣ 🔥 **Roast Master** (Fast & Sarcastic)\n"
            msg += "3️⃣ 👔 **Professional** (Efficient & Polished)\n"
            msg += "4️⃣ 🧙‍♂️ **Mystical Wizard** (Wise & Enigmatic)\n\n"
            msg += "_Reply with **1, 2, 3, or 4** to breathe life into your AI._"
            return msg, None, False

        elif state == self.STATE_REG_PERSONA:
            system_prompt = self.PERSONAS.get("1") # Default
            if text in self.PERSONAS:
                system_prompt = self.PERSONAS[text]
            
            from app.core.database import update_system_prompt
            
            # Finalize Registration
            from app.core.database import set_professional_account
            success, msg = register_user(
                data['username'], 
                data['email'], 
                data['password'], 
                platform, 
                platform_id,
                avatar_url=data.get('avatar_url'),
                bio="Professional Content Creator" if data.get('is_professional') else "Member of the TrueFriend Community"
            )
            
            if not success:
                return f"❌ **Registration Failed**: {msg}\n\n_Please try again or contact support._", None, False

            from app.core.database import get_user_by_platform, set_user_personalization
            user = get_user_by_platform(platform, platform_id)
            if user:
                u_id = user[0]
                update_system_prompt(u_id, system_prompt)
                set_user_personalization(u_id, gender=data.get('gender'), ai_gender=data.get('ai_gender'))
                if data.get('is_professional'):
                    set_professional_account(u_id, 1)
            
            clear_state(platform_id)
            
            onboarding_msg = "🎊 *Welcome to the Family!* 🎊\n\n"
            onboarding_msg += f"Your account for **{data['username']}** is officially active. I've set up your profile and personality just the way you like it.\n\n"
            onboarding_msg += "💡 **How to make the most of TrueFriend:**\n"
            onboarding_msg += "• Type `/help` to explore all my secret powers 🌟\n"
            onboarding_msg += "• Use `/mood` to change how I talk to you anytime ✨\n"
            onboarding_msg += "• `/friends` is where your squad lives! Add someone with `/add_friend` 👥\n\n"
            onboarding_msg += "_I'm so excited to start this journey with you. What's on your mind?_"
            
            return onboarding_msg, None, True

        return None, None, False

    def start_registration(self, platform_id, platform):
        """Start the registration flow with a premium welcome."""
        set_state(platform_id, platform, self.STATE_REG_USERNAME, {})
        welcome = (
            "🚀 **Welcome to TrueFriend AI**\n\n"
            "I'm about to become your favorite companion, but first, I need a few details to build your unique profile.\n\n"
            "✨ [Step 1/7] Let's begin!\n"
            "**Choose a unique Username:**"
        )
        return welcome
