import os
import re

server_js_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\server.js"
apcre_api_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py"

print("=== INSPECTING SERVER.JS (NODE/EXPRESS NETWORKING & SIGNALING) ===")
if os.path.exists(server_js_path):
    with open(server_js_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    # 1. Look for routes
    routes = re.findall(r'app\.(post|get|put|delete)\([\'"]([^\'"]+)[\'"]', content)
    print(f"Express Routes Found ({len(routes)}):")
    for r in routes[:15]:
        print(f"  {r[0].upper()} {r[1]}")
        
    # 2. Look for command whitelist or validation
    print("\nCommand Whitelist Logic:")
    whitelist_matches = [line for line in content.splitlines() if "whitelist" in line.lower() or "cmd" in line.lower()]
    for line in whitelist_matches[:12]:
        print(f"  {line.strip()}")
        
    # 3. Look for WebRTC signaling event handlers (Socket.io)
    print("\nWebRTC / Socket.io Event Listeners:")
    socket_events = re.findall(r'\.on\([\'"]([^\'"]+)[\'"]', content)
    print(f"  Events: {list(set(socket_events))}")
else:
    print("server.js not found at specified path.")

print("\n=== INSPECTING APCRE_API.PY (FLASK & AI ENGINE PARSERS/AGENTS) ===")
if os.path.exists(apcre_api_path):
    with open(apcre_api_path, "r", encoding="utf-8", errors="ignore") as f:
        api_content = f.read()
        
    # 1. Look for Flask endpoints
    flask_routes = re.findall(r'@app\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?', api_content)
    print(f"Flask Endpoints Found ({len(flask_routes)}):")
    for fr in flask_routes[:15]:
        methods = fr[1].replace("'", "").replace('"', '').strip() if fr[1] else "GET"
        print(f"  {methods} {fr[0]}")
        
    # 2. Look for AST parsing methods
    print("\nAST Parsing Functions:")
    ast_funcs = [line for line in api_content.splitlines() if "def " in line and ("ast" in line.lower() or "parse" in line.lower() or "node" in line.lower())]
    for line in ast_funcs[:10]:
        print(f"  {line.strip()}")
        
    # 3. Look for Sandbox Execution
    print("\nSandbox Execution logic:")
    sandbox_lines = [line for line in api_content.splitlines() if "subprocess" in line or "stderr" in line or "exec" in line]
    for line in sandbox_lines[:8]:
        print(f"  {line.strip()}")
else:
    print("apcre_api.py not found.")
