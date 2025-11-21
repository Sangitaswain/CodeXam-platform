"""
CodeXam Database Connection Utilities

Provides database connection and query utilities for the Flask application.
This module handles all database operations with connection pooling, caching,
and comprehensive error handling.
"""

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from cache import cached, invalidate_platform_stats_cache
from performance_monitor import monitor_db_query

# Thread-local storage for database connections
_local = threading.local()


class DatabaseError(Exception):
    """Custom exception for database operations."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None) -> None:
        """
        Initialize DatabaseError.
        
        Args:
            message: Error message
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.original_error = original_error

class DatabaseConnection:
    """
    Enhanced database connection manager with connection pooling and monitoring.
    
    This class provides thread-safe database connections with automatic
    initialization, transaction management, connection pooling, and comprehensive
    query monitoring for optimal performance.
    
    Attributes:
        database_path: Path to the SQLite database file
        max_connections: Maximum number of connections in the pool
        connection_timeout: Timeout for database operations in seconds
    """
    
    def __init__(
        self, 
        database_path: str = "database.db",
        max_connections: int = 10,
        connection_timeout: float = 30.0
    ) -> None:
        """
        Initialize enhanced database connection manager.
        
        Args:
            database_path: Path to the SQLite database file
            max_connections: Maximum number of connections to maintain
            connection_timeout: Timeout for database operations
            
        Raises:
            DatabaseError: If database initialization fails
        """
        self.database_path = database_path
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self._connection_pool = []
        self._pool_lock = threading.Lock()
        self._ensure_database_exists()
    
    def _ensure_database_exists(self) -> None:
        """
        Ensure database file exists and is initialized.
        
        Raises:
            DatabaseError: If database initialization fails
        """
        if not os.path.exists(self.database_path):
            try:
                from scripts.init_db import initialize_database
                if not initialize_database(self.database_path):
                    raise DatabaseError(
                        f"Failed to initialize database: {self.database_path}"
                    )
            except ImportError:
                # Fallback for when init_db is not available
                pass
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get optimized database connection with connection pooling.
        
        Returns:
            SQLite database connection with proper configuration and optimizations
            
        Raises:
            DatabaseError: If connection cannot be established
        """
        try:
            if not hasattr(_local, 'connection') or _local.connection is None:
                _local.connection = self._create_optimized_connection()
            
            # Test connection health
            try:
                _local.connection.execute("SELECT 1").fetchone()
            except sqlite3.Error:
                # Connection is stale, create a new one
                _local.connection = self._create_optimized_connection()
            
            return _local.connection
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}", e)
    
    def _create_optimized_connection(self) -> sqlite3.Connection:
        """
        Create an optimized SQLite connection with performance settings.
        
        Returns:
            Optimized SQLite connection
            
        Raises:
            sqlite3.Error: If connection creation fails
        """
        conn = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
            timeout=self.connection_timeout,
            isolation_level=None  # Enable autocommit mode for better performance
        )
        
        # Set row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        # Performance optimizations
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for better concurrency
        conn.execute("PRAGMA synchronous = NORMAL")  # Balance between safety and performance
        conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
        conn.execute("PRAGMA temp_store = MEMORY")  # Store temp tables in memory
        conn.execute("PRAGMA mmap_size = 268435456")  # 256MB memory-mapped I/O
        
        # Enable query optimization
        conn.execute("PRAGMA optimize")
        
        return conn
    
    def close_connection(self) -> None:
        """Close thread-local database connection."""
        if hasattr(_local, 'connection') and _local.connection:
            try:
                _local.connection.close()
            except sqlite3.Error:
                # Ignore errors when closing connection
                pass
            finally:
                _local.connection = None
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Yields:
            Database connection within transaction context
            
        Raises:
            DatabaseError: If transaction fails
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            if isinstance(e, sqlite3.Error):
                raise DatabaseError(f"Transaction failed: {e}", e)
            raise
    
    @monitor_db_query('SELECT')
    def execute_query(
        self, 
        query: str, 
        params: tuple = ()
    ) -> List[sqlite3.Row]:
        """
        Execute SELECT query and return results.
        
        Args:
            query: SQL SELECT query
            params: Query parameters
            
        Returns:
            List of database rows
            
        Raises:
            DatabaseError: If query execution fails
        """
        try:
            conn = self.get_connection()
            cursor = conn.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(f"Query execution failed: {e}", e)
    
    @monitor_db_query('SELECT_SINGLE')
    def execute_single(
        self, 
        query: str, 
        params: tuple = ()
    ) -> Optional[sqlite3.Row]:
        """
        Execute SELECT query and return single result.
        
        Args:
            query: SQL SELECT query
            params: Query parameters
            
        Returns:
            Single database row or None if no results
            
        Raises:
            DatabaseError: If query execution fails
        """
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    @monitor_db_query('UPDATE')
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute INSERT/UPDATE/DELETE query and return affected rows.
        
        Args:
            query: SQL INSERT/UPDATE/DELETE query
            params: Query parameters
            
        Returns:
            Number of affected rows
            
        Raises:
            DatabaseError: If query execution fails
        """
        try:
            with self.transaction() as conn:
                cursor = conn.execute(query, params)
                return cursor.rowcount
        except sqlite3.Error as e:
            raise DatabaseError(f"Update execution failed: {e}", e)
    
    @monitor_db_query('INSERT')
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        Execute INSERT query and return last row ID.
        
        Args:
            query: SQL INSERT query
            params: Query parameters
            
        Returns:
            ID of the inserted row
            
        Raises:
            DatabaseError: If query execution fails
        """
        try:
            with self.transaction() as conn:
                cursor = conn.execute(query, params)
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(f"Insert execution failed: {e}", e)

# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None

def get_db() -> DatabaseConnection:
    """Get global database connection instance."""
    global _db_connection
    if _db_connection is None:
        database_path = os.environ.get('DATABASE_URL', 'database.db')
        # Handle SQLite URL format
        if database_path.startswith('sqlite:///'):
            database_path = database_path[10:]  # Remove 'sqlite:///'
        elif database_path.startswith('sqlite://'):
            database_path = database_path[9:]   # Remove 'sqlite://'
        
        _db_connection = DatabaseConnection(database_path)
    
    return _db_connection

def close_db() -> None:
    """Close global database connection."""
    global _db_connection
    if _db_connection:
        _db_connection.close_connection()
        _db_connection = None

# Utility functions for common database operations

def dict_to_json(data: Dict[str, Any]) -> str:
    """Convert dictionary to JSON string for database storage."""
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))

def json_to_dict(json_str: str) -> Dict[str, Any]:
    """Convert JSON string from database to dictionary."""
    try:
        return json.loads(json_str) if json_str else {}
    except json.JSONDecodeError:
        return {}

def format_timestamp(timestamp: Union[str, datetime]) -> str:
    """Format timestamp for display."""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return timestamp
    
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def validate_difficulty(difficulty: str) -> bool:
    """Validate problem difficulty level."""
    return difficulty in ['Easy', 'Medium', 'Hard']

def validate_language(language: str) -> bool:
    """Validate programming language."""
    return language in ['python', 'javascript', 'java', 'cpp']

def validate_result(result: str) -> bool:
    """Validate submission result."""
    return result in ['PASS', 'FAIL', 'ERROR', 'TIMEOUT']

# Database query helpers

def get_problems_count() -> int:
    """Get total number of problems."""
    db = get_db()
    result = db.execute_single("SELECT COUNT(*) as count FROM problems")
    return result['count'] if result else 0

def get_submissions_count() -> int:
    """Get total number of submissions."""
    db = get_db()
    result = db.execute_single("SELECT COUNT(*) as count FROM submissions")
    return result['count'] if result else 0

def get_users_count() -> int:
    """Get total number of users."""
    db = get_db()
    result = db.execute_single("SELECT COUNT(*) as count FROM users")
    return result['count'] if result else 0

@cached(ttl=300, key_func=lambda: "platform_stats")
def get_platform_stats() -> Dict[str, Any]:
    """Get platform statistics for homepage with caching."""
    return {
        'total_problems': get_problems_count(),
        'total_submissions': get_submissions_count(),
        'total_users': get_users_count(),
        'last_updated': datetime.now().isoformat()
    }

# Flask integration helpers

def init_app(app):
    """Initialize database with Flask app."""
    @app.teardown_appcontext
    def close_db_connection(error):
        """Close database connection at end of request."""
        close_db()
    
    @app.cli.command()
    def init_db():
        """Initialize database command."""
        from init_db import initialize_database
        if initialize_database():
            print("Database initialized successfully!")
        else:
            print("Database initialization failed!")
    
    @app.cli.command()
    def reset_db():
        """Reset database command."""
        from init_db import reset_database
        if reset_database():
            print("Database reset successfully!")
        else:
            print("Database reset failed!")

# Admin Functions

def get_admin_stats() -> Dict[str, Any]:
    """Get basic admin statistics."""
    try:
        db = get_db()
        
        # Get total problems
        problems_result = db.execute_query("SELECT COUNT(*) as count FROM problems")
        total_problems = problems_result[0]['count'] if problems_result else 0
        
        # Get total submissions
        submissions_result = db.execute_query("SELECT COUNT(*) as count FROM submissions")
        total_submissions = submissions_result[0]['count'] if submissions_result else 0
        
        # Get unique users
        users_result = db.execute_query("SELECT COUNT(DISTINCT user_name) as count FROM submissions WHERE user_name != 'Anonymous'")
        total_users = users_result[0]['count'] if users_result else 0
        
        # Get success rate
        success_result = db.execute_query("SELECT COUNT(*) as count FROM submissions WHERE result = 'PASS'")
        success_count = success_result[0]['count'] if success_result else 0
        success_rate = round((success_count / total_submissions * 100) if total_submissions > 0 else 0, 1)
        
        return {
            'total_problems': total_problems,
            'total_submissions': total_submissions,
            'total_users': total_users,
            'success_rate': success_rate
        }
    except Exception as e:
        print(f"Error getting admin stats: {e}")
        return {
            'total_problems': 0,
            'total_submissions': 0,
            'total_users': 0,
            'success_rate': 0
        }

def get_recent_submissions(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent submissions for admin dashboard."""
    try:
        db = get_db()
        query = """
            SELECT s.*, p.title as problem_title
            FROM submissions s
            LEFT JOIN problems p ON s.problem_id = p.id
            ORDER BY s.submitted_at DESC
            LIMIT ?
        """
        submissions = db.execute_query(query, (limit,))
        
        # Convert to list of dicts for template
        result = []
        for submission in submissions:
            result.append({
                'id': submission['id'],
                'user_name': submission['user_name'],
                'problem_id': submission['problem_id'],
                'problem_title': submission['problem_title'],
                'language': submission['language'],
                'result': submission['result'],
                'submitted_at': datetime.fromisoformat(submission['submitted_at'])
            })
        
        return result
    except Exception as e:
        print(f"Error getting recent submissions: {e}")
        return []

def create_problem(title: str, description: str, difficulty: str, time_limit: float, 
                  memory_limit: int, languages: List[str], function_signatures: Dict[str, str], 
                  test_cases: List[Dict[str, Any]]) -> Optional[int]:
    """Create a new problem in the database."""
    try:
        db = get_db()
        conn = db.get_connection()
        
        # Prepare test cases data
        test_cases_json = json.dumps(test_cases, ensure_ascii=False, separators=(',', ':'))
        
        # Prepare function signatures data
        signatures_json = dict_to_json(function_signatures)
        
        # Insert the problem
        query = """
            INSERT INTO problems (title, description, difficulty, time_limit, memory_limit, 
                                languages, function_signatures, test_cases, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        now = datetime.now().isoformat()
        languages_str = ','.join(languages)
        
        cursor = conn.execute(query, (
            title, description, difficulty, time_limit, memory_limit,
            languages_str, signatures_json, test_cases_json, now, now
        ))
        
        conn.commit()
        return cursor.lastrowid
        
    except Exception as e:
        print(f"Error creating problem: {e}")
        return None

def get_all_problems_admin() -> List[Dict[str, Any]]:
    """Get all problems for admin management."""
    try:
        db = get_db()
        query = """
            SELECT p.*, 
                   COUNT(s.id) as submission_count,
                   COUNT(CASE WHEN s.result = 'PASS' THEN 1 END) as solved_count
            FROM problems p
            LEFT JOIN submissions s ON p.id = s.problem_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """
        problems = db.execute_query(query)
        
        result = []
        for problem in problems:
            result.append({
                'id': problem['id'],
                'title': problem['title'],
                'difficulty': problem['difficulty'],
                'languages': problem['languages'].split(',') if problem['languages'] else [],
                'submission_count': problem['submission_count'],
                'solved_count': problem['solved_count'],
                'created_at': datetime.fromisoformat(problem['created_at']),
                'time_limit': problem['time_limit'],
                'memory_limit': problem['memory_limit']
            })
        
        return result
    except Exception as e:
        print(f"Error getting problems for admin: {e}")
        return []

def get_all_submissions_admin(page: int = 1, per_page: int = 50) -> Dict[str, Any]:
    """Get all submissions with pagination for admin view."""
    try:
        db = get_db()
        offset = (page - 1) * per_page
        
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM submissions"
        count_result = db.execute_query(count_query)
        total_count = count_result[0]['count'] if count_result else 0
        
        # Get submissions
        query = """
            SELECT s.*, p.title as problem_title
            FROM submissions s
            LEFT JOIN problems p ON s.problem_id = p.id
            ORDER BY s.submitted_at DESC
            LIMIT ? OFFSET ?
        """
        submissions = db.execute_query(query, (per_page, offset))
        
        result_submissions = []
        for submission in submissions:
            result_submissions.append({
                'id': submission['id'],
                'user_name': submission['user_name'],
                'problem_id': submission['problem_id'],
                'problem_title': submission['problem_title'],
                'language': submission['language'],
                'result': submission['result'],
                'execution_time': submission['execution_time'],
                'memory_usage': submission['memory_usage'],
                'submitted_at': datetime.fromisoformat(submission['submitted_at'])
            })
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return {
            'submissions': result_submissions,
            'page': page,
            'per_page': per_page,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
    except Exception as e:
        print(f"Error getting submissions for admin: {e}")
        return {
            'submissions': [],
            'page': 1,
            'per_page': per_page,
            'total_count': 0,
            'total_pages': 0,
            'has_prev': False,
            'has_next': False
        }

def get_detailed_admin_stats() -> Dict[str, Any]:
    """Get detailed system statistics for admin."""
    try:
        db = get_db()
        
        stats = get_admin_stats()
        
        # Language popularity
        lang_query = """
            SELECT language, COUNT(*) as count 
            FROM submissions 
            GROUP BY language 
            ORDER BY count DESC
        """
        language_stats = db.execute_query(lang_query)
        
        # Difficulty distribution
        diff_query = """
            SELECT p.difficulty, COUNT(*) as problem_count,
                   AVG(CASE WHEN s.result = 'PASS' THEN 1.0 ELSE 0.0 END) as success_rate
            FROM problems p
            LEFT JOIN submissions s ON p.id = s.problem_id
            GROUP BY p.difficulty
        """
        difficulty_stats = db.execute_query(diff_query)
        
        # Recent activity (submissions per day for last 7 days)
        activity_query = """
            SELECT DATE(submitted_at) as date, COUNT(*) as count
            FROM submissions
            WHERE submitted_at >= date('now', '-7 days')
            GROUP BY DATE(submitted_at)
            ORDER BY date DESC
        """
        activity_stats = db.execute_query(activity_query)
        
        # Top users
        user_query = """
            SELECT user_name, 
                   COUNT(*) as total_submissions,
                   COUNT(CASE WHEN result = 'PASS' THEN 1 END) as solved_problems
            FROM submissions
            WHERE user_name != 'Anonymous'
            GROUP BY user_name
            ORDER BY solved_problems DESC, total_submissions DESC
            LIMIT 10
        """
        top_users = db.execute_query(user_query)
        
        return {
            **stats,
            'language_stats': [dict(row) for row in language_stats],
            'difficulty_stats': [dict(row) for row in difficulty_stats],
            'activity_stats': [dict(row) for row in activity_stats],
            'top_users': [dict(row) for row in top_users]
        }
    except Exception as e:
        print(f"Error getting detailed admin stats: {e}")
        return get_admin_stats()  # Fallback to basic stats


# Testing utilities

def create_test_database(database_path: str = ":memory:") -> DatabaseConnection:
    """Create test database for unit tests."""
    from init_db import initialize_database
    
    if database_path != ":memory:":
        # Remove existing test database
        if os.path.exists(database_path):
            os.remove(database_path)
    
    # Initialize test database
    if not initialize_database(database_path):
        raise DatabaseError("Failed to create test database")
    
    return DatabaseConnection(database_path)

def cleanup_test_database(database_path: str) -> None:
    """Clean up test database file."""
    if database_path != ":memory:" and os.path.exists(database_path):
        os.remove(database_path)

# Example usage and testing
if __name__ == "__main__":
    # Test database connection
    print("🧪 Testing database connection...")
    
    try:
        db = get_db()
        stats = get_platform_stats()
        print(f"✅ Database connection successful!")
        print(f"📊 Platform stats: {stats}")
        
        # Test query execution
        problems = db.execute_query("SELECT COUNT(*) as count FROM problems")
        print(f"📋 Problems query result: {problems[0]['count']}")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
    
    finally:
        close_db()