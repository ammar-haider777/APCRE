file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py"

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if "llm" in line.lower():
            print(f"Line {idx+1}: {line.strip()[:120]}")
