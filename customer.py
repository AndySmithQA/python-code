"""
Legacy Customer Module - Demonstrates god object and tight coupling
Issues:
- God object doing too much
- Tight coupling with database
- No separation of concerns
- Mixed business logic and data access
- No input validation
- Primitive obsession
"""

from datetime import datetime
from database import Database
import re


class Customer:
    """God object with too many responsibilities"""
    
    def __init__(self, name=None, email=None, phone=None, address=None, customer_id=None):
        # Direct database dependency (tight coupling)
        self.db = Database()
        
        # Primitive obsession - using strings/ints instead of value objects
        self.id = customer_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.accounts = []
        
        if customer_id:
            self.load_from_database()
    
    def load_from_database(self):
        """Mixed data access with business logic"""
        try:
            # Direct database access
            result = self.db.get_customer_by_id(self.id)
            if result:
                customer_data = result[0]
                self.name = customer_data['name']
                self.email = customer_data['email']
                self.phone = customer_data['phone']
                self.address = customer_data['address']
                self.load_accounts()
        except Exception as e:
            print(f"Error loading customer: {e}")  # Poor error handling
    
    def load_accounts(self):
        """Method doing too much - violates SRP"""
        query = f"SELECT * FROM accounts WHERE customer_id = {self.id}"
        accounts_data = self.db.execute_query(query)
        
        for account_data in accounts_data:
            # Creating objects inside method (tight coupling)
            from account import Account  # Circular import risk
            account = Account(
                account_id=account_data['id'],
                account_number=account_data['account_number'],
                account_type=account_data['account_type'],
                balance=account_data['balance'],
                customer_id=self.id
            )
            self.accounts.append(account)
    
    def save(self):
        """Validation mixed with persistence"""
        # Inline validation (should be separated)
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Customer name is required")
        
        if self.email and not self.is_valid_email(self.email):
            raise ValueError("Invalid email format")
        
        if self.phone and not self.is_valid_phone(self.phone):
            raise ValueError("Invalid phone format")
        
        try:
            # Direct database save
            self.db.save_customer(self.name, self.email, self.phone, self.address)
            print(f"Customer {self.name} saved successfully")
        except Exception as e:
            print(f"Error saving customer: {e}")
            raise
    
    def is_valid_email(self, email):
        """Primitive validation logic embedded in domain object"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def is_valid_phone(self, phone):
        """More embedded validation"""
        # Simple phone validation
        pattern = r'^\+?1?-?\.?\s?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
        return re.match(pattern, phone.replace(' ', '')) is not None
    
    def create_account(self, account_type, initial_deposit=0):
        """Business logic mixed with object creation"""
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative")
        
        if account_type not in ['CHECKING', 'SAVINGS', 'CREDIT']:
            raise ValueError("Invalid account type")
        
        # Hard-coded business rules
        min_deposit = 100 if account_type == 'SAVINGS' else 25
        if initial_deposit < min_deposit:
            raise ValueError(f"Minimum deposit for {account_type} is ${min_deposit}")
        
        # Direct object creation and database access
        from account import Account
        import random
        
        # Poor account number generation
        account_number = f"{account_type[:3]}{random.randint(100000, 999999)}"
        
        try:
            self.db.save_account(self.id, account_number, account_type, initial_deposit)
            
            # Create account object
            account = Account(
                account_number=account_number,
                account_type=account_type,
                balance=initial_deposit,
                customer_id=self.id
            )
            self.accounts.append(account)
            
            # Direct notification (tight coupling)
            self.send_account_creation_notification(account)
            
            return account
        except Exception as e:
            print(f"Error creating account: {e}")
            raise
    
    def send_account_creation_notification(self, account):
        """Notification logic embedded in customer class"""
        from notification import NotificationService
        notification_service = NotificationService()
        
        message = f"New {account.account_type} account {account.account_number} created with balance ${account.balance}"
        notification_service.send_email(self.email, "New Account Created", message)
    
    def get_total_balance(self):
        """Feature envy - accessing other objects' data"""
        total = 0
        for account in self.accounts:
            if account.status == 'ACTIVE':
                total += account.balance
        return total
    
    def get_account_summary(self):
        """Presentation logic in domain object"""
        summary = f"Customer: {self.name}\n"
        summary += f"Email: {self.email}\n"
        summary += f"Phone: {self.phone}\n"
        summary += f"Total Balance: ${self.get_total_balance():.2f}\n"
        summary += "Accounts:\n"
        
        for account in self.accounts:
            summary += f"  - {account.account_type} ({account.account_number}): ${account.balance:.2f}\n"
        
        return summary
    
    def transfer_between_accounts(self, from_account_number, to_account_number, amount):
        """Complex business logic with no separation"""
        from_account = None
        to_account = None
        
        # Finding accounts (should be in repository)
        for account in self.accounts:
            if account.account_number == from_account_number:
                from_account = account
            if account.account_number == to_account_number:
                to_account = account
        
        if not from_account or not to_account:
            raise ValueError("One or both accounts not found")
        
        if from_account.balance < amount:
            raise ValueError("Insufficient funds")
        
        # Direct method calls (tight coupling)
        from_account.withdraw(amount, f"Transfer to {to_account_number}")
        to_account.deposit(amount, f"Transfer from {from_account_number}")
        
        print(f"Transferred ${amount} from {from_account_number} to {to_account_number}")
    
    def generate_monthly_statement(self):
        """Reporting logic in domain object"""
        from reporting import ReportGenerator
        report_gen = ReportGenerator()
        return report_gen.generate_customer_statement(self.id)
    
    def __str__(self):
        return f"Customer({self.id}, {self.name}, {self.email})"
