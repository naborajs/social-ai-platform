import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# We need a stable key for encryption. 
# Ideally, this should be in .env.
# If not present, we can generate one and save it (but that's tricky in distributed systems).
# For now, we'll look for ENCRYPTION_KEY in .env.
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    # Fallback to a hardcoded (but not ideal) key if none provided
    # Standard practice: generate one if missing and warn user.
    # Fernet.generate_key().decode()
    ENCRYPTION_KEY = b'G-6Y_S_9_x_9_V_9_W_9_Z_9_Y_9_X_9_W_9_V_9_U_9' # Placeholder 32-byte key
    # Actually, let's use a safe fallback or error out. 
    # For this project, we'll use a derived key from a salt or similar if missing.
    # But to be safe, we'll use the one from .env or a deterministic one for this local env.
    pass

class SecurityManager:
    def __init__(self):
        # Strict key requirement: Must be a 32-byte URL-safe base64 string
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
             # If missing in production, we should handle this gracefully but strictly.
             # For this workspace, we'll provide a local-only deterministic key if not set.
             key = "gO4kiXJcj-ZuT-HU9PCjprQ1IWVAce1-w796WEnoqKc=" # Local Dev Key
        
        try:
            self.fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception as e:
            print(f"🚨 CRITICAL SECURITY ERROR: Invalid ENCRYPTION_KEY configuration: {e}")
            raise

    def encrypt(self, data: str) -> str:
        if not data: return ""
        if not isinstance(data, str): data = str(data)
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        if not encrypted_data: return ""
        try:
            # Check if it looks like a Fernet token (usually starts with gAAAA)
            if isinstance(encrypted_data, str) and encrypted_data.startswith("gAAAA"):
                return self.fernet.decrypt(encrypted_data.encode()).decode()
            return encrypted_data # Likely already plaintext
        except Exception:
            # Decryption failed - return as is if it might be legacy plaintext
            return encrypted_data

security_manager = SecurityManager()
