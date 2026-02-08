"""
Authentication Routes - User registration, login, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional
import logging
from datetime import datetime, timedelta
from authlib.integrations.starlette_client import OAuth
import httpx

from app.database import get_db
from app.models.models import User, UserSettings
from app.models.user_leads import UserLead
from app.schemas import UserCreate, UserLogin, UserResponse, Token, UserSettingsResponse, UserSettingsUpdate, PasswordChange, DeleteAccountRequest
from app.utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user
)
from app.middleware.rate_limiter import limiter
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# OAuth Configuration
oauth = OAuth()

# Register Google OAuth
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Rate limit: 5 registrations per minute
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
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
    
    # Track user lead for marketing
    try:
        user_lead = UserLead(
            email=new_user.email,
            phone=new_user.phone,
            name=new_user.full_name,
            source=user_data.source if hasattr(user_data, 'source') else 'direct_signup',
            signup_date=func.now(),
            is_verified=False,
            is_active=True
        )
        db.add(user_lead)
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to create user lead: {str(e)}")
    
    # Create default settings for user
    default_settings = UserSettings(user_id=new_user.id)
    db.add(default_settings)
    db.commit()
    
    logger.info(f"User registered successfully: {new_user.email} (ID: {new_user.id})")
    
    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }


@router.post("/check-email")
@limiter.limit("20/minute")
async def check_email(request: Request, db: Session = Depends(get_db)):
    """Check if email exists (for UX purposes)"""
    try:
        data = await request.json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return {"exists": False, "message": "Email required"}
        
        user = db.query(User).filter(User.email == email).first()
        return {
            "exists": bool(user),
            "message": "User found" if user else "No account with this email"
        }
    except Exception as e:
        logger.error(f"Error checking email: {e}")
        return {"exists": False, "message": "Error checking email"}


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")  # Rate limit: 10 login attempts per minute
async def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    logger.info(f"Login attempt for email: {credentials.email}")
    
    # Constants for lockout
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # Find user by email (email is already normalized via schema validator)
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        logger.warning(f"Login failed: User not found - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={
                "WWW-Authenticate": "Bearer",
                "X-Auth-Hint": "signup"  # Hint for frontend to suggest signup
            },
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining_minutes = int((user.locked_until - datetime.utcnow()).total_seconds() / 60) + 1
        logger.warning(f"Login failed: Account locked - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account temporarily locked. Try again in {remaining_minutes} minutes.",
            headers={"X-Auth-Hint": "locked"},
        )
    
    # Clear lockout if expired
    if user.locked_until and user.locked_until <= datetime.utcnow():
        user.locked_until = None
        user.failed_login_attempts = 0
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        # Track failed attempt
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        
        # Lock account after too many attempts
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            db.commit()
            logger.warning(f"Account locked due to too many failed attempts: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Too many failed attempts. Account locked for {LOCKOUT_DURATION_MINUTES} minutes.",
                headers={"X-Auth-Hint": "locked"},
            )
        
        db.commit()
        remaining_attempts = MAX_FAILED_ATTEMPTS - user.failed_login_attempts
        logger.warning(f"Login failed: Invalid password - {credentials.email} ({remaining_attempts} attempts left)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect email or password. {remaining_attempts} attempts remaining.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login failed: Inactive user - {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Successful login - reset failed attempts and update last login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
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


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password (requires current password)"""
    logger.info(f"Password change attempt for user: {current_user.email}")
    
    # OAuth users can't change password this way
    if current_user.oauth_provider and not current_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth users cannot change password. Please use your OAuth provider."
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        logger.warning(f"Password change failed: Invalid current password - {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Don't allow same password
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    logger.info(f"Password changed successfully: {current_user.email}")
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout endpoint - primarily for audit/tracking.
    Frontend should clear stored tokens.
    For JWT, actual invalidation requires token blacklisting (not implemented).
    """
    logger.info(f"User logged out: {current_user.email} (ID: {current_user.id})")
    return {"message": "Logged out successfully"}


@router.delete("/me")
async def delete_account(
    delete_request: DeleteAccountRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete user account permanently"""
    logger.info(f"Account deletion request for user: {current_user.email}")
    
    # Verify confirmation text
    if delete_request.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please type 'DELETE' to confirm account deletion"
        )
    
    # OAuth users only need confirmation, password users need password verification
    if current_user.hashed_password:
        if not verify_password(delete_request.password, current_user.hashed_password):
            logger.warning(f"Account deletion failed: Invalid password - {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password is incorrect"
            )
    
    user_email = current_user.email
    user_id = current_user.id
    
    # Delete user (cascade will delete related records)
    db.delete(current_user)
    db.commit()
    
    logger.info(f"Account deleted successfully: {user_email} (ID: {user_id})")
    return {"message": "Account deleted successfully"}


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

@router.post("/leads/capture")
@limiter.limit("10/hour")
async def capture_lead(
    request: Request,
    response: Response,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    source: str = "unknown",
    db: Session = Depends(get_db)
):
    """
    Capture user email/phone for marketing (before full signup)
    Used for export gates, timed popups, etc.
    """
    if not email and not phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or phone is required"
        )
    
    try:
        # Check if lead already exists
        existing_lead = None
        if email:
            existing_lead = db.query(UserLead).filter(UserLead.email == email).first()
        elif phone:
            existing_lead = db.query(UserLead).filter(UserLead.phone == phone).first()
        
        if existing_lead:
            # Update interaction count and last active
            existing_lead.interaction_count += 1
            existing_lead.last_active = func.now()
            db.commit()
            
            return {
                "success": True,
                "message": "Lead updated",
                "lead_id": existing_lead.id
            }
        
        # Create new lead
        new_lead = UserLead(
            email=email,
            phone=phone,
            source=source,
            signup_date=func.now(),
            last_active=func.now(),
            interaction_count=1,
            is_active=True,
            is_verified=False
        )
        
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
        
        logger.info(f"New lead captured: {email or phone} from {source}")
        
        return {
            "success": True,
            "message": "Lead captured successfully",
            "lead_id": new_lead.id
        }
        
    except Exception as e:
        logger.error(f"Error capturing lead: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to capture lead"
        )


# ============================================================================
# Google OAuth Routes
# ============================================================================

@router.get("/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured"
        )
    
    redirect_uri = settings.GOOGLE_REDIRECT_URI or f"{request.base_url}api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            # Fetch user info manually if not in token
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {token["access_token"]}'}
                )
                user_info = response.json()
        
        email = user_info.get('email')
        google_id = user_info.get('sub') or user_info.get('id')
        full_name = user_info.get('name')
        picture = user_info.get('picture')
        email_verified = user_info.get('email_verified', False)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Update existing user with Google info if not already set
            if not user.oauth_provider:
                user.oauth_provider = 'google'
                user.oauth_id = google_id
                user.profile_picture_url = picture
                user.is_verified = email_verified
            
            # Update profile picture if changed
            if picture and user.profile_picture_url != picture:
                user.profile_picture_url = picture
            
            db.commit()
            logger.info(f"Existing user logged in via Google: {email}")
        else:
            # Create new user
            user = User(
                email=email,
                full_name=full_name,
                oauth_provider='google',
                oauth_id=google_id,
                profile_picture_url=picture,
                is_active=True,
                is_verified=email_verified,
                hashed_password=None  # No password for OAuth users
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create default settings
            default_settings = UserSettings(user_id=user.id)
            db.add(default_settings)
            db.commit()
            
            # Track user lead
            try:
                user_lead = UserLead(
                    email=user.email,
                    name=user.full_name,
                    source='google_oauth',
                    signup_date=func.now(),
                    is_verified=email_verified,
                    is_active=True
                )
                db.add(user_lead)
                db.commit()
            except Exception as e:
                logger.warning(f"Failed to create user lead: {str(e)}")
            
            logger.info(f"New user registered via Google: {email}")
        
        # Create JWT token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Redirect to frontend with token
        frontend_url = request.base_url.replace('/api/auth/google/callback', '')
        redirect_url = f"{frontend_url}dashboard.html?token={access_token}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        # Redirect to login page with error
        error_url = f"{request.base_url}login.html?error=oauth_failed"
        return RedirectResponse(url=error_url)


@router.post("/google/verify")
async def google_verify_token(token: str, db: Session = Depends(get_db)):
    """Verify Google ID token (for Google Sign-In JavaScript SDK)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://oauth2.googleapis.com/tokeninfo?id_token={token}'
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            user_info = response.json()
            
            # Verify audience (client ID)
            if user_info.get('aud') != settings.GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token audience"
                )
            
            email = user_info.get('email')
            google_id = user_info.get('sub')
            full_name = user_info.get('name')
            picture = user_info.get('picture')
            email_verified = user_info.get('email_verified') == 'true'
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by Google"
                )
            
            # Check if user exists
            user = db.query(User).filter(User.email == email).first()
            
            if user:
                # Update existing user
                if not user.oauth_provider:
                    user.oauth_provider = 'google'
                    user.oauth_id = google_id
                    user.profile_picture_url = picture
                    user.is_verified = email_verified
                
                if picture and user.profile_picture_url != picture:
                    user.profile_picture_url = picture
                
                db.commit()
                logger.info(f"Existing user logged in via Google token: {email}")
            else:
                # Create new user
                user = User(
                    email=email,
                    full_name=full_name,
                    oauth_provider='google',
                    oauth_id=google_id,
                    profile_picture_url=picture,
                    is_active=True,
                    is_verified=email_verified,
                    hashed_password=None
                )
                
                db.add(user)
                db.commit()
                db.refresh(user)
                
                # Create default settings
                default_settings = UserSettings(user_id=user.id)
                db.add(default_settings)
                db.commit()
                
                logger.info(f"New user registered via Google token: {email}")
            
            # Create JWT token
            access_token = create_access_token(data={"sub": str(user.id)})
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "profile_picture_url": user.profile_picture_url
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify Google token"
        )


