"""
User Leads Model
Tracks user sign-ups for customer acquisition and marketing
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base


class UserLead(Base):
    """User leads for customer acquisition tracking"""
    __tablename__ = "user_leads"

    id = Column(Integer, primary_key=True, index=True)
    
    # Contact information
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    
    # User details
    name = Column(String(200), nullable=True)
    
    # Tracking
    source = Column(String(100), nullable=True)  # demo-banner, export-gate, guest-banner, etc.
    signup_date = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    interaction_count = Column(Integer, default=1)
    
    # Marketing
    subscribed_newsletter = Column(Boolean, default=True)
    converted_to_paid = Column(Boolean, default=False)
    conversion_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "name": self.name,
            "source": self.source,
            "signup_date": self.signup_date.isoformat() if self.signup_date else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "interaction_count": self.interaction_count,
            "subscribed_newsletter": self.subscribed_newsletter,
            "is_verified": self.is_verified
        }
