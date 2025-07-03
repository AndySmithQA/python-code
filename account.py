"""
Legacy Account Module - Demonstrates mixed concerns and poor encapsulation
Issues:
- Mixed business logic with data access
- No proper encapsulation
- Direct database access
- No transaction management
- Poor error handling
- Violation of SRP
"""

from datetime import datetime
from database import Database


class Account:
    """Account class with poor separation of concerns"""
    
    def __init__(self, account_id=None, account_number=None, account_type=None, 
                 balance=0, customer_id=None, status='ACTIVE'):
        # Direct database dependency
        self.db = Database()
        
        # Primitive obsession
        self.id = account_id
        self.account_number = account_number
        self.account_type = account_type
        self.balance = balance
        self.customer_id = customer_id
        self.status = status
        self.transactions = []
        
        if account_id:
            self.load_transactions()
    
    def load_transactions(self):
        """Data access mixed with object initialization"""
        query = f"SELECT * FROM transactions WHERE account_id = {self.id} ORDER BY timestamp DESC"
        try:
            transactions_data = self.db.execute_query(query)
            for trans_data in transactions_data:
                # Creating transaction objects inline
                transaction = {
                    'id': trans_data['id'],
                    'type': trans_data['transaction_type'],
                    'amount': trans_data['amount'],
                    'description': trans_data['description'],
                    'timestamp': trans_data['timestamp'],
                    'balance_after': trans_data['balance_after']
                }
                self.transactions.append(transaction)
        except Exception as e:
            print(f"Error loading transactions: {e}")
    
    def deposit(self, amount, description="Deposit"):
        """Business logic mixed with data persistence"""
        # Inline validation
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        if self.status != 'ACTIVE':
            raise ValueError("Cannot deposit to inactive account")
        
        # Direct balance manipulation
        old_balance = self.balance
        self.balance += amount
        
        try:
            # Direct database updates
            self.db.update_account_balance(self.id, self.balance)
            self.db.save_transaction(self.id, 'DEPOSIT', amount, description, self.balance)
            
            # Add to local transactions list
            transaction = {
                'type': 'DEPOSIT',
                'amount': amount,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'balance_after': self.balance
            }
            self.transactions.insert(0, transaction)  # Insert at beginning
            
            # Direct notification (tight coupling)
            self.send_transaction_notification('deposit', amount)
            
            print(f"Deposited ${amount:.2f}. New balance: ${self.balance:.2f}")
            return True
            
        except Exception as e:
            # Rollback in application code (poor transaction management)
            self.balance = old_balance
            print(f"Deposit failed: {e}")
            raise
    
    def withdraw(self, amount, description="Withdrawal"):
        """More mixed concerns"""
        # Validation logic embedded
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if self.status != 'ACTIVE':
            raise ValueError("Cannot withdraw from inactive account")
        
        # Hard-coded business rules
        if self.account_type == 'SAVINGS' and amount > 5000:
            raise ValueError("Daily withdrawal limit for savings account is $5000")
        
        if self.balance < amount:
            # Check for overdraft protection (hard-coded logic)
            overdraft_limit = self.get_overdraft_limit()
            if (self.balance + overdraft_limit) < amount:
                raise ValueError("Insufficient funds including overdraft")
        
        old_balance = self.balance
        self.balance -= amount
        
        try:
            # Direct database operations
            self.db.update_account_balance(self.id, self.balance)
            self.db.save_transaction(self.id, 'WITHDRAWAL', -amount, description, self.balance)
            
            transaction = {
                'type': 'WITHDRAWAL',
                'amount': -amount,
                'description': description,
                'timestamp': datetime.now().isoformat(),
                'balance_after': self.balance
            }
            self.transactions.insert(0, transaction)
            
            # Direct notification
            self.send_transaction_notification('withdrawal', amount)
            
            print(f"Withdrew ${amount:.2f}. New balance: ${self.balance:.2f}")
            return True
            
        except Exception as e:
            # Manual rollback
            self.balance = old_balance
            print(f"Withdrawal failed: {e}")
            raise
    
    def get_overdraft_limit(self):
        """Hard-coded business rules"""
        if self.account_type == 'CHECKING':
            return 500  # $500 overdraft limit
        elif self.account_type == 'SAVINGS':
            return 0    # No overdraft for savings
        else:
            return 1000  # $1000 for credit accounts
    
    def send_transaction_notification(self, transaction_type, amount):
        """Notification responsibility in domain object"""
        from notification import NotificationService
        notification_service = NotificationService()
        
        # Get customer email (feature envy)
        customer_query = f"SELECT email FROM customers WHERE id = {self.customer_id}"
        customer_data = self.db.execute_query(customer_query)
        
        if customer_data and customer_data[0]['email']:
            email = customer_data[0]['email']
            subject = f"Transaction Alert - {self.account_number}"
            message = f"${amount:.2f} {transaction_type} processed. New balance: ${self.balance:.2f}"
            notification_service.send_email(email, subject, message)
    
    def calculate_interest(self):
        """Business logic with hard-coded rates"""
        if self.account_type == 'SAVINGS':
            # Hard-coded interest rate
            annual_rate = 0.02  # 2% annual
            monthly_rate = annual_rate / 12
            interest = self.balance * monthly_rate
            
            if interest > 0:
                self.deposit(interest, "Monthly interest")
                return interest
        return 0
    
    def apply_monthly_fee(self):
        """More hard-coded business rules"""
        fee = 0
        
        if self.account_type == 'CHECKING' and self.balance < 1000:
            fee = 10  # $10 monthly maintenance fee
        elif self.account_type == 'SAVINGS' and self.balance < 500:
            fee = 5   # $5 monthly fee for low balance
        
        if fee > 0:
            self.withdraw(fee, f"Monthly maintenance fee - {self.account_type}")
        
        return fee
    
    def get_transaction_history(self, limit=None):
        """Data formatting in domain object"""
        transactions = self.transactions[:limit] if limit else self.transactions
        
        history = f"Transaction History for Account {self.account_number}\n"
        history += "=" * 50 + "\n"
        
        for trans in transactions:
            history += f"{trans['timestamp'][:10]} | {trans['type']:12} | "
            history += f"${abs(trans['amount']):8.2f} | ${trans['balance_after']:10.2f} | "
            history += f"{trans['description']}\n"
        
        return history
    
    def close_account(self):
        """Account closure with mixed concerns"""
        if self.balance != 0:
            raise ValueError("Account must have zero balance to close")
        
        # Check for pending transactions (should be in service layer)
        recent_transactions = [t for t in self.transactions if 
                             (datetime.now() - datetime.fromisoformat(t['timestamp'])).days < 3]
        
        if recent_transactions:
            raise ValueError("Cannot close account with recent transactions")
        
        try:
            # Direct database update
            query = f"UPDATE accounts SET status = 'CLOSED' WHERE id = {self.id}"
            self.db.execute_query(query)
            self.status = 'CLOSED'
            
            # Send closure notification
            from notification import NotificationService
            notification_service = NotificationService()
            
            # Get customer details (feature envy again)
            customer_query = f"SELECT name, email FROM customers WHERE id = {self.customer_id}"
            customer_data = self.db.execute_query(customer_query)
            
            if customer_data and customer_data[0]['email']:
                email = customer_data[0]['email']
                name = customer_data[0]['name']
                subject = "Account Closure Confirmation"
                message = f"Dear {name}, your account {self.account_number} has been successfully closed."
                notification_service.send_email(email, subject, message)
            
            print(f"Account {self.account_number} closed successfully")
            return True
            
        except Exception as e:
            print(f"Error closing account: {e}")
            raise
    
    def generate_statement(self, start_date=None, end_date=None):
        """Reporting logic in domain object"""
        from reporting import ReportGenerator
        report_gen = ReportGenerator()
        return report_gen.generate_account_statement(self.id, start_date, end_date)
    
    def __str__(self):
        return f"Account({self.account_number}, {self.account_type}, ${self.balance:.2f})"
