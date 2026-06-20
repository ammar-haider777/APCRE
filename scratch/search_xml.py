import zipfile
import xml.etree.ElementTree as ET

docx_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"

with zipfile.ZipFile(docx_path) as docx:
    xml_content = docx.read('word/document.xml')
    
# Let's search the raw xml string for "Vite", "5173", and "Ollama" in the context of some characters before and after!
xml_str = xml_content.decode('utf-8', errors='ignore')

def search_context(term, size=100):
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

search_context("Vite")
search_context("5173")
