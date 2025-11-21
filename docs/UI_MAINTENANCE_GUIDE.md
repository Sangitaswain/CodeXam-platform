# CodeXam UI Maintenance Guide

## Overview

This maintenance guide provides comprehensive instructions for maintaining, updating, and extending the CodeXam UI template system. It covers routine maintenance tasks, troubleshooting procedures, and best practices for keeping the "Elite Coding Arena" interface running smoothly.

## Routine Maintenance Tasks

### Daily Monitoring

#### Performance Metrics
- Monitor page load times (target: < 3 seconds on 3G)
- Check Lighthouse scores (accessibility: 95+, performance: 90+)
- Verify CSS/JS file sizes remain optimized
- Monitor error logs for frontend issues

#### Accessibility Checks
- Run automated accessibility scans
- Check keyboard navigation functionality
- Verify screen reader compatibility
- Test color contrast ratios

#### Browser Compatibility
- Test critical user flows in major browsers
- Check mobile responsiveness on various devices
- Verify touch interactions work properly
- Test form submissions and AJAX functionality

### Weekly Tasks

#### Code Quality Review
```bash
# Run CSS linting
npx stylelint "static/css/**/*.css"

# Check JavaScript for errors
npx eslint "static/js/**/*.js"

# Validate HTML templates
html5validator templates/

# Check for accessibility issues
axe-core --include "body" --exclude ".skip-axe"
```

#### Performance Optimization
```bash
# Minify CSS and JavaScript
python simple_optimize.py

# Optimize images
imagemin static/img/* --out-dir=static/img/optimized/

# Check bundle sizes
du -sh static/css/style.min.css
du -sh static/js/main.min.js
```

#### Security Updates
- Update dependencies in `requirements.txt`
- Check for XSS vulnerabilities in templates
- Verify CSRF protection is working
- Review Content Security Policy headers

### Monthly Tasks

#### Comprehensive Testing
```bash
# Run full test suite
python -m pytest tests/ -v

# Test accessibility compliance
python run_accessibility_tests.py

# Cross-browser testing
python run_cross_browser_tests.py

# Integration testing
python task_6_1_integration.py
```

#### Documentation Updates
- Review and update component documentation
- Update style guide with any changes
- Check code examples for accuracy
- Update maintenance procedures

## File Structure and Organization

### Template Files
```
templates/
├── base.html           # Master template - critical for all pages
├── index.html          # Landing page
├── problems.html       # Problem listing
├── problem.html        # Problem solving interface
├── submissions.html    # Submission history
├── leaderboard.html    # User rankings
└── set_name.html      # User name modal
```

### Static Assets
```
static/
├── css/
│   ├── style.css          # Main stylesheet (development)
│   ├── style.min.css      # Minified stylesheet (production)
│   └── clean-nav.css      # Navigation-specific styles
├── js/
│   ├── main.js            # Main JavaScript (development)
│   ├── main.min.js        # Minified JavaScript (production)
│   └── performance-monitor.js # Performance monitoring
└── img/
    ├── icons/             # SVG icons and favicons
    └── optimized/         # Compressed images
```

### Documentation Files
```
├── UI_TEMPLATE_DOCUMENTATION.md    # Complete template documentation
├── STYLE_GUIDE.md                  # Design system and style guide
├── COMPONENT_LIBRARY.md            # Reusable component library
└── UI_MAINTENANCE_GUIDE.md         # This file
```

## Common Maintenance Procedures

### Updating CSS Styles

#### Adding New Styles
1. Edit `static/css/style.css` (never edit minified files directly)
2. Follow established naming conventions
3. Use CSS custom properties for colors and spacing
4. Test responsive behavior
5. Run minification process

```bash
# Minify updated CSS
python simple_optimize.py
```

#### Modifying Existing Styles
1. Locate the relevant CSS section
2. Make changes while preserving existing functionality
3. Test in multiple browsers
4. Check accessibility compliance
5. Update minified assets

```css
/* Example: Updating button hover effects */
.btn-cyber:hover {
    box-shadow: 0 0 20px rgba(0, 255, 65, 0.6);
    transform: translateY(-2px);
    /* New property */
    filter: brightness(1.1);
}
```

### Adding New Components

#### Component Development Process
1. Design the component following the style guide
2. Create HTML structure with proper accessibility
3. Add CSS styling using established patterns
4. Implement JavaScript functionality if needed
5. Document the component in the library
6. Test thoroughly across browsers and devices

#### Example: Adding a New Card Type
```html
<!-- 1. HTML Structure -->
<div class="cyber-card notification-card">
    <div class="card-header">
        <div class="notification-icon">
            <i class="fas fa-bell"></i>
        </div>
        <h5 class="card-title">Notification Title</h5>
    </div>
    <div class="card-body">
        <p class="notification-message">Notification content here</p>
        <small class="notification-time">2 minutes ago</small>
    </div>
</div>
```

```css
/* 2. CSS Styling */
.notification-card {
    border-left: 3px solid var(--cyber-primary);
}

.notification-icon {
    color: var(--cyber-primary);
    margin-right: var(--space-3);
}

.notification-time {
    color: var(--cyber-text-muted);
}
```

### Template Modifications

#### Safe Template Editing
1. Always backup existing templates before major changes
2. Test changes locally before deploying
3. Verify all Jinja2 template variables are properly handled
4. Check for breaking changes in template inheritance
5. Update related templates if necessary

#### Template Inheritance Changes
When modifying `base.html`:
1. Check all child templates for compatibility
2. Test navigation functionality
3. Verify CSS/JS includes are working
4. Check responsive behavior
5. Test accessibility features

### JavaScript Updates

#### Adding New Functionality
```javascript
// Example: Adding a new interactive feature
function initializeNewFeature() {
    const elements = document.querySelectorAll('.new-feature');
    
    elements.forEach(element => {
        element.addEventListener('click', function() {
            // Feature logic here
            this.classList.toggle('active');
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeNewFeature();
});
```

#### Modifying Existing JavaScript
1. Locate the relevant function or event handler
2. Make changes while maintaining backward compatibility
3. Test interactive functionality
4. Check for console errors
5. Update minified assets

## Troubleshooting Guide

### Common Issues and Solutions

#### Layout Problems

**Issue**: Cards not displaying properly on mobile
```css
/* Solution: Check responsive grid settings */
.problems-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--space-6);
}

/* Ensure minimum width isn't too large for mobile */
@media (max-width: 576px) {
    .problems-grid {
        grid-template-columns: 1fr;
    }
}
```

**Issue**: Navigation menu not collapsing on mobile
```javascript
// Solution: Check Bootstrap JavaScript is loaded
// Verify data-bs-toggle attributes are correct
<button class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav">
```

#### Performance Issues

**Issue**: Slow page loading
1. Check CSS/JS file sizes
2. Verify images are optimized
3. Check for unused CSS/JS
4. Test network tab in browser dev tools

```bash
# Optimize assets
python simple_optimize.py

# Check file sizes
ls -lh static/css/style.min.css
ls -lh static/js/main.min.js
```

**Issue**: Poor Lighthouse scores
1. Check accessibility violations
2. Optimize largest contentful paint
3. Minimize cumulative layout shift
4. Optimize first input delay

#### Accessibility Problems

**Issue**: Keyboard navigation not working
```html
<!-- Solution: Ensure proper tabindex and focus management -->
<button class="btn btn-cyber" tabindex="0">
    Submit Code
</button>

<!-- Add focus styles -->
<style>
.btn-cyber:focus-visible {
    outline: 2px solid var(--cyber-primary);
    outline-offset: 2px;
}
</style>
```

**Issue**: Screen reader compatibility
```html
<!-- Solution: Add proper ARIA labels and roles -->
<nav role="navigation" aria-label="Main navigation">
    <ul class="navbar-nav">
        <li class="nav-item">
            <a class="nav-link" href="/problems" aria-label="Browse coding problems">
                Problems
            </a>
        </li>
    </ul>
</nav>
```

#### Cross-Browser Issues

**Issue**: Styles not working in older browsers
```css
/* Solution: Add vendor prefixes and fallbacks */
.cyber-card {
    background: #1a1a1a; /* Fallback */
    background: var(--cyber-bg-secondary);
    
    display: -webkit-box; /* Fallback */
    display: -ms-flexbox; /* Fallback */
    display: flex;
}
```

### Debugging Tools and Commands

#### CSS Debugging
```bash
# Check for CSS syntax errors
npx stylelint "static/css/**/*.css" --fix

# Validate CSS
npx css-validator static/css/style.css
```

#### JavaScript Debugging
```bash
# Check for JavaScript errors
npx eslint "static/js/**/*.js" --fix

# Check for unused code
npx eslint "static/js/**/*.js" --ext .js --no-unused-vars
```

#### Template Debugging
```python
# Test template rendering
from flask import Flask, render_template
app = Flask(__name__)

with app.app_context():
    try:
        rendered = render_template('problems.html', problems=[])
        print("Template renders successfully")
    except Exception as e:
        print(f"Template error: {e}")
```

## Deployment Procedures

### Pre-Deployment Checklist

- [ ] All tests passing (`python -m pytest tests/`)
- [ ] Accessibility compliance verified
- [ ] Cross-browser testing complete
- [ ] Performance benchmarks met
- [ ] CSS/JS assets minified
- [ ] Documentation updated
- [ ] Backup created

### Production Deployment

```bash
# 1. Minify assets
python simple_optimize.py

# 2. Run final tests
python task_6_1_integration.py

# 3. Check file integrity
sha256sum static/css/style.min.css
sha256sum static/js/main.min.js

# 4. Deploy files
# (Deployment process depends on hosting environment)

# 5. Verify deployment
curl -I https://your-domain.com/static/css/style.min.css
```

### Post-Deployment Verification

1. Test critical user paths
2. Check console for errors
3. Verify asset loading
4. Test form submissions
5. Check mobile responsiveness

## Monitoring and Analytics

### Performance Monitoring

```javascript
// Monitor page load times
window.addEventListener('load', function() {
    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
    console.log('Page load time:', loadTime, 'ms');
    
    // Send to analytics if needed
    if (loadTime > 3000) {
        console.warn('Page load time exceeds target');
    }
});
```

### Error Tracking

```javascript
// Monitor JavaScript errors
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Log to error tracking service
});

// Monitor unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
});
```

### User Experience Metrics

- Track form submission success rates
- Monitor code editor usage patterns
- Measure time spent on problem pages
- Track navigation patterns

## Version Control and Branching

### Git Workflow for UI Changes

```bash
# Create feature branch for UI changes
git checkout -b ui/feature-name

# Make changes and test thoroughly
git add .
git commit -m "Add new component: notification cards"

# Test in staging environment
git checkout staging
git merge ui/feature-name

# Deploy to production
git checkout main
git merge staging
git tag -a v1.2.0 -m "Release version 1.2.0"
```

### Change Documentation

```markdown
# CHANGELOG.md format
## [1.2.0] - 2025-07-27

### Added
- New notification card component
- Enhanced mobile navigation
- Performance monitoring dashboard

### Changed
- Updated button hover effects
- Improved color contrast ratios

### Fixed
- Navigation menu collapse on mobile
- Form validation error messages
```

## Emergency Procedures

### Critical Bug Fixes

1. **Identify the Issue**
   - Check error logs
   - Reproduce the problem
   - Assess impact on users

2. **Quick Fix Implementation**
   ```bash
   # Create hotfix branch
   git checkout -b hotfix/critical-bug
   
   # Make minimal changes to fix issue
   # Test fix thoroughly
   
   # Deploy immediately
   git checkout main
   git merge hotfix/critical-bug
   ```

3. **Post-Fix Actions**
   - Monitor for additional issues
   - Update documentation
   - Plan permanent solution if needed

### Rollback Procedures

```bash
# Rollback to previous version
git checkout main
git reset --hard HEAD~1

# Or rollback to specific version
git checkout main
git reset --hard v1.1.0

# Force push if necessary (use with caution)
git push --force-with-lease origin main
```

## Best Practices Summary

### Code Quality
- Follow established naming conventions
- Write semantic HTML
- Use CSS custom properties
- Implement proper error handling
- Add comprehensive comments

### Performance
- Minimize HTTP requests
- Optimize images and assets
- Use efficient CSS selectors
- Implement lazy loading where appropriate
- Monitor bundle sizes

### Accessibility
- Use semantic HTML elements
- Provide proper ARIA labels
- Ensure keyboard navigation
- Maintain color contrast ratios
- Test with screen readers

### Maintainability
- Document all changes
- Use consistent code formatting
- Write reusable components
- Keep documentation updated
- Regular code reviews

This maintenance guide ensures the CodeXam UI system remains robust, performant, and accessible while providing clear procedures for ongoing development and troubleshooting.
