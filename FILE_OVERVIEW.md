# Legacy Banking Application - File Overview

This document provides an overview of all files in the legacy banking application and their purposes for TDD refactoring training.

## Application Structure

```
banking_app/
├── README.md                    # Project overview and setup instructions
├── TDD_REFACTORING_GUIDE.md    # Comprehensive TDD refactoring guide
├── requirements.txt             # Python dependencies
├── demo.py                      # Demonstration script showing legacy issues
├── main.py                      # Main application entry point
├── customer.py                  # Customer management (God object)
├── account.py                   # Account operations (mixed concerns)
├── transaction.py               # Transaction processing (poor separation)
├── database.py                  # Direct database access (anti-pattern)
├── notification.py              # Notification system (hard dependencies)
├── reporting.py                 # Report generation (god object)
├── legacy_utils.py              # Utility functions (static methods)
└── tests/
    └── test_basic.py           # Basic test suite (minimal coverage)
```

## File Descriptions

### Core Application Files

#### `main.py`
- **Purpose**: Main application entry point with CLI interface
- **Legacy Issues**: 
  - Procedural programming mixed with OOP
  - No dependency injection
  - Mixed concerns (UI, business logic, data access)
  - Poor error handling
  - Global state management
- **Refactoring Target**: Extract controllers, implement clean architecture

#### `customer.py`
- **Purpose**: Customer management and business logic
- **Legacy Issues**:
  - God object doing too much (validation, persistence, business logic, notifications)
  - Tight coupling with database
  - Feature envy (accessing other objects' data)
  - Mixed concerns (business logic with data access)
  - Primitive obsession (using strings/ints instead of value objects)
- **Refactoring Target**: Extract customer entity, repository, and services

#### `account.py`
- **Purpose**: Account operations and transaction handling
- **Legacy Issues**:
  - Mixed business logic with data persistence
  - Direct database access
  - Poor encapsulation
  - No transaction management
  - Violation of Single Responsibility Principle
- **Refactoring Target**: Extract account entity, transaction service, and repository

#### `transaction.py`
- **Purpose**: Transaction processing and business rules
- **Legacy Issues**:
  - Procedural code mixed with OOP
  - Mixed data access with business logic
  - No proper transaction management
  - Hard-coded business rules
  - Poor error handling
- **Refactoring Target**: Extract transaction entity, service layer, and domain events

#### `database.py`
- **Purpose**: Database access and SQL operations
- **Legacy Issues**:
  - Direct database access without abstraction
  - SQL injection vulnerabilities
  - No connection pooling
  - Hard-coded connection details
  - Mixed business logic in data layer
- **Refactoring Target**: Extract repository interfaces and implementations

#### `notification.py`
- **Purpose**: Notification and email services
- **Legacy Issues**:
  - Hard-coded dependencies (SMTP settings)
  - Mixed concerns (email formatting with sending)
  - No dependency injection
  - Business logic in notification service
  - No error handling
- **Refactoring Target**: Extract notification interfaces and implementations

#### `reporting.py`
- **Purpose**: Report generation and formatting
- **Legacy Issues**:
  - God object handling all reporting
  - Mixed data access with presentation logic
  - Hard-coded formatting
  - Poor performance (N+1 queries)
  - No separation between data and presentation
- **Refactoring Target**: Extract report services and formatters

#### `legacy_utils.py`
- **Purpose**: Utility functions and helper methods
- **Legacy Issues**:
  - Utility classes with static methods (procedural programming)
  - Hard-coded constants
  - Mixed responsibilities
  - Poor error handling
  - No input validation
- **Refactoring Target**: Extract value objects and domain services

### Supporting Files

#### `demo.py`
- **Purpose**: Demonstration script showing legacy code issues
- **Features**:
  - Creates sample data
  - Demonstrates each legacy anti-pattern
  - Shows testing challenges
  - Runs basic test suite
- **Usage**: `python demo.py`

#### `tests/test_basic.py`
- **Purpose**: Basic test suite showing legacy testing challenges
- **Features**:
  - Minimal test coverage
  - Shows difficulty of testing legacy code
  - Demonstrates mocking challenges
  - Examples of integration vs unit tests
- **Usage**: `python tests/test_basic.py`

#### `requirements.txt`
- **Purpose**: Python package dependencies
- **Features**:
  - Minimal dependencies (typical of legacy systems)
  - Comments on packages to add during refactoring
  - Testing dependencies

#### `README.md`
- **Purpose**: Project overview and setup instructions
- **Features**:
  - Legacy code issues present
  - Application structure
  - How to use for TDD training
  - Running instructions

#### `TDD_REFACTORING_GUIDE.md`
- **Purpose**: Comprehensive guide for TDD refactoring
- **Features**:
  - Step-by-step refactoring process
  - TDD best practices
  - Specific exercises
  - Code examples
  - Success criteria

## Legacy Code Anti-Patterns Demonstrated

### 1. God Objects
- **Customer**: Handles validation, persistence, business logic, notifications
- **ReportGenerator**: Handles all reporting functionality
- **TransactionProcessor**: Handles all transaction types

### 2. Tight Coupling
- Direct database access in domain objects
- Hard-coded dependencies
- Circular import risks

### 3. Mixed Concerns
- Business logic in data access layer
- Presentation logic in domain objects
- Validation scattered throughout

### 4. Poor Testability
- No dependency injection
- Static dependencies
- Direct database access

### 5. Primitive Obsession
- Using strings for account numbers
- Using floats for money
- Using strings for email addresses

### 6. Feature Envy
- Methods accessing data from other objects excessively
- Customer accessing Account data

### 7. Long Methods
- Methods doing multiple things
- Complex conditional logic

### 8. Hard-Coded Dependencies
- SMTP settings in notification service
- Database connection strings
- Business rules embedded in code

## TDD Refactoring Targets

### Phase 1: Basic Refactoring
1. **Extract Value Objects**: Money, AccountNumber, Email, Phone
2. **Extract Repositories**: CustomerRepository, AccountRepository, TransactionRepository
3. **Extract Services**: AccountService, TransactionService, NotificationService
4. **Add Dependency Injection**: Service container, configuration management

### Phase 2: Advanced Refactoring
1. **Implement Clean Architecture**: Domain, application, infrastructure layers
2. **Add Domain Events**: Account created, money deposited, transfer completed
3. **Implement CQRS**: Separate command and query responsibilities
4. **Add Event Sourcing**: Store events instead of current state

### Phase 3: Modern Patterns
1. **Microservices**: Split into customer, account, transaction services
2. **API Layer**: REST/GraphQL APIs
3. **Message Queues**: Asynchronous processing
4. **Monitoring**: Logging, metrics, health checks

## How to Use This for Training

### 1. Initial Assessment
- Run `python demo.py` to see legacy issues
- Review code to identify anti-patterns
- Run tests to see testing challenges

### 2. TDD Practice
- Start with writing tests for existing functionality
- Refactor one anti-pattern at a time
- Ensure all tests pass after each refactoring

### 3. Advanced Techniques
- Practice test doubles (mocks, stubs, fakes)
- Learn dependency injection patterns
- Implement clean architecture

### 4. Measurement
- Measure code coverage
- Track cyclomatic complexity
- Monitor code duplication

## Learning Objectives

After completing the refactoring exercises, participants should understand:

1. **TDD Process**: Red-Green-Refactor cycle
2. **Clean Code**: SOLID principles, design patterns
3. **Testing**: Unit, integration, and end-to-end testing
4. **Architecture**: Clean architecture, dependency injection
5. **Domain Modeling**: Entities, value objects, services
6. **Refactoring**: Safe refactoring techniques
7. **Legacy Code**: Strategies for dealing with legacy systems

This application provides a realistic example of legacy code that can be systematically refactored using TDD practices, making it an excellent training tool for developers learning to work with existing codebases.
