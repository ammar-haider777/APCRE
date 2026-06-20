import sys

def search_keywords(file_path, keywords):
    print(f"--- Searching {file_path} ---")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for idx, line in enumerate(lines):
        line_num = idx + 1
        for kw in keywords:
            if kw.lower() in line.lower():
                print(f"Line {line_num}: {line.strip()[:120]}")
                break

if __name__ == "__main__":
    search_keywords(r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\Editor.jsx", ["getSocketUrl", "5000", "io("])
    search_keywords(r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\app\editor\page.jsx", ["getSocketUrl", "5000", "io("])
