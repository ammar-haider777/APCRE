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
