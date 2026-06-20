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
