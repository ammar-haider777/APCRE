import zipfile
import xml.etree.ElementTree as ET

docx_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis_Updated.docx"

with zipfile.ZipFile(docx_path) as docx:
    xml_content = docx.read('word/document.xml')

xml_str = xml_content.decode('utf-8', errors='ignore')
lines = xml_str.splitlines()
print(f"Number of lines: {len(lines)}")
for idx, l in enumerate(lines):
    print(f"Line {idx+1} length: {len(l)}")

# Let's inspect line 2, around column 35968
if len(lines) >= 2:
    line2 = lines[1]
    col = 77980
    start = max(0, col - 150)
    end = min(len(line2), col + 150)
    print(f"\n--- Line 2 around column {col} ---")
    print(line2[start:end])
    # Let's print individual characters with index
    print("\nCharacters right around the error index:")
    for i in range(max(0, col - 20), min(len(line2), col + 20)):
        print(f"Col {i}: {line2[i]!r}")
else:
    print("Line 2 not found!")
