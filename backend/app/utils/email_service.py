"""
Email Service - Gmail SMTP for sending emails
Can be easily swapped to SendGrid/Resend later
"""
import smtplib
import secrets
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
from jinja2 import Template

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service using Gmail SMTP.
    
    Setup Instructions:
    1. Enable 2FA on your Google account
    2. Go to: Google Account → Security → App Passwords
    3. Create a new App Password for "Mail"
    4. Use that 16-character password as SMTP_PASSWORD
    
    Environment Variables:
    - SMTP_USER: your-email@gmail.com
    - SMTP_PASSWORD: your-16-char-app-password
    """
    
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        self.from_name = settings.SMTP_FROM_NAME
        self.frontend_url = settings.FRONTEND_URL
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(self.user and self.password)
    
    def _create_message(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> MIMEMultipart:
        """Create email message with HTML and plain text versions"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email
        
        # Plain text version (fallback)
        if text_content:
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)
        
        # HTML version (preferred)
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        return message
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email via Gmail SMTP.
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("Email service not configured. Set SMTP_USER and SMTP_PASSWORD.")
            return False
        
        try:
            message = self._create_message(to_email, subject, html_content, text_content)
            
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()  # Enable TLS
                server.login(self.user, self.password)
                server.sendmail(self.from_email, to_email, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed. Check your Gmail App Password: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            return False
    
    def generate_verification_token(self) -> str:
        """Generate a secure random token for email verification"""
        return secrets.token_urlsafe(32)
    
    def get_verification_expiry(self) -> datetime:
        """Get the expiry datetime for verification token"""
        return datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)
    
    def send_verification_email(
        self,
        to_email: str,
        user_name: str,
        verification_token: str
    ) -> bool:
        """Send email verification link to user"""
        
        verification_url = f"{self.frontend_url}/verify-email.html?token={verification_token}"
        
        subject = "Verify your MFHelper account"
        
        html_content = VERIFICATION_EMAIL_TEMPLATE.render(
            user_name=user_name or "there",
            verification_url=verification_url,
            expire_hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS,
            app_name=settings.APP_NAME
        )
        
        text_content = f"""
Hi {user_name or 'there'},

Welcome to MFHelper! Please verify your email address by clicking the link below:

{verification_url}

This link will expire in {settings.EMAIL_VERIFICATION_EXPIRE_HOURS} hours.

If you didn't create an account, you can safely ignore this email.

Best regards,
The MFHelper Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """Send password reset link to user"""
        
        reset_url = f"{self.frontend_url}/reset-password.html?token={reset_token}"
        
        subject = "Reset your MFHelper password"
        
        html_content = PASSWORD_RESET_EMAIL_TEMPLATE.render(
            user_name=user_name or "there",
            reset_url=reset_url,
            expire_hours=1,  # Password reset tokens expire in 1 hour
            app_name=settings.APP_NAME
        )
        
        text_content = f"""
Hi {user_name or 'there'},

You requested to reset your MFHelper password. Click the link below:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

Best regards,
The MFHelper Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_welcome_email(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """Send welcome email after verification"""
        
        subject = "Welcome to MFHelper! 🎉"
        
        html_content = WELCOME_EMAIL_TEMPLATE.render(
            user_name=user_name or "there",
            dashboard_url=f"{self.frontend_url}/dashboard.html",
            app_name=settings.APP_NAME
        )
        
        text_content = f"""
Hi {user_name or 'there'},

Welcome to MFHelper! Your email has been verified and your account is ready.

Start managing your mutual fund portfolio:
{self.frontend_url}/dashboard.html

Best regards,
The MFHelper Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)


# Email Templates (Jinja2)
VERIFICATION_EMAIL_TEMPLATE = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 40px;">
        <!-- Logo -->
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #7FC04C; margin: 0; font-size: 28px;">{{ app_name }}</h1>
        </div>
        
        <!-- Content -->
        <div style="color: #333333;">
            <h2 style="color: #333333; margin-bottom: 20px;">Verify your email address</h2>
            
            <p style="font-size: 16px; line-height: 1.6;">
                Hi {{ user_name }},
            </p>
            
            <p style="font-size: 16px; line-height: 1.6;">
                Welcome to {{ app_name }}! Please verify your email address by clicking the button below:
            </p>
            
            <!-- CTA Button -->
            <div style="text-align: center; margin: 40px 0;">
                <a href="{{ verification_url }}" 
                   style="background-color: #7FC04C; color: #ffffff; padding: 14px 40px; 
                          text-decoration: none; border-radius: 8px; font-size: 16px; 
                          font-weight: 600; display: inline-block;">
                    Verify Email Address
                </a>
            </div>
            
            <p style="font-size: 14px; color: #666666; line-height: 1.6;">
                This link will expire in {{ expire_hours }} hours.
            </p>
            
            <p style="font-size: 14px; color: #666666; line-height: 1.6;">
                If the button doesn't work, copy and paste this link into your browser:
                <br>
                <a href="{{ verification_url }}" style="color: #7FC04C; word-break: break-all;">
                    {{ verification_url }}
                </a>
            </p>
            
            <hr style="border: none; border-top: 1px solid #eeeeee; margin: 30px 0;">
            
            <p style="font-size: 12px; color: #999999; line-height: 1.6;">
                If you didn't create an account with {{ app_name }}, you can safely ignore this email.
            </p>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; margin-top: 40px; color: #999999; font-size: 12px;">
            <p>&copy; 2026 {{ app_name }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
""")

PASSWORD_RESET_EMAIL_TEMPLATE = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 40px;">
        <!-- Logo -->
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #7FC04C; margin: 0; font-size: 28px;">{{ app_name }}</h1>
        </div>
        
        <!-- Content -->
        <div style="color: #333333;">
            <h2 style="color: #333333; margin-bottom: 20px;">Reset your password</h2>
            
            <p style="font-size: 16px; line-height: 1.6;">
                Hi {{ user_name }},
            </p>
            
            <p style="font-size: 16px; line-height: 1.6;">
                We received a request to reset your password. Click the button below to create a new password:
            </p>
            
            <!-- CTA Button -->
            <div style="text-align: center; margin: 40px 0;">
                <a href="{{ reset_url }}" 
                   style="background-color: #7FC04C; color: #ffffff; padding: 14px 40px; 
                          text-decoration: none; border-radius: 8px; font-size: 16px; 
                          font-weight: 600; display: inline-block;">
                    Reset Password
                </a>
            </div>
            
            <p style="font-size: 14px; color: #666666; line-height: 1.6;">
                This link will expire in {{ expire_hours }} hour(s).
            </p>
            
            <p style="font-size: 14px; color: #666666; line-height: 1.6;">
                If the button doesn't work, copy and paste this link into your browser:
                <br>
                <a href="{{ reset_url }}" style="color: #7FC04C; word-break: break-all;">
                    {{ reset_url }}
                </a>
            </p>
            
            <hr style="border: none; border-top: 1px solid #eeeeee; margin: 30px 0;">
            
            <p style="font-size: 12px; color: #999999; line-height: 1.6;">
                If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.
            </p>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; margin-top: 40px; color: #999999; font-size: 12px;">
            <p>&copy; 2026 {{ app_name }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
""")

WELCOME_EMAIL_TEMPLATE = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 40px;">
        <!-- Logo -->
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #7FC04C; margin: 0; font-size: 28px;">{{ app_name }}</h1>
        </div>
        
        <!-- Content -->
        <div style="color: #333333;">
            <h2 style="color: #333333; margin-bottom: 20px;">Welcome to {{ app_name }}! 🎉</h2>
            
            <p style="font-size: 16px; line-height: 1.6;">
                Hi {{ user_name }},
            </p>
            
            <p style="font-size: 16px; line-height: 1.6;">
                Your email has been verified and your account is ready! Start managing your mutual fund portfolio today.
            </p>
            
            <h3 style="color: #333333; margin-top: 30px;">What you can do:</h3>
            <ul style="font-size: 16px; line-height: 1.8; color: #555555;">
                <li>📊 Upload your CAS statement to import your portfolio</li>
                <li>📈 Track performance with real-time NAV updates</li>
                <li>🔍 Analyze fund overlap and diversification</li>
                <li>🎯 Plan your financial goals</li>
            </ul>
            
            <!-- CTA Button -->
            <div style="text-align: center; margin: 40px 0;">
                <a href="{{ dashboard_url }}" 
                   style="background-color: #7FC04C; color: #ffffff; padding: 14px 40px; 
                          text-decoration: none; border-radius: 8px; font-size: 16px; 
                          font-weight: 600; display: inline-block;">
                    Go to Dashboard
                </a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #eeeeee; margin: 30px 0;">
            
            <p style="font-size: 14px; color: #666666; line-height: 1.6;">
                Need help? Just reply to this email and we'll be happy to assist.
            </p>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; margin-top: 40px; color: #999999; font-size: 12px;">
            <p>&copy; 2026 {{ app_name }}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
""")


# Singleton instance
email_service = EmailService()
