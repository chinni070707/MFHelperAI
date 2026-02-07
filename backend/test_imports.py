"""Test script to identify which import is hanging"""
import sys
print("Starting import test...", flush=True)

print("1. Testing config import...", flush=True)
from app.config import settings
print("[OK] Config imported", flush=True)

print("2. Testing database import...", flush=True)
from app.database import engine, Base
print("[OK] Database imported", flush=True)

print("3. Testing logger import...", flush=True)
from app.utils.logger import setup_logging
print("[OK] Logger imported", flush=True)

print("4. Testing sentry import...", flush=True)
from app.utils.sentry import init_sentry
print("[OK] Sentry imported", flush=True)

print("5. Testing cache import...", flush=True)
from app.utils.cache import cache
print("[OK] Cache imported", flush=True)

print("6. Testing rate limiter import...", flush=True)
from app.middleware.rate_limiter import limiter
print("[OK] Rate limiter imported", flush=True)

print("7. Testing routes import...", flush=True)
from app.routes import portfolio
print("[OK] Portfolio route imported", flush=True)

from app.routes import upload
print("[OK] Upload route imported", flush=True)

from app.routes import analytics
print("[OK] Analytics route imported", flush=True)

from app.routes import auth
print("[OK] Auth route imported", flush=True)

from app.routes import ai
print("[OK] AI route imported", flush=True)

print("\n[SUCCESS] All imports successful!", flush=True)
