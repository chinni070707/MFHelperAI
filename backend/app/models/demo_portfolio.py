"""
Demo Portfolio Model
Stores template portfolio data for demo mode
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base


class DemoPortfolio(Base):
    """Demo portfolio holdings template"""
    __tablename__ = "demo_portfolio"

    id = Column(Integer, primary_key=True, index=True)
    scheme_name = Column(String(500), nullable=False)
    scheme_code = Column(String(50), nullable=True)
    units = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)
    current_nav = Column(Float, nullable=False)
    invested_amount = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    gain_loss = Column(Float, nullable=False)
    gain_loss_percent = Column(Float, nullable=False)
    
    # Optional fields
    amc = Column(String(200), nullable=True)
    category = Column(String(100), nullable=True)
    sub_category = Column(String(100), nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "scheme_name": self.scheme_name,
            "scheme_code": self.scheme_code,
            "units": self.units,
            "avg_cost": self.avg_cost,
            "current_nav": self.current_nav,
            "invested_amount": self.invested_amount,
            "current_value": self.current_value,
            "gain_loss": self.gain_loss,
            "gain_loss_percent": self.gain_loss_percent,
            "amc": self.amc,
            "category": self.category,
            "sub_category": self.sub_category
        }
