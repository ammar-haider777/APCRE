# -*- coding: utf-8 -*-
import os

db_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\apcre_topics_db.py"

with open(db_path, "r", encoding="utf-8") as f:
    content = f.read()

# Python extension code to append
extension_code = """

# ═══════════════════════════════════════════════════════════════
# DYNAMIC ADDITIONS FOR EXPANDED KNOWLEDGE COVERAGE (5 TOPICS)
# ═══════════════════════════════════════════════════════════════

APCRE_TOPICS_ALIASES.update({
    "regex": "regex", "regular expression": "regex", "regular expressions": "regex",
    "memory_management": "memory_management", "memory management": "memory_management", "garbage collection": "memory_management",
    "backtracking": "backtracking", "backtrack": "backtracking", "constraint solving": "backtracking",
    "greedy_algorithms": "greedy_algorithms", "greedy": "greedy_algorithms", "greedy algorithm": "greedy_algorithms",
    "dynamic_programming": "dynamic_programming", "dp": "dynamic_programming", "memoization": "dynamic_programming", "tabulation": "dynamic_programming"
})

APCRE_TOPICS_DATABASE.update({
    "regex": {
        "title": "Regular Expressions (Regex) in Python",
        "category": "Python Fundamentals",
        "analogy": "A specialized search template or stencil used to find and extract matching patterns from a block of text.",
        "concept": "Regular Expressions (Regex) provide a powerful, domain-specific language for string pattern matching and manipulation using Python's built-in `re` module. It enables searching, splitting, replacing, and grouping characters.",
        "code": "import re\\n\\ntext = 'User login: ammar_haider, Email: ammar@uet.edu.pk, Date: 2026-05-26'\\n# Match email pattern\\nemail_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\\\.[a-zA-Z]{2,}'\\nemail = re.search(email_pattern, text)\\nif email:\\n    print(\\'Found email:\\', email.group(0))",
        "dry_run": "1. Compile search pattern \\'email_pattern\\'.\\n2. re.search scans \\'text\\' string from left to right.\\n3. Finds \\'ammar@uet.edu.pk\\', matches groups, returns Match object.",
        "complexity": "| Operation | Time Complexity | Space Complexity |\\n| :--- | :--- | :--- |\\n| Regex Compilation | $O(M)$ | $O(M)$ |\\n| Search / Match | $O(N)$ average | $O(1)$ |",
        "edge_cases": "* **ReDoS (Regex Denial of Service):** Catastrophic backtracking caused by nested quantifiers like `(a+)+`. Always keep quantifiers distinct!\\n* **Raw Strings:** Always use raw strings (`r\\'...\\'`) to prevent backslash escaping traps in pattern definitions."
    },
    "memory_management": {
        "title": "Python Memory Management & Garbage Collection",
        "category": "Python Fundamentals",
        "analogy": "A librarian who keeps track of how many people are reading a book, and automatically returns it to the shelf when no one is holding it.",
        "concept": "Python manages memory dynamically using reference counting and a cyclic garbage collector. Every object has a reference count, which increments when bound and decrements when out of scope. When it hits zero, Python automatically deallocates the memory.",
        "code": "import sys\\nimport gc\\n\\nclass Block:\\n    def __init__(self):\\n        self.data = [0] * 1000\\n\\n# Create reference\\nx = Block()\\nprint(\\'Reference count:\\', sys.getrefcount(x) - 1)  # Subtract temporary arg ref\\n# Force cycle collection\\ngc.collect()",
        "dry_run": "1. Object \\'Block()\\' allocated in heap, reference count set to 1.\\n2. sys.getrefcount increments count temporarily, then decrements.\\n3. GC runs cyclically to identify and collect unreachable self-referential containers.",
        "complexity": "| Mechanism | Time Complexity | Space Complexity |\\n| :--- | :--- | :--- |\\n| Reference Counting | $O(1)$ | $O(1)$ |\\n| Cyclic Garbage Collection | $O(N)$ during collections | $O(1)$ |",
        "edge_cases": "* **Circular References:** Two objects referencing each other (e.g., `a.b = b` and `b.a = a`) will never reach reference count 0. The cyclic Garbage Collector must detect and free them during collections."
    },
    "backtracking": {
        "title": "Backtracking & Constraint Satisfaction Algorithms",
        "category": "Data Structures & Algorithms",
        "analogy": "Solving a maze by taking a path until you hit a dead end, then backtracking to the last junction and trying the alternative path.",
        "concept": "Backtracking is a systematic, recursive search method that builds a candidate solution step-by-step and retracts (backtracks) as soon as it determines the candidate cannot lead to a valid solution. Used for N-Queens, Sudoku, and subset sums.",
        "code": "def solve_n_queens(n):\\n    def backtrack(r, cols, pos_diag, neg_diag):\\n        if r == n:\\n            return 1\\n        solutions = 0\\n        for c in range(n):\\n            if c in cols or (r + c) in pos_diag or (r - c) in neg_diag:\\n                continue\\n            cols.add(c); pos_diag.add(r + c); neg_diag.add(r - c)\\n            solutions += backtrack(r + 1, cols, pos_diag, neg_diag)\\n            cols.remove(c); pos_diag.remove(r + c); neg_diag.remove(r - c)\\n        return solutions\\n    return backtrack(0, set(), set(), set())\\n\\nprint(\\'N-Queens(4) solutions:\\', solve_n_queens(4))",
        "dry_run": "1. Start row 0. Try col 0.\\n2. Recursively try row 1. Flag collisions on diagonals/cols.\\n3. If invalid col, backtrack, remove column flag, try next col.",
        "complexity": "| Algorithm | Time Complexity | Space Complexity |\\n| :--- | :--- | :--- |\\n| N-Queens Solver | $O(N!)$ | $O(N)$ recursion depth |",
        "edge_cases": "* **Stack Overflow:** High recursion depths can trigger recursion limit errors. Scale maximum recursion limit if needed.\\n* **Branch Pruning:** Without intelligent branch pruning, complexity remains fully exponential."
    },
    "greedy_algorithms": {
        "title": "Greedy Optimization Algorithms",
        "category": "Data Structures & Algorithms",
        "analogy": "A shopper who always picks the most expensive item first to maximize value, or a driver who always turns towards the shortest street without looking at the whole map.",
        "concept": "Greedy algorithms make the locally optimal choice at each step in the hope that it will lead to a globally optimal solution. While fast, they do not guarantee global optimality except on specific problems like Fractional Knapsack, Huffman Coding, and Prim/Kruskal.",
        "code": "def fractional_knapsack(weights, values, capacity):\\n    # Calculate value density and sort\\n    items = sorted(zip(weights, values), key=lambda x: x[1]/x[0], reverse=True)\\n    total_val = 0.0\\n    for w, v in items:\\n        if capacity >= w:\\n            capacity -= w; total_val += v\\n        else:\\n            total_val += v * (capacity / w); break\\n    return total_val\\n\\nprint(\\'Knapsack Max Val:\\', fractional_knapsack([10, 20, 30], [60, 100, 120], 50))",
        "dry_run": "1. Sort items by value density: [6.0, 5.0, 4.0].\\n2. Insert item 1 (10kg, $60), cap becomes 40kg.\\n3. Insert item 2 (20kg, $100), cap becomes 20kg.\\n4. Take fraction (20/30) of item 3 ($80), Knapsack full.",
        "complexity": "| Algorithm | Time Complexity | Space Complexity |\\n| :--- | :--- | :--- |\\n| Greedy Knapsack | $O(N \\\\log N)$ sorting | $O(N)$ storage |",
        "edge_cases": "* **0/1 Knapsack Limitations:** Greedy choice fails for 0/1 knapsack where items cannot be divided. For 0/1 Knapsack, dynamic programming must be used instead."
    },
    "dynamic_programming": {
        "title": "Dynamic Programming (DP) & Overlapping Subproblems",
        "category": "Data Structures & Algorithms",
        "analogy": "Instead of writing down 1+1+1+1+1=5, writing down 5, and then when someone adds a +1, immediately answering 6 because you remembered the previous 5.",
        "concept": "Dynamic Programming (DP) is an algorithmic paradigm that solves complex problems by breaking them down into overlapping subproblems, solving each subproblem exactly once, and storing their solutions (memoization or tabulation) to prevent redundant work.",
        "code": "def coin_change(coins, amount):\\n    dp = [float(\\'inf\\')] * (amount + 1)\\n    dp[0] = 0\\n    for a in range(1, amount + 1):\\n        for c in coins:\\n            if a - c >= 0:\\n                dp[a] = min(dp[a], 1 + dp[a - c])\\n    return dp[amount] if dp[amount] != float(\\'inf\\') else -1\\n\\nprint(\\'Min Coins for 11:\\', coin_change([1, 2, 5], 11))",
        "dry_run": "1. Create dp array of size 12. dp[0]=0.\\n2. Outer loop amount 1 to 11. dp[1] checks coin 1 -> dp[1]=1.\\n3. dp[11] checks coin 5 -> min(dp[11], 1 + dp[6]) -> dp[11]=3.",
        "complexity": "| Algorithm | Time Complexity | Space Complexity |\\n| :--- | :--- | :--- |\\n| Tabulated DP Coin Change | $O(N \\\\times A)$ | $O(A)$ array space |",
        "edge_cases": "* **Memory Overflow:** Large state tables can exhaust RAM. Optimize spatial complexity by storing only the previous active state columns when possible."
    }
})

"""

# Check if already appended to avoid duplicates
if "DYNAMIC ADDITIONS FOR EXPANDED KNOWLEDGE" not in content:
    with open(db_path, "a", encoding="utf-8") as f:
        f.write(extension_code)
    print("Success: 5 new educational topics successfully appended to apcre_topics_db.py.")
else:
    print("Warning: Educational topics are already appended to apcre_topics_db.py.")
