"""
Comprehensive Test Suite for Legacy Banking Application - Phase 1
This test suite establishes baseline test coverage for existing functionality
before beginning TDD refactoring.

These tests capture the current behavior of the legacy system, including
its flaws and anti-patterns, so we can safely refactor while maintaining
functionality.
"""

import unittest
import sys
import os
import tempfile
import sqlite3
from unittest.mock import patch, MagicMock, call
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from customer import Customer
from account import Account
from transaction import TransactionProcessor
from database import Database
from notification import NotificationService
from reporting import ReportGenerator
from legacy_utils import LegacyUtils, ValidationUtils, DateUtils, StringUtils, ConfigUtils


class TestCustomerFunctionality(unittest.TestCase):
    """Comprehensive tests for Customer class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary database for testing
        self.test_db_fd, self.test_db_path = tempfile.mkstemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)
    
    @patch('customer.Database')
    def test_customer_creation_with_valid_data(self, mock_db):
        """Test creating a customer with valid data"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Act
        customer = Customer(
            name="John Doe",
            email="john@example.com",
            phone="555-123-4567",
            address="123 Main St"
        )
        
        # Assert
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.email, "john@example.com")
        self.assertEqual(customer.phone, "555-123-4567")
        self.assertEqual(customer.address, "123 Main St")
        self.assertIsNone(customer.id)
        self.assertEqual(customer.accounts, [])
    
    @patch('customer.Database')
    def test_customer_save_valid_data(self, mock_db):
        """Test saving a customer with valid data"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.save_customer.return_value = None
        
        customer = Customer(
            name="Jane Smith",
            email="jane@example.com",
            phone="555-987-6543",
            address="456 Oak Ave"
        )
        
        # Act & Assert - should not raise exception
        customer.save()
        mock_db_instance.save_customer.assert_called_once_with(
            "Jane Smith", "jane@example.com", "555-987-6543", "456 Oak Ave"
        )
    
    @patch('customer.Database')
    def test_customer_save_invalid_email(self, mock_db):
        """Test saving customer with invalid email raises ValueError"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        customer = Customer(
            name="John Doe",
            email="invalid-email",
            phone="555-123-4567",
            address="123 Main St"
        )
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            customer.save()
        
        self.assertIn("Invalid email format", str(context.exception))
    
    @patch('customer.Database')
    def test_customer_save_invalid_phone(self, mock_db):
        """Test saving customer with invalid phone raises ValueError"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        customer = Customer(
            name="John Doe",
            email="john@example.com",
            phone="123",  # Invalid phone
            address="123 Main St"
        )
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            customer.save()
        
        self.assertIn("Invalid phone format", str(context.exception))
    
    @patch('customer.Database')
    def test_customer_save_empty_name(self, mock_db):
        """Test saving customer with empty name raises ValueError"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        customer = Customer(
            name="",  # Empty name
            email="john@example.com",
            phone="555-123-4567",
            address="123 Main St"
        )
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            customer.save()
        
        self.assertIn("Customer name is required", str(context.exception))
    
    @patch('customer.Database')
    @patch('notification.NotificationService')
    @patch('account.Account')
    def test_customer_create_checking_account(self, mock_account, mock_notification, mock_db):
        """Test creating a checking account for customer"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.save_account.return_value = None
        
        mock_account_instance = MagicMock()
        mock_account_instance.account_number = "CHK123456"
        mock_account_instance.account_type = "CHECKING"
        mock_account_instance.balance = 100.0
        mock_account.return_value = mock_account_instance
        
        customer = Customer(name="John Doe", customer_id=1)
        customer.id = 1
        
        # Act
        account = customer.create_account("CHECKING", 100.0)
        
        # Assert
        self.assertEqual(account.account_type, "CHECKING")
        self.assertEqual(account.balance, 100.0)
        self.assertIn(account, customer.accounts)
    
    @patch('customer.Database')
    def test_customer_create_account_insufficient_deposit(self, mock_db):
        """Test creating account with insufficient initial deposit"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        customer = Customer(name="John Doe", customer_id=1)
        customer.id = 1
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            customer.create_account("SAVINGS", 50.0)  # Below minimum $100
        
        self.assertIn("Minimum deposit for SAVINGS is $100", str(context.exception))
    
    @patch('customer.Database')
    def test_customer_create_account_invalid_type(self, mock_db):
        """Test creating account with invalid account type"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        customer = Customer(name="John Doe", customer_id=1)
        customer.id = 1
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            customer.create_account("INVALID", 100.0)
        
        self.assertIn("Invalid account type", str(context.exception))
    
    @patch('customer.Database')
    def test_customer_get_total_balance(self, mock_db):
        """Test calculating total customer balance"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        customer = Customer(name="John Doe", customer_id=1)
        
        # Mock accounts
        account1 = MagicMock()
        account1.status = 'ACTIVE'
        account1.balance = 1500.0
        
        account2 = MagicMock()
        account2.status = 'ACTIVE'
        account2.balance = 2500.0
        
        account3 = MagicMock()
        account3.status = 'CLOSED'
        account3.balance = 1000.0
        
        customer.accounts = [account1, account2, account3]
        
        # Act
        total_balance = customer.get_total_balance()
        
        # Assert
        self.assertEqual(total_balance, 4000.0)  # Only active accounts


class TestAccountFunctionality(unittest.TestCase):
    """Comprehensive tests for Account class functionality"""
    
    @patch('account.Database')
    def test_account_creation(self, mock_db):
        """Test account creation with valid data"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Act
        account = Account(
            account_number="CHK123456",
            account_type="CHECKING",
            balance=1000.0,
            customer_id=1,
            status="ACTIVE"
        )
        
        # Assert
        self.assertEqual(account.account_number, "CHK123456")
        self.assertEqual(account.account_type, "CHECKING")
        self.assertEqual(account.balance, 1000.0)
        self.assertEqual(account.customer_id, 1)
        self.assertEqual(account.status, "ACTIVE")
    
    @patch('account.Database')
    @patch('notification.NotificationService')
    def test_account_deposit_valid_amount(self, mock_notification, mock_db):
        """Test depositing valid amount to account"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.update_account_balance.return_value = None
        mock_db_instance.save_transaction.return_value = None
        mock_db_instance.execute_query.return_value = [{'email': 'test@example.com'}]
        
        account = Account(
            account_id=1,
            account_number="CHK123456",
            account_type="CHECKING",
            balance=1000.0,
            customer_id=1,
            status="ACTIVE"
        )
        
        # Act
        result = account.deposit(500.0, "Test deposit")
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(account.balance, 1500.0)
        mock_db_instance.update_account_balance.assert_called_once_with(1, 1500.0)
        mock_db_instance.save_transaction.assert_called_once()
    
    @patch('account.Database')
    def test_account_deposit_negative_amount(self, mock_db):
        """Test depositing negative amount raises ValueError"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        account = Account(
            account_number="CHK123456",
            account_type="CHECKING",
            balance=1000.0,
            customer_id=1,
            status="ACTIVE"
        )
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            account.deposit(-100.0)
        
        self.assertIn("Deposit amount must be positive", str(context.exception))
    
    @patch('account.Database')
    def test_account_deposit_inactive_account(self, mock_db):
        """Test depositing to inactive account raises ValueError"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        account = Account(
            account_number="CHK123456",
            account_type="CHECKING",
            balance=1000.0,
            customer_id=1,
            status="CLOSED"
        )
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            account.deposit(100.0)
        
        self.assertIn("Cannot deposit to inactive account", str(context.exception))
    
    @patch('account.Database')
    @patch('notification.NotificationService')
    def test_account_withdraw_valid_amount(self, mock_notification, mock_db):
        """Test withdrawing valid amount from account"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.update_account_balance.return_value = None
        mock_db_instance.save_transaction.return_value = None
        mock_db_instance.execute_query.return_value = [{'email': 'test@example.com'}]
        
        account = Account(
            account_id=1,
            account_number="CHK123456",
            account_type="CHECKING",
            balance=1000.0,
            customer_id=1,
            status="ACTIVE"
        )
        
        # Act
        result = account.withdraw(300.0, "Test withdrawal")
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(account.balance, 700.0)
        mock_db_instance.update_account_balance.assert_called_once_with(1, 700.0)
        mock_db_instance.save_transaction.assert_called_once()
    
    @patch('account.Database')
    def test_account_withdraw_insufficient_funds(self, mock_db):
        """Test withdrawing more than balance raises ValueError"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        account = Account(
            account_number="CHK123456",
            account_type="CHECKING",
            balance=1000.0,
            customer_id=1,
            status="ACTIVE"
        )
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            account.withdraw(2000.0)  # More than balance + overdraft
        
        self.assertIn("Insufficient funds", str(context.exception))
    
    @patch('account.Database')
    def test_account_withdraw_savings_limit(self, mock_db):
        """Test withdrawing above savings account limit"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        account = Account(
            account_number="SAV123456",
            account_type="SAVINGS",
            balance=10000.0,
            customer_id=1,
            status="ACTIVE"
        )
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            account.withdraw(6000.0)  # Above $5000 limit
        
        self.assertIn("Daily withdrawal limit for savings account is $5000", str(context.exception))
    
    def test_account_get_overdraft_limit(self):
        """Test overdraft limit calculation for different account types"""
        # Test checking account
        checking_account = Account(account_type="CHECKING", balance=0)
        self.assertEqual(checking_account.get_overdraft_limit(), 500)
        
        # Test savings account
        savings_account = Account(account_type="SAVINGS", balance=0)
        self.assertEqual(savings_account.get_overdraft_limit(), 0)
        
        # Test credit account
        credit_account = Account(account_type="CREDIT", balance=0)
        self.assertEqual(credit_account.get_overdraft_limit(), 1000)
    
    @patch('account.Database')
    @patch('notification.NotificationService')
    def test_account_calculate_interest_savings(self, mock_notification, mock_db):
        """Test interest calculation for savings account"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.update_account_balance.return_value = None
        mock_db_instance.save_transaction.return_value = None
        mock_db_instance.execute_query.return_value = [{'email': 'test@example.com'}]
        
        account = Account(
            account_id=1,
            account_number="SAV123456",
            account_type="SAVINGS",
            balance=12000.0,  # $12,000 balance
            customer_id=1,
            status="ACTIVE"
        )
        
        # Act
        interest = account.calculate_interest()
        
        # Assert
        expected_interest = 12000.0 * (0.02 / 12)  # 2% annual / 12 months
        self.assertEqual(interest, expected_interest)
        self.assertEqual(account.balance, 12000.0 + expected_interest)
    
    def test_account_calculate_interest_checking(self):
        """Test interest calculation for checking account (should be 0)"""
        # Arrange
        account = Account(
            account_type="CHECKING",
            balance=1000.0
        )
        
        # Act
        interest = account.calculate_interest()
        
        # Assert
        self.assertEqual(interest, 0)
    
    @patch('account.Database')
    @patch('notification.NotificationService')
    def test_account_apply_monthly_fee_low_balance_checking(self, mock_notification, mock_db):
        """Test monthly fee application for low balance checking account"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.update_account_balance.return_value = None
        mock_db_instance.save_transaction.return_value = None
        mock_db_instance.execute_query.return_value = [{'email': 'test@example.com'}]
        
        account = Account(
            account_id=1,
            account_number="CHK123456",
            account_type="CHECKING",
            balance=500.0,  # Below $1000 threshold
            customer_id=1,
            status="ACTIVE"
        )
        
        # Act
        fee = account.apply_monthly_fee()
        
        # Assert
        self.assertEqual(fee, 10)  # $10 fee
        self.assertEqual(account.balance, 490.0)  # Balance reduced by fee
    
    def test_account_apply_monthly_fee_high_balance(self):
        """Test no monthly fee for high balance account"""
        # Arrange
        account = Account(
            account_type="CHECKING",
            balance=2000.0  # Above $1000 threshold
        )
        
        # Act
        fee = account.apply_monthly_fee()
        
        # Assert
        self.assertEqual(fee, 0)  # No fee
        self.assertEqual(account.balance, 2000.0)  # Balance unchanged


class TestTransactionProcessor(unittest.TestCase):
    """Comprehensive tests for TransactionProcessor functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = TransactionProcessor()
    
    @patch('transaction.Database')
    @patch('transaction.NotificationService')
    def test_process_transfer_valid(self, mock_notification, mock_db):
        """Test processing a valid transfer between accounts"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Mock account data
        from_account = {
            'id': 1, 'balance': 1000.0, 'status': 'ACTIVE', 
            'account_type': 'CHECKING', 'account_number': 'CHK123',
            'customer_id': 1
        }
        to_account = {
            'id': 2, 'balance': 500.0, 'status': 'ACTIVE',
            'account_type': 'SAVINGS', 'account_number': 'SAV456',
            'customer_id': 2
        }
        
        self.processor.get_account_by_id = MagicMock(side_effect=[from_account, to_account])
        self.processor.check_daily_limits = MagicMock(return_value=True)
        self.processor.save_transfer_transactions = MagicMock()
        self.processor.send_transfer_notifications = MagicMock()
        
        mock_db_instance.update_account_balance.return_value = None
        
        # Act
        result = self.processor.process_transfer(1, 2, 300.0, "Test transfer")
        
        # Assert
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['from_balance'], 700.0)
        self.assertEqual(result['to_balance'], 800.0)
        self.assertIsNotNone(result['transaction_id'])
    
    @patch('transaction.Database')
    def test_process_transfer_insufficient_funds(self, mock_db):
        """Test transfer with insufficient funds"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        from_account = {
            'id': 1, 'balance': 100.0, 'status': 'ACTIVE',
            'account_type': 'CHECKING', 'account_number': 'CHK123'
        }
        to_account = {
            'id': 2, 'balance': 500.0, 'status': 'ACTIVE',
            'account_type': 'SAVINGS', 'account_number': 'SAV456'
        }
        
        self.processor.get_account_by_id = MagicMock(side_effect=[from_account, to_account])
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.processor.process_transfer(1, 2, 1000.0, "Test transfer")
        
        self.assertIn("Insufficient funds", str(context.exception))
    
    @patch('transaction.Database')
    def test_process_transfer_invalid_accounts(self, mock_db):
        """Test transfer with invalid account IDs"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        self.processor.get_account_by_id = MagicMock(side_effect=[None, None])
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.processor.process_transfer(999, 888, 100.0, "Test transfer")
        
        self.assertIn("Invalid account(s)", str(context.exception))
    
    @patch('transaction.Database')
    def test_process_transfer_inactive_accounts(self, mock_db):
        """Test transfer with inactive accounts"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        from_account = {
            'id': 1, 'balance': 1000.0, 'status': 'CLOSED',  # Inactive
            'account_type': 'CHECKING', 'account_number': 'CHK123'
        }
        to_account = {
            'id': 2, 'balance': 500.0, 'status': 'ACTIVE',
            'account_type': 'SAVINGS', 'account_number': 'SAV456'
        }
        
        self.processor.get_account_by_id = MagicMock(side_effect=[from_account, to_account])
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.processor.process_transfer(1, 2, 100.0, "Test transfer")
        
        self.assertIn("Source account is not active", str(context.exception))
    
    @patch('transaction.Database')
    def test_process_transfer_amount_too_large(self, mock_db):
        """Test transfer with amount exceeding maximum limit"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        from_account = {
            'id': 1, 'balance': 50000.0, 'status': 'ACTIVE',
            'account_type': 'CHECKING', 'account_number': 'CHK123'
        }
        to_account = {
            'id': 2, 'balance': 500.0, 'status': 'ACTIVE',
            'account_type': 'SAVINGS', 'account_number': 'SAV456'
        }
        
        self.processor.get_account_by_id = MagicMock(side_effect=[from_account, to_account])
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.processor.process_transfer(1, 2, 30000.0, "Large transfer")  # Above $25,000 limit
        
        self.assertIn("Transfer amount exceeds maximum limit", str(context.exception))
    
    @patch('transaction.Database')
    def test_check_daily_limits_within_limit(self, mock_db):
        """Test daily limit checking within allowed limits"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.execute_query.return_value = [{'total_amount': -2000.0, 'transaction_count': 5}]
        
        self.processor.db = mock_db_instance
        
        # Act
        result = self.processor.check_daily_limits(1, 1000.0)  # Total would be 3000, under 10000 limit
        
        # Assert
        self.assertTrue(result)
    
    @patch('transaction.Database')
    def test_check_daily_limits_exceeds_amount_limit(self, mock_db):
        """Test daily limit checking exceeding amount limit"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.execute_query.return_value = [{'total_amount': -9500.0, 'transaction_count': 10}]
        
        self.processor.db = mock_db_instance
        
        # Act
        result = self.processor.check_daily_limits(1, 1000.0)  # Total would be 10500, over 10000 limit
        
        # Assert
        self.assertFalse(result)
    
    @patch('transaction.Database')
    def test_check_daily_limits_exceeds_transaction_count(self, mock_db):
        """Test daily limit checking exceeding transaction count limit"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.execute_query.return_value = [{'total_amount': -1000.0, 'transaction_count': 50}]
        
        self.processor.db = mock_db_instance
        
        # Act
        result = self.processor.check_daily_limits(1, 100.0)  # 50 transactions = limit
        
        # Assert
        self.assertFalse(result)
    
    @patch('transaction.Database')
    @patch('transaction.NotificationService')
    def test_process_bill_payment_valid(self, mock_notification, mock_db):
        """Test processing a valid bill payment"""
        # Arrange
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        account = {
            'id': 1, 'balance': 1000.0, 'customer_id': 1
        }
        customer = {
            'email': 'test@example.com'
        }
        
        self.processor.get_account_by_id = MagicMock(return_value=account)
        self.processor.get_customer_by_id = MagicMock(return_value=customer)
        mock_db_instance.update_account_balance.return_value = None
        mock_db_instance.save_transaction.return_value = None
        
        # Act
        result = self.processor.process_bill_payment(1, "Electric Company", 150.0, "REF123")
        
        # Assert
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['reference'], 'REF123')
        self.assertEqual(result['new_balance'], 850.0)


class TestLegacyUtilsComprehensive(unittest.TestCase):
    """Comprehensive tests for all utility functions"""
    
    def test_generate_account_number_all_types(self):
        """Test account number generation for all account types"""
        # Test known types
        checking = LegacyUtils.generate_account_number("CHECKING")
        self.assertTrue(checking.startswith("CHK"))
        self.assertEqual(len(checking), 10)
        
        savings = LegacyUtils.generate_account_number("SAVINGS")
        self.assertTrue(savings.startswith("SAV"))
        self.assertEqual(len(savings), 10)
        
        credit = LegacyUtils.generate_account_number("CREDIT")
        self.assertTrue(credit.startswith("CRD"))
        self.assertEqual(len(credit), 10)
        
        # Test unknown type
        unknown = LegacyUtils.generate_account_number("UNKNOWN")
        self.assertTrue(unknown.startswith("UNK"))
        self.assertEqual(len(unknown), 10)
    
    def test_validate_email_comprehensive(self):
        """Test email validation with various formats"""
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk",
            "123@domain.com",
            "test@sub.domain.com"
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(LegacyUtils.validate_email(email))
        
        # Invalid emails - some may pass due to legacy validation issues
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "",
            "user space@domain.com"
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                if email is not None:  # Skip None test as it causes issues
                    self.assertFalse(LegacyUtils.validate_email(email))
                    
        # Known legacy validation bug - this should be invalid but passes
        # TODO: Fix during TDD refactoring
        legacy_bug_email = "user@domain..com"
        result = LegacyUtils.validate_email(legacy_bug_email)
        # Documenting current behavior (will be fixed in refactoring)
        self.assertTrue(result)  # Current legacy behavior (incorrect)
    
    def test_validate_phone_comprehensive(self):
        """Test phone validation with various formats"""
        # Valid phones
        valid_phones = [
            "1234567890",
            "11234567890",
            "(123) 456-7890",
            "123-456-7890",
            "123.456.7890",
            "123 456 7890"
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                self.assertTrue(LegacyUtils.validate_phone(phone))
        
        # Invalid phones
        invalid_phones = [
            "123",
            "12345678901234",  # Too long
            "",
            None,
            "abcdefghij",
            "123-45"
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                self.assertFalse(LegacyUtils.validate_phone(phone))
    
    def test_calculate_interest_all_types(self):
        """Test interest calculation for different compounding types"""
        principal = 1000.0
        rate = 0.05  # 5%
        periods = 12
        
        # Monthly compounding
        monthly = LegacyUtils.calculate_interest(principal, rate, periods, 'monthly')
        expected_monthly = principal * (1 + rate/12) ** periods
        self.assertAlmostEqual(monthly, expected_monthly, places=2)
        
        # Daily compounding
        daily = LegacyUtils.calculate_interest(principal, rate, periods, 'daily')
        expected_daily = principal * (1 + rate/365) ** periods
        self.assertAlmostEqual(daily, expected_daily, places=2)
        
        # Simple interest
        simple = LegacyUtils.calculate_interest(principal, rate, periods, 'simple')
        expected_simple = principal * (1 + rate * periods)
        self.assertAlmostEqual(simple, expected_simple, places=2)
    
    def test_validate_password_comprehensive(self):
        """Test password validation with various passwords"""
        # Valid passwords
        valid_passwords = [
            "Password123",
            "MySecure1Pass",
            "Complex9Password",
            "Test1234"
        ]
        
        for password in valid_passwords:
            with self.subTest(password=password):
                valid, msg = LegacyUtils.validate_password(password)
                self.assertTrue(valid)
                self.assertEqual(msg, "Password valid")
        
        # Invalid passwords
        invalid_cases = [
            ("short", "Password too short"),
            ("alllowercase1", "Password must contain uppercase letter"),
            ("ALLUPPERCASE1", "Password must contain lowercase letter"),
            ("NoNumbers", "Password must contain digit")
        ]
        
        for password, expected_msg in invalid_cases:
            with self.subTest(password=password):
                valid, msg = LegacyUtils.validate_password(password)
                self.assertFalse(valid)
                self.assertIn(expected_msg, msg)
    
    def test_is_business_day(self):
        """Test business day checking"""
        # Test weekdays (business days)
        monday = datetime(2023, 7, 3)  # Monday
        tuesday = datetime(2023, 7, 4)  # Tuesday
        friday = datetime(2023, 7, 7)   # Friday
        
        self.assertTrue(LegacyUtils.is_business_day(monday))
        self.assertTrue(LegacyUtils.is_business_day(tuesday))
        self.assertTrue(LegacyUtils.is_business_day(friday))
        
        # Test weekends (not business days)
        saturday = datetime(2023, 7, 8)  # Saturday
        sunday = datetime(2023, 7, 9)    # Sunday
        
        self.assertFalse(LegacyUtils.is_business_day(saturday))
        self.assertFalse(LegacyUtils.is_business_day(sunday))
    
    def test_format_account_number(self):
        """Test account number formatting"""
        # Test long account number
        long_number = "1234567890"
        formatted = LegacyUtils.format_account_number(long_number)
        self.assertEqual(formatted, "123-456-7890")
        
        # Test short account number
        short_number = "12345"
        formatted_short = LegacyUtils.format_account_number(short_number)
        self.assertEqual(formatted_short, "12345")
    
    def test_mask_account_number(self):
        """Test account number masking"""
        # Test long account number
        long_number = "1234567890"
        masked = LegacyUtils.mask_account_number(long_number)
        self.assertEqual(masked, "****-7890")
        
        # Test short account number
        short_number = "123"
        masked_short = LegacyUtils.mask_account_number(short_number)
        self.assertEqual(masked_short, "123")


class TestValidationUtilsComprehensive(unittest.TestCase):
    """Comprehensive tests for ValidationUtils"""
    
    def test_validate_amount_edge_cases(self):
        """Test amount validation with edge cases"""
        # Valid amounts
        valid_amounts = [0, 0.01, 100, 999999.99]
        
        for amount in valid_amounts:
            with self.subTest(amount=amount):
                valid, msg = ValidationUtils.validate_amount(amount)
                self.assertTrue(valid)
                self.assertEqual(msg, "Valid amount")
        
        # Invalid amounts
        invalid_cases = [
            (-1, "Amount cannot be negative"),
            (1000001, "Amount exceeds maximum limit"),
            ("invalid", "Amount must be numeric"),
            (100.123, "Amount cannot have more than 2 decimal places")
        ]
        
        for amount, expected_msg in invalid_cases:
            with self.subTest(amount=amount):
                valid, msg = ValidationUtils.validate_amount(amount)
                self.assertFalse(valid)
                self.assertIn(expected_msg, msg)
    
    def test_validate_account_type_all_types(self):
        """Test account type validation for all valid and invalid types"""
        valid_types = ['CHECKING', 'SAVINGS', 'CREDIT', 'MONEY_MARKET']
        
        for account_type in valid_types:
            with self.subTest(account_type=account_type):
                self.assertTrue(ValidationUtils.validate_account_type(account_type))
        
        invalid_types = ['INVALID', 'checking', 'savings', '', None]
        
        for account_type in invalid_types:
            with self.subTest(account_type=account_type):
                self.assertFalse(ValidationUtils.validate_account_type(account_type))
    
    def test_validate_transaction_type_all_types(self):
        """Test transaction type validation"""
        valid_types = ['DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT', 'BILL_PAYMENT', 'INTEREST']
        
        for transaction_type in valid_types:
            with self.subTest(transaction_type=transaction_type):
                self.assertTrue(ValidationUtils.validate_transaction_type(transaction_type))
        
        invalid_types = ['INVALID', 'deposit', 'withdrawal', '', None]
        
        for transaction_type in invalid_types:
            with self.subTest(transaction_type=transaction_type):
                self.assertFalse(ValidationUtils.validate_transaction_type(transaction_type))


if __name__ == '__main__':
    print("Running Comprehensive Legacy Banking Application Tests - Phase 1")
    print("=" * 70)
    print("These tests establish baseline coverage for existing functionality")
    print("before beginning TDD refactoring.")
    print("=" * 70)
    
    # Run tests with high verbosity
    unittest.main(verbosity=2)
