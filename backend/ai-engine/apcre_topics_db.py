"""
APCRE AI Engine - Highly Intelligent & Robust Production-Quality Flask API
Specialized in Python programming, AST-based code review, self-correcting Coder Agent,
and stateful, multi-turn educational tutoring. Runs 100% locally and privately.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import ast
import json
import re
import os
import sys
import pickle
import textwrap
import subprocess
import datetime
from collections import Counter
import urllib.request
import urllib.error

# ═══════════════════════════════════════════════════════════════
# Flask App Setup
# ═══════════════════════════════════════════════════════════════
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ═══════════════════════════════════════════════════════════════
# ML Model Loading
# ═══════════════════════════════════════════════════════════════
MODEL_LOADED = False
vectorizer = None
model = None

try:
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml_model.pkl")
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            data = pickle.load(f)
        if isinstance(data, (tuple, list)) and len(data) == 2:
            vectorizer, model = data
            MODEL_LOADED = True
            print("[APCRE] ML model loaded successfully.")
        else:
            print("[APCRE] WARNING: ml_model.pkl has unexpected format.")
    else:
        print("[APCRE] WARNING: ml_model.pkl not found. Training must be run first.")
except Exception as e:
    print(f"[APCRE] WARNING: Could not load ml_model.pkl: {e}")
    print("[APCRE] ML classification disabled; using rules only.")

# ═══════════════════════════════════════════════════════════════
# Conversational State Manager (Multi-Turn Context & Topic Switching)
# ═══════════════════════════════════════════════════════════════

class ConversationState:
    """Stateful memory for individual user conversations."""
    def __init__(self):
        self.current_topic = None
        self.previous_topic = None
        self.difficulty = "intermediate"  # beginner, intermediate, advanced
        self.turns = 0
        self.history = []  # list of (user_msg, assistant_reply)
        self.code_context = ""

SESSION_MEMORY = {}

def get_conversation_state(room_id: str) -> ConversationState:
    key = room_id or "global"
    if key not in SESSION_MEMORY:
        SESSION_MEMORY[key] = ConversationState()
    return SESSION_MEMORY[key]

# ═══════════════════════════════════════════════════════════════
# Comprehensive Lexical Mapping & Alias Catalog (All 80+ Topics)
# ═══════════════════════════════════════════════════════════════

APCRE_TOPICS_ALIASES = {
    # 1. Built-in Data Structures
    "list": "list", "lists": "list",
    "tuple": "tuple", "tuples": "tuple",
    "set": "set", "sets": "set",
    "frozenset": "frozenset", "frozensets": "frozenset", "froze set": "frozenset",
    "dict": "dict", "dictioanry": "dict", "dictionaries": "dict", "dictionary": "dict",
    "string": "string", "strings": "string",
    "array": "array", "arrays": "array",
    "bytearray": "bytearray", "bytearrays": "bytearray", "byte array": "bytearray",
    "deque": "deque", "deques": "deque", "double ended queue": "deque",
    "heap": "heap", "heaps": "heap",
    "queue": "queue_simple", "queues": "queue_simple",
    "priority_queue": "priority_queue", "priority queue": "priority_queue", "priority queues": "priority_queue",
    
    # 2. Linear Data Structures
    "dynamic_array": "dynamic_array", "dynamic array": "dynamic_array", "dynamic arrays": "dynamic_array",
    "singly_linked_list": "singly_linked_list", "singly linked list": "singly_linked_list",
    "doubly_linked_list": "doubly_linked_list", "doubly linked list": "doubly_linked_list",
    "circular_linked_list": "circular_linked_list", "circular linked list": "circular_linked_list",
    "stack": "stack", "stacks": "stack",
    "simple_queue": "simple_queue", "simple queue": "simple_queue",
    "circular_queue": "circular_queue", "circular queue": "circular_queue",
    
    # 3. Non-Linear Data Structures
    "binary_tree": "binary_tree", "binary tree": "binary_tree", "binary trees": "binary_tree",
    "bst": "bst", "binary search tree": "bst", "binary search trees": "bst",
    "avl_tree": "avl_tree", "avl tree": "avl_tree", "avl": "avl_tree",
    "segment_tree": "segment_tree", "segment tree": "segment_tree",
    "fenwick_tree": "fenwick_tree", "fenwick tree": "fenwick_tree", "binary indexed tree": "fenwick_tree",
    "trie": "trie", "tries": "trie",
    "heap_tree": "heap_tree", "heap tree": "heap_tree",
    "b_tree": "b_tree", "b tree": "b_tree", "btree": "b_tree",
    "red_black_tree": "red_black_tree", "red black tree": "red_black_tree", "red-black": "red_black_tree",
    "n_ary_tree": "n_ary_tree", "n ary tree": "n_ary_tree", "n-ary tree": "n_ary_tree",
    "directed_graph": "directed_graph", "directed graph": "directed_graph",
    "undirected_graph": "undirected_graph", "undirected graph": "undirected_graph",
    "weighted_graph": "weighted_graph", "weighted graph": "weighted_graph",
    "unweighted_graph": "unweighted_graph", "unweighted graph": "unweighted_graph",
    "cyclic_graph": "cyclic_graph", "cyclic graph": "cyclic_graph",
    "acyclic_graph": "acyclic_graph", "acyclic graph": "acyclic_graph",
    "dag": "dag", "directed acyclic graph": "dag",
    "hash_table": "hash_table", "hash table": "hash_table", "hashmap": "hash_table", "hash map": "hash_table",
    "hash_set": "hash_set", "hash set": "hash_set", "hashset": "hash_set",
    
    # 4. Advanced Data Structures
    "suffix_array": "suffix_array", "suffix array": "suffix_array",
    "suffix_tree": "suffix_tree", "suffix tree": "suffix_tree",
    "disjoint_set": "disjoint_set", "disjoint set": "disjoint_set", "union find": "disjoint_set", "union_find": "disjoint_set",
    "bloom_filter": "bloom_filter", "bloom filter": "bloom_filter",
    "sparse_table": "sparse_table", "sparse table": "sparse_table",
    "skip_list": "skip_list", "skip list": "skip_list",
    "lru_cache": "lru_cache", "lru cache": "lru_cache", "lru": "lru_cache",
    "monotonic_stack": "monotonic_stack", "monotonic stack": "monotonic_stack",
    "monotonic_queue": "monotonic_queue", "monotonic queue": "monotonic_queue",
    
    # 5. Searching Algorithms
    "linear_search": "linear_search", "linear search": "linear_search",
    "binary_search": "binary_search", "binary search": "binary_search",
    "jump_search": "jump_search", "jump search": "jump_search",
    "interpolation_search": "interpolation_search", "interpolation search": "interpolation_search",
    "exponential_search": "exponential_search", "exponential search": "exponential_search",
    
    # 6. Sorting Algorithms
    "bubble_sort": "bubble_sort", "bubble sort": "bubble_sort",
    "selection_sort": "selection_sort", "selection sort": "selection_sort",
    "insertion_sort": "insertion_sort", "insertion sort": "insertion_sort",
    "merge_sort": "merge_sort", "merge sort": "merge_sort",
    "quick_sort": "quick_sort", "quick sort": "quick_sort",
    "heap_sort": "heap_sort", "heap sort": "heap_sort",
    "counting_sort": "counting_sort", "counting sort": "counting_sort",
    "radix_sort": "radix_sort", "radix sort": "radix_sort",
    "bucket_sort": "bucket_sort", "bucket sort": "bucket_sort",
    
    # 7. Recursion & Backtracking
    "recursive_thinking": "recursive_thinking", "recursive thinking": "recursive_thinking", "recursion": "recursive_thinking",
    "base_case": "base_case", "base case": "base_case", "base cases": "base_case",
    "n_queens": "n_queens", "n queens": "n_queens", "n-queens": "n_queens",
    "sudoku_solver": "sudoku_solver", "sudoku solver": "sudoku_solver", "sudoku": "sudoku_solver",
    "permutations": "permutations", "permutation": "permutations",
    "combinations": "combinations", "combination": "combinations",
    
    # 8. Graph Algorithms
    "bfs": "bfs", "breadth first search": "bfs",
    "dfs": "dfs", "depth first search": "dfs",
    "dijkstra": "dijkstra", "dijkstras": "dijkstra",
    "bellman_ford": "bellman_ford", "bellman ford": "bellman_ford", "bellman-ford": "bellman_ford",
    "floyd_warshall": "floyd_warshall", "floyd warshall": "floyd_warshall", "floyd-warshall": "floyd_warshall",
    "kruskal": "kruskal", "kruskals": "kruskal",
    "prim": "prim", "prims": "prim",
    "topological_sort": "topological_sort", "topological sort": "topological_sort",
    "cycle_detection": "cycle_detection", "cycle detection": "cycle_detection",
    "shortest_path": "shortest_path", "shortest path": "shortest_path",
    
    # 9. Dynamic Programming
    "memoization": "memoization", "memoized": "memoization",
    "tabulation": "tabulation", "tabulated": "tabulation", "tabulate": "tabulation",
    "knapsack": "knapsack",
    "lcs": "lcs", "longest common subsequence": "lcs",
    "lis": "lis", "longest increasing subsequence": "lis",
    "coin_change": "coin_change", "coin change": "coin_change",
    "matrix_chain": "matrix_chain", "matrix chain": "matrix_chain", "matrix chain multiplication": "matrix_chain",
    
    # 10. Complexity Analysis
    "time_complexity": "time_complexity", "time complexity": "time_complexity",
    "space_complexity": "space_complexity", "space complexity": "space_complexity",
    "big_o": "big_o", "big o": "big_o", "big-o": "big_o",
    "big_theta": "big_theta", "big theta": "big_theta",
    "big_omega": "big_omega", "big omega": "big_omega",
    
    # 11. OOP Core
    "class": "class", "classes": "class",
    "object": "object", "objects": "object",
    "attribute": "attribute", "attributes": "attribute",
    "method": "method", "methods": "method",
    "constructor": "constructor", "constructors": "constructor",
    "destructor": "destructor", "destructors": "destructor",
    "self_keyword": "self_keyword", "self keyword": "self_keyword", "self": "self_keyword",
    "encapsulation": "encapsulation",
    "abstraction": "abstraction",
    "inheritance": "inheritance",
    "polymorphism": "polymorphism",
    
    # 12. OOP Inheritance Types
    "single_inheritance": "single_inheritance", "single inheritance": "single_inheritance",
    "multiple_inheritance": "multiple_inheritance", "multiple inheritance": "multiple_inheritance",
    "multilevel_inheritance": "multilevel_inheritance", "multilevel inheritance": "multilevel_inheritance",
    "hierarchical_inheritance": "hierarchical_inheritance", "hierarchical inheritance": "hierarchical_inheritance",
    "hybrid_inheritance": "hybrid_inheritance", "hybrid inheritance": "hybrid_inheritance",
    
    # 13. Polymorphism Types
    "method_overriding": "method_overriding", "method overriding": "method_overriding",
    "method_overloading": "method_overloading", "method overloading": "method_overloading",
    "operator_overloading": "operator_overloading", "operator overloading": "operator_overloading",
    "duck_typing": "duck_typing", "duck typing": "duck_typing",
    
    # 14. Advanced OOP
    "abstract_class": "abstract_class", "abstract class": "abstract_class",
    "interface": "interface", "interfaces": "interface",
    "decorator": "decorator", "decorators": "decorator",
    "property_decorator": "property_decorator", "property decorator": "property_decorator",
    "static_method": "static_method", "static method": "static_method",
    "class_method": "class_method", "class method": "class_method",
    "magic_method": "magic_method", "magic method": "magic_method", "dunder method": "magic_method", "dunder": "magic_method",
    "composition": "composition",
    "aggregation": "aggregation",
    "association": "association",
    "mro": "mro", "method resolution order": "mro",
    "solid": "solid", "solid principles": "solid",
    "singleton": "singleton",
    "factory": "factory",
    "observer": "observer",
    "strategy": "strategy",
    "mvc": "mvc",
    "adapter": "adapter",
    "builder": "builder",
    
    # 15. Programming Fundamentals
    "variable": "variable", "variables": "variable",
    "data_type": "data_type", "data type": "data_type", "data types": "data_type",
    "type_casting": "type_casting", "type casting": "type_casting", "typecast": "type_casting",
    "io": "io", "input output": "io", "input/output": "io",
    "operator": "operator", "operators": "operator",
    "conditional": "conditional", "conditionals": "conditional", "conditional statement": "conditional", "conditional statements": "conditional",
    "loop": "loop", "loops": "loop",
    "function": "function", "functions": "function",
    "lambda": "lambda", "lambda function": "lambda", "lambda functions": "lambda",
    "comprehension": "comprehension", "comprehensions": "comprehension", "list comprehension": "comprehension", "dict comprehension": "comprehension",
    "exception": "exception", "exceptions": "exception", "exception handling": "exception",
    "module": "module", "modules": "module", "package": "module", "packages": "module",
    "file_handling": "file_handling", "file handling": "file_handling",
    "iterator": "iterator", "iterators": "iterator",
    "generator": "generator", "generators": "generator",
    "context_manager": "context_manager", "context manager": "context_manager",
    "venv": "venv", "virtual environment": "venv", "virtual environments": "venv",
    "async_prog": "async_prog", "async": "async_prog", "asyncio": "async_prog", "async programming": "async_prog",
    "multithreading": "multithreading", "threading": "multithreading",
    "multiprocessing": "multiprocessing"
}

# ═══════════════════════════════════════════════════════════════
# Dynamic Synthesis Content Database
# ═══════════════════════════════════════════════════════════════

APCRE_TOPICS_DATABASE = {
    # 1. Built-in Data Structures
    "list": {
        "title": "Python Lists",
        "category": "Built-in Data Structures",
        "analogy": "A expandable shopping list where items are kept in a specific order and you can write, scratch off, or insert items anywhere.",
        "concept": "Python Lists are mutable, ordered, dynamic arrays that can hold heterogeneous elements. Under the hood, they are implemented as contiguous arrays of references to other Python objects.",
        "code": textwrap.dedent("""
            # Creating and manipulating a dynamic list
            fruits = ["apple", "banana"]
            fruits.append("cherry")      # O(1) amortized insertion at tail
            fruits.insert(1, "orange")   # O(N) insertion requiring index shift
            popped = fruits.pop()        # O(1) removal from tail
            print("Fruits:", fruits)
            print("Popped item:", popped)
        """).strip(),
        "dry_run": "1. Initialize `fruits` with references to 'apple' and 'banana'.\n2. `append('cherry')` maps to contiguous slot, list size expands.\n3. `insert(1, 'orange')` pushes 'banana' and 'cherry' forward in memory by 1 slot, inserts 'orange' at index 1.\n4. `pop()` returns 'cherry' and frees slot.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Append / Pop (tail) | $O(1)$ |\n| Insert / Delete (middle) | $O(N)$ |\n| Index Lookup `lst[i]` | $O(1)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **IndexError:** Accessing `lst[len(lst)]` throws index out of range. Remember Python lists are 0-indexed!\n• **Shallow Copy:** `lst2 = lst1` creates a reference copy, modifying `lst2` affects `lst1`. Use `lst1.copy()` for a shallow copy."
    },
    "tuple": {
        "title": "Python Tuples",
        "category": "Built-in Data Structures",
        "analogy": "A sealed, laminated certificate. Once the fields are printed, they can never be altered or erased.",
        "concept": "Tuples are immutable, ordered collections. Because they are immutable, they are hashable (can be used as dictionary keys) and are highly memory-efficient compared to lists.",
        "code": textwrap.dedent("""
            # Creating tuples and using them as hash keys
            coordinates = (40.7128, -74.0060)
            loc_dict = {coordinates: "New York"}
            print("Coordinates:", coordinates)
            print("Location:", loc_dict[coordinates])
        """).strip(),
        "dry_run": "1. Coordinates tuple is allocated contiguous, fixed-size memory.\n2. Hash calculation is executed on tuple elements.\n3. Key-value mapped in dictionary table.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Index Lookup `tup[i]` | $O(1)$ |\n| Tuple Allocation | $O(N)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Single-element tuple:** Creating `t = (5)` results in an integer. You must include a trailing comma: `t = (5,)`.\n• **Nested Mutability:** If a tuple contains a list, e.g. `t = (1, [2, 3])`, the list can still be modified!"
    },
    "set": {
        "title": "Python Sets",
        "category": "Built-in Data Structures",
        "analogy": "A bag of labeled lottery balls. No duplicates allowed, and the order they roll around is completely random.",
        "concept": "Sets are mutable, unordered collections of unique, hashable elements. They are implemented under the hood as Hash Tables, enabling extremely fast membership testing.",
        "code": textwrap.dedent("""
            # Set operations for uniqueness and relationships
            primes = {2, 3, 5, 7}
            primes.add(11)                  # O(1) insertion
            print("Is 5 prime?", 5 in primes) # O(1) membership lookup!
            
            evens = {2, 4, 6, 8}
            print("Intersection:", primes & evens) # Prime evens: {2}
        """).strip(),
        "dry_run": "1. Primer set allocates hash buckets.\n2. `add(11)` hashes 11, places in matching slot.\n3. Membership check `5 in primes` hashes 5, searches bucket slot instantly.",
        "complexity": "| Operation | Average Case | Worst Case |\n| :--- | :--- | :--- |\n| Add / Remove | $O(1)$ | $O(N)$ (hash collision) |\n| Membership check | $O(1)$ | $O(N)$ |\n| Space Complexity | $O(N)$ | $O(N)$ |",
        "edge_cases": "• **Unhashable elements:** Adding a list or dictionary to a set raises `TypeError: unhashable type`.\n• **Empty set notation:** `s = {}` creates an empty dictionary! Use `s = set()`."
    },
    "frozenset": {
        "title": "Python Frozensets",
        "category": "Built-in Data Structures",
        "analogy": "An un-modifiable set of locked values. You can read them, check if they exist, but never add or remove any.",
        "concept": "Frozensets are immutable sets. They provide all standard mathematical set operations (union, intersection) but are hashable, meaning they can be nested inside other sets or used as dictionary keys.",
        "code": textwrap.dedent("""
            # Frozenset used as dictionary keys
            fs = frozenset([1, 2, 3])
            d = {fs: "Locked ID"}
            print("Frozenset:", fs)
            print("Dictionary lookup:", d[fs])
        """).strip(),
        "dry_run": "1. Frozenset allocates static hash table layout.\n2. Elements are verified as immutable.\n3. Safe insertion as key in dictionary table.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Membership test | $O(1)$ |\n| Union / Intersection | $O(S + T)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Modification attempt:** Calling `fs.add(4)` throws `AttributeError: 'frozenset' object has no attribute 'add'`."
    },
    "dict": {
        "title": "Python Dictionaries",
        "category": "Built-in Data Structures",
        "analogy": "A physical phonebook where you open a unique contact name to instantly find their phone number without flipping through every page.",
        "concept": "Dictionaries are mutable, ordered collections of key-value pairs (ordered since Python 3.6). They are highly optimized hash tables. Keys must be unique and hashable.",
        "code": textwrap.dedent("""
            # Dictionary hashing lookup
            user = {"username": "ammar", "role": "admin"}
            user["email"] = "ammar@example.com"  # O(1) insert
            print("Role:", user.get("role"))    # O(1) lookup
        """).strip(),
        "dry_run": "1. Instantiates hash table mapping hashes of strings to values.\n2. `user['email']` hashes 'email', binds value to index.\n3. `get('role')` returns value at key hash bucket.",
        "complexity": "| Operation | Average Case | Worst Case |\n| :--- | :--- | :--- |\n| Get / Set / Delete | $O(1)$ | $O(N)$ |\n| Iteration | $O(N)$ | $O(N)$ |\n| Space Complexity | $O(N)$ | $O(N)$ |",
        "edge_cases": "• **KeyError:** Querying `user['nonexistent']` directly throws KeyError. Guard with `.get('key', default)`.\n• **Mutable Keys:** Attempting to use a list as a key raises `TypeError: unhashable type`."
    },
    "string": {
        "title": "Python Strings",
        "category": "Built-in Data Structures",
        "analogy": "A printed string of text in a book. You can read it, copy parts of it, but you can never rewrite characters directly on the page.",
        "concept": "Strings are immutable sequences of Unicode characters. Any operation that modifies a string (like concatenation or replacement) creates a new string object in memory.",
        "code": textwrap.dedent("""
            # String immutability and slicing
            text = "Python Programming"
            sliced = text[:6]         # O(K) slice copy: "Python"
            replaced = text.replace("Python", "APCRE") # Creates a new string!
            print("Original:", text)
            print("Replaced:", replaced)
        """).strip(),
        "dry_run": "1. Allocates string object 'Python Programming'.\n2. Slicing copies characters from index 0 to 5, allocates new string object 'Python'.\n3. Replacement copies string data, constructs new object.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Concatenation `s1 + s2` | $O(N + M)$ |\n| Slicing `s[i:j]` | $O(J - I)$ |\n| Search `pattern in string` | $O(N)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **String Concatenation Loop:** Running `s += char` in a loop runs in $O(N^2)$ due to constant memory re-allocation. Use `''.join(list_of_chars)` for optimal $O(N)$ performance."
    },
    "array": {
        "title": "Python Arrays",
        "category": "Built-in Data Structures",
        "analogy": "A uniform egg carton. It can only hold eggs (same data type), and it has a fixed size.",
        "concept": "Python's `array` module provides memory-efficient arrays of basic values (integers, floats) restricted to a single type code. They consume significantly less memory than standard heterogeneous lists.",
        "code": textwrap.dedent("""
            import array
            # Create array of signed integers ('i')
            numbers = array.array('i', [10, 20, 30])
            numbers.append(40)  # O(1) amortized
            print("Array:", numbers)
        """).strip(),
        "dry_run": "1. Allocates homogeneous, contiguous block of raw 4-byte integers.\n2. `append(40)` maps 40 directly to the next contiguous block.\n3. Index lookup queries mathematical offset in memory.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Append / Pop | $O(1)$ amortized |\n| Index Lookup `arr[i]` | $O(1)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Type Mismatch:** Appending a float to an integer array `numbers.append(5.5)` throws `TypeError: integer argument expected, got float`."
    },
    "bytearray": {
        "title": "Python Byte Arrays",
        "category": "Built-in Data Structures",
        "analogy": "A digital film reel. Each cell contains a raw pixel value (byte) that you can rewrite or splice in real time.",
        "concept": "A `bytearray` is a mutable sequence of integers in the range 0 <= x < 256. It is ideal for binary data manipulation, network sockets, and image/file decoding.",
        "code": textwrap.dedent("""
            # Manipulating raw binary bytes
            binary_data = bytearray(b"Hello")
            binary_data[0] = 0x4A  # ASCII 'J'
            print("Modified Byte Array:", binary_data) # b"Jello"
        """).strip(),
        "dry_run": "1. Binds raw mutable array of 8-bit integers representing ASCII values.\n2. Overwrites index 0 with byte representation of 'J' (0x4A).\n3. Renders byte sequence.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Get / Set index | $O(1)$ |\n| Append / Pop | $O(1)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Out of Range:** Assigning a value outside 0-255 (e.g. `binary_data[0] = 300`) raises `ValueError: byte must be in range(0, 256)`."
    },
    "deque": {
        "title": "Double-Ended Queues (Deques)",
        "category": "Built-in Data Structures",
        "analogy": "A double-ended train tunnel. Cars can enter or exit from both the left end or the right end with ease.",
        "concept": "Deques (`collections.deque`) are double-ended queues implemented as doubly linked lists of memory blocks. They support fast, thread-safe, $O(1)$ appends and pops from both sides.",
        "code": textwrap.dedent("""
            from collections import deque
            dq = deque(["task2", "task3"])
            dq.append("task4")     # O(1) right append
            dq.appendleft("task1") # O(1) left append!
            print("Deque State:", dq)
        """).strip(),
        "dry_run": "1. Instantiates double-ended blocks linked bidirectionally.\n2. `append('task4')` updates right head pointer.\n3. `appendleft('task1')` updates left head pointer instantly in $O(1)$ without shifting arrays.",
        "complexity": "| Operation | Deque | Standard List |\n| :--- | :--- | :--- |\n| Append Left | $O(1)$ | $O(N)$ |\n| Append Right | $O(1)$ | $O(1)$ (amortized) |\n| Index Lookup | $O(N)$ (slow) | $O(1)$ (fast) |",
        "edge_cases": "• **Maxlen Limit:** You can set a capacity: `deque(maxlen=3)`. Appending a fourth item will automatically discard the opposite end item to maintain size!"
    },
    "heap": {
        "title": "Min-Heaps (Priority Queue)",
        "category": "Built-in Data Structures",
        "analogy": "A corporate escalation ladder where the employee with the lowest priority value (highest urgency) is always at the top of the meeting queue.",
        "concept": "Heaps are binary trees where parent nodes are always smaller than or equal to their children (Min-Heap). Python's `heapq` module implements min-heaps using standard 0-indexed lists.",
        "code": textwrap.dedent("""
            import heapq
            data = [5, 1, 9, 3]
            heapq.heapify(data)       # In-place heap construction in O(N)
            heapq.heappush(data, 2)   # O(log N) push
            smallest = heapq.heappop(data) # O(log N) pop smallest (1)
            print("Heap:", data)
            print("Smallest extracted:", smallest)
        """).strip(),
        "dry_run": "1. `heapify` transforms list to heap layout.\n2. `heappush(2)` appends 2 to end, runs bubble-up comparisons to place it.\n3. `heappop()` replaces root with last item, runs bubble-down to restore heap property.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Heapify list | $O(N)$ |\n| Push / Pop | $O(\log N)$ |\n| Peek Minimum | $O(1)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Empty Heap Pop:** Calling `heapq.heappop([])` raises `IndexError: index out of range`."
    },
    "queue_simple": {
        "title": "Simple Queues (FIFO)",
        "category": "Built-in Data Structures",
        "analogy": "A checkout line at a store: the first customer to join the line is served first.",
        "concept": "A Queue is a linear LIFO structure. Python provides the thread-safe `queue.Queue` class, which handles locking natively, making it ideal for multi-threaded producer-consumer patterns.",
        "code": textwrap.dedent("""
            import queue
            q = queue.Queue(maxsize=3)
            q.put("user1")    # Enqueue (blocking if full)
            q.put("user2")
            first = q.get()   # Dequeue (blocking if empty)
            print("Served:", first)
        """).strip(),
        "dry_run": "1. `Queue` initializes condition variables and lock gates.\n2. `put` acquires lock, appends to internal deque, releases lock.\n3. `get` pops from left of deque safely.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Enqueue (`put`) | $O(1)$ |\n| Dequeue (`get`) | $O(1)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Blocking Put:** Putting into a full queue blocks the thread indefinitely. Use `put_nowait()` or set a `timeout` parameter to avoid lock-ups."
    },
    "priority_queue": {
        "title": "Priority Queues",
        "category": "Built-in Data Structures",
        "analogy": "An emergency room triage. The patient arriving with a severe condition is seen immediately, bypassing less critical patients who arrived earlier.",
        "concept": "Priority Queues store elements with an associated priority score. Elements are dequeued in order of their priority level. Implemented internally via Min-Heaps.",
        "code": textwrap.dedent("""
            from queue import PriorityQueue
            pq = PriorityQueue()
            # Insert tuple: (priority_score, value)
            pq.put((2, "Study Stacks"))
            pq.put((1, "Fix Critical Bug"))
            pq.put((3, "Format Logs"))
            
            # Dequeues smallest priority score first
            highest_priority = pq.get()
            print("Next Task:", highest_priority[1]) # "Fix Critical Bug"
        """).strip(),
        "dry_run": "1. Instantiates Min-Heap priority queue.\n2. `put((1, 'Fix Critical Bug'))` pushes tuple into heap, sorting by index 0.\n3. `get()` extracts root tuple `(1, ...)`.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Enqueue (`put`) | $O(\log N)$ |\n| Dequeue (`get`) | $O(\log N)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Priority Ties:** If priority scores match, e.g. `(1, TaskA)` and `(1, TaskB)`, Python attempts to compare the task values. If task values are uncomparable dictionaries, it raises `TypeError`. Use a unique tie-breaker index: `(1, tie_breaker_id, Task)`."
    },

    # 2. Linear Data Structures
    "dynamic_array": {
        "title": "Dynamic Arrays",
        "category": "Linear Data Structures",
        "analogy": "A stadium section that automatically expands its seating capacity when the crowd gets too large.",
        "concept": "A Dynamic Array is a linear structure with automatic resizing. When the array is full, it allocates a new contiguous block of memory (usually double the capacity) and copies the old elements over.",
        "code": textwrap.dedent("""
            class SimpleDynamicArray:
                def __init__(self):
                    self.capacity = 2
                    self.size = 0
                    self.data = [None] * self.capacity
                
                def append(self, val):
                    if self.size == self.capacity:
                        self._resize()
                    self.data[self.size] = val
                    self.size += 1
                
                def _resize(self):
                    self.capacity *= 2
                    new_data = [None] * self.capacity
                    for i in range(self.size):
                        new_data[i] = self.data[i]
                    self.data = new_data
        """).strip(),
        "dry_run": "1. Initialize with capacity 2. `append(1)` -> `[1, None]`.\n2. `append(2)` -> `[1, 2]`. Array is full.\n3. `append(3)` triggers `_resize()`. Capacity grows to 4, allocates `[1, 2, None, None]`, appends 3.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Append | $O(1)$ amortized ($O(N)$ during resize) |\n| Lookup | $O(1)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Memory Allocation Overhead:** High resizing frequency causes lag. Choose an optimal expansion multiplier (like 1.5 or 2) to balance memory consumption and execution speed."
    },
    "singly_linked_list": {
        "title": "Singly Linked List",
        "category": "Linear Data Structures",
        "analogy": "A line of dancers where each dancer has their hands placed exclusively on the shoulders of the dancer directly in front of them.",
        "concept": "A Singly Linked List is a linear data structure consisting of nodes where each node references the next node in the chain. Traversals are strictly forward-only.",
        "code": textwrap.dedent("""
            class Node:
                def __init__(self, data):
                    self.data = data
                    self.next = None
            
            class SinglyLinkedList:
                def __init__(self):
                    self.head = None
                def prepend(self, data):
                    new_node = Node(data)
                    new_node.next = self.head
                    self.head = new_node
        """).strip(),
        "dry_run": "1. Node creates item value.\n2. New node `next` points to current head reference.\n3. `head` pointer updates to reference the new node.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Prepend | $O(1)$ |\n| Append / Search | $O(N)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Null Checks:** Iterating through the list without guarding against `None` (empty head) will instantly throw `AttributeError` exceptions."
    },
    "doubly_linked_list": {
        "title": "Doubly Linked List",
        "category": "Linear Data Structures",
        "analogy": "A chain of people holding hands both forward and backward, allowing messages to be passed smoothly up or down the line.",
        "concept": "A Doubly Linked List is a collection of nodes where each node holds pointers to both its successor (next) and predecessor (prev) nodes, allowing bidirectional traversal.",
        "code": textwrap.dedent("""
            class DLLNode:
                def __init__(self, data):
                    self.data = data
                    self.next = None
                    self.prev = None
            
            class DoublyLinkedList:
                def __init__(self):
                    self.head = None
                def prepend(self, data):
                    new_node = DLLNode(data)
                    if self.head:
                        self.head.prev = new_node
                    new_node.next = self.head
                    self.head = new_node
        """).strip(),
        "dry_run": "1. Instantiate new doubly-linked node.\n2. If head is present, set its previous pointer to reference new node.\n3. Link new node successor to head, and assign head to new node.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Prepend / Insert Head | $O(1)$ |\n| Append / Search | $O(N)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Pointer Integrity:** Inserting or removing nodes from a doubly linked list requires updating 4 pointers (`next`, `prev` of surrounding nodes). Misalignments cause infinite circular loops."
    },
    "circular_linked_list": {
        "title": "Circular Linked List",
        "category": "Linear Data Structures",
        "analogy": "A multiplayer card game where turn rotation loops back to player 1 after the last player takes their turn.",
        "concept": "In a Circular Linked List, the tail node's `next` pointer references the root head node instead of `None`, closing the list into a continuous ring.",
        "code": textwrap.dedent("""
            class Node:
                def __init__(self, data):
                    self.data = data
                    self.next = None
            
            class CircularLinkedList:
                def __init__(self):
                    self.head = None
                def append(self, data):
                    new_node = Node(data)
                    if not self.head:
                        self.head = new_node
                        new_node.next = self.head
                        return
                    curr = self.head
                    while curr.next != self.head:
                        curr = curr.next
                    curr.next = new_node
                    new_node.next = self.head
        """).strip(),
        "dry_run": "1. Append to empty list: set `head = new_node`, and circular reference `new_node.next = head`.\n2. Append to populated list: traverse until `curr.next == head`.\n3. Set `curr.next = new_node` and loop closure `new_node.next = head`.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Insertion / Deletion | $O(N)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Infinite Traversal Loop:** Using a standard `while curr:` condition on a circular list causes infinite loops. Always terminate loops when `curr.next == head` is matched!"
    },
    "stack": {
        "title": "Stacks (LIFO)",
        "category": "Linear Data Structures",
        "analogy": "A vertical stack of books. You can only place a new book on top, and you must remove the top book first.",
        "concept": "A Stack is a Last-In, First-Out (LIFO) collection. Insertion (push) and deletion (pop) take place at the same end.",
        "code": textwrap.dedent("""
            class Stack:
                def __init__(self):
                    self._items = []
                def push(self, val): self._items.append(val)
                def pop(self):
                    if not self._items: raise IndexError("Pop from empty stack")
                    return self._items.pop()
        """).strip(),
        "dry_run": "1. `push(10)` appends 10 to internal array. Array state: `[10]`.\n2. `push(20)` appends 20 to internal array. Array state: `[10, 20]`.\n3. `pop()` extracts the last item at index 1 (20). Array state: `[10]`.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Push / Pop | $O(1)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Stack Underflow:** Popping from an empty stack throws IndexError. Always verify structural capacity beforehand using `if not stack:`."
    },
    "simple_queue": {
        "title": "Simple Queue (FIFO)",
        "category": "Linear Data Structures",
        "analogy": "A line of cars at a toll booth: the first car to enter the lane pays first and exits first.",
        "concept": "A Queue is a linear First-In, First-Out (FIFO) collection. Elements are inserted at the Rear (enqueue) and removed from the Front (dequeue).",
        "code": textwrap.dedent("""
            from collections import deque
            class SimpleQueue:
                def __init__(self):
                    self._items = deque()
                def enqueue(self, val): self._items.append(val)
                def dequeue(self):
                    if not self._items: raise IndexError("Dequeue from empty queue")
                    return self._items.popleft()
        """).strip(),
        "dry_run": "1. `enqueue(10)` -> `deque([10])`.\n2. `enqueue(20)` -> `deque([10, 20])`.\n3. `dequeue()` pops index 0 left item (10), returns it -> `deque([20])`.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Enqueue | $O(1)$ |\n| Dequeue | $O(1)$ (using deque) |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Queue Underflow:** Dequeuing from an empty queue throws IndexError. Always wrap operations with a check: `if len(queue) == 0:`."
    },
    "circular_queue": {
        "title": "Circular Queues",
        "category": "Linear Data Structures",
        "analogy": "A ring road with fixed parking bays. When a car parks in the last bay, the next car wraps around to park in slot 0.",
        "concept": "A Circular Queue is a fixed-size queue where the last position is circularly connected to the first position. This structure avoids memory waste in arrays by wrapping indices using modulo arithmetic: `(index + 1) % capacity`.",
        "code": textwrap.dedent("""
            class CircularQueue:
                def __init__(self, k):
                    self.k = k
                    self.queue = [None] * k
                    self.head = -1
                    self.tail = -1
                
                def enqueue(self, value):
                    if ((self.tail + 1) % self.k) == self.head:
                        return False # Full
                    if self.head == -1:
                        self.head = 0
                    self.tail = (self.tail + 1) % self.k
                    self.queue[self.tail] = value
                    return True
        """).strip(),
        "dry_run": "1. Initialize queue of size 3: `[None, None, None]`, pointers `head=0, tail=-1`.\n2. `enqueue(10)` -> `tail=( -1 + 1 ) % 3 = 0`, queue: `[10, None, None]`.\n3. `enqueue(20)` -> `tail=1`, queue: `[10, 20, None]`.\n4. `enqueue(30)` -> `tail=2`, queue: `[10, 20, 30]`. Queue is now full.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Enqueue / Dequeue | $O(1)$ |\n| Space Complexity | $O(K)$ |",
        "edge_cases": "• **Index Wraparound checks:** Ensure the queue full condition is verified as `(tail + 1) % k == head` to prevent overwriting un-dequeued values."
    },

    # 3. Non-Linear Data Structures
    "binary_tree": {
        "title": "Binary Tree",
        "category": "Non-Linear Data Structures",
        "analogy": "A family tree where each parent has at most two children.",
        "concept": "A Binary Tree is a hierarchical structure where each node has at most two children, referred to as the left child and the right child.",
        "code": textwrap.dedent("""
            class TreeNode:
                def __init__(self, val):
                    self.val = val
                    self.left = None
                    self.right = None
        """).strip(),
        "dry_run": "1. `TreeNode(10)` allocates root.\n2. Root `left` is assigned reference to `TreeNode(5)`.\n3. Root `right` is assigned reference to `TreeNode(15)`.",
        "complexity": "| Tree Type | Time Complexity (Traversals) |\n| :--- | :--- |\n| DFS / BFS | $O(N)$ |\n| Space Complexity | $O(H)$ (Height of tree call stack depth) |",
        "edge_cases": "• **Leaf Check:** Ensure traversals safely check `if not root: return` to prevent infinite recursion on leaf nodes."
    },
    "bst": {
        "title": "Binary Search Tree (BST)",
        "category": "Non-Linear Data Structures",
        "analogy": "A highly organized filing cabinet where files are sorted alphabetically: files starting with letters before 'M' go left, and letters after go right.",
        "concept": "A BST is a binary tree where left child values are strictly smaller than the parent node, and right child values are strictly larger. This ordered property enables fast $O(\log N)$ searches.",
        "code": textwrap.dedent("""
            class TreeNode:
                def __init__(self, val):
                    self.val = val
                    self.left = None
                    self.right = None
            
            def insert(root, val):
                if not root: return TreeNode(val)
                if val < root.val:
                    root.left = insert(root.left, val)
                else:
                    root.right = insert(root.right, val)
                return root
        """).strip(),
        "dry_run": "1. Inserting 7 into tree with root 10. `7 < 10`, traverse left.\n2. Left child is 5. `7 > 5`, traverse right.\n3. Right child of 5 is None. Insert new `TreeNode(7)`.",
        "complexity": "| Condition | Average Case | Worst Case |\n| :--- | :--- | :--- |\n| Search / Insert | $O(\log N)$ | $O(N)$ |\n| Space Complexity | $O(H)$ | $O(N)$ |",
        "edge_cases": "• **Skewed Trees:** Inserting already sorted data `[1, 2, 3]` results in a chain of right-only child nodes, causing BST search to slow to linear $O(N)$. Self-balancing AVL trees resolve this."
    },
    "avl_tree": {
        "title": "AVL Trees",
        "category": "Non-Linear Data Structures",
        "analogy": "A balanced mobile hanging over a crib that dynamically self-adjusts when one side becomes too heavy.",
        "concept": "An AVL tree is a self-balancing Binary Search Tree. It maintains a **Balance Factor** (height difference between left and right subtrees) of at most 1 for every node. It restores balance dynamically using Single or Double rotations.",
        "code": textwrap.dedent("""
            class AVLNode:
                def __init__(self, val):
                    self.val = val
                    self.left = None
                    self.right = None
                    self.height = 1
            
            def right_rotate(y):
                x = y.left
                T2 = x.right
                x.right = y
                y.left = T2
                y.height = max(get_height(y.left), get_height(y.right)) + 1
                x.height = max(get_height(x.left), get_height(x.right)) + 1
                return x
        """).strip(),
        "dry_run": "1. Insert item that makes left child too deep (balance factor > 1).\n2. Call `right_rotate(y)`.\n3. Left child `x` is promoted to root, original root `y` becomes its right child.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Search / Insert | $O(\log N)$ (Guaranteed!) |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Double Rotations:** If a node's left child is right-heavy, a single rotation is insufficient. You must execute a Left-Right double rotation."
    },
    "segment_tree": {
        "title": "Segment Tree",
        "category": "Non-Linear Data Structures",
        "concept": "A Segment Tree is a binary tree used for storing intervals or segments. It allows querying of intervals (e.g. range sum or range minimum) and updating of array values, both in fast $O(\log N)$ time.",
        "code": textwrap.dedent("""
            def build_tree(arr, tree, start, end, node):
                if start == end:
                    tree[node] = arr[start]
                    return
                mid = (start + end) // 2
                build_tree(arr, tree, start, mid, 2 * node)
                build_tree(arr, tree, mid + 1, end, 2 * node + 1)
                tree[node] = tree[2 * node] + tree[2 * node + 1]
        """).strip(),
        "dry_run": "1. Array `[1, 3, 5]` divided at mid=1. Left branch `[1, 3]`, right branch `[5]`.\n2. Left branch divided: index 0 is 1, index 1 is 3.\n3. Base elements written to leaves, parents sum up: root is 9.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Build Tree | $O(N)$ |\n| Range Query / Update | $O(\log N)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Array Size bounds:** The heap representation of a segment tree requires an array allocation of size $4N$ to avoid index out of bounds errors."
    },
    "fenwick_tree": {
        "title": "Fenwick Tree (Binary Indexed Tree)",
        "category": "Non-Linear Data Structures",
        "concept": "A Fenwick Tree is a highly compact data structure that maintains prefix sums for arrays. It runs range sum queries and point updates in fast $O(\log N)$ time while using exactly $O(N)$ memory.",
        "code": textwrap.dedent("""
            class FenwickTree:
                def __init__(self, size):
                    self.tree = [0] * (size + 1)
                def update(self, i, delta):
                    i += 1
                    while i < len(self.tree):
                        self.tree[i] += delta
                        i += i & (-i) # Move to next index using bitwise logic
        """).strip(),
        "dry_run": "1. `update(1, 5)` converts 1 to 1-based index 2.\n2. `i & (-i)` determines the step size. Adds 5 to `tree[2]`.\n3. Index increments by bitwise step to update subsequent parent nodes.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Range Query | $O(\log N)$ |\n| Point Update | $O(\log N)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **1-Based Indexing:** Fenwick tree updates rely on bitwise logic (`i & -i`), which stalls indefinitely if index `i` is 0. Always convert input arrays to 1-based indices."
    },
    "trie": {
        "title": "Trie (Prefix Tree)",
        "category": "Non-Linear Data Structures",
        "analogy": "Mobile phone autocomplete. When you type 'cat', the search navigates from 'c' to 'a' to 't' to suggest words.",
        "concept": "A Trie is an advanced search tree used to store associative keys, usually strings. Every path down the tree represents a word prefix, enabling high-performance autocomplete engines.",
        "code": textwrap.dedent("""
            class TrieNode:
                def __init__(self):
                    self.children = {}
                    self.is_end_of_word = False
            
            class Trie:
                def __init__(self):
                    self.root = TrieNode()
                def insert(self, word):
                    curr = self.root
                    for char in word:
                        if char not in curr.children:
                            curr.children[char] = TrieNode()
                        curr = curr.children[char]
                    curr.is_end_of_word = True
        """).strip(),
        "dry_run": "1. Inserting 'cat'. Start at root TrieNode.\n2. 'c' is not in root children, create new TrieNode under key 'c'. Move current pointer.\n3. Create TrieNode under 'a', move pointer. Create under 't', move pointer.\n4. Set `is_end_of_word = True` on 't' node.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Insert / Search | $O(L)$ (L is word length) |\n| Space Complexity | $O(N \cdot L)$ |",
        "edge_cases": "• **Word Deletion:** Deleting words from a Trie requires recursively cleaning up nodes that have no other children to prevent orphan memory slots."
    },
    "heap_tree": {
        "title": "Heap Tree",
        "category": "Non-Linear Data Structures",
        "concept": "A Heap Tree is a complete binary tree satisfying the heap property: parent nodes are always larger than or equal to their children (Max-Heap), or smaller than or equal to their children (Min-Heap).",
        "code": textwrap.dedent("""
            # Bubble up heap restoration
            def heapify_up(arr, i):
                parent = (i - 1) // 2
                if parent >= 0 and arr[i] > arr[parent]:
                    arr[i], arr[parent] = arr[parent], arr[i]
                    heapify_up(arr, parent)
        """).strip(),
        "dry_run": "1. Append element to the leaf array position of heap tree.\n2. Compare new leaf node with its parent at `(i - 1) // 2`.\n3. If larger, swap nodes and recursively check new parent slots.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Push / Pop | $O(\log N)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Index Bounds:** The mathematical parent of index 0 evaluates as `(0-1)//2 = -1`. Guard your checks against negative index boundaries."
    },
    "b_tree": {
        "title": "B-Tree",
        "category": "Non-Linear Data Structures",
        "concept": "A B-Tree is a self-balancing search tree designed to store large blocks of sorted data. Unlike binary trees, B-tree nodes can contain multiple keys and have more than two children, making them ideal for database systems and hard disk storage.",
        "code": textwrap.dedent("""
            class BTreeNode:
                def __init__(self, leaf=True):
                    self.keys = []
                    self.children = []
                    self.leaf = leaf
        """).strip(),
        "dry_run": "1. Keys are inserted sorted inside a B-Tree node.\n2. When keys inside a node exceed a predefined threshold, the node splits.\n3. The median key is promoted to the parent, creating child split blocks.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Search / Insert / Delete | $O(\log N)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Disk I/O alignment:** B-Tree node sizes are configured to match disk block boundaries (usually 4KB) to minimize hardware retrieval operations."
    },
    "red_black_tree": {
        "title": "Red-Black Tree",
        "category": "Non-Linear Data Structures",
        "concept": "A Red-Black Tree is a self-balancing Binary Search Tree where each node has a color attribute (Red or Black). Balance is maintained using color rules and node rotations, ensuring searches never degrade to linear time.",
        "code": textwrap.dedent("""
            class RBTNode:
                def __init__(self, val, color="RED"):
                    self.val = val
                    self.color = color
                    self.left = None
                    self.right = None
                    self.parent = None
        """).strip(),
        "dry_run": "1. New nodes are inserted colored RED.\n2. If the parent is also RED, a color violation occurs.\n3. The tree self-corrects by flipping colors or performing left/right rotations.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Search / Insert | $O(\log N)$ (Guaranteed) |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Double Red violations:** If a red node has a red child, the tree must balance itself by recoloring the parent and uncle nodes or executing rotations."
    },
    "n_ary_tree": {
        "title": "N-ary Tree",
        "category": "Non-Linear Data Structures",
        "concept": "An N-ary tree is a tree where each node can have at most N children. It is used to represent structural hierarchies like file directory systems.",
        "code": textwrap.dedent("""
            class NaryNode:
                def __init__(self, val):
                    self.val = val
                    self.children = [] # Dynamic children array
        """).strip(),
        "dry_run": "1. `NaryNode('/')` allocates root node.\n2. Root children list appends folder node `'home'` and `'etc'`.\n3. Node `'home'` children list appends user directory node `'ammar'`.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Traversal (DFS/BFS) | $O(N)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Infinite loops:** If graph cyclic references are mistakenly represented as tree links, traversals will loop indefinitely. Always check for parent pointer constraints."
    },
    "directed_graph": {
        "title": "Directed Graph",
        "category": "Non-Linear Data Structures",
        "concept": "A Directed Graph is a graph where edges have arrows indicating direction. Travel is restricted to one-way paths between vertices.",
        "code": textwrap.dedent("""
            class DirectedGraph:
                def __init__(self):
                    self.adj = {}
                def add_edge(self, u, v):
                    self.adj.setdefault(u, []).append(v) # One-way link u -> v
        """).strip(),
        "dry_run": "1. `add_edge('A', 'B')` -> adds `'B'` to `'A'`'s adjacency list.\n2. Querying `'B'`'s neighbors returns empty list because path is strictly one-way.",
        "complexity": "| Operation | Adjacency List |\n| :--- | :--- |\n| Add Edge | $O(1)$ |\n| Space Complexity | $O(V + E)$ |",
        "edge_cases": "• **In-degree Tracking:** Calculating how many paths point *to* a vertex in directed graphs requires keeping a separate hashmap or doing a full scan of all adjacency lists."
    },
    "undirected_graph": {
        "title": "Undirected Graph",
        "category": "Non-Linear Data Structures",
        "concept": "An Undirected Graph is a graph where edges represent bidirectional relationships. A link between A and B is walkable in both directions.",
        "code": textwrap.dedent("""
            class Graph:
                def __init__(self):
                    self.adj = {}
                def add_edge(self, u, v):
                    self.adj.setdefault(u, []).append(v)
                    self.adj.setdefault(v, []).append(u) # Bidirectional link
        """).strip(),
        "dry_run": "1. `add_edge('A', 'B')` -> appends `'B'` to `'A'` neighbor array.\n2. Appends `'A'` to `'B'` neighbor array, creating a two-way path.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Add Edge | $O(1)$ |\n| Space Complexity | $O(V + E)$ |",
        "edge_cases": "• **Duplicate Links:** Prevent appending `'B'` to `'A'` multiple times by checking membership before insertion, or by using sets in place of lists."
    },
    "weighted_graph": {
        "title": "Weighted Graph",
        "category": "Non-Linear Data Structures",
        "concept": "A Weighted Graph is a graph where each edge has a numerical cost (weight). This value represents distance, travel time, or toll fees, which is essential for shortest path algorithms like Dijkstra's.",
        "code": textwrap.dedent("""
            class WeightedGraph:
                def __init__(self):
                    self.adj = {}
                def add_edge(self, u, v, weight):
                    # Store neighbors as tuple pairs: (neighbor, weight)
                    self.adj.setdefault(u, []).append((v, weight))
        """).strip(),
        "dry_run": "1. `add_edge('A', 'B', 5)` -> records `('B', 5)` under key `'A'`.\n2. Shortest-path scans sum edge weights along travel routes to find the lowest cost path.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Add edge | $O(1)$ |\n| Space Complexity | $O(V + E)$ |",
        "edge_cases": "• **Negative Weights:** Weighted graphs with negative edge weights cause Dijkstra's algorithm to loop infinitely. Use the Bellman-Ford algorithm to handle negative weights securely."
    },
    "unweighted_graph": {
        "title": "Unweighted Graph",
        "category": "Non-Linear Data Structures",
        "concept": "An Unweighted Graph has uniform edge costs. The shortest path between two nodes is simply the path with the minimum number of edge hops, calculated efficiently via BFS.",
        "code": textwrap.dedent("""
            # Hops count shortest path using BFS on unweighted graph
            from collections import deque
            def shortest_path_unweighted(graph, start, end):
                queue = deque([[start]])
                visited = {start}
                while queue:
                    path = queue.popleft()
                    node = path[-1]
                    if node == end: return path
                    for neighbor in graph.get(node, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(path + [neighbor])
        """).strip(),
        "dry_run": "1. Start queue with path `['A']`. `visited = {'A'}`.\n2. Dequeue `['A']`. Neighbors are `'B'` and `'C'`.\n3. Append paths `['A', 'B']` and `['A', 'C']` to queue. First match returns path.",
        "complexity": "| Operation | Time/Space Complexity |\n| :--- | :--- |\n| Shortest Path Hops | $O(V + E)$ |\n| Space Complexity | $O(V)$ |",
        "edge_cases": "• **Disconnected Nodes:** If the target node is isolated, BFS will exhaustively search the graph and return `None`."
    },
    "cyclic_graph": {
        "title": "Cyclic Graph",
        "category": "Non-Linear Data Structures",
        "concept": "A Cyclic Graph is a graph containing at least one cycle (a closed path starting and ending at the same node). Traversals must track visited nodes to avoid infinite loops.",
        "code": textwrap.dedent("""
            # Cycle detection in directed graph using DFS coloring
            def has_cycle(node, adj, visited, rec_stack):
                visited.add(node)
                rec_stack.add(node)
                for neighbor in adj.get(node, []):
                    if neighbor not in visited:
                        if has_cycle(neighbor, adj, visited, rec_stack):
                            return True
                    elif neighbor in rec_stack:
                        return True # Cycle detected!
                rec_stack.remove(node)
                return False
        """).strip(),
        "dry_run": "1. `has_cycle('A')` -> adds `'A'` to `visited` and active recursion stack `rec_stack`.\n2. Calls `'B'`, adds to stack.\n3. If `'B'` neighbor points back to `'A'`, matching `neighbor in rec_stack` triggers `True`.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Cycle Check | $O(V + E)$ |\n| Space Complexity | $O(V)$ |",
        "edge_cases": "• **Self-Loops:** A node pointing directly to itself is a cycle of length 1. Ensure your algorithms handle self-loops correctly."
    },
    "acyclic_graph": {
        "title": "Acyclic Graph",
        "category": "Non-Linear Data Structures",
        "concept": "An Acyclic Graph contains no cycles. A famous example is a **Tree**, which is simply a connected, undirected acyclic graph.",
        "code": textwrap.dedent("""
            # Unconnected Acyclic Graph traversal
            def traverse(graph):
                visited = set()
                for node in graph:
                    if node not in visited:
                        # Safe to traverse without back-edge cycle checks
                        pass
        """).strip(),
        "dry_run": "1. Loop over graph nodes.\n2. Check `visited` set. If clean, proceed to traverse safely without worrying about cycle loops.",
        "complexity": "| Operation | Time/Space Complexity |\n| :--- | :--- |\n| DFS Acyclic | $O(V + E)$ |\n| Space Complexity | $O(V)$ |",
        "edge_cases": "• **Forests:** Disconnected acyclic graphs are called forests. Ensure your traversals scan all nodes to cover disconnected segments."
    },
    "dag": {
        "title": "Directed Acyclic Graph (DAG)",
        "category": "Non-Linear Data Structures",
        "analogy": "A university degree plan: you must pass lower-level prerequisites (ancestor nodes) before unlocking advanced courses (descendant nodes).",
        "concept": "A DAG is a directed graph with no cycles. This acyclic property enables topological sorting (ordering nodes linearly based on dependencies).",
        "code": textwrap.dedent("""
            # Topological sort in a DAG (Kahn's algorithm using in-degrees)
            from collections import deque
            def topological_sort(v, adj):
                in_degree = {i: 0 for i in range(v)}
                for u in adj:
                    for neighbor in adj[u]:
                        in_degree[neighbor] += 1
                queue = deque([u for u in in_degree if in_degree[u] == 0])
                order = []
                while queue:
                    u = queue.popleft()
                    order.append(u)
                    for neighbor in adj.get(u, []):
                        in_degree[neighbor] -= 1
                        if in_degree[neighbor] == 0:
                            queue.append(neighbor)
                return order
        """).strip(),
        "dry_run": "1. Count incoming edges (in-degree) for all vertices.\n2. Enqueue nodes with in-degree 0 (no prerequisites).\n3. Dequeue, append to order, decrement neighbors' in-degree. Enqueue any neighbors that hit 0.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Topological Sort | $O(V + E)$ |\n| Space Complexity | $O(V)$ |",
        "edge_cases": "• **Graph has cycle:** If Kahn's algorithm output list length is less than total vertices `V`, the graph contains a cycle (cannot be topologically sorted)."
    },
    "hash_table": {
        "title": "Hash Table / Hash Map",
        "category": "Non-Linear Data Structures",
        "concept": "A Hash Table maps unique keys to values using a hash function. It calculates an index where values are stored, enabling extremely fast constant-time lookup, insertion, and deletion.",
        "code": textwrap.dedent("""
            class HashTable:
                def __init__(self):
                    self.size = 8
                    self.slots = [[] for _ in range(self.size)]
                def insert(self, key, val):
                    idx = hash(key) % self.size
                    self.slots[idx].append((key, val))
        """).strip(),
        "dry_run": "1. `insert('name', 'ammar')` hashes key 'name' to an integer.\n2. Modulo operator limits index: `hash % 8 = 3`.\n3. Appends key-value pair `('name', 'ammar')` to bucket 3.",
        "complexity": "| Operation | Average Case | Worst Case (all collide) |\n| :--- | :--- | :--- |\n| Lookup / Insert | $O(1)$ | $O(N)$ |\n| Space Complexity | $O(N)$ | $O(N)$ |",
        "edge_cases": "• **High Collision Rate:** If many keys hash to the same bucket, lookup degrades to $O(N)$. Resolve this with a robust hash function and dynamic resizing."
    },
    "hash_set": {
        "title": "Hash Set",
        "category": "Non-Linear Data Structures",
        "concept": "A Hash Set is a collection of unique keys implemented using a hash table, offering $O(1)$ membership lookups.",
        "code": textwrap.dedent("""
            class HashSet:
                def __init__(self):
                    self.slots = [[] for _ in range(8)]
                def add(self, val):
                    idx = hash(val) % 8
                    if val not in self.slots[idx]:
                        self.slots[idx].append(val)
        """).strip(),
        "dry_run": "1. `add(44)` hashes 44, calculates slot modulo index.\n2. Checks if 44 exists in bucket list. If absent, appends to bucket.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Add / Membership | $O(1)$ |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Unhashable Data Types:** Attempting to store mutable objects (like lists) will throw `TypeError: unhashable type`."
    },

    # 4. Advanced Data Structures
    "suffix_array": {
        "title": "Suffix Array",
        "category": "Advanced Data Structures",
        "concept": "A Suffix Array is a sorted array of all suffixes of a string. It is a highly compact data structure used in string matching and genome sequence searching.",
        "code": textwrap.dedent("""
            def build_suffix_array(text):
                # Pair suffix strings with their original starting index, then sort
                suffixes = sorted([(text[i:], i) for i in range(len(text))])
                return [index for suffix, index in suffixes]
        """).strip(),
        "dry_run": "1. Suffixes of 'banana' are: 'banana', 'anana', 'nana', 'ana', 'na', 'a'.\n2. Sorted suffixes: 'a' (5), 'ana' (3), 'anana' (1), 'banana' (0), 'na' (4), 'nana' (2).\n3. Suffix array yields: `[5, 3, 1, 0, 4, 2]`.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Build Array | $O(N^2 \log N)$ (naive) / $O(N \log N)$ (optimal) |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Large Datasets:** Naive sorting of suffix strings is memory-intensive. Use prefix doubling algorithms to sort suffixes in optimal $O(N \log N)$ time."
    },
    "suffix_tree": {
        "title": "Suffix Tree",
        "category": "Advanced Data Structures",
        "concept": "A Suffix Tree is a compressed trie containing all suffixes of a given string. It solves complex string problems (like locating the longest repeating substring) in ultra-fast linear $O(N)$ time.",
        "code": textwrap.dedent("""
            # Conceptual Suffix Tree Node representation
            class SuffixTreeNode:
                def __init__(self):
                    self.children = {}
                    self.start_index = -1
                    self.end_index = -1
        """).strip(),
        "dry_run": "1. Build suffixes, compress single-child nodes into single edges (edge compression).\n2. Search patterns by traversing character edges down the tree.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Build / Search | $O(N)$ (using Ukkonen's algorithm) |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Termination character:** Appending a unique terminal character (like `'$'`) at the end of strings prevents suffixes from matching interior nodes, ensuring every suffix ends at a leaf."
    },
    "disjoint_set": {
        "title": "Disjoint Set (Union-Find)",
        "category": "Advanced Data Structures",
        "analogy": "Merging small social groups: when two people become friends, their entire friendship groups merge under a single group leader.",
        "concept": "Union-Find is a data structure that tracks elements split into non-overlapping subsets. It offers two primary operations:\n1. **Find:** Identify the representative leader of a subset.\n2. **Union:** Merge two disjoint subsets into a single group.",
        "code": textwrap.dedent("""
            class DisjointSet:
                def __init__(self, n):
                    self.parent = list(range(n))
                    self.rank = [0] * n
                
                def find(self, i):
                    # Path Compression optimization
                    if self.parent[i] == i:
                        return i
                    self.parent[i] = self.find(self.parent[i])
                    return self.parent[i]
                
                def union(self, i, j):
                    root_i = self.find(i)
                    root_j = self.find(j)
                    if root_i != root_j:
                        # Union by Rank optimization
                        if self.rank[root_i] < self.rank[root_j]:
                            self.parent[root_i] = root_j
                        else:
                            self.parent[root_j] = root_i
                            if self.rank[root_i] == self.rank[root_j]:
                                self.rank[root_i] += 1
        """).strip(),
        "dry_run": "1. `find(3)` traces parent links up to subset leader.\n2. **Path Compression:** Re-binds all intermediate nodes' parent pointers directly to the leader, speeding up subsequent queries.\n3. **Union by Rank:** Attaches the shallower tree root under the deeper root to keep the overall tree flat.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Find / Union | $O(\\alpha(N))$ (Inverse Ackermann function - practically $O(1)$) |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Cycle Detection:** If `find(i) == find(j)` before performing union, adding an edge between them creates a cycle. This is the core logic used in Kruskal's MST algorithm!"
    },
    "bloom_filter": {
        "title": "Bloom Filter",
        "category": "Advanced Data Structures",
        "analogy": "A bouncer with a checklist. If they say your name is *not* on the list, you are definitely not invited. If they say your name *is* on the list, you might be invited (possible false positive), but you'll have to double-check.",
        "concept": "A Bloom Filter is a space-efficient, probabilistic data structure used to test set membership. It guarantees **zero false negatives**, but has a small probability of **false positives**.",
        "code": textwrap.dedent("""
            class SimpleBloomFilter:
                def __init__(self, size=100):
                    self.size = size
                    self.bit_array = [0] * size
                def add(self, item):
                    # Compute multiple distinct hash indices
                    idx1 = hash(item) % self.size
                    idx2 = (hash(item) * 31) % self.size
                    self.bit_array[idx1] = 1
                    self.bit_array[idx2] = 1
                def check(self, item):
                    idx1 = hash(item) % self.size
                    idx2 = (hash(item) * 31) % self.size
                    return self.bit_array[idx1] == 1 and self.bit_array[idx2] == 1
        """).strip(),
        "dry_run": "1. `add('apple')` hashes 'apple' to indices 12 and 45. Sets `bit_array[12] = 1, bit_array[45] = 1`.\n2. `check('banana')` hashes 'banana' to indices 12 and 90. Since `bit_array[90] == 0`, it returns `False` (definitely not in set!).\n3. `check('cherry')` hashes 'cherry' to indices 12 and 45. Both bits are 1, returning `True` (possibly in set, false positive).",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Add / Check | $O(K)$ (K is hash count) |\n| Space Complexity | $O(M)$ (M is bit capacity - independent of element count!) |",
        "edge_cases": "• **No Deletions Allowed:** You cannot delete items from a standard Bloom Filter. Clearing a bit could accidentally delete other elements that hash to that same index."
    },
    "sparse_table": {
        "title": "Sparse Table",
        "category": "Advanced Data Structures",
        "concept": "A Sparse Table is an advanced static data structure used to answer Range Minimum Queries (RMQ) in lightning-fast $O(1)$ constant time after a one-time $O(N \log N)$ preprocessing step.",
        "code": textwrap.dedent("""
            # Preprocessing sparse table for range minimum queries
            import math
            def build_sparse_table(arr):
                n = len(arr)
                cols = int(math.log2(n)) + 1
                st = [[0] * cols for _ in range(n)]
                for i in range(n): st[i][0] = arr[i]
                for j in range(1, cols):
                    for i in range(n - (1 << j) + 1):
                        st[i][j] = min(st[i][j-1], st[i + (1 << (j-1))][j-1])
                return st
        """).strip(),
        "dry_run": "1. Fills column 0 with raw array elements.\n2. Fills column 1 with the minimum of intervals of size 2.\n3. Fills column 2 with the minimum of intervals of size 4, using values from column 1.",
        "complexity": "| Phase | Time Complexity |\n| :--- | :--- |\n| Preprocessing | $O(N \log N)$ |\n| Range Query (RMQ) | $O(1)$ |\n| Space Complexity | $O(N \log N)$ |",
        "edge_cases": "• **Immutable Data:** Sparse tables are ideal for static databases. If array elements are modified, the entire table must be rebuilt from scratch."
    },
    "skip_list": {
        "title": "Skip List",
        "category": "Advanced Data Structures",
        "analogy": "A subway network with express lines that skip smaller local stops, allowing you to travel quickly before switching to a local train for your final stop.",
        "concept": "A Skip List is a probabilistic data structure that enables fast $O(\log N)$ search, insertion, and deletion within a sorted linked list by maintaining multiple hierarchy levels of express links.",
        "code": textwrap.dedent("""
            class SkipListNode:
                def __init__(self, val, level):
                    self.val = val
                    self.forward = [None] * (level + 1) # Express link references
        """).strip(),
        "dry_run": "1. Search starts at the highest express level.\n2. Traverses forward as long as nodes are smaller than target. If larger, drops down 1 level.\n3. Repeats until index matches target on base local list.",
        "complexity": "| Operation | Average Case | Worst Case |\n| :--- | :--- | :--- |\n| Search / Insert | $O(\log N)$ | $O(N)$ |\n| Space Complexity | $O(N)$ | $O(N \log N)$ |",
        "edge_cases": "• **Random Level Generation:** Level heights are chosen via coin flips (e.g. 50% probability). Bad random sequences can skew skip links, slowing search performance."
    },
    "lru_cache": {
        "title": "LRU Cache",
        "category": "Advanced Data Structures",
        "analogy": "A small desk with limited space. When a new book arrives and the desk is full, you pack away the book you haven't opened in the longest time.",
        "concept": "An LRU (Least Recently Used) Cache discards the oldest, least accessed elements first when capacity is reached. It is implemented using a **Hash Map** combined with a **Doubly Linked List** to achieve $O(1)$ lookups and updates.",
        "code": textwrap.dedent("""
            class DLLNode:
                def __init__(self, key, val):
                    self.key = key
                    self.val = val
                    self.prev = None
                    self.next = None
            
            class LRUCache:
                def __init__(self, capacity):
                    self.capacity = capacity
                    self.cache = {} # Hash map
                    self.head = DLLNode(0, 0)
                    self.tail = DLLNode(0, 0)
                    self.head.next = self.tail
                    self.tail.prev = self.head
                
                def _remove(self, node):
                    p = node.prev
                    n = node.next
                    p.next = n
                    n.prev = p
                
                def _add(self, node):
                    # Add to head (most recently used)
                    p = self.head.next
                    self.head.next = node
                    node.prev = self.head
                    node.next = p
                    p.prev = node
        """).strip(),
        "dry_run": "1. `get(key)` checks hash map. If present, removes node from DLL, and prepends it to head (marking it most recently used).\n2. `put(key, value)` adds node. If size exceeds capacity, evicts tail node `tail.prev` and removes it from both DLL and hash map.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Get / Put | $O(1)$ |\n| Space Complexity | $O(C)$ (C is capacity) |\n| Space Complexity | $O(C)$ |",
        "edge_cases": "• **Thread Safety:** Standard Python dicts are not thread-safe. Wrap cache operations in threading locks for multi-threaded systems."
    },
    "monotonic_stack": {
        "title": "Monotonic Stack",
        "category": "Advanced Data Structures",
        "concept": "A Monotonic Stack maintains elements in a strict sorted order (increasing or decreasing). It is highly efficient for finding the next greater or smaller element in an array.",
        "code": textwrap.dedent("""
            def next_greater_element(arr):
                # Monotonic decreasing stack storing indices
                res = [-1] * len(arr)
                stack = []
                for i in range(len(arr)):
                    while stack and arr[i] > arr[stack[-1]]:
                        idx = stack.pop()
                        res[idx] = arr[i]
                    stack.append(i)
                return res
        """).strip(),
        "dry_run": "1. Loop index `i=0`, push index 0 (`arr[0]=2`) onto stack: `[0]`.\n2. Loop index `i=1` (`arr[1]=5`). Since `5 > 2`, pop index 0, set `res[0] = 5`. Push index 1: `[1]`.\n3. Resolves all indices in optimal linear time.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Process Array | $O(N)$ (Each element pushed/popped at most once!) |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Elements with no greater value:** Elements with no larger values are left with default value `-1`."
    },
    "monotonic_queue": {
        "title": "Monotonic Queue",
        "category": "Advanced Data Structures",
        "concept": "A Monotonic Queue maintains elements in a strict sorted order. It is most famous for solving the **Sliding Window Maximum** problem in optimal $O(N)$ time.",
        "code": textwrap.dedent("""
            from collections import deque
            def max_sliding_window(nums, k):
                # Monotonic decreasing queue storing indices
                dq = deque()
                res = []
                for i, num in enumerate(nums):
                    if dq and dq[0] < i - k + 1:
                        dq.popleft() # Remove out of window indices
                    while dq and nums[dq[-1]] < num:
                        dq.pop()     # Maintain decreasing order
                    dq.append(i)
                    if i >= k - 1:
                        res.append(nums[dq[0]])
                return res
        """).strip(),
        "dry_run": "1. For sliding window size 3. `append(i)` after popping out-of-bounds indices and smaller elements.\n2. Smallest/obsolete index elements are discarded from queue rear.\n3. The sliding maximum is always kept at index 0 (`dq[0]`).",
        "complexity": "| Operation | Time/Space Complexity |\n| :--- | :--- |\n| Sliding Window | $O(N)$ |\n| Space Complexity | $O(K)$ (K is window size) |",
        "edge_cases": "• **Window size > Array length:** Guard against `k > len(nums)` to avoid empty outputs."
    },

    # 5. Searching Algorithms
    "linear_search": {
        "title": "Linear Search",
        "category": "Searching Algorithms",
        "concept": "Linear Search scans every element sequentially from index 0 to N-1 until the target is found. It works on completely unsorted collections.",
        "code": textwrap.dedent("""
            def linear_search(arr, target):
                for i in range(len(arr)):
                    if arr[i] == target:
                        return i
                return -1
        """).strip(),
        "dry_run": "1. Loop index `i` from 0 to array length minus 1.\n2. Compare `arr[i]` with target. If matched, return index.\n3. If loop ends without a match, return `-1`.",
        "complexity": "| Condition | Time Complexity |\n| :--- | :--- |\n| Best Case | $O(1)$ |\n| Average / Worst Case | $O(N)$ |\n| Space Complexity | $O(1)$ |",
        "edge_cases": "• **Duplicate Targets:** Linear search returns the *first* matching index. Modify it to return a list of all matching indices if duplicates must be tracked."
    },
    "binary_search": {
        "title": "Binary Search",
        "category": "Searching Algorithms",
        "concept": "Binary Search works strictly on sorted arrays by repeatedly dividing the search space in half. It compares the target with the middle element, cutting search time to logarithmic complexity.",
        "code": textwrap.dedent("""
            def binary_search(arr, target):
                low, high = 0, len(arr) - 1
                while low <= high:
                    mid = (low + high) // 2
                    if arr[mid] == target: return mid
                    elif arr[mid] < target: low = mid + 1
                    else: high = mid - 1
                return -1
        """).strip(),
        "dry_run": "1. `low=0`, `high=4`, `arr=[1, 3, 5, 7, 9]`, target is 7.\n2. `mid=(0+4)//2=2`. `arr[2]=5`. Since `5 < 7`, set `low=3`.\n3. `mid=(3+4)//2=3`. `arr[3]=7`. Target matched! Returns index `3`.",
        "complexity": "| Condition | Time Complexity |\n| :--- | :--- |\n| Best Case | $O(1)$ |\n| Average / Worst Case | $O(\log N)$ |\n| Space Complexity | $O(1)$ |",
        "edge_cases": "• **Unsorted Arrays:** Running binary search on unsorted data yields incorrect results. Always ensure data is sorted beforehand.\n• **Integer Overflow:** In languages like Java, `(low + high) // 2` can overflow. Use `low + (high - low) // 2` for absolute safety."
    },
    "jump_search": {
        "title": "Jump Search",
        "category": "Searching Algorithms",
        "concept": "Jump Search works on sorted arrays. It jumps ahead by fixed steps (usually of size $\sqrt{N}$) and then performs a linear search backward once it passes the target.",
        "code": textwrap.dedent("""
            import math
            def jump_search(arr, target):
                n = len(arr)
                step = int(math.sqrt(n))
                prev = 0
                while arr[min(step, n)-1] < target:
                    prev = step
                    step += int(math.sqrt(n))
                    if prev >= n: return -1
                while arr[prev] < target:
                    prev += 1
                    if prev == min(step, n): return -1
                if arr[prev] == target: return prev
                return -1
        """).strip(),
        "dry_run": "1. Size N=9, step size is $\sqrt{9}=3$.\n2. Compare index 2. Target is larger, jump to index 5. Target is smaller, run linear search backward.\n3. Scans indices 3 and 4, locates target.",
        "complexity": "| Metric | Complexity |\n| :--- | :--- |\n| Time Complexity | $O(\\sqrt{N})$ |\n| Space Complexity | $O(1)$ |",
        "edge_cases": "• **Step Size choice:** Step sizes too small degrade performance to linear. Step sizes too large degrade search to binary boundaries. $\sqrt{N}$ is mathematically optimal."
    },
    "interpolation_search": {
        "title": "Interpolation Search",
        "category": "Searching Algorithms",
        "concept": "Interpolation Search is an optimized version of binary search for **uniformly distributed** sorted arrays. It estimates the target's position (similar to looking up 'Z' near the back of a dictionary), achieving $O(\log \log N)$ search time.",
        "code": textwrap.dedent("""
            def interpolation_search(arr, target):
                low, high = 0, len(arr) - 1
                while low <= high and target >= arr[low] and target <= arr[high]:
                    # Estimate index mathematically
                    pos = low + int(((high - low) / (arr[high] - arr[low])) * (target - arr[low]))
                    if arr[pos] == target: return pos
                    if arr[pos] < target: low = pos + 1
                    else: high = pos - 1
                return -1
        """).strip(),
        "dry_run": "1. Uniform array `[10, 20, 30, 40]`, target 30.\n2. Formula predicts position: `pos = 0 + ((3/30) * 20) = 2`.\n3. Checks `arr[2] = 30`. Targets matches in exactly 1 comparison!",
        "complexity": "| Distribution | Time Complexity | Worst Case (skewed) |\n| :--- | :--- | :--- |\n| **Uniform** | $O(\log \log N)$ | $O(N)$ |\n| Space Complexity | $O(1)$ | $O(1)$ |",
        "edge_cases": "• **Non-Uniform Datasets:** On skewed distributions (e.g. `[1, 2, 1000, 1001]`), index calculations skew incorrectly, causing search time to slow to $O(N)$."
    },
    "exponential_search": {
        "title": "Exponential Search",
        "category": "Searching Algorithms",
        "concept": "Exponential Search is ideal for sorted arrays of **infinite or unbounded size**. It finds a small range where the target resides by doubling indices exponentially (`1, 2, 4, 8...`), and then runs binary search within that range.",
        "code": textwrap.dedent("""
            def exponential_search(arr, target):
                n = len(arr)
                if n == 0: return -1
                if arr[0] == target: return 0
                i = 1
                while i < n and arr[i] <= target:
                    i *= 2
                return binary_search_slice(arr, target, i // 2, min(i, n - 1))
        """).strip(),
        "dry_run": "1. Target is 13. Index `i` doubles: 1, 2, 4, 8, 16. Stop since `arr[16] > 13`.\n2. Binary search runs within bounds `[8, 16]`.\n3. Locates target efficiently.",
        "complexity": "| Metric | Complexity |\n| :--- | :--- |\n| Time Complexity | $O(\log I)$ (I is target index position) |\n| Space Complexity | $O(1)$ |",
        "edge_cases": "• **Bound overflow:** Ensure boundary checks use `min(i, n - 1)` to prevent list index errors."
    },

    # 6. Sorting Algorithms
    "bubble_sort": {
        "title": "Bubble Sort",
        "category": "Sorting Algorithms",
        "concept": "Bubble Sort is a simple, comparison-based sorting algorithm. It repeatedly steps through the list, compares adjacent elements, and swaps them if they are in the wrong order. Large elements 'bubble' to the top in each pass.",
        "code": textwrap.dedent("""
            def bubble_sort(arr):
                n = len(arr)
                for i in range(n):
                    swapped = False
                    for j in range(0, n-i-1):
                        if arr[j] > arr[j+1]:
                            arr[j], arr[j+1] = arr[j+1], arr[j]
                            swapped = True
                    if not swapped: break # Optimized early exit
                return arr
        """).strip(),
        "dry_run": "1. Array `[4, 2, 5]`. Compare indices 0 and 1: `4 > 2`, swap -> `[2, 4, 5]`.\n2. Compare indices 1 and 2: `4 < 5`, no swap. Loop continues.\n3. Early exit flag `swapped` evaluates as False. Sort finishes.",
        "complexity": "| Condition | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Best Case (Sorted) | $O(N)$ | $O(1)$ |\n| Worst Case (Reversed) | $O(N^2)$ | $O(1)$ |",
        "edge_cases": "• **Early Exit Optimization:** Un-optimized bubble sort always runs in $O(N^2)$ time. Implement a `swapped` flag to exit early if a pass completes without any swaps."
    },
    "selection_sort": {
        "title": "Selection Sort",
        "category": "Sorting Algorithms",
        "concept": "Selection Sort divides the array into sorted and unsorted segments. It repeatedly finds the minimum element from the unsorted segment and swaps it into the sorted segment.",
        "code": textwrap.dedent("""
            def selection_sort(arr):
                n = len(arr)
                for i in range(n):
                    min_idx = i
                    for j in range(i+1, n):
                        if arr[j] < arr[min_idx]:
                            min_idx = j
                    arr[i], arr[min_idx] = arr[min_idx], arr[i]
                return arr
        """).strip(),
        "dry_run": "1. Unsorted array `[64, 25, 12]`. Scan index 0 to 2, find minimum element `12`.\n2. Swap index 0 with minimum element -> `[12, 25, 64]`.\n3. Scan remaining elements, indices already sorted.",
        "complexity": "| Condition | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| All Cases | $O(N^2)$ | $O(1)$ |\n| Stability | Unstable | |",
        "edge_cases": "• **Inefficient Swaps:** Selection sort performs swaps even if elements are already in their correct positions. Guard swaps with `if min_idx != i:`."
    },
    "insertion_sort": {
        "title": "Insertion Sort",
        "category": "Sorting Algorithms",
        "analogy": "Sorting a hand of playing cards. You pick one card at a time and slide it into its correct position relative to the sorted cards in your other hand.",
        "concept": "Insertion Sort builds a sorted array one element at a time. It takes each new element and inserts it into its correct position relative to the sorted segment by shifting larger elements forward.",
        "code": textwrap.dedent("""
            def insertion_sort(arr):
                for i in range(1, len(arr)):
                    key = arr[i]
                    j = i - 1
                    while j >= 0 and key < arr[j]:
                        arr[j + 1] = arr[j]
                        j -= 1
                    arr[j + 1] = key
                return arr
        """).strip(),
        "dry_run": "1. Array `[5, 2, 9]`. `key=2`, compare with 5. `2 < 5`, shift 5 forward: `[5, 5, 9]`.\n2. Insert key at index 0 -> `[2, 5, 9]`.\n3. Next key is 9. `9 > 5`, remains in place.",
        "complexity": "| Condition | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Best Case (Sorted) | $O(N)$ | $O(1)$ |\n| Worst Case | $O(N^2)$ | $O(1)$ |",
        "edge_cases": "• **Partially Sorted Arrays:** Insertion sort is highly efficient for partially sorted arrays, outperforming advanced algorithms like Quick Sort in these specific scenarios."
    },
    "merge_sort": {
        "title": "Merge Sort",
        "category": "Sorting Algorithms",
        "concept": "Merge Sort is a stable, divide-and-conquer algorithm. It recursively splits the array in half until it reaches single-element lists, and then merges these sorted sublists back together.",
        "code": textwrap.dedent("""
            def merge_sort(arr):
                if len(arr) <= 1: return arr
                mid = len(arr) // 2
                left = merge_sort(arr[:mid])
                right = merge_sort(arr[mid:])
                return merge(left, right)
            
            def merge(left, right):
                res = []
                i = j = 0
                while i < len(left) and j < len(right):
                    if left[i] < right[j]:
                        res.append(left[i]); i += 1
                    else:
                        res.append(right[j]); j += 1
                res.extend(left[i:])
                res.extend(right[j:])
                return res
        """).strip(),
        "dry_run": "1. Array `[4, 2, 1, 3]` split into `[4, 2]` and `[1, 3]`.\n2. Splits further to single units. Merge `[4]` and `[2]` into sorted `[2, 4]`.\n3. Merge `[2, 4]` and `[1, 3]`: compares indices, yields sorted `[1, 2, 3, 4]`.",
        "complexity": "| Condition | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| All Cases | $O(N \log N)$ | $O(N)$ |\n| Stability | Stable | |",
        "edge_cases": "• **Memory Allocation:** Merge sort requires allocating temporary arrays of size $N$ during the merge phase. For memory-constrained systems, prefer in-place algorithms like Quick Sort."
    },
    "quick_sort": {
        "title": "Quick Sort",
        "category": "Sorting Algorithms",
        "concept": "Quick Sort is a divide-and-conquer algorithm. It selects a 'pivot' element, partitions the array into elements smaller and larger than the pivot, and recursively sorts these sub-partitions in-place.",
        "code": textwrap.dedent("""
            def quick_sort(arr):
                if len(arr) <= 1: return arr
                pivot = arr[len(arr) // 2]
                left = [x for x in arr if x < pivot]
                middle = [x for x in arr if x == pivot]
                right = [x for x in arr if x > pivot]
                return quick_sort(left) + middle + quick_sort(right)
        """).strip(),
        "dry_run": "1. Array `[3, 6, 2, 8]`. Pivot is index 2 (`2`).\n2. Partition: left `[]`, middle `[2]`, right `[3, 6, 8]`.\n3. Recursively sort right partition. Pivot is `6`. Yields `[3] + [6] + [8]`.\n4. Concatenate segments: `[2, 3, 6, 8]`.",
        "complexity": "| Condition | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Average Case | $O(N \log N)$ | $O(\log N)$ (recursion stack) |\n| Worst Case (Sorted) | $O(N^2)$ | $O(N)$ |\n| Stability | Unstable | |",
        "edge_cases": "• **Worst-case Mitigation:** Sorting already sorted arrays using the first element as pivot degrades performance to $O(N^2)$. Modern engines choose random or median pivots to maintain $O(N \log N)$ speed."
    },
    "heap_sort": {
        "title": "Heap Sort",
        "category": "Sorting Algorithms",
        "concept": "Heap Sort is a comparison-based sorting algorithm. It builds a Max-Heap from the input array, repeatedly extracts the maximum element (root), and restores the heap property, sorting in-place.",
        "code": textwrap.dedent("""
            def heapify(arr, n, i):
                largest = i
                l = 2 * i + 1
                r = 2 * i + 2
                if l < n and arr[l] > arr[largest]: largest = l
                if r < n and arr[r] > arr[largest]: largest = r
                if largest != i:
                    arr[i], arr[largest] = arr[largest], arr[i]
                    heapify(arr, n, largest)
        """).strip(),
        "dry_run": "1. Build Max-Heap from input array.\n2. Swap the largest element at root index 0 with the last element of the heap array.\n3. Decrement heap size, run `heapify` on root node to restore Max-Heap property.",
        "complexity": "| Condition | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| All Cases | $O(N \log N)$ | $O(1)$ |\n| Stability | Unstable | |",
        "edge_cases": "• **In-place Sorting:** Heap sort is highly efficient because it sorts in-place with zero external memory allocation ($O(1)$ space), outperforming merge sort in memory-restricted systems."
    },
    "counting_sort": {
        "title": "Counting Sort",
        "category": "Sorting Algorithms",
        "concept": "Counting Sort is a non-comparison based sorting algorithm. It counts the occurrences of each unique value in a frequency array, and calculates their sorted positions, achieving linear time complexity.",
        "code": textwrap.dedent("""
            def counting_sort(arr):
                if not arr: return arr
                max_val = max(arr)
                count = [0] * (max_val + 1)
                for num in arr: count[num] += 1
                res = []
                for val, freq in enumerate(count):
                    res.extend([val] * freq)
                return res
        """).strip(),
        "dry_run": "1. Array `[1, 4, 1]`, max element is 4. Frequencies: `count = [0, 2, 0, 0, 1]`.\n2. Iterates over frequency count array: 0 zeros, 2 ones, 1 four.\n3. Rebuilds sorted array: `[1, 1, 4]`.",
        "complexity": "| Phase | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Sorting | $O(N + K)$ (K is max value) | $O(N + K)$ |\n| Stability | Stable | |",
        "edge_cases": "• **Large Range Keys:** If the array contains a huge element (e.g. `[1, 2, 1000000]`), counting sort will attempt to allocate a massive frequency array of size 1,000,000, exhausting memory. Use only on bounded, small range keys."
    },
    "radix_sort": {
        "title": "Radix Sort",
        "category": "Sorting Algorithms",
        "concept": "Radix Sort is a non-comparison based sorting algorithm. It sorts integers digit-by-digit, starting from the least significant digit (LSD) to the most significant digit, using a stable sorting algorithm (like counting sort) as a subroutine.",
        "code": textwrap.dedent("""
            def radix_sort(arr):
                if not arr: return arr
                max_val = max(arr)
                exp = 1
                while max_val // exp > 0:
                    counting_sort_by_digit(arr, exp)
                    exp *= 10
        """).strip(),
        "dry_run": "1. Array `[170, 45, 75]`. First pass: sort by units digit `[170, 45, 75]`.\n2. Second pass: sort by tens digit `[170, 45, 75]`.\n3. Third pass: sort by hundreds digit `[45, 75, 170]`. Yields sorted array.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Radix sort | $O(D \cdot (N + K))$ (D is digit count) |\n| Space Complexity | $O(N + K)$ |",
        "edge_cases": "• **Negative Integers:** Standard Radix Sort assumes positive integers. For negative numbers, sort negative and positive elements separately and concatenate the results."
    },
    "bucket_sort": {
        "title": "Bucket Sort",
        "category": "Sorting Algorithms",
        "concept": "Bucket Sort distributes array elements into multiple 'buckets'. Each bucket is then sorted individually (using another sorting algorithm like insertion sort), and the elements are concatenated to form the sorted array.",
        "code": textwrap.dedent("""
            def bucket_sort(arr):
                if not arr: return arr
                bucket_count = len(arr)
                buckets = [[] for _ in range(bucket_count)]
                for val in arr:
                    # Distribute elements uniformly
                    idx = int(val * bucket_count)
                    buckets[min(idx, bucket_count - 1)].append(val)
                for b in buckets: b.sort()
                res = []
                for b in buckets: res.extend(b)
                return res
        """).strip(),
        "dry_run": "1. Array `[0.42, 0.32, 0.75]`. Create 3 buckets.\n2. Distribute: `0.32` to bucket 0, `0.42` to bucket 1, `0.75` to bucket 2.\n3. Sort each bucket and concatenate: `[0.32, 0.42, 0.75]`.",
        "complexity": "| Distribution | Time Complexity | Worst Case (skewed) |\n| :--- | :--- | :--- |\n| **Uniform** | $O(N + K)$ | $O(N^2)$ |\n| Space Complexity | $O(N + K)$ | $O(N + K)$ |",
        "edge_cases": "• **Non-Uniform Datasets:** If all elements are clustered tightly (e.g. `[0.91, 0.92, 0.93]`), they will all fall into a single bucket, degrading Bucket Sort to the speed of the underlying sorting algorithm."
    },

    # 7. Recursion & Backtracking
    "recursive_thinking": {
        "title": "Recursive Thinking & base cases",
        "category": "Recursion & Backtracking",
        "concept": "Recursive Thinking is the process of breaking a problem down into smaller, self-similar subproblems. Every recursive function must define a **Base Case** to stop execution and prevent infinite loops.",
        "code": textwrap.dedent("""
            def sum_recursive(n):
                # Base Case: Stop recursion when n is 0
                if n == 0: return 0
                # Recursive Step: Reduce problem size
                return n + sum_recursive(n - 1)
        """).strip(),
        "dry_run": "1. Call `sum_recursive(2)` -> returns `2 + sum_recursive(1)`.\n2. Call `sum_recursive(1)` -> returns `1 + sum_recursive(0)`.\n3. Call `sum_recursive(0)` -> base case matched, returns `0`.\n4. Resolves: `1 + 0 = 1` -> `2 + 1 = 3`.",
        "complexity": "| Operation | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Sum recursive | $O(N)$ | $O(N)$ (call stack depth) |",
        "edge_cases": "• **Infinite Loops:** Bypassing base cases causes the call stack to exceed Python's recursion limit, raising `RecursionError`."
    },
    "base_case": {
        "title": "Base Cases in Recursion",
        "category": "Recursion & Backtracking",
        "concept": "The Base Case is the anchor of a recursive function. It returns a value directly without making further recursive calls, unwinding the call stack and returning values back up the execution chain.",
        "code": textwrap.dedent("""
            # Base Case preventing infinite loop
            def count_down(n):
                if n <= 0:
                    print("Go!")
                    return # Base case exit
                print(n)
                count_down(n - 1)
        """).strip(),
        "dry_run": "1. Call `count_down(1)` -> prints 1, calls `count_down(0)`.\n2. Call `count_down(0)` -> matches base case `n <= 0`, prints 'Go!', returns, unwinding stack.",
        "complexity": "| Phase | Complexity |\n| :--- | :--- |\n| Time Complexity | $O(N)$ |\n| Space Complexity | $O(N)$ (stack frames) |",
        "edge_cases": "• **Incorrect boundaries:** Using exact equality checks like `if n == 0:` can cause infinite loops if `n` is negative or a float. Use range inequality checks like `if n <= 0:`."
    },
    "n_queens": {
        "title": "N-Queens Solver (Backtracking)",
        "category": "Recursion & Backtracking",
        "analogy": "Solving a puzzle by pencil: you draw a line, and if you get stuck, you erase your last few lines and try a different path until you solve it.",
        "concept": "The N-Queens puzzle is the problem of placing N chess queens on an N×N chessboard so that no two queens threaten each other. It is solved using backtracking: trying a placement, and undoing it (backtracking) if it leads to an invalid board state.",
        "code": textwrap.dedent("""
            def solve_n_queens(n):
                board = [["."] * n for _ in range(n)]
                res = []
                def backtrack(r, cols, pos_diag, neg_diag):
                    if r == n:
                        res.append(["".join(row) for row in board])
                        return
                    for c in range(n):
                        if c in cols or (r+c) in pos_diag or (r-c) in neg_diag: continue
                        board[r][c] = "Q"
                        cols.add(c); pos_diag.add(r+c); neg_diag.add(r-c)
                        backtrack(r + 1, cols, pos_diag, neg_diag)
                        # Backtrack (undo state)
                        board[r][c] = "."
                        cols.remove(c); pos_diag.remove(r+c); neg_diag.remove(r-c)
                backtrack(0, set(), set(), set())
                return res
        """).strip(),
        "dry_run": "1. Try placing Queen in row 0, column 0.\n2. Move to row 1. Try placing Queen in column 2 (column 0 and 1 are threatened).\n3. If row 3 placements are all blocked, backtrack: remove Queen from row 1, column 2, and try another slot.",
        "complexity": "| Operation | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| N-Queens Solver | $O(N!)$ | $O(N^2)$ (board state) |",
        "edge_cases": "• **No Solution Boards:** For $N=2$ and $N=3$, the algorithm runs exhaustively and returns an empty list `[]` (no valid placements possible)."
    },
    "sudoku_solver": {
        "title": "Sudoku Solver (Backtracking)",
        "category": "Recursion & Backtracking",
        "concept": "Sudoku Solver uses backtracking. It finds an empty cell, tries digits 1-9, verifies constraints, and recursively attempts to solve the board. If it gets stuck, it backtracks and tries the next number.",
        "code": textwrap.dedent("""
            def solve_sudoku(board):
                for r in range(9):
                    for c in range(9):
                        if board[r][c] == ".":
                            for num in map(str, range(1, 10)):
                                if is_valid(board, r, c, num):
                                    board[r][c] = num
                                    if solve_sudoku(board): return True
                                    board[r][c] = "." # Backtrack
                            return False
                return True
        """).strip(),
        "dry_run": "1. Scan board, locate empty cell at row 0, column 2.\n2. Try placing number '3'. Check if unique in row, column, and 3x3 grid. Yes.\n3. Set `board[0][2] = '3'`, recursively solve next cell. If it fails, reset cell to `'.'`.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Sudoku Solver | $O(9^{N})$ (N is empty cells) |\n| Space Complexity | $O(1)$ (Fixed 9x9 board size) |",
        "edge_cases": "• **Unsolvable Board Input:** If the initial board violates Sudoku rules (e.g. duplicate numbers in a row), the solver will return `False` immediately."
    },
    "permutations": {
        "title": "Permutations (Backtracking)",
        "category": "Recursion & Backtracking",
        "concept": "Permutations represent all possible ordered arrangements of a set of elements. They are generated recursively by swapping elements or tracking visited states.",
        "code": textwrap.dedent("""
            def permute(nums):
                res = []
                def backtrack(path, remaining):
                    if not remaining:
                        res.append(path)
                        return
                    for i in range(len(remaining)):
                        backtrack(path + [remaining[i]], remaining[:i] + remaining[i+1:])
                backtrack([], nums)
                return res
        """).strip(),
        "dry_run": "1. `nums=[1, 2]`. Call `backtrack([], [1, 2])`.\n2. Loop index 0: call `backtrack([1], [2])` -> yields `[1, 2]`.\n3. Loop index 1: call `backtrack([2], [1])` -> yields `[2, 1]`.\n4. Returns list of all arrangements.",
        "complexity": "| Operation | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Permutations | $O(N!)$ | $O(N!)$ |",
        "edge_cases": "• **Duplicate Inputs:** If input arrays contain duplicate numbers (e.g. `[1, 1, 2]`), sorting the array and skipping duplicates in loops is required to avoid duplicate arrangements."
    },
    "combinations": {
        "title": "Combinations (Backtracking)",
        "category": "Recursion & Backtracking",
        "concept": "Combinations represent all possible selections of $K$ elements from a set of $N$ elements, where order does not matter.",
        "code": textwrap.dedent("""
            def combine(n, k):
                res = []
                def backtrack(start, path):
                    if len(path) == k:
                        res.append(path)
                        return
                    for i in range(start, n + 1):
                        backtrack(i + 1, path + [i])
                backtrack(1, [])
                return res
        """).strip(),
        "dry_run": "1. `combine(3, 2)` -> call `backtrack(1, [])`.\n2. Branch 1: `path=[1]`, call `backtrack(2, [1])`.\n3. Branch 1-1: `path=[1, 2]`. Match length 2, append to results.",
        "complexity": "| Operation | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Combinations | $O(\\binom{N}{K})$ | $O(\\binom{N}{K})$ |",
        "edge_cases": "• **Invalid Ranges:** If $K > N$ or $K < 0$, combinations are mathematically impossible; the algorithm should return `[]` instantly."
    },

    # 8. Graph Algorithms
    "bfs": {
        "title": "Breadth-First Search (BFS)",
        "category": "Graph Algorithms",
        "analogy": "A drop of water spreading outward in a pool: it wet all immediately adjacent ripples before moving to the next concentric layer.",
        "concept": "BFS is a graph traversal algorithm. It starts at a designated node and explores all of its neighbors at the current depth level before moving to nodes at the next depth level. It uses a **Queue** (FIFO) to manage traversal.",
        "code": textwrap.dedent("""
            from collections import deque
            def bfs(graph, start):
                visited = {start}
                queue = deque([start])
                while queue:
                    node = queue.popleft()
                    print(node, end=" ")
                    for neighbor in graph.get(node, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
        """).strip(),
        "dry_run": "1. Start `queue = deque(['A'])`, `visited = {'A'}`.\n2. Dequeue `'A'`. Neighbors are `'B'`, `'C'`. Mark visited, enqueue both. Queue: `['B', 'C']`.\n3. Dequeue `'B'`. Neighbors are `'A'` (visited), `'D'`. Enqueue `'D'`. Queue: `['C', 'D']`.\n4. Traversal runs level-by-level.",
        "complexity": "| Phase | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| BFS Traversal | $O(V + E)$ | $O(V)$ |\n| Space Complexity | $O(V)$ | |",
        "edge_cases": "• **Disconnected Graphs:** BFS starting at A will never reach nodes in disconnected segments. Loop over all graph keys to ensure full traversal."
    },
    "dfs": {
        "title": "Depth-First Search (DFS)",
        "category": "Graph Algorithms",
        "analogy": "Exploring a maze: you walk down a single path as far as you can until you hit a dead end, and then backtrack to try the last fork in the road.",
        "concept": "DFS is a graph traversal algorithm. It starts at a designated node and explores as deep as possible along each branch before backtracking. It uses recursion or a **Stack** (LIFO) to manage traversal.",
        "code": textwrap.dedent("""
            def dfs(graph, start, visited=None):
                if visited is None: visited = set()
                visited.add(start)
                print(start, end=" ")
                for neighbor in graph.get(start, []):
                    if neighbor not in visited:
                        dfs(graph, neighbor, visited)
        """).strip(),
        "dry_run": "1. Call `dfs('A')` -> marks `'A'` visited. Neighbors are `'B'`, `'C'`.\n2. Call `dfs('B')` (first neighbor) -> marks `'B'` visited. Neighbors is `'D'`.\n3. Call `dfs('D')` -> dead end, return back to `'B'` -> return back to `'A'`.\n4. Call `dfs('C')` -> marks `'C'` visited.",
        "complexity": "| Phase | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| DFS Traversal | $O(V + E)$ | $O(V)$ (call stack depth) |\n| Space Complexity | $O(V)$ | |",
        "edge_cases": "• **Cycles:** Graphs with cyclic loops will cause infinite recursion and crash if you fail to maintain a `visited` set to track traversed nodes."
    },
    "dijkstra": {
        "title": "Dijkstra's Shortest Path Algorithm",
        "category": "Graph Algorithms",
        "analogy": "Google Maps calculating the fastest driving route from your home to a restaurant, scanning different highway combinations based on mileage and traffic delays.",
        "concept": "Dijkstra's algorithm finds the shortest path from a single source node to all other nodes in a weighted graph with non-negative edge weights. It uses a **Min-Priority Queue** to repeatedly select the closest unvisited node and relax its neighbors.",
        "code": textwrap.dedent("""
            import heapq
            def dijkstra(graph, start):
                # Min-Priority queue storing (distance, node) pairs
                pq = [(0, start)]
                distances = {node: float('inf') for node in graph}
                distances[start] = 0
                visited = set()
                
                while pq:
                    dist, u = heapq.heappop(pq)
                    if u in visited: continue
                    visited.add(u)
                    
                    for neighbor, weight in graph.get(u, []):
                        if neighbor in visited: continue
                        new_dist = dist + weight
                        if new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist
                            heapq.heappush(pq, (new_dist, neighbor))
                return distances
        """).strip(),
        "dry_run": "1. `pq = [(0, 'A')]`, `distances = {'A': 0, 'B': inf, 'C': inf}`.\n2. Pop `'A'`. Neighbors are `('B', 4)` and `('C', 1)`.\n3. Relax B: `new_dist = 0 + 4 = 4 < inf`. Update B to 4, push `(4, 'B')`.\n4. Relax C: `new_dist = 0 + 1 = 1 < inf`. Update C to 1, push `(1, 'C')`.\n5. Pop C next because it has the minimum distance. Recursively relax neighbors.",
        "complexity": "| Priority Queue Implementation | Time Complexity |\n| :--- | :--- |\n| Min-Heap (standard) | $O((V + E) \log V)$ |\n| Fibonacci Heap (theoretical) | $O(E + V \log V)$ |\n| Space Complexity | $O(V)$ |",
        "edge_cases": "• **Negative Weights:** Dijkstra's algorithm assumes non-negative weights. If negative edges exist, the algorithm can loop infinitely, updating distances incorrectly. Use the Bellman-Ford algorithm instead."
    },
    "bellman_ford": {
        "title": "Bellman-Ford Algorithm",
        "category": "Graph Algorithms",
        "concept": "The Bellman-Ford algorithm calculates shortest paths from a single source node in a weighted graph. Unlike Dijkstra's, it **handles negative edge weights** and can detect negative cycles (cycles where the total weight is negative).",
        "code": textwrap.dedent("""
            def bellman_ford(vertices, edges, start):
                dist = {i: float('inf') for i in range(vertices)}
                dist[start] = 0
                # Relax all edges V-1 times
                for _ in range(vertices - 1):
                    for u, v, w in edges:
                        if dist[u] != float('inf') and dist[u] + w < dist[v]:
                            dist[v] = dist[u] + w
                # Check for negative weight cycles
                for u, v, w in edges:
                    if dist[u] != float('inf') and dist[u] + w < dist[v]:
                        raise ValueError("Graph contains a negative weight cycle!")
                return dist
        """).strip(),
        "dry_run": "1. Set all distances to `inf`, except `start = 0`.\n2. Iterate through all edges, updating `dist[v] = min(dist[v], dist[u] + weight)`.\n3. Run a final pass: if a distance can still be reduced, it means a negative cycle exists, reducing path weights infinitely.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Shortest path | $O(V \cdot E)$ |\n| Space Complexity | $O(V)$ |",
        "edge_cases": "• **Negative Weight Cycle Detection:** If the graph has a cycle whose total edge sum is negative, paths can be relaxed infinitely. Bellman-Ford detects this and raises an error to prevent infinite loops."
    },
    "floyd_warshall": {
        "title": "Floyd-Warshall Algorithm",
        "category": "Graph Algorithms",
        "concept": "The Floyd-Warshall algorithm computes shortest paths between **all pairs of vertices** in a weighted graph in $O(V^3)$ time, utilizing dynamic programming.",
        "code": textwrap.dedent("""
            def floyd_warshall(graph, v):
                # Initialize distance matrix
                dist = [[float('inf')] * v for _ in range(v)]
                for i in range(v): dist[i][i] = 0
                for u in graph:
                    for v_node, w in graph[u]:
                        dist[u][v_node] = w
                
                # DP transitions
                for k in range(v):
                    for i in range(v):
                        for j in range(v):
                            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
                return dist
        """).strip(),
        "dry_run": "1. Initialize $V \times V$ distance grid.\n2. For each intermediate vertex `k`, check if routing from `i` to `j` via `k` (`dist[i][k] + dist[k][j]`) is shorter than the direct path `dist[i][j]`.\n3. Update matrix value with minimum distance.",
        "complexity": "| Phase | Complexity |\n| :--- | :--- |\n| Time Complexity | $O(V^3)$ |\n| Space Complexity | $O(V^2)$ |",
        "edge_cases": "• **Negative Cycles:** Floyd-Warshall detects negative cycles if diagonal values `dist[i][i]` become negative (meaning a node can travel to itself with a net-negative cost)."
    },
    "kruskal": {
        "title": "Kruskal's Minimum Spanning Tree (MST)",
        "category": "Graph Algorithms",
        "concept": "Kruskal's algorithm finds a Minimum Spanning Tree (MST) for a connected, weighted undirected graph. It sorts all edges by weight and uses a **Disjoint Set (Union-Find)** to add edges one-by-one, ensuring no cycles are created.",
        "code": textwrap.dedent("""
            def kruskal(vertices, edges):
                # edges is list of tuples: (weight, u, v)
                edges.sort()
                ds = DisjointSet(vertices)
                mst = []
                mst_cost = 0
                for w, u, v in edges:
                    if ds.find(u) != ds.find(v):
                        ds.union(u, v)
                        mst.append((u, v, w))
                        mst_cost += w
                return mst, mst_cost
        """).strip(),
        "dry_run": "1. Sort all edges in ascending order of weight.\n2. Iterate through sorted edges. Check if endpoints `u` and `v` belong to the same subset using `ds.find(u) == ds.find(v)`.\n3. If they belong to different subsets, merge them using `ds.union()` and append the edge to the MST. If they are in the same subset, skip the edge to avoid creating a cycle.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Sort edges | $O(E \log E)$ |\n| Union-Find checks | $O(E \cdot \\alpha(V))$ |\n| Total Complexity | $O(E \log E)$ or $O(E \log V)$ |\n| Space Complexity | $O(V)$ |",
        "edge_cases": "• **Disconnected Graphs:** Kruskal's algorithm will only find a Minimum Spanning Forest (MSF) if the graph is disconnected. Ensure the graph is connected before running MST."
    },
    "prim": {
        "title": "Prim's Minimum Spanning Tree (MST)",
        "category": "Graph Algorithms",
        "concept": "Prim's algorithm finds a Minimum Spanning Tree (MST) for a connected, weighted undirected graph. It grows the MST one vertex at a time, starting from a random node and repeatedly adding the cheapest edge that connects a vertex in the MST to a vertex outside the MST.",
        "code": textwrap.dedent("""
            import heapq
            def prim(graph, start):
                mst = []
                visited = {start}
                # Min-Priority queue storing (weight, u, v)
                edges = [(w, start, v) for v, w in graph.get(start, [])]
                heapq.heapify(edges)
                
                while edges:
                    w, u, v = heapq.heappop(edges)
                    if v in visited: continue
                    visited.add(v)
                    mst.append((u, v, w))
                    
                    for next_node, weight in graph.get(v, []):
                        if next_node not in visited:
                            heapq.heappush(edges, (weight, v, next_node))
                return mst
        """).strip(),
        "dry_run": "1. Mark `start` visited. Load neighbors' edges into the min-priority queue.\n2. Pop the cheapest edge `(weight, u, v)`. If target node `v` is unvisited, add it to the MST.\n3. Load `v`'s neighbors into the queue, repeat until all vertices are visited.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Pop cheap edge | $O(E \log V)$ |\n| Space Complexity | $O(V + E)$ |",
        "edge_cases": "• **Graph Connection:** If the input graph is disconnected, Prim's will only traverse the connected component containing the start node, failing to span all vertices."
    },
    "topological_sort": {
        "title": "Topological Sort",
        "category": "Graph Algorithms",
        "concept": "Topological Sort linearly orders the vertices of a Directed Acyclic Graph (DAG) such that for every directed edge $U \rightarrow V$, vertex $U$ comes before $V$. It is commonly used for scheduling task dependencies.",
        "code": textwrap.dedent("""
            def topological_sort_dfs(v, adj):
                visited = set()
                stack = []
                def dfs_helper(node):
                    visited.add(node)
                    for neighbor in adj.get(node, []):
                        if neighbor not in visited:
                            dfs_helper(neighbor)
                    stack.append(node) # Push to stack when all neighbors finished
                for i in range(v):
                    if i not in visited:
                        dfs_helper(i)
                return stack[::-1] # Reverse stack to get topological order
        """).strip(),
        "dry_run": "1. Run DFS starting at vertex 0.\n2. Traverse neighbors recursively. When a node's neighbors are fully visited (e.g. leaf node 2), push node 2 to the stack.\n3. Complete traversals. Reversing the stack yields the correct dependency order.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Topological Sort | $O(V + E)$ |\n| Space Complexity | $O(V)$ (recursion stack depth) |",
        "edge_cases": "• **Cycle Presence:** Running topological sort on graphs with cyclic dependencies yields invalid orderings. Always verify the graph is a DAG before sorting."
    },
    "cycle_detection": {
        "title": "Cycle Detection",
        "category": "Graph Algorithms",
        "concept": "Cycle Detection checks if a graph contains any cycles. It is commonly implemented using DFS with a recursion stack (for directed graphs) or parent trackers (for undirected graphs).",
        "code": textwrap.dedent("""
            # Undirected cycle detection using DFS with parent tracker
            def is_cyclic_undirected(node, parent, adj, visited):
                visited.add(node)
                for neighbor in adj.get(node, []):
                    if neighbor not in visited:
                        if is_cyclic_undirected(neighbor, node, adj, visited):
                            return True
                    elif neighbor != parent:
                        return True # Cycle detected! (visited neighbor is not parent)
                return False
        """).strip(),
        "dry_run": "1. Run DFS. Traverse node `A` to `B`. Set `parent = A`.\n2. Traverse `B` to `C`. Set `parent = B`.\n3. If `C` has neighbor `A` (already visited) and `A != parent` (A is not B), a cycle is detected.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Cycle Detection | $O(V + E)$ |\n| Space Complexity | $O(V)$ |",
        "edge_cases": "• **Isolated Cyclic Subgraphs:** Ensure the cycle detector iterates over all vertices in the graph to find cycles in disconnected subgraphs."
    },
    "shortest_path": {
        "title": "Shortest Path Algorithms",
        "category": "Graph Algorithms",
        "concept": "Shortest Path algorithms calculate the path with the minimum edge sum between vertices. The choice of algorithm depends on graph properties:\n1. **BFS:** Best for unweighted graphs ($O(V + E)$ time).\n2. **Dijkstra:** Best for weighted graphs with non-negative weights ($O((V+E)\log V)$ time).\n3. **Bellman-Ford:** Handles negative weights and detects negative cycles ($O(V \cdot E)$ time).\n4. **Floyd-Warshall:** Calculates shortest paths between all pairs of nodes ($O(V^3)$ time).",
        "code": textwrap.dedent("""
            # Chooses BFS for unweighted hops, Dijkstra for weighted routes
            def resolve_shortest_path(graph, start, end, weighted=False):
                if not weighted:
                    return shortest_path_unweighted(graph, start, end)
                else:
                    return dijkstra(graph, start)
        """).strip(),
        "dry_run": "1. Check if graph has weights. If unweighted, run BFS to find the path with the minimum number of edge hops.\n2. If weighted, run Dijkstra's algorithm to calculate the route with the lowest total edge weight.",
        "complexity": "| Algorithm | Time Complexity | Best Case Scenario |\n| :--- | :--- | :--- |\n| **BFS** | $O(V + E)$ | Unweighted hops |\n| **Dijkstra** | $O((V+E)\log V)$ | Weighted, non-negative edges |\n| **Bellman-Ford** | $O(V \cdot E)$ | Handles negative weights |\n| **Floyd-Warshall** | $O(V^3)$ | All-pairs shortest paths |",
        "edge_cases": "• **Zero-Weight Cycles:** Graphs with loops whose total weight is 0 can cause Dijkstra to loop infinitely if visited states are not tracked correctly."
    },

    # 9. Dynamic Programming
    "memoization": {
        "title": "DP: Memoization (Top-Down)",
        "category": "Dynamic Programming",
        "concept": "Memoization is a top-down dynamic programming technique. It starts with standard recursion and caches computed subproblem results in a hashmap or array, preventing redundant calculations.",
        "code": textwrap.dedent("""
            # Top-down memoized Fibonacci
            def fib_memo(n, memo=None):
                if memo is None: memo = {}
                if n in memo: return memo[n] # Return cached result
                if n <= 0: return 0
                if n == 1: return 1
                memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
                return memo[n]
        """).strip(),
        "dry_run": "1. `fib_memo(5)` calls `fib_memo(4)` and `fib_memo(3)`.\n2. When calculating `fib_memo(4)`, it computes and caches the result of `fib_memo(3)` in `memo`.\n3. The subsequent `fib_memo(3)` call returns the cached result instantly, skipping duplicate subtree calculations.",
        "complexity": "| Operation | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Memoized | $O(N)$ | $O(N)$ (recursion stack + cache) |",
        "edge_cases": "• **Recursion Limit:** For very large inputs (e.g. `n > 1000`), top-down memoization raises a `RecursionError`. Use bottom-up tabulation to avoid recursion limits."
    },
    "tabulation": {
        "title": "DP: Tabulation (Bottom-Up)",
        "category": "Dynamic Programming",
        "concept": "Tabulation is a bottom-up dynamic programming technique. It builds a table iteratively, starting from the smallest base cases and filling the grid until it reaches the target solution, avoiding recursive stack overhead.",
        "code": textwrap.dedent("""
            # Bottom-up tabulated Fibonacci
            def fib_tab(n):
                if n <= 0: return 0
                if n == 1: return 1
                tb = [0] * (n + 1)
                tb[1] = 1
                for i in range(2, n + 1):
                    tb[i] = tb[i - 1] + tb[i - 2]
                return tb[n]
        """).strip(),
        "dry_run": "1. Allocates array `[0, 1, 0, 0, 0, 0]` for `n=5`.\n2. Loop index `i` from 2 to 5. `tb[2] = tb[1] + tb[0] = 1`.\n3. `tb[3] = 2`, `tb[4] = 3`, `tb[5] = 5`. Returns `5` without recursion stack overhead.",
        "complexity": "| Operation | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Tabulated | $O(N)$ | $O(N)$ (or $O(1)$ with variables) |",
        "edge_cases": "• **Space Optimization:** You can reduce space complexity from $O(N)$ to $O(1)$ by keeping track of only the last two computed states using variables instead of an entire array."
    },
    "knapsack": {
        "title": "0-1 Knapsack Problem (DP)",
        "category": "Dynamic Programming",
        "concept": "The 0-1 Knapsack problem is a classic optimization problem. Given items with weights and values, choose a subset of items that maximizes total value without exceeding the knapsack's weight capacity. Elements cannot be divided (either pick it, 1, or leave it, 0).",
        "code": textwrap.dedent("""
            def knapsack(weights, values, capacity):
                n = len(weights)
                dp = [[0] * (capacity + 1) for _ in range(n + 1)]
                for i in range(1, n + 1):
                    for w in range(1, capacity + 1):
                        if weights[i-1] <= w:
                            # Max value: include item or exclude item
                            dp[i][w] = max(values[i-1] + dp[i-1][w-weights[i-1]], dp[i-1][w])
                        else:
                            dp[i][w] = dp[i-1][w]
                return dp[n][capacity]
        """).strip(),
        "dry_run": "1. Prepares $N \times W$ capacity grid.\n2. Iterates over items. If the current item's weight is less than target capacity `w`, compare the value of including it (`value + dp[i-1][w - weight]`) with the value of excluding it (`dp[i-1][w]`).\n3. Stores the maximum value in the grid. The bottom-right cell contains the optimal solution.",
        "complexity": "| Operation | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Knapsack solver | $O(N \cdot W)$ | $O(N \cdot W)$ (or $O(W)$ with 1D array) |",
        "edge_cases": "• **Float Weights:** Dynamic programming knapsack assumes integer capacities. If weights are floats, scale them to integers or use branch-and-bound approximation algorithms."
    },
    "lcs": {
        "title": "Longest Common Subsequence (LCS)",
        "category": "Dynamic Programming",
        "concept": "LCS finds the longest subsequence common to two strings (where elements do not need to be consecutive). It is commonly used in file diff tools and bioinformatics.",
        "code": textwrap.dedent("""
            def lcs(s1, s2):
                m, n = len(s1), len(s2)
                dp = [[0] * (n + 1) for _ in range(m + 1)]
                for i in range(1, m + 1):
                    for j in range(1, n + 1):
                        if s1[i-1] == s2[j-1]:
                            dp[i][j] = dp[i-1][j-1] + 1
                        else:
                            dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                return dp[m][n]
        """).strip(),
        "dry_run": "1. Grid `dp` initialized with 0s. Compare characters `s1[i-1]` and `s2[j-1]`.\n2. If characters match, increment the diagonal value: `dp[i-1][j-1] + 1`.\n3. If they don't match, propagate the maximum neighboring value: `max(dp[i-1][j], dp[i][j-1])`.",
        "complexity": "| String Sizes | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| $M$ and $N$ | $O(M \cdot N)$ | $O(M \cdot N)$ |",
        "edge_cases": "• **Empty String input:** If either string is empty, the LCS is 0; the grid correctly remains filled with 0s."
    },
    "lis": {
        "title": "Longest Increasing Subsequence (LIS)",
        "category": "Dynamic Programming",
        "concept": "LIS finds the length of the longest subsequence in an array such that all elements of the subsequence are sorted in strictly ascending order.",
        "code": textwrap.dedent("""
            def lis(nums):
                if not nums: return 0
                dp = [1] * len(nums)
                for i in range(1, len(nums)):
                    for j in range(i):
                        if nums[i] > nums[j]:
                            dp[i] = max(dp[i], dp[j] + 1)
                return max(dp)
        """).strip(),
        "dry_run": "1. `nums=[10, 22, 9]`. `dp` initialized to `[1, 1, 1]`.\n2. Compare index 1 with 0: `22 > 10`, update `dp[1] = max(1, dp[0] + 1) = 2`.\n3. Compare index 2 with 0 and 1: `9` is smaller, `dp[2]` remains 1. Maximum LIS is 2.",
        "complexity": "| Algorithm | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Naive DP | $O(N^2)$ | $O(N)$ |\n| Binary Search (Patience Sorting) | $O(N \log N)$ | $O(N)$ |",
        "edge_cases": "• **Empty Array Input:** Guard against empty arrays by returning `0` immediately."
    },
    "coin_change": {
        "title": "Coin Change Problem (DP)",
        "category": "Dynamic Programming",
        "concept": "The Coin Change problem calculates the minimum number of coins required to make a target amount. It is solved using bottom-up tabulation.",
        "code": textwrap.dedent("""
            def coin_change(coins, amount):
                dp = [float('inf')] * (amount + 1)
                dp[0] = 0
                for coin in coins:
                    for i in range(coin, amount + 1):
                        dp[i] = min(dp[i], dp[i - coin] + 1)
                return dp[amount] if dp[amount] != float('inf') else -1
        """).strip(),
        "dry_run": "1. `coins=[1, 2]`, `amount=3`. `dp` array initialized to `[0, inf, inf, inf]`.\n2. Loop `coin=1`: `dp[1] = min(inf, dp[0]+1) = 1`, `dp[2] = 2`, `dp[3] = 3`.\n3. Loop `coin=2`: `dp[2] = min(2, dp[0]+1) = 1`, `dp[3] = min(3, dp[1]+1) = 2`. Optimal coins count is 2.",
        "complexity": "| Coins & Amount | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| $C$ and $A$ | $O(C \cdot A)$ | $O(A)$ |",
        "edge_cases": "• **Unsolvable Amounts:** If no combination of coins can make the target amount, the algorithm returns `-1`."
    },
    "matrix_chain": {
        "title": "Matrix Chain Multiplication (DP)",
        "category": "Dynamic Programming",
        "concept": "Matrix Chain Multiplication calculates the most efficient way to multiply a chain of matrices. It does not perform the actual multiplication, but finds the parenthesization ordering that minimizes scalar multiplications.",
        "code": textwrap.dedent("""
            def matrix_chain_order(p):
                n = len(p) - 1
                m = [[0] * (n + 1) for _ in range(n + 1)]
                for l in range(2, n + 1): # l is chain length
                    for i in range(1, n - l + 2):
                        j = i + l - 1
                        m[i][j] = float('inf')
                        for k in range(i, j):
                            q = m[i][k] + m[k+1][j] + p[i-1]*p[k]*p[j]
                            if q < m[i][j]: m[i][j] = q
                return m[1][n]
        """).strip(),
        "dry_run": "1. Takes dimensions list `p` (e.g. `[10, 20, 30]`). Prepares $N \times N$ multiplier grid.\n2. Iterates over chain lengths, calculating the scalar multiplication cost of splitting at each intermediate point `k`.\n3. Stores the minimum cost, returning the optimal value at `m[1][n]`.",
        "complexity": "| Matrix Count | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| $N$ matrices | $O(N^3)$ | $O(N^2)$ |",
        "edge_cases": "• **Single Matrix Chain:** If only 1 matrix exists (`len(p) <= 2`), the multiplication cost is 0."
    },

    # 10. Complexity Analysis
    "time_complexity": {
        "title": "Time Complexity & Big O",
        "category": "Complexity Analysis",
        "concept": "Time Complexity quantifies the amount of time an algorithm takes to run as a function of the input length $N$. Big O notation describes the upper bound (worst-case scenario) of this execution time.",
        "code": textwrap.dedent("""
            # Time complexity examples
            def constant_time(arr):
                return arr[0] # O(1) time
            
            def linear_time(arr):
                for x in arr:
                    print(x) # O(N) time
            
            def quadratic_time(arr):
                for x in arr:
                    for y in arr:
                        print(x, y) # O(N^2) time
        """).strip(),
        "dry_run": "1. Constant time accesses index 0 directly without looping.\n2. Linear time executes one instruction per element.\n3. Quadratic time runs nested loops, executing $N \times N$ operations.",
        "complexity": "| Class | Time Complexity | Common Example |\n| :--- | :--- | :--- |\n| Constant | $O(1)$ | Hash lookup |\n| Logarithmic | $O(\log N)$ | Binary Search |\n| Linear | $O(N)$ | Linear Search |\n| Linearithmic | $O(N \log N)$ | Merge Sort |\n| Quadratic | $O(N^2)$ | Nested loops (Bubble Sort) |",
        "edge_cases": "• **Hidden Constants:** Big O notation discards constants (e.g. $O(2N)$ becomes $O(N)$). However, in production environments, large constants can significantly impact execution times."
    },
    "space_complexity": {
        "title": "Space Complexity Analysis",
        "category": "Complexity Analysis",
        "concept": "Space Complexity quantifies the total memory consumed by an algorithm (including input parameters, local variables, and the call stack) as a function of the input size $N$.",
        "code": textwrap.dedent("""
            def constant_space(n):
                total = 0
                for i in range(n): total += i
                return total # O(1) auxiliary space
            
            def linear_space(n):
                # Allocates memory of size N
                return [i for i in range(n)] # O(N) space
        """).strip(),
        "dry_run": "1. `constant_space` reuse the single variable `total` in memory.\n2. `linear_space` allocates a list of $N$ items, utilizing $O(N)$ bytes.",
        "complexity": "| Algorithm | Auxiliary Space Complexity |\n| :--- | :--- |\n| Iterative sum | $O(1)$ |\n| Recursive sum | $O(N)$ (due to call stack frames) |\n| Matrix Allocation | $O(N^2)$ |",
        "edge_cases": "• **Call Stack space:** Recursive algorithms consume call stack frames in memory. Forgetting to account for the call stack leads to incomplete space complexity analysis."
    },
    "big_o": {
        "title": "Big O Notation (Worst Case)",
        "category": "Complexity Analysis",
        "concept": "Big O ($O$) describes the mathematical upper bound of an algorithm's growth rate. It guarantees that the execution time will not exceed this limit, representing the worst-case scenario.",
        "code": textwrap.dedent("""
            # Worst-case search is O(N)
            def find_item(arr, target):
                for i in range(len(arr)):
                    if arr[i] == target:
                        return i
                return -1 # O(N) time
        """).strip(),
        "dry_run": "1. Search targets index 0. Returns in $O(1)$ time (best case).\n2. Search target is absent. Scans the entire array, returning in $O(N)$ worst-case time.",
        "complexity": "Big O represents the asymptotic upper bound: $f(N) = O(g(N))$ if there exist constants $C$ and $N_0$ such that $f(N) \le C \cdot g(N)$ for all $N \ge N_0$.",
        "edge_cases": "• **Amortized Analysis:** Some operations (like dynamic array append) take $O(N)$ worst-case time occasionally but $O(1)$ average time. Big O describes this using amortized complexity."
    },
    "big_theta": {
        "title": "Big Theta Notation (Average Case)",
        "category": "Complexity Analysis",
        "concept": "Big Theta ($\Theta$) describes the tight asymptotic bound of an algorithm's growth rate, representing the average-case scenario where the time complexity is bounded from both above and below.",
        "code": textwrap.dedent("""
            # Matrix traversal is strictly Theta(N^2)
            def print_matrix(matrix):
                n = len(matrix)
                for i in range(n):
                    for j in range(n):
                        print(matrix[i][j])
        """).strip(),
        "dry_run": "1. Traversing a matrix requires visiting every cell. The algorithm always performs exactly $N \times N$ operations, regardless of value distribution.",
        "complexity": "Big Theta represents the tight bound: $f(N) = \Theta(g(N))$ if there exist positive constants $C_1, C_2,$ and $N_0$ such that $C_1 \cdot g(N) \le f(N) \le C_2 \cdot g(N)$ for all $N \ge N_0$.",
        "edge_cases": "• **Algorithm Instability:** Some algorithms (like Quick Sort) have different average and worst-case bounds. Quick Sort is $\Theta(N \log N)$ on average, but $O(N^2)$ in the worst case."
    },
    "big_omega": {
        "title": "Big Omega Notation (Best Case)",
        "category": "Complexity Analysis",
        "concept": "Big Omega ($\Omega$) describes the mathematical lower bound of an algorithm's growth rate, representing the best-case (quickest possible) execution time.",
        "code": textwrap.dedent("""
            # Linear search is Omega(1) best-case
            def linear_search_omega(arr, target):
                if arr[0] == target: return 0
                # ... rest of search
        """).strip(),
        "dry_run": "1. If target is located at index 0, the search exits immediately. The best-case complexity is constant $\Omega(1)$ time.",
        "complexity": "Big Omega represents the lower bound: $f(N) = \Omega(g(N))$ if there exist constants $C$ and $N_0$ such that $f(N) \ge C \cdot g(N)$ for all $N \ge N_0$.",
        "edge_cases": "• **Trivial Best Case bounds:** Simply checking if an array is empty at the start of a function yields an $\Omega(1)$ best-case check, but does not reflect the algorithm's actual operational work."
    },

    # 11. OOP Core
    "class": {
        "title": "OOP: Classes & Blueprints",
        "category": "Object-Oriented Programming (OOP)",
        "analogy": "An architectural blueprint of a house. The blueprint itself is not a house, but it defines the structure, layout, and building instructions.",
        "concept": "A Class is a user-defined prototype or blueprint that bundles data (attributes) and behavior (methods) together.",
        "code": textwrap.dedent("""
            class Student:
                \"\"\"Class blueprint defining student attributes.\"\"\"
                def __init__(self, name, age):
                    self.name = name # Attribute
                    self.age = age   # Attribute
        """).strip(),
        "dry_run": "1. Declares class `Student`.\n2. Defines the standard initialization constructor `__init__`.\n3. Allocates instance variables inside class namespace.",
        "complexity": "| OOP Phase | Complexity |\n| :--- | :--- |\n| Class definition | $O(1)$ |\n| Space Complexity | $O(1)$ |",
        "edge_cases": "• **Empty Class definition:** Empty classes require a `pass` statement to avoid syntax compile errors: `class Empty: pass`."
    },
    "object": {
        "title": "OOP: Objects & Instances",
        "category": "Object-Oriented Programming (OOP)",
        "analogy": "A physical house built from the architectural blueprint. You can walk inside, paint the walls, or open the doors of this specific house instance.",
        "concept": "An Object is a concrete instance of a class. It occupies memory space and holds state variables unique to that instance.",
        "code": textwrap.dedent("""
            # Instantiating student objects
            student1 = Student("Ammar", 23)
            student2 = Student("Ali", 25)
            print("Student 1 name:", student1.name)
        """).strip(),
        "dry_run": "1. Calls constructor `Student(...)`.\n2. Instantiates new object `student1` in memory, binding name to 'Ammar'.\n3. Instantiates `student2` in a separate memory slot, keeping states isolated.",
        "complexity": "| Phase | Complexity |\n| :--- | :--- |\n| Instantiation | $O(1)$ |\n| Space Complexity | $O(1)$ |",
        "edge_cases": "• **Shared References:** Assigning `obj2 = obj1` does not copy the object. Both variables reference the exact same memory instance. Modifying `obj2` alters `obj1`."
    },
    "attribute": {
        "title": "OOP: Attributes & State",
        "category": "Object-Oriented Programming (OOP)",
        "concept": "Attributes are variables bound to a class or an object instance that define its state. They can be instance attributes (unique to each object) or class attributes (shared across all instances of that class).",
        "code": textwrap.dedent("""
            class Course:
                # Class attribute (shared by all instances)
                platform = "APCRE"
                
                def __init__(self, title):
                    # Instance attribute (unique to each instance)
                    self.title = title
        """).strip(),
        "dry_run": "1. `Course` class binds class attribute `'platform' = 'APCRE'`.\n2. Instantiates course `c1 = Course('Python')`. Sets instance attribute `title` to `'Python'`.\n3. Accessing `c1.platform` references the class attribute.",
        "complexity": "| Operation | Time Complexity |\n| :--- | :--- |\n| Get / Set attribute | $O(1)$ |\n| Space Complexity | $O(1)$ |",
        "edge_cases": "• **Attribute Shadowing:** Modifying a class attribute via an instance (`c1.platform = 'New'`) creates a local instance attribute, shadowing the class attribute for that instance without modifying the shared class value."
    },
    "method": {
        "title": "OOP: Methods & Behavior",
        "category": "Object-Oriented Programming (OOP)",
        "concept": "Methods are functions defined inside a class that operate on object instances. They must accept the instance (`self`) as their first parameter to access instance attributes.",
        "code": textwrap.dedent("""
            class Counter:
                def __init__(self):
                    self.count = 0
                def increment(self):
                    # Instance method modifying state
                    self.count += 1
        """).strip(),
        "dry_run": "1. Instantiate `c = Counter()`.\n2. Call `c.increment()`. The instance `c` is implicitly passed as the first parameter `self`.\n3. Modifies `self.count` to 1.",
        "complexity": "| Phase | Complexity |\n| :--- | :--- |\n| Method invocation | $O(1)$ |\n| Space Complexity | $O(1)$ |",
        "edge_cases": "• **Missing Self Parameter:** Forgetting to declare `self` as the first argument in instance methods raises a `TypeError` when the method is invoked."
    },
    "constructor": {
        "title": "OOP: Constructors (`__init__`)",
        "category": "Object-Oriented Programming (OOP)",
        "concept": "A Constructor is a special method called automatically when an object is instantiated. In Python, the constructor is defined using the `__init__` method, which is used to initialize the object's attributes.",
        "code": textwrap.dedent("""
            class Node:
                def __init__(self, val=0):
                    self.val = val
                    self.left = None
        """).strip(),
        "dry_run": "1. `Node(10)` triggers `__init__` automatically.\n2. Binds instance variables `self.val = 10` and `self.left = None`.\n3. Returns the initialized node object.",
        "complexity": "| Constructor | Time Complexity |\n| :--- | :--- |\n| Initialization | $O(1)$ |\n| Space Complexity | $O(1)$ |",
        "edge_cases": "• **Returning Values:** Constructors must never return a value (other than `None`). Attempting to return a value raises a `TypeError`."
    },
    "destructor": {
        "title": "OOP: Destructors (`__del__`)",
        "category": "Object-Oriented Programming (OOP)",
        "concept": "A Destructor is a special method called automatically when an object is about to be destroyed or garbage collected. In Python, the destructor is defined using the `__del__` method.",
        "code": textwrap.dedent("""
            class FileLock:
                def __init__(self, path):
                    self.path = path
                    print(f"Locked: {path}")
                def __del__(self):
                    # Destructor releasing resources
                    print(f"Released lock for: {self.path}")
        """).strip(),
        "dry_run": "1. `lock = FileLock('data.txt')` creates instance.\n2. Running `del lock` deletes the reference.\n3. The garbage collector triggers `__del__` automatically, releasing the file lock.",
        "complexity": "| Operation | Time/Space Complexity |\n| :--- | :--- |\n| Destruction | $O(1)$ |\n| Space Complexity | $O(1)$ |",
        "edge_cases": "• **Circular References:** If two objects reference each other, their reference count never drops to 0, preventing Python's garbage collector from triggering destructors."
    },
    "self_keyword": {
        "title": "OOP: The `self` Keyword",
        "category": "Object-Oriented Programming (OOP)",
        "concept": "The `self` keyword represents the current instance of the class. It binds instance attributes and methods to the specific object in memory, distinguishing it from local or global variables.",
        "code": textwrap.dedent("""
            class User:
                def __init__(self, username):
                    self.username = username # self binds value to this object
                def greet(self):
                    return f"Hello, I am {self.username}"
        """).strip(),
        "dry_run": "1. Instantiate `u = User('ammar')`.\n2. `self` points to the memory address of `u`.\n3. `greet()` accesses `self.username`, which resolves to `'ammar'`.",
        "complexity": "The `self` keyword is a pointer reference that resolves in $O(1)$ constant time with zero overhead.",
        "edge_cases": "• **Naming Convention:** `self` is a strong convention, not a strict keyword in Python. You could theoretically name it `this` or `me`, but doing so violates PEP 8 and makes your code un-pythonic."
    },
    "encapsulation": {
        "title": "OOP Pillar 1: Encapsulation",
        "category": "Object-Oriented Programming (OOP)",
        "analogy": "A secure capsule pill. The active medicine is sealed inside, and patients can only access it by swallowing the capsule whole.",
        "concept": "Encapsulation restricts direct access to an object's state and exposes it only through public methods (getters and setters). In Python, private variables are indicated using a double underscore prefix `__` (which triggers name mangling).",
        "code": textwrap.dedent("""
            class UserProfile:
                def __init__(self, age):
                    self.__age = age # Private attribute (name-mangled)
                
                @property
                def age(self):
                    return self.__age
                
                @age.setter
                def age(self, new_age):
                    if new_age < 0: raise ValueError("Age cannot be negative")
                    self.__age = new_age
        """).strip(),
        "dry_run": "1. `profile = UserProfile(23)` sets mangled attribute `_UserProfile__age = 23`.\n2. Accessing `profile.age` calls the `@property` getter.\n3. Modifying `profile.age = -5` invokes the setter, validating input and raising an error.",
        "complexity": "| Getter / Setter | Complexity |\n| :--- | :--- |\n| Access / Mutation | $O(1)$ |\n| Space Complexity | $O(1)$ |",
        "edge_cases": "• **Direct Name Mangling Access:** Private variables can technically still be accessed directly using their mangled names (`profile._UserProfile__age = 25`), which bypasses encapsulation controls."
    },
    "abstraction": {
        "title": "OOP Pillar 2: Abstraction",
        "category": "Object-Oriented Programming (OOP)",
        "analogy": "A car dashboard: you press the accelerator pedal to speed up, without needing to understand the complex fuel injection physics occurring under the hood.",
        "concept": "Abstraction hides complex implementation details and exposes only essential features. In Python, it is implemented using abstract base classes (from the `abc` module) and abstract methods.",
        "code": textwrap.dedent("""
            from abc import ABC, abstractmethod
            class PaymentProcessor(ABC):
                @abstractmethod
                def process_payment(self, amount):
                    pass
            
            class StripeProcessor(PaymentProcessor):
                def process_payment(self, amount):
                    print(f"Charging ${amount} via Stripe API...")
        """).strip(),
        "dry_run": "1. `PaymentProcessor` defines the abstract interface.\n2. `StripeProcessor` inherits from the abstract base class and implements the required `process_payment` method.\n3. Clients invoke `process_payment` without needing to know the underlying API details.",
        "complexity": "Abstraction is a design-time architectural pattern that incurs zero runtime performance overhead.",
        "edge_cases": "• **Instantiating Abstract Classes:** Attempting to instantiate `PaymentProcessor()` directly raises a `TypeError`."
    },
    "inheritance": {
        "title": "OOP Pillar 3: Inheritance",
        "category": "Object-Oriented Programming (OOP)",
        "analogy": "Generic parent traits: you inherit your parent's general features (like height or eye color), but you can still develop your own unique skills.",
        "concept": "Inheritance allows a subclass to inherit attributes and methods from a parent class, promoting code reuse. Subclasses can override parent methods to implement specialized behavior.",
        "code": textwrap.dedent("""
            class Device:
                def __init__(self, brand):
                    self.brand = brand
                def power_on(self):
                    return "Powering on..."
            
            class Laptop(Device):
                def __init__(self, brand, ram):
                    super().__init__(brand) # Correct parent constructor call
                    self.ram = ram
        """).strip(),
        "dry_run": "1. Instantiate `Laptop('APCRE', 16)`.\n2. `super().__init__('APCRE')` calls the parent constructor, binding the `brand` attribute.\n3. The laptop instance inherits the `power_on` method from the parent class.",
        "complexity": "Constructor chain calls run in $O(1)$ constant time with negligible overhead.",
        "edge_cases": "• **Forgot Super Call:** Failing to call `super().__init__()` inside a subclass constructor prevents parent attributes from being initialized, raising `AttributeError` exceptions."
    },
    "polymorphism": {
        "title": "OOP Pillar 4: Polymorphism",
        "category": "Object-Oriented Programming (OOP)",
        "analogy": "A universal 'play' button. Pressing it plays audio on a CD player, starts a video on a DVD player, or launches a game on a console.",
        "concept": "Polymorphism allows different classes to implement identical methods in distinct, specialized ways. Method overriding is the most common implementation in Python.",
        "code": textwrap.dedent("""
            class Dog:
                def make_sound(self): return "Woof!"
            class Cat:
                def make_sound(self): return "Meow!"
            
            # Polymorphic function handling different classes
            def pet_sound(pet_obj):
                print(pet_obj.make_sound())
        """).strip(),
        "dry_run": "1. Call `pet_sound(Dog())`. The function executes the dog's `make_sound` method, printing 'Woof!'.\n2. Call `pet_sound(Cat())`. The function executes the cat's `make_sound` method, printing 'Meow!'.",
        "complexity": "Method lookups in dynamic polymorphism are resolved in $O(1)$ time.",
        "edge_cases": "• **Duck Typing:** In Python, polymorphism does not require strict class inheritance. As long as an object implements the required method ('if it walks like a duck and quacks like a duck'), it is accepted."
    },

    # 12. OOP Inheritance Types
    "single_inheritance": {
        "title": "Single Inheritance",
        "category": "Inheritance Types",
        "concept": "Single Inheritance occurs when a subclass inherits from exactly one parent class, representing a straightforward hierarchical relationship.",
        "code": textwrap.dedent("""
            class Parent:
                pass
            class Child(Parent):
                # Inherits from exactly 1 parent
                pass
        """).strip(),
        "dry_run": "1. Class `Child` inherits all methods and attributes defined in `Parent`.\n2. Method Resolution Order (MRO) checks `Child` first, then `Parent`.",
        "complexity": "Lookup resolution runs in $O(1)$ constant time.",
        "edge_cases": "• **Parent Constructor overrides:** If the child defines its own constructor, you must call `super().__init__()` to initialize parent attributes."
    },
    "multiple_inheritance": {
        "title": "Multiple Inheritance",
        "category": "Inheritance Types",
        "concept": "Multiple Inheritance occurs when a subclass inherits from more than one parent class. Python resolves method lookup order using the **Method Resolution Order (MRO)** algorithm.",
        "code": textwrap.dedent("""
            class Flyer:
                def fly(self): return "Flying..."
            class Swimmer:
                def swim(self): return "Swimming..."
            
            # Inherits from both Flyer and Swimmer
            class Duck(Flyer, Swimmer):
                pass
        """).strip(),
        "dry_run": "1. Instantiate `d = Duck()`.\n2. Calling `d.fly()` resolves to the `Flyer` parent class.\n3. Calling `d.swim()` resolves to the `Swimmer` parent class.",
        "complexity": "MRO lookup takes $O(1)$ time.",
        "edge_cases": "• **The Diamond Problem:** If two parent classes inherit from the same grandparent and define the same method, Python resolves the conflict using Method Resolution Order (MRO)."
    },
    "multilevel_inheritance": {
        "title": "Multilevel Inheritance",
        "category": "Inheritance Types",
        "concept": "Multilevel Inheritance occurs when a class inherits from a subclass, creating a multi-layered inheritance chain (e.g. Grandparent $\rightarrow$ Parent $\rightarrow$ Child).",
        "code": textwrap.dedent("""
            class Organism:
                pass
            class Animal(Organism):
                pass
            class Mammal(Animal):
                # Inherits from Animal, which inherits from Organism
                pass
        """).strip(),
        "dry_run": "1. `Mammal` inherits all attributes and methods defined in both `Animal` and `Organism`.\n2. MRO checks classes in order: `Mammal` $\rightarrow$ `Animal` $\rightarrow$ `Organism` $\rightarrow$ `object`.",
        "complexity": "Method lookups resolve in $O(1)$ constant time.",
        "edge_cases": "• **Distant overrides:** Modifying grandparent methods can have unintended side effects down the inheritance chain. Ensure abstract methods are overridden carefully."
    },
    "hierarchical_inheritance": {
        "title": "Hierarchical Inheritance",
        "category": "Inheritance Types",
        "concept": "Hierarchical Inheritance occurs when multiple subclasses inherit from a single parent class, sharing a common base structure.",
        "code": textwrap.dedent("""
            class Shape:
                pass
            class Circle(Shape): pass
            class Square(Shape): pass # BothCircle and Square inherit from Shape
        """).strip(),
        "dry_run": "1. Both circular and square instances inherit attributes defined in the base `Shape` class.\n2. State modifications inside `Circle` do not affect `Square`.",
        "complexity": "Attribute and method lookups resolve in $O(1)$ time.",
        "edge_cases": "• **Base Class changes:** Modifying parent classes affects all child subclasses. Avoid breaking changes in parent contracts."
    },
    "hybrid_inheritance": {
        "title": "Hybrid Inheritance",
        "category": "Inheritance Types",
        "concept": "Hybrid Inheritance is a combination of two or more inheritance types (e.g., combining multiple and multilevel inheritance). Python handles this safely using the C3 linearization algorithm to define a clear Method Resolution Order (MRO).",
        "code": textwrap.dedent("""
            class A: pass
            class B(A): pass
            class C(A): pass
            class D(B, C): pass # Hybrid mix
        """).strip(),
        "dry_run": "1. MRO resolves linear lookup order for class `D`.\n2. Checks `D` $\rightarrow$ `B` $\rightarrow$ `C` $\rightarrow$ `A` $\rightarrow$ `object` to avoid duplicate grandparent checks.",
        "complexity": "Dynamic MRO linearizations run at class creation time, incurring zero runtime search overhead.",
        "edge_cases": "• **MRO Failures:** If you define invalid inheritance loops (e.g. `class D(A, B)` where `B` inherits from `A`), Python raises `TypeError: Cannot create a consistent Method Resolution Order (MRO)` at compile time."
    },

    # 13. Polymorphism Types
    "method_overriding": {
        "title": "Method Overriding",
        "category": "Polymorphism Types",
        "concept": "Method Overriding allows a subclass to provide a specific implementation of a method that is already defined in its parent class.",
        "code": textwrap.dedent("""
            class Parent:
                def greet(self): return "Hello from Parent"
            class Child(Parent):
                def greet(self): return "Hello from Child" # Overrides parent method
        """).strip(),
        "dry_run": "1. Instantiate `c = Child()`.\n2. Calling `c.greet()` executes the overridden child method, returning 'Hello from Child'.\n3. The parent class version is shadowed for this instance.",
        "complexity": "Method lookups take $O(1)$ constant time.",
        "edge_cases": "• **Calling Parent Method:** Subclasses can still invoke the parent version of a method using the `super()` keyword: `super().greet()`."
    },
    "method_overloading": {
        "title": "Method Overloading",
        "category": "Polymorphism Types",
        "concept": "Method Overloading allows a class to define multiple methods with the same name but different parameter counts or types. Python does not support standard method overloading natively. Instead, it is implemented using default arguments or variable positional arguments (`*args`).",
        "code": textwrap.dedent("""
            class Calculator:
                def add(self, a, b, c=0):
                    # Simulating overloading using default arguments
                    return a + b + c
        """).strip(),
        "dry_run": "1. `add(2, 3)` matches default parameter `c=0`, returning 5.\n2. `add(2, 3, 4)` overrides default parameter `c`, returning 9.",
        "complexity": "Conditional checks resolve in $O(1)$ constant time.",
        "edge_cases": "• **Multiple Definitions:** Defining the same function name multiple times in a Python class is invalid; the last definition simply overwrites all previous ones."
    },
    "operator_overloading": {
        "title": "Operator Overloading",
        "category": "Polymorphism Types",
        "concept": "Operator Overloading allows you to define how built-in operators (like `+`, `-`, `*`) behave when applied to custom objects. It is implemented using magic/dunder methods (e.g. `__add__` for `+`).",
        "code": textwrap.dedent("""
            class Point:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y
                def __add__(self, other):
                    # Overloading the '+' operator
                    return Point(self.x + other.x, self.y + other.y)
        """).strip(),
        "dry_run": "1. `p1 = Point(1, 2)`, `p2 = Point(3, 4)`.\n2. `p1 + p2` automatically triggers `p1.__add__(p2)`.\n3. Returns a new `Point(4, 6)` instance.",
        "complexity": "Dunder method lookups resolve in $O(1)$ time.",
        "edge_cases": "• **Type Safety:** If `other` is not an instance of the expected class, the operation raises a `TypeError`. Use `isinstance()` checks to handle invalid types gracefully."
    },
    "duck_typing": {
        "title": "Duck Typing",
        "category": "Polymorphism Types",
        "analogy": "If it walks like a duck and quacks like a duck, then it is a duck! You don't need a DNA test (class check) to verify.",
        "concept": "Duck Typing is a dynamic typing paradigm where an object's suitability is determined by the presence of specific methods and properties, rather than its inheritance hierarchy.",
        "code": textwrap.dedent("""
            class Duck:
                def quack(self): return "Quack!"
            class Person:
                # Duck typed: implements the same interface
                def quack(self): return "I am quacking like a duck!"
            
            def make_it_quack(obj):
                print(obj.quack())
        """).strip(),
        "dry_run": "1. `make_it_quack(Person())` executes without errors because `Person` implements the `quack` method.\n2. No strict class checks are performed, promoting highly flexible designs.",
        "complexity": "Dynamic attribute lookups resolve in $O(1)$ constant time.",
        "edge_cases": "• **Missing Methods:** If the passed object does not implement the expected method, Python raises an `AttributeError` at runtime. Guard operations using `hasattr(obj, 'method')` if needed."
    },

    # 14. Advanced OOP
    "abstract_class": {
        "title": "Abstract Classes & Interfaces",
        "category": "Advanced OOP",
        "concept": "Abstract Classes define template blueprints for subclasses. They contain abstract methods that must be implemented by subclasses, and cannot be instantiated directly.",
        "code": textwrap.dedent("""
            from abc import ABC, abstractmethod
            class Vehicle(ABC):
                @abstractmethod
                def start_engine(self):
                    pass
        """).strip(),
        "dry_run": "1. `Vehicle` defines the abstract base class and contract.\n2. Subclasses must implement `start_engine` to be instantiable.\n3. Ensures structural consistency across different classes.",
        "complexity": "Interface constraints are validated at instantiation time in $O(1)$ time.",
        "edge_cases": "• **Forgot Implementation:** If a subclass forgets to override an abstract method, attempting to instantiate it raises a `TypeError`."
    },
    "interface": {
        "title": "Interfaces in Python",
        "category": "Advanced OOP",
        "concept": "Python does not have a native `interface` keyword. Instead, interfaces are implemented using Abstract Base Classes containing only abstract methods with no implementation body.",
        "code": textwrap.dedent("""
            from abc import ABC, abstractmethod
            class DBConnection(ABC):
                @abstractmethod
                def connect(self): pass
                @abstractmethod
                def close(self): pass
        """).strip(),
        "dry_run": "1. `DBConnection` defines a clean interface contract.\n2. Any class implementing it must define both `connect` and `close` methods.\n3. Promotes clean, loosely coupled architectures.",
        "complexity": "Zero runtime overhead.",
        "edge_cases": "• **Partial Implementation:** Concrete subclasses must implement *all* abstract methods defined in the interface to be instantiable."
    },
    "decorator": {
        "title": "Python Decorators",
        "category": "Advanced OOP",
        "analogy": "Gift wrapping a present. The wrapping paper decorates and enhances the present without changing the gift inside.",
        "concept": "Decorators wrap functions or classes to extend their behavior without modifying them directly. They are syntactically applied using the `@` symbol.",
        "code": textwrap.dedent("""
            def log_decorator(func):
                def wrapper(*args, **kwargs):
                    print("Executing function...")
                    return func(*args, **kwargs)
                return wrapper
            
            @log_decorator
            def say_hello():
                print("Hello!")
        """).strip(),
        "dry_run": "1. Applying `@log_decorator` replaces the original `say_hello` with `log_decorator(say_hello)`.\n2. Invoking `say_hello()` executes the `wrapper` function, printing the log before running the original function code.",
        "complexity": "Function wrapper resolutions add a negligible, single-hop $O(1)$ call overhead.",
        "edge_cases": "• **Metadata Loss:** Decorators replace functions with wrappers, losing metadata (like docstrings and names). Use `functools.wraps` on wrappers to preserve original function details."
    },
    "property_decorator": {
        "title": "Property Decorators (`@property`)",
        "category": "Advanced OOP",
        "concept": "The `@property` decorator allows you to define getter and setter methods that can be accessed like standard attributes, combining encapsulation with clean, pythonic syntax.",
        "code": textwrap.dedent("""
            class Circle:
                def __init__(self, radius):
                    self._radius = radius
                @property
                def radius(self):
                    return self._radius
                @radius.setter
                def radius(self, val):
                    if val < 0: raise ValueError("Radius must be positive")
                    self._radius = val
        """).strip(),
        "dry_run": "1. `c = Circle(5)` binds `_radius`.\n2. Querying `c.radius` invokes the getter method.\n3. Assigning `c.radius = 10` executes the setter method, validating the new value.",
        "complexity": "Property lookups resolve in $O(1)$ constant time.",
        "edge_cases": "• **Recursive Loop Trap:** Setting `self.radius = val` (without underscore) inside the setter creates an infinite recursion loop that crashes the interpreter. Always use protected variables like `self._radius`!"
    },
    "static_method": {
        "title": "Static Methods (`@staticmethod`)",
        "category": "Advanced OOP",
        "concept": "Static Methods (`@staticmethod`) are functions defined inside a class that do not access instance (`self`) or class (`cls`) state. They behave like normal functions but are nested inside the class namespace.",
        "code": textwrap.dedent("""
            class MathUtils:
                @staticmethod
                def add(x, y):
                    # Independent helper function
                    return x + y
        """).strip(),
        "dry_run": "1. Call `MathUtils.add(5, 10)` directly without instantiating the class.\n2. No instance reference is passed, keeping the operation pure and stateless.",
        "complexity": "Invoked in $O(1)$ constant time.",
        "edge_cases": "• **State Access Attempt:** Attempting to access `self` or `cls` inside static methods raises a `NameError`."
    },
    "class_method": {
        "title": "Class Methods (`@classmethod`)",
        "category": "Advanced OOP",
        "concept": "Class Methods (`@classmethod`) accept the class itself (`cls`) as their first parameter instead of an instance. They are ideal for creating factory methods that instantiate objects using custom configurations.",
        "code": textwrap.dedent("""
            class User:
                def __init__(self, name):
                    self.name = name
                @classmethod
                def from_guest(cls):
                    # Factory method creating guest user
                    return cls("Guest User")
        """).strip(),
        "dry_run": "1. Call `User.from_guest()`.\n2. The class reference `User` is passed as parameter `cls`.\n3. The class is instantiated dynamically, returning a Guest User.",
        "complexity": "Factory method executions run in $O(1)$ constant time.",
        "edge_cases": "• **Hardcoding class names:** Always instantiate using `cls(...)` rather than the hardcoded class name (`User(...)`) inside class methods to support inheritance cleanly."
    },
    "magic_method": {
        "title": "Magic & Dunder Methods",
        "category": "Advanced OOP",
        "concept": "Magic (or Dunder, double-underscore) methods are special built-in methods used to implement operator overloading and customize core class behaviors (e.g., representation, length, comparison).",
        "code": textwrap.dedent("""
            class Book:
                def __init__(self, title):
                    self.title = title
                def __str__(self):
                    # Custom user-facing string representation
                    return f"Book: {self.title}"
                def __len__(self):
                    # Custom length definition
                    return len(self.title)
        """).strip(),
        "dry_run": "1. `b = Book('APCRE')`.\n2. Calling `print(b)` automatically triggers `b.__str__()`.\n3. Calling `len(b)` automatically triggers `b.__len__()`.",
        "complexity": "Dunder method lookups resolve in $O(1)$ constant time.",
        "edge_cases": "• **Wrong Return Types:** Dunder methods must return specific types (e.g. `__str__` must return a string, `__len__` must return an integer) or Python raises a `TypeError`."
    },
    "composition": {
        "title": "Composition (Has-A relationship)",
        "category": "Advanced OOP",
        "analogy": "A physical computer: it contains a motherboard, a CPU, and RAM. The computer 'has a' CPU; it is not 'is a' CPU.",
        "concept": "Composition is a design relationship where a class contains references to instances of other classes. It is highly preferred over inheritance ('favor object composition over class inheritance') to keep classes loosely coupled.",
        "code": textwrap.dedent("""
            class CPU: pass
            class RAM: pass
            
            class Computer:
                def __init__(self):
                    # Composition: Computer owns these parts
                    self.cpu = CPU()
                    self.ram = RAM()
        """).strip(),
        "dry_run": "1. Instantiating `Computer` automatically instantiates internal `CPU` and `RAM` instances.\n2. The computer holds references to these component parts, controlling their lifecycle.",
        "complexity": "Instantiation overhead is $O(1)$.",
        "edge_cases": "• **Strong Ownership:** In composition, components do not exist independently. When the host `Computer` object is garbage collected, the internal `CPU` and `RAM` instances are also destroyed."
    },
    "aggregation": {
        "title": "Aggregation (Has-A weak relationship)",
        "category": "Advanced OOP",
        "analogy": "A department has professors. If the department is closed down, the professors still exist independently and can join other departments.",
        "concept": "Aggregation is a weak 'has-a' relationship where child components exist independently of the host parent class.",
        "code": textwrap.dedent("""
            class Professor:
                def __init__(self, name): self.name = name
            
            class Department:
                def __init__(self, professor_list):
                    # Aggregation: professors passed from outside
                    self.professors = professor_list
        """).strip(),
        "dry_run": "1. Create professor `p1 = Professor('Ammar')`.\n2. Create department `d = Department([p1])`.\n3. Deleting department `d` does not affect professor `p1`, which continues to exist in memory.",
        "complexity": "Reference assignments take $O(1)$ time.",
        "edge_cases": "• **Dangling References:** Ensure child lifecycles are managed safely since they exist outside parent scopes."
    },
    "association": {
        "title": "Association",
        "category": "Advanced OOP",
        "concept": "Association is a general relationship between two classes where objects interact but exist independently (e.g. a Teacher and a Student).",
        "code": textwrap.dedent("""
            class Student: pass
            class Teacher:
                def teach(self, student_obj):
                    # Association: temporary interaction
                    pass
        """).strip(),
        "dry_run": "1. Teacher instance interacts with a Student instance during method execution.\n2. Both objects remain completely independent with no ownership relationships.",
        "complexity": "Runs in $O(1)$ time.",
        "edge_cases": "• **Bidirectional association:** Bidirectional associations can create complex dependency graphs; limit coupling where possible to keep code maintainable."
    },
    "mro": {
        "title": "Method Resolution Order (MRO)",
        "category": "Advanced OOP",
        "concept": "MRO defines the order in which Python searches parent classes for a method or attribute in multiple inheritance. It is resolved using the C3 Linearization algorithm. You can inspect it using the `__mro__` attribute or `.mro()` method.",
        "code": textwrap.dedent("""
            class A: pass
            class B(A): pass
            class C(A): pass
            class D(B, C): pass
            
            print("MRO Order:", D.mro())
        """).strip(),
        "dry_run": "1. MRO calculates the linear order for class `D`.\n2. C3 Linearization prioritizes local subclasses over distant grandparents.\n3. The resulting lookup path is: `D` $\rightarrow$ `B` $\rightarrow$ `C` $\rightarrow$ `A` $\rightarrow$ `object`.",
        "complexity": "MRO lookup takes $O(1)$ constant time.",
        "edge_cases": "• **Unresolvable MRO:** Defining cyclic inheritance patterns (e.g., `class D(A, B)` where `B` inherits from `A` but you attempt to override class orders) raises a `TypeError` at compile time."
    },
    "solid": {
        "title": "SOLID Design Principles",
        "category": "Advanced OOP",
        "concept": "SOLID is an acronym for five design principles that make software designs more understandable, flexible, and maintainable:\n1. **Single Responsibility (SRP):** A class should have one reason to change.\n2. **Open/Closed (OCP):** Classes should be open for extension, closed for modification.\n3. **Liskov Substitution (LSP):** Subclasses must be substitutable for parents.\n4. **Interface Segregation (ISP):** Avoid fat interfaces; segregating into specific endpoints is better.\n5. **Dependency Inversion (DIP):** Depend on abstractions, not concretes.",
        "code": textwrap.dedent("""
            # SRP: Keep user database storage isolated from user notifications
            class UserDB:
                def save_user(self, user): pass
            
            class UserNotifier:
                def send_welcome_email(self, user): pass
        """).strip(),
        "dry_run": "1. Instead of creating a single class that saves users and sends emails, we split the responsibilities.\n2. Changing email configurations does not impact database storage code, preventing regression bugs.",
        "complexity": "SOLID is an architectural pattern that improves maintainability, incurring zero performance cost.",
        "edge_cases": "• **Over-engineering:** Applying SOLID principles to simple, one-off scripts adds unnecessary complexity. Use them only when scaling software systems."
    },
    "singleton": {
        "title": "Singleton Pattern",
        "category": "Design Patterns",
        "concept": "The Singleton pattern restricts the instantiation of a class to exactly one instance. It is ideal for shared resources like database connection pools or configuration managers.",
        "code": textwrap.dedent("""
            class Singleton:
                _instance = None
                def __new__(cls, *args, **kwargs):
                    if not cls._instance:
                        cls._instance = super().__new__(cls)
                    return cls._instance
        """).strip(),
        "dry_run": "1. `s1 = Singleton()` -> checks `_instance`. Since it is None, it creates a new instance.\n2. `s2 = Singleton()` -> checks `_instance`. It exists, so it returns the existing instance.\n3. Both `s1` and `s2` point to the exact same memory address.",
        "complexity": "Constructor checks run in $O(1)$ constant time.",
        "edge_cases": "• **Multi-threading:** In multi-threaded environments, concurrent calls can cause duplicate instantiations. Wrap instance checks in thread locks to guarantee uniqueness."
    },
    "factory": {
        "title": "Factory Pattern",
        "category": "Design Patterns",
        "concept": "The Factory pattern provides an interface for creating objects in a superclass, but allows subclasses to alter the type of objects that will be created, promoting loose coupling.",
        "code": textwrap.dedent("""
            class Dog:
                def speak(self): return "Woof!"
            class Cat:
                def speak(self): return "Meow!"
            
            class PetFactory:
                @staticmethod
                def get_pet(pet_type):
                    if pet_type == "dog": return Dog()
                    if pet_type == "cat": return Cat()
                    raise ValueError("Unknown pet type")
        """).strip(),
        "dry_run": "1. Client calls `PetFactory.get_pet('dog')`.\n2. The factory parses the input string, instantiates the matching class, and returns the `Dog` instance.\n3. The client is completely decoupled from the specific class constructors.",
        "complexity": "Factory lookups run in $O(1)$ constant time.",
        "edge_cases": "• **Extensibility:** When adding new classes, the factory switch block must be updated. Resolve this dynamically using registry dictionaries."
    },
    "observer": {
        "title": "Observer Pattern",
        "category": "Design Patterns",
        "concept": "The Observer pattern defines a one-to-many dependency relationship. When a 'Subject' changes its state, all its registered 'Observers' are notified and updated automatically.",
        "code": textwrap.dedent("""
            class Subject:
                def __init__(self):
                    self._observers = []
                def attach(self, observer):
                    self._observers.append(observer)
                def notify(self, message):
                    for observer in self._observers:
                        observer.update(message)
        """).strip(),
        "dry_run": "1. Observers register themselves using `subject.attach(self)`.\n2. The subject changes state and calls `notify('New Article!')`.\n3. Iterates through the list of registered observers and runs their `update` methods.",
        "complexity": "| Phase | Complexity |\n| :--- | :--- |\n| Notification | $O(N)$ (N is observer count) |\n| Space Complexity | $O(N)$ |",
        "edge_cases": "• **Memory Leaks:** Observers hold strong references to subjects, which can prevent garbage collection. Use weak references to avoid memory leaks."
    },
    "strategy": {
        "title": "Strategy Pattern",
        "category": "Design Patterns",
        "concept": "The Strategy pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable, allowing the algorithm to vary independently of the clients that use it.",
        "code": textwrap.dedent("""
            class DiscountStrategy:
                def apply(self, price): pass
            
            class TenPercentDiscount(DiscountStrategy):
                def apply(self, price): return price * 0.9
            
            class Order:
                def __init__(self, price, strategy: DiscountStrategy):
                    self.price = price
                    self.strategy = strategy
                def get_total(self):
                    return self.strategy.apply(self.price)
        """).strip(),
        "dry_run": "1. Instantiate order: `order = Order(100, TenPercentDiscount())`.\n2. `order.get_total()` executes the injected strategy.\n3. Easily swap discount algorithms without modifying the core `Order` class.",
        "complexity": "Runs in $O(1)$ constant time.",
        "edge_cases": "• **Strategy Overhead:** Clients must be aware of the different strategies to choose the correct one, increasing coupling in simple scripts."
    },
    "mvc": {
        "title": "MVC Pattern",
        "category": "Design Patterns",
        "concept": "MVC (Model-View-Controller) is an architectural pattern that separates an application into three main components:\n1. **Model:** Manages data and business logic.\n2. **View:** Renders the user interface.\n3. **Controller:** Handles user input and updates the Model and View.",
        "code": textwrap.dedent("""
            class Model:
                def __init__(self): self.data = "APCRE Study"
            class View:
                def render(self, data): print("View Display:", data)
            class Controller:
                def __init__(self, model, view):
                    self.model = model
                    self.view = view
                def update(self):
                    self.view.render(self.model.data)
        """).strip(),
        "dry_run": "1. Controller coordinates operations.\n2. Fetches current state from the Model.\n3. Passes state data to the View to be rendered.",
        "complexity": "Architectural design pattern with no runtime overhead.",
        "edge_cases": "• **Massive Controller Anti-pattern:** Placing too much logic inside the Controller leads to bloated, unmaintainable classes. Keep controllers thin by encapsulating business logic inside the Model."
    },
    "adapter": {
        "title": "Adapter Pattern",
        "category": "Design Patterns",
        "concept": "The Adapter pattern allows classes with incompatible interfaces to work together by wrapping one class in an adapter that translates requests.",
        "code": textwrap.dedent("""
            class OldSystem:
                def legacy_request(self): return "Legacy Response"
            
            class Adapter:
                def __init__(self, old_system):
                    self.old_system = old_system
                def request(self):
                    # Translation layer
                    return f"Adapted: {self.old_system.legacy_request()}"
        """).strip(),
        "dry_run": "1. Client expects the new `request()` interface.\n2. Invoking `Adapter.request()` translates the call and runs the old system's `legacy_request()` method.\n3. Returns the formatted response successfully.",
        "complexity": "Adds a single-hop $O(1)$ method call overhead.",
        "edge_cases": "• **Two-way adapters:** If bidirectionality is required, the adapter must implement translations for both target interfaces."
    },
    "builder": {
        "title": "Builder Pattern",
        "category": "Design Patterns",
        "concept": "The Builder pattern separates the construction of a complex object from its representation, allowing the same construction process to create different representations.",
        "code": textwrap.dedent("""
            class Computer:
                def __init__(self):
                    self.parts = []
            
            class ComputerBuilder:
                def __init__(self):
                    self.computer = Computer()
                def add_cpu(self):
                    self.computer.parts.append("CPU")
                    return self # Return self for method chaining
                def add_ram(self):
                    self.computer.parts.append("RAM")
                    return self
                def build(self):
                    return self.computer
        """).strip(),
        "dry_run": "1. Instantiate: `builder = ComputerBuilder()`.\n2. Method chaining: `builder.add_cpu().add_ram().build()`.\n3. Constructs and returns the fully assembled computer object.",
        "complexity": "Construction steps run in $O(1)$ constant time.",
        "edge_cases": "• **Partially Built Objects:** Guard the final `build()` method to ensure that all required core components are present before returning the object."
    },

    # 15. Programming Fundamentals
    "variable": {
        "title": "Variables & States",
        "category": "Python Programming Fundamentals",
        "concept": "In Python, a variable is simply a reference (pointer) to an object stored in memory. Variables are dynamically typed and do not require type declarations.",
        "code": textwrap.dedent("""
            x = 10         # x references integer object 10
            x = "Python"   # x now references string object "Python"
        """).strip(),
        "dry_run": "1. Allocates integer object 10, binds reference to `x`.\n2. Allocates string object 'Python', redirects reference `x` to this new object.\n3. Old integer object 10 reference count drops, marking it for garbage collection.",
        "complexity": "Variable declarations and reference bindings take $O(1)$ constant time.",
        "edge_cases": "• **Shared References:** Assigning `y = x` binds `y` to the same object. For mutable objects (like lists), modifying `y` also modifies `x`!"
    },
    "data_type": {
        "title": "Python Data Types",
        "category": "Python Programming Fundamentals",
        "concept": "Python's core built-in data types include:\n- **Numeric:** `int`, `float`, `complex`\n- **Sequence:** `list`, `tuple`, `range`, `str`\n- **Mapping:** `dict`\n- **Set:** `set`, `frozenset`\n- **Boolean:** `bool`\n- **Binary:** `bytes`, `bytearray`",
        "code": textwrap.dedent("""
            # Dynamic type identification
            value = 42.5
            print("Type:", type(value)) # <class 'float'>
        """).strip(),
        "dry_run": "1. Allocates float object 42.5.\n2. Querying `type(value)` returns the underlying class constructor reference.",
        "complexity": "Type checks run in $O(1)$ constant time.",
        "edge_cases": "• **Dynamic Typing traps:** Because variables are dynamically typed, ensure inputs are validated using `isinstance()` before performing mathematical operations."
    },
    "type_casting": {
        "title": "Type Casting",
        "category": "Python Programming Fundamentals",
        "concept": "Type Casting converts a variable from one data type to another. It can be implicit (done automatically by Python) or explicit (done manually using functions like `int()`, `float()`, `str()`).",
        "code": textwrap.dedent("""
            # Explicit type casting
            num_str = "100"
            num_int = int(num_str)  # Cast string to int
            print("Calculated:", num_int + 5)
        """).strip(),
        "dry_run": "1. Binds string reference `'100'`.\n2. `int('100')` parses characters and allocates a new integer object `100`.\n3. Performs addition successfully.",
        "complexity": "Parsing strings of length $L$ to integers takes $O(L)$ time.",
        "edge_cases": "• **Casting Failures:** Casting non-numeric strings (e.g. `int('abc')`) raises a `ValueError`. Wrap casting in `try-except` blocks."
    },
    "io": {
        "title": "Input / Output",
        "category": "Python Programming Fundamentals",
        "concept": "Input/Output allows programs to interact with users. Python uses the `input()` function for reading user inputs (always returned as strings) and `print()` for console outputs.",
        "code": textwrap.dedent("""
            # Simple Input/Output
            name = input("Enter your name: ")
            print(f"Hello, {name}!")
        """).strip(),
        "dry_run": "1. `input()` halts execution, awaiting standard input streams.\n2. User types input and hits Enter. Value is returned as a string.\n3. `print()` formats and writes the output string to standard output.",
        "complexity": "I/O speeds depend heavily on hardware terminal rendering and user input speed.",
        "edge_cases": "• **Non-Interactive Mode:** Running `input()` in non-interactive environments (like automated backend subprocesses) raises an `EOFError`."
    },
    "operator": {
        "title": "Python Operators",
        "category": "Python Programming Fundamentals",
        "concept": "Python operators are symbols used to perform operations on variables. Types include:\n- **Arithmetic:** `+`, `-`, `*`, `/`, `%`, `//` (floor division), `**` (exponentiation)\n- **Comparison:** `==`, `!=`, `<`, `>`, `<=`, `>=`\n- **Logical:** `and`, `or`, `not`\n- **Bitwise:** `&`, `|`, `^`, `~`, `<<`, `>>`\n- **Assignment:** `=`, `+=`, `-=`\n- **Identity / Membership:** `is`, `is not`, `in`, `not in`",
        "code": textwrap.dedent("""
            # Mathematical operations
            a, b = 5, 2
            print("Floor Division:", a // b)  # 2
            print("Exponentiation:", a ** b)  # 25
        """).strip(),
        "dry_run": "1. Performs floor division `5 // 2`, discarding fractional remainders and returning integer 2.\n2. Exponentiation calculates $5^2$, returning 25.",
        "complexity": "Arithmetic calculations are resolved in hardware $O(1)$ constant time.",
        "edge_cases": "• **Floating Point precision:** Float calculations can suffer from rounding errors due to binary representation (e.g. `0.1 + 0.2` yields `0.30000000000000004`). Use the `decimal` module for absolute precision."
    },
    "conditional": {
        "title": "Conditional Statements",
        "category": "Python Programming Fundamentals",
        "concept": "Conditional Statements control execution flow based on boolean expressions using `if`, `elif`, and `else` blocks.",
        "code": textwrap.dedent("""
            def evaluate_score(score):
                if score >= 90: return "A"
                elif score >= 80: return "B"
                else: return "C"
        """).strip(),
        "dry_run": "1. If `score = 85`, checks the first condition `85 >= 90`. Evaluates as False.\n2. Checks the second condition `85 >= 80`. Evaluates as True. Exits and returns 'B'.",
        "complexity": "Conditional branch tests are resolved in $O(1)$ constant time.",
        "edge_cases": "• **Condition Order:** Always arrange conditions from most specific to most general to avoid incorrect evaluations."
    },
    "loop": {
        "title": "Loops & Iterations",
        "category": "Python Programming Fundamentals",
        "concept": "Loops repeat a block of code. Python supports two main loop types:\n1. **`for` loop:** Iterates over a sequence (list, range, string).\n2. **`while` loop:** Repeats code as long as a boolean condition remains True.",
        "code": textwrap.dedent("""
            # Iterating using a for loop
            for i in range(3):
                print(i) # 0, 1, 2
        """).strip(),
        "dry_run": "1. `range(3)` yields index 0. Prints 0.\n2. Iterates to index 1. Prints 1.\n3. Iterates to index 2. Prints 2. Loop finishes.",
        "complexity": "A loop executing $N$ times runs in $O(N)$ linear time.",
        "edge_cases": "• **Infinite loops:** If a `while` loop's condition never becomes False, it loops infinitely, exhausting CPU resources. Always ensure the loop variable is updated."
    },
    "function": {
        "title": "Functions & Scope",
        "category": "Python Programming Fundamentals",
        "concept": "Functions are reusable blocks of code. They accept parameters, execute logic in their local scope, and return values using the `return` keyword.",
        "code": textwrap.dedent("""
            def greet_user(username: str) -> str:
                \"\"\"Greet the user.\"\"\"
                return f"Welcome, {username}"
        """).strip(),
        "dry_run": "1. Call `greet_user('ammar')`. Parameters are bound to local scope variable `username`.\n2. String formatting is executed.\n3. Returns the result string and exits local scope.",
        "complexity": "Function calls execute in $O(1)$ time.",
        "edge_cases": "• **Variable Scope:** Variables defined inside a function belong to its local scope and cannot be accessed outside the function."
    },
    "lambda": {
        "title": "Lambda Functions",
        "category": "Python Programming Fundamentals",
        "concept": "Lambda functions are small, anonymous, one-line functions defined using the `lambda` keyword. They are ideal for quick, throwaway operations.",
        "code": textwrap.dedent("""
            # Lambda function sorting coordinates by y-value
            points = [(1, 9), (2, 3), (3, 5)]
            points.sort(key=lambda p: p[1])
            print("Sorted points:", points) # [(2, 3), (3, 5), (1, 9)]
        """).strip(),
        "dry_run": "1. `points.sort` iterates through the list of tuples.\n2. Runs the lambda function `lambda p: p[1]` on each tuple, returning its y-value.\n3. Sorts tuples based on the returned y-values.",
        "complexity": "Lambda creations take $O(1)$ time, with identical execution speed to standard functions.",
        "edge_cases": "• **Complexity Trap:** Lambda functions are restricted to a single expression. Attempting to write complex logic or multiline statements inside a lambda violates Python syntax."
    },
    "comprehension": {
        "title": "List & Dict Comprehensions",
        "category": "Python Programming Fundamentals",
        "concept": "Comprehensions provide a concise way to create lists, dictionaries, or sets from existing iterables, replacing slow, verbose `for` loop append blocks.",
        "code": textwrap.dedent("""
            # 1. List Comprehension
            squares = [x**2 for x in range(5)] # [0, 1, 4, 9, 16]
            
            # 2. Dict Comprehension
            square_dict = {x: x**2 for x in range(3)} # {0: 0, 1: 1, 2: 4}
        """).strip(),
        "dry_run": "1. `list` comprehension allocates the list and evaluates the expression for each index.\n2. Iterates internally, appending values to the list.\n3. Returns the populated collection.",
        "complexity": "| Operation | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Comprehension | $O(N)$ | $O(N)$ |",
        "edge_cases": "• **Over-complicating nesting:** Writing deeply nested list comprehensions with multiple `if` conditions makes code extremely hard to read. Split complex loops into standard, readable blocks."
    },
    "exception": {
        "title": "Exception Handling",
        "category": "Python Programming Fundamentals",
        "concept": "Exceptions are runtime errors that halt script execution. Exception handling intercepts these errors using `try`, `except`, `else`, and `finally` blocks, keeping the application stable and alive.",
        "code": textwrap.dedent("""
            try:
                result = 10 / 0
            except ZeroDivisionError:
                result = 0 # Recovery path
            finally:
                print("Execution complete")
        """).strip(),
        "dry_run": "1. `try` block executes division. `10 / 0` raises a `ZeroDivisionError` exception.\n2. Execution immediately jumps to the matching `except ZeroDivisionError` block.\n3. Binds `result = 0`, and runs the `finally` block unconditionally.",
        "complexity": "Normal paths have zero cost. Exception raises walk stack frames in $O(H)$ time.",
        "edge_cases": "• **Bare Except:** Using `except:` catches critical system events like Ctrl+C. Always catch specific exception classes or use `except Exception:`."
    },
    "module": {
        "title": "Modules & Packages",
        "category": "Python Programming Fundamentals",
        "concept": "Modules are `.py` files containing code that can be imported and reused. Packages are directories containing multiple modules and an `__init__.py` file.",
        "code": textwrap.dedent("""
            # Importing a module
            import math
            print("Square Root:", math.sqrt(16))
        """).strip(),
        "dry_run": "1. `import math` checks if the module is already cached in `sys.modules`.\n2. If absent, locates the file, compiles it to bytecode, and runs it to bind the module namespace.",
        "complexity": "Module lookups and imports take $O(1)$ time after initial loading.",
        "edge_cases": "• **Circular Imports:** If Module A imports Module B, and Module B imports Module A, Python raises an `ImportError` due to circular dependency loops."
    },
    "file_handling": {
        "title": "File Handling",
        "category": "Python Programming Fundamentals",
        "concept": "File handling allows programs to read and write files persistently on disk. Python uses the built-in `open()` function, which should always be wrapped in a context manager (`with` statement) to release system resources safely.",
        "code": textwrap.dedent("""
            # Secure file write and read
            with open("report.txt", "w", encoding="utf-8") as f:
                f.write("APCRE Pro log")
            
            with open("report.txt", "r", encoding="utf-8") as f:
                print("Content:", f.read())
        """).strip(),
        "dry_run": "1. Context manager requests a file handle from the OS in write mode `'w'`.\n2. Writes content to the file buffer, flushing to disk.\n3. Automatically closes the file handle when exiting the `with` block.",
        "complexity": "Disk I/O operations are highly dependent on hardware speed, usually taking $O(N)$ time relative to file size.",
        "edge_cases": "• **Missing Files:** Opening a non-existent file in read mode `r` raises a `FileNotFoundError`. Always wrap read operations in try-except blocks."
    },
    "iterator": {
        "title": "Iterators & Iterables",
        "category": "Python Programming Fundamentals",
        "concept": "An Iterable is any object that can return an Iterator (e.g. a list). An Iterator is an object that yields elements one-by-one using the `__next__()` method, raising `StopIteration` when all elements are exhausted.",
        "code": textwrap.dedent("""
            numbers = [10, 20]
            my_iterator = iter(numbers) # Get iterator
            print(next(my_iterator))    # 10
            print(next(my_iterator))    # 20
        """).strip(),
        "dry_run": "1. `iter(numbers)` calls `numbers.__iter__()`, returning an iterator object.\n2. `next(my_iterator)` calls `__next__()`, returning the element at the current index and moving the pointer forward.\n3. Subsequent calls raise `StopIteration` once the array bounds are reached.",
        "complexity": "Retrieving the next element takes $O(1)$ constant time.",
        "edge_cases": "• **Exhausted Iterators:** Once an iterator raises `StopIteration`, it is exhausted and cannot be reset. You must create a new iterator instance to traverse the collection again."
    },
    "generator": {
        "title": "Generators & lazy yield",
        "category": "Python Programming Fundamentals",
        "analogy": "A restaurant making meals to order. Instead of pre-cooking 100 pizzas that go stale on the counter, the chef bakes one fresh pizza at a time only when a customer orders it.",
        "concept": "Generators are special functions that return lazy iterators using the `yield` keyword. Unlike standard functions that return all elements at once, generators produce values one-by-one, saving significant memory when working with large datasets.",
        "code": textwrap.dedent("""
            def count_generator(n):
                # Lazy value generator
                for i in range(n):
                    yield i
            
            gen = count_generator(100000)
            print("First value:", next(gen)) # 0 (Generated on-demand!)
        """).strip(),
        "dry_run": "1. Call `count_generator(100000)`. Python does not run the function body; instead, it returns a generator object.\n2. `next(gen)` executes the function body until it hits the `yield` statement.\n3. Pauses function execution, saves local state, and returns value `0`. Subsequent calls resume execution from this saved state.",
        "complexity": "| Operation | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Value Yield | $O(1)$ | $O(1)$ (practically constant!) |\n| List Equivalent | $O(N)$ | $O(N)$ |",
        "edge_cases": "• **Generator Expressiveness:** You can also create generators using generator expressions: `gen = (x**2 for x in range(10))`."
    },
    "context_manager": {
        "title": "Context Managers",
        "category": "Python Programming Fundamentals",
        "concept": "Context Managers guarantee that allocated system resources (like file handles or database locks) are released safely when operations finish, using `__enter__` and `__exit__` methods inside `with` blocks.",
        "code": textwrap.dedent("""
            class CustomLock:
                def __enter__(self):
                    print("Acquiring Lock...")
                    return self
                def __exit__(self, exc_type, exc_val, exc_tb):
                    print("Releasing Lock safely...")
                    return True # Suppress exceptions
            
            with CustomLock() as lock:
                print("Running operations...")
        """).strip(),
        "dry_run": "1. `with CustomLock()` instantiates the class, executing `__enter__()` to acquire the lock.\n2. Code inside the block runs.\n3. When exiting the block, `__exit__()` executes automatically, releasing the lock safely even if errors occurred inside the block.",
        "complexity": "Entering and exiting context manager blocks takes $O(1)$ constant time.",
        "edge_cases": "• **Exception Suppression:** Returning `True` from `__exit__` tells Python to suppress any exceptions raised inside the block. Ensure this behavior is intended to avoid hiding critical bugs."
    },
    "venv": {
        "title": "Virtual Environments",
        "category": "Python Programming Fundamentals",
        "concept": "Virtual Environments isolate project-specific dependencies. They prevent conflicts between packages required by different applications on the same computer.",
        "code": textwrap.dedent("""
            # Shell commands to configure virtual environment
            # 1. Create: python -m venv .venv
            # 2. Activate (Windows): .venv\\Scripts\\activate
            # 3. Install: pip install -r requirements.txt
        """).strip(),
        "dry_run": "1. Creates a local directory containing copies of the Python executable and pip packages.\n2. Activation updates the environment's `PATH` to point to the local `.venv` binaries first, isolating project dependencies.",
        "complexity": "Isolation is resolved at shell configuration time with zero runtime overhead.",
        "edge_cases": "• **Global Package leakage:** Failing to activate the local virtual environment causes package installations to go to global system directories, leading to dependency conflicts."
    },
    "async_prog": {
        "title": "Async Programming (`asyncio`)",
        "category": "Python Programming Fundamentals",
        "analogy": "A single chef cooking in a kitchen. While waiting for a pot of water to boil (I/O wait), they chop vegetables (CPU task) instead of standing still doing nothing.",
        "concept": "Async programming uses a single-threaded **Event Loop** to run concurrent operations. It uses `async def` and `await` keywords, releasing control of the thread during slow I/O operations (like network requests) to run other tasks.",
        "code": textwrap.dedent("""
            import asyncio
            
            async def fetch_data(task_id):
                print(f"Start Task {task_id}")
                await asyncio.sleep(1) # Simulate slow I/O wait
                print(f"End Task {task_id}")
                return {"task": task_id}
            
            async def main():
                # Run tasks concurrently on the event loop
                results = await asyncio.gather(fetch_data(1), fetch_data(2))
                print(results)
            
            # Start loop
            asyncio.run(main())
        """).strip(),
        "dry_run": "1. `asyncio.run(main())` starts the single-threaded event loop.\n2. `asyncio.gather` registers two tasks on the loop.\n3. Task 1 starts, hits `await asyncio.sleep(1)`. It suspends and releases control of the thread.\n4. The event loop switches to Task 2, which starts and suspends. When the sleep timers expire, both tasks resume and complete concurrently.",
        "complexity": "| Concurrent Style | Concurrency | Thread Overhead | Ideal For |\n| :--- | :--- | :--- | :--- |\n| **Asyncio** | Single-threaded | Extremely low | I/O-bound tasks (network, APIs) |\n| **Multithreading**| Multi-threaded | Moderate (OS context shifts)| Network operations |\n| **Multiprocessing**| Multi-process | High (isolated RAM) | CPU-bound computations |",
        "edge_cases": "• **Blocking Calls:** Blocking functions (like `time.sleep()`) block the entire event loop, freezing all concurrent async tasks. Always use async-compliant libraries (like `aiohttp` or `asyncio.sleep()`) to avoid freezing the loop."
    },
    "multithreading": {
        "title": "Multithreading & GIL",
        "category": "Python Programming Fundamentals",
        "concept": "Multithreading runs multiple execution threads concurrently. In Python, the **Global Interpreter Lock (GIL)** allows only one thread to execute Python bytecode at a time. This makes multithreading highly efficient for **I/O-bound tasks**, but useless for speeding up **CPU-bound tasks**.",
        "code": textwrap.dedent("""
            import threading
            import time
            
            def log_task(name):
                print(f"Thread {name} starting...")
                time.sleep(1) # I/O bound wait
                print(f"Thread {name} finished.")
            
            t1 = threading.Thread(target=log_task, args=("T1",))
            t2 = threading.Thread(target=log_task, args=("T2",))
            t1.start(); t2.start()
            t1.join(); t2.join()
        """).strip(),
        "dry_run": "1. `t1.start()` requests a new thread from the OS, launching it concurrently.\n2. Both threads start, execute `time.sleep(1)` to release CPU control, and run concurrently.\n3. `t1.join()` halts the main program thread until `t1` finishes execution.",
        "complexity": "Thread creation and context switching are managed by the OS, incurring moderate system overhead.",
        "edge_cases": "• **Race Conditions:** Multiple threads accessing and modifying a shared variable concurrently can cause data corruption. Use `threading.Lock` to synchronize access safely."
    },
    "multiprocessing": {
        "title": "Multiprocessing",
        "category": "Python Programming Fundamentals",
        "concept": "Multiprocessing bypasses the Global Interpreter Lock (GIL) by allocating **multiple CPU cores** and launching separate processes, each with its own isolated Python interpreter and memory space. It is ideal for speeding up heavy **CPU-bound computations**.",
        "code": textwrap.dedent("""
            import multiprocessing
            
            def calculate_square(num):
                return num * num
            
            if __name__ == '__main__':
                # Launch process pool utilizing all CPU cores
                with multiprocessing.Pool() as pool:
                    results = pool.map(calculate_square, [10, 20, 30])
                print("Results:", results)
        """).strip(),
        "dry_run": "1. `multiprocessing.Pool()` spawns multiple independent Python processes.\n2. `pool.map` distributes the input array across the processes.\n3. Processes run in parallel on separate CPU cores, return values, and merge results.",
        "complexity": "| Concurrent Model | Parallelism | CPU Overhead | Memory Overhead |\n| :--- | :--- | :--- | :--- |\n| **Multithreading**| Concurrent (GIL) | Low | Low (shared memory) |\n| **Multiprocessing**| Real Parallelism | High | High (isolated RAM copies) |\n| Space Complexity | $O(N \cdot P)$ (P processes) | | |",
        "edge_cases": "• **Windows Process Spawning:** On Windows, subprocesses import the main module, which can cause infinite process spawning loops. Always guard entry points with `if __name__ == '__main__':`."
    }
}


# ═══════════════════════════════════════════════════════════════
# DYNAMIC ADDITIONS FOR EXPANDED KNOWLEDGE COVERAGE (5 TOPICS)
# ═══════════════════════════════════════════════════════════════

APCRE_TOPICS_ALIASES.update({
    "regex": "regex", "regular expression": "regex", "regular expressions": "regex",
    "memory_management": "memory_management", "memory management": "memory_management", "garbage collection": "memory_management",
    "backtracking": "backtracking", "backtrack": "backtracking", "constraint solving": "backtracking",
    "greedy_algorithms": "greedy_algorithms", "greedy": "greedy_algorithms", "greedy algorithm": "greedy_algorithms",
    "dynamic_programming": "dynamic_programming", "dynamic programming": "dynamic_programming", "dp": "dynamic_programming", "memoization": "dynamic_programming", "tabulation": "dynamic_programming"
})

APCRE_TOPICS_DATABASE.update({
    "regex": {
        "title": "Regular Expressions (Regex) in Python",
        "category": "Python Fundamentals",
        "analogy": "A specialized search template or stencil used to find and extract matching patterns from a block of text.",
        "concept": "Regular Expressions (Regex) provide a powerful, domain-specific language for string pattern matching and manipulation using Python's built-in `re` module. It enables searching, splitting, replacing, and grouping characters.",
        "code": "import re\n\ntext = 'User login: ammar_haider, Email: ammar@uet.edu.pk, Date: 2026-05-26'\n# Match email pattern\nemail_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}'\nemail = re.search(email_pattern, text)\nif email:\n    print(\'Found email:\', email.group(0))",
        "dry_run": "1. Compile search pattern \'email_pattern\'.\n2. re.search scans \'text\' string from left to right.\n3. Finds \'ammar@uet.edu.pk\', matches groups, returns Match object.",
        "complexity": "| Operation | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Regex Compilation | $O(M)$ | $O(M)$ |\n| Search / Match | $O(N)$ average | $O(1)$ |",
        "edge_cases": "* **ReDoS (Regex Denial of Service):** Catastrophic backtracking caused by nested quantifiers like `(a+)+`. Always keep quantifiers distinct!\n* **Raw Strings:** Always use raw strings (`r\'...\'`) to prevent backslash escaping traps in pattern definitions."
    },
    "memory_management": {
        "title": "Python Memory Management & Garbage Collection",
        "category": "Python Fundamentals",
        "analogy": "A librarian who keeps track of how many people are reading a book, and automatically returns it to the shelf when no one is holding it.",
        "concept": "Python manages memory dynamically using reference counting and a cyclic garbage collector. Every object has a reference count, which increments when bound and decrements when out of scope. When it hits zero, Python automatically deallocates the memory.",
        "code": "import sys\nimport gc\n\nclass Block:\n    def __init__(self):\n        self.data = [0] * 1000\n\n# Create reference\nx = Block()\nprint(\'Reference count:\', sys.getrefcount(x) - 1)  # Subtract temporary arg ref\n# Force cycle collection\ngc.collect()",
        "dry_run": "1. Object \'Block()\' allocated in heap, reference count set to 1.\n2. sys.getrefcount increments count temporarily, then decrements.\n3. GC runs cyclically to identify and collect unreachable self-referential containers.",
        "complexity": "| Mechanism | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Reference Counting | $O(1)$ | $O(1)$ |\n| Cyclic Garbage Collection | $O(N)$ during collections | $O(1)$ |",
        "edge_cases": "* **Circular References:** Two objects referencing each other (e.g., `a.b = b` and `b.a = a`) will never reach reference count 0. The cyclic Garbage Collector must detect and free them during collections."
    },
    "backtracking": {
        "title": "Backtracking & Constraint Satisfaction Algorithms",
        "category": "Data Structures & Algorithms",
        "analogy": "Solving a maze by taking a path until you hit a dead end, then backtracking to the last junction and trying the alternative path.",
        "concept": "Backtracking is a systematic, recursive search method that builds a candidate solution step-by-step and retracts (backtracks) as soon as it determines the candidate cannot lead to a valid solution. Used for N-Queens, Sudoku, and subset sums.",
        "code": "def solve_n_queens(n):\n    def backtrack(r, cols, pos_diag, neg_diag):\n        if r == n:\n            return 1\n        solutions = 0\n        for c in range(n):\n            if c in cols or (r + c) in pos_diag or (r - c) in neg_diag:\n                continue\n            cols.add(c); pos_diag.add(r + c); neg_diag.add(r - c)\n            solutions += backtrack(r + 1, cols, pos_diag, neg_diag)\n            cols.remove(c); pos_diag.remove(r + c); neg_diag.remove(r - c)\n        return solutions\n    return backtrack(0, set(), set(), set())\n\nprint(\'N-Queens(4) solutions:\', solve_n_queens(4))",
        "dry_run": "1. Start row 0. Try col 0.\n2. Recursively try row 1. Flag collisions on diagonals/cols.\n3. If invalid col, backtrack, remove column flag, try next col.",
        "complexity": "| Algorithm | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| N-Queens Solver | $O(N!)$ | $O(N)$ recursion depth |",
        "edge_cases": "* **Stack Overflow:** High recursion depths can trigger recursion limit errors. Scale maximum recursion limit if needed.\n* **Branch Pruning:** Without intelligent branch pruning, complexity remains fully exponential."
    },
    "greedy_algorithms": {
        "title": "Greedy Optimization Algorithms",
        "category": "Data Structures & Algorithms",
        "analogy": "A shopper who always picks the most expensive item first to maximize value, or a driver who always turns towards the shortest street without looking at the whole map.",
        "concept": "Greedy algorithms make the locally optimal choice at each step in the hope that it will lead to a globally optimal solution. While fast, they do not guarantee global optimality except on specific problems like Fractional Knapsack, Huffman Coding, and Prim/Kruskal.",
        "code": "def fractional_knapsack(weights, values, capacity):\n    # Calculate value density and sort\n    items = sorted(zip(weights, values), key=lambda x: x[1]/x[0], reverse=True)\n    total_val = 0.0\n    for w, v in items:\n        if capacity >= w:\n            capacity -= w; total_val += v\n        else:\n            total_val += v * (capacity / w); break\n    return total_val\n\nprint(\'Knapsack Max Val:\', fractional_knapsack([10, 20, 30], [60, 100, 120], 50))",
        "dry_run": "1. Sort items by value density: [6.0, 5.0, 4.0].\n2. Insert item 1 (10kg, $60), cap becomes 40kg.\n3. Insert item 2 (20kg, $100), cap becomes 20kg.\n4. Take fraction (20/30) of item 3 ($80), Knapsack full.",
        "complexity": "| Algorithm | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Greedy Knapsack | $O(N \\log N)$ sorting | $O(N)$ storage |",
        "edge_cases": "* **0/1 Knapsack Limitations:** Greedy choice fails for 0/1 knapsack where items cannot be divided. For 0/1 Knapsack, dynamic programming must be used instead."
    },
    "dynamic_programming": {
        "title": "Dynamic Programming (DP) & Overlapping Subproblems",
        "category": "Data Structures & Algorithms",
        "analogy": "Instead of writing down 1+1+1+1+1=5, writing down 5, and then when someone adds a +1, immediately answering 6 because you remembered the previous 5.",
        "concept": "Dynamic Programming (DP) is an algorithmic paradigm that solves complex problems by breaking them down into overlapping subproblems, solving each subproblem exactly once, and storing their solutions (memoization or tabulation) to prevent redundant work.",
        "code": "def coin_change(coins, amount):\n    dp = [float(\'inf\')] * (amount + 1)\n    dp[0] = 0\n    for a in range(1, amount + 1):\n        for c in coins:\n            if a - c >= 0:\n                dp[a] = min(dp[a], 1 + dp[a - c])\n    return dp[amount] if dp[amount] != float(\'inf\') else -1\n\nprint(\'Min Coins for 11:\', coin_change([1, 2, 5], 11))",
        "dry_run": "1. Create dp array of size 12. dp[0]=0.\n2. Outer loop amount 1 to 11. dp[1] checks coin 1 -> dp[1]=1.\n3. dp[11] checks coin 5 -> min(dp[11], 1 + dp[6]) -> dp[11]=3.",
        "complexity": "| Algorithm | Time Complexity | Space Complexity |\n| :--- | :--- | :--- |\n| Tabulated DP Coin Change | $O(N \\times A)$ | $O(A)$ array space |",
        "edge_cases": "* **Memory Overflow:** Large state tables can exhaust RAM. Optimize spatial complexity by storing only the previous active state columns when possible."
    }
})

