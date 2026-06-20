import zipfile
import shutil

src_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"
tmp_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis_tmp.docx"

with zipfile.ZipFile(src_path, 'r') as src_zip:
    with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as tmp_zip:
        for item in src_zip.infolist():
            content = src_zip.read(item.filename)
            if item.filename == 'word/document.xml':
                xml_str = content.decode('utf-8', errors='ignore')
                # Let's replace Voice & Video with Voice &amp; Video
                if "Voice & Video" in xml_str:
                    xml_str = xml_str.replace("Voice & Video", "Voice &amp; Video")
                    print("Found and replaced 'Voice & Video' with 'Voice &amp; Video'")
                else:
                    print("'Voice & Video' not found in document.xml")
                content = xml_str.encode('utf-8')
            tmp_zip.writestr(item, content)

shutil.move(tmp_path, src_path)
print("Saved fixed docx!")
