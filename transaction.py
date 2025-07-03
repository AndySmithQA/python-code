"""
Legacy Transaction Module - Demonstrates procedural code and mixed concerns
Issues:
- Procedural programming instead of OOP
- Mixed business logic with data access
- No transaction management
- Poor error handling
- Hard-coded business rules
- No validation layer
"""

from datetime import datetime, timedelta
from database import Database
from notification import NotificationService
import uuid


class TransactionProcessor:
    """Transaction processor with god object anti-pattern"""
    
    def __init__(self):
        # Direct dependencies
        self.db = Database()
        self.notification_service = NotificationService()
        
        # Hard-coded limits
        self.daily_transfer_limit = 10000
        self.monthly_transfer_limit = 50000
        self.max_transactions_per_day = 50
    
    def process_transfer(self, from_account_id, to_account_id, amount, description="Transfer"):
        """Complex method doing too much"""
        try:
            # Get account details (should be in repository)
            from_account = self.get_account_by_id(from_account_id)
            to_account = self.get_account_by_id(to_account_id)
            
            if not from_account or not to_account:
                raise ValueError("Invalid account(s)")
            
            # Validation logic embedded
            self.validate_transfer(from_account, to_account, amount)
            
            # Check daily limits (business logic in processor)
            if not self.check_daily_limits(from_account_id, amount):
                raise ValueError("Daily transfer limit exceeded")
            
            # Process the transfer
            transaction_id = str(uuid.uuid4())
            
            # Manual transaction management (no proper transactions)
            old_from_balance = from_account['balance']
            old_to_balance = to_account['balance']
            
            try:
                # Update balances
                new_from_balance = old_from_balance - amount
                new_to_balance = old_to_balance + amount
                
                # Direct database updates
                self.db.update_account_balance(from_account_id, new_from_balance)
                self.db.update_account_balance(to_account_id, new_to_balance)
                
                # Save transaction records
                self.save_transfer_transactions(from_account_id, to_account_id, amount, description, transaction_id)
                
                # Send notifications (mixed concerns)
                self.send_transfer_notifications(from_account, to_account, amount)
                
                return {
                    'transaction_id': transaction_id,
                    'status': 'SUCCESS',
                    'from_balance': new_from_balance,
                    'to_balance': new_to_balance
                }
                
            except Exception as e:
                # Manual rollback (poor transaction management)
                self.db.update_account_balance(from_account_id, old_from_balance)
                self.db.update_account_balance(to_account_id, old_to_balance)
                raise Exception(f"Transfer failed: {e}")
                
        except Exception as e:
            print(f"Transfer processing error: {e}")
            raise
    
    def get_account_by_id(self, account_id):
        """Data access in business logic layer"""
        query = f"SELECT * FROM accounts WHERE id = {account_id}"
        result = self.db.execute_query(query)
        return result[0] if result else None
    
    def validate_transfer(self, from_account, to_account, amount):
        """Validation logic with hard-coded rules"""
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        
        if from_account['status'] != 'ACTIVE':
            raise ValueError("Source account is not active")
        
        if to_account['status'] != 'ACTIVE':
            raise ValueError("Destination account is not active")
        
        if from_account['balance'] < amount:
            # Check overdraft (hard-coded logic)
            overdraft_limit = 500 if from_account['account_type'] == 'CHECKING' else 0
            if (from_account['balance'] + overdraft_limit) < amount:
                raise ValueError("Insufficient funds")
        
        # Hard-coded business rules
        if amount > 25000:  # Large transaction
            raise ValueError("Transfer amount exceeds maximum limit")
        
        # Account type restrictions
        if from_account['account_type'] == 'SAVINGS' and amount > 5000:
            raise ValueError("Savings account transfer limit is $5000")
    
    def check_daily_limits(self, account_id, amount):
        """Daily limit checking with embedded SQL"""
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        
        # Get today's transfers
        query = f"""
            SELECT SUM(amount) as total_amount, COUNT(*) as transaction_count
            FROM transactions 
            WHERE account_id = {account_id} 
            AND transaction_type IN ('TRANSFER_OUT', 'WITHDRAWAL')
            AND timestamp >= '{start_of_day.isoformat()}'
        """
        
        result = self.db.execute_query(query)
        
        if result and result[0]:
            daily_total = result[0]['total_amount'] or 0
            transaction_count = result[0]['transaction_count'] or 0
            
            if abs(daily_total) + amount > self.daily_transfer_limit:
                return False
            
            if transaction_count >= self.max_transactions_per_day:
                return False
        
        return True
    
    def save_transfer_transactions(self, from_account_id, to_account_id, amount, description, transaction_id):
        """Transaction saving with manual coordination"""
        timestamp = datetime.now().isoformat()
        
        # Get current balances
        from_account = self.get_account_by_id(from_account_id)
        to_account = self.get_account_by_id(to_account_id)
        
        # Save outgoing transaction
        self.db.save_transaction(
            from_account_id, 
            'TRANSFER_OUT', 
            -amount, 
            f"{description} to Account #{to_account['account_number']}", 
            from_account['balance']
        )
        
        # Save incoming transaction
        self.db.save_transaction(
            to_account_id, 
            'TRANSFER_IN', 
            amount, 
            f"{description} from Account #{from_account['account_number']}", 
            to_account['balance']
        )
    
    def send_transfer_notifications(self, from_account, to_account, amount):
        """Notification logic in transaction processor"""
        # Get customer emails
        from_customer = self.get_customer_by_id(from_account['customer_id'])
        to_customer = self.get_customer_by_id(to_account['customer_id'])
        
        # Send notification to sender
        if from_customer and from_customer['email']:
            self.notification_service.send_transaction_alert(
                from_customer['email'],
                'TRANSFER_OUT',
                -amount,
                from_account['account_number'],
                from_account['balance']
            )
        
        # Send notification to receiver
        if to_customer and to_customer['email']:
            self.notification_service.send_transaction_alert(
                to_customer['email'],
                'TRANSFER_IN',
                amount,
                to_account['account_number'],
                to_account['balance']
            )
    
    def get_customer_by_id(self, customer_id):
        """More data access in business logic"""
        query = f"SELECT * FROM customers WHERE id = {customer_id}"
        result = self.db.execute_query(query)
        return result[0] if result else None
    
    def process_bill_payment(self, account_id, payee, amount, reference_number):
        """Bill payment with no separation of concerns"""
        try:
            account = self.get_account_by_id(account_id)
            
            if not account:
                raise ValueError("Account not found")
            
            # Validation
            if account['balance'] < amount:
                raise ValueError("Insufficient funds")
            
            if amount > 10000:  # Hard-coded limit
                raise ValueError("Bill payment limit exceeded")
            
            # Process payment
            new_balance = account['balance'] - amount
            self.db.update_account_balance(account_id, new_balance)
            
            # Save transaction
            description = f"Bill Payment to {payee} (Ref: {reference_number})"
            self.db.save_transaction(account_id, 'BILL_PAYMENT', -amount, description, new_balance)
            
            # Send confirmation (mixed concerns)
            customer = self.get_customer_by_id(account['customer_id'])
            if customer and customer['email']:
                subject = "Bill Payment Confirmation"
                message = f"Bill payment of ${amount:.2f} to {payee} has been processed. Reference: {reference_number}"
                self.notification_service.send_email(customer['email'], subject, message)
            
            return {
                'status': 'SUCCESS',
                'reference': reference_number,
                'new_balance': new_balance
            }
            
        except Exception as e:
            print(f"Bill payment error: {e}")
            raise
    
    def process_batch_payments(self, payments):
        """Batch processing without proper transaction management"""
        results = []
        
        for payment in payments:
            try:
                result = self.process_transfer(
                    payment['from_account_id'],
                    payment['to_account_id'],
                    payment['amount'],
                    payment.get('description', 'Batch payment')
                )
                results.append(result)
                
            except Exception as e:
                # Continue processing other payments (no all-or-nothing semantics)
                results.append({
                    'status': 'FAILED',
                    'error': str(e),
                    'from_account_id': payment['from_account_id']
                })
        
        return results
    
    def get_transaction_summary(self, account_id, start_date=None, end_date=None):
        """Reporting logic in transaction processor"""
        query = f"SELECT * FROM transactions WHERE account_id = {account_id}"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC"
        
        transactions = self.db.execute_query(query, params if params else None)
        
        # Calculate summary (presentation logic in business layer)
        total_debits = sum(t['amount'] for t in transactions if t['amount'] < 0)
        total_credits = sum(t['amount'] for t in transactions if t['amount'] > 0)
        
        return {
            'transactions': transactions,
            'total_credits': total_credits,
            'total_debits': abs(total_debits),
            'net_change': total_credits + total_debits,
            'transaction_count': len(transactions)
        }
    
    def detect_suspicious_activity(self, account_id):
        """Fraud detection in transaction processor"""
        # Get recent transactions
        last_24_hours = datetime.now() - timedelta(hours=24)
        
        query = f"""
            SELECT * FROM transactions 
            WHERE account_id = {account_id} 
            AND timestamp >= '{last_24_hours.isoformat()}'
            ORDER BY timestamp DESC
        """
        
        recent_transactions = self.db.execute_query(query)
        
        # Hard-coded fraud rules
        suspicious_indicators = []
        
        # Too many transactions
        if len(recent_transactions) > 20:
            suspicious_indicators.append("High transaction frequency")
        
        # Large amounts
        large_transactions = [t for t in recent_transactions if abs(t['amount']) > 5000]
        if len(large_transactions) > 3:
            suspicious_indicators.append("Multiple large transactions")
        
        # Round number transactions (possible fraud indicator)
        round_transactions = [t for t in recent_transactions if t['amount'] % 100 == 0]
        if len(round_transactions) > 10:
            suspicious_indicators.append("Multiple round-number transactions")
        
        return suspicious_indicators
