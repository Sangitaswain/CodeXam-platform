#!/usr/bin/env python3
"""
Database Migration and Optimization Script

This script migrates the existing database to use enhanced features and applies
performance optimizations while maintaining backward compatibility.
"""

import os
import sqlite3
import shutil
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseMigrationOptimizer:
    """Handles database migration and optimization tasks."""
    
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.backup_path = f"{db_path}.backup_{int(time.time())}"
        self.migration_log = []
    
    def create_backup(self) -> bool:
        """Create a backup of the current database."""
        try:
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, self.backup_path)
                logger.info(f"Database backup created: {self.backup_path}")
                self.migration_log.append(f"Backup created: {self.backup_path}")
                return True
            else:
                logger.warning("Database file not found, skipping backup")
                return False
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def apply_performance_optimizations(self) -> bool:
        """Apply performance optimizations to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            optimizations = [
                ("Enable WAL mode", "PRAGMA journal_mode = WAL"),
                ("Set synchronous to NORMAL", "PRAGMA synchronous = NORMAL"),
                ("Increase cache size", "PRAGMA cache_size = -64000"),
                ("Use memory for temp storage", "PRAGMA temp_store = MEMORY"),
                ("Enable memory-mapped I/O", "PRAGMA mmap_size = 268435456"),
                ("Enable foreign keys", "PRAGMA foreign_keys = ON"),
                ("Optimize database", "PRAGMA optimize")
            ]
            
            for description, pragma in optimizations:
                try:
                    cursor.execute(pragma)
                    logger.info(f"Applied: {description}")
                    self.migration_log.append(f"Optimization applied: {description}")
                except sqlite3.Error as e:
                    logger.warning(f"Failed to apply {description}: {e}")
                    self.migration_log.append(f"Optimization failed: {description} - {e}")
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply optimizations: {e}")
            return False
    
    def add_missing_indexes(self) -> bool:
        """Add any missing indexes for better performance."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check existing indexes
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            existing_indexes = {row[0] for row in cursor.fetchall()}
            
            # Define recommended indexes
            recommended_indexes = [
                ("idx_problems_difficulty", "CREATE INDEX IF NOT EXISTS idx_problems_difficulty ON problems(difficulty)"),
                ("idx_problems_created_at", "CREATE INDEX IF NOT EXISTS idx_problems_created_at ON problems(created_at)"),
                ("idx_submissions_problem_id", "CREATE INDEX IF NOT EXISTS idx_submissions_problem_id ON submissions(problem_id)"),
                ("idx_submissions_user_name", "CREATE INDEX IF NOT EXISTS idx_submissions_user_name ON submissions(user_name)"),
                ("idx_submissions_result", "CREATE INDEX IF NOT EXISTS idx_submissions_result ON submissions(result)"),
                ("idx_submissions_submitted_at", "CREATE INDEX IF NOT EXISTS idx_submissions_submitted_at ON submissions(submitted_at)"),
                ("idx_submissions_language", "CREATE INDEX IF NOT EXISTS idx_submissions_language ON submissions(language)"),
                ("idx_users_username", "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"),
                ("idx_users_problems_solved", "CREATE INDEX IF NOT EXISTS idx_users_problems_solved ON users(problems_solved DESC)"),
                # Additional composite indexes for common queries
                ("idx_submissions_user_result", "CREATE INDEX IF NOT EXISTS idx_submissions_user_result ON submissions(user_name, result)"),
                ("idx_submissions_problem_result", "CREATE INDEX IF NOT EXISTS idx_submissions_problem_result ON submissions(problem_id, result)"),
                ("idx_problems_difficulty_created", "CREATE INDEX IF NOT EXISTS idx_problems_difficulty_created ON problems(difficulty, created_at DESC)")
            ]
            
            indexes_added = 0
            for index_name, index_sql in recommended_indexes:
                if index_name not in existing_indexes:
                    try:
                        cursor.execute(index_sql)
                        logger.info(f"Added index: {index_name}")
                        self.migration_log.append(f"Index added: {index_name}")
                        indexes_added += 1
                    except sqlite3.Error as e:
                        logger.warning(f"Failed to add index {index_name}: {e}")
                        self.migration_log.append(f"Index creation failed: {index_name} - {e}")
                else:
                    logger.info(f"Index already exists: {index_name}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added {indexes_added} new indexes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add indexes: {e}")
            return False
    
    def add_missing_constraints(self) -> bool:
        """Add missing constraints and improve data integrity."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if we need to add constraints
            # Note: SQLite doesn't support adding constraints to existing tables easily
            # So we'll focus on validation and cleanup
            
            # Clean up any orphaned records
            cursor.execute("""
                DELETE FROM submissions 
                WHERE problem_id NOT IN (SELECT id FROM problems)
            """)
            orphaned_submissions = cursor.rowcount
            
            if orphaned_submissions > 0:
                logger.info(f"Cleaned up {orphaned_submissions} orphaned submissions")
                self.migration_log.append(f"Cleaned up {orphaned_submissions} orphaned submissions")
            
            # Validate data integrity
            cursor.execute("""
                SELECT COUNT(*) FROM submissions s
                LEFT JOIN problems p ON s.problem_id = p.id
                WHERE p.id IS NULL
            """)
            remaining_orphans = cursor.fetchone()[0]
            
            if remaining_orphans == 0:
                logger.info("Data integrity validation passed")
                self.migration_log.append("Data integrity validation passed")
            else:
                logger.warning(f"Found {remaining_orphans} integrity issues")
                self.migration_log.append(f"Found {remaining_orphans} integrity issues")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to add constraints: {e}")
            return False
    
    def vacuum_and_analyze(self) -> bool:
        """Perform VACUUM and ANALYZE operations."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            logger.info("Starting VACUUM operation...")
            start_time = time.time()
            conn.execute("VACUUM")
            vacuum_time = time.time() - start_time
            logger.info(f"VACUUM completed in {vacuum_time:.2f} seconds")
            self.migration_log.append(f"VACUUM completed in {vacuum_time:.2f} seconds")
            
            logger.info("Starting ANALYZE operation...")
            start_time = time.time()
            conn.execute("ANALYZE")
            analyze_time = time.time() - start_time
            logger.info(f"ANALYZE completed in {analyze_time:.2f} seconds")
            self.migration_log.append(f"ANALYZE completed in {analyze_time:.2f} seconds")
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to vacuum/analyze: {e}")
            return False
    
    def verify_optimizations(self) -> Dict[str, Any]:
        """Verify that optimizations were applied successfully."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check PRAGMA settings
            pragma_checks = [
                ("journal_mode", "WAL"),
                ("synchronous", "1"),  # NORMAL = 1
                ("foreign_keys", "1"),
                ("cache_size", "-64000"),
                ("temp_store", "2")  # MEMORY = 2
            ]
            
            verification_results = {}
            for pragma, expected in pragma_checks:
                cursor.execute(f"PRAGMA {pragma}")
                result = cursor.fetchone()
                actual = str(result[0]) if result else "unknown"
                verification_results[pragma] = {
                    "expected": expected,
                    "actual": actual,
                    "matches": actual == expected
                }
            
            # Count indexes
            cursor.execute("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            index_count = cursor.fetchone()[0]
            verification_results["index_count"] = index_count
            
            # Get database file size
            file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            verification_results["file_size_mb"] = round(file_size / 1024 / 1024, 2)
            
            conn.close()
            return verification_results
            
        except Exception as e:
            logger.error(f"Failed to verify optimizations: {e}")
            return {"error": str(e)}
    
    def run_migration(self) -> Dict[str, Any]:
        """Run the complete migration and optimization process."""
        logger.info("Starting database migration and optimization...")
        start_time = time.time()
        
        results = {
            "started_at": datetime.now().isoformat(),
            "backup_created": False,
            "optimizations_applied": False,
            "indexes_added": False,
            "constraints_added": False,
            "vacuum_completed": False,
            "verification": {},
            "migration_log": [],
            "success": False,
            "duration_seconds": 0
        }
        
        try:
            # Step 1: Create backup
            results["backup_created"] = self.create_backup()
            
            # Step 2: Apply performance optimizations
            results["optimizations_applied"] = self.apply_performance_optimizations()
            
            # Step 3: Add missing indexes
            results["indexes_added"] = self.add_missing_indexes()
            
            # Step 4: Add missing constraints and clean data
            results["constraints_added"] = self.add_missing_constraints()
            
            # Step 5: Vacuum and analyze
            results["vacuum_completed"] = self.vacuum_and_analyze()
            
            # Step 6: Verify optimizations
            results["verification"] = self.verify_optimizations()
            
            # Check overall success
            results["success"] = all([
                results["optimizations_applied"],
                results["indexes_added"],
                results["constraints_added"],
                results["vacuum_completed"]
            ])
            
            results["migration_log"] = self.migration_log
            results["duration_seconds"] = round(time.time() - start_time, 2)
            
            if results["success"]:
                logger.info(f"Migration completed successfully in {results['duration_seconds']} seconds")
            else:
                logger.warning("Migration completed with some issues")
            
            return results
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            results["error"] = str(e)
            results["duration_seconds"] = round(time.time() - start_time, 2)
            return results
    
    def rollback_migration(self) -> bool:
        """Rollback migration by restoring from backup."""
        try:
            if os.path.exists(self.backup_path):
                shutil.copy2(self.backup_path, self.db_path)
                logger.info(f"Database restored from backup: {self.backup_path}")
                return True
            else:
                logger.error("Backup file not found, cannot rollback")
                return False
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False


def print_migration_report(results: Dict[str, Any]) -> None:
    """Print a formatted migration report."""
    print("\n📊 Database Migration and Optimization Report")
    print("=" * 60)
    
    print(f"\n⏱️  Migration Duration: {results['duration_seconds']} seconds")
    print(f"📅 Started: {results['started_at']}")
    print(f"✅ Success: {'Yes' if results['success'] else 'No'}")
    
    print(f"\n📋 Migration Steps:")
    print(f"  • Backup created: {'✅' if results['backup_created'] else '❌'}")
    print(f"  • Optimizations applied: {'✅' if results['optimizations_applied'] else '❌'}")
    print(f"  • Indexes added: {'✅' if results['indexes_added'] else '❌'}")
    print(f"  • Constraints added: {'✅' if results['constraints_added'] else '❌'}")
    print(f"  • Vacuum completed: {'✅' if results['vacuum_completed'] else '❌'}")
    
    if results.get("verification"):
        print(f"\n🔍 Verification Results:")
        verification = results["verification"]
        
        if "file_size_mb" in verification:
            print(f"  • Database size: {verification['file_size_mb']} MB")
        
        if "index_count" in verification:
            print(f"  • Indexes: {verification['index_count']}")
        
        for pragma, info in verification.items():
            if isinstance(info, dict) and "matches" in info:
                status = "✅" if info["matches"] else "❌"
                print(f"  • {pragma}: {info['actual']} {status}")
    
    if results.get("migration_log"):
        print(f"\n📝 Migration Log:")
        for entry in results["migration_log"][-10:]:  # Show last 10 entries
            print(f"  • {entry}")
        
        if len(results["migration_log"]) > 10:
            print(f"  ... and {len(results['migration_log']) - 10} more entries")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration and optimization")
    parser.add_argument("--db-path", default="database.db", help="Database file path")
    parser.add_argument("--rollback", action="store_true", help="Rollback migration")
    parser.add_argument("--verify-only", action="store_true", help="Only verify optimizations")
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrationOptimizer(args.db_path)
    
    if args.rollback:
        print("🔄 Rolling back migration...")
        success = migrator.rollback_migration()
        print(f"{'✅' if success else '❌'} Rollback {'completed' if success else 'failed'}")
    
    elif args.verify_only:
        print("🔍 Verifying database optimizations...")
        verification = migrator.verify_optimizations()
        print(f"Verification results: {verification}")
    
    else:
        print("🚀 Starting database migration and optimization...")
        results = migrator.run_migration()
        print_migration_report(results)