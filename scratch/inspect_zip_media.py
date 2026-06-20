import zipfile

docx_path = r"C:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\APCRE_Final_Year_Thesis_Updated.docx"

with zipfile.ZipFile(docx_path) as docx:
    for f in docx.namelist():
        if "media" in f or "rels" in f:
            print(f)
