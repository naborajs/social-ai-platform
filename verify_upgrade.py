from app.core.bot_core import UnifiedBot
from app.core.error_handler import error_handler
from app.core.user_flow import ConversationManager
from unittest.mock import MagicMock
import os

def test_onboarding_flow():
    print("\n--- Testing Onboarding Flow ---")
    cm = ConversationManager()
    welcome = cm.start_registration("test_user_1", "whatsapp")
    print(f"Welcome Message: {welcome}")
    
    # Simulate first step
    response, _, _ = cm.handle_input("test_user_1", "whatsapp", "Nishant")
    print(f"Step 2 (Email) Response: {response}")
    
    if "[Step 2/6]" in response:
        print("✅ Step indicators working.")
    else:
        print("❌ Step indicators missing.")

def test_error_handling():
    print("\n--- Testing Error Handling ---")
    bot = UnifiedBot()
    # Simulate a crash in handle_message by providing invalid input or mocking
    try:
        # Intentionally cause an error if possible, or just call handler
        res = error_handler.handle_exception(Exception("Test Error"), platform="telegram", platform_id="123", context="Verification")
        print(f"ErrorHandler Response: {res}")
        if any(kw in res for kw in ["Oops", "bump", "My apologies", "Whoops"]):
            print("✅ ErrorHandler returned a graceful message.")
        else:
            print("❌ ErrorHandler message unexpected.")
    except Exception as e:
        print(f"❌ ErrorHandler itself failed: {e}")

def test_bot_commands():
    print("\n--- Testing Premium Commands ---")
    bot = UnifiedBot()
    help_text = bot.handle_message("/help", "telegram", "123")
    if "TrueFriend AI Experience" in help_text:
        print("✅ help command upgraded.")
    else:
        print("❌ help command not updated.")
        
    about_text = bot.handle_message("/about", "telegram", "123")
    if "👑 TrueFriend Premium AI 👑" in about_text:
        print("✅ about command upgraded.")
    else:
        print("❌ about command not updated.")

if __name__ == "__main__":
    test_onboarding_flow()
    test_error_handling()
    test_bot_commands()
    print("\n✨ Verification Complete!")
