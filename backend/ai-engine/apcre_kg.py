# -*- coding: utf-8 -*-
"""
APCRE Services - Software Engineering Knowledge Graph (SE-KG)
Acts as the reasoning backbone, modeling structural relations between
Algorithms, Data Structures, SOLID principles, Design Patterns, and Code Smells.
Backed by SQLite for offline persistence and NetworkX-like logical structures.
"""

import sqlite3
import os

class SoftwareKnowledgeGraph:
    """
    Relational Knowledge Graph managing software engineering concepts,
    SOLID principles, design patterns, and code optimizations.
    """
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apcre_knowledge_graph.db")
        self._initialize_database()

    def _initialize_database(self):
        """Creates table schemas for nodes and edges if not already initialized."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Nodes Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kg_nodes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT
            )
        """)
        
        # 2. Edges/Relationships Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kg_edges (
                source_id TEXT,
                target_id TEXT,
                relationship TEXT NOT NULL,
                FOREIGN KEY(source_id) REFERENCES kg_nodes(id),
                FOREIGN KEY(target_id) REFERENCES kg_nodes(id),
                PRIMARY KEY(source_id, target_id, relationship)
            )
        """)
        
        conn.commit()
        
        # Seed initial core nodes and edges if empty
        cursor.execute("SELECT COUNT(*) FROM kg_nodes")
        if cursor.fetchone()[0] == 0:
            self._seed_knowledge_graph(cursor)
            conn.commit()
            
        conn.close()

    def _seed_knowledge_graph(self, cursor):
        """Seeds UET Taxila graduate-level software reasoning nodes and edges."""
        # 1. Seed Nodes
        nodes = [
            # Data Structures
            ("ds_array", "Array", "Data Structure", "Contiguous block of memory storing homogeneous elements."),
            ("ds_linkedlist", "Linked List", "Data Structure", "Linear nodes chained via pointers."),
            ("ds_bst", "Binary Search Tree", "Data Structure", "Node-based binary tree with left < node < right ordering."),
            ("ds_avl", "AVL Tree", "Data Structure", "Self-balancing binary search tree with height-difference factor <= 1."),
            ("ds_heap", "Binary Heap", "Data Structure", "Complete binary tree satisfying heap invariant (min/max)."),
            ("ds_hash", "Hash Table", "Data Structure", "Associative key-value mapping utilizing an index hash function."),
            
            # Algorithms
            ("alg_binary_search", "Binary Search", "Algorithm", "Logarithmic interval search over sorted collections."),
            ("alg_dijkstra", "Dijkstra's Algorithm", "Algorithm", "Shortest path solver on weighted graphs without negative edges."),
            ("alg_memoization", "Memoization", "Algorithm", "Caching expensive function results to optimize subproblems."),
            ("alg_quicksort", "Quick Sort", "Algorithm", "Pivot-based divide-and-conquer sorting."),
            
            # SOLID Principles
            ("solid_srp", "Single Responsibility Principle (SRP)", "SOLID", "A class should have only one reason to change."),
            ("solid_ocp", "Open-Closed Principle (OCP)", "SOLID", "Software modules should be open for extension but closed for modification."),
            ("solid_lsp", "Liskov Substitution Principle (LSP)", "SOLID", "Subclasses must be substitutable for their superclasses without affecting correctness."),
            ("solid_dip", "Dependency Inversion Principle (DIP)", "SOLID", "High-level modules should depend on abstractions, not concretions."),
            
            # Design Patterns
            ("pat_singleton", "Singleton Pattern", "Design Pattern", "Restricts instantiation of a class to a single object instance."),
            ("pat_factory", "Factory Method Pattern", "Design Pattern", "Provides an interface for creating objects in a superclass."),
            ("pat_observer", "Observer Pattern", "Design Pattern", "Define a one-to-many dependency relationship between objects."),
            
            # Code Smells & Security anti-patterns
            ("smell_nested_loop", "Nested Loops", "Code Smell", "Loops nested inside loops causing exponential O(N^2) complexity."),
            ("smell_global_mutations", "Global Mutations", "Code Smell", "Direct modifications to global state, breaking modular encapsulation."),
            ("smell_eval_exec", "Dynamic Metaprogramming", "Security Risk", "Using eval() or exec() with untrusted variable code execution."),
            ("smell_bare_except", "Bare Except", "Code Smell", "Catching all exceptions indiscriminately, hiding critical bugs.")
        ]
        
        cursor.executemany("INSERT INTO kg_nodes VALUES (?, ?, ?, ?)", nodes)
        
        # 2. Seed Edges/Relationships
        edges = [
            ("alg_binary_search", "ds_array", "Uses"),
            ("alg_dijkstra", "ds_heap", "Uses"),
            ("alg_memoization", "ds_hash", "Uses"),
            
            # SOLID Violations link
            ("smell_global_mutations", "solid_srp", "Violates"),
            ("smell_nested_loop", "ds_avl", "OptimizedBy"),
            ("smell_eval_exec", "solid_ocp", "Violates"),
            ("smell_bare_except", "solid_srp", "Violates"),
            
            # Data structure relations
            ("ds_avl", "ds_bst", "InheritsFrom"),
            ("ds_heap", "ds_array", "BackedBy"),
            
            # Design pattern connections
            ("pat_observer", "solid_dip", "ConformsTo")
        ]
        
        cursor.executemany("INSERT INTO kg_edges VALUES (?, ?, ?)", edges)

    def get_related_concepts(self, node_id: str) -> list:
        """Returns all concepts connected to the target node along with relationship types."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query outgoing relations
        cursor.execute("""
            SELECT n.name, n.category, e.relationship, n.description
            FROM kg_edges e
            JOIN kg_nodes n ON e.target_id = n.id
            WHERE e.source_id = ?
        """, (node_id,))
        relations = cursor.fetchall()
        
        # Query incoming relations
        cursor.execute("""
            SELECT n.name, n.category, e.relationship, n.description
            FROM kg_edges e
            JOIN kg_nodes n ON e.source_id = n.id
            WHERE e.target_id = ?
        """, (node_id,))
        incoming = [(r[0], r[1], f"Is{r[2]}By", r[3]) for r in cursor.fetchall()]
        
        conn.close()
        return relations + incoming

    def get_optimization_path(self, smell_id: str) -> dict:
        """Statically resolves how to optimize a detected code smell or violation using the graph."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.target_id, n.name, e.relationship
            FROM kg_edges e
            JOIN kg_nodes n ON e.target_id = n.id
            WHERE e.source_id = ?
        """, (smell_id,))
        
        paths = cursor.fetchall()
        conn.close()
        
        result = {
            "violates": [],
            "optimized_by": [],
            "uses": []
        }
        
        for target_id, name, rel in paths:
            if rel.lower() == "violates":
                result["violates"].append(name)
            elif rel.lower() == "optimizedby" or rel.lower() == "optimized_by":
                result["optimized_by"].append(name)
            elif rel.lower() == "uses":
                result["uses"].append(name)
                
        return result
