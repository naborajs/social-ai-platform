from app.core.bot_core import UnifiedBot
from app.core.database import register_user, init_db, set_verified_status
import os
import multiprocessing

def verify_v40():
    init_db()
    print("--- Verifying v4.0 Diamond Features ---")
    
    # Setup test user (Owner/Nishant)
    username = "nishant"
    register_user(username, "boss@ns.com", "password123", platform="telegram", platform_id="123456")
    set_verified_status(1, 1) # Set as verified
    
    queues = {
        "whatsapp": multiprocessing.Queue(),
        "telegram": multiprocessing.Queue()
    }
    bot = UnifiedBot(queues)
    
    # 1. Test Public Feed
    print("\n[1] Testing /post and /feed...")
    bot.handle_message("/post Hello world! This is v4.0 Diamond. 💎", "telegram", "123456")
    msg = bot.handle_message("/feed", "telegram", "123456")
    print(f"Response:\n{msg}")
    if "Public Social Feed" in msg and "Hello world" in msg:
        print("✅ Feed logic verified.")
    else:
        print("❌ Feed logic failed.")

    # 2. Test Stories
    print("\n[2] Testing /story and /stories...")
    bot.handle_message("/story Lunch with my AI friend! 🥙", "telegram", "123456")
    msg = bot.handle_message("/stories", "telegram", "123456")
    print(f"Response:\n{msg}")
    if "Active Stories" in msg and "Lunch with my AI" in msg:
        print("✅ Story logic verified.")
    else:
        print("❌ Story logic failed.")

    # 3. Test Broadcast (Creator Tool)
    print("\n[3] Testing /broadcast...")
    msg = bot.handle_message("/broadcast New video drops at 5PM! 📹", "telegram", "123456")
    print(f"Response: {msg}")
    if "Broadcast sent" in msg:
        print("✅ Broadcast system verified.")
    else:
        print("❌ Broadcast system failed.")

    # 4. Test Caption Tool
    print("\n[4] Testing /caption...")
    msg = bot.handle_message("/caption gaming laptops", "telegram", "123456")
    print(f"Response (truncated):\n{msg[:100]}...")
    if "caption" in msg.lower() or "script" in msg.lower():
        print("✅ Caption tool AI verified.")
    else:
        print("❌ Caption tool failed.")

    # 5. Test Imagine Tool
    print("\n[5] Testing /imagine...")
    msg = bot.handle_message("/imagine a diamond robot", "telegram", "123456")
    print(f"Response: {msg}")
    if "Diamond Engine" in msg:
        print("✅ Imagine logic verified.")
    else:
        print("❌ Imagine logic failed.")

    print("\n✨ v4.0 Diamond Logic Check Complete! ✨")

if __name__ == "__main__":
    verify_v40()
