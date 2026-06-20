file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py"

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "app.run" in line or "__main__" in line or "5001" in line:
        print(f"Line {idx+1}: {line.strip()}")
