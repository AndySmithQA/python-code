"""
Legacy Utilities Module - Demonstrates various code smells and anti-patterns
Issues:
- Utility classes (procedural programming)
- Static methods everywhere
- Hard-coded constants
- Mixed responsibilities
- Poor error handling
- No input validation
"""

import random
import string
import re
from datetime import datetime, timedelta
import hashlib
import os


class LegacyUtils:
    """Utility class with static methods (anti-pattern)"""
    
    # Hard-coded constants (should be in configuration)
    ACCOUNT_NUMBER_LENGTH = 10
    PASSWORD_MIN_LENGTH = 8
    TRANSACTION_ID_LENGTH = 16
    
    @staticmethod
    def generate_account_number(account_type):
        """Account number generation with hard-coded logic"""
        # Hard-coded prefixes
        prefixes = {
            'CHECKING': 'CHK',
            'SAVINGS': 'SAV', 
            'CREDIT': 'CRD'
        }
        
        prefix = prefixes.get(account_type, 'UNK')
        
        # Poor random number generation
        random_part = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        
        return f"{prefix}{random_part}"
    
    @staticmethod
    def validate_email(email):
        """Email validation with basic regex"""
        if not email:
            return False
        
        # Simple regex (not comprehensive)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Phone validation with multiple formats"""
        if not phone:
            return False
        
        # Remove all non-digits
        digits_only = re.sub(r'\D', '', phone)
        
        # Check various lengths (US-centric)
        if len(digits_only) == 10:
            return True
        elif len(digits_only) == 11 and digits_only[0] == '1':
            return True
        
        return False
    
    @staticmethod
    def format_currency(amount):
        """Currency formatting without locale support"""
        if amount is None:
            return "$0.00"
        
        # Basic formatting (no locale consideration)
        return f"${amount:,.2f}"
    
    @staticmethod
    def calculate_interest(principal, rate, periods, compound_type='monthly'):
        """Interest calculation with hard-coded logic"""
        if compound_type == 'monthly':
            monthly_rate = rate / 12
            return principal * (1 + monthly_rate) ** periods
        elif compound_type == 'daily':
            daily_rate = rate / 365
            return principal * (1 + daily_rate) ** periods
        else:
            # Simple interest
            return principal * (1 + rate * periods)
    
    @staticmethod
    def hash_password(password):
        """Weak password hashing"""
        # Using MD5 (insecure)
        return hashlib.md5(password.encode()).hexdigest()
    
    @staticmethod
    def validate_password(password):
        """Password validation with hard-coded rules"""
        if len(password) < LegacyUtils.PASSWORD_MIN_LENGTH:
            return False, "Password too short"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain digit"
        
        return True, "Password valid"
    
    @staticmethod
    def generate_transaction_id():
        """Transaction ID generation"""
        # Using timestamp + random (not guaranteed unique)
        timestamp = str(int(datetime.now().timestamp()))
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"TXN{timestamp}{random_part}"
    
    @staticmethod
    def is_business_day(date):
        """Business day checking (US-centric)"""
        # Only checks weekends, no holiday support
        return date.weekday() < 5
    
    @staticmethod
    def calculate_business_days(start_date, end_date):
        """Business days calculation without holiday consideration"""
        business_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if LegacyUtils.is_business_day(current_date):
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
    
    @staticmethod
    def format_account_number(account_number):
        """Account number formatting"""
        if len(account_number) >= 10:
            # Format as XXX-XXX-XXXX
            return f"{account_number[:3]}-{account_number[3:6]}-{account_number[6:]}"
        return account_number
    
    @staticmethod
    def mask_account_number(account_number):
        """Account number masking for display"""
        if len(account_number) > 4:
            return f"****-{account_number[-4:]}"
        return account_number
    
    @staticmethod
    def calculate_age(birth_date):
        """Age calculation"""
        today = datetime.now().date()
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    @staticmethod
    def validate_ssn(ssn):
        """SSN validation (US-specific)"""
        # Remove non-digits
        digits_only = re.sub(r'\D', '', ssn)
        
        # Check length
        if len(digits_only) != 9:
            return False
        
        # Basic format validation (XXX-XX-XXXX)
        pattern = r'^\d{3}-?\d{2}-?\d{4}$'
        return re.match(pattern, ssn) is not None


class DateUtils:
    """Date utility class with more static methods"""
    
    @staticmethod
    def get_month_start(date=None):
        """Get start of month"""
        if date is None:
            date = datetime.now()
        return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_month_end(date=None):
        """Get end of month"""
        if date is None:
            date = datetime.now()
        
        # Calculate last day of month
        if date.month == 12:
            next_month = date.replace(year=date.year + 1, month=1, day=1)
        else:
            next_month = date.replace(month=date.month + 1, day=1)
        
        return next_month - timedelta(days=1)
    
    @staticmethod
    def format_date(date, format_type='standard'):
        """Date formatting with limited options"""
        if format_type == 'standard':
            return date.strftime('%Y-%m-%d')
        elif format_type == 'display':
            return date.strftime('%B %d, %Y')
        elif format_type == 'short':
            return date.strftime('%m/%d/%Y')
        else:
            return str(date)


class StringUtils:
    """String utility class"""
    
    @staticmethod
    def clean_string(text):
        """String cleaning with basic operations"""
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters (too aggressive)
        cleaned = re.sub(r'[^\w\s.-]', '', cleaned)
        
        return cleaned
    
    @staticmethod
    def capitalize_name(name):
        """Name capitalization with simple logic"""
        if not name:
            return ""
        
        # Simple title case (doesn't handle prefixes like 'von', 'de', etc.)
        return name.title()
    
    @staticmethod
    def generate_random_string(length, include_numbers=True):
        """Random string generation"""
        chars = string.ascii_letters
        if include_numbers:
            chars += string.digits
        
        return ''.join(random.choices(chars, k=length))


class ValidationUtils:
    """Validation utility class with mixed responsibilities"""
    
    @staticmethod
    def validate_amount(amount):
        """Amount validation with business rules"""
        if not isinstance(amount, (int, float)):
            return False, "Amount must be numeric"
        
        if amount < 0:
            return False, "Amount cannot be negative"
        
        if amount > 1000000:  # Hard-coded limit
            return False, "Amount exceeds maximum limit"
        
        # Check decimal places
        if isinstance(amount, float) and len(str(amount).split('.')[-1]) > 2:
            return False, "Amount cannot have more than 2 decimal places"
        
        return True, "Valid amount"
    
    @staticmethod
    def validate_account_type(account_type):
        """Account type validation"""
        valid_types = ['CHECKING', 'SAVINGS', 'CREDIT', 'MONEY_MARKET']
        return account_type in valid_types
    
    @staticmethod
    def validate_transaction_type(transaction_type):
        """Transaction type validation"""
        valid_types = ['DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT', 'BILL_PAYMENT', 'INTEREST']
        return transaction_type in valid_types


class ConfigUtils:
    """Configuration utilities with hard-coded values"""
    
    # Hard-coded configuration (should be externalized)
    DATABASE_PATH = "banking.db"
    LOG_LEVEL = "INFO"
    EMAIL_SERVER = "smtp.gmail.com"
    EMAIL_PORT = 587
    
    TRANSACTION_LIMITS = {
        'CHECKING': {'daily': 5000, 'monthly': 50000},
        'SAVINGS': {'daily': 2500, 'monthly': 25000},
        'CREDIT': {'daily': 10000, 'monthly': 100000}
    }
    
    INTEREST_RATES = {
        'CHECKING': 0.001,  # 0.1% annual
        'SAVINGS': 0.02,    # 2% annual
        'MONEY_MARKET': 0.025  # 2.5% annual
    }
    
    @staticmethod
    def get_transaction_limit(account_type, period):
        """Get transaction limits with fallback"""
        return ConfigUtils.TRANSACTION_LIMITS.get(account_type, {}).get(period, 1000)
    
    @staticmethod
    def get_interest_rate(account_type):
        """Get interest rate with fallback"""
        return ConfigUtils.INTEREST_RATES.get(account_type, 0.0)
    
    @staticmethod
    def get_config_value(key, default=None):
        """Get configuration value from environment or default"""
        return os.environ.get(key, default)
