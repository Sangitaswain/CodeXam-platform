#!/usr/bin/env python3
"""
CodeXam Accessibility Testing Runner

This script runs comprehensive accessibility tests on the CodeXam UI templates
and generates detailed reports for WCAG 2.1 AA compliance verification.

Usage:
    python run_accessibility_tests.py [--headless] [--pages page1,page2] [--output report.html]
"""

import argparse
import sys
import os
import json
import time
from pathlib import Path

# Add tests directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

try:
    from test_accessibility import AccessibilityTester, AccessibilityIssue
except ImportError as e:
    print(f"Error importing accessibility tester: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install selenium beautifulsoup4 requests pytest")
    sys.exit(1)


class AccessibilityTestRunner:
    """Main test runner for accessibility testing."""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.tester = AccessibilityTester(base_url)
        
    def run_tests(self, pages=None, headless=True, output_format="html"):
        """Run accessibility tests and generate reports."""
        
        if pages is None:
            pages = [
                '/',
                '/problems', 
                '/problem/1',
                '/submissions',
                '/leaderboard'
            ]
            
        print("🚀 Starting CodeXam Accessibility Testing")
        print("=" * 50)
        print(f"Base URL: {self.base_url}")
        print(f"Pages to test: {len(pages)}")
        print(f"Headless mode: {headless}")
        print("")
        
        # Run tests
        start_time = time.time()
        results = self.tester.run_comprehensive_test(pages)
        end_time = time.time()
        
        # Generate reports
        self.generate_console_report(results, end_time - start_time)
        
        if output_format == "html":
            html_report = self.generate_html_report(results)
            with open("accessibility_report.html", "w", encoding="utf-8") as f:
                f.write(html_report)
            print(f"📄 HTML report saved: accessibility_report.html")
            
        if output_format == "json":
            json_report = self.generate_json_report(results)
            with open("accessibility_report.json", "w", encoding="utf-8") as f:
                json.dump(json_report, f, indent=2, default=str)
            print(f"📄 JSON report saved: accessibility_report.json")
            
        # Generate text report
        text_report = self.tester.generate_report(results)
        with open("accessibility_report.txt", "w", encoding="utf-8") as f:
            f.write(text_report)
        print(f"📄 Text report saved: accessibility_report.txt")
        
        return results
        
    def generate_console_report(self, results, duration):
        """Generate console summary report."""
        print("📊 Test Results Summary")
        print("-" * 30)
        
        total_issues = len(self.tester.issues)
        critical_issues = len([i for i in self.tester.issues if i.severity == 'critical'])
        major_issues = len([i for i in self.tester.issues if i.severity == 'major'])
        minor_issues = len([i for i in self.tester.issues if i.severity == 'minor'])
        
        print(f"⏱️  Test Duration: {duration:.2f} seconds")
        print(f"📄 Pages Tested: {len(results)}")
        print(f"🐛 Total Issues: {total_issues}")
        
        if critical_issues > 0:
            print(f"🔴 Critical Issues: {critical_issues}")
        if major_issues > 0:
            print(f"🟡 Major Issues: {major_issues}")
        if minor_issues > 0:
            print(f"🔵 Minor Issues: {minor_issues}")
            
        # WCAG Compliance Status
        wcag_status = "✅ PASS" if critical_issues == 0 and major_issues == 0 else "❌ FAIL"
        print(f"🎯 WCAG 2.1 AA Compliance: {wcag_status}")
        print("")
        
        # Top issues by page
        if self.tester.issues:
            print("🔍 Issues by Page:")
            issues_by_page = {}
            for issue in self.tester.issues:
                page = issue.page.replace(self.base_url, '')
                if page not in issues_by_page:
                    issues_by_page[page] = []
                issues_by_page[page].append(issue)
                
            for page, page_issues in issues_by_page.items():
                critical = len([i for i in page_issues if i.severity == 'critical'])
                major = len([i for i in page_issues if i.severity == 'major'])
                minor = len([i for i in page_issues if i.severity == 'minor'])
                
                status_icon = "🔴" if critical > 0 else "🟡" if major > 0 else "🔵" if minor > 0 else "✅"
                print(f"  {status_icon} {page}: {len(page_issues)} issues")
                
        print("")
        
    def generate_html_report(self, results):
        """Generate comprehensive HTML report."""
        
        # Calculate summary stats
        total_issues = len(self.tester.issues)
        critical_issues = len([i for i in self.tester.issues if i.severity == 'critical'])
        major_issues = len([i for i in self.tester.issues if i.severity == 'major'])
        minor_issues = len([i for i in self.tester.issues if i.severity == 'minor'])
        
        wcag_status = "PASS" if critical_issues == 0 and major_issues == 0 else "FAIL"
        wcag_class = "pass" if wcag_status == "PASS" else "fail"
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeXam Accessibility Report</title>
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
        
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
        }}
        
        .header p {{
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
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
            letter-spacing: 1px;
        }}
        
        .summary-card .value {{
            font-size: 2rem;
            font-weight: bold;
            margin: 0;
        }}
        
        .critical {{ color: #e74c3c; }}
        .major {{ color: #f39c12; }}
        .minor {{ color: #3498db; }}
        .pass {{ color: #27ae60; }}
        .fail {{ color: #e74c3c; }}
        
        .wcag-status {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .wcag-status.pass {{
            border-left: 5px solid #27ae60;
        }}
        
        .wcag-status.fail {{
            border-left: 5px solid #e74c3c;
        }}
        
        .page-results {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            overflow: hidden;
        }}
        
        .page-header {{
            background: #f8f9fa;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .page-header h2 {{
            margin: 0;
            color: #495057;
        }}
        
        .test-results {{
            padding: 1.5rem;
        }}
        
        .test-category {{
            margin-bottom: 2rem;
        }}
        
        .test-category h3 {{
            color: #495057;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }}
        
        .test-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #f8f9fa;
        }}
        
        .test-item:last-child {{
            border-bottom: none;
        }}
        
        .test-name {{
            font-weight: 500;
        }}
        
        .test-status {{
            font-weight: bold;
        }}
        
        .test-status.pass {{
            color: #27ae60;
        }}
        
        .test-status.fail {{
            color: #e74c3c;
        }}
        
        .issues-section {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        
        .issues-header {{
            background: #f8f9fa;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #dee2e6;
        }}
        
        .issues-content {{
            padding: 1.5rem;
        }}
        
        .issue-item {{
            border-left: 4px solid #dee2e6;
            padding: 1rem;
            margin-bottom: 1rem;
            background: #f8f9fa;
            border-radius: 0 4px 4px 0;
        }}
        
        .issue-item.critical {{
            border-left-color: #e74c3c;
            background: #fdf2f2;
        }}
        
        .issue-item.major {{
            border-left-color: #f39c12;
            background: #fef9e7;
        }}
        
        .issue-item.minor {{
            border-left-color: #3498db;
            background: #f0f8ff;
        }}
        
        .issue-severity {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }}
        
        .issue-severity.critical {{
            background: #e74c3c;
            color: white;
        }}
        
        .issue-severity.major {{
            background: #f39c12;
            color: white;
        }}
        
        .issue-severity.minor {{
            background: #3498db;
            color: white;
        }}
        
        .issue-description {{
            font-weight: 500;
            margin-bottom: 0.5rem;
        }}
        
        .issue-details {{
            font-size: 0.9rem;
            color: #666;
        }}
        
        .recommendations {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1.5rem;
        }}
        
        .recommendations h2 {{
            color: #495057;
            margin-bottom: 1rem;
        }}
        
        .recommendations ul {{
            padding-left: 1.5rem;
        }}
        
        .recommendations li {{
            margin-bottom: 0.5rem;
        }}
        
        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}
            
            .test-item {{
                flex-direction: column;
                align-items: flex-start;
                gap: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 CodeXam Accessibility Report</h1>
        <p>Generated on {time.strftime('%Y-%m-%d at %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>Total Issues</h3>
            <p class="value">{total_issues}</p>
        </div>
        <div class="summary-card">
            <h3>Critical Issues</h3>
            <p class="value critical">{critical_issues}</p>
        </div>
        <div class="summary-card">
            <h3>Major Issues</h3>
            <p class="value major">{major_issues}</p>
        </div>
        <div class="summary-card">
            <h3>Minor Issues</h3>
            <p class="value minor">{minor_issues}</p>
        </div>
    </div>
    
    <div class="wcag-status {wcag_class}">
        <h2>WCAG 2.1 AA Compliance: <span class="{wcag_class}">{wcag_status}</span></h2>
        <p>{'All critical and major accessibility barriers have been resolved.' if wcag_status == 'PASS' else 'Critical or major accessibility issues found that prevent WCAG compliance.'}</p>
    </div>
"""
        
        # Add page results
        for page, page_results in results.items():
            html += f"""
    <div class="page-results">
        <div class="page-header">
            <h2>📄 Page: {page}</h2>
        </div>
        <div class="test-results">
"""
            
            # Add test categories
            for test_type, test_results in page_results.items():
                html += f"""
            <div class="test-category">
                <h3>{test_type.replace('_', ' ').title()}</h3>
"""
                
                if test_type == 'color_contrast':
                    total_elements = len(test_results)
                    failing_elements = len([r for r in test_results if not r.passes_aa])
                    
                    html += f"""
                <div class="test-item">
                    <span class="test-name">Elements Tested</span>
                    <span class="test-status">{total_elements}</span>
                </div>
                <div class="test-item">
                    <span class="test-name">Failing AA Standard</span>
                    <span class="test-status {'fail' if failing_elements > 0 else 'pass'}">{failing_elements}</span>
                </div>
"""
                    
                elif isinstance(test_results, dict):
                    for test, result in test_results.items():
                        status_class = "pass" if result else "fail"
                        status_text = "✓ Pass" if result else "✗ Fail"
                        
                        html += f"""
                <div class="test-item">
                    <span class="test-name">{test.replace('_', ' ').title()}</span>
                    <span class="test-status {status_class}">{status_text}</span>
                </div>
"""
                
                html += "</div>"
                
            html += """
        </div>
    </div>
"""
        
        # Add issues section
        if self.tester.issues:
            html += """
    <div class="issues-section">
        <div class="issues-header">
            <h2>🐛 Detailed Issues</h2>
        </div>
        <div class="issues-content">
"""
            
            for issue in self.tester.issues[:20]:  # Show first 20 issues
                html += f"""
            <div class="issue-item {issue.severity}">
                <span class="issue-severity {issue.severity}">{issue.severity}</span>
                <div class="issue-description">{issue.description}</div>
                <div class="issue-details">
                    <strong>Element:</strong> {issue.element}<br>
                    <strong>WCAG Criterion:</strong> {issue.wcag_criterion}<br>
                    <strong>Page:</strong> {issue.page}
                </div>
            </div>
"""
            
            if len(self.tester.issues) > 20:
                html += f"<p><em>... and {len(self.tester.issues) - 20} more issues. See full report for details.</em></p>"
                
            html += """
        </div>
    </div>
"""
        
        # Add recommendations
        html += """
    <div class="recommendations">
        <h2>📋 Recommendations</h2>
        <ul>
            <li>Fix all critical and major accessibility issues before deployment</li>
            <li>Implement proper ARIA labels for all interactive elements</li>
            <li>Ensure all images have descriptive alternative text</li>
            <li>Improve color contrast ratios to meet WCAG AA standards (4.5:1 minimum)</li>
            <li>Test with actual screen readers (NVDA, JAWS, VoiceOver)</li>
            <li>Implement keyboard navigation testing in CI/CD pipeline</li>
            <li>Conduct regular accessibility audits during development</li>
            <li>Train development team on accessibility best practices</li>
        </ul>
    </div>
    
</body>
</html>
"""
        
        return html
        
    def generate_json_report(self, results):
        """Generate JSON report for programmatic use."""
        return {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_url': self.base_url,
            'summary': {
                'total_issues': len(self.tester.issues),
                'critical_issues': len([i for i in self.tester.issues if i.severity == 'critical']),
                'major_issues': len([i for i in self.tester.issues if i.severity == 'major']),
                'minor_issues': len([i for i in self.tester.issues if i.severity == 'minor']),
                'wcag_compliant': len([i for i in self.tester.issues if i.severity in ['critical', 'major']]) == 0
            },
            'results': results,
            'issues': [
                {
                    'severity': issue.severity,
                    'type': issue.type,
                    'element': issue.element,
                    'description': issue.description,
                    'wcag_criterion': issue.wcag_criterion,
                    'page': issue.page
                }
                for issue in self.tester.issues
            ]
        }


def main():
    """Main function to run accessibility tests."""
    parser = argparse.ArgumentParser(description='Run CodeXam accessibility tests')
    parser.add_argument('--headless', action='store_true', 
                       help='Run browser in headless mode (default: True)')
    parser.add_argument('--pages', type=str,
                       help='Comma-separated list of pages to test (default: all main pages)')
    parser.add_argument('--output', choices=['html', 'json', 'text'], default='html',
                       help='Output format for detailed report (default: html)')
    parser.add_argument('--url', type=str, default='http://localhost:5000',
                       help='Base URL for testing (default: http://localhost:5000)')
    
    args = parser.parse_args()
    
    # Parse pages
    pages = None
    if args.pages:
        pages = [page.strip() for page in args.pages.split(',')]
        
    # Create test runner
    runner = AccessibilityTestRunner(args.url)
    
    try:
        # Run tests
        results = runner.run_tests(
            pages=pages,
            headless=args.headless,
            output_format=args.output
        )
        
        # Exit with error code if there are critical or major issues
        critical_issues = len([i for i in runner.tester.issues if i.severity == 'critical'])
        major_issues = len([i for i in runner.tester.issues if i.severity == 'major'])
        
        if critical_issues > 0 or major_issues > 0:
            print(f"\n❌ Accessibility testing failed: {critical_issues} critical, {major_issues} major issues")
            sys.exit(1)
        else:
            print(f"\n✅ Accessibility testing passed: No critical or major issues found")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()