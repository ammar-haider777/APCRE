# -*- coding: utf-8 -*-
"""
APCRE Services - Research Assistant Mode (Phase 11)
Generates structured academic research content for the AI-Powered Code Review
Engine project. Supports literature reviews, gap analysis, novelty formulation,
future work directions, research questions, experimental design, benchmarking
methodology, and IEEE/ACM conference paper outlines.

All content is pre-written template text; zero external API calls are made.
"""

import os
import sys
import datetime


def safe_print(text):
    """Windows CP1252-safe print wrapper."""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(str(text).encode("utf-8", errors="replace").decode("utf-8"))


class ResearchAssistant:
    """
    Offline research assistant that generates structured academic content
    for the APCRE (AI-Powered Code Review Engine) project. Every research
    type returns a dict with title, content, sections, and citation stubs
    so downstream modules can render or export the material directly.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(self):
        self._timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._research_types = [
            "literature_review",
            "research_gaps",
            "novelty_statement",
            "future_work",
            "research_questions",
            "experimental_design",
            "benchmark_plan",
            "conference_outline",
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate(self, topic: str, research_type: str = "literature_review") -> dict:
        """
        Generate structured research content.

        Parameters
        ----------
        topic : str
            The research topic or title string.
        research_type : str
            One of: literature_review, research_gaps, novelty_statement,
            future_work, research_questions, experimental_design,
            benchmark_plan, conference_outline.

        Returns
        -------
        dict
            Keys: title, content, sections, citations_placeholder
        """
        rt = research_type.lower().strip()
        dispatch = {
            "literature_review":    self._literature_review,
            "research_gaps":        self._research_gaps,
            "novelty_statement":    self._novelty_statement,
            "future_work":          self._future_work,
            "research_questions":   self._research_questions,
            "experimental_design":  self._experimental_design,
            "benchmark_plan":       self._benchmark_plan,
            "conference_outline":   self._conference_outline,
        }

        handler = dispatch.get(rt)
        if handler is None:
            return {
                "title": f"Unknown Research Type: {research_type}",
                "content": (
                    f"The research type '{research_type}' is not supported. "
                    f"Available types: {', '.join(self._research_types)}"
                ),
                "sections": [],
                "citations_placeholder": [],
            }

        return handler(topic)

    # ------------------------------------------------------------------
    # 1. Literature Review
    # ------------------------------------------------------------------
    def _literature_review(self, topic: str) -> dict:
        title = f"Literature Review: {topic}"
        sections = [
            {
                "heading": "1. Abstract Syntax Tree (AST) Based Code Analyzers",
                "body": (
                    "AST-based static analysis has been the bedrock of automated code quality "
                    "assessment since the early linting tools of the 1970s. Modern AST analyzers "
                    "such as Pylint, Flake8, and ESLint parse source code into tree representations "
                    "that capture syntactic and structural relationships. Recent extensions including "
                    "Tree-sitter provide incremental, language-agnostic parsing that enables real-time "
                    "code analysis inside editors and CI pipelines. However, AST-only approaches are "
                    "inherently limited to surface-level structural patterns and cannot capture deeper "
                    "semantic intent such as algorithmic complexity or design-pattern adherence."
                ),
            },
            {
                "heading": "2. Machine Learning for Code Quality Assessment",
                "body": (
                    "The application of machine learning to source code has accelerated rapidly with "
                    "the emergence of large language models (LLMs). CodeBERT, GraphCodeBERT, and "
                    "UniXcoder introduced transformer-based pre-training objectives that jointly model "
                    "natural language and programming languages. Subsequent work such as CodeT5+ and "
                    "StarCoder demonstrated that scaling data and model size yields impressive "
                    "zero-shot code generation and review capabilities. Parallel research on "
                    "graph neural networks (GNNs) applied to program dependence graphs has shown "
                    "promise for vulnerability detection and clone identification. Despite these "
                    "advances, most ML-based code review systems require cloud-hosted inference "
                    "endpoints, introducing latency, cost, and privacy concerns for enterprise users."
                ),
            },
            {
                "heading": "3. Static Analysis Tools and IDE Integrations",
                "body": (
                    "Commercial and open-source static analysis platforms—SonarQube, CodeClimate, "
                    "Codacy, DeepSource—have converged on a SaaS delivery model that scans "
                    "repositories via CI webhooks. These tools combine rule-based checkers with "
                    "limited ML heuristics for code smell and bug detection. IDE-side integrations "
                    "(VS Code extensions, JetBrains inspections) provide immediate developer "
                    "feedback but rely on simplified rule subsets. A notable gap exists between the "
                    "expressiveness of cloud-hosted analysis pipelines and the constrained offline "
                    "analysis available to individual developers."
                ),
            },
            {
                "heading": "4. Semantic Code Understanding",
                "body": (
                    "Semantic understanding goes beyond syntax to interpret programmer intent, "
                    "algorithmic behavior, and architectural patterns. Techniques include control-flow "
                    "and data-flow analysis, symbolic execution, abstract interpretation, and neural "
                    "program embeddings. Recent work on code summarization (e.g., CodeSearchNet, "
                    "CoSQA) and program comprehension benchmarks highlights the need for models that "
                    "bridge structural and semantic analysis. APCRE's contribution lies in fusing "
                    "AST-derived structural features with lightweight ML-based semantic embeddings "
                    "entirely on the local machine, enabling privacy-preserving deep code review."
                ),
            },
            {
                "heading": "5. Privacy and Offline Code Analysis",
                "body": (
                    "Privacy-sensitive industries (finance, healthcare, defense) increasingly demand "
                    "code analysis that never transmits source code to external servers. Existing "
                    "solutions either sacrifice analytical depth for privacy (local linters) or "
                    "sacrifice privacy for depth (cloud ML services). Federated learning and "
                    "on-device inference with quantized models (ONNX Runtime, TensorFlow Lite) "
                    "represent emerging approaches but remain largely experimental for code review "
                    "workloads. APCRE addresses this gap with a fully offline engine combining "
                    "deterministic rule-based analysis and pre-trained statistical models."
                ),
            },
        ]

        content = "\n\n".join(
            f"{s['heading']}\n{s['body']}" for s in sections
        )

        citations = [
            "[1] Alon, U. et al. 'code2vec: Learning Distributed Representations of Code.' POPL 2019.",
            "[2] Feng, Z. et al. 'CodeBERT: A Pre-Trained Model for Programming and Natural Languages.' EMNLP 2020.",
            "[3] Guo, D. et al. 'GraphCodeBERT: Pre-training Code Representations with Data Flow.' ICLR 2021.",
            "[4] Wang, Y. et al. 'CodeT5+: Open Code Large Language Models for Code Understanding and Generation.' EMNLP 2023.",
            "[5] Li, R. et al. 'StarCoder: May the Source Be With You!' TMLR 2023.",
            "[6] OWASP Foundation. 'OWASP Top Ten 2021.' https://owasp.org/Top10/",
            "[7] Johnson, B. et al. 'Why Don\\'t Software Developers Use Static Analysis Tools to Find Bugs?' ICSE 2013.",
            "[8] Habib, A. & Pradel, M. 'How Many of All Bugs Do We Find? A Study of Static Bug Detectors.' ASE 2018.",
            "[9] Tree-sitter Contributors. 'Tree-sitter: An Incremental Parsing System.' https://tree-sitter.github.io/",
            "[10] SonarSource. 'SonarQube - Continuous Code Quality.' https://www.sonarsource.com/",
        ]

        return {
            "title": title,
            "content": content,
            "sections": [s["heading"] for s in sections],
            "citations_placeholder": citations,
        }

    # ------------------------------------------------------------------
    # 2. Research Gaps
    # ------------------------------------------------------------------
    def _research_gaps(self, topic: str) -> dict:
        title = f"Research Gaps Analysis: {topic}"
        sections = [
            {
                "heading": "Gap 1: Cloud Dependency of ML-Based Code Review",
                "body": (
                    "The overwhelming majority of ML-powered code analysis tools (GitHub Copilot, "
                    "Amazon CodeWhisperer, Tabnine Enterprise) require persistent cloud connectivity "
                    "for inference. This architecture imposes three fundamental constraints: (a) network "
                    "latency that degrades developer workflow, (b) ongoing API costs that scale with "
                    "usage, and (c) mandatory transmission of proprietary source code to third-party "
                    "servers. No existing tool offers the analytical depth of cloud-based ML review "
                    "while operating entirely offline on consumer-grade hardware."
                ),
            },
            {
                "heading": "Gap 2: Latency in Real-Time Code Feedback",
                "body": (
                    "Current cloud-hosted review services introduce round-trip latencies of 500ms to "
                    "5 seconds per analysis request, depending on payload size and server load. For "
                    "interactive developer workflows—keystroke-level feedback, inline suggestions, "
                    "real-time refactoring—this latency is prohibitive. Local linters respond in "
                    "milliseconds but provide only shallow syntactic checks. There is a critical gap "
                    "for sub-100ms semantic analysis that operates without network dependency."
                ),
            },
            {
                "heading": "Gap 3: Source Code Privacy and Compliance",
                "body": (
                    "Regulatory frameworks (GDPR, HIPAA, SOC-2, ITAR) and enterprise security "
                    "policies often prohibit transmitting source code to external cloud endpoints. "
                    "Current tools offer limited self-hosted alternatives (SonarQube Community) "
                    "but these lack ML-driven semantic analysis. The gap between compliance-safe "
                    "tooling and state-of-the-art ML code review remains unaddressed."
                ),
            },
            {
                "heading": "Gap 4: Fragmented Structural and Semantic Analysis",
                "body": (
                    "Existing approaches treat structural analysis (AST parsing, control-flow) and "
                    "semantic analysis (embeddings, LLM-based review) as independent pipelines. "
                    "No current system fuses AST-derived structural features with neural semantic "
                    "embeddings in a single, unified scoring framework that produces coherent "
                    "multi-dimensional code quality assessments."
                ),
            },
            {
                "heading": "Gap 5: Lack of Offline Knowledge Graphs for Code Review",
                "body": (
                    "Knowledge graphs have demonstrated value for software engineering tasks "
                    "(API recommendation, bug localization) but existing implementations rely on "
                    "cloud-hosted graph databases (Neo4j Aura, Amazon Neptune). There is no "
                    "lightweight, file-based knowledge graph solution designed for local code review "
                    "that captures cross-file relationships, design patterns, and historical "
                    "refactoring decisions."
                ),
            },
        ]

        content = "\n\n".join(
            f"{s['heading']}\n{s['body']}" for s in sections
        )

        citations = [
            "[1] Ziegler, A. et al. 'Productivity Assessment of Neural Code Completion.' MAPS 2022.",
            "[2] Vaithilingam, P. et al. 'Expectation vs. Experience: Evaluating the Usability of Code Generation Tools.' CHI 2022.",
            "[3] European Parliament. 'General Data Protection Regulation (GDPR).' Regulation (EU) 2016/679.",
            "[4] Allamanis, M. et al. 'A Survey of Machine Learning for Big Code and Naturalness.' CSUR 2018.",
            "[5] Zhou, Y. et al. 'Devign: Effective Vulnerability Identification by Learning Comprehensive Program Semantics.' NeurIPS 2019.",
        ]

        return {
            "title": title,
            "content": content,
            "sections": [s["heading"] for s in sections],
            "citations_placeholder": citations,
        }

    # ------------------------------------------------------------------
    # 3. Novelty Statement
    # ------------------------------------------------------------------
    def _novelty_statement(self, topic: str) -> dict:
        title = f"Novelty Statement: {topic}"
        sections = [
            {
                "heading": "Core Innovation: Local Semantic-Structural Fusion Engine",
                "body": (
                    "APCRE (AI-Powered Code Review Engine) introduces a novel architecture that "
                    "fuses deterministic AST-based structural analysis with lightweight machine "
                    "learning semantic embeddings in a single, unified offline pipeline. Unlike "
                    "existing tools that treat structure and semantics independently—or that require "
                    "cloud-hosted inference—APCRE operates entirely on the developer's local machine "
                    "with zero external API calls while delivering multi-dimensional code quality "
                    "scores encompassing correctness, style, complexity, security, and design-pattern "
                    "adherence."
                ),
            },
            {
                "heading": "Differentiating Contributions",
                "body": (
                    "1. Semantic-Structural Fusion: APCRE combines Tree-sitter incremental AST "
                    "parsing with TF-IDF and numpy-based feature embeddings to produce a unified "
                    "code quality vector. This fusion captures both surface-level coding standards "
                    "and deeper algorithmic intent without requiring GPU acceleration.\n\n"
                    "2. Fully Offline Architecture: All analysis—static rules, ML inference, knowledge "
                    "graph queries, security scanning—executes locally using only the Python standard "
                    "library and numpy. No telemetry, no cloud dependency, no data exfiltration.\n\n"
                    "3. Integrated Knowledge Graph: An SQLite-backed knowledge graph tracks cross-file "
                    "relationships, design patterns, and refactoring history, enabling context-aware "
                    "review that improves over successive analysis sessions.\n\n"
                    "4. Multi-Agent Planning: A task planner agent decomposes complex review requests "
                    "into executable DAGs with McCabe complexity estimation, enabling structured, "
                    "risk-aware refactoring workflows.\n\n"
                    "5. Security Intelligence Engine: OWASP Top 10 and CWE-mapped vulnerability "
                    "detection with CVSS-based risk scoring integrated directly into the review flow."
                ),
            },
            {
                "heading": "Positioning Relative to Prior Art",
                "body": (
                    "While CodeBERT, GraphCodeBERT, and CodeT5+ have advanced neural code "
                    "understanding, they operate as cloud-hosted models or require GPU-equipped "
                    "infrastructure. SonarQube and DeepSource provide rule-based analysis but lack "
                    "semantic depth. APCRE uniquely occupies the intersection: production-grade "
                    "semantic analysis that is fully self-contained, privacy-preserving, and "
                    "deployable on standard developer hardware."
                ),
            },
        ]

        content = "\n\n".join(
            f"{s['heading']}\n{s['body']}" for s in sections
        )

        citations = [
            "[1] Feng, Z. et al. 'CodeBERT: A Pre-Trained Model for Programming and Natural Languages.' EMNLP 2020.",
            "[2] Wang, Y. et al. 'CodeT5+: Open Code Large Language Models.' EMNLP 2023.",
            "[3] Alon, U. et al. 'code2vec: Learning Distributed Representations of Code.' POPL 2019.",
            "[4] SonarSource. 'SonarQube Documentation.' https://docs.sonarsource.com/",
            "[5] OWASP Foundation. 'OWASP Top Ten 2021.' https://owasp.org/Top10/",
        ]

        return {
            "title": title,
            "content": content,
            "sections": [s["heading"] for s in sections],
            "citations_placeholder": citations,
        }

    # ------------------------------------------------------------------
    # 4. Future Work
    # ------------------------------------------------------------------
    def _future_work(self, topic: str) -> dict:
        title = f"Future Work Directions: {topic}"
        sections = [
            {
                "heading": "Direction 1: On-Device Large Language Model Integration",
                "body": (
                    "Investigate the integration of quantized small language models (SLMs) such as "
                    "Phi-3-mini, Gemma-2B, or TinyLlama for local natural-language code review "
                    "generation. ONNX Runtime and llama.cpp enable CPU-only inference with models "
                    "under 4 GB, potentially allowing APCRE to generate human-readable review "
                    "narratives while preserving the fully offline guarantee."
                ),
            },
            {
                "heading": "Direction 2: Multi-Language AST Unification",
                "body": (
                    "Extend the Tree-sitter parsing layer to support a unified intermediate "
                    "representation (IR) across Python, JavaScript, TypeScript, Java, C++, and Go. "
                    "A language-agnostic IR would allow the ML scoring model to transfer quality "
                    "heuristics across languages without language-specific retraining."
                ),
            },
            {
                "heading": "Direction 3: Incremental Learning from Developer Feedback",
                "body": (
                    "Implement an online learning loop where developers accept or reject individual "
                    "review suggestions. Accepted suggestions reinforce model weights via lightweight "
                    "gradient updates (e.g., LoRA fine-tuning on CPU), while rejected suggestions "
                    "contribute negative examples. Over time, the model personalizes to the team's "
                    "coding standards and preferences."
                ),
            },
            {
                "heading": "Direction 4: Repository-Scale Architecture Analysis",
                "body": (
                    "Evolve the knowledge graph component to perform repository-wide architectural "
                    "analysis: detect circular dependencies, identify god classes, map module "
                    "coupling and cohesion metrics, and generate architecture decision records "
                    "(ADRs) automatically from commit history."
                ),
            },
            {
                "heading": "Direction 5: CI/CD Pipeline Integration",
                "body": (
                    "Develop GitHub Actions, GitLab CI, and Azure DevOps pipeline integrations that "
                    "run APCRE as a self-hosted analysis step. Gate pull requests on composite "
                    "quality scores, security threat levels, and complexity thresholds without "
                    "transmitting code to external services."
                ),
            },
            {
                "heading": "Direction 6: Explainable AI for Code Review Decisions",
                "body": (
                    "Augment the scoring pipeline with SHAP or LIME-based feature attribution to "
                    "explain why specific quality scores were assigned. Provide developers with "
                    "transparent, actionable reasoning behind each suggestion rather than opaque "
                    "numerical scores."
                ),
            },
        ]

        content = "\n\n".join(
            f"{s['heading']}\n{s['body']}" for s in sections
        )

        citations = [
            "[1] Abdin, M. et al. 'Phi-3 Technical Report.' Microsoft Research 2024.",
            "[2] Hu, E.J. et al. 'LoRA: Low-Rank Adaptation of Large Language Models.' ICLR 2022.",
            "[3] Lundberg, S. & Lee, S. 'A Unified Approach to Interpreting Model Predictions.' NeurIPS 2017.",
            "[4] Ribeiro, M.T. et al. 'Why Should I Trust You? Explaining the Predictions of Any Classifier.' KDD 2016.",
            "[5] GitHub. 'GitHub Actions Documentation.' https://docs.github.com/en/actions",
        ]

        return {
            "title": title,
            "content": content,
            "sections": [s["heading"] for s in sections],
            "citations_placeholder": citations,
        }

    # ------------------------------------------------------------------
    # 5. Research Questions
    # ------------------------------------------------------------------
    def _research_questions(self, topic: str) -> dict:
        title = f"Research Questions & Hypotheses: {topic}"
        sections = [
            {
                "heading": "RQ1: Effectiveness of Semantic-Structural Fusion",
                "body": (
                    "Question: Does fusing AST-derived structural features with TF-IDF semantic "
                    "embeddings produce more accurate code quality assessments than either approach "
                    "in isolation?\n\n"
                    "Hypothesis H1: A combined semantic-structural scoring model achieves at least "
                    "15% higher precision and recall on code smell detection benchmarks compared to "
                    "AST-only analysis (Pylint) and embedding-only analysis.\n\n"
                    "Variables: Independent — analysis mode (structural-only, semantic-only, fused). "
                    "Dependent — precision, recall, F1-score on labeled code smell datasets."
                ),
            },
            {
                "heading": "RQ2: Offline Viability on Consumer Hardware",
                "body": (
                    "Question: Can a fully offline code review engine deliver sub-200ms analysis "
                    "latency on standard developer hardware (8 GB RAM, quad-core CPU) without "
                    "requiring GPU acceleration?\n\n"
                    "Hypothesis H2: APCRE achieves median analysis latency under 200ms for files "
                    "up to 1000 LOC on a reference machine with 8 GB RAM and an Intel i5 processor.\n\n"
                    "Variables: Independent — file size (LOC), hardware configuration. "
                    "Dependent — wall-clock analysis latency (ms), memory consumption (MB)."
                ),
            },
            {
                "heading": "RQ3: Privacy Preservation vs. Analytical Depth",
                "body": (
                    "Question: To what extent does enforcing zero-network-dependency analysis "
                    "compromise the depth and accuracy of code review compared to cloud-hosted "
                    "alternatives?\n\n"
                    "Hypothesis H3: APCRE's offline analysis achieves at least 80% of the defect "
                    "detection rate of cloud-hosted tools (SonarCloud, CodeClimate) while "
                    "maintaining complete data privacy.\n\n"
                    "Variables: Independent — tool (APCRE, SonarCloud, CodeClimate). "
                    "Dependent — defect detection rate, false positive rate, privacy compliance."
                ),
            },
            {
                "heading": "RQ4: Knowledge Graph Impact on Cross-File Analysis",
                "body": (
                    "Question: Does an SQLite-backed local knowledge graph improve the accuracy of "
                    "cross-file code review compared to single-file analysis?\n\n"
                    "Hypothesis H4: Enabling the knowledge graph component increases cross-file "
                    "issue detection (e.g., unused imports across modules, circular dependencies) "
                    "by at least 25% over isolated single-file analysis.\n\n"
                    "Variables: Independent — knowledge graph enabled/disabled. "
                    "Dependent — cross-file issue detection rate, analysis time overhead."
                ),
            },
            {
                "heading": "RQ5: Security Scanning Accuracy",
                "body": (
                    "Question: How does APCRE's OWASP/CWE-mapped security scanner compare to "
                    "dedicated SAST tools (Bandit, Semgrep) in vulnerability detection accuracy?\n\n"
                    "Hypothesis H5: APCRE's security engine achieves comparable recall (within 10% "
                    "margin) to Bandit on Python-specific vulnerability benchmarks while providing "
                    "integrated code quality context.\n\n"
                    "Variables: Independent — tool (APCRE SIE, Bandit, Semgrep). "
                    "Dependent — vulnerability recall, precision, CVSS score correlation."
                ),
            },
        ]

        content = "\n\n".join(
            f"{s['heading']}\n{s['body']}" for s in sections
        )

        citations = [
            "[1] Wohlin, C. et al. 'Experimentation in Software Engineering.' Springer 2012.",
            "[2] Basili, V.R. et al. 'The Goal Question Metric Approach.' Encyclopedia of Software Engineering 1994.",
            "[3] Kitchenham, B. & Charters, S. 'Guidelines for Performing Systematic Literature Reviews.' EBSE 2007.",
            "[4] Habib, A. & Pradel, M. 'How Many of All Bugs Do We Find? A Study of Static Bug Detectors.' ASE 2018.",
            "[5] NIST. 'Static Analysis Tool Exposition (SATE).' https://samate.nist.gov/SATE.html",
        ]

        return {
            "title": title,
            "content": content,
            "sections": [s["heading"] for s in sections],
            "citations_placeholder": citations,
        }

    # ------------------------------------------------------------------
    # 6. Experimental Design
    # ------------------------------------------------------------------
    def _experimental_design(self, topic: str) -> dict:
        title = f"Experimental Design: {topic}"
        sections = [
            {
                "heading": "1. Independent Variables",
                "body": (
                    "IV-1: Analysis Mode — Three levels: (a) Structural-only (AST/Tree-sitter), "
                    "(b) Semantic-only (TF-IDF + numpy embeddings), (c) Fused (APCRE full pipeline).\n"
                    "IV-2: File Complexity — Stratified by McCabe cyclomatic complexity: Low (1-5), "
                    "Medium (6-15), High (16+).\n"
                    "IV-3: File Size — Bins of 0-100 LOC, 101-500 LOC, 501-1000 LOC, 1000+ LOC.\n"
                    "IV-4: Language — Python 3.x (primary), with extension benchmarks for JavaScript "
                    "and TypeScript."
                ),
            },
            {
                "heading": "2. Dependent Variables / Metrics",
                "body": (
                    "DV-1: Defect Detection Rate — Proportion of known defects correctly flagged.\n"
                    "DV-2: False Positive Rate — Proportion of clean code incorrectly flagged.\n"
                    "DV-3: Precision, Recall, F1-Score — Standard classification metrics per defect category.\n"
                    "DV-4: Analysis Latency — Wall-clock milliseconds from invocation to result.\n"
                    "DV-5: Memory Consumption — Peak RSS in MB during analysis.\n"
                    "DV-6: Security Score Accuracy — Correlation between APCRE CVSS scores and "
                    "ground-truth vulnerability severity."
                ),
            },
            {
                "heading": "3. Baselines and Controls",
                "body": (
                    "Baseline-1: Pylint 3.x — Industry-standard Python linter (structural analysis).\n"
                    "Baseline-2: SonarQube Community Edition — Self-hosted static analysis.\n"
                    "Baseline-3: Bandit — Python security-focused SAST tool.\n"
                    "Baseline-4: CodeClimate (cloud) — SaaS code quality platform (where policies permit).\n"
                    "Control: All tools evaluated on identical file corpora with identical hardware "
                    "specifications. Three independent runs per measurement to account for variance."
                ),
            },
            {
                "heading": "4. Dataset",
                "body": (
                    "Primary corpus: 500 Python files sourced from curated open-source repositories "
                    "(Django, Flask, scikit-learn, requests) with manually labeled defect annotations.\n"
                    "Secondary corpus: APCRE synthetic dataset (generated by apcre_dataset_builder.py) "
                    "containing 200 files with injected code smells, security vulnerabilities, and "
                    "complexity anti-patterns.\n"
                    "Validation split: 70% training / 15% validation / 15% test (for ML components)."
                ),
            },
            {
                "heading": "5. Statistical Analysis Plan",
                "body": (
                    "Significance testing: Paired Wilcoxon signed-rank test (non-parametric) for "
                    "pairwise tool comparisons on each metric. Bonferroni correction for multiple "
                    "comparisons. Effect size reported via Cliff's delta.\n"
                    "Confidence level: alpha = 0.05.\n"
                    "Reporting: Results presented as box plots with median, IQR, and outlier markers. "
                    "Latency reported as median and 95th percentile."
                ),
            },
        ]

        content = "\n\n".join(
            f"{s['heading']}\n{s['body']}" for s in sections
        )

        citations = [
            "[1] Wohlin, C. et al. 'Experimentation in Software Engineering.' Springer 2012.",
            "[2] Arcuri, A. & Briand, L.C. 'A Practical Guide for Using Statistical Tests.' ICSE 2011.",
            "[3] Cliff, N. 'Ordinal Methods for Behavioral Data Analysis.' Psychology Press 1996.",
            "[4] Django Software Foundation. 'Django Source Repository.' https://github.com/django/django",
            "[5] Pedregosa, F. et al. 'Scikit-learn: Machine Learning in Python.' JMLR 2011.",
        ]

        return {
            "title": title,
            "content": content,
            "sections": [s["heading"] for s in sections],
            "citations_placeholder": citations,
        }

    # ------------------------------------------------------------------
    # 7. Benchmark Plan
    # ------------------------------------------------------------------
    def _benchmark_plan(self, topic: str) -> dict:
        title = f"Benchmarking Methodology: {topic}"
        sections = [
            {
                "heading": "1. Benchmark Objectives",
                "body": (
                    "The benchmarking campaign aims to: (a) quantify APCRE's defect detection "
                    "accuracy relative to established tools, (b) measure runtime performance "
                    "(latency and throughput) on consumer-grade hardware, (c) evaluate memory "
                    "efficiency for large repository scans, and (d) validate security scanning "
                    "coverage against NIST SATE reference datasets."
                ),
            },
            {
                "heading": "2. Hardware and Software Environment",
                "body": (
                    "Reference Machine: Intel Core i5-12400 (6C/12T), 16 GB DDR4, 512 GB NVMe SSD.\n"
                    "Minimum Viable Machine: Intel Core i5-8250U (4C/8T), 8 GB DDR4, 256 GB SSD.\n"
                    "OS: Windows 11 23H2, Ubuntu 22.04 LTS (cross-platform validation).\n"
                    "Runtime: Python 3.10+, numpy (latest stable), SQLite 3.39+.\n"
                    "Isolation: Each tool run in a clean virtual environment; system load < 5% idle."
                ),
            },
            {
                "heading": "3. Benchmark Suites",
                "body": (
                    "Suite A — Code Smell Detection: 300 Python files with labeled smells (long method, "
                    "god class, feature envy, data clumps, dead code). Ground truth from manual "
                    "expert annotation with inter-annotator agreement (Cohen's kappa >= 0.75).\n\n"
                    "Suite B — Security Vulnerability Detection: 150 Python files with injected "
                    "OWASP Top 10 vulnerabilities (SQL injection, command injection, hardcoded "
                    "credentials, insecure deserialization). Ground truth from NIST SATE Juliet "
                    "Test Suite adaptations.\n\n"
                    "Suite C — Performance Stress Test: Files of increasing size (100, 500, 1K, 5K, "
                    "10K LOC) analyzed 100 times each to establish latency distributions.\n\n"
                    "Suite D — Repository-Scale Scan: Full repository analysis of Django (approx. "
                    "250K LOC) measuring end-to-end wall clock time and peak memory."
                ),
            },
            {
                "heading": "4. Metrics and Reporting",
                "body": (
                    "Primary Metrics:\n"
                    "  - Precision, Recall, F1 (per defect category)\n"
                    "  - Median latency (ms) and P95 latency (ms)\n"
                    "  - Peak memory (MB)\n"
                    "  - Throughput (files/second)\n\n"
                    "Secondary Metrics:\n"
                    "  - False discovery rate (FDR)\n"
                    "  - Mean time to first result (TTFR)\n"
                    "  - CVSS score correlation (Spearman's rho) for security findings\n\n"
                    "Visualization: Box plots, latency CDFs, radar charts for multi-dimensional "
                    "quality comparison."
                ),
            },
            {
                "heading": "5. Reproducibility Protocol",
                "body": (
                    "All benchmark scripts, datasets, configuration files, and raw results are "
                    "versioned in the project repository under /benchmarks/. A Makefile (or "
                    "run_benchmarks.py) automates the full benchmark suite. Docker containers "
                    "with pinned dependency versions ensure cross-environment reproducibility. "
                    "Each experiment is repeated 3 times; reported values are medians with IQR."
                ),
            },
        ]

        content = "\n\n".join(
            f"{s['heading']}\n{s['body']}" for s in sections
        )

        citations = [
            "[1] NIST. 'Static Analysis Tool Exposition (SATE VI).' https://samate.nist.gov/SATE6.html",
            "[2] Okutan, A. & Yildiz, O.T. 'Software Defect Prediction Using Bayesian Networks.' ESE 2014.",
            "[3] Lacchia, M. 'wemake-python-styleguide: The Strictest Python Linter.' https://github.com/wemake-services/wemake-python-styleguide",
            "[4] Cohen, J. 'A Coefficient of Agreement for Nominal Scales.' EPM 1960.",
            "[5] Blackburn, S.M. et al. 'The DaCapo Benchmarks.' OOPSLA 2006.",
        ]

        return {
            "title": title,
            "content": content,
            "sections": [s["heading"] for s in sections],
            "citations_placeholder": citations,
        }

    # ------------------------------------------------------------------
    # 8. Conference Outline
    # ------------------------------------------------------------------
    def _conference_outline(self, topic: str) -> dict:
        title = f"IEEE/ACM Conference Paper Outline: {topic}"
        sections = [
            {
                "heading": "I. Title and Abstract",
                "body": (
                    "Proposed Title: 'APCRE: A Privacy-Preserving AI Engine for Offline "
                    "Semantic-Structural Code Review'\n\n"
                    "Abstract (150-250 words): Present the problem of cloud-dependent code review "
                    "tools and privacy concerns. Introduce APCRE as a novel fully offline engine "
                    "that fuses AST-based structural analysis with lightweight ML semantic embeddings. "
                    "Summarize key results: defect detection accuracy comparable to cloud tools, "
                    "sub-200ms latency on consumer hardware, and zero data exfiltration. State "
                    "contributions and availability."
                ),
            },
            {
                "heading": "II. Introduction",
                "body": (
                    "Motivate the research problem: increasing reliance on cloud-hosted AI code "
                    "review vs. growing privacy requirements. State the research questions (RQ1-RQ5). "
                    "Outline contributions: (1) semantic-structural fusion architecture, (2) fully "
                    "offline implementation, (3) integrated security scanning, (4) local knowledge "
                    "graph, (5) comprehensive empirical evaluation."
                ),
            },
            {
                "heading": "III. Related Work",
                "body": (
                    "Cover three pillars: (A) AST-based static analysis tools and their limitations, "
                    "(B) ML-based code understanding models (CodeBERT, code2vec, StarCoder) and their "
                    "cloud dependency, (C) privacy-preserving software engineering tools. Position "
                    "APCRE relative to each pillar."
                ),
            },
            {
                "heading": "IV. System Architecture",
                "body": (
                    "Describe the APCRE pipeline: Tree-sitter parsing -> AST feature extraction -> "
                    "TF-IDF semantic embedding -> feature fusion -> ML scoring model -> knowledge "
                    "graph update -> security scan overlay. Include architecture diagram, data flow, "
                    "and component interaction descriptions. Detail the SQLite-backed knowledge "
                    "graph schema."
                ),
            },
            {
                "heading": "V. Methodology",
                "body": (
                    "Define the experimental setup: datasets, baselines (Pylint, SonarQube, Bandit), "
                    "hardware specifications, metrics (Precision, Recall, F1, latency, memory), and "
                    "statistical tests (Wilcoxon, Cliff's delta). Explain the benchmark suites and "
                    "reproducibility protocol."
                ),
            },
            {
                "heading": "VI. Results and Analysis",
                "body": (
                    "Present results per research question with tables and figures:\n"
                    "  - RQ1: Fusion vs. structural-only vs. semantic-only accuracy comparison.\n"
                    "  - RQ2: Latency distributions across file sizes and hardware tiers.\n"
                    "  - RQ3: Defect detection parity analysis with cloud tools.\n"
                    "  - RQ4: Knowledge graph impact on cross-file analysis.\n"
                    "  - RQ5: Security scanner comparison with Bandit/Semgrep.\n"
                    "Include statistical significance indicators and effect sizes."
                ),
            },
            {
                "heading": "VII. Discussion",
                "body": (
                    "Interpret findings, discuss limitations (e.g., current Python-only support, "
                    "absence of natural-language explanations), threats to validity (construct, "
                    "internal, external), and implications for privacy-sensitive development teams."
                ),
            },
            {
                "heading": "VIII. Conclusion and Future Work",
                "body": (
                    "Summarize contributions and key findings. Outline future directions: multi-language "
                    "support, on-device SLM integration, incremental learning, CI/CD pipeline "
                    "integration. Emphasize the broader impact on privacy-preserving software "
                    "engineering tooling."
                ),
            },
            {
                "heading": "IX. References",
                "body": (
                    "Format per IEEE or ACM citation style. Minimum 25-30 references covering "
                    "AST analysis, ML for code, static analysis benchmarks, privacy regulations, "
                    "and software engineering experimentation methodology."
                ),
            },
        ]

        content = "\n\n".join(
            f"{s['heading']}\n{s['body']}" for s in sections
        )

        citations = [
            "[1] IEEE. 'IEEE Conference Paper Template.' https://www.ieee.org/conferences/publishing/templates.html",
            "[2] ACM. 'ACM Primary Article Template.' https://www.acm.org/publications/proceedings-template",
            "[3] Feng, Z. et al. 'CodeBERT: A Pre-Trained Model for Programming and Natural Languages.' EMNLP 2020.",
            "[4] Guo, D. et al. 'GraphCodeBERT: Pre-training Code Representations with Data Flow.' ICLR 2021.",
            "[5] Alon, U. et al. 'code2vec: Learning Distributed Representations of Code.' POPL 2019.",
            "[6] Li, R. et al. 'StarCoder: May the Source Be With You!' TMLR 2023.",
            "[7] OWASP Foundation. 'OWASP Top Ten 2021.' https://owasp.org/Top10/",
            "[8] Wohlin, C. et al. 'Experimentation in Software Engineering.' Springer 2012.",
        ]

        return {
            "title": title,
            "content": content,
            "sections": [s["heading"] for s in sections],
            "citations_placeholder": citations,
        }


# ======================================================================
# Test Block
# ======================================================================
if __name__ == "__main__":
    assistant = ResearchAssistant()

    safe_print("=" * 70)
    safe_print("APCRE Research Assistant - Phase 11 Self-Test")
    safe_print("=" * 70)

    test_topic = "AI-Powered Code Review Engine (APCRE)"
    test_types = [
        "literature_review",
        "research_gaps",
        "novelty_statement",
        "future_work",
        "research_questions",
        "experimental_design",
        "benchmark_plan",
        "conference_outline",
    ]

    for rt in test_types:
        safe_print(f"\n{'─' * 60}")
        safe_print(f"Research Type: {rt}")
        safe_print(f"{'─' * 60}")

        result = assistant.generate(test_topic, rt)

        safe_print(f"  Title   : {result['title']}")
        safe_print(f"  Sections: {len(result['sections'])}")
        for s in result["sections"]:
            safe_print(f"    - {s}")
        safe_print(f"  Citations: {len(result['citations_placeholder'])}")
        safe_print(f"  Content length: {len(result['content'])} chars")

        # Validate structure
        assert "title" in result, f"Missing 'title' in {rt}"
        assert "content" in result, f"Missing 'content' in {rt}"
        assert "sections" in result, f"Missing 'sections' in {rt}"
        assert "citations_placeholder" in result, f"Missing 'citations_placeholder' in {rt}"
        assert len(result["sections"]) > 0, f"Empty sections in {rt}"
        assert len(result["content"]) > 100, f"Content too short in {rt}"

    # Test unknown type
    safe_print(f"\n{'─' * 60}")
    safe_print("Testing unknown research_type...")
    unknown = assistant.generate(test_topic, "invalid_type")
    assert "Unknown Research Type" in unknown["title"]
    safe_print(f"  Handled gracefully: {unknown['title']}")

    safe_print(f"\n{'=' * 70}")
    safe_print("ALL TESTS PASSED - Research Assistant module is operational.")
    safe_print(f"{'=' * 70}")
