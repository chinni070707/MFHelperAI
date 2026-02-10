"""
MFHelper - Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
import logging


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}
    
    # Application
    APP_NAME: str = "MFHelper"
    DEBUG: bool = True  # Set to True for development, False for production
    SECRET_KEY: str = "change-this-in-production-use-env-file"
    
    # Database (using sync SQLite for simplicity)
    DATABASE_URL: str = "sqlite:///./mfhelper.db"
    # For PostgreSQL in production:
    # DATABASE_URL: str = "postgresql://user:password@localhost/mfhelper"
    
    # Redis (for caching and rate limiting)
    # Set to redis://localhost:6379/0 for local development
    # Set to redis://redis:6379/0 in Docker Compose
    REDIS_URL: Optional[str] = None  # os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT Settings
    JWT_SECRET_KEY: str = "change-this-in-production-use-env-file"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google OAuth Settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None  # e.g., http://localhost:8000/api/auth/google/callback
    
    # CAMS API (Get from CAMS after registration)
    CAMS_API_URL: str = "https://api.camsonline.com/v1"
    CAMS_API_KEY: Optional[str] = None
    CAMS_API_SECRET: Optional[str] = None
    
    # KFintech API
    KFINTECH_API_URL: str = "https://api.kfintech.com/v1"
    KFINTECH_API_KEY: Optional[str] = None
    KFINTECH_API_SECRET: Optional[str] = None
    
    # MFU API
    MFU_API_URL: str = "https://api.mfuindia.com/v1"
    MFU_USER_ID: Optional[str] = None
    MFU_PASSWORD: Optional[str] = None
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = [".xlsx", ".xls", ".csv", ".pdf"]
    UPLOAD_DIR: str = "./uploads"
    
    # Email Settings (Gmail SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None  # Your Gmail address
    SMTP_PASSWORD: Optional[str] = None  # Gmail App Password (not your regular password)
    SMTP_FROM_EMAIL: Optional[str] = None  # From address (defaults to SMTP_USER)
    SMTP_FROM_NAME: str = "MFHelper"
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24  # Token valid for 24 hours
    
    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:8000"  # Change in production
    
    # Fund Data
    FUND_MASTER_PATH: str = "./data/fund_master.json"
    AMC_MASTER_PATH: str = "./data/amc_master.json"


settings = Settings()

# Auto-detect environment and set DEBUG appropriately
# Force DEBUG=True only in local development (when using SQLite)
# In production (Render/PostgreSQL), respect the DEBUG env var
if settings.DATABASE_URL.startswith("sqlite"):
    # Local development - force DEBUG=True for convenience
    settings.DEBUG = True

logger = logging.getLogger(__name__)
logger.info(f"Environment: {'Local (SQLite)' if settings.DATABASE_URL.startswith('sqlite') else 'Production'}, DEBUG={settings.DEBUG}")

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
