from app.core.database import register_user, verify_user, send_friend_request, get_friend_requests, accept_friend_request, get_friends, create_group, join_group
import os
import time

def verify_social():
    print("[+] Testing Social Features...")
    
    ts = int(time.time())
    user_a = f"user_a_{ts}"
    user_b = f"user_b_{ts}"
    
    # 1. Setup Test Users
    print(f"-> Registering {user_a} and {user_b}...")
    register_user(user_a, f"a{ts}@test.com", "pass123", "whatsapp", f"wa_a_{ts}")
    register_user(user_b, f"b{ts}@test.com", "pass123", "whatsapp", f"wa_b_{ts}")
    
    id_a = verify_user(user_a, "pass123")
    id_b = verify_user(user_b, "pass123")
    
    print(f"IDs: User A={id_a}, User B={id_b}")
    
    if not id_a or not id_b:
        print("!! Critical error: User registration failed.")
        # Try to register manually once to see error
        res = register_user(user_a + "_remade", "remade@test.com", "pass123")
        print(f"Retry Result: {res}")
        return

    # 2. Test Friend Request
    print(f"\n-> Sending friend request from {user_a} to {user_b}...")
    success, msg = send_friend_request(id_a, user_b)
    print(f"Result: {msg.encode('ascii', 'ignore').decode('ascii')}")
    
    # 3. Test View Requests
    print(f"\n-> {user_b} checking requests...")
    requests = get_friend_requests(id_b)
    print(f"Pending Requests for B: {requests}")
    assert user_a in requests
    
    # 4. Test Accept Friend
    print(f"\n-> {user_b} accepting request from {user_a}...")
    success, msg = accept_friend_request(id_b, user_a)
    print(f"Result: {msg.encode('ascii', 'ignore').decode('ascii')}")
    
    # 5. Test List Friends
    print(f"\n-> {user_a} checking friends...")
    friends = get_friends(id_a)
    print(f"Friends of A: {friends}")
    assert user_b in friends
    
    # 6. Test Group Creation
    print(f"\n-> {user_a} creating group 'Hackers'...")
    group_id = create_group("Hackers", id_a)
    print(f"Group Created with ID: {group_id}")
    
    # 7. Test Group Join
    print(f"\n-> {user_b} joining group 'Hackers'...")
    success, msg = join_group(group_id, id_b)
    print(f"Result: {msg.encode('ascii', 'ignore').decode('ascii')}")
    
    print("\n[+] Social Verification Complete!")

if __name__ == "__main__":
    verify_social()
