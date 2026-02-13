from app.core.bot_core import UnifiedBot
from app.core.database import register_user, init_db, set_professional_account, follow_user
import os
import multiprocessing

def verify_v50():
    init_db()
    print("--- Verifying v5.0 Creator Edition Features ---")
    
    # Setup test users
    creator_id = 1
    follower_id = 2
    register_user("creator_king", "king@creators.com", "pass123", platform="telegram", platform_id="king_tg")
    register_user("fan_boy", "fan@users.com", "pass123", platform="telegram", platform_id="fan_tg")
    
    set_professional_account(creator_id, 1) # Set as professional
    
    queues = {
        "whatsapp": multiprocessing.Queue(),
        "telegram": multiprocessing.Queue()
    }
    bot = UnifiedBot(queues)
    
    # 1. Test Follow System
    print("\n[1] Testing Follow system...")
    success, msg = follow_user(follower_id, "creator_king")
    print(f"Follow Response: {msg}")
    if "following creator_king" in msg:
        print("✅ Follow logic verified.")
    else:
        print("❌ Follow logic failed.")

    # 2. Test Post Visibility & Notifications
    print("\n[2] Testing Post Visibility & Notifications...")
    # Public post should be in feed and notify followers
    res = bot.handle_message("/post Hello Fans! This is public. --public", "telegram", "king_tg")
    print(f"Post Response: {res}")
    
    # Private post should NOT be in public feed (logic check via feed)
    bot.handle_message("/post Secret for VIPs only. --private", "telegram", "king_tg")
    
    feed_msg = bot.handle_message("/feed", "telegram", "fan_tg")
    print(f"Feed Response:\n{feed_msg}")
    
    if "Hello Fans" in feed_msg and "Secret for VIPs" not in feed_msg:
        print("✅ Visibility filtering verified.")
    else:
        print("❌ Visibility filtering failed.")

    # 3. Test Analytics (Views)
    print("\n[3] Testing Analytics Dashboard...")
    # The view should have been logged when fan_boy called /feed
    stats_msg = bot.handle_message("/stats", "telegram", "king_tg")
    print(f"Stats Dashboard:\n{stats_msg}")
    if "Total Reach" in stats_msg and "1 views" in stats_msg:
        print("✅ Analytics reach counting verified.")
    else:
        print("❌ Analytics reach counting failed.")

    # 4. Test Professional Account Toggle
    print("\n[4] Testing /professional command...")
    msg = bot.handle_message("/professional", "telegram", "fan_tg")
    print(f"Response: {msg}")
    if "Professional Mode" in msg:
        print("✅ Self-upgrade to Professional verified.")
    else:
        print("❌ Self-upgrade failed.")

    print("\n✨ v5.0 Creator Edition Logic Check Complete! ✨")

if __name__ == "__main__":
    verify_v50()
