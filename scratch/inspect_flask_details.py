import os

apcre_api_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py"

def safe_print(text):
    print(text.encode('ascii', errors='replace').decode('ascii'))

if os.path.exists(apcre_api_path):
    with open(apcre_api_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    lines = content.splitlines()
    
    # 1. Search for @app.route("/api/review")
    safe_print("--- Inspecting /api/review Flask Route ---")
    found_route = False
    for idx, line in enumerate(lines):
        if '/api/review' in line:
            found_route = True
            safe_print(f"Found at line {idx+1}:")
            start_l = max(0, idx - 5)
            end_l = min(len(lines), idx + 60)
            for i in range(start_l, end_l):
                safe_print(f"  {i+1}: {lines[i]}")
            break
            
    # 2. Search for visit_ExceptHandler to show how bare except is caught in AST
    safe_print("\n--- Inspecting visit_ExceptHandler AST parser ---")
    for idx, line in enumerate(lines):
        if 'def visit_ExceptHandler' in line:
            safe_print(f"Found at line {idx+1}:")
            start_l = max(0, idx - 2)
            end_l = min(len(lines), idx + 25)
            for i in range(start_l, end_l):
                safe_print(f"  {i+1}: {lines[i]}")
            break
            
    # 3. Search for visit_Name to show how SQL/Exec injection are caught in AST
    safe_print("\n--- Inspecting visit_Name or eval/exec AST parser ---")
    for idx, line in enumerate(lines):
        if 'def visit_Name' in line or 'visit_Call' in line:
            safe_print(f"Found at line {idx+1}:")
            start_l = max(0, idx - 2)
            end_l = min(len(lines), idx + 25)
            for i in range(start_l, end_l):
                safe_print(f"  {i+1}: {lines[i]}")
            break
else:
    safe_print("apcre_api.py not found.")
