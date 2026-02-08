"""
MFHelper - Database Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    full_name = Column(String(255))
    pan = Column(String(10), unique=True, index=True)  # PAN for MF lookup
    phone = Column(String(15))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # OAuth fields
    oauth_provider = Column(String(50))  # 'google', 'github', etc.
    oauth_id = Column(String(255))  # Unique ID from OAuth provider
    profile_picture_url = Column(String(500))  # Profile image URL
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    holdings = relationship("Holding", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserSettings(Base):
    """User preferences and settings"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # UI Preferences
    theme = Column(String(20), default="light")  # 'light', 'dark', 'auto'
    language = Column(String(10), default="en")
    currency = Column(String(10), default="INR")
    date_format = Column(String(20), default="DD/MM/YYYY")
    
    # Notification Preferences
    email_notifications = Column(Boolean, default=True)
    portfolio_alerts = Column(Boolean, default=True)
    market_updates = Column(Boolean, default=False)
    
    # Portfolio Preferences
    default_view = Column(String(50), default="summary")  # 'summary', 'detailed', 'charts'
    show_xirr = Column(Boolean, default=True)
    group_by = Column(String(20), default="category")  # 'category', 'amc', 'none'
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="settings")


class Portfolio(Base):
    """Portfolio model - represents a snapshot of user's MF portfolio"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), default="My Portfolio")
    source = Column(String(50))  # 'excel', 'cas_pdf', 'cams_api', 'kfintech_api'
    snapshot_date = Column(DateTime, default=func.now())
    
    # Summary metrics (cached)
    total_invested = Column(Float, default=0)
    total_current = Column(Float, default=0)
    total_gain = Column(Float, default=0)
    xirr = Column(Float)
    
    # Allocation percentages
    large_cap_pct = Column(Float, default=0)
    mid_cap_pct = Column(Float, default=0)
    small_cap_pct = Column(Float, default=0)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio")
    
    # Composite Indexes for fast queries
    __table_args__ = (
        Index('idx_portfolio_user_created', 'user_id', 'created_at'),
        Index('idx_portfolio_user_snapshot', 'user_id', 'snapshot_date'),
    )


class Holding(Base):
    """Individual fund holding"""
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    
    # Fund details
    fund_name = Column(String(500), nullable=False)
    scheme_code = Column(String(20))  # AMFI code
    isin = Column(String(20))
    folio_number = Column(String(50))
    
    # AMC & Category
    amc = Column(String(100))
    category = Column(String(50))  # Large Cap, Mid Cap, Small Cap, etc.
    sub_category = Column(String(50))
    investment_style = Column(String(50))  # GARP, Momentum, Value, etc.
    
    # Financial data
    units = Column(Float, default=0)
    nav = Column(Float)
    invested_amount = Column(Float, default=0)
    current_value = Column(Float, default=0)
    gain_loss = Column(Float, default=0)
    return_pct = Column(Float, default=0)
    
    # Performance metrics
    one_year_return = Column(Float)
    three_year_return = Column(Float)
    five_year_return = Column(Float)
    alpha = Column(Float)
    beta = Column(Float)
    sharpe_ratio = Column(Float)
    down_capture = Column(Float)
    
    # Timestamps
    last_transaction_date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="holdings")
    portfolio = relationship("Portfolio", back_populates="holdings")
    
    # Composite Indexes for fast queries
    __table_args__ = (
        Index('idx_holding_portfolio_user', 'portfolio_id', 'user_id'),
        Index('idx_holding_user_created', 'user_id', 'created_at'),
        Index('idx_holding_scheme_isin', 'scheme_code', 'isin'),
        Index('idx_holding_amc', 'amc', 'category'),
    )


class Transaction(Base):
    """Fund transactions for XIRR calculation"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    holding_id = Column(Integer, ForeignKey("holdings.id"))
    
    fund_name = Column(String(500))
    folio_number = Column(String(50))
    transaction_type = Column(String(50))  # Purchase, Redemption, SIP, SWP, etc.
    transaction_date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    units = Column(Float)
    nav = Column(Float)
    
    created_at = Column(DateTime, default=func.now())
    
    # Composite Indexes for XIRR and transaction lookups
    __table_args__ = (
        Index('idx_transaction_user_date', 'user_id', 'transaction_date'),
        Index('idx_transaction_holding_date', 'holding_id', 'transaction_date'),
        Index('idx_transaction_folio_date', 'folio_number', 'transaction_date'),
    )


class FundMaster(Base):
    """Master data for mutual funds"""
    __tablename__ = "fund_master"
    
    id = Column(Integer, primary_key=True, index=True)
    scheme_code = Column(String(20), unique=True, index=True)
    isin = Column(String(20), index=True)
    scheme_name = Column(String(500))
    amc = Column(String(100))
    category = Column(String(50))
    sub_category = Column(String(50))
    investment_style = Column(String(50))
    
    # Risk metrics
    risk_grade = Column(String(20))
    expense_ratio = Column(Float)
    aum = Column(Float)
    
    # Performance
    one_year_return = Column(Float)
    three_year_return = Column(Float)
    five_year_return = Column(Float)
    
    # Additional fields
    plan_type = Column(String(20), default="Direct")  # Direct or Regular
    current_nav = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Updated timestamp
    updated_at = Column(DateTime, default=func.now())
    
    # Composite Indexes for fund search and lookups
    __table_args__ = (
        Index('idx_fund_amc_category', 'amc', 'category'),
        Index('idx_fund_scheme_isin', 'scheme_code', 'isin'),
        Index('idx_fund_active', 'is_active', 'amc'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'scheme_code': self.scheme_code,
            'scheme_name': self.scheme_name,
            'amc': self.amc,
            'category': self.category,
            'current_nav': self.current_nav,
            'plan_type': self.plan_type,
            'is_active': self.is_active
        }
    
    def to_dropdown_option(self):
        """Convert to dropdown option for UI"""
        return {
            'value': self.scheme_code,
            'label': self.scheme_name,
            'scheme_name': self.scheme_name,
            'amc': self.amc,
            'category': self.category
        }
