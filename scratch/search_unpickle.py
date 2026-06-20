import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py"

print("Searching for model unpickling in apcre_api.py...")
if os.path.exists(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines, 1):
                if "ml_model.pkl" in line or "pickle.load" in line or "MODEL_LOADED" in line:
                    start = max(0, idx - 5)
                    end = min(len(lines), idx + 25)
                    print(f"--- Line {idx} ---")
                    for i in range(start, end):
                        print(f"Line {i+1}: {lines[i].rstrip()}")
    except Exception as e:
        print(f"Error reading file: {e}")
else:
    print("apcre_api.py not found.")
