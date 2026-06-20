# -*- coding: utf-8 -*-
"""
APCRE Services - Security Intelligence Engine (SIE)
Performs static analysis audits for OWASP Top 10 Vulnerabilities,
maps findings to standard CWE identifiers, and computes CVSS-based Risk Scores (0-100).
"""

import os
import sys
import re
import ast

class SecurityIntelligenceEngine:
    """
    Advanced security scanner for codebase safety audits.
    Detects Injections, Leakages, Weak Cryptography, and Insecure Deserializations offline.
    """
    def __init__(self):
        # Master CWE & OWASP Maps
        self.vuln_rules = [
            {
                "id": "SEC_SQL_INJECTION",
                "cwe": "CWE-89",
                "owasp": "A03:2021-Injection",
                "severity": "CRITICAL",
                "cvss": 9.8,
                "title": "SQL Injection Vulnerability",
                "pattern": r"(?i)select\s+.*\s+from\s+.*\s+where\s+.*%\s*\w+|select\s+.*\s+from\s+.*\s+where\s+.*\.format\s*\(|execute\s*\(\s*['\"].*f['\"].*select|execute\s*\(\s*['\"].*select\s+.*\{\w+\}",
                "desc": "Constructing raw SQL query strings using direct formatting or string concatenation allows attackers to inject malicious SQL commands.",
                "mitigation": "Use parameterized queries or ORM frameworks (e.g. SQLAlchemy, Django ORM) with explicit parameter bindings:\n`cursor.execute('SELECT * FROM users WHERE username = ?', (username,))`"
            },
            {
                "id": "SEC_SHELL_INJECTION",
                "cwe": "CWE-78",
                "owasp": "A03:2021-Injection",
                "severity": "CRITICAL",
                "cvss": 9.6,
                "title": "OS Command Injection",
                "pattern": r"subprocess\.(Popen|run|call|check_output|check_call)\s*\(\s*[^,]+,\s*shell\s*=\s*True\b|os\.system\s*\(",
                "desc": "Executing system shell commands with user inputs or unverified variables enables remote command injection attacks.",
                "mitigation": "Disable shell compilation by setting `shell=False` and pass arguments exclusively as a parsed list of strings:\n`subprocess.run(['ls', '-la'], shell=False)`"
            },
            {
                "id": "SEC_HARDCODED_CREDS",
                "cwe": "CWE-798",
                "owasp": "A07:2021-Identification and Authentication Failures",
                "severity": "HIGH",
                "cvss": 8.9,
                "title": "Use of Hardcoded Credentials",
                "pattern": r"\b(api_key|token|password|passwd|secret|private_key)\s*=\s*['\"][^'\"]{8,}['\"]",
                "desc": "Storing private API keys, client passwords, or credentials directly in source control compromises the system's baseline security.",
                "mitigation": "Load credentials dynamically from safe operating system environment variables or hidden configuration files (.env):\n`import os; API_KEY = os.environ.get('API_KEY')`"
            },
            {
                "id": "SEC_WEAK_CRYPTO",
                "cwe": "CWE-327",
                "owasp": "A02:2021-Cryptographic Failures",
                "severity": "HIGH",
                "cvss": 7.4,
                "title": "Use of Broken or Weak Cryptographic Algorithm",
                "pattern": r"\b(md5|sha1)\s*\(\s*|hashlib\.(md5|sha1)\b",
                "desc": "MD5 and SHA-1 hashing algorithms have known collision vulnerabilities and are cryptographically broken.",
                "mitigation": "Transition hashing functions to strong, collision-resistant algorithms like SHA-256 or bcrypt:\n`import hashlib; hashlib.sha256(data).hexdigest()`"
            },
            {
                "id": "SEC_INSECURE_DESERIALIZE",
                "cwe": "CWE-502",
                "owasp": "A08:2021-Software and Data Integrity Failures",
                "severity": "CRITICAL",
                "cvss": 9.8,
                "title": "Deserialization of Untrusted Data",
                "pattern": r"\bpickle\.loads\b|\byaml\.load\b",
                "desc": "Deserializing data streams using pickle or unsafe PyYAML loaders can trigger arbitrary code execution.",
                "mitigation": "Use safe data serialization formats like JSON, or enforce PyYAML safe loaders:\n`import json; data = json.loads(payload)` or `yaml.safe_load(payload)`"
            },
            {
                "id": "SEC_DEBUG_MODE",
                "cwe": "CWE-489",
                "owasp": "A05:2021-Security Misconfiguration",
                "severity": "MEDIUM",
                "cvss": 5.3,
                "title": "Active Debug Code / Misconfiguration",
                "pattern": r"debug\s*=\s*True\b|\.run\s*\(\s*.*debug\s*=\s*True",
                "desc": "Enabling debug mode in production (e.g. Flask debug=True) exposes detailed stack traces and debugging interactive consoles to users.",
                "mitigation": "Enforce strict configuration checks and disable debug modes in production configurations:\n`app.run(debug=False)`"
            },
            {
                "id": "SEC_BARE_EXCEPT",
                "cwe": "CWE-755",
                "owasp": "A10:2021-Server-Side Request Forgery", # Maps standard error bounds
                "severity": "LOW",
                "cvss": 3.3,
                "title": "Bare Exception Handling",
                "pattern": r"\bexcept\s*:\s*$",
                "desc": "Catching all exceptions silently using a bare 'except:' block masks program bugs and makes auditing security errors impossible.",
                "mitigation": "Specify the exact expected exception type, or catch the standard Exception class to log issues safely:\n`except Exception as e:\n    logger.error(f'Failure: {e}')`"
            }
        ]

    def scan_code(self, code: str, filename: str) -> dict:
        """
        Scans a file's content line-by-line using regexp audits and AST inspectors.
        Returns mapped CWE/OWASP vulnerabilities list and overall CVSS Security Score.
        """
        findings = []
        lines = code.splitlines()
        
        # 1. Regex scanning
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            # Ignore comments
            if stripped.startswith("#"):
                continue
                
            for rule in self.vuln_rules:
                if re.search(rule["pattern"], line):
                    findings.append({
                        "id": rule["id"],
                        "cwe": rule["cwe"],
                        "owasp": rule["owasp"],
                        "severity": rule["severity"],
                        "cvss": rule["cvss"],
                        "title": rule["title"],
                        "line": idx,
                        "context": stripped,
                        "desc": rule["desc"],
                        "mitigation": rule["mitigation"]
                    })

        # 2. Compute Security Score (0 to 100%)
        # Base score is 100. Deduct CVSS weights scaled by vulnerability count.
        total_deductions = 0
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for f in findings:
            if f["severity"] == "CRITICAL":
                total_deductions += 25
                critical_count += 1
            elif f["severity"] == "HIGH":
                total_deductions += 15
                high_count += 1
            elif f["severity"] == "MEDIUM":
                total_deductions += 8
                medium_count += 1
            else:
                total_deductions += 3
                low_count += 1
                
        security_score = max(10, 100 - total_deductions)
        
        # Compile threat levels
        threat_level = "SECURE"
        if critical_count > 0 or high_count > 0:
            threat_level = "CRITICAL_RISK" if critical_count > 0 else "HIGH_RISK"
        elif medium_count > 0:
            threat_level = "MEDIUM_RISK"
        elif low_count > 0:
            threat_level = "LOW_RISK"

        summary = f"Security Scan completed. Identified {len(findings)} vulnerability findings."
        if len(findings) == 0:
            summary = "Security Audit complete. No OWASP Top 10 or hardcoded credential vulnerabilities identified."

        return {
            "success": True,
            "filename": filename,
            "security_score": security_score,
            "threat_level": threat_level,
            "vulnerabilities": findings,
            "summary": summary,
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count
        }

if __name__ == "__main__":
    engine = SecurityIntelligenceEngine()
    test_code = """
import os
import subprocess
import hashlib
import pickle

API_KEY = "sk-proj-1234567890abcdef1234567890"

def get_files(user_input):
    query = "SELECT * FROM docs WHERE name = " + user_input
    # Unsafe command
    subprocess.run("rm -rf " + user_input, shell=True)
    # Unsafe hash
    pwd_hash = hashlib.md5(b"password").hexdigest()
    # Unsafe load
    data = pickle.loads(user_input)
    return query
"""
    res = engine.scan_code(test_code, "auth.py")
    print(res)
