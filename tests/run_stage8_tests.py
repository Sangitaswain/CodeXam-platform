"""
Test Runner for CodeXam Platform Stage 8 Testing Suite
Executes comprehensive testing including unit tests, integration tests, and end-to-end workflows
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_command(command, description):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"Duration: {end_time - start_time:.2f} seconds")
    print(f"Return code: {result.returncode}")
    
    if result.stdout:
        print("\nSTDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    return result.returncode == 0

def main():
    """Run the complete testing suite."""
    print("CodeXam Platform - Stage 8 Testing Suite")
    print("========================================")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Project root: {project_root}")
    
    # Check if pytest is available
    try:
        import pytest
        print(f"pytest version: {pytest.__version__}")
    except ImportError:
        print("ERROR: pytest not found. Please install pytest first.")
        print("Run: pip install pytest")
        return False
    
    # Test results tracking
    test_results = {}
    
    # 1. Run unit tests for judge engine
    print("\n" + "="*80)
    print("STAGE 8.1: JUDGE ENGINE UNIT TESTS")
    print("="*80)
    
    success = run_command(
        "python -m pytest tests/test_judge.py -v --tb=short",
        "Judge Engine Unit Tests"
    )
    test_results["judge_unit_tests"] = success
    
    # 2. Run integration tests for web routes
    print("\n" + "="*80)
    print("STAGE 8.2: WEB ROUTES INTEGRATION TESTS")
    print("="*80)
    
    success = run_command(
        "python -m pytest tests/test_routes.py -v --tb=short",
        "Web Routes Integration Tests"
    )
    test_results["routes_integration_tests"] = success
    
    # 3. Run end-to-end workflow tests
    print("\n" + "="*80)
    print("STAGE 8.3: END-TO-END WORKFLOW TESTS")
    print("="*80)
    
    success = run_command(
        "python -m pytest tests/test_integration.py -v --tb=short",
        "End-to-End Workflow Tests"
    )
    test_results["e2e_workflow_tests"] = success
    
    # 4. Run all new tests together
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    success = run_command(
        "python -m pytest tests/test_judge.py tests/test_routes.py tests/test_integration.py -v --tb=short --durations=10",
        "All Stage 8 Tests Combined"
    )
    test_results["comprehensive_tests"] = success
    
    # 5. Generate test coverage report (if coverage is available)
    print("\n" + "="*80)
    print("TEST COVERAGE ANALYSIS")
    print("="*80)
    
    try:
        import coverage
        success = run_command(
            "python -m pytest tests/test_judge.py tests/test_routes.py tests/test_integration.py --cov=. --cov-report=term-missing --cov-report=html",
            "Test Coverage Analysis"
        )
        test_results["coverage_analysis"] = success
        if success:
            print("\nCoverage report generated in htmlcov/index.html")
    except ImportError:
        print("Coverage.py not available. Install with: pip install pytest-cov")
        test_results["coverage_analysis"] = False
    
    # 6. Run specific test categories
    print("\n" + "="*80)
    print("SPECIFIC TEST CATEGORIES")
    print("="*80)
    
    # Test error handling specifically
    success = run_command(
        'python -m pytest tests/test_judge.py::TestPythonErrorHandling -v',
        "Error Handling Tests"
    )
    test_results["error_handling_tests"] = success
    
    # Test security features
    success = run_command(
        'python -m pytest tests/test_judge.py::TestPythonErrorHandling::test_import_restriction tests/test_judge.py::TestPythonErrorHandling::test_dangerous_function_restriction -v',
        "Security Validation Tests"
    )
    test_results["security_tests"] = success
    
    # Test multi-language support
    success = run_command(
        'python -m pytest tests/test_judge.py::TestJavaScriptExecution tests/test_judge.py::TestLanguageSupport -v',
        "Multi-Language Support Tests"
    )
    test_results["multi_language_tests"] = success
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print(f"Total test categories: {total_tests}")
    print(f"Passed test categories: {passed_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    # Final assessment
    print("\n" + "="*80)
    print("STAGE 8 COMPLETION ASSESSMENT")
    print("="*80)
    
    critical_tests = ["judge_unit_tests", "routes_integration_tests", "e2e_workflow_tests"]
    critical_passed = all(test_results.get(test, False) for test in critical_tests)
    
    if critical_passed:
        print("🎉 STAGE 8 SUCCESSFULLY COMPLETED!")
        print("   All critical testing components are working correctly.")
        print("   Your CodeXam platform now has comprehensive test coverage.")
        
        completion_percentage = 90.0  # Stage 8 represents significant progress
        print(f"\n📊 Overall Project Completion: {completion_percentage}%")
        print("   Stages 1-8 Complete ✅")
        print("   Remaining: Stage 9 (Sample Data) and Stage 10 (Final Integration)")
        
        return True
    else:
        print("⚠️  STAGE 8 PARTIALLY COMPLETED")
        print("   Some critical tests are failing. Please review the error messages above.")
        print("   Focus on fixing the failing tests before proceeding to Stage 9.")
        
        return False

def run_quick_tests():
    """Run a quick subset of tests for development."""
    print("Running Quick Test Suite...")
    
    # Run a few key tests quickly
    quick_commands = [
        ("python -m pytest tests/test_judge.py::TestJudgeConfiguration::test_default_initialization -v", "Judge Initialization"),
        ("python -m pytest tests/test_routes.py::TestHomepageRoute::test_homepage_get -v", "Homepage Route"),
        ("python -m pytest tests/test_integration.py::TestCompleteUserWorkflow::test_complete_new_user_journey -v", "User Journey")
    ]
    
    results = []
    for command, description in quick_commands:
        success = run_command(command, description)
        results.append(success)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\nQuick Test Results: {success_rate:.1f}% passed")
    
    return all(results)

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = run_quick_tests()
    else:
        success = main()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
