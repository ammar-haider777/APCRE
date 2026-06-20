file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\app\editor\page.jsx"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(1674, 0, -1):
    line = lines[idx]
    if line.startswith("function ") or line.startswith("const ") or "export default" in line:
        print(f"Line {idx+1}: {line.strip()}")
        break
