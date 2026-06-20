with open(r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\src\app\editor\page.jsx", 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if "rightpanel" in line.lower():
            print(f"Line {idx+1}: {line.strip()[:100]}")
