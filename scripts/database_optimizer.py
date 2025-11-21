#!/usr/bin/env python3
"""
Database Optimization and Migration Script for CodeXam Platform

This script provides comprehensive database optimization including:
- Index creation and management
- Query performance analysis
- Database maintenance operations
- Migration utilities
- Performance monitoring

Usage:
    python scripts/database_optimizer.py --optimize
    python scripts/database_optimizer.py --analyze
    python scripts/database_optimizer.py --vacuum
    python scripts/database_optimizer.py --migrate

@version 3.0.0
@author CodeXam Development Team
"""

import argparse
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database import get_db, DatabaseError
from database_optimizations import DatabaseOptimizer, get_optimizer
from advanced_cache import get_advanced_cache, warm_platform_cache


class DatabaseMigrator:
    """
    Database migration and optimization manager.
    
    Handles database schema migrations, performance optimizations,
    and maintenance operations for the CodeXam platform.
    """
    
    def __init__(self, database_path: str = None):
        """
        Initialize database migrator.
        
        Args:
            database_path: Optional path to database file
        """
        self.database_path = database_path or "database.db"
        self.migration_history = []
        
    def get_schema_version(self) -> int:
        """Get current database schema version."""
        try:
            db = get_db()
            result = db.execute_single(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            )
            return result['version'] if result else 0
        except:
            # Schema version table doesn't exist, assume version 0
            return 0
    
    def create_schema_version_table(self) -> None:
        """Create schema version tracking table."""
        try:
            db = get_db()
            db.execute_update("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            """)
            print("✅ Schema version table created")
        except Exception as e:
            print(f"❌ Failed to create schema version table: {e}")
    
    def apply_migration(self, version: int, description: str, sql_commands: List[str]) -> bool:
        """
        Apply a database migration.
        
        Args:
            version: Migration version number
            description: Migration description
            sql_commands: List of SQL commands to execute
            
        Returns:
            True if migration was successful
        """
        current_version = self.get_schema_version()
        
        if version <= current_version:
            print(f"⏭️  Migration {version} already applied, skipping")
            return True
        
        print(f"🔄 Applying migration {version}: {description}")
        
        try:
            db = get_db()
            
            # Execute migration commands in a transaction
            with db.transaction() as conn:
                for command in sql_commands:
                    if command.strip():
                        conn.execute(command)
                
                # Record migration
                conn.execute(
                    "INSERT INTO schema_version (version, description) VALUES (?, ?)",
                    (version, description)
                )
            
            print(f"✅ Migration {version} applied successfully")
            self.migration_history.append((version, description, True))
            return True
            
        except Exception as e:
            print(f"❌ Migration {version} failed: {e}")
            self.migration_history.append((version, description, False))
            return False
    
    def run_migrations(self) -> bool:
        """Run all pending database migrations."""
        print("🚀 Starting database migrations...")
        
        # Ensure schema version table exists
        self.create_schema_version_table()
        
        # Define migrations
        migrations = [
            (1, "Add performance indexes", [
                "CREATE INDEX IF NOT EXISTS idx_problems_difficulty ON problems(difficulty)",
                "CREATE INDEX IF NOT EXISTS idx_problems_created_at ON problems(created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_submissions_user_name ON submissions(user_name)",
                "CREATE INDEX IF NOT EXISTS idx_submissions_problem_id ON submissions(problem_id)",
                "CREATE INDEX IF NOT EXISTS idx_submissions_result ON submissions(result)",
                "CREATE INDEX IF NOT EXISTS idx_submissions_submitted_at ON submissions(submitted_at DESC)",
            ]),
            
            (2, "Add composite indexes for common queries", [
                "CREATE INDEX IF NOT EXISTS idx_submissions_user_problem ON submissions(user_name, problem_id)",
                "CREATE INDEX IF NOT EXISTS idx_submissions_problem_result ON submissions(problem_id, result)",
                "CREATE INDEX IF NOT EXISTS idx_submissions_user_result ON submissions(user_name, result)",
                "CREATE INDEX IF NOT EXISTS idx_submissions_recent_activity ON submissions(submitted_at DESC, user_name, result)",
            ]),
            
            (3, "Add execution time and memory usage columns if missing", [
                """
                ALTER TABLE submissions ADD COLUMN execution_time REAL DEFAULT 0.0
                """,
                """
                ALTER TABLE submissions ADD COLUMN memory_used INTEGER DEFAULT 0
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_submissions_performance ON submissions(execution_time, memory_used)
                """,
            ]),
            
            (4, "Add problem statistics columns", [
                """
                ALTER TABLE problems ADD COLUMN time_limit REAL DEFAULT 5.0
                """,
                """
                ALTER TABLE problems ADD COLUMN memory_limit INTEGER DEFAULT 128000000
                """,
                """
                ALTER TABLE problems ADD COLUMN languages TEXT DEFAULT 'python,javascript,java,cpp'
                """,
            ]),
            
            (5, "Create users table for better user management", [
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_submissions INTEGER DEFAULT 0,
                    solved_problems INTEGER DEFAULT 0
                )
                """,
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
                "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active DESC)",
            ]),
            
            (6, "Add problem tags and categories", [
                """
                ALTER TABLE problems ADD COLUMN tags TEXT DEFAULT ''
                """,
                """
                ALTER TABLE problems ADD COLUMN category TEXT DEFAULT 'General'
                """,
                "CREATE INDEX IF NOT EXISTS idx_problems_category ON problems(category)",
                "CREATE INDEX IF NOT EXISTS idx_problems_tags ON problems(tags)",
            ]),
        ]
        
        # Apply migrations
        success_count = 0
        for version, description, commands in migrations:
            if self.apply_migration(version, description, commands):
                success_count += 1
        
        print(f"📊 Migration summary: {success_count}/{len(migrations)} migrations applied")
        
        # Run optimization after migrations
        if success_count > 0:
            self.optimize_database()
        
        return success_count == len(migrations)
    
    def optimize_database(self) -> None:
        """Run comprehensive database optimization."""
        print("🚀 Starting database optimization...")
        
        try:
            # Get optimizer and run optimizations
            optimizer = get_optimizer()
            optimizer.optimize_queries()
            optimizer.analyze_tables()
            
            # Vacuum database to reclaim space
            optimizer.vacuum_database()
            
            print("✅ Database optimization completed successfully")
            
        except Exception as e:
            print(f"❌ Database optimization failed: {e}")
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze database performance and return statistics."""
        print("📊 Analyzing database performance...")
        
        try:
            db = get_db()
            
            # Get table sizes
            table_stats = {}
            tables = ['problems', 'submissions', 'users', 'schema_version']
            
            for table in tables:
                try:
                    count_result = db.execute_single(f"SELECT COUNT(*) as count FROM {table}")
                    table_stats[table] = count_result['count'] if count_result else 0
                except:
                    table_stats[table] = 0
            
            # Get index usage statistics
            index_stats = db.execute_query("""
                SELECT name, tbl_name 
                FROM sqlite_master 
                WHERE type = 'index' AND name NOT LIKE 'sqlite_%'
                ORDER BY tbl_name, name
            """)
            
            # Get database file size
            db_size = os.path.getsize(self.database_path) if os.path.exists(self.database_path) else 0
            
            # Get query performance stats from optimizer
            optimizer = get_optimizer()
            query_stats = optimizer.get_query_performance_stats()
            
            performance_report = {
                'database_size_mb': round(db_size / 1024 / 1024, 2),
                'table_counts': table_stats,
                'index_count': len(index_stats),
                'indexes': [dict(row) for row in index_stats],
                'query_performance': query_stats,
                'schema_version': self.get_schema_version(),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            print("✅ Performance analysis completed")
            return performance_report
            
        except Exception as e:
            print(f"❌ Performance analysis failed: {e}")
            return {}
    
    def vacuum_database(self) -> None:
        """Vacuum database to reclaim space and optimize storage."""
        print("🧹 Starting database vacuum...")
        
        try:
            start_time = time.time()
            
            # Get file size before vacuum
            size_before = os.path.getsize(self.database_path) if os.path.exists(self.database_path) else 0
            
            # Run vacuum
            db = get_db()
            db.get_connection().execute("VACUUM")
            
            # Get file size after vacuum
            size_after = os.path.getsize(self.database_path) if os.path.exists(self.database_path) else 0
            
            end_time = time.time()
            space_saved = size_before - size_after
            
            print(f"✅ Database vacuum completed in {end_time - start_time:.2f} seconds")
            print(f"📦 Space saved: {space_saved / 1024 / 1024:.2f} MB")
            
        except Exception as e:
            print(f"❌ Database vacuum failed: {e}")
    
    def backup_database(self, backup_path: str = None) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Optional backup file path
            
        Returns:
            True if backup was successful
        """
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"database_backup_{timestamp}.db"
        
        print(f"💾 Creating database backup: {backup_path}")
        
        try:
            # Use SQLite backup API for consistent backup
            source_conn = sqlite3.connect(self.database_path)
            backup_conn = sqlite3.connect(backup_path)
            
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            backup_size = os.path.getsize(backup_path)
            print(f"✅ Database backup created successfully ({backup_size / 1024 / 1024:.2f} MB)")
            
            return True
            
        except Exception as e:
            print(f"❌ Database backup failed: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if restore was successful
        """
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        print(f"🔄 Restoring database from backup: {backup_path}")
        
        try:
            # Create backup of current database
            current_backup = f"database_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            self.backup_database(current_backup)
            
            # Restore from backup
            backup_conn = sqlite3.connect(backup_path)
            restore_conn = sqlite3.connect(self.database_path)
            
            backup_conn.backup(restore_conn)
            
            backup_conn.close()
            restore_conn.close()
            
            print(f"✅ Database restored successfully")
            print(f"📦 Previous database backed up as: {current_backup}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database restore failed: {e}")
            return False
    
    def check_integrity(self) -> bool:
        """Check database integrity."""
        print("🔍 Checking database integrity...")
        
        try:
            db = get_db()
            
            # Run integrity check
            result = db.execute_single("PRAGMA integrity_check")
            
            if result and result[0] == 'ok':
                print("✅ Database integrity check passed")
                return True
            else:
                print(f"❌ Database integrity check failed: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Database integrity check failed: {e}")
            return False


def main():
    """Main entry point for database optimizer script."""
    parser = argparse.ArgumentParser(
        description="CodeXam Database Optimizer and Migration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/database_optimizer.py --migrate          # Run database migrations
  python scripts/database_optimizer.py --optimize        # Optimize database performance
  python scripts/database_optimizer.py --analyze         # Analyze database performance
  python scripts/database_optimizer.py --vacuum          # Vacuum database to reclaim space
  python scripts/database_optimizer.py --backup          # Create database backup
  python scripts/database_optimizer.py --integrity       # Check database integrity
  python scripts/database_optimizer.py --warm-cache      # Warm application cache
  python scripts/database_optimizer.py --all             # Run all optimizations
        """
    )
    
    parser.add_argument("--migrate", action="store_true", help="Run database migrations")
    parser.add_argument("--optimize", action="store_true", help="Optimize database performance")
    parser.add_argument("--analyze", action="store_true", help="Analyze database performance")
    parser.add_argument("--vacuum", action="store_true", help="Vacuum database")
    parser.add_argument("--backup", action="store_true", help="Create database backup")
    parser.add_argument("--restore", type=str, help="Restore from backup file")
    parser.add_argument("--integrity", action="store_true", help="Check database integrity")
    parser.add_argument("--warm-cache", action="store_true", help="Warm application cache")
    parser.add_argument("--all", action="store_true", help="Run all optimizations")
    parser.add_argument("--database", type=str, help="Database file path")
    
    args = parser.parse_args()
    
    # Initialize migrator
    migrator = DatabaseMigrator(args.database)
    
    success = True
    
    try:
        if args.all:
            # Run all optimizations
            print("🚀 Running comprehensive database optimization...")
            
            success &= migrator.check_integrity()
            success &= migrator.run_migrations()
            migrator.optimize_database()
            migrator.vacuum_database()
            
            performance_report = migrator.analyze_performance()
            if performance_report:
                print("\n📊 Performance Report:")
                print(f"  Database Size: {performance_report['database_size_mb']} MB")
                print(f"  Schema Version: {performance_report['schema_version']}")
                print(f"  Total Problems: {performance_report['table_counts'].get('problems', 0)}")
                print(f"  Total Submissions: {performance_report['table_counts'].get('submissions', 0)}")
                print(f"  Total Users: {performance_report['table_counts'].get('users', 0)}")
                print(f"  Indexes: {performance_report['index_count']}")
            
            if args.warm_cache:
                warm_platform_cache()
            
        else:
            # Run specific operations
            if args.integrity:
                success &= migrator.check_integrity()
            
            if args.migrate:
                success &= migrator.run_migrations()
            
            if args.optimize:
                migrator.optimize_database()
            
            if args.vacuum:
                migrator.vacuum_database()
            
            if args.backup:
                success &= migrator.backup_database()
            
            if args.restore:
                success &= migrator.restore_database(args.restore)
            
            if args.analyze:
                performance_report = migrator.analyze_performance()
                if performance_report:
                    print("\n📊 Performance Analysis Results:")
                    import json
                    print(json.dumps(performance_report, indent=2))
            
            if args.warm_cache:
                warm_platform_cache()
        
        if success:
            print("\n🎉 Database optimization completed successfully!")
        else:
            print("\n⚠️  Some operations completed with warnings or errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()