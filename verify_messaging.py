import sys
import time
import multiprocessing
from app.core.bot_core import UnifiedBot
from app.core.database import register_user, verify_user, send_friend_request, accept_friend_request, set_preferred_platform, update_platform_id

def safe_print(msg):
    sys.__stdout__.write(str(msg).encode('ascii', 'ignore').decode('ascii') + "\n")
    sys.__stdout__.flush()

def verify_messaging():
    safe_print("[+] Testing Advanced Messaging & Routing...")
    
    # 1. Setup
    ts = int(time.time())
    user1 = f"alice_{ts}"
    user2 = f"bob_{ts}"
    
    register_user(user1, f"alice{ts}@test.com", "pass123", "whatsapp", f"wa_alice_{ts}")
    register_user(user2, f"bob{ts}@test.com", "pass123", "telegram", f"tg_bob_{ts}")
    
    id1 = verify_user(user1, "pass123")
    id2 = verify_user(user2, "pass123")
    
    update_platform_id(id1, "whatsapp", f"wa_alice_{ts}")
    update_platform_id(id2, "telegram", f"tg_bob_{ts}")
    
    send_friend_request(id1, user2)
    accept_friend_request(id2, user1)
    
    set_preferred_platform(id2, "telegram")
    
    # 2. Test Dispatch via Queue
    queue = multiprocessing.Queue()
    bot = UnifiedBot(queue)
    
    safe_print(f"\n-> {user1} sending private message to {user2}...")
    res = bot.handle_message(f"/msg {user2} Hello Bob!", "whatsapp", f"wa_alice_{ts}")
    safe_print(f"Result: {res}")
    
    if not queue.empty():
        item = queue.get()
        safe_print(f"Queue Item: {item}")
        assert item['platform'] == 'telegram'
        assert item['target'] == f"tg_bob_{ts}"
        assert "Hello Bob!" in item['text']
        safe_print("[OK] Message successfully routed to Queue for Telegram!")
    else:
        safe_print("[!!] Error: Message not found in Queue.")
    
    # 3. Test Routing Change
    set_preferred_platform(id2, "whatsapp")
    update_platform_id(id2, "whatsapp", f"wa_bob_{ts}")
    
    safe_print(f"\n-> {user1} sending another message (Bob changed preference to WA)...")
    res = bot.handle_message(f"/msg {user2} Are you there?", "whatsapp", f"wa_alice_{ts}")
    safe_print(f"Result: {res}")
    
    if not queue.empty():
        item = queue.get()
        safe_print(f"Queue Item: {item}")
        assert item['platform'] == 'whatsapp'
        assert item['target'] == f"wa_bob_{ts}"
        safe_print("[OK] Message successfully routed to Queue for WhatsApp!")
    
    # 4. Test Block/Privacy
    from app.core.database import block_user
    block_user(id2, user1)
    safe_print(f"\n-> {user1} trying to message {user2} after being blocked...")
    res = bot.handle_message(f"/msg {user2} Unblock me!", "whatsapp", f"wa_alice_{ts}")
    safe_print(f"Result: {res}")
    assert "blocked" in str(res).lower()
    safe_print("[OK] Privacy guard active.")

    safe_print("\n[+] Advanced Messaging Verification Complete!")

if __name__ == "__main__":
    verify_messaging()
