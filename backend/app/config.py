"""
MFHelper - Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
import sys


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
    print(f"[DEBUG] Local Development Mode: DEBUG={settings.DEBUG}", file=sys.stderr)
else:
    # Production environment - respect DEBUG from environment variable
    print(f"[DEBUG] Production Mode: DEBUG={settings.DEBUG}", file=sys.stderr)

# Debug: Print database info
print(f"[DEBUG] Database: {settings.DATABASE_URL.split('@')[0] if '@' in settings.DATABASE_URL else 'sqlite'}...", file=sys.stderr)
print(f"[DEBUG] DEBUG Type: {type(settings.DEBUG)}", file=sys.stderr)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
