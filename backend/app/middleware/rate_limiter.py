"""
Rate Limiting Middleware for MFHelper
Protects against brute force attacks and API abuse
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    headers_enabled=True
)

# Auth endpoints are more restrictive
auth_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10 per minute", "100 per hour"],
    storage_uri="memory://",
    headers_enabled=True
)
