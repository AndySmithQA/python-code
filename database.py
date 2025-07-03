"""
Legacy Database Module - Demonstrates poor database access patterns
Issues:
- Direct database access without abstraction
- No connection pooling
- SQL injection vulnerabilities
- No transaction management
- Hard-coded connection details
"""

import sqlite3
import os
from datetime import datetime


class Database:
    """Legacy database class with anti-patterns"""
    
    def __init__(self):
        # Hard-coded database path (anti-pattern)
        self.db_path = "banking.db"
        self.connection = None
        self.create_tables()
    
    def connect(self):
        """Direct connection without pooling"""
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def create_tables(self):
        """Create tables with no migration management"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Create customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                created_at TEXT
            )
        """)
        
        # Create accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                account_number TEXT UNIQUE,
                account_type TEXT,
                balance REAL,
                status TEXT,
                created_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        
        # Create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                transaction_type TEXT,
                amount REAL,
                description TEXT,
                timestamp TEXT,
                balance_after REAL,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        
        conn.commit()
    
    def execute_query(self, query, params=None):
        """Vulnerable to SQL injection"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        return cursor.fetchall()
    
    def get_customer_by_id(self, customer_id):
        """Direct SQL in business logic layer"""
        query = f"SELECT * FROM customers WHERE id = {customer_id}"  # SQL injection risk
        return self.execute_query(query)
    
    def save_customer(self, name, email, phone, address):
        """No transaction management"""
        query = """
            INSERT INTO customers (name, email, phone, address, created_at)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (name, email, phone, address, datetime.now().isoformat()))
    
    def save_account(self, customer_id, account_number, account_type, balance):
        """Mixed concerns - business logic in data layer"""
        # Check if account number already exists (business logic in data layer)
        existing = self.execute_query(
            "SELECT * FROM accounts WHERE account_number = ?", 
            (account_number,)
        )
        if existing:
            raise Exception("Account number already exists")
        
        query = """
            INSERT INTO accounts (customer_id, account_number, account_type, balance, status, created_at)
            VALUES (?, ?, ?, ?, 'ACTIVE', ?)
        """
        return self.execute_query(query, (customer_id, account_number, account_type, balance, datetime.now().isoformat()))
    
    def update_account_balance(self, account_id, new_balance):
        """No optimistic locking"""
        query = f"UPDATE accounts SET balance = {new_balance} WHERE id = {account_id}"
        return self.execute_query(query)
    
    def save_transaction(self, account_id, transaction_type, amount, description, balance_after):
        """No validation"""
        query = """
            INSERT INTO transactions (account_id, transaction_type, amount, description, timestamp, balance_after)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (account_id, transaction_type, amount, description, datetime.now().isoformat(), balance_after))
    
    def get_account_by_number(self, account_number):
        """String concatenation vulnerability"""
        query = f"SELECT * FROM accounts WHERE account_number = '{account_number}'"
        return self.execute_query(query)
    
    def close(self):
        """Manual connection management"""
        if self.connection:
            self.connection.close()
            self.connection = None
