import os

src_dir = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui"
search_terms = ["Run AI Review", "ChatGPT", "f1Score", "90", "violations"]

print("Starting codebase search...")
for root, dirs, files in os.walk(src_dir):
    if "node_modules" in root or ".venv" in root:
        continue
    for file in files:
        if file.endswith((".jsx", ".js", ".css")):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        for term in search_terms:
                            if term in line:
                                print(f"[FOUND] File: {os.path.relpath(file_path, src_dir)} | Line {idx}: {line.strip()}")
            except Exception as e:
                pass
print("Search complete.")
