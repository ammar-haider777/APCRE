file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\app\editor\page.jsx"

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if "ctrl" in line.lower() or "keydown" in line.lower() or "meta" in line.lower():
            print(f"Line {idx+1}: {line.strip()[:120]}")
