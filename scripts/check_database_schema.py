#!/usr/bin/env python3
"""
Database Schema Checker

This script examines the current database schema and identifies potential issues.
Provides comprehensive analysis of table structure, indexes, and potential problems.
"""

import os
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import Config
except ImportError:
    # Fallback if config not available
    class Config:
        DATABASE_PATH = "database.db"

# Constants for schema validation
EXPECTED_TABLES = {
    'problems': ['id', 'title', 'description', 'difficulty', 'function_signatures', 'sample_input', 'sample_output', 'created_at'],
    'submissions': ['id', 'problem_id', 'user_name', 'code', 'language', 'result', 'execution_time', 'submitted_at', 'error_message']
}

REQUIRED_INDEXES = [
    ('submissions', 'problem_id'),
    ('submissions', 'user_name'),
    ('submissions', 'result'),
    ('problems', 'difficulty')
]

FOREIGN_KEY_RELATIONSHIPS = {
    'submissions.problem_id': 'problems.id'
}

class DatabaseSchemaChecker:
    """Database schema validation and analysis tool."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the schema checker.
        
        Args:
            db_path: Path to the database file. Uses config default if None.
        """
        self.db_path = db_path or getattr(Config, 'DATABASE_PATH', 'database.db')
        
    def _get_database_connection(self) -> sqlite3.Connection:
        """Get a database connection with proper configuration.
        
        Returns:
            Configured SQLite connection
            
        Raises:
            FileNotFoundError: If database file doesn't exist
            sqlite3.Error: If connection fails
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
            
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

def check_database_schema(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Check database schema and identify issues.
    
    Args:
        db_path: Path to database file. Uses default if None.
        
    Returns:
        Dictionary containing schema analysis results
    """
    checker = DatabaseSchemaChecker(db_path)
    return checker.analyze_schema()

def validate_database_health(db_path: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Quick health check for database schema.
    
    Args:
        db_path: Path to database file
        
    Returns:
        Tuple of (is_healthy, list_of_critical_issues)
    """
    schema_info = check_database_schema(db_path)
    
    if "error" in schema_info:
        return False, [schema_info["error"]]
    
    critical_issues = [i for i in schema_info["issues"] if i.startswith("❌")]
    return len(critical_issues) == 0, critical_issues

class DatabaseSchemaChecker:
    """Database schema validation and analysis tool."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the schema checker."""
        self.db_path = db_path or getattr(Config, 'DATABASE_PATH', 'database.db')
        
    def _get_database_connection(self) -> sqlite3.Connection:
        """Get a database connection with proper configuration."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
            
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def analyze_schema(self) -> Dict[str, Any]:
        """Analyze database schema and identify issues.
        
        Returns:
            Dictionary containing comprehensive schema analysis
        """
        try:
            with self._get_database_connection() as conn:
                cursor = conn.cursor()
                
                schema_info = {
                    "database_path": self.db_path,
                    "tables": self._get_table_list(cursor),
                    "table_details": {},
                    "indexes": self._get_index_info(cursor),
                    "issues": [],
                    "recommendations": []
                }
                
                # Analyze each table
                for table in schema_info["tables"]:
                    schema_info["table_details"][table] = self._analyze_table(cursor, table)
                
                # Perform comprehensive issue detection
                schema_info["issues"] = self._detect_schema_issues(schema_info)
                schema_info["recommendations"] = self._generate_recommendations(schema_info)
                
                return schema_info
                
        except FileNotFoundError as e:
            return {"error": f"Database not found: {e}"}
        except sqlite3.Error as e:
            return {"error": f"Database error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}
    
    def _get_table_list(self, cursor: sqlite3.Cursor) -> List[str]:
        """Get list of all user tables in the database."""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        return [row[0] for row in cursor.fetchall()]
    
    def _analyze_table(self, cursor: sqlite3.Cursor, table_name: str) -> Dict[str, Any]:
        """Analyze a specific table structure and content.
        
        Args:
            cursor: Database cursor
            table_name: Name of table to analyze
            
        Returns:
            Dictionary containing table analysis
        """
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        # Get foreign key information
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        foreign_keys = cursor.fetchall()
        
        return {
            "columns": [
                {
                    "name": col[1],
                    "type": col[2],
                    "not_null": bool(col[3]),
                    "default": col[4],
                    "primary_key": bool(col[5])
                }
                for col in columns
            ],
            "row_count": row_count,
            "foreign_keys": [
                {
                    "column": fk[3],
                    "references_table": fk[2],
                    "references_column": fk[4]
                }
                for fk in foreign_keys
            ]
        }
    
    def _get_index_info(self, cursor: sqlite3.Cursor) -> List[Dict[str, Any]]:
        """Get information about all indexes in the database."""
        cursor.execute("""
            SELECT name, tbl_name, sql 
            FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        indexes = cursor.fetchall()
        
        return [
            {
                "name": idx[0],
                "table": idx[1],
                "sql": idx[2]
            }
            for idx in indexes
        ]
    
    def _detect_schema_issues(self, schema_info: Dict[str, Any]) -> List[str]:
        """Detect potential issues in the database schema.
        
        Args:
            schema_info: Schema analysis results
            
        Returns:
            List of identified issues
        """
        issues = []
        
        # Check for missing expected tables
        issues.extend(self._check_missing_tables(schema_info))
        
        # Check for missing primary keys
        issues.extend(self._check_primary_keys(schema_info))
        
        # Check for missing indexes on foreign keys
        issues.extend(self._check_foreign_key_indexes(schema_info))
        
        # Check for missing required columns
        issues.extend(self._check_required_columns(schema_info))
        
        # Check for performance issues
        issues.extend(self._check_performance_issues(schema_info))
        
        return issues
    
    def _check_missing_tables(self, schema_info: Dict[str, Any]) -> List[str]:
        """Check for missing expected tables."""
        issues = []
        existing_tables = set(schema_info["tables"])
        expected_tables = set(EXPECTED_TABLES.keys())
        
        missing_tables = expected_tables - existing_tables
        for table in missing_tables:
            issues.append(f"❌ Missing expected table: {table}")
            
        return issues
    
    def _check_primary_keys(self, schema_info: Dict[str, Any]) -> List[str]:
        """Check for tables without primary keys."""
        issues = []
        
        for table, details in schema_info["table_details"].items():
            has_pk = any(col["primary_key"] for col in details["columns"])
            if not has_pk:
                issues.append(f"⚠️  Table '{table}' has no primary key")
                
        return issues
    
    def _check_foreign_key_indexes(self, schema_info: Dict[str, Any]) -> List[str]:
        """Check for missing indexes on foreign key columns."""
        issues = []
        
        for table, details in schema_info["table_details"].items():
            for col in details["columns"]:
                # Check if this looks like a foreign key
                if col["name"].endswith("_id") and col["name"] != "id":
                    # Check if there's an index on this column
                    index_exists = any(
                        table == idx["table"] and col["name"] in (idx["sql"] or "")
                        for idx in schema_info["indexes"]
                    )
                    if not index_exists:
                        issues.append(f"🔍 Missing index on foreign key: {table}.{col['name']}")
                        
        return issues
    
    def _check_required_columns(self, schema_info: Dict[str, Any]) -> List[str]:
        """Check for missing required columns in expected tables."""
        issues = []
        
        for table, expected_columns in EXPECTED_TABLES.items():
            if table in schema_info["table_details"]:
                existing_columns = {col["name"] for col in schema_info["table_details"][table]["columns"]}
                missing_columns = set(expected_columns) - existing_columns
                
                for column in missing_columns:
                    issues.append(f"📋 Missing required column: {table}.{column}")
                    
        return issues
    
    def _check_performance_issues(self, schema_info: Dict[str, Any]) -> List[str]:
        """Check for potential performance issues."""
        issues = []
        
        # Check for large tables without proper indexes
        for table, details in schema_info["table_details"].items():
            if details["row_count"] > 1000:  # Arbitrary threshold
                table_indexes = [idx for idx in schema_info["indexes"] if idx["table"] == table]
                if len(table_indexes) < 2:  # Should have at least PK + one other index
                    issues.append(f"⚡ Large table '{table}' ({details['row_count']} rows) may need more indexes")
                    
        return issues
    
    def _generate_recommendations(self, schema_info: Dict[str, Any]) -> List[str]:
        """Generate recommendations for schema improvements.
        
        Args:
            schema_info: Schema analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Recommend missing indexes
        for table_name, column_name in REQUIRED_INDEXES:
            if table_name in schema_info["table_details"]:
                index_exists = any(
                    table_name == idx["table"] and column_name in (idx["sql"] or "")
                    for idx in schema_info["indexes"]
                )
                if not index_exists:
                    recommendations.append(f"💡 Consider adding index: CREATE INDEX idx_{table_name}_{column_name} ON {table_name}({column_name})")
        
        # Recommend foreign key constraints
        for fk_def, target in FOREIGN_KEY_RELATIONSHIPS.items():
            table, column = fk_def.split('.')
            target_table, target_column = target.split('.')
            
            if table in schema_info["table_details"]:
                table_details = schema_info["table_details"][table]
                has_fk = any(
                    fk["column"] == column and fk["references_table"] == target_table
                    for fk in table_details["foreign_keys"]
                )
                if not has_fk:
                    recommendations.append(f"🔗 Consider adding foreign key constraint: {table}.{column} -> {target}")
        
        return recommendations

class SchemaReporter:
    """Handles formatting and display of schema analysis results."""
    
    @staticmethod
    def print_schema_report(schema_info: Dict[str, Any], verbose: bool = False) -> None:
        """Print a comprehensive formatted schema report.
        
        Args:
            schema_info: Schema analysis results
            verbose: Whether to include detailed information
        """
        if "error" in schema_info:
            print(f"❌ Error: {schema_info['error']}")
            return
        
        SchemaReporter._print_header(schema_info)
        SchemaReporter._print_tables_summary(schema_info, verbose)
        SchemaReporter._print_indexes_summary(schema_info, verbose)
        SchemaReporter._print_issues_summary(schema_info)
        SchemaReporter._print_recommendations(schema_info)
        SchemaReporter._print_footer(schema_info)
    
    @staticmethod
    def _print_header(schema_info: Dict[str, Any]) -> None:
        """Print report header."""
        print("\n" + "=" * 70)
        print("📊 CodeXam Database Schema Analysis Report")
        print("=" * 70)
        print(f"Database: {schema_info.get('database_path', 'Unknown')}")
        print(f"Tables: {len(schema_info['tables'])}")
        print(f"Indexes: {len(schema_info['indexes'])}")
        print(f"Issues: {len(schema_info['issues'])}")
    
    @staticmethod
    def _print_tables_summary(schema_info: Dict[str, Any], verbose: bool) -> None:
        """Print tables summary."""
        print(f"\n📋 Tables Analysis ({len(schema_info['tables'])} tables)")
        print("-" * 50)
        
        for table in sorted(schema_info["tables"]):
            details = schema_info["table_details"][table]
            status = "✅" if table in EXPECTED_TABLES else "ℹ️"
            print(f"{status} {table:<20} ({details['row_count']:>6} rows)")
            
            if verbose:
                # Show column details
                for col in details["columns"]:
                    markers = []
                    if col["primary_key"]:
                        markers.append("PK")
                    if col["not_null"]:
                        markers.append("NOT NULL")
                    if col["default"]:
                        markers.append(f"DEFAULT {col['default']}")
                    
                    marker_str = f" [{', '.join(markers)}]" if markers else ""
                    print(f"    • {col['name']:<20} {col['type']:<15}{marker_str}")
                
                # Show foreign keys
                if details["foreign_keys"]:
                    print("    Foreign Keys:")
                    for fk in details["foreign_keys"]:
                        print(f"      → {fk['column']} references {fk['references_table']}.{fk['references_column']}")
                print()
    
    @staticmethod
    def _print_indexes_summary(schema_info: Dict[str, Any], verbose: bool) -> None:
        """Print indexes summary."""
        print(f"\n🔍 Indexes Analysis ({len(schema_info['indexes'])} indexes)")
        print("-" * 50)
        
        if not schema_info["indexes"]:
            print("⚠️  No custom indexes found")
            return
        
        # Group indexes by table
        indexes_by_table = {}
        for idx in schema_info["indexes"]:
            table = idx["table"]
            if table not in indexes_by_table:
                indexes_by_table[table] = []
            indexes_by_table[table].append(idx)
        
        for table in sorted(indexes_by_table.keys()):
            print(f"  📊 {table}:")
            for idx in indexes_by_table[table]:
                print(f"    • {idx['name']}")
                if verbose and idx["sql"]:
                    print(f"      SQL: {idx['sql']}")
    
    @staticmethod
    def _print_issues_summary(schema_info: Dict[str, Any]) -> None:
        """Print issues summary."""
        issues = schema_info["issues"]
        print(f"\n⚠️  Issues Found ({len(issues)} issues)")
        print("-" * 50)
        
        if not issues:
            print("✅ No issues detected - schema looks good!")
            return
        
        # Group issues by severity
        critical_issues = [i for i in issues if i.startswith("❌")]
        warning_issues = [i for i in issues if i.startswith("⚠️")]
        info_issues = [i for i in issues if i.startswith(("🔍", "📋", "⚡"))]
        
        if critical_issues:
            print("  🚨 Critical Issues:")
            for issue in critical_issues:
                print(f"    {issue}")
        
        if warning_issues:
            print("  ⚠️  Warnings:")
            for issue in warning_issues:
                print(f"    {issue}")
        
        if info_issues:
            print("  ℹ️  Information:")
            for issue in info_issues:
                print(f"    {issue}")
    
    @staticmethod
    def _print_recommendations(schema_info: Dict[str, Any]) -> None:
        """Print recommendations."""
        recommendations = schema_info.get("recommendations", [])
        if not recommendations:
            return
        
        print(f"\n💡 Recommendations ({len(recommendations)} suggestions)")
        print("-" * 50)
        
        for rec in recommendations:
            print(f"  {rec}")
    
    @staticmethod
    def _print_footer(schema_info: Dict[str, Any]) -> None:
        """Print report footer."""
        print("\n" + "=" * 70)
        
        # Calculate health score
        total_checks = len(EXPECTED_TABLES) * 3  # Tables, columns, indexes
        issues_count = len(schema_info["issues"])
        health_score = max(0, 100 - (issues_count * 10))
        
        if health_score >= 90:
            status = "🟢 Excellent"
        elif health_score >= 70:
            status = "🟡 Good"
        elif health_score >= 50:
            status = "🟠 Needs Attention"
        else:
            status = "🔴 Critical"
        
        print(f"Schema Health Score: {health_score}/100 {status}")
        print("=" * 70)

def print_schema_report(schema_info: Dict[str, Any], verbose: bool = False) -> None:
    """Print a formatted schema report.
    
    Args:
        schema_info: Schema analysis results
        verbose: Whether to include detailed information
    """
    SchemaReporter.print_schema_report(schema_info, verbose)

def main() -> None:
    """Main function with command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze CodeXam database schema and identify issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python check_database_schema.py                    # Basic analysis
  python check_database_schema.py --verbose          # Detailed analysis
  python check_database_schema.py --db custom.db     # Custom database
  python check_database_schema.py --json             # JSON output
  python check_database_schema.py --fix              # Show fix suggestions
        """
    )
    
    parser.add_argument(
        "--db", "--database",
        type=str,
        help="Path to database file (default: from config)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed information including column details"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Show SQL commands to fix identified issues"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only show errors and critical issues"
    )
    
    args = parser.parse_args()
    
    try:
        # Perform schema analysis
        schema_info = check_database_schema(args.db)
        
        if args.json:
            import json
            print(json.dumps(schema_info, indent=2, default=str))
        elif args.quiet:
            _print_quiet_report(schema_info)
        else:
            print_schema_report(schema_info, args.verbose)
            
        if args.fix:
            _print_fix_suggestions(schema_info)
            
        # Exit with error code if issues found
        if "error" in schema_info:
            sys.exit(1)
        elif schema_info.get("issues"):
            sys.exit(2)  # Issues found but not critical errors
        else:
            sys.exit(0)  # All good
            
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def _print_quiet_report(schema_info: Dict[str, Any]) -> None:
    """Print minimal report showing only errors and critical issues."""
    if "error" in schema_info:
        print(f"❌ {schema_info['error']}")
        return
    
    critical_issues = [i for i in schema_info["issues"] if i.startswith("❌")]
    if critical_issues:
        print("🚨 Critical Issues:")
        for issue in critical_issues:
            print(f"  {issue}")
    else:
        print("✅ No critical issues found")

def _print_fix_suggestions(schema_info: Dict[str, Any]) -> None:
    """Print SQL commands to fix identified issues."""
    if "error" in schema_info:
        return
    
    print(f"\n🔧 Fix Suggestions")
    print("-" * 50)
    
    # Generate SQL fixes based on recommendations
    for rec in schema_info.get("recommendations", []):
        if "CREATE INDEX" in rec:
            # Extract and format the SQL command
            sql_start = rec.find("CREATE INDEX")
            if sql_start != -1:
                sql_command = rec[sql_start:]
                print(f"  {sql_command};")
    
    # Add other fix suggestions
    missing_tables = [i for i in schema_info["issues"] if "Missing expected table" in i]
    if missing_tables:
        print("\n  -- Create missing tables:")
        print("  -- Run: python scripts/init_db.py")

if __name__ == "__main__":
    main()