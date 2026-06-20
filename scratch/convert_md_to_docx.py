import zipfile
import shutil
import os
import re

md_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_AI_Model_Documentation_Defense.md"
template_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis_Updated.docx"
output_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_AI_Model_Documentation_Defense.docx"

def xml_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def parse_inline_formatting(text):
    # Splits text by bold markers **
    parts = re.split(r'(\*\*.*?\*\*)', text)
    runs_xml = []
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            inner = part[2:-2]
            runs_xml.append(f"<w:r><w:rPr><w:b/></w:rPr><w:t xml:space=\"preserve\">{xml_escape(inner)}</w:t></w:r>")
        else:
            if part:
                runs_xml.append(f"<w:r><w:t xml:space=\"preserve\">{xml_escape(part)}</w:t></w:r>")
    return "".join(runs_xml)

def make_word_table(rows):
    # Construct a w:tbl element from raw rows
    tbl_xml = ["<w:tbl><w:tblPr><w:tblStyle w:val=\"TableGrid\"/><w:tblW w:type=\"auto\" w:w=\"0\"/><w:tblLook w:firstColumn=\"1\" w:firstRow=\"1\" w:lastColumn=\"0\" w:lastRow=\"0\" w:noHBand=\"0\" w:noVBand=\"1\" w:val=\"04A0\"/></w:tblPr>"]
    
    # Analyze table headers and dividers
    valid_rows = []
    for r in rows:
        cells = [c.strip() for c in r.split("|")[1:-1]]
        # Ignore divider row (e.g. :---)
        if cells and all(re.match(r'^:?-+:?$', c) for c in cells):
            continue
        valid_rows.append(cells)
        
    for r_idx, cells in enumerate(valid_rows):
        tbl_xml.append("<w:tr>")
        for c_idx, cell in enumerate(cells):
            tbl_xml.append("<w:tc>")
            # Align formatting: bold for headers
            if r_idx == 0:
                p_xml = f"<w:p><w:pPr><w:jc w:val=\"center\"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val=\"20\"/></w:rPr><w:t>{xml_escape(cell)}</w:t></w:r></w:p>"
            else:
                runs = parse_inline_formatting(cell)
                p_xml = f"<w:p><w:pPr><w:sz w:val=\"19\"/></w:pPr>{runs}</w:p>"
            tbl_xml.append(p_xml)
            tbl_xml.append("</w:tc>")
        tbl_xml.append("</w:tr>")
        
    tbl_xml.append("</w:tbl>")
    return "".join(tbl_xml)

def convert_md_to_docx():
    print(f"Reading Markdown: {md_path}...")
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    paragraphs_xml = []
    in_table = False
    table_rows = []
    
    for line in lines:
        stripped = line.strip()
        
        # Handle Table parsing
        if stripped.startswith("|"):
            in_table = True
            table_rows.append(stripped)
            continue
        elif in_table:
            # Table ended, build it
            paragraphs_xml.append(make_word_table(table_rows))
            table_rows = []
            in_table = False
            
        if not stripped:
            continue
            
        # Heading 1
        if stripped.startswith("# "):
            text = stripped[2:]
            paragraphs_xml.append(f"<w:p><w:pPr><w:pStyle w:val=\"Heading1\"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val=\"28\"/></w:rPr><w:t>{xml_escape(text)}</w:t></w:r></w:p>")
        # Heading 2
        elif stripped.startswith("## "):
            text = stripped[3:]
            paragraphs_xml.append(f"<w:p><w:pPr><w:pStyle w:val=\"Heading2\"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val=\"24\"/></w:rPr><w:t>{xml_escape(text)}</w:t></w:r></w:p>")
        # Heading 3
        elif stripped.startswith("### "):
            text = stripped[4:]
            paragraphs_xml.append(f"<w:p><w:pPr><w:pStyle w:val=\"Heading3\"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val=\"20\"/></w:rPr><w:t>{xml_escape(text)}</w:t></w:r></w:p>")
        # Bullet list item
        elif stripped.startswith("* ") or stripped.startswith("- "):
            text = stripped[2:]
            runs = parse_inline_formatting(text)
            paragraphs_xml.append(f"<w:p><w:pPr><w:pStyle w:val=\"ListBullet\"/></w:pPr>{runs}</w:p>")
        # Numbered list item
        elif re.match(r'^\d+\.\s+', stripped):
            text = re.sub(r'^\d+\.\s+', '', stripped)
            runs = parse_inline_formatting(text)
            paragraphs_xml.append(f"<w:p><w:pPr><w:pStyle w:val=\"ListNumber\"/></w:pPr>{runs}</w:p>")
        # Mermaid / Code block wrappers
        elif stripped.startswith("```"):
            continue
        # Standard Paragraph
        else:
            runs = parse_inline_formatting(stripped)
            paragraphs_xml.append(f"<w:p>{runs}</w:p>")
            
    # Compile the final document.xml contents
    body_xml = "".join(paragraphs_xml)
    document_xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\"><w:body>{body_xml}</w:body></w:document>"
    
    # Build the docx by cloning template zip structure
    print(f"Creating DOCX from template: {template_path} -> {output_path}...")
    with zipfile.ZipFile(template_path, 'r') as src_zip:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as tmp_zip:
            for item in src_zip.infolist():
                content = src_zip.read(item.filename)
                if item.filename == 'word/document.xml':
                    content = document_xml.encode('utf-8')
                tmp_zip.writestr(item, content)
                
    print(f"[OK] Successfully saved final Word Document to: {output_path}")

if __name__ == "__main__":
    convert_md_to_docx()
