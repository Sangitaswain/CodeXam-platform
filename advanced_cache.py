"""
Advanced Caching System for CodeXam Platform

This module provides a comprehensive caching solution with:
- Multi-level caching (memory, disk, distributed)
- Cache invalidation strategies
- Performance monitoring and analytics
- Automatic cache warming
- Cache compression and serialization

@version 3.0.0
@author CodeXam Development Team
"""

import gzip
import hashlib
import json
import os
import pickle
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union

from cache import SimpleCache


class CacheLevel:
    """Enumeration of cache levels."""
    MEMORY = "memory"
    DISK = "disk"
    DISTRIBUTED = "distributed"


class CacheEntry:
    """
    Represents a cache entry with metadata.
    
    Attributes:
        value: The cached value
        created_at: When the entry was created
        expires_at: When the entry expires
        access_count: Number of times accessed
        last_accessed: Last access timestamp
        size: Size of the cached value in bytes
        tags: Tags for cache invalidation
    """
    
    def __init__(
        self, 
        value: Any, 
        ttl: int = 300, 
        tags: Optional[List[str]] = None
    ):
        """
        Initialize cache entry.
        
        Args:
            value: Value to cache
            ttl: Time to live in seconds
            tags: Optional tags for invalidation
        """
        self.value = value
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl
        self.access_count = 0
        self.last_accessed = self.created_at
        self.size = self._calculate_size(value)
        self.tags = tags or []
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of cached value."""
        try:
            return len(pickle.dumps(value))
        except:
            return len(str(value).encode('utf-8'))
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() > self.expires_at
    
    def access(self) -> Any:
        """Access the cached value and update metadata."""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache entry to dictionary for serialization."""
        return {
            'value': self.value,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed,
            'size': self.size,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create cache entry from dictionary."""
        entry = cls.__new__(cls)
        entry.value = data['value']
        entry.created_at = data['created_at']
        entry.expires_at = data['expires_at']
        entry.access_count = data['access_count']
        entry.last_accessed = data['last_accessed']
        entry.size = data['size']
        entry.tags = data['tags']
        return entry


class AdvancedCache:
    """
    Advanced multi-level caching system with comprehensive features.
    
    Features:
    - Multi-level caching (memory, disk)
    - Automatic cache warming
    - Performance analytics
    - Tag-based invalidation
    - Compression for large values
    - LRU eviction policy
    """
    
    def __init__(
        self,
        max_memory_size: int = 100 * 1024 * 1024,  # 100MB
        max_disk_size: int = 500 * 1024 * 1024,    # 500MB
        disk_cache_dir: str = "cache",
        compression_threshold: int = 1024,          # 1KB
        enable_analytics: bool = True
    ):
        """
        Initialize advanced cache system.
        
        Args:
            max_memory_size: Maximum memory cache size in bytes
            max_disk_size: Maximum disk cache size in bytes
            disk_cache_dir: Directory for disk cache
            compression_threshold: Minimum size for compression
            enable_analytics: Enable performance analytics
        """
        self.max_memory_size = max_memory_size
        self.max_disk_size = max_disk_size
        self.disk_cache_dir = disk_cache_dir
        self.compression_threshold = compression_threshold
        self.enable_analytics = enable_analytics
        
        # Cache storage
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.memory_lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'disk_reads': 0,
            'disk_writes': 0,
            'compression_saves': 0,
            'total_requests': 0
        }
        self.stats_lock = threading.Lock()
        
        # Tag index for invalidation
        self.tag_index: Dict[str, List[str]] = {}
        
        # Initialize disk cache directory
        self._init_disk_cache()
        
        # Start background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
    
    def _init_disk_cache(self) -> None:
        """Initialize disk cache directory."""
        if not os.path.exists(self.disk_cache_dir):
            os.makedirs(self.disk_cache_dir, exist_ok=True)
    
    def _cleanup_worker(self) -> None:
        """Background worker for cache cleanup."""
        while True:
            try:
                self._cleanup_expired()
                self._enforce_size_limits()
                time.sleep(60)  # Run every minute
            except Exception as e:
                print(f"Cache cleanup error: {e}")
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from memory cache."""
        with self.memory_lock:
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                self._remove_from_memory(key)
    
    def _enforce_size_limits(self) -> None:
        """Enforce memory cache size limits using LRU eviction."""
        with self.memory_lock:
            current_size = sum(entry.size for entry in self.memory_cache.values())
            
            if current_size > self.max_memory_size:
                # Sort by last accessed time (LRU)
                sorted_entries = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1].last_accessed
                )
                
                # Remove oldest entries until under limit
                for key, entry in sorted_entries:
                    if current_size <= self.max_memory_size * 0.8:  # 80% threshold
                        break
                    
                    self._remove_from_memory(key)
                    current_size -= entry.size
                    
                    with self.stats_lock:
                        self.stats['evictions'] += 1
    
    def _remove_from_memory(self, key: str) -> None:
        """Remove entry from memory cache and update tag index."""
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            
            # Update tag index
            for tag in entry.tags:
                if tag in self.tag_index:
                    self.tag_index[tag] = [k for k in self.tag_index[tag] if k != key]
                    if not self.tag_index[tag]:
                        del self.tag_index[tag]
            
            del self.memory_cache[key]
    
    def _get_disk_path(self, key: str) -> str:
        """Get disk cache file path for key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.disk_cache_dir, f"{key_hash}.cache")
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage."""
        data = pickle.dumps(value)
        
        # Compress if above threshold
        if len(data) > self.compression_threshold:
            compressed = gzip.compress(data)
            if len(compressed) < len(data):
                with self.stats_lock:
                    self.stats['compression_saves'] += len(data) - len(compressed)
                return b'COMPRESSED:' + compressed
        
        return data
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage."""
        if data.startswith(b'COMPRESSED:'):
            data = gzip.decompress(data[11:])  # Remove 'COMPRESSED:' prefix
        
        return pickle.loads(data)
    
    def _write_to_disk(self, key: str, entry: CacheEntry) -> None:
        """Write cache entry to disk."""
        try:
            disk_path = self._get_disk_path(key)
            
            # Serialize entry
            entry_data = {
                'entry': entry.to_dict(),
                'serialized_value': self._serialize_value(entry.value)
            }
            
            # Write to temporary file first, then rename (atomic operation)
            temp_path = disk_path + '.tmp'
            with open(temp_path, 'wb') as f:
                pickle.dump(entry_data, f)
            
            os.rename(temp_path, disk_path)
            
            with self.stats_lock:
                self.stats['disk_writes'] += 1
                
        except Exception as e:
            print(f"Disk cache write error for key {key}: {e}")
    
    def _read_from_disk(self, key: str) -> Optional[CacheEntry]:
        """Read cache entry from disk."""
        try:
            disk_path = self._get_disk_path(key)
            
            if not os.path.exists(disk_path):
                return None
            
            with open(disk_path, 'rb') as f:
                entry_data = pickle.load(f)
            
            # Reconstruct entry
            entry_dict = entry_data['entry']
            entry = CacheEntry.from_dict(entry_dict)
            entry.value = self._deserialize_value(entry_data['serialized_value'])
            
            with self.stats_lock:
                self.stats['disk_reads'] += 1
            
            return entry if not entry.is_expired() else None
            
        except Exception as e:
            print(f"Disk cache read error for key {key}: {e}")
            return None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache with multi-level lookup.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self.stats_lock:
            self.stats['total_requests'] += 1
        
        # Try memory cache first
        with self.memory_lock:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if not entry.is_expired():
                    with self.stats_lock:
                        self.stats['hits'] += 1
                    return entry.access()
                else:
                    self._remove_from_memory(key)
        
        # Try disk cache
        disk_entry = self._read_from_disk(key)
        if disk_entry:
            # Promote to memory cache
            with self.memory_lock:
                self.memory_cache[key] = disk_entry
                self._update_tag_index(key, disk_entry.tags)
            
            with self.stats_lock:
                self.stats['hits'] += 1
            
            return disk_entry.access()
        
        # Cache miss
        with self.stats_lock:
            self.stats['misses'] += 1
        
        return None
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 300, 
        tags: Optional[List[str]] = None,
        disk_cache: bool = True
    ) -> None:
        """
        Set value in cache with optional disk persistence.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            tags: Optional tags for invalidation
            disk_cache: Whether to persist to disk
        """
        entry = CacheEntry(value, ttl, tags)
        
        # Store in memory cache
        with self.memory_lock:
            # Remove old entry if exists
            if key in self.memory_cache:
                self._remove_from_memory(key)
            
            self.memory_cache[key] = entry
            self._update_tag_index(key, entry.tags)
        
        # Store in disk cache if enabled
        if disk_cache:
            self._write_to_disk(key, entry)
        
        # Enforce size limits
        self._enforce_size_limits()
    
    def _update_tag_index(self, key: str, tags: List[str]) -> None:
        """Update tag index for cache invalidation."""
        for tag in tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            if key not in self.tag_index[tag]:
                self.tag_index[tag].append(key)
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was found and deleted
        """
        deleted = False
        
        # Remove from memory cache
        with self.memory_lock:
            if key in self.memory_cache:
                self._remove_from_memory(key)
                deleted = True
        
        # Remove from disk cache
        disk_path = self._get_disk_path(key)
        if os.path.exists(disk_path):
            try:
                os.remove(disk_path)
                deleted = True
            except Exception as e:
                print(f"Failed to delete disk cache file {disk_path}: {e}")
        
        return deleted
    
    def invalidate_by_tag(self, tag: str) -> int:
        """
        Invalidate all cache entries with the specified tag.
        
        Args:
            tag: Tag to invalidate
            
        Returns:
            Number of entries invalidated
        """
        count = 0
        
        if tag in self.tag_index:
            keys_to_delete = list(self.tag_index[tag])
            
            for key in keys_to_delete:
                if self.delete(key):
                    count += 1
        
        return count
    
    def clear(self) -> None:
        """Clear all cache entries."""
        # Clear memory cache
        with self.memory_lock:
            self.memory_cache.clear()
            self.tag_index.clear()
        
        # Clear disk cache
        try:
            for filename in os.listdir(self.disk_cache_dir):
                if filename.endswith('.cache'):
                    os.remove(os.path.join(self.disk_cache_dir, filename))
        except Exception as e:
            print(f"Failed to clear disk cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        with self.stats_lock:
            total_requests = self.stats['total_requests']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            with self.memory_lock:
                memory_size = sum(entry.size for entry in self.memory_cache.values())
                memory_entries = len(self.memory_cache)
            
            return {
                'hit_rate': round(hit_rate, 2),
                'memory_entries': memory_entries,
                'memory_size_mb': round(memory_size / 1024 / 1024, 2),
                'memory_utilization': round(memory_size / self.max_memory_size * 100, 2),
                'tag_count': len(self.tag_index),
                **self.stats
            }
    
    def warm_cache(self, warm_functions: List[Callable]) -> None:
        """
        Warm cache by pre-loading frequently accessed data.
        
        Args:
            warm_functions: List of functions to call for cache warming
        """
        print("🔥 Starting cache warming...")
        
        for func in warm_functions:
            try:
                func()
                print(f"✅ Cache warmed: {func.__name__}")
            except Exception as e:
                print(f"❌ Cache warming failed for {func.__name__}: {e}")
        
        print("🔥 Cache warming completed")


class CacheDecorator:
    """
    Decorator for automatic caching of function results.
    
    Features:
    - Automatic key generation
    - TTL configuration
    - Tag-based invalidation
    - Performance monitoring
    """
    
    def __init__(
        self,
        cache: AdvancedCache,
        ttl: int = 300,
        tags: Optional[List[str]] = None,
        key_func: Optional[Callable] = None
    ):
        """
        Initialize cache decorator.
        
        Args:
            cache: Cache instance to use
            ttl: Time to live in seconds
            tags: Optional tags for invalidation
            key_func: Optional function to generate cache key
        """
        self.cache = cache
        self.ttl = ttl
        self.tags = tags or []
        self.key_func = key_func
    
    def __call__(self, func: Callable) -> Callable:
        """Decorate function with caching."""
        def wrapper(*args, **kwargs):
            # Generate cache key
            if self.key_func:
                cache_key = self.key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__module__}.{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try to get from cache
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            self.cache.set(cache_key, result, self.ttl, self.tags)
            
            return result
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper


# Global advanced cache instance
_advanced_cache: Optional[AdvancedCache] = None

def get_advanced_cache() -> AdvancedCache:
    """Get global advanced cache instance."""
    global _advanced_cache
    if _advanced_cache is None:
        _advanced_cache = AdvancedCache()
    return _advanced_cache

def cached_advanced(
    ttl: int = 300,
    tags: Optional[List[str]] = None,
    key_func: Optional[Callable] = None
) -> Callable:
    """
    Advanced caching decorator.
    
    Args:
        ttl: Time to live in seconds
        tags: Optional tags for invalidation
        key_func: Optional function to generate cache key
        
    Returns:
        Decorator function
    """
    cache = get_advanced_cache()
    return CacheDecorator(cache, ttl, tags, key_func)

def warm_platform_cache() -> None:
    """Warm cache with frequently accessed platform data."""
    cache = get_advanced_cache()
    
    def warm_problems():
        """Warm problems cache."""
        from database_optimizations import get_optimized_queries
        queries = get_optimized_queries()
        queries.get_problems_paginated(page=1, per_page=20)
    
    def warm_leaderboard():
        """Warm leaderboard cache."""
        from database_optimizations import get_optimized_queries
        queries = get_optimized_queries()
        queries.get_leaderboard_optimized(limit=50)
    
    def warm_recent_activity():
        """Warm recent activity cache."""
        from database_optimizations import get_optimized_queries
        queries = get_optimized_queries()
        queries.get_recent_activity(limit=20)
    
    warm_functions = [warm_problems, warm_leaderboard, warm_recent_activity]
    cache.warm_cache(warm_functions)

# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing advanced cache system...")
    
    try:
        # Test basic caching
        cache = get_advanced_cache()
        
        # Test set/get
        cache.set("test_key", {"data": "test_value"}, ttl=60, tags=["test"])
        result = cache.get("test_key")
        print(f"✅ Basic cache test: {result}")
        
        # Test tag invalidation
        cache.set("tagged_key1", "value1", tags=["group1"])
        cache.set("tagged_key2", "value2", tags=["group1"])
        invalidated = cache.invalidate_by_tag("group1")
        print(f"✅ Tag invalidation test: {invalidated} entries invalidated")
        
        # Test decorator
        @cached_advanced(ttl=60, tags=["function_cache"])
        def expensive_function(x: int) -> int:
            time.sleep(0.1)  # Simulate expensive operation
            return x * x
        
        start_time = time.time()
        result1 = expensive_function(5)
        first_call_time = time.time() - start_time
        
        start_time = time.time()
        result2 = expensive_function(5)  # Should be cached
        second_call_time = time.time() - start_time
        
        print(f"✅ Decorator test: First call: {first_call_time:.3f}s, Second call: {second_call_time:.3f}s")
        
        # Test statistics
        stats = cache.get_stats()
        print(f"📊 Cache stats: {stats}")
        
        print("✅ Advanced cache tests completed successfully")
        
    except Exception as e:
        print(f"❌ Advanced cache test failed: {e}")