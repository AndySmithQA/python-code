"""
Test Runner for Legacy Banking Application
This script runs all test suites and provides a comprehensive overview
of test coverage and results.
"""

import sys
import os
import unittest
import subprocess
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_test_suite(test_module, description):
    """Run a specific test suite and return results"""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    try:
        # Load and run the test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_module)
        
        # Run tests with detailed output
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)
        
        return {
            'module': test_module,
            'description': description,
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success': result.wasSuccessful(),
            'failure_details': result.failures,
            'error_details': result.errors
        }
        
    except Exception as e:
        print(f"Error running {test_module}: {e}")
        return {
            'module': test_module,
            'description': description,
            'tests_run': 0,
            'failures': 0,
            'errors': 1,
            'success': False,
            'failure_details': [],
            'error_details': [('Test Suite Error', str(e))]
        }


def print_test_summary(results):
    """Print a comprehensive test summary"""
    print(f"\n{'='*80}")
    print("COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = sum(r['tests_run'] for r in results)
    total_failures = sum(r['failures'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    successful_suites = sum(1 for r in results if r['success'])
    
    print(f"Test Execution Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Test Suites: {len(results)}")
    print(f"Successful Test Suites: {successful_suites}")
    print(f"Failed Test Suites: {len(results) - successful_suites}")
    print(f"Total Tests Run: {total_tests}")
    print(f"Total Failures: {total_failures}")
    print(f"Total Errors: {total_errors}")
    print(f"Overall Success Rate: {((total_tests - total_failures - total_errors) / total_tests * 100):.1f}%" if total_tests > 0 else "N/A")
    
    print(f"\n{'Test Suite Results':40} {'Tests':8} {'Fail':6} {'Error':6} {'Status':8}")
    print("-" * 80)
    
    for result in results:
        status = "PASS" if result['success'] else "FAIL"
        print(f"{result['description'][:40]:40} {result['tests_run']:8} {result['failures']:6} {result['errors']:6} {status:8}")
    
    # Print detailed failure information
    if total_failures > 0 or total_errors > 0:
        print(f"\n{'='*80}")
        print("DETAILED FAILURE/ERROR REPORT")
        print(f"{'='*80}")
        
        for result in results:
            if result['failures'] or result['errors']:
                print(f"\n{result['description']} ({result['module']}):")
                print("-" * 40)
                
                for test, traceback in result['failure_details']:
                    print(f"FAILURE: {test}")
                    print(f"Details: {traceback}")
                    print()
                
                for test, traceback in result['error_details']:
                    print(f"ERROR: {test}")
                    print(f"Details: {traceback}")
                    print()


def analyze_test_coverage():
    """Analyze what functionality is being tested"""
    print(f"\n{'='*80}")
    print("TEST COVERAGE ANALYSIS")
    print(f"{'='*80}")
    
    coverage_areas = {
        "Customer Management": [
            "Customer creation and validation",
            "Customer data persistence",
            "Account creation for customers",
            "Customer business rules"
        ],
        "Account Operations": [
            "Account creation with different types",
            "Deposit and withdrawal operations",
            "Balance calculations and updates",
            "Account status management",
            "Interest calculations",
            "Monthly fee applications"
        ],
        "Transaction Processing": [
            "Transfer between accounts",
            "Bill payment processing",
            "Transaction validation",
            "Daily limits enforcement",
            "Batch payment processing"
        ],
        "Data Access Layer": [
            "Database connection management",
            "CRUD operations for customers",
            "CRUD operations for accounts",
            "Transaction history storage",
            "SQL injection vulnerability testing"
        ],
        "Business Rules": [
            "Minimum deposit requirements",
            "Withdrawal limits",
            "Overdraft calculations",
            "Account type restrictions",
            "Transfer limits"
        ],
        "Validation & Utilities": [
            "Email validation",
            "Phone number validation",
            "Amount validation",
            "Password validation",
            "Account number generation",
            "Currency formatting"
        ]
    }
    
    for area, items in coverage_areas.items():
        print(f"\n{area}:")
        for item in items:
            print(f"  ✓ {item}")
    
    print(f"\n{'NOT YET COVERED (Future TDD Refactoring)':}")
    uncovered_areas = [
        "Notification service functionality",
        "Report generation and formatting",
        "Complex integration scenarios",
        "Performance and load testing",
        "Security and authentication",
        "Configuration management",
        "Error handling and recovery",
        "Event sourcing and domain events"
    ]
    
    for item in uncovered_areas:
        print(f"  ⚠ {item}")


def provide_tdd_guidance():
    """Provide guidance on next steps for TDD refactoring"""
    print(f"\n{'='*80}")
    print("TDD REFACTORING GUIDANCE")
    print(f"{'='*80}")
    
    print("""
Phase 1: Foundation (COMPLETED)
✓ Comprehensive test coverage for existing functionality
✓ Database operations testing
✓ Business logic validation
✓ Utility function testing

Phase 2: Next Steps for TDD Refactoring
□ Extract Value Objects:
  - Money class for currency amounts
  - AccountNumber class for account identifiers
  - Email and Phone classes for contact information
  
□ Extract Repository Pattern:
  - CustomerRepository interface and implementation
  - AccountRepository interface and implementation
  - TransactionRepository interface and implementation
  
□ Extract Services:
  - AccountService for account-related business logic
  - TransactionService for transaction processing
  - NotificationService interface for decoupling
  
□ Implement Dependency Injection:
  - Service container for managing dependencies
  - Configuration management for external settings
  - Factory patterns for object creation

Phase 3: Advanced Refactoring
□ Clean Architecture Implementation:
  - Domain layer with entities and value objects
  - Application layer with use cases
  - Infrastructure layer with external concerns
  
□ Domain Events:
  - Event-driven architecture
  - Loose coupling between components
  - Audit trail and business intelligence

Key TDD Principles to Follow:
1. Red-Green-Refactor cycle
2. Write tests first, then implement
3. Keep tests simple and focused
4. Refactor in small increments
5. Maintain test coverage above 90%
6. Test behavior, not implementation details
""")


def main():
    """Main test runner function"""
    print("LEGACY BANKING APPLICATION - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("This test suite establishes baseline coverage for TDD refactoring")
    print("=" * 80)
    
    # Define test suites to run
    test_suites = [
        ('test_basic', 'Basic Legacy Testing Challenges'),
        ('test_comprehensive', 'Comprehensive Functionality Tests'),
        ('test_database', 'Database and Repository Tests'),
        ('test_business_logic', 'Business Logic and Rules Tests')
    ]
    
    results = []
    
    # Change to tests directory
    original_dir = os.getcwd()
    test_dir = os.path.join(os.path.dirname(__file__))
    if test_dir:
        os.chdir(test_dir)
    
    try:
        # Run each test suite
        for module, description in test_suites:
            result = run_test_suite(module, description)
            results.append(result)
        
        # Print comprehensive summary
        print_test_summary(results)
        
        # Analyze test coverage
        analyze_test_coverage()
        
        # Provide TDD guidance
        provide_tdd_guidance()
        
        # Final recommendations
        print(f"\n{'='*80}")
        print("RECOMMENDATIONS")
        print(f"{'='*80}")
        
        total_tests = sum(r['tests_run'] for r in results)
        total_failures = sum(r['failures'] for r in results)
        total_errors = sum(r['errors'] for r in results)
        
        if total_failures == 0 and total_errors == 0:
            print("🎉 All tests passed! You're ready to begin TDD refactoring.")
            print("\nNext Steps:")
            print("1. Read TDD_REFACTORING_GUIDE.md for detailed instructions")
            print("2. Start with extracting the Money value object")
            print("3. Gradually refactor one component at a time")
            print("4. Maintain test coverage throughout the process")
        else:
            print("⚠ Some tests failed. Review the failures above before proceeding.")
            print("\nRecommendations:")
            print("1. Fix failing tests to establish a solid baseline")
            print("2. Ensure all legacy functionality is properly tested")
            print("3. Add any missing test cases")
            print("4. Then proceed with TDD refactoring")
        
        print(f"\nTest Results Summary: {total_tests} tests, {total_failures} failures, {total_errors} errors")
        
    finally:
        # Return to original directory
        os.chdir(original_dir)
    
    return results


if __name__ == "__main__":
    results = main()
    
    # Exit with appropriate code
    total_failures = sum(r['failures'] for r in results)
    total_errors = sum(r['errors'] for r in results)
    
    if total_failures > 0 or total_errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)
