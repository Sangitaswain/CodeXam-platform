# Component Library Documentation

## CodeXam UI Component Library

This document provides a comprehensive library of reusable UI components for the CodeXam platform. All components follow the "Elite Coding Arena" design system with cyber-punk aesthetics.

## Navigation Components

### Main Navigation

**File**: `templates/base.html`
**Class**: `.cyber-nav`

```html
<nav class="navbar navbar-expand-lg navbar-dark cyber-nav sticky-top">
    <div class="container">
        <a class="navbar-brand cyber-brand" href="{{ url_for('routes.index') }}">
            <span class="brand-icon">&lt;/&gt;</span>
            <span class="brand-text">CodeXam</span>
        </a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <a class="nav-link cyber-nav-link" href="{{ url_for('routes.index') }}">
                        <i class="fas fa-home"></i> Home
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link cyber-nav-link" href="{{ url_for('routes.problems') }}">
                        <i class="fas fa-code"></i> Problems
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link cyber-nav-link" href="{{ url_for('routes.leaderboard') }}">
                        <i class="fas fa-trophy"></i> Leaderboard
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link cyber-nav-link" href="{{ url_for('routes.submissions') }}">
                        <i class="fas fa-history"></i> Submissions
                    </a>
                </li>
            </ul>
            
            <div class="navbar-nav">
                <div class="nav-item user-status">
                    <span class="user-name">{{ session.user_name or 'Anonymous' }}</span>
                    <button class="btn btn-cyber-ghost btn-sm" data-bs-toggle="modal" data-bs-target="#nameModal">
                        <i class="fas fa-user"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
</nav>
```

**CSS**:
```css
.cyber-nav {
    background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
    border-bottom: 1px solid rgba(0, 255, 65, 0.2);
    backdrop-filter: blur(10px);
}

.cyber-brand {
    font-family: var(--font-mono);
    font-weight: 700;
    color: var(--cyber-primary);
    text-decoration: none;
}

.cyber-nav-link {
    color: var(--cyber-text-secondary);
    transition: all 0.3s ease;
    position: relative;
}

.cyber-nav-link:hover,
.cyber-nav-link.active {
    color: var(--cyber-primary);
}
```

### Breadcrumb Navigation

```html
<nav aria-label="breadcrumb" class="cyber-breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item">
            <a href="{{ url_for('routes.index') }}">Home</a>
        </li>
        <li class="breadcrumb-item">
            <a href="{{ url_for('routes.problems') }}">Problems</a>
        </li>
        <li class="breadcrumb-item active" aria-current="page">
            {{ problem.title }}
        </li>
    </ol>
</nav>
```

## Button Components

### Primary Button (`.btn-cyber`)

```html
<button class="btn btn-cyber">
    <i class="fas fa-play"></i>
    Start Challenge
</button>
```

**CSS**:
```css
.btn-cyber {
    background: linear-gradient(135deg, var(--cyber-primary), var(--cyber-secondary));
    color: var(--cyber-bg-primary);
    border: 1px solid var(--cyber-primary);
    font-family: var(--font-mono);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
    transition: all 0.3s ease;
}

.btn-cyber:hover {
    box-shadow: 0 0 20px rgba(0, 255, 65, 0.6);
    transform: translateY(-2px);
}
```

### Secondary Button (`.btn-cyber-outline`)

```html
<button class="btn btn-cyber-outline">
    <i class="fas fa-filter"></i>
    Filter
</button>
```

### Ghost Button (`.btn-cyber-ghost`)

```html
<button class="btn btn-cyber-ghost">
    <i class="fas fa-user"></i>
</button>
```

### Loading Button State

```html
<button class="btn btn-cyber" id="submitBtn" disabled>
    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
    Submitting...
</button>
```

## Card Components

### Problem Card

```html
<div class="col-lg-4 col-md-6 mb-4">
    <div class="cyber-card problem-card h-100">
        <div class="card-header d-flex justify-content-between align-items-start">
            <h5 class="card-title mb-0">{{ problem.title }}</h5>
            <span class="badge status-{{ problem.difficulty.lower() }}">
                {{ problem.difficulty }}
            </span>
        </div>
        <div class="card-body">
            <p class="card-text text-muted">
                {{ problem.description[:100] }}...
            </p>
            <div class="problem-stats d-flex justify-content-between">
                <small class="text-muted">
                    <i class="fas fa-users"></i>
                    {{ problem.solved_count }} solved
                </small>
                <small class="text-muted">
                    <i class="fas fa-code"></i>
                    {{ problem.total_submissions }} submissions
                </small>
            </div>
        </div>
        <div class="card-footer">
            <a href="{{ url_for('routes.problem', id=problem.id) }}" 
               class="btn btn-cyber btn-sm w-100">
                <i class="fas fa-play"></i>
                Start Challenge
            </a>
        </div>
    </div>
</div>
```

### Statistics Card

```html
<div class="col-md-3 mb-4">
    <div class="cyber-card stat-card text-center">
        <div class="stat-icon">
            <i class="fas fa-code-branch"></i>
        </div>
        <div class="stat-number" data-count="{{ total_problems }}">0</div>
        <div class="stat-label">Total Problems</div>
    </div>
</div>
```

### Result Card

```html
<div class="cyber-card result-card">
    <div class="result-header d-flex justify-content-between align-items-center">
        <span class="result-status status-passed">
            <i class="fas fa-check-circle"></i>
            Passed
        </span>
        <span class="result-time">
            <i class="fas fa-clock"></i>
            0.23s
        </span>
    </div>
    <div class="result-body">
        <pre class="result-output">All test cases passed successfully!</pre>
    </div>
</div>
```

## Form Components

### Input Field

```html
<div class="form-group mb-3">
    <label for="username" class="form-label">Username</label>
    <input type="text" 
           class="cyber-input" 
           id="username" 
           name="username" 
           placeholder="Enter username"
           required>
    <div class="form-text">Choose a unique username for the arena</div>
</div>
```

### Select Dropdown

```html
<div class="form-group mb-3">
    <label for="language" class="form-label">Programming Language</label>
    <select class="cyber-select" id="language" name="language" required>
        <option value="">Select Language</option>
        <option value="python">Python</option>
        <option value="javascript">JavaScript</option>
        <option value="java">Java</option>
        <option value="cpp">C++</option>
    </select>
</div>
```

### Textarea (Code Editor)

```html
<div class="form-group mb-3">
    <label for="code" class="form-label">Your Solution</label>
    <textarea class="cyber-textarea code-input" 
              id="code" 
              name="code"
              rows="15" 
              placeholder="# Write your code here..."
              spellcheck="false"
              required></textarea>
    <div class="form-text">Use Ctrl+Enter to submit your solution</div>
</div>
```

### Filter Form

```html
<form class="filter-form mb-4" method="GET">
    <div class="row g-3 align-items-end">
        <div class="col-md-4">
            <label for="difficulty" class="form-label">Difficulty</label>
            <select class="cyber-select" id="difficulty" name="difficulty">
                <option value="">All Difficulties</option>
                <option value="Easy" {{ 'selected' if difficulty_filter == 'Easy' }}>Easy</option>
                <option value="Medium" {{ 'selected' if difficulty_filter == 'Medium' }}>Medium</option>
                <option value="Hard" {{ 'selected' if difficulty_filter == 'Hard' }}>Hard</option>
            </select>
        </div>
        <div class="col-md-6">
            <label for="search" class="form-label">Search Problems</label>
            <input type="text" 
                   class="cyber-input" 
                   id="search" 
                   name="search" 
                   placeholder="Search by title..."
                   value="{{ search_query or '' }}">
        </div>
        <div class="col-md-2">
            <button type="submit" class="btn btn-cyber w-100">
                <i class="fas fa-search"></i>
                Filter
            </button>
        </div>
    </div>
</form>
```

## Status Components

### Difficulty Badges

```html
<span class="badge status-easy">Easy</span>
<span class="badge status-medium">Medium</span>
<span class="badge status-hard">Hard</span>
```

### Submission Status Badges

```html
<span class="badge status-passed">
    <i class="fas fa-check-circle"></i>
    Passed
</span>

<span class="badge status-failed">
    <i class="fas fa-times-circle"></i>
    Failed
</span>

<span class="badge status-pending">
    <i class="fas fa-clock"></i>
    Pending
</span>
```

### User Status Indicator

```html
<div class="user-status d-flex align-items-center">
    <div class="status-dot online"></div>
    <span class="user-name">{{ session.user_name or 'Anonymous' }}</span>
</div>
```

## Table Components

### Submissions Table

```html
<div class="table-responsive">
    <table class="table table-dark cyber-table">
        <thead>
            <tr>
                <th>Problem</th>
                <th>Language</th>
                <th>Status</th>
                <th>Time</th>
                <th>Submitted</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for submission in submissions %}
            <tr class="submission-row">
                <td>
                    <a href="{{ url_for('routes.problem', id=submission.problem_id) }}" 
                       class="text-decoration-none">
                        {{ submission.problem.title }}
                    </a>
                </td>
                <td>
                    <span class="badge bg-secondary">{{ submission.language.title() }}</span>
                </td>
                <td>
                    <span class="badge status-{{ submission.status.lower() }}">
                        {{ submission.status }}
                    </span>
                </td>
                <td>{{ submission.execution_time }}s</td>
                <td>{{ submission.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                <td>
                    <button class="btn btn-cyber-ghost btn-sm" 
                            onclick="toggleCode({{ submission.id }})">
                        <i class="fas fa-code"></i>
                        View Code
                    </button>
                </td>
            </tr>
            <tr class="code-preview" id="code-{{ submission.id }}" style="display: none;">
                <td colspan="6">
                    <pre class="code-display"><code>{{ submission.code }}</code></pre>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

### Leaderboard Table

```html
<div class="table-responsive">
    <table class="table table-dark cyber-table">
        <thead>
            <tr>
                <th>Rank</th>
                <th>User</th>
                <th>Problems Solved</th>
                <th>Total Submissions</th>
                <th>Success Rate</th>
            </tr>
        </thead>
        <tbody>
            {% for user in users %}
            <tr class="{{ 'current-user' if user.name == session.user_name }}">
                <td>
                    <span class="rank-badge rank-{{ loop.index }}">
                        {{ loop.index }}
                    </span>
                </td>
                <td>
                    <div class="user-info d-flex align-items-center">
                        <div class="user-avatar">{{ user.name[0].upper() }}</div>
                        <span class="user-name">{{ user.name }}</span>
                    </div>
                </td>
                <td>{{ user.problems_solved }}</td>
                <td>{{ user.total_submissions }}</td>
                <td>{{ user.success_rate }}%</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

## Modal Components

### Name Setting Modal

```html
<div class="modal fade" id="nameModal" tabindex="-1" aria-labelledby="nameModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content cyber-modal">
            <div class="modal-header">
                <h5 class="modal-title" id="nameModalLabel">Set Your Arena Name</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <form action="{{ url_for('routes.set_name') }}" method="POST">
                <div class="modal-body">
                    <div class="form-group">
                        <label for="name" class="form-label">Choose your hacker alias:</label>
                        <input type="text" 
                               class="cyber-input" 
                               id="name" 
                               name="name" 
                               value="{{ session.user_name or '' }}" 
                               placeholder="Enter your arena name"
                               required>
                        <div class="form-text">
                            This name will appear on the leaderboard and submissions
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-cyber-outline" data-bs-dismiss="modal">
                        Cancel
                    </button>
                    <button type="submit" class="btn btn-cyber">
                        <i class="fas fa-save"></i>
                        Save Name
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
```

## Layout Components

### Hero Section

```html
<section class="hero-section">
    <div class="container">
        <div class="row justify-content-center text-center">
            <div class="col-lg-8">
                <h1 class="hero-title">
                    <span class="typing-text" data-text="Welcome to the Elite Coding Arena">
                        Welcome to the Elite Coding Arena
                    </span>
                </h1>
                <p class="hero-subtitle">
                    Master algorithms, solve challenges, dominate the leaderboard
                </p>
                <div class="hero-actions">
                    <a href="{{ url_for('routes.problems') }}" class="btn btn-cyber btn-lg">
                        <i class="fas fa-rocket"></i>
                        Initialize_Challenge()
                    </a>
                </div>
            </div>
        </div>
    </div>
</section>
```

### Statistics Section

```html
<section class="stats-section">
    <div class="container">
        <div class="row">
            <div class="col-md-3 mb-4">
                <div class="cyber-card stat-card text-center">
                    <div class="stat-icon">
                        <i class="fas fa-code-branch"></i>
                    </div>
                    <div class="stat-number" data-count="{{ total_problems }}">0</div>
                    <div class="stat-label">Total Problems</div>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="cyber-card stat-card text-center">
                    <div class="stat-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="stat-number" data-count="{{ total_users }}">0</div>
                    <div class="stat-label">Active Coders</div>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="cyber-card stat-card text-center">
                    <div class="stat-icon">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <div class="stat-number" data-count="{{ total_solutions }}">0</div>
                    <div class="stat-label">Solutions Submitted</div>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="cyber-card stat-card text-center">
                    <div class="stat-icon">
                        <i class="fas fa-trophy"></i>
                    </div>
                    <div class="stat-number" data-count="{{ challenges_completed }}">0</div>
                    <div class="stat-label">Challenges Completed</div>
                </div>
            </div>
        </div>
    </div>
</section>
```

### Split Layout (Problem Detail)

```html
<div class="problem-container">
    <div class="problem-description">
        <div class="cyber-card">
            <div class="card-header">
                <h2>{{ problem.title }}</h2>
                <span class="badge status-{{ problem.difficulty.lower() }}">
                    {{ problem.difficulty }}
                </span>
            </div>
            <div class="card-body">
                <div class="problem-content">
                    {{ problem.description | safe }}
                </div>
                <div class="problem-examples">
                    <h4>Examples</h4>
                    {% for example in problem.examples %}
                    <div class="example">
                        <strong>Input:</strong>
                        <pre><code>{{ example.input }}</code></pre>
                        <strong>Output:</strong>
                        <pre><code>{{ example.output }}</code></pre>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
    
    <div class="code-editor">
        <div class="cyber-card">
            <div class="card-header">
                <h4>Code Editor</h4>
                <select class="cyber-select" id="languageSelect">
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="java">Java</option>
                    <option value="cpp">C++</option>
                </select>
            </div>
            <div class="card-body">
                <textarea class="cyber-textarea code-input" 
                          id="codeInput" 
                          placeholder="# Write your code here..."
                          spellcheck="false"></textarea>
                <button class="btn btn-cyber w-100 mt-3" onclick="submitCode()">
                    <i class="fas fa-play"></i>
                    Run Code
                </button>
            </div>
        </div>
    </div>
</div>
```

## Loading Components

### Loading Spinner

```html
<div class="loading-spinner">
    <div class="spinner-border text-success" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
</div>
```

### Progress Bar

```html
<div class="progress cyber-progress">
    <div class="progress-bar" 
         role="progressbar" 
         style="width: 75%" 
         aria-valuenow="75" 
         aria-valuemin="0" 
         aria-valuemax="100">
        75%
    </div>
</div>
```

### Skeleton Loading

```html
<div class="skeleton-loader">
    <div class="skeleton-line"></div>
    <div class="skeleton-line short"></div>
    <div class="skeleton-line"></div>
    <div class="skeleton-line medium"></div>
</div>
```

## Empty State Components

### No Problems Found

```html
<div class="empty-state text-center py-5">
    <div class="empty-icon">
        <i class="fas fa-search"></i>
    </div>
    <h3>No Problems Found</h3>
    <p class="text-muted">
        Try adjusting your search criteria or browse all problems
    </p>
    <a href="{{ url_for('routes.problems') }}" class="btn btn-cyber">
        <i class="fas fa-code"></i>
        Browse All Problems
    </a>
</div>
```

### No Submissions Yet

```html
<div class="empty-state text-center py-5">
    <div class="empty-icon">
        <i class="fas fa-code"></i>
    </div>
    <h3>No Submissions Yet</h3>
    <p class="text-muted">
        Start solving problems to see your submission history here
    </p>
    <a href="{{ url_for('routes.problems') }}" class="btn btn-cyber">
        <i class="fas fa-rocket"></i>
        Start Coding
    </a>
</div>
```

## JavaScript Integration

### Component Initialization

```javascript
// Initialize all components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCounters();
    initializeTypingAnimation();
    initializeCodeEditor();
    initializeFormValidation();
});

// Counter animation for statistics
function initializeCounters() {
    const counters = document.querySelectorAll('.stat-number[data-count]');
    counters.forEach(counter => {
        const target = parseInt(counter.dataset.count);
        animateCounter(counter, target);
    });
}

function animateCounter(element, target) {
    let current = 0;
    const increment = target / 100;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 20);
}
```

This component library provides all the necessary building blocks for creating consistent, accessible, and visually appealing interfaces in the CodeXam platform while maintaining the cyber-punk aesthetic and elite coding arena theme.
