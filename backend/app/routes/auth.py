"""
Authentication Routes - User registration, login, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.models.models import User, UserSettings
from app.schemas import UserCreate, UserLogin, UserResponse, Token, UserSettingsResponse, UserSettingsUpdate
from app.utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    logger.info(f"Registration attempt for email: {user_data.email}")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"Registration failed: Email already exists - {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if PAN already exists
    if user_data.pan:
        existing_pan = db.query(User).filter(User.pan == user_data.pan).first()
        if existing_pan:
            logger.warning(f"Registration failed: PAN already exists - {user_data.pan}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PAN already registered"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        pan=user_data.pan,
        phone=user_data.phone,
        is_active=True,
        is_verified=False  # Email verification can be added later
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create default settings for user
    default_settings = UserSettings(user_id=new_user.id)
    db.add(default_settings)
    db.commit()
    
    logger.info(f"User registered successfully: {new_user.email} (ID: {new_user.id})")
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    logger.info(f"Login attempt for email: {credentials.email}")
    
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        logger.warning(f"Login failed: User not found - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Login failed: Invalid password - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login failed: Inactive user - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    full_name: Optional[str] = None,
    phone: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    logger.info(f"Profile update for user: {current_user.email}")
    
    if full_name is not None:
        current_user.full_name = full_name
    if phone is not None:
        current_user.phone = phone
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"Profile updated successfully: {current_user.email}")
    return current_user


@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user settings"""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not settings:
        # Create default settings if they don't exist
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_data: UserSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user settings"""
    logger.info(f"Settings update for user: {current_user.email}")
    
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    # Update settings
    update_data = settings_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    logger.info(f"Settings updated successfully: {current_user.email}")
    return settings

