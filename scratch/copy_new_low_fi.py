import os
import shutil

target_path = r"C:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\HCI Assignment 2\apcre_low_fi_sketch.png"
brain_dir = r"C:\Users\WAZIR AMMAR HAIDER\.gemini\antigravity\brain\6debdddc-4cc1-426b-9547-c836a8af4e3e"

# Find the newest generated low-fi sketch
candidates = []
for f in os.listdir(brain_dir):
    if f.startswith("apcre_low_fi_sketch") and f.endswith(".png"):
        full = os.path.join(brain_dir, f)
        candidates.append((os.path.getmtime(full), full))

if candidates:
    # Sort by modification time descending to get the newest
    candidates.sort(reverse=True)
    newest_src = candidates[0][1]
    
    # Overwrite the target image
    shutil.copy2(newest_src, target_path)
    print(f"Successfully replaced paper prototype image with: {newest_src}")
else:
    print("Error: No low-fi sketch candidates found in the database.")
