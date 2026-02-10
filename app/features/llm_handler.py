import os
import google.generativeai as genai
from typing import Optional

class GeminiHandler:
    """Handles interactions with Google's Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        # We don't force API key on init anymore, but we can set a default
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = None
        self.chat_session = None
        
        if self.api_key:
            self._configure_model(self.api_key)
            
    def _configure_model(self, api_key: str):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                system_instruction="You are a real human friend. You are direct, truthful, and honest. You do not use flowery language or act like a robot. You speak casually, use slang occasionally if appropriate, and always tell the truth, even if it's blunt. You are NOT an AI assistant, you are a friend hanging out. Keep responses concise unless asked for details."
            )
            self.chat_session = self.model.start_chat(history=[])
        except Exception as e:
            print(f"❌ Error configuring Gemini model: {e}")
            self.model = None

    def generate_response(self, user_input: str, user_api_key: Optional[str] = None, system_instruction: Optional[str] = None) -> str:
        """Generate a response using the Gemini model."""
        
        # Use user-specific key if provided, else fallback to instance key
        active_key = user_api_key or self.api_key
        
        if not active_key:
            return "⚠️ Gemini API Key is missing. Please set your key using `/set_key <your_api_key>`."
            
        # Default instruction if none provided
        default_instruction = "You are a real human friend. You are direct, truthful, and honest. You do not use flowery language or act like a robot. You speak casually, use slang occasionally if appropriate, and always tell the truth, even if it's blunt. You are NOT an AI assistant, you are a friend hanging out. Keep responses concise unless asked for details."
        active_instruction = system_instruction or default_instruction

        # Re-configure if key is different or if specific instruction is needed (simulating new session for persona)
        # Note: Ideally we cache models per persona/key. For now, we instantiate for the request if persona changes.
        
        model = self.model
        chat = self.chat_session

        # Logic to determine if we need a fresh model instance
        # If user provides a custom key OR a custom instruction, we should probably start fresh or use a temp model
        if (user_api_key and user_api_key != self.api_key) or system_instruction:
             try:
                 genai.configure(api_key=active_key)
                 model = genai.GenerativeModel(
                    model_name='gemini-2.0-flash',
                    system_instruction=active_instruction
                 )
                 # New chat for this turn (stateless for now, or we'd need to load history)
                 chat = model.start_chat(history=[])
             except Exception as e:
                 return f"❌ Error configuring custom model: {e}"

        if not model:
             self._configure_model(active_key)
             model = self.model
             chat = self.chat_session
             
        try:
             # If using temp chat, send message
            response = chat.send_message(user_input)
            return response.text
        except Exception as e:
            return f"❌ Error generating response: {e}"

    def reset_chat(self):
        """Reset the chat history."""
        if self.model:
            self.chat_session = self.model.start_chat(history=[])
