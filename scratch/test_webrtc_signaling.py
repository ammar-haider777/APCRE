import socketio
import time
import sys

client_a = socketio.Client()
client_b = socketio.Client()

received_by_b = None
received_by_a = None
left_call_received = None

users_in_room = []

@client_b.on("rtc:signal")
def on_signal_b(data):
    global received_by_b
    print("[Client B] Received WebRTC signal from Client A:", data)
    received_by_b = data

@client_a.on("rtc:signal")
def on_signal_a(data):
    global received_by_a
    print("[Client A] Received WebRTC signal from Client B:", data)
    received_by_a = data

@client_b.on("rtc:leave-call")
def on_leave_b():
    global left_call_received
    print("[Client B] Received 'rtc:leave-call' event from Client A!")
    left_call_received = True

@client_b.on("room:users")
def on_users_b(users):
    global users_in_room
    print("[Client B] Current room users updated:", users)
    users_in_room = users

@client_a.on("room:users")
def on_users_a(users):
    print("[Client A] Current room users updated:", users)

def run_test():
    global received_by_a, received_by_b, left_call_received, users_in_room
    
    signaling_server_url = "http://localhost:5000"
    print(f"Connecting clients to APCRE signaling server at {signaling_server_url}...")
    
    try:
        client_a.connect(signaling_server_url, transports=["websocket"])
        print("[Client A] Connected with ID:", client_a.sid)
        
        client_b.connect(signaling_server_url, transports=["websocket"])
        print("[Client B] Connected with ID:", client_b.sid)
    except Exception as e:
        print(f"ERROR: Failed to connect to server: {e}")
        print("Please ensure APCRE Node.js backend is running on port 5000!")
        sys.exit(1)

    room_id = "test-verification-room"
    
    print(f"\n--- STEP 1: Both clients joining room '{room_id}' ---")
    client_a.emit("room:join", {
        "roomId": room_id,
        "user": {"name": "Simulated Laptop A", "email": "laptop.a@email.com"}
    })
    time.sleep(0.5)
    
    client_b.emit("room:join", {
        "roomId": room_id,
        "user": {"name": "Simulated Phone B", "email": "phone.b@email.com"}
    })
    
    # Wait up to 5 seconds for both clients to be reported in the room users list
    print("Waiting for signaling server to confirm both users are joined...")
    success = False
    for i in range(10):
        time.sleep(0.5)
        if len(users_in_room) >= 2:
            print("Server confirmed both clients are in the same room!")
            success = True
            break
            
    if not success:
        print("FAIL: Users were not registered in room by the server in time.")
        sys.exit(1)

    print("\n--- STEP 2: Client A sending WebRTC Offer (Device 1 -> Device 2) ---")
    offer_payload = {
        "roomId": room_id,
        "signal": {
            "type": "offer",
            "offer": {
                "type": "offer",
                "sdp": "v=0\r\no=- 4611731400 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE video audio\r\n..."
            }
        }
    }
    client_a.emit("rtc:signal", offer_payload)
    
    # Wait for Client B to receive
    time.sleep(1.5)
    if received_by_b and received_by_b.get("signal", {}).get("type") == "offer":
        print("SUCCESS: Client B received the SDP Offer successfully!")
    else:
        print("FAIL: Client B did not receive the SDP Offer.")
        sys.exit(1)

    print("\n--- STEP 3: Client B sending WebRTC Answer (Device 2 -> Device 1) ---")
    answer_payload = {
        "roomId": room_id,
        "signal": {
            "type": "answer",
            "answer": {
                "type": "answer",
                "sdp": "v=0\r\no=- 4611731400 3 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=group:BUNDLE video audio\r\n..."
            }
        }
    }
    client_b.emit("rtc:signal", answer_payload)
    
    # Wait for Client A to receive
    time.sleep(1.5)
    if received_by_a and received_by_a.get("signal", {}).get("type") == "answer":
        print("SUCCESS: Client A received the SDP Answer successfully!")
    else:
        print("FAIL: Client A did not receive the SDP Answer.")
        sys.exit(1)

    print("\n--- STEP 4: Client A leaving the call ---")
    client_a.emit("rtc:leave-call", {"roomId": room_id})
    time.sleep(1.5)
    
    if left_call_received:
        print("SUCCESS: Client B received the leave call notice successfully!")
    else:
        print("FAIL: Client B did not receive the leave call notification.")
        sys.exit(1)

    print("\n=== ALL SIGNALING AND CONNECTIVITY CHECKS PASSED SUCCESSFULLY! ===")
    print("Dual-device WebRTC call negotiation via Socket.IO is fully validated.")
    
    client_a.disconnect()
    client_b.disconnect()

if __name__ == "__main__":
    run_test()
