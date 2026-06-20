# -*- coding: utf-8 -*-
"""
APCRE Services - Architecture Recommendation Engine (ARE)
Phase 10: Analyzes repository structure, detects current architecture patterns
(monolithic, MVC-like, layered, microservices-like, etc.), recommends optimal
target architectures, and generates actionable migration plans with estimated
improvement benefits.

Works 100% offline using only Python standard library modules (ast, os, re).
No external API calls or third-party dependencies required.
"""

import os
import re
import ast
import math
import json
from collections import defaultdict


class ArchitectureRecommendationEngine:
    """
    Intelligent architecture analysis engine that performs deep static analysis
    on multi-language codebases (Python, Java, JavaScript, TypeScript) to detect
    structural patterns and recommend industry-standard architecture migrations.

    Supported detection patterns:
        - Monolithic (single-module, tightly coupled)
        - MVC-like (Model-View-Controller separation)
        - Layered (presentation, business, data tiers)
        - Microservices-like (independent service modules)
        - Event-Driven (message/event bus patterns)

    Supported recommendations:
        - MVC (Model-View-Controller)
        - MVVM (Model-View-ViewModel)
        - Clean Architecture (Uncle Bob)
        - Hexagonal Architecture (Ports & Adapters)
        - Microservices
        - Modular Monolith
    """

    # ------------------------------------------------------------------ #
    #  Directory / file-name heuristic markers for pattern detection
    # ------------------------------------------------------------------ #
    LAYER_MARKERS = {
        "model":        ["model", "models", "entity", "entities", "domain", "schema", "schemas"],
        "view":         ["view", "views", "template", "templates", "page", "pages", "ui", "frontend", "component", "components"],
        "controller":   ["controller", "controllers", "handler", "handlers", "endpoint", "endpoints", "api", "routes", "router", "routers"],
        "service":      ["service", "services", "usecase", "usecases", "use_case", "use_cases", "business", "logic"],
        "repository":   ["repository", "repositories", "repo", "repos", "dao", "data", "database", "db", "persistence", "storage"],
        "middleware":   ["middleware", "middlewares", "interceptor", "interceptors", "filter", "filters"],
        "config":       ["config", "configs", "configuration", "settings", "env"],
        "test":         ["test", "tests", "spec", "specs", "__tests__", "testing"],
        "util":         ["util", "utils", "utility", "utilities", "helper", "helpers", "common", "shared", "lib"],
        "infra":        ["infra", "infrastructure", "adapter", "adapters", "port", "ports", "gateway", "gateways"],
        "event":        ["event", "events", "message", "messages", "queue", "queues", "subscriber", "publisher", "listener"],
    }

    # Import patterns that hint at framework / architecture style
    FRAMEWORK_HINTS = {
        "django":   r"\bfrom\s+django\b|\bimport\s+django\b",
        "flask":    r"\bfrom\s+flask\b|\bimport\s+flask\b",
        "fastapi":  r"\bfrom\s+fastapi\b|\bimport\s+fastapi\b",
        "express":  r"\brequire\s*\(\s*['\"]express['\"]\s*\)|from\s+['\"]express['\"]",
        "spring":   r"\bimport\s+org\.springframework\b|@RestController|@Service|@Repository",
        "react":    r"\bfrom\s+['\"]react['\"]|import\s+React\b",
        "angular":  r"\bfrom\s+['\"]@angular\b|@Component|@NgModule",
        "vue":      r"\bfrom\s+['\"]vue['\"]|createApp|defineComponent",
    }

    SUPPORTED_EXTENSIONS = {".py", ".java", ".js", ".ts", ".jsx", ".tsx"}

    SKIP_DIRS = {
        ".venv", "venv", "node_modules", "__pycache__", ".git", ".hg",
        "dist", "build", ".tox", ".mypy_cache", ".pytest_cache",
        "egg-info", ".eggs", "site-packages", "migrations",
    }

    def __init__(self):
        """Initialize the Architecture Recommendation Engine with zero external dependencies."""
        self.reset()

    def reset(self):
        """Clear all internal analysis state for a fresh run."""
        self.files = []                       # list of (rel_path, abs_path, extension)
        self.file_count = 0
        self.total_lines = 0
        self.total_classes = 0
        self.total_functions = 0
        self.total_imports = 0
        self.module_count = 0                 # distinct directories containing source files
        self.class_distribution = defaultdict(int)   # directory -> class count
        self.function_distribution = defaultdict(int)
        self.import_graph = defaultdict(set)          # file -> set of imported module names
        self.layer_hits = defaultdict(int)             # layer_name -> directory match count
        self.framework_hits = defaultdict(int)         # framework -> file match count
        self.per_file_metrics = {}                     # rel_path -> {classes, functions, imports, lines}

    # ================================================================== #
    #  PUBLIC API
    # ================================================================== #

    def analyze(self, repo_path: str) -> dict:
        """
        Main entry point.  Recursively scans *repo_path* for Python, Java,
        JavaScript, and TypeScript source files and returns a comprehensive
        architecture analysis dictionary.

        Parameters
        ----------
        repo_path : str
            Absolute or relative path to the repository root directory.

        Returns
        -------
        dict
            Keys:
                current_architecture   – detected pattern label (str)
                recommended_architecture – recommended target (str)
                migration_plan         – ordered list of migration steps
                expected_benefits      – dict with improvement estimates
                analysis_summary       – dict with raw scan metrics
        """
        self.reset()
        repo_path = os.path.abspath(repo_path)

        if not os.path.isdir(repo_path):
            return self._error_result(f"Path does not exist or is not a directory: {repo_path}")

        # ----------------------------------------------------------
        # Phase 1 – Recursive file discovery
        # ----------------------------------------------------------
        self._discover_files(repo_path)

        if self.file_count == 0:
            return self._error_result("No supported source files found in the repository.")

        # ----------------------------------------------------------
        # Phase 2 – Parse every discovered file
        # ----------------------------------------------------------
        for rel_path, abs_path, ext in self.files:
            self._parse_file(rel_path, abs_path, ext, repo_path)

        # ----------------------------------------------------------
        # Phase 3 – Detect current architecture pattern
        # ----------------------------------------------------------
        current_arch = self._detect_current_architecture()

        # ----------------------------------------------------------
        # Phase 4 – Recommend target architecture
        # ----------------------------------------------------------
        recommended_arch = self._recommend_architecture(current_arch)

        # ----------------------------------------------------------
        # Phase 5 – Generate migration plan
        # ----------------------------------------------------------
        migration_plan = self._generate_migration_plan(current_arch, recommended_arch)

        # ----------------------------------------------------------
        # Phase 6 – Estimate expected benefits
        # ----------------------------------------------------------
        expected_benefits = self._estimate_benefits(current_arch, recommended_arch)

        # ----------------------------------------------------------
        # Phase 7 – Compile analysis summary
        # ----------------------------------------------------------
        analysis_summary = {
            "files_count": self.file_count,
            "total_lines": self.total_lines,
            "classes_count": self.total_classes,
            "functions_count": self.total_functions,
            "imports_count": self.total_imports,
            "modules_count": self.module_count,
            "layer_distribution": dict(self.layer_hits),
            "framework_hints": {k: v for k, v in self.framework_hits.items() if v > 0},
            "class_distribution_by_module": dict(self.class_distribution),
            "function_distribution_by_module": dict(self.function_distribution),
        }

        return {
            "success": True,
            "current_architecture": current_arch,
            "recommended_architecture": recommended_arch,
            "migration_plan": migration_plan,
            "expected_benefits": expected_benefits,
            "analysis_summary": analysis_summary,
        }

    # ================================================================== #
    #  PHASE 1 – FILE DISCOVERY
    # ================================================================== #

    def _discover_files(self, repo_path: str):
        """Walk the repo tree and collect all supported source files."""
        source_dirs = set()

        for root, dirs, filenames in os.walk(repo_path):
            # Prune skip directories in-place for efficiency
            dirs[:] = [d for d in dirs if d.lower() not in self.SKIP_DIRS
                       and not d.endswith(".egg-info")]

            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    abs_path = os.path.join(root, fname)
                    rel_path = os.path.relpath(abs_path, repo_path)
                    self.files.append((rel_path, abs_path, ext))
                    source_dirs.add(os.path.relpath(root, repo_path))

        self.file_count = len(self.files)
        self.module_count = len(source_dirs) if source_dirs else 0

    # ================================================================== #
    #  PHASE 2 – FILE PARSING
    # ================================================================== #

    def _parse_file(self, rel_path: str, abs_path: str, ext: str, repo_root: str):
        """Parse a single source file and extract structural metrics."""
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        except Exception:
            return

        lines = content.splitlines()
        line_count = len(lines)
        self.total_lines += line_count

        # Determine containing module directory
        parent_dir = os.path.relpath(os.path.dirname(abs_path), repo_root)
        if parent_dir == ".":
            parent_dir = "<root>"

        # Detect layer markers from directory path components
        path_parts = set()
        for part in rel_path.replace("\\", "/").lower().split("/"):
            path_parts.add(os.path.splitext(part)[0])

        for layer_name, markers in self.LAYER_MARKERS.items():
            for marker in markers:
                if marker in path_parts:
                    self.layer_hits[layer_name] += 1
                    break

        # Detect framework hints from file content
        for fw_name, pattern in self.FRAMEWORK_HINTS.items():
            if re.search(pattern, content, re.IGNORECASE):
                self.framework_hits[fw_name] += 1

        # Language-specific parsing
        if ext == ".py":
            classes, functions, imports = self._parse_python_ast(content)
        else:
            classes, functions, imports = self._parse_generic_regex(content, ext)

        self.total_classes += classes
        self.total_functions += functions
        self.total_imports += imports
        self.class_distribution[parent_dir] += classes
        self.function_distribution[parent_dir] += functions

        # Track per-file metrics
        self.per_file_metrics[rel_path] = {
            "classes": classes,
            "functions": functions,
            "imports": imports,
            "lines": line_count,
        }

    def _parse_python_ast(self, source: str):
        """Use Python's ast module for accurate Python source parsing."""
        classes = 0
        functions = 0
        imports = 0

        try:
            tree = ast.parse(source, mode="exec")
        except SyntaxError:
            # Fallback to regex for files with syntax errors
            return self._parse_generic_regex(source, ".py")

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes += 1
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                functions += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports += 1
                # Record import names for dependency analysis
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.import_graph[source[:40]].add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.import_graph[source[:40]].add(node.module.split(".")[0])

        return classes, functions, imports

    def _parse_generic_regex(self, content: str, ext: str):
        """Regex-based structural parsing for Java, JavaScript, and TypeScript."""
        classes = 0
        functions = 0
        imports = 0

        if ext in (".java",):
            classes = len(re.findall(r"\b(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+\w+", content))
            functions = len(re.findall(r"\b(?:public|private|protected|static)\s+[\w<>\[\]]+\s+\w+\s*\(", content))
            imports = len(re.findall(r"^\s*import\s+", content, re.MULTILINE))

        elif ext in (".js", ".jsx", ".ts", ".tsx"):
            # ES6 classes
            classes = len(re.findall(r"\bclass\s+\w+", content))
            # Function declarations, arrow functions, and method definitions
            func_decl = len(re.findall(r"\bfunction\s+\w+\s*\(", content))
            arrow_fn = len(re.findall(r"\b(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?\(", content))
            method_fn = len(re.findall(r"^\s+\w+\s*\([^)]*\)\s*\{", content, re.MULTILINE))
            functions = func_decl + arrow_fn + method_fn
            # ES6 imports + require()
            imports = len(re.findall(r"^\s*import\s+", content, re.MULTILINE))
            imports += len(re.findall(r"\brequire\s*\(", content))

        return classes, functions, imports

    # ================================================================== #
    #  PHASE 3 – ARCHITECTURE DETECTION
    # ================================================================== #

    def _detect_current_architecture(self) -> str:
        """
        Infer the dominant architecture pattern from structural signals.

        Detection heuristics:
          1. MVC-like:  model + view + controller layers all present
          2. Layered:   model/service/repository layers with no strong view/controller split
          3. Microservices-like: many modules with independent service directories
          4. Event-Driven: strong event/message layer signals
          5. Monolithic: default fallback when no clear layering detected
        """
        m = self.layer_hits.get("model", 0)
        v = self.layer_hits.get("view", 0)
        c = self.layer_hits.get("controller", 0)
        s = self.layer_hits.get("service", 0)
        r = self.layer_hits.get("repository", 0)
        e = self.layer_hits.get("event", 0)
        infra = self.layer_hits.get("infra", 0)

        # Compute an architectural signal strength score for each candidate
        scores = {}

        # MVC: needs all three pillars
        if m > 0 and v > 0 and c > 0:
            scores["MVC-like"] = m + v + c + (s * 0.5)

        # Layered: service + repository tiers without strong view/controller split
        if s > 0 and r > 0:
            scores["Layered"] = s + r + (m * 0.5) + (infra * 0.3)

        # Microservices-like: many independent modules with service dirs
        if self.module_count >= 8 and s >= 3:
            scores["Microservices-like"] = self.module_count * 0.3 + s * 2

        # Event-Driven: strong event/messaging signals
        if e >= 2:
            scores["Event-Driven"] = e * 3 + (s * 0.5)

        # Hexagonal hints: infra + ports/adapters directories
        if infra >= 2 and (s > 0 or r > 0):
            scores["Hexagonal-like"] = infra * 2 + s + r

        if not scores:
            return "Monolithic"

        # Return the highest-scoring pattern
        best = max(scores, key=scores.get)
        return best

    # ================================================================== #
    #  PHASE 4 – ARCHITECTURE RECOMMENDATION
    # ================================================================== #

    def _recommend_architecture(self, current: str) -> str:
        """
        Based on detected pattern plus quantitative metrics, recommend the
        optimal target architecture from the supported set.
        """
        files = self.file_count
        classes = self.total_classes
        functions = self.total_functions
        modules = self.module_count
        lines = self.total_lines
        has_service = self.layer_hits.get("service", 0) > 0
        has_infra = self.layer_hits.get("infra", 0) > 0

        # ---- Very large codebase → Microservices or Modular Monolith ----
        if files > 200 or lines > 50000:
            if modules >= 10 and has_service:
                return "Microservices"
            return "Modular Monolith"

        # ---- Large codebase → Clean Architecture or Hexagonal ----
        if files > 80 or lines > 20000:
            if has_infra:
                return "Hexagonal Architecture"
            return "Clean Architecture"

        # ---- Medium codebase ----
        if files > 30 or lines > 8000:
            if current == "MVC-like":
                # Already MVC-shaped – suggest Clean Architecture as evolution
                return "Clean Architecture"
            if current == "Layered":
                return "Hexagonal Architecture"
            # Generic medium repo – MVVM if it has view/model, else MVC
            if self.layer_hits.get("view", 0) > 0 and self.layer_hits.get("model", 0) > 0:
                return "MVVM"
            return "MVC"

        # ---- Small codebase ----
        if current == "Monolithic":
            if classes > 10:
                return "MVC"
            return "Modular Monolith"

        # ---- Fallback: If already structured, suggest next-level ----
        upgrade_map = {
            "MVC-like":           "Clean Architecture",
            "Layered":            "Hexagonal Architecture",
            "Microservices-like": "Microservices",
            "Event-Driven":       "Microservices",
            "Hexagonal-like":     "Clean Architecture",
            "Monolithic":         "MVC",
        }
        return upgrade_map.get(current, "MVC")

    # ================================================================== #
    #  PHASE 5 – MIGRATION PLAN GENERATION
    # ================================================================== #

    def _generate_migration_plan(self, current: str, target: str) -> list:
        """
        Build an ordered, actionable migration plan from *current* to *target*.
        Each step is a descriptive string suitable for project tracking.
        """
        steps = []

        # Universal preamble steps
        steps.append(f"Step 1: Audit existing '{current}' architecture – catalog all {self.file_count} source files across {self.module_count} modules.")
        steps.append(f"Step 2: Establish comprehensive test coverage (unit + integration) before refactoring to prevent regressions.")
        steps.append(f"Step 3: Identify and document all {self.total_imports} cross-module dependencies for safe decoupling.")

        # Target-specific migration instructions
        if target == "MVC":
            steps.extend([
                "Step 4: Create 'models/' directory – migrate all data classes, entities, and schema definitions.",
                "Step 5: Create 'views/' directory – extract all presentation logic, templates, and UI components.",
                "Step 6: Create 'controllers/' directory – relocate all request handlers, routers, and API endpoints.",
                "Step 7: Introduce a service layer between controllers and models for business logic isolation.",
                "Step 8: Refactor direct model access in views to go through controllers.",
                "Step 9: Validate MVC boundaries with architectural fitness functions (import rule checks).",
            ])

        elif target == "MVVM":
            steps.extend([
                "Step 4: Create 'models/' directory – isolate domain entities and data access objects.",
                "Step 5: Create 'viewmodels/' directory – implement ViewModel classes that expose observable state for each view.",
                "Step 6: Create 'views/' directory – ensure views bind exclusively to ViewModel properties (no direct model access).",
                "Step 7: Implement data-binding or reactive state management between Views and ViewModels.",
                "Step 8: Extract business rules from views into ViewModel or dedicated service classes.",
                "Step 9: Add ViewModel unit tests verifying state transformations without UI dependencies.",
            ])

        elif target == "Clean Architecture":
            steps.extend([
                "Step 4: Define 'domain/entities/' – move all core business entities and value objects (zero external dependencies).",
                "Step 5: Define 'domain/use_cases/' – extract all business rules into UseCase interactor classes.",
                "Step 6: Define 'interfaces/' (or 'ports/') – create abstract repository and gateway interfaces.",
                "Step 7: Define 'infrastructure/' – implement concrete adapters for databases, APIs, and external services.",
                "Step 8: Define 'presentation/' – wire controllers/views to invoke UseCases via dependency injection.",
                "Step 9: Enforce the Dependency Rule: inner layers must never import from outer layers.",
                "Step 10: Add architectural lint rules or fitness functions to CI/CD pipeline to prevent boundary violations.",
            ])

        elif target == "Hexagonal Architecture":
            steps.extend([
                "Step 4: Define 'domain/' – isolate all core business logic and entities with zero framework dependencies.",
                "Step 5: Define 'ports/inbound/' – create driving port interfaces (e.g., service APIs, command handlers).",
                "Step 6: Define 'ports/outbound/' – create driven port interfaces (e.g., repository, messaging, external API contracts).",
                "Step 7: Define 'adapters/inbound/' – implement HTTP controllers, CLI handlers, and message consumers.",
                "Step 8: Define 'adapters/outbound/' – implement database repositories, API clients, and message publishers.",
                "Step 9: Wire adapters to ports using dependency injection; domain must depend only on port interfaces.",
                "Step 10: Validate hexagonal boundaries: no adapter-to-adapter imports, no domain-to-adapter imports.",
            ])

        elif target == "Microservices":
            steps.extend([
                "Step 4: Identify bounded contexts – group related classes and functions into candidate service boundaries.",
                f"Step 5: Decompose the {self.module_count} existing modules into independently deployable service packages.",
                "Step 6: Define API contracts (REST/gRPC) between services; eliminate shared mutable state.",
                "Step 7: Implement service discovery and inter-service communication (HTTP or message queue).",
                "Step 8: Set up independent databases per service (Database-per-Service pattern).",
                "Step 9: Add health checks, circuit breakers, and observability (logging, tracing) to each service.",
                "Step 10: Containerize services (Docker) and define orchestration (docker-compose / Kubernetes manifests).",
                "Step 11: Implement CI/CD pipelines for independent service deployment.",
            ])

        elif target == "Modular Monolith":
            steps.extend([
                "Step 4: Define clear module boundaries – group related source files into self-contained packages.",
                "Step 5: Enforce module encapsulation – each module exposes a public API; internals remain private.",
                "Step 6: Introduce an internal dependency rule: modules may only depend on each other's public APIs.",
                "Step 7: Extract shared utilities into a 'common/' or 'shared/' module.",
                "Step 8: Add module-level integration tests validating inter-module contracts.",
                "Step 9: Prepare for future microservice extraction by minimizing cross-module database access.",
            ])

        else:
            steps.append(f"Step 4: Research and plan migration path from '{current}' to '{target}'.")

        # Universal closing steps
        steps.append(f"Step {len(steps) + 1}: Perform end-to-end regression testing after migration.")
        steps.append(f"Step {len(steps) + 1}: Update project documentation, architecture decision records (ADRs), and README.")

        return steps

    # ================================================================== #
    #  PHASE 6 – BENEFIT ESTIMATION
    # ================================================================== #

    def _estimate_benefits(self, current: str, target: str) -> dict:
        """
        Estimate expected improvement percentages for key software quality
        attributes after migrating from *current* to *target* architecture.

        Estimates are based on industry heuristics and the size/complexity
        of the analyzed codebase.
        """
        # Base improvement matrix (current -> target -> quality attribute delta)
        improvement_matrix = {
            ("Monolithic", "MVC"):                      {"maintainability": 35, "testability": 30, "scalability": 15, "team_velocity": 25},
            ("Monolithic", "MVVM"):                     {"maintainability": 38, "testability": 35, "scalability": 15, "team_velocity": 28},
            ("Monolithic", "Clean Architecture"):       {"maintainability": 50, "testability": 45, "scalability": 25, "team_velocity": 35},
            ("Monolithic", "Hexagonal Architecture"):   {"maintainability": 48, "testability": 50, "scalability": 28, "team_velocity": 32},
            ("Monolithic", "Microservices"):             {"maintainability": 40, "testability": 35, "scalability": 55, "team_velocity": 30},
            ("Monolithic", "Modular Monolith"):          {"maintainability": 40, "testability": 35, "scalability": 20, "team_velocity": 30},
            ("MVC-like", "Clean Architecture"):          {"maintainability": 30, "testability": 35, "scalability": 20, "team_velocity": 20},
            ("MVC-like", "MVVM"):                        {"maintainability": 15, "testability": 20, "scalability": 10, "team_velocity": 12},
            ("MVC-like", "Hexagonal Architecture"):      {"maintainability": 28, "testability": 35, "scalability": 22, "team_velocity": 18},
            ("MVC-like", "Microservices"):                {"maintainability": 20, "testability": 20, "scalability": 45, "team_velocity": 15},
            ("Layered", "Clean Architecture"):            {"maintainability": 25, "testability": 30, "scalability": 18, "team_velocity": 20},
            ("Layered", "Hexagonal Architecture"):        {"maintainability": 30, "testability": 35, "scalability": 22, "team_velocity": 22},
            ("Layered", "Microservices"):                 {"maintainability": 18, "testability": 18, "scalability": 40, "team_velocity": 15},
            ("Microservices-like", "Microservices"):      {"maintainability": 15, "testability": 15, "scalability": 20, "team_velocity": 18},
            ("Event-Driven", "Microservices"):            {"maintainability": 20, "testability": 20, "scalability": 30, "team_velocity": 15},
            ("Hexagonal-like", "Clean Architecture"):     {"maintainability": 18, "testability": 20, "scalability": 12, "team_velocity": 15},
        }

        base = improvement_matrix.get((current, target))

        if base is None:
            # Fallback generic estimates
            base = {"maintainability": 25, "testability": 20, "scalability": 15, "team_velocity": 18}

        # Scale adjustments based on codebase complexity
        complexity_factor = 1.0
        if self.total_lines > 30000:
            complexity_factor = 1.15  # larger codebases benefit more
        elif self.total_lines > 10000:
            complexity_factor = 1.08
        elif self.total_lines < 1000:
            complexity_factor = 0.85  # small projects benefit less

        benefits = {}
        for key, value in base.items():
            adjusted = min(70, int(value * complexity_factor))
            benefits[f"{key}_improvement_percent"] = adjusted

        # Compute overall improvement as weighted average
        weights = {"maintainability": 0.35, "testability": 0.25, "scalability": 0.25, "team_velocity": 0.15}
        overall = 0
        for key, w in weights.items():
            overall += benefits.get(f"{key}_improvement_percent", 0) * w
        benefits["overall_improvement_percent"] = round(overall, 1)

        # Add migration effort estimate
        if self.file_count > 150:
            benefits["estimated_migration_effort"] = "High (8-16 weeks for a team of 3-5)"
        elif self.file_count > 50:
            benefits["estimated_migration_effort"] = "Medium (4-8 weeks for a team of 2-4)"
        elif self.file_count > 15:
            benefits["estimated_migration_effort"] = "Low-Medium (2-4 weeks for a team of 1-3)"
        else:
            benefits["estimated_migration_effort"] = "Low (1-2 weeks for 1-2 developers)"

        return benefits

    # ================================================================== #
    #  UTILITIES
    # ================================================================== #

    def _error_result(self, message: str) -> dict:
        """Return a standardized error response dict."""
        return {
            "success": False,
            "current_architecture": "Unknown",
            "recommended_architecture": "N/A",
            "migration_plan": [],
            "expected_benefits": {},
            "analysis_summary": {
                "files_count": 0,
                "total_lines": 0,
                "classes_count": 0,
                "functions_count": 0,
                "imports_count": 0,
                "modules_count": 0,
                "layer_distribution": {},
                "framework_hints": {},
                "class_distribution_by_module": {},
                "function_distribution_by_module": {},
            },
            "error": message,
        }


# ====================================================================== #
#  SELF-TEST HARNESS
# ====================================================================== #

def safe_print(text):
    """Windows CP1252-safe printing with Unicode fallback."""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(text.encode("ascii", errors="replace").decode("ascii"))


if __name__ == "__main__":
    engine = ArchitectureRecommendationEngine()

    # Determine a sensible test path – scan this engine's own directory
    test_path = os.path.dirname(os.path.abspath(__file__))
    safe_print(f"{'=' * 72}")
    safe_print(f"  APCRE Architecture Recommendation Engine - Self-Test")
    safe_print(f"{'=' * 72}")
    safe_print(f"  Scanning: {test_path}")
    safe_print(f"{'=' * 72}\n")

    result = engine.analyze(test_path)

    if result.get("success"):
        summary = result["analysis_summary"]
        safe_print(f"  [SCAN RESULTS]")
        safe_print(f"    Files Analyzed      : {summary['files_count']}")
        safe_print(f"    Total Lines of Code : {summary['total_lines']}")
        safe_print(f"    Classes Found       : {summary['classes_count']}")
        safe_print(f"    Functions Found     : {summary['functions_count']}")
        safe_print(f"    Imports Found       : {summary['imports_count']}")
        safe_print(f"    Modules (Dirs)      : {summary['modules_count']}")
        safe_print(f"")
        safe_print(f"  [LAYER DISTRIBUTION]")
        for layer, count in sorted(summary["layer_distribution"].items(), key=lambda x: -x[1]):
            safe_print(f"    {layer:<20s} : {count} hits")
        safe_print(f"")

        if summary["framework_hints"]:
            safe_print(f"  [FRAMEWORK HINTS]")
            for fw, count in summary["framework_hints"].items():
                safe_print(f"    {fw:<20s} : detected in {count} files")
            safe_print(f"")

        safe_print(f"  [ARCHITECTURE ANALYSIS]")
        safe_print(f"    Current Architecture    : {result['current_architecture']}")
        safe_print(f"    Recommended Architecture: {result['recommended_architecture']}")
        safe_print(f"")

        safe_print(f"  [MIGRATION PLAN]")
        for step in result["migration_plan"]:
            safe_print(f"    {step}")
        safe_print(f"")

        safe_print(f"  [EXPECTED BENEFITS]")
        for key, val in result["expected_benefits"].items():
            if isinstance(val, (int, float)):
                safe_print(f"    {key:<40s} : {val}%")
            else:
                safe_print(f"    {key:<40s} : {val}")
    else:
        safe_print(f"  [ERROR] {result.get('error', 'Unknown error')}")

    safe_print(f"\n{'=' * 72}")
    safe_print(f"  Self-test complete.")
    safe_print(f"{'=' * 72}")
