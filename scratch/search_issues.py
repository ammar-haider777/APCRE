import os

file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\Editor.jsx"

print("Searching for issues state/variable in Editor.jsx...")
if os.path.exists(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines, 1):
                if "const [issues" in line or "let issues" in line or "issues," in line or "setIssues" in line:
                    print(f"Line {idx}: {line.strip()}")
    except Exception as e:
        print(f"Error reading file: {e}")
else:
    print("Editor.jsx not found.")
