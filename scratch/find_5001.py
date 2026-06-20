import os

backend_dir = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend"

for root, dirs, files in os.walk(backend_dir):
    for file in files:
        if file.endswith(".py") or file.endswith(".js") or file.endswith(".json"):
            fp = os.path.join(root, file)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if "5001" in content:
                    print(f"Found 5001 in {fp}")
            except Exception as e:
                pass
