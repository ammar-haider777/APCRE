# -*- coding: utf-8 -*-
import os

target_path = r"c:\Users\WAZIR AMMAR HAIDER\Desktop\fyp\Source_Code\apcre-ui\backend\ai-engine\train_apcre_model.py"

# Define the new expanded script content
script_content = """# -*- coding: utf-8 -*-
\"\"\"
APCRE Services - Rigorously Trained Multi-Class Machine Learning Classifier
Customized for UET Taxila FYP Software Engineering Department.
Trains a balanced, expanded 120-sample dataset (30 per class) with TF-IDF and LogisticRegression.
Saves model and vectorizer locally to 'ml_model.pkl'.
\"\"\"

import pickle
import os
import sys

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import classification_report, accuracy_score
    import numpy as np
    print("[APCRE Trainer] Successfully loaded scikit-learn modules.")
except ImportError:
    print("[APCRE Trainer] Error: scikit-learn is not installed in the active environment.")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# 120-Sample Balanced Dataset (30 per Class)
# ═══════════════════════════════════════════════════════════════
X_train = [
    # ───────────────────────────────────────────────────────────────
    # CLASS 1: Premium OOP & Data Structures (30 Samples)
    # ───────────────────────────────────────────────────────────────
    # 1.1 Stack FIFO
    \"\"\"
    class Stack:
        \\\"\\\"\\\"Efficient implementation of stack data structure.\\\"\\\"\\\"
        def __init__(self):
            self._items = []
        def push(self, item):
            self._items.append(item)
        def pop(self):
            if not self._items:
                raise IndexError("Pop from empty stack")
            return self._items.pop()
        def size(self):
            return len(self._items)
    \"\"\",
    # 1.2 Binary Tree Node
    \"\"\"
    class TreeNode:
        \\\"\\\"\\\"Node definition for binary tree structures.\\\"\\\"\\\"
        def __init__(self, key):
            self.key = key
            self.left = None
            self.right = None
    \"\"\",
    # 1.3 Clean OOP Subclassing
    \"\"\"
    class Animal:
        def __init__(self, name: str):
            self._name = name
        @property
        def name(self):
            return self._name
        def make_sound(self):
            pass

    class Cat(Animal):
        def __init__(self, name: str, breed: str):
            super().__init__(name)
            self._breed = breed
        def make_sound(self):
            return "Meow!"
    \"\"\",
    # 1.4 Optimal O(N) pair finder
    \"\"\"
    def find_pairs_optimal(numbers, target):
        \\\"\\\"\\\"Find pairs that sum to target in O(N) complexity using a hash set.\\\"\\\"\\\"
        seen = set()
        pairs = []
        for num in numbers:
            complement = target - num
            if complement in seen:
                pairs.append((num, complement))
            seen.add(num)
        return pairs
    \"\"\",
    # 1.5 Adjacency Graph
    \"\"\"
    class Graph:
        def __init__(self):
            self.adjacency_list = {}
        def add_vertex(self, vertex):
            if vertex not in self.adjacency_list:
                self.adjacency_list[vertex] = []
        def add_edge(self, v1, v2):
            self.adjacency_list[v1].append(v2)
            self.adjacency_list[v2].append(v1)
    \"\"\",
    # 1.6 O(log N) BST Insertion
    \"\"\"
    class BST:
        \\\"\\\"\\\"Binary Search Tree implementation with O(log N) insert/search.\\\"\\\"\\\"
        def __init__(self):
            self.root = None
        def insert(self, key):
            self.root = self._insert(self.root, key)
        def _insert(self, node, key):
            if node is None:
                return TreeNode(key)
            if key < node.key:
                node.left = self._insert(node.left, key)
            else:
                node.right = self._insert(node.right, key)
            return node
    \"\"\",
    # 1.7 Singly LinkedList
    \"\"\"
    class Node:
        def __init__(self, data=None):
            self.data = data
            self.next = None

    class LinkedList:
        \\\"\\\"\\\"Efficient Singly Linked List with linear operations.\\\"\\\"\\\"
        def __init__(self):
            self.head = None
        def append(self, data):
            new_node = Node(data)
            if not self.head:
                self.head = new_node
                return
            last = self.head
            while last.next:
                last = last.next
            last.next = new_node
    \"\"\",
    # 1.8 Encapsulated User Account
    \"\"\"
    class UserAccount:
        def __init__(self, username, email):
            self._username = username
            self._email = email
        @property
        def email(self):
            return self._email
        @email.setter
        def email(self, new_email):
            if "@" in new_email:
                self._email = new_email
            else:
                raise ValueError("Invalid email format")
    \"\"\",
    # 1.9 BST Search
    \"\"\"
    class BSTSearch:
        \\\"\\\"\\\"Binary Search Tree lookup with O(log N) average time complexity.\\\"\\\"\\\"
        def __init__(self, val=0):
            self.val = val
            self.left = None
            self.right = None
        def search(self, root, key):
            if root is None or root.val == key:
                return root
            if root.val < key:
                return self.search(root.right, key)
            return self.search(root.left, key)
    \"\"\",
    # 1.10 Doubly LinkedList deletion
    \"\"\"
    class DLLNode:
        def __init__(self, val):
            self.val = val
            self.next = None
            self.prev = None

    class DoublyLinkedList:
        \\\"\\\"\\\"Doubly linked list with clean bidirectional node pointer updates.\\\"\\\"\\\"
        def __init__(self):
            self.head = None
        def remove_node(self, node):
            if not self.head or not node:
                return
            if self.head == node:
                self.head = node.next
            if node.next:
                node.next.prev = node.prev
            if node.prev:
                node.prev.next = node.next
    \"\"\",
    # 1.11 Encapsulated Stack
    \"\"\"
    class EncapsulatedStack:
        \\\"\\\"\\\"Encapsulated stack protecting structural bounds with properties.\\\"\\\"\\\"
        def __init__(self, limit=10):
            self._limit = limit
            self._data = []
        @property
        def is_empty(self):
            return len(self._data) == 0
        def push(self, item):
            if len(self._data) >= self._limit:
                raise OverflowError("Stack full")
            self._data.append(item)
        def pop(self):
            if self.is_empty:
                raise IndexError("Pop from empty stack")
            return self._data.pop()
    \"\"\",
    # 1.12 Set intersection O(N+M)
    \"\"\"
    def intersect_optimal(list1, list2):
        \\\"\\\"\\\"Determine common elements in O(N + M) complexity using sets.\\\"\\\"\\\"
        set1 = set(list1)
        set2 = set(list2)
        return list(set1.intersection(set2))
    \"\"\",
    # 1.13 Min Heap Push/Pop
    \"\"\"
    class MinHeap:
        \\\"\\\"\\\"Binary Min-Heap with O(log N) operations.\\\"\\\"\\\"
        def __init__(self):
            self.heap = []
        def push(self, val):
            self.heap.append(val)
            self._upheap(len(self.heap) - 1)
        def pop(self):
            if not self.heap:
                raise IndexError("Empty heap")
            self._swap(0, len(self.heap) - 1)
            val = self.heap.pop()
            self._downheap(0)
            return val
        def _swap(self, i, j):
            self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        def _upheap(self, idx):
            p = (idx - 1) // 2
            if idx > 0 and self.heap[idx] < self.heap[p]:
                self._swap(idx, p)
                self._upheap(p)
        def _downheap(self, idx):
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx
            if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
                smallest = left
            if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
                smallest = right
            if smallest != idx:
                self._swap(idx, smallest)
                self._downheap(smallest)
    \"\"\",
    # 1.14 Double Stack Queue
    \"\"\"
    class QueueTwoStacks:
        \\\"\\\"\\\"Optimal FIFO Queue implemented using two LIFO stacks.\\\"\\\"\\\"
        def __init__(self):
            self.in_stack = []
            self.out_stack = []
        def enqueue(self, item):
            self.in_stack.append(item)
        def dequeue(self):
            if not self.out_stack:
                while self.in_stack:
                    self.out_stack.append(self.in_stack.pop())
            if not self.out_stack:
                raise IndexError("Queue empty")
            return self.out_stack.pop()
    \"\"\",
    # 1.15 AVL Height Check
    \"\"\"
    class AVLTreeNode:
        def __init__(self, val):
            self.val = val
            self.left = None
            self.right = None
            self.height = 1

    def get_height(node):
        return node.height if node else 0

    def get_balance(node):
        if not node: return 0
        return get_height(node.left) - get_height(node.right)
    \"\"\",
    # 1.16 Dijkstra Node Priority
    \"\"\"
    class PriorityNode:
        \\\"\\\"\\\"Graph node with cost priorities for Dijkstra algorithm.\\\"\\\"\\\"
        def __init__(self, name: str, cost: float):
            self._name = name
            self._cost = cost
        @property
        def name(self):
            return self._name
        @property
        def cost(self):
            return self._cost
        def __lt__(self, other):
            return self._cost < other._cost
    \"\"\",
    # 1.17 Singly Linked List Reversal
    \"\"\"
    def reverse_linked_list(head):
        \\\"\\\"\\\"Reverse singly linked list nodes in O(N) time and O(1) space.\\\"\\\"\\\"
        prev = None
        curr = head
        while curr:
            next_temp = curr.next
            curr.next = prev
            prev = curr
            curr = next_temp
        return prev
    \"\"\",
    # 1.18 Circular Queue
    \"\"\"
    class CircularFIFOQueue:
        \\\"\\\"\\\"FIFO Queue wrapping dynamically via modulo pointer indexing.\\\"\\\"\\\"
        def __init__(self, cap=5):
            self._data = [None] * cap
            self._cap = cap
            self._head = 0
            self._tail = 0
            self._size = 0
        def enqueue(self, val):
            if self._size == self._cap:
                raise OverflowError("Queue full")
            self._data[self._tail] = val
            self._tail = (self._tail + 1) % self._cap
            self._size += 1
    \"\"\",
    # 1.19 Dynamic Array Resizing
    \"\"\"
    class ResizingArray:
        \\\"\\\"\\\"Contiguous memory block with O(1) amortized tail insertions.\\\"\\\"\\\"
        def __init__(self):
            self._cap = 2
            self._size = 0
            self._items = [None] * self._cap
        def append(self, val):
            if self._size == self._cap:
                self._resize(self._cap * 2)
            self._items[self._size] = val
            self._size += 1
        def _resize(self, new_cap):
            new_data = [None] * new_cap
            for i in range(self._size):
                new_data[i] = self._items[i]
            self._items = new_data
            self._cap = new_cap
    \"\"\",
    # 1.20 Topological Sort
    \"\"\"
    class TopologicalSorter:
        \\\"\\\"\\\"Exposes clean graph dependency sorting using DFS node cycles.\\\"\\\"\\\"
        def __init__(self, num_nodes: int):
            self._nodes = num_nodes
            self._adj = {i: [] for i in range(num_nodes)}
        def add_dependency(self, u: int, v: int):
            self._adj[u].append(v)
    \"\"\",
    # 1.21 Quick Sort
    \"\"\"
    def quick_sort(arr: list) -> list:
        \\\"\\\"\\\"Efficient partition-based sorting O(N log N) average complexity.\\\"\\\"\\\"
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_sort(left) + middle + quick_sort(right)
    \"\"\",
    # 1.22 Memoized Fibonacci
    \"\"\"
    class FibonacciMemo:
        \\\"\\\"\\\"Computes Fibonacci numbers in linear O(N) using dynamic programming.\\\"\\\"\\\"
        def __init__(self):
            self._cache = {0: 0, 1: 1}
        def get_value(self, n: int) -> int:
            if n not in self._cache:
                self._cache[n] = self.get_value(n - 1) + self.get_value(n - 2)
            return self._cache[n]
    \"\"\",
    # 1.23 Graph BFS
    \"\"\"
    from collections import deque
    def graph_bfs(graph: dict, start_vertex) -> list:
        \\\"\\\"\\\"Traverse graph BFS style using an efficient double-ended queue.\\\"\\\"\\\"
        visited = set([start_vertex])
        queue = deque([start_vertex])
        path = []
        while queue:
            vertex = queue.popleft()
            path.append(vertex)
            for neighbor in graph.get(vertex, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return path
    \"\"\",
    # 1.24 Prefix Trie
    \"\"\"
    class TrieNode:
        def __init__(self):
            self.children = {}
            self.is_end_of_word = False

    class PrefixTrie:
        \\\"\\\"\\\"Encapsulated prefix tree with efficient standard operations.\\\"\\\"\\\"
        def __init__(self):
            self.root = TrieNode()
        def insert(self, word: str) -> None:
            node = self.root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.is_end_of_word = True
    \"\"\",
    # 1.25 Custom Chaining Hash Map
    \"\"\"
    class HashBucketNode:
        def __init__(self, key, val):
            self.key = key
            self.val = val
            self.next = None

    class ChainingHashMap:
        \\\"\\\"\\\"Hash map resolving collisions via linked list chaining.\\\"\\\"\\\"
        def __init__(self, capacity: int = 37):
            self._capacity = capacity
            self._buckets = [None] * capacity
        def _get_hash(self, key) -> int:
            return hash(key) % self._capacity
    \"\"\",
    # 1.26 Graph DFS Iterative
    \"\"\"
    def graph_dfs_iterative(graph: dict, start) -> list:
        \\\"\\\"\\\"Standard graph depth-first traversal using custom tracking stack.\\\"\\\"\\\"
        visited = set()
        stack = [start]
        path = []
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                visited.add(vertex)
                path.append(vertex)
                for neighbor in reversed(graph.get(vertex, [])):
                    if neighbor not in visited:
                        stack.append(neighbor)
        return path
    \"\"\",
    # 1.27 List Comprehension Transpose
    \"\"\"
    def optimal_matrix_transpose(matrix: list) -> list:
        \\\"\\\"\\\"Transpose matrix columns using zip with O(R * C) optimal bounds.\\\"\\\"\\\"
        if not matrix or not matrix[0]:
            return []
        return [list(row) for row in zip(*matrix)]
    \"\"\",
    # 1.28 Priority Queue Heap
    \"\"\"
    import heapq
    class PriorityQueue:
        \\\"\\\"\\\"Thread-safe priority queue wrapper using standard library heapq.\\\"\\\"\\\"
        def __init__(self):
            self._queue = []
            self._index = 0
        def push(self, item, priority: float):
            heapq.heappush(self._queue, (-priority, self._index, item))
            self._index += 1
        def pop(self):
            if not self._queue:
                raise IndexError("Pop from empty queue")
            return heapq.heappop(self._queue)[-1]
    \"\"\",
    # 1.29 Custom Deque
    \"\"\"
    class BidirectionalNode:
        def __init__(self, val=None):
            self.val = val
            self.next = None
            self.prev = None

    class CustomDeque:
        \\\"\\\"\\\"Encapsulated Double Ended Queue with clear boundary safety.\\\"\\\"\\\"
        def __init__(self):
            self.head = BidirectionalNode()
            self.tail = BidirectionalNode()
            self.head.next = self.tail
            self.tail.prev = self.head
    \"\"\",
    # 1.30 Binary Search Iterative
    \"\"\"
    def binary_search(arr: list, target) -> int:
        \\\"\\\"\\\"Classic lookup in sorted list with O(log N) operations.\\\"\\\"\\\"
        low, high = 0, len(arr) - 1
        while low <= high:
            mid = (low + high) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                low = mid + 1
            else:
                high = mid - 1
        return -1
    \"\"\",

    # ───────────────────────────────────────────────────────────────
    # CLASS 2: Suboptimal Data Structures (30 Samples)
    # ───────────────────────────────────────────────────────────────
    # 2.1 Nested search O(N^2)
    \"\"\"
    def find_pairs_slow(numbers, target):
        \\\"\\\"\\\"Inefficient sum search using O(N^2) nested loops.\\\"\\\"\\\"
        pairs = []
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                if numbers[i] + numbers[j] == target:
                    pairs.append((numbers[i], numbers[j]))
        return pairs
    \"\"\",
    # 2.2 Duplication slow
    \"\"\"
    def find_duplicates_slow(lst):
        \\\"\\\"\\\"Slow duplication check using nested loops and count calls.\\\"\\\"\\\"
        dups = []
        for item in lst:
            if lst.count(item) > 1 and item not in dups:
                dups.append(item)
        return dups
    \"\"\",
    # 2.3 Dict lookup slow
    \"\"\"
    def get_value_from_dictionary(dct, key):
        \\\"\\\"\\\"Slow key lookup by iterating keys instead of O(1) hash access.\\\"\\\"\\\"
        for k in dct.keys():
            if k == key:
                return dct[k]
        return None
    \"\"\",
    # 2.4 Set search slow
    \"\"\"
    def slow_search(data, value):
        \\\"\\\"\\\"Redundant O(N) search on a raw list instead of converting to set.\\\"\\\"\\\"
        found = False
        for x in data:
            if x == value:
                found = True
        return found
    \"\"\",
    # 2.5 Bubble sort O(N^2)
    \"\"\"
    def bubble_sort(arr):
        \\\"\\\"\\\"Bubble sort with nested O(N^2) loops.\\\"\\\"\\\"
        n = len(arr)
        for i in range(n):
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
        return arr
    \"\"\",
    # 2.6 List intersection slow
    \"\"\"
    def find_common_elements_slow(lst1, lst2):
        \\\"\\\"\\\"Find intersection using nested loops instead of set intersection.\\\"\\\"\\\"
        common = []
        for x in lst1:
            for y in lst2:
                if x == y and x not in common:
                    common.append(x)
        return common
    \"\"\",
    # 2.7 Matrix iterate slow
    \"\"\"
    def check_contains_slow(matrix, target):
        \\\"\\\"\\\"Iterates all cells in a sorted matrix instead of binary search.\\\"\\\"\\\"
        for row in range(len(matrix)):
            for col in range(len(matrix[0])):
                if matrix[row][col] == target:
                    return True
        return False
    \"\"\",
    # 2.8 List lookup slow
    \"\"\"
    def list_lookup_in_loop(large_list, query_list):
        \\\"\\\"\\\"Slow lookup of item in large_list for each item in query_list.\\\"\\\"\\\"
        results = []
        for item in query_list:
            if item in large_list:
                results.append(item)
        return results
    \"\"\",
    # 2.9 Matrix multiply O(N^3)
    \"\"\"
    def slow_matrix_multiplication(A, B):
        \\\"\\\"\\\"Cubical O(N^3) nested loops for naive matrix multiply.\\\"\\\"\\\"
        n = len(A)
        C = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    C[i][j] += A[i][k] * B[k][j]
        return C
    \"\"\",
    # 2.10 List unique slow
    \"\"\"
    def lookup_duplicates_slow(data):
        \\\"\\\"\\\"O(N^2) list membership scans inside loops instead of sets.\\\"\\\"\\\"
        unique_items = []
        for x in data:
            if x not in unique_items:
                unique_items.append(x)
        return unique_items
    \"\"\",
    # 2.11 Element shift slow
    \"\"\"
    def redundant_copy_slow(arr):
        \\\"\\\"\\\"O(N^2) element shifting by naive duplicate removal loop.\\\"\\\"\\\"
        out = []
        for x in arr:
            for y in arr:
                if x == y and x not in out:
                     out.append(x)
        return out
    \"\"\",
    # 2.12 Frequency loop slow
    \"\"\"
    def count_frequency_slow(items):
        \\\"\\\"\\\"Inefficient frequency count using list.count() inside a loop.\\\"\\\"\\\"
        freq = {}
        for x in items:
            if items.count(x) > 1:
                freq[x] = items.count(x)
        return freq
    \"\"\",
    # 2.13 Un-indexed list search
    \"\"\"
    def unindexed_nested_search(data1, data2):
        \\\"\\\"\\\"Lookups in dynamic raw lists inside nested loops creating O(N^3).\\\"\\\"\\\"
        matches = []
        for item1 in data1:
            for item2 in data2:
                if item1 == item2:
                    if item1 in data1 and item2 in data2:
                        matches.append(item1)
        return matches
    \"\"\",
    # 2.14 List count duplicates
    \"\"\"
    def duplicate_count_nested_loop(collection):
        \\\"\\\"\\\"Determine repeats via duplicate nested index counters.\\\"\\\"\\\"
        repeats = []
        for i in range(len(collection)):
            for j in range(len(collection)):
                if i != j and collection[i] == collection[j]:
                    if collection[i] not in repeats:
                        repeats.append(collection[i])
        return repeats
    \"\"\",
    # 2.15 Naive Selection Sort
    \"\"\"
    def naive_selection_sort(items):
        \\\"\\\"\\\"Sort list naively by scanning minimums inside nested loop.\\\"\\\"\\\"
        for i in range(len(items)):
            min_idx = i
            for j in range(i + 1, len(items)):
                if items[j] < items[min_idx]:
                    min_idx = j
            items[i], items[min_idx] = items[min_idx], items[i]
        return items
    \"\"\",
    # 2.16 Nested list counts
    \"\"\"
    def double_list_count_check(list_a, list_b):
        \\\"\\\"\\\"Slow comparison by invoking count checks repeatedly inside loop.\\\"\\\"\\\"
        out = []
        for x in list_a:
            if list_a.count(x) > 1 and list_b.count(x) > 1:
                out.append(x)
        return out
    \"\"\",
    # 2.17 Polynomial loop iterate
    \"\"\"
    def polynomial_loop_matrix_transpose(matrix):
        \\\"\\\"\\\"Slow transpose iteration by calling cell access inside loops.\\\"\\\"\\\"
        n = len(matrix)
        out = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    if k == 0:
                        out[j][i] = matrix[i][j]
        return out
    \"\"\",
    # 2.18 Set difference naive
    \"\"\"
    def set_difference_slow(lst1, lst2):
        \\\"\\\"\\\"Determine list exclusion naively scanning elements in loop.\\\"\\\"\\\"
        diff = []
        for x in lst1:
            if x not in lst2:
                for y in lst1:
                    if y == x and y not in diff:
                        diff.append(y)
        return diff
    \"\"\",
    # 2.19 Naive string concat
    \"\"\"
    def slow_string_concat_loop(strings):
        \\\"\\\"\\\"Inefficiently concatenate strings in loop creating O(N^2) allocations.\\\"\\\"\\\"
        res = ""
        for s in strings:
            for char in s:
                res = res + char
        return res
    \"\"\",
    # 2.20 Slow linear list lookup
    \"\"\"
    def linear_list_lookup_loop(items, targets):
        \\\"\\\"\\\"Search targets in raw items lists inside nested loop.\\\"\\\"\\\"
        found = []
        for t in targets:
            for x in items:
                if x == t:
                    found.append(x)
        return found
    \"\"\",
    # 2.21 Slow Matrix Transpose
    \"\"\"
    def slow_matrix_transpose(matrix):
        \\\"\\\"\\\"Transpose matrix naively using multiple nested redundant loops.\\\"\\\"\\\"
        rows = len(matrix)
        cols = len(matrix[0])
        result = [[0]*rows for _ in range(cols)]
        for r in range(rows):
            for c in range(cols):
                for k in range(rows):
                    if k == r:
                        result[c][r] = matrix[r][c]
        return result
    \"\"\",
    # 2.22 Fibonacci Recursion (Slow)
    \"\"\"
    def slow_fibonacci(n):
        \\\"\\\"\\\"Extremely slow exponential O(2^N) recursive fibonacci.\\\"\\\"\\\"
        if n <= 0:
            return 0
        if n == 1:
            return 1
        return slow_fibonacci(n - 1) + slow_fibonacci(n - 2)
    \"\"\",
    # 2.23 Linear graph search
    \"\"\"
    def slow_graph_path_check(edges_list, start, end):
        \\\"\\\"\\\"Linear search over all edges inside loop creating quadratic checks.\\\"\\\"\\\"
        paths = []
        for x in edges_list:
            for y in edges_list:
                if x[0] == start and y[1] == end:
                    for z in edges_list:
                        if x[1] == z[0] and z[1] == y[0]:
                            paths.append((x, z, y))
        return paths
    \"\"\",
    # 2.24 Slow Substring Search
    \"\"\"
    def manual_substring_search(text, pattern):
        \\\"\\\"\\\"Inefficient index iteration of substring match O(N*M) complexity.\\\"\\\"\\\"
        matches = []
        for i in range(len(text) - len(pattern) + 1):
            match = True
            for j in range(len(pattern)):
                if text[i+j] != pattern[j]:
                    match = False
            if match:
                matches.append(i)
        return matches
    \"\"\",
    # 2.25 Selection Sort (Slow)
    \"\"\"
    def selection_sort_slow(items):
        \\\"\\\"\\\"Selection sort with multiple nested index scanning and counts.\\\"\\\"\\\"
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[j] < items[i]:
                    items[i], items[j] = items[j], items[i]
        return items
    \"\"\",
    # 2.26 Inefficient Unique Count
    \"\"\"
    def count_uniques_slow(data):
        \\\"\\\"\\\"Inefficient unique count scanning counts over large list.\\\"\\\"\\\"
        unique_count = 0
        for x in data:
            if data.count(x) == 1:
                unique_count += 1
        return unique_count
    \"\"\",
    # 2.27 Naive List Filtering
    \"\"\"
    def filter_lists_slow(list1, list2):
        \\\"\\\"\\\"Filter items in list1 that are not in list2 using nested loops.\\\"\\\"\\\"
        out = []
        for x in list1:
            for y in list2:
                if x == y:
                    if x not in out:
                        out.append(x)
        return out
    \"\"\",
    # 2.28 Cubical O(N^3) Matrix Sum
    \"\"\"
    def cubical_matrix_sum(matrix):
        \\\"\\\"\\\"Naive O(N^3) cell traversal to calculate sum of rows.\\\"\\\"\\\"
        total = 0
        n = len(matrix)
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    if k == 0:
                        total += matrix[i][j]
        return total
    \"\"\",
    # 2.29 List index lookup in loop
    \"\"\"
    def lookup_index_loop_slow(items, query):
        \\\"\\\"\\\"O(N^2) search by calling index lookup repeatedly inside loop.\\\"\\\"\\\"
        indices = []
        for q in query:
            if q in items:
                indices.append(items.index(q))
        return indices
    \"\"\",
    # 2.30 Slow Set Intersection
    \"\"\"
    def list_intersection_naive(lst1, lst2):
        \\\"\\\"\\\"Determines intersection by looping list 1 and scanning list 2.\\\"\\\"\\\"
        shared = []
        for x in lst1:
            if x in lst2:
                if x not in shared:
                    shared.append(x)
        return shared
    \"\"\",

    # ───────────────────────────────────────────────────────────────
    # CLASS 3: Poor OOP Architecture (30 Samples)
    # ───────────────────────────────────────────────────────────────
    # 3.1 Car missing init
    \"\"\"
    class Car:
        # Missing proper __init__ constructor, uses loose details setter
        def set_details(self, make, model):
            self.make = make
            self.model = model
        def display(self):
            print(self.make, self.model)
    \"\"\",
    # 3.2 Account missing property
    \"\"\"
    class Account:
        # Lacks any data encapsulation or property getters
        def __init__(self, balance):
            self.balance = balance
        def get_balance(self):
            return self.balance
    \"\"\",
    # 3.3 Subclass missing super
    \"\"\"
    class ChildClass:
        # Implements OOP inheritance subclassing without calling parent init
        def __init__(self, action):
            self.action = action
        def do_action(self):
            pass
    \"\"\",
    # 3.4 Rectangle missing init
    \"\"\"
    class Rectangle:
        # Missing constructor __init__, misses encapsulation
        def set_dims(self, w, h):
            self.w = w
            self.h = h
        def area(self):
            return self.w * self.h
    \"\"\",
    # 3.5 Student missing constructor
    \"\"\"
    class Student:
        # No __init__, uses loose setters to define instance fields
        def initialize(self, name, roll_no):
            self.name = name
            self.roll_no = roll_no
        def get_name(self):
            return self.name
    \"\"\",
    # 3.6 Dog missing super
    \"\"\"
    class Dog:
        # Inherits from Animal but fails to invoke super().__init__
        def __init__(self, breed):
            self.breed = breed
    \"\"\",
    # 3.7 Product missing init
    \"\"\"
    class Product:
        # Lacks any __init__ or private member protection
        def set_price(self, price):
            self.price = price
        def get_price(self):
            return self.price
    \"\"\",
    # 3.8 DB missing constructor
    \"\"\"
    class DatabaseConnection:
        # Missing __init__ constructor, requires setup call
        def configure(self, host, port):
            self.host = host
            self.port = port
        def connect(self):
            print("Connecting to", self.host)
    \"\"\",
    # 3.9 Coordinates Point loose
    \"\"\"
    class CoordinatesPoint:
        # Missing constructor __init__, directly sets dynamic fields
        def configure(self, lat, lon):
            self.latitude = lat
            self.longitude = lon
        def format_str(self):
            return f"{self.latitude}, {self.longitude}"
    \"\"\",
    # 3.10 SubWorker missing super
    \"\"\"
    class ParentWorker:
        def __init__(self, wage):
            self.wage = wage

    class SubWorker(ParentWorker):
        # Missing super().__init__(wage) call in custom subclass init
        def __init__(self, wage, shift):
            self.shift = shift
        def print_wage(self):
            print(self.wage)
    \"\"\",
    # 3.11 UserObject loose
    \"\"\"
    class LooseUserObject:
        # Missing proper constructor encapsulation, uses direct assignment
        def setup_profile(self, name, age):
            self.name = name
            self.age = age
        def update_age(self, new_age):
            self.age = new_age
    \"\"\",
    # 3.12 Account direct access
    \"\"\"
    class DirectAccountConfig:
        # Un-encapsulated class variable initialization with no constructor
        def set_keys(self, access_key, secret_key):
            self.access_key = access_key
            self.secret_key = secret_key
        def get_access(self):
            return self.access_key
    \"\"\",
    # 3.13 Class using global variables
    \"\"\"
    class GlobalUserBinder:
        # Avoids instance context variables, binds dynamically to global state
        def bind_user(self, uid):
            global current_user_id
            current_user_id = uid
        def fetch_user(self):
            return current_user_id
    \"\"\",
    # 3.14 Direct mutations of properties
    \"\"\"
    class MutatingCircle:
        # Exposes fields directly to outside modification without validation
        def set_radius(self, r):
            self.radius = r
        def area(self):
            return 3.14159 * self.radius * self.radius
    \"\"\",
    # 3.15 Direct database config
    \"\"\"
    class LooseDBClient:
        # Missing initial constructor, directly assigns raw server config
        def setup(self, db_url):
            self.url = db_url
        def query(self):
            print("Querying database at", self.url)
    \"\"\",
    # 3.16 Method overloading mimicking
    \"\"\"
    class FakeOverloader:
        # Implements poor object behavior using manual type validations inside loose methods
        def execute(self, a, b=None):
            if b is None:
                self.val = a
            else:
                self.val = a + b
    \"\"\",
    # 3.17 Point missing constructor
    \"\"\"
    class Point3D:
        # Lacks proper __init__ and exposes coordinates directly without setters
        def set_xyz(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z
        def sum_coords(self):
            return self.x + self.y + self.z
    \"\"\",
    # 3.18 Loose Config Map
    \"\"\"
    class LooseConfigMap:
        # Exposes configurations directly without initial configuration
        def load_defaults(self):
            self.env = "dev"
            self.port = 8080
        def get_env(self):
            return self.env
    \"\"\",
    # 3.19 Subclass no parent call
    \"\"\"
    class Component:
        def __init__(self, name):
            self.name = name

    class Button(Component):
        # Missing parent initial constructor call button
        def __init__(self, action):
            self.action = action
        def run(self):
            print("Executing:", self.action)
    \"\"\",
    # 3.20 Loose Session Object
    \"\"\"
    class UserSession:
        # Missing proper __init__, sessions mapped on loose dynamic assignments
        def login(self, token):
            self.token = token
        def get_token(self):
            return self.token
    \"\"\",
    # 3.21 Animal missing constructor
    \"\"\"
    class DogSubclass:
        # Dynamic variable setup inside method instead of constructor
        def setup_dog(self, name, breed):
            self.name = name
            self.breed = breed
        def bark(self):
            print(self.name, "says woof")
    \"\"\",
    # 3.22 Employee dynamic attributes
    \"\"\"
    class EmployeeRecord:
        # Avoids initial __init__, attributes attached on method call
        def configure_record(self, emp_id, salary):
            self.emp_id = emp_id
            self.salary = salary
        def display(self):
            return f"ID: {self.emp_id}"
    \"\"\",
    # 3.23 BankAccount missing properties
    \"\"\"
    class UnprotectedAccount:
        # Exposes mutable balance directly without properties/getters
        def __init__(self, start_balance):
            self.balance = start_balance
        def deposit(self, amt):
            self.balance += amt
    \"\"\",
    # 3.24 Shape no parent call
    \"\"\"
    class ParentShape:
        def __init__(self, color):
            self.color = color

    class ChildCircle(ParentShape):
        # Child class constructor overrides parent but fails to invoke super()
        def __init__(self, color, radius):
            self.radius = radius
    \"\"\",
    # 3.25 Book direct access
    \"\"\"
    class LooseBookObject:
        # Lacks properly formatted __init__ constructor config
        def set_metadata(self, title, author):
            self.title = title
            self.author = author
    \"\"\",
    # 3.26 Device missing constructor
    \"\"\"
    class NetworkDevice:
        # Dynamic configuration without constructor instantiation
        def assign_ips(self, ip, gateway):
            self.ip = ip
            self.gateway = gateway
    \"\"\",
    # 3.27 Global state binder
    \"\"\"
    class GlobalDBSession:
        # Binds session attributes directly to global maps
        def bind_db(self, db_name):
            global active_db_name
            active_db_name = db_name
    \"\"\",
    # 3.28 Loose Session Token
    \"\"\"
    class LooseWebSession:
        # Session tokens attached dynamic outside standard setup
        def initialize_token(self, token_val):
            self.token = token_val
    \"\"\",
    # 3.29 Mutating Point
    \"\"\"
    class Vector3D:
        # Missing constructor, directly assigns raw coordinates
        def set_coords(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z
    \"\"\",
    # 3.30 Loose Config Manager
    \"\"\"
    class LooseConfigClient:
        # Missing constructor config, directly runs options setter
        def configure_options(self, debug_mode):
            self.debug = debug_mode
    \"\"\",

    # ───────────────────────────────────────────────────────────────
    # CLASS 4: Style & PEP 8 Anti-patterns (30 Samples)
    # ───────────────────────────────────────────────────────────────
    # 4.1 camelCase, bare except
    \"\"\"
    def calculateAverageValue(numbersList, limitValue=10):
        # camelCase naming and mutable defaults
        totalValue = 0
        try:
            for val in numbersList:
                totalValue += val
        except:
            # Bare except clause
            pass
        return totalValue / len(numbersList)
    \"\"\",
    # 4.2 mutable default, == None comparison
    \"\"\"
    def processData(dataMap={}):
        # Mutable defaults are unsafe
        if dataMap == None:
            # Comparison to None using ==
            dataMap = {"default": 1}
        print("Processing data map", dataMap)
    \"\"\",
    # 4.3 Star import, camelCase, mutable default list
    \"\"\"
    from math import *
    def computeCircleArea(radiusValue, optionsList=[]):
        # Star import, camelCase, mutable default list
        if optionsList == None:
            optionsList = []
        try:
            return pi * radiusValue * radiusValue
        except:
            pass
    \"\"\",
    # 4.4 camelCase parameter, mutable dictionary default
    \"\"\"
    def retrieveUserProfile(userIdValue, cacheMap={}):
        # camelCase parameter, mutable dictionary default
        if userIdValue == None:
            return None
        try:
            val = cacheMap[userIdValue]
        except:
            pass
        return val
    \"\"\",
    # 4.5 camelCase naming, bare except
    \"\"\"
    def parseRawJSON(jsonTextString=""):
        # camelCase naming convention
        resultDict = {}
        try:
            import json
            resultDict = json.loads(jsonTextString)
        except:
            # Bare except block catches KeyboardInterrupt
            pass
        return resultDict
    \"\"\",
    # 4.6 camelCase name, poor comparisons
    \"\"\"
    def executeActionOnData(dataItemsList, operationCallback=None):
        # camelCase name and poor comparisons
        if dataItemsList == None:
            dataItemsList = []
        for x in dataItemsList:
            try:
                operationCallback(x)
            except:
                pass
    \"\"\",
    # 4.7 Mutable default dict, camelCase variable naming
    \"\"\"
    def loadConfigData(configFilePath=None, activeSettingsDict={}):
        # Mutable default dict, camelCase variable naming
        if configFilePath == None:
            configFilePath = "config.json"
        try:
            print("Loading file", configFilePath)
        except:
            pass
    \"\"\",
    # 4.8 Mutable default argument list and camelCase function name
    \"\"\"
    def cleanUpTemporaryFiles(filePathsList=[]):
        # Mutable default argument list and camelCase function name
        if filePathsList == None:
            filePathsList = []
        try:
            import os
            for path in filePathsList:
                os.remove(path)
        except:
            pass
    \"\"\",
    # 4.9 camelCase configs, bare except
    \"\"\"
    def loadConfigurationsFromFile(filePathName=""):
        # camelCase variable and bare except style
        if filePathName == None:
            filePathName = "default.cfg"
        try:
            with open(filePathName, "r") as f:
                return f.read()
        except:
            pass
    \"\"\",
    # 4.10 camelCase parameter, mutable default dict
    \"\"\"
    def saveUserData(userIdValue, payloadDict={}):
        # camelCase parameters, mutable default dict, == None comparison
        if userIdValue == None:
            raise ValueError("Missing ID")
        try:
            print("Saving", userIdValue, payloadDict)
        except Exception:
            pass
    \"\"\",
    # 4.11 Mutable default list, camelCase configs
    \"\"\"
    def collectMetricsList(targetEndpointString="", accumulatedList=[]):
        # Mutable default list and camelCase variable names
        if targetEndpointString == None:
            targetEndpointString = "localhost"
        try:
            accumulatedList.append(targetEndpointString)
        except:
            pass
    \"\"\",
    # 4.12 camelCase, mutable default dict, bare except
    \"\"\"
    def cleanupActiveSessions(activeSessionsMap={}):
        # camelCase naming, mutable default dict, unused variable, bare except
        temporarySessionCount = 0
        try:
            activeSessionsMap.clear()
        except:
            pass
    \"\"\",
    # 4.13 print debug statements, camelCase
    \"\"\"
    def printTemporaryUserRecords(recordsList=[]):
        # print statements for debugging, camelCase, mutable default
        if recordsList == None:
            recordsList = []
        for r in recordsList:
            print("DEBUG: User record is", r)
        try:
            print("Completed print run")
        except:
            pass
    \"\"\",
    # 4.14 eval usage, bare except
    \"\"\"
    def evaluateDynamicExpression(exprString=""):
        # camelCase parameter, eval usage, bare except
        try:
            resultValue = eval(exprString)
            return resultValue
        except:
            pass
    \"\"\",
    # 4.15 comparison with True
    \"\"\"
    def verifyAdminStatus(userRoleString="", isActiveStatus=True):
        # Comparison with True using ==, camelCase parameter
        if isActiveStatus == True:
            try:
                print("Role is", userRoleString)
            except:
                pass
    \"\"\",
    # 4.16 camelCase list comprehension
    \"\"\"
    def filterEmptyNames(namesList=[]):
        # camelCase parameter, mutable default list, unused variable in loop
        if namesList == None:
            namesList = []
        filteredNames = [n.strip() for n in namesList if n == None]
        try:
            print("Filter complete")
        except:
            pass
    \"\"\",
    # 4.17 bare try-except, print debug
    \"\"\"
    def executeCalculationRun(valA=0, valB=0):
        # camelCase, print debug, bare except
        try:
            print("valA:", valA, "valB:", valB)
            return valA + valB
        except:
            pass
    \"\"\",
    # 4.18 mutable default, == None comparison
    \"\"\"
    def generateMetricsReport(inputDataDict={}):
        # Mutable default dict, == None comparison
        if inputDataDict == None:
            inputDataDict = {}
        try:
            print("Report created successfully")
        except:
            pass
    \"\"\",
    # 4.19 camelCase method names
    \"\"\"
    def clearCachedSessionElements(sessionsCacheMap={}):
        # camelCase naming, mutable default dict, bare except
        try:
            sessionsCacheMap.clear()
        except:
            pass
    \"\"\",
    # 4.20 print debug, == None comparison
    \"\"\"
    def checkAuthenticationToken(tokenValue=""):
        # camelCase parameter, print statements, == None comparison
        if tokenValue == None:
            print("Authentication failed: token is None")
        try:
            print("Authentication succeeded")
        except:
            pass
    \"\"\",
    # 4.21 print debug, camelCase
    \"\"\"
    def analyzeFileContents(fileNameVal):
        # camelCase and print statements
        print("DEBUG: Processing file", fileNameVal)
        try:
            with open(fileNameVal, "r") as f:
                return f.read()
        except:
            pass
    \"\"\",
    # 4.22 comparisons with True/None
    \"\"\"
    def checkStatusFlag(isActive=True):
        # Comparison with True using == and camelCase parameter
        if isActive == True:
            print("Status is active")
    \"\"\",
    # 4.23 mutable defaults list/dict
    \"\"\"
    def registerNewUser(userName, rolesList=[]):
        # Mutable default argument list in method signature
        if rolesList == None:
            rolesList = []
        try:
            print("Registering user", userName)
        except:
            pass
    \"\"\",
    # 4.24 bare try-except statement
    \"\"\"
    def convertToInt(rawStringVal):
        # Bare except block catches KeyboardInterrupt and camelCase parameter
        try:
            return int(rawStringVal)
        except:
            pass
    \"\"\",
    # 4.25 star import math/sys
    \"\"\"
    from os import *
    def listDirectoryElements(pathName):
        # Star import and camelCase variable
        try:
            return listdir(pathName)
        except:
            pass
    \"\"\",
    # 4.26 print debugging statements
    \"\"\"
    def calculateProduct(valA, valB):
        # Multiple print statements and camelCase names
        print("DEBUG: valA =", valA)
        print("DEBUG: valB =", valB)
        try:
            return valA * valB
        except:
            pass
    \"\"\",
    # 4.27 camelCase variables and parameter
    \"\"\"
    def getUserRecord(userIdInput):
        # camelCase variable names and parameters
        userRecordData = {}
        try:
            print("Fetching ID", userIdInput)
        except:
            pass
    \"\"\",
    # 4.28 comparison with False
    \"\"\"
    def checkNetworkState(isConnectedVal=True):
        # Comparison with False using == and camelCase
        if isConnectedVal == False:
            print("Network is disconnected")
    \"\"\",
    # 4.29 bare except with mutable default
    \"\"\"
    def queryEndpointData(urlTextString="", paramsDict={}):
        # Mutable default dict, camelCase, bare except
        try:
            print("Fetching URL", urlTextString)
        except:
            pass
    \"\"\",
    # 4.30 mutable default dictionary, camelCase
    \"\"\"
    def cacheSessionTokens(sessionMapData={}):
        # Mutable default dict, camelCase parameter
        try:
            print("Caching session dictionary", sessionMapData)
        except:
            pass
    \"\"\"
]

y_train = (
    ["Premium OOP & Data Structures (Clean O(1) operations & proper abstraction)"] * 30 +
    ["Suboptimal Data Structures (O(N^2) Loop complexity detected)"] * 30 +
    ["Poor OOP Architecture (Missing constructor __init__ or properties)"] * 30 +
    ["Style & PEP 8 Anti-patterns (CamelCase, Bare excepts, or Mutable defaults)"] * 30
)

# ═══════════════════════════════════════════════════════════════
# Model Training Execution
# ═══════════════════════════════════════════════════════════════
def train_model():
    print("[APCRE Trainer] Balanced Training Samples loaded successfully: 120 examples.")
    
    # 1. Stratified 4-Fold validation check prior to final saving to verify F1-performance
    skf = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
    accs = []
    vectorizer_temp = TfidfVectorizer(token_pattern=r"(?u)\\b\\w+\\b")
    
    all_y_true = []
    all_y_pred = []
    
    for train_idx, test_idx in skf.split(X_train, y_train):
        X_tr = [X_train[i] for i in train_idx]
        y_tr = [y_train[i] for i in train_idx]
        X_te = [X_train[i] for i in test_idx]
        y_te = [y_train[i] for i in test_idx]
        
        X_tr_vec = vectorizer_temp.fit_transform(X_tr)
        X_te_vec = vectorizer_temp.transform(X_te)
        
        clf = LogisticRegression(C=1.0, max_iter=200)
        clf.fit(X_tr_vec, y_tr)
        
        preds = clf.predict(X_te_vec)
        all_y_true.extend(y_te)
        all_y_pred.extend(preds)
        accs.append(accuracy_score(y_te, preds))
        
    print("\\n--- Empirical Validation Cross-Validation Metrics ---")
    print(classification_report(all_y_true, all_y_pred))
    print(f"Overall Accuracy: {np.mean(accs)*100:.2f}%")
    
    # 2. Final training run over the complete 120-sample dataset
    print("\\n[APCRE Trainer] Fitting TfidfVectorizer over all 120 samples...")
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\\b\\w+\\b")
    X_vec = vectorizer.fit_transform(X_train)
    
    print("[APCRE Trainer] Training LogisticRegression Classifier...")
    model = LogisticRegression(C=1.0, max_iter=200)
    model.fit(X_vec, y_train)
    
    # 3. Saving pickled pipeline
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml_model.pkl")
    print(f"[APCRE Trainer] Saving final model and vectorizer to {model_path}...")
    with open(model_path, "wb") as f:
        pickle.dump((vectorizer, model), f)
    print("[APCRE Trainer] Pickled model dumped successfully. Local training completed!")

if __name__ == "__main__":
    train_model()
"""

# Write to file
with open(target_path, "w", encoding="utf-8") as f:
    f.write(script_content)

print("[Generator] New train_apcre_model.py successfully written.")
