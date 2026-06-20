md_path = r"C:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\HCI Assignment 2\APCRE_HCI_Assignment_Report.md"

with open(md_path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace text annotations with markdown image renders
low_fi_anno = "*(Refer to apcre_low_fi_sketch.png for the physical paper prototype layout)*"
low_fi_img = "![Figure 2.1: Low-Fidelity Paper Prototype Sketch](apcre_low_fi_sketch.png)\n*Figure 2.1: Low-Fidelity Paper Prototype Sketch (APCRE IDE Dashboard Layout)*"

high_fi_anno = "*(Refer to apcre_high_fi_mockup.png for the final system interface)*"
high_fi_img = "![Figure 3.1: High-Fidelity UI Mockup](apcre_high_fi_mockup.png)\n*Figure 3.1: High-Fidelity UI Mockup (APCRE Dark-Mode IDE Dashboard)*"

text = text.replace(low_fi_anno, low_fi_img)
text = text.replace(high_fi_anno, high_fi_img)

with open(md_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Successfully updated Markdown report with inline image rendering links.")
