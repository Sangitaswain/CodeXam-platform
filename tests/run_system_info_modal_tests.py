#!/usr/bin/env python3
"""
Comprehensive Test Runner for System Info Modal
Runs all test suites and generates detailed reports
"""

import pytest
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class SystemInfoModalTestRunner:
    """Comprehensive test runner for System Info Modal."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    def run_all_tests(self):
        """Run all test suites for System Info Modal."""
        print("🚀 Starting System Info Modal Test Suite")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Define test suites
        test_suites = [
            {
                'name': 'Core Functionality Tests',
                'file': 'tests/test_system_info_modal.py',
                'description': 'Tests API endpoints, helpers, and integration'
            },
            {
                'name': 'JavaScript Functionality Tests',
                'file': 'tests/test_system_info_modal_js.py',
                'description': 'Tests JavaScript modal behavior and interactions'
            },
            {
                'name': 'Performance Tests',
                'file': 'tests/test_system_info_modal_performance.py',
                'description': 'Tests performance, load times, and resource usage'
            },
            {
                'name': 'Accessibility Tests',
                'file': 'tests/test_system_info_modal_accessibility.py',
                'description': 'Tests WCAG 2.1 AA compliance and accessibility'
            }
        ]
        
        # Run each test suite
        for suite in test_suites:
            print(f"\n📋 Running {suite['name']}")
            print(f"   {suite['description']}")
            print("-" * 50)
            
            result = self._run_test_suite(suite['file'])
            self.test_results[suite['name']] = result
            
            if result['success']:
                print(f"✅ {suite['name']}: PASSED")
            else:
                print(f"❌ {suite['name']}: FAILED")
            
            print(f"   Tests run: {result['total']}")
            print(f"   Passed: {result['passed']}")
            print(f"   Failed: {result['failed']}")
            print(f"   Skipped: {result['skipped']}")
            print(f"   Duration: {result['duration']:.2f}s")
        
        self.end_time = time.time()
        
        # Generate summary report
        self._generate_summary_report()
        
        # Generate detailed report
        self._generate_detailed_report()
        
        return self._get_overall_success()
    
    def _run_test_suite(self, test_file):
        """Run a single test suite."""
        start_time = time.time()
        
        # Check if test file exists
        if not os.path.exists(test_file):
            return {
                'success': False,
                'total': 0,
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'duration': 0,
                'error': f"Test file {test_file} not found"
            }
        
        try:
            # Run pytest with basic reporting
            result = pytest.main([
                test_file,
                '-v',
                '--tb=short',
                '-x'  # Stop on first failure for faster feedback
            ])
            
            duration = time.time() - start_time
            
            # Parse result based on pytest exit code
            report_data = self._parse_pytest_result(result)
            
            return {
                'success': result == 0,
                'total': report_data.get('summary', {}).get('total', 0),
                'passed': report_data.get('summary', {}).get('passed', 0),
                'failed': report_data.get('summary', {}).get('failed', 0),
                'skipped': report_data.get('summary', {}).get('skipped', 0),
                'duration': duration,
                'details': report_data
            }
            
        except Exception as e:
            duration = time.time() - start_time
            return {
                'success': False,
                'total': 0,
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'duration': duration,
                'error': str(e)
            }
    
    def _parse_pytest_result(self, result_code):
        """Parse pytest result based on exit code."""
        # pytest exit codes:
        # 0: All tests passed
        # 1: Tests were collected and run but some of the tests failed
        # 2: Test execution was interrupted by the user
        # 3: Internal error happened while executing tests
        # 4: pytest command line usage error
        # 5: No tests were collected
        
        if result_code == 0:
            return {'summary': {'total': 1, 'passed': 1, 'failed': 0, 'skipped': 0}}
        elif result_code == 1:
            return {'summary': {'total': 1, 'passed': 0, 'failed': 1, 'skipped': 0}}
        elif result_code == 5:
            return {'summary': {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}}
        else:
            return {'summary': {'total': 1, 'passed': 0, 'failed': 1, 'skipped': 0}}
    
    def _parse_json_report(self):
        """Parse pytest JSON report."""
        try:
            if os.path.exists('test_report.json'):
                with open('test_report.json', 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _generate_summary_report(self):
        """Generate summary report."""
        print("\n" + "=" * 60)
        print("📊 SYSTEM INFO MODAL TEST SUMMARY")
        print("=" * 60)
        
        total_duration = self.end_time - self.start_time
        overall_success = self._get_overall_success()
        
        # Calculate totals
        total_tests = sum(result['total'] for result in self.test_results.values())
        total_passed = sum(result['passed'] for result in self.test_results.values())
        total_failed = sum(result['failed'] for result in self.test_results.values())
        total_skipped = sum(result['skipped'] for result in self.test_results.values())
        
        print(f"Overall Status: {'✅ PASSED' if overall_success else '❌ FAILED'}")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Test Suites: {len(self.test_results)}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        print(f"Skipped: {total_skipped}")
        
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Test Suite Breakdown:")
        for suite_name, result in self.test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  {suite_name}: {status}")
            print(f"    Tests: {result['total']} | Passed: {result['passed']} | Failed: {result['failed']} | Skipped: {result['skipped']}")
            
            if 'error' in result:
                print(f"    Error: {result['error']}")
        
        # Recommendations
        print("\n🎯 Recommendations:")
        if overall_success:
            print("  ✅ All tests passed! System Info Modal is ready for deployment.")
            print("  🔄 Consider running performance tests under load.")
            print("  📱 Test on various devices and browsers.")
        else:
            print("  ❌ Some tests failed. Review failures before deployment.")
            print("  🔧 Fix failing tests and re-run test suite.")
            print("  📝 Check logs for detailed error information.")
    
    def _generate_detailed_report(self):
        """Generate detailed HTML report."""
        try:
            report_html = self._create_html_report()
            
            # Save report
            report_file = f"system_info_modal_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(report_file, 'w') as f:
                f.write(report_html)
            
            print(f"\n📄 Detailed report saved: {report_file}")
            
        except Exception as e:
            print(f"\n⚠️  Could not generate detailed report: {e}")
    
    def _create_html_report(self):
        """Create HTML test report."""
        overall_success = self._get_overall_success()
        total_duration = self.end_time - self.start_time
        
        # Calculate totals
        total_tests = sum(result['total'] for result in self.test_results.values())
        total_passed = sum(result['passed'] for result in self.test_results.values())
        total_failed = sum(result['failed'] for result in self.test_results.values())
        total_skipped = sum(result['skipped'] for result in self.test_results.values())
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Info Modal Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .status-pass {{ color: #28a745; }}
        .status-fail {{ color: #dc3545; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .test-suite {{ margin-bottom: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        .test-suite-header {{ background: #f8f9fa; padding: 15px; font-weight: bold; }}
        .test-suite-content {{ padding: 15px; }}
        .test-details {{ margin-top: 10px; font-size: 0.9em; color: #666; }}
        .progress-bar {{ width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: #28a745; transition: width 0.3s; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 System Info Modal Test Report</h1>
            <h2 class="{'status-pass' if overall_success else 'status-fail'}">
                {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}
            </h2>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <div style="font-size: 2em; font-weight: bold;">{total_tests}</div>
            </div>
            <div class="summary-card">
                <h3>Passed</h3>
                <div style="font-size: 2em; font-weight: bold; color: #28a745;">{total_passed}</div>
            </div>
            <div class="summary-card">
                <h3>Failed</h3>
                <div style="font-size: 2em; font-weight: bold; color: #dc3545;">{total_failed}</div>
            </div>
            <div class="summary-card">
                <h3>Skipped</h3>
                <div style="font-size: 2em; font-weight: bold; color: #ffc107;">{total_skipped}</div>
            </div>
            <div class="summary-card">
                <h3>Duration</h3>
                <div style="font-size: 2em; font-weight: bold;">{total_duration:.1f}s</div>
            </div>
            <div class="summary-card">
                <h3>Success Rate</h3>
                <div style="font-size: 2em; font-weight: bold;">
                    {(total_passed / total_tests * 100) if total_tests > 0 else 0:.1f}%
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(total_passed / total_tests * 100) if total_tests > 0 else 0}%"></div>
                </div>
            </div>
        </div>
        
        <h2>📋 Test Suite Details</h2>
        """
        
        for suite_name, result in self.test_results.items():
            status_class = "status-pass" if result['success'] else "status-fail"
            status_text = "✅ PASSED" if result['success'] else "❌ FAILED"
            
            html += f"""
        <div class="test-suite">
            <div class="test-suite-header">
                <span class="{status_class}">{status_text}</span> - {suite_name}
            </div>
            <div class="test-suite-content">
                <div class="test-details">
                    <strong>Tests:</strong> {result['total']} | 
                    <strong>Passed:</strong> {result['passed']} | 
                    <strong>Failed:</strong> {result['failed']} | 
                    <strong>Skipped:</strong> {result['skipped']} | 
                    <strong>Duration:</strong> {result['duration']:.2f}s
                </div>
                """
            
            if 'error' in result:
                html += f'<div style="color: #dc3545; margin-top: 10px;"><strong>Error:</strong> {result["error"]}</div>'
            
            html += """
            </div>
        </div>
            """
        
        html += """
        <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px;">
            <h3>🎯 Next Steps</h3>
            """
        
        if overall_success:
            html += """
            <ul>
                <li>✅ All tests passed! System Info Modal is ready for deployment.</li>
                <li>🔄 Consider running performance tests under load.</li>
                <li>📱 Test on various devices and browsers.</li>
                <li>🚀 Deploy to staging environment for final testing.</li>
            </ul>
            """
        else:
            html += """
            <ul>
                <li>❌ Some tests failed. Review failures before deployment.</li>
                <li>🔧 Fix failing tests and re-run test suite.</li>
                <li>📝 Check logs for detailed error information.</li>
                <li>🔍 Debug failed test cases individually.</li>
            </ul>
            """
        
        html += """
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def _get_overall_success(self):
        """Check if all test suites passed."""
        return all(result['success'] for result in self.test_results.values())
    
    def run_specific_suite(self, suite_name):
        """Run a specific test suite."""
        suite_files = {
            'core': 'tests/test_system_info_modal.py',
            'js': 'tests/test_system_info_modal_js.py',
            'performance': 'tests/test_system_info_modal_performance.py',
            'accessibility': 'tests/test_system_info_modal_accessibility.py'
        }
        
        if suite_name not in suite_files:
            print(f"❌ Unknown test suite: {suite_name}")
            print(f"Available suites: {', '.join(suite_files.keys())}")
            return False
        
        print(f"🚀 Running {suite_name} test suite...")
        result = self._run_test_suite(suite_files[suite_name])
        
        if result['success']:
            print(f"✅ {suite_name} tests: PASSED")
        else:
            print(f"❌ {suite_name} tests: FAILED")
        
        return result['success']


def main():
    """Main entry point."""
    runner = SystemInfoModalTestRunner()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        suite_name = sys.argv[1].lower()
        success = runner.run_specific_suite(suite_name)
        sys.exit(0 if success else 1)
    else:
        # Run all tests
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()