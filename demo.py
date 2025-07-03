"""
Demo Script for Legacy Banking Application
This script demonstrates the legacy code patterns and sets up sample data
"""

from customer import Customer
from account import Account
from transaction import TransactionProcessor
from reporting import ReportGenerator
from notification import NotificationService
from database import Database


def create_sample_data():
    """Create sample customers and accounts for demonstration"""
    print("Creating sample data...")
    
    try:
        # Create customers
        customer1 = Customer(
            name="John Smith",
            email="john.smith@email.com",
            phone="555-123-4567",
            address="123 Main St, Anytown, ST 12345"
        )
        customer1.save()
        
        customer2 = Customer(
            name="Jane Doe", 
            email="jane.doe@email.com",
            phone="555-987-6543",
            address="456 Oak Ave, Another City, ST 67890"
        )
        customer2.save()
        
        print(f"Created customers: {customer1.name}, {customer2.name}")
        
        # Create accounts for customer1
        account1 = customer1.create_account("CHECKING", 1500.0)
        account2 = customer1.create_account("SAVINGS", 5000.0)
        
        # Create account for customer2
        account3 = customer2.create_account("CHECKING", 2000.0)
        
        print(f"Created accounts: {account1.account_number}, {account2.account_number}, {account3.account_number}")
        
        # Perform some transactions
        processor = TransactionProcessor()
        
        # Deposits
        account1.deposit(500.0, "Initial deposit")
        account3.deposit(300.0, "Payroll deposit")
        
        # Withdrawals
        account1.withdraw(200.0, "ATM withdrawal")
        account2.withdraw(100.0, "Check payment")
        
        # Transfer between accounts
        processor.process_transfer(
            account1.id, 
            account3.id, 
            250.0, 
            "Transfer to Jane"
        )
        
        print("Sample transactions completed!")
        
        return [customer1, customer2], [account1, account2, account3]
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        return [], []


def demonstrate_legacy_issues():
    """Demonstrate various legacy code issues"""
    print("\n" + "="*60)
    print("DEMONSTRATING LEGACY CODE ISSUES")
    print("="*60)
    
    customers, accounts = create_sample_data()
    
    if not customers or not accounts:
        print("Failed to create sample data. Exiting demonstration.")
        return
    
    customer1, customer2 = customers
    account1, account2, account3 = accounts
    
    # Issue 1: God Object - Customer doing too much
    print("\n1. GOD OBJECT ISSUE:")
    print("Customer class handles validation, persistence, business logic, and notifications")
    summary = customer1.get_account_summary()
    print(summary)
    
    # Issue 2: Tight Coupling - Direct database access
    print("\n2. TIGHT COUPLING ISSUE:")
    print("Classes directly access database, making testing difficult")
    
    # Issue 3: Mixed Concerns - Business logic with data access
    print("\n3. MIXED CONCERNS ISSUE:")
    print("Account class mixes business logic with database operations")
    try:
        account1.withdraw(10000.0)  # Should fail due to insufficient funds
    except ValueError as e:
        print(f"Business rule enforced in domain object: {e}")
    
    # Issue 4: Poor Error Handling
    print("\n4. POOR ERROR HANDLING:")
    print("Generic exceptions without proper handling")
    
    # Issue 5: Hard-coded Dependencies
    print("\n5. HARD-CODED DEPENDENCIES:")
    print("Notification service has hard-coded SMTP settings")
    notification_service = NotificationService()
    print(f"SMTP Server: {notification_service.smtp_server}")
    print(f"Username: {notification_service.username}")
    
    # Issue 6: No Separation of Concerns
    print("\n6. NO SEPARATION OF CONCERNS:")
    print("Reporting logic mixed with data access and formatting")
    report_gen = ReportGenerator()
    report = report_gen.generate_customer_statement(customer1.id)
    print("Generated report (first 300 chars):")
    print(report[:300] + "...")
    
    # Issue 7: Primitive Obsession
    print("\n7. PRIMITIVE OBSESSION:")
    print("Using primitives instead of value objects")
    print(f"Account balance as float: {account1.balance} (should be Money object)")
    print(f"Account number as string: {account1.account_number} (should be AccountNumber object)")
    
    # Issue 8: Feature Envy
    print("\n8. FEATURE ENVY:")
    print("Customer class accessing Account data excessively")
    total_balance = customer1.get_total_balance()
    print(f"Total customer balance: ${total_balance:.2f}")
    
    # Issue 9: Long Methods
    print("\n9. LONG METHODS:")
    print("Methods doing multiple things (see account.deposit() method)")
    
    # Issue 10: Static Dependencies
    print("\n10. STATIC DEPENDENCIES:")
    print("Utility classes with static methods making testing hard")
    from legacy_utils import LegacyUtils
    account_num = LegacyUtils.generate_account_number("CHECKING")
    print(f"Generated account number: {account_num}")


def demonstrate_testing_challenges():
    """Show why the current code is hard to test"""
    print("\n" + "="*60)
    print("TESTING CHALLENGES IN LEGACY CODE")
    print("="*60)
    
    print("\n1. DIRECT DATABASE DEPENDENCIES:")
    print("   - Tests require actual database")
    print("   - Tests are slow and unreliable")
    print("   - Hard to set up test data")
    
    print("\n2. TIGHT COUPLING:")
    print("   - Cannot mock dependencies easily")
    print("   - Tests have side effects")
    print("   - Cannot test in isolation")
    
    print("\n3. MIXED CONCERNS:")
    print("   - Cannot test business logic separately")
    print("   - Tests cover multiple layers")
    print("   - Hard to identify failure points")
    
    print("\n4. STATIC DEPENDENCIES:")
    print("   - Cannot inject test doubles")
    print("   - Global state affects tests")
    print("   - Tests are not deterministic")
    
    print("\n5. POOR SEPARATION:")
    print("   - Cannot test individual responsibilities")
    print("   - Tests become integration tests")
    print("   - Hard to achieve good coverage")


def run_basic_tests():
    """Run the basic test suite"""
    print("\n" + "="*60)
    print("RUNNING BASIC TEST SUITE")
    print("="*60)
    
    try:
        import subprocess
        result = subprocess.run([
            "python", "-m", "pytest", "tests/test_basic.py", "-v"
        ], capture_output=True, text=True, cwd=".")
        
        print("Test Output:")
        print(result.stdout)
        
        if result.stderr:
            print("Test Errors:")
            print(result.stderr)
            
        print(f"Test Exit Code: {result.returncode}")
        
    except Exception as e:
        print(f"Error running tests: {e}")


def main():
    """Main demonstration function"""
    print("LEGACY BANKING APPLICATION - TDD REFACTORING DEMO")
    print("=" * 60)
    print("This demonstration shows a legacy banking application with")
    print("common anti-patterns and code smells that can be refactored")
    print("using Test-Driven Development (TDD) practices.")
    print("=" * 60)
    
    # Demonstrate legacy issues
    demonstrate_legacy_issues()
    
    # Show testing challenges
    demonstrate_testing_challenges()
    
    # Run basic tests
    run_basic_tests()
    
    print("\n" + "="*60)
    print("NEXT STEPS FOR TDD REFACTORING:")
    print("="*60)
    print("1. Review TDD_REFACTORING_GUIDE.md")
    print("2. Start with writing comprehensive tests")
    print("3. Identify and extract value objects")
    print("4. Implement repository pattern")
    print("5. Extract business services")
    print("6. Add dependency injection")
    print("7. Implement clean architecture")
    print("="*60)
    
    print("\nTo run the interactive application:")
    print("python main.py")
    
    print("\nTo run tests:")
    print("python -m pytest tests/ -v")


if __name__ == "__main__":
    main()
