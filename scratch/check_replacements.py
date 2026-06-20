# Let's inspect the current state of all replacement terms

terms = [
    # 1. Vite/React Client
    {"old": "(Vite/React Client)", "new": "(Next.js Client)"},
    # 2. React (Vite build system) on 5173
    {"old": "React (Vite build system) executing client-side state machine on port 5173", "new": "React (Next.js build system) executing client-side state machine on port 3000"},
    # 3. Secure Express.js Proxy Middleware
    {"old": "Secure Express.js Proxy Middleware:", "new": "Secure Node.js Proxy Gateway:"},
    # 4. Gateway whitelist on Port 5000
    {"old": "acting as a gateway and command whitelist server on Port 5000", "new": "acting as a gateway whitelisting commands, resolving dynamic ports, and coordinating WebRTC Voice & Video call channels entirely on Port 5000"},
    # 5. mediation/security proxy layer (Express.js)
    {"old": "mediation/security proxy layer (Express.js)", "new": "mediation/security proxy layer (Node.js Gateway)"},
    # 6. Express security gateway on port 5000
    {"old": "Express security gateway on port 5000", "new": "Node.js security gateway on port 5000"},
    # 7. Express proxy
    {"old": "Express proxy", "new": "Node.js Gateway proxy"},
    # 8. Express Security Gateway:
    {"old": "Express Security Gateway:", "new": "Node.js Security Gateway:"},
    # 9. Node.js server exposing REST APIs on 5000
    {"old": "Node.js server exposing REST APIs and managing Whitelist inputs on port 5000", "new": "Node.js server exposing REST APIs, whitelisting commands, managing inputs, and coordinating WebRTC calls on port 5000"},
    # 10. Abstract tutoring system
    {"old": "provides line-by-line dry-run traces of 153 critical algorithms and structures.", "new": "integrates with local Ollama completions (like Llama-3) to respond dynamically like GPT, and provides line-by-line dry-run traces of 153 critical algorithms and structures, augmented by a custom Scikit-Learn ML Quality Ensemble code classifier."},
    # 11. Abstract custom scikit-learn
    {"old": "custom scikit-learn model executing local code quality classifications, and a stateful educational tutoring system.", "new": "custom scikit-learn model executing local code quality classifications, a stateful educational tutoring system with local Ollama LLM integration, and a peer-to-peer WebRTC Voice, Video, and Screen Sharing Room system."}
]

with open(r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\scratch\thesis_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("=== REPLACEMENT TARGET STATUS REPORT ===")
for idx, term in enumerate(terms):
    print(f"\nTerm {idx+1}:")
    
    # Check old
    old_found = term["old"] in text
    if not old_found:
        # Check subparts of old
        words = term["old"].split()
        sub_found = False
        if len(words) > 2:
            mid = " ".join(words[1:-1])
            if mid in text:
                sub_found = True
                print(f"  Old term NOT fully found, but mid-part '{mid}' is found!")
        if not sub_found:
            print("  Old term: NOT FOUND")
    else:
        print("  Old term: FOUND!")
        
    # Check new
    new_found = term["new"] in text
    if new_found:
        print("  New term: ALREADY REPLACED (FOUND!)")
    else:
        # Check subparts of new
        words = term["new"].split()
        sub_found = False
        if len(words) > 2:
            mid = " ".join(words[1:-1])
            if mid in text:
                sub_found = True
                print(f"  New term: PARTIALLY FOUND (mid-part '{mid[:50]}...')")
        if not sub_found:
            print("  New term: NOT FOUND")
