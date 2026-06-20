import sys

def search_assistant(file_path):
    print(f"\n=== Searching {file_path} ===")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        if "assistant" in line.lower() or "active programming" in line.lower():
            print(f"Line {idx+1}: {line.strip()[:120]}")

search_assistant(r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\server.js")
search_assistant(r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py")
