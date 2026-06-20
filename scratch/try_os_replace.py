import os
import shutil

src_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"
tmp_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis_tmp.docx"

if os.path.exists(tmp_path):
    print(f"Temporary file exists (size: {os.path.getsize(tmp_path)} bytes).")
    try:
        # Use os.replace which is atomic and overwrites on Windows
        os.replace(tmp_path, src_path)
        print("Success! Overwrote the original thesis file using os.replace.")
    except Exception as e:
        print(f"Error using os.replace: {e}")
else:
    print("Temporary file does not exist.")
