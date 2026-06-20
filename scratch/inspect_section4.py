import zipfile

docx_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"

with zipfile.ZipFile(docx_path) as docx:
    xml_content = docx.read('word/document.xml')
    
xml_str = xml_content.decode('utf-8', errors='ignore')

# Search around the caption of Table 4.2
caption = "Table 4.2: Comparative Evaluation of Review Engines Against Baselines"
idx = xml_str.find(caption)
if idx != -1:
    print(f"Found caption at index {idx}")
    print("\n--- Surrounding XML (800 chars) ---")
    snippet = xml_str[idx - 100: idx + 700]
    print(snippet.encode('ascii', errors='replace').decode('ascii'))
else:
    print("Caption not found!")
