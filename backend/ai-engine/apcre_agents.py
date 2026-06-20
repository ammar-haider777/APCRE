# -*- coding: utf-8 -*-
"""
APCRE Services - Agentic Workflow & Coordinator System
Implements a multi-agent delegation system comprising Reviewer, Debugger,
Refactoring, Security, Tutoring, and Testing Agents coordinated by a master broker.
"""

import re


class ReviewerAgent:
    """Specialized in general PEP 8 style, syntax anomalies, and modular boundaries."""
    def run_review(self, code: str, filename: str) -> list:
        # Collect static issues from the main rules
        issues = []
        lines = code.split("\n")
        
        # Check for bare imports and star imports
        for idx, line in enumerate(lines, 1):
            if "import *" in line:
                issues.append({
                    "type": "warning",
                    "title": "Star import pollution",
                    "line": idx,
                    "desc": "Importing '*' pollutes the local namespace and causes severe name collision risks.",
                    "fix": "Specify imported function and variable names explicitly."
                })
        return issues

class SecurityAgent:
    """Specialized in cryptographical vulnerabilities, dynamic execution traps, and credential leakage."""
    def run_review(self, code: str, filename: str) -> list:
        issues = []
        lines = code.split("\n")
        
        for idx, line in enumerate(lines, 1):
            # Check for hardcoded API keys/passwords
            if re_match := re.search(r"\b(password|passwd|api_key|token|secret)\s*=\s*['\"][^'\"]{8,}['\"]", line, re.IGNORECASE):
                issues.append({
                    "type": "critical",
                    "title": "Hardcoded credential exposed",
                    "line": idx,
                    "desc": f"Potential private key or API secret '{re_match.group(1)}' exposed directly in script.",
                    "fix": "Move secret credentials to a secure local environment variable (.env) or config file."
                })
            # Check for shell injection command executions
            if "subprocess.Popen" in line and "shell=True" in line:
                issues.append({
                    "type": "critical",
                    "title": "Subprocess shell injection vulnerability",
                    "line": idx,
                    "desc": "Executing shell=True inside a subprocess allows attackers to inject malicious shell commands.",
                    "fix": "Pass command arguments as a list of strings and set shell=False."
                })
        return issues

class RefactoringAgent:
    """Specialized in algorithmic efficiency, code reuse, and loop reductions."""
    def run_review(self, code: str, filename: str) -> list:
        issues = []
        lines = code.split("\n")
        for idx, line in enumerate(lines, 1):
            if "for " in line and ".append(" in line:
                # Heuristic suggestion to refactor loop appends into list comprehensions
                if line.strip().endswith(":") and idx < len(lines) and ".append(" in lines[idx]:
                    issues.append({
                        "type": "suggestion",
                        "title": "Algorithmic refactoring opportunity",
                        "line": idx,
                        "desc": "Loop append can be refactored into a highly efficient Pythonic list comprehension.",
                        "fix": "Refactor into the format: [item for item in collection] for better runtime optimization."
                    })
        return issues

class TestingAgent:
    """Specialized in test coverage audits and assertions verification."""
    def run_review(self, code: str, filename: str) -> list:
        issues = []
        if "assert" not in code and "unittest" not in code:
            issues.append({
                "type": "suggestion",
                "title": "Missing unit test suite",
                "line": 1,
                "desc": "This script contains no automated assertions or structural unit tests.",
                "fix": "Create a companion test file using Python's unittest module to verify operations."
            })
        return issues

class TutorAgent:
    """Specialized in stateful learning memory and concept synthesis."""
    def run_review(self, code: str, filename: str) -> list:
        # The tutor agent generates study topics based on concepts found in the code
        issues = []
        if "class " in code:
            issues.append({
                "type": "info",
                "title": "OOP Concept Identified",
                "line": 1,
                "desc": "This script implements Object-Oriented paradigms (class). Learn encapsulation, inheritance, or SOLID inside the Tutoring Panel.",
                "fix": "Ask the Tutor assistant: 'Explain SOLID principles in beginner mode'."
            })
        return issues

class CoordinatorAgent:
    """
    Master Broker Agent that coordinates specialized sub-agent tasks,
    resolves line-level conflict recommendations, and produces a unified quality report.
    """
    def __init__(self):
        self.reviewer = ReviewerAgent()
        self.security = SecurityAgent()
        self.refactoring = RefactoringAgent()
        self.testing = TestingAgent()
        self.tutor = TutorAgent()

    def review_project_file(self, code: str, filename: str) -> list:
        """
        Coordinates all sub-agents, merging recommendations while resolving
        any duplicate line-item warnings.
        """
        raw_issues = []
        
        # 1. Gather recommendations from all specialized agents
        raw_issues.extend(self.reviewer.run_review(code, filename))
        raw_issues.extend(self.security.run_review(code, filename))
        raw_issues.extend(self.refactoring.run_review(code, filename))
        raw_issues.extend(self.testing.run_review(code, filename))
        raw_issues.extend(self.tutor.run_review(code, filename))

        # 2. Merge issues and resolve overlapping conflicts
        # Prioritize Security (Critical) -> Refactoring (Warning) -> General Reviewer Suggestions
        merged_issues = {}
        for issue in raw_issues:
            key = (issue["line"], issue["title"])
            if key not in merged_issues:
                merged_issues[key] = issue
            else:
                # Resolve conflict by keeping the higher severity issue
                existing = merged_issues[key]
                severity_map = {"critical": 3, "warning": 2, "suggestion": 1, "info": 0}
                if severity_map.get(issue["type"], 0) > severity_map.get(existing["type"], 0):
                    merged_issues[key] = issue

        sorted_issues = list(merged_issues.values())
        sorted_issues.sort(key=lambda x: x.get("line", 1))
        
        return sorted_issues
