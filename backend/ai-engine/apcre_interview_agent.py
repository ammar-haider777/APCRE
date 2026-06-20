# -*- coding: utf-8 -*-
"""
APCRE Services - Adaptive Engineering Interview Agent (Phase 19)
Conducts intelligent technical interviews across DSA, OOP, System Design,
and Code Review categories with adaptive difficulty scaling.

Features:
  - Question banks with 5+ questions per category at easy/medium/hard levels
  - Keyword/concept-based answer evaluation with partial credit scoring
  - Adaptive difficulty: score >= 80 raises difficulty, score < 50 lowers it
  - Session management with UUID-based tracking
  - Comprehensive session reports with strengths, weaknesses, and recommendations

Works 100% offline with zero external API calls.
Uses only Python standard library.
"""

import os
import uuid
import random
import re
import datetime


class InterviewAgent:
    """
    AI-powered adaptive interview engine that evaluates engineering candidates
    across multiple technical domains with progressive difficulty adjustment.
    """

    # ──────────────────────────────────────────────────────────────
    #  Difficulty levels used for adaptive scaling
    # ──────────────────────────────────────────────────────────────
    DIFFICULTY_EASY = "easy"
    DIFFICULTY_MEDIUM = "medium"
    DIFFICULTY_HARD = "hard"
    DIFFICULTY_ORDER = [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD]

    def __init__(self):
        """Initialise question banks and in-memory session store."""
        self.sessions = {}  # session_id -> session data dict
        self.question_bank = self._build_question_bank()

    # ================================================================
    #  PUBLIC API
    # ================================================================

    def start_interview(self, category: str = "dsa") -> dict:
        """
        Begin a new interview session for the given category.

        Args:
            category: One of 'dsa', 'oop', 'system_design', 'code_review'.

        Returns:
            dict with session_id, category, difficulty, and the first question.
        """
        category = category.lower().strip()
        if category not in self.question_bank:
            return {
                "success": False,
                "error": f"Unknown category '{category}'. "
                         f"Valid options: {list(self.question_bank.keys())}"
            }

        session_id = str(uuid.uuid4())
        first_difficulty = self.DIFFICULTY_MEDIUM
        question = self._pick_question(category, first_difficulty, asked_ids=[])

        self.sessions[session_id] = {
            "session_id": session_id,
            "category": category,
            "current_difficulty": first_difficulty,
            "current_question": question,
            "history": [],           # list of {question, answer, score, feedback}
            "asked_ids": [question["id"]],
            "started_at": datetime.datetime.now().isoformat(),
            "finished": False
        }

        return {
            "success": True,
            "session_id": session_id,
            "category": category,
            "difficulty": first_difficulty,
            "question_number": 1,
            "question": question["question"],
            "hint": question.get("hint", "")
        }

    def evaluate_answer(self, session_id: str, answer: str) -> dict:
        """
        Evaluate a candidate's answer for the current session question.

        Scoring strategy:
          - Each question carries a set of *expected_keywords* (concepts).
          - Partial credit: score = (matched / total) * 100
          - Bonus points (+5 each) for mentioning bonus keywords.

        Adaptive difficulty:
          - score >= 80 -> raise difficulty
          - score <  50 -> lower difficulty

        Args:
            session_id: UUID string from start_interview().
            answer: Free-text answer from the candidate.

        Returns:
            dict with score, feedback, correct_answer, and next_question (or
            a completion flag if the bank is exhausted).
        """
        if session_id not in self.sessions:
            return {"success": False, "error": "Invalid or expired session_id."}

        session = self.sessions[session_id]
        if session["finished"]:
            return {"success": False, "error": "Session already finished."}

        question = session["current_question"]

        # ── Score the answer ──────────────────────────────────────
        score, matched, missed = self._score_answer(answer, question)

        # ── Build qualitative feedback ────────────────────────────
        feedback = self._build_feedback(score, matched, missed, question)

        # ── Record in history ─────────────────────────────────────
        session["history"].append({
            "question_id": question["id"],
            "question": question["question"],
            "difficulty": session["current_difficulty"],
            "answer": answer,
            "score": score,
            "matched_keywords": matched,
            "missed_keywords": missed,
            "feedback": feedback
        })

        # ── Adapt difficulty ──────────────────────────────────────
        new_difficulty = self._adapt_difficulty(session["current_difficulty"], score)
        session["current_difficulty"] = new_difficulty

        # ── Pick next question ────────────────────────────────────
        next_q = self._pick_question(
            session["category"], new_difficulty, session["asked_ids"]
        )

        if next_q is None:
            session["finished"] = True
            session["finished_at"] = datetime.datetime.now().isoformat()
            return {
                "success": True,
                "score": score,
                "feedback": feedback,
                "correct_answer": question["correct_answer"],
                "difficulty_change": f"{session['current_difficulty']}",
                "interview_complete": True,
                "message": "All available questions have been asked. "
                           "Use get_session_report() for your results."
            }

        session["current_question"] = next_q
        session["asked_ids"].append(next_q["id"])

        return {
            "success": True,
            "score": score,
            "feedback": feedback,
            "correct_answer": question["correct_answer"],
            "difficulty_change": new_difficulty,
            "next_question": {
                "question_number": len(session["history"]) + 1,
                "difficulty": new_difficulty,
                "question": next_q["question"],
                "hint": next_q.get("hint", "")
            }
        }

    def get_session_report(self, session_id: str) -> dict:
        """
        Generate a comprehensive performance report for a completed
        (or in-progress) interview session.

        Returns:
            dict with overall_score, total_questions, strengths, weaknesses,
            difficulty_progression, and learning_recommendations.
        """
        if session_id not in self.sessions:
            return {"success": False, "error": "Invalid or expired session_id."}

        session = self.sessions[session_id]
        history = session["history"]

        if not history:
            return {
                "success": False,
                "error": "No answers have been submitted yet."
            }

        scores = [h["score"] for h in history]
        overall_score = round(sum(scores) / len(scores), 1)

        # ── Strengths & Weaknesses ────────────────────────────────
        strong_topics = []
        weak_topics = []
        all_matched = []
        all_missed = []

        for h in history:
            all_matched.extend(h["matched_keywords"])
            all_missed.extend(h["missed_keywords"])
            if h["score"] >= 70:
                strong_topics.append(h["question_id"])
            elif h["score"] < 50:
                weak_topics.append(h["question_id"])

        # Deduplicate
        all_matched = list(set(all_matched))
        all_missed = list(set(all_missed))

        # ── Difficulty progression ────────────────────────────────
        diff_progression = [h["difficulty"] for h in history]

        # ── Learning recommendations ──────────────────────────────
        recommendations = self._generate_recommendations(
            session["category"], weak_topics, all_missed, overall_score
        )

        # ── Grade label ───────────────────────────────────────────
        if overall_score >= 90:
            grade = "Excellent"
        elif overall_score >= 75:
            grade = "Good"
        elif overall_score >= 55:
            grade = "Average"
        elif overall_score >= 35:
            grade = "Below Average"
        else:
            grade = "Needs Improvement"

        return {
            "success": True,
            "session_id": session_id,
            "category": session["category"],
            "total_questions": len(history),
            "overall_score": overall_score,
            "grade": grade,
            "strengths": strong_topics,
            "weaknesses": weak_topics,
            "concepts_demonstrated": all_matched,
            "concepts_missed": all_missed,
            "difficulty_progression": diff_progression,
            "learning_recommendations": recommendations,
            "started_at": session["started_at"],
            "finished_at": session.get("finished_at", "in-progress")
        }

    # ================================================================
    #  PRIVATE – Scoring & Feedback
    # ================================================================

    def _score_answer(self, answer: str, question: dict) -> tuple:
        """
        Score an answer based on keyword/concept matching.

        Returns (score, matched_list, missed_list).
        """
        answer_lower = answer.lower()
        expected = question["expected_keywords"]
        bonus = question.get("bonus_keywords", [])

        matched = [kw for kw in expected if kw.lower() in answer_lower]
        missed = [kw for kw in expected if kw.lower() not in answer_lower]

        if len(expected) == 0:
            base_score = 50
        else:
            base_score = int((len(matched) / len(expected)) * 100)

        # Bonus points for extra depth
        bonus_matched = [kw for kw in bonus if kw.lower() in answer_lower]
        bonus_pts = len(bonus_matched) * 5

        score = min(100, base_score + bonus_pts)
        matched.extend(bonus_matched)
        return score, matched, missed

    def _build_feedback(self, score: int, matched: list,
                        missed: list, question: dict) -> str:
        """Generate qualitative feedback text from the scoring result."""
        parts = []

        if score >= 90:
            parts.append("Outstanding answer! You demonstrated deep understanding.")
        elif score >= 70:
            parts.append("Good answer with solid coverage of key concepts.")
        elif score >= 50:
            parts.append("Acceptable answer, but several important concepts were missing.")
        elif score >= 30:
            parts.append("Partial answer. Review the core concepts for this topic.")
        else:
            parts.append("The answer did not address the expected concepts. "
                         "Consider studying this topic thoroughly.")

        if matched:
            parts.append(f"Concepts you covered: {', '.join(matched)}.")
        if missed:
            parts.append(f"Concepts you missed: {', '.join(missed)}.")

        return " ".join(parts)

    def _adapt_difficulty(self, current: str, score: int) -> str:
        """
        Adjust difficulty based on score:
          score >= 80 -> harder
          score <  50 -> easier
          else        -> stay same
        """
        idx = self.DIFFICULTY_ORDER.index(current)

        if score >= 80 and idx < len(self.DIFFICULTY_ORDER) - 1:
            return self.DIFFICULTY_ORDER[idx + 1]
        elif score < 50 and idx > 0:
            return self.DIFFICULTY_ORDER[idx - 1]
        return current

    def _pick_question(self, category: str, difficulty: str,
                       asked_ids: list) -> dict | None:
        """
        Pick a random un-asked question at the target difficulty.
        Falls back to adjacent difficulties if none remain.
        Returns None if the entire category is exhausted.
        """
        bank = self.question_bank.get(category, [])

        # Try exact difficulty first
        candidates = [q for q in bank
                      if q["difficulty"] == difficulty and q["id"] not in asked_ids]
        if candidates:
            return random.choice(candidates)

        # Fallback: try any difficulty in the category
        candidates = [q for q in bank if q["id"] not in asked_ids]
        if candidates:
            return random.choice(candidates)

        return None

    def _generate_recommendations(self, category: str, weak_topics: list,
                                  missed_concepts: list,
                                  overall_score: float) -> list:
        """Build a list of actionable learning recommendations."""
        recs = []

        # Category-specific generic advice
        category_resources = {
            "dsa": "Practice on platforms like LeetCode or HackerRank focusing on "
                   "trees, graphs, and dynamic programming.",
            "oop": "Review SOLID principles and design patterns from "
                   "'Head First Design Patterns' or 'Clean Code' by Robert Martin.",
            "system_design": "Study 'Designing Data-Intensive Applications' by "
                             "Martin Kleppmann and practice whiteboard system designs.",
            "code_review": "Read PEP 8, OWASP guidelines, and practice reviewing "
                           "open-source pull requests on GitHub."
        }

        if overall_score < 70:
            recs.append(category_resources.get(category, "Review fundamentals."))

        if missed_concepts:
            unique_missed = list(set(missed_concepts))[:8]
            recs.append(
                f"Focus on these concepts: {', '.join(unique_missed)}."
            )

        if weak_topics:
            recs.append(
                f"Revisit question areas: {', '.join(weak_topics)}."
            )

        if overall_score >= 80:
            recs.append("Strong performance! Consider tackling advanced system "
                        "design or competitive programming challenges.")
        elif overall_score >= 60:
            recs.append("Solid foundation. Deepen understanding of the missed "
                        "concepts and practice timed interview simulations.")
        else:
            recs.append("Dedicate structured study time to each weak area. "
                        "Use spaced repetition to reinforce key concepts.")

        return recs

    # ================================================================
    #  QUESTION BANK BUILDER
    # ================================================================

    def _build_question_bank(self) -> dict:
        """
        Construct the master question bank.

        Each question is a dict:
          id, category, difficulty, question, hint,
          expected_keywords, bonus_keywords, correct_answer
        """
        bank = {
            "dsa": self._dsa_questions(),
            "oop": self._oop_questions(),
            "system_design": self._system_design_questions(),
            "code_review": self._code_review_questions()
        }
        return bank

    # ──────────────────────────────────────────────────────────────
    #  DSA Questions
    # ──────────────────────────────────────────────────────────────
    def _dsa_questions(self) -> list:
        return [
            # --- EASY ---
            {
                "id": "dsa_sort_easy",
                "category": "dsa",
                "difficulty": self.DIFFICULTY_EASY,
                "question": (
                    "Explain the difference between Bubble Sort and Selection Sort. "
                    "What is the time complexity of each?"
                ),
                "hint": "Think about how elements are compared and swapped.",
                "expected_keywords": [
                    "bubble sort", "selection sort", "O(n^2)",
                    "swap", "comparison"
                ],
                "bonus_keywords": ["stable", "in-place", "adaptive"],
                "correct_answer": (
                    "Bubble Sort repeatedly swaps adjacent elements if they are "
                    "in the wrong order, bubbling the largest element to the end "
                    "each pass. Selection Sort finds the minimum element in the "
                    "unsorted portion and places it at the beginning. Both have "
                    "O(n^2) worst-case time complexity, but Bubble Sort is stable "
                    "while Selection Sort is not. Bubble Sort can terminate early "
                    "if no swaps occur (adaptive), making best case O(n)."
                )
            },
            {
                "id": "dsa_hash_easy",
                "category": "dsa",
                "difficulty": self.DIFFICULTY_EASY,
                "question": (
                    "What is a hash table? Explain how collisions are handled."
                ),
                "hint": "Consider chaining and open addressing.",
                "expected_keywords": [
                    "hash function", "key-value", "collision",
                    "chaining", "O(1)"
                ],
                "bonus_keywords": ["load factor", "rehashing", "open addressing"],
                "correct_answer": (
                    "A hash table is a data structure that maps keys to values "
                    "using a hash function for O(1) average lookup. Collisions "
                    "(two keys mapping to the same index) are handled via "
                    "chaining (linked lists at each bucket) or open addressing "
                    "(probing for the next empty slot). The load factor determines "
                    "when to resize/rehash the table."
                )
            },
            # --- MEDIUM ---
            {
                "id": "dsa_graph_medium",
                "category": "dsa",
                "difficulty": self.DIFFICULTY_MEDIUM,
                "question": (
                    "Compare BFS and DFS graph traversal algorithms. When would "
                    "you choose one over the other?"
                ),
                "hint": "Think about queue vs stack, and shortest path scenarios.",
                "expected_keywords": [
                    "BFS", "DFS", "queue", "stack",
                    "shortest path", "traversal"
                ],
                "bonus_keywords": [
                    "level-order", "recursion", "topological",
                    "connected components"
                ],
                "correct_answer": (
                    "BFS (Breadth-First Search) uses a queue and explores all "
                    "neighbours at the current depth before moving deeper. It "
                    "finds the shortest path in unweighted graphs. DFS "
                    "(Depth-First Search) uses a stack (or recursion) and "
                    "explores as far as possible along each branch before "
                    "backtracking. DFS is preferred for topological sorting, "
                    "cycle detection, and pathfinding in mazes, while BFS is "
                    "ideal for shortest-path and level-order traversals."
                )
            },
            {
                "id": "dsa_dp_medium",
                "category": "dsa",
                "difficulty": self.DIFFICULTY_MEDIUM,
                "question": (
                    "What is dynamic programming? Explain the difference between "
                    "memoization (top-down) and tabulation (bottom-up) approaches."
                ),
                "hint": "Think about overlapping subproblems and optimal substructure.",
                "expected_keywords": [
                    "dynamic programming", "overlapping subproblems",
                    "optimal substructure", "memoization", "tabulation"
                ],
                "bonus_keywords": ["Fibonacci", "top-down", "bottom-up", "cache"],
                "correct_answer": (
                    "Dynamic programming solves complex problems by breaking them "
                    "into overlapping subproblems that exhibit optimal substructure. "
                    "Memoization (top-down) uses recursion with a cache to store "
                    "computed results. Tabulation (bottom-up) iteratively builds a "
                    "table from the smallest subproblems upward. Memoization is "
                    "easier to implement but may hit recursion limits; tabulation "
                    "avoids stack overflow and is generally faster."
                )
            },
            # --- HARD ---
            {
                "id": "dsa_avl_hard",
                "category": "dsa",
                "difficulty": self.DIFFICULTY_HARD,
                "question": (
                    "Explain AVL tree balancing. Describe all four rotation cases "
                    "and when each is applied. What is the time complexity of "
                    "insertion in an AVL tree?"
                ),
                "hint": "Consider balance factors and LL, RR, LR, RL rotations.",
                "expected_keywords": [
                    "AVL", "balance factor", "rotation",
                    "left rotation", "right rotation", "O(log n)"
                ],
                "bonus_keywords": [
                    "LL", "RR", "LR", "RL", "height",
                    "self-balancing", "binary search tree"
                ],
                "correct_answer": (
                    "An AVL tree is a self-balancing binary search tree where the "
                    "balance factor (height difference of left and right subtrees) "
                    "of every node is -1, 0, or 1. After insertion, if a node "
                    "becomes unbalanced, one of four rotations is performed: "
                    "LL (Right Rotation) when the left subtree of the left child "
                    "is too tall; RR (Left Rotation) for the right subtree of the "
                    "right child; LR (Left-Right Double Rotation) for the right "
                    "subtree of the left child; RL (Right-Left Double Rotation) "
                    "for the left subtree of the right child. Insertion is O(log n) "
                    "because the tree height is always O(log n)."
                )
            },
            {
                "id": "dsa_advanced_sort_hard",
                "category": "dsa",
                "difficulty": self.DIFFICULTY_HARD,
                "question": (
                    "Compare Merge Sort, Quick Sort, and Heap Sort. Discuss their "
                    "time/space complexities and stability. When is each preferred?"
                ),
                "hint": "Consider worst-case guarantees and cache performance.",
                "expected_keywords": [
                    "merge sort", "quick sort", "heap sort",
                    "O(n log n)", "stable", "in-place"
                ],
                "bonus_keywords": [
                    "divide and conquer", "pivot", "cache-friendly",
                    "worst-case", "O(n) space"
                ],
                "correct_answer": (
                    "Merge Sort: O(n log n) worst-case, stable, but requires "
                    "O(n) extra space. Quick Sort: O(n log n) average, O(n^2) "
                    "worst-case (poor pivot), in-place, unstable, but excellent "
                    "cache performance. Heap Sort: O(n log n) guaranteed, in-place, "
                    "unstable, poor cache locality. Merge Sort is preferred when "
                    "stability matters (linked lists); Quick Sort for general-purpose "
                    "arrays; Heap Sort when guaranteed O(n log n) with O(1) space "
                    "is needed."
                )
            },
        ]

    # ──────────────────────────────────────────────────────────────
    #  OOP Questions
    # ──────────────────────────────────────────────────────────────
    def _oop_questions(self) -> list:
        return [
            # --- EASY ---
            {
                "id": "oop_encapsulation_easy",
                "category": "oop",
                "difficulty": self.DIFFICULTY_EASY,
                "question": (
                    "What is encapsulation in OOP? How does Python implement it "
                    "compared to languages like Java?"
                ),
                "hint": "Think about access modifiers and naming conventions.",
                "expected_keywords": [
                    "encapsulation", "private", "public",
                    "data hiding", "underscore"
                ],
                "bonus_keywords": [
                    "name mangling", "double underscore", "getter", "setter"
                ],
                "correct_answer": (
                    "Encapsulation bundles data and methods that operate on that "
                    "data within a class, restricting direct access to internal "
                    "state. Java uses explicit access modifiers (private, protected, "
                    "public). Python uses naming conventions: a single underscore "
                    "prefix (_var) signals 'protected', and a double underscore "
                    "prefix (__var) triggers name mangling for stronger hiding, "
                    "though nothing is truly private in Python."
                )
            },
            {
                "id": "oop_inheritance_easy",
                "category": "oop",
                "difficulty": self.DIFFICULTY_EASY,
                "question": (
                    "Explain the difference between inheritance and composition. "
                    "When should you prefer one over the other?"
                ),
                "hint": "Think 'is-a' versus 'has-a' relationships.",
                "expected_keywords": [
                    "inheritance", "composition", "is-a", "has-a",
                    "code reuse"
                ],
                "bonus_keywords": [
                    "coupling", "flexibility", "delegation",
                    "favor composition"
                ],
                "correct_answer": (
                    "Inheritance creates an 'is-a' relationship where a subclass "
                    "inherits behavior from a parent class. Composition creates a "
                    "'has-a' relationship where a class contains instances of other "
                    "classes. Composition is generally preferred ('favor composition "
                    "over inheritance') because it provides greater flexibility, "
                    "lower coupling, and easier testing. Use inheritance for true "
                    "type hierarchies and composition for assembling behaviors."
                )
            },
            # --- MEDIUM ---
            {
                "id": "oop_abc_medium",
                "category": "oop",
                "difficulty": self.DIFFICULTY_MEDIUM,
                "question": (
                    "What are Abstract Base Classes (ABCs) in Python? How do you "
                    "define and use them with the abc module?"
                ),
                "hint": "Think about @abstractmethod and the ABC metaclass.",
                "expected_keywords": [
                    "abstract", "ABC", "abstractmethod",
                    "interface", "cannot instantiate"
                ],
                "bonus_keywords": [
                    "abc module", "metaclass", "contract",
                    "template method"
                ],
                "correct_answer": (
                    "Abstract Base Classes define interfaces or contracts that "
                    "subclasses must implement. In Python, you import ABC and "
                    "abstractmethod from the abc module, then create a class "
                    "inheriting from ABC with methods decorated with "
                    "@abstractmethod. ABCs cannot be instantiated directly; "
                    "subclasses must override all abstract methods. They enforce "
                    "a consistent API across class hierarchies."
                )
            },
            {
                "id": "oop_property_medium",
                "category": "oop",
                "difficulty": self.DIFFICULTY_MEDIUM,
                "question": (
                    "Explain Python's @property decorator. How does it relate "
                    "to getters and setters? Provide a usage example."
                ),
                "hint": "Think about controlled attribute access.",
                "expected_keywords": [
                    "property", "decorator", "getter", "setter",
                    "attribute"
                ],
                "bonus_keywords": [
                    "deleter", "descriptor", "validation",
                    "computed property"
                ],
                "correct_answer": (
                    "The @property decorator lets you define methods that are "
                    "accessed like attributes. The getter is defined with "
                    "@property, the setter with @name.setter, and optionally "
                    "a deleter with @name.deleter. This enables data validation, "
                    "computed properties, and encapsulation without changing the "
                    "public API. Example: @property def name(self): return "
                    "self._name; @name.setter def name(self, value): "
                    "self._name = value"
                )
            },
            # --- HARD ---
            {
                "id": "oop_solid_hard",
                "category": "oop",
                "difficulty": self.DIFFICULTY_HARD,
                "question": (
                    "Explain the SOLID principles of object-oriented design. "
                    "Give a brief example of how violating the Single Responsibility "
                    "Principle leads to maintenance issues."
                ),
                "hint": "S-O-L-I-D: five principles by Robert C. Martin.",
                "expected_keywords": [
                    "single responsibility", "open closed",
                    "Liskov substitution", "interface segregation",
                    "dependency inversion"
                ],
                "bonus_keywords": [
                    "Robert Martin", "SOLID", "cohesion",
                    "decoupling", "abstraction"
                ],
                "correct_answer": (
                    "SOLID: (S) Single Responsibility - a class should have one "
                    "reason to change; (O) Open/Closed - open for extension, "
                    "closed for modification; (L) Liskov Substitution - subtypes "
                    "must be substitutable for their base types; (I) Interface "
                    "Segregation - many specific interfaces over one general; "
                    "(D) Dependency Inversion - depend on abstractions, not "
                    "concretions. Violating SRP (e.g., a class handling database "
                    "access, business logic, AND email sending) makes the class "
                    "fragile — any change to email logic risks breaking database "
                    "operations."
                )
            },
            {
                "id": "oop_design_patterns_hard",
                "category": "oop",
                "difficulty": self.DIFFICULTY_HARD,
                "question": (
                    "Compare the Factory Method and Abstract Factory design "
                    "patterns. When would you use each?"
                ),
                "hint": "One creates a single product; the other creates families.",
                "expected_keywords": [
                    "factory method", "abstract factory",
                    "creational pattern", "interface", "subclass"
                ],
                "bonus_keywords": [
                    "Gang of Four", "product family",
                    "loose coupling", "polymorphism"
                ],
                "correct_answer": (
                    "Factory Method defines an interface for creating a single "
                    "object but lets subclasses decide which class to instantiate. "
                    "Abstract Factory provides an interface for creating families "
                    "of related objects without specifying concrete classes. Use "
                    "Factory Method when you have one product type with variations; "
                    "use Abstract Factory when you need to create coherent families "
                    "of products (e.g., UI toolkit with matching buttons, menus, "
                    "and scrollbars for different platforms)."
                )
            },
        ]

    # ──────────────────────────────────────────────────────────────
    #  System Design Questions
    # ──────────────────────────────────────────────────────────────
    def _system_design_questions(self) -> list:
        return [
            # --- EASY ---
            {
                "id": "sd_mvc_easy",
                "category": "system_design",
                "difficulty": self.DIFFICULTY_EASY,
                "question": (
                    "Compare the MVC and MVVM architectural patterns. "
                    "What are the key differences?"
                ),
                "hint": "Think about data binding and the role of the controller vs view-model.",
                "expected_keywords": [
                    "MVC", "MVVM", "model", "view",
                    "controller", "view-model"
                ],
                "bonus_keywords": [
                    "data binding", "separation of concerns",
                    "two-way binding", "observer"
                ],
                "correct_answer": (
                    "MVC (Model-View-Controller) separates application logic into "
                    "three components: Model (data), View (UI), and Controller "
                    "(handles input and updates Model). MVVM (Model-View-ViewModel) "
                    "replaces the Controller with a ViewModel that uses data binding "
                    "to automatically sync the View and Model. MVVM is preferred in "
                    "modern UI frameworks (WPF, Vue.js, Angular) because two-way "
                    "data binding reduces boilerplate code."
                )
            },
            {
                "id": "sd_cache_easy",
                "category": "system_design",
                "difficulty": self.DIFFICULTY_EASY,
                "question": (
                    "What are caching strategies? Explain the differences between "
                    "cache-aside, write-through, and write-behind caching."
                ),
                "hint": "Think about when data is written to cache vs database.",
                "expected_keywords": [
                    "cache", "cache-aside", "write-through",
                    "latency", "cache miss"
                ],
                "bonus_keywords": [
                    "write-behind", "TTL", "eviction",
                    "LRU", "Redis"
                ],
                "correct_answer": (
                    "Cache-aside (lazy loading): application checks cache first; "
                    "on miss, loads from database and populates cache. "
                    "Write-through: data is written to both cache and database "
                    "simultaneously, ensuring consistency but adding latency. "
                    "Write-behind (write-back): data is written to cache first "
                    "and asynchronously flushed to database, reducing latency but "
                    "risking data loss. Common eviction policies include LRU "
                    "(Least Recently Used) and TTL (Time To Live)."
                )
            },
            # --- MEDIUM ---
            {
                "id": "sd_loadbalancer_medium",
                "category": "system_design",
                "difficulty": self.DIFFICULTY_MEDIUM,
                "question": (
                    "Explain load balancing strategies. Compare round-robin, "
                    "least connections, and consistent hashing."
                ),
                "hint": "Consider traffic distribution and server health.",
                "expected_keywords": [
                    "load balancer", "round-robin",
                    "least connections", "distribute", "traffic"
                ],
                "bonus_keywords": [
                    "consistent hashing", "health check",
                    "sticky sessions", "horizontal scaling"
                ],
                "correct_answer": (
                    "Load balancers distribute incoming traffic across multiple "
                    "servers. Round-robin assigns requests cyclically to each "
                    "server. Least connections routes to the server with the "
                    "fewest active connections. Consistent hashing maps requests "
                    "to servers using a hash ring, minimising redistribution when "
                    "servers are added or removed. Health checks ensure traffic "
                    "is only sent to healthy servers."
                )
            },
            {
                "id": "sd_messagequeue_medium",
                "category": "system_design",
                "difficulty": self.DIFFICULTY_MEDIUM,
                "question": (
                    "What are message queues and when would you use them in a "
                    "distributed system? Give examples of popular implementations."
                ),
                "hint": "Think about decoupling, async processing, and back-pressure.",
                "expected_keywords": [
                    "message queue", "asynchronous",
                    "decoupling", "producer", "consumer"
                ],
                "bonus_keywords": [
                    "RabbitMQ", "Kafka", "back-pressure",
                    "dead letter queue", "pub/sub"
                ],
                "correct_answer": (
                    "Message queues enable asynchronous communication between "
                    "services by decoupling producers (senders) from consumers "
                    "(receivers). They buffer messages, handle traffic spikes, "
                    "and ensure reliability through persistence and acknowledgments. "
                    "Use cases include order processing, email notifications, "
                    "and log aggregation. Popular implementations: RabbitMQ "
                    "(AMQP-based), Apache Kafka (distributed log), and AWS SQS "
                    "(managed cloud queue)."
                )
            },
            # --- HARD ---
            {
                "id": "sd_sharding_hard",
                "category": "system_design",
                "difficulty": self.DIFFICULTY_HARD,
                "question": (
                    "Explain database sharding. What are horizontal vs vertical "
                    "sharding? Discuss the challenges and trade-offs involved."
                ),
                "hint": "Think about partition keys, cross-shard queries, and rebalancing.",
                "expected_keywords": [
                    "sharding", "horizontal", "partition",
                    "scalability", "shard key"
                ],
                "bonus_keywords": [
                    "vertical sharding", "cross-shard join",
                    "rebalancing", "consistent hashing", "hotspot"
                ],
                "correct_answer": (
                    "Sharding partitions a database across multiple servers. "
                    "Horizontal sharding splits rows across shards using a shard "
                    "key (e.g., user_id % N). Vertical sharding splits columns/"
                    "tables across servers. Challenges: cross-shard joins are "
                    "expensive, rebalancing data when adding shards is complex, "
                    "hotspots occur if the shard key distribution is uneven, and "
                    "maintaining ACID transactions across shards requires "
                    "distributed protocols (2PC, Saga)."
                )
            },
            {
                "id": "sd_cap_hard",
                "category": "system_design",
                "difficulty": self.DIFFICULTY_HARD,
                "question": (
                    "Explain the CAP theorem. How do different databases "
                    "(e.g., PostgreSQL, MongoDB, Cassandra) make trade-offs "
                    "between consistency, availability, and partition tolerance?"
                ),
                "hint": "You can only guarantee two of the three at any time.",
                "expected_keywords": [
                    "CAP", "consistency", "availability",
                    "partition tolerance", "trade-off"
                ],
                "bonus_keywords": [
                    "eventual consistency", "CP", "AP",
                    "Cassandra", "PostgreSQL"
                ],
                "correct_answer": (
                    "The CAP theorem states that a distributed system can only "
                    "guarantee two of three properties: Consistency (all nodes see "
                    "the same data), Availability (every request gets a response), "
                    "and Partition Tolerance (system operates despite network "
                    "splits). PostgreSQL is CP (consistency + partition tolerance). "
                    "Cassandra is AP (availability + partition tolerance with "
                    "eventual consistency). MongoDB defaults to CP but can be "
                    "tuned for availability."
                )
            },
        ]

    # ──────────────────────────────────────────────────────────────
    #  Code Review Questions (buggy code snippets)
    # ──────────────────────────────────────────────────────────────
    def _code_review_questions(self) -> list:
        return [
            # --- EASY ---
            {
                "id": "cr_bare_except_easy",
                "category": "code_review",
                "difficulty": self.DIFFICULTY_EASY,
                "question": (
                    "Review this code and identify the issues:\n\n"
                    "```python\n"
                    "def fetch_data(url):\n"
                    "    try:\n"
                    "        response = requests.get(url)\n"
                    "        data = response.json()\n"
                    "        return data\n"
                    "    except:\n"
                    "        pass\n"
                    "```"
                ),
                "hint": "Look at exception handling and return values.",
                "expected_keywords": [
                    "bare except", "pass", "silent failure",
                    "specific exception", "return None"
                ],
                "bonus_keywords": [
                    "logging", "Exception as e",
                    "requests.RequestException", "error handling"
                ],
                "correct_answer": (
                    "Issues: (1) Bare 'except:' catches all exceptions including "
                    "SystemExit and KeyboardInterrupt, masking real bugs. Should "
                    "catch specific exceptions (e.g., requests.RequestException). "
                    "(2) 'pass' silently swallows errors with no logging or "
                    "fallback. (3) Function implicitly returns None on failure, "
                    "which callers may not handle. Fix: catch specific exceptions, "
                    "log the error, and return a meaningful default or re-raise."
                )
            },
            {
                "id": "cr_docstring_easy",
                "category": "code_review",
                "difficulty": self.DIFFICULTY_EASY,
                "question": (
                    "Review this code and identify the issues:\n\n"
                    "```python\n"
                    "def calc(a, b, c, d):\n"
                    "    x = a * b + c\n"
                    "    y = x / d\n"
                    "    z = y ** 2 - a\n"
                    "    return z\n"
                    "```"
                ),
                "hint": "Think about readability, documentation, and edge cases.",
                "expected_keywords": [
                    "docstring", "variable names",
                    "division by zero", "readability"
                ],
                "bonus_keywords": [
                    "type hints", "descriptive names", "PEP 8",
                    "ZeroDivisionError"
                ],
                "correct_answer": (
                    "Issues: (1) No docstring explaining what the function "
                    "calculates. (2) Non-descriptive parameter names (a, b, c, d) "
                    "and variable names (x, y, z) make the code unreadable. "
                    "(3) No guard against division by zero when d=0. (4) No type "
                    "hints. Fix: add a docstring, use descriptive names, add "
                    "type hints, and handle d=0 with a guard clause."
                )
            },
            # --- MEDIUM ---
            {
                "id": "cr_sql_injection_medium",
                "category": "code_review",
                "difficulty": self.DIFFICULTY_MEDIUM,
                "question": (
                    "Review this code and identify the security vulnerability:\n\n"
                    "```python\n"
                    "def get_user(username):\n"
                    "    query = f\"SELECT * FROM users WHERE name = '{username}'\"\n"
                    "    cursor.execute(query)\n"
                    "    return cursor.fetchone()\n"
                    "```"
                ),
                "hint": "Think about what happens if username contains special SQL characters.",
                "expected_keywords": [
                    "SQL injection", "parameterized",
                    "f-string", "user input", "sanitize"
                ],
                "bonus_keywords": [
                    "prepared statement", "ORM",
                    "Bobby Tables", "CWE-89"
                ],
                "correct_answer": (
                    "Critical SQL Injection vulnerability: the username is directly "
                    "interpolated into the SQL query using an f-string. An attacker "
                    "can inject malicious SQL (e.g., username = \"' OR 1=1; --\") "
                    "to dump the entire table or modify data. Fix: use "
                    "parameterized queries: cursor.execute('SELECT * FROM users "
                    "WHERE name = ?', (username,)) or use an ORM."
                )
            },
            {
                "id": "cr_nested_loops_medium",
                "category": "code_review",
                "difficulty": self.DIFFICULTY_MEDIUM,
                "question": (
                    "Review this code and identify performance issues:\n\n"
                    "```python\n"
                    "def find_duplicates(items):\n"
                    "    duplicates = []\n"
                    "    for i in range(len(items)):\n"
                    "        for j in range(len(items)):\n"
                    "            if i != j and items[i] == items[j]:\n"
                    "                if items[i] not in duplicates:\n"
                    "                    duplicates.append(items[i])\n"
                    "    return duplicates\n"
                    "```"
                ),
                "hint": "Think about time complexity and data structures.",
                "expected_keywords": [
                    "O(n^2)", "nested loops", "set",
                    "performance", "duplicate"
                ],
                "bonus_keywords": [
                    "Counter", "collections", "hash set",
                    "O(n)", "dictionary"
                ],
                "correct_answer": (
                    "Issues: (1) O(n^2) nested loops make this extremely slow for "
                    "large lists. (2) 'if items[i] not in duplicates' is another "
                    "O(n) scan inside the inner loop, making it O(n^3) overall. "
                    "(3) Using a list for 'duplicates' instead of a set. Fix: "
                    "use collections.Counter or a dictionary to count occurrences "
                    "in O(n), then filter items with count > 1."
                )
            },
            # --- HARD ---
            {
                "id": "cr_thread_safety_hard",
                "category": "code_review",
                "difficulty": self.DIFFICULTY_HARD,
                "question": (
                    "Review this code and identify the concurrency issue:\n\n"
                    "```python\n"
                    "import threading\n"
                    "\n"
                    "class BankAccount:\n"
                    "    def __init__(self):\n"
                    "        self.balance = 0\n"
                    "\n"
                    "    def deposit(self, amount):\n"
                    "        current = self.balance\n"
                    "        self.balance = current + amount\n"
                    "\n"
                    "    def withdraw(self, amount):\n"
                    "        if self.balance >= amount:\n"
                    "            current = self.balance\n"
                    "            self.balance = current - amount\n"
                    "```"
                ),
                "hint": "Think about what happens when two threads call deposit simultaneously.",
                "expected_keywords": [
                    "race condition", "thread safety",
                    "lock", "mutex", "concurrent"
                ],
                "bonus_keywords": [
                    "atomic", "critical section",
                    "threading.Lock", "TOCTOU"
                ],
                "correct_answer": (
                    "Classic race condition: deposit() reads self.balance into "
                    "'current', then writes back. If two threads read the same "
                    "balance simultaneously, one deposit is lost. Similarly, "
                    "withdraw() has a TOCTOU (time-of-check-to-time-of-use) bug: "
                    "the balance check and subtraction are not atomic. Fix: use "
                    "threading.Lock() to guard critical sections: "
                    "with self.lock: self.balance += amount."
                )
            },
            {
                "id": "cr_memory_leak_hard",
                "category": "code_review",
                "difficulty": self.DIFFICULTY_HARD,
                "question": (
                    "Review this code and identify the resource management issue:\n\n"
                    "```python\n"
                    "class DataProcessor:\n"
                    "    def __init__(self):\n"
                    "        self.cache = {}\n"
                    "        self.connections = []\n"
                    "\n"
                    "    def process(self, filepath):\n"
                    "        f = open(filepath, 'r')\n"
                    "        data = f.read()\n"
                    "        self.cache[filepath] = data\n"
                    "        conn = create_db_connection()\n"
                    "        self.connections.append(conn)\n"
                    "        result = conn.execute('SELECT * FROM results')\n"
                    "        return result\n"
                    "```"
                ),
                "hint": "Think about file handles, connection pools, and unbounded caches.",
                "expected_keywords": [
                    "file not closed", "resource leak",
                    "context manager", "with statement",
                    "memory leak"
                ],
                "bonus_keywords": [
                    "connection pool", "unbounded cache",
                    "finally", "__del__", "LRU cache"
                ],
                "correct_answer": (
                    "Issues: (1) File handle is never closed — should use "
                    "'with open(...) as f:' context manager. (2) Database "
                    "connections accumulate in self.connections without ever "
                    "being closed, causing connection exhaustion. (3) self.cache "
                    "grows unboundedly — every file processed stays in memory "
                    "forever, causing a memory leak. Fix: use context managers "
                    "for files and connections, implement connection pooling, and "
                    "limit cache size with an LRU eviction policy."
                )
            },
        ]


# ════════════════════════════════════════════════════════════════
#  STANDALONE TEST BLOCK
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":

    def safe_print(*args, **kwargs):
        """Handle Windows CP1252 encoding edge-cases."""
        try:
            print(*args, **kwargs)
        except (UnicodeEncodeError, UnicodeDecodeError):
            text = " ".join(str(a) for a in args)
            print(text.encode("ascii", errors="replace").decode("ascii"), **kwargs)

    agent = InterviewAgent()

    safe_print("=" * 70)
    safe_print("APCRE - Adaptive Engineering Interview Agent (Phase 19)")
    safe_print("=" * 70)

    # ── Start a DSA interview ─────────────────────────────────
    safe_print("\n[1] Starting DSA interview...")
    result = agent.start_interview("dsa")
    safe_print(f"    Session ID : {result['session_id']}")
    safe_print(f"    Category   : {result['category']}")
    safe_print(f"    Difficulty : {result['difficulty']}")
    safe_print(f"    Question   : {result['question'][:100]}...")

    session_id = result["session_id"]

    # ── Answer 1: Good answer (should raise difficulty) ────────
    safe_print("\n[2] Submitting a STRONG answer...")
    answer1 = (
        "BFS uses a queue and explores all neighbours level by level, "
        "finding the shortest path in unweighted graphs. DFS uses a stack "
        "or recursion and goes as deep as possible before backtracking. "
        "BFS is good for shortest path and level-order traversal. DFS is "
        "useful for topological sorting and cycle detection in connected "
        "components."
    )
    eval1 = agent.evaluate_answer(session_id, answer1)
    safe_print(f"    Score      : {eval1['score']}")
    safe_print(f"    Feedback   : {eval1['feedback'][:120]}...")
    safe_print(f"    Difficulty : {eval1.get('difficulty_change', 'N/A')}")
    if "next_question" in eval1:
        safe_print(f"    Next Q     : {eval1['next_question']['question'][:100]}...")

    # ── Answer 2: Weak answer (should lower difficulty) ────────
    safe_print("\n[3] Submitting a WEAK answer...")
    answer2 = "I think it sorts things."
    eval2 = agent.evaluate_answer(session_id, answer2)
    safe_print(f"    Score      : {eval2['score']}")
    safe_print(f"    Feedback   : {eval2['feedback'][:120]}...")
    safe_print(f"    Difficulty : {eval2.get('difficulty_change', 'N/A')}")

    # ── Answer 3: Medium answer ──────────────────────────────
    if "next_question" in eval2:
        safe_print("\n[4] Submitting a MEDIUM answer...")
        answer3 = (
            "A hash table uses a hash function to map keys to values "
            "with O(1) average lookup. Collisions are handled with chaining."
        )
        eval3 = agent.evaluate_answer(session_id, answer3)
        safe_print(f"    Score      : {eval3['score']}")
        safe_print(f"    Feedback   : {eval3['feedback'][:120]}...")

    # ── Session Report ────────────────────────────────────────
    safe_print("\n[5] Generating session report...")
    report = agent.get_session_report(session_id)
    safe_print(f"    Overall Score       : {report['overall_score']}")
    safe_print(f"    Grade               : {report['grade']}")
    safe_print(f"    Total Questions     : {report['total_questions']}")
    safe_print(f"    Strengths           : {report['strengths']}")
    safe_print(f"    Weaknesses          : {report['weaknesses']}")
    safe_print(f"    Concepts Covered    : {report['concepts_demonstrated']}")
    safe_print(f"    Concepts Missed     : {report['concepts_missed']}")
    safe_print(f"    Difficulty Path     : {report['difficulty_progression']}")
    safe_print(f"    Recommendations     :")
    for rec in report["learning_recommendations"]:
        safe_print(f"      - {rec}")

    # ── Invalid category test ─────────────────────────────────
    safe_print("\n[6] Testing invalid category...")
    bad = agent.start_interview("quantum_physics")
    safe_print(f"    Error: {bad['error']}")

    # ── Quick Code Review interview ───────────────────────────
    safe_print("\n[7] Starting Code Review interview...")
    cr = agent.start_interview("code_review")
    safe_print(f"    Session    : {cr['session_id'][:8]}...")
    safe_print(f"    Question   : {cr['question'][:100]}...")

    safe_print("\n" + "=" * 70)
    safe_print("All tests passed successfully!")
    safe_print("=" * 70)
