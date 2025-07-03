"""
Legacy Reporting Module - Demonstrates god object and mixed concerns
Issues:
- God object with too many responsibilities
- Mixed data access with presentation logic
- Hard-coded formatting
- No separation between data and presentation
- Direct database access
- Poor performance (N+1 queries)
"""

from datetime import datetime, timedelta
from database import Database
import calendar


class ReportGenerator:
    """God object handling all reporting functionality"""
    
    def __init__(self):
        # Direct database dependency
        self.db = Database()
        
        # Hard-coded formatting constants
        self.REPORT_WIDTH = 80
        self.DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
        self.CURRENCY_FORMAT = "${:,.2f}"
    
    def generate_customer_statement(self, customer_id, start_date=None, end_date=None):
        """Customer statement with mixed data access and formatting"""
        try:
            # Get customer data (direct SQL)
            customer_query = f"SELECT * FROM customers WHERE id = {customer_id}"
            customer_data = self.db.execute_query(customer_query)
            
            if not customer_data:
                return "Customer not found"
            
            customer = customer_data[0]
            
            # Get customer accounts (N+1 query problem)
            accounts_query = f"SELECT * FROM accounts WHERE customer_id = {customer_id}"
            accounts = self.db.execute_query(accounts_query)
            
            # Build statement (presentation logic mixed with data access)
            statement = self.build_statement_header(customer)
            statement += self.build_accounts_summary(accounts)
            
            # Get transactions for each account (more N+1 queries)
            for account in accounts:
                statement += self.build_account_transactions(account, start_date, end_date)
            
            statement += self.build_statement_footer()
            
            return statement
            
        except Exception as e:
            return f"Error generating statement: {e}"
    
    def build_statement_header(self, customer):
        """HTML/text generation in business logic"""
        header = "=" * self.REPORT_WIDTH + "\n"
        header += "LEGACY BANK - CUSTOMER STATEMENT".center(self.REPORT_WIDTH) + "\n"
        header += "=" * self.REPORT_WIDTH + "\n"
        header += f"Customer: {customer['name']}\n"
        header += f"Email: {customer['email']}\n"
        header += f"Phone: {customer['phone']}\n"
        header += f"Address: {customer['address']}\n"
        header += f"Statement Date: {datetime.now().strftime(self.DATE_FORMAT)}\n"
        header += "-" * self.REPORT_WIDTH + "\n"
        return header
    
    def build_accounts_summary(self, accounts):
        """Account summary formatting"""
        summary = "ACCOUNTS SUMMARY\n"
        summary += "-" * self.REPORT_WIDTH + "\n"
        
        total_balance = 0
        for account in accounts:
            balance = account['balance']
            total_balance += balance
            
            summary += f"{account['account_type']:15} {account['account_number']:15} "
            summary += f"{self.CURRENCY_FORMAT.format(balance):>15} {account['status']:10}\n"
        
        summary += "-" * self.REPORT_WIDTH + "\n"
        summary += f"{'TOTAL BALANCE:':45} {self.CURRENCY_FORMAT.format(total_balance):>15}\n"
        summary += "-" * self.REPORT_WIDTH + "\n\n"
        
        return summary
    
    def build_account_transactions(self, account, start_date=None, end_date=None):
        """Transaction details with embedded SQL"""
        account_section = f"ACCOUNT: {account['account_number']} ({account['account_type']})\n"
        account_section += "-" * self.REPORT_WIDTH + "\n"
        
        # Build dynamic query (SQL in presentation layer)
        query = f"SELECT * FROM transactions WHERE account_id = {account['id']}"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT 50"  # Hard-coded limit
        
        transactions = self.db.execute_query(query, params if params else None)
        
        if not transactions:
            account_section += "No transactions found.\n\n"
            return account_section
        
        # Format transactions (presentation logic)
        account_section += f"{'Date':12} {'Type':15} {'Amount':12} {'Balance':12} {'Description':25}\n"
        account_section += "-" * self.REPORT_WIDTH + "\n"
        
        for trans in transactions:
            date_str = trans['timestamp'][:10]  # Simple date extraction
            amount_str = self.CURRENCY_FORMAT.format(trans['amount'])
            balance_str = self.CURRENCY_FORMAT.format(trans['balance_after'])
            
            # Truncate description if too long
            description = trans['description'][:25] if len(trans['description']) > 25 else trans['description']
            
            account_section += f"{date_str:12} {trans['transaction_type']:15} "
            account_section += f"{amount_str:>12} {balance_str:>12} {description:25}\n"
        
        account_section += "\n"
        return account_section
    
    def build_statement_footer(self):
        """Footer formatting"""
        footer = "=" * self.REPORT_WIDTH + "\n"
        footer += "Thank you for banking with Legacy Bank!\n"
        footer += "For questions, contact us at support@legacybank.com\n"
        footer += "=" * self.REPORT_WIDTH + "\n"
        return footer
    
    def generate_account_statement(self, account_id, start_date=None, end_date=None):
        """Account-specific statement"""
        try:
            # Get account details
            account_query = f"SELECT * FROM accounts WHERE id = {account_id}"
            account_data = self.db.execute_query(account_query)
            
            if not account_data:
                return "Account not found"
            
            account = account_data[0]
            
            # Get customer info
            customer_query = f"SELECT * FROM customers WHERE id = {account['customer_id']}"
            customer_data = self.db.execute_query(customer_query)
            customer = customer_data[0] if customer_data else {}
            
            # Build statement
            statement = self.build_account_statement_header(account, customer)
            statement += self.build_account_transactions(account, start_date, end_date)
            statement += self.build_statement_footer()
            
            return statement
            
        except Exception as e:
            return f"Error generating account statement: {e}"
    
    def build_account_statement_header(self, account, customer):
        """Account statement header"""
        header = "=" * self.REPORT_WIDTH + "\n"
        header += "LEGACY BANK - ACCOUNT STATEMENT".center(self.REPORT_WIDTH) + "\n"
        header += "=" * self.REPORT_WIDTH + "\n"
        header += f"Account Number: {account['account_number']}\n"
        header += f"Account Type: {account['account_type']}\n"
        header += f"Account Holder: {customer.get('name', 'Unknown')}\n"
        header += f"Current Balance: {self.CURRENCY_FORMAT.format(account['balance'])}\n"
        header += f"Statement Date: {datetime.now().strftime(self.DATE_FORMAT)}\n"
        header += "-" * self.REPORT_WIDTH + "\n"
        return header
    
    def generate_monthly_summary_report(self):
        """Monthly summary with complex embedded logic"""
        try:
            # Calculate current month dates
            now = datetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get all customers (inefficient query)
            customers = self.db.execute_query("SELECT * FROM customers")
            
            report = "=" * self.REPORT_WIDTH + "\n"
            report += f"MONTHLY SUMMARY REPORT - {now.strftime('%B %Y')}".center(self.REPORT_WIDTH) + "\n"
            report += "=" * self.REPORT_WIDTH + "\n"
            
            total_customers = len(customers)
            total_accounts = 0
            total_balance = 0
            total_transactions = 0
            
            # Process each customer (N+1 queries)
            for customer in customers:
                # Get customer accounts
                accounts_query = f"SELECT * FROM accounts WHERE customer_id = {customer['id']}"
                accounts = self.db.execute_query(accounts_query)
                
                customer_balance = 0
                customer_transactions = 0
                
                for account in accounts:
                    total_accounts += 1
                    customer_balance += account['balance']
                    
                    # Get monthly transactions
                    trans_query = f"""
                        SELECT COUNT(*) as count FROM transactions 
                        WHERE account_id = {account['id']} 
                        AND timestamp >= '{start_of_month.isoformat()}'
                    """
                    trans_result = self.db.execute_query(trans_query)
                    customer_transactions += trans_result[0]['count'] if trans_result else 0
                
                total_balance += customer_balance
                total_transactions += customer_transactions
            
            # Build summary
            report += f"Total Customers: {total_customers}\n"
            report += f"Total Accounts: {total_accounts}\n"
            report += f"Total Balance: {self.CURRENCY_FORMAT.format(total_balance)}\n"
            report += f"Total Transactions This Month: {total_transactions}\n"
            report += f"Average Balance per Customer: {self.CURRENCY_FORMAT.format(total_balance / total_customers if total_customers > 0 else 0)}\n"
            
            # Add account type breakdown (more queries)
            report += "\nACCOUNT TYPE BREAKDOWN:\n"
            report += "-" * 40 + "\n"
            
            account_types = ['CHECKING', 'SAVINGS', 'CREDIT']
            for acc_type in account_types:
                type_query = f"SELECT COUNT(*) as count, SUM(balance) as total FROM accounts WHERE account_type = '{acc_type}'"
                type_result = self.db.execute_query(type_query)
                
                if type_result and type_result[0]:
                    count = type_result[0]['count'] or 0
                    total = type_result[0]['total'] or 0
                    report += f"{acc_type:15}: {count:5} accounts, {self.CURRENCY_FORMAT.format(total):>15}\n"
            
            report += "\n" + "=" * self.REPORT_WIDTH + "\n"
            
            return report
            
        except Exception as e:
            return f"Error generating monthly report: {e}"
    
    def generate_transaction_volume_report(self, days=30):
        """Transaction volume analysis with embedded analytics"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            report = "=" * self.REPORT_WIDTH + "\n"
            report += f"TRANSACTION VOLUME REPORT - Last {days} Days".center(self.REPORT_WIDTH) + "\n"
            report += "=" * self.REPORT_WIDTH + "\n"
            
            # Get transaction summary
            summary_query = f"""
                SELECT 
                    transaction_type,
                    COUNT(*) as count,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount
                FROM transactions 
                WHERE timestamp >= '{start_date.isoformat()}'
                GROUP BY transaction_type
                ORDER BY count DESC
            """
            
            summary = self.db.execute_query(summary_query)
            
            report += f"{'Transaction Type':20} {'Count':8} {'Total Amount':15} {'Avg Amount':12}\n"
            report += "-" * self.REPORT_WIDTH + "\n"
            
            for row in summary:
                report += f"{row['transaction_type']:20} {row['count']:8} "
                report += f"{self.CURRENCY_FORMAT.format(row['total_amount'] or 0):>15} "
                report += f"{self.CURRENCY_FORMAT.format(row['avg_amount'] or 0):>12}\n"
            
            # Daily breakdown (more complex query)
            daily_query = f"""
                SELECT 
                    DATE(timestamp) as transaction_date,
                    COUNT(*) as daily_count,
                    SUM(amount) as daily_total
                FROM transactions 
                WHERE timestamp >= '{start_date.isoformat()}'
                GROUP BY DATE(timestamp)
                ORDER BY transaction_date DESC
                LIMIT 10
            """
            
            daily_data = self.db.execute_query(daily_query)
            
            report += "\nDAILY BREAKDOWN (Last 10 Days):\n"
            report += "-" * 50 + "\n"
            report += f"{'Date':12} {'Transactions':12} {'Total Amount':15}\n"
            report += "-" * 50 + "\n"
            
            for row in daily_data:
                report += f"{row['transaction_date']:12} {row['daily_count']:12} "
                report += f"{self.CURRENCY_FORMAT.format(row['daily_total'] or 0):>15}\n"
            
            return report
            
        except Exception as e:
            return f"Error generating transaction volume report: {e}"
    
    def export_to_csv(self, report_type, **kwargs):
        """CSV export with hardcoded formatting"""
        # This method would export reports to CSV
        # For brevity, just returning a placeholder
        return f"CSV export for {report_type} not implemented in legacy system"
    
    def generate_regulatory_report(self):
        """Regulatory reporting with compliance logic embedded"""
        # This would contain complex regulatory logic
        # Mixed with data access and formatting
        return "Regulatory reporting requires manual intervention in legacy system"
