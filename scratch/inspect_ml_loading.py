import os

apcre_api_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py"

def safe_print(text):
    print(text.encode('ascii', errors='replace').decode('ascii'))

if os.path.exists(apcre_api_path):
    with open(apcre_api_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    lines = content.splitlines()
    safe_print("--- Searching for ml_model.pkl or predict inside apcre_api.py ---")
    for idx, line in enumerate(lines):
        if "ml_model.pkl" in line or "pickle.load" in line or ".predict(" in line:
            if "predict_proba" in line or "StratifiedKFold" in line:
                continue # Skip definitions if any
            safe_print(f"Line {idx+1}: {line}")
else:
    safe_print("apcre_api.py not found.")
