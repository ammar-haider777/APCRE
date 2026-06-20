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
