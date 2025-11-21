#!/usr/bin/env python3
"""
Database Optimization Analyzer

This script analyzes the database for performance issues and optimization opportunities.
"""

import sqlite3
import os
import time
from typing import List, Dict, Any, Tuple
from contextlib import contextmanager

class DatabaseOptimizationAnalyzer:
    """Analyzes database for optimization opportunities."""
    
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.issues = []
        self.recommendations = []
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def analyze_query_performance(self) -> Dict[str, Any]:
        """Analyze query performance and identify slow queries."""
        performance_issues = []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Test common queries and measure performance
            test_queries = [
                ("Get all problems", "SELECT * FROM problems ORDER BY created_at DESC"),
                ("Get submissions by user", "SELECT * FROM submissions WHERE user_name = 'testuser' ORDER BY submitted_at DESC"),
                ("Get problem with submissions", """
                    SELECT p.*, COUNT(s.id) as submission_count 
                    FROM problems p 
                    LEFT JOIN submissions s ON p.id = s.problem_id 
                    GROUP BY p.id
                """),
                ("Get leaderboard", """
                    SELECT user_name, COUNT(CASE WHEN result = 'PASS' THEN 1 END) as solved_count,
                           COUNT(*) as total_submissions
                    FROM submissions 
                    WHERE user_name != 'Anonymous'
                    GROUP BY user_name 
                    ORDER BY solved_count DESC, total_submissions ASC
                    LIMIT 10
                """),
                ("Get recent submissions", """
                    SELECT s.*, p.title as problem_title
                    FROM submissions s
                    LEFT JOIN problems p ON s.problem_id = p.id
                    ORDER BY s.submitted_at DESC
                    LIMIT 20
                """)
            ]
            
            for query_name, query in test_queries:
                start_time = time.time()
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    end_time = time.time()
                    
                    execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    
                    if execution_time > 100:  # Flag queries taking more than 100ms
                        performance_issues.append({
                            "query": query_name,
                            "execution_time_ms": round(execution_time, 2),
                            "result_count": len(results),
                            "issue": "Slow query execution"
                        })
                    
                except Exception as e:
                    performance_issues.append({
                        "query": query_name,
                        "error": str(e),
                        "issue": "Query execution failed"
                    })
        
        return {
            "performance_issues": performance_issues,
            "total_issues": len(performance_issues)
        }
    
    def analyze_table_statistics(self) -> Dict[str, Any]:
        """Analyze table statistics and identify potential issues."""
        table_stats = {}
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                
                # Get table size (approximate) - simplified approach
                cursor.execute(f"SELECT COUNT(*) * 1000 FROM {table}")  # Rough estimate
                size_result = cursor.fetchone()[0]
                table_size = size_result if size_result else 0
                
                # Check for unused space
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                table_stats[table] = {
                    "row_count": row_count,
                    "estimated_size_bytes": table_size,
                    "column_count": len(columns),
                    "columns": [col[1] for col in columns]
                }
                
                # Check for potential issues
                if row_count > 10000:
                    self.issues.append(f"Large table: {table} has {row_count} rows - consider partitioning or archiving")
                
                if table_size > 10 * 1024 * 1024:  # 10MB
                    self.issues.append(f"Large table size: {table} is approximately {table_size / 1024 / 1024:.1f}MB")
        
        return table_stats
    
    def analyze_index_usage(self) -> Dict[str, Any]:
        """Analyze index usage and effectiveness."""
        index_analysis = {}
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all indexes
            cursor.execute("""
                SELECT name, tbl_name, sql 
                FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            indexes = cursor.fetchall()
            
            for index in indexes:
                index_name, table_name, sql = index
                
                # Analyze index effectiveness (simplified)
                try:
                    # Check if index is being used in common queries
                    cursor.execute(f"EXPLAIN QUERY PLAN SELECT * FROM {table_name} WHERE ROWID = 1")
                    query_plan = cursor.fetchall()
                    
                    index_analysis[index_name] = {
                        "table": table_name,
                        "sql": sql,
                        "query_plan_sample": [dict(row) for row in query_plan]
                    }
                    
                except Exception as e:
                    index_analysis[index_name] = {
                        "table": table_name,
                        "sql": sql,
                        "error": str(e)
                    }
        
        return index_analysis
    
    def check_database_integrity(self) -> Dict[str, Any]:
        """Check database integrity and consistency."""
        integrity_issues = []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check database integrity
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchall()
            
            if integrity_result[0][0] != "ok":
                integrity_issues.extend([row[0] for row in integrity_result])
            
            # Check foreign key constraints
            cursor.execute("PRAGMA foreign_key_check")
            fk_violations = cursor.fetchall()
            
            if fk_violations:
                integrity_issues.extend([f"Foreign key violation: {row}" for row in fk_violations])
            
            # Check for orphaned records
            cursor.execute("""
                SELECT COUNT(*) FROM submissions s 
                LEFT JOIN problems p ON s.problem_id = p.id 
                WHERE p.id IS NULL
            """)
            orphaned_submissions = cursor.fetchone()[0]
            
            if orphaned_submissions > 0:
                integrity_issues.append(f"Found {orphaned_submissions} orphaned submissions")
        
        return {
            "integrity_issues": integrity_issues,
            "has_issues": len(integrity_issues) > 0
        }
    
    def generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on analysis."""
        recommendations = []
        
        # Database configuration recommendations
        recommendations.extend([
            "Enable WAL mode for better concurrency: PRAGMA journal_mode = WAL",
            "Optimize cache size: PRAGMA cache_size = -64000 (64MB)",
            "Use memory for temp storage: PRAGMA temp_store = MEMORY",
            "Enable memory-mapped I/O: PRAGMA mmap_size = 268435456 (256MB)",
            "Regular VACUUM to reclaim space: VACUUM",
            "Update table statistics: ANALYZE"
        ])
        
        # Query optimization recommendations
        recommendations.extend([
            "Use prepared statements for repeated queries",
            "Implement connection pooling for high-traffic scenarios",
            "Consider adding composite indexes for complex WHERE clauses",
            "Use LIMIT clauses for large result sets",
            "Implement pagination for large data displays"
        ])
        
        # Maintenance recommendations
        recommendations.extend([
            "Regular database backups",
            "Monitor database file size growth",
            "Archive old submission data if needed",
            "Regular integrity checks",
            "Monitor query performance in production"
        ])
        
        return recommendations
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete database analysis."""
        print("🔍 Starting database optimization analysis...")
        
        # Run all analyses
        performance_analysis = self.analyze_query_performance()
        table_stats = self.analyze_table_statistics()
        index_analysis = self.analyze_index_usage()
        integrity_check = self.check_database_integrity()
        recommendations = self.generate_optimization_recommendations()
        
        return {
            "performance": performance_analysis,
            "table_statistics": table_stats,
            "index_analysis": index_analysis,
            "integrity": integrity_check,
            "issues": self.issues,
            "recommendations": recommendations,
            "summary": {
                "total_issues": len(self.issues) + performance_analysis["total_issues"],
                "tables_analyzed": len(table_stats),
                "indexes_analyzed": len(index_analysis),
                "integrity_ok": not integrity_check["has_issues"]
            }
        }

def print_analysis_report(analysis: Dict[str, Any]) -> None:
    """Print formatted analysis report."""
    print("\n📊 Database Optimization Analysis Report")
    print("=" * 60)
    
    # Summary
    summary = analysis["summary"]
    print(f"\n📋 Summary:")
    print(f"  • Tables analyzed: {summary['tables_analyzed']}")
    print(f"  • Indexes analyzed: {summary['indexes_analyzed']}")
    print(f"  • Total issues found: {summary['total_issues']}")
    print(f"  • Database integrity: {'✅ OK' if summary['integrity_ok'] else '❌ Issues found'}")
    
    # Performance issues
    perf_issues = analysis["performance"]["performance_issues"]
    if perf_issues:
        print(f"\n⚡ Performance Issues ({len(perf_issues)}):")
        for issue in perf_issues:
            if "execution_time_ms" in issue:
                print(f"  • {issue['query']}: {issue['execution_time_ms']}ms ({issue['result_count']} results)")
            else:
                print(f"  • {issue['query']}: {issue.get('error', issue['issue'])}")
    
    # Table statistics
    print(f"\n📊 Table Statistics:")
    for table, stats in analysis["table_statistics"].items():
        size_mb = stats["estimated_size_bytes"] / 1024 / 1024
        print(f"  • {table}: {stats['row_count']} rows, ~{size_mb:.1f}MB, {stats['column_count']} columns")
    
    # Issues
    if analysis["issues"]:
        print(f"\n⚠️  Issues ({len(analysis['issues'])}):")
        for issue in analysis["issues"]:
            print(f"  • {issue}")
    
    # Integrity issues
    if analysis["integrity"]["integrity_issues"]:
        print(f"\n🔒 Integrity Issues:")
        for issue in analysis["integrity"]["integrity_issues"]:
            print(f"  • {issue}")
    
    # Recommendations
    print(f"\n💡 Optimization Recommendations:")
    for i, rec in enumerate(analysis["recommendations"][:10], 1):  # Show top 10
        print(f"  {i}. {rec}")
    
    if len(analysis["recommendations"]) > 10:
        print(f"  ... and {len(analysis['recommendations']) - 10} more recommendations")

if __name__ == "__main__":
    if not os.path.exists("database.db"):
        print("❌ Database file not found!")
        exit(1)
    
    analyzer = DatabaseOptimizationAnalyzer()
    analysis = analyzer.run_full_analysis()
    print_analysis_report(analysis)