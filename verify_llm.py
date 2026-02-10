import os
from llm_handler import GeminiHandler
from dotenv import load_dotenv

load_dotenv()
import sys
sys.stdout.reconfigure(encoding='utf-8')

def verify_gemini():
    print("🔍 Checking Google API Key...")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "your_google_api_key_here" in api_key:
        print("❌ Error: GOOGLE_API_KEY not found or not set in .env file.")
        return

    print("✅ API Key found.")
    
    print("🤖 Initializing Gemini Handler...")
    try:
        handler = GeminiHandler()
        print("✅ Handler initialized.")
        
        print("💬 Testing response generation...")
        response = handler.generate_response("Hello, are you working?")
        print(f"✅ Response received: {response}")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")

if __name__ == "__main__":
    verify_gemini()
