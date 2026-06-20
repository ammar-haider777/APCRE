# -*- coding: utf-8 -*-
filepath = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_topics_db.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_part = '"dynamic_programming": "dynamic_programming"'
new_part = '"dynamic_programming": "dynamic_programming", "dynamic programming": "dynamic_programming"'

if old_part in content:
    content = content.replace(old_part, new_part)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success: Dynamic programming alias updated successfully!")
else:
    print("Error: Target alias string not found.")
