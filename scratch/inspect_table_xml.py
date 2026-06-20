import zipfile

docx_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"

with zipfile.ZipFile(docx_path) as docx:
    xml_content = docx.read('word/document.xml')
    
xml_str = xml_content.decode('utf-8', errors='ignore')

def search_around(term, size=300):
    idx = 0
    while True:
        idx = xml_str.find(term, idx)
        if idx == -1:
            break
        print(f"\n--- Found '{term}' at index {idx} ---")
        print(xml_str[max(0, idx-size):min(len(xml_str), idx+len(term)+size)])
        idx += len(term)

search_around("ML Engine Quality Classification Metrics")
search_around("Table 4.1")
search_around("Table 4.2")
