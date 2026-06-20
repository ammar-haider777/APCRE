import os

server_js_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\server.js"

def safe_print(text):
    print(text.encode('ascii', errors='replace').decode('ascii'))

if os.path.exists(server_js_path):
    with open(server_js_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    lines = content.splitlines()
    safe_print("--- Searching for command execution endpoint in server.js ---")
    for idx, line in enumerate(lines):
        if "/api/run" in line or "/api/execute" in line or "spawn(" in line or "exec(" in line:
            safe_print(f"Match found at line {idx+1}:")
            start_l = max(0, idx - 15)
            end_l = min(len(lines), idx + 25)
            for i in range(start_l, end_l):
                safe_print(f"  {i+1}: {lines[i]}")
            safe_print("-" * 50)
            
    safe_print("\n--- Searching for Socket.IO event listeners in server.js ---")
    io_found = False
    for idx, line in enumerate(lines):
        if "io.on(" in line or "socket.on(" in line:
            if not io_found:
                safe_print(f"Found socket logic starting around line {idx+1}:")
                end_l = min(len(lines), idx + 100)
                for i in range(idx, end_l):
                    safe_print(f"  {i+1}: {lines[i]}")
                io_found = True
else:
    safe_print("server.js not found.")
