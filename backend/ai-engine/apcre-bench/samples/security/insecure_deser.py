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
