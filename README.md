# Legacy Banking Application - TDD Refactoring Exercise

This is a deliberately designed legacy banking application that demonstrates common anti-patterns and code smells. It's designed to be used as a teaching tool for Test-Driven Development (TDD) and refactoring practices.

## Legacy Code Issues Present

1. **Tight Coupling**: Classes are heavily dependent on each other
2. **God Objects**: Single classes doing too much
3. **No Separation of Concerns**: Business logic mixed with data access and presentation
4. **Hard to Test**: Direct database access, no dependency injection
5. **Poor Error Handling**: Generic exceptions without proper handling
6. **No Input Validation**: Missing or inadequate validation
7. **Static Dependencies**: Hard-coded dependencies making testing difficult
8. **Large Methods**: Methods doing multiple things
9. **Primitive Obsession**: Using primitives instead of value objects
10. **Feature Envy**: Methods accessing data from other objects excessively

## Application Structure

```
banking_app/
├── account.py          # Account management with legacy patterns
├── customer.py         # Customer management with tight coupling
├── transaction.py      # Transaction processing with mixed concerns
├── database.py         # Direct database access (legacy pattern)
├── notification.py     # Notification system with hard dependencies
├── reporting.py        # Reporting with god object pattern
├── main.py            # Main application entry point
├── legacy_utils.py    # Utility functions with various code smells
└── tests/             # Minimal tests (as in legacy systems)
    └── test_basic.py  # Basic tests to start TDD refactoring
```

## How to Use This for TDD Training

1. **Start with Tests**: Write tests for existing functionality
2. **Identify Code Smells**: Review code and identify anti-patterns
3. **Refactor Incrementally**: Use TDD to refactor small pieces
4. **Extract Classes**: Break down god objects
5. **Inject Dependencies**: Remove hard dependencies
6. **Create Value Objects**: Replace primitive obsession
7. **Separate Concerns**: Split mixed responsibilities

## Running the Application

```bash
python main.py
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Refactoring Goals

Transform this legacy code into:
- Well-tested, maintainable code
- Proper separation of concerns
- Dependency injection
- Value objects for domain concepts
- Clean architecture patterns
