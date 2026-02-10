from colorama import Fore, Style, init
import random

init(autoreset=True)

class LoveCalculator:
    def calculate_love(self, name1: str, name2: str) -> str:
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        
        # simple deterministic algorithm based on character codes
        combined_names = name1 + name2
        score = 0
        for char in combined_names:
            score += ord(char)
        
        # deterministic percentage
        percentage = (score * 7) % 101
        
        if percentage > 85:
            message = "💖 A Match Made in Heaven! 💖"
        elif percentage > 60:
            message = "❤️ Great Potential! ❤️"
        elif percentage > 40:
            message = "💛 Could Work Out! 💛"
        else:
            message = "💔 Maybe Just Friends? 💔"
            
        return f"\n{Fore.MAGENTA}Love Calculator Results:{Style.RESET_ALL}\n" \
               f"{Fore.CYAN}{name1.title()} + {name2.title()} = {percentage}%{Style.RESET_ALL}\n" \
               f"{Fore.YELLOW}{message}{Style.RESET_ALL}"
