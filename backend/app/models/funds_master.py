"""
Funds Master Model
Stores comprehensive mutual fund scheme information
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.sql import func
from app.database import Base


class FundMaster(Base):
    """Master list of all mutual fund schemes"""
    __tablename__ = "funds_master"

    id = Column(Integer, primary_key=True, index=True)
    
    # Scheme identifiers
    scheme_name = Column(String(500), nullable=False, index=True)
    scheme_code = Column(String(50), unique=True, index=True)
    isin = Column(String(20), nullable=True)
    
    # Fund details
    amc = Column(String(200), nullable=False, index=True)  # Asset Management Company
    category = Column(String(100), nullable=False, index=True)  # Equity, Debt, Hybrid, etc.
    sub_category = Column(String(100), nullable=True)
    
    # NAV information
    current_nav = Column(Float, nullable=True)
    nav_date = Column(DateTime(timezone=True), nullable=True)
    
    # Fund characteristics
    expense_ratio = Column(Float, nullable=True)
    aum = Column(Float, nullable=True)  # Assets Under Management (in crores)
    inception_date = Column(DateTime(timezone=True), nullable=True)
    
    # Plan type
    plan_type = Column(String(20), nullable=True)  # Direct, Regular
    option_type = Column(String(20), nullable=True)  # Growth, Dividend
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Create composite index for faster searches
    __table_args__ = (
        Index('idx_amc_category', 'amc', 'category'),
        Index('idx_scheme_name_search', 'scheme_name'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "scheme_name": self.scheme_name,
            "scheme_code": self.scheme_code,
            "isin": self.isin,
            "amc": self.amc,
            "category": self.category,
            "sub_category": self.sub_category,
            "current_nav": self.current_nav,
            "nav_date": self.nav_date.isoformat() if self.nav_date else None,
            "expense_ratio": self.expense_ratio,
            "aum": self.aum,
            "plan_type": self.plan_type,
            "option_type": self.option_type
        }
    
    def to_dropdown_option(self):
        """Simplified format for dropdown selection"""
        label = self.scheme_name
        if self.amc:
            label += f" ({self.amc})"
        if self.plan_type:
            label += f" - {self.plan_type}"
            
        return {
            "value": self.id,
            "label": label,
            "scheme_name": self.scheme_name,
            "scheme_code": self.scheme_code,
            "amc": self.amc,
            "category": self.category,
            "current_nav": self.current_nav
        }
