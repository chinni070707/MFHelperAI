"""
Email Service using Resend
Handles OTP, verification, and transactional emails
"""
import os
from typing import Optional
from fastapi import BackgroundTasks
import httpx

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "noreply@mfhelper.com")
RESEND_API_URL = "https://api.resend.com/emails"

class EmailService:
    """Email service using Resend API"""
    
    def __init__(self):
        self.api_key = RESEND_API_KEY
        self.from_email = RESEND_FROM_EMAIL
        self.api_url = RESEND_API_URL
        
    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        reply_to: Optional[str] = None
    ) -> dict:
        """
        Send email via Resend API
        
        Args:
            to: Recipient email
            subject: Email subject
            html: HTML content
            reply_to: Reply-to email (optional)
            
        Returns:
            dict: Response from Resend API
        """
        if not self.api_key:
            print("⚠️ RESEND_API_KEY not configured - email not sent")
            return {"status": "skipped", "reason": "API key not configured"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": self.from_email,
            "to": [to],
            "subject": subject,
            "html": html
        }
        
        if reply_to:
            payload["reply_to"] = reply_to
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code in [200, 201]:
                    return {
                        "status": "sent",
                        "data": response.json()
                    }
                else:
                    return {
                        "status": "failed",
                        "error": response.text,
                        "status_code": response.status_code
                    }
        except Exception as e:
            print(f"❌ Email send failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def send_otp_email(
        self,
        to: str,
        otp: str,
        name: Optional[str] = None,
        expires_in_minutes: int = 10
    ) -> dict:
        """Send OTP verification email"""
        from .email_templates import generate_otp_email
        
        html = generate_otp_email(
            otp=otp,
            name=name or to.split('@')[0],
            expires_in_minutes=expires_in_minutes
        )
        
        return await self.send_email(
            to=to,
            subject=f"Your OTP Code: {otp}",
            html=html
        )
    
    async def send_welcome_email(
        self,
        to: str,
        name: str
    ) -> dict:
        """Send welcome email to new user"""
        from .email_templates import generate_welcome_email
        
        html = generate_welcome_email(name=name)
        
        return await self.send_email(
            to=to,
            subject="Welcome to MFHelper! 🎉",
            html=html
        )
    
    async def send_password_reset_email(
        self,
        to: str,
        reset_token: str,
        name: Optional[str] = None
    ) -> dict:
        """Send password reset email"""
        from .email_templates import generate_password_reset_email
        
        # Construct reset URL (adjust based on your frontend URL)
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        html = generate_password_reset_email(
            name=name or to.split('@')[0],
            reset_url=reset_url
        )
        
        return await self.send_email(
            to=to,
            subject="Reset Your Password - MFHelper",
            html=html
        )
    
    async def send_portfolio_update_email(
        self,
        to: str,
        name: str,
        portfolio_summary: dict
    ) -> dict:
        """Send portfolio update notification"""
        from .email_templates import generate_portfolio_update_email
        
        html = generate_portfolio_update_email(
            name=name,
            total_value=portfolio_summary.get('total_value', 0),
            total_invested=portfolio_summary.get('total_invested', 0),
            returns=portfolio_summary.get('returns', 0),
            returns_pct=portfolio_summary.get('returns_pct', 0)
        )
        
        return await self.send_email(
            to=to,
            subject="Your Portfolio Update - MFHelper",
            html=html
        )
    
    async def send_feedback_confirmation(
        self,
        to: str,
        name: str,
        feedback_type: str
    ) -> dict:
        """Send feedback confirmation email"""
        from .email_templates import generate_feedback_confirmation_email
        
        html = generate_feedback_confirmation_email(
            name=name,
            feedback_type=feedback_type
        )
        
        return await self.send_email(
            to=to,
            subject="We received your feedback - MFHelper",
            html=html
        )
    
    def send_email_background(
        self,
        background_tasks: BackgroundTasks,
        to: str,
        subject: str,
        html: str,
        reply_to: Optional[str] = None
    ):
        """
        Send email in background task
        
        Usage:
            email_service.send_email_background(
                background_tasks=background_tasks,
                to="user@example.com",
                subject="Test",
                html="<h1>Hello</h1>"
            )
        """
        background_tasks.add_task(
            self.send_email,
            to=to,
            subject=subject,
            html=html,
            reply_to=reply_to
        )

# Singleton instance
email_service = EmailService()
