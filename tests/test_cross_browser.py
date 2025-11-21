#!/usr/bin/env python3
"""
Cross-Browser and Device Testing Suite for CodeXam UI Templates

This module implements comprehensive cross-browser and device testing to ensure
consistent behavior and appearance across different browsers, operating systems,
and device types.

Requirements addressed: Requirement 7 - Cross-platform compatibility
"""

import pytest
import time
import json
import os
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWaitort WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from urllib.parse import urljoin
import platform

# Configuration constants
DEFAULT_TIMEOUT = 30
DEFAULT_IMPLICIT_WAIT = 10
MIN_TOUCH_TARGET_SIZE = 44
MIN_MOBILE_FONT_SIZE = 14
SCREENSHOT_DIR = "test_screenshots"
DEFAULT_BASE_URL = "http://localhost:5000"

# Browser user agents
USER_AGENTS = {
    'desktop': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'tablet': 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
    'mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
}


@dataclass
class BrowserConfig:
    """Browser configuration for testing."""
    name: str
    driver_class: type
    options_class: type
    capabilities: Dict
    mobile_emulation: Optional[Dict] = None


@dataclass
class DeviceConfig:
    """Device configuration for responsive testing."""
    name: str
    width: int
    height: int
    user_agent: str
    touch_enabled: bool = False
    pixel_ratio: float = 1.0


@dataclass
class TestResult:
    """Test result for a specific browser/device combination."""
    browser: str
    device: str
    page: str
    test_name: str
    passed: bool
    error_message: str = ""
    screenshot_path: str = ""
    execution_time: float = 0.0


class BrowserDriverManager:
    """Manages browser driver setup and configuration."""
    
    def __init__(self):
        self.browsers = {
            'chrome': BrowserConfig(
                name='Chrome',
                driver_class=webdriver.Chrome,
                options_class=ChromeOptions,
                capabilities={'browserName': 'chrome', 'version': 'latest'}
            ),
            'firefox': BrowserConfig(
                name='Firefox',
                driver_class=webdriver.Firefox,
                options_class=FirefoxOptions,
                capabilities={'browserName': 'firefox', 'version': 'latest'}
            ),
            'edge': BrowserConfig(
                name='Edge',
                driver_class=webdriver.Edge,
                options_class=EdgeOptions,
                capabilities={'browserName': 'MicrosoftEdge', 'version': 'latest'}
            )
        }
    
    def setup_driver(self, browser_name: str, device_config: DeviceConfig, headless: bool = True) -> Optional[webdriver.Remote]:
        """Set up WebDriver for specific browser and device."""
        if browser_name not in self.browsers:
            return None
            
        browser_config = self.browsers[browser_name]
        options = browser_config.options_class()
        
        self._configure_common_options(options, device_config, headless)
        self._configure_browser_specific_options(options, browser_name, device_config)
        
        try:
            driver = browser_config.driver_class(options=options)
            driver.set_window_size(device_config.width, device_config.height)
            driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT)
            return driver
        except Exception as e:
            print(f"Failed to create {browser_name} driver: {e}")
            return None
    
    def _configure_common_options(self, options, device_config: DeviceConfig, headless: bool):
        """Configure common options for all browsers."""
        if headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--window-size={device_config.width},{device_config.height}')
        options.add_argument(f'--user-agent={device_config.user_agent}')
    
    def _configure_browser_specific_options(self, options, browser_name: str, device_config: DeviceConfig):
        """Configure browser-specific options."""
        if browser_name == 'chrome':
            self._configure_chrome_options(options, device_config)
        elif browser_name == 'firefox':
            self._configure_firefox_options(options, device_config)
    
    def _configure_chrome_options(self, options, device_config: DeviceConfig):
        """Configure Chrome-specific options."""
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if device_config.touch_enabled:
            mobile_emulation = {
                "deviceMetrics": {
                    "width": device_config.width,
                    "height": device_config.height,
                    "pixelRatio": device_config.pixel_ratio
                },
                "userAgent": device_config.user_agent
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    def _configure_firefox_options(self, options, device_config: DeviceConfig):
        """Configure Firefox-specific options."""
        options.set_preference("general.useragent.override", device_config.user_agent)


class TestRunner:
    """Handles individual test execution and validation."""
    
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
    
    def test_page_load(self, page_url: str, timeout: int = DEFAULT_TIMEOUT) -> Tuple[bool, str, float]:
        """Test basic page loading functionality."""
        start_time = time.time()
        
        try:
            self.driver.get(page_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Validate page structure
            if not self._validate_page_structure():
                return False, "Invalid page structure", time.time() - start_time
            
            # Check for JavaScript errors
            if not self._check_javascript_errors():
                return False, "JavaScript errors detected", time.time() - start_time
                
            return True, "", time.time() - start_time
            
        except TimeoutException:
            return False, "Page load timeout", time.time() - start_time
        except Exception as e:
            return False, str(e), time.time() - start_time
    
    def _validate_page_structure(self) -> bool:
        """Validate basic page structure."""
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            return body is not None
        except NoSuchElementException:
            return False
    
    def _check_javascript_errors(self) -> bool:
        """Check for JavaScript errors in browser console."""
        try:
            logs = self.driver.get_log('browser')
            js_errors = [log for log in logs if log['level'] == 'SEVERE']
            return len(js_errors) == 0
        except Exception:
            # Some browsers might not support log retrieval
            return True


class ScreenshotManager:
    """Manages screenshot capture and organization."""
    
    def __init__(self, screenshots_dir: str = "test_screenshots"):
        self.screenshots_dir = screenshots_dir
        os.makedirs(screenshots_dir, exist_ok=True)
    
    def take_screenshot(self, driver: webdriver.Remote, browser: str, device: str, 
                       page: str, test_name: str) -> str:
        """Take screenshot for test documentation."""
        timestamp = int(time.time())
        filename = f"{browser}_{device}_{self._sanitize_filename(page)}_{test_name}_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        try:
            driver.save_screenshot(filepath)
            return filepath
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return ""
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        return filename.replace('/', 'home').replace('\\', '_').replace(':', '_')


class CrossBrowserTester:
    """Main cross-browser testing orchestrator."""
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.driver_manager = BrowserDriverManager()
        self.screenshot_manager = ScreenshotManager(SCREENSHOT_DIR)
        self.device_configs = self._initialize_device_configs()
        self.test_pages = self._initialize_test_pages()
    
    def _initialize_device_configs(self) -> Dict[str, DeviceConfig]:
        """Initialize device configurations using constants."""
        return {
            'desktop': DeviceConfig(
                name='Desktop', width=1920, height=1080,
                user_agent=USER_AGENTS['desktop']
            ),
            'laptop': DeviceConfig(
                name='Laptop', width=1366, height=768,
                user_agent=USER_AGENTS['desktop']
            ),
            'tablet': DeviceConfig(
                name='Tablet', width=768, height=1024,
                user_agent=USER_AGENTS['tablet'],
                touch_enabled=True, pixel_ratio=2.0
            ),
            'mobile': DeviceConfig(
                name='Mobile', width=375, height=667,
                user_agent=USER_AGENTS['mobile'],
                touch_enabled=True, pixel_ratio=2.0
            ),
            'mobile_large': DeviceConfig(
                name='Mobile Large', width=414, height=896,
                user_agent=USER_AGENTS['mobile'],
                touch_enabled=True, pixel_ratio=3.0
            )
        }
    
    def _initialize_test_pages(self) -> List[Dict[str, str]]:
        """Initialize test pages configuration."""
        return [
            {'path': '/', 'name': 'Homepage'},
            {'path': '/problems', 'name': 'Problems List'},
            {'path': '/problem/1', 'name': 'Problem Detail'},
            {'path': '/submissions', 'name': 'Submissions'},
            {'path': '/leaderboard', 'name': 'Leaderboard'}
        ]
        
        # Browser configurations
        self.browsers = {
            'chrome': BrowserConfig(
                name='Chrome',
                driver_class=webdriver.Chrome,
                options_class=ChromeOptions,
                capabilities={
                    'browserName': 'chrome',
                    'version': 'latest'
                }
            ),
            'firefox': BrowserConfig(
                name='Firefox',
                driver_class=webdriver.Firefox,
                options_class=FirefoxOptions,
                capabilities={
                    'browserName': 'firefox',
                    'version': 'latest'
                }
            ),
            'edge': BrowserConfig(
                name='Edge',
                driver_class=webdriver.Edge,
                options_class=EdgeOptions,
                capabilities={
                    'browserName': 'MicrosoftEdge',
                    'version': 'latest'
                }
            )
        }
        
        # Device configurations for responsive testing
        self.devices = {
            'desktop': DeviceConfig(
                name='Desktop',
                width=1920,
                height=1080,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ),
            'laptop': DeviceConfig(
                name='Laptop',
                width=1366,
                height=768,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ),
            'tablet': DeviceConfig(
                name='Tablet',
                width=768,
                height=1024,
                user_agent='Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
                touch_enabled=True,
                pixel_ratio=2.0
            ),
            'mobile': DeviceConfig(
                name='Mobile',
                width=375,
                height=667,
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
                touch_enabled=True,
                pixel_ratio=2.0
            ),
            'mobile_large': DeviceConfig(
                name='Mobile Large',
                width=414,
                height=896,
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
                touch_enabled=True,
                pixel_ratio=3.0
            )
        }
        
        # Pages to test
        self.test_pages = [
            {'path': '/', 'name': 'Homepage'},
            {'path': '/problems', 'name': 'Problems List'},
            {'path': '/problem/1', 'name': 'Problem Detail'},
            {'path': '/submissions', 'name': 'Submissions'},
            {'path': '/leaderboard', 'name': 'Leaderboard'}
        ]
        
    def setup_driver(self, browser_name: str, device_name: str, headless: bool = True) -> webdriver.Remote:
        """Set up WebDriver for specific browser and device."""
        browser_config = self.browsers[browser_name]
        device_config = self.devices[device_name]
        
        # Create browser options
        options = browser_config.options_class()
        
        if headless:
            options.add_argument('--headless')
            
        # Common options for all browsers
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--window-size={device_config.width},{device_config.height}')
        options.add_argument(f'--user-agent={device_config.user_agent}')
        
        # Browser-specific configurations
        if browser_name == 'chrome':
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Mobile emulation for Chrome
            if device_config.touch_enabled:
                mobile_emulation = {
                    "deviceMetrics": {
                        "width": device_config.width,
                        "height": device_config.height,
                        "pixelRatio": device_config.pixel_ratio
                    },
                    "userAgent": device_config.user_agent
                }
                options.add_experimental_option("mobileEmulation", mobile_emulation)
                
        elif browser_name == 'firefox':
            # Firefox-specific options
            options.set_preference("general.useragent.override", device_config.user_agent)
            
        # Create driver
        try:
            driver = browser_config.driver_class(options=options)
            driver.set_window_size(device_config.width, device_config.height)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            print(f"Failed to create {browser_name} driver: {e}")
            return None
            
    def take_screenshot(self, driver: webdriver.Remote, browser: str, device: str, page: str, test_name: str) -> str:
        """Take screenshot for test documentation."""
        timestamp = int(time.time())
        filename = f"{browser}_{device}_{page.replace('/', 'home')}_{test_name}_{timestamp}.png"
        filepath = os.path.join(self.screenshots_dir, filename)
        
        try:
            driver.save_screenshot(filepath)
            return filepath
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return ""
            
    def test_page_load(self, driver: webdriver.Remote, page_url: str) -> Tuple[bool, str, float]:
        """Test basic page loading functionality."""
        start_time = time.time()
        
        try:
            driver.get(page_url)
            
            # Wait for page to load
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Check for basic page elements
            body = driver.find_element(By.TAG_NAME, "body")
            if not body:
                return False, "No body element found", time.time() - start_time
                
            # Check for JavaScript errors
            logs = driver.get_log('browser')
            js_errors = [log for log in logs if log['level'] == 'SEVERE']
            
            if js_errors:
                error_messages = [log['message'] for log in js_errors]
                return False, f"JavaScript errors: {'; '.join(error_messages)}", time.time() - start_time
                
            return True, "", time.time() - start_time
            
        except TimeoutException:
            return False, "Page load timeout", time.time() - start_time
        except Exception as e:
            return False, str(e), time.time() - start_time
            
    def test_responsive_layout(self, driver: webdriver.Remote, device_config: DeviceConfig) -> Tuple[bool, str]:
        """Test responsive layout for specific device."""
        try:
            # Check viewport meta tag
            viewport_meta = driver.find_elements(By.CSS_SELECTOR, "meta[name='viewport']")
            if not viewport_meta:
                return False, "Missing viewport meta tag"
                
            # Check for horizontal scrollbar (should not exist on mobile)
            if device_config.width <= 768:
                body_width = driver.execute_script("return document.body.scrollWidth")
                window_width = driver.execute_script("return window.innerWidth")
                
                if body_width > window_width + 10:  # Allow small tolerance
                    return False, f"Horizontal scroll detected: body={body_width}px, window={window_width}px"
                    
            # Check navigation responsiveness
            nav_elements = driver.find_elements(By.CSS_SELECTOR, "nav, .navbar")
            if nav_elements:
                nav = nav_elements[0]
                nav_display = nav.value_of_css_property("display")
                
                if device_config.width <= 768:
                    # Mobile navigation should be collapsible
                    hamburger = driver.find_elements(By.CSS_SELECTOR, ".navbar-toggle, .hamburger, [data-bs-toggle='collapse']")
                    if not hamburger:
                        return False, "Missing mobile navigation toggle"
                        
            # Check text readability (font size should be appropriate)
            body = driver.find_element(By.TAG_NAME, "body")
            font_size = body.value_of_css_property("font-size")
            font_size_px = float(font_size.replace('px', ''))
            
            if device_config.touch_enabled and font_size_px < 14:
                return False, f"Font size too small for mobile: {font_size_px}px"
                
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_touch_interactions(self, driver: webdriver.Remote, device_config: DeviceConfig) -> Tuple[bool, str]:
        """Test touch interactions for mobile devices."""
        if not device_config.touch_enabled:
            return True, "Not a touch device"
            
        try:
            # Test button touch targets (should be at least 44px)
            buttons = driver.find_elements(By.CSS_SELECTOR, "button, .btn, a")
            
            for button in buttons[:5]:  # Test first 5 buttons
                if not button.is_displayed():
                    continue
                    
                size = button.size
                if size['width'] < 44 or size['height'] < 44:
                    button_text = button.text[:20] if button.text else "unknown"
                    return False, f"Touch target too small: {button_text} ({size['width']}x{size['height']}px)"
                    
            # Test touch scrolling
            actions = ActionChains(driver)
            body = driver.find_element(By.TAG_NAME, "body")
            
            # Simulate touch scroll
            actions.click_and_hold(body).move_by_offset(0, -100).release().perform()
            time.sleep(0.5)
            
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_form_functionality(self, driver: webdriver.Remote) -> Tuple[bool, str]:
        """Test form functionality across browsers."""
        try:
            # Find forms on the page
            forms = driver.find_elements(By.TAG_NAME, "form")
            
            if not forms:
                return True, "No forms to test"
                
            for form in forms:
                # Test form inputs
                inputs = form.find_elements(By.CSS_SELECTOR, "input, textarea, select")
                
                for input_elem in inputs:
                    if not input_elem.is_displayed():
                        continue
                        
                    input_type = input_elem.get_attribute('type')
                    
                    # Skip hidden and submit inputs
                    if input_type in ['hidden', 'submit', 'button']:
                        continue
                        
                    # Test input focus
                    input_elem.click()
                    focused_element = driver.switch_to.active_element
                    
                    if focused_element != input_elem:
                        return False, f"Input focus failed for {input_type} input"
                        
                    # Test input typing (for text inputs)
                    if input_type in ['text', 'email', 'password'] or input_elem.tag_name == 'textarea':
                        input_elem.clear()
                        input_elem.send_keys("test input")
                        
                        if input_elem.get_attribute('value') != "test input":
                            return False, f"Input typing failed for {input_type} input"
                            
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_ajax_functionality(self, driver: webdriver.Remote) -> Tuple[bool, str]:
        """Test AJAX functionality and dynamic content."""
        try:
            # Look for elements that might trigger AJAX requests
            ajax_triggers = driver.find_elements(By.CSS_SELECTOR, 
                "[data-bs-toggle], .btn-submit, #submit-code, .filter-select")
                
            if not ajax_triggers:
                return True, "No AJAX triggers found"
                
            # Test a simple AJAX interaction if available
            for trigger in ajax_triggers[:2]:  # Test first 2 triggers
                if not trigger.is_displayed():
                    continue
                    
                # Record initial page state
                initial_html = driver.page_source
                
                # Trigger the action
                try:
                    trigger.click()
                    time.sleep(2)  # Wait for potential AJAX response
                    
                    # Check if page state changed (indicating AJAX worked)
                    new_html = driver.page_source
                    
                    # For now, just check that no JavaScript errors occurred
                    logs = driver.get_log('browser')
                    js_errors = [log for log in logs if log['level'] == 'SEVERE']
                    
                    if js_errors:
                        error_messages = [log['message'] for log in js_errors]
                        return False, f"AJAX JavaScript errors: {'; '.join(error_messages)}"
                        
                except Exception as e:
                    # Some triggers might not work without proper setup, that's OK
                    continue
                    
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def test_css_rendering(self, driver: webdriver.Remote) -> Tuple[bool, str]:
        """Test CSS rendering and styling consistency."""
        try:
            # Check if CSS is loaded
            stylesheets = driver.find_elements(By.CSS_SELECTOR, "link[rel='stylesheet']")
            
            if not stylesheets:
                return False, "No stylesheets found"
                
            # Check basic styling
            body = driver.find_element(By.TAG_NAME, "body")
            body_bg = body.value_of_css_property("background-color")
            
            # Check if custom styles are applied (not default browser styles)
            if body_bg in ['rgba(0, 0, 0, 0)', 'transparent']:
                # Check for other styling indicators
                nav_elements = driver.find_elements(By.CSS_SELECTOR, "nav, .navbar")
                if nav_elements:
                    nav_bg = nav_elements[0].value_of_css_property("background-color")
                    if nav_bg in ['rgba(0, 0, 0, 0)', 'transparent']:
                        return False, "CSS styles may not be loading properly"
                        
            # Check for layout issues
            elements_with_zero_height = driver.execute_script("""
                var elements = document.querySelectorAll('*');
                var zeroHeight = [];
                for (var i = 0; i < elements.length; i++) {
                    var el = elements[i];
                    if (el.offsetHeight === 0 && el.offsetWidth > 0 && 
                        window.getComputedStyle(el).display !== 'none') {
                        zeroHeight.push(el.tagName + (el.className ? '.' + el.className.split(' ')[0] : ''));
                    }
                }
                return zeroHeight.slice(0, 5); // Return first 5
            """)
            
            if elements_with_zero_height:
                return False, f"Elements with zero height detected: {', '.join(elements_with_zero_height)}"
                
            return True, ""
            
        except Exception as e:
            return False, str(e)
            
    def run_browser_test(self, browser_name: str, device_name: str, headless: bool = True) -> List[TestResult]:
        """Run complete test suite for a browser/device combination."""
        print(f"Testing {browser_name} on {device_name}...")
        
        if browser_name not in self.driver_manager.browsers:
            return self._create_unsupported_browser_results(browser_name, device_name)
        
        if device_name not in self.device_configs:
            return self._create_unsupported_device_results(browser_name, device_name)
        
        device_config = self.device_configs[device_name]
        browser_results = []
        
        # Use context manager for proper resource cleanup
        with self._get_driver_context(browser_name, device_config, headless) as driver:
            if not driver:
                return self._create_driver_setup_failure_results(browser_name, device_name)
            
            test_runner = TestRunner(driver)
            browser_results = self._run_all_page_tests(test_runner, browser_name, device_name, device_config)
        
        return browser_results
    
    def _create_unsupported_browser_results(self, browser_name: str, device_name: str) -> List[TestResult]:
        """Create results for unsupported browser."""
        return [TestResult(
            browser=browser_name,
            device=device_name,
            page="N/A",
            test_name="browser_support",
            passed=False,
            error_message=f"Unsupported browser: {browser_name}"
        )]
    
    def _create_unsupported_device_results(self, browser_name: str, device_name: str) -> List[TestResult]:
        """Create results for unsupported device."""
        return [TestResult(
            browser=browser_name,
            device=device_name,
            page="N/A",
            test_name="device_support",
            passed=False,
            error_message=f"Unsupported device: {device_name}"
        )]
    
    def _create_driver_setup_failure_results(self, browser_name: str, device_name: str) -> List[TestResult]:
        """Create results for driver setup failure."""
        return [TestResult(
            browser=browser_name,
            device=device_name,
            page=page['name'],
            test_name="driver_setup",
            passed=False,
            error_message=f"Failed to setup {browser_name} driver"
        ) for page in self.test_pages]
    
    @contextmanager
    def _get_driver_context(self, browser_name: str, device_config: DeviceConfig, headless: bool):
        """Context manager for proper driver resource management."""
        driver = None
        try:
            driver = self.driver_manager.setup_driver(browser_name, device_config, headless)
            yield driver
        except Exception as e:
            print(f"Error in driver context: {e}")
            yield None
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    print(f"Error closing driver: {e}")
    
    def _run_all_page_tests(self, test_runner: TestRunner, browser_name: str, 
                           device_name: str, device_config: DeviceConfig) -> List[TestResult]:
        """Run all tests for all pages."""
        results = []
        
        for page in self.test_pages:
            page_url = urljoin(self.base_url, page['path'])
            page_name = page['name']
            
            print(f"  Testing {page_name}...")
            
            # Run individual tests for this page
            page_results = self._run_page_tests(
                test_runner, browser_name, device_name, device_config, 
                page_url, page_name
            )
            results.extend(page_results)
        
        return results
    
    def _run_page_tests(self, test_runner: TestRunner, browser_name: str, device_name: str,
                       device_config: DeviceConfig, page_url: str, page_name: str) -> List[TestResult]:
        """Run all tests for a specific page."""
        results = []
        
        # Test 1: Page Load (prerequisite for other tests)
        page_load_result = self._test_page_load(test_runner, browser_name, device_name, page_url, page_name)
        results.append(page_load_result)
        
        # Skip other tests if page doesn't load
        if not page_load_result.passed:
            return results
        
        # Test 2: Responsive Layout
        results.append(self._test_responsive_layout(test_runner, browser_name, device_name, device_config, page_name))
        
        # Test 3: Touch Interactions (mobile only)
        results.append(self._test_touch_interactions(test_runner, browser_name, device_name, device_config, page_name))
        
        # Test 4: Form Functionality
        results.append(self._test_form_functionality(test_runner, browser_name, device_name, page_name))
        
        # Test 5: AJAX Functionality
        results.append(self._test_ajax_functionality(test_runner, browser_name, device_name, page_name))
        
        # Test 6: CSS Rendering
        results.append(self._test_css_rendering(test_runner, browser_name, device_name, page_name))
        
        return results
    
    def _test_page_load(self, test_runner: TestRunner, browser_name: str, device_name: str,
                       page_url: str, page_name: str) -> TestResult:
        """Test page loading functionality."""
        passed, error, exec_time = test_runner.test_page_load(page_url)
        screenshot_path = ""
        
        if not passed:
            screenshot_path = self.screenshot_manager.take_screenshot(
                test_runner.driver, browser_name, device_name, page_name, "page_load_error"
            )
        
        return TestResult(
            browser=browser_name,
            device=device_name,
            page=page_name,
            test_name="page_load",
            passed=passed,
            error_message=error,
            screenshot_path=screenshot_path,
            execution_time=exec_time
        )
                
            device_config = self.devices[device_name]
            
            # Test each page
            for page in self.test_pages:
                page_url = urljoin(self.base_url, page['path'])
                page_name = page['name']
                
                print(f"  Testing {page_name}...")
                
                # Test 1: Page Load
                passed, error, exec_time = self.test_page_load(driver, page_url)
                screenshot_path = ""
                
                if not passed:
                    screenshot_path = self.take_screenshot(driver, browser_name, device_name, page_name, "page_load_error")
                    
                browser_results.append(TestResult(
                    browser=browser_name,
                    device=device_name,
                    page=page_name,
                    test_name="page_load",
                    passed=passed,
                    error_message=error,
                    screenshot_path=screenshot_path,
                    execution_time=exec_time
                ))
                
                if not passed:
                    continue  # Skip other tests if page doesn't load
                    
                # Test 2: Responsive Layout
                passed, error = self.test_responsive_layout(driver, device_config)
                if not passed:
                    screenshot_path = self.take_screenshot(driver, browser_name, device_name, page_name, "responsive_error")
                    
                browser_results.append(TestResult(
                    browser=browser_name,
                    device=device_name,
                    page=page_name,
                    test_name="responsive_layout",
                    passed=passed,
                    error_message=error,
                    screenshot_path=screenshot_path
                ))
                
                # Test 3: Touch Interactions (mobile only)
                passed, error = self.test_touch_interactions(driver, device_config)
                if not passed:
                    screenshot_path = self.take_screenshot(driver, browser_name, device_name, page_name, "touch_error")
                    
                browser_results.append(TestResult(
                    browser=browser_name,
                    device=device_name,
                    page=page_name,
                    test_name="touch_interactions",
                    passed=passed,
                    error_message=error,
                    screenshot_path=screenshot_path
                ))
                
                # Test 4: Form Functionality
                passed, error = self.test_form_functionality(driver)
                if not passed:
                    screenshot_path = self.take_screenshot(driver, browser_name, device_name, page_name, "form_error")
                    
                browser_results.append(TestResult(
                    browser=browser_name,
                    device=device_name,
                    page=page_name,
                    test_name="form_functionality",
                    passed=passed,
                    error_message=error,
                    screenshot_path=screenshot_path
                ))
                
                # Test 5: AJAX Functionality
                passed, error = self.test_ajax_functionality(driver)
                if not passed:
                    screenshot_path = self.take_screenshot(driver, browser_name, device_name, page_name, "ajax_error")
                    
                browser_results.append(TestResult(
                    browser=browser_name,
                    device=device_name,
                    page=page_name,
                    test_name="ajax_functionality",
                    passed=passed,
                    error_message=error,
                    screenshot_path=screenshot_path
                ))
                
                # Test 6: CSS Rendering
                passed, error = self.test_css_rendering(driver)
                if not passed:
                    screenshot_path = self.take_screenshot(driver, browser_name, device_name, page_name, "css_error")
                    
                browser_results.append(TestResult(
                    browser=browser_name,
                    device=device_name,
                    page=page_name,
                    test_name="css_rendering",
                    passed=passed,
                    error_message=error,
                    screenshot_path=screenshot_path
                ))
                
        except Exception as e:
            print(f"Error testing {browser_name} on {device_name}: {e}")
            
        finally:
            if driver:
                driver.quit()
                
        return browser_results
        
    def run_comprehensive_test(self, browsers: List[str] = None, devices: List[str] = None, headless: bool = True) -> List[TestResult]:
        """Run comprehensive cross-browser testing."""
        print("🚀 Starting Cross-Browser and Device Testing")
        print("=" * 50)
        
        if browsers is None:
            browsers = ['chrome']  # Default to Chrome for basic testing
            
        if devices is None:
            devices = ['desktop', 'tablet', 'mobile']
            
        all_results = []
        
        for browser in browsers:
            if browser not in self.browsers:
                print(f"⚠️  Browser {browser} not supported, skipping...")
                continue
                
            for device in devices:
                if device not in self.devices:
                    print(f"⚠️  Device {device} not supported, skipping...")
                    continue
                    
                browser_results = self.run_browser_test(browser, device, headless)
                all_results.extend(browser_results)
                
        self.results = all_results
        return all_results
        
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        if not self.results:
            return "No test results available."
            
        report = []
        report.append("🌐 Cross-Browser and Device Testing Report")
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
        
        # Results by browser/device
        browser_device_results = {}
        for result in self.results:
            key = f"{result.browser}_{result.device}"
            if key not in browser_device_results:
                browser_device_results[key] = []
            browser_device_results[key].append(result)
            
        for combo, results in browser_device_results.items():
            browser, device = combo.split('_', 1)
            combo_passed = len([r for r in results if r.passed])
            combo_total = len(results)
            
            status = "✅" if combo_passed == combo_total else "❌"
            report.append(f"{status} {browser.title()} on {device.title()}: {combo_passed}/{combo_total}")
            
            # Show failed tests
            failed_results = [r for r in results if not r.passed]
            if failed_results:
                for failed in failed_results:
                    report.append(f"  ❌ {failed.page} - {failed.test_name}: {failed.error_message}")
                    
        report.append("")
        
        # Detailed results by test type
        test_types = {}
        for result in self.results:
            if result.test_name not in test_types:
                test_types[result.test_name] = []
            test_types[result.test_name].append(result)
            
        report.append("📋 Results by Test Type")
        for test_type, results in test_types.items():
            passed = len([r for r in results if r.passed])
            total = len(results)
            report.append(f"  {test_type.replace('_', ' ').title()}: {passed}/{total}")
            
        report.append("")
        
        # Recommendations
        report.append("💡 Recommendations")
        if failed_tests > 0:
            report.append("1. Fix failing tests before deployment")
            report.append("2. Test on actual devices for mobile validation")
            report.append("3. Consider progressive enhancement for older browsers")
            report.append("4. Implement feature detection for browser-specific functionality")
        else:
            report.append("1. All tests passed! Consider expanding test coverage")
            report.append("2. Test on additional browsers and devices")
            report.append("3. Implement automated cross-browser testing in CI/CD")
            
        return "\n".join(report)


# Pytest integration
@pytest.fixture
def cross_browser_tester():
    """Pytest fixture for cross-browser tester."""
    return CrossBrowserTester()


class TestCrossBrowser:
    """Pytest test class for cross-browser testing."""
    
    def test_chrome_desktop(self, cross_browser_tester):
        """Test Chrome on desktop."""
        results = cross_browser_tester.run_comprehensive_test(['chrome'], ['desktop'])
        
        failed_results = [r for r in results if not r.passed]
        assert len(failed_results) == 0, f"Chrome desktop tests failed: {failed_results}"
        
    def test_chrome_mobile(self, cross_browser_tester):
        """Test Chrome on mobile."""
        results = cross_browser_tester.run_comprehensive_test(['chrome'], ['mobile'])
        
        failed_results = [r for r in results if not r.passed]
        assert len(failed_results) == 0, f"Chrome mobile tests failed: {failed_results}"
        
    def test_firefox_desktop(self, cross_browser_tester):
        """Test Firefox on desktop."""
        results = cross_browser_tester.run_comprehensive_test(['firefox'], ['desktop'])
        
        failed_results = [r for r in results if not r.passed]
        assert len(failed_results) == 0, f"Firefox desktop tests failed: {failed_results}"
        
    @pytest.mark.skipif(platform.system() != "Windows", reason="Edge only available on Windows")
    def test_edge_desktop(self, cross_browser_tester):
        """Test Edge on desktop."""
        results = cross_browser_tester.run_comprehensive_test(['edge'], ['desktop'])
        
        failed_results = [r for r in results if not r.passed]
        assert len(failed_results) == 0, f"Edge desktop tests failed: {failed_results}"


def main():
    """Main function to run cross-browser tests."""
    tester = CrossBrowserTester()
    
    # Available browsers (check which are installed)
    available_browsers = []
    for browser in ['chrome', 'firefox', 'edge']:
        try:
            driver = tester.setup_driver(browser, 'desktop', headless=True)
            if driver:
                available_browsers.append(browser)
                driver.quit()
        except:
            print(f"⚠️  {browser.title()} not available")
            
    if not available_browsers:
        print("❌ No browsers available for testing")
        return 1
        
    print(f"🌐 Testing with browsers: {', '.join(available_browsers)}")
    
    # Run tests
    results = tester.run_comprehensive_test(
        browsers=available_browsers,
        devices=['desktop', 'tablet', 'mobile'],
        headless=True
    )
    
    # Generate report
    report = tester.generate_report()
    print("\n" + report)
    
    # Save report
    with open("cross_browser_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"📄 Report saved to: cross_browser_report.txt")
    
    # Return exit code
    failed_tests = len([r for r in results if not r.passed])
    if failed_tests > 0:
        print(f"\n❌ Cross-browser testing failed: {failed_tests} tests failed")
        return 1
    else:
        print(f"\n✅ Cross-browser testing passed: All tests successful")
        return 0


if __name__ == "__main__":
    exit(main())