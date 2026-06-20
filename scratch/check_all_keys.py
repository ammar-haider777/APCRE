# -*- coding: utf-8 -*-
import sys
sys.path.append(r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine")

import apcre_topics_db

db = apcre_topics_db.APCRE_TOPICS_DATABASE
keys = sorted(list(db.keys()))

print(f"Total topics: {len(keys)}")
# Print 4 columns of keys
for i in range(0, len(keys), 4):
    row = keys[i:i+4]
    row_str = "".join([f"{k:<30}" for k in row])
    print(row_str)
