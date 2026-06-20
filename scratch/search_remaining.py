import zipfile

docx_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"

with zipfile.ZipFile(docx_path) as docx:
    xml_content = docx.read('word/document.xml')
    
xml_str = xml_content.decode('utf-8', errors='ignore')

def search_partial(term):
    print(f"\nSearching for '{term}':")
    idx = 0
    found = False
    while True:
        idx = xml_str.find(term, idx)
        if idx == -1:
            break
        found = True
        start = max(0, idx - 100)
        end = min(len(xml_str), idx + len(term) + 100)
        print(f"  Found at index {idx}: ... {xml_str[start:end]} ...")
        idx += len(term)
    if not found:
        print("  NOT FOUND")

# Let's search for partials
search_partial("517")
search_partial("Vite")
search_partial("vite")
search_partial("state machine")
search_partial("stateful educational tutoring")
search_partial("educational tutoring system")
search_partial("custom scikit-learn")
search_partial("scikit-learn")
search_partial("PEP 8")
