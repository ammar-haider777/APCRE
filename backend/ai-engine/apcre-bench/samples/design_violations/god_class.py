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
        report = f"Report: {title}\nUsers: {len(self.users)}\nLogs: {len(self.logs)}"
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
