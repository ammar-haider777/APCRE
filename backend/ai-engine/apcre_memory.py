# -*- coding: utf-8 -*-
"""
APCRE Services - Engineering Memory System (EMS)
Implements persistent local SQLite memory of historical reviews, bugs,
and successful repairs. Integrates 768-D semantic vector cosine similarity search.
"""

import os
import sys
import sqlite3
import json
import numpy as np

# Ensure code_embedder is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from code_embedder import CodeEmbedder

class EngineeringMemory:
    """
    Persistent SQLite engineering memory with local semantic vector index.
    """
    def __init__(self, db_path: str = "apcre_memory.db"):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
        self.embedder = CodeEmbedder()
        self._init_db()

    def _init_db(self):
        """Initializes SQLite schema for persistent engineering memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table to store historical cases (bugs, fixes, reviews, architectures)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engineering_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snippet TEXT NOT NULL,
                fix_code TEXT,
                category TEXT NOT NULL,
                cwe_id TEXT,
                metadata TEXT,
                embedding BLOB,
                success_rate REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        
        # Seed initial standard cases if the database is empty
        self._seed_initial_cases()

    def add_case(self, snippet: str, fix_code: str, category: str, cwe_id: str = None, metadata: dict = None, success_rate: float = 1.0):
        """Adds a new engineering case with its semantic vector embedding to SQLite."""
        embedding_vec = self.embedder.get_embedding(snippet)
        embedding_blob = embedding_vec.tobytes()
        
        meta_str = json.dumps(metadata or {})
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO engineering_cases (snippet, fix_code, category, cwe_id, metadata, embedding, success_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (snippet, fix_code, category, cwe_id, meta_str, embedding_blob, success_rate))
        conn.commit()
        conn.close()

    def search_similar_cases(self, query_snippet: str, category: str = None, limit: int = 3) -> list:
        """
        Calculates cosine similarity between the query snippet's 768-D vector
        and all stored memory records, returning the top matches sorted by similarity score.
        """
        query_vec = self.embedder.get_embedding(query_snippet)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("SELECT id, snippet, fix_code, category, cwe_id, metadata, embedding, success_rate FROM engineering_cases WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT id, snippet, fix_code, category, cwe_id, metadata, embedding, success_rate FROM engineering_cases")
            
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            case_id, snippet, fix_code, cat, cwe, meta, emb_blob, success_rate = row
            
            if emb_blob:
                try:
                    stored_vec = np.frombuffer(emb_blob, dtype=np.float32)
                    # Compute Cosine Similarity: Since both vectors are L2-normalized, similarity = dot product
                    # Let's perform a robust safe computation
                    dot_product = np.dot(query_vec, stored_vec)
                    norm_q = np.linalg.norm(query_vec)
                    norm_s = np.linalg.norm(stored_vec)
                    
                    if norm_q > 0 and norm_s > 0:
                        similarity = float(dot_product / (norm_q * norm_s))
                    else:
                        similarity = 0.0
                except Exception:
                    similarity = 0.0
            else:
                similarity = 0.0
                
            results.append({
                "id": case_id,
                "snippet": snippet,
                "fix_code": fix_code,
                "category": cat,
                "cwe_id": cwe,
                "metadata": json.loads(meta or "{}"),
                "similarity_score": round(similarity, 4),
                "success_rate": success_rate
            })
            
        # Sort by similarity score descending
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:limit]

    def _seed_initial_cases(self):
        """Pre-seeds standard high-fidelity engineering memories for cold starts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM engineering_cases")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            return
            
        # 1. Bare Except Case
        self.add_case(
            snippet="""try:\n    value = cache[key]\nexcept:\n    value = None""",
            fix_code="""try:\n    value = cache[key]\nexcept KeyError:\n    value = None""",
            category="code_smell",
            cwe_id="CWE-755",
            metadata={"title": "Bare Exception Catch", "refactor_time_hours": 0.1}
        )
        
        # 2. Hardcoded API key
        self.add_case(
            snippet="""OPENAI_KEY = "sk-proj-1234567890abcdef12345" """,
            fix_code="""import os\nOPENAI_KEY = os.environ.get("OPENAI_KEY")""",
            category="security",
            cwe_id="CWE-798",
            metadata={"title": "Hardcoded API Token Exposure", "refactor_time_hours": 0.5}
        )
        
        # 3. Subprocess shell execution
        self.add_case(
            snippet="""subprocess.run("ls " + folder_path, shell=True)""",
            fix_code="""subprocess.run(["ls", folder_path], shell=False)""",
            category="security",
            cwe_id="CWE-78",
            metadata={"title": "Unsafe Shell Commands Execution", "refactor_time_hours": 0.4}
        )
        
        # 4. Monolithic Loop
        self.add_case(
            snippet="""out = []\nfor item in collection:\n    if item.is_valid():\n        out.append(item.value)""",
            fix_code="""out = [item.value for item in collection if item.is_valid()]""",
            category="performance",
            metadata={"title": "Nested Appends to List Comprehension", "refactor_time_hours": 0.2}
        )

if __name__ == "__main__":
    memory = EngineeringMemory("apcre_memory_test.db")
    test_query = """
try:
    x = int(input_data)
except:
    x = 0
"""
    similar = memory.search_similar_cases(test_query)
    for s in similar:
        print(f"ID: {s['id']} | Similarity: {s['similarity_score']} | CWE: {s['cwe_id']}")
