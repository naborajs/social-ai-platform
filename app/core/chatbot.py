import json
import re
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Imports from app features
try:
    from app.features.llm_handler import GeminiHandler
    from app.features.love_calculator import LoveCalculator
except ImportError:
    # Fallback if running as script from root without app package resolution (legacy)
    # But ideally this should run as module
    pass

# Initialize colorama
init(autoreset=True)

load_dotenv()

class ChatBot:
    """A realistic chatbot with proper error handling and emoji support."""
    
    def __init__(self):
        self.name = "ChatBot"
        self.version = "2.0"
        self.conversation_history: List[Dict[str, str]] = []
        self.user_name: Optional[str] = None
        self.emotion_state = "neutral"
        self.knowledge_base = self._initialize_knowledge_base()
        self.response_templates = self._initialize_response_templates()
        self.greeting_count = 0
        self.error_count = 0
        self.love_calculator = LoveCalculator()
        try:
            self.llm_handler = GeminiHandler()
            print(f"{Fore.GREEN}✅ Gemini API Connected!{Style.RESET_ALL}")
        except Exception as e:
            self.llm_handler = None
            print(f"{Fore.RED}⚠️ Gemini API not connected: {e}{Style.RESET_ALL}")
        
    def _initialize_knowledge_base(self) -> Dict[str, List[str]]:
        """Initialize the knowledge base with common topics."""
        return {
            "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"],
            "goodbye": ["bye", "goodbye", "see you", "farewell", "exit", "quit", "quit chat"],
            "name": ["what is your name", "who are you", "what do you call yourself"],
            "weather": ["weather", "rain", "sunny", "temperature", "forecast"],
            "time": ["what time", "what's the time", "current time", "tell me time"],
            "help": ["help", "assist", "support", "how can you help"],
            "joke": ["joke", "funny", "make me laugh", "tell me something funny"],
            "thanks": ["thank", "thanks", "thank you", "appreciate"],
            "math": ["calculate", "math", "plus", "minus", "multiply", "divide"],
            "feelings": ["how are you", "how is it going", "what's up", "how do you feel"]
        }
    
    def _initialize_response_templates(self) -> Dict[str, List[str]]:
        """Initialize response templates for different intents."""
        return {
            "greeting": [
                "Hello! 👋 I'm {bot_name}, nice to meet you! How can I help you today?",
                "Hi there! 😊 Welcome! What can I do for you?",
                "Hey! 👋 Great to see you! What's on your mind?",
                "Greetings! 🎉 I'm here to help. What do you need?",
            ],
            "goodbye": [
                "Goodbye! 👋 It was nice talking to you. See you soon!",
                "Bye! 😊 Take care and have a great day!",
                "See you later! 🚀 Thanks for chatting with me!",
                "Farewell! 👋 Come back anytime!",
            ],
            "name": [
                "I'm {bot_name}! 🤖 A helpful chatbot created to assist you.",
                "My name is {bot_name}! 😊 Nice to meet you!",
                "I go by {bot_name}! 👋 How can I help?",
            ],
            "help": [
                "I can help you with: greetings, jokes, weather info, time, math problems, and general conversation! 🆘",
                "I'm here to assist! 🤝 You can ask me jokes, tell the time, do math, or just chat!",
                "Of course! 😊 I can tell jokes, give time, help with math, and much more!",
            ],
            "joke": [
                "Why don't programmers like nature? 🌳 It has too many bugs! 😄",
                "How many programmers does it take to change a light bulb? 💡 None, that's a hardware problem! 🔧",
                "Why do Java developers wear glasses? 👓 Because they can't C#! 😄",
                "What's a programmer's favorite hangout place? 🍺 Foo Bar!",
            ],
            "time": [
                "The current time is {time}! ⏰",
                "It's {time} right now! 🕐",
                "Current time: {time}! ⌚",
            ],
            "weather": [
                "I don't have real-time weather data, 🌤️ but I'd suggest checking a weather website!",
                "Weather info isn't available in my system, 🌈 try a weather app instead!",
            ],
            "thanks": [
                "You're welcome! 😊 Anytime!",
                "Happy to help! 🎉",
                "No problem at all! 👍",
                "Glad I could assist! 🌟",
            ],
            "feelings": [
                "I'm doing great, thanks for asking! 😊 How about you?",
                "I'm functioning perfectly! 🤖 How are you doing?",
                "All systems go! 🚀 What about you?",
                "I'm feeling helpful! 💪 How are you?",
            ],
            "default": [
                "That's interesting! 🤔 Tell me more about that.",
                "I see what you mean! 😊 Can you elaborate?",
                "That's a good point! 💭 What else?",
                "Interesting perspective! 🧠 I'd like to know more!",
            ]
        }
    
    def get_current_time(self) -> str:
        """Get the current time in HH:MM:SS format."""
        try:
            return datetime.now().strftime("%H:%M:%S")
        except Exception as e:
            self.error_count += 1
            return "Unable to retrieve time ⏰"
    
    def preprocess_input(self, user_input: str) -> str:
        """Preprocess user input by cleaning and normalizing."""
        try:
            if not isinstance(user_input, str):
                raise TypeError("Input must be a string!")
            
            user_input = user_input.strip().lower()
            user_input = re.sub(r'\s+', ' ', user_input)
            return user_input
        except TypeError as e:
            self.error_count += 1
            return ""
        except Exception as e:
            self.error_count += 1
            return ""
    
    def extract_intent(self, user_input: str) -> Tuple[str, float]:
        """Extract intent from user input with confidence score."""
        try:
            processed_input = self.preprocess_input(user_input)
            
            if not processed_input:
                return "unknown", 0.0
            
            intent_scores = {}
            
            for intent, keywords in self.knowledge_base.items():
                score = 0.0
                for keyword in keywords:
                    if keyword in processed_input:
                        score += 1
                
                if score > 0:
                    intent_scores[intent] = score / len(keywords)
            
            if not intent_scores:
                return "default", 0.0
            
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            
            return best_intent, confidence
        except Exception as e:
            self.error_count += 1
            return "default", 0.0
    
    def extract_user_info(self, user_input: str) -> None:
        """Extract user information from input."""
        try:
            processed_input = self.preprocess_input(user_input)
            
            if "my name is" in processed_input:
                name_match = re.search(r"my name is (.+?)(?:\.|$|!|\?)", processed_input)
                if name_match:
                    self.user_name = name_match.group(1).strip().title()
            elif "i'm" in processed_input and "chatbot" not in processed_input:
                name_match = re.search(r"i'm (.+?)(?:\.|$|!|\?)", processed_input)
                if name_match:
                    self.user_name = name_match.group(1).strip().title()
        except Exception as e:
            self.error_count += 1
    
    def handle_math(self, user_input: str) -> Optional[str]:
        """Handle simple math operations."""
        try:
            processed_input = self.preprocess_input(user_input)
            
            math_patterns = [
                r"(\d+)\s*\+\s*(\d+)",
                r"(\d+)\s*-\s*(\d+)",
                r"(\d+)\s*\*\s*(\d+)",
                r"(\d+)\s*/\s*(\d+)",
            ]
            
            for pattern in math_patterns:
                match = re.search(pattern, processed_input)
                if match:
                    num1, num2 = int(match.group(1)), int(match.group(2))
                    
                    if '+' in match.group(0):
                        result = num1 + num2
                        return f"🧮 {num1} + {num2} = {result}"
                    elif '-' in match.group(0):
                        result = num1 - num2
                        return f"🧮 {num1} - {num2} = {result}"
                    elif '*' in match.group(0):
                        result = num1 * num2
                        return f"🧮 {num1} × {num2} = {result}"
                    elif '/' in match.group(0):
                        if num2 == 0:
                            return "❌ Cannot divide by zero! 0️⃣"
                        result = num1 / num2
                        return f"🧮 {num1} ÷ {num2} = {result:.2f}"
            
            return None
        except ZeroDivisionError:
            self.error_count += 1
            return "❌ Division by zero is not allowed! 0️⃣"
        except ValueError:
            self.error_count += 1
            return "❌ Invalid number format! 🚨"
        except Exception as e:
            self.error_count += 1
            return "❌ Error processing math: Something unexpected happened!"
    
    def generate_response(self, user_input: str, user_api_key: Optional[str] = None, system_instruction: Optional[str] = None) -> str:
        """Generate an appropriate response based on user input."""
        try:
            if not user_input:
                return "❌ Please say something! I'm listening... 👂"
            
            # Check for specific commands first
            if user_input.lower() == "time":
                 return f"The current time is {self.get_current_time()}! ⏰"

            # Use Gemini for all other responses
            if self.llm_handler:
                return self.llm_handler.generate_response(user_input, user_api_key=user_api_key, system_instruction=system_instruction)
            
            # Fallback if LLM is not available
            intent, confidence = self.extract_intent(user_input)
            
            self.extract_user_info(user_input)
            
            math_result = self.handle_math(user_input)
            if math_result:
                return math_result

            # Check for love calculator command
            if "love" in user_input.lower() and ("and" in user_input.lower() or "with" in user_input.lower()):
                 # Extract names - simple heuristic
                 words = user_input.split()
                 names = [w for w in words if w.lower() not in ["love", "calculate", "between", "and", "with", "score", "percentage", "is", "what", "the"]]
                 if len(names) >= 2:
                     return self.love_calculator.calculate_love(names[0], names[1])
            
            if intent in self.response_templates:
                response = random.choice(self.response_templates[intent])
            else:
                response = random.choice(self.response_templates["default"])
            
            response = response.format(
                bot_name=self.name,
                time=self.get_current_time(),
                user_name=self.user_name or "friend"
            )
            
            if intent == "greeting":
                self.greeting_count += 1
                if self.user_name:
                    response = f"Hello {self.user_name}! 👋 {response}"
            
            return response
        except Exception as e:
            self.error_count += 1
            return f"❌ Unexpected error occurred! Please try again. 🔧 Error: {e}"
    
    def save_conversation(self, filename: str = "conversation_log.json") -> bool:
        """Save conversation history to a file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            self.error_count += 1
            print(f"❌ Error saving conversation: {e}")
            return False
        except Exception as e:
            self.error_count += 1
            print(f"❌ Unexpected error while saving: {e}")
            return False
    
    def load_conversation(self, filename: str = "conversation_log.json") -> bool:
        """Load conversation history from a file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)
            return True
        except FileNotFoundError:
            print("⚠️ Conversation file not found!")
            return False
        except json.JSONDecodeError:
            self.error_count += 1
            print("❌ Error decoding conversation file!")
            return False
        except Exception as e:
            self.error_count += 1
            print(f"❌ Error loading conversation: {e}")
            return False
    
    def display_stats(self) -> None:
        """Display chatbot statistics."""
        try:
            print("\n" + f"{Fore.CYAN}="*50)
            print(f"{Fore.YELLOW}📊 CHATBOT STATISTICS")
            print(f"{Fore.CYAN}="*50)
            print(f"👤 Bot Name: {Fore.GREEN}{self.name}{Style.RESET_ALL}")
            print(f"📌 Bot Version: {Fore.GREEN}{self.version}{Style.RESET_ALL}")
            print(f"💬 Total Messages: {Fore.BLUE}{len(self.conversation_history)}{Style.RESET_ALL}")
            print(f"👋 Greeting Count: {Fore.BLUE}{self.greeting_count}{Style.RESET_ALL}")
            print(f"⚠️ Error Count: {Fore.RED}{self.error_count}{Style.RESET_ALL}")
            if self.user_name:
                print(f"👥 User Name: {Fore.MAGENTA}{self.user_name}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}="*50 + f"{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"{Fore.RED}❌ Error displaying stats: {e}{Style.RESET_ALL}")

    def chat(self) -> None:
        """Start the main chatbot loop."""
        try:
            print("\n" + f"{Fore.CYAN}🤖 "*20)
            print(f"{Fore.YELLOW}Welcome to {self.name}! 🎉{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Type 'quit' or 'exit' to end the conversation.")
            print(f"Type 'stats' to see chatbot statistics.")
            print(f"Type 'help' for available commands.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}🤖 "*20 + f"{Style.RESET_ALL}\n")
            
            while True:
                try:
                    user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}").strip()
                    
                    if not user_input:
                        print(f"{Fore.YELLOW}Bot: Please say something! 🤔{Style.RESET_ALL}\n")
                        continue
                    
                    if user_input.lower() in ["quit", "exit"]:
                        farewell_response = random.choice(self.response_templates["goodbye"])
                        print(f"{Fore.CYAN}Bot: {farewell_response}{Style.RESET_ALL}\n")
                        self.save_conversation()
                        break
                    
                    if user_input.lower() == "stats":
                        self.display_stats()
                        continue
                    
                    if user_input.lower() == "help":
                        print(f"\n{Fore.CYAN}Bot: 📚 I can help with:{Style.RESET_ALL}")
                        print("  • Greetings and casual chat 💬")
                        print("  • Jokes and humor 😄")
                        print("  • Current time ⏰")
                        print("  • Basic math operations 🧮")
                        print("  • Love Calculator 💖 (e.g., 'love John and Mary')")
                        print("  • Weather inquiries 🌤️")
                        print("  • General questions 🤔")
                        print("  Commands: 'stats', 'help', 'quit'\n")
                        continue
                    
                    response = self.generate_response(user_input)
                    # Check if response already has color codes (like from love calculator)
                    if "\x1b[" in response:
                         print(f"{Fore.CYAN}Bot:{Style.RESET_ALL} {response}\n")
                    else:
                         print(f"{Fore.CYAN}Bot: {response}{Style.RESET_ALL}\n")
                    
                    self.conversation_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "user": user_input,
                        "bot": response
                    })
                    
                except KeyboardInterrupt:
                    print(f"\n\n{Fore.RED}Bot: Session interrupted! 🛑 Saving conversation...{Style.RESET_ALL}\n")
                    self.save_conversation()
                    break
                except Exception as e:
                    self.error_count += 1
                    print(f"{Fore.RED}Bot: ❌ An error occurred: {e}{Style.RESET_ALL}\n")
                    
        except Exception as e:
            self.error_count += 1
            print(f"{Fore.RED}❌ Critical error in chat loop: {e}{Style.RESET_ALL}")
        finally:
            self.save_conversation()
            print(f"{Fore.YELLOW}👋 Thank you for chatting! Goodbye! 🚀{Style.RESET_ALL}")

