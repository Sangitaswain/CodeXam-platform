#!/usr/bin/env python3
"""
Database Integration Layer for CodeXam Platform

This module integrates the optimized database with enhanced caching
and performance monitoring to provide a unified high-performance
data access layer.

Version: 2.0.0
Author: CodeXam Development Team
"""

import time
import threading
import logging
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from functools import wraps
import sqlite3

# Import our custom modules
from database_optimized import OptimizedDatabase, get_optimized_db
from cache_enhanced import EnhancedCache, get_cache_manager
from performance_monitor import get_performance_monitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedDatabase:
    """Integrated database layer with caching and performance monitoring."""
    
    def __init__(self, database_path: str = 'database.db', 
                 cache_config: Dict[str, Any] = None,
                 enable_monitoring: bool = True):
        
        self.database_path = database_path
        self.enable_monitoring = enable_monitoring
        
        # Initialize optimized database
        self.db = get_optimized_db(database_path)
        
        # Initialize cache
        cache_manager = get_cache_manager()
        cache_config = cache_config or {
            'memory_size': 2000,
            'default_ttl': 600,
            'enable_statistics': True
        }
        
        try:
            self.cache = cache_manager.get_cache('main')
            if self.cache is None:
                self.cache = cache_manager.create_cache('main', **cache_config)
        except ValueError:
            # Cache already exists
            self.cache = cache_manager.get_cache('main')
        
        # Initialize performance monitoring
        if enable_monitoring:
            self.monitor = get_performance_monitor()
        else:
            self.monitor = None
        
        # Cache warming strategies
        self._setup_cache_warming()
        
        logger.info(f"Integrated database initialized: {database_path}")
    
    def _setup_cache_warming(self) -> None:
        """Setup cache warming strategies."""
        if not self.cache:
            return
        
        # Register warming strategies
        def warm_popular_problems():
            """Warm cache with popular problems."""
            try:
                problems = self.db.execute_query(
                    'SELECT * FROM problems ORDER BY view_count DESC LIMIT 20',
                    use_cache=False
                )
                
                for problem in problems:
                    cache_key = f"problem:{problem['id']}"
                    self.cache.set(
                        cache_key, 
                        dict(problem), 
                        ttl=1800,  # 30 minutes
                        tags=['problems', 'popular'],
                        priority=3
                    )
                
                logger.info(f"Warmed cache with {len(problems)} popular problems")
                
            except Exception as e:
                logger.error(f"Popular problems warming failed: {e}")
        
        def warm_leaderboard():
            """Warm cache with leaderboard data."""
            try:
                leaderboard = self.get_leaderboard(50, use_cache=False)
                
                self.cache.set(
                    'leaderboard:top50',
                    leaderboard,
                    ttl=600,  # 10 minutes
                    tags=['leaderboard', 'users'],
                    priority=2
                )
                
                logger.info("Warmed cache with leaderboard data")
                
            except Exception as e:
                logger.error(f"Leaderboard warming failed: {e}")
        
        def warm_problem_stats():
            """Warm cache with problem statistics."""
            try:
                stats = self.db.execute_query('''
                    SELECT 
                        difficulty,
                        COUNT(*) as count,
                        AVG(success_rate) as avg_success_rate
                    FROM problems 
                    GROUP BY difficulty
                ''', use_cache=False)
                
                self.cache.set(
                    'problem_stats:by_difficulty',
                    [dict(row) for row in stats],
                    ttl=3600,  # 1 hour
                    tags=['problems', 'stats'],
                    priority=2
                )
                
                logger.info("Warmed cache with problem statistics")
                
            except Exception as e:
                logger.error(f"Problem stats warming failed: {e}")
        
        # Note: Cache warming would be implemented if we had the full cache warmer
        # For now, we'll call these manually when needed
        self.warming_strategies = {
            'popular_problems': warm_popular_problems,
            'leaderboard': warm_leaderboard,
            'problem_stats': warm_problem_stats
        }
    
    def _monitor_query(self, query: str, params: tuple, execution_time: float, 
                      rows_affected: int, cache_hit: bool = False, error: str = None) -> None:
        """Monitor query performance."""
        if not self.monitor:
            return
        
        query_hash = hashlib.md5(f"{query}:{params}".encode()).hexdigest()
        
        self.monitor.collector.record_query_performance(
            query_hash=query_hash,
            query_text=query,
            execution_time=execution_time,
            rows_affected=rows_affected,
            cache_hit=cache_hit,
            error=error
        )
    
    def _get_cache_key(self, query: str, params: tuple) -> str:
        """Generate cache key for query."""
        return hashlib.md5(f"{query}:{params}".encode()).hexdigest()
    
    def _determine_cache_tags(self, query: str) -> List[str]:
        """Determine cache tags based on query content."""
        tags = []
        query_lower = query.lower()
        
        if 'problems' in query_lower:
            tags.append('problems')
        if 'submissions' in query_lower:
            tags.append('submissions')
        if 'user_stats' in query_lower:
            tags.append('users')
        if 'leaderboard' in query_lower or 'order by' in query_lower:
            tags.append('leaderboard')
        
        return tags
    
    def execute_query(self, query: str, params: tuple = (), 
                     cache_ttl: Optional[int] = None, 
                     use_cache: bool = True,
                     cache_priority: int = 1) -> List[sqlite3.Row]:
        """Execute SELECT query with integrated caching and monitoring."""
        start_time = time.time()
        cache_hit = False
        error = None
        result = []
        
        try:
            # Check cache first for SELECT queries
            if use_cache and query.strip().upper().startswith('SELECT'):
                cache_key = self._get_cache_key(query, params)
                cached_result = self.cache.get(cache_key)
                
                if cached_result is not None:
                    cache_hit = True
                    result = cached_result
                    execution_time = time.time() - start_time
                    
                    # Monitor cache hit
                    self._monitor_query(query, params, execution_time, len(result), cache_hit)
                    
                    return result
            
            # Execute query through optimized database
            result = self.db.execute_query(query, params, cache_ttl, use_cache=False)
            
            # Cache the result if it's a SELECT query
            if use_cache and query.strip().upper().startswith('SELECT') and result:
                cache_key = self._get_cache_key(query, params)
                tags = self._determine_cache_tags(query)
                
                self.cache.set(
                    cache_key, 
                    result, 
                    ttl=cache_ttl or self.cache.default_ttl,
                    tags=tags,
                    priority=cache_priority
                )
            
        except Exception as e:
            error = str(e)
            logger.error(f"Query execution failed: {query} - {e}")
            raise
        
        finally:
            execution_time = time.time() - start_time
            self._monitor_query(query, params, execution_time, len(result), cache_hit, error)
        
        return result
    
    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query with cache invalidation and monitoring."""
        start_time = time.time()
        error = None
        rows_affected = 0
        
        try:
            # Execute write query
            rows_affected = self.db.execute_write(query, params)
            
            # Invalidate related cache entries
            self._invalidate_cache_for_write(query)
            
        except Exception as e:
            error = str(e)
            logger.error(f"Write query execution failed: {query} - {e}")
            raise
        
        finally:
            execution_time = time.time() - start_time
            self._monitor_query(query, params, execution_time, rows_affected, False, error)
        
        return rows_affected
    
    def execute_transaction(self, queries: List[Tuple[str, tuple]]) -> List[int]:
        """Execute multiple queries in a transaction with monitoring."""
        start_time = time.time()
        error = None
        results = []
        
        try:
            # Execute transaction
            results = self.db.execute_transaction(queries)
            
            # Invalidate cache for all write operations
            for query, _ in queries:
                if not query.strip().upper().startswith('SELECT'):
                    self._invalidate_cache_for_write(query)
        
        except Exception as e:
            error = str(e)
            logger.error(f"Transaction failed: {e}")
            raise
        
        finally:
            execution_time = time.time() - start_time
            if self.monitor:
                self.monitor.collector.record_metric(
                    'transaction_time',
                    execution_time,
                    'seconds',
                    'database'
                )
        
        return results
    
    def _invalidate_cache_for_write(self, query: str) -> None:
        """Invalidate cache entries affected by write operations."""
        query_upper = query.upper()
        tags_to_invalidate = []
        
        if 'problems' in query.lower():
            tags_to_invalidate.extend(['problems', 'popular'])
        if 'submissions' in query.lower():
            tags_to_invalidate.extend(['submissions', 'users', 'leaderboard'])
        if 'user_stats' in query.lower():
            tags_to_invalidate.extend(['users', 'leaderboard'])
        
        if tags_to_invalidate:
            invalidated = self.cache.invalidate_by_tags(tags_to_invalidate)
            if invalidated > 0:
                logger.debug(f"Invalidated {invalidated} cache entries for tags: {tags_to_invalidate}")\n    \n    # High-level convenience methods with optimized caching\n    \n    def get_problems(self, difficulty: Optional[str] = None, \n                    limit: int = 50, offset: int = 0,\n                    use_cache: bool = True) -> List[Dict[str, Any]]:\n        \"\"\"Get problems with optimized caching.\"\"\"\n        if difficulty:\n            query = '''\n                SELECT id, title, description, difficulty, view_count, \n                       submission_count, success_rate, created_at\n                FROM problems \n                WHERE difficulty = ? \n                ORDER BY created_at DESC \n                LIMIT ? OFFSET ?\n            '''\n            params = (difficulty, limit, offset)\n            cache_ttl = 600  # 10 minutes\n        else:\n            query = '''\n                SELECT id, title, description, difficulty, view_count, \n                       submission_count, success_rate, created_at\n                FROM problems \n                ORDER BY created_at DESC \n                LIMIT ? OFFSET ?\n            '''\n            params = (limit, offset)\n            cache_ttl = 300  # 5 minutes\n        \n        results = self.execute_query(query, params, cache_ttl, use_cache, cache_priority=2)\n        return [dict(row) for row in results]\n    \n    def get_problem_by_id(self, problem_id: int, use_cache: bool = True) -> Optional[Dict[str, Any]]:\n        \"\"\"Get problem by ID with aggressive caching.\"\"\"\n        query = '''\n            SELECT id, title, description, difficulty, function_signatures, \n                   test_cases, view_count, submission_count, success_rate, created_at\n            FROM problems \n            WHERE id = ?\n        '''\n        \n        results = self.execute_query(query, (problem_id,), cache_ttl=1800, \n                                   use_cache=use_cache, cache_priority=3)\n        \n        if results:\n            problem = dict(results[0])\n            \n            # Update view count asynchronously\n            if use_cache:\n                threading.Thread(\n                    target=self._increment_view_count, \n                    args=(problem_id,), \n                    daemon=True\n                ).start()\n            \n            return problem\n        \n        return None\n    \n    def _increment_view_count(self, problem_id: int) -> None:\n        \"\"\"Increment problem view count asynchronously.\"\"\"\n        try:\n            self.execute_write(\n                'UPDATE problems SET view_count = view_count + 1 WHERE id = ?',\n                (problem_id,)\n            )\n        except Exception as e:\n            logger.error(f\"Failed to increment view count for problem {problem_id}: {e}\")\n    \n    def get_user_submissions(self, user_name: str, limit: int = 20, \n                           use_cache: bool = True) -> List[Dict[str, Any]]:\n        \"\"\"Get user submissions with caching.\"\"\"\n        query = '''\n            SELECT s.id, s.problem_id, p.title as problem_title, s.language, \n                   s.result, s.execution_time, s.memory_used, s.submitted_at\n            FROM submissions s\n            JOIN problems p ON s.problem_id = p.id\n            WHERE s.user_name = ?\n            ORDER BY s.submitted_at DESC\n            LIMIT ?\n        '''\n        \n        results = self.execute_query(query, (user_name, limit), cache_ttl=300, \n                                   use_cache=use_cache, cache_priority=1)\n        return [dict(row) for row in results]\n    \n    def get_leaderboard(self, limit: int = 10, use_cache: bool = True) -> List[Dict[str, Any]]:\n        \"\"\"Get user leaderboard with caching.\"\"\"\n        query = '''\n            SELECT user_name, problems_solved, success_rate, \n                   total_submissions, last_submission_at\n            FROM user_stats\n            WHERE problems_solved > 0\n            ORDER BY problems_solved DESC, success_rate DESC\n            LIMIT ?\n        '''\n        \n        results = self.execute_query(query, (limit,), cache_ttl=600, \n                                   use_cache=use_cache, cache_priority=2)\n        return [dict(row) for row in results]\n    \n    def create_submission(self, problem_id: int, user_name: str, language: str, \n                         code: str, result: str, message: str = None,\n                         execution_time: float = None, memory_used: int = None) -> int:\n        \"\"\"Create a new submission with optimized user stats update.\"\"\"\n        # Insert submission\n        submission_query = '''\n            INSERT INTO submissions \n            (problem_id, user_name, language, code, result, message, \n             execution_time, memory_used, submitted_at)\n            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)\n        '''\n        \n        submission_id = self.execute_write(\n            submission_query,\n            (problem_id, user_name, language, code, result, message, \n             execution_time, memory_used)\n        )\n        \n        # Update user stats asynchronously\n        threading.Thread(\n            target=self._update_user_stats_async,\n            args=(user_name,),\n            daemon=True\n        ).start()\n        \n        # Update problem stats asynchronously\n        threading.Thread(\n            target=self._update_problem_stats_async,\n            args=(problem_id,),\n            daemon=True\n        ).start()\n        \n        return submission_id\n    \n    def _update_user_stats_async(self, user_name: str) -> None:\n        \"\"\"Update user statistics asynchronously.\"\"\"\n        try:\n            self.db.update_user_stats(user_name)\n        except Exception as e:\n            logger.error(f\"Failed to update user stats for {user_name}: {e}\")\n    \n    def _update_problem_stats_async(self, problem_id: int) -> None:\n        \"\"\"Update problem statistics asynchronously.\"\"\"\n        try:\n            # Update submission count and success rate\n            self.execute_write('''\n                UPDATE problems SET \n                    submission_count = (\n                        SELECT COUNT(*) FROM submissions WHERE problem_id = ?\n                    ),\n                    success_rate = (\n                        SELECT ROUND(\n                            CAST(SUM(CASE WHEN result = 'PASS' THEN 1 ELSE 0 END) AS REAL) / \n                            COUNT(*) * 100, 2\n                        )\n                        FROM submissions WHERE problem_id = ?\n                    )\n                WHERE id = ?\n            ''', (problem_id, problem_id, problem_id))\n            \n        except Exception as e:\n            logger.error(f\"Failed to update problem stats for {problem_id}: {e}\")\n    \n    def warm_cache(self, strategy_name: str = None) -> None:\n        \"\"\"Manually warm cache with specified strategy or all strategies.\"\"\"\n        if strategy_name:\n            if strategy_name in self.warming_strategies:\n                self.warming_strategies[strategy_name]()\n            else:\n                logger.warning(f\"Unknown warming strategy: {strategy_name}\")\n        else:\n            # Run all warming strategies\n            for name, strategy in self.warming_strategies.items():\n                try:\n                    strategy()\n                except Exception as e:\n                    logger.error(f\"Warming strategy {name} failed: {e}\")\n    \n    def get_performance_stats(self) -> Dict[str, Any]:\n        \"\"\"Get comprehensive performance statistics.\"\"\"\n        stats = {\n            'database': self.db.get_performance_stats(),\n            'cache': self.cache.get_stats() if self.cache else None\n        }\n        \n        if self.monitor:\n            stats['monitoring'] = self.monitor.get_dashboard_data()\n        \n        return stats\n    \n    def optimize_database(self) -> Dict[str, Any]:\n        \"\"\"Run database optimization.\"\"\"\n        return self.db.optimize_database()\n    \n    def close(self) -> None:\n        \"\"\"Close database connections and cleanup resources.\"\"\"\n        if self.db:\n            self.db.close()\n        \n        if self.cache:\n            self.cache.clear()\n        \n        logger.info(\"Integrated database closed\")\n\n\n# Global integrated database instance\n_integrated_db = None\n_db_lock = threading.Lock()\n\n\ndef get_integrated_db(database_path: str = 'database.db', \n                     cache_config: Dict[str, Any] = None,\n                     enable_monitoring: bool = True) -> IntegratedDatabase:\n    \"\"\"Get singleton integrated database instance.\"\"\"\n    global _integrated_db\n    \n    if _integrated_db is None:\n        with _db_lock:\n            if _integrated_db is None:\n                _integrated_db = IntegratedDatabase(\n                    database_path, cache_config, enable_monitoring\n                )\n    \n    return _integrated_db\n\n\ndef close_integrated_db() -> None:\n    \"\"\"Close the global integrated database instance.\"\"\"\n    global _integrated_db\n    \n    if _integrated_db is not None:\n        with _db_lock:\n            if _integrated_db is not None:\n                _integrated_db.close()\n                _integrated_db = None\n\n\nif __name__ == '__main__':\n    # Example usage and testing\n    db = get_integrated_db('test_integrated.db')\n    \n    try:\n        # Test basic operations\n        problems = db.get_problems(limit=5)\n        print(f\"Retrieved {len(problems)} problems\")\n        \n        # Test caching\n        start_time = time.time()\n        problems_cached = db.get_problems(limit=5)  # Should be cached\n        cache_time = time.time() - start_time\n        print(f\"Cached query took {cache_time:.4f} seconds\")\n        \n        # Warm cache\n        db.warm_cache()\n        \n        # Get performance stats\n        stats = db.get_performance_stats()\n        print(f\"Performance stats: {stats['cache']}\")\n        \n    finally:\n        close_integrated_db()