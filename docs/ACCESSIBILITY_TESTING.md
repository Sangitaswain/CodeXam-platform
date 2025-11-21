# CodeXam Accessibility Testing Guide

This document provides comprehensive guidance for accessibility testing of the CodeXam UI templates to ensure WCAG 2.1 AA compliance.

## Overview

The CodeXam platform implements comprehensive accessibility testing to ensure all users, including those with disabilities, can effectively use the coding challenge platform. Our testing approach combines automated tools, manual testing procedures, and continuous integration to maintain high accessibility standards.

## Testing Framework

### Automated Testing Tools

1. **Custom Accessibility Test Suite** (`tests/test_accessibility.py`)
   - Color contrast analysis
   - Keyboard navigation testing
   - ARIA label validation
   - Screen reader compatibility checks
   - HTML structure validation

2. **Lighthouse CI Integration**
   - Automated accessibility audits
   - Performance and SEO testing
   - Best practices validation
   - Continuous monitoring

3. **Browser-based Testing**
   - Selenium WebDriver automation
   - Cross-browser compatibility
   - Responsive design testing
   - Focus management validation

### Manual Testing Procedures

1. **Screen Reader Testing**
   - NVDA (Windows)
   - JAWS (Windows)
   - VoiceOver (macOS)
   - TalkBack (Android)

2. **Keyboard Navigation Testing**
   - Tab order validation
   - Focus indicator visibility
   - Skip link functionality
   - Keyboard trap detection

3. **Visual Testing**
   - Color contrast verification
   - High contrast mode testing
   - Zoom testing (up to 200%)
   - Color blindness simulation

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements-accessibility.txt

# Install Chrome/Chromium for automated testing
# Ubuntu/Debian:
sudo apt-get install chromium-browser chromium-chromedriver

# macOS:
brew install --cask google-chrome
brew install chromedriver

# Windows:
# Download Chrome and ChromeDriver manually
```

### Running Tests

```bash
# Run all accessibility tests
python run_accessibility_tests.py

# Run tests in headless mode (CI/CD)
python run_accessibility_tests.py --headless

# Test specific pages
python run_accessibility_tests.py --pages "/,/problems,/problem/1"

# Generate different report formats
python run_accessibility_tests.py --output html    # HTML report
python run_accessibility_tests.py --output json    # JSON report
python run_accessibility_tests.py --output text    # Text report

# Run with pytest
pytest tests/test_accessibility.py -v

# Run Lighthouse audit
npm install -g @lhci/cli
lhci autorun --config=.lighthouserc.json
```

## Test Coverage

### Pages Tested

| Page | Priority | Key Features |
|------|----------|--------------|
| Homepage (/) | High | Hero section, statistics, navigation |
| Problems List (/problems) | High | Problem cards, filters, search |
| Problem Detail (/problem/1) | Critical | Code editor, problem description |
| Submissions (/submissions) | Medium | Data tables, history |
| Leaderboard (/leaderboard) | Medium | Rankings, user profiles |

### Accessibility Features Tested

#### 1. Keyboard Navigation
- **Tab Order**: Logical progression through interactive elements
- **Focus Indicators**: Visible focus states for all interactive elements
- **Skip Links**: "Skip to main content" functionality
- **Keyboard Shortcuts**: Custom shortcuts don't conflict with assistive technology
- **Focus Management**: Proper focus handling in modals and dynamic content

#### 2. Screen Reader Compatibility
- **Semantic HTML**: Proper use of headings, landmarks, and structure
- **ARIA Labels**: Descriptive labels for all interactive elements
- **Live Regions**: Status updates announced to screen readers
- **Table Headers**: Proper association of data cells with headers
- **Form Labels**: All form controls have associated labels

#### 3. Visual Accessibility
- **Color Contrast**: 4.5:1 ratio for normal text, 3:1 for large text
- **Color Independence**: Information not conveyed by color alone
- **Focus Visibility**: Clear focus indicators with 3:1 contrast ratio
- **Responsive Design**: Usable at 200% zoom level
- **High Contrast**: Compatible with high contrast modes

#### 4. Content Accessibility
- **Alternative Text**: Descriptive alt text for all informative images
- **Headings Structure**: Logical heading hierarchy (H1 → H2 → H3)
- **Language Declaration**: HTML lang attribute properly set
- **Error Messages**: Clear, descriptive error messages
- **Instructions**: Helpful instructions for complex interactions

## Test Results and Reporting

### Report Formats

1. **HTML Report** (`accessibility_report.html`)
   - Visual dashboard with charts and graphs
   - Detailed issue breakdown by page
   - WCAG compliance status
   - Recommendations and next steps

2. **JSON Report** (`accessibility_report.json`)
   - Machine-readable format for CI/CD integration
   - Structured data for programmatic analysis
   - Issue tracking and trend analysis

3. **Text Report** (`accessibility_report.txt`)
   - Command-line friendly format
   - Quick overview of issues
   - Suitable for email notifications

### Issue Severity Levels

#### Critical Issues
- Complete barriers to access
- WCAG 2.1 AA failures
- Keyboard traps
- Missing alternative text for informative images
- Insufficient color contrast (below 4.5:1)

#### Major Issues
- Significant usability problems
- Missing or inadequate labels
- Poor focus management
- Confusing navigation
- Inconsistent behavior

#### Minor Issues
- Enhancement opportunities
- Suboptimal but functional
- Style improvements
- Performance optimizations

## Continuous Integration

### GitHub Actions Workflow

The accessibility testing is integrated into our CI/CD pipeline:

```yaml
# .github/workflows/accessibility-testing.yml
- Runs on every push and pull request
- Tests all main pages automatically
- Generates reports and artifacts
- Fails build if critical issues found
- Comments on PRs with results
```

### Quality Gates

- **Critical Issues**: 0 allowed (build fails)
- **Major Issues**: 0 allowed (build fails)
- **Minor Issues**: Up to 10 allowed (build passes with warnings)
- **WCAG Compliance**: Must achieve AA level

## Manual Testing Procedures

### Screen Reader Testing Checklist

#### NVDA Testing (Windows)
1. **Installation**: Download from [nvaccess.org](https://www.nvaccess.org/)
2. **Basic Navigation**:
   - `H` - Navigate by headings
   - `K` - Navigate by links
   - `B` - Navigate by buttons
   - `F` - Navigate by form fields
   - `T` - Navigate by tables
   - `D` - Navigate by landmarks

3. **Testing Procedure**:
   ```
   1. Start NVDA
   2. Open browser and navigate to CodeXam
   3. Use heading navigation to understand page structure
   4. Test all interactive elements
   5. Verify form labels and error messages
   6. Check table navigation (if applicable)
   7. Test dynamic content updates
   ```

#### VoiceOver Testing (macOS)
1. **Activation**: `Cmd + F5` or System Preferences → Accessibility
2. **Basic Navigation**:
   - `VO + Right Arrow` - Next item
   - `VO + Left Arrow` - Previous item
   - `VO + U` - Web rotor (navigation menu)
   - `VO + Cmd + H` - Next heading

3. **Testing Procedure**:
   ```
   1. Enable VoiceOver
   2. Open Safari and navigate to CodeXam
   3. Use web rotor to navigate by headings, links, form controls
   4. Test all interactive elements
   5. Verify announcements for dynamic content
   6. Check form interaction and validation
   ```

### Keyboard Navigation Testing

#### Test Procedure
1. **Tab Navigation**:
   ```
   1. Start at top of page
   2. Press Tab to move through interactive elements
   3. Verify logical order (left-to-right, top-to-bottom)
   4. Check all buttons, links, form controls are reachable
   5. Ensure focus indicators are visible
   ```

2. **Reverse Navigation**:
   ```
   1. Use Shift+Tab to navigate backwards
   2. Verify reverse order matches forward order
   3. Ensure no elements are skipped
   ```

3. **Skip Links**:
   ```
   1. Press Tab on page load
   2. Verify skip link appears
   3. Activate skip link (Enter/Space)
   4. Verify focus moves to main content
   ```

### Color Contrast Testing

#### Tools
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Colour Contrast Analyser](https://www.tpgi.com/color-contrast-checker/)
- Browser developer tools

#### Test Procedure
1. **Identify Text Elements**:
   - Body text
   - Navigation links
   - Button text
   - Form labels
   - Status messages

2. **Measure Contrast**:
   ```
   1. Use color picker to get foreground/background colors
   2. Input colors into contrast checker
   3. Verify ratio meets WCAG requirements:
      - Normal text: 4.5:1 minimum
      - Large text: 3.0:1 minimum
      - UI components: 3.0:1 minimum
   ```

3. **Test Different States**:
   - Normal state
   - Hover state
   - Focus state
   - Active state
   - Disabled state

## Troubleshooting

### Common Issues and Solutions

#### 1. ChromeDriver Issues
```bash
# Update ChromeDriver
pip install --upgrade selenium
webdriver-manager --chrome

# Manual installation
# Download from https://chromedriver.chromium.org/
# Add to PATH or specify location in tests
```

#### 2. Headless Mode Problems
```bash
# Add display for headless testing
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &

# Alternative: use --headless flag
python run_accessibility_tests.py --headless
```

#### 3. Permission Issues
```bash
# Fix Chrome sandbox issues
google-chrome --no-sandbox --disable-dev-shm-usage

# Or run with different user
sudo -u www-data python run_accessibility_tests.py
```

#### 4. Network Timeouts
```python
# Increase timeouts in accessibility_config.json
{
  "testing_config": {
    "timeout": 60,
    "page_load_timeout": 60
  }
}
```

### Debugging Tips

1. **Enable Verbose Logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Take Screenshots**:
   ```python
   driver.save_screenshot('debug_screenshot.png')
   ```

3. **Inspect Elements**:
   ```python
   element = driver.find_element(By.ID, "problematic-element")
   print(f"Element HTML: {element.get_attribute('outerHTML')}")
   ```

4. **Check Console Errors**:
   ```python
   logs = driver.get_log('browser')
   for log in logs:
       print(f"Console: {log}")
   ```

## Best Practices

### Development Guidelines

1. **Semantic HTML First**:
   ```html
   <!-- Good -->
   <button type="submit">Submit Solution</button>
   <nav aria-label="Main navigation">...</nav>
   <main id="main-content">...</main>
   
   <!-- Avoid -->
   <div onclick="submit()">Submit Solution</div>
   <div class="navigation">...</div>
   <div class="content">...</div>
   ```

2. **Proper ARIA Usage**:
   ```html
   <!-- Form labels -->
   <label for="username">Username:</label>
   <input type="text" id="username" required aria-describedby="username-help">
   <div id="username-help">Enter your coding handle</div>
   
   <!-- Status messages -->
   <div aria-live="polite" id="status"></div>
   
   <!-- Complex widgets -->
   <div role="tablist" aria-label="Code editor options">
     <button role="tab" aria-selected="true" aria-controls="python-panel">Python</button>
     <button role="tab" aria-selected="false" aria-controls="js-panel">JavaScript</button>
   </div>
   ```

3. **Focus Management**:
   ```javascript
   // Modal focus management
   function openModal(modal) {
     modal.style.display = 'block';
     modal.querySelector('.modal-title').focus();
     trapFocus(modal);
   }
   
   function closeModal(modal, returnFocus) {
     modal.style.display = 'none';
     returnFocus.focus();
   }
   ```

4. **Color and Contrast**:
   ```css
   /* Ensure sufficient contrast */
   .btn-primary {
     background: #007bff;  /* 4.5:1 contrast with white text */
     color: #ffffff;
   }
   
   /* Don't rely on color alone */
   .status-success {
     color: #28a745;
     background: url('checkmark.svg') no-repeat left center;
   }
   
   .status-error {
     color: #dc3545;
     background: url('error.svg') no-repeat left center;
   }
   ```

### Testing Guidelines

1. **Test Early and Often**:
   - Run accessibility tests during development
   - Include accessibility in code reviews
   - Test with actual assistive technology

2. **Comprehensive Coverage**:
   - Test all user workflows
   - Include error states and edge cases
   - Test responsive breakpoints

3. **Real User Testing**:
   - Include users with disabilities in testing
   - Gather feedback on usability
   - Iterate based on real-world usage

## Resources

### WCAG Guidelines
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM WCAG 2 Checklist](https://webaim.org/standards/wcag/checklist)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)

### Testing Tools
- [WAVE Web Accessibility Evaluator](https://wave.webaim.org/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Color Oracle](https://colororacle.org/) (Color blindness simulator)

### Screen Readers
- [NVDA](https://www.nvaccess.org/) (Free, Windows)
- [JAWS](https://www.freedomscientific.com/products/software/jaws/) (Commercial, Windows)
- [VoiceOver](https://support.apple.com/guide/voiceover/) (Built-in, macOS/iOS)
- [TalkBack](https://support.google.com/accessibility/android/answer/6283677) (Built-in, Android)

### Learning Resources
- [WebAIM Training](https://webaim.org/training/)
- [Deque University](https://dequeuniversity.com/)
- [A11y Project](https://www.a11yproject.com/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

## Support

For questions about accessibility testing or to report accessibility issues:

1. **Create an Issue**: Use the GitHub issue tracker with the "accessibility" label
2. **Documentation**: Check this guide and the manual testing checklist
3. **Team Contact**: Reach out to the development team for guidance

Remember: Accessibility is not a one-time task but an ongoing commitment to inclusive design and development.