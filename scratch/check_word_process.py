import os
import subprocess

src_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"
dir_path = os.path.dirname(src_path)

print("Checking files in directory:")
for f in os.listdir(dir_path):
    if "APCRE" in f or "~$" in f:
        print(f"  {f} (size: {os.path.getsize(os.path.join(dir_path, f)) if os.path.isfile(os.path.join(dir_path, f)) else 'N/A'})")

print("\nChecking for running WINWORD.EXE processes:")
try:
    output = subprocess.check_output("tasklist", shell=True).decode('utf-8', errors='ignore')
    if "WINWORD" in output or "winword" in output.lower():
        print("Microsoft Word (WINWORD.EXE) IS RUNNING!")
    else:
        print("Microsoft Word is NOT running.")
except Exception as e:
    print(f"Error checking processes: {e}")
