# -*- coding: utf-8 -*-
api_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py"

with open(api_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("--- Searching for AST Visitor and Reviews ---")
for idx, line in enumerate(lines, 1):
    if "class " in line and ("visitor" in line.lower() or "audit" in line.lower() or "review" in line.lower() or "ast" in line.lower()):
        print(f"Line {idx}: {line.strip()}")
    if "def run_full_review" in line:
        print(f"Line {idx}: {line.strip()}")
