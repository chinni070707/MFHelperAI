"""
Database models for fund holdings and related data
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class FundMaster(Base):
    """Master table for mutual funds"""
    __tablename__ = "fund_master"
    
    id = Column(Integer, primary_key=True, index=True)
    fund_key = Column(String(200), unique=True, index=True, nullable=False)
    fund_name = Column(String(500), nullable=False, index=True)
    amc = Column(String(200), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    isin = Column(String(50), index=True)
    scheme_code = Column(String(50), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    holdings = relationship("FundHolding", back_populates="fund", cascade="all, delete-orphan")
    sector_allocations = relationship("FundSectorAllocation", back_populates="fund", cascade="all, delete-orphan")

class FundHolding(Base):
    """Individual stock holdings in a fund"""
    __tablename__ = "fund_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("fund_master.id", ondelete="CASCADE"), nullable=False, index=True)
    stock_name = Column(String(200), nullable=False, index=True)
    weight = Column(Float, nullable=False)  # Percentage
    sector = Column(String(100), index=True)
    as_of_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    fund = relationship("FundMaster", back_populates="holdings")

class FundSectorAllocation(Base):
    """Sector-wise allocation in a fund"""
    __tablename__ = "fund_sector_allocation"
    
    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("fund_master.id", ondelete="CASCADE"), nullable=False, index=True)
    sector = Column(String(100), nullable=False, index=True)
    weight = Column(Float, nullable=False)  # Percentage
    as_of_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    fund = relationship("FundMaster", back_populates="sector_allocations")

class DataUpdateLog(Base):
    """Track data update history"""
    __tablename__ = "data_update_log"
    
    id = Column(Integer, primary_key=True, index=True)
    update_type = Column(String(100), nullable=False)  # 'full', 'incremental', 'manual'
    source = Column(String(200))  # 'amfi', 'manual', 'api'
    funds_updated = Column(Integer)
    status = Column(String(50))  # 'success', 'failed', 'partial'
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    update_metadata = Column(JSON)  # Store additional info (renamed from metadata)
