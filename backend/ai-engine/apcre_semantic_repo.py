# -*- coding: utf-8 -*-
"""
APCRE Services - Phase 14: Semantic Repository Intelligence
Crawls Python repositories, performs deep AST-based structural extraction of
functions, classes, and modules, then builds semantic inter-module links using
CodeEmbedder cosine similarity. Designed for 100% offline operation with zero
external API dependencies.

Key capabilities:
  - Recursive Python file discovery with smart directory exclusions
  - Full AST extraction: functions, classes, module-level docstrings
  - Function summaries: name, args, return type hints, docstring, line count,
    detected side effects (file I/O, network, subprocess, database)
  - Class summaries: name, methods list, base classes, constructor args,
    encapsulation score (public vs private member ratio)
  - Module summaries: filename, top-level functions, classes, imports
  - Architecture summary: total files, modules, dependency map
  - Semantic link graph via CodeEmbedder cosine similarity (threshold > 0.85)
"""

import os
import sys
import ast
import re

# Ensure sibling modules are importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Graceful CodeEmbedder import with fallback
try:
    from code_embedder import CodeEmbedder
    HAS_EMBEDDER = True
except ImportError:
    HAS_EMBEDDER = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ---------------------------------------------------------------------------
# Side-effect detection patterns
# ---------------------------------------------------------------------------
# Calls or attribute accesses that indicate file I/O operations
_FILE_IO_PATTERNS = re.compile(
    r"\b(open|read|write|readlines|writelines|readline|"
    r"os\.path|os\.remove|os\.rename|os\.makedirs|os\.mkdir|os\.listdir|"
    r"shutil\.copy|shutil\.move|shutil\.rmtree|"
    r"pathlib\.Path|json\.load|json\.dump|csv\.reader|csv\.writer)\b",
    re.IGNORECASE,
)

# Calls that indicate network / HTTP operations
_NETWORK_PATTERNS = re.compile(
    r"\b(requests\.|urllib\.|http\.client|socket\.|httplib|"
    r"urlopen|urlretrieve|aiohttp|httpx)\b",
    re.IGNORECASE,
)

# Calls that indicate subprocess / OS command execution
_SUBPROCESS_PATTERNS = re.compile(
    r"\b(subprocess\.|os\.system|os\.popen|os\.exec|Popen|"
    r"exec\(|eval\(|compile\()\b",
    re.IGNORECASE,
)

# Calls that indicate database operations
_DATABASE_PATTERNS = re.compile(
    r"\b(sqlite3\.|psycopg2\.|mysql\.|pymongo\.|sqlalchemy\.|"
    r"connect\(|cursor\(|execute\(|commit\(|rollback\()\b",
    re.IGNORECASE,
)

# Directories to skip during recursive crawling
_SKIP_DIRS = frozenset({
    ".venv", "venv", "env", ".env",
    "node_modules", "__pycache__", ".git",
    "dist", "build", ".tox", ".eggs",
    "site-packages", ".mypy_cache", ".pytest_cache",
})


def safe_print(text: str) -> None:
    """Windows-safe console print that handles CP1252 encoding issues."""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(text.encode("ascii", errors="replace").decode("ascii"))


class SemanticRepositoryIntelligence:
    """
    Deep semantic analysis engine for Python repositories.
    Extracts structural metadata via AST and builds semantic similarity
    links between modules using offline code embeddings.
    """

    def __init__(self):
        """
        Initialises the semantic repository intelligence engine.
        Attempts to load CodeEmbedder for semantic link construction;
        falls back gracefully if unavailable.
        """
        self.embedder = CodeEmbedder() if HAS_EMBEDDER else None
        self._similarity_threshold = 0.85

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_repository(self, repo_path: str) -> dict:
        """
        Performs a complete semantic analysis of a Python repository.

        Parameters
        ----------
        repo_path : str
            Absolute or relative path to the repository root directory.

        Returns
        -------
        dict
            Keys:
              functions          – list of function summary dicts
              classes            – list of class summary dicts
              modules            – list of module summary dicts
              architecture_summary – high-level architecture dict
              semantic_links     – list of module-pair similarity dicts
        """
        if not os.path.exists(repo_path):
            return self._empty_result("Repository path does not exist: " + repo_path)

        # 1. Discover Python files
        py_files = self._crawl_python_files(repo_path)
        if not py_files:
            return self._empty_result("No Python files found in: " + repo_path)

        all_functions = []
        all_classes = []
        all_modules = []
        dependency_map = {}  # module_name -> list of imported module names
        module_sources = {}  # rel_path -> source code (for embedding)

        # 2. Parse each file
        for filepath in py_files:
            rel_path = os.path.relpath(filepath, repo_path)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                    source = fh.read()
            except Exception:
                continue

            module_sources[rel_path] = source

            try:
                tree = ast.parse(source, filename=rel_path)
            except SyntaxError:
                # Record the module but skip detailed extraction
                all_modules.append({
                    "filename": rel_path,
                    "top_level_functions": [],
                    "classes": [],
                    "imports": [],
                    "module_docstring": None,
                    "parse_error": True,
                })
                continue

            # Extract module-level docstring
            module_docstring = ast.get_docstring(tree)

            # Extract imports
            imports = self._extract_imports(tree)
            module_name = os.path.splitext(os.path.basename(filepath))[0]
            dependency_map[module_name] = imports

            # Extract functions and classes
            func_summaries = []
            class_summaries = []
            source_lines = source.splitlines()

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    summary = self._extract_function_summary(node, source_lines, rel_path)
                    func_summaries.append(summary)
                    all_functions.append(summary)

                elif isinstance(node, ast.ClassDef):
                    cls_summary = self._extract_class_summary(node, source_lines, rel_path)
                    class_summaries.append(cls_summary)
                    all_classes.append(cls_summary)

                    # Also extract methods as functions (with class context)
                    for item in ast.iter_child_nodes(node):
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            method_summary = self._extract_function_summary(
                                item, source_lines, rel_path,
                                parent_class=node.name,
                            )
                            all_functions.append(method_summary)

            all_modules.append({
                "filename": rel_path,
                "top_level_functions": [f["name"] for f in func_summaries],
                "classes": [c["name"] for c in class_summaries],
                "imports": imports,
                "module_docstring": module_docstring,
                "parse_error": False,
            })

        # 3. Build architecture summary
        architecture_summary = {
            "total_files": len(py_files),
            "total_modules": len(all_modules),
            "total_functions": len(all_functions),
            "total_classes": len(all_classes),
            "dependency_map": dependency_map,
        }

        # 4. Build semantic links
        semantic_links = self._build_semantic_links(module_sources)

        return {
            "functions": all_functions,
            "classes": all_classes,
            "modules": all_modules,
            "architecture_summary": architecture_summary,
            "semantic_links": semantic_links,
        }

    # ------------------------------------------------------------------
    # File discovery
    # ------------------------------------------------------------------

    def _crawl_python_files(self, root_dir: str) -> list:
        """Recursively discovers .py files while skipping irrelevant directories."""
        py_files = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Prune skipped directories in-place so os.walk does not descend
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            for fname in filenames:
                if fname.endswith(".py"):
                    py_files.append(os.path.join(dirpath, fname))
        return py_files

    # ------------------------------------------------------------------
    # AST extraction helpers
    # ------------------------------------------------------------------

    def _extract_imports(self, tree: ast.Module) -> list:
        """Returns a deduplicated list of top-level imported module names."""
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
        return sorted(imports)

    def _extract_function_summary(
        self,
        node,
        source_lines: list,
        rel_path: str,
        parent_class: str = None,
    ) -> dict:
        """
        Builds a rich summary dict for a single function or method node.
        """
        # Basic metadata
        name = node.name
        docstring = ast.get_docstring(node)
        is_async = isinstance(node, ast.AsyncFunctionDef)

        # Line count
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start_line
        line_count = end_line - start_line + 1

        # Arguments
        args_info = self._extract_args(node.args)

        # Return type hint
        return_type = None
        if node.returns:
            try:
                return_type = ast.unparse(node.returns)
            except Exception:
                return_type = "<complex>"

        # Side-effect detection on the function body source
        body_source = "\n".join(source_lines[start_line - 1: end_line])
        side_effects = self._detect_side_effects(body_source)

        # Decorator list
        decorators = []
        for dec in node.decorator_list:
            try:
                decorators.append(ast.unparse(dec))
            except Exception:
                decorators.append("<decorator>")

        return {
            "name": name,
            "qualified_name": f"{parent_class}.{name}" if parent_class else name,
            "module": rel_path,
            "args": args_info,
            "return_type": return_type,
            "docstring": docstring,
            "line_number": start_line,
            "line_count": line_count,
            "is_async": is_async,
            "decorators": decorators,
            "side_effects": side_effects,
            "parent_class": parent_class,
        }

    def _extract_args(self, arguments_node: ast.arguments) -> list:
        """Extracts argument names and their type annotations from an ast.arguments node."""
        args_list = []
        for arg in arguments_node.args:
            annotation = None
            if arg.annotation:
                try:
                    annotation = ast.unparse(arg.annotation)
                except Exception:
                    annotation = "<complex>"
            args_list.append({
                "name": arg.arg,
                "type_hint": annotation,
            })
        return args_list

    def _extract_class_summary(
        self,
        node: ast.ClassDef,
        source_lines: list,
        rel_path: str,
    ) -> dict:
        """
        Builds a rich summary dict for a single class definition node.
        """
        name = node.name
        docstring = ast.get_docstring(node)

        # Base classes
        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except Exception:
                bases.append("<complex>")

        # Line count
        start_line = node.lineno
        end_line = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start_line
        line_count = end_line - start_line + 1

        # Methods and attributes
        methods = []
        constructor_args = []
        public_members = 0
        private_members = 0

        for item in ast.iter_child_nodes(node):
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)

                # Count public vs private for encapsulation score
                if item.name.startswith("_") and not item.name.startswith("__"):
                    private_members += 1
                elif not item.name.startswith("_"):
                    public_members += 1

                # Extract constructor args
                if item.name == "__init__":
                    constructor_args = self._extract_args(item.args)
                    # Remove 'self' from constructor args
                    constructor_args = [a for a in constructor_args if a["name"] != "self"]

        # Encapsulation score: ratio of explicitly private members
        total_members = public_members + private_members
        if total_members > 0:
            # Higher score = better encapsulation (more private members)
            encapsulation_score = round((private_members / total_members) * 100, 1)
        else:
            encapsulation_score = 100.0  # No members = no violations

        # Decorators on the class itself
        decorators = []
        for dec in node.decorator_list:
            try:
                decorators.append(ast.unparse(dec))
            except Exception:
                decorators.append("<decorator>")

        return {
            "name": name,
            "module": rel_path,
            "base_classes": bases,
            "methods": methods,
            "constructor_args": constructor_args,
            "docstring": docstring,
            "line_number": start_line,
            "line_count": line_count,
            "encapsulation_score": encapsulation_score,
            "decorators": decorators,
            "method_count": len(methods),
        }

    # ------------------------------------------------------------------
    # Side-effect detection
    # ------------------------------------------------------------------

    def _detect_side_effects(self, source_fragment: str) -> list:
        """
        Scans a source code fragment for known side-effect patterns.
        Returns a list of detected side-effect categories.
        """
        effects = []
        if _FILE_IO_PATTERNS.search(source_fragment):
            effects.append("file_io")
        if _NETWORK_PATTERNS.search(source_fragment):
            effects.append("network")
        if _SUBPROCESS_PATTERNS.search(source_fragment):
            effects.append("subprocess")
        if _DATABASE_PATTERNS.search(source_fragment):
            effects.append("database")
        return effects

    # ------------------------------------------------------------------
    # Semantic link construction
    # ------------------------------------------------------------------

    def _build_semantic_links(self, module_sources: dict) -> list:
        """
        Computes pairwise cosine similarity between all module embeddings
        and returns links where similarity exceeds the configured threshold.

        Parameters
        ----------
        module_sources : dict
            Mapping of relative file path -> full source code string.

        Returns
        -------
        list of dict
            Each dict contains: module_a, module_b, similarity
        """
        if not self.embedder or not HAS_NUMPY:
            return []

        # Generate embeddings
        paths = list(module_sources.keys())
        if len(paths) < 2:
            return []

        embeddings = {}
        for path in paths:
            try:
                emb = self.embedder.get_embedding(module_sources[path])
                embeddings[path] = emb
            except Exception:
                continue

        if len(embeddings) < 2:
            return []

        # Compute pairwise cosine similarity
        links = []
        emb_paths = list(embeddings.keys())
        for i in range(len(emb_paths)):
            for j in range(i + 1, len(emb_paths)):
                vec_a = embeddings[emb_paths[i]]
                vec_b = embeddings[emb_paths[j]]
                similarity = self._cosine_similarity(vec_a, vec_b)
                if similarity >= self._similarity_threshold:
                    links.append({
                        "module_a": emb_paths[i],
                        "module_b": emb_paths[j],
                        "similarity": round(float(similarity), 4),
                    })

        # Sort by descending similarity
        links.sort(key=lambda x: x["similarity"], reverse=True)
        return links

    @staticmethod
    def _cosine_similarity(vec_a, vec_b) -> float:
        """Computes cosine similarity between two numpy vectors."""
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _empty_result(self, message: str) -> dict:
        """Returns a standardised empty result dict with an error message."""
        return {
            "functions": [],
            "classes": [],
            "modules": [],
            "architecture_summary": {
                "total_files": 0,
                "total_modules": 0,
                "total_functions": 0,
                "total_classes": 0,
                "dependency_map": {},
                "error": message,
            },
            "semantic_links": [],
        }


# ======================================================================
# Self-test block
# ======================================================================
if __name__ == "__main__":
    safe_print("=" * 72)
    safe_print("APCRE Phase 14 - Semantic Repository Intelligence - Self Test")
    safe_print("=" * 72)

    engine = SemanticRepositoryIntelligence()

    # Use the ai-engine directory itself as the test repository
    test_repo = os.path.dirname(os.path.abspath(__file__))
    safe_print(f"\n[*] Analysing repository: {test_repo}")

    result = engine.analyze_repository(test_repo)

    # Architecture summary
    arch = result["architecture_summary"]
    safe_print(f"\n--- Architecture Summary ---")
    safe_print(f"  Total files     : {arch['total_files']}")
    safe_print(f"  Total modules   : {arch['total_modules']}")
    safe_print(f"  Total functions : {arch['total_functions']}")
    safe_print(f"  Total classes   : {arch['total_classes']}")
    safe_print(f"  Dependencies    : {len(arch['dependency_map'])} modules mapped")

    # Show first 5 functions
    safe_print(f"\n--- Functions (showing first 5 of {len(result['functions'])}) ---")
    for func in result["functions"][:5]:
        side = ", ".join(func["side_effects"]) if func["side_effects"] else "none"
        rtype = func["return_type"] or "untyped"
        safe_print(f"  {func['qualified_name']}() -> {rtype}  [{func['line_count']} lines] side_effects=[{side}]")

    # Show first 5 classes
    safe_print(f"\n--- Classes (showing first 5 of {len(result['classes'])}) ---")
    for cls in result["classes"][:5]:
        bases = ", ".join(cls["base_classes"]) if cls["base_classes"] else "none"
        safe_print(f"  {cls['name']} (bases: {bases}) [{cls['method_count']} methods, encapsulation={cls['encapsulation_score']}%]")

    # Show first 5 modules
    safe_print(f"\n--- Modules (showing first 5 of {len(result['modules'])}) ---")
    for mod in result["modules"][:5]:
        safe_print(f"  {mod['filename']}: {len(mod['top_level_functions'])} functions, {len(mod['classes'])} classes, {len(mod['imports'])} imports")

    # Semantic links
    safe_print(f"\n--- Semantic Links (cosine > {engine._similarity_threshold}) ---")
    if result["semantic_links"]:
        for link in result["semantic_links"][:10]:
            safe_print(f"  {link['module_a']} <-> {link['module_b']}  similarity={link['similarity']}")
    else:
        if not HAS_EMBEDDER:
            safe_print("  [WARN] CodeEmbedder not available - semantic links disabled")
        else:
            safe_print("  No module pairs exceeded the similarity threshold.")

    safe_print(f"\n{'=' * 72}")
    safe_print("Phase 14 self-test complete.")
    safe_print("=" * 72)
