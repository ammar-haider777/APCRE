file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\learning\LearningLayout.jsx"

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if "videoUrl" in line:
            print(f"Line {idx+1}: {line.strip()[:100]}")
