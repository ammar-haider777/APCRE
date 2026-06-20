import zipfile
import xml.etree.ElementTree as ET

docx_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"

with zipfile.ZipFile(docx_path) as docx:
    xml_content = docx.read('word/document.xml')
    
xml_str = xml_content.decode('utf-8', errors='ignore')

tbl_start = xml_str.find("<w:tbl>", xml_str.find("Table 4.1 below:"))
tbl_end = xml_str.find("</w:tbl>", tbl_start) + 8
table_xml = xml_str[tbl_start:tbl_end]

wrapped_xml = f'<root xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">{table_xml}</root>'

ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
root = ET.fromstring(wrapped_xml)

new_rows_data = [
    ["Clean Code", "0.8519", "0.8400", "0.8459", "1.8 ms"],
    ["API Design Problems", "0.9584", "0.9800", "0.9691", "1.8 ms"],
    ["Architectural Violations", "0.8515", "0.8600", "0.8557", "1.8 ms"],
    ["Code Smells", "0.9164", "0.9100", "0.9132", "1.8 ms"],
    ["Concurrency Issues", "0.9567", "0.9600", "0.9583", "1.8 ms"],
    ["Design Pattern Violations", "0.9508", "0.9400", "0.9454", "1.8 ms"],
    ["Error Handling Problems", "0.9403", "0.9412", "0.9407", "1.8 ms"],
    ["High Coupling", "0.9586", "0.9413", "0.9499", "1.8 ms"]
]

# tr elements
trs = root.findall('.//w:tr', ns)
# Row 0 is header, rows 1 to 8 are the ones we want to replace
for row_idx in range(1, 9):
    tr = trs[row_idx]
    data = new_rows_data[row_idx - 1]
    
    tcs = tr.findall('.//w:tc', ns)
    for col_idx, val in enumerate(data):
        tc = tcs[col_idx]
        ts = tc.findall('.//w:t', ns)
        if ts:
            ts[0].text = val
            # Clear any other text runs in this cell
            for extra_t in ts[1:]:
                extra_t.text = ""
        else:
            print(f"Warning: No w:t found in Row {row_idx}, Col {col_idx}")

# Let's serialize back to XML
ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
modified_wrapped = ET.tostring(root, encoding='utf-8').decode('utf-8')

# Strip the root wrapper
prefix = '<root xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
suffix = '</root>'
if modified_wrapped.startswith(prefix) and modified_wrapped.endswith(suffix):
    new_table_xml = modified_wrapped[len(prefix): -len(suffix)]
    print("\nSuccessfully serialized and stripped table!")
    print(f"New table XML length: {len(new_table_xml)}")
    
    # Verify by parsing new_table_xml
    verify_root = ET.fromstring(f'<root xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">{new_table_xml}</root>')
    verify_rows = []
    for tr in verify_root.findall('.//w:tr', ns):
        cells = []
        for tc in tr.findall('.//w:tc', ns):
            texts = []
            for t in tc.findall('.//w:t', ns):
                if t.text:
                    texts.append(t.text)
            cells.append("".join(texts))
        verify_rows.append(cells)
        
    print("\n--- Verified Updated Table 4.1 Rows ---")
    for idx, r in enumerate(verify_rows):
        print(f"Row {idx}: {r}")
else:
    print("Error: Could not strip root wrapper!")
