import os

file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\Editor.jsx"

print("Searching for RightPanel instantiation in Editor.jsx...")
if os.path.exists(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines, 1):
                if "<RightPanel" in line or "RightPanel" in line:
                    # Print 5 lines before and 5 lines after the instantiation
                    start = max(0, idx - 5)
                    end = min(len(lines), idx + 10)
                    print(f"--- Line {idx} ---")
                    for i in range(start, end):
                        print(f"Line {i+1}: {lines[i].strip()}")
    except Exception as e:
        print(f"Error reading file: {e}")
else:
    print("Editor.jsx not found.")
