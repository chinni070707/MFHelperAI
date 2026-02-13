"""
OTP (One-Time Password) Service
Generates and verifies OTPs for email/phone verification
"""
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.orm import Session

# In-memory OTP storage (for production, use Redis or database)
otp_store: Dict[str, Dict] = {}

class OTPService:
    """Service for generating and verifying OTPs"""
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """
        Generate random numeric OTP
        
        Args:
            length: Length of OTP (default: 6)
            
        Returns:
            str: Generated OTP
        """
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def store_otp(
        identifier: str,
        otp: str,
        expires_in_minutes: int = 10,
        purpose: str = "verification",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Store OTP with expiration
        
        Args:
            identifier: Email or phone number
            otp: Generated OTP
            expires_in_minutes: Expiration time in minutes
            purpose: Purpose of OTP (verification, password_reset, etc.)
            metadata: Additional metadata to store
            
        Returns:
            dict: Stored OTP data
        """
        expiry = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        otp_data = {
            "otp": otp,
            "identifier": identifier,
            "purpose": purpose,
            "expires_at": expiry,
            "attempts": 0,
            "max_attempts": 3,
            "created_at": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        # Store with composite key: identifier + purpose
        key = f"{identifier}:{purpose}"
        otp_store[key] = otp_data
        
        return otp_data
    
    @staticmethod
    def verify_otp(
        identifier: str,
        otp: str,
        purpose: str = "verification"
    ) -> Dict:
        """
        Verify OTP
        
        Args:
            identifier: Email or phone number
            otp: OTP to verify
            purpose: Purpose of OTP
            
        Returns:
            dict: Verification result
        """
        key = f"{identifier}:{purpose}"
        stored_data = otp_store.get(key)
        
        if not stored_data:
            return {
                "valid": False,
                "error": "OTP not found or expired"
            }
        
        # Check expiration
        if datetime.utcnow() > stored_data["expires_at"]:
            del otp_store[key]
            return {
                "valid": False,
                "error": "OTP expired"
            }
        
        # Check max attempts
        if stored_data["attempts"] >= stored_data["max_attempts"]:
            del otp_store[key]
            return {
                "valid": False,
                "error": "Maximum verification attempts exceeded"
            }
        
        # Verify OTP
        stored_data["attempts"] += 1
        
        if stored_data["otp"] == otp:
            # OTP valid - remove from store
            del otp_store[key]
            return {
                "valid": True,
                "message": "OTP verified successfully",
                "metadata": stored_data.get("metadata", {})
            }
        else:
            remaining_attempts = stored_data["max_attempts"] - stored_data["attempts"]
            return {
                "valid": False,
                "error": f"Invalid OTP. {remaining_attempts} attempts remaining"
            }
    
    @staticmethod
    def resend_otp(
        identifier: str,
        purpose: str = "verification"
    ) -> Dict:
        """
        Check if OTP can be resent (cooldown period)
        
        Args:
            identifier: Email or phone number
            purpose: Purpose of OTP
            
        Returns:
            dict: Resend eligibility status
        """
        key = f"{identifier}:{purpose}"
        stored_data = otp_store.get(key)
        
        if not stored_data:
            return {
                "can_resend": True,
                "message": "No active OTP found"
            }
        
        # Check if OTP was created less than 1 minute ago
        time_since_creation = datetime.utcnow() - stored_data["created_at"]
        cooldown_seconds = 60  # 1 minute cooldown
        
        if time_since_creation.total_seconds() < cooldown_seconds:
            remaining_seconds = cooldown_seconds - int(time_since_creation.total_seconds())
            return {
                "can_resend": False,
                "message": f"Please wait {remaining_seconds} seconds before requesting new OTP"
            }
        
        return {
            "can_resend": True,
            "message": "You can request a new OTP"
        }
    
    @staticmethod
    def cleanup_expired_otps():
        """Remove expired OTPs from store"""
        current_time = datetime.utcnow()
        expired_keys = [
            key for key, data in otp_store.items()
            if current_time > data["expires_at"]
        ]
        
        for key in expired_keys:
            del otp_store[key]
        
        return len(expired_keys)

# Singleton instance
otp_service = OTPService()
