# -*- coding: utf-8 -*-
"""
APCRE Services - Self-Improvement Calibration Engine (Phase 17)

Tracks the AI engine's review performance over time by persisting every
review attempt (task type, code snippet, success/failure, confidence,
execution time) into a local SQLite database.  Provides calibrated
confidence scoring that adjusts raw model confidence by the historical
success-to-failure ratio, and exposes statistics and trend data so the
system can observe—and improve on—its own accuracy trajectory.

Key capabilities:
  * record_attempt        – persist a single review outcome
  * get_calibrated_confidence – Bayesian-style confidence adjustment
  * get_statistics        – aggregate metrics (success rate, avg time, etc.)
  * get_improvement_trend – most recent N records for trend visualisation

All data is stored in a SQLite file co-located with the module.
Works 100 % offline with zero external API calls.
"""

import os
import sqlite3
import time
from datetime import datetime


def safe_print(*args, **kwargs):
    """Windows-safe print that replaces unencodable characters."""
    try:
        print(*args, **kwargs)
    except (UnicodeEncodeError, OSError):
        text = " ".join(str(a) for a in args)
        print(text.encode("ascii", errors="replace").decode("ascii"), **kwargs)


class SelfImprovementEngine:
    """
    Self-Improvement Calibration Engine for APCRE.

    Maintains a local SQLite database of historical review attempts and
    uses the accumulated evidence to calibrate future confidence scores.
    The calibration formula penalises confidence proportionally to the
    ratio of past failures:

        adjusted = base_confidence * (1 - 0.2 * (failed / (successful + 1)))

    This ensures that a model which has been consistently wrong on a
    particular task type will report lower (more honest) confidence
    until its track record improves.
    """

    # ------------------------------------------------------------------
    # Construction & schema bootstrap
    # ------------------------------------------------------------------
    def __init__(self, db_path: str = "apcre_self_improvement.db"):
        """
        Initialises the engine and ensures the backing SQLite database
        and schema exist.

        Args:
            db_path: Filename (or relative path) for the SQLite DB.
                     Resolved relative to the directory containing this
                     module so the DB always lives beside the code.
        """
        self.db_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), db_path
        )
        self._init_db()

    def _init_db(self):
        """Creates the ``performance_records`` table if it does not exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_records (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type       TEXT    NOT NULL,
                code_snippet    TEXT,
                attempt_count   INTEGER NOT NULL DEFAULT 1,
                success         BOOLEAN NOT NULL DEFAULT 0,
                confidence      REAL    NOT NULL DEFAULT 0.5,
                execution_time  REAL    NOT NULL DEFAULT 0.0,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------
    def record_attempt(
        self,
        task_type: str,
        code_snippet: str,
        attempt_count: int,
        success: bool,
        confidence: float,
        execution_time: float,
    ) -> int:
        """
        Persists a single review-attempt record.

        Args:
            task_type:      Category of the task (e.g. 'security',
                            'code_smell', 'performance').
            code_snippet:   The source code that was reviewed.
            attempt_count:  How many attempts were needed for this task.
            success:        Whether the review was ultimately successful.
            confidence:     The model's raw confidence score (0.0–1.0).
            execution_time: Wall-clock seconds the review took.

        Returns:
            The ``id`` of the newly inserted row.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO performance_records
                (task_type, code_snippet, attempt_count, success,
                 confidence, execution_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (task_type, code_snippet, attempt_count, int(success),
             confidence, execution_time),
        )
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return row_id

    # ------------------------------------------------------------------
    # Calibration
    # ------------------------------------------------------------------
    def get_calibrated_confidence(
        self, base_confidence: float, task_type: str = None
    ) -> float:
        """
        Returns a calibrated confidence score adjusted by historical
        success / failure ratio.

        Formula:
            adjusted = base_confidence * (1 - 0.2 * (failed / (successful + 1)))

        If no historical data is available the ``base_confidence`` is
        returned unchanged.  The result is clamped to [0.0, 1.0].

        Args:
            base_confidence: Raw confidence from the model (0.0–1.0).
            task_type:       Optional task type filter.  When provided,
                             only records of that type are considered.

        Returns:
            Calibrated confidence value (float, 0.0–1.0).
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if task_type:
            cursor.execute(
                "SELECT success, COUNT(*) FROM performance_records "
                "WHERE task_type = ? GROUP BY success",
                (task_type,),
            )
        else:
            cursor.execute(
                "SELECT success, COUNT(*) FROM performance_records "
                "GROUP BY success"
            )

        rows = cursor.fetchall()
        conn.close()

        successful = 0
        failed = 0
        for success_flag, count in rows:
            if success_flag:
                successful += count
            else:
                failed += count

        if successful + failed == 0:
            return float(base_confidence)

        adjusted = base_confidence * (1.0 - 0.2 * (failed / (successful + 1)))
        return float(max(0.0, min(1.0, adjusted)))

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------
    def get_statistics(self, task_type: str = None) -> dict:
        """
        Returns aggregate performance statistics, optionally filtered by
        task type.

        Returned dict keys:
            * total_attempts   – total number of recorded attempts
            * success_rate     – proportion of successful attempts
            * avg_confidence   – mean raw confidence across all records
            * avg_execution_time – mean execution time (seconds)
            * calibration_factor – the multiplier that would be applied
                                   to a confidence of 1.0

        Args:
            task_type: Optional filter.

        Returns:
            Dictionary of aggregate statistics.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        base_query = "SELECT COUNT(*), AVG(confidence), AVG(execution_time) FROM performance_records"
        success_query = "SELECT COUNT(*) FROM performance_records WHERE success = 1"

        if task_type:
            base_query += " WHERE task_type = ?"
            success_query += " AND task_type = ?"
            cursor.execute(base_query, (task_type,))
            total, avg_conf, avg_time = cursor.fetchone()
            cursor.execute(success_query, (task_type,))
            success_count = cursor.fetchone()[0]
        else:
            cursor.execute(base_query)
            total, avg_conf, avg_time = cursor.fetchone()
            cursor.execute(success_query)
            success_count = cursor.fetchone()[0]

        conn.close()

        total = total or 0
        avg_conf = avg_conf or 0.0
        avg_time = avg_time or 0.0
        success_count = success_count or 0
        failed_count = total - success_count

        success_rate = (success_count / total) if total > 0 else 0.0
        calibration_factor = (
            1.0 - 0.2 * (failed_count / (success_count + 1))
        ) if total > 0 else 1.0

        return {
            "total_attempts": total,
            "success_rate": round(success_rate, 4),
            "avg_confidence": round(avg_conf, 4),
            "avg_execution_time": round(avg_time, 4),
            "calibration_factor": round(max(0.0, min(1.0, calibration_factor)), 4),
        }

    # ------------------------------------------------------------------
    # Trend analysis
    # ------------------------------------------------------------------
    def get_improvement_trend(self, limit: int = 20) -> list:
        """
        Returns the *limit* most recent performance records, ordered
        from oldest to newest so that the caller can visualise the
        improvement trajectory over time.

        Args:
            limit: Maximum number of records to return (default 20).

        Returns:
            List of dicts, each containing: id, task_type, attempt_count,
            success, confidence, execution_time, created_at.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, task_type, attempt_count, success,
                   confidence, execution_time, created_at
            FROM performance_records
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()

        # Reverse so the list runs oldest → newest
        rows.reverse()

        trend = []
        for row in rows:
            trend.append({
                "id": row[0],
                "task_type": row[1],
                "attempt_count": row[2],
                "success": bool(row[3]),
                "confidence": row[4],
                "execution_time": row[5],
                "created_at": row[6],
            })
        return trend


# ======================================================================
# Quick self-test
# ======================================================================
if __name__ == "__main__":
    TEST_DB = "apcre_self_improvement_test.db"
    test_db_full = os.path.join(os.path.dirname(os.path.abspath(__file__)), TEST_DB)

    # Clean up any previous test database
    if os.path.exists(test_db_full):
        os.remove(test_db_full)

    engine = SelfImprovementEngine(db_path=TEST_DB)

    safe_print("=" * 64)
    safe_print("  APCRE Self-Improvement Calibration Engine - Self Test")
    safe_print("=" * 64)

    # -- Record a mix of successes and failures -----------------------
    sample_attempts = [
        ("security",    "password = 'admin123'",          1, True,  0.92, 0.34),
        ("security",    "eval(user_input)",                2, False, 0.65, 0.58),
        ("code_smell",  "except:\\n    pass",              1, True,  0.88, 0.22),
        ("performance", "for i in range(len(lst)): ...",   1, True,  0.75, 0.41),
        ("security",    "subprocess.run(cmd, shell=True)", 1, True,  0.90, 0.30),
        ("code_smell",  "x = x",                          3, False, 0.40, 1.12),
        ("performance", "time.sleep(0) in loop",           1, True,  0.82, 0.29),
        ("security",    "pickle.loads(data)",              1, False, 0.55, 0.47),
        ("code_smell",  "import *",                        1, True,  0.87, 0.19),
        ("performance", "string += chunk in loop",         2, True,  0.78, 0.36),
    ]

    safe_print("\n[1] Recording sample attempts ...")
    for task, snippet, attempts, success, conf, exec_t in sample_attempts:
        row_id = engine.record_attempt(task, snippet, attempts, success, conf, exec_t)
        status = "OK" if success else "FAIL"
        safe_print(f"  #{row_id:>3d}  [{status:>4s}]  {task:<12s}  conf={conf:.2f}  time={exec_t:.2f}s")

    # -- Overall statistics -------------------------------------------
    safe_print("\n[2] Overall statistics:")
    stats = engine.get_statistics()
    for key, val in stats.items():
        safe_print(f"  {key:<22s}: {val}")

    # -- Per-task-type statistics --------------------------------------
    safe_print("\n[3] Per-task-type statistics:")
    for task_type in ("security", "code_smell", "performance"):
        ts = engine.get_statistics(task_type=task_type)
        safe_print(f"  --- {task_type} ---")
        for key, val in ts.items():
            safe_print(f"    {key:<22s}: {val}")

    # -- Calibrated confidence ----------------------------------------
    safe_print("\n[4] Calibrated confidence (base = 0.85):")
    overall = engine.get_calibrated_confidence(0.85)
    safe_print(f"  Overall calibrated   : {overall:.4f}")
    for task_type in ("security", "code_smell", "performance"):
        cal = engine.get_calibrated_confidence(0.85, task_type=task_type)
        safe_print(f"  {task_type:<22s}: {cal:.4f}")

    # -- Improvement trend --------------------------------------------
    safe_print("\n[5] Improvement trend (last 20 records):")
    trend = engine.get_improvement_trend(limit=20)
    safe_print(f"  {'#':<4s} {'Type':<14s} {'Success':<9s} {'Confidence':<12s} {'Time (s)':<10s}")
    safe_print(f"  {'-'*4} {'-'*14} {'-'*9} {'-'*12} {'-'*10}")
    for rec in trend:
        status = "Yes" if rec["success"] else "No"
        safe_print(
            f"  {rec['id']:<4d} {rec['task_type']:<14s} {status:<9s} "
            f"{rec['confidence']:<12.4f} {rec['execution_time']:<10.4f}"
        )

    # -- Cleanup test database ----------------------------------------
    if os.path.exists(test_db_full):
        os.remove(test_db_full)
        safe_print(f"\n[*] Test database cleaned up: {TEST_DB}")

    safe_print("\n" + "=" * 64)
    safe_print("  Self-test complete - all operations executed successfully.")
    safe_print("=" * 64)
