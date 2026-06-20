# -*- coding: utf-8 -*-
import sys
sys.path.append(r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine")

import apcre_topics_db

db = apcre_topics_db.APCRE_TOPICS_DATABASE
keys = sorted(list(db.keys()))

print(f"Total topics in database: {len(keys)}")
print("--- List of first 40 topics ---")
for k in keys[:40]:
    print(f" - {k}")

# Check coverage for some specific requested concepts
requested = [
    "variables", "data_types", "loops", "functions", "recursion", "file_handling", "exception_handling",
    "decorators", "generators", "comprehensions", "regex", "async", "threading", "memory_management",
    "linked_list", "stack", "queue", "tree", "graph", "heap", "trie", "hash_table",
    "backtracking", "greedy", "dynamic_programming", "complexity",
    "encapsulation", "abstraction", "inheritance", "polymorphism",
    "composition", "aggregation", "association", "solid", "design_patterns"
]

print("\n--- Coverage Check ---")
for req in requested:
    matches = [k for k in keys if req in k.lower()]
    print(f"Requested: '{req}' -> Matches: {matches}")
