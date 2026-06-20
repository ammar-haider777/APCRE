keywords = ['Search files...', 'Explorer', 'View Courses', 'className="w-[280px]', 'w-72', 'File tree']

with open('c:/Users/WAZIR AMMAR HAIDER/Desktop/fyp/Source_Code/apcre-ui/src/Editor.jsx', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if any(kw in line for kw in keywords):
            print(f"{i}: {line.strip()[:100]}")
