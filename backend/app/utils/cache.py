"""
Redis Caching Utility for MFHelper
Provides decorators and functions for caching frequently accessed data
"""
import redis
import json
import logging
from functools import wraps
from typing import Optional, Any, Callable
from datetime import timedelta

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis client
redis_client: Optional[redis.Redis] = None

if settings.REDIS_URL:
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        # Test connection
        redis_client.ping()
        logger.info(f"[OK] Redis connected: {settings.REDIS_URL}")
    except Exception as e:
        logger.warning(f"[WARN] Redis connection failed: {e}. Caching disabled.")
        redis_client = None
else:
    logger.info("Redis URL not configured. Caching disabled.")


class CacheManager:
    """
    Cache manager with helper methods for common caching patterns
    """
    
    @staticmethod
    def is_available() -> bool:
        """Check if Redis is available"""
        return redis_client is not None
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        if not redis_client:
            return None
        
        try:
            value = redis_client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache GET error for {key}: {e}")
            return None
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 1 hour)
        """
        if not redis_client:
            return False
        
        try:
            redis_client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value, default=str)  # default=str handles datetime
            )
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache SET error for {key}: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from cache"""
        if not redis_client:
            return False
        
        try:
            redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache DELETE error for {key}: {e}")
            return False
    
    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Redis key pattern (e.g., "user:123:*")
        
        Returns:
            Number of keys deleted
        """
        if not redis_client:
            return 0
        
        try:
            keys = redis_client.keys(pattern)
            if keys:
                deleted = redis_client.delete(*keys)
                logger.info(f"Cache DELETE pattern '{pattern}': {deleted} keys")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache DELETE pattern error for {pattern}: {e}")
            return 0
    
    @staticmethod
    def get_stats() -> dict:
        """Get cache statistics"""
        if not redis_client:
            return {"status": "unavailable"}
        
        try:
            info = redis_client.info('stats')
            return {
                "status": "connected",
                "hits": info.get('keyspace_hits', 0),
                "misses": info.get('keyspace_misses', 0),
                "hit_rate": f"{info.get('keyspace_hits', 0) / (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)) * 100:.1f}%"
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"status": "error", "message": str(e)}


def cached(key_prefix: str, ttl: int = 3600):
    """
    Decorator to cache function results
    
    Usage:
        @cached(key_prefix="fund", ttl=3600)
        def get_fund_by_id(fund_id: int):
            # Expensive database query
            return fund_data
    
    Args:
        key_prefix: Prefix for cache key (e.g., "fund", "portfolio")
        ttl: Time to live in seconds (default: 1 hour)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip caching if Redis is unavailable
            if not CacheManager.is_available():
                return func(*args, **kwargs)
            
            # Generate cache key from function name and arguments
            # Format: prefix:funcname:arg1:arg2:kwkey=kwval
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = CacheManager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheManager.set(cache_key, result, ttl=ttl)
            return result
        
        return wrapper
    return decorator


def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a user"""
    patterns = [
        f"portfolio:*:{user_id}:*",
        f"holdings:*:{user_id}:*",
        f"user:*:{user_id}:*",
    ]
    total_deleted = 0
    for pattern in patterns:
        total_deleted += CacheManager.delete_pattern(pattern)
    
    logger.info(f"Invalidated {total_deleted} cache entries for user {user_id}")
    return total_deleted


def invalidate_fund_cache(fund_id: Optional[int] = None, scheme_code: Optional[str] = None):
    """Invalidate cache entries for a specific fund or all funds"""
    if fund_id:
        pattern = f"fund:*:{fund_id}:*"
    elif scheme_code:
        pattern = f"fund:*:{scheme_code}:*"
    else:
        pattern = "fund:*"
    
    deleted = CacheManager.delete_pattern(pattern)
    logger.info(f"Invalidated {deleted} cache entries for fund pattern '{pattern}'")
    return deleted


# Convenience instances
cache = CacheManager()
