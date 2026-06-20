# -*- coding: utf-8 -*-
"""
APCRE Services - Autonomous Dataset Builder V2 (Phase 12)
Crawls Python repositories, extracts individual functions via AST parsing,
auto-labels each function with a quality class (good / needs_improvement / poor)
using offline static-analysis metrics (cyclomatic complexity, line count,
docstring presence, naming conventions, nesting depth), deduplicates samples
via SHA-256 hash comparison, and balances classes by oversampling minorities.

All processing is 100% offline with zero external API calls.
Uses only Python standard library modules: ast, os, json, hashlib, random, re, collections.
"""

import ast
import os
import json
import hashlib
import random
import re
from collections import Counter


class DatasetBuilderV2:
    """
    Repository-scale autonomous dataset builder for training APCRE quality models.
    Extracts function-level samples, computes static-analysis metrics, assigns
    quality labels, removes duplicates, and balances the final dataset.
    """

    # ── Quality thresholds ────────────────────────────────────────────
    # Cyclomatic complexity boundaries
    COMPLEXITY_GOOD_MAX = 5
    COMPLEXITY_POOR_MIN = 10

    # Line count boundaries (function body only)
    LINES_GOOD_MAX = 25
    LINES_POOR_MIN = 60

    # Maximum nesting depth boundaries
    NESTING_GOOD_MAX = 3
    NESTING_POOR_MIN = 5

    # Minimum "bad signals" to push a function into the *poor* bucket
    POOR_SIGNAL_THRESHOLD = 2
    # Minimum "good signals" to qualify for the *good* bucket
    GOOD_SIGNAL_THRESHOLD = 3

    def __init__(self, output_dir: str = "apcre_dataset"):
        """
        Initialise the dataset builder.

        Args:
            output_dir: Directory where exported dataset files will be written.
                        Created automatically on first export if it doesn't exist.
        """
        self.output_dir = output_dir
        self.samples = []           # list[dict] - final labelled samples
        self.duplicates_removed = 0
        self._seen_hashes = set()   # SHA-256 hashes for duplicate detection

    # ══════════════════════════════════════════════════════════════════
    #  PUBLIC API
    # ══════════════════════════════════════════════════════════════════

    def build_from_repository(self, repo_path: str) -> dict:
        """
        Main entry point.  Recursively crawls *repo_path* for Python files,
        extracts every function definition, labels it, deduplicates, and
        balances the resulting dataset.

        Args:
            repo_path: Absolute or relative path to a Python project directory.

        Returns:
            dict with keys:
                total_samples        - int
                class_distribution   - dict[str, int]
                duplicates_removed   - int
                samples              - list[dict]
        """
        if not os.path.isdir(repo_path):
            return self._empty_result("Repository path does not exist or is not a directory.")

        # Reset state for fresh build
        self.samples = []
        self.duplicates_removed = 0
        self._seen_hashes = set()

        # 1. Recursively discover Python files
        py_files = self._discover_python_files(repo_path)
        if not py_files:
            return self._empty_result("No Python files found in the repository.")

        # 2. Extract functions and compute metrics from each file
        raw_samples = []
        for filepath in py_files:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                    source = fh.read()
            except Exception:
                continue

            rel_path = os.path.relpath(filepath, repo_path)
            extracted = self._extract_functions(source, rel_path)
            raw_samples.extend(extracted)

        # 3. Deduplicate using SHA-256 of normalised source code
        deduped = self._deduplicate(raw_samples)

        # 4. Auto-label each sample based on static metrics
        labelled = []
        for sample in deduped:
            label = self._classify(sample["metrics"])
            sample["label"] = label
            labelled.append(sample)

        # 5. Balance classes via oversampling of minority classes
        self.samples = self._balance_classes(labelled)

        return {
            "total_samples": len(self.samples),
            "class_distribution": dict(Counter(s["label"] for s in self.samples)),
            "duplicates_removed": self.duplicates_removed,
            "samples": self.samples,
        }

    def export_json(self, output_path: str = None) -> str:
        """
        Serialise the current dataset to a JSON file.

        Args:
            output_path: Optional explicit file path.  When *None* the file is
                         written to ``<output_dir>/apcre_dataset_v2.json``.

        Returns:
            Absolute path to the written JSON file.
        """
        if output_path is None:
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(self.output_dir, "apcre_dataset_v2.json")

        parent = os.path.dirname(os.path.abspath(output_path))
        os.makedirs(parent, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(self.samples, fh, indent=2, ensure_ascii=False)

        return os.path.abspath(output_path)

    def get_statistics(self) -> dict:
        """
        Return summary statistics about the current dataset.

        Returns:
            dict with keys: total_samples, class_distribution, duplicates_removed
        """
        return {
            "total_samples": len(self.samples),
            "class_distribution": dict(Counter(s["label"] for s in self.samples)),
            "duplicates_removed": self.duplicates_removed,
        }

    # ══════════════════════════════════════════════════════════════════
    #  PRIVATE HELPERS – file discovery
    # ══════════════════════════════════════════════════════════════════

    @staticmethod
    def _discover_python_files(root_dir: str) -> list:
        """Walk *root_dir* and return a sorted list of ``.py`` file paths,
        skipping common non-source directories."""
        skip_dirs = {".venv", "venv", "node_modules", "__pycache__", ".git",
                     "dist", "build", ".tox", ".eggs", "env", ".mypy_cache"}
        py_files = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Prune ignored directories in-place so os.walk won't descend
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            for fname in filenames:
                if fname.endswith(".py"):
                    py_files.append(os.path.join(dirpath, fname))
        return sorted(py_files)

    # ══════════════════════════════════════════════════════════════════
    #  PRIVATE HELPERS – AST extraction & metrics
    # ══════════════════════════════════════════════════════════════════

    def _extract_functions(self, source: str, filename: str) -> list:
        """Parse *source* with the ``ast`` module and yield one sample dict per
        function/method definition found."""
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        source_lines = source.splitlines()
        samples = []

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            # Extract source lines for this function
            start = node.lineno - 1          # 0-indexed
            end = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start + 1
            func_lines = source_lines[start:end]
            func_code = "\n".join(func_lines)

            # Compute static metrics
            metrics = self._compute_metrics(node, func_lines)

            samples.append({
                "code": func_code,
                "label": None,               # assigned later
                "metrics": metrics,
                "filename": filename,
                "function_name": node.name,
            })

        return samples

    def _compute_metrics(self, node, func_lines: list) -> dict:
        """Compute a battery of static-analysis metrics for a single function
        AST node."""
        return {
            "cyclomatic_complexity": self._cyclomatic_complexity(node),
            "line_count": len(func_lines),
            "has_docstring": self._has_docstring(node),
            "naming_convention_ok": self._check_naming(node.name),
            "max_nesting_depth": self._max_nesting_depth(node),
            "parameter_count": self._param_count(node),
            "has_return": self._has_return(node),
            "blank_line_ratio": self._blank_ratio(func_lines),
        }

    # ── individual metric calculators ─────────────────────────────────

    @staticmethod
    def _cyclomatic_complexity(node) -> int:
        """McCabe-style cyclomatic complexity.  Counts decision points inside
        the function body (if, elif, for, while, and, or, except, with,
        assert, comprehension ifs)."""
        complexity = 1  # base path
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.IfExp)):
                complexity += 1
            elif isinstance(child, (ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, (ast.While,)):
                complexity += 1
            elif isinstance(child, (ast.ExceptHandler,)):
                complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each additional boolean operator adds a path
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += len(child.ifs)
        return complexity

    @staticmethod
    def _has_docstring(node) -> bool:
        """Return True when the function has a docstring as its first statement."""
        if not node.body:
            return False
        first = node.body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, (ast.Constant,)):
            return isinstance(first.value.value, str)
        return False

    @staticmethod
    def _check_naming(name: str) -> bool:
        """Return True when the function name follows PEP-8 snake_case or is a
        dunder method."""
        if name.startswith("__") and name.endswith("__"):
            return True
        return bool(re.match(r"^[a-z][a-z0-9_]*$", name))

    @staticmethod
    def _max_nesting_depth(node, _depth: int = 0) -> int:
        """Recursively compute the maximum nesting depth of control-flow
        structures inside *node*."""
        nesting_types = (ast.If, ast.For, ast.While, ast.With,
                         ast.AsyncFor, ast.AsyncWith, ast.Try,
                         ast.ExceptHandler)
        max_depth = _depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, nesting_types):
                child_depth = DatasetBuilderV2._max_nesting_depth(child, _depth + 1)
                if child_depth > max_depth:
                    max_depth = child_depth
            else:
                child_depth = DatasetBuilderV2._max_nesting_depth(child, _depth)
                if child_depth > max_depth:
                    max_depth = child_depth
        return max_depth

    @staticmethod
    def _param_count(node) -> int:
        """Count the total number of parameters (positional + keyword + *args + **kwargs)."""
        args = node.args
        count = len(args.args) + len(args.kwonlyargs)
        if args.vararg:
            count += 1
        if args.kwarg:
            count += 1
        return count

    @staticmethod
    def _has_return(node) -> bool:
        """Check whether the function contains at least one explicit return
        statement with a value."""
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value is not None:
                return True
        return False

    @staticmethod
    def _blank_ratio(lines: list) -> float:
        """Fraction of blank lines in the function body."""
        if not lines:
            return 0.0
        blanks = sum(1 for ln in lines if ln.strip() == "")
        return round(blanks / len(lines), 3)

    # ══════════════════════════════════════════════════════════════════
    #  PRIVATE HELPERS – deduplication
    # ══════════════════════════════════════════════════════════════════

    def _deduplicate(self, samples: list) -> list:
        """Remove exact duplicates by hashing the normalised (whitespace-
        stripped, lowered) source code with SHA-256."""
        unique = []
        for sample in samples:
            normalised = re.sub(r"\s+", "", sample["code"]).lower()
            digest = hashlib.sha256(normalised.encode("utf-8")).hexdigest()
            if digest in self._seen_hashes:
                self.duplicates_removed += 1
                continue
            self._seen_hashes.add(digest)
            unique.append(sample)
        return unique

    # ══════════════════════════════════════════════════════════════════
    #  PRIVATE HELPERS – classification & labelling
    # ══════════════════════════════════════════════════════════════════

    def _classify(self, metrics: dict) -> str:
        """Assign a quality label (``good``, ``needs_improvement``, or
        ``poor``) based on weighted static-analysis signals.

        Scoring strategy:
            • Count "good" signals and "poor" signals independently.
            • If poor signals >= POOR_SIGNAL_THRESHOLD  → ``poor``
            • If good signals >= GOOD_SIGNAL_THRESHOLD  → ``good``
            • Otherwise                                 → ``needs_improvement``
        """
        good_signals = 0
        poor_signals = 0

        # — Cyclomatic complexity ——————————————————————————
        cc = metrics["cyclomatic_complexity"]
        if cc <= self.COMPLEXITY_GOOD_MAX:
            good_signals += 1
        if cc >= self.COMPLEXITY_POOR_MIN:
            poor_signals += 1

        # — Line count ——————————————————————————————————————
        lc = metrics["line_count"]
        if lc <= self.LINES_GOOD_MAX:
            good_signals += 1
        if lc >= self.LINES_POOR_MIN:
            poor_signals += 1

        # — Docstring presence ————————————————————————————
        if metrics["has_docstring"]:
            good_signals += 1
        else:
            poor_signals += 1

        # — Naming convention ————————————————————————————
        if metrics["naming_convention_ok"]:
            good_signals += 1
        else:
            poor_signals += 1

        # — Nesting depth ————————————————————————————————
        nd = metrics["max_nesting_depth"]
        if nd <= self.NESTING_GOOD_MAX:
            good_signals += 1
        if nd >= self.NESTING_POOR_MIN:
            poor_signals += 1

        # — Return statement presence ————————————————————
        if metrics["has_return"]:
            good_signals += 1

        # Decision
        if poor_signals >= self.POOR_SIGNAL_THRESHOLD:
            return "poor"
        if good_signals >= self.GOOD_SIGNAL_THRESHOLD:
            return "good"
        return "needs_improvement"

    # ══════════════════════════════════════════════════════════════════
    #  PRIVATE HELPERS – class balancing
    # ══════════════════════════════════════════════════════════════════

    @staticmethod
    def _balance_classes(samples: list) -> list:
        """Balance the dataset by oversampling minority classes to match the
        majority class size.  Uses random selection with a fixed seed for
        reproducibility."""
        if not samples:
            return samples

        random.seed(42)

        buckets = {}
        for s in samples:
            buckets.setdefault(s["label"], []).append(s)

        max_count = max(len(v) for v in buckets.values())

        balanced = []
        for label, items in buckets.items():
            balanced.extend(items)
            deficit = max_count - len(items)
            if deficit > 0:
                oversampled = random.choices(items, k=deficit)
                balanced.extend(oversampled)

        # Shuffle to avoid label ordering bias
        random.shuffle(balanced)
        return balanced

    # ══════════════════════════════════════════════════════════════════
    #  PRIVATE HELPERS – misc
    # ══════════════════════════════════════════════════════════════════

    @staticmethod
    def _empty_result(msg: str) -> dict:
        """Return a well-formed but empty result dict with a status message."""
        return {
            "total_samples": 0,
            "class_distribution": {},
            "duplicates_removed": 0,
            "samples": [],
            "message": msg,
        }


# ══════════════════════════════════════════════════════════════════════
#  STANDALONE SELF-TEST
# ══════════════════════════════════════════════════════════════════════

def _safe_print(*args, **kwargs):
    """Print helper that gracefully handles Windows CP1252 encoding errors."""
    try:
        print(*args, **kwargs)
    except (UnicodeEncodeError, UnicodeDecodeError):
        text = " ".join(str(a) for a in args)
        print(text.encode("ascii", errors="replace").decode("ascii"))


if __name__ == "__main__":
    _safe_print("=" * 70)
    _safe_print("  APCRE Dataset Builder V2 - Self-Test")
    _safe_print("=" * 70)

    builder = DatasetBuilderV2(output_dir="apcre_dataset_test")

    # Use the ai-engine directory itself as a test repository
    test_repo = os.path.dirname(os.path.abspath(__file__))
    _safe_print(f"\n[1] Building dataset from: {test_repo}")

    result = builder.build_from_repository(test_repo)

    _safe_print(f"\n[2] Results:")
    _safe_print(f"    Total samples ........... {result['total_samples']}")
    _safe_print(f"    Class distribution ...... {result['class_distribution']}")
    _safe_print(f"    Duplicates removed ...... {result['duplicates_removed']}")

    # Show first 3 samples
    _safe_print(f"\n[3] Sample preview (first 3):")
    for i, sample in enumerate(result["samples"][:3]):
        _safe_print(f"\n    --- Sample {i + 1} ---")
        _safe_print(f"    File:     {sample['filename']}")
        _safe_print(f"    Function: {sample['function_name']}")
        _safe_print(f"    Label:    {sample['label']}")
        _safe_print(f"    Metrics:  {sample['metrics']}")
        code_preview = sample["code"][:120].replace("\n", "\\n")
        _safe_print(f"    Code:     {code_preview}...")

    # Test statistics API
    _safe_print(f"\n[4] Statistics via get_statistics():")
    stats = builder.get_statistics()
    _safe_print(f"    {stats}")

    # Test JSON export
    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apcre_dataset_test")
    export_path = os.path.join(export_dir, "apcre_dataset_v2.json")
    written = builder.export_json(export_path)
    _safe_print(f"\n[5] Exported dataset to: {written}")

    # Verify the JSON file is valid
    with open(written, "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    _safe_print(f"    Verified: loaded {len(loaded)} samples from JSON file.")

    # Clean up test export
    try:
        os.remove(written)
        os.rmdir(export_dir)
        _safe_print(f"    Cleanup: removed test export directory.")
    except Exception:
        pass

    _safe_print(f"\n{'=' * 70}")
    _safe_print(f"  Self-test complete. All checks passed.")
    _safe_print(f"{'=' * 70}")
