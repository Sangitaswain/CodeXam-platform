"""
API Helper Functions for System Info Modal

Provides real system information and statistics for the API endpoints.
This module contains utilities for gathering system metrics, database
health information, and platform statistics for monitoring dashboards.
"""

import logging
import os
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from database import get_db, get_platform_stats
from models import Problem, Submission

logger = logging.getLogger(__name__)

def get_real_system_info() -> Dict[str, Any]:
    """
    Get real system information using psutil.
    
    Returns:
        Dictionary containing platform info, performance metrics,
        database health, and timestamp
        
    Raises:
        ImportError: If psutil is not available, falls back to mock data
    """
    try:
        import psutil
        
        # Get system information
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        # Format uptime
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m"
        
        # Get memory info
        memory = psutil.virtual_memory()
        
        # Get CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get disk info
        disk = psutil.disk_usage('/')
        
        return {
            'platform': {
                'name': 'CodeXam Elite Arena',
                'version': '2.1.0',
                'uptime': uptime_str,
                'status': 'OPERATIONAL',
                'boot_time': boot_time.isoformat()
            },
            'performance': {
                'cpu_usage': round(cpu_percent, 1),
                'memory_usage': round(memory.percent, 1),
                'memory_total': round(memory.total / (1024**3), 2),  # GB
                'memory_available': round(memory.available / (1024**3), 2),  # GB
                'disk_usage': round((disk.used / disk.total) * 100, 1),
                'disk_total': round(disk.total / (1024**3), 2),  # GB
                'disk_free': round(disk.free / (1024**3), 2)  # GB
            },
            'database': get_database_health(),
            'timestamp': datetime.now().isoformat()
        }
    except ImportError:
        return get_mock_system_info()
    except Exception as e:
        logger.error(f"Error getting real system info: {e}")
        return get_mock_system_info()

def get_mock_system_info() -> Dict[str, Any]:
    """
    Get mock system information for development.
    
    Returns:
        Dictionary containing mock platform info, performance metrics,
        database health, and timestamp for development/testing purposes
    """
    return {
        'platform': {
            'name': 'CodeXam Elite Arena',
            'version': '2.1.0',
            'uptime': '72h 15m 42s',
            'status': 'OPERATIONAL',
            'boot_time': (datetime.now() - timedelta(hours=72, minutes=15)).isoformat()
        },
        'performance': {
            'cpu_usage': 23.5,
            'memory_usage': 45.2,
            'memory_total': 16.0,
            'memory_available': 8.8,
            'disk_usage': 12.8,
            'disk_total': 500.0,
            'disk_free': 436.0
        },
        'database': get_database_health(),
        'timestamp': datetime.now().isoformat()
    }

def get_database_health() -> Dict[str, Any]:
    """
    Get database health information.
    
    Returns:
        Dictionary containing database status, response time,
        connection info, and health status
        
    Raises:
        Exception: Database connection or query errors are caught
        and returned in the health status
    """
    try:
        start_time = time.time()
        
        # Test database connection
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Simple query to test responsiveness
        cursor.execute("SELECT COUNT(*) FROM problems")
        problem_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM submissions")
        submission_count = cursor.fetchone()[0]
        
        conn.close()
        
        response_time = (time.time() - start_time) * 1000  # ms
        
        return {
            'status': 'CONNECTED',
            'response_time': response_time,  # Return numeric value
            'connections': 1,  # SQLite doesn't have connection pooling
            'queries': problem_count + submission_count,
            'health': 'HEALTHY' if response_time < 100 else 'SLOW'
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'status': 'ERROR',
            'response_time': -1,  # Use -1 to indicate error
            'connections': 0,
            'queries': 0,
            'health': 'UNHEALTHY',
            'error': str(e)
        }

def get_enhanced_platform_stats():
    """Get enhanced platform statistics with additional metrics."""
    try:
        # Get basic stats
        basic_stats = get_platform_stats()
        
        # Get additional statistics
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Language distribution
        cursor.execute("""
            SELECT language, COUNT(*) as count
            FROM submissions 
            GROUP BY language 
            ORDER BY count DESC
        """)
        language_stats = dict(cursor.fetchall())
        
        # Success rates by language
        cursor.execute("""
            SELECT 
                language,
                COUNT(*) as total,
                SUM(CASE WHEN result = 'PASS' THEN 1 ELSE 0 END) as passed
            FROM submissions 
            GROUP BY language
        """)
        language_success = {}
        for lang, total, passed in cursor.fetchall():
            language_success[lang] = {
                'total': total,
                'passed': passed,
                'success_rate': round((passed / total) * 100, 1) if total > 0 else 0
            }
        
        # Problem difficulty distribution
        cursor.execute("""
            SELECT difficulty, COUNT(*) as count
            FROM problems 
            GROUP BY difficulty
        """)
        difficulty_stats = dict(cursor.fetchall())
        
        # Recent activity (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM submissions 
            WHERE submitted_at > ?
        """, (yesterday,))
        recent_submissions = cursor.fetchone()[0]
        
        # Top performers (users with most solved problems)
        cursor.execute("""
            SELECT 
                user_name,
                COUNT(DISTINCT problem_id) as problems_solved
            FROM submissions 
            WHERE result = 'PASS'
            GROUP BY user_name
            ORDER BY problems_solved DESC
            LIMIT 10
        """)
        top_performers = [
            {'user': user, 'solved': count}
            for user, count in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            'basic': basic_stats,
            'languages': {
                'distribution': language_stats,
                'success_rates': language_success
            },
            'problems': {
                'difficulty_distribution': difficulty_stats,
                'total': basic_stats.get('total_problems', 0)
            },
            'activity': {
                'recent_submissions': recent_submissions,
                'total_submissions': basic_stats.get('total_submissions', 0)
            },
            'leaderboard': {
                'top_performers': top_performers
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting enhanced platform stats: {e}")
        # Return basic stats as fallback
        return {
            'basic': get_platform_stats(),
            'languages': {'distribution': {}, 'success_rates': {}},
            'problems': {'difficulty_distribution': {}, 'total': 0},
            'activity': {'recent_submissions': 0, 'total_submissions': 0},
            'leaderboard': {'top_performers': []},
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

def perform_health_checks():
    """Perform comprehensive health checks."""
    try:
        health_data = {
            'overall_status': 'HEALTHY',
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Database health check
        db_health = get_database_health()
        health_data['checks']['database'] = {
            'status': db_health['status'],
            'response_time': db_health['response_time'],
            'health': db_health['health']
        }
        
        # File system check
        try:
            # Check if database file exists and is writable
            db_path = 'database.db'
            if os.path.exists(db_path):
                if os.access(db_path, os.R_OK | os.W_OK):
                    fs_status = 'HEALTHY'
                else:
                    fs_status = 'READ_ONLY'
            else:
                fs_status = 'MISSING'
                
            health_data['checks']['filesystem'] = {
                'status': fs_status,
                'database_file': 'EXISTS' if os.path.exists(db_path) else 'MISSING',
                'permissions': 'RW' if os.access(db_path, os.R_OK | os.W_OK) else 'RO'
            }
        except Exception as e:
            health_data['checks']['filesystem'] = {
                'status': 'ERROR',
                'error': str(e)
            }
        
        # Memory check (if psutil available)
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_status = 'HEALTHY' if memory.percent < 80 else 'HIGH'
            
            health_data['checks']['memory'] = {
                'status': memory_status,
                'usage_percent': round(memory.percent, 1),
                'available_gb': round(memory.available / (1024**3), 2)
            }
        except ImportError:
            health_data['checks']['memory'] = {
                'status': 'UNAVAILABLE',
                'note': 'psutil not installed'
            }
        
        # Determine overall status
        check_statuses = [check.get('status', 'UNKNOWN') for check in health_data['checks'].values()]
        if any(status in ['ERROR', 'UNHEALTHY'] for status in check_statuses):
            health_data['overall_status'] = 'UNHEALTHY'
        elif any(status in ['SLOW', 'HIGH', 'READ_ONLY'] for status in check_statuses):
            health_data['overall_status'] = 'DEGRADED'
        
        return health_data
        
    except Exception as e:
        logger.error(f"Error performing health checks: {e}")
        return {
            'overall_status': 'ERROR',
            'checks': {},
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

def create_error_response(message, status_code, error_code):
    """Create standardized error response."""
    from flask import jsonify
    
    return jsonify({
        'status': 'error',
        'error': {
            'message': message,
            'code': error_code,
            'timestamp': datetime.now().isoformat()
        }
    }), status_code

def format_ascii_table(data, headers):
    """Format data as ASCII table for terminal display."""
    if not data:
        return "No data available"
    
    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(header)
        for row in data:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width + 2)
    
    # Create table
    lines = []
    
    # Header
    header_line = "│"
    for i, header in enumerate(headers):
        header_line += f" {header:<{col_widths[i]-1}}│"
    lines.append(header_line)
    
    # Separator
    sep_line = "├"
    for width in col_widths:
        sep_line += "─" * width + "┼"
    sep_line = sep_line[:-1] + "┤"
    lines.append(sep_line)
    
    # Data rows
    for row in data:
        data_line = "│"
        for i, cell in enumerate(row):
            if i < len(col_widths):
                data_line += f" {str(cell):<{col_widths[i]-1}}│"
        lines.append(data_line)
    
    # Top and bottom borders
    top_line = "┌" + "─".join("─" * width for width in col_widths).replace("─", "─").replace("─", "─") + "┐"
    bottom_line = "└" + "─".join("─" * width for width in col_widths).replace("─", "─").replace("─", "─") + "┘"
    
    # Fix borders
    top_line = "┌" + "┬".join("─" * width for width in col_widths) + "┐"
    bottom_line = "└" + "┴".join("─" * width for width in col_widths) + "┘"
    
    return "\n".join([top_line] + lines + [bottom_line])

def format_ascii_chart(data, title="Chart", max_width=50):
    """Format data as ASCII bar chart."""
    if not data:
        return "No data available"
    
    lines = [f"📊 {title}", ""]
    
    # Find max value for scaling
    max_value = max(data.values()) if data else 1
    
    for label, value in data.items():
        # Calculate bar length
        bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
        bar = "█" * bar_length
        
        # Format line
        line = f"{label:<15} │{bar:<{max_width}} {value}"
        lines.append(line)
    
    return "\n".join(lines)