# -*- coding: utf-8 -*-
"""
APCRE Services - Executable Task Planner Agent
Decomposes complex requests into task Directed Acyclic Graphs (DAGs) using NetworkX,
estimating risk, McCabe complexity weights, and refactoring sequences.
"""

import os
import sys
import re
import ast

try:
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False

class TaskPlanner:
    """
    Intelligent software planning agent. Decomposes coding challenges,
    estimates complexity and risk, and constructs task dependency DAGs.
    """
    def __init__(self, workspace_dir: str = ""):
        self.workspace_dir = workspace_dir
        self.dag = nx.DiGraph() if HAS_NX else {}

    def plan_task(self, prompt: str, code: str = "", filename: str = "script.py") -> dict:
        """
        Decomposes a user task and active code into a structured execution DAG.
        Estimates McCabe complexity weightings, potential risks, and returns a serializable plan.
        """
        # 1. Parse existing code features for complexity estimates
        cyclomatic_complexity = self._estimate_mccabe_complexity(code)
        risk_level, risk_factors = self._estimate_risk_level(code, cyclomatic_complexity, prompt)
        
        # 2. Decompose prompt and code into discrete sub-tasks
        subtasks = self._decompose_tasks(prompt, code, filename, cyclomatic_complexity, risk_level)
        
        # 3. Build NetworkX Directed Acyclic Graph (DAG) for the tasks
        nodes = []
        edges = []
        
        if HAS_NX:
            self.dag.clear()
            # Add nodes
            for task in subtasks:
                self.dag.add_node(
                    task["id"],
                    title=task["title"],
                    description=task["description"],
                    estimated_complexity=task["estimated_complexity"],
                    risk=task["risk"]
                )
                nodes.append({
                    "id": task["id"],
                    "title": task["title"],
                    "description": task["description"],
                    "estimated_complexity": task["estimated_complexity"],
                    "risk": task["risk"]
                })
            
            # Add sequential dependency edges
            for i in range(len(subtasks) - 1):
                self.dag.add_edge(subtasks[i]["id"], subtasks[i+1]["id"])
                edges.append({
                    "from": subtasks[i]["id"],
                    "to": subtasks[i+1]["id"],
                    "relationship": "RequiresCompletionOf"
                })
            
            # Get topological order
            try:
                topological_order = list(nx.topological_sort(self.dag))
            except nx.NetworkXUnfeasible:
                topological_order = [t["id"] for t in subtasks]
        else:
            # Fallback when NetworkX is not installed
            for task in subtasks:
                nodes.append({
                    "id": task["id"],
                    "title": task["title"],
                    "description": task["description"],
                    "estimated_complexity": task["estimated_complexity"],
                    "risk": task["risk"]
                })
            for i in range(len(subtasks) - 1):
                edges.append({
                    "from": subtasks[i]["id"],
                    "to": subtasks[i+1]["id"],
                    "relationship": "RequiresCompletionOf"
                })
            topological_order = [t["id"] for t in subtasks]

        return {
            "success": True,
            "target_file": filename,
            "mccabe_complexity": cyclomatic_complexity,
            "estimated_risk": risk_level,
            "risk_factors": risk_factors,
            "topological_order": topological_order,
            "tasks": nodes,
            "dependencies": edges,
            "summary": f"Decomposed target task into {len(nodes)} sequential executable sub-tasks."
        }

    def _estimate_mccabe_complexity(self, code: str) -> int:
        """Statically estimates McCabe cyclomatic complexity of Python code using AST."""
        if not code.strip():
            return 1
        
        try:
            tree = ast.parse(code)
            complexity = 1
            # McCabe cyclomatic complexity: V(G) = E - N + 2P
            # Simple heuristic: 1 + number of branching decision points (if, for, while, except, bool ops)
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            return complexity
        except Exception:
            # Lexical fallback regex count
            branch_points = len(re.findall(r"\b(if|for|while|except|with|and|or)\b", code))
            return 1 + branch_points

    def _estimate_risk_level(self, code: str, complexity: int, prompt: str) -> tuple:
        """Determines the task execution risk level (Low, Medium, High)."""
        factors = []
        risk_score = 0
        
        # Check code structure
        if complexity > 12:
            factors.append("High Cyclomatic Complexity (>12)")
            risk_score += 3
        elif complexity > 6:
            factors.append("Moderate Cyclomatic Complexity (>6)")
            risk_score += 1

        if "import subprocess" in code or "subprocess.run" in code or "subprocess.Popen" in code:
            factors.append("OS Subprocess commands executing in script")
            risk_score += 3
        if "eval(" in code or "exec(" in code:
            factors.append("Dynamic script evaluation (eval/exec)")
            risk_score += 4
        if "sqlite" in code.lower() or "db.connect" in code.lower() or "sql" in code.lower():
            factors.append("Database connection or SQL schema manipulations")
            risk_score += 2

        # Check prompt indicators
        p_lower = prompt.lower()
        if any(w in p_lower for w in ["database", "schema", "migration", "sql"]):
            factors.append("Task requests transactional data adjustments")
            risk_score += 2
        if any(w in p_lower for w in ["optimize", "refactor", "complexity", "speed"]):
            factors.append("Algorithmic optimization requested")
            risk_score += 1
        if any(w in p_lower for w in ["thread", "asyncio", "parallel", "concurrency"]):
            factors.append("Concurrent thread safety required")
            risk_score += 3

        if risk_score >= 6:
            level = "HIGH"
        elif risk_score >= 3:
            level = "MEDIUM"
        else:
            level = "LOW"
            
        if not factors:
            factors.append("None detected. Standard clean refactoring pipeline.")

        return level, factors

    def _decompose_tasks(self, prompt: str, code: str, filename: str, complexity: int, risk: str) -> list:
        """Decomposes the prompt into structured components."""
        subtasks = []
        
        # Task 1: Static Code Smell Audit and Planning
        subtasks.append({
            "id": "T1_STATIC_AUDIT",
            "title": "Statically Audit Code Structures & Identify Smells",
            "description": f"Scan '{filename}' for bare exceptions, unused imports, magic numbers, and complexity limits.",
            "estimated_complexity": 2,
            "risk": "LOW"
        })
        
        # Task 2: Core Semantic Feature Enhancements
        p_lower = prompt.lower()
        core_desc = "Implement prompt request requirements and adapt functions signatures."
        if "oop" in p_lower or "class" in p_lower:
            core_desc = "Apply premium OOP patterns: enforce encapsulation properties and class constructor bounds."
        elif any(w in p_lower for w in ["sort", "search", "complexity", "algorithm", "speed"]):
            core_desc = "Optimize search/sort loops structure, eliminating O(N^2) nesting where possible."
        elif any(w in p_lower for w in ["db", "sql", "sqlite"]):
            core_desc = "Implement safe database transactional commits and configure parameters inputs."
        
        subtasks.append({
            "id": "T2_CORE_IMPLEMENT",
            "title": "Refactor Code Structures and Implement Enhancements",
            "description": core_desc,
            "estimated_complexity": max(3, complexity - 2),
            "risk": risk
        })
        
        # Task 3: Robust Exception Boundaries
        subtasks.append({
            "id": "T3_EXCEPTION_BOUND",
            "title": "Establish Error Boundaries and Parameter Sanity Checks",
            "description": "Construct explicit try-except wrappers and assert that arguments correspond to clean input guidelines.",
            "estimated_complexity": 2,
            "risk": "LOW"
        })
        
        # Task 4: Dynamic Sandbox Verification
        subtasks.append({
            "id": "T4_TEST_VERIFICATION",
            "title": "Generate Autonomous Test Suites & Verify Sandbox",
            "description": "Synthesize a unittest suite checking standard parameters, boundary conditions, and assert exit code is 0.",
            "estimated_complexity": 3,
            "risk": "MEDIUM" if risk == "HIGH" else "LOW"
        })
        
        return subtasks

if __name__ == "__main__":
    planner = TaskPlanner()
    test_code = """
def sum_even_numbers(arr):
    # Missing type assertions
    total = 0
    for x in arr:
        if x % 2 == 0:
            total += x
    return total
"""
    res = planner.plan_task("Refactor loop efficiency and add tests", test_code, "sum.py")
    print(res)
