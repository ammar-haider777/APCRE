import os

workspace_dir = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code"

for root, dirs, files in os.walk(workspace_dir):
    for file in files:
        if "thesis" in file.lower():
            fp = os.path.join(root, file)
            print(f"Found thesis file: {fp} ({os.path.getsize(fp)} bytes)")
