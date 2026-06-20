# -*- coding: utf-8 -*-
"""
APCRE Services - Phase 18: APCRE-Bench Public Benchmark Dataset
Constructs a reproducible, annotated benchmark corpus of Python code samples
spanning four quality categories: Good OOP Practice, Bad Practice, Security Flaws,
and SOLID/Design Violations.  Each sample carries ground-truth metadata (expected
quality class, CWE identifiers, SOLID violation tags, and cyclomatic complexity
estimates) enabling rigorous evaluation of the APCRE classification pipeline.

Dataset layout:
    apcre-bench/
        samples/good/              - exemplary OOP Python files
        samples/bad/               - anti-pattern / code-smell files
        samples/security/          - files with deliberate security flaws
        samples/design_violations/ - files violating SOLID / design principles
        metadata.json              - ground-truth annotation manifest
        splits.json                - reproducible 80/20 train/test split
"""

import os
import json
import random


class APCREBench:
    """
    APCRE-Bench Public Benchmark Dataset Builder.
    Generates a self-contained corpus of annotated Python code samples for
    training and evaluating the AI-Powered Code Review Engine.
    """

    def __init__(self, bench_dir: str = 'apcre-bench'):
        """
        Initialise the benchmark builder.

        Args:
            bench_dir: Name of the benchmark directory (created alongside this module).
        """
        self.bench_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), bench_dir
        )
        self.categories = ['good', 'bad', 'security', 'design_violations']
        self.metadata_path = os.path.join(self.bench_dir, 'metadata.json')
        self.splits_path = os.path.join(self.bench_dir, 'splits.json')

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(self) -> dict:
        """
        Build the complete APCRE-Bench dataset from scratch.

        Returns:
            dict with keys: success, bench_dir, total_samples, categories,
                            metadata_path, splits_path
        """
        # 1. Create directory tree
        self._create_directories()

        # 2. Seed sample files across all categories
        samples_meta = []
        samples_meta.extend(self._seed_good_samples())
        samples_meta.extend(self._seed_bad_samples())
        samples_meta.extend(self._seed_security_samples())
        samples_meta.extend(self._seed_design_violation_samples())

        # 3. Write metadata.json
        metadata = {
            "benchmark": "APCRE-Bench",
            "version": "1.0.0",
            "description": "Ground-truth annotated Python benchmark corpus for AI code review evaluation.",
            "total_samples": len(samples_meta),
            "categories": {cat: 0 for cat in self.categories},
            "samples": samples_meta,
        }
        for entry in samples_meta:
            metadata["categories"][entry["category"]] += 1

        with open(self.metadata_path, 'w', encoding='utf-8') as fp:
            json.dump(metadata, fp, indent=2, ensure_ascii=False)

        # 4. Write splits.json (reproducible 80/20 train/test)
        random.seed(42)
        filenames = [s["filename"] for s in samples_meta]
        shuffled = filenames[:]
        random.shuffle(shuffled)
        split_idx = int(len(shuffled) * 0.8)
        splits = {
            "seed": 42,
            "train_ratio": 0.8,
            "test_ratio": 0.2,
            "train": shuffled[:split_idx],
            "test": shuffled[split_idx:],
        }
        with open(self.splits_path, 'w', encoding='utf-8') as fp:
            json.dump(splits, fp, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "bench_dir": self.bench_dir,
            "total_samples": len(samples_meta),
            "categories": metadata["categories"],
            "metadata_path": self.metadata_path,
            "splits_path": self.splits_path,
        }

    def get_statistics(self) -> dict:
        """
        Return aggregate statistics for the current benchmark dataset.

        Returns:
            dict with total_samples, category_distribution, train_count, test_count
        """
        metadata = self.load_metadata()
        splits = self._load_splits()

        return {
            "total_samples": metadata.get("total_samples", 0),
            "category_distribution": metadata.get("categories", {}),
            "train_count": len(splits.get("train", [])),
            "test_count": len(splits.get("test", [])),
        }

    def load_metadata(self) -> dict:
        """
        Read and return the persisted metadata.json.

        Returns:
            dict - full metadata manifest including per-sample annotations.
        """
        if not os.path.exists(self.metadata_path):
            return {"error": "metadata.json not found. Run build() first."}

        with open(self.metadata_path, 'r', encoding='utf-8') as fp:
            return json.load(fp)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_splits(self) -> dict:
        """Read and return splits.json."""
        if not os.path.exists(self.splits_path):
            return {}
        with open(self.splits_path, 'r', encoding='utf-8') as fp:
            return json.load(fp)

    def _create_directories(self):
        """Ensure the benchmark directory tree exists."""
        for cat in self.categories:
            path = os.path.join(self.bench_dir, 'samples', cat)
            os.makedirs(path, exist_ok=True)

    def _write_sample(self, category: str, filename: str, content: str):
        """Write a single sample file into the appropriate category folder."""
        path = os.path.join(self.bench_dir, 'samples', category, filename)
        with open(path, 'w', encoding='utf-8') as fp:
            fp.write(content)

    # ==================================================================
    # GOOD practice samples  (>= 5)
    # ==================================================================

    def _seed_good_samples(self) -> list:
        """Seed exemplary OOP Python files demonstrating best practices."""
        samples = []

        # --- Good 1: Repository pattern with encapsulation ---
        self._write_sample('good', 'user_repository.py', '''\
# -*- coding: utf-8 -*-
"""User repository implementing clean data access layer."""


class User:
    """Domain entity representing an application user."""

    def __init__(self, user_id: int, username: str, email: str) -> None:
        self._user_id: int = user_id
        self._username: str = username
        self._email: str = email

    @property
    def user_id(self) -> int:
        """Return the immutable user identifier."""
        return self._user_id

    @property
    def username(self) -> str:
        """Return the username."""
        return self._username

    @property
    def email(self) -> str:
        """Return the user email address."""
        return self._email

    def __repr__(self) -> str:
        return f"User(id={self._user_id}, username={self._username!r})"


class UserRepository:
    """In-memory repository with proper encapsulation and type hints."""

    def __init__(self) -> None:
        self._store: dict[int, User] = {}

    def add(self, user: User) -> None:
        """Persist a user entity."""
        if not isinstance(user, User):
            raise TypeError("Expected a User instance.")
        self._store[user.user_id] = user

    def find_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by primary key."""
        return self._store.get(user_id)

    def list_all(self) -> list[User]:
        """Return all stored users."""
        return list(self._store.values())

    def count(self) -> int:
        """Return the total number of persisted users."""
        return len(self._store)
''')
        samples.append({
            "filename": "user_repository.py",
            "category": "good",
            "expected_class": "good_practice",
            "cwe_ids": [],
            "solid_violations": [],
            "expected_complexity": "low",
            "tags": ["encapsulation", "type_hints", "docstrings", "SRP"],
        })

        # --- Good 2: Strategy pattern ---
        self._write_sample('good', 'sorting_strategy.py', '''\
# -*- coding: utf-8 -*-
"""Strategy pattern for pluggable sorting algorithms."""

from abc import ABC, abstractmethod


class SortStrategy(ABC):
    """Abstract base class for sorting strategies."""

    @abstractmethod
    def sort(self, data: list[int]) -> list[int]:
        """Sort and return a new sorted list."""
        ...


class BubbleSort(SortStrategy):
    """Bubble-sort implementation (educational)."""

    def sort(self, data: list[int]) -> list[int]:
        """O(n^2) comparison sort."""
        arr = data[:]
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr


class MergeSort(SortStrategy):
    """Merge-sort implementation."""

    def sort(self, data: list[int]) -> list[int]:
        """O(n log n) divide-and-conquer sort."""
        if len(data) <= 1:
            return data[:]
        mid = len(data) // 2
        left = self.sort(data[:mid])
        right = self.sort(data[mid:])
        return self._merge(left, right)

    @staticmethod
    def _merge(left: list[int], right: list[int]) -> list[int]:
        """Merge two sorted sublists."""
        result: list[int] = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result


class SortContext:
    """Client context that delegates sorting to a chosen strategy."""

    def __init__(self, strategy: SortStrategy) -> None:
        self._strategy: SortStrategy = strategy

    def execute(self, data: list[int]) -> list[int]:
        """Execute the configured sorting strategy."""
        return self._strategy.sort(data)
''')
        samples.append({
            "filename": "sorting_strategy.py",
            "category": "good",
            "expected_class": "good_practice",
            "cwe_ids": [],
            "solid_violations": [],
            "expected_complexity": "medium",
            "tags": ["strategy_pattern", "OCP", "polymorphism", "docstrings"],
        })

        # --- Good 3: Clean validator with SRP ---
        self._write_sample('good', 'input_validator.py', '''\
# -*- coding: utf-8 -*-
"""Input validation utilities following the Single Responsibility Principle."""

import re


class ValidationResult:
    """Immutable result of a validation check."""

    def __init__(self, is_valid: bool, message: str = "") -> None:
        self._is_valid: bool = is_valid
        self._message: str = message

    @property
    def is_valid(self) -> bool:
        """Whether the validation passed."""
        return self._is_valid

    @property
    def message(self) -> str:
        """Human-readable validation message."""
        return self._message


class EmailValidator:
    """Validates email addresses using a compiled regex pattern."""

    _PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    )

    def validate(self, email: str) -> ValidationResult:
        """Check whether *email* conforms to a valid email format."""
        if not email or not isinstance(email, str):
            return ValidationResult(False, "Email must be a non-empty string.")
        if self._PATTERN.match(email):
            return ValidationResult(True, "Valid email address.")
        return ValidationResult(False, f"Invalid email format: {email!r}")


class PasswordValidator:
    """Enforces minimum password strength requirements."""

    MIN_LENGTH: int = 8

    def validate(self, password: str) -> ValidationResult:
        """Ensure *password* meets strength criteria."""
        if len(password) < self.MIN_LENGTH:
            return ValidationResult(
                False, f"Password must be at least {self.MIN_LENGTH} characters."
            )
        if not re.search(r"[A-Z]", password):
            return ValidationResult(False, "Password must contain an uppercase letter.")
        if not re.search(r"[0-9]", password):
            return ValidationResult(False, "Password must contain a digit.")
        return ValidationResult(True, "Password meets strength requirements.")
''')
        samples.append({
            "filename": "input_validator.py",
            "category": "good",
            "expected_class": "good_practice",
            "cwe_ids": [],
            "solid_violations": [],
            "expected_complexity": "low",
            "tags": ["SRP", "encapsulation", "regex", "type_hints"],
        })

        # --- Good 4: Observer pattern ---
        self._write_sample('good', 'event_system.py', '''\
# -*- coding: utf-8 -*-
"""Observer pattern event system with type-safe subscriptions."""

from typing import Callable


class EventBus:
    """Publish-subscribe event bus decoupling producers from consumers."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable) -> None:
        """Register *callback* to be invoked when *event_name* fires."""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """Remove a previously registered callback."""
        if event_name in self._subscribers:
            self._subscribers[event_name] = [
                cb for cb in self._subscribers[event_name] if cb is not callback
            ]

    def publish(self, event_name: str, data: dict | None = None) -> int:
        """
        Fire *event_name*, invoking all registered callbacks with *data*.

        Returns:
            Number of subscribers notified.
        """
        listeners = self._subscribers.get(event_name, [])
        for listener in listeners:
            listener(data)
        return len(listeners)

    def subscriber_count(self, event_name: str) -> int:
        """Return number of subscribers for *event_name*."""
        return len(self._subscribers.get(event_name, []))
''')
        samples.append({
            "filename": "event_system.py",
            "category": "good",
            "expected_class": "good_practice",
            "cwe_ids": [],
            "solid_violations": [],
            "expected_complexity": "low",
            "tags": ["observer_pattern", "DIP", "loose_coupling", "docstrings"],
        })

        # --- Good 5: Clean data pipeline ---
        self._write_sample('good', 'data_pipeline.py', '''\
# -*- coding: utf-8 -*-
"""Composable data transformation pipeline."""


class TransformStep:
    """Single named transformation step in a pipeline."""

    def __init__(self, name: str, transform_fn) -> None:
        self._name: str = name
        self._fn = transform_fn

    @property
    def name(self) -> str:
        """Human-readable step name."""
        return self._name

    def apply(self, data: list) -> list:
        """Apply the transformation function to *data*."""
        return [self._fn(item) for item in data]


class DataPipeline:
    """
    Ordered chain of TransformSteps applied sequentially.
    Follows the Open-Closed Principle: add steps without modifying existing ones.
    """

    def __init__(self) -> None:
        self._steps: list[TransformStep] = []

    def add_step(self, step: TransformStep) -> "DataPipeline":
        """Append a transformation step and return self for fluent chaining."""
        self._steps.append(step)
        return self

    def execute(self, data: list) -> list:
        """Run all registered steps in order."""
        result = data
        for step in self._steps:
            result = step.apply(result)
        return result

    def describe(self) -> list[str]:
        """List the names of all registered pipeline steps."""
        return [step.name for step in self._steps]
''')
        samples.append({
            "filename": "data_pipeline.py",
            "category": "good",
            "expected_class": "good_practice",
            "cwe_ids": [],
            "solid_violations": [],
            "expected_complexity": "low",
            "tags": ["OCP", "composition", "fluent_api", "type_hints"],
        })

        # --- Good 6: Generic stack with generics ---
        self._write_sample('good', 'generic_stack.py', '''\
# -*- coding: utf-8 -*-
"""Type-safe generic stack implementation."""

from typing import TypeVar, Generic

T = TypeVar("T")


class Stack(Generic[T]):
    """LIFO stack with bounded capacity and clean error handling."""

    DEFAULT_CAPACITY: int = 256

    def __init__(self, capacity: int = DEFAULT_CAPACITY) -> None:
        self._items: list[T] = []
        self._capacity: int = capacity

    def push(self, item: T) -> None:
        """Push *item* onto the stack."""
        if len(self._items) >= self._capacity:
            raise OverflowError(f"Stack capacity ({self._capacity}) exceeded.")
        self._items.append(item)

    def pop(self) -> T:
        """Remove and return the top item."""
        if self.is_empty():
            raise IndexError("Cannot pop from an empty stack.")
        return self._items.pop()

    def peek(self) -> T:
        """Return the top item without removing it."""
        if self.is_empty():
            raise IndexError("Cannot peek at an empty stack.")
        return self._items[-1]

    def is_empty(self) -> bool:
        """Check whether the stack has no elements."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the current number of items."""
        return len(self._items)

    def __repr__(self) -> str:
        return f"Stack(size={self.size()}, capacity={self._capacity})"
''')
        samples.append({
            "filename": "generic_stack.py",
            "category": "good",
            "expected_class": "good_practice",
            "cwe_ids": [],
            "solid_violations": [],
            "expected_complexity": "low",
            "tags": ["generics", "encapsulation", "error_handling", "docstrings"],
        })

        return samples

    # ==================================================================
    # BAD practice samples  (>= 5)
    # ==================================================================

    def _seed_bad_samples(self) -> list:
        """Seed anti-pattern / code-smell Python files."""
        samples = []

        # --- Bad 1: Bare exceptions, no docstrings, magic numbers ---
        self._write_sample('bad', 'data_processor_bad.py', '''\
import os

x = []
y = 0
data = None

def proc(f):
    global x, y, data
    try:
        fh = open(f)
        data = fh.read()
        fh.close()
    except:
        pass
    for i in range(0, len(data)):
        if data[i] == 42:
            x.append(data[i])
            y = y + 1
    if y > 7:
        return 1
    else:
        return 0

def run():
    global x, y
    r = proc("input.dat")
    if r == 1:
        for i in range(0, len(x)):
            print(x[i] * 3.14159)
    x = []
    y = 0
''')
        samples.append({
            "filename": "data_processor_bad.py",
            "category": "bad",
            "expected_class": "bad_practice",
            "cwe_ids": ["CWE-755"],
            "solid_violations": ["SRP"],
            "expected_complexity": "high",
            "tags": ["bare_except", "magic_numbers", "global_state", "no_docstrings"],
        })

        # --- Bad 2: Monolithic function ---
        self._write_sample('bad', 'monolith_handler.py', '''\
import json, os, sys

def handle_everything(action, payload, db_path, log_path, retries):
    result = None
    if action == "read":
        f = open(db_path)
        raw = f.read()
        f.close()
        result = json.loads(raw)
        lf = open(log_path, "a")
        lf.write("read done\\n")
        lf.close()
    elif action == "write":
        f = open(db_path, "w")
        f.write(json.dumps(payload))
        f.close()
        lf = open(log_path, "a")
        lf.write("write done\\n")
        lf.close()
    elif action == "delete":
        os.remove(db_path)
        lf = open(log_path, "a")
        lf.write("delete done\\n")
        lf.close()
    elif action == "retry":
        for i in range(0, retries):
            try:
                handle_everything("read", payload, db_path, log_path, 0)
            except:
                pass
    elif action == "validate":
        if payload is None:
            return -1
        if len(str(payload)) < 3:
            return -2
        if len(str(payload)) > 10000:
            return -3
        return 0
    return result
''')
        samples.append({
            "filename": "monolith_handler.py",
            "category": "bad",
            "expected_class": "bad_practice",
            "cwe_ids": ["CWE-755"],
            "solid_violations": ["SRP", "OCP"],
            "expected_complexity": "very_high",
            "tags": ["monolithic", "bare_except", "no_docstrings", "no_context_managers"],
        })

        # --- Bad 3: Deep nesting, no type hints ---
        self._write_sample('bad', 'nested_nightmare.py', '''\
records = []

def process(items, mode, flag):
    global records
    for i in range(len(items)):
        for j in range(len(items[i])):
            if mode == 1:
                if flag:
                    if items[i][j] > 0:
                        if items[i][j] < 100:
                            if items[i][j] != 50:
                                records.append(items[i][j] * 2)
                            else:
                                records.append(0)
                        else:
                            records.append(-1)
                    else:
                        records.append(-2)
                else:
                    records.append(items[i][j])
            elif mode == 2:
                for k in range(len(items[i][j])):
                    records.append(items[i][j][k])

def get():
    global records
    return records

def clear():
    global records
    records = []
''')
        samples.append({
            "filename": "nested_nightmare.py",
            "category": "bad",
            "expected_class": "bad_practice",
            "cwe_ids": [],
            "solid_violations": ["SRP"],
            "expected_complexity": "very_high",
            "tags": ["deep_nesting", "global_state", "no_docstrings", "no_type_hints"],
        })

        # --- Bad 4: God function with string formatting abuse ---
        self._write_sample('bad', 'report_builder_bad.py', '''\
import time

ALL_REPORTS = []

def make_report(title, rows, fmt, dest, send_email, email_addr, cc_list):
    global ALL_REPORTS
    out = ""
    out = out + "REPORT: " + title + "\\n"
    out = out + "DATE: " + str(time.time()) + "\\n"
    out = out + "=" * 40 + "\\n"
    for r in rows:
        line = ""
        for c in r:
            line = line + str(c) + " | "
        out = out + line + "\\n"
    out = out + "=" * 40 + "\\n"
    if fmt == "txt":
        f = open(dest, "w")
        f.write(out)
        f.close()
    elif fmt == "csv":
        f = open(dest, "w")
        for r in rows:
            f.write(",".join([str(c) for c in r]) + "\\n")
        f.close()
    if send_email:
        print("Sending to " + email_addr)
        for cc in cc_list:
            print("CC: " + cc)
    ALL_REPORTS.append(out)
    return out
''')
        samples.append({
            "filename": "report_builder_bad.py",
            "category": "bad",
            "expected_class": "bad_practice",
            "cwe_ids": [],
            "solid_violations": ["SRP", "OCP"],
            "expected_complexity": "high",
            "tags": ["god_function", "global_state", "no_docstrings", "string_concat"],
        })

        # --- Bad 5: Mutable default argument, shadowing ---
        self._write_sample('bad', 'cache_bad.py', '''\
store = {}

def add(key, value, cache={}):
    cache[key] = value
    store[key] = value
    return cache

def get(key, default=0):
    try:
        return store[key]
    except:
        return default

def remove(key):
    try:
        del store[key]
    except:
        pass

def clear(store={}):
    store = {}
    return store

def size():
    global store
    return len(store)
''')
        samples.append({
            "filename": "cache_bad.py",
            "category": "bad",
            "expected_class": "bad_practice",
            "cwe_ids": ["CWE-755"],
            "solid_violations": ["SRP"],
            "expected_complexity": "medium",
            "tags": ["mutable_default", "bare_except", "shadowing", "global_state"],
        })

        # --- Bad 6: Hardcoded paths, no error handling ---
        self._write_sample('bad', 'config_loader_bad.py', '''\
import json

def load():
    f = open("C:/Users/admin/config.json")
    d = json.loads(f.read())
    f.close()
    return d

def save(d):
    f = open("C:/Users/admin/config.json", "w")
    f.write(json.dumps(d))
    f.close()

def get_val(d, k):
    return d[k]

def set_val(d, k, v):
    d[k] = v
    save(d)
''')
        samples.append({
            "filename": "config_loader_bad.py",
            "category": "bad",
            "expected_class": "bad_practice",
            "cwe_ids": [],
            "solid_violations": ["DIP"],
            "expected_complexity": "low",
            "tags": ["hardcoded_paths", "no_error_handling", "no_docstrings", "no_type_hints"],
        })

        return samples

    # ==================================================================
    # SECURITY flaw samples  (>= 3)
    # ==================================================================

    def _seed_security_samples(self) -> list:
        """Seed files with deliberate, annotated security vulnerabilities."""
        samples = []

        # --- Security 1: SQL Injection ---
        self._write_sample('security', 'sql_injection_vuln.py', '''\
# -*- coding: utf-8 -*-
"""VULNERABLE: SQL injection via string formatting - for benchmark only."""

import sqlite3


def get_user(username):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result


def search_products(keyword):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE name LIKE '%%%s%%'" % keyword)
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_record(table, record_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE id = {record_id}")
    conn.commit()
    conn.close()
''')
        samples.append({
            "filename": "sql_injection_vuln.py",
            "category": "security",
            "expected_class": "security_flaw",
            "cwe_ids": ["CWE-89"],
            "solid_violations": [],
            "expected_complexity": "low",
            "tags": ["sql_injection", "string_formatting", "OWASP_A03"],
        })

        # --- Security 2: Hardcoded credentials ---
        self._write_sample('security', 'hardcoded_creds.py', '''\
# -*- coding: utf-8 -*-
"""VULNERABLE: Hardcoded secrets and credentials - for benchmark only."""

import hashlib


DATABASE_HOST = "prod-db.internal.company.com"
DATABASE_USER = "admin"
DATABASE_PASSWORD = "SuperSecret123!"

API_KEY = "sk-proj-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
JWT_SECRET = "my-jwt-secret-never-change-this-1234567890"

def authenticate(user, passwd):
    if user == "admin" and passwd == "admin123":
        return True
    stored_hash = hashlib.md5(passwd.encode()).hexdigest()
    return stored_hash == "5f4dcc3b5aa765d61d8327deb882cf99"


def get_api_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "X-Secret": JWT_SECRET,
    }


def connect_database():
    conn_str = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/prod"
    return conn_str
''')
        samples.append({
            "filename": "hardcoded_creds.py",
            "category": "security",
            "expected_class": "security_flaw",
            "cwe_ids": ["CWE-798", "CWE-327"],
            "solid_violations": [],
            "expected_complexity": "low",
            "tags": ["hardcoded_credentials", "weak_crypto", "OWASP_A07"],
        })

        # --- Security 3: Shell injection ---
        self._write_sample('security', 'shell_injection.py', '''\
# -*- coding: utf-8 -*-
"""VULNERABLE: OS command injection via shell=True - for benchmark only."""

import subprocess
import os


def list_files(directory):
    result = subprocess.run("ls -la " + directory, shell=True, capture_output=True)
    return result.stdout.decode()


def ping_host(hostname):
    output = subprocess.check_output(
        "ping -c 4 " + hostname, shell=True
    )
    return output.decode()


def cleanup_temp(user_path):
    os.system("rm -rf " + user_path)


def compress_logs(log_dir, archive_name):
    cmd = f"tar -czf {archive_name} {log_dir}"
    subprocess.Popen(cmd, shell=True)
''')
        samples.append({
            "filename": "shell_injection.py",
            "category": "security",
            "expected_class": "security_flaw",
            "cwe_ids": ["CWE-78"],
            "solid_violations": [],
            "expected_complexity": "low",
            "tags": ["shell_injection", "os_system", "OWASP_A03"],
        })

        # --- Security 4: Insecure deserialization + debug mode ---
        self._write_sample('security', 'insecure_deser.py', '''\
# -*- coding: utf-8 -*-
"""VULNERABLE: Insecure deserialization and debug exposure - for benchmark only."""

import pickle


def load_session(raw_bytes):
    session = pickle.loads(raw_bytes)
    return session


def save_session(session_obj, filepath):
    with open(filepath, "wb") as f:
        pickle.dump(session_obj, f)


def start_web_app():
    try:
        from flask import Flask
        app = Flask(__name__)
        app.run(host="0.0.0.0", port=8080, debug=True)
    except ImportError:
        pass
''')
        samples.append({
            "filename": "insecure_deser.py",
            "category": "security",
            "expected_class": "security_flaw",
            "cwe_ids": ["CWE-502", "CWE-489"],
            "solid_violations": [],
            "expected_complexity": "low",
            "tags": ["insecure_deserialization", "debug_mode", "OWASP_A08"],
        })

        return samples

    # ==================================================================
    # DESIGN VIOLATION samples  (>= 3)
    # ==================================================================

    def _seed_design_violation_samples(self) -> list:
        """Seed files demonstrating SOLID and design-principle violations."""
        samples = []

        # --- Design 1: God class violating SRP ---
        self._write_sample('design_violations', 'god_class.py', '''\
# -*- coding: utf-8 -*-
"""VIOLATION: God class handling too many unrelated responsibilities."""

import json
import os
import time


class ApplicationManager:
    """Manages users, logging, database, email, and reports - SRP violation."""

    def __init__(self):
        self.users = []
        self.logs = []
        self.db_data = {}
        self.email_queue = []
        self.reports = []
        self.config = {}

    def add_user(self, name, email):
        self.users.append({"name": name, "email": email, "created": time.time()})

    def remove_user(self, name):
        self.users = [u for u in self.users if u["name"] != name]

    def log_message(self, level, message):
        self.logs.append({"level": level, "msg": message, "ts": time.time()})

    def save_logs(self, path):
        with open(path, "w") as f:
            json.dump(self.logs, f)

    def db_insert(self, table, record):
        if table not in self.db_data:
            self.db_data[table] = []
        self.db_data[table].append(record)

    def db_query(self, table, key, value):
        return [r for r in self.db_data.get(table, []) if r.get(key) == value]

    def queue_email(self, to, subject, body):
        self.email_queue.append({"to": to, "subject": subject, "body": body})

    def send_all_emails(self):
        for email in self.email_queue:
            print(f"Sending: {email['subject']} -> {email['to']}")
        self.email_queue.clear()

    def generate_report(self, title):
        report = f"Report: {title}\\nUsers: {len(self.users)}\\nLogs: {len(self.logs)}"
        self.reports.append(report)
        return report

    def export_report(self, index, filepath):
        with open(filepath, "w") as f:
            f.write(self.reports[index])

    def load_config(self, path):
        with open(path) as f:
            self.config = json.load(f)

    def get_config(self, key):
        return self.config.get(key)
''')
        samples.append({
            "filename": "god_class.py",
            "category": "design_violations",
            "expected_class": "design_violation",
            "cwe_ids": [],
            "solid_violations": ["SRP"],
            "expected_complexity": "high",
            "tags": ["god_class", "SRP_violation", "low_cohesion"],
        })

        # --- Design 2: Tight coupling violating DIP ---
        self._write_sample('design_violations', 'tight_coupling.py', '''\
# -*- coding: utf-8 -*-
"""VIOLATION: Tight coupling - high-level module depends on concrete implementations."""


class MySQLDatabase:
    """Concrete MySQL implementation."""

    def __init__(self):
        self.connected = False
        self.data = {}

    def connect(self):
        self.connected = True

    def insert(self, table, record):
        if table not in self.data:
            self.data[table] = []
        self.data[table].append(record)

    def fetch(self, table):
        return self.data.get(table, [])


class UserService:
    """Directly instantiates and depends on MySQLDatabase - DIP violation."""

    def __init__(self):
        self.db = MySQLDatabase()
        self.db.connect()

    def create_user(self, name, email):
        self.db.insert("users", {"name": name, "email": email})

    def get_users(self):
        return self.db.fetch("users")


class OrderService:
    """Also directly couples to MySQLDatabase - cannot swap implementations."""

    def __init__(self):
        self.db = MySQLDatabase()
        self.db.connect()

    def place_order(self, user, product, qty):
        self.db.insert("orders", {"user": user, "product": product, "qty": qty})

    def get_orders(self):
        return self.db.fetch("orders")
''')
        samples.append({
            "filename": "tight_coupling.py",
            "category": "design_violations",
            "expected_class": "design_violation",
            "cwe_ids": [],
            "solid_violations": ["DIP", "OCP"],
            "expected_complexity": "medium",
            "tags": ["tight_coupling", "DIP_violation", "concrete_dependency"],
        })

        # --- Design 3: LSP violation ---
        self._write_sample('design_violations', 'lsp_violation.py', '''\
# -*- coding: utf-8 -*-
"""VIOLATION: Liskov Substitution Principle - subclass breaks parent contract."""


class Rectangle:
    """Base rectangle with independent width and height."""

    def __init__(self, width, height):
        self._width = width
        self._height = height

    def set_width(self, w):
        self._width = w

    def set_height(self, h):
        self._height = h

    def area(self):
        return self._width * self._height


class Square(Rectangle):
    """Square forces width == height, breaking Rectangle's contract."""

    def __init__(self, side):
        super().__init__(side, side)

    def set_width(self, w):
        self._width = w
        self._height = w  # violates independent dimension contract

    def set_height(self, h):
        self._width = h  # violates independent dimension contract
        self._height = h


def compute_area(rect):
    """Expects a Rectangle: set width=5, height=4, area should be 20."""
    rect.set_width(5)
    rect.set_height(4)
    return rect.area()
''')
        samples.append({
            "filename": "lsp_violation.py",
            "category": "design_violations",
            "expected_class": "design_violation",
            "cwe_ids": [],
            "solid_violations": ["LSP"],
            "expected_complexity": "low",
            "tags": ["LSP_violation", "inheritance_abuse", "contract_breach"],
        })

        # --- Design 4: Interface Segregation violation ---
        self._write_sample('design_violations', 'isp_violation.py', '''\
# -*- coding: utf-8 -*-
"""VIOLATION: Interface Segregation - fat interface forces unused implementations."""

from abc import ABC, abstractmethod


class Worker(ABC):
    """Fat interface forcing all workers to implement every method."""

    @abstractmethod
    def code(self):
        ...

    @abstractmethod
    def test(self):
        ...

    @abstractmethod
    def design(self):
        ...

    @abstractmethod
    def manage(self):
        ...

    @abstractmethod
    def deploy(self):
        ...


class JuniorDeveloper(Worker):
    """Junior dev forced to implement manage/deploy which are not their role."""

    def code(self):
        return "Writing Python code"

    def test(self):
        return "Running unit tests"

    def design(self):
        raise NotImplementedError("Juniors do not design architecture")

    def manage(self):
        raise NotImplementedError("Juniors do not manage teams")

    def deploy(self):
        raise NotImplementedError("Juniors do not deploy to production")


class ProjectManager(Worker):
    """PM forced to implement code/test/deploy which are not their role."""

    def code(self):
        raise NotImplementedError("PMs do not write code")

    def test(self):
        raise NotImplementedError("PMs do not run tests")

    def design(self):
        return "Designing system architecture"

    def manage(self):
        return "Managing project timeline"

    def deploy(self):
        raise NotImplementedError("PMs do not deploy")
''')
        samples.append({
            "filename": "isp_violation.py",
            "category": "design_violations",
            "expected_class": "design_violation",
            "cwe_ids": [],
            "solid_violations": ["ISP"],
            "expected_complexity": "medium",
            "tags": ["ISP_violation", "fat_interface", "NotImplementedError_abuse"],
        })

        return samples


# ======================================================================
# Test block
# ======================================================================

def _safe_print(text: str) -> None:
    """Windows CP1252-safe print wrapper."""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(text.encode('ascii', errors='replace').decode('ascii'))


if __name__ == '__main__':
    _safe_print("=" * 70)
    _safe_print("  APCRE-Bench Public Benchmark Dataset Builder  (Phase 18)")
    _safe_print("=" * 70)

    bench = APCREBench()

    # Build the full dataset
    result = bench.build()

    if result.get("success"):
        _safe_print(f"\n[OK] Benchmark dataset built successfully.")
        _safe_print(f"     Directory : {result['bench_dir']}")
        _safe_print(f"     Total     : {result['total_samples']} samples")
        _safe_print(f"     Categories: {json.dumps(result['categories'], indent=2)}")
        _safe_print(f"     Metadata  : {result['metadata_path']}")
        _safe_print(f"     Splits    : {result['splits_path']}")
    else:
        _safe_print("[FAIL] Build did not succeed.")

    # Load and display statistics
    _safe_print("\n" + "-" * 70)
    _safe_print("  Dataset Statistics")
    _safe_print("-" * 70)
    stats = bench.get_statistics()
    _safe_print(f"  Total samples       : {stats['total_samples']}")
    _safe_print(f"  Category breakdown  : {json.dumps(stats['category_distribution'], indent=2)}")
    _safe_print(f"  Train split count   : {stats['train_count']}")
    _safe_print(f"  Test  split count   : {stats['test_count']}")

    # Verify metadata round-trip
    _safe_print("\n" + "-" * 70)
    _safe_print("  Metadata Verification")
    _safe_print("-" * 70)
    meta = bench.load_metadata()
    for entry in meta.get("samples", []):
        tags_str = ", ".join(entry.get("tags", []))
        cwes_str = ", ".join(entry.get("cwe_ids", [])) if entry.get("cwe_ids") else "none"
        solid_str = ", ".join(entry.get("solid_violations", [])) if entry.get("solid_violations") else "none"
        _safe_print(
            f"  [{entry['category']:>19}] {entry['filename']:<28} "
            f"CWE: {cwes_str:<16} SOLID: {solid_str:<10} "
            f"complexity: {entry['expected_complexity']}"
        )

    _safe_print("\n" + "=" * 70)
    _safe_print("  APCRE-Bench Phase 18 complete.")
    _safe_print("=" * 70)
