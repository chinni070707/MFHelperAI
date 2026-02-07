"""Test script to identify which import is hanging"""
import sys
print("Starting import test...", flush=True)

print("1. Testing config import...", flush=True)
from app.config import settings
print("✓ Config imported", flush=True)

print("2. Testing database import...", flush=True)
from app.database import engine, Base
print("✓ Database imported", flush=True)

print("3. Testing logger import...", flush=True)
from app.utils.logger import setup_logging
print("✓ Logger imported", flush=True)

print("4. Testing sentry import...", flush=True)
from app.utils.sentry import init_sentry
print("✓ Sentry imported", flush=True)

print("5. Testing cache import...", flush=True)
from app.utils.cache import cache
print("✓ Cache imported", flush=True)

print("6. Testing rate limiter import...", flush=True)
from app.middleware.rate_limiter import limiter
print("✓ Rate limiter imported", flush=True)

print("7. Testing routes import...", flush=True)
from app.routes import portfolio
print("✓ Portfolio route imported", flush=True)

from app.routes import upload
print("✓ Upload route imported", flush=True)

from app.routes import analytics
print("✓ Analytics route imported", flush=True)

from app.routes import auth
print("✓ Auth route imported", flush=True)

from app.routes import ai
print("✓ AI route imported", flush=True)

print("\n✅ All imports successful!", flush=True)
