import os

filepath = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\server.js"
if os.path.exists(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    start_line = None
    for i, line in enumerate(lines):
        if 'app.post("/api/agent/automate"' in line:
            start_line = i
            break
            
    if start_line is not None:
        print(f"Lines around `/api/agent/automate` start:")
        for j in range(start_line, min(len(lines), start_line + 25)):
            safe_line = lines[j].encode('ascii', errors='replace').decode('ascii').strip()
            print(f"  {j+1}: {safe_line}")
else:
    print("server.js not found.")
