import os

desktop = r"c:\Users\WAZIR AMMAR HAIDER\Desktop"
image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")

print("--- Searching for image files in Desktop and subdirectories ---")
found_count = 0

# Limit search depth to prevent excessive scanning
for root, dirs, files in os.walk(desktop):
    # Skip .git, node_modules, .next, etc. to be fast
    if any(ignore in root for ignore in [".git", "node_modules", ".next", ".venv"]):
        continue
    for f in files:
        if f.lower().endswith(image_extensions):
            full_path = os.path.join(root, f)
            # Ignore Antigravity artifacts or logo placeholders unless relevant
            if "antigravity" in full_path or "gemini" in full_path:
                continue
            print(f"Found image: {f} in folder: {root} (size: {os.path.getsize(full_path)} bytes)")
            found_count += 1
            if found_count > 40:
                print("Too many images found, stopping search.")
                break
    if found_count > 40:
        break
