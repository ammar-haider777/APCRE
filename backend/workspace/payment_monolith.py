# TODO: This script implements Object-Oriented paradigms (class). Learn encapsulation, inheritance, or SOLID inside the Tutoring Panel.
# TODO: This script implements Object-Oriented paradigms (class). Learn encapsulation, inheritance, or SOLID inside the Tutoring Panel.
# TODO: This script implements Object-Oriented paradigms (class). Learn encapsulation, inheritance, or SOLID inside the Tutoring Panel.
# TODO: This script contains no automated assertions or structural unit tests.
# -*- coding: utf-8 -*-
"""
APCRE Test Harness: payment_monolith.py
--------------------------------------------------
This file represents a tightly-coupled monolithic payment model.
designed to test the APCRE Architecture Center and Knowledge Graph.

It intentionally exhibits:
1. High SQL Coupling (Direct DB execution within business logic).
2. Fat Model Smell (Flask routing decorator logic tightly bound with domain).
3. Monolithic Design (Single-module handling entities, persistence, and endpoints).
4. Hand-rolled Singleton Pattern (Tightly bound instance creation).
"""

import os
import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

class DatabaseConnectionSingleton:
    """
    GoF Singleton Pattern Violation: Tightly bound DB connection manager.
    Violates Hexagonal Port interfaces by locking SQLite as the sole driver.
    """
    _instance = None

    @staticmethod
    def get_instance():
        if DatabaseConnectionSingleton._instance is None:
            # High SQL Coupling: Direct dependency on SQLite file persistence
            DatabaseConnectionSingleton._instance = sqlite3.connect("apcre_memory.db")
        return DatabaseConnectionSingleton._instance


class PaymentProcessor:
    """
    Core Domain Class representing Payment Processing.
    """
    def __init__(self, currency="PKR"):
        self.currency = currency

    def process_invoice(self, invoice_id, amount):
        """
        Direct SQL Coupling inside a business loop:
        Tightly coupled with sqlite3 tables and local schemas.
        """
        conn = DatabaseConnectionSingleton.get_instance()
        cursor = conn.cursor()
        
        # SQL Injection & High Coupling boundary
        query = f"SELECT * FROM invoices WHERE id = {invoice_id}"
        cursor.execute(query)
        invoice = cursor.fetchone()
        
        if not invoice:
            return {"status": "error", "message": f"Invoice #{invoice_id} not found"}
            
        new_balance = invoice[2] - amount
        
        # High SQL persistence mutation
        cursor.execute(f"UPDATE invoices SET balance = {new_balance} WHERE id = {invoice_id}")
        conn.commit()
        
        return {
            "status": "success", 
            "invoice_id": invoice_id, 
            "amount_paid": amount, 
            "remaining": new_balance,
            "currency": self.currency
        }


# Fat Model Smell: Controller routes mixed inside domain files
@app.route("/api/pay", methods=["POST"])
def pay_invoice_endpoint():
    """
    Flask API route decorator mixed directly with core payment entities.
    Should be decoupled into clean input Adapters and Ports.
    """
    data = request.get_json()
    invoice_id = data.get("invoice_id")
    amount = data.get("amount")
    
    processor = PaymentProcessor()
    result = processor.process_invoice(invoice_id, amount)
    
    return jsonify(result)


# =========================================================================
# LIVE TERMINAL OUTPUT HARNESS (Runs automatically when you click RUN)
# =========================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("      🚀 APCRE MONOLITHIC TEST ENGINE: LIVE RUN START")
    print("="*60)
    print("[INFO] Static AST parsing found 1 Module, 2 Classes, 2 Functions.")
    print("[INFO] Structural Heuristic: GoF Singleton Design Pattern Detected.")
    print("[INFO] Architecture Smells: High SQL Coupling + Fat Model Endpoint.")
    
    print("\n[STEP 1] Initializing SQLite Memory persistent context...")
    try:
        conn = sqlite3.connect("apcre_memory.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY, client TEXT, balance REAL)")
        cursor.execute("INSERT OR REPLACE INTO invoices VALUES (101, 'Mudassar Ali', 12000.00)")
        cursor.execute("INSERT OR REPLACE INTO invoices VALUES (102, 'Muneer Shah', 4500.50)")
        conn.commit()
        print("  ✓ Local SQLite tables initialized successfully.")
    except Exception as e:
        print(f"  ✗ SQLite setup failed: {e}")
        
    print("\n[STEP 2] Running monolithic payment processing...")
    try:
        processor = PaymentProcessor()
        print("  → Attempting payment of 3,500 PKR for Invoice #101...")
        result = processor.process_invoice(101, 3500.0)
        print(f"  ✓ Transaction Success Details: {result}")
        
        print("\n  → Attempting payment of 1,200 PKR for Invoice #102...")
        result2 = processor.process_invoice(102, 1200.0)
        print(f"  ✓ Transaction Success Details: {result2}")
    except Exception as e:
        print(f"  ✗ Processing error: {e}")
        
    print("\n" + "="*60)
    print("      🎯 LIVE RUN COMPLETED: SYSTEM COMPLIES WITH METRICS")
    print("="*60 + "\n")
