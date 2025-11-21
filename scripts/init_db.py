#!/usr/bin/env python3
"""
CodeXam Database Initialization
Creates SQLite database schema and tables for the CodeXam platform
"""

import sqlite3
import os
import sys
from datetime import datetime
from typing import Optional

# Database schema SQL statements
SCHEMA_SQL = """
-- Problems table
-- Stores coding problems with descriptions, test cases, and metadata
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    function_signatures TEXT NOT NULL,  -- JSON string with language-specific signatures
    test_cases TEXT NOT NULL,          -- JSON string with input/output test cases
    sample_input TEXT,                 -- Example input for display
    sample_output TEXT,                -- Example output for display
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Submissions table
-- Tracks user code submissions and results
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    language TEXT NOT NULL CHECK (language IN ('python', 'javascript', 'java', 'cpp')),
    code TEXT NOT NULL,
    result TEXT NOT NULL CHECK (result IN ('PASS', 'FAIL', 'ERROR', 'TIMEOUT')),
    execution_time REAL DEFAULT 0.0,   -- Execution time in seconds
    memory_used INTEGER DEFAULT 0,     -- Memory used in bytes
    error_message TEXT,                -- Error details if result is ERROR
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problem_id) REFERENCES problems (id) ON DELETE CASCADE
);

-- Users table (for future use - Phase 2)
-- Basic user tracking for leaderboard and statistics
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    display_name TEXT NOT NULL,
    problems_solved INTEGER DEFAULT 0,
    total_submissions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Indexes for performance optimization
INDEXES_SQL = """
-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_problems_difficulty ON problems(difficulty);
CREATE INDEX IF NOT EXISTS idx_problems_created_at ON problems(created_at);

CREATE INDEX IF NOT EXISTS idx_submissions_problem_id ON submissions(problem_id);
CREATE INDEX IF NOT EXISTS idx_submissions_user_name ON submissions(user_name);
CREATE INDEX IF NOT EXISTS idx_submissions_result ON submissions(result);
CREATE INDEX IF NOT EXISTS idx_submissions_submitted_at ON submissions(submitted_at);
CREATE INDEX IF NOT EXISTS idx_submissions_language ON submissions(language);

-- Composite indexes for optimized queries
CREATE INDEX IF NOT EXISTS idx_submissions_user_problem ON submissions(user_name, problem_id, submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_submissions_leaderboard ON submissions(user_name, result, problem_id);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_problems_solved ON users(problems_solved DESC);
"""

# Triggers for maintaining data consistency
TRIGGERS_SQL = """
-- Update timestamp trigger for problems
CREATE TRIGGER IF NOT EXISTS update_problems_timestamp 
    AFTER UPDATE ON problems
    FOR EACH ROW
BEGIN
    UPDATE problems SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update user statistics trigger
CREATE TRIGGER IF NOT EXISTS update_user_stats_on_submission
    AFTER INSERT ON submissions
    FOR EACH ROW
    WHEN NEW.result = 'PASS'
BEGIN
    INSERT OR IGNORE INTO users (username, display_name) 
    VALUES (NEW.user_name, NEW.user_name);
    
    UPDATE users 
    SET total_submissions = total_submissions + 1,
        problems_solved = (
            SELECT COUNT(DISTINCT problem_id) 
            FROM submissions 
            WHERE user_name = NEW.user_name AND result = 'PASS'
        ),
        last_active = CURRENT_TIMESTAMP
    WHERE username = NEW.user_name;
END;

-- Update total submissions for all submissions
CREATE TRIGGER IF NOT EXISTS update_user_total_submissions
    AFTER INSERT ON submissions
    FOR EACH ROW
BEGIN
    INSERT OR IGNORE INTO users (username, display_name) 
    VALUES (NEW.user_name, NEW.user_name);
    
    UPDATE users 
    SET total_submissions = total_submissions + 1,
        last_active = CURRENT_TIMESTAMP
    WHERE username = NEW.user_name;
END;
"""

class DatabaseManager:
    """Database connection and management utilities."""
    
    def __init__(self, database_path: str = "database.db"):
        """Initialize database manager with path."""
        self.database_path = database_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """Create and return database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(
                self.database_path,
                check_same_thread=False,
                timeout=30.0
            )
            # Enable foreign key constraints
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Set row factory for dict-like access
            self.connection.row_factory = sqlite3.Row
        
        return self.connection
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_script(self, script: str) -> None:
        """Execute SQL script with error handling."""
        try:
            conn = self.connect()
            conn.executescript(script)
            conn.commit()
            print(f"✅ Successfully executed SQL script")
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        try:
            conn = self.connect()
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return cursor.fetchone() is not None
        except sqlite3.Error:
            return False
    
    def get_table_info(self, table_name: str) -> list:
        """Get table schema information."""
        try:
            conn = self.connect()
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Error getting table info for {table_name}: {e}")
            return []
    
    def get_database_stats(self) -> dict:
        """Get database statistics."""
        try:
            conn = self.connect()
            stats = {}
            
            # Get table counts
            tables = ['problems', 'submissions', 'users']
            for table in tables:
                if self.table_exists(table):
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]
                else:
                    stats[f"{table}_count"] = 0
            
            # Get database file size
            if os.path.exists(self.database_path):
                stats['database_size_bytes'] = os.path.getsize(self.database_path)
                stats['database_size_mb'] = round(stats['database_size_bytes'] / (1024 * 1024), 2)
            else:
                stats['database_size_bytes'] = 0
                stats['database_size_mb'] = 0
            
            return stats
        except sqlite3.Error as e:
            print(f"❌ Error getting database stats: {e}")
            return {}

def initialize_database(database_path: str = "database.db", force: bool = False) -> bool:
    """
    Initialize the CodeXam database with schema, indexes, and triggers.
    
    Args:
        database_path: Path to SQLite database file
        force: If True, recreate database even if it exists
    
    Returns:
        True if successful, False otherwise
    """
    print(f"🚀 Initializing CodeXam database: {database_path}")
    
    # Check if database exists and handle force flag
    if os.path.exists(database_path) and not force:
        print(f"📁 Database file already exists: {database_path}")
        
        # Verify existing database structure
        db_manager = DatabaseManager(database_path)
        required_tables = ['problems', 'submissions', 'users']
        
        missing_tables = []
        for table in required_tables:
            if not db_manager.table_exists(table):
                missing_tables.append(table)
        
        if missing_tables:
            print(f"⚠️  Missing tables: {missing_tables}")
            print("🔧 Creating missing tables...")
        else:
            print("✅ All required tables exist")
            stats = db_manager.get_database_stats()
            print(f"📊 Database stats: {stats}")
            return True
    
    elif force and os.path.exists(database_path):
        print(f"🗑️  Removing existing database (force=True)")
        os.remove(database_path)
    
    try:
        # Create database manager
        db_manager = DatabaseManager(database_path)
        
        # Create schema
        print("📋 Creating database schema...")
        db_manager.execute_script(SCHEMA_SQL)
        
        # Create indexes
        print("🔍 Creating performance indexes...")
        db_manager.execute_script(INDEXES_SQL)
        
        # Create triggers
        print("⚡ Creating database triggers...")
        db_manager.execute_script(TRIGGERS_SQL)
        
        # Verify database creation
        required_tables = ['problems', 'submissions', 'users']
        for table in required_tables:
            if not db_manager.table_exists(table):
                raise Exception(f"Failed to create table: {table}")
        
        # Display database statistics
        stats = db_manager.get_database_stats()
        print(f"📊 Database initialized successfully!")
        print(f"   - Problems: {stats.get('problems_count', 0)}")
        print(f"   - Submissions: {stats.get('submissions_count', 0)}")
        print(f"   - Users: {stats.get('users_count', 0)}")
        print(f"   - Database size: {stats.get('database_size_mb', 0)} MB")
        
        db_manager.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def reset_database(database_path: str = "database.db") -> bool:
    """
    Reset database by dropping all tables and recreating schema.
    
    Args:
        database_path: Path to SQLite database file
    
    Returns:
        True if successful, False otherwise
    """
    print(f"🔄 Resetting CodeXam database: {database_path}")
    
    try:
        db_manager = DatabaseManager(database_path)
        conn = db_manager.connect()
        
        # Drop all tables
        print("🗑️  Dropping existing tables...")
        drop_sql = """
        DROP TABLE IF EXISTS submissions;
        DROP TABLE IF EXISTS problems;
        DROP TABLE IF EXISTS users;
        """
        conn.executescript(drop_sql)
        conn.commit()
        
        db_manager.close()
        
        # Reinitialize database
        return initialize_database(database_path, force=True)
        
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")
        return False

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CodeXam Database Initialization")
    parser.add_argument(
        "--database", "-d",
        default="database.db",
        help="Database file path (default: database.db)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force recreation of existing database"
    )
    parser.add_argument(
        "--reset", "-r",
        action="store_true",
        help="Reset database by dropping all tables"
    )
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Show database statistics"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Production mode - requires confirmation for destructive operations"
    )
    
    args = parser.parse_args()
    
    # Production safety check
    if args.production and (args.force or args.reset):
        confirm = input("⚠️  Production mode: Are you sure? (type 'yes' to confirm): ")
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled")
            sys.exit(1)
    
    # Handle different operations
    if args.stats:
        db_manager = DatabaseManager(args.database)
        if os.path.exists(args.database):
            stats = db_manager.get_database_stats()
            print(f"📊 Database Statistics for {args.database}:")
            for key, value in stats.items():
                print(f"   - {key}: {value}")
        else:
            print(f"❌ Database file not found: {args.database}")
        return
    
    if args.reset:
        success = reset_database(args.database)
    else:
        success = initialize_database(args.database, args.force)
    
    if success:
        print("✅ Database operation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Database operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()