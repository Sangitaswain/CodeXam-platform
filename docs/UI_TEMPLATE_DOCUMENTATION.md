# CodeXam UI Template Documentation

## Overview

This documentation provides a comprehensive guide to the CodeXam UI template system, including template structure, component usage, CSS conventions, and best practices for maintaining the "Elite Coding Arena" dark hacker theme.

## Template Architecture

### Base Template Structure

The UI system is built on a hierarchical template structure with `base.html` as the foundation:

```
templates/
├── base.html           # Master template with navigation and layout
├── index.html          # Landing page - "Elite Coding Arena"
├── problems.html       # Problem list with filtering
├── problem.html        # Problem detail with code editor
├── submissions.html    # Submission history with results
├── leaderboard.html    # Leaderboard with podium design
└── set_name.html      # User name setting modal
```

### Template Hierarchy

```
base.html
├── index.html          (Landing page)
├── problems.html       (Problem listing)
├── problem.html        (Problem solving interface)
├── submissions.html    (History and results)
└── leaderboard.html    (Rankings and achievements)
```

## Core Templates

### 1. Base Template (`templates/base.html`)

**Purpose**: Master template providing consistent layout, navigation, and theme foundation.

**Key Features**:
- Dark hacker theme with cyber-punk aesthetics
- Responsive navigation with glowing effects
- User status management
- Performance optimization integration
- Accessibility compliance

**Template Structure**:
```html
<!DOCTYPE html>
<html lang="en" class="h-100">
<head>
    <!-- Meta tags and performance optimizations -->
    <!-- Critical CSS inlined for performance -->
</head>
<body class="d-flex flex-column h-100 bg-dark text-light">
    <!-- Navigation with cyber branding -->
    <nav class="navbar navbar-expand-lg navbar-dark cyber-nav">
        <!-- Terminal-style navigation -->
    </nav>
    
    <!-- Main content area -->
    <main class="flex-shrink-0">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer and scripts -->
</body>
</html>
```

**Usage Example**:
```html
{% extends "base.html" %}
{% block title %}Your Page Title{% endblock %}
{% block content %}
    <!-- Your page content here -->
{% endblock %}
```

### 2. Landing Page (`templates/index.html`)

**Purpose**: "Elite Coding Arena" welcome page with hero section and statistics.

**Key Components**:
- Hero section with animated typing effect
- Statistics cards with terminal styling
- Feature showcase with glowing effects
- Call-to-action button with cyber aesthetics

**Usage Context**: Displayed when users first visit the platform or navigate to home.

### 3. Problems List (`templates/problems.html`)

**Purpose**: Display available coding problems with filtering and search.

**Key Components**:
- Responsive card grid layout
- Difficulty filtering and search
- Problem statistics display
- Empty state handling

**Template Variables**:
```python
{
    'problems': [
        {
            'id': int,
            'title': str,
            'difficulty': str,  # 'Easy', 'Medium', 'Hard'
            'description': str,
            'solved_count': int,
            'total_submissions': int
        }
    ],
    'difficulty_filter': str,
    'search_query': str
}
```

### 4. Problem Detail (`templates/problem.html`)

**Purpose**: Problem solving interface with integrated code editor.

**Key Components**:
- Split-pane layout (problem description + code editor)
- Multi-language code editor with syntax highlighting
- Submission system with real-time feedback
- Result display with execution statistics

**Template Variables**:
```python
{
    'problem': {
        'id': int,
        'title': str,
        'difficulty': str,
        'description': str,
        'input_format': str,
        'output_format': str,
        'examples': [
            {'input': str, 'output': str}
        ],
        'constraints': str
    },
    'languages': ['python', 'javascript', 'java', 'cpp'],
    'templates': {
        'python': str,
        'javascript': str,
        # ... other language templates
    }
}
```

### 5. Submissions History (`templates/submissions.html`)

**Purpose**: Display user's submission history with filtering and code preview.

**Key Components**:
- Responsive table/card layout
- Status filtering (All, Passed, Failed)
- Expandable code preview
- Pagination support

### 6. Leaderboard (`templates/leaderboard.html`)

**Purpose**: Display user rankings with podium design for top performers.

**Key Components**:
- Podium layout for top 3 users
- Ranked list for remaining users
- User highlighting and achievement indicators
- Responsive design adaptations

## CSS Architecture and Design System

### Color System

The CodeXam UI uses a cyber-punk color palette with CSS custom properties:

```css
:root {
    /* Primary Colors */
    --cyber-primary: #00ff41;      /* Neon green */
    --cyber-secondary: #0d7a2b;    /* Dark green */
    --cyber-accent: #39ff14;       /* Bright green */
    
    /* Background Colors */
    --cyber-bg-primary: #0a0a0a;   /* Deep black */
    --cyber-bg-secondary: #1a1a1a; /* Dark gray */
    --cyber-bg-tertiary: #2d2d2d;  /* Medium gray */
    
    /* Text Colors */
    --cyber-text-primary: #e0e0e0; /* Light gray */
    --cyber-text-secondary: #b0b0b0; /* Medium gray */
    --cyber-text-muted: #808080;   /* Muted gray */
    
    /* Status Colors */
    --cyber-success: #00ff41;      /* Success green */
    --cyber-warning: #ffaa00;      /* Warning orange */
    --cyber-danger: #ff0040;       /* Error red */
    --cyber-info: #00aaff;         /* Info blue */
}
```

### Typography System

```css
/* Font Families */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
--font-sans: 'Space Grotesk', 'Inter', sans-serif;

/* Font Sizes */
--fs-xs: 0.75rem;    /* 12px */
--fs-sm: 0.875rem;   /* 14px */
--fs-base: 1rem;     /* 16px */
--fs-lg: 1.125rem;   /* 18px */
--fs-xl: 1.25rem;    /* 20px */
--fs-2xl: 1.5rem;    /* 24px */
--fs-3xl: 1.875rem;  /* 30px */
--fs-4xl: 2.25rem;   /* 36px */
```

### Component Classes

#### Navigation Components
```css
.cyber-nav          /* Main navigation styling */
.cyber-brand        /* Brand logo with glow effect */
.cyber-nav-link     /* Navigation link styling */
.user-status        /* User status indicator */
```

#### Button Components
```css
.btn-cyber          /* Primary cyber button */
.btn-cyber-outline  /* Outlined cyber button */
.btn-cyber-ghost    /* Ghost cyber button */
.btn-glow           /* Button with glow effect */
```

#### Card Components
```css
.cyber-card         /* Base card component */
.problem-card       /* Problem list card */
.stat-card          /* Statistics card */
.result-card        /* Submission result card */
```

#### Form Components
```css
.cyber-input        /* Input field styling */
.cyber-select       /* Select dropdown styling */
.cyber-textarea     /* Textarea styling */
.form-cyber         /* Form container */
```

#### Status Indicators
```css
.status-easy        /* Easy difficulty badge */
.status-medium      /* Medium difficulty badge */
.status-hard        /* Hard difficulty badge */
.status-passed      /* Passed submission status */
.status-failed      /* Failed submission status */
.status-pending     /* Pending submission status */
```

## Component Library

### 1. Problem Card Component

**Usage**: Display problem information in grid layout.

```html
<div class="col-lg-4 col-md-6 mb-4">
    <div class="cyber-card problem-card h-100">
        <div class="card-header">
            <h5 class="card-title">{{ problem.title }}</h5>
            <span class="badge status-{{ problem.difficulty.lower() }}">
                {{ problem.difficulty }}
            </span>
        </div>
        <div class="card-body">
            <p class="card-text">{{ problem.description[:100] }}...</p>
            <div class="problem-stats">
                <small class="text-muted">
                    {{ problem.solved_count }} solved
                </small>
            </div>
        </div>
        <div class="card-footer">
            <a href="{{ url_for('routes.problem', id=problem.id) }}" 
               class="btn btn-cyber btn-sm">
                Start Challenge
            </a>
        </div>
    </div>
</div>
```

### 2. Status Badge Component

**Usage**: Display status indicators with appropriate styling.

```html
<!-- Difficulty Badges -->
<span class="badge status-easy">Easy</span>
<span class="badge status-medium">Medium</span>
<span class="badge status-hard">Hard</span>

<!-- Submission Status Badges -->
<span class="badge status-passed">Passed</span>
<span class="badge status-failed">Failed</span>
<span class="badge status-pending">Pending</span>
```

### 3. Code Editor Component

**Usage**: Multi-language code editor with syntax highlighting.

```html
<div class="code-editor-container">
    <div class="editor-header">
        <select class="cyber-select" id="languageSelect">
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
        </select>
        <button class="btn btn-cyber btn-sm" id="submitCode">
            <i class="fas fa-play"></i> Run Code
        </button>
    </div>
    <textarea class="cyber-textarea code-input" 
              id="codeInput" 
              placeholder="# Write your code here..."
              spellcheck="false"></textarea>
</div>
```

### 4. Result Display Component

**Usage**: Show code execution results with status styling.

```html
<div class="result-container" style="display: none;">
    <div class="cyber-card result-card">
        <div class="result-header">
            <span class="result-status"></span>
            <span class="result-time"></span>
        </div>
        <div class="result-body">
            <pre class="result-output"></pre>
        </div>
    </div>
</div>
```

## JavaScript Integration

### Code Editor Functionality

```javascript
// Language template switching
function switchLanguage(language) {
    const templates = {
        'python': '# Write your Python code here\ndef solution():\n    pass',
        'javascript': '// Write your JavaScript code here\nfunction solution() {\n    \n}',
        'java': '// Write your Java code here\npublic class Solution {\n    \n}',
        'cpp': '// Write your C++ code here\n#include <iostream>\nusing namespace std;\n\nint main() {\n    \n}'
    };
    
    document.getElementById('codeInput').value = templates[language] || '';
}

// Code submission with AJAX
function submitCode() {
    const code = document.getElementById('codeInput').value;
    const language = document.getElementById('languageSelect').value;
    const problemId = document.getElementById('problemId').value;
    
    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrf_token]').value
        },
        body: JSON.stringify({
            code: code,
            language: language,
            problem_id: problemId
        })
    })
    .then(response => response.json())
    .then(data => displayResult(data))
    .catch(error => console.error('Error:', error));
}
```

### Animation and Effects

```javascript
// Typing animation for hero section
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

// Glow effect on hover
document.querySelectorAll('.btn-glow').forEach(button => {
    button.addEventListener('mouseenter', function() {
        this.style.boxShadow = '0 0 20px var(--cyber-primary)';
    });
    
    button.addEventListener('mouseleave', function() {
        this.style.boxShadow = '0 0 10px var(--cyber-primary)';
    });
});
```

## Accessibility Features

### ARIA Labels and Roles

```html
<!-- Navigation with proper ARIA -->
<nav class="navbar" role="navigation" aria-label="Main navigation">
    <a class="navbar-brand" href="/" aria-label="CodeXam home">
        <span class="cyber-brand">&lt;/&gt; CodeXam</span>
    </a>
</nav>

<!-- Form with accessibility -->
<form role="form" aria-label="Code submission form">
    <label for="languageSelect" class="sr-only">Programming Language</label>
    <select id="languageSelect" aria-label="Select programming language">
        <option value="python">Python</option>
    </select>
    
    <label for="codeInput" class="sr-only">Code Editor</label>
    <textarea id="codeInput" 
              aria-label="Code editor" 
              aria-describedby="codeHelp"></textarea>
    <div id="codeHelp" class="sr-only">
        Enter your code solution here
    </div>
</form>
```

### Keyboard Navigation

```javascript
// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter to submit code
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        submitCode();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Focus management
function manageFocus() {
    // Ensure focus is trapped within modals
    const modal = document.querySelector('.modal.show');
    if (modal) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        // Focus first element
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    }
}
```

### Color Contrast Compliance

All color combinations meet WCAG 2.1 AA standards:

- Text on background: 7:1 contrast ratio
- Interactive elements: 4.5:1 minimum contrast
- Focus indicators: 3:1 contrast with adjacent colors

## Responsive Design Patterns

### Breakpoints

```css
/* Mobile First Approach */
@media (min-width: 576px) { /* Small devices */ }
@media (min-width: 768px) { /* Medium devices */ }
@media (min-width: 992px) { /* Large devices */ }
@media (min-width: 1200px) { /* Extra large devices */ }
```

### Layout Adaptations

```css
/* Problem detail page responsive layout */
.problem-container {
    display: grid;
    gap: 1rem;
    grid-template-columns: 1fr;
}

@media (min-width: 992px) {
    .problem-container {
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
    }
}

/* Navigation responsive behavior */
.cyber-nav .navbar-nav {
    flex-direction: column;
}

@media (min-width: 768px) {
    .cyber-nav .navbar-nav {
        flex-direction: row;
    }
}
```

## Performance Optimization

### Critical CSS Inlining

Critical CSS for above-the-fold content is inlined in the base template:

```html
<style>
/* Critical CSS inlined for performance */
body { background: #0a0a0a; color: #e0e0e0; }
.cyber-nav { background: linear-gradient(135deg, #1a1a1a, #2d2d2d); }
/* ... other critical styles ... */
</style>
```

### Asset Loading Strategy

```html
<!-- Preload critical resources -->
<link rel="preload" href="{{ url_for('static', filename='css/style.min.css') }}" as="style">
<link rel="preload" href="{{ url_for('static', filename='js/main.min.js') }}" as="script">

<!-- Load CSS asynchronously -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.min.css') }}" media="print" onload="this.media='all'">

<!-- Load JavaScript with defer -->
<script src="{{ url_for('static', filename='js/main.min.js') }}" defer></script>
```

## Best Practices

### Template Development

1. **Extend Base Template**: Always extend `base.html` for consistency
2. **Use Semantic HTML**: Proper HTML5 semantic elements
3. **Follow BEM Methodology**: For CSS class naming (when not using utility classes)
4. **Include ARIA Labels**: For accessibility compliance
5. **Test Responsiveness**: On multiple devices and screen sizes

### CSS Guidelines

1. **Use CSS Custom Properties**: For consistent theming
2. **Mobile-First Approach**: Start with mobile styles, enhance for larger screens
3. **Avoid Inline Styles**: Use CSS classes for all styling
4. **Optimize Performance**: Minimize CSS, use efficient selectors
5. **Maintain Consistency**: Follow established design patterns

### JavaScript Best Practices

1. **Progressive Enhancement**: Ensure basic functionality without JavaScript
2. **Event Delegation**: For dynamic content
3. **Error Handling**: Graceful degradation for failed AJAX requests
4. **Accessibility**: Manage focus and keyboard navigation
5. **Performance**: Debounce user input, lazy load content

## Maintenance Guide

### Adding New Templates

1. Create new template file in `templates/` directory
2. Extend `base.html` template
3. Follow established CSS class conventions
4. Include proper accessibility attributes
5. Test responsive design
6. Update this documentation

### Modifying Existing Templates

1. Test changes in multiple browsers
2. Verify accessibility compliance
3. Check responsive behavior
4. Update related CSS/JavaScript
5. Document significant changes

### Updating Styles

1. Use CSS custom properties for theme changes
2. Maintain consistent naming conventions
3. Test color contrast ratios
4. Verify cross-browser compatibility
5. Update minified assets for production

### Performance Monitoring

Regular performance checks should include:

- Page load times (target: < 3 seconds on 3G)
- Lighthouse accessibility score (target: 95+)
- CSS/JavaScript file sizes
- Image optimization
- Critical CSS coverage

## Troubleshooting

### Common Issues

1. **Layout Breaking on Mobile**: Check responsive breakpoints and grid systems
2. **Accessibility Violations**: Use automated testing tools and manual verification
3. **Performance Issues**: Check asset sizes and loading strategies
4. **Cross-Browser Inconsistencies**: Test in all target browsers
5. **JavaScript Errors**: Check console for errors and implement proper error handling

### Debug Tools

- Browser Developer Tools
- Lighthouse for performance and accessibility
- WAVE Web Accessibility Evaluator
- aXe DevTools for accessibility testing
- Responsive design testing tools

This documentation provides the foundation for maintaining and extending the CodeXam UI template system while preserving its cyber-punk aesthetic and ensuring accessibility compliance.
