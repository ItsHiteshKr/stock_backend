"""
Simple in-memory cache for stock data to avoid Yahoo Finance rate limits
Uses TTL (Time To Live) to automatically expire cached data
"""
import time
from typing import Any, Optional
from threading import Lock

class SimpleCache:
    """Thread-safe in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache = {}
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expiry = self._cache[key]
            
            # Check if expired
            if time.time() > expiry:
                del self._cache[key]
                return None
            
            return value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 120):
        """Set value in cache with TTL (default 2 minutes)"""
        with self._lock:
            expiry = time.time() + ttl_seconds
            self._cache[key] = (value, expiry)
    
    def delete(self, key: str):
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """Clear entire cache"""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self):
        """Get cache statistics"""
        with self._lock:
            total_keys = len(self._cache)
            expired_keys = 0
            current_time = time.time()
            
            for key, (value, expiry) in self._cache.items():
                if current_time > expiry:
                    expired_keys += 1
            
            return {
                "total_keys": total_keys,
                "active_keys": total_keys - expired_keys,
                "expired_keys": expired_keys
            }


# Global cache instance
stock_cache = SimpleCache()


# Cache TTL configurations (in seconds)
CACHE_TTL = {
    "live_price": 120,        # 2 minutes for live prices
    "historical": 3600,       # 1 hour for historical data
    "intraday": 60,           # 1 minute for intraday data
    "indicators": 1800,       # 30 minutes for indicators
    "search": 86400,          # 24 hours for search results
}


def get_cache_key(prefix: str, *args) -> str:
    """Generate cache key from prefix and arguments"""
    return f"{prefix}:{':'.join(str(arg) for arg in args)}"
