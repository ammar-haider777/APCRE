file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\app\editor\page.jsx"

with open(file_path, 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if "<RightPanel" in line or "</RightPanel" in line:
            print(f"Line {idx+1}: {line.strip()}")
