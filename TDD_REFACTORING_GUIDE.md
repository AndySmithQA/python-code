# TDD Refactoring Exercise Guide

This guide walks you through refactoring the legacy banking application using Test-Driven Development (TDD) practices.

## Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the existing tests to see current state:
```bash
python -m pytest tests/ -v
```

3. Run the application to understand functionality:
```bash
python main.py
```

## TDD Refactoring Process

### Phase 1: Establish Test Coverage (Red-Green-Refactor)

#### Step 1: Write Tests for Existing Functionality
Before refactoring, write comprehensive tests for current behavior:

1. **Customer Tests**
   - Customer creation validation
   - Email/phone validation
   - Account creation for customers
   - Customer data persistence

2. **Account Tests**
   - Account creation with different types
   - Deposit/withdrawal operations
   - Balance calculations
   - Transaction history
   - Account closure

3. **Transaction Tests**
   - Transfer between accounts
   - Bill payments
   - Transaction limits
   - Fraud detection

4. **Utility Tests**
   - Input validation
   - Currency formatting
   - Date calculations
   - Password validation

#### Step 2: Identify Code Smells and Anti-Patterns

Review the code and identify:

1. **God Objects**
   - `Customer` class doing too much
   - `ReportGenerator` handling all reporting
   - `TransactionProcessor` mixing concerns

2. **Tight Coupling**
   - Direct database access in domain objects
   - Hard-coded dependencies
   - Circular import risks

3. **Mixed Concerns**
   - Business logic in data access layer
   - Presentation logic in domain objects
   - Validation scattered throughout

4. **Poor Testability**
   - No dependency injection
   - Static dependencies
   - Direct database access

### Phase 2: Extract and Refactor (TDD Approach)

#### Step 3: Extract Value Objects
Apply TDD to create value objects:

1. **Money Value Object**
```python
# Test first
def test_money_creation():
    money = Money(100.50)
    assert money.amount == 100.50
    assert str(money) == "$100.50"

def test_money_addition():
    money1 = Money(100)
    money2 = Money(50)
    result = money1 + money2
    assert result.amount == 150

# Then implement
class Money:
    def __init__(self, amount):
        if amount < 0:
            raise ValueError("Money cannot be negative")
        self._amount = round(amount, 2)
    
    @property
    def amount(self):
        return self._amount
    
    def __add__(self, other):
        return Money(self._amount + other.amount)
    
    def __str__(self):
        return f"${self._amount:.2f}"
```

2. **Account Number Value Object**
3. **Email Address Value Object**
4. **Phone Number Value Object**

#### Step 4: Extract Repositories (Data Access Layer)
Use TDD to create repository pattern:

1. **Customer Repository**
```python
# Test first
def test_customer_repository_save():
    repo = CustomerRepository()
    customer = Customer("John Doe", "john@example.com")
    
    saved_customer = repo.save(customer)
    assert saved_customer.id is not None

def test_customer_repository_find_by_id():
    repo = CustomerRepository()
    customer = repo.find_by_id(1)
    assert customer.name == "John Doe"

# Then implement
class CustomerRepository:
    def __init__(self, database):
        self._database = database
    
    def save(self, customer):
        # Implementation
        pass
    
    def find_by_id(self, customer_id):
        # Implementation
        pass
```

2. **Account Repository**
3. **Transaction Repository**

#### Step 5: Extract Services (Business Logic Layer)
Apply TDD to extract business services:

1. **Account Service**
```python
# Test first
def test_account_service_create_account():
    customer_repo = Mock()
    account_repo = Mock()
    notification_service = Mock()
    
    service = AccountService(customer_repo, account_repo, notification_service)
    
    account = service.create_account(
        customer_id=1,
        account_type=AccountType.CHECKING,
        initial_deposit=Money(100)
    )
    
    assert account.account_type == AccountType.CHECKING
    assert account.balance.amount == 100
    notification_service.send_welcome_email.assert_called_once()

# Then implement
class AccountService:
    def __init__(self, customer_repo, account_repo, notification_service):
        self._customer_repo = customer_repo
        self._account_repo = account_repo
        self._notification_service = notification_service
    
    def create_account(self, customer_id, account_type, initial_deposit):
        # Business logic implementation
        pass
```

2. **Transaction Service**
3. **Notification Service Interface**

#### Step 6: Implement Dependency Injection
Use TDD to create dependency injection:

1. **Service Container**
2. **Configuration Management**
3. **Factory Patterns**

### Phase 3: Advanced Refactoring

#### Step 7: Implement Clean Architecture
Apply TDD to restructure into clean architecture:

1. **Domain Layer**
   - Entities (Customer, Account, Transaction)
   - Value Objects (Money, AccountNumber, Email)
   - Domain Services
   - Repository Interfaces

2. **Application Layer**
   - Use Cases/Application Services
   - DTOs (Data Transfer Objects)
   - Application Interfaces

3. **Infrastructure Layer**
   - Repository Implementations
   - Database Access
   - External Service Integrations

4. **Presentation Layer**
   - Controllers/Handlers
   - Request/Response Models
   - UI Logic

#### Step 8: Add Advanced Features with TDD

1. **Event Sourcing**
```python
# Test first
def test_account_events_are_recorded():
    account = Account.create(AccountNumber("123"), Money(100))
    account.deposit(Money(50))
    
    events = account.get_uncommitted_events()
    assert len(events) == 2
    assert isinstance(events[0], AccountCreated)
    assert isinstance(events[1], MoneyDeposited)

# Then implement event sourcing
```

2. **CQRS (Command Query Responsibility Segregation)**
3. **Domain Events**
4. **Saga Pattern for Complex Transactions**

## Refactoring Exercises

### Exercise 1: Extract Money Value Object
1. Write tests for Money class
2. Implement Money class
3. Replace all amount calculations to use Money
4. Ensure all tests pass

### Exercise 2: Extract Account Repository
1. Define AccountRepository interface
2. Write tests for repository operations
3. Implement repository
4. Inject repository into Account class
5. Remove direct database access from Account

### Exercise 3: Extract Transaction Service
1. Write tests for transaction operations
2. Implement TransactionService
3. Move business logic from TransactionProcessor
4. Add proper transaction management

### Exercise 4: Implement Validation Layer
1. Create validation interfaces
2. Write validation tests
3. Implement validators
4. Integrate with domain objects

## Testing Strategies

### Unit Testing
- Test individual classes in isolation
- Use mocks for dependencies
- Focus on business logic
- Aim for high code coverage

### Integration Testing
- Test component interactions
- Use test databases
- Test real database operations
- Verify service integrations

### End-to-End Testing
- Test complete user workflows
- Use test automation
- Verify system behavior
- Test error scenarios

## Common Refactoring Patterns

### 1. Extract Method
Break large methods into smaller, focused methods.

### 2. Extract Class
Split classes with multiple responsibilities.

### 3. Move Method
Move methods to more appropriate classes.

### 4. Replace Conditional with Polymorphism
Use inheritance instead of if/else statements.

### 5. Introduce Parameter Object
Group related parameters into objects.

### 6. Replace Magic Numbers with Constants
Create named constants for magic numbers.

## Success Criteria

After refactoring, the code should have:

1. **High Test Coverage** (>90%)
2. **Separated Concerns** (each class has single responsibility)
3. **Dependency Injection** (no hard-coded dependencies)
4. **Clean Architecture** (layers are properly separated)
5. **Value Objects** (primitive obsession eliminated)
6. **Repository Pattern** (data access abstracted)
7. **Domain Events** (loose coupling between components)
8. **Comprehensive Validation** (input validation at boundaries)
9. **Error Handling** (proper exception handling)
10. **Documentation** (code is self-documenting)

## Tools and Resources

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **coverage**: Test coverage

### Refactoring Tools
- **rope**: Python refactoring library
- **IDE refactoring**: Use IDE refactoring features
- **git**: Version control for safe refactoring

### Learning Resources
- "Refactoring" by Martin Fowler
- "Clean Code" by Robert Martin
- "Clean Architecture" by Robert Martin
- "Test Driven Development" by Kent Beck

## Next Steps

1. Start with simple refactoring exercises
2. Gradually increase complexity
3. Always maintain test coverage
4. Refactor in small increments
5. Commit frequently
6. Get code reviews
7. Measure and improve code quality metrics

Remember: The goal is not just to refactor, but to learn TDD practices and clean code principles that can be applied to real-world legacy systems.
