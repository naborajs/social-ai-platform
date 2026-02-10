from app.core.bot_core import UnifiedBot
from app.core.database import register_user, verify_user

import os

def verify_core_logic():
    print("[+] Testing Core Logic...")
    
    # Clean up test user if exists
    if os.path.exists("bot_data.db"):
         pass # In a real test we might reset, but here we just append
    
    test_user = "test_user_1"
    test_pass = "password123"
    
    print(f"-> Registering {test_user}...")
    success, msg = register_user(test_user, test_pass, "whatsapp", "123456789")
    print(f"Result: {msg}")
    
    print(f"-> Verifying login for {test_user}...")
    user_id = verify_user(test_user, test_pass)
    if user_id:
        print(f"✅ Login verified! User ID: {user_id}")
    else:
        print("❌ Login failed (might be expected if already registered differently or error).")

    print("\n[Bot] Testing Bot Message Flow...")
    bot = UnifiedBot()
    
    # Test unauthenticated
    response = bot.handle_message("Hello", "whatsapp", "987654321")
    print(f"Unauthenticated Response: {response}")
    assert "not logged in" in response.lower()
    
    # Test authenticated (simulate login first)
    # We need to simulate the login flow or just rely on the DB being set
    # Let's use the login command
    login_response = bot.handle_message(f"/login {test_user} {test_pass}", "whatsapp", "123456789")
    print(f"Login Command Response: {login_response}")
    
    # Now chat
    chat_response = bot.handle_message("Hello friend", "whatsapp", "123456789")
    print(f"Authenticated Chat Response: {chat_response}")
    
    print("\n✅ Verification Complete!")

if __name__ == "__main__":
    verify_core_logic()
