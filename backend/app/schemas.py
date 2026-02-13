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
    confirm_password: Optional[str] = None  # Optional for backwards compatibility
    accepted_terms: bool = False  # Track TOS acceptance
    
    @validator('email', pre=True)
    def normalize_email(cls, v):
        """Normalize email to lowercase"""
        if v:
            return v.strip().lower()
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate password confirmation matches"""
        if v is not None and 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    @validator('email', pre=True)
    def normalize_email(cls, v):
        """Normalize email to lowercase"""
        if v:
            return v.strip().lower()
        return v


class PasswordChange(BaseModel):
    """Schema for password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('new_password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class DeleteAccountRequest(BaseModel):
    """Schema for account deletion confirmation"""
    password: str
    confirmation: str = Field(..., description="Must be 'DELETE' to confirm")


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
    goal_planning_data: Optional[dict] = None


class UserSettingsUpdate(UserSettingsBase):
    pass


class UserSettingsResponse(UserSettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Goal Schemas
class GoalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Custom name for the goal")
    icon_type: str = Field(default="custom", description="Icon type: house, vehicle, education, marriage, vacation, business, emergency, custom, expense")
    amount: float = Field(..., gt=0, description="Goal amount in rupees")
    age: int = Field(..., gt=0, le=150, description="Age when goal is to be achieved")


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    icon_type: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    age: Optional[int] = Field(None, gt=0, le=150)


class GoalResponse(GoalBase):
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
