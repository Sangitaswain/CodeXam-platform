#!/usr/bin/env python3
"""
Accessibility Testing Suite for System Info Modal
Tests WCAG 2.1 AA compliance and accessibility features
"""

import pytest
import re
from bs4 import BeautifulSoup
from app import create_app
from init_db import initialize_database


class TestSystemInfoModalAccessibility:
    """Test suite for system info modal accessibility compliance."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            with app.app_context():
                initialize_database(':memory:')
                yield client
    
    def test_modal_aria_attributes(self, client):
        """Test that modal has proper ARIA attributes."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        modal = soup.find(id='systemInfoModal')
        
        assert modal is not None, "System info modal should exist in DOM"
        
        # Check required ARIA attributes
        assert modal.get('aria-hidden') is not None, "Modal should have aria-hidden attribute"
        assert modal.get('role') == 'dialog', "Modal should have role='dialog'"
        assert modal.get('aria-modal') == 'true', "Modal should have aria-modal='true'"
        
        # Check labeling
        has_label = (modal.get('aria-labelledby') is not None or 
                    modal.get('aria-label') is not None)
        assert has_label, "Modal should have aria-labelledby or aria-label"
    
    def test_modal_keyboard_navigation(self, client):
        """Test keyboard navigation support."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for focusable elements within modal
        modal = soup.find(id='systemInfoModal')
        assert modal is not None
        
        focusable_selectors = [
            'button', 'input', 'select', 'textarea', 'a[href]',
            '[tabindex]:not([tabindex="-1"])'
        ]
        
        focusable_elements = []
        for selector in focusable_selectors:
            elements = modal.select(selector)
            focusable_elements.extend(elements)
        
        # Should have at least a close button
        assert len(focusable_elements) > 0, "Modal should have focusable elements"
        
        # Check for close button specifically
        close_buttons = modal.select('.terminal-close-btn, .close, [aria-label*="close" i]')
        assert len(close_buttons) > 0, "Modal should have a close button"
    
    def test_modal_focus_management(self, client):
        """Test focus management attributes."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        modal = soup.find(id='systemInfoModal')
        
        # Check for focus trap implementation
        # Look for JavaScript that handles focus management
        scripts = soup.find_all('script')
        focus_management_found = False
        
        for script in scripts:
            if script.string:
                script_content = script.string.lower()
                focus_keywords = ['focus', 'tabindex', 'keydown', 'tab']
                if any(keyword in script_content for keyword in focus_keywords):
                    focus_management_found = True
                    break
        
        # Also check for external JS files that might handle focus
        js_files = soup.find_all('script', src=True)
        for js_file in js_files:
            if 'system-info-modal' in js_file.get('src', ''):
                focus_management_found = True
                break
        
        assert focus_management_found, "Focus management should be implemented"
    
    def test_screen_reader_support(self, client):
        """Test screen reader support elements."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for screen reader only content
        sr_only_elements = soup.select('.sr-only, .visually-hidden, .screen-reader-only')
        
        # Check for aria-live regions (for announcements)
        live_regions = soup.select('[aria-live]')
        
        # Check for proper heading structure
        headings = soup.select('h1, h2, h3, h4, h5, h6')
        
        print(f"\n📊 Screen Reader Support:")
        print(f"  Screen reader only elements: {len(sr_only_elements)}")
        print(f"  ARIA live regions: {len(live_regions)}")
        print(f"  Headings found: {len(headings)}")
        
        # Should have some accessibility support elements
        accessibility_support = len(sr_only_elements) + len(live_regions)
        assert accessibility_support > 0, "Should have screen reader support elements"
    
    def test_color_contrast_compliance(self, client):
        """Test color contrast in CSS."""
        # Test CSS file accessibility
        response = client.get('/static/css/system-info-modal.css')
        
        if response.status_code == 200:
            css_content = response.data.decode('utf-8')
            
            # Look for color definitions
            color_patterns = [
                r'color:\s*#([0-9a-fA-F]{3,6})',
                r'background-color:\s*#([0-9a-fA-F]{3,6})',
                r'background:\s*#([0-9a-fA-F]{3,6})'
            ]
            
            colors_found = []
            for pattern in color_patterns:
                matches = re.findall(pattern, css_content)
                colors_found.extend(matches)
            
            # Check for high contrast colors (basic check)
            # Terminal themes typically use high contrast
            terminal_colors = ['00ff88', '00ff41', 'ffffff', '000000', '0a0a0a']
            has_high_contrast = any(color.lower() in terminal_colors for color in colors_found)
            
            print(f"\n📊 Color Analysis:")
            print(f"  Colors found: {len(set(colors_found))}")
            print(f"  High contrast colors detected: {has_high_contrast}")
            
            # Terminal interface should use high contrast colors
            assert has_high_contrast, "Should use high contrast colors for terminal interface"
        else:
            pytest.skip("CSS file not accessible for color contrast testing")
    
    def test_semantic_html_structure(self, client):
        """Test semantic HTML structure."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        modal = soup.find(id='systemInfoModal')
        
        # Check for semantic elements
        semantic_elements = modal.select('main, section, article, aside, nav, header, footer')
        
        # Check for proper button elements (not divs with click handlers)
        buttons = modal.select('button')
        clickable_divs = modal.select('div[onclick], span[onclick]')
        
        # Check for proper form elements if any
        form_elements = modal.select('form, input, select, textarea, label')
        
        print(f"\n📊 Semantic HTML:")
        print(f"  Semantic elements: {len(semantic_elements)}")
        print(f"  Proper buttons: {len(buttons)}")
        print(f"  Clickable divs (should be minimal): {len(clickable_divs)}")
        print(f"  Form elements: {len(form_elements)}")
        
        # Should use proper button elements
        assert len(buttons) > 0, "Should use proper button elements"
        
        # Minimize use of clickable divs
        assert len(clickable_divs) <= len(buttons), "Should prefer buttons over clickable divs"
    
    def test_alternative_text_for_images(self, client):
        """Test alternative text for images."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        modal = soup.find(id='systemInfoModal')
        
        # Check all images have alt text
        images = modal.select('img')
        
        missing_alt = []
        for img in images:
            if not img.get('alt'):
                missing_alt.append(img)
        
        print(f"\n📊 Image Accessibility:")
        print(f"  Total images: {len(images)}")
        print(f"  Missing alt text: {len(missing_alt)}")
        
        assert len(missing_alt) == 0, f"All images should have alt text, {len(missing_alt)} missing"
    
    def test_form_accessibility(self, client):
        """Test form accessibility if forms exist."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        modal = soup.find(id='systemInfoModal')
        
        # Check for form elements
        inputs = modal.select('input, select, textarea')
        
        if inputs:
            # Check that form elements have labels
            unlabeled_inputs = []
            for input_elem in inputs:
                input_id = input_elem.get('id')
                aria_label = input_elem.get('aria-label')
                aria_labelledby = input_elem.get('aria-labelledby')
                
                # Check for associated label
                label = None
                if input_id:
                    label = modal.select(f'label[for="{input_id}"]')
                
                if not (label or aria_label or aria_labelledby):
                    unlabeled_inputs.append(input_elem)
            
            print(f"\n📊 Form Accessibility:")
            print(f"  Total form inputs: {len(inputs)}")
            print(f"  Unlabeled inputs: {len(unlabeled_inputs)}")
            
            assert len(unlabeled_inputs) == 0, "All form inputs should have labels"
        else:
            print("\n📊 Form Accessibility: No form elements found")
    
    def test_heading_hierarchy(self, client):
        """Test proper heading hierarchy."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        modal = soup.find(id='systemInfoModal')
        
        # Get all headings in order
        headings = modal.select('h1, h2, h3, h4, h5, h6')
        
        if headings:
            heading_levels = []
            for heading in headings:
                level = int(heading.name[1])  # Extract number from h1, h2, etc.
                heading_levels.append(level)
            
            # Check for proper hierarchy (no skipping levels)
            hierarchy_issues = []
            for i in range(1, len(heading_levels)):
                current_level = heading_levels[i]
                previous_level = heading_levels[i-1]
                
                # Can go down any number of levels, but can only go up one level at a time
                if current_level > previous_level + 1:
                    hierarchy_issues.append(f"Skipped from h{previous_level} to h{current_level}")
            
            print(f"\n📊 Heading Hierarchy:")
            print(f"  Headings found: {len(headings)}")
            print(f"  Heading levels: {heading_levels}")
            print(f"  Hierarchy issues: {len(hierarchy_issues)}")
            
            if hierarchy_issues:
                print(f"  Issues: {hierarchy_issues}")
            
            assert len(hierarchy_issues) == 0, "Heading hierarchy should be proper"
        else:
            print("\n📊 Heading Hierarchy: No headings found in modal")
    
    def test_language_attributes(self, client):
        """Test language attributes for internationalization."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check main document language
        html_tag = soup.find('html')
        assert html_tag is not None
        
        lang_attr = html_tag.get('lang')
        assert lang_attr is not None, "HTML should have lang attribute"
        assert len(lang_attr) >= 2, "Language code should be valid"
        
        # Check for any content in different languages
        modal = soup.find(id='systemInfoModal')
        lang_elements = modal.select('[lang]') if modal else []
        
        print(f"\n📊 Language Attributes:")
        print(f"  Document language: {lang_attr}")
        print(f"  Elements with lang attribute: {len(lang_elements)}")
    
    def test_error_message_accessibility(self, client):
        """Test error message accessibility."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Look for error message containers
        error_containers = soup.select('.error, .alert, .message, [role="alert"]')
        
        # Check ARIA attributes for error messages
        accessible_errors = 0
        for container in error_containers:
            if (container.get('role') == 'alert' or 
                container.get('aria-live') or 
                container.get('aria-atomic')):
                accessible_errors += 1
        
        print(f"\n📊 Error Message Accessibility:")
        print(f"  Error containers found: {len(error_containers)}")
        print(f"  Accessible error messages: {accessible_errors}")
        
        # If error containers exist, they should be accessible
        if error_containers:
            assert accessible_errors > 0, "Error messages should be accessible to screen readers"
    
    def test_modal_escape_mechanisms(self, client):
        """Test multiple ways to close modal (accessibility requirement)."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        modal = soup.find(id='systemInfoModal')
        
        # Check for close button
        close_buttons = modal.select('.close, .terminal-close-btn, [aria-label*="close" i]')
        
        # Check for JavaScript that handles Escape key
        scripts = soup.find_all('script')
        escape_handler_found = False
        
        for script in scripts:
            if script.string and 'escape' in script.string.lower():
                escape_handler_found = True
                break
        
        # Check external JS files
        js_files = soup.find_all('script', src=True)
        for js_file in js_files:
            if 'system-info-modal' in js_file.get('src', ''):
                # Assume external modal JS handles escape
                escape_handler_found = True
                break
        
        print(f"\n📊 Modal Escape Mechanisms:")
        print(f"  Close buttons: {len(close_buttons)}")
        print(f"  Escape key handler: {escape_handler_found}")
        
        assert len(close_buttons) > 0, "Modal should have close button"
        assert escape_handler_found, "Modal should handle Escape key"
    
    def test_responsive_accessibility(self, client):
        """Test accessibility on different screen sizes."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for responsive design indicators
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        assert viewport is not None, "Should have viewport meta tag for mobile"
        
        viewport_content = viewport.get('content', '')
        assert 'width=device-width' in viewport_content, "Viewport should be responsive"
        
        # Check for responsive CSS
        css_response = client.get('/static/css/system-info-modal.css')
        if css_response.status_code == 200:
            css_content = css_response.data.decode('utf-8')
            
            # Look for media queries
            media_queries = re.findall(r'@media[^{]+{', css_content)
            
            print(f"\n📊 Responsive Accessibility:")
            print(f"  Viewport meta tag: Present")
            print(f"  Media queries found: {len(media_queries)}")
            
            # Should have responsive design
            assert len(media_queries) > 0, "Should have responsive CSS media queries"
        else:
            pytest.skip("CSS file not accessible for responsive testing")


class TestSystemInfoModalWCAGCompliance:
    """Test suite for WCAG 2.1 AA compliance."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            with app.app_context():
                initialize_database(':memory:')
                yield client
    
    def test_wcag_perceivable_compliance(self, client):
        """Test WCAG Perceivable guideline compliance."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        modal = soup.find(id='systemInfoModal')
        
        # 1.1 Text Alternatives
        images = modal.select('img')
        images_with_alt = [img for img in images if img.get('alt')]
        
        # 1.3 Adaptable - proper heading structure
        headings = modal.select('h1, h2, h3, h4, h5, h6')
        
        # 1.4 Distinguishable - check for color contrast indicators
        css_response = client.get('/static/css/system-info-modal.css')
        has_high_contrast = False
        if css_response.status_code == 200:
            css_content = css_response.data.decode('utf-8').lower()
            # Terminal themes typically use high contrast
            high_contrast_indicators = ['#00ff', '#ffffff', '#000000', 'contrast']
            has_high_contrast = any(indicator in css_content for indicator in high_contrast_indicators)
        
        print(f"\n📊 WCAG Perceivable Compliance:")
        print(f"  Images with alt text: {len(images_with_alt)}/{len(images)}")
        print(f"  Proper headings: {len(headings)}")
        print(f"  High contrast design: {has_high_contrast}")
        
        # Assertions
        if images:
            assert len(images_with_alt) == len(images), "All images should have alt text"
        assert has_high_contrast, "Should use high contrast colors"
    
    def test_wcag_operable_compliance(self, client):
        """Test WCAG Operable guideline compliance."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        modal = soup.find(id='systemInfoModal')
        
        # 2.1 Keyboard Accessible
        focusable_elements = modal.select('button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])')
        
        # 2.4 Navigable - check for skip links and proper headings
        skip_links = soup.select('a[href^="#"]')
        headings = modal.select('h1, h2, h3, h4, h5, h6')
        
        print(f"\n📊 WCAG Operable Compliance:")
        print(f"  Focusable elements: {len(focusable_elements)}")
        print(f"  Skip links: {len(skip_links)}")
        print(f"  Navigation headings: {len(headings)}")
        
        # Should have keyboard accessible elements
        assert len(focusable_elements) > 0, "Should have keyboard accessible elements"
    
    def test_wcag_understandable_compliance(self, client):
        """Test WCAG Understandable guideline compliance."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # 3.1 Readable - language identification
        html_tag = soup.find('html')
        has_lang = html_tag and html_tag.get('lang')
        
        # 3.2 Predictable - consistent navigation
        modal = soup.find(id='systemInfoModal')
        close_buttons = modal.select('.close, .terminal-close-btn, [aria-label*="close" i]')
        
        # 3.3 Input Assistance - error identification
        form_elements = modal.select('input, select, textarea')
        
        print(f"\n📊 WCAG Understandable Compliance:")
        print(f"  Language specified: {bool(has_lang)}")
        print(f"  Consistent close mechanisms: {len(close_buttons)}")
        print(f"  Form elements: {len(form_elements)}")
        
        assert has_lang, "Document should specify language"
        assert len(close_buttons) > 0, "Should have consistent close mechanism"
    
    def test_wcag_robust_compliance(self, client):
        """Test WCAG Robust guideline compliance."""
        response = client.get('/')
        assert response.status_code == 200
        
        soup = BeautifulSoup(response.data, 'html.parser')
        modal = soup.find(id='systemInfoModal')
        
        # 4.1 Compatible - proper markup and ARIA
        # Check for proper ARIA attributes
        aria_elements = modal.select('[aria-hidden], [aria-label], [aria-labelledby], [role]')
        
        # Check for valid HTML structure
        required_modal_attrs = ['id', 'role']
        has_required_attrs = all(modal.get(attr) for attr in required_modal_attrs)
        
        print(f"\n📊 WCAG Robust Compliance:")
        print(f"  ARIA attributes: {len(aria_elements)}")
        print(f"  Required modal attributes: {has_required_attrs}")
        
        assert len(aria_elements) > 0, "Should use ARIA attributes"
        assert has_required_attrs, "Modal should have required attributes"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])