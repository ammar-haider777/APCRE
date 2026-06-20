src_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"

try:
    with open(src_path, 'a+b') as f:
        print("Success! The file is NOT locked by any process and can be opened for writing.")
except Exception as e:
    print(f"Error opening file: {e}")
