"""
CodeXam Database Connection Utilities
Provides database connection and query utilities for the Flask application
"""

import sqlite3
import os
import json
from typing import Optional, Dict, List, Any, Union
from contextlib import contextmanager
from datetime import datetime
import threading

# Thread-local storage for database connections
_local = threading.local()

class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass

class DatabaseConnection:
    """Database connection manager with utilities."""
    
    def __init__(self, database_path: str = "database.db"):
        """Initialize database connection manager."""
        self.database_path = database_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self) -> None:
        """Ensure database file exists and is initialized."""
        if not os.path.exists(self.database_path):
            from init_db import initialize_database
            if not initialize_database(self.database_path):
                raise DatabaseError(f"Failed to initialize database: {self.database_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(_local, 'connection') or _local.connection is None:
            _local.connection = sqlite3.connect(
                self.database_path,
                check_same_thread=False,
                timeout=30.0
            )
            # Enable foreign key constraints
            _local.connection.execute("PRAGMA foreign_keys = ON")
            # Set row factory for dict-like access
            _local.connection.row_factory = sqlite3.Row
        
        return _local.connection
    
    def close_connection(self) -> None:
        """Close thread-local database connection."""
        if hasattr(_local, 'connection') and _local.connection:
            _local.connection.close()
            _local.connection = None
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute SELECT query and return results."""
        try:
            conn = self.get_connection()
            cursor = conn.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(f"Query execution failed: {e}")
    
    def execute_single(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute SELECT query and return single result."""
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows."""
        try:
            with self.transaction() as conn:
                cursor = conn.execute(query, params)
                return cursor.rowcount
        except sqlite3.Error as e:
            raise DatabaseError(f"Update execution failed: {e}")
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT query and return last row ID."""
        try:
            with self.transaction() as conn:
                cursor = conn.execute(query, params)
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(f"Insert execution failed: {e}")

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

def get_platform_stats() -> Dict[str, Any]:
    """Get platform statistics for homepage."""
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