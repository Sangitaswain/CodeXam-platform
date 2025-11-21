#!/usr/bin/env python3
"""
CodeXam System Health Check
Comprehensive system validation and health monitoring
"""

import sys
import os
import subprocess
import time
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
import sqlite3

class HealthChecker:
    """Comprehensive health checker for CodeXam platform."""
    
    def __init__(self):
        """Initialize health checker."""
        self.checks = []
        self.start_time = time.time()
    
    def log_check(self, name: str, status: bool, message: str = "", details: Dict = None) -> bool:
        """Log a health check result."""
        result = {
            'name': name,
            'status': 'PASS' if status else 'FAIL',
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.checks.append(result)
        
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name}: {message}")
        
        return status
    
    def check_python_version(self) -> bool:
        """Check Python version compatibility."""
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 8:
                return self.log_check(
                    "Python Version", 
                    True, 
                    f"Python {version.major}.{version.minor}.{version.micro}",
                    {"version": f"{version.major}.{version.minor}.{version.micro}"}
                )
            else:
                return self.log_check(
                    "Python Version", 
                    False, 
                    f"Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)"
                )
        except Exception as e:
            return self.log_check("Python Version", False, f"Error: {e}")
    
    def check_dependencies(self) -> bool:
        """Check required Python dependencies."""
        try:
            required_packages = [
                'flask', 'jinja2', 'werkzeug', 'psutil', 'requests'
            ]
            
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if not missing_packages:
                return self.log_check(
                    "Python Dependencies", 
                    True, 
                    f"All {len(required_packages)} packages available"
                )
            else:
                return self.log_check(
                    "Python Dependencies", 
                    False, 
                    f"Missing packages: {', '.join(missing_packages)}"
                )
        except Exception as e:
            return self.log_check("Python Dependencies", False, f"Error: {e}")
    
    def check_external_tools(self) -> bool:
        """Check external tools availability."""
        tools = {
            'node': ['node', '--version'],
            'java': ['java', '--version'],
            'gcc': ['gcc', '--version']
        }
        
        available_tools = []
        missing_tools = []
        
        for tool, command in tools.items():
            try:
                result = subprocess.run(
                    command, 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                if result.returncode == 0:
                    available_tools.append(tool)
                else:
                    missing_tools.append(tool)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing_tools.append(tool)
        
        if len(available_tools) >= 2:  # At least 2 tools should be available
            return self.log_check(
                "External Tools", 
                True, 
                f"Available: {', '.join(available_tools)}",
                {"available": available_tools, "missing": missing_tools}
            )
        else:
            return self.log_check(
                "External Tools", 
                False, 
                f"Missing critical tools: {', '.join(missing_tools)}"
            )
    
    def check_database(self) -> bool:
        """Check database connectivity and structure."""
        try:
            from database import get_db
            
            db = get_db()
            
            # Test basic query
            result = db.execute_query("SELECT 1 as test")
            if not result or result[0]['test'] != 1:
                return self.log_check("Database", False, "Basic query failed")
            
            # Check required tables
            tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
            tables = db.execute_query(tables_query)
            table_names = [table['name'] for table in tables]
            
            required_tables = ['problems', 'submissions']
            missing_tables = [t for t in required_tables if t not in table_names]
            
            if missing_tables:
                return self.log_check(
                    "Database", 
                    False, 
                    f"Missing tables: {', '.join(missing_tables)}"
                )
            
            # Check data counts
            problems_count = db.execute_single("SELECT COUNT(*) as count FROM problems")['count']
            submissions_count = db.execute_single("SELECT COUNT(*) as count FROM submissions")['count']
            
            return self.log_check(
                "Database", 
                True, 
                f"Connected, {problems_count} problems, {submissions_count} submissions",
                {
                    "tables": table_names,
                    "problems_count": problems_count,
                    "submissions_count": submissions_count
                }
            )
            
        except Exception as e:
            return self.log_check("Database", False, f"Error: {e}")
    
    def check_judge_engine(self) -> bool:
        """Check judge engine functionality."""
        try:
            from judge import SimpleJudge
            
            judge = SimpleJudge()
            
            # Test Python execution
            test_cases = [{'input': '2 7\n9', 'expected_output': '[0, 1]'}]
            python_code = 'def solution(nums, target):\n    return [0, 1]'
            
            result = judge.execute_code('python', python_code, test_cases)
            
            if 'result' in result:
                return self.log_check(
                    "Judge Engine", 
                    True, 
                    f"Python execution working - result: {result['result']}",
                    {"execution_time": result.get('execution_time', 0)}
                )
            else:
                return self.log_check("Judge Engine", False, "Invalid result format")
                
        except Exception as e:
            return self.log_check("Judge Engine", False, f"Error: {e}")
    
    def check_caching_system(self) -> bool:
        """Check caching system functionality."""
        try:
            from cache import cache
            
            # Test cache operations
            test_key = f"health_check_{int(time.time())}"
            test_value = "health_check_value"
            
            cache.set(test_key, test_value, 60)
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                stats = cache.stats()
                return self.log_check(
                    "Caching System", 
                    True, 
                    f"Working, {stats['total_entries']} entries",
                    stats
                )
            else:
                return self.log_check("Caching System", False, "Cache retrieval failed")
                
        except Exception as e:
            return self.log_check("Caching System", False, f"Error: {e}")
    
    def check_performance_monitoring(self) -> bool:
        """Check performance monitoring system."""
        try:
            from performance_monitor import metrics
            
            # Test metrics recording
            metrics.record_request('/health', 'GET', 0.1, 200)
            stats = metrics.get_request_stats()
            
            if 'total_requests' in stats:
                return self.log_check(
                    "Performance Monitoring", 
                    True, 
                    f"Working, {stats['total_requests']} requests tracked"
                )
            else:
                return self.log_check("Performance Monitoring", False, "Invalid stats format")
                
        except Exception as e:
            return self.log_check("Performance Monitoring", False, f"Error: {e}")
    
    def check_static_assets(self) -> bool:
        """Check static assets availability."""
        try:
            required_assets = [
                'static/css/style.css',
                'static/js/main.js'
            ]
            
            optional_assets = [
                'static/optimized/style.min.css',
                'static/optimized/main.min.js'
            ]
            
            missing_required = []
            missing_optional = []
            
            for asset in required_assets:
                if not os.path.exists(asset):
                    missing_required.append(asset)
            
            for asset in optional_assets:
                if not os.path.exists(asset):
                    missing_optional.append(asset)
            
            if missing_required:
                return self.log_check(
                    "Static Assets", 
                    False, 
                    f"Missing required assets: {', '.join(missing_required)}"
                )
            
            message = "All required assets available"
            if missing_optional:
                message += f" (optional missing: {len(missing_optional)})"
            
            return self.log_check("Static Assets", True, message)
            
        except Exception as e:
            return self.log_check("Static Assets", False, f"Error: {e}")
    
    def check_system_resources(self) -> bool:
        """Check system resource availability."""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free_gb = disk.free / (1024**3)
            
            # Check thresholds
            issues = []
            if cpu_percent > 90:
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            if memory_percent > 90:
                issues.append(f"High memory usage: {memory_percent:.1f}%")
            if disk_percent > 90:
                issues.append(f"High disk usage: {disk_percent:.1f}%")
            if memory_available_gb < 0.5:
                issues.append(f"Low available memory: {memory_available_gb:.1f}GB")
            if disk_free_gb < 1.0:
                issues.append(f"Low disk space: {disk_free_gb:.1f}GB")
            
            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available_gb": round(memory_available_gb, 2),
                "disk_percent": disk_percent,
                "disk_free_gb": round(disk_free_gb, 2)
            }
            
            if issues:
                return self.log_check(
                    "System Resources", 
                    False, 
                    f"Issues: {'; '.join(issues)}",
                    details
                )
            else:
                return self.log_check(
                    "System Resources", 
                    True, 
                    f"CPU: {cpu_percent:.1f}%, Memory: {memory_percent:.1f}%, Disk: {disk_percent:.1f}%",
                    details
                )
                
        except Exception as e:
            return self.log_check("System Resources", False, f"Error: {e}")
    
    def check_configuration(self) -> bool:
        """Check application configuration."""
        try:
            # Check environment variables
            env_vars = {
                'FLASK_ENV': os.environ.get('FLASK_ENV', 'development'),
                'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
                'DATABASE_URL': os.environ.get('DATABASE_URL', 'sqlite:///database.db')
            }
            
            issues = []
            
            # Check for production security
            if env_vars['FLASK_ENV'] == 'production':
                if env_vars['SECRET_KEY'] == 'dev-secret-key-change-in-production':
                    issues.append("Using default SECRET_KEY in production")
            
            # Check database URL format
            db_url = env_vars['DATABASE_URL']
            if not any(db_url.startswith(prefix) for prefix in ['sqlite://', 'postgresql://', 'mysql://']):
                issues.append("Invalid DATABASE_URL format")
            
            if issues:
                return self.log_check(
                    "Configuration", 
                    False, 
                    f"Issues: {'; '.join(issues)}",
                    env_vars
                )
            else:
                return self.log_check(
                    "Configuration", 
                    True, 
                    f"Environment: {env_vars['FLASK_ENV']}",
                    env_vars
                )
                
        except Exception as e:
            return self.log_check("Configuration", False, f"Error: {e}")
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        print("🏥 CodeXam System Health Check")
        print("=" * 50)
        
        # Run all checks
        checks = [
            self.check_python_version,
            self.check_dependencies,
            self.check_external_tools,
            self.check_database,
            self.check_judge_engine,
            self.check_caching_system,
            self.check_performance_monitoring,
            self.check_static_assets,
            self.check_system_resources,
            self.check_configuration
        ]
        
        for check in checks:
            check()
        
        # Calculate summary
        passed_checks = [c for c in self.checks if c['status'] == 'PASS']
        failed_checks = [c for c in self.checks if c['status'] == 'FAIL']
        
        execution_time = time.time() - self.start_time
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'execution_time': round(execution_time, 2),
            'total_checks': len(self.checks),
            'passed': len(passed_checks),
            'failed': len(failed_checks),
            'success_rate': len(passed_checks) / len(self.checks) * 100 if self.checks else 0,
            'overall_status': 'HEALTHY' if len(failed_checks) == 0 else 'UNHEALTHY',
            'checks': self.checks
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print health check summary."""
        print("\n" + "=" * 50)
        print("📊 HEALTH CHECK SUMMARY")
        print("=" * 50)
        
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Checks Passed: {summary['passed']}/{summary['total_checks']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Execution Time: {summary['execution_time']}s")
        
        if summary['failed'] > 0:
            print(f"\n❌ Failed Checks:")
            for check in summary['checks']:
                if check['status'] == 'FAIL':
                    print(f"   • {check['name']}: {check['message']}")
        
        if summary['overall_status'] == 'HEALTHY':
            print("\n🎉 System is healthy and ready for operation!")
        else:
            print("\n⚠️ System has issues that need attention.")
    
    def save_report(self, summary: Dict[str, Any], filename: str = None):
        """Save health check report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\n📄 Health report saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save report: {e}")

def main():
    """Main health check execution."""
    checker = HealthChecker()
    summary = checker.run_all_checks()
    checker.print_summary(summary)
    
    # Save report if requested
    if '--save-report' in sys.argv:
        checker.save_report(summary)
    
    # Return appropriate exit code
    return 0 if summary['overall_status'] == 'HEALTHY' else 1

if __name__ == "__main__":
    sys.exit(main())