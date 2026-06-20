# -*- coding: utf-8 -*-
"""
APCRE Services - Design Review Agent (DRA)
Phase 6 of the APCRE Implementation Plan.

Performs comprehensive architectural and design-quality analysis on Python
source code using only the standard-library `ast` module.  All evaluations
run 100% offline with zero external API calls.

Evaluation axes:
  1. SOLID Principles compliance (SRP, OCP, LSP, ISP, DIP)
  2. Design Patterns detection  (Singleton, Factory, Observer, Strategy)
  3. Code Smells detection       (monoliths, deep nesting, bare excepts,
                                  global mutations, magic numbers)
  4. Technical Debt estimation   (refactoring hours derived from smells)

Returns a structured dict with keys:
  solid_violations, design_patterns, code_smells,
  technical_debt_hours, overall_score (0-100), recommendations
"""

import os
import sys
import ast
import re
import math

# ---------------------------------------------------------------------------
# Safe print helper for Windows CP-1252 terminals
# ---------------------------------------------------------------------------

def _safe_print(*args, **kwargs):
    """Print with fallback encoding to prevent CP-1252 crashes on Windows."""
    try:
        print(*args, **kwargs)
    except (UnicodeEncodeError, UnicodeDecodeError, OSError):
        try:
            text = " ".join(str(a) for a in args)
            print(text.encode("ascii", errors="replace").decode("ascii"), **kwargs)
        except Exception:
            pass


# ===========================================================================
#  Design Review Engine
# ===========================================================================

class DesignReviewEngine:
    """
    AI-Powered Design Review Engine.
    Evaluates Python source for SOLID adherence, known design patterns,
    code smells, and projected technical-debt cost.
    """

    # ── Tuneable thresholds ────────────────────────────────────────────────
    MAX_CLASS_LINES         = 200   # SRP: lines-of-code cap per class
    MAX_METHODS_PER_CLASS   = 15    # ISP: method-count cap per class
    MAX_METHOD_LINES        = 50    # Code-smell: monolithic method
    MAX_NESTING_DEPTH       = 3     # Code-smell: deep nesting
    MAX_INHERITANCE_DEPTH   = 4     # LSP: deep inheritance chains
    MAX_PARAMS_PER_METHOD   = 7     # Code-smell: too many parameters
    MAGIC_NUMBER_THRESHOLD  = 2     # Ignore 0, 1, 2 (common sentinels)

    # ── Technical-debt cost model (hours per occurrence) ───────────────────
    DEBT_WEIGHTS = {
        "solid_violation":   1.5,
        "code_smell_minor":  0.25,
        "code_smell_major":  0.75,
        "code_smell_critical": 2.0,
    }

    # ------------------------------------------------------------------
    def __init__(self):
        """Initialise the engine — no external dependencies required."""
        self._tree = None
        self._source_lines = []
        self._filename = ""

    # ==================================================================
    #  Public API
    # ==================================================================

    def review(self, code: str, filename: str = "") -> dict:
        """
        Run the full design review pipeline on *code*.

        Parameters
        ----------
        code : str
            Raw Python source code to analyse.
        filename : str, optional
            Filename hint for contextual reporting.

        Returns
        -------
        dict
            {
              "solid_violations":     [...],
              "design_patterns":      [...],
              "code_smells":          [...],
              "technical_debt_hours": float,
              "overall_score":        int,   # 0-100
              "recommendations":      [...]
            }
        """
        self._filename = filename or "<anonymous>"
        self._source_lines = code.splitlines()

        # Attempt to parse the AST ─ return a graceful error on failure
        try:
            self._tree = ast.parse(code, filename=self._filename)
        except SyntaxError as exc:
            return {
                "solid_violations": [],
                "design_patterns": [],
                "code_smells": [{
                    "id": "SMELL_SYNTAX_ERROR",
                    "severity": "CRITICAL",
                    "message": f"Cannot parse source: {exc}",
                    "line": getattr(exc, "lineno", None),
                }],
                "technical_debt_hours": 4.0,
                "overall_score": 0,
                "recommendations": [
                    "Fix the syntax error before any design review can proceed."
                ],
            }

        # Run each analysis pass
        solid       = self._check_solid_principles()
        patterns    = self._detect_design_patterns()
        smells      = self._detect_code_smells()
        debt_hours  = self._estimate_technical_debt(solid, smells)
        score       = self._compute_overall_score(solid, smells, debt_hours)
        recs        = self._generate_recommendations(solid, patterns, smells)

        return {
            "solid_violations":     solid,
            "design_patterns":      patterns,
            "code_smells":          smells,
            "technical_debt_hours": round(debt_hours, 2),
            "overall_score":        score,
            "recommendations":      recs,
        }

    # ==================================================================
    #  SOLID Principles Compliance
    # ==================================================================

    def _check_solid_principles(self) -> list:
        """Evaluate SRP, OCP, LSP, ISP, DIP on every class in the AST."""
        violations = []

        classes = [n for n in ast.walk(self._tree) if isinstance(n, ast.ClassDef)]

        for cls_node in classes:
            cls_name = cls_node.name
            cls_start = cls_node.lineno
            cls_end = self._node_end_line(cls_node)
            cls_lines = cls_end - cls_start + 1

            methods = [n for n in cls_node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            public_methods = [m for m in methods if not m.name.startswith("_")]

            # ── SRP: Single Responsibility ────────────────────────────
            if cls_lines > self.MAX_CLASS_LINES:
                violations.append({
                    "principle": "SRP",
                    "class": cls_name,
                    "line": cls_start,
                    "message": (
                        f"Class '{cls_name}' spans {cls_lines} lines "
                        f"(threshold {self.MAX_CLASS_LINES}). "
                        "Consider splitting into smaller, focused classes."
                    ),
                })

            # ── ISP: Interface Segregation ────────────────────────────
            if len(public_methods) > self.MAX_METHODS_PER_CLASS:
                violations.append({
                    "principle": "ISP",
                    "class": cls_name,
                    "line": cls_start,
                    "message": (
                        f"Class '{cls_name}' exposes {len(public_methods)} "
                        f"public methods (threshold {self.MAX_METHODS_PER_CLASS}). "
                        "Consider segregating into smaller interfaces."
                    ),
                })

            # ── OCP: Open/Closed ──────────────────────────────────────
            # Heuristic: long if/elif chains inside methods suggest the
            # class is not open for extension via polymorphism.
            for method in methods:
                elif_count = self._count_elif_chains(method)
                if elif_count >= 5:
                    violations.append({
                        "principle": "OCP",
                        "class": cls_name,
                        "line": method.lineno,
                        "message": (
                            f"Method '{cls_name}.{method.name}' contains "
                            f"{elif_count} elif branches. "
                            "Favour polymorphism or strategy patterns "
                            "to keep the class closed for modification."
                        ),
                    })

            # ── LSP: Liskov Substitution ──────────────────────────────
            # Check inheritance depth via recursive base resolution.
            depth = self._inheritance_depth(cls_node, classes)
            if depth > self.MAX_INHERITANCE_DEPTH:
                violations.append({
                    "principle": "LSP",
                    "class": cls_name,
                    "line": cls_start,
                    "message": (
                        f"Class '{cls_name}' has an inheritance depth of "
                        f"{depth} (threshold {self.MAX_INHERITANCE_DEPTH}). "
                        "Deep hierarchies risk violating the Liskov "
                        "Substitution Principle."
                    ),
                })

            # ── DIP: Dependency Inversion ─────────────────────────────
            # Heuristic: __init__ body directly instantiates concrete
            # classes (Name calls) instead of accepting abstractions.
            init_methods = [m for m in methods if m.name == "__init__"]
            for init in init_methods:
                concrete_deps = self._find_concrete_instantiations(init)
                if len(concrete_deps) >= 3:
                    violations.append({
                        "principle": "DIP",
                        "class": cls_name,
                        "line": init.lineno,
                        "message": (
                            f"Class '{cls_name}.__init__' directly creates "
                            f"{len(concrete_deps)} concrete objects "
                            f"({', '.join(concrete_deps[:5])}). "
                            "Consider injecting dependencies via "
                            "constructor parameters or abstract factories."
                        ),
                    })

        return violations

    # ==================================================================
    #  Design Pattern Detection
    # ==================================================================

    def _detect_design_patterns(self) -> list:
        """Detect common GoF patterns via AST and naming heuristics."""
        patterns = []

        classes = [n for n in ast.walk(self._tree) if isinstance(n, ast.ClassDef)]

        for cls_node in classes:
            cls_name = cls_node.name
            methods = [n for n in cls_node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            method_names = [m.name for m in methods]

            # ── Singleton ─────────────────────────────────────────────
            # Presence of `_instance` attribute and `__new__` or
            # `get_instance` / `getInstance` method.
            body_src = ast.dump(cls_node)
            has_instance_attr = "_instance" in body_src
            has_new_or_getter = (
                "__new__" in method_names
                or "get_instance" in method_names
                or "getInstance" in method_names
            )
            if has_instance_attr and has_new_or_getter:
                patterns.append({
                    "pattern": "Singleton",
                    "class": cls_name,
                    "line": cls_node.lineno,
                    "confidence": "HIGH",
                    "evidence": "Detected `_instance` attribute with "
                                "`__new__` or `get_instance` method.",
                })

            # ── Factory ───────────────────────────────────────────────
            # Method named `create_*` or `build_*` that returns
            # different types, or a class whose name ends with Factory.
            factory_methods = [
                m for m in methods
                if m.name.startswith("create") or m.name.startswith("build")
            ]
            if factory_methods or cls_name.endswith("Factory"):
                evidence_parts = []
                if cls_name.endswith("Factory"):
                    evidence_parts.append(f"Class name '{cls_name}' ends with 'Factory'")
                if factory_methods:
                    names = ", ".join(m.name for m in factory_methods)
                    evidence_parts.append(f"Factory methods detected: {names}")
                patterns.append({
                    "pattern": "Factory",
                    "class": cls_name,
                    "line": cls_node.lineno,
                    "confidence": "MEDIUM",
                    "evidence": "; ".join(evidence_parts) + ".",
                })

            # ── Observer ──────────────────────────────────────────────
            # Methods named subscribe/unsubscribe/notify (or add_observer
            # / remove_observer / notify_observers).
            observer_keywords = {
                "subscribe", "unsubscribe", "notify",
                "add_observer", "remove_observer", "notify_observers",
                "attach", "detach", "notify_all",
                "register", "unregister",
            }
            found_observer = observer_keywords.intersection(set(method_names))
            if len(found_observer) >= 2:
                patterns.append({
                    "pattern": "Observer",
                    "class": cls_name,
                    "line": cls_node.lineno,
                    "confidence": "HIGH",
                    "evidence": (
                        f"Observer lifecycle methods detected: "
                        f"{', '.join(sorted(found_observer))}."
                    ),
                })

            # ── Strategy ──────────────────────────────────────────────
            # A class that stores a callable/strategy in __init__ and
            # delegates to it, OR named *Strategy.
            strategy_hints = (
                cls_name.endswith("Strategy")
                or "set_strategy" in method_names
                or "execute" in method_names
            )
            stores_callable = any(
                "strategy" in ast.dump(m).lower()
                for m in methods if m.name == "__init__"
            )
            if strategy_hints and stores_callable:
                patterns.append({
                    "pattern": "Strategy",
                    "class": cls_name,
                    "line": cls_node.lineno,
                    "confidence": "MEDIUM",
                    "evidence": "Strategy storage and delegation detected.",
                })
            elif cls_name.endswith("Strategy"):
                patterns.append({
                    "pattern": "Strategy",
                    "class": cls_name,
                    "line": cls_node.lineno,
                    "confidence": "LOW",
                    "evidence": f"Class name '{cls_name}' follows Strategy naming convention.",
                })

        return patterns

    # ==================================================================
    #  Code Smells Detection
    # ==================================================================

    def _detect_code_smells(self) -> list:
        """Identify structural code smells across the entire AST."""
        smells = []

        # ── Monolithic methods (>50 lines) ────────────────────────────
        for node in ast.walk(self._tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_len = self._node_end_line(node) - node.lineno + 1
                if func_len > self.MAX_METHOD_LINES:
                    smells.append({
                        "id": "SMELL_MONOLITHIC_METHOD",
                        "severity": "MAJOR",
                        "line": node.lineno,
                        "message": (
                            f"Function/method '{node.name}' spans {func_len} "
                            f"lines (threshold {self.MAX_METHOD_LINES}). "
                            "Extract helper functions for readability."
                        ),
                    })

                # ── Too many parameters ───────────────────────────────
                param_count = self._count_params(node)
                if param_count > self.MAX_PARAMS_PER_METHOD:
                    smells.append({
                        "id": "SMELL_TOO_MANY_PARAMS",
                        "severity": "MINOR",
                        "line": node.lineno,
                        "message": (
                            f"Function '{node.name}' accepts {param_count} "
                            f"parameters (threshold {self.MAX_PARAMS_PER_METHOD}). "
                            "Consider a parameter object or builder."
                        ),
                    })

        # ── Deeply nested loops / conditionals (depth > 3) ────────────
        self._walk_nesting(self._tree, 0, smells)

        # ── Bare except clauses ───────────────────────────────────────
        for node in ast.walk(self._tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    smells.append({
                        "id": "SMELL_BARE_EXCEPT",
                        "severity": "MAJOR",
                        "line": node.lineno,
                        "message": (
                            "Bare `except:` clause silently swallows all "
                            "exceptions including KeyboardInterrupt. "
                            "Catch specific exception types."
                        ),
                    })

        # ── Global mutations ──────────────────────────────────────────
        for node in ast.walk(self._tree):
            if isinstance(node, ast.Global):
                for name in node.names:
                    smells.append({
                        "id": "SMELL_GLOBAL_MUTATION",
                        "severity": "MAJOR",
                        "line": node.lineno,
                        "message": (
                            f"Global variable '{name}' mutated inside a "
                            "function scope. Prefer passing state explicitly "
                            "or using class attributes."
                        ),
                    })

        # ── Magic numbers ─────────────────────────────────────────────
        for node in ast.walk(self._tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # Skip trivial values 0, 1, -1, 2 and values used in
                # obvious contexts (line numbers, range args, etc.)
                if abs(node.value) > self.MAGIC_NUMBER_THRESHOLD:
                    # Only flag if not inside a constant assignment
                    # (NAME = 42 at module level is fine)
                    parent_is_assign = self._parent_is_module_assign(node)
                    if not parent_is_assign:
                        smells.append({
                            "id": "SMELL_MAGIC_NUMBER",
                            "severity": "MINOR",
                            "line": getattr(node, "lineno", 0),
                            "message": (
                                f"Magic number {node.value} detected. "
                                "Extract into a named constant for clarity."
                            ),
                        })

        return smells

    # ==================================================================
    #  Technical Debt Estimation
    # ==================================================================

    def _estimate_technical_debt(self, solid: list, smells: list) -> float:
        """Estimate refactoring effort in developer-hours."""
        hours = 0.0
        hours += len(solid) * self.DEBT_WEIGHTS["solid_violation"]

        for s in smells:
            sev = s.get("severity", "MINOR").upper()
            if sev == "CRITICAL":
                hours += self.DEBT_WEIGHTS["code_smell_critical"]
            elif sev == "MAJOR":
                hours += self.DEBT_WEIGHTS["code_smell_major"]
            else:
                hours += self.DEBT_WEIGHTS["code_smell_minor"]

        return hours

    # ==================================================================
    #  Overall Score (0-100)
    # ==================================================================

    def _compute_overall_score(self, solid: list, smells: list,
                               debt_hours: float) -> int:
        """
        Composite quality score.  Starts at 100 and deducts points
        for violations, smells, and debt.
        """
        score = 100.0

        # SOLID violations: -8 each (capped at -40)
        score -= min(len(solid) * 8, 40)

        # Smells: variable weight
        for s in smells:
            sev = s.get("severity", "MINOR").upper()
            if sev == "CRITICAL":
                score -= 15
            elif sev == "MAJOR":
                score -= 5
            else:
                score -= 2

        # Technical debt penalty: -1 per 0.5 hours (capped at -20)
        score -= min(debt_hours * 2, 20)

        return max(0, min(100, int(round(score))))

    # ==================================================================
    #  Recommendations
    # ==================================================================

    def _generate_recommendations(self, solid: list, patterns: list,
                                   smells: list) -> list:
        """Generate prioritised, actionable recommendations."""
        recs = []

        # ── SOLID-based recommendations ───────────────────────────────
        principles_violated = set(v["principle"] for v in solid)

        if "SRP" in principles_violated:
            recs.append(
                "SOLID/SRP: One or more classes are too large. "
                "Decompose them into cohesive, single-responsibility units."
            )
        if "OCP" in principles_violated:
            recs.append(
                "SOLID/OCP: Long if/elif chains indicate the code is not "
                "open for extension. Introduce polymorphism or the "
                "Strategy pattern."
            )
        if "LSP" in principles_violated:
            recs.append(
                "SOLID/LSP: Deep inheritance hierarchies risk breaking "
                "substitutability. Prefer composition over inheritance."
            )
        if "ISP" in principles_violated:
            recs.append(
                "SOLID/ISP: Classes expose too many public methods. "
                "Split into focused interfaces or mix-in classes."
            )
        if "DIP" in principles_violated:
            recs.append(
                "SOLID/DIP: Concrete dependencies are instantiated "
                "directly. Inject abstractions via constructor parameters."
            )

        # ── Smell-based recommendations ───────────────────────────────
        smell_ids = set(s["id"] for s in smells)

        if "SMELL_MONOLITHIC_METHOD" in smell_ids:
            recs.append(
                "Refactoring: Break long methods into smaller helper "
                "functions (aim for <50 lines each)."
            )
        if "SMELL_BARE_EXCEPT" in smell_ids:
            recs.append(
                "Error Handling: Replace bare `except:` with specific "
                "exception types to avoid masking bugs."
            )
        if "SMELL_GLOBAL_MUTATION" in smell_ids:
            recs.append(
                "State Management: Eliminate `global` mutations. Pass "
                "state via parameters or encapsulate in a class."
            )
        if "SMELL_MAGIC_NUMBER" in smell_ids:
            recs.append(
                "Readability: Extract magic numbers into named constants "
                "at module or class level."
            )
        if "SMELL_TOO_MANY_PARAMS" in smell_ids:
            recs.append(
                "API Design: Functions with many parameters are hard to "
                "use. Consider a parameter object or keyword arguments."
            )

        # ── Pattern-based guidance ────────────────────────────────────
        pattern_names = set(p["pattern"] for p in patterns)

        if "Singleton" in pattern_names:
            recs.append(
                "Pattern Note: Singleton detected — ensure thread safety "
                "and avoid hidden global state."
            )
        if "Observer" in pattern_names:
            recs.append(
                "Pattern Note: Observer pattern detected — consider using "
                "weak references to prevent memory leaks."
            )

        if not recs:
            recs.append(
                "Excellent! No significant design issues detected. "
                "The codebase follows clean architecture principles."
            )

        return recs

    # ==================================================================
    #  AST Helper Utilities
    # ==================================================================

    def _node_end_line(self, node: ast.AST) -> int:
        """Return the last line number occupied by *node*."""
        if hasattr(node, "end_lineno") and node.end_lineno is not None:
            return node.end_lineno
        # Fallback: walk children
        max_line = getattr(node, "lineno", 1)
        for child in ast.walk(node):
            ln = getattr(child, "lineno", 0)
            if ln > max_line:
                max_line = ln
        return max_line

    def _count_elif_chains(self, node: ast.AST) -> int:
        """Count the longest if/elif chain length inside *node*."""
        max_chain = 0
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                chain = 1
                cursor = child
                while cursor.orelse:
                    if (len(cursor.orelse) == 1
                            and isinstance(cursor.orelse[0], ast.If)):
                        chain += 1
                        cursor = cursor.orelse[0]
                    else:
                        break
                if chain > max_chain:
                    max_chain = chain
        return max_chain

    def _inheritance_depth(self, cls_node: ast.ClassDef,
                           all_classes: list) -> int:
        """Calculate maximum inheritance depth for *cls_node*."""
        class_map = {c.name: c for c in all_classes}
        visited = set()

        def _depth(name: str) -> int:
            if name in visited or name not in class_map:
                return 0
            visited.add(name)
            cls = class_map[name]
            max_d = 0
            for base in cls.bases:
                base_name = None
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                if base_name:
                    d = 1 + _depth(base_name)
                    if d > max_d:
                        max_d = d
            return max_d

        return _depth(cls_node.name)

    def _find_concrete_instantiations(self, node: ast.AST) -> list:
        """Return names of classes directly instantiated inside *node*."""
        names = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    # Heuristic: PascalCase names are likely class constructors
                    name = child.func.id
                    if name and name[0].isupper():
                        names.append(name)
        return names

    def _count_params(self, func_node: ast.FunctionDef) -> int:
        """Count the total parameters of a function (excluding 'self'/'cls')."""
        args = func_node.args
        count = len(args.args) + len(args.posonlyargs) + len(args.kwonlyargs)
        if args.vararg:
            count += 1
        if args.kwarg:
            count += 1
        # Subtract self/cls
        if args.args and args.args[0].arg in ("self", "cls"):
            count -= 1
        return count

    def _walk_nesting(self, node: ast.AST, depth: int, smells: list):
        """
        Recursively walk the AST tracking nesting depth of loops and
        conditionals. Flag when depth exceeds the threshold.
        """
        nesting_types = (ast.For, ast.While, ast.If, ast.With,
                         ast.AsyncFor, ast.AsyncWith)

        for child in ast.iter_child_nodes(node):
            if isinstance(child, nesting_types):
                new_depth = depth + 1
                if new_depth > self.MAX_NESTING_DEPTH:
                    smells.append({
                        "id": "SMELL_DEEP_NESTING",
                        "severity": "MAJOR",
                        "line": child.lineno,
                        "message": (
                            f"Nesting depth {new_depth} exceeds threshold "
                            f"of {self.MAX_NESTING_DEPTH}. "
                            "Extract inner blocks into helper functions."
                        ),
                    })
                self._walk_nesting(child, new_depth, smells)
            else:
                self._walk_nesting(child, depth, smells)

    def _parent_is_module_assign(self, target_node: ast.AST) -> bool:
        """
        Check whether *target_node* is the value side of a module-level
        assignment (e.g. ``MAX_SIZE = 1024``).  If so, it is a named
        constant and should NOT be flagged as a magic number.
        """
        for node in self._tree.body:
            if isinstance(node, ast.Assign):
                # Walk the value sub-tree
                for child in ast.walk(node.value):
                    if child is target_node:
                        return True
            elif isinstance(node, ast.AnnAssign) and node.value:
                for child in ast.walk(node.value):
                    if child is target_node:
                        return True
        return False


# =======================================================================
#  Standalone Self-Test
# =======================================================================

if __name__ == "__main__":
    engine = DesignReviewEngine()

    sample_code = '''\
import os
import hashlib

THRESHOLD = 100
counter = 0

class UserManager:
    """Manages user CRUD, auth, logging, emailing — too many responsibilities."""

    def __init__(self):
        self.db = DatabaseConnection()
        self.cache = RedisCache()
        self.logger = FileLogger()
        self.mailer = SMTPMailer()

    def get_user(self, user_id):
        global counter
        counter += 1
        query = "SELECT * FROM users WHERE id = " + str(user_id)
        return query

    def create_user(self, name, email, age, role, department, location, phone, manager):
        """Too many parameters — code smell."""
        if role == "admin":
            pass
        elif role == "editor":
            pass
        elif role == "viewer":
            pass
        elif role == "guest":
            pass
        elif role == "superadmin":
            pass
        elif role == "auditor":
            pass

    def delete_user(self, uid):
        try:
            os.remove(f"/data/users/{uid}")
        except:
            pass

    def send_email(self, to, subject, body):
        pass

    def log_action(self, action):
        pass

    def compute_metrics(self, data):
        result = 0
        for i in data:
            for j in data:
                for k in data:
                    for m in data:
                        result += i * j * k * m * 3.14159
        return result

    def export_report(self, fmt):
        pass

    def import_data(self, source):
        pass

    def validate_input(self, value):
        if value > 42:
            return True
        return False

    def archive_user(self, uid):
        pass

    def restore_user(self, uid):
        pass

    def merge_users(self, uid1, uid2):
        pass

    def split_account(self, uid):
        pass

    def transfer_ownership(self, from_uid, to_uid):
        pass

    def generate_token(self, uid):
        return hashlib.md5(str(uid).encode()).hexdigest()

    def revoke_token(self, token):
        pass


class EventBus:
    """Observer pattern implementation."""

    def __init__(self):
        self._listeners = {}

    def subscribe(self, event, callback):
        self._listeners.setdefault(event, []).append(callback)

    def unsubscribe(self, event, callback):
        if event in self._listeners:
            self._listeners[event].remove(callback)

    def notify(self, event, *args):
        for cb in self._listeners.get(event, []):
            cb(*args)


class DatabaseSingleton:
    """Singleton pattern implementation."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_instance(cls):
        return cls._instance
'''

    result = engine.review(sample_code, "example_module.py")

    _safe_print("=" * 70)
    _safe_print("  APCRE Design Review Agent - Self-Test Report")
    _safe_print("=" * 70)

    _safe_print(f"\n  Overall Design Score : {result['overall_score']} / 100")
    _safe_print(f"  Technical Debt Est.  : {result['technical_debt_hours']} hours")

    _safe_print(f"\n--- SOLID Violations ({len(result['solid_violations'])}) ---")
    for v in result["solid_violations"]:
        _safe_print(f"  [{v['principle']}] Line {v['line']}: {v['message']}")

    _safe_print(f"\n--- Design Patterns ({len(result['design_patterns'])}) ---")
    for p in result["design_patterns"]:
        _safe_print(f"  [{p['pattern']}] {p['class']} (confidence: {p['confidence']})")
        _safe_print(f"    Evidence: {p['evidence']}")

    _safe_print(f"\n--- Code Smells ({len(result['code_smells'])}) ---")
    for s in result["code_smells"]:
        _safe_print(f"  [{s['severity']}] Line {s.get('line', '?')}: {s['message']}")

    _safe_print(f"\n--- Recommendations ({len(result['recommendations'])}) ---")
    for idx, r in enumerate(result["recommendations"], 1):
        _safe_print(f"  {idx}. {r}")

    _safe_print("\n" + "=" * 70)
    _safe_print("  Self-test complete.")
    _safe_print("=" * 70)
