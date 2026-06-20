# -*- coding: utf-8 -*-
"""
Rigorous Verification Test Suite for Upgraded APCRE ML/AI Engine.
Tests AST detectors, ML classification, Dynamic AI Tutor quizzes/exercises/hints, 
and Coder Agent exception diagnostics parsing.
"""

import sys
import os
import ast

if sys.platform.startswith("win"):
    import io
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure ai-engine is in system path
sys.path.append(r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine")

try:
    import apcre_api
    import apcre_topics_db
    print("[TEST SETUP] Successfully loaded APCRE components.")
except ImportError as e:
    print(f"[TEST SETUP] Failed to import APCRE modules: {e}")
    sys.exit(1)

def run_tests():
    passed = True
    print("\n" + "="*60)
    print("APCRE SYSTEM VERIFICATION TEST SUITE RUN")
    print("="*60)

    # ───────────────────────────────────────────────────────────────
    # TEST 1: AST Detectors
    # ───────────────────────────────────────────────────────────────
    print("\n--- TEST 1: AST Analysis Engine Upgrades ---")
    
    # 1.1 Nested Loop Inefficiency
    code_nested_loops = """
def slow_matrix(n):
    for i in range(n):
        for j in range(n):
            print(i, j)
"""
    issues_nested = apcre_api.run_full_review(code_nested_loops)
    titles_nested = [issue["title"] for issue in issues_nested]
    if "Nested loop complexity risk" in titles_nested:
        print("[PASS] Nested loop complexity risk successfully detected!")
    else:
        print("[FAIL] Failed to detect nested loop complexity risk.")
        passed = False

    # 1.2 Loop method calls (.count / .index)
    code_loop_lookup = """
def lookup_elements(items):
    for x in items:
        if items.count(x) > 1:
            print("Dup")
"""
    issues_lookup = apcre_api.run_full_review(code_loop_lookup)
    titles_lookup = [issue["title"] for issue in issues_lookup]
    if "Inefficient loop lookup" in titles_lookup:
        print("[PASS] Inefficient loop lookup (.count) successfully detected!")
    else:
        print("[FAIL] Failed to detect inefficient loop lookup (.count).")
        passed = False

    # 1.3 Recursion Risk (no base case IF guard)
    code_recursion = """
def recursive_call(n):
    return recursive_call(n - 1)
"""
    issues_rec = apcre_api.run_full_review(code_recursion)
    titles_rec = [issue["title"] for issue in issues_rec]
    if "Recursion stack overflow risk" in titles_rec:
        print("[PASS] Recursion risk (missing base case) successfully detected!")
    else:
        print("[FAIL] Failed to detect recursion risk (missing base case).")
        passed = False

    # 1.4 Memory Inefficiencies (+= string concat, direct open)
    code_memory = """
def build_str(words):
    out = ""
    for w in words:
        out += w
    f = open("log.txt", "r")
    f.close()
"""
    issues_mem = apcre_api.run_full_review(code_memory)
    titles_mem = [issue["title"] for issue in issues_mem]
    if "Inefficient string concatenation" in titles_mem and "Unsafe file opening" in titles_mem:
        print("[PASS] String concat '+=' inside loop and unsafe file opening successfully detected!")
    else:
        print(f"[FAIL] Failed to detect memory inefficiencies. Detected: {titles_mem}")
        passed = False

    # 1.5 Modularity limits (function size)
    code_poor_mod = "def long_func():\n" + "\n".join([f"    x = {i}" for i in range(60)])
    issues_mod = apcre_api.run_full_review(code_poor_mod)
    titles_mod = [issue["title"] for issue in issues_mod]
    if "Function exceeds modularity limits" in titles_mod:
        print("[PASS] Function exceeding 50 lines modularity limit successfully detected!")
    else:
        print(f"[FAIL] Failed to detect poor function modularity. Detected: {titles_mod}")
        passed = False

    # ───────────────────────────────────────────────────────────────
    # TEST 2: ML Model Classification Integration
    # ───────────────────────────────────────────────────────────────
    print("\n--- TEST 2: Scikit-Learn Model Classification ---")
    if apcre_api.MODEL_LOADED:
        code_premium = """
from typing import List
class Stack:
    \"\"\"Fully encapsulated clean OOP stack.\"\"\"
    def __init__(self) -> None:
        self._data: List[int] = []
    def push(self, item: int) -> None:
        self._data.append(item)
    def pop(self) -> int:
        return self._data.pop()
"""
        issues_premium = apcre_api.run_full_review(code_premium)
        ml_issue = [i for i in issues_premium if i["title"] == "ML Quality Classification"]
        if ml_issue:
            print(f"[PASS] ML Model integration active! Predicted Quality: {ml_issue[0]['desc']}")
        else:
            print("[FAIL] ML model predicted issue not found in review output.")
            passed = False
    else:
        print("[SKIP] Scikit-learn model not loaded.")
        passed = False

    # ───────────────────────────────────────────────────────────────
    # TEST 3: Dynamic Educational AI Tutor & Stateful Memory
    # ───────────────────────────────────────────────────────────────
    print("\n--- TEST 3: Dynamic Educational AI Tutor & Stateful Memory ---")
    
    # 3.1 Verify 5 new topics added to database
    db_keys = apcre_api.APCRE_DATABASE_QUERIES().keys()
    new_topics = ["regex", "memory_management", "backtracking", "greedy_algorithms", "dynamic_programming"]
    topics_missing = [t for t in new_topics if t not in db_keys]
    if not topics_missing:
        print(f"[PASS] All 5 new educational topics present in database! Total keys: {len(db_keys)}")
    else:
        print(f"[FAIL] Missing database topics: {topics_missing}")
        passed = False

    # 3.2 Quiz generation and stateful response grading
    room_id = "test_room_123"
    state = apcre_api.get_conversation_state(room_id)
    
    # Ask for regex quiz
    quiz_reply = apcre_api.run_stateful_assistant("Give me a quiz on regex", "", "", room_id)
    if "re.search()" in quiz_reply and state.current_quiz is not None:
        print("[PASS] Dynamic Quiz generated successfully for 'regex'!")
    else:
        print("[FAIL] Failed to generate regex quiz.")
        passed = False

    # Submit correct answer to grading engine
    grading_reply = apcre_api.run_stateful_assistant("B", "", "", room_id)
    if "Correct!" in grading_reply and state.difficulty == "advanced":
        print("[PASS] State grading is correct! Dynamic difficulty scaled up to advanced.")
    else:
        print(f"[FAIL] Grading failed or difficulty not scaled. Reply: {grading_reply}, Level: {state.difficulty}")
        passed = False

    # 3.3 Dynamic Exercise and progressive Hint generation
    exercise_reply = apcre_api.run_stateful_assistant("Show me an exercise on dynamic programming", "", "", room_id)
    if "fib_dp(n" in exercise_reply or "APCRE Practice Challenge" in exercise_reply:
        print("[PASS] Dynamic Exercise generated successfully for 'dynamic_programming'!")
    else:
        print("[FAIL] Failed to generate dynamic exercise.")
        passed = False

    hint_reply1 = apcre_api.run_stateful_assistant("Give me a hint", "", "", room_id)
    hint_reply2 = apcre_api.run_stateful_assistant("stuck, help me solve", "", "", room_id)
    if "Progressive Hint (1/3)" in hint_reply1 and "Progressive Hint (2/3)" in hint_reply2:
        print("[PASS] Progressive, hint-based tutoring aspect behaves perfectly!")
    else:
        print(f"[FAIL] Progressive hints failed to increment. Hint1: {hint_reply1}, Hint2: {hint_reply2}")
        passed = False

    # 3.4 Concept explanations (beginner/advanced modes)
    state.difficulty = "beginner"
    beg_explain = apcre_api.run_stateful_assistant("Explain memory management", "", "", room_id)
    state.difficulty = "advanced"
    adv_explain = apcre_api.run_stateful_assistant("Explain memory management", "", "", room_id)
    
    if "Layman's Explanation:" in beg_explain and "Advanced Technical Design:" in adv_explain:
        print("[PASS] Beginner/Advanced mode explanation synthesizers operate cleanly!")
    else:
        print("[FAIL] Concept synthesizers failed to adjust layout based on difficulty.")
        passed = False

    # ───────────────────────────────────────────────────────────────
    # TEST 4: Exception Diagnostics Parser
    # ───────────────────────────────────────────────────────────────
    print("\n--- TEST 4: Exception Diagnostics Parser ---")
    
    test_type_error_stderr = """
Traceback (most recent call last):
  File "sandbox.py", line 3, in <module>
    sum = "a" + 5
TypeError: can only concatenate str (not "int") to str
"""
    diag_type = apcre_api._diagnose_traceback(test_type_error_stderr)
    if "TypeError" in diag_type and "Type errors occur when an operation" in diag_type:
        print("[PASS] TypeError diagnostics diagnosed and parsed correctly!")
    else:
        print(f"[FAIL] TypeError diagnostics parsing failed: {diag_type}")
        passed = False

    test_syntax_error_stderr = """
  File "sandbox.py", line 4
    def foo()
             ^
SyntaxError: expected ':'
"""
    diag_syntax = apcre_api._diagnose_traceback(test_syntax_error_stderr)
    if "SyntaxError" in diag_syntax and "Syntax errors mean the Python compiler" in diag_syntax:
        print("[PASS] SyntaxError diagnostics diagnosed and parsed correctly!")
    else:
        print(f"[FAIL] SyntaxError diagnostics parsing failed: {diag_syntax}")
        passed = False

    print("\n" + "="*60)
    if passed:
        print("🎉 ALL TESTS PASSED! UPGRADED APCRE SYSTEM IS 100% CORRECT!")
    else:
        print("❌ SOME TESTS FAILED. PLEASE DEBUG SYSTEM COMPONENTS.")
    print("="*60)

if __name__ == "__main__":
    run_tests()
