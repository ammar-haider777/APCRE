import os

filepath = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\server.js"
if os.path.exists(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if "5001" in line or "assistant" in line or "review" in line:
            print(f"Line {i+1}:")
            for j in range(max(0, i-3), min(len(lines), i+12)):
                safe_line = lines[j].encode('ascii', errors='replace').decode('ascii').strip()
                print(f"  {j+1}: {safe_line}")
