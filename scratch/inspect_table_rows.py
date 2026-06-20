import zipfile

docx_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"

with zipfile.ZipFile(docx_path) as docx:
    xml_content = docx.read('word/document.xml')
    
xml_str = xml_content.decode('utf-8', errors='ignore')

# Let's find index of "Table 4.2" and the table that immediately follows it
tbl_start = xml_str.find("<w:tbl>", xml_str.find("Table 4.2, APCRE achieves"))
tbl_end = xml_str.find("</w:tbl>", tbl_start) + 8

table_xml = xml_str[tbl_start:tbl_end]

wrapped_xml = f'<root xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">{table_xml}</root>'

import xml.etree.ElementTree as ET
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
root = ET.fromstring(wrapped_xml)

rows = []
for tr in root.findall('.//w:tr', ns):
    cells = []
    for tc in tr.findall('.//w:tc', ns):
        texts = []
        for t in tc.findall('.//w:t', ns):
            texts.append(t.text if t.text else "")
        cells.append("".join(texts))
    rows.append(cells)

print("\n--- Extracted Table 4.2 Rows & Cells ---")
for idx, r in enumerate(rows):
    print(f"Row {idx}: {r}")
