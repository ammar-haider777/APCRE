import urllib.request
import json
import time

def make_request(url, payload):
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return 500, {"error": str(e)}

def safe_print(msg):
    # Print safely on Windows CP1252 to avoid UnicodeEncodeErrors
    print(msg.encode('ascii', errors='replace').decode('ascii'))

safe_print("=== VERIFYING STATEFUL AI TUTOR ASSISTANT ===")

# Test 1: First turn - ask about linked list
payload_1 = {
    "message": "can you explain linked lists for a beginner?",
    "filename": "demo.py",
    "code": "",
    "roomId": "test_room_123"
}
status_1, data_1 = make_request("http://localhost:5001/api/assistant", payload_1)
safe_print(f"Test 1 status: {status_1}")
if status_1 == 200:
    reply = data_1.get("reply", "")
    safe_print(f"Reply includes LinkedList: {'Singly & Doubly Linked Lists' in reply}")
    safe_print(f"Reply includes analogy: {'treasure hunt' in reply}")
else:
    safe_print(f"Test 1 FAILED: {data_1}")

# Test 2: Multi-turn context retention (ask for code without explicitly repeating the topic)
payload_2 = {
    "message": "show me the code",
    "filename": "demo.py",
    "code": "",
    "roomId": "test_room_123"
}
status_2, data_2 = make_request("http://localhost:5001/api/assistant", payload_2)
safe_print(f"Test 2 status: {status_2}")
if status_2 == 200:
    reply = data_2.get("reply", "")
    safe_print(f"Reply includes Node class: {'class Node' in reply}")
    safe_print(f"Reply retains topic: {'Singly Linked List Implementation' in reply}")
else:
    safe_print(f"Test 2 FAILED: {data_2}")

# Test 3: Topic Switching (shift focus to recursion)
payload_3 = {
    "message": "what about recursion?",
    "filename": "demo.py",
    "code": "",
    "roomId": "test_room_123"
}
status_3, data_3 = make_request("http://localhost:5001/api/assistant", payload_3)
safe_print(f"Test 3 status: {status_3}")
if status_3 == 200:
    reply = data_3.get("reply", "")
    safe_print(f"Reply includes Recursion: {'Recursion & Call Stacks' in reply}")
    safe_print(f"Detects topic switch: {'smoothly transitioning' in reply.lower() or 'topic shifting' in reply.lower()}")
else:
    safe_print(f"Test 3 FAILED: {data_3}")


safe_print("\n=== VERIFYING AUTONOMOUS CODER AGENT SELF-CORRECTION ===")

# Test 4: Dynamic Average with custom numbers
payload_4 = {
    "prompt": "calculate average of 25 75 100 50",
    "code": "",
    "filename": "test_avg_agent.py",
    "workspace_dir": r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\workspace"
}
status_4, data_4 = make_request("http://localhost:5001/api/agent/automate", payload_4)
safe_print(f"Test 4 status: {status_4}")
if status_4 == 200:
    success = data_4.get("success", False)
    safe_print(f"Agent finished successfully: {success}")
    logs = data_4.get("logs", [])
    for log in logs:
        safe_print(f"  [{log['status'].upper()}] {log['step']}")
    stdout = data_4.get("stdout", "")
    safe_print(f"Script output average is 62.50: {'62.50' in stdout}")
else:
    safe_print(f"Test 4 FAILED: {data_4}")

# Test 5: Dynamic Binary Search tree with traversals
payload_5 = {
    "prompt": "write a binary search tree structure with traversals",
    "code": "",
    "filename": "test_tree_agent.py",
    "workspace_dir": r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\workspace"
}
status_5, data_5 = make_request("http://localhost:5001/api/agent/automate", payload_5)
safe_print(f"Test 5 status: {status_5}")
if status_5 == 200:
    success = data_5.get("success", False)
    safe_print(f"Agent finished successfully: {success}")
    logs = data_5.get("logs", [])
    for log in logs:
        safe_print(f"  [{log['status'].upper()}] {log['step']}")
else:
    safe_print(f"Test 5 FAILED: {data_5}")
