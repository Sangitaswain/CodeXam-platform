#!/usr/bin/env python3
"""
Cross-Browser and Device Testing Runner for CodeXam

This script runs comprehensive cross-browser and device testing to ensure
consistent behavior and appearance across different platforms.

Usage:
    python run_cross_browser_tests.py [--browsers chrome,firefox] [--devices desktop,mobile] [--headless]
"""

import argparse
import sys
import os
import json
import time
import concurrent.futures
from pathlib import Path

# Add tests directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

try:
    from test_cross_browser import CrossBrowserTester, TestResult
except ImportError as e:
    print(f"Error importing cross-browser tester: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install selenium webdriver-manager")
    sys.exit(1)


class CrossBrowserTestRunner:
    """Main test runner for cross-browser testing."""
    
    def __init__(self, config_file="device_testing_config.json", base_url="http://localhost:5000"):
        self.base_url = base_url
        self.config = self.load_config(config_file)
        self.tester = CrossBrowserTester(base_url)
        self.results = []
        
    def load_config(self, config_file):
        """Load testing configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file {config_file} not found, using defaults")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config file: {e}")
            sys.exit(1)
            
    def get_default_config(self):
        """Get default configuration if config file is missing."""
        return {
            "browsers": {
                "chrome": {"enabled": True},
                "firefox": {"enabled": True},
                "edge": {"enabled": True}
            },
            "devices": {
                "desktop": {"standard_desktop": {"name": "Desktop", "width": 1366, "height": 768}},
                "mobile": {"iphone_se": {"name": "Mobile", "width": 375, "height": 667}}
            },
            "test_scenarios": {
                "page_load": {"enabled": True},
                "responsive_layout": {"enabled": True},
                "forms": {"enabled": True}
            }
        }
        
    def get_available_browsers(self):
        """Check which browsers are available for testing."""
        available = []
        
        for browser_name, browser_config in self.config.get("browsers", {}).items():
            if not browser_config.get("enabled", True):
                continue
                
            try:
                # Try to create a driver to test availability
                driver = self.tester.setup_driver(browser_name, 'desktop', headless=True)
                if driver:
                    available.append(browser_name)
                    driver.quit()
            except Exception as e:
                print(f"⚠️  {browser_name.title()} not available: {e}")
                
        return available
        
    def run_browser_device_combination(self, browser, device_category, device_name, device_config, headless=True):
        """Run tests for a specific browser/device combination."""
        print(f"🧪 Testing {browser.title()} on {device_config['name']}...")
        
        # Update tester device configuration
        self.tester.devices[device_name] = type('DeviceConfig', (), {
            'name': device_config['name'],
            'width': device_config['width'],
            'height': device_config['height'],
            'user_agent': device_config.get('user_agent', ''),
            'touch_enabled': device_config.get('touch_enabled', False),
            'pixel_ratio': device_config.get('pixel_ratio', 1.0)
        })()
        
        # Run tests for this combination
        results = self.tester.run_browser_test(browser, device_name, headless)
        return results
        
    def run_parallel_tests(self, browser_device_combinations, headless=True, max_workers=2):
        """Run tests in parallel for faster execution."""
        print(f"🚀 Running tests in parallel with {max_workers} workers...")
        
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all test jobs
            future_to_combo = {}
            
            for browser, device_category, device_name, device_config in browser_device_combinations:
                future = executor.submit(
                    self.run_browser_device_combination,
                    browser, device_category, device_name, device_config, headless
                )
                future_to_combo[future] = (browser, device_config['name'])
                
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_combo):
                browser, device_name = future_to_combo[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                    print(f"✅ Completed {browser.title()} on {device_name}")
                except Exception as e:
                    print(f"❌ Failed {browser.title()} on {device_name}: {e}")
                    
        return all_results
        
    def run_sequential_tests(self, browser_device_combinations, headless=True):
        """Run tests sequentially."""
        all_results = []
        
        for browser, device_category, device_name, device_config in browser_device_combinations:
            results = self.run_browser_device_combination(
                browser, device_category, device_name, device_config, headless
            )
            all_results.extend(results)
            
        return all_results
        
    def run_tests(self, browsers=None, devices=None, headless=True, parallel=False):
        """Run comprehensive cross-browser tests."""
        print("🌐 Starting Cross-Browser and Device Testing")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Headless mode: {headless}")
        print(f"Parallel execution: {parallel}")
        print("")
        
        # Get available browsers
        available_browsers = self.get_available_browsers()
        if not available_browsers:
            print("❌ No browsers available for testing")
            return []
            
        # Filter requested browsers
        if browsers:
            test_browsers = [b for b in browsers if b in available_browsers]
        else:
            test_browsers = available_browsers
            
        if not test_browsers:
            print("❌ No requested browsers available")
            return []
            
        print(f"🌐 Testing browsers: {', '.join(test_browsers)}")
        
        # Prepare device configurations
        device_combinations = []
        
        for device_category, devices_in_category in self.config.get("devices", {}).items():
            # Skip if specific devices requested and this category not included
            if devices and device_category not in devices:
                continue
                
            for device_name, device_config in devices_in_category.items():
                device_combinations.append((device_category, device_name, device_config))
                
        if not device_combinations:
            print("❌ No devices configured for testing")
            return []
            
        print(f"📱 Testing devices: {', '.join([d[2]['name'] for d in device_combinations])}")
        print("")
        
        # Create browser/device combinations
        browser_device_combinations = []
        for browser in test_browsers:
            for device_category, device_name, device_config in device_combinations:
                browser_device_combinations.append((browser, device_category, device_name, device_config))
                
        print(f"🧪 Total test combinations: {len(browser_device_combinations)}")
        print("")
        
        # Run tests
        start_time = time.time()
        
        if parallel and len(browser_device_combinations) > 1:
            results = self.run_parallel_tests(browser_device_combinations, headless)
        else:
            results = self.run_sequential_tests(browser_device_combinations, headless)
            
        end_time = time.time()
        
        self.results = results
        
        # Generate summary
        self.generate_console_summary(results, end_time - start_time)
        
        return results
        
    def generate_console_summary(self, results, duration):
        """Generate console summary of test results."""
        print("\n" + "=" * 60)
        print("📊 Cross-Browser Testing Results Summary")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = len([r for r in results if r.passed])
        failed_tests = total_tests - passed_tests
        
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🧪 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
            
        print("")
        
        # Results by browser
        browser_results = {}
        for result in results:
            if result.browser not in browser_results:
                browser_results[result.browser] = {'passed': 0, 'failed': 0}
            if result.passed:
                browser_results[result.browser]['passed'] += 1
            else:
                browser_results[result.browser]['failed'] += 1
                
        print("🌐 Results by Browser:")
        for browser, stats in browser_results.items():
            total = stats['passed'] + stats['failed']
            rate = (stats['passed'] / total * 100) if total > 0 else 0
            status = "✅" if stats['failed'] == 0 else "❌"
            print(f"  {status} {browser.title()}: {stats['passed']}/{total} ({rate:.1f}%)")
            
        print("")
        
        # Results by device
        device_results = {}
        for result in results:
            if result.device not in device_results:
                device_results[result.device] = {'passed': 0, 'failed': 0}
            if result.passed:
                device_results[result.device]['passed'] += 1
            else:
                device_results[result.device]['failed'] += 1
                
        print("📱 Results by Device:")
        for device, stats in device_results.items():
            total = stats['passed'] + stats['failed']
            rate = (stats['passed'] / total * 100) if total > 0 else 0
            status = "✅" if stats['failed'] == 0 else "❌"
            print(f"  {status} {device}: {stats['passed']}/{total} ({rate:.1f}%)")
            
        print("")
        
        # Show critical failures
        critical_failures = [r for r in results if not r.passed and r.test_name in ['page_load', 'css_rendering']]
        if critical_failures:
            print("🚨 Critical Failures:")
            for failure in critical_failures[:5]:  # Show first 5
                print(f"  ❌ {failure.browser}/{failure.device} - {failure.page}: {failure.error_message}")
            if len(critical_failures) > 5:
                print(f"  ... and {len(critical_failures) - 5} more critical failures")
            print("")
            
    def generate_html_report(self, results):
        """Generate HTML report for cross-browser testing."""
        
        # Calculate summary stats
        total_tests = len(results)
        passed_tests = len([r for r in results if r.passed])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeXam Cross-Browser Testing Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .summary-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .summary-card h3 {{
            margin: 0 0 0.5rem 0;
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
        }}
        
        .summary-card .value {{
            font-size: 2rem;
            font-weight: bold;
            margin: 0;
        }}
        
        .passed {{ color: #27ae60; }}
        .failed {{ color: #e74c3c; }}
        .rate {{ color: #3498db; }}
        
        .results-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .browser-results {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .browser-header {{
            background: #f8f9fa;
            padding: 1rem;
            border-bottom: 1px solid #dee2e6;
            font-weight: bold;
        }}
        
        .device-result {{
            padding: 1rem;
            border-bottom: 1px solid #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .device-result:last-child {{
            border-bottom: none;
        }}
        
        .device-name {{
            font-weight: 500;
        }}
        
        .test-status {{
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }}
        
        .status-badge {{
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }}
        
        .status-pass {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .failures-section {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        
        .failures-header {{
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            font-weight: bold;
        }}
        
        .failure-item {{
            padding: 1rem;
            border-bottom: 1px solid #f8f9fa;
        }}
        
        .failure-item:last-child {{
            border-bottom: none;
        }}
        
        .failure-title {{
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 0.5rem;
        }}
        
        .failure-details {{
            color: #666;
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}
            
            .results-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 Cross-Browser Testing Report</h1>
        <p>Generated on {time.strftime('%Y-%m-%d at %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>Total Tests</h3>
            <p class="value">{total_tests}</p>
        </div>
        <div class="summary-card">
            <h3>Passed</h3>
            <p class="value passed">{passed_tests}</p>
        </div>
        <div class="summary-card">
            <h3>Failed</h3>
            <p class="value failed">{failed_tests}</p>
        </div>
        <div class="summary-card">
            <h3>Success Rate</h3>
            <p class="value rate">{success_rate:.1f}%</p>
        </div>
    </div>
"""
        
        # Group results by browser
        browser_results = {}
        for result in results:
            if result.browser not in browser_results:
                browser_results[result.browser] = {}
            if result.device not in browser_results[result.browser]:
                browser_results[result.browser][result.device] = {'passed': 0, 'failed': 0, 'tests': []}
            
            if result.passed:
                browser_results[result.browser][result.device]['passed'] += 1
            else:
                browser_results[result.browser][result.device]['failed'] += 1
            browser_results[result.browser][result.device]['tests'].append(result)
            
        # Add browser results
        html += '<div class="results-grid">'
        
        for browser, devices in browser_results.items():
            html += f'''
    <div class="browser-results">
        <div class="browser-header">
            🌐 {browser.title()}
        </div>
'''
            
            for device, stats in devices.items():
                total = stats['passed'] + stats['failed']
                status_class = "status-pass" if stats['failed'] == 0 else "status-fail"
                status_text = "✅ All Passed" if stats['failed'] == 0 else f"❌ {stats['failed']} Failed"
                
                html += f'''
        <div class="device-result">
            <div class="device-name">📱 {device}</div>
            <div class="test-status">
                <span>{stats['passed']}/{total}</span>
                <span class="status-badge {status_class}">{status_text}</span>
            </div>
        </div>
'''
            
            html += '</div>'
            
        html += '</div>'
        
        # Add failures section
        failed_results = [r for r in results if not r.passed]
        if failed_results:
            html += '''
    <div class="failures-section">
        <div class="failures-header">
            🚨 Test Failures
        </div>
'''
            
            for failure in failed_results[:20]:  # Show first 20 failures
                html += f'''
        <div class="failure-item">
            <div class="failure-title">
                {failure.browser.title()} / {failure.device} - {failure.page}
            </div>
            <div class="failure-details">
                <strong>Test:</strong> {failure.test_name}<br>
                <strong>Error:</strong> {failure.error_message}
            </div>
        </div>
'''
            
            if len(failed_results) > 20:
                html += f'<div class="failure-item"><em>... and {len(failed_results) - 20} more failures</em></div>'
                
            html += '</div>'
            
        html += '''
</body>
</html>
'''
        
        return html
        
    def save_reports(self, results):
        """Save test reports in multiple formats."""
        reports_dir = Path("cross_browser_reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Text report
        text_report = self.tester.generate_report()
        text_file = reports_dir / "cross_browser_report.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(text_report)
        print(f"📄 Text report saved: {text_file}")
        
        # HTML report
        html_report = self.generate_html_report(results)
        html_file = reports_dir / "cross_browser_report.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_report)
        print(f"📄 HTML report saved: {html_file}")
        
        # JSON report
        json_report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_tests': len(results),
                'passed_tests': len([r for r in results if r.passed]),
                'failed_tests': len([r for r in results if not r.passed]),
                'success_rate': (len([r for r in results if r.passed]) / len(results) * 100) if results else 0
            },
            'results': [
                {
                    'browser': r.browser,
                    'device': r.device,
                    'page': r.page,
                    'test_name': r.test_name,
                    'passed': r.passed,
                    'error_message': r.error_message,
                    'execution_time': r.execution_time
                }
                for r in results
            ]
        }
        
        json_file = reports_dir / "cross_browser_report.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_report, f, indent=2)
        print(f"📄 JSON report saved: {json_file}")


def main():
    """Main function to run cross-browser tests."""
    parser = argparse.ArgumentParser(description='Run CodeXam cross-browser tests')
    parser.add_argument('--browsers', type=str,
                       help='Comma-separated list of browsers to test (chrome,firefox,edge)')
    parser.add_argument('--devices', type=str,
                       help='Comma-separated list of device categories to test (desktop,tablet,mobile)')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browsers in headless mode (default: True)')
    parser.add_argument('--parallel', action='store_true',
                       help='Run tests in parallel for faster execution')
    parser.add_argument('--url', type=str, default='http://localhost:5000',
                       help='Base URL for testing (default: http://localhost:5000)')
    parser.add_argument('--config', type=str, default='device_testing_config.json',
                       help='Configuration file path')
    
    args = parser.parse_args()
    
    # Parse browsers and devices
    browsers = args.browsers.split(',') if args.browsers else None
    devices = args.devices.split(',') if args.devices else None
    
    # Create test runner
    runner = CrossBrowserTestRunner(args.config, args.url)
    
    try:
        # Run tests
        results = runner.run_tests(
            browsers=browsers,
            devices=devices,
            headless=args.headless,
            parallel=args.parallel
        )
        
        if not results:
            print("❌ No tests were executed")
            sys.exit(1)
            
        # Save reports
        runner.save_reports(results)
        
        # Exit with appropriate code
        failed_tests = len([r for r in results if not r.passed])
        success_rate = (len([r for r in results if r.passed]) / len(results) * 100) if results else 0
        
        if failed_tests > 0:
            print(f"\n❌ Cross-browser testing failed: {failed_tests} tests failed ({success_rate:.1f}% success rate)")
            sys.exit(1)
        else:
            print(f"\n✅ Cross-browser testing passed: All tests successful ({success_rate:.1f}% success rate)")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()