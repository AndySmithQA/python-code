"""
Legacy Main Application - Demonstrates procedural programming and poor architecture
Issues:
- Procedural programming instead of proper architecture
- No dependency injection
- Mixed concerns (UI, business logic, data access)
- Poor error handling
- No proper application structure
- Global state management
"""

import sys
from datetime import datetime
from customer import Customer
from account import Account
from transaction import TransactionProcessor
from reporting import ReportGenerator
from database import Database
from notification import NotificationService
from legacy_utils import LegacyUtils


class BankingApp:
    """Main application class with god object pattern"""
    
    def __init__(self):
        # Direct instantiation of dependencies (no DI)
        self.db = Database()
        self.transaction_processor = TransactionProcessor()
        self.report_generator = ReportGenerator()
        self.notification_service = NotificationService()
        
        # Global state
        self.current_customer = None
        self.current_account = None
        self.session_data = {}
    
    def run(self):
        """Main application loop with embedded menu logic"""
        print("=" * 60)
        print("WELCOME TO LEGACY BANK SYSTEM")
        print("=" * 60)
        print("WARNING: This is a legacy system for TDD training purposes")
        print("Contains multiple anti-patterns and code smells")
        print("=" * 60)
        
        while True:
            try:
                self.show_main_menu()
                choice = input("\nEnter your choice: ").strip()
                
                if choice == '1':
                    self.create_customer()
                elif choice == '2':
                    self.find_customer()
                elif choice == '3':
                    self.account_operations()
                elif choice == '4':
                    self.transaction_operations()
                elif choice == '5':
                    self.reporting_menu()
                elif choice == '6':
                    self.admin_operations()
                elif choice == '0':
                    print("Thank you for using Legacy Bank System!")
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Please try again.")
    
    def show_main_menu(self):
        """Menu display with hard-coded strings"""
        print("\n" + "=" * 40)
        print("LEGACY BANK - MAIN MENU")
        print("=" * 40)
        print("1. Create New Customer")
        print("2. Find Customer")
        print("3. Account Operations")
        print("4. Transaction Operations")
        print("5. Reports")
        print("6. Admin Operations")
        print("0. Exit")
        print("=" * 40)
        
        if self.current_customer:
            print(f"Current Customer: {self.current_customer.name}")
        if self.current_account:
            print(f"Current Account: {self.current_account.account_number}")
    
    def create_customer(self):
        """Customer creation with inline validation"""
        print("\n--- CREATE NEW CUSTOMER ---")
        
        try:
            # Inline input gathering
            name = input("Enter customer name: ").strip()
            if not name:
                print("Name is required!")
                return
            
            email = input("Enter email: ").strip()
            if email and not LegacyUtils.validate_email(email):
                print("Invalid email format!")
                return
            
            phone = input("Enter phone number: ").strip()
            if phone and not LegacyUtils.validate_phone(phone):
                print("Invalid phone format!")
                return
            
            address = input("Enter address: ").strip()
            
            # Direct object creation
            customer = Customer(name=name, email=email, phone=phone, address=address)
            customer.save()
            
            self.current_customer = customer
            print(f"Customer created successfully! ID: {customer.id}")
            
            # Ask if they want to create an account
            create_account = input("Would you like to create an account? (y/n): ").strip().lower()
            if create_account == 'y':
                self.create_account_for_customer()
                
        except Exception as e:
            print(f"Error creating customer: {e}")
    
    def find_customer(self):
        """Customer lookup with direct database access"""
        print("\n--- FIND CUSTOMER ---")
        
        try:
            customer_id = input("Enter customer ID: ").strip()
            if not customer_id.isdigit():
                print("Invalid customer ID!")
                return
            
            customer = Customer(customer_id=int(customer_id))
            if customer.name:  # Check if customer exists
                self.current_customer = customer
                print(f"Customer found: {customer.name}")
                print(customer.get_account_summary())
            else:
                print("Customer not found!")
                
        except Exception as e:
            print(f"Error finding customer: {e}")
    
    def create_account_for_customer(self):
        """Account creation with embedded business logic"""
        if not self.current_customer:
            print("No customer selected!")
            return
        
        print("\n--- CREATE ACCOUNT ---")
        print("Account Types:")
        print("1. Checking")
        print("2. Savings") 
        print("3. Credit")
        
        choice = input("Select account type: ").strip()
        
        account_types = {'1': 'CHECKING', '2': 'SAVINGS', '3': 'CREDIT'}
        account_type = account_types.get(choice)
        
        if not account_type:
            print("Invalid account type!")
            return
        
        try:
            initial_deposit = float(input("Enter initial deposit: $"))
            
            account = self.current_customer.create_account(account_type, initial_deposit)
            self.current_account = account
            
            print(f"Account created successfully!")
            print(f"Account Number: {account.account_number}")
            print(f"Balance: ${account.balance:.2f}")
            
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    def account_operations(self):
        """Account operations menu"""
        if not self.current_customer:
            print("Please select a customer first!")
            return
        
        print("\n--- ACCOUNT OPERATIONS ---")
        print("1. View Accounts")
        print("2. Select Account")
        print("3. Create New Account")
        print("4. Close Account")
        print("5. View Account Statement")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            self.view_accounts()
        elif choice == '2':
            self.select_account()
        elif choice == '3':
            self.create_account_for_customer()
        elif choice == '4':
            self.close_account()
        elif choice == '5':
            self.view_account_statement()
        else:
            print("Invalid choice!")
    
    def view_accounts(self):
        """Account listing with formatting"""
        print("\n--- CUSTOMER ACCOUNTS ---")
        if not self.current_customer.accounts:
            print("No accounts found.")
            return
        
        for i, account in enumerate(self.current_customer.accounts, 1):
            print(f"{i}. {account.account_type} - {account.account_number} - ${account.balance:.2f}")
    
    def select_account(self):
        """Account selection logic"""
        self.view_accounts()
        
        if not self.current_customer.accounts:
            return
        
        try:
            choice = int(input("Select account number: ")) - 1
            if 0 <= choice < len(self.current_customer.accounts):
                self.current_account = self.current_customer.accounts[choice]
                print(f"Selected account: {self.current_account.account_number}")
            else:
                print("Invalid account selection!")
        except ValueError:
            print("Please enter a valid number!")
    
    def transaction_operations(self):
        """Transaction operations menu"""
        if not self.current_account:
            print("Please select an account first!")
            return
        
        print(f"\n--- TRANSACTIONS - {self.current_account.account_number} ---")
        print(f"Current Balance: ${self.current_account.balance:.2f}")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Transfer to Another Account")
        print("4. View Transaction History")
        print("5. Pay Bill")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            self.deposit_money()
        elif choice == '2':
            self.withdraw_money()
        elif choice == '3':
            self.transfer_money()
        elif choice == '4':
            self.view_transaction_history()
        elif choice == '5':
            self.pay_bill()
        else:
            print("Invalid choice!")
    
    def deposit_money(self):
        """Deposit operation with inline logic"""
        try:
            amount = float(input("Enter deposit amount: $"))
            description = input("Enter description (optional): ").strip()
            
            if not description:
                description = "Cash deposit"
            
            self.current_account.deposit(amount, description)
            
        except ValueError:
            print("Please enter a valid amount!")
        except Exception as e:
            print(f"Deposit failed: {e}")
    
    def withdraw_money(self):
        """Withdrawal operation"""
        try:
            amount = float(input("Enter withdrawal amount: $"))
            description = input("Enter description (optional): ").strip()
            
            if not description:
                description = "Cash withdrawal"
            
            self.current_account.withdraw(amount, description)
            
        except ValueError:
            print("Please enter a valid amount!")
        except Exception as e:
            print(f"Withdrawal failed: {e}")
    
    def transfer_money(self):
        """Transfer operation with embedded logic"""
        try:
            to_account_number = input("Enter destination account number: ").strip()
            amount = float(input("Enter transfer amount: $"))
            description = input("Enter description (optional): ").strip()
            
            if not description:
                description = "Account transfer"
            
            # Find destination account (inefficient)
            to_account = None
            to_account_data = self.db.get_account_by_number(to_account_number)
            
            if not to_account_data:
                print("Destination account not found!")
                return
            
            # Process transfer
            result = self.transaction_processor.process_transfer(
                self.current_account.id,
                to_account_data[0]['id'],
                amount,
                description
            )
            
            if result['status'] == 'SUCCESS':
                print("Transfer completed successfully!")
                print(f"New balance: ${result['from_balance']:.2f}")
            
        except ValueError:
            print("Please enter a valid amount!")
        except Exception as e:
            print(f"Transfer failed: {e}")
    
    def view_transaction_history(self):
        """Transaction history display"""
        try:
            limit = input("Enter number of transactions to show (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            
            history = self.current_account.get_transaction_history(limit)
            print(history)
            
        except Exception as e:
            print(f"Error retrieving history: {e}")
    
    def pay_bill(self):
        """Bill payment operation"""
        try:
            payee = input("Enter payee name: ").strip()
            amount = float(input("Enter amount: $"))
            reference = input("Enter reference number: ").strip()
            
            result = self.transaction_processor.process_bill_payment(
                self.current_account.id,
                payee,
                amount,
                reference
            )
            
            print("Bill payment processed successfully!")
            print(f"Reference: {result['reference']}")
            
        except ValueError:
            print("Please enter a valid amount!")
        except Exception as e:
            print(f"Bill payment failed: {e}")
    
    def reporting_menu(self):
        """Reporting operations"""
        print("\n--- REPORTS ---")
        print("1. Customer Statement")
        print("2. Account Statement") 
        print("3. Monthly Summary")
        print("4. Transaction Volume Report")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            self.generate_customer_statement()
        elif choice == '2':
            self.generate_account_statement()
        elif choice == '3':
            self.generate_monthly_summary()
        elif choice == '4':
            self.generate_transaction_volume_report()
        else:
            print("Invalid choice!")
    
    def generate_customer_statement(self):
        """Customer statement generation"""
        if not self.current_customer:
            print("Please select a customer first!")
            return
        
        statement = self.report_generator.generate_customer_statement(self.current_customer.id)
        print(statement)
    
    def generate_account_statement(self):
        """Account statement generation"""
        if not self.current_account:
            print("Please select an account first!")
            return
        
        statement = self.report_generator.generate_account_statement(self.current_account.id)
        print(statement)
    
    def generate_monthly_summary(self):
        """Monthly summary report"""
        summary = self.report_generator.generate_monthly_summary_report()
        print(summary)
    
    def generate_transaction_volume_report(self):
        """Transaction volume report"""
        try:
            days = input("Enter number of days (default 30): ").strip()
            days = int(days) if days.isdigit() else 30
            
            report = self.report_generator.generate_transaction_volume_report(days)
            print(report)
            
        except Exception as e:
            print(f"Error generating report: {e}")
    
    def admin_operations(self):
        """Admin operations (simplified)"""
        print("\n--- ADMIN OPERATIONS ---")
        print("1. Database Status")
        print("2. Send Test Notification")
        print("3. Apply Interest")
        print("4. Apply Monthly Fees")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            self.show_database_status()
        elif choice == '2':
            self.send_test_notification()
        elif choice == '3':
            self.apply_interest()
        elif choice == '4':
            self.apply_monthly_fees()
        else:
            print("Invalid choice!")
    
    def show_database_status(self):
        """Database status display"""
        try:
            customers = self.db.execute_query("SELECT COUNT(*) as count FROM customers")
            accounts = self.db.execute_query("SELECT COUNT(*) as count FROM accounts")
            transactions = self.db.execute_query("SELECT COUNT(*) as count FROM transactions")
            
            print("\n--- DATABASE STATUS ---")
            print(f"Customers: {customers[0]['count'] if customers else 0}")
            print(f"Accounts: {accounts[0]['count'] if accounts else 0}")
            print(f"Transactions: {transactions[0]['count'] if transactions else 0}")
            
        except Exception as e:
            print(f"Error checking database status: {e}")
    
    def send_test_notification(self):
        """Test notification sending"""
        email = input("Enter email address: ").strip()
        if email:
            success = self.notification_service.send_email(
                email,
                "Test Notification",
                "This is a test notification from Legacy Bank System."
            )
            print("Notification sent!" if success else "Failed to send notification!")
    
    def apply_interest(self):
        """Interest application (admin function)"""
        if not self.current_account:
            print("Please select an account first!")
            return
        
        interest = self.current_account.calculate_interest()
        if interest > 0:
            print(f"Interest applied: ${interest:.2f}")
        else:
            print("No interest applicable for this account type.")
    
    def apply_monthly_fees(self):
        """Monthly fee application"""
        if not self.current_account:
            print("Please select an account first!")
            return
        
        fee = self.current_account.apply_monthly_fee()
        if fee > 0:
            print(f"Monthly fee applied: ${fee:.2f}")
        else:
            print("No monthly fee applicable.")
    
    def close_account(self):
        """Account closure operation"""
        if not self.current_account:
            print("Please select an account first!")
            return
        
        try:
            confirm = input(f"Are you sure you want to close account {self.current_account.account_number}? (yes/no): ")
            if confirm.lower() == 'yes':
                self.current_account.close_account()
                self.current_account = None
                print("Account closed successfully!")
            else:
                print("Account closure cancelled.")
                
        except Exception as e:
            print(f"Error closing account: {e}")
    
    def view_account_statement(self):
        """Account statement viewing"""
        if not self.current_account:
            print("Please select an account first!")
            return
        
        statement = self.current_account.generate_statement()
        print(statement)


def main():
    """Main function with direct instantiation"""
    try:
        app = BankingApp()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
