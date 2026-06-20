import zipfile

docx_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"

with zipfile.ZipFile(docx_path) as docx:
    xml_content = docx.read('word/document.xml')
    
xml_str = xml_content.decode('utf-8', errors='ignore')

def inspect_runs(term):
    print(f"\n--- Inspecting runs containing '{term}' ---")
    idx = 0
    found = False
    while True:
        idx = xml_str.find(term, idx)
        if idx == -1:
            break
        found = True
        # Find the start of the <w:p> containing this, and the end of the </w:p>
        p_start = xml_str.rfind("<w:p", 0, idx)
        # Handle cases where <w:p> has attributes
        p_end = xml_str.find("</w:p>", idx) + 6
        p_xml = xml_str[p_start:p_end]
        print(f"p_xml (first 400 chars):")
        print(p_xml[:400].encode('ascii', errors='replace').decode('ascii'))
        print(f"p_xml (last 400 chars):")
        print(p_xml[-400:].encode('ascii', errors='replace').decode('ascii'))
        idx += len(term)
    if not found:
        print("  NOT FOUND")

inspect_runs("stratified 4-fold")
inspect_runs("auditing routine recorded")
inspect_runs("exact classification boundaries")
inspect_runs("optimal trade-offs")
