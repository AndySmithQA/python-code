"""
Basic Test Suite for Legacy Banking Application
This represents the minimal testing typically found in legacy systems.

As part of TDD refactoring, you should:
1. Add comprehensive tests for existing functionality
2. Write tests before refactoring
3. Ensure all tests pass after refactoring
4. Add new tests for new functionality
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from customer import Customer
from account import Account
from legacy_utils import LegacyUtils, ValidationUtils
from database import Database


class TestLegacyUtils(unittest.TestCase):
    """Basic tests for utility functions"""
    
    def test_validate_email_valid(self):
        """Test email validation with valid email"""
        self.assertTrue(LegacyUtils.validate_email("test@example.com"))
        self.assertTrue(LegacyUtils.validate_email("user.name@domain.org"))
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid email"""
        self.assertFalse(LegacyUtils.validate_email("invalid-email"))
        self.assertFalse(LegacyUtils.validate_email("@domain.com"))
        self.assertFalse(LegacyUtils.validate_email("user@"))
        self.assertFalse(LegacyUtils.validate_email(""))
        self.assertFalse(LegacyUtils.validate_email(None))
    
    def test_validate_phone_valid(self):
        """Test phone validation with valid numbers"""
        self.assertTrue(LegacyUtils.validate_phone("1234567890"))
        self.assertTrue(LegacyUtils.validate_phone("11234567890"))
        self.assertTrue(LegacyUtils.validate_phone("(123) 456-7890"))
    
    def test_validate_phone_invalid(self):
        """Test phone validation with invalid numbers"""
        self.assertFalse(LegacyUtils.validate_phone("123"))
        self.assertFalse(LegacyUtils.validate_phone(""))
        self.assertFalse(LegacyUtils.validate_phone(None))
    
    def test_format_currency(self):
        """Test currency formatting"""
        self.assertEqual(LegacyUtils.format_currency(1234.56), "$1,234.56")
        self.assertEqual(LegacyUtils.format_currency(0), "$0.00")
        self.assertEqual(LegacyUtils.format_currency(None), "$0.00")
    
    def test_generate_account_number(self):
        """Test account number generation"""
        checking_num = LegacyUtils.generate_account_number("CHECKING")
        self.assertTrue(checking_num.startswith("CHK"))
        self.assertEqual(len(checking_num), 10)
        
        savings_num = LegacyUtils.generate_account_number("SAVINGS")
        self.assertTrue(savings_num.startswith("SAV"))
    
    def test_validate_password(self):
        """Test password validation"""
        valid, msg = LegacyUtils.validate_password("Password123")
        self.assertTrue(valid)
        
        invalid, msg = LegacyUtils.validate_password("weak")
        self.assertFalse(invalid)
        self.assertIn("short", msg)


class TestValidationUtils(unittest.TestCase):
    """Tests for validation utilities"""
    
    def test_validate_amount_valid(self):
        """Test amount validation with valid amounts"""
        valid, msg = ValidationUtils.validate_amount(100.50)
        self.assertTrue(valid)
        
        valid, msg = ValidationUtils.validate_amount(0)
        self.assertTrue(valid)
    
    def test_validate_amount_invalid(self):
        """Test amount validation with invalid amounts"""
        valid, msg = ValidationUtils.validate_amount(-10)
        self.assertFalse(valid)
        
        valid, msg = ValidationUtils.validate_amount("invalid")
        self.assertFalse(valid)
        
        valid, msg = ValidationUtils.validate_amount(2000000)  # Exceeds limit
        self.assertFalse(valid)
    
    def test_validate_account_type(self):
        """Test account type validation"""
        self.assertTrue(ValidationUtils.validate_account_type("CHECKING"))
        self.assertTrue(ValidationUtils.validate_account_type("SAVINGS"))
        self.assertFalse(ValidationUtils.validate_account_type("INVALID"))


class TestCustomerBasic(unittest.TestCase):
    """Basic tests for Customer class - these tests show the challenges of testing legacy code"""
    
    @patch('customer.Database')
    def test_customer_creation(self, mock_db):
        """Test customer creation with mocked database"""
        # Mock database behavior
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        customer = Customer(name="John Doe", email="john@example.com", phone="1234567890")
        
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.email, "john@example.com")
        self.assertEqual(customer.phone, "1234567890")
    
    def test_customer_email_validation(self):
        """Test customer email validation"""
        # This test shows how hard it is to test legacy code due to tight coupling
        with self.assertRaises(ValueError):
            customer = Customer(name="John Doe", email="invalid-email")
            customer.save()  # This will fail due to database dependency


class TestAccountBasic(unittest.TestCase):
    """Basic tests for Account class - demonstrates testing challenges"""
    
    @patch('account.Database')
    def test_account_creation(self, mock_db):
        """Test account creation with mocked database"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        account = Account(
            account_number="CHK1234567",
            account_type="CHECKING",
            balance=1000.0,
            customer_id=1
        )
        
        self.assertEqual(account.account_number, "CHK1234567")
        self.assertEqual(account.account_type, "CHECKING")
        self.assertEqual(account.balance, 1000.0)
    
    @patch('account.Database')
    def test_deposit_validation(self, mock_db):
        """Test deposit amount validation"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        account = Account(
            account_number="CHK1234567",
            account_type="CHECKING",
            balance=1000.0,
            customer_id=1,
            status='ACTIVE'
        )
        
        # Test negative deposit
        with self.assertRaises(ValueError):
            account.deposit(-100)
    
    @patch('account.Database')
    def test_withdrawal_validation(self, mock_db):
        """Test withdrawal validation"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        account = Account(
            account_number="CHK1234567",
            account_type="CHECKING",
            balance=1000.0,
            customer_id=1,
            status='ACTIVE'
        )
        
        # Test negative withdrawal
        with self.assertRaises(ValueError):
            account.withdraw(-100)
        
        # Test insufficient funds
        with self.assertRaises(ValueError):
            account.withdraw(2000)  # More than balance + overdraft


class TestDatabaseBasic(unittest.TestCase):
    """Basic database tests - shows need for better testing strategy"""
    
    def setUp(self):
        """Set up test database"""
        # In a real legacy system, this might use the actual database
        # which makes tests slow and unreliable
        self.db = Database()
    
    def test_database_connection(self):
        """Test database connection"""
        conn = self.db.connect()
        self.assertIsNotNone(conn)
    
    def test_table_creation(self):
        """Test that tables are created"""
        # This test is fragile because it depends on actual database state
        self.db.create_tables()
        
        # In legacy systems, we often can't easily verify table creation
        # without actually querying the database


class TestIntegrationBasic(unittest.TestCase):
    """Basic integration tests showing legacy testing challenges"""
    
    def test_customer_account_creation_flow(self):
        """Test the full flow of creating customer and account"""
        # This test shows how integration tests in legacy systems
        # often have to deal with real database connections
        # and are therefore slow and potentially unreliable
        
        # In a real TDD refactoring exercise, you would:
        # 1. Write more comprehensive tests like this
        # 2. Gradually add mocking and dependency injection
        # 3. Refactor to make code more testable
        pass  # Placeholder - would implement actual integration test


if __name__ == '__main__':
    # Run the tests
    print("Running Legacy Banking Application Tests")
    print("=" * 50)
    print("NOTE: These tests demonstrate typical legacy testing challenges:")
    print("- Tight coupling makes mocking difficult")
    print("- Database dependencies make tests slow")
    print("- Mixed concerns make isolated testing hard")
    print("- Limited test coverage due to testing difficulties")
    print("=" * 50)
    
    unittest.main(verbosity=2)
