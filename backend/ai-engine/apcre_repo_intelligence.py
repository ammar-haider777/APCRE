# -*- coding: utf-8 -*-
"""
APCRE Services - Repository-Scale Intelligence & Graphing Engine
Crawls workspaces, parses cross-module dependencies, builds Directed Graphs
via NetworkX, and computes Architecture, Security, Scalability, and Maintainability.
"""

import os
import re
import sys
import numpy as np

# Try importing NetworkX with a robust standard library dictionary fallback
try:
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False

# Ensure tree-sitter parser is accessible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tree_sitter_parser import MultiLangParser

class RepositoryIntelligence:
    """
    Automated crawler and static structure graphing engine for multi-file repositories.
    """
    def __init__(self):
        self.parser = MultiLangParser()
        self.dependency_graph = nx.DiGraph() if HAS_NX else {}
        self.architecture_graph = nx.DiGraph() if HAS_NX else {}
        self.complexity_graph = nx.DiGraph() if HAS_NX else {}
        
    def analyze_repository(self, workspace_dir: str) -> dict:
        """
        Crawls a workspace, parses all Python, Java, C++, JS, and TS files,
        builds structural NetworkX graphs, and computes final project scores.
        """
        if not os.path.exists(workspace_dir):
            return self._empty_result("Workspace directory does not exist.")
            
        py_files = []
        for root, _, filenames in os.walk(workspace_dir):
            # Ignore binary/venv/caching directories to prevent bloat
            if any(x in root for x in (".venv", "node_modules", "__pycache__", ".git", "dist", "build", ".next", "scratch", ".system_generated", ".agents", "public")):
                continue
            for fname in filenames:
                if fname.endswith((".py", ".java", ".cpp", ".cc", ".js", ".ts", ".jsx", ".tsx")):
                    py_files.append(os.path.join(root, fname))
                    
        if not py_files:
            return self._empty_result("No source files found in the specified workspace.")

        # Reset graphs
        if HAS_NX:
            self.dependency_graph.clear()
            self.architecture_graph.clear()
            self.complexity_graph.clear()
        else:
            self.dependency_graph = {}
            self.architecture_graph = {}
            self.complexity_graph = {}

        # Parsing states
        total_classes = 0
        total_methods = 0
        encapsulation_violations = 0
        security_vulnerabilities = 0
        nested_loop_risks = 0
        overall_complexity = 0
        missing_docstrings = 0
        total_lines = 0
        
        file_metrics = {}
        cross_imports = []
        db_issues = []
        circular_imports = []
        repository_classes_map = []
        repository_imports_map = []

        # 1. Walk through all files and extract metrics & dependencies
        for filepath in py_files:
            filename = os.path.basename(filepath)
            rel_path = os.path.relpath(filepath, workspace_dir)
            
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue
                
            lines = content.splitlines()
            total_lines += len(lines)
            
            # Statically detect imports
            imported_modules = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("import ") or stripped.startswith("from "):
                    parts = stripped.split()
                    if len(parts) >= 2:
                        if parts[0] == "import":
                            # capture e.g. 'os'
                            mod_name = parts[1].split(",")[0].split(".")[0]
                            imported_modules.append(mod_name)
                        elif parts[0] == "from":
                            mod_name = parts[1].split(".")[0]
                            imported_modules.append(mod_name)

            file_metrics[rel_path] = imported_modules
            
            # Map dependency node
            if HAS_NX:
                self.dependency_graph.add_node(rel_path, type="file", lines=len(lines))
                for imp in imported_modules:
                    # Find if imported file exists in our repository list
                    for possible_file in py_files:
                        poss_rel = os.path.relpath(possible_file, workspace_dir)
                        poss_base = os.path.splitext(os.path.basename(possible_file))[0]
                        if imp == poss_base and poss_rel != rel_path:
                            self.dependency_graph.add_edge(rel_path, poss_rel, relationship="Imports")
                            cross_imports.append({
                                "from_file": rel_path,
                                "imported_file": poss_rel
                            })

            # Check database transaction configuration smells
            if any(kw in content.lower() for kw in ("sqlite", "postgres", "mysql", "connect", "sqlalchemy", "db")):
                if "autocommit" not in content.lower() and "commit()" not in content.lower():
                    db_issues.append({
                        "file": rel_path,
                        "title": "Missing Explicit Database Commit Guarantee",
                        "desc": "Found connection triggers without safe autocommit scopes or transactional commit blocks."
                    })
                if "select * from" in content.lower():
                    db_issues.append({
                        "file": rel_path,
                        "title": "Wildcard SQL Query",
                        "desc": "Using 'SELECT *' causes schema coupling and unnecessary memory overhead."
                    })

            # Run parsing metrics
            ext = os.path.splitext(filename)[1]
            lang_map = {".py": "python", ".java": "java", ".cpp": "cpp", ".cc": "cpp", ".js": "javascript", ".ts": "typescript", ".jsx": "javascript", ".tsx": "typescript"}
            lang = lang_map.get(ext, "python")
            
            try:
                struct = self.parser.parse_structure(content, lang)
                total_classes += struct["classes"]
                total_methods += struct["methods"]
                encapsulation_violations += struct["encapsulation_violations"]
                security_vulnerabilities += struct["security_anti_patterns"]
                nested_loop_risks += struct["nested_loops"]
                overall_complexity += struct["cyclomatic_complexity"]
                
                # Append structures
                if struct.get("classes_details"):
                    repository_classes_map.append({
                        "file": rel_path,
                        "classes": struct["classes_details"]
                    })
                if struct.get("imports_list"):
                    repository_imports_map.append({
                        "file": rel_path,
                        "imports": struct["imports_list"]
                    })

                # Check for docstrings heuristic
                if lang == "python":
                    docstring_matches = len(re.findall(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', content))
                    if docstring_matches < struct["methods"]:
                        missing_docstrings += (struct["methods"] - docstring_matches)
                else:
                    comments = len(re.findall(r"/\*[\s\S]*?\*/|//.*", content))
                    if comments < struct["methods"]:
                        missing_docstrings += (struct["methods"] - comments)

                # Add architecture & complexity nodes
                if HAS_NX:
                    if struct["classes"] > 0:
                        self.architecture_graph.add_node(rel_path, classes=struct["classes"], inheritance=struct["max_inheritance_depth"])
                    if struct["methods"] > 0:
                        self.complexity_graph.add_node(rel_path, methods=struct["methods"], complexity=struct["cyclomatic_complexity"])
            except Exception:
                pass

        # 2. Check for circular imports using NetworkX cycles finder
        if HAS_NX:
            try:
                cycles = list(nx.simple_cycles(self.dependency_graph))
                for cyc in cycles:
                    circular_imports.append(" -> ".join(cyc) + " -> " + cyc[0])
            except Exception:
                pass

        # 3. Calculate scores (0 - 100%)
        
        # Architecture Score: encapsulation mutations + circular imports
        arch_deductions = (encapsulation_violations * 6) + (len(circular_imports) * 20)
        arch_score = max(20, min(100, 100 - arch_deductions))

        # Security Score: vulnerabilities + credentials/injections
        sec_deductions = (security_vulnerabilities * 25) + (len(re.findall(r"\b(api_key|token|password|secret)\s*=\s*['\"][^'\"]{8,}['\"]", str(py_files), re.I)) * 30)
        sec_score = max(10, min(100, 100 - sec_deductions))

        # Scalability Score: nested loop complexity + database transaction faults
        scale_deductions = (nested_loop_risks * 15) + (len(db_issues) * 12) + (overall_complexity > 50) * 15
        scale_score = max(25, min(100, 100 - scale_deductions))

        # Maintainability Score: size + complexity + missing documentation
        methods_per_class = total_methods / max(1, total_classes)
        maint_deductions = (methods_per_class > 8) * 10 + (missing_docstrings * 3) + (overall_complexity > 40) * 15 + (total_lines > 2000) * 10
        maint_score = max(30, min(100, 100 - maint_deductions))

        summary_msg = f"Successfully crawled and audited repository. Analyzed {len(py_files)} source files ({total_lines} lines of code)."

        return {
            "success": True,
            "architecture_score": int(arch_score),
            "security_score": int(sec_score),
            "scalability_score": int(scale_score),
            "maintainability_score": int(maint_score),
            "files_analyzed": len(py_files),
            "total_lines": total_lines,
            "total_classes": total_classes,
            "total_methods": total_methods,
            "encapsulation_violations": encapsulation_violations,
            "nested_loop_risks": nested_loop_risks,
            "security_vulnerabilities": security_vulnerabilities,
            "database_schema_issues": db_issues,
            "circular_imports": circular_imports,
            "cross_file_imports": cross_imports,
            "repository_classes_map": repository_classes_map,
            "repository_imports_map": repository_imports_map,
            "summary": summary_msg
        }

    def _empty_result(self, msg: str) -> dict:
        return {
            "success": False,
            "architecture_score": 100,
            "security_score": 100,
            "scalability_score": 100,
            "maintainability_score": 100,
            "files_analyzed": 0,
            "total_lines": 0,
            "total_classes": 0,
            "total_methods": 0,
            "encapsulation_violations": 0,
            "nested_loop_risks": 0,
            "security_vulnerabilities": 0,
            "database_schema_issues": [],
            "circular_imports": [],
            "cross_file_imports": [],
            "summary": msg
        }
