#!/usr/bin/env python3
"""
Comprehensive Accessibility Testing Suite for CodeXam UI Templates

This module implements automated accessibility testing to ensure WCAG 2.1 AA compliance
across all UI templates. It tests color contrast, keyboard navigation, ARIA labels,
screen reader compatibility, and other accessibility requirements.

Requirements addressed: Requirement 7 - Accessibility and responsive design
"""

import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class AccessibilityIssue:
    """Represents an accessibility issue found during testing."""
    severity: str  # 'critical', 'major', 'minor'
    type: str      # 'contrast', 'aria', 'keyboard', 'structure'
    element: str   # CSS selector or description
    description: str
    wcag_criterion: str
    page: str


@dataclass
class ColorContrastResult:
    """Represents a color contrast test result."""
    foreground: str
    background: str
    ratio: float
    passes_aa: bool
    passes_aaa: bool
    element: str


class AccessibilityTester:
    """Main accessibility testing class."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.driver = None
        self.issues: List[AccessibilityIssue] = []
        self.test_results = {
            'color_contrast': [],
            'keyboard_navigation': [],
            'aria_labels': [],
            'screen_reader': [],
            'structure': []
        }
        
    def setup_driver(self, headless: bool = True):
        """Set up Chrome WebDriver with accessibility testing options."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Enable accessibility features
        chrome_options.add_argument("--force-renderer-accessibility")
        chrome_options.add_argument("--enable-accessibility-logging")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def teardown_driver(self):
        """Clean up WebDriver."""
        if self.driver:
            self.driver.quit()
            
    def get_page_content(self, url: str) -> BeautifulSoup:
        """Get page content for static analysis."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def test_color_contrast(self, page_url: str) -> List[ColorContrastResult]:
        """Test color contrast ratios for WCAG compliance."""
        print(f"Testing color contrast for {page_url}")
        
        self.driver.get(page_url)
        time.sleep(2)  # Allow page to load
        
        # Inject color contrast testing script
        contrast_script = """
        function getContrastRatio(fg, bg) {
            function getLuminance(color) {
                const rgb = color.match(/\\d+/g);
                if (!rgb) return 0;
                
                const [r, g, b] = rgb.map(c => {
                    c = parseInt(c) / 255;
                    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
                });
                
                return 0.2126 * r + 0.7152 * g + 0.0722 * b;
            }
            
            const l1 = getLuminance(fg);
            const l2 = getLuminance(bg);
            const lighter = Math.max(l1, l2);
            const darker = Math.min(l1, l2);
            
            return (lighter + 0.05) / (darker + 0.05);
        }
        
        const results = [];
        const elements = document.querySelectorAll('*');
        
        elements.forEach(el => {
            const style = window.getComputedStyle(el);
            const color = style.color;
            const backgroundColor = style.backgroundColor;
            
            if (color && backgroundColor && 
                color !== 'rgba(0, 0, 0, 0)' && 
                backgroundColor !== 'rgba(0, 0, 0, 0)') {
                
                const ratio = getContrastRatio(color, backgroundColor);
                const fontSize = parseFloat(style.fontSize);
                const fontWeight = style.fontWeight;
                
                const isLargeText = fontSize >= 18 || (fontSize >= 14 && fontWeight >= 700);
                const aaThreshold = isLargeText ? 3.0 : 4.5;
                const aaaThreshold = isLargeText ? 4.5 : 7.0;
                
                results.push({
                    element: el.tagName + (el.className ? '.' + el.className.split(' ')[0] : ''),
                    foreground: color,
                    background: backgroundColor,
                    ratio: ratio,
                    passes_aa: ratio >= aaThreshold,
                    passes_aaa: ratio >= aaaThreshold,
                    font_size: fontSize,
                    is_large_text: isLargeText
                });
            }
        });
        
        return results;
        """
        
        try:
            results = self.driver.execute_script(contrast_script)
            contrast_results = []
            
            for result in results:
                contrast_result = ColorContrastResult(
                    foreground=result['foreground'],
                    background=result['background'],
                    ratio=result['ratio'],
                    passes_aa=result['passes_aa'],
                    passes_aaa=result['passes_aaa'],
                    element=result['element']
                )
                contrast_results.append(contrast_result)
                
                # Record issues for AA failures
                if not result['passes_aa']:
                    self.issues.append(AccessibilityIssue(
                        severity='major',
                        type='contrast',
                        element=result['element'],
                        description=f"Color contrast ratio {result['ratio']:.2f} fails WCAG AA standard",
                        wcag_criterion='1.4.3 Contrast (Minimum)',
                        page=page_url
                    ))
                    
            return contrast_results
            
        except Exception as e:
            print(f"Error testing color contrast: {e}")
            return []

    def test_keyboard_navigation(self, page_url: str) -> Dict[str, bool]:
        """Test keyboard navigation functionality."""
        print(f"Testing keyboard navigation for {page_url}")
        
        self.driver.get(page_url)
        time.sleep(2)
        
        results = {
            'tab_navigation': False,
            'skip_links': False,
            'focus_visible': False,
            'keyboard_traps': False,
            'logical_order': False
        }
        
        try:
            # Test tab navigation
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.click()  # Focus on page
            
            # Get all focusable elements
            focusable_script = """
            const focusableElements = document.querySelectorAll(
                'a[href], button, input, textarea, select, details, [tabindex]:not([tabindex="-1"])'
            );
            return Array.from(focusableElements).map(el => ({
                tag: el.tagName,
                id: el.id,
                className: el.className,
                tabIndex: el.tabIndex,
                visible: el.offsetParent !== null
            }));
            """
            
            focusable_elements = self.driver.execute_script(focusable_script)
            visible_focusable = [el for el in focusable_elements if el['visible']]
            
            if len(visible_focusable) > 0:
                results['tab_navigation'] = True
                
                # Test tab order
                current_element = self.driver.switch_to.active_element
                tab_order = []
                
                for i in range(min(10, len(visible_focusable))):  # Test first 10 elements
                    current_element.send_keys(Keys.TAB)
                    time.sleep(0.1)
                    new_element = self.driver.switch_to.active_element
                    
                    if new_element != current_element:
                        tab_order.append({
                            'tag': new_element.tag_name,
                            'id': new_element.get_attribute('id'),
                            'class': new_element.get_attribute('class')
                        })
                        current_element = new_element
                    else:
                        break
                
                results['logical_order'] = len(tab_order) > 0
                
            # Test for skip links
            skip_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='#']")
            skip_link_texts = ['skip to main', 'skip to content', 'skip navigation']
            
            for link in skip_links:
                link_text = link.get_attribute('textContent').lower()
                if any(skip_text in link_text for skip_text in skip_link_texts):
                    results['skip_links'] = True
                    break
                    
            # Test focus visibility
            focus_script = """
            const testElement = document.querySelector('button, a, input');
            if (testElement) {
                testElement.focus();
                const style = window.getComputedStyle(testElement, ':focus');
                return style.outline !== 'none' || style.boxShadow !== 'none';
            }
            return false;
            """
            
            results['focus_visible'] = self.driver.execute_script(focus_script)
            
        except Exception as e:
            print(f"Error testing keyboard navigation: {e}")
            
        # Record issues
        for test, passed in results.items():
            if not passed:
                self.issues.append(AccessibilityIssue(
                    severity='major',
                    type='keyboard',
                    element='page',
                    description=f"Keyboard navigation test failed: {test}",
                    wcag_criterion='2.1.1 Keyboard',
                    page=page_url
                ))
                
        return results

    def test_aria_labels(self, page_url: str) -> Dict[str, List[str]]:
        """Test ARIA labels and accessibility attributes."""
        print(f"Testing ARIA labels for {page_url}")
        
        self.driver.get(page_url)
        time.sleep(2)
        
        results = {
            'missing_alt_text': [],
            'missing_labels': [],
            'invalid_aria': [],
            'missing_headings': [],
            'missing_landmarks': []
        }
        
        try:
            # Test for missing alt text on images
            images = self.driver.find_elements(By.TAG_NAME, "img")
            for img in images:
                alt_text = img.get_attribute('alt')
                src = img.get_attribute('src')
                if alt_text is None or alt_text.strip() == '':
                    results['missing_alt_text'].append(src or 'unknown')
                    
            # Test for missing form labels
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input, textarea, select")
            for input_elem in inputs:
                input_id = input_elem.get_attribute('id')
                input_type = input_elem.get_attribute('type')
                
                # Skip hidden inputs
                if input_type == 'hidden':
                    continue
                    
                # Check for label
                label = None
                if input_id:
                    try:
                        label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                    except NoSuchElementException:
                        pass
                        
                # Check for aria-label or aria-labelledby
                aria_label = input_elem.get_attribute('aria-label')
                aria_labelledby = input_elem.get_attribute('aria-labelledby')
                
                if not label and not aria_label and not aria_labelledby:
                    results['missing_labels'].append(f"{input_elem.tag_name}#{input_id or 'no-id'}")
                    
            # Test heading structure
            headings = self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
            if len(headings) == 0:
                results['missing_headings'].append('No headings found on page')
            else:
                # Check for h1
                h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
                if len(h1_elements) == 0:
                    results['missing_headings'].append('No h1 element found')
                elif len(h1_elements) > 1:
                    results['missing_headings'].append('Multiple h1 elements found')
                    
            # Test for landmarks
            landmarks = self.driver.find_elements(By.CSS_SELECTOR, 
                "main, nav, header, footer, aside, section[aria-label], [role='main'], [role='navigation'], [role='banner'], [role='contentinfo']")
            
            required_landmarks = ['main', 'navigation']
            found_landmarks = []
            
            for landmark in landmarks:
                role = landmark.get_attribute('role')
                tag = landmark.tag_name.lower()
                
                if role:
                    found_landmarks.append(role)
                elif tag in ['main', 'nav', 'header', 'footer']:
                    landmark_map = {'nav': 'navigation', 'header': 'banner', 'footer': 'contentinfo'}
                    found_landmarks.append(landmark_map.get(tag, tag))
                    
            for required in required_landmarks:
                if required not in found_landmarks:
                    results['missing_landmarks'].append(f"Missing {required} landmark")
                    
        except Exception as e:
            print(f"Error testing ARIA labels: {e}")
            
        # Record issues
        for category, issues in results.items():
            for issue in issues:
                self.issues.append(AccessibilityIssue(
                    severity='major',
                    type='aria',
                    element=issue,
                    description=f"ARIA/accessibility issue: {category}",
                    wcag_criterion='4.1.2 Name, Role, Value',
                    page=page_url
                ))
                
        return results

    def test_screen_reader_compatibility(self, page_url: str) -> Dict[str, bool]:
        """Test screen reader compatibility features."""
        print(f"Testing screen reader compatibility for {page_url}")
        
        self.driver.get(page_url)
        time.sleep(2)
        
        results = {
            'semantic_html': False,
            'aria_live_regions': False,
            'descriptive_links': False,
            'table_headers': False,
            'form_instructions': False
        }
        
        try:
            # Test semantic HTML usage
            semantic_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "main, nav, header, footer, article, section, aside")
            results['semantic_html'] = len(semantic_elements) > 0
            
            # Test for ARIA live regions
            live_regions = self.driver.find_elements(By.CSS_SELECTOR, 
                "[aria-live], [role='status'], [role='alert']")
            results['aria_live_regions'] = len(live_regions) > 0
            
            # Test descriptive link text
            links = self.driver.find_elements(By.TAG_NAME, "a")
            descriptive_links = 0
            generic_terms = ['click here', 'read more', 'more', 'here', 'link']
            
            for link in links:
                link_text = link.get_attribute('textContent').lower().strip()
                if link_text and not any(term in link_text for term in generic_terms):
                    descriptive_links += 1
                    
            results['descriptive_links'] = descriptive_links > len(links) * 0.8 if links else True
            
            # Test table headers
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            if tables:
                tables_with_headers = 0
                for table in tables:
                    headers = table.find_elements(By.TAG_NAME, "th")
                    if headers:
                        tables_with_headers += 1
                results['table_headers'] = tables_with_headers == len(tables)
            else:
                results['table_headers'] = True  # No tables to test
                
            # Test form instructions
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            if forms:
                forms_with_instructions = 0
                for form in forms:
                    instructions = form.find_elements(By.CSS_SELECTOR, 
                        ".form-text, .help-text, [aria-describedby]")
                    if instructions:
                        forms_with_instructions += 1
                results['form_instructions'] = forms_with_instructions > 0
            else:
                results['form_instructions'] = True  # No forms to test
                
        except Exception as e:
            print(f"Error testing screen reader compatibility: {e}")
            
        # Record issues
        for test, passed in results.items():
            if not passed:
                self.issues.append(AccessibilityIssue(
                    severity='major',
                    type='screen_reader',
                    element='page',
                    description=f"Screen reader compatibility issue: {test}",
                    wcag_criterion='4.1.3 Status Messages',
                    page=page_url
                ))
                
        return results

    def test_page_structure(self, page_url: str) -> Dict[str, bool]:
        """Test page structure and document outline."""
        print(f"Testing page structure for {page_url}")
        
        self.driver.get(page_url)
        time.sleep(2)
        
        results = {
            'valid_html': False,
            'proper_nesting': False,
            'unique_ids': False,
            'lang_attribute': False,
            'page_title': False
        }
        
        try:
            # Test for lang attribute
            html_element = self.driver.find_element(By.TAG_NAME, "html")
            lang = html_element.get_attribute('lang')
            results['lang_attribute'] = bool(lang and lang.strip())
            
            # Test for page title
            title = self.driver.title
            results['page_title'] = bool(title and title.strip() and title != 'Document')
            
            # Test for unique IDs
            id_script = """
            const elements = document.querySelectorAll('[id]');
            const ids = Array.from(elements).map(el => el.id);
            const uniqueIds = new Set(ids);
            return ids.length === uniqueIds.size;
            """
            results['unique_ids'] = self.driver.execute_script(id_script)
            
            # Test proper nesting (basic check)
            nesting_script = """
            const buttons = document.querySelectorAll('button');
            const links = document.querySelectorAll('a');
            
            for (let button of buttons) {
                if (button.querySelector('a') || button.closest('a')) {
                    return false;
                }
            }
            
            for (let link of links) {
                if (link.querySelector('button') || link.closest('button')) {
                    return false;
                }
            }
            
            return true;
            """
            results['proper_nesting'] = self.driver.execute_script(nesting_script)
            
            # Basic HTML validation (check for common issues)
            validation_script = """
            const issues = [];
            
            // Check for missing alt attributes on images
            const images = document.querySelectorAll('img:not([alt])');
            if (images.length > 0) issues.push('Missing alt attributes');
            
            // Check for empty headings
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            for (let heading of headings) {
                if (!heading.textContent.trim()) {
                    issues.push('Empty heading found');
                    break;
                }
            }
            
            return issues.length === 0;
            """
            results['valid_html'] = self.driver.execute_script(validation_script)
            
        except Exception as e:
            print(f"Error testing page structure: {e}")
            
        # Record issues
        for test, passed in results.items():
            if not passed:
                self.issues.append(AccessibilityIssue(
                    severity='major',
                    type='structure',
                    element='page',
                    description=f"Page structure issue: {test}",
                    wcag_criterion='4.1.1 Parsing',
                    page=page_url
                ))
                
        return results

    def run_comprehensive_test(self, pages: List[str]) -> Dict:
        """Run comprehensive accessibility tests on all pages."""
        print("Starting comprehensive accessibility testing...")
        
        self.setup_driver()
        
        try:
            all_results = {}
            
            for page in pages:
                page_url = urljoin(self.base_url, page)
                print(f"\nTesting page: {page_url}")
                
                page_results = {
                    'color_contrast': self.test_color_contrast(page_url),
                    'keyboard_navigation': self.test_keyboard_navigation(page_url),
                    'aria_labels': self.test_aria_labels(page_url),
                    'screen_reader': self.test_screen_reader_compatibility(page_url),
                    'structure': self.test_page_structure(page_url)
                }
                
                all_results[page] = page_results
                
        finally:
            self.teardown_driver()
            
        return all_results

    def generate_report(self, results: Dict) -> str:
        """Generate a comprehensive accessibility report."""
        report = []
        report.append("# CodeXam Accessibility Testing Report")
        report.append("=" * 50)
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_issues = len(self.issues)
        critical_issues = len([i for i in self.issues if i.severity == 'critical'])
        major_issues = len([i for i in self.issues if i.severity == 'major'])
        minor_issues = len([i for i in self.issues if i.severity == 'minor'])
        
        report.append("## Summary")
        report.append(f"Total Issues Found: {total_issues}")
        report.append(f"- Critical: {critical_issues}")
        report.append(f"- Major: {major_issues}")
        report.append(f"- Minor: {minor_issues}")
        report.append("")
        
        # WCAG Compliance Status
        wcag_status = "PASS" if critical_issues == 0 and major_issues == 0 else "FAIL"
        report.append(f"## WCAG 2.1 AA Compliance: {wcag_status}")
        report.append("")
        
        # Detailed Results by Page
        for page, page_results in results.items():
            report.append(f"## Page: {page}")
            report.append("-" * 30)
            
            for test_type, test_results in page_results.items():
                report.append(f"### {test_type.replace('_', ' ').title()}")
                
                if test_type == 'color_contrast':
                    failing_contrasts = [r for r in test_results if not r.passes_aa]
                    report.append(f"- Total elements tested: {len(test_results)}")
                    report.append(f"- Failing AA standard: {len(failing_contrasts)}")
                    
                    if failing_contrasts:
                        report.append("- Failing elements:")
                        for contrast in failing_contrasts[:5]:  # Show first 5
                            report.append(f"  - {contrast.element}: {contrast.ratio:.2f}")
                            
                elif isinstance(test_results, dict):
                    for test, result in test_results.items():
                        status = "✓" if result else "✗"
                        report.append(f"- {test.replace('_', ' ').title()}: {status}")
                        
                report.append("")
                
        # Issues by Category
        if self.issues:
            report.append("## Issues by Category")
            
            issues_by_type = {}
            for issue in self.issues:
                if issue.type not in issues_by_type:
                    issues_by_type[issue.type] = []
                issues_by_type[issue.type].append(issue)
                
            for issue_type, type_issues in issues_by_type.items():
                report.append(f"### {issue_type.replace('_', ' ').title()} Issues")
                for issue in type_issues[:10]:  # Show first 10 per category
                    report.append(f"- **{issue.severity.upper()}**: {issue.description}")
                    report.append(f"  - Element: {issue.element}")
                    report.append(f"  - WCAG: {issue.wcag_criterion}")
                    report.append(f"  - Page: {issue.page}")
                    report.append("")
                    
        # Recommendations
        report.append("## Recommendations")
        report.append("1. Fix all critical and major accessibility issues")
        report.append("2. Implement proper ARIA labels for interactive elements")
        report.append("3. Ensure all images have descriptive alt text")
        report.append("4. Improve color contrast ratios to meet WCAG AA standards")
        report.append("5. Test with actual screen readers (NVDA, JAWS, VoiceOver)")
        report.append("6. Implement keyboard navigation testing in CI/CD pipeline")
        report.append("")
        
        return "\n".join(report)


# Test fixtures and pytest integration
@pytest.fixture
def accessibility_tester():
    """Pytest fixture for accessibility tester."""
    return AccessibilityTester()


class TestAccessibility:
    """Pytest test class for accessibility testing."""
    
    def test_homepage_accessibility(self, accessibility_tester):
        """Test homepage accessibility."""
        results = accessibility_tester.run_comprehensive_test(['/'])
        
        # Assert no critical issues
        critical_issues = [i for i in accessibility_tester.issues if i.severity == 'critical']
        assert len(critical_issues) == 0, f"Critical accessibility issues found: {critical_issues}"
        
        # Assert basic requirements are met
        homepage_results = results['/']
        assert homepage_results['structure']['lang_attribute'], "Missing lang attribute"
        assert homepage_results['structure']['page_title'], "Missing or invalid page title"
        
    def test_problems_page_accessibility(self, accessibility_tester):
        """Test problems page accessibility."""
        results = accessibility_tester.run_comprehensive_test(['/problems'])
        
        critical_issues = [i for i in accessibility_tester.issues if i.severity == 'critical']
        assert len(critical_issues) == 0, f"Critical accessibility issues found: {critical_issues}"
        
    def test_problem_detail_accessibility(self, accessibility_tester):
        """Test problem detail page accessibility."""
        results = accessibility_tester.run_comprehensive_test(['/problem/1'])
        
        critical_issues = [i for i in accessibility_tester.issues if i.severity == 'critical']
        assert len(critical_issues) == 0, f"Critical accessibility issues found: {critical_issues}"
        
        # Test code editor accessibility
        problem_results = results['/problem/1']
        assert problem_results['keyboard_navigation']['tab_navigation'], "Code editor not keyboard accessible"
        
    def test_submissions_page_accessibility(self, accessibility_tester):
        """Test submissions page accessibility."""
        results = accessibility_tester.run_comprehensive_test(['/submissions'])
        
        critical_issues = [i for i in accessibility_tester.issues if i.severity == 'critical']
        assert len(critical_issues) == 0, f"Critical accessibility issues found: {critical_issues}"
        
    def test_leaderboard_accessibility(self, accessibility_tester):
        """Test leaderboard page accessibility."""
        results = accessibility_tester.run_comprehensive_test(['/leaderboard'])
        
        critical_issues = [i for i in accessibility_tester.issues if i.severity == 'critical']
        assert len(critical_issues) == 0, f"Critical accessibility issues found: {critical_issues}"


def main():
    """Main function to run accessibility tests and generate report."""
    tester = AccessibilityTester()
    
    # Test all main pages
    pages_to_test = [
        '/',
        '/problems',
        '/problem/1',
        '/submissions',
        '/leaderboard'
    ]
    
    print("Running comprehensive accessibility tests...")
    results = tester.run_comprehensive_test(pages_to_test)
    
    # Generate and save report
    report = tester.generate_report(results)
    
    with open('accessibility_report.txt', 'w') as f:
        f.write(report)
        
    print("\nAccessibility testing complete!")
    print(f"Report saved to: accessibility_report.txt")
    print(f"Total issues found: {len(tester.issues)}")
    
    # Print summary
    if tester.issues:
        print("\nIssue Summary:")
        for severity in ['critical', 'major', 'minor']:
            count = len([i for i in tester.issues if i.severity == severity])
            if count > 0:
                print(f"- {severity.title()}: {count}")
    else:
        print("✅ No accessibility issues found!")


if __name__ == "__main__":
    main()