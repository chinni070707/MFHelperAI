"""
Email verification endpoints
Handles OTP generation, verification, and email sending
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session

from app.services.email_service import email_service
from app.services.otp_service import otp_service
from app.database import get_db
from app.models.models import User

router = APIRouter(prefix="/api/email", tags=["email"])

# Request/Response Models
class SendOTPRequest(BaseModel):
    email: EmailStr
    purpose: str = "verification"  # verification, password_reset, etc.

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
    purpose: str = "verification"

class SendTestEmailRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class FeedbackRequest(BaseModel):
    name: str
    email: EmailStr
    feedback_type: str  # bug, feature, general
    subject: str
    message: str

@router.post("/send-otp")
async def send_otp(
    request: SendOTPRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate and send OTP to email
    
    Purpose types:
    - verification: Email verification for new users
    - password_reset: Password reset request
    - login: Secure login
    """
    # Check if can resend
    resend_check = otp_service.resend_otp(request.email, request.purpose)
    if not resend_check["can_resend"]:
        raise HTTPException(
            status_code=429,
            detail=resend_check["message"]
        )
    
    # Generate OTP
    otp = otp_service.generate_otp(length=6)
    
    # Store OTP
    otp_service.store_otp(
        identifier=request.email,
        otp=otp,
        expires_in_minutes=10,
        purpose=request.purpose
    )
    
    # Send email in background
    result = await email_service.send_otp_email(
        to=request.email,
        otp=otp,
        expires_in_minutes=10
    )
    
    if result.get("status") == "sent":
        return {
            "success": True,
            "message": "OTP sent to your email",
            "expires_in": 600  # 10 minutes in seconds
        }
    elif result.get("status") == "skipped":
        # Development mode - return OTP for testing
        return {
            "success": True,
            "message": "Email service not configured - OTP shown for testing",
            "otp": otp,  # Only in development!
            "expires_in": 600
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP email"
        )

@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    """Verify OTP sent to email"""
    
    result = otp_service.verify_otp(
        identifier=request.email,
        otp=request.otp,
        purpose=request.purpose
    )
    
    if result["valid"]:
        return {
            "success": True,
            "message": result["message"],
            "metadata": result.get("metadata", {})
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=result["error"]
        )

@router.post("/send-welcome")
async def send_welcome_email(
    request: SendTestEmailRequest,
    background_tasks: BackgroundTasks
):
    """Send welcome email to new user"""
    
    name = request.name or request.email.split('@')[0]
    
    result = await email_service.send_welcome_email(
        to=request.email,
        name=name
    )
    
    if result.get("status") == "sent":
        return {
            "success": True,
            "message": "Welcome email sent"
        }
    elif result.get("status") == "skipped":
        return {
            "success": True,
            "message": "Email service not configured",
            "note": "Set RESEND_API_KEY in .env to enable emails"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send welcome email"
        )

@router.post("/send-feedback")
async def send_feedback(
    request: FeedbackRequest,
    background_tasks: BackgroundTasks
):
    """
    Receive and acknowledge user feedback
    Sends confirmation email to user
    """
    
    # Send confirmation email to user
    result = await email_service.send_feedback_confirmation(
        to=request.email,
        name=request.name,
        feedback_type=request.feedback_type
    )
    
    # TODO: Store feedback in database or send to admin email
    # For now, just log it
    print(f"""
    📧 NEW FEEDBACK RECEIVED
    ========================
    From: {request.name} ({request.email})
    Type: {request.feedback_type}
    Subject: {request.subject}
    Message: {request.message}
    ========================
    """)
    
    return {
        "success": True,
        "message": "Thank you for your feedback! We'll review it shortly."
    }

@router.post("/test-email")
async def test_email_service(
    request: SendTestEmailRequest,
    background_tasks: BackgroundTasks
):
    """
    Test email service configuration
    Sends a test email to verify setup
    """
    
    result = await email_service.send_email(
        to=request.email,
        subject="Test Email from MFHelper",
        html=f"""
        <h1>Email Service Test</h1>
        <p>Hi {request.name or 'there'},</p>
        <p>If you're seeing this, your email service is working correctly! ✅</p>
        <p>Sent from MFHelper</p>
        """
    )
    
    if result.get("status") == "sent":
        return {
            "success": True,
            "message": "Test email sent successfully",
            "email_id": result.get("data", {}).get("id")
        }
    elif result.get("status") == "skipped":
        return {
            "success": False,
            "message": "Email service not configured. Set RESEND_API_KEY in .env file.",
            "instructions": "Get API key from https://resend.com/api-keys"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Email test failed: {result.get('error', 'Unknown error')}"
        )

@router.get("/cleanup-expired")
async def cleanup_expired_otps():
    """Cleanup expired OTPs (admin endpoint)"""
    
    count = otp_service.cleanup_expired_otps()
    
    return {
        "success": True,
        "message": f"Cleaned up {count} expired OTPs"
    }
