import os

api_file = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_api.py"

with open(api_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

for kw in ["openai", "gemini", "google", "ollama", "api_key", "llm", "groq", "gpt", "model"]:
    if kw in content.lower():
        print(f"Found {kw}")
