import zipfile
import shutil
import os

src_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis.docx"
tmp_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\APCRE_Final_Year_Thesis_tmp.docx"

def perform_replacements():
    print(f"Reading {src_path}...")
    replacements = {
        "(Vite/React Client)": "(Next.js Client)",
        "React (Vite build system) executing client-side state machine on port 5173.": "React (Next.js build system) executing client-side state machine on port 3000.",
        "React (Vite build system) executing client-side state machine on port 5173": "React (Next.js build system) executing client-side state machine on port 3000",
        "Secure Express.js Proxy Middleware:": "Secure Node.js Proxy Gateway:",
        " A robust backend acting as a gateway and command whitelist server on Port 5000.": " A robust backend acting as a gateway whitelisting commands, resolving dynamic ports, and coordinating WebRTC Voice & Video call channels entirely on Port 5000.",
        "mediation/security proxy layer (Express.js)": "mediation/security proxy layer (Node.js Gateway)",
        "Express security gateway on port 5000": "Node.js security gateway on port 5000",
        "Express proxy": "Node.js Gateway proxy",
        "Express Security Gateway:": "Node.js Security Gateway:",
        "Node.js server exposing REST APIs and managing Whitelist inputs on port 5000.": "Node.js server exposing REST APIs, whitelisting commands, managing inputs, and coordinating WebRTC calls on port 5000.",
        "stateful educational tutoring system. The stateful assistant maintains session context, dynamically adjusts conversational tone to the user’s experience levels, and provides line-by-line dry-run traces of 153 critical algorithms and structures.": "stateful educational tutoring system. The stateful assistant maintains session context, dynamically adjusts conversational tone to the user’s experience levels, integrates with local Ollama completions (like Llama-3) to respond dynamically like GPT, and provides line-by-line dry-run traces of 153 critical algorithms and structures, augmented by a custom Scikit-Learn ML Quality Ensemble code classifier.",
        "custom scikit-learn model executing local code quality classifications, and a stateful educational tutoring system.": "custom scikit-learn model executing local code quality classifications, a stateful educational tutoring system with local Ollama LLM integration, and a peer-to-peer WebRTC Voice, Video, and Screen Sharing Room system."
    }

    with zipfile.ZipFile(src_path, 'r') as src_zip:
        with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as tmp_zip:
            for item in src_zip.infolist():
                content = src_zip.read(item.filename)
                if item.filename == 'word/document.xml':
                    xml_str = content.decode('utf-8')
                    print("\n--- Performing XML String Replacements ---")
                    for old_text, new_text in replacements.items():
                        clean_old = old_text.replace("**", "")
                        clean_new = new_text.replace("**", "")
                        if clean_old in xml_str:
                            xml_str = xml_str.replace(clean_old, clean_new)
                            print(f"[OK] Replaced: '{clean_old[:40]}' -> '{clean_new[:40]}'")
                        else:
                            print(f"[WARN] Term not found in XML: '{clean_old[:40]}'")
                    content = xml_str.encode('utf-8')
                tmp_zip.writestr(item, content)

    # Overwrite the original docx file with the updated temporary docx
    shutil.move(tmp_path, src_path)
    print("\nSuccessfully updated APCRE_Final_Year_Thesis.docx!")

if __name__ == "__main__":
    perform_replacements()
