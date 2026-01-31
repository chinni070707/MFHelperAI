"""
Pydantic Schemas for API Request/Response
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    pan: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# User Settings Schemas
class UserSettingsBase(BaseModel):
    theme: Optional[str] = "light"
    language: Optional[str] = "en"
    currency: Optional[str] = "INR"
    date_format: Optional[str] = "DD/MM/YYYY"
    email_notifications: Optional[bool] = True
    portfolio_alerts: Optional[bool] = True
    market_updates: Optional[bool] = False
    default_view: Optional[str] = "summary"
    show_xirr: Optional[bool] = True
    group_by: Optional[str] = "category"


class UserSettingsUpdate(UserSettingsBase):
    pass


class UserSettingsResponse(UserSettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Portfolio Schemas
class PortfolioSummary(BaseModel):
    total_invested: float
    total_current: float
    total_gain: float
    return_pct: float
    xirr: Optional[float] = None


class HoldingBase(BaseModel):
    fund_name: str
    amc: Optional[str] = None
    category: Optional[str] = None
    invested_amount: float
    current_value: float
    units: Optional[float] = None
    nav: Optional[float] = None


class HoldingResponse(HoldingBase):
    id: int
    gain_loss: float
    return_pct: float
    
    class Config:
        from_attributes = True


class PortfolioResponse(BaseModel):
    id: int
    name: str
    source: Optional[str] = None
    snapshot_date: datetime
    total_invested: float
    total_current: float
    total_gain: float
    holdings_count: int = 0
    
    class Config:
        from_attributes = True
