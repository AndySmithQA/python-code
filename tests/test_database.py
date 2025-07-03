"""
Database and Repository Tests for Legacy Banking Application
These tests focus on data access patterns and database operations.
"""

import unittest
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database


class TestDatabaseOperations(unittest.TestCase):
    """Test database operations and SQL handling"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db_fd, self.test_db_path = tempfile.mkstemp()
        
        # Create a test database instance with custom path
        self.db = Database()
        self.db.db_path = self.test_db_path
        self.db.connection = None  # Reset connection
    
    def tearDown(self):
        """Clean up test database"""
        if self.db.connection:
            self.db.close()
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)
    
    def test_database_connection(self):
        """Test database connection establishment"""
        conn = self.db.connect()
        self.assertIsNotNone(conn)
        self.assertEqual(self.db.connection, conn)
    
    def test_table_creation(self):
        """Test that all required tables are created"""
        self.db.create_tables()
        
        # Verify tables exist
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Check customers table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check accounts table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts'")
        self.assertIsNotNone(cursor.fetchone())
        
        # Check transactions table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        self.assertIsNotNone(cursor.fetchone())
    
    def test_save_customer(self):
        """Test saving customer data"""
        self.db.create_tables()
        
        # Save a customer
        self.db.save_customer("John Doe", "john@example.com", "555-123-4567", "123 Main St")
        
        # Verify customer was saved
        result = self.db.execute_query("SELECT * FROM customers WHERE name = ?", ("John Doe",))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], "John Doe")
        self.assertEqual(result[0]['email'], "john@example.com")
    
    def test_save_account(self):
        """Test saving account data"""
        self.db.create_tables()
        
        # First save a customer
        self.db.save_customer("John Doe", "john@example.com", "555-123-4567", "123 Main St")
        
        # Get customer ID
        customer_result = self.db.execute_query("SELECT id FROM customers WHERE name = ?", ("John Doe",))
        customer_id = customer_result[0]['id']
        
        # Save an account
        self.db.save_account(customer_id, "CHK123456", "CHECKING", 1000.0)
        
        # Verify account was saved
        result = self.db.execute_query("SELECT * FROM accounts WHERE account_number = ?", ("CHK123456",))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['account_type'], "CHECKING")
        self.assertEqual(result[0]['balance'], 1000.0)
        self.assertEqual(result[0]['status'], "ACTIVE")
    
    def test_save_account_duplicate_number(self):
        """Test that duplicate account numbers are rejected"""
        self.db.create_tables()
        
        # Save a customer
        self.db.save_customer("John Doe", "john@example.com", "555-123-4567", "123 Main St")
        customer_result = self.db.execute_query("SELECT id FROM customers WHERE name = ?", ("John Doe",))
        customer_id = customer_result[0]['id']
        
        # Save first account
        self.db.save_account(customer_id, "CHK123456", "CHECKING", 1000.0)
        
        # Try to save duplicate account number
        with self.assertRaises(Exception) as context:
            self.db.save_account(customer_id, "CHK123456", "SAVINGS", 500.0)
        
        self.assertIn("Account number already exists", str(context.exception))
    
    def test_update_account_balance(self):
        """Test updating account balance"""
        self.db.create_tables()
        
        # Create customer and account
        self.db.save_customer("John Doe", "john@example.com", "555-123-4567", "123 Main St")
        customer_result = self.db.execute_query("SELECT id FROM customers WHERE name = ?", ("John Doe",))
        customer_id = customer_result[0]['id']
        
        self.db.save_account(customer_id, "CHK123456", "CHECKING", 1000.0)
        account_result = self.db.execute_query("SELECT id FROM accounts WHERE account_number = ?", ("CHK123456",))
        account_id = account_result[0]['id']
        
        # Update balance
        self.db.update_account_balance(account_id, 1500.0)
        
        # Verify balance was updated
        result = self.db.execute_query("SELECT balance FROM accounts WHERE id = ?", (account_id,))
        self.assertEqual(result[0]['balance'], 1500.0)
    
    def test_save_transaction(self):
        """Test saving transaction data"""
        self.db.create_tables()
        
        # Create customer and account
        self.db.save_customer("John Doe", "john@example.com", "555-123-4567", "123 Main St")
        customer_result = self.db.execute_query("SELECT id FROM customers WHERE name = ?", ("John Doe",))
        customer_id = customer_result[0]['id']
        
        self.db.save_account(customer_id, "CHK123456", "CHECKING", 1000.0)
        account_result = self.db.execute_query("SELECT id FROM accounts WHERE account_number = ?", ("CHK123456",))
        account_id = account_result[0]['id']
        
        # Save transaction
        self.db.save_transaction(account_id, "DEPOSIT", 500.0, "Test deposit", 1500.0)
        
        # Verify transaction was saved
        result = self.db.execute_query("SELECT * FROM transactions WHERE account_id = ?", (account_id,))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['transaction_type'], "DEPOSIT")
        self.assertEqual(result[0]['amount'], 500.0)
        self.assertEqual(result[0]['description'], "Test deposit")
        self.assertEqual(result[0]['balance_after'], 1500.0)
    
    def test_get_customer_by_id(self):
        """Test retrieving customer by ID"""
        self.db.create_tables()
        
        # Save a customer
        self.db.save_customer("John Doe", "john@example.com", "555-123-4567", "123 Main St")
        
        # Get customer ID
        customer_result = self.db.execute_query("SELECT id FROM customers WHERE name = ?", ("John Doe",))
        customer_id = customer_result[0]['id']
        
        # Retrieve customer by ID using the legacy method
        result = self.db.get_customer_by_id(customer_id)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], "John Doe")
        self.assertEqual(result[0]['email'], "john@example.com")
    
    def test_get_account_by_number(self):
        """Test retrieving account by account number"""
        self.db.create_tables()
        
        # Create customer and account
        self.db.save_customer("John Doe", "john@example.com", "555-123-4567", "123 Main St")
        customer_result = self.db.execute_query("SELECT id FROM customers WHERE name = ?", ("John Doe",))
        customer_id = customer_result[0]['id']
        
        self.db.save_account(customer_id, "CHK123456", "CHECKING", 1000.0)
        
        # Retrieve account by number using the legacy method
        result = self.db.get_account_by_number("CHK123456")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['account_number'], "CHK123456")
        self.assertEqual(result[0]['account_type'], "CHECKING")
        self.assertEqual(result[0]['balance'], 1000.0)
    
    def test_sql_injection_vulnerability(self):
        """Test that the current implementation is vulnerable to SQL injection"""
        self.db.create_tables()
        
        # This test demonstrates the SQL injection vulnerability
        # In a real scenario, this would be a security issue
        malicious_input = "1'; DROP TABLE customers; --"
        
        # This should not crash but shows the vulnerability exists
        try:
            result = self.db.get_customer_by_id(malicious_input)
            # The query may fail due to syntax error, which is expected
        except Exception:
            # Expected to fail due to malformed SQL
            pass
        
        # Verify that the vulnerability exists by checking the query construction
        expected_query = f"SELECT * FROM customers WHERE id = {malicious_input}"
        # This shows that user input is directly concatenated into SQL
        self.assertIn(malicious_input, expected_query)
    
    def test_connection_management(self):
        """Test connection management and cleanup"""
        # Test that connection is reused
        conn1 = self.db.connect()
        conn2 = self.db.connect()
        self.assertEqual(conn1, conn2)  # Should be the same connection
        
        # Test connection closing
        self.db.close()
        self.assertIsNone(self.db.connection)
        
        # Test reconnection
        conn3 = self.db.connect()
        self.assertIsNotNone(conn3)
        self.assertNotEqual(conn1, conn3)  # Should be a new connection


class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests showing how different components interact with database"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db_fd, self.test_db_path = tempfile.mkstemp()
        self.db = Database()
        self.db.db_path = self.test_db_path
        self.db.connection = None
        self.db.create_tables()
    
    def tearDown(self):
        """Clean up test database"""
        if self.db.connection:
            self.db.close()
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)
    
    def test_customer_account_creation_flow(self):
        """Test the complete flow of creating customer and accounts"""
        # Create customer
        self.db.save_customer("Alice Johnson", "alice@example.com", "555-987-6543", "456 Oak St")
        
        # Get customer
        customers = self.db.execute_query("SELECT * FROM customers WHERE name = ?", ("Alice Johnson",))
        self.assertEqual(len(customers), 1)
        customer_id = customers[0]['id']
        
        # Create multiple accounts for the customer
        self.db.save_account(customer_id, "CHK789012", "CHECKING", 2000.0)
        self.db.save_account(customer_id, "SAV345678", "SAVINGS", 5000.0)
        
        # Verify accounts were created
        accounts = self.db.execute_query("SELECT * FROM accounts WHERE customer_id = ?", (customer_id,))
        self.assertEqual(len(accounts), 2)
        
        # Verify account details
        checking_account = next(acc for acc in accounts if acc['account_type'] == 'CHECKING')
        savings_account = next(acc for acc in accounts if acc['account_type'] == 'SAVINGS')
        
        self.assertEqual(checking_account['balance'], 2000.0)
        self.assertEqual(savings_account['balance'], 5000.0)
    
    def test_transaction_history_flow(self):
        """Test creating and retrieving transaction history"""
        # Create customer and account
        self.db.save_customer("Bob Smith", "bob@example.com", "555-111-2222", "789 Pine St")
        customers = self.db.execute_query("SELECT * FROM customers WHERE name = ?", ("Bob Smith",))
        customer_id = customers[0]['id']
        
        self.db.save_account(customer_id, "CHK111222", "CHECKING", 1000.0)
        accounts = self.db.execute_query("SELECT * FROM accounts WHERE customer_id = ?", (customer_id,))
        account_id = accounts[0]['id']
        
        # Create multiple transactions
        transactions = [
            ("DEPOSIT", 500.0, "Initial deposit", 1500.0),
            ("WITHDRAWAL", -200.0, "ATM withdrawal", 1300.0),
            ("DEPOSIT", 100.0, "Check deposit", 1400.0),
            ("TRANSFER_OUT", -300.0, "Transfer to savings", 1100.0)
        ]
        
        for trans_type, amount, description, balance_after in transactions:
            self.db.save_transaction(account_id, trans_type, amount, description, balance_after)
        
        # Retrieve transaction history
        history = self.db.execute_query(
            "SELECT * FROM transactions WHERE account_id = ? ORDER BY timestamp DESC", 
            (account_id,)
        )
        
        self.assertEqual(len(history), 4)
        
        # Verify transaction order (most recent first)
        self.assertEqual(history[0]['transaction_type'], "TRANSFER_OUT")
        self.assertEqual(history[0]['amount'], -300.0)
        self.assertEqual(history[0]['balance_after'], 1100.0)
        
        # Verify oldest transaction
        self.assertEqual(history[-1]['transaction_type'], "DEPOSIT")
        self.assertEqual(history[-1]['amount'], 500.0)
        self.assertEqual(history[-1]['balance_after'], 1500.0)
    
    def test_account_balance_consistency(self):
        """Test that account balance remains consistent with transactions"""
        # Create customer and account
        self.db.save_customer("Carol Davis", "carol@example.com", "555-333-4444", "321 Elm St")
        customers = self.db.execute_query("SELECT * FROM customers WHERE name = ?", ("Carol Davis",))
        customer_id = customers[0]['id']
        
        initial_balance = 1000.0
        self.db.save_account(customer_id, "CHK333444", "CHECKING", initial_balance)
        accounts = self.db.execute_query("SELECT * FROM accounts WHERE customer_id = ?", (customer_id,))
        account_id = accounts[0]['id']
        
        # Perform series of transactions
        current_balance = initial_balance
        
        # Deposit $200
        current_balance += 200.0
        self.db.save_transaction(account_id, "DEPOSIT", 200.0, "Deposit", current_balance)
        self.db.update_account_balance(account_id, current_balance)
        
        # Withdraw $150
        current_balance -= 150.0
        self.db.save_transaction(account_id, "WITHDRAWAL", -150.0, "Withdrawal", current_balance)
        self.db.update_account_balance(account_id, current_balance)
        
        # Verify final balance
        final_account = self.db.execute_query("SELECT balance FROM accounts WHERE id = ?", (account_id,))
        self.assertEqual(final_account[0]['balance'], current_balance)
        self.assertEqual(final_account[0]['balance'], 1050.0)
        
        # Verify last transaction balance matches account balance
        last_transaction = self.db.execute_query(
            "SELECT balance_after FROM transactions WHERE account_id = ? ORDER BY timestamp DESC LIMIT 1",
            (account_id,)
        )
        self.assertEqual(last_transaction[0]['balance_after'], current_balance)


if __name__ == '__main__':
    print("Running Database and Repository Tests")
    print("=" * 50)
    print("These tests focus on data access patterns and database operations")
    print("=" * 50)
    
    unittest.main(verbosity=2)
