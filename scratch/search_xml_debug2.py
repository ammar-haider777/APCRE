import zipfile

docx_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"

with zipfile.ZipFile(docx_path) as docx:
    xml_content = docx.read('word/document.xml')
    
xml_str = xml_content.decode('utf-8', errors='ignore')

def search_context(term, size=120):
    idx = 0
    while True:
        idx = xml_str.find(term, idx)
        if idx == -1:
            break
        start = max(0, idx - size)
        end = min(len(xml_str), idx + len(term) + size)
        print(f"\n--- Found '{term}' at index {idx} ---")
        print(xml_str[start:end])
        idx += len(term)

search_context("Gateway")
search_context("Middleware")
search_context("5000")
