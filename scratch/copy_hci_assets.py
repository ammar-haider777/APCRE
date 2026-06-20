import os
import shutil

target_dir = r"C:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\HCI Assignment 2"
os.makedirs(target_dir, exist_ok=True)
print(f"Created target directory: {target_dir}")

# Source paths of the generated images
brain_dir = r"C:\Users\WAZIR AMMAR HAIDER\.gemini\antigravity\brain\6debdddc-4cc1-426b-9547-c836a8af4e3e"
low_fi_src = None
high_fi_src = None

for f in os.listdir(brain_dir):
    if f.startswith("apcre_low_fi_sketch") and f.endswith(".png"):
        low_fi_src = os.path.join(brain_dir, f)
    elif f.startswith("apcre_high_fi_mockup") and f.endswith(".png"):
        high_fi_src = os.path.join(brain_dir, f)

if low_fi_src:
    shutil.copy2(low_fi_src, os.path.join(target_dir, "apcre_low_fi_sketch.png"))
    print(f"Copied low-fi sketch to target directory.")
else:
    print("Warning: low-fi source image not found.")

if high_fi_src:
    shutil.copy2(high_fi_src, os.path.join(target_dir, "apcre_high_fi_mockup.png"))
    print(f"Copied high-fi mockup to target directory.")
else:
    print("Warning: high-fi source image not found.")
