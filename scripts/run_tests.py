#!/usr/bin/env python3
"""
Test runner script for CodeXam platform.

This script provides various testing options including:
- Unit tests
- Integration tests
- Security tests
- Performance tests
- Coverage reporting
- Test result analysis
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRunner:
    """Test runner with comprehensive options and reporting."""
    
    def __init__(self):
        self.project_root = project_root
        self.test_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def run_unit_tests(self, verbose: bool = False) -> int:
        """Run unit tests only."""
        print("🧪 Running unit tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-m", "unit",
            "--tb=short",
            "--durations=10"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.call(cmd, cwd=self.project_root)
    
    def run_integration_tests(self, verbose: bool = False) -> int:
        """Run integration tests only."""
        print("🔗 Running integration tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-m", "integration",
            "--tb=short",
            "--durations=10"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.call(cmd, cwd=self.project_root)
    
    def run_security_tests(self, verbose: bool = False) -> int:
        """Run security tests only."""
        print("🔒 Running security tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-m", "security",
            "--tb=short",
            "--durations=10"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.call(cmd, cwd=self.project_root)
    
    def run_performance_tests(self, verbose: bool = False) -> int:
        """Run performance tests only."""
        print("⚡ Running performance tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-m", "performance",
            "--tb=short",
            "--durations=20"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.call(cmd, cwd=self.project_root)
    
    def run_smoke_tests(self, verbose: bool = False) -> int:
        """Run smoke tests for quick validation."""
        print("💨 Running smoke tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-m", "smoke",
            "--tb=line",
            "--maxfail=5"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.call(cmd, cwd=self.project_root)
    
    def run_all_tests(self, verbose: bool = False, coverage: bool = True) -> int:
        """Run all tests with optional coverage."""
        print("🚀 Running all tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "--tb=short",
            "--durations=20"
        ]
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend([
                "--cov=.",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-report=xml",
                "--cov-fail-under=70"
            ])
        
        return subprocess.call(cmd, cwd=self.project_root)
    
    def run_specific_test(self, test_path: str, verbose: bool = False) -> int:
        """Run a specific test file or test function."""
        print(f"🎯 Running specific test: {test_path}")
        
        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.call(cmd, cwd=self.project_root)
    
    def run_failed_tests(self, verbose: bool = False) -> int:
        """Re-run only the tests that failed in the last run."""
        print("🔄 Re-running failed tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "--lf",  # Last failed
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.call(cmd, cwd=self.project_root)
    
    def generate_coverage_report(self) -> int:
        """Generate detailed coverage report."""
        print("📊 Generating coverage report...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=.",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-only"
        ]
        
        result = subprocess.call(cmd, cwd=self.project_root)
        
        if result == 0:
            print(f"📈 Coverage report generated in: {self.project_root}/htmlcov/index.html")
        
        return result
    
    def run_parallel_tests(self, num_workers: int = None, verbose: bool = False) -> int:
        """Run tests in parallel using pytest-xdist."""
        print(f"⚡ Running tests in parallel...")
        
        try:
            import xdist
        except ImportError:
            print("❌ pytest-xdist not installed. Install with: pip install pytest-xdist")
            return 1
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-n", str(num_workers or "auto"),
            "--tb=short",
            "--durations=10"
        ]
        
        if verbose:
            cmd.append("-v")
        
        return subprocess.call(cmd, cwd=self.project_root)
    
    def validate_test_environment(self) -> bool:
        """Validate that the test environment is properly set up."""
        print("🔍 Validating test environment...")
        
        # Check if test directory exists
        if not self.test_dir.exists():
            print(f"❌ Test directory not found: {self.test_dir}")
            return False
        
        # Check if pytest is installed
        try:
            import pytest
            print(f"✅ pytest version: {pytest.__version__}")
        except ImportError:
            print("❌ pytest not installed. Install with: pip install pytest")
            return False
        
        # Check if test files exist
        test_files = list(self.test_dir.glob("test_*.py"))
        if not test_files:
            print(f"❌ No test files found in {self.test_dir}")
            return False
        
        print(f"✅ Found {len(test_files)} test files")
        
        # Check if conftest.py exists
        conftest_path = self.test_dir / "conftest.py"
        if conftest_path.exists():
            print("✅ conftest.py found")
        else:
            print("⚠️  conftest.py not found - some fixtures may not work")
        
        # Check database file
        db_path = self.project_root / "database.db"
        if db_path.exists():
            print("✅ Database file found")
        else:
            print("⚠️  Database file not found - will be created during tests")
        
        print("✅ Test environment validation complete")
        return True
    
    def clean_test_artifacts(self) -> None:
        """Clean up test artifacts and temporary files."""
        print("🧹 Cleaning test artifacts...")
        
        artifacts_to_clean = [
            ".pytest_cache",
            "__pycache__",
            "htmlcov",
            ".coverage",
            "coverage.xml",
            "test_database.db"
        ]
        
        for artifact in artifacts_to_clean:
            artifact_path = self.project_root / artifact
            if artifact_path.exists():
                if artifact_path.is_file():
                    artifact_path.unlink()
                    print(f"🗑️  Removed file: {artifact}")
                elif artifact_path.is_dir():
                    import shutil
                    shutil.rmtree(artifact_path)
                    print(f"🗑️  Removed directory: {artifact}")
        
        print("✅ Test artifacts cleaned")
    
    def run_test_suite(self, suite_type: str, verbose: bool = False) -> Dict[str, Any]:
        """Run a complete test suite and return results."""
        start_time = time.time()
        
        suite_runners = {
            "unit": self.run_unit_tests,
            "integration": self.run_integration_tests,
            "security": self.run_security_tests,
            "performance": self.run_performance_tests,
            "smoke": self.run_smoke_tests,
            "all": self.run_all_tests
        }
        
        if suite_type not in suite_runners:
            raise ValueError(f"Unknown test suite: {suite_type}")
        
        print(f"🏃 Starting {suite_type} test suite...")
        
        result_code = suite_runners[suite_type](verbose=verbose)
        end_time = time.time()
        duration = end_time - start_time
        
        result = {
            "suite_type": suite_type,
            "result_code": result_code,
            "duration": duration,
            "success": result_code == 0,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if result["success"]:
            print(f"✅ {suite_type} test suite completed successfully in {duration:.2f}s")
        else:
            print(f"❌ {suite_type} test suite failed in {duration:.2f}s")
        
        return result


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="CodeXam Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py --unit                    # Run unit tests only
  python scripts/run_tests.py --integration             # Run integration tests only
  python scripts/run_tests.py --security                # Run security tests only
  python scripts/run_tests.py --performance             # Run performance tests only
  python scripts/run_tests.py --smoke                   # Run smoke tests only
  python scripts/run_tests.py --all                     # Run all tests
  python scripts/run_tests.py --all --coverage          # Run all tests with coverage
  python scripts/run_tests.py --specific tests/test_models.py  # Run specific test file
  python scripts/run_tests.py --failed                  # Re-run failed tests
  python scripts/run_tests.py --parallel                # Run tests in parallel
  python scripts/run_tests.py --validate                # Validate test environment
  python scripts/run_tests.py --clean                   # Clean test artifacts
        """
    )
    
    # Test suite options
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    # Specific test options
    parser.add_argument("--specific", type=str, help="Run specific test file or function")
    parser.add_argument("--failed", action="store_true", help="Re-run only failed tests")
    
    # Execution options
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--workers", type=int, help="Number of parallel workers")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    
    # Utility options
    parser.add_argument("--validate", action="store_true", help="Validate test environment")
    parser.add_argument("--clean", action="store_true", help="Clean test artifacts")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Handle utility options first
    if args.validate:
        success = runner.validate_test_environment()
        return 0 if success else 1
    
    if args.clean:
        runner.clean_test_artifacts()
        return 0
    
    # Determine which tests to run
    if args.unit:
        return runner.run_unit_tests(verbose=args.verbose)
    elif args.integration:
        return runner.run_integration_tests(verbose=args.verbose)
    elif args.security:
        return runner.run_security_tests(verbose=args.verbose)
    elif args.performance:
        return runner.run_performance_tests(verbose=args.verbose)
    elif args.smoke:
        return runner.run_smoke_tests(verbose=args.verbose)
    elif args.all:
        return runner.run_all_tests(verbose=args.verbose, coverage=args.coverage)
    elif args.specific:
        return runner.run_specific_test(args.specific, verbose=args.verbose)
    elif args.failed:
        return runner.run_failed_tests(verbose=args.verbose)
    elif args.parallel:
        return runner.run_parallel_tests(num_workers=args.workers, verbose=args.verbose)
    else:
        # Default: run smoke tests for quick validation
        print("No specific test suite specified. Running smoke tests...")
        return runner.run_smoke_tests(verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())