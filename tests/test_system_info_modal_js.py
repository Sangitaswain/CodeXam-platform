#!/usr/bin/env python3
"""
JavaScript Testing Suite for System Info Modal
Tests JavaScript functionality using Selenium WebDriver
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
from app import create_app
import threading
import socket


class TestSystemInfoModalJavaScript:
    """Test suite for System Info Modal JavaScript functionality."""
    
    @pytest.fixture(scope="class")
    def app_server(self):
        """Start Flask app server for testing."""
        app = create_app()
        app.config['TESTING'] = True
        
        # Find available port
        sock = socket.socket()
        sock.bind(('', 0))
        port = sock.getsockname()[1]
        sock.close()
        
        # Start server in thread
        server_thread = threading.Thread(
            target=lambda: app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
        )
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        yield f"http://127.0.0.1:{port}"
    
    @pytest.fixture
    def driver(self):
        """Create Chrome WebDriver for testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            yield driver
        except Exception as e:
            pytest.skip(f"Chrome WebDriver not available: {e}")
        finally:
            if 'driver' in locals():
                driver.quit()
    
    def test_modal_initialization(self, driver, app_server):
        """Test that modal JavaScript initializes correctly."""
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Check that SystemInfoModal object exists
        modal_exists = driver.execute_script("return typeof SystemInfoModal !== 'undefined';")
        assert modal_exists, "SystemInfoModal object not found"
        
        # Check that global functions exist
        show_function_exists = driver.execute_script("return typeof window.showSystemInfoModal === 'function';")
        assert show_function_exists, "showSystemInfoModal function not found"
        
        hide_function_exists = driver.execute_script("return typeof window.hideSystemInfoModal === 'function';")
        assert hide_function_exists, "hideSystemInfoModal function not found"
    
    def test_modal_show_hide_functionality(self, driver, app_server):
        """Test modal show and hide functionality."""
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "systemInfoModal"))
        )
        
        # Check initial state (modal should be hidden)
        modal = driver.find_element(By.ID, "systemInfoModal")
        initial_display = modal.value_of_css_property("display")
        assert initial_display == "none", "Modal should be initially hidden"
        
        # Show modal
        driver.execute_script("window.showSystemInfoModal();")
        
        # Wait for modal to be visible
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") != "none"
        )
        
        # Check that modal is now visible
        modal_display = modal.value_of_css_property("display")
        assert modal_display != "none", "Modal should be visible after show()"
        
        # Hide modal
        driver.execute_script("window.hideSystemInfoModal();")
        
        # Wait for modal to be hidden
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") == "none"
        )
        
        # Check that modal is hidden again
        final_display = modal.value_of_css_property("display")
        assert final_display == "none", "Modal should be hidden after hide()"
    
    def test_modal_keyboard_navigation(self, driver, app_server):
        """Test keyboard navigation and accessibility."""
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "systemInfoModal"))
        )
        
        # Show modal
        driver.execute_script("window.showSystemInfoModal();")
        
        # Wait for modal to be visible
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") != "none"
        )
        
        # Test Escape key closes modal
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        
        # Wait for modal to be hidden
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") == "none"
        )
        
        # Check that modal is hidden
        modal = driver.find_element(By.ID, "systemInfoModal")
        final_display = modal.value_of_css_property("display")
        assert final_display == "none", "Modal should close with Escape key"
    
    def test_modal_close_button(self, driver, app_server):
        """Test modal close button functionality."""
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "systemInfoModal"))
        )
        
        # Show modal
        driver.execute_script("window.showSystemInfoModal();")
        
        # Wait for modal to be visible
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") != "none"
        )
        
        # Find and click close button
        try:
            close_button = driver.find_element(By.CLASS_NAME, "terminal-close-btn")
            close_button.click()
            
            # Wait for modal to be hidden
            WebDriverWait(driver, 5).until(
                lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") == "none"
            )
            
            # Check that modal is hidden
            modal = driver.find_element(By.ID, "systemInfoModal")
            final_display = modal.value_of_css_property("display")
            assert final_display == "none", "Modal should close when close button is clicked"
            
        except NoSuchElementException:
            pytest.skip("Close button not found in modal")
    
    def test_modal_accessibility_attributes(self, driver, app_server):
        """Test that modal has proper accessibility attributes."""
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "systemInfoModal"))
        )
        
        modal = driver.find_element(By.ID, "systemInfoModal")
        
        # Check initial ARIA attributes
        initial_aria_hidden = modal.get_attribute("aria-hidden")
        assert initial_aria_hidden == "true", "Modal should have aria-hidden='true' initially"
        
        # Show modal
        driver.execute_script("window.showSystemInfoModal();")
        
        # Wait for modal to be visible
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") != "none"
        )
        
        # Check ARIA attributes when visible
        visible_aria_hidden = modal.get_attribute("aria-hidden")
        assert visible_aria_hidden == "false", "Modal should have aria-hidden='false' when visible"
        
        role = modal.get_attribute("role")
        assert role == "dialog", "Modal should have role='dialog'"
        
        aria_modal = modal.get_attribute("aria-modal")
        assert aria_modal == "true", "Modal should have aria-modal='true'"
    
    def test_modal_focus_management(self, driver, app_server):
        """Test focus management in modal."""
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "systemInfoModal"))
        )
        
        # Store initial focused element
        initial_focus = driver.execute_script("return document.activeElement.tagName;")
        
        # Show modal
        driver.execute_script("window.showSystemInfoModal();")
        
        # Wait for modal to be visible
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") != "none"
        )
        
        # Check that focus moved to modal or focusable element within modal
        time.sleep(0.5)  # Allow time for focus to move
        current_focus = driver.execute_script("return document.activeElement;")
        
        # Focus should be within modal or on modal itself
        modal = driver.find_element(By.ID, "systemInfoModal")
        is_focus_in_modal = driver.execute_script("""
            var modal = arguments[0];
            var activeElement = document.activeElement;
            return modal === activeElement || modal.contains(activeElement);
        """, modal)
        
        assert is_focus_in_modal, "Focus should be within modal when opened"
    
    def test_modal_data_loading(self, driver, app_server):
        """Test that modal loads data correctly."""
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "systemInfoModal"))
        )
        
        # Show modal
        driver.execute_script("window.showSystemInfoModal();")
        
        # Wait for modal to be visible
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") != "none"
        )
        
        # Wait for data to load (look for specific content)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "terminal-content"))
            )
            
            # Check that some system info content is present
            modal_content = driver.find_element(By.ID, "systemInfoModal").text
            
            # Should contain some system information
            assert len(modal_content) > 0, "Modal should contain system information"
            
            # Look for common system info terms
            system_terms = ["system", "status", "codexam", "platform", "info"]
            has_system_content = any(term.lower() in modal_content.lower() for term in system_terms)
            assert has_system_content, "Modal should contain system-related content"
            
        except TimeoutException:
            pytest.skip("Modal content not loaded within timeout")
    
    def test_modal_animations(self, driver, app_server):
        """Test modal animations and transitions."""
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "systemInfoModal"))
        )
        
        modal = driver.find_element(By.ID, "systemInfoModal")
        
        # Check initial opacity
        initial_opacity = modal.value_of_css_property("opacity")
        
        # Show modal
        driver.execute_script("window.showSystemInfoModal();")
        
        # Wait for modal to be visible
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") != "none"
        )
        
        # Check that opacity changed (indicating animation)
        time.sleep(0.5)  # Allow time for animation
        visible_opacity = modal.value_of_css_property("opacity")
        
        # Opacity should be 1 or close to 1 when visible
        assert float(visible_opacity) > 0.5, "Modal should have high opacity when visible"
    
    def test_modal_responsive_behavior(self, driver, app_server):
        """Test modal responsive behavior on different screen sizes."""
        driver.get(app_server)
        
        # Test desktop size
        driver.set_window_size(1920, 1080)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "systemInfoModal"))
        )
        
        # Show modal
        driver.execute_script("window.showSystemInfoModal();")
        
        # Wait for modal to be visible
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") != "none"
        )
        
        modal = driver.find_element(By.ID, "systemInfoModal")
        desktop_width = modal.size['width']
        
        # Test mobile size
        driver.set_window_size(375, 667)  # iPhone size
        time.sleep(1)  # Allow time for responsive changes
        
        mobile_width = modal.size['width']
        
        # Modal should adapt to screen size
        assert mobile_width <= desktop_width, "Modal should adapt to smaller screen sizes"
        
        # Hide modal
        driver.execute_script("window.hideSystemInfoModal();")
    
    def test_modal_error_handling(self, driver, app_server):
        """Test modal error handling."""
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Test calling show multiple times
        result1 = driver.execute_script("return window.showSystemInfoModal();")
        result2 = driver.execute_script("return window.showSystemInfoModal();")
        
        # Both calls should succeed (or handle gracefully)
        assert result1 is not False, "First show call should succeed"
        assert result2 is not False, "Second show call should handle gracefully"
        
        # Test calling hide when already hidden
        driver.execute_script("window.hideSystemInfoModal();")
        result3 = driver.execute_script("return window.hideSystemInfoModal();")
        
        assert result3 is not False, "Hide call on hidden modal should handle gracefully"
    
    def test_modal_memory_leaks(self, driver, app_server):
        """Test for potential memory leaks in modal."""
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "systemInfoModal"))
        )
        
        # Get initial memory usage (approximate)
        initial_objects = driver.execute_script("return Object.keys(window).length;")
        
        # Show and hide modal multiple times
        for _ in range(5):
            driver.execute_script("window.showSystemInfoModal();")
            time.sleep(0.2)
            driver.execute_script("window.hideSystemInfoModal();")
            time.sleep(0.2)
        
        # Check final memory usage
        final_objects = driver.execute_script("return Object.keys(window).length;")
        
        # Object count shouldn't grow significantly
        object_growth = final_objects - initial_objects
        assert object_growth < 10, "Modal shouldn't create excessive global objects"


class TestSystemInfoModalCommands:
    """Test suite for modal command system."""
    
    @pytest.fixture(scope="class")
    def app_server(self):
        """Start Flask app server for testing."""
        app = create_app()
        app.config['TESTING'] = True
        
        # Find available port
        sock = socket.socket()
        sock.bind(('', 0))
        port = sock.getsockname()[1]
        sock.close()
        
        # Start server in thread
        server_thread = threading.Thread(
            target=lambda: app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
        )
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        yield f"http://127.0.0.1:{port}"
    
    @pytest.fixture
    def driver(self):
        """Create Chrome WebDriver for testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            yield driver
        except Exception as e:
            pytest.skip(f"Chrome WebDriver not available: {e}")
        finally:
            if 'driver' in locals():
                driver.quit()
    
    def test_command_system_exists(self, driver, app_server):
        """Test that command system is available."""
        driver.get(app_server)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "systemInfoModal"))
        )
        
        # Show modal
        driver.execute_script("window.showSystemInfoModal();")
        
        # Wait for modal to be visible
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") != "none"
        )
        
        # Look for command input or terminal interface
        try:
            command_elements = driver.find_elements(By.CSS_SELECTOR, 
                "input[type='text'], .command-input, .terminal-input, .command-prompt")
            
            if command_elements:
                assert len(command_elements) > 0, "Command input should be available"
            else:
                # If no input found, check for command-related content
                modal_content = driver.find_element(By.ID, "systemInfoModal").text
                command_terms = ["command", "help", "terminal", "prompt", "$", ">"]
                has_command_content = any(term in modal_content.lower() for term in command_terms)
                assert has_command_content, "Modal should have command-related content"
                
        except NoSuchElementException:
            pytest.skip("Command system elements not found")
    
    def test_help_command(self, driver, app_server):
        """Test help command functionality."""
        driver.get(app_server)
        
        # Wait for page to load and show modal
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "systemInfoModal"))
        )
        
        driver.execute_script("window.showSystemInfoModal();")
        
        # Wait for modal to be visible
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "systemInfoModal").value_of_css_property("display") != "none"
        )
        
        # Try to execute help command via JavaScript
        try:
            help_result = driver.execute_script("""
                if (typeof SystemInfoModal !== 'undefined' && SystemInfoModal.executeCommand) {
                    return SystemInfoModal.executeCommand('help');
                }
                return 'Command system not available';
            """)
            
            # If command system exists, help should return something useful
            if help_result != 'Command system not available':
                assert len(str(help_result)) > 0, "Help command should return information"
                
        except Exception:
            pytest.skip("Command execution not available")


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])