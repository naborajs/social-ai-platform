from app.core.bot_core import UnifiedBot
from app.core.database import register_user, get_user_by_username, init_db
import os
import multiprocessing

def verify_v38():
    init_db()
    print("--- Verifying v3.8 Gold Features ---")
    
    # Setup test user
    username = "NishantTest"
    register_user(username, "test@ns.com", "password123", platform="telegram", platform_id="999888")
    
    queues = {
        "whatsapp": multiprocessing.Queue(),
        "telegram": multiprocessing.Queue()
    }
    bot = UnifiedBot(queues)
    
    # 1. Test Settings Menu
    print("\n[1] Testing /settings menu...")
    msg = bot.handle_message("/settings", "telegram", "999888")
    print(f"Response:\n{msg}")
    if "TrueFriend Settings Menu" in msg:
        print("✅ Settings menu displayed.")
    else:
        print("❌ Settings menu failed.")

    # 2. Test Mood Switch via /s
    print("\n[2] Testing /s mood sarcastic...")
    msg = bot.handle_message("/s mood sarcastic", "telegram", "999888")
    print(f"Response: {msg}")
    if "Sarcastic" in msg:
        print("✅ Mood switched successfully.")
    else:
        print("❌ Mood switch failed.")

    # 3. Test Usage Dashboard
    print("\n[3] Testing /usage dashboard...")
    msg = bot.handle_message("/usage", "telegram", "999888")
    print(f"Response:\n{msg}")
    if "TrueFriend Report" in msg:
        print("✅ Usage dashboard displayed.")
    else:
        print("❌ Usage dashboard failed.")

    # 4. Test Search
    print("\n[4] Testing /search...")
    msg = bot.handle_message("/search Nish", "telegram", "999888")
    print(f"Response:\n{msg}")
    if "Search Results" in msg:
        print("✅ Search functionality working.")
    else:
        print("❌ Search failed.")

    # 5. Test Profile Info
    print("\n[5] Testing /info...")
    msg = bot.handle_message(f"/info {username}", "telegram", "999888")
    print(f"Response:\n{msg}")
    if f"Profile: {username}" in msg and "Mutuals" in msg:
        print("✅ Profile card working.")
    else:
        print("❌ Profile card failed.")

    print("\n✨ v3.8 Verification Logic Check Complete! ✨")

if __name__ == "__main__":
    verify_v38()
