#!/usr/bin/env python3
"""
Elite Theme Integration Test
Tests the new dark hacker theme implementation
"""

import os
import sys
from pathlib import Path

def test_css_architecture():
    """Test that the CSS architecture is properly set up."""
    css_file = Path("static/css/style.css")
    
    if not css_file.exists():
        print("❌ CSS file not found")
        return False
    
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Check for key CSS custom properties
    required_properties = [
        '--bg-primary: #0a0a0a',
        '--accent-primary: #00ff88',
        '--font-mono:',
        '.cyber-navbar',
        '.btn-cyber',
        '.difficulty-badge'
    ]
    
    for prop in required_properties:
        if prop not in css_content:
            print(f"❌ Missing CSS property: {prop}")
            return False
    
    print("✅ CSS architecture properly implemented")
    return True

def test_base_template():
    """Test that the base template exists and has cyber elements."""
    template_file = Path("templates/base.html")
    
    if not template_file.exists():
        print("❌ Base template not found")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Check for key template elements
    required_elements = [
        'cyber-navbar',
        'brand-icon',
        '</> CodeXam',
        'animate-pulse',
        'btn-cyber',
        'JetBrains Mono'
    ]
    
    for element in required_elements:
        if element not in template_content:
            print(f"❌ Missing template element: {element}")
            return False
    
    print("✅ Base template properly implemented")
    return True

def test_landing_page():
    """Test that the landing page has elite theme elements."""
    template_file = Path("templates/index.html")
    
    if not template_file.exists():
        print("❌ Landing page template not found")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Check for key landing page elements
    required_elements = [
        'Elite Coding Arena',
        'Initialize_Challenge()',
        'terminal-prompt',
        'hero-section',
        'cyber-card',
        'Elite Developer Arsenal'
    ]
    
    for element in required_elements:
        if element not in template_content:
            print(f"❌ Missing landing page element: {element}")
            return False
    
    print("✅ Landing page properly implemented")
    return True

def test_problem_list():
    """Test that the problem list has cyber theme."""
    template_file = Path("templates/problems.html")
    
    if not template_file.exists():
        print("❌ Problem list template not found")
        return False
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Check for key problem list elements
    required_elements = [
        'Problem Set',
        'cyber-card',
        'difficulty-badge',
        'btn-cyber-primary',
        'search-input',
        'problems-grid'
    ]
    
    for element in required_elements:
        if element not in template_content:
            print(f"❌ Missing problem list element: {element}")
            return False
    
    print("✅ Problem list properly implemented")
    return True

def test_app_integration():
    """Test that the app can import and create successfully."""
    try:
        import app
        flask_app = app.create_app(testing=True)
        print("✅ App creates successfully with elite theme")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def main():
    """Run all elite theme tests."""
    print("🚀 Testing Elite Hacker Theme Implementation...")
    print("=" * 50)
    
    tests = [
        test_css_architecture,
        test_base_template,
        test_landing_page,
        test_problem_list,
        test_app_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ELITE THEME FULLY OPERATIONAL!")
        print("🔥 Ready for the coding arena!")
        return True
    else:
        print("⚠️  Some issues found, check output above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)