#!/usr/bin/env python3
"""
Responsive Design Testing for CodeXam UI Templates

This module tests responsive design implementation across different screen sizes
and devices to ensure optimal user experience on all platforms.

Requirements addressed: Requirement 7 - Responsive design principles
"""

import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ResponsiveBreakpoint:
    """Represents a responsive breakpoint configuration."""
    name: str
    min_width: int
    max_width: int
    description: str


@dataclass
class ResponsiveTestResult:
    """Test result for responsive design testing."""
    breakpoint: str
    test_name: str
    passed: bool
    error_message: str = ""
    screenshot_path: str = ""


class ResponsiveDesignTester:
    """Main responsive design testing class."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.driver = None
        self.results: List[ResponsiveTestResult] = []
        
        # Bootstrap 5 breakpoints (matching CodeXam design)
        self.breakpoints = {
            'xs': ResponsiveBreakpoint('xs', 0, 575, 'Extra small devices (phones)'),
            'sm': ResponsiveBreakpoint('sm', 576, 767, 'Small devices (landscape phones)'),
            'md': ResponsiveBreakpoint('md', 768, 991, 'Medium devices (tablets)'),
            'lg': ResponsiveBreakpoint('lg', 992, 1199, 'Large devices (desktops)'),
            'xl': ResponsiveBreakpoint('xl', 1200, 1399, 'Extra large devices (large desktops)'),
            'xxl': ResponsiveBreakpoint('xxl', 1400, 9999, 'Extra extra large devices')
        }
        
        # Test viewports for each breakpoint
        self.test_viewports = {
            'xs': [(320, 568), (375, 667)],  # iPhone SE, iPhone 6/7/8
            'sm': [(576, 768), (667, 375)],  # Small landscape, iPhone landscape
            'md': [(768, 1024), (800, 600)], # iPad portrait, small tablet
            'lg': [(992, 768), (1024, 768)], # Desktop, laptop
            'xl': [(1200, 800), (1366, 768)], # Large desktop, standard laptop
            'xxl': [(1400, 900), (1920, 1080)] # Very large desktop, full HD
        }
        
    def setup_driver(self, width: int, height: int, headless: bool = True) -> webdriver.Chrome:
        """Set up Chrome WebDriver with specific viewport size."""
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--window-size={width},{height}')
        
        # Mobile emulation for small screens
        if width <= 768:
            mobile_emulation = {
                "deviceMetrics": {
                    "width": width,
                    "height": height,
                    "pixelRatio": 2.0
                },
                "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)
            
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(width, height)
        self.driver.implicitly_wait(10)
        return self.driver
        
    def teardown_driver(self):
        """Clean up WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    def test_viewport_meta_tag(self, page_url: str) -> Tuple[bool, str]:
        """Test for proper viewport meta tag."""
        try:
            self.driver.get(page_url)
            
            viewport_meta = self.driver.find_elements(By.CSS_SELECTOR, "meta[name='viewport']")
            
            if not viewport_meta:
                return False, "Missing viewport meta tag"
                
            viewport_content = viewport_meta[0].get_attribute('content')
            
            # Check for essential viewport properties
            required_properties = ['width=device-width', 'initial-scale=1']
            for prop in required_properties:
                if prop not in viewport_content:
                    return False, f"Viewport meta tag missing '{prop}'"
                    
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_horizontal_scroll(self, breakpoint_name: str) -> Tuple[bool, str]:
        """Test for unwanted horizontal scrolling."""
        try:
            # Get page dimensions
            body_width = self.driver.execute_script("return document.body.scrollWidth")
            window_width = self.driver.execute_script("return window.innerWidth")
            
            # Allow small tolerance for rounding
            if body_width > window_width + 5:
                return False, f"Horizontal scroll detected: body={body_width}px, window={window_width}px"
                
            # Check for elements extending beyond viewport
            overflowing_elements = self.driver.execute_script("""
                var elements = document.querySelectorAll('*');
                var overflowing = [];
                var windowWidth = window.innerWidth;
                
                for (var i = 0; i < elements.length; i++) {
                    var el = elements[i];
                    var rect = el.getBoundingClientRect();
                    
                    if (rect.right > windowWidth + 5) {
                        overflowing.push({
                            tag: el.tagName,
                            className: el.className,
                            right: rect.right,
                            width: rect.width
                        });
                    }
                }
                
                return overflowing.slice(0, 3); // Return first 3
            """)
            
            if overflowing_elements:
                element_info = overflowing_elements[0]
                return False, f"Element extends beyond viewport: {element_info['tag']}.{element_info['className']} (right: {element_info['right']}px)"
                
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_navigation_responsiveness(self, breakpoint_name: str) -> Tuple[bool, str]:
        """Test navigation responsiveness."""
        try:
            # Find navigation elements
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, .navbar")
            
            if not nav_elements:
                return True, "No navigation found"
                
            nav = nav_elements[0]
            
            # For mobile breakpoints, check for hamburger menu
            if breakpoint_name in ['xs', 'sm']:
                hamburger = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".navbar-toggle, .hamburger, [data-bs-toggle='collapse'], .navbar-toggler")
                
                if not hamburger:
                    return False, "Missing mobile navigation toggle"
                    
                # Test hamburger functionality
                hamburger[0].click()
                time.sleep(0.5)
                
                # Check if menu is visible after click
                nav_menu = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".navbar-collapse, .navbar-nav, .mobile-menu")
                
                if nav_menu:
                    menu_visible = nav_menu[0].is_displayed()
                    if not menu_visible:
                        return False, "Mobile menu not visible after toggle"
                        
            # For desktop breakpoints, check that navigation is fully visible
            elif breakpoint_name in ['lg', 'xl', 'xxl']:
                nav_links = nav.find_elements(By.CSS_SELECTOR, "a, .nav-link")
                
                if nav_links:
                    # Check if navigation links are visible
                    visible_links = [link for link in nav_links if link.is_displayed()]
                    if len(visible_links) < len(nav_links) * 0.8:  # At least 80% should be visible
                        return False, "Navigation links not fully visible on desktop"
                        
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_content_layout(self, breakpoint_name: str) -> Tuple[bool, str]:
        """Test content layout responsiveness."""
        try:
            # Test grid layouts
            grid_containers = self.driver.find_elements(By.CSS_SELECTOR, 
                ".row, .grid, .problems-grid, .stats-grid, .d-grid")
                
            for container in grid_containers:
                if not container.is_displayed():
                    continue
                    
                # Check if grid items are properly arranged
                grid_items = container.find_elements(By.CSS_SELECTOR, 
                    ".col, .col-*, [class*='col-'], .grid-item, .card")
                
                if grid_items:
                    # For mobile, items should stack vertically
                    if breakpoint_name in ['xs', 'sm']:
                        # Check if items are stacked (similar Y positions indicate horizontal layout)
                        y_positions = [item.location['y'] for item in grid_items[:3] if item.is_displayed()]
                        if len(set(y_positions)) < len(y_positions) * 0.7:  # Most should have different Y positions
                            return False, f"Grid items not stacking properly on {breakpoint_name}"
                            
            # Test text readability
            body = self.driver.find_element(By.TAG_NAME, "body")
            font_size = body.value_of_css_property("font-size")
            font_size_px = float(font_size.replace('px', ''))
            
            # Mobile devices should have readable font sizes
            if breakpoint_name in ['xs', 'sm'] and font_size_px < 14:
                return False, f"Font size too small for mobile: {font_size_px}px"
                
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_touch_targets(self, breakpoint_name: str) -> Tuple[bool, str]:
        """Test touch target sizes for mobile devices."""
        if breakpoint_name not in ['xs', 'sm']:
            return True, "Not a mobile breakpoint"
            
        try:
            # Find interactive elements
            interactive_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "button, .btn, a, input[type='button'], input[type='submit'], .clickable")
                
            for element in interactive_elements:
                if not element.is_displayed():
                    continue
                    
                size = element.size
                
                # Touch targets should be at least 44x44px (Apple HIG) or 48x48px (Material Design)
                min_size = 44
                if size['width'] < min_size or size['height'] < min_size:
                    element_text = element.text[:20] if element.text else element.get_attribute('class')
                    return False, f"Touch target too small: {element_text} ({size['width']}x{size['height']}px)"
                    
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_form_responsiveness(self, breakpoint_name: str) -> Tuple[bool, str]:
        """Test form responsiveness."""
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            
            if not forms:
                return True, "No forms found"
                
            for form in forms:
                if not form.is_displayed():
                    continue
                    
                # Test form inputs
                inputs = form.find_elements(By.CSS_SELECTOR, "input, textarea, select")
                
                for input_elem in inputs:
                    if not input_elem.is_displayed():
                        continue
                        
                    input_width = input_elem.size['width']
                    form_width = form.size['width']
                    
                    # On mobile, inputs should not be too narrow
                    if breakpoint_name in ['xs', 'sm']:
                        if input_width < form_width * 0.8:  # Should use most of form width
                            input_type = input_elem.get_attribute('type')
                            return False, f"Form input too narrow on mobile: {input_type} ({input_width}px)"
                            
                    # Test input focus on mobile
                    if breakpoint_name in ['xs', 'sm']:
                        input_elem.click()
                        time.sleep(0.2)
                        
                        # Check if input is focused
                        focused_element = self.driver.switch_to.active_element
                        if focused_element != input_elem:
                            return False, "Input focus failed on mobile"
                            
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_image_responsiveness(self, breakpoint_name: str) -> Tuple[bool, str]:
        """Test image responsiveness."""
        try:
            images = self.driver.find_elements(By.TAG_NAME, "img")
            
            for img in images:
                if not img.is_displayed():
                    continue
                    
                # Check if image has responsive classes or styles
                img_classes = img.get_attribute('class') or ''
                img_style = img.get_attribute('style') or ''
                
                # Images should be responsive
                is_responsive = (
                    'img-responsive' in img_classes or
                    'img-fluid' in img_classes or
                    'max-width: 100%' in img_style or
                    'width: 100%' in img_style
                )
                
                if not is_responsive:
                    # Check computed styles
                    max_width = img.value_of_css_property('max-width')
                    width = img.value_of_css_property('width')
                    
                    if max_width != '100%' and width != '100%':
                        img_src = img.get_attribute('src')
                        return False, f"Image not responsive: {img_src}"
                        
                # Check if image overflows container
                img_width = img.size['width']
                parent = self.driver.execute_script("return arguments[0].parentElement", img)
                parent_width = parent.size['width']
                
                if img_width > parent_width + 5:  # Allow small tolerance
                    return False, f"Image overflows container: {img_width}px > {parent_width}px"
                    
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_table_responsiveness(self, breakpoint_name: str) -> Tuple[bool, str]:
        """Test table responsiveness."""
        try:
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            
            if not tables:
                return True, "No tables found"
                
            for table in tables:
                if not table.is_displayed():
                    continue
                    
                table_width = table.size['width']
                container = self.driver.execute_script("return arguments[0].parentElement", table)
                container_width = container.size['width']
                
                # On mobile, tables should either:
                # 1. Fit within container, or
                # 2. Have horizontal scroll capability
                if breakpoint_name in ['xs', 'sm']:
                    if table_width > container_width + 5:
                        # Check if table container has overflow scroll
                        overflow_x = container.value_of_css_property('overflow-x')
                        if overflow_x not in ['scroll', 'auto']:
                            return False, f"Table overflows without scroll on mobile: {table_width}px > {container_width}px"
                            
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_code_editor_responsiveness(self, breakpoint_name: str, page_url: str) -> Tuple[bool, str]:
        """Test code editor responsiveness (specific to problem detail page)."""
        if '/problem/' not in page_url:
            return True, "Not a problem detail page"
            
        try:
            # Find code editor elements
            code_editors = self.driver.find_elements(By.CSS_SELECTOR, 
                ".code-editor, #code-editor, textarea[id*='code'], .editor-container")
                
            if not code_editors:
                return True, "No code editor found"
                
            editor = code_editors[0]
            
            # On mobile, editor should be usable
            if breakpoint_name in ['xs', 'sm']:
                editor_width = editor.size['width']
                editor_height = editor.size['height']
                
                # Editor should have reasonable dimensions
                if editor_width < 300:
                    return False, f"Code editor too narrow on mobile: {editor_width}px"
                    
                if editor_height < 200:
                    return False, f"Code editor too short on mobile: {editor_height}px"
                    
                # Test editor interaction
                editor.click()
                editor.send_keys("test code")
                
                if editor.get_attribute('value') != "test code":
                    return False, "Code editor not functional on mobile"
                    
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def run_responsive_tests(self, page_url: str, breakpoint_name: str, viewport: Tuple[int, int]) -> List[ResponsiveTestResult]:
        """Run responsive tests for a specific breakpoint and viewport."""
        width, height = viewport
        results = []
        
        print(f"  Testing {breakpoint_name} ({width}x{height})...")
        
        try:
            self.setup_driver(width, height, headless=True)
            self.driver.get(page_url)
            time.sleep(2)  # Allow page to load
            
            # Test 1: Viewport Meta Tag
            passed, error = self.test_viewport_meta_tag(page_url)
            results.append(ResponsiveTestResult(
                breakpoint=f"{breakpoint_name}_{width}x{height}",
                test_name="viewport_meta_tag",
                passed=passed,
                error_message=error
            ))
            
            # Test 2: Horizontal Scroll
            passed, error = self.test_horizontal_scroll(breakpoint_name)
            results.append(ResponsiveTestResult(
                breakpoint=f"{breakpoint_name}_{width}x{height}",
                test_name="horizontal_scroll",
                passed=passed,
                error_message=error
            ))
            
            # Test 3: Navigation Responsiveness
            passed, error = self.test_navigation_responsiveness(breakpoint_name)
            results.append(ResponsiveTestResult(
                breakpoint=f"{breakpoint_name}_{width}x{height}",
                test_name="navigation_responsiveness",
                passed=passed,
                error_message=error
            ))
            
            # Test 4: Content Layout
            passed, error = self.test_content_layout(breakpoint_name)
            results.append(ResponsiveTestResult(
                breakpoint=f"{breakpoint_name}_{width}x{height}",
                test_name="content_layout",
                passed=passed,
                error_message=error
            ))
            
            # Test 5: Touch Targets (mobile only)
            passed, error = self.test_touch_targets(breakpoint_name)
            results.append(ResponsiveTestResult(
                breakpoint=f"{breakpoint_name}_{width}x{height}",
                test_name="touch_targets",
                passed=passed,
                error_message=error
            ))
            
            # Test 6: Form Responsiveness
            passed, error = self.test_form_responsiveness(breakpoint_name)
            results.append(ResponsiveTestResult(
                breakpoint=f"{breakpoint_name}_{width}x{height}",
                test_name="form_responsiveness",
                passed=passed,
                error_message=error
            ))
            
            # Test 7: Image Responsiveness
            passed, error = self.test_image_responsiveness(breakpoint_name)
            results.append(ResponsiveTestResult(
                breakpoint=f"{breakpoint_name}_{width}x{height}",
                test_name="image_responsiveness",
                passed=passed,
                error_message=error
            ))
            
            # Test 8: Table Responsiveness
            passed, error = self.test_table_responsiveness(breakpoint_name)
            results.append(ResponsiveTestResult(
                breakpoint=f"{breakpoint_name}_{width}x{height}",
                test_name="table_responsiveness",
                passed=passed,
                error_message=error
            ))
            
            # Test 9: Code Editor Responsiveness (problem pages only)
            passed, error = self.test_code_editor_responsiveness(breakpoint_name, page_url)
            results.append(ResponsiveTestResult(
                breakpoint=f"{breakpoint_name}_{width}x{height}",
                test_name="code_editor_responsiveness",
                passed=passed,
                error_message=error
            ))
            
        except Exception as e:
            print(f"Error testing {breakpoint_name} ({width}x{height}): {e}")
            
        finally:
            self.teardown_driver()
            
        return results
        
    def run_comprehensive_responsive_test(self, pages: List[str] = None) -> List[ResponsiveTestResult]:
        """Run comprehensive responsive design tests."""
        print("📱 Starting Responsive Design Testing")
        print("=" * 50)
        
        if pages is None:
            pages = [
                '/',
                '/problems',
                '/problem/1',
                '/submissions',
                '/leaderboard'
            ]
            
        all_results = []
        
        for page in pages:
            page_url = f"{self.base_url}{page}"
            print(f"\nTesting page: {page}")
            
            # Test key breakpoints
            key_breakpoints = ['xs', 'sm', 'md', 'lg', 'xl']
            
            for breakpoint_name in key_breakpoints:
                if breakpoint_name not in self.test_viewports:
                    continue
                    
                viewports = self.test_viewports[breakpoint_name]
                
                # Test first viewport for each breakpoint
                viewport = viewports[0]
                page_results = self.run_responsive_tests(page_url, breakpoint_name, viewport)
                all_results.extend(page_results)
                
        self.results = all_results
        return all_results
        
    def generate_report(self) -> str:
        """Generate responsive design test report."""
        if not self.results:
            return "No responsive design test results available."
            
        report = []
        report.append("📱 Responsive Design Testing Report")
        report.append("=" * 50)
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.passed])
        failed_tests = total_tests - passed_tests
        
        report.append("📊 Summary")
        report.append(f"Total Tests: {total_tests}")
        report.append(f"✅ Passed: {passed_tests}")
        report.append(f"❌ Failed: {failed_tests}")
        report.append(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        report.append("")
        
        # Results by breakpoint
        breakpoint_results = {}
        for result in self.results:
            breakpoint = result.breakpoint.split('_')[0]  # Extract breakpoint name
            if breakpoint not in breakpoint_results:
                breakpoint_results[breakpoint] = {'passed': 0, 'failed': 0}
            if result.passed:
                breakpoint_results[breakpoint]['passed'] += 1
            else:
                breakpoint_results[breakpoint]['failed'] += 1
                
        report.append("📱 Results by Breakpoint:")
        for breakpoint, stats in breakpoint_results.items():
            total = stats['passed'] + stats['failed']
            rate = (stats['passed'] / total * 100) if total > 0 else 0
            status = "✅" if stats['failed'] == 0 else "❌"
            bp_info = self.breakpoints.get(breakpoint, type('', (), {'description': 'Unknown'})())
            report.append(f"  {status} {breakpoint.upper()}: {stats['passed']}/{total} ({rate:.1f}%) - {bp_info.description}")
            
        report.append("")
        
        # Failed tests
        failed_results = [r for r in self.results if not r.passed]
        if failed_results:
            report.append("❌ Failed Tests:")
            for failure in failed_results:
                report.append(f"  • {failure.breakpoint} - {failure.test_name}: {failure.error_message}")
                
        report.append("")
        
        # Recommendations
        report.append("💡 Recommendations:")
        if failed_tests > 0:
            report.append("1. Fix responsive design issues before deployment")
            report.append("2. Test on actual devices for validation")
            report.append("3. Implement mobile-first design approach")
            report.append("4. Use CSS Grid and Flexbox for flexible layouts")
            report.append("5. Ensure touch targets meet minimum size requirements")
        else:
            report.append("1. All responsive tests passed!")
            report.append("2. Consider testing on additional device sizes")
            report.append("3. Validate with real device testing")
            
        return "\n".join(report)


def main():
    """Main function to run responsive design tests."""
    tester = ResponsiveDesignTester()
    
    # Run tests
    results = tester.run_comprehensive_responsive_test()
    
    # Generate report
    report = tester.generate_report()
    print("\n" + report)
    
    # Save report
    with open("responsive_design_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"📄 Report saved to: responsive_design_report.txt")
    
    # Return exit code
    failed_tests = len([r for r in results if not r.passed])
    if failed_tests > 0:
        print(f"\n❌ Responsive design testing failed: {failed_tests} tests failed")
        return 1
    else:
        print(f"\n✅ Responsive design testing passed: All tests successful")
        return 0


if __name__ == "__main__":
    exit(main())