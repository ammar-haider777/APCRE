file_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\app\editor\page.jsx"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def print_context(line_num, context_size=15):
    start = max(0, line_num - context_size)
    end = min(len(lines), line_num + context_size)
    print(f"\n--- Context around Line {line_num} ---")
    for idx in range(start, end):
        print(f"{idx+1}: {lines[idx].strip()[:100]}")

print_context(1675)
print_context(4216)
