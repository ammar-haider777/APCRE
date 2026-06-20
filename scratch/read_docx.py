import zipfile
import xml.etree.ElementTree as ET

docx_path = r"C:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\HCI Assignment 2\APCRE_HCI_Assignment_Report_Real_Images.docx"

def extract_text_from_docx(path):
    try:
        with zipfile.ZipFile(path) as docx:
            xml_content = docx.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            # Namespace map
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            paragraphs = []
            for p in root.findall('.//w:p', ns):
                texts = []
                for t in p.findall('.//w:t', ns):
                    texts.append(t.text)
                if texts:
                    paragraphs.append("".join(texts))
            return "\n".join(paragraphs)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    text = extract_text_from_docx(docx_path)
    print("--- Word Docx Text (First 1500 chars) ---")
    print(text[:1500])
    
    # Save the full extracted text into a txt file so we can view it cleanly!
    with open(r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\scratch\thesis_text.txt", 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"\nSaved full text to scratch/thesis_text.txt (Total chars: {len(text)})")
