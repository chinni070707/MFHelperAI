"""
Market data models for stock information and fund analysis
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Index, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Stock(Base):
    """Master stock data with market cap"""
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, index=True, nullable=False)  # NSE symbol
    company_name = Column(String(500), nullable=False, index=True)
    isin = Column(String(20), unique=True, index=True)
    
    # Market cap classification
    market_cap = Column(Float)  # in Crores
    market_cap_category = Column(String(20), index=True)  # 'Large', 'Mid', 'Small', 'Micro'
    
    # Sector classification
    sector = Column(String(100), index=True)
    industry = Column(String(100), index=True)
    
    # Exchange info
    exchange = Column(String(20))  # 'NSE', 'BSE'
    bse_code = Column(String(20), index=True)
    nse_symbol = Column(String(50), index=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    market_cap_history = relationship("StockMarketCapHistory", back_populates="stock", cascade="all, delete-orphan")


class StockMarketCapHistory(Base):
    """Historical market cap data for versioning"""
    __tablename__ = "stock_market_cap_history"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, index=True, nullable=False)
    
    # Market cap data
    market_cap = Column(Float, nullable=False)
    market_cap_category = Column(String(20), nullable=False)
    
    # Version tracking
    effective_date = Column(Date, nullable=False, index=True)
    snapshot_date = Column(DateTime, default=datetime.utcnow)
    
    # Source info
    source = Column(String(50))  # 'nse', 'bse', 'manual'
    
    # Index for querying by date
    __table_args__ = (
        Index('idx_stock_effective_date', 'stock_id', 'effective_date'),
    )
    
    # Relationships
    stock = relationship("Stock", back_populates="market_cap_history")


class FundHoldingSnapshot(Base):
    """Versioned fund holdings - stores historical data"""
    __tablename__ = "fund_holding_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, index=True, nullable=False)
    
    # Stock details
    stock_symbol = Column(String(50), nullable=False, index=True)
    stock_name = Column(String(200), nullable=False)
    weight = Column(Float, nullable=False)  # Percentage
    
    # Classification at time of snapshot
    market_cap = Column(Float)
    market_cap_category = Column(String(20))  # Large/Mid/Small at that time
    sector = Column(String(100))
    
    # Version tracking
    as_of_date = Column(Date, nullable=False, index=True)  # Fund factsheet date
    snapshot_date = Column(DateTime, default=datetime.utcnow)  # When we captured it
    
    # Data source
    source = Column(String(50))  # 'amfi', 'valueresearch', 'morningstar'
    
    # Index for efficient querying
    __table_args__ = (
        Index('idx_fund_as_of_date', 'fund_id', 'as_of_date'),
    )


class FundClassification(Base):
    """Pre-calculated fund classification based on holdings"""
    __tablename__ = "fund_classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, index=True, nullable=False)
    
    # Calculated allocation percentages
    large_cap_percentage = Column(Float, default=0)
    mid_cap_percentage = Column(Float, default=0)
    small_cap_percentage = Column(Float, default=0)
    
    # Top sectors
    top_sector_1 = Column(String(100))
    top_sector_1_weight = Column(Float)
    top_sector_2 = Column(String(100))
    top_sector_2_weight = Column(Float)
    top_sector_3 = Column(String(100))
    top_sector_3_weight = Column(Float)
    
    # Concentration metrics
    top_10_holdings_weight = Column(Float)  # % of portfolio in top 10 stocks
    number_of_stocks = Column(Integer)
    
    # Classification metadata
    as_of_date = Column(Date, nullable=False, index=True)
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Index for latest classification
    __table_args__ = (
        Index('idx_fund_latest_classification', 'fund_id', 'as_of_date'),
    )
