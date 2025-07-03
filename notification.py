"""
Legacy Notification Module - Demonstrates hard dependencies and mixed concerns
Issues:
- Hard-coded dependencies (SMTP settings)
- No dependency injection
- Mixed concerns (email formatting with sending)
- No error handling
- No configuration management
- Synchronous operations blocking
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging


class NotificationService:
    """Notification service with hard dependencies"""
    
    def __init__(self):
        # Hard-coded configuration (anti-pattern)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = "bank@example.com"  # Hard-coded credentials
        self.password = "hardcoded_password"  # Security issue
        self.from_email = "noreply@legacybank.com"
        
        # Direct logging setup
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def send_email(self, to_email, subject, message):
        """Email sending with mixed concerns"""
        try:
            # Email formatting embedded in sending logic
            formatted_message = self.format_email_message(message)
            
            # Direct SMTP connection (no connection pooling)
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # Hard-coded authentication
            server.login(self.username, self.password)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach body
            msg.attach(MIMEText(formatted_message, 'html'))
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            # Direct logging
            self.logger.info(f"Email sent to {to_email}: {subject}")
            
            # Save to database for audit (mixed concerns)
            self.save_notification_log(to_email, subject, message, 'EMAIL', 'SENT')
            
            return True
            
        except Exception as e:
            # Poor error handling
            print(f"Failed to send email: {e}")
            self.save_notification_log(to_email, subject, message, 'EMAIL', 'FAILED')
            return False
    
    def format_email_message(self, message):
        """HTML formatting embedded in service"""
        # Hard-coded HTML template
        html_template = f"""
        <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px;">
                    <div style="background-color: #1e3a8a; color: white; padding: 20px; text-align: center;">
                        <h1>Legacy Bank</h1>
                    </div>
                    <div style="padding: 20px; background-color: #f8f9fa;">
                        <p>Dear Valued Customer,</p>
                        <div style="background-color: white; padding: 15px; border-left: 4px solid #1e3a8a; margin: 10px 0;">
                            {message}
                        </div>
                        <p>Thank you for banking with us.</p>
                        <p>Best regards,<br>Legacy Bank Team</p>
                    </div>
                    <div style="background-color: #6b7280; color: white; padding: 10px; text-align: center; font-size: 12px;">
                        <p>This is an automated message. Please do not reply.</p>
                        <p>© 2025 Legacy Bank. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        return html_template
    
    def send_sms(self, phone_number, message):
        """SMS functionality with hard-coded provider"""
        try:
            # Simulate SMS sending (would normally use SMS provider API)
            print(f"SMS sent to {phone_number}: {message}")
            
            # Log SMS (mixed concerns)
            self.save_notification_log(phone_number, "SMS Alert", message, 'SMS', 'SENT')
            return True
            
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            self.save_notification_log(phone_number, "SMS Alert", message, 'SMS', 'FAILED')
            return False
    
    def save_notification_log(self, recipient, subject, message, notification_type, status):
        """Audit logging with direct database access"""
        from database import Database
        
        db = Database()
        
        # Create notifications table if not exists (mixed concerns)
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT,
                subject TEXT,
                message TEXT,
                notification_type TEXT,
                status TEXT,
                sent_at TEXT
            )
        """)
        
        # Save notification log
        query = """
            INSERT INTO notifications (recipient, subject, message, notification_type, status, sent_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        db.execute_query(query, (recipient, subject, message, notification_type, status, datetime.now().isoformat()))
    
    def send_welcome_email(self, customer_name, customer_email):
        """Business logic in notification service"""
        subject = "Welcome to Legacy Bank!"
        message = f"""
        Welcome {customer_name}!
        
        Thank you for choosing Legacy Bank for your banking needs.
        
        Your account has been successfully created. You can now:
        • Access your accounts online
        • Make deposits and withdrawals
        • Transfer funds between accounts
        • View transaction history
        
        If you have any questions, please contact our customer service.
        """
        
        return self.send_email(customer_email, subject, message)
    
    def send_low_balance_alert(self, customer_email, account_number, balance):
        """More business logic in wrong layer"""
        subject = "Low Balance Alert"
        message = f"""
        Your account {account_number} has a low balance.
        
        Current balance: ${balance:.2f}
        
        Please consider making a deposit to avoid any overdraft fees.
        """
        
        return self.send_email(customer_email, subject, message)
    
    def send_transaction_alert(self, customer_email, transaction_type, amount, account_number, new_balance):
        """Transaction formatting in notification service"""
        subject = f"Transaction Alert - {account_number}"
        
        message = f"""
        A {transaction_type.lower()} transaction has been processed on your account.
        
        Transaction Details:
        • Account: {account_number}
        • Type: {transaction_type}
        • Amount: ${abs(amount):.2f}
        • New Balance: ${new_balance:.2f}
        • Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        If you did not authorize this transaction, please contact us immediately.
        """
        
        return self.send_email(customer_email, subject, message)
    
    def send_monthly_statement_notification(self, customer_email, customer_name):
        """Statement notification with embedded logic"""
        subject = "Your Monthly Statement is Ready"
        message = f"""
        Dear {customer_name},
        
        Your monthly bank statement is now available.
        
        You can view your statement by logging into your online banking account
        or visiting any of our branch locations.
        
        Statement includes:
        • Account balances
        • Transaction history
        • Interest earned
        • Fees charged
        """
        
        return self.send_email(customer_email, subject, message)
    
    def get_notification_history(self, recipient=None, notification_type=None):
        """Data access in notification service"""
        from database import Database
        
        db = Database()
        
        query = "SELECT * FROM notifications WHERE 1=1"
        params = []
        
        if recipient:
            query += " AND recipient = ?"
            params.append(recipient)
        
        if notification_type:
            query += " AND notification_type = ?"
            params.append(notification_type)
        
        query += " ORDER BY sent_at DESC"
        
        return db.execute_query(query, params if params else None)
