# -*- coding: utf-8 -*-
import os

api_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py"

with open(api_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    (
        '"### 🤖 Welcome to the APCRE AI Tutor Platform!\\n\\n"',
        '"Welcome to the APCRE AI Tutor Platform!\\n\\n"'
    ),
    (
        "f\"### 🔍 Code Review: {filename or 'untitled.py'}\\n\\n\"",
        "f\"Code Review: {filename or 'untitled.py'}\\n\\n\""
    ),
    (
        "response = f\"### 🔍 Code Review & Debugging Guide: {filename or 'untitled.py'}\\n\\n\"",
        "response = f\"Code Review & Debugging Guide: {filename or 'untitled.py'}\\n\\n\""
    ),
    (
        'response += "---\\n\\n### 💡 Clean Refactored Implementation\\n"',
        'response += "---\\n\\nClean Refactored Implementation:\\n"'
    ),
    (
        "response = f\"## 📚 APCRE Mentor: {db_entry['title']}\\n\"",
        "response = f\"APCRE Mentor: {db_entry['title']}\\n\""
    ),
    (
        'response += "### 💡 Core Concept\\n"',
        'response += "Core Concept:\\n"'
    ),
    (
        'response += "### ⚡ Advanced Architectural Insight\\n"',
        'response += "Advanced Architectural Insight:\\n"'
    ),
    (
        'response += "### 🐍 Python Implementation\\n"',
        'response += "Python Implementation:\\n"'
    ),
    (
        'response += "### 📊 Step-by-Step Dry Run / Trace\\n"',
        'response += "Step-by-Step Dry Run / Trace:\\n"'
    ),
    (
        'response += "### ⏱️ Complexity Analysis\\n"',
        'response += "Complexity Analysis:\\n"'
    ),
    (
        'response += "### ⚠️ Critical Edge Cases & Traps\\n"',
        'response += "Critical Edge Cases & Traps:\\n"'
    ),
    (
        '"### 🤖 APCRE Proprietary AI Engine\\n\\n"',
        '"APCRE Proprietary AI Engine:\\n\\n"'
    )
]

success_count = 0
for idx, (target, replacement) in enumerate(replacements, 1):
    if target in content:
        content = content.replace(target, replacement)
        print(f"Success {idx}: Replaced successfully.")
        success_count += 1
    else:
        # Check normalized search
        print(f"Warning {idx}: Block not found exactly. Checking alternative coding...")
        target_norm = target.replace('\r\n', '\n')
        if target_norm in content:
            content = content.replace(target_norm, replacement.replace('\r\n', '\n'))
            print(f"Success {idx} (Normalized): Replaced.")
            success_count += 1
        else:
            print(f"Error {idx}: Completely missed!")

if success_count > 0:
    with open(api_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Updater] Emojis & raw Markdown headers cleaned: {success_count} replacements applied.")
else:
    print("[Updater] Aborting file write due to no matches.")
