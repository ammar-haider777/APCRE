import sys

file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\app\editor\page.jsx"

def search_keywords(keywords):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for idx, line in enumerate(lines):
        line_num = idx + 1
        for kw in keywords:
            if kw.lower() in line.lower():
                print(f"Line {line_num}: {line.strip()[:120]}")
                break

if __name__ == "__main__":
    kws = sys.argv[1:] if len(sys.argv) > 1 else ["socket", "webrtc", "room", "ice"]
    search_keywords(kws)
