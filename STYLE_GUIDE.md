# CodeXam Style Guide

## Design Philosophy

The CodeXam platform embodies the "Elite Coding Arena" concept with a cyber-punk aesthetic that creates an immersive coding environment. This style guide ensures consistency across all UI components while maintaining the dark hacker theme.

## Visual Identity

### Brand Elements

**Logo**: `</> CodeXam`
- Uses monospace font (JetBrains Mono)
- Neon green color (#00ff41)
- Subtle glow effect on hover
- Terminal-style bracket notation

**Tagline**: "Elite Coding Arena"
- Positioned as hero headline
- Animated typing effect
- Glitch text animation on load

### Color Palette

#### Primary Colors
```css
--cyber-primary: #00ff41      /* Neon Green - Primary brand color */
--cyber-secondary: #0d7a2b    /* Dark Green - Secondary actions */
--cyber-accent: #39ff14       /* Bright Green - Highlights and accents */
```

#### Background Colors
```css
--cyber-bg-primary: #0a0a0a   /* Deep Black - Main background */
--cyber-bg-secondary: #1a1a1a /* Dark Gray - Card backgrounds */
--cyber-bg-tertiary: #2d2d2d  /* Medium Gray - Elevated surfaces */
```

#### Text Colors
```css
--cyber-text-primary: #e0e0e0 /* Light Gray - Primary text */
--cyber-text-secondary: #b0b0b0 /* Medium Gray - Secondary text */
--cyber-text-muted: #808080   /* Muted Gray - Disabled/placeholder text */
```

#### Status Colors
```css
--cyber-success: #00ff41      /* Success Green - Passed tests */
--cyber-warning: #ffaa00      /* Warning Orange - Pending states */
--cyber-danger: #ff0040       /* Error Red - Failed tests */
--cyber-info: #00aaff         /* Info Blue - Information displays */
```

#### Difficulty Colors
```css
--difficulty-easy: #4ade80    /* Light Green - Easy problems */
--difficulty-medium: #fbbf24  /* Yellow - Medium problems */
--difficulty-hard: #f87171    /* Light Red - Hard problems */
```

### Typography

#### Font Families
```css
/* Monospace - Code and tech elements */
--font-mono: 'JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', monospace;

/* Sans-serif - UI text and content */
--font-sans: 'Space Grotesk', 'Inter', 'Segoe UI', sans-serif;
```

#### Font Scale
```css
--fs-xs: 0.75rem      /* 12px - Small labels */
--fs-sm: 0.875rem     /* 14px - Body small */
--fs-base: 1rem       /* 16px - Body text */
--fs-lg: 1.125rem     /* 18px - Large body */
--fs-xl: 1.25rem      /* 20px - Small headings */
--fs-2xl: 1.5rem      /* 24px - Medium headings */
--fs-3xl: 1.875rem    /* 30px - Large headings */
--fs-4xl: 2.25rem     /* 36px - Hero headings */
--fs-5xl: 3rem        /* 48px - Display headings */
```

#### Font Weights
```css
--fw-light: 300
--fw-normal: 400
--fw-medium: 500
--fw-semibold: 600
--fw-bold: 700
```

### Spacing System

#### Base Spacing Scale
```css
--space-1: 0.25rem    /* 4px */
--space-2: 0.5rem     /* 8px */
--space-3: 0.75rem    /* 12px */
--space-4: 1rem       /* 16px */
--space-5: 1.25rem    /* 20px */
--space-6: 1.5rem     /* 24px */
--space-8: 2rem       /* 32px */
--space-10: 2.5rem    /* 40px */
--space-12: 3rem      /* 48px */
--space-16: 4rem      /* 64px */
--space-20: 5rem      /* 80px */
--space-24: 6rem      /* 96px */
```

#### Component Spacing
- **Cards**: `--space-6` padding, `--space-4` margin
- **Buttons**: `--space-3` vertical, `--space-6` horizontal padding
- **Forms**: `--space-4` between fields
- **Navigation**: `--space-4` between items

## Component Design System

### Buttons

#### Primary Button (`.btn-cyber`)
```css
.btn-cyber {
    background: linear-gradient(135deg, var(--cyber-primary), var(--cyber-secondary));
    color: var(--cyber-bg-primary);
    border: 1px solid var(--cyber-primary);
    border-radius: 0.375rem;
    padding: var(--space-3) var(--space-6);
    font-family: var(--font-mono);
    font-weight: var(--fw-semibold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.3s ease;
    box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
}

.btn-cyber:hover {
    box-shadow: 0 0 20px rgba(0, 255, 65, 0.6);
    transform: translateY(-2px);
}
```

#### Secondary Button (`.btn-cyber-outline`)
```css
.btn-cyber-outline {
    background: transparent;
    color: var(--cyber-primary);
    border: 1px solid var(--cyber-primary);
    /* ... similar styling with outline variation */
}
```

#### Ghost Button (`.btn-cyber-ghost`)
```css
.btn-cyber-ghost {
    background: transparent;
    color: var(--cyber-text-secondary);
    border: 1px solid transparent;
    /* ... minimal styling for subtle actions */
}
```

### Cards

#### Base Card (`.cyber-card`)
```css
.cyber-card {
    background: var(--cyber-bg-secondary);
    border: 1px solid rgba(0, 255, 65, 0.2);
    border-radius: 0.5rem;
    padding: var(--space-6);
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.cyber-card:hover {
    border-color: rgba(0, 255, 65, 0.5);
    box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);
    transform: translateY(-2px);
}
```

#### Problem Card (`.problem-card`)
- Extends `.cyber-card`
- Includes difficulty badge
- Hover effects with glow
- Statistics display area

#### Statistics Card (`.stat-card`)
- Terminal-style appearance
- Monospace typography
- Animated counters
- Neon accent borders

### Forms

#### Input Fields (`.cyber-input`)
```css
.cyber-input {
    background: var(--cyber-bg-primary);
    color: var(--cyber-text-primary);
    border: 1px solid rgba(0, 255, 65, 0.3);
    border-radius: 0.375rem;
    padding: var(--space-3) var(--space-4);
    font-family: var(--font-mono);
    transition: all 0.3s ease;
}

.cyber-input:focus {
    border-color: var(--cyber-primary);
    box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
    outline: none;
}
```

#### Select Dropdowns (`.cyber-select`)
- Similar styling to inputs
- Custom dropdown arrow
- Hover and focus states
- Option styling consistency

#### Textareas (`.cyber-textarea`)
- Code editor styling
- Monospace font
- Line number integration
- Syntax highlighting support

### Navigation

#### Main Navigation (`.cyber-nav`)
```css
.cyber-nav {
    background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
    border-bottom: 1px solid rgba(0, 255, 65, 0.2);
    backdrop-filter: blur(10px);
    position: sticky;
    top: 0;
    z-index: 1000;
}
```

#### Navigation Links (`.cyber-nav-link`)
```css
.cyber-nav-link {
    color: var(--cyber-text-secondary);
    padding: var(--space-3) var(--space-4);
    text-decoration: none;
    transition: all 0.3s ease;
    position: relative;
}

.cyber-nav-link:hover,
.cyber-nav-link.active {
    color: var(--cyber-primary);
}

.cyber-nav-link.active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--cyber-primary);
    box-shadow: 0 0 5px var(--cyber-primary);
}
```

### Status Indicators

#### Badges
```css
.badge {
    font-family: var(--font-mono);
    font-size: var(--fs-xs);
    font-weight: var(--fw-semibold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: var(--space-1) var(--space-3);
    border-radius: 1rem;
}

/* Difficulty Badges */
.status-easy {
    background: var(--difficulty-easy);
    color: var(--cyber-bg-primary);
}

.status-medium {
    background: var(--difficulty-medium);
    color: var(--cyber-bg-primary);
}

.status-hard {
    background: var(--difficulty-hard);
    color: var(--cyber-bg-primary);
}

/* Status Badges */
.status-passed {
    background: var(--cyber-success);
    color: var(--cyber-bg-primary);
}

.status-failed {
    background: var(--cyber-danger);
    color: white;
}

.status-pending {
    background: var(--cyber-warning);
    color: var(--cyber-bg-primary);
}
```

## Animation Guidelines

### Micro-Interactions

#### Hover Effects
```css
/* Standard hover transition */
.interactive-element {
    transition: all 0.3s ease;
}

.interactive-element:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);
}
```

#### Glow Effects
```css
.glow-on-hover:hover {
    box-shadow: 0 0 20px rgba(0, 255, 65, 0.6);
    border-color: var(--cyber-primary);
}
```

#### Loading States
```css
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.loading {
    animation: pulse 1.5s ease-in-out infinite;
}
```

### Page Transitions

#### Fade In Animation
```css
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.6s ease-out;
}
```

#### Typing Animation
```javascript
function typeText(element, text, speed = 50) {
    let i = 0;
    element.innerHTML = '';
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}
```

## Layout Patterns

### Grid System

#### Problem Grid
```css
.problems-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--space-6);
    padding: var(--space-6);
}
```

#### Split Layout (Problem Detail)
```css
.split-layout {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--space-4);
}

@media (min-width: 992px) {
    .split-layout {
        grid-template-columns: 1fr 1fr;
        gap: var(--space-8);
    }
}
```

### Container Patterns

#### Page Container
```css
.page-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--space-4);
}
```

#### Content Section
```css
.content-section {
    padding: var(--space-12) 0;
}

.content-section + .content-section {
    border-top: 1px solid rgba(0, 255, 65, 0.1);
}
```

## Responsive Design

### Breakpoint Strategy

```css
/* Mobile First Approach */
/* Base styles: 0-575px (Mobile) */

@media (min-width: 576px) {
    /* Small devices and up */
}

@media (min-width: 768px) {
    /* Medium devices and up */
}

@media (min-width: 992px) {
    /* Large devices and up */
}

@media (min-width: 1200px) {
    /* Extra large devices and up */
}
```

### Responsive Patterns

#### Navigation Collapse
```css
.navbar-nav {
    flex-direction: column;
    width: 100%;
}

@media (min-width: 768px) {
    .navbar-nav {
        flex-direction: row;
        width: auto;
    }
}
```

#### Card Stacking
```css
.card-grid {
    grid-template-columns: 1fr;
}

@media (min-width: 768px) {
    .card-grid {
        grid-template-columns: 1fr 1fr;
    }
}

@media (min-width: 1200px) {
    .card-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}
```

## Accessibility Standards

### Color Contrast

All color combinations meet WCAG 2.1 AA standards:

- **Normal text**: 4.5:1 contrast ratio minimum
- **Large text**: 3:1 contrast ratio minimum
- **Interactive elements**: 3:1 contrast ratio with adjacent colors

### Focus Indicators

```css
.focusable:focus {
    outline: 2px solid var(--cyber-primary);
    outline-offset: 2px;
    box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
}

/* Remove default focus outline */
.focusable:focus {
    outline: none;
}

/* Custom focus ring */
.focusable:focus-visible {
    box-shadow: 0 0 0 2px var(--cyber-primary);
}
```

### Screen Reader Support

```css
/* Screen reader only text */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
```

## Performance Guidelines

### CSS Optimization

#### Critical CSS
- Inline critical above-the-fold styles
- Load non-critical CSS asynchronously
- Use CSS custom properties for theme consistency

#### Efficient Selectors
```css
/* Good - Specific and efficient */
.cyber-card { }
.btn-cyber { }

/* Avoid - Overly complex selectors */
div.container > ul li:nth-child(odd) a { }
```

### Asset Loading

```html
<!-- Preload critical resources -->
<link rel="preload" href="/static/css/style.min.css" as="style">
<link rel="preload" href="/static/fonts/jetbrains-mono.woff2" as="font" type="font/woff2" crossorigin>

<!-- Load CSS with fallback -->
<link rel="stylesheet" href="/static/css/style.min.css" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="/static/css/style.min.css"></noscript>
```

## Code Examples

### Complete Component Example

```html
<!-- Problem Card Component -->
<div class="col-lg-4 col-md-6 mb-4">
    <div class="cyber-card problem-card h-100" role="article">
        <div class="card-header d-flex justify-content-between align-items-start">
            <h5 class="card-title mb-0">{{ problem.title }}</h5>
            <span class="badge status-{{ problem.difficulty.lower() }}" 
                  aria-label="Difficulty: {{ problem.difficulty }}">
                {{ problem.difficulty }}
            </span>
        </div>
        <div class="card-body">
            <p class="card-text text-muted">
                {{ problem.description[:100] }}{% if problem.description|length > 100 %}...{% endif %}
            </p>
            <div class="problem-stats d-flex justify-content-between">
                <small class="text-muted">
                    <i class="fas fa-users" aria-hidden="true"></i>
                    {{ problem.solved_count }} solved
                </small>
                <small class="text-muted">
                    <i class="fas fa-clock" aria-hidden="true"></i>
                    {{ problem.estimated_time }} min
                </small>
            </div>
        </div>
        <div class="card-footer">
            <a href="{{ url_for('routes.problem', id=problem.id) }}" 
               class="btn btn-cyber btn-sm w-100"
               aria-label="Start solving {{ problem.title }}">
                <i class="fas fa-play" aria-hidden="true"></i>
                Start Challenge
            </a>
        </div>
    </div>
</div>
```

### Form Component Example

```html
<!-- Code Submission Form -->
<form class="code-submission-form" role="form" aria-label="Code submission">
    <div class="form-group mb-3">
        <label for="languageSelect" class="form-label">Programming Language</label>
        <select class="cyber-select" id="languageSelect" name="language" required>
            <option value="">Select Language</option>
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
        </select>
    </div>
    
    <div class="form-group mb-3">
        <label for="codeInput" class="form-label">Your Solution</label>
        <textarea class="cyber-textarea code-input" 
                  id="codeInput" 
                  name="code"
                  rows="15" 
                  placeholder="# Write your code here..."
                  spellcheck="false"
                  required
                  aria-describedby="codeHelp"></textarea>
        <div id="codeHelp" class="form-text">
            Write your solution code. Use Ctrl+Enter to submit.
        </div>
    </div>
    
    <div class="form-actions d-flex justify-content-between">
        <button type="button" class="btn btn-cyber-outline" onclick="resetCode()">
            <i class="fas fa-undo" aria-hidden="true"></i>
            Reset
        </button>
        <button type="submit" class="btn btn-cyber" id="submitBtn">
            <i class="fas fa-play" aria-hidden="true"></i>
            Run Code
        </button>
    </div>
</form>
```

## Maintenance and Updates

### Version Control

Track changes to the style guide:
- Document breaking changes
- Maintain backwards compatibility when possible
- Update component examples
- Test across all templates

### Style Guide Updates

When updating the style guide:
1. Update this document
2. Update component examples
3. Test in all browsers
4. Validate accessibility compliance
5. Update minified assets

### Browser Support

Target browser support:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Testing Checklist

Before releasing style updates:
- [ ] Visual regression testing
- [ ] Accessibility audit (WAVE, aXe)
- [ ] Performance impact assessment
- [ ] Cross-browser testing
- [ ] Mobile responsiveness validation
- [ ] Color contrast verification

This style guide ensures consistent implementation of the CodeXam "Elite Coding Arena" design system while maintaining accessibility, performance, and user experience standards.

## Related Documentation

- [Implementation Guide](IMPLEMENTATION_GUIDE.md) - Complete development history and technical architecture
- [Deployment Guide](DEPLOYMENT.md) - Production deployment and configuration
- [Database Management Guide](DATABASE_MANAGEMENT_GUIDE.md) - Database operations and maintenance
- [UI Template Documentation](UI_TEMPLATE_DOCUMENTATION.md) - Detailed template implementation guide
- [UI Maintenance Guide](UI_MAINTENANCE_GUIDE.md) - Template maintenance and updates
