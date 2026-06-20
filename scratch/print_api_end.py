file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line in lines[-25:]:
    print(line.strip())
