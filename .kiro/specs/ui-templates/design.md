# Design Document

## Overview

The UI templates design for CodeXam focuses on creating a cohesive, responsive, and accessible user interface that seamlessly integrates with the existing Flask backend. The design follows a component-based approach using Bootstrap 5 as the foundation, enhanced with custom CSS that implements the CodeXam design system defined in ui_ux.md.

**Design Philosophy:**
- Mobile-first responsive design
- Accessibility-first approach (WCAG 2.1 AA compliance)
- Component-based architecture for maintainability
- Progressive enhancement for better performance
- Consistent visual language across all pages

## Architecture

### Template Hierarchy

```
templates/
├── base.html                 # Base template with navigation and common elements
├── index.html               # Landing page extending base
├── problems.html            # Problem list page extending base
├── problem.html             # Problem detail with code editor extending base
├── submissions.html         # Submission history extending base
├── leaderboard.html         # Leaderboard extending base
├── set_name.html           # User identification modal extending base
└── partials/               # Reusable template components
    ├── navbar.html         # Navigation component
    ├── footer.html         # Footer component
    ├── problem_card.html   # Problem card component
    ├── submission_row.html # Submission table row component
    └── result_display.html # Code execution result component
```

### CSS Architecture

```
static/css/
├── bootstrap.min.css       # Bootstrap 5 framework
└── style.css              # Custom CodeXam styles
    ├── CSS Custom Properties (Design System)
    ├── Base Styles
    ├── Component Styles
    ├── Utility Classes
    └── Responsive Overrides
```

### JavaScript Architecture

```
static/js/
├── bootstrap.min.js        # Bootstrap 5 JavaScript
└── editor.js              # Code editor functionality
    ├── Language Management
    ├── Template Switching
    ├── Code Submission
    ├── Result Display
    └── Mobile Adaptations
```

## Dark Hacker Theme Design System

### Color Palette (Inspired by Elite Coding Arena)

```css
:root {
  /* Dark Theme Base Colors */
  --bg-primary: #0a0a0a;           /* Deep black background */
  --bg-secondary: #1a1a1a;        /* Card/panel backgrounds */
  --bg-tertiary: #2a2a2a;         /* Elevated surfaces */
  --bg-accent: #0f1419;           /* Code editor background */
  
  /* Hacker Green Accent System */
  --accent-primary: #00ff88;       /* Bright cyber green */
  --accent-secondary: #00cc6a;     /* Darker green for hover */
  --accent-tertiary: #004d26;      /* Dark green for backgrounds */
  --accent-glow: rgba(0, 255, 136, 0.3); /* Glow effects */
  
  /* Status Colors (Hacker Theme) */
  --status-success: #00ff88;       /* Accepted - Bright green */
  --status-error: #ff4757;         /* Wrong Answer - Cyber red */
  --status-warning: #ffa502;       /* Time Limit - Cyber orange */
  --status-info: #3742fa;          /* Info - Cyber blue */
  
  /* Text Colors */
  --text-primary: #ffffff;         /* Primary white text */
  --text-secondary: #a0a0a0;       /* Muted gray text */
  --text-tertiary: #666666;        /* Subtle gray text */
  --text-accent: #00ff88;          /* Accent green text */
  
  /* Border Colors */
  --border-primary: #333333;       /* Subtle borders */
  --border-accent: #00ff88;        /* Accent borders */
  --border-glow: rgba(0, 255, 136, 0.5); /* Glowing borders */
}
```

### Typography (Hacker Aesthetic)

```css
:root {
  /* Font Families */
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace;
  --font-sans: 'Inter', 'SF Pro Display', system-ui, sans-serif;
  --font-display: 'Space Grotesk', 'Inter', sans-serif;
  
  /* Font Sizes (Refined Scale) */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */
  --text-5xl: 3rem;       /* 48px */
}
```

## Components and Interfaces

### 1. Base Template System (Dark Hacker Theme)

**Base Template (`base.html`)**
- Dark theme foundation with cyber aesthetics
- Glowing accent elements and hover effects
- Terminal-inspired typography and spacing
- Neon green accent system throughout
- Matrix-style background patterns (subtle)

**Key Features:**
- Dark mode optimized for long coding sessions
- High contrast for accessibility in dark environments
- Cyber-punk inspired visual elements
- Terminal/console aesthetic touches
- Performance optimized dark theme

### 2. Navigation Component (Elite Hacker Style)

**Cyber Navigation Bar**
- Terminal-style brand with `</>` CodeXam logo
- Glowing green accent on active navigation items
- Sleek dark background with subtle borders
- User status with "online" indicator
- Hacker-style button designs

**Implementation Details:**
```html
<nav class="cyber-navbar" role="navigation" aria-label="Main navigation">
  <div class="navbar-container">
    <!-- Brand Section (Terminal Style) -->
    <div class="navbar-brand">
      <a href="/" class="brand-link">
        <span class="brand-icon">&lt;/&gt;</span>
        <span class="brand-text">CodeXam</span>
        <span class="brand-status">●</span>
      </a>
    </div>
    
    <!-- Navigation Links (Cyber Style) -->
    <div class="navbar-nav">
      <a href="/problems" class="nav-link" data-text="Problems">
        <span class="nav-icon">⚡</span>
        <span>Problems</span>
      </a>
      <a href="/submissions" class="nav-link" data-text="Submissions">
        <span class="nav-icon">📊</span>
        <span>Submissions</span>
      </a>
      <a href="/leaderboard" class="nav-link" data-text="Leaderboard">
        <span class="nav-icon">🏆</span>
        <span>Leaderboard</span>
      </a>
    </div>
    
    <!-- User Section (Hacker Style) -->
    <div class="navbar-user">
      <div class="user-info">
        <span class="user-status">●</span>
        <span class="user-name">{{ session.user_name or 'Anonymous' }}</span>
      </div>
      <button class="btn-cyber btn-sm">
        <span>Login</span>
        <span class="btn-glow"></span>
      </button>
    </div>
  </div>
</nav>

<style>
.cyber-navbar {
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  border-bottom: 1px solid var(--border-primary);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-primary);
  text-decoration: none;
  font-family: var(--font-mono);
  font-weight: 600;
}

.brand-icon {
  color: var(--accent-primary);
  font-size: 1.2rem;
  text-shadow: 0 0 10px var(--accent-glow);
}

.brand-status {
  color: var(--accent-primary);
  animation: pulse 2s infinite;
}

.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
  font-family: var(--font-sans);
}

.nav-link:hover,
.nav-link.active {
  color: var(--accent-primary);
  background: rgba(0, 255, 136, 0.1);
  box-shadow: 0 0 20px var(--accent-glow);
}

.btn-cyber {
  position: relative;
  background: transparent;
  border: 1px solid var(--accent-primary);
  color: var(--accent-primary);
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  font-family: var(--font-mono);
  font-size: 0.875rem;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
}

.btn-cyber:hover {
  background: var(--accent-primary);
  color: var(--bg-primary);
  box-shadow: 0 0 20px var(--accent-glow);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
```

### 3. Landing Page Design (Elite Coding Arena)

**Hero Section (Cyber Aesthetic)**
- "Elite Coding Arena" headline with glitch effects
- "The hardcore coding challenge engine for serious developers"
- Animated terminal-style text with typing effects
- Cyber-punk gradient background with floating code elements
- Glowing CTA button: "Initialize_Challenge()" 

**Statistics Dashboard (Hacker Style)**
```html
<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-value">500+</div>
    <div class="stat-label">ACTIVE PROBLEMS</div>
    <div class="stat-trend">↗ +20 from last month</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">2.5K</div>
    <div class="stat-label">DAILY USERS</div>
    <div class="stat-trend">↗ +15% from last week</div>
  </div>
</div>
```

**Feature Highlights (Elite Developer Arsenal)**
- **Clean Code Editor**: Built-in Python editor with syntax highlighting
- **Instant Evaluation**: Lightning-fast code execution engine
- **Skill Building**: Progress from beginner to advanced levels
- **Community Driven**: Learn from others and share solutions

**Terminal-Style Status Messages**
- `> System ready. Challenges loading...`
- `> Initialize_Challenge() →`
- `> System Status: ONLINE`

### 4. Problem List Interface (Problem Set Arena)

**Cyber Card Grid Layout**
- Dark cards with glowing borders on hover
- Difficulty badges with neon colors
- Problem completion checkmarks with green glow
- Hover effects with subtle animations

**Problem Card Component (Hacker Style):**
```html
<div class="problem-card cyber-card" role="article">
  <div class="card-glow"></div>
  
  <div class="problem-header">
    <div class="problem-status">
      {% if problem.completed %}
        <span class="status-icon completed">✓</span>
      {% else %}
        <span class="status-icon pending">○</span>
      {% endif %}
    </div>
    
    <h3 class="problem-title">
      <a href="/problem/{{ problem.id }}">{{ problem.title }}</a>
    </h3>
    
    <span class="difficulty-badge difficulty-{{ problem.difficulty.lower() }}">
      {{ problem.difficulty }}
    </span>
  </div>
  
  <p class="problem-description">{{ problem.description[:120] }}...</p>
  
  <div class="problem-tags">
    {% for tag in problem.tags %}
      <span class="tag">{{ tag }}</span>
    {% endfor %}
  </div>
  
  <div class="problem-stats">
    <div class="stat-item">
      <span class="stat-icon">👥</span>
      <span class="stat-value">{{ problem.solved_count }}</span>
      <span class="stat-label">solved</span>
    </div>
    <div class="stat-item">
      <span class="stat-icon">⚡</span>
      <span class="stat-value">{{ problem.avg_time }}</span>
      <span class="stat-label">avg</span>
    </div>
  </div>
  
  <div class="problem-actions">
    <button class="btn-cyber-primary">
      <span>Solve Challenge</span>
      <span class="btn-arrow">→</span>
    </button>
  </div>
</div>

<style>
.cyber-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 0.75rem;
  padding: 1.5rem;
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
}

.cyber-card:hover {
  border-color: var(--accent-primary);
  box-shadow: 0 8px 32px rgba(0, 255, 136, 0.2);
  transform: translateY(-4px);
}

.cyber-card:hover .card-glow {
  opacity: 1;
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.difficulty-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: var(--font-mono);
  text-transform: uppercase;
}

.difficulty-easy {
  background: rgba(0, 255, 136, 0.2);
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary);
}

.difficulty-medium {
  background: rgba(255, 165, 2, 0.2);
  color: #ffa502;
  border: 1px solid #ffa502;
}

.difficulty-hard {
  background: rgba(255, 71, 87, 0.2);
  color: #ff4757;
  border: 1px solid #ff4757;
}

.btn-cyber-primary {
  background: transparent;
  border: 1px solid var(--accent-primary);
  color: var(--accent-primary);
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-family: var(--font-mono);
  font-size: 0.875rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  width: 100%;
  justify-content: center;
}

.btn-cyber-primary:hover {
  background: var(--accent-primary);
  color: var(--bg-primary);
  box-shadow: 0 0 20px var(--accent-glow);
}
</style>
```

**Empty State Design (Hacker Theme)**
- Terminal-style ASCII art
- "No challenges loaded. Initialize_Arena()?"
- Glowing "Access All Challenges" button

### 5. Problem Detail Interface (Code Arena)

**Split-Pane Layout (IDE Style)**
- Left pane: Problem briefing with terminal-style formatting
- Right pane: Full IDE-like code editor with dark theme
- Resizable splitter with cyber-style handle
- Mobile: Tabbed interface with smooth transitions

**Problem Description Section (Mission Briefing):**
```html
<div class="problem-briefing">
  <div class="briefing-header">
    <div class="problem-meta">
      <span class="problem-id">#{{ problem.id }}</span>
      <h1 class="problem-title">{{ problem.title }}</h1>
      <span class="difficulty-badge difficulty-{{ problem.difficulty.lower() }}">
        {{ problem.difficulty }}
      </span>
    </div>
    
    <div class="problem-stats">
      <div class="stat">
        <span class="stat-label">Acceptance</span>
        <span class="stat-value">{{ problem.acceptance_rate }}%</span>
      </div>
      <div class="stat">
        <span class="stat-label">Submissions</span>
        <span class="stat-value">{{ problem.submission_count }}</span>
      </div>
    </div>
  </div>
  
  <div class="problem-content">
    <section class="problem-statement">
      <h3>Problem Statement</h3>
      <div class="statement-content">{{ problem.description | safe }}</div>
    </section>
    
    <section class="problem-examples">
      <h3>Examples</h3>
      <div class="example-block">
        <div class="example-header">Example 1:</div>
        <div class="code-block">
          <div class="code-label">Input:</div>
          <pre><code>{{ problem.sample_input }}</code></pre>
        </div>
        <div class="code-block">
          <div class="code-label">Output:</div>
          <pre><code>{{ problem.sample_output }}</code></pre>
        </div>
      </div>
    </section>
  </div>
</div>
```

**Code Editor Interface (Cyber IDE):**
```html
<div class="code-arena">
  <div class="editor-header">
    <div class="editor-tabs">
      <div class="tab active">
        <span class="tab-icon">📝</span>
        <span>solution.py</span>
      </div>
    </div>
    
    <div class="editor-controls">
      <select class="language-selector cyber-select">
        <option value="python">Python 3</option>
        <option value="javascript">JavaScript</option>
        <option value="java">Java</option>
        <option value="cpp">C++</option>
      </select>
      
      <button class="btn-cyber btn-sm" id="run-code">
        <span>▶ Run</span>
      </button>
    </div>
  </div>
  
  <div class="editor-container">
    <div class="line-numbers" id="line-numbers"></div>
    <textarea class="code-editor" id="code-input" spellcheck="false">
def solution(nums, target):
    # Your code here
    pass
    </textarea>
  </div>
  
  <div class="editor-footer">
    <div class="editor-info">
      <span class="language-info">Python 3</span>
      <span class="separator">•</span>
      <span class="line-info">Line 3, Col 9</span>
    </div>
    
    <button class="btn-cyber-primary btn-lg" id="submit-solution">
      <span>Submit Solution</span>
      <span class="submit-arrow">→</span>
    </button>
  </div>
</div>
```

**Result Display Component (Cyber Results):**
```html
<div class="submission-result result-{{ result.status.lower() }}" role="alert">
  <div class="result-header">
    <div class="result-status">
      {% if result.status == 'ACCEPTED' %}
        <span class="status-icon accepted">✓</span>
        <span class="status-text">Accepted</span>
      {% elif result.status == 'WRONG_ANSWER' %}
        <span class="status-icon wrong">✗</span>
        <span class="status-text">Wrong Answer</span>
      {% elif result.status == 'TIME_LIMIT_EXCEEDED' %}
        <span class="status-icon timeout">⏱</span>
        <span class="status-text">Time Limit Exceeded</span>
      {% endif %}
    </div>
  </div>
  
  <div class="result-metrics">
    <div class="metric-card">
      <div class="metric-icon">⚡</div>
      <div class="metric-label">Execution Time</div>
      <div class="metric-value">{{ result.execution_time }}ms</div>
    </div>
    
    <div class="metric-card">
      <div class="metric-icon">💾</div>
      <div class="metric-label">Memory Usage</div>
      <div class="metric-value">{{ result.memory_used }}MB</div>
    </div>
  </div>
  
  <div class="test-cases-progress">
    <div class="progress-header">
      <span>Test Cases Progress</span>
      <span class="progress-text">{{ result.passed_tests }}/{{ result.total_tests }} passed</span>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" style="width: {{ (result.passed_tests / result.total_tests * 100) }}%"></div>
    </div>
  </div>
</div>

<style>
.code-arena {
  background: var(--bg-accent);
  border: 1px solid var(--border-primary);
  border-radius: 0.75rem;
  overflow: hidden;
  font-family: var(--font-mono);
}

.editor-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.code-editor {
  background: var(--bg-accent);
  color: var(--text-primary);
  border: none;
  outline: none;
  font-family: var(--font-mono);
  font-size: 0.875rem;
  line-height: 1.5;
  padding: 1rem;
  resize: none;
  width: 100%;
  min-height: 400px;
}

.result-accepted {
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid var(--accent-primary);
}

.result-wrong {
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid #ff4757;
}

.result-timeout {
  background: rgba(255, 165, 2, 0.1);
  border: 1px solid #ffa502;
}
</style>
```

### 6. Submission History Interface

**Table-Based Layout**
- Responsive table that adapts to mobile screens
- Sortable columns (problem, language, status, date)
- Filterable by problem and result status
- Expandable rows for code preview

**Mobile Adaptations:**
- Card-based layout on small screens
- Collapsible details sections
- Touch-friendly interaction areas
- Horizontal scrolling for table data

**Empty State:**
- Motivational message for new users
- Direct link to browse problems
- Progress encouragement

### 7. Leaderboard Interface

**Podium Design**
- Special highlighting for top 3 performers
- Trophy icons and achievement badges
- User avatars (generated from initials)
- Animated ranking transitions

**Leaderboard List:**
- Ranked list with position indicators
- User statistics (problems solved, success rate)
- Current user highlighting
- Pagination for large user bases

**Responsive Design:**
- Horizontal scrolling on mobile
- Simplified statistics display
- Touch-friendly interaction areas

## Data Models

### Template Context Data

**Base Template Context:**
```python
{
    'user_name': session.get('user_name', 'Anonymous'),
    'current_page': request.endpoint,
    'flash_messages': get_flashed_messages(with_categories=True)
}
```

**Problem List Context:**
```python
{
    'problems': [
        {
            'id': int,
            'title': str,
            'description': str,
            'difficulty': str,  # Easy, Medium, Hard
            'solved_count': int,
            'avg_time': str,
            'created_at': datetime
        }
    ],
    'difficulty_filter': str,
    'total_count': int
}
```

**Problem Detail Context:**
```python
{
    'problem': {
        'id': int,
        'title': str,
        'description': str,
        'difficulty': str,
        'function_signatures': dict,  # Per language
        'sample_input': str,
        'sample_output': str,
        'constraints': list
    },
    'user_submissions': list,
    'supported_languages': list
}
```

**Submission History Context:**
```python
{
    'submissions': [
        {
            'id': int,
            'problem_title': str,
            'language': str,
            'result': str,  # PASS, FAIL, ERROR
            'execution_time': float,
            'submitted_at': datetime,
            'code_preview': str
        }
    ],
    'filter_problem': str,
    'filter_status': str,
    'total_count': int
}
```

**Leaderboard Context:**
```python
{
    'leaderboard': [
        {
            'rank': int,
            'user_name': str,
            'problems_solved': int,
            'total_submissions': int,
            'success_rate': float,
            'is_current_user': bool
        }
    ],
    'current_user_rank': int,
    'total_users': int
}
```

## Error Handling

### Template Error Handling

**Graceful Degradation:**
- Handle missing or null data gracefully
- Provide fallback content for empty states
- Display user-friendly error messages
- Maintain layout integrity during errors

**Error Display Patterns:**
```html
<!-- Graceful handling of missing data -->
{{ problem.title or 'Untitled Problem' }}

<!-- Safe iteration with fallbacks -->
{% for submission in submissions %}
  <!-- submission content -->
{% else %}
  <div class="empty-state">
    <p>No submissions yet. Start solving problems!</p>
  </div>
{% endfor %}

<!-- Error message display -->
{% if error_message %}
  <div class="alert alert-danger" role="alert">
    {{ error_message }}
  </div>
{% endif %}
```

### Form Validation

**Client-Side Validation:**
- HTML5 form validation attributes
- JavaScript validation for complex rules
- Real-time feedback during input
- Accessible error messaging

**Server-Side Integration:**
- Flask-WTF form integration
- CSRF protection on all forms
- Validation error display
- Form state preservation

## Testing Strategy

### Template Testing

**Unit Testing:**
- Template rendering with various data scenarios
- Error handling and edge cases
- Accessibility compliance testing
- Cross-browser compatibility

**Integration Testing:**
- End-to-end user workflows
- Form submission and validation
- AJAX interactions and responses
- Mobile device testing

**Performance Testing:**
- Page load times and optimization
- Large dataset rendering
- Mobile performance metrics
- Accessibility tool validation

## Security Considerations

### Template Security

**XSS Prevention:**
- Automatic escaping of user content
- Safe handling of HTML content
- CSRF token inclusion in forms
- Content Security Policy headers

**Data Sanitization:**
```html
<!-- Safe output of user content -->
{{ user_input | e }}

<!-- Safe HTML rendering when needed -->
{{ trusted_html | safe }}

<!-- CSRF protection in forms -->
<form method="POST">
  {{ csrf_token() }}
  <!-- form fields -->
</form>
```

### Accessibility Security

**Screen Reader Support:**
- Proper ARIA labels and roles
- Semantic HTML structure
- Focus management for dynamic content
- Alternative text for visual elements

**Keyboard Navigation:**
- Tab order management
- Skip links for main content
- Keyboard shortcuts for common actions
- Focus indicators for all interactive elements

## Performance Optimization

### Frontend Performance

**Asset Optimization:**
- Minified CSS and JavaScript
- Optimized images and icons
- CDN delivery for static assets
- Browser caching strategies

**Rendering Optimization:**
- Efficient Jinja2 template structure
- Minimal DOM manipulation
- Progressive enhancement approach
- Lazy loading for non-critical content

**Mobile Performance:**
- Touch-optimized interactions
- Reduced data usage
- Offline capability considerations
- Fast loading on slow connections

## Responsive Design Strategy

### Breakpoint System

**Mobile-First Approach:**
```css
/* Base styles for mobile */
.problem-card { /* mobile styles */ }

/* Tablet and up */
@media (min-width: 768px) {
  .problem-card { /* tablet styles */ }
}

/* Desktop and up */
@media (min-width: 992px) {
  .problem-card { /* desktop styles */ }
}
```

**Layout Adaptations:**
- Single column on mobile
- Two columns on tablet
- Three columns on desktop
- Flexible grid system

### Component Responsiveness

**Navigation:**
- Hamburger menu on mobile
- Full navigation on desktop
- Touch-friendly tap targets
- Accessible menu controls

**Code Editor:**
- Full-width on mobile
- Split-pane on desktop
- Resizable panels
- Touch-optimized controls

**Tables:**
- Horizontal scroll on mobile
- Card layout alternative
- Priority-based column hiding
- Touch-friendly sorting

## Implementation Timeline

### Phase 1: Foundation (Week 1)
- Base template and navigation
- CSS architecture setup
- Responsive framework implementation
- Accessibility foundation

### Phase 2: Core Pages (Week 2)
- Landing page implementation
- Problem list interface
- Basic styling and interactions
- Mobile responsiveness

### Phase 3: Advanced Features (Week 3)
- Problem detail with code editor
- Submission history interface
- Leaderboard implementation
- Advanced interactions

### Phase 4: Polish and Testing (Week 4)
- Cross-browser testing
- Accessibility compliance
- Performance optimization
- User experience refinement

This design provides a comprehensive foundation for implementing the CodeXam UI templates while maintaining consistency, accessibility, and performance across all platform features.