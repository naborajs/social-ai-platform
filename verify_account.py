from database import register_user, verify_user, change_password, recover_account, change_username
import sqlite3
import os

DB_NAME = "bot_data.db"

def verify_account_management():
    print("🧪 Testing Account Management...")
    
    # Setup test user
    test_user = "security_test_user"
    test_pass = "secure123"
    
    # Register
    print(f"👉 Registering {test_user}...")
    success, msg = register_user(test_user, test_pass)
    print(f"Result: {msg}")
    
    if "Backup Key" not in msg:
        print("❌ Recovery key not returned in registration message!")
        return

    # Extract recovery key (simple parsing)
    import re
    match = re.search(r"`([a-f0-9]+)`", msg)
    if not match:
        print("❌ Could not parse recovery key.")
        return
    recovery_key = match.group(1)
    print(f"🔑 Recovery Key extracted: {recovery_key}")
    
    # Login
    print("👉 Verifying Login...")
    user_id = verify_user(test_user, test_pass)
    if not user_id:
        print("❌ Login failed after registration.")
        return
    print("✅ Login successful.")
    
    # Change Password
    print("👉 Changing Password...")
    change_password(user_id, "newpass456")
    
    # Verify Old Password Fails
    if verify_user(test_user, test_pass):
        print("❌ Old password still works!")
    else:
        print("✅ Old password rejected.")
        
    # Verify New Password Works
    if verify_user(test_user, "newpass456"):
        print("✅ New password verified.")
    else:
         print("❌ New password failed.")
         
    # Account Recovery
    print("👉 Testing Account Recovery...")
    success, msg = recover_account(recovery_key, "recovered789")
    print(f"Recovery Result: {msg}")
    
    if verify_user(test_user, "recovered789"):
        print("✅ Login with recovered password successful.")
    else:
        print("❌ Recovery failed to update password.")

    print("\n✅ Account Management Verification Complete!")

if __name__ == "__main__":
    verify_account_management()
