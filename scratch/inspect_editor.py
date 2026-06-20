import os
import sys

filepath = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\Editor.jsx"
if os.path.exists(filepath):
    print("Editor.jsx exists!")
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print("Total lines:", len(lines))
    
    # Let's search for lines containing both "agent" and other interesting keywords, or "recognition"
    keywords = ["recognition", "voice", "microphone", "agent", "automate"]
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for kw in keywords:
            if kw in line_lower:
                safe_line = line.encode('ascii', errors='replace').decode('ascii').strip()
                print(f"Line {i+1} ({kw}): {safe_line[:120]}")
else:
    print("Editor.jsx not found at:", filepath)
