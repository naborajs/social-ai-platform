from app.core.chatbot import ChatBot
from app.features.love_calculator import LoveCalculator

def verify():
    print("Testing Love Calculator...")
    lc = LoveCalculator()
    result = lc.calculate_love("Romeo", "Juliet")
    print(f"Result: {result}")
    
    print("\nInitializing ChatBot...")
    try:
        bot = ChatBot()
        print("ChatBot initialized successfully.")
        
        # Test love command processing
        response = bot.generate_response("love Romeo and Juliet")
        print(f"Bot Response to love command: {response}")
        
    except Exception as e:
        print(f"Error initializing ChatBot: {e}")

if __name__ == "__main__":
    verify()
