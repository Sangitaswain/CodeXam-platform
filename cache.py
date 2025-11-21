"""
CodeXam Caching System

Simple in-memory caching with TTL support for improved performance.
This module provides thread-safe caching capabilities with automatic
expiration, cache statistics, and decorator-based caching for functions.
"""

import hashlib
import json
import threading
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

class SimpleCache:
    """
    Thread-safe in-memory cache with TTL support.
    
    This class provides a simple caching mechanism with automatic expiration,
    hit tracking, and cleanup capabilities. All operations are thread-safe.
    
    Attributes:
        _cache: Internal cache storage dictionary
        _lock: Thread lock for synchronization
    """
    
    def __init__(self) -> None:
        """Initialize the cache with empty storage and thread lock."""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry['expires_at'] > time.time():
                    entry['hits'] += 1
                    entry['last_accessed'] = time.time()
                    return entry['value']
                else:
                    # Expired, remove from cache
                    del self._cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Set value in cache with TTL (time to live) in seconds.
        
        Args:
            key: Cache key to store under
            value: Value to cache
            ttl: Time to live in seconds (default: 300 seconds / 5 minutes)
        """
        with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time(),
                'last_accessed': time.time(),
                'hits': 0
            }
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was found and deleted, False otherwise
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries and return count of removed items.
        
        Returns:
            Number of expired entries that were removed
        """
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for key, entry in self._cache.items():
                if entry['expires_at'] <= current_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics including entry count,
            total hits, and estimated memory usage
        """
        with self._lock:
            total_entries = len(self._cache)
            total_hits = sum(entry['hits'] for entry in self._cache.values())
            
            return {
                'total_entries': total_entries,
                'total_hits': total_hits,
                'memory_usage_estimate': sum(
                    len(str(entry['value'])) for entry in self._cache.values()
                )
            }

# Global cache instance
cache = SimpleCache()

def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_func: Optional function to generate cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_data = {
                    'func': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                }
                key_str = json.dumps(key_data, sort_keys=True, default=str)
                cache_key = hashlib.md5(key_str.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        # Add cache management methods to the decorated function
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_stats = lambda: cache.stats()
        
        return wrapper
    return decorator

def cache_key_for_user_submissions(user_name: str, limit: int = 50) -> str:
    """Generate cache key for user submissions."""
    return f"user_submissions:{user_name}:{limit}"

def cache_key_for_leaderboard(limit: int = 50) -> str:
    """Generate cache key for leaderboard."""
    return f"leaderboard:{limit}"

def cache_key_for_platform_stats() -> str:
    """Generate cache key for platform statistics."""
    return "platform_stats"

def cache_key_for_problem(problem_id: int) -> str:
    """Generate cache key for problem data."""
    return f"problem:{problem_id}"

# Cache cleanup task (should be run periodically)
def cleanup_cache():
    """Clean up expired cache entries."""
    removed_count = cache.cleanup_expired()
    if removed_count > 0:
        print(f"Cache cleanup: removed {removed_count} expired entries")
    return removed_count

# Performance monitoring
class CacheMetrics:
    """Track cache performance metrics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self._lock = threading.Lock()
    
    def record_hit(self):
        with self._lock:
            self.hits += 1
    
    def record_miss(self):
        with self._lock:
            self.misses += 1
    
    def record_set(self):
        with self._lock:
            self.sets += 1
    
    def record_delete(self):
        with self._lock:
            self.deletes += 1
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'hits': self.hits,
                'misses': self.misses,
                'sets': self.sets,
                'deletes': self.deletes,
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests
            }
    
    def reset(self):
        with self._lock:
            self.hits = 0
            self.misses = 0
            self.sets = 0
            self.deletes = 0

# Global metrics instance
metrics = CacheMetrics()

# Example usage decorators for common functions
def cache_platform_stats(func):
    """Cache platform statistics for 5 minutes."""
    return cached(ttl=300, key_func=lambda: cache_key_for_platform_stats())(func)

def cache_leaderboard(func):
    """Cache leaderboard for 2 minutes."""
    return cached(ttl=120, key_func=lambda limit=50: cache_key_for_leaderboard(limit))(func)

def cache_user_submissions(func):
    """Cache user submissions for 1 minute."""
    return cached(ttl=60, key_func=lambda user_name, limit=50: cache_key_for_user_submissions(user_name, limit))(func)

def cache_problem_data(func):
    """Cache problem data for 10 minutes."""
    return cached(ttl=600, key_func=lambda problem_id: cache_key_for_problem(problem_id))(func)

# Cache invalidation helpers
def invalidate_user_cache(user_name: str):
    """Invalidate all cache entries for a specific user."""
    # This is a simple implementation - in production you might want a more sophisticated approach
    keys_to_delete = []
    for key in cache._cache.keys():
        if f"user_submissions:{user_name}" in key:
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache.delete(key)

def invalidate_leaderboard_cache():
    """Invalidate leaderboard cache."""
    keys_to_delete = []
    for key in cache._cache.keys():
        if key.startswith("leaderboard:"):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache.delete(key)

def invalidate_platform_stats_cache():
    """Invalidate platform statistics cache."""
    cache.delete(cache_key_for_platform_stats())

# Background cache cleanup (run this periodically)
def start_cache_cleanup_task():
    """Start background task to clean up expired cache entries."""
    import threading
    import time
    
    def cleanup_worker():
        while True:
            time.sleep(300)  # Run every 5 minutes
            cleanup_cache()
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    return cleanup_thread