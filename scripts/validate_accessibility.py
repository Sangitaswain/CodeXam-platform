#!/usr/bin/env python3
"""
Quick Accessibility Validation Script

This script performs basic accessibility validation on the CodeXam templates
without requiring a running server. It checks for common accessibility issues
in the HTML templates directly.

Usage: python validate_accessibility.py
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """Represents a validation issue found in templates."""
    file: str
    line: int
    severity: str
    type: str
    message: str
    element: str


class TemplateAccessibilityValidator:
    """Validates HTML templates for accessibility issues."""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.issues: List[ValidationIssue] = []
        
    def validate_all_templates(self) -> List[ValidationIssue]:
        """Validate all HTML templates in the templates directory."""
        print("🔍 Validating CodeXam templates for accessibility issues...")
        print("=" * 60)
        
        template_files = list(self.templates_dir.glob("*.html"))
        
        for template_file in template_files:
            print(f"Checking {template_file.name}...")
            self.validate_template(template_file)
            
        return self.issues
        
    def validate_template(self, template_path: Path):
        """Validate a single template file."""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Run validation checks
            self.check_html_structure(template_path, soup, content)
            self.check_images(template_path, soup)
            self.check_forms(template_path, soup)
            self.check_headings(template_path, soup)
            self.check_links(template_path, soup)
            self.check_buttons(template_path, soup)
            self.check_aria_attributes(template_path, soup)
            self.check_landmarks(template_path, soup)
            self.check_tables(template_path, soup)
            
        except Exception as e:
            self.add_issue(template_path, 0, 'critical', 'parsing', 
                          f"Could not parse template: {e}", "file")
                          
    def add_issue(self, file_path: Path, line: int, severity: str, 
                  issue_type: str, message: str, element: str):
        """Add a validation issue to the list."""
        self.issues.append(ValidationIssue(
            file=str(file_path.name),
            line=line,
            severity=severity,
            type=issue_type,
            message=message,
            element=element
        ))
        
    def get_line_number(self, content: str, element_str: str) -> int:
        """Get approximate line number for an element."""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if element_str in line:
                return i
        return 0
        
    def check_html_structure(self, file_path: Path, soup: BeautifulSoup, content: str):
        """Check basic HTML structure requirements."""
        
        # Check for lang attribute
        html_tag = soup.find('html')
        if html_tag and not html_tag.get('lang'):
            self.add_issue(file_path, self.get_line_number(content, '<html'), 
                          'major', 'structure', 
                          'Missing lang attribute on html element', 'html')
                          
        # Check for page title
        title_tag = soup.find('title')
        if not title_tag or not title_tag.get_text().strip():
            self.add_issue(file_path, self.get_line_number(content, '<title'), 
                          'major', 'structure', 
                          'Missing or empty page title', 'title')
                          
        # Check for main landmark
        main_tag = soup.find('main')
        main_role = soup.find(attrs={'role': 'main'})
        if not main_tag and not main_role:
            self.add_issue(file_path, 0, 'major', 'structure', 
                          'Missing main landmark', 'page')
                          
        # Check for navigation landmark
        nav_tag = soup.find('nav')
        nav_role = soup.find(attrs={'role': 'navigation'})
        if not nav_tag and not nav_role:
            self.add_issue(file_path, 0, 'minor', 'structure', 
                          'Missing navigation landmark', 'page')
                          
    def check_images(self, file_path: Path, soup: BeautifulSoup):
        """Check image accessibility."""
        images = soup.find_all('img')
        
        for img in images:
            # Check for alt attribute
            if not img.get('alt') and img.get('alt') != '':
                self.add_issue(file_path, 0, 'major', 'images', 
                              'Image missing alt attribute', 
                              f"img[src='{img.get('src', 'unknown')}']")
                              
            # Check for empty alt on decorative images
            src = img.get('src', '')
            if any(keyword in src.lower() for keyword in ['decoration', 'spacer', 'pixel']):
                if img.get('alt') != '':
                    self.add_issue(file_path, 0, 'minor', 'images', 
                                  'Decorative image should have empty alt attribute', 
                                  f"img[src='{src}']")
                                  
    def check_forms(self, file_path: Path, soup: BeautifulSoup):
        """Check form accessibility."""
        form_controls = soup.find_all(['input', 'textarea', 'select'])
        
        for control in form_controls:
            control_type = control.get('type', 'text')
            
            # Skip hidden inputs
            if control_type == 'hidden':
                continue
                
            control_id = control.get('id')
            control_name = control.get('name', 'unknown')
            
            # Check for associated label
            label = None
            if control_id:
                label = soup.find('label', attrs={'for': control_id})
                
            # Check for aria-label or aria-labelledby
            aria_label = control.get('aria-label')
            aria_labelledby = control.get('aria-labelledby')
            
            if not label and not aria_label and not aria_labelledby:
                self.add_issue(file_path, 0, 'major', 'forms', 
                              'Form control missing label', 
                              f"{control.name}[name='{control_name}']")
                              
            # Check required fields have aria-required
            if control.get('required') and not control.get('aria-required'):
                self.add_issue(file_path, 0, 'minor', 'forms', 
                              'Required field should have aria-required="true"', 
                              f"{control.name}[name='{control_name}']")
                              
    def check_headings(self, file_path: Path, soup: BeautifulSoup):
        """Check heading structure."""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            self.add_issue(file_path, 0, 'major', 'structure', 
                          'No headings found on page', 'page')
            return
            
        # Check for h1
        h1_elements = soup.find_all('h1')
        if len(h1_elements) == 0:
            self.add_issue(file_path, 0, 'major', 'structure', 
                          'No h1 element found', 'page')
        elif len(h1_elements) > 1:
            self.add_issue(file_path, 0, 'major', 'structure', 
                          'Multiple h1 elements found', 'page')
                          
        # Check heading hierarchy
        heading_levels = []
        for heading in headings:
            level = int(heading.name[1])
            heading_levels.append(level)
            
            # Check for empty headings
            if not heading.get_text().strip():
                self.add_issue(file_path, 0, 'major', 'structure', 
                              'Empty heading found', heading.name)
                              
        # Check for skipped heading levels
        for i in range(1, len(heading_levels)):
            current_level = heading_levels[i]
            prev_level = heading_levels[i-1]
            
            if current_level > prev_level + 1:
                self.add_issue(file_path, 0, 'minor', 'structure', 
                              f'Heading level skipped: h{prev_level} to h{current_level}', 
                              f'h{current_level}')
                              
    def check_links(self, file_path: Path, soup: BeautifulSoup):
        """Check link accessibility."""
        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href')
            link_text = link.get_text().strip()
            aria_label = link.get('aria-label')
            
            # Check for empty links
            if not link_text and not aria_label:
                self.add_issue(file_path, 0, 'major', 'links', 
                              'Link has no accessible text', 
                              f"a[href='{href}']")
                              
            # Check for generic link text
            generic_terms = ['click here', 'read more', 'more', 'here', 'link']
            if link_text.lower() in generic_terms:
                self.add_issue(file_path, 0, 'minor', 'links', 
                              f'Generic link text: "{link_text}"', 
                              f"a[href='{href}']")
                              
            # Check for links that open in new window
            target = link.get('target')
            if target == '_blank':
                # Should have indication for screen readers
                if 'new window' not in link_text.lower() and 'new tab' not in link_text.lower():
                    if not aria_label or ('new window' not in aria_label.lower() and 'new tab' not in aria_label.lower()):
                        self.add_issue(file_path, 0, 'minor', 'links', 
                                      'Link opens in new window without indication', 
                                      f"a[href='{href}']")
                                      
    def check_buttons(self, file_path: Path, soup: BeautifulSoup):
        """Check button accessibility."""
        buttons = soup.find_all('button')
        
        for button in buttons:
            button_text = button.get_text().strip()
            aria_label = button.get('aria-label')
            
            # Check for empty buttons
            if not button_text and not aria_label:
                button_id = button.get('id', 'unknown')
                self.add_issue(file_path, 0, 'major', 'buttons', 
                              'Button has no accessible text', 
                              f"button[id='{button_id}']")
                              
            # Check for generic button text
            generic_terms = ['click', 'button', 'submit']
            if button_text.lower() in generic_terms:
                self.add_issue(file_path, 0, 'minor', 'buttons', 
                              f'Generic button text: "{button_text}"', 
                              f"button")
                              
    def check_aria_attributes(self, file_path: Path, soup: BeautifulSoup):
        """Check ARIA attributes usage."""
        
        # Check for aria-hidden on focusable elements
        hidden_elements = soup.find_all(attrs={'aria-hidden': 'true'})
        for element in hidden_elements:
            if element.name in ['a', 'button', 'input', 'textarea', 'select']:
                self.add_issue(file_path, 0, 'major', 'aria', 
                              'Focusable element should not have aria-hidden="true"', 
                              element.name)
                              
            # Check if element has tabindex
            if element.get('tabindex') and element.get('tabindex') != '-1':
                self.add_issue(file_path, 0, 'major', 'aria', 
                              'aria-hidden element should not be focusable', 
                              element.name)
                              
        # Check for proper aria-labelledby references
        labelledby_elements = soup.find_all(attrs={'aria-labelledby': True})
        for element in labelledby_elements:
            labelledby_ids = element.get('aria-labelledby').split()
            for label_id in labelledby_ids:
                if not soup.find(attrs={'id': label_id}):
                    self.add_issue(file_path, 0, 'major', 'aria', 
                                  f'aria-labelledby references non-existent id: {label_id}', 
                                  element.name)
                                  
    def check_landmarks(self, file_path: Path, soup: BeautifulSoup):
        """Check landmark usage."""
        
        # Check for multiple main landmarks
        main_elements = soup.find_all('main')
        main_roles = soup.find_all(attrs={'role': 'main'})
        total_main = len(main_elements) + len(main_roles)
        
        if total_main > 1:
            self.add_issue(file_path, 0, 'major', 'landmarks', 
                          'Multiple main landmarks found', 'page')
                          
        # Check for banner landmark
        header_elements = soup.find_all('header')
        banner_roles = soup.find_all(attrs={'role': 'banner'})
        
        if not header_elements and not banner_roles:
            self.add_issue(file_path, 0, 'minor', 'landmarks', 
                          'Missing banner landmark', 'page')
                          
        # Check for contentinfo landmark
        footer_elements = soup.find_all('footer')
        contentinfo_roles = soup.find_all(attrs={'role': 'contentinfo'})
        
        if not footer_elements and not contentinfo_roles:
            self.add_issue(file_path, 0, 'minor', 'landmarks', 
                          'Missing contentinfo landmark', 'page')
                          
    def check_tables(self, file_path: Path, soup: BeautifulSoup):
        """Check table accessibility."""
        tables = soup.find_all('table')
        
        for table in tables:
            # Check for table headers
            headers = table.find_all('th')
            if not headers:
                self.add_issue(file_path, 0, 'major', 'tables', 
                              'Table missing header cells (th)', 'table')
                              
            # Check for table caption or aria-label
            caption = table.find('caption')
            aria_label = table.get('aria-label')
            aria_labelledby = table.get('aria-labelledby')
            
            if not caption and not aria_label and not aria_labelledby:
                self.add_issue(file_path, 0, 'minor', 'tables', 
                              'Table missing caption or aria-label', 'table')
                              
    def generate_report(self) -> str:
        """Generate a text report of validation results."""
        if not self.issues:
            return "✅ No accessibility issues found in templates!"
            
        report = []
        report.append("🔍 CodeXam Template Accessibility Validation Report")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        total_issues = len(self.issues)
        critical_issues = len([i for i in self.issues if i.severity == 'critical'])
        major_issues = len([i for i in self.issues if i.severity == 'major'])
        minor_issues = len([i for i in self.issues if i.severity == 'minor'])
        
        report.append("📊 Summary:")
        report.append(f"  Total Issues: {total_issues}")
        report.append(f"  🔴 Critical: {critical_issues}")
        report.append(f"  🟡 Major: {major_issues}")
        report.append(f"  🔵 Minor: {minor_issues}")
        report.append("")
        
        # Issues by file
        issues_by_file = {}
        for issue in self.issues:
            if issue.file not in issues_by_file:
                issues_by_file[issue.file] = []
            issues_by_file[issue.file].append(issue)
            
        for file_name, file_issues in issues_by_file.items():
            report.append(f"📄 {file_name}:")
            report.append("-" * 40)
            
            for issue in file_issues:
                severity_icon = {"critical": "🔴", "major": "🟡", "minor": "🔵"}
                icon = severity_icon.get(issue.severity, "⚪")
                
                report.append(f"  {icon} {issue.type.upper()}: {issue.message}")
                report.append(f"     Element: {issue.element}")
                if issue.line > 0:
                    report.append(f"     Line: {issue.line}")
                report.append("")
                
        # Recommendations
        report.append("💡 Recommendations:")
        report.append("  1. Fix all critical and major issues before deployment")
        report.append("  2. Add proper alt text to all informative images")
        report.append("  3. Ensure all form controls have associated labels")
        report.append("  4. Implement proper heading hierarchy")
        report.append("  5. Add ARIA labels where semantic HTML is insufficient")
        report.append("  6. Test with actual screen readers for validation")
        report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run template validation."""
    validator = TemplateAccessibilityValidator()
    
    # Check if templates directory exists
    if not validator.templates_dir.exists():
        print(f"❌ Templates directory not found: {validator.templates_dir}")
        print("Please run this script from the project root directory.")
        return 1
        
    # Run validation
    issues = validator.validate_all_templates()
    
    # Generate and display report
    report = validator.generate_report()
    print("\n" + report)
    
    # Save report to file
    with open("template_accessibility_validation.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"📄 Report saved to: template_accessibility_validation.txt")
    
    # Return exit code based on issues found
    critical_issues = len([i for i in issues if i.severity == 'critical'])
    major_issues = len([i for i in issues if i.severity == 'major'])
    
    if critical_issues > 0:
        print(f"\n❌ Validation failed: {critical_issues} critical issues found")
        return 1
    elif major_issues > 0:
        print(f"\n⚠️  Validation completed with warnings: {major_issues} major issues found")
        return 0
    else:
        print(f"\n✅ Validation passed: No critical or major issues found")
        return 0


if __name__ == "__main__":
    exit(main())