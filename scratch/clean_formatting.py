# -*- coding: utf-8 -*-
import os

api_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py"

with open(api_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Greeting replacement
old_greeting = """    if any(msg_lower.startswith(w) for w in greetings) or msg_lower == "help" or msg_lower == "":
        return (
            "Welcome to the APCRE AI Tutor Platform!\\n\\n"
            "I am your dedicated senior mentor and intelligent programming assistant. "
            "I run completely locally as the **APCRE Proprietary AI Engine**.\\n\\n"
            "#### How I can assist you:\\n"
            "* 🔍 **Interactive Python Code Reviews:** Paste some code, type **'review'**, and I will perform an AST review & generate fixes.\\n"
            "* 💡 **Comprehensive Programming Guides:** Ask me to teach you any core computer science topic.\\n"
            "* ⚙️ **Specialized Domain Expertise:** I have deep knowledge in:\\n"
            "  - **Data Structures & Algorithms:** LinkedLists, Trees/BSTs, Graphs, Stacks/Queues, Sorting/Searching, Hashing, Dynamic Programming.\\n"
            "  - **Object-Oriented Programming (OOP):** Encapsulation, Properties, Inheritance, Polymorphism.\\n"
            "  - **Systems & Automation:** APIs (Flask), Databases (SQLite), File Handling, Exception Safety, SOLID principles.\\n\\n"
            "**Pro-tip:** Share some Python code in the editor, and then ask me to **review**, **debug**, or **explain** it!"
        )"""

new_greeting = """    if any(msg_lower.startswith(w) for w in greetings) or msg_lower == "help" or msg_lower == "":
        return (
            "Welcome to the APCRE AI Tutor Platform!\\n\\n"
            "I am your dedicated senior mentor and intelligent programming assistant. "
            "I run completely locally as the APCRE Proprietary AI Engine.\\n\\n"
            "How I can assist you:\\n"
            "- Interactive Python Code Reviews: Paste some code, type 'review', and I will perform an AST review & generate fixes.\\n"
            "- Comprehensive Programming Guides: Ask me to teach you any core computer science topic.\\n"
            "- Specialized Domain Expertise: I have deep knowledge in:\\n"
            "  - Data Structures & Algorithms: LinkedLists, Trees/BSTs, Graphs, Stacks/Queues, Sorting/Searching, Hashing, Dynamic Programming.\\n"
            "  - Object-Oriented Programming (OOP): Encapsulation, Properties, Inheritance, Polymorphism.\\n"
            "  - Systems & Automation: APIs (Flask), Databases (SQLite), File Handling, Exception Safety, SOLID principles.\\n\\n"
            "Pro-tip: Share some Python code in the editor, and then ask me to review, debug, or explain it!"
        )"""

# 2. Category header
old_cat = 'response += f"**Category:** *{db_entry[\'category\']}* | **Perceived Level:** *{state.difficulty.title()}*\\n\\n"'
new_cat = 'response += f"Category: {db_entry[\'category\']} | Perceived Level: {state.difficulty.title()}\\n\\n"'

# 3. Switch header
old_switch = 'switch_header = f"> [!NOTE]\\n> **Topic Shifting:** Smoothly transitioning from **{state.current_topic.replace(\'_\', \' \').title()}** to **{topic.replace(\'_\', \' \').title()}**.\\n\\n"'
new_switch = 'switch_header = f"Topic Shifting: Smoothly transitioning from {state.current_topic.replace(\'_\', \' \').title()} to {topic.replace(\'_\', \' \').title()}.\\n\\n"'

# 4. Tip/Analogy
old_analogy = 'response += f"> [!TIP]\\n> **Real-world Analogy:** {db_entry.get(\'analogy\', \'A structured representation.\')}\\n\\n"'
new_analogy = 'response += f"Real-world Analogy: {db_entry.get(\'analogy\', \'A structured representation.\')}\\n\\n"'

# 5. Beginner note
old_beg = 'response += "*(This is a beginner-friendly conceptual explanation. You can ask for \'advanced insights\' or \'code implementation\' to dive deeper!)*\\n\\n"'
new_beg = 'response += "(This is a beginner-friendly conceptual explanation. You can ask for \'advanced insights\' or \'code implementation\' to dive deeper!)\\n\\n"'

# 6. Title description
old_title_desc = 'response += f"Here is a production-level, optimized, and docstring-documented implementation of **{db_entry[\'title\']}**:\\n\\n"'
new_title_desc = 'response += f"Here is a production-level, optimized, and docstring-documented implementation of {db_entry[\'title\']}:\\n\\n"'

# 7. Helper guidance
old_helper = 'response += "💬 *Would you like me to show you the **code**, explain a **dry run** trace, list **complexity** bounds, or identify **edge cases** for this topic? Tell me what you need!*"'
new_helper = 'response += "Would you like me to show you the code, explain a dry run trace, list complexity bounds, or identify edge cases for this topic? Tell me what you need!"'

# Apply
replacements = [
    (old_greeting, new_greeting, "Greeting Block"),
    (old_cat, new_cat, "Category Details"),
    (old_switch, new_switch, "Switch Header Details"),
    (old_analogy, new_analogy, "Analogy blockquote details"),
    (old_beg, new_beg, "Beginner Guidance details"),
    (old_title_desc, new_title_desc, "Title Implementation Description"),
    (old_helper, new_helper, "Friendly Helper Guidance prompt")
]

success_count = 0
for idx, (old, new, desc) in enumerate(replacements, 1):
    if old in content:
        content = content.replace(old, new)
        print(f"Success {idx}: Replaced '{desc}' successfully.")
        success_count += 1
    else:
        # Check normalized search
        old_norm = old.replace('\r\n', '\n')
        if old_norm in content:
            content = content.replace(old_norm, new.replace('\r\n', '\n'))
            print(f"Success {idx} (Normalized): Replaced '{desc}'.")
            success_count += 1
        else:
            print(f"Warning {idx}: Could not find '{desc}' in content.")

if success_count > 0:
    with open(api_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Formatting] Applied {success_count} format cleanup replacements in Editor backend.")
else:
    print("[Formatting] No format changes applied.")
