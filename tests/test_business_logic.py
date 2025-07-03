"""
Business Logic Tests for Legacy Banking Application
These tests focus on business rules and domain logic.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from customer import Customer
from account import Account
from transaction import TransactionProcessor


class TestBusinessRules(unittest.TestCase):
    """Test business rules and domain logic"""
    
    @patch('customer.Database')
    def test_customer_validation_rules(self, mock_db):
        """Test customer validation business rules"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Test email validation rule
        customer = Customer(
            name="John Doe",
            email="invalid-email",
            phone="555-123-4567",
            address="123 Main St"
        )
        
        with self.assertRaises(ValueError) as context:
            customer.save()
        
        self.assertIn("Invalid email format", str(context.exception))
        
        # Test phone validation rule
        customer.email = "john@example.com"
        customer.phone = "123"  # Too short
        
        with self.assertRaises(ValueError) as context:
            customer.save()
        
        self.assertIn("Invalid phone format", str(context.exception))
    
    @patch('customer.Database')
    def test_account_creation_business_rules(self, mock_db):
        """Test account creation business rules"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        customer = Customer(name="John Doe", customer_id=1)
        customer.id = 1
        
        # Test minimum deposit rules
        test_cases = [
            ("CHECKING", 24.99, "Minimum deposit for CHECKING is $25"),
            ("SAVINGS", 99.99, "Minimum deposit for SAVINGS is $100"),
        ]
        
        for account_type, deposit, expected_error in test_cases:
            with self.subTest(account_type=account_type, deposit=deposit):
                with self.assertRaises(ValueError) as context:
                    customer.create_account(account_type, deposit)
                
                self.assertIn(expected_error, str(context.exception))
        
        # Test negative deposit
        with self.assertRaises(ValueError) as context:
            customer.create_account("CHECKING", -100.0)
        
        self.assertIn("Initial deposit cannot be negative", str(context.exception))
    
    @patch('account.Database')
    def test_account_transaction_business_rules(self, mock_db):
        """Test account transaction business rules"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Test deposit rules
        account = Account(
            account_number="CHK123456",
            account_type="CHECKING",
            balance=1000.0,
            customer_id=1,
            status="ACTIVE"
        )
        
        # Test negative deposit
        with self.assertRaises(ValueError) as context:
            account.deposit(-100.0)
        
        self.assertIn("Deposit amount must be positive", str(context.exception))
        
        # Test deposit to inactive account
        account.status = "CLOSED"
        with self.assertRaises(ValueError) as context:
            account.deposit(100.0)
        
        self.assertIn("Cannot deposit to inactive account", str(context.exception))
    
    @patch('account.Database')
    def test_withdrawal_business_rules(self, mock_db):
        """Test withdrawal business rules"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Test insufficient funds
        account = Account(
            account_number="CHK123456",
            account_type="CHECKING",
            balance=100.0,
            customer_id=1,
            status="ACTIVE"
        )
        
        with self.assertRaises(ValueError) as context:
            account.withdraw(1000.0)  # More than balance + overdraft
        
        self.assertIn("Insufficient funds", str(context.exception))
        
        # Test savings account withdrawal limit
        savings_account = Account(
            account_number="SAV123456",
            account_type="SAVINGS",
            balance=10000.0,
            customer_id=1,
            status="ACTIVE"
        )
        
        with self.assertRaises(ValueError) as context:
            savings_account.withdraw(6000.0)  # Above $5000 limit
        
        self.assertIn("Daily withdrawal limit for savings account is $5000", str(context.exception))
    
    @patch('transaction.Database')
    def test_transfer_business_rules(self, mock_db):
        """Test transfer business rules"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        processor = TransactionProcessor()
        
        # Test transfer amount limits
        from_account = {
            'id': 1, 'balance': 50000.0, 'status': 'ACTIVE',
            'account_type': 'CHECKING', 'account_number': 'CHK123'
        }
        to_account = {
            'id': 2, 'balance': 1000.0, 'status': 'ACTIVE',
            'account_type': 'SAVINGS', 'account_number': 'SAV456'
        }
        
        processor.get_account_by_id = MagicMock(side_effect=[from_account, to_account])
        
        # Test maximum transfer limit
        with self.assertRaises(ValueError) as context:
            processor.process_transfer(1, 2, 30000.0, "Large transfer")  # Above $25,000 limit
        
        self.assertIn("Transfer amount exceeds maximum limit", str(context.exception))
        
        # Test savings account transfer limit
        from_account['account_type'] = 'SAVINGS'
        processor.get_account_by_id = MagicMock(side_effect=[from_account, to_account])
        
        with self.assertRaises(ValueError) as context:
            processor.process_transfer(1, 2, 6000.0, "Large savings transfer")
        
        self.assertIn("Savings account transfer limit is $5000", str(context.exception))
    
    def test_overdraft_limit_calculation(self):
        """Test overdraft limit calculation rules"""
        # Test checking account overdraft
        checking = Account(account_type="CHECKING", balance=0)
        self.assertEqual(checking.get_overdraft_limit(), 500)
        
        # Test savings account overdraft (none)
        savings = Account(account_type="SAVINGS", balance=0)
        self.assertEqual(savings.get_overdraft_limit(), 0)
        
        # Test credit account overdraft
        credit = Account(account_type="CREDIT", balance=0)
        self.assertEqual(credit.get_overdraft_limit(), 1000)
    
    @patch('account.Database')
    @patch('notification.NotificationService')
    def test_interest_calculation_rules(self, mock_notification, mock_db):
        """Test interest calculation business rules"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.update_account_balance.return_value = None
        mock_db_instance.save_transaction.return_value = None
        mock_db_instance.execute_query.return_value = [{'email': 'test@example.com'}]
        
        # Test savings account interest
        savings = Account(
            account_id=1,
            account_type="SAVINGS",
            balance=12000.0,
            customer_id=1,
            status="ACTIVE"
        )
        
        interest = savings.calculate_interest()
        expected_interest = 12000.0 * (0.02 / 12)  # 2% annual / 12 months
        self.assertEqual(interest, expected_interest)
        
        # Test checking account (no interest)
        checking = Account(account_type="CHECKING", balance=5000.0)
        interest = checking.calculate_interest()
        self.assertEqual(interest, 0)
    
    @patch('account.Database')
    @patch('notification.NotificationService')
    def test_monthly_fee_rules(self, mock_notification, mock_db):
        """Test monthly fee business rules"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.update_account_balance.return_value = None
        mock_db_instance.save_transaction.return_value = None
        mock_db_instance.execute_query.return_value = [{'email': 'test@example.com'}]
        
        # Test checking account low balance fee
        checking_low = Account(
            account_id=1,
            account_type="CHECKING",
            balance=500.0,  # Below $1000 threshold
            customer_id=1,
            status="ACTIVE"
        )
        
        fee = checking_low.apply_monthly_fee()
        self.assertEqual(fee, 10)  # $10 fee
        
        # Test checking account high balance (no fee)
        checking_high = Account(
            account_type="CHECKING",
            balance=2000.0  # Above $1000 threshold
        )
        
        fee = checking_high.apply_monthly_fee()
        self.assertEqual(fee, 0)  # No fee
        
        # Test savings account low balance fee
        savings_low = Account(
            account_id=1,
            account_type="SAVINGS",
            balance=300.0,  # Below $500 threshold
            customer_id=1,
            status="ACTIVE"
        )
        
        fee = savings_low.apply_monthly_fee()
        self.assertEqual(fee, 5)  # $5 fee


class TestComplexBusinessScenarios(unittest.TestCase):
    """Test complex business scenarios and edge cases"""
    
    @patch('customer.Database')
    @patch('notification.NotificationService')
    @patch('account.Account')
    def test_customer_multiple_account_creation(self, mock_account, mock_notification, mock_db):
        """Test creating multiple accounts for same customer"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.save_account.return_value = None
        
        customer = Customer(name="John Doe", customer_id=1)
        customer.id = 1
        
        # Setup mock account instances
        mock_account_instance = MagicMock()
        mock_account_instance.account_number = "CHK123456"
        mock_account_instance.account_type = "CHECKING"
        mock_account_instance.balance = 1000.0
        mock_account.return_value = mock_account_instance
        
        # Create first account
        account1 = customer.create_account("CHECKING", 1000.0)
        self.assertEqual(len(customer.accounts), 1)
        
        # Create second account
        mock_account_instance2 = MagicMock()
        mock_account_instance2.account_number = "SAV789012"
        mock_account_instance2.account_type = "SAVINGS"
        mock_account_instance2.balance = 5000.0
        mock_account.return_value = mock_account_instance2
        
        account2 = customer.create_account("SAVINGS", 5000.0)
        self.assertEqual(len(customer.accounts), 2)
    
    @patch('customer.Database')
    def test_customer_transfer_between_own_accounts(self, mock_db):
        """Test transferring money between customer's own accounts"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        customer = Customer(name="John Doe", customer_id=1)
        
        # Mock accounts
        checking_account = MagicMock()
        checking_account.account_number = "CHK123456"
        checking_account.balance = 2000.0
        checking_account.withdraw = MagicMock()
        
        savings_account = MagicMock()
        savings_account.account_number = "SAV789012"
        savings_account.balance = 1000.0
        savings_account.deposit = MagicMock()
        
        customer.accounts = [checking_account, savings_account]
        
        # Perform transfer
        customer.transfer_between_accounts("CHK123456", "SAV789012", 500.0)
        
        # Verify transfer methods were called
        checking_account.withdraw.assert_called_once_with(500.0, "Transfer to SAV789012")
        savings_account.deposit.assert_called_once_with(500.0, "Transfer from CHK123456")
    
    @patch('customer.Database')
    def test_customer_transfer_insufficient_funds(self, mock_db):
        """Test transfer with insufficient funds"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        customer = Customer(name="John Doe", customer_id=1)
        
        # Mock accounts
        checking_account = MagicMock()
        checking_account.account_number = "CHK123456"
        checking_account.balance = 100.0  # Low balance
        
        savings_account = MagicMock()
        savings_account.account_number = "SAV789012"
        savings_account.balance = 1000.0
        
        customer.accounts = [checking_account, savings_account]
        
        # Test insufficient funds
        with self.assertRaises(ValueError) as context:
            customer.transfer_between_accounts("CHK123456", "SAV789012", 500.0)
        
        self.assertIn("Insufficient funds", str(context.exception))
    
    @patch('customer.Database')
    def test_customer_transfer_account_not_found(self, mock_db):
        """Test transfer with non-existent account"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        customer = Customer(name="John Doe", customer_id=1)
        
        # Mock one account
        checking_account = MagicMock()
        checking_account.account_number = "CHK123456"
        checking_account.balance = 2000.0
        
        customer.accounts = [checking_account]
        
        # Test transfer to non-existent account
        with self.assertRaises(ValueError) as context:
            customer.transfer_between_accounts("CHK123456", "NONEXISTENT", 500.0)
        
        self.assertIn("One or both accounts not found", str(context.exception))
    
    @patch('transaction.Database')
    def test_daily_transaction_limits(self, mock_db):
        """Test daily transaction limits business rule"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        processor = TransactionProcessor()
        processor.db = mock_db_instance
        
        # Test within daily limit
        mock_db_instance.execute_query.return_value = [{'total_amount': -5000.0, 'transaction_count': 10}]
        
        result = processor.check_daily_limits(1, 1000.0)  # Total would be 6000, under 10000 limit
        self.assertTrue(result)
        
        # Test exceeding daily amount limit
        mock_db_instance.execute_query.return_value = [{'total_amount': -9500.0, 'transaction_count': 20}]
        
        result = processor.check_daily_limits(1, 1000.0)  # Total would be 10500, over 10000 limit
        self.assertFalse(result)
        
        # Test exceeding daily transaction count limit
        mock_db_instance.execute_query.return_value = [{'total_amount': -1000.0, 'transaction_count': 50}]
        
        result = processor.check_daily_limits(1, 100.0)  # 50 transactions = limit
        self.assertFalse(result)
    
    @patch('transaction.Database')
    def test_batch_payment_processing(self, mock_db):
        """Test batch payment processing business logic"""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        
        processor = TransactionProcessor()
        
        # Mock successful transfer method
        def mock_transfer(from_id, to_id, amount, description):
            if amount <= 1000:  # Simulate success for amounts <= 1000
                return {'status': 'SUCCESS', 'from_balance': 500.0, 'to_balance': 1500.0}
            else:
                raise ValueError("Amount too large")
        
        processor.process_transfer = MagicMock(side_effect=mock_transfer)
        
        # Test batch with mixed results
        payments = [
            {'from_account_id': 1, 'to_account_id': 2, 'amount': 500.0, 'description': 'Payment 1'},
            {'from_account_id': 3, 'to_account_id': 4, 'amount': 2000.0, 'description': 'Payment 2'},  # Will fail
            {'from_account_id': 5, 'to_account_id': 6, 'amount': 300.0, 'description': 'Payment 3'},
        ]
        
        results = processor.process_batch_payments(payments)
        
        # Verify results
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['status'], 'SUCCESS')
        self.assertEqual(results[1]['status'], 'FAILED')
        self.assertEqual(results[2]['status'], 'SUCCESS')
        
        # Verify partial processing (some succeed, some fail)
        successful_payments = [r for r in results if r['status'] == 'SUCCESS']
        failed_payments = [r for r in results if r['status'] == 'FAILED']
        
        self.assertEqual(len(successful_payments), 2)
        self.assertEqual(len(failed_payments), 1)


if __name__ == '__main__':
    print("Running Business Logic Tests")
    print("=" * 50)
    print("These tests focus on business rules and domain logic")
    print("=" * 50)
    
    unittest.main(verbosity=2)
