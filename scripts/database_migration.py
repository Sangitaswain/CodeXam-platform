#!/usr/bin/env python3
"""
Database Migration Script for CodeXam Platform

This script handles database migrations, index creation, and performance optimizations.
It can be run standalone or integrated into the application startup process.

Usage:
    python scripts/database_migration.py --create-indexes
    python scripts/database_migration.py --optimize
    python scripts/database_migration.py --analyze
    python scripts/database_migration.py --all

@version 1.0.0
@author CodeXam Development Team
"""

import argparse
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database import get_db
from database_optimization import initialize_database_optimization


class DatabaseMigration:
    """Database migration and optimization manager."""
    
    def __init__(self, database_path: str = "database.db"):
        """
        Initialize database migration manager.
        
        Args:
            database_path: Path to the SQLite database file
        """
        self.database_path = database_path
        self.migration_log = []
    
    def create_indexes(self) -> bool:
        """
        Create performance indexes for the database.
        
        Returns:
            True if successful
        """
        print("🔧 Creating database indexes...")
        
        indexes = [
            # Problems table indexes
            {
                'name': 'idx_problems_difficulty',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_problems_difficulty ON problems(difficulty)',
                'description': 'Index on problems difficulty for filtering'
            },
            {
                'name': 'idx_problems_created_at',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_problems_created_at ON problems(created_at DESC)',
                'description': 'Index on problems creation date for sorting'
            },
            {
                'name': 'idx_problems_title',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_problems_title ON problems(title)',
                'description': 'Index on problems title for searching'
            },
            
            # Submissions table indexes
            {
                'name': 'idx_submissions_user_name',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_submissions_user_name ON submissions(user_name)',
                'description': 'Index on submissions user_name for user queries'
            },
            {
                'name': 'idx_submissions_problem_id',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_submissions_problem_id ON submissions(problem_id)',
                'description': 'Index on submissions problem_id for problem queries'
            },
            {
                'name': 'idx_submissions_result',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_submissions_result ON submissions(result)',
                'description': 'Index on submissions result for filtering'
            },
            {
                'name': 'idx_submissions_submitted_at',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_submissions_submitted_at ON submissions(submitted_at DESC)',
                'description': 'Index on submissions timestamp for sorting'
            },
            {
                'name': 'idx_submissions_language',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_submissions_language ON submissions(language)',
                'description': 'Index on submissions language for statistics'
            },
            
            # Composite indexes for common query patterns
            {
                'name': 'idx_submissions_user_problem',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_submissions_user_problem ON submissions(user_name, problem_id)',
                'description': 'Composite index for user-problem queries'
            },
            {
                'name': 'idx_submissions_problem_result',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_submissions_problem_result ON submissions(problem_id, result)',
                'description': 'Composite index for problem success rate queries'
            },
            {
                'name': 'idx_submissions_user_result',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_submissions_user_result ON submissions(user_name, result)',
                'description': 'Composite index for user success rate queries'
            },
            {
                'name': 'idx_submissions_recent_pass',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_submissions_recent_pass ON submissions(submitted_at DESC, result) WHERE result = "PASS"',
                'description': 'Partial index for recent successful submissions'
            },
            
            # Users table indexes (if exists)
            {
                'name': 'idx_users_username',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)',
                'description': 'Index on users username (if users table exists)'
            },
            {
                'name': 'idx_users_created_at',
                'sql': 'CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC)',
                'description': 'Index on users creation date (if users table exists)'
            }
        ]
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            created_count = 0
            skipped_count = 0
            
            for index in indexes:
                try:
                    start_time = time.time()
                    cursor.execute(index['sql'])
                    execution_time = time.time() - start_time
                    
                    created_count += 1
                    self.migration_log.append({
                        'action': 'CREATE_INDEX',
                        'name': index['name'],
                        'description': index['description'],
                        'execution_time': execution_time,
                        'status': 'SUCCESS'
                    })
                    
                    print(f"  ✅ {index['name']}: {index['description']} ({execution_time:.3f}s)")
                    
                except sqlite3.Error as e:
                    if "already exists" in str(e).lower():
                        skipped_count += 1
                        print(f"  ⏭️  {index['name']}: Already exists")
                    else:
                        print(f"  ❌ {index['name']}: Failed - {e}")
                        self.migration_log.append({
                            'action': 'CREATE_INDEX',
                            'name': index['name'],
                            'description': index['description'],
                            'error': str(e),
                            'status': 'FAILED'
                        })
            
            conn.commit()
            conn.close()
            
            print(f"\n📊 Index creation summary:")
            print(f"  • Created: {created_count}")
            print(f"  • Skipped: {skipped_count}")
            print(f"  • Total: {len(indexes)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Index creation failed: {e}")
            return False
    
    def optimize_database(self) -> bool:
        """
        Optimize database with PRAGMA settings and ANALYZE.
        
        Returns:
            True if successful
        """
        print("⚡ Optimizing database...")
        
        optimizations = [
            {
                'name': 'Enable WAL mode',
                'sql': 'PRAGMA journal_mode = WAL',
                'description': 'Enable Write-Ahead Logging for better concurrency'
            },
            {
                'name': 'Set synchronous mode',
                'sql': 'PRAGMA synchronous = NORMAL',
                'description': 'Balance between safety and performance'
            },
            {
                'name': 'Set cache size',
                'sql': 'PRAGMA cache_size = -64000',
                'description': 'Set 64MB cache size'
            },
            {
                'name': 'Enable memory temp store',
                'sql': 'PRAGMA temp_store = MEMORY',
                'description': 'Store temporary tables in memory'
            },
            {
                'name': 'Set memory map size',
                'sql': 'PRAGMA mmap_size = 268435456',
                'description': 'Set 256MB memory-mapped I/O'
            },
            {
                'name': 'Enable foreign keys',
                'sql': 'PRAGMA foreign_keys = ON',
                'description': 'Enable foreign key constraints'
            }
        ]
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            for opt in optimizations:
                try:
                    start_time = time.time()
                    cursor.execute(opt['sql'])
                    execution_time = time.time() - start_time
                    
                    self.migration_log.append({
                        'action': 'OPTIMIZE',
                        'name': opt['name'],
                        'description': opt['description'],
                        'execution_time': execution_time,
                        'status': 'SUCCESS'
                    })
                    
                    print(f"  ✅ {opt['name']}: {opt['description']} ({execution_time:.3f}s)")
                    
                except sqlite3.Error as e:
                    print(f"  ❌ {opt['name']}: Failed - {e}")
                    self.migration_log.append({
                        'action': 'OPTIMIZE',
                        'name': opt['name'],
                        'description': opt['description'],
                        'error': str(e),
                        'status': 'FAILED'
                    })
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Database optimization failed: {e}")
            return False
    
    def analyze_database(self) -> bool:
        """
        Analyze database for query optimization.
        
        Returns:
            True if successful
        """
        print("📊 Analyzing database...")
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            start_time = time.time()
            cursor.execute('ANALYZE')
            execution_time = time.time() - start_time
            
            conn.commit()
            conn.close()
            
            self.migration_log.append({
                'action': 'ANALYZE',
                'name': 'Database Analysis',
                'description': 'Update query planner statistics',
                'execution_time': execution_time,
                'status': 'SUCCESS'
            })
            
            print(f"  ✅ Database analysis completed ({execution_time:.3f}s)")
            return True
            
        except Exception as e:
            print(f"❌ Database analysis failed: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information and statistics.
        
        Returns:
            Database information dictionary
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get database size
            db_size = os.path.getsize(self.database_path) if os.path.exists(self.database_path) else 0
            
            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get index information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            
            # Get row counts
            table_stats = {}
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_stats[table] = count
                except sqlite3.Error:
                    table_stats[table] = 'N/A'
            
            conn.close()
            
            return {
                'database_path': self.database_path,
                'database_size_mb': round(db_size / (1024 * 1024), 2),
                'tables': tables,
                'table_count': len(tables),
                'indexes': indexes,
                'index_count': len(indexes),
                'table_stats': table_stats,
                'last_analyzed': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to get database info: {e}")
            return {}
    
    def print_migration_log(self) -> None:
        """Print migration log summary."""
        if not self.migration_log:
            print("📝 No migration actions performed")
            return
        
        print("\n📝 Migration Log:")
        print("=" * 80)
        
        success_count = 0
        failed_count = 0
        total_time = 0
        
        for entry in self.migration_log:
            status_icon = "✅" if entry['status'] == 'SUCCESS' else "❌"
            action = entry['action']
            name = entry['name']
            description = entry.get('description', '')
            
            if entry['status'] == 'SUCCESS':
                success_count += 1
                exec_time = entry.get('execution_time', 0)
                total_time += exec_time
                print(f"{status_icon} [{action}] {name}: {description} ({exec_time:.3f}s)")
            else:
                failed_count += 1
                error = entry.get('error', 'Unknown error')
                print(f"{status_icon} [{action}] {name}: {error}")
        
        print("=" * 80)
        print(f"📊 Summary: {success_count} successful, {failed_count} failed, {total_time:.3f}s total")


def main():
    """Main entry point for database migration script."""
    parser = argparse.ArgumentParser(
        description="CodeXam Database Migration and Optimization Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/database_migration.py --create-indexes
  python scripts/database_migration.py --optimize
  python scripts/database_migration.py --analyze
  python scripts/database_migration.py --all
  python scripts/database_migration.py --info
        """
    )
    
    parser.add_argument(
        '--create-indexes', 
        action='store_true',
        help='Create performance indexes'
    )
    parser.add_argument(
        '--optimize', 
        action='store_true',
        help='Optimize database with PRAGMA settings'
    )
    parser.add_argument(
        '--analyze', 
        action='store_true',
        help='Analyze database for query optimization'
    )
    parser.add_argument(
        '--all', 
        action='store_true',
        help='Run all optimization steps'
    )
    parser.add_argument(
        '--info', 
        action='store_true',
        help='Show database information'
    )
    parser.add_argument(
        '--database', 
        type=str,
        default='database.db',
        help='Database file path (default: database.db)'
    )
    
    args = parser.parse_args()
    
    # Check if database exists
    if not os.path.exists(args.database):
        print(f"❌ Database file not found: {args.database}")
        print("   Please run 'python init_db.py' first to create the database.")
        return 1
    
    # Initialize migration manager
    migration = DatabaseMigration(args.database)
    
    print(f"🚀 CodeXam Database Migration Tool")
    print(f"📁 Database: {args.database}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = True
    
    # Show database info
    if args.info or args.all:
        db_info = migration.get_database_info()
        if db_info:
            print("📊 Database Information:")
            print(f"  • Size: {db_info['database_size_mb']} MB")
            print(f"  • Tables: {db_info['table_count']} ({', '.join(db_info['tables'])})")
            print(f"  • Indexes: {db_info['index_count']}")
            print(f"  • Table Statistics:")
            for table, count in db_info['table_stats'].items():
                print(f"    - {table}: {count} rows")
            print()
    
    # Create indexes
    if args.create_indexes or args.all:
        if not migration.create_indexes():
            success = False
        print()
    
    # Optimize database
    if args.optimize or args.all:
        if not migration.optimize_database():
            success = False
        print()
    
    # Analyze database
    if args.analyze or args.all:
        if not migration.analyze_database():
            success = False
        print()
    
    # Print migration log
    migration.print_migration_log()
    
    print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("🎉 Database migration completed successfully!")
        return 0
    else:
        print("❌ Database migration completed with errors!")
        return 1


if __name__ == "__main__":
    sys.exit(main())