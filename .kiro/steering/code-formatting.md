# Code Formatting and Autofix Rules

## Autofix Policy

### NEVER Auto-format These Files
- **Configuration files**: `config.py`, `.env`, `requirements.txt`
- **Database files**: `init_db.py`, `seed_problems.py`, `reset_db.py`
- **Template files**: All `.html` files in `templates/`
- **Static files**: CSS, JavaScript files in `static/`
- **Test files**: Files in `tests/` directory
- **Documentation**: All `.md` files

### Manual Formatting Only
When working with the above files, always:
1. **Format manually** according to project standards
2. **Preserve existing structure** and indentation
3. **Maintain consistency** with established patterns
4. **Ask before making** formatting changes

## Code Style Guidelines

### Python Code Standards (PEP 8 Compliant)

#### Import Organization
```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
from flask import Flask, request, jsonify
import pytest

# Local application imports
from models import Problem, Submission
from judge import SimpleJudge
from config import Config
```

#### Function and Class Definitions
```python
class Problem:
    """Represents a coding problem with test cases."""
    
    def __init__(self, title: str, difficulty: str, description: str):
        """Initialize a new problem.
        
        Args:
            title: The problem title
            difficulty: Problem difficulty (Easy, Medium, Hard)
            description: Detailed problem description
        """
        self.title = title
        self.difficulty = difficulty
        self.description = description
    
    def validate(self) -> bool:
        """Validate problem data.
        
        Returns:
            True if valid, raises ValueError if invalid
        """
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Problem title cannot be empty")
        
        valid_difficulties = ['Easy', 'Medium', 'Hard']
        if self.difficulty not in valid_difficulties:
            raise ValueError(f"Invalid difficulty: {self.difficulty}")
        
        return True
```

#### Variable and Function Naming
```python
# GOOD: Clear, descriptive names
def calculate_submission_score(submission_time: float, memory_used: int) -> int:
    """Calculate score based on performance metrics."""
    base_score = 100
    time_penalty = min(submission_time * 0.1, 20)
    memory_penalty = min(memory_used / 1024 / 1024, 10)
    
    final_score = base_score - time_penalty - memory_penalty
    return max(int(final_score), 0)

# BAD: Unclear, abbreviated names
def calc_score(t, m):
    s = 100 - t * 0.1 - m / 1024 / 1024
    return max(int(s), 0)
```

### HTML Template Standards

#### Jinja2 Template Structure
```html
<!-- Base template structure -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CodeXam{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="{{ url_for('static', filename='css/bootstrap.min.css') }}" rel="stylesheet">
    <!-- Custom CSS -->
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    {% include 'partials/navbar.html' %}
    
    <!-- Flash messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container mt-3">
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}
    
    <!-- Main content -->
    <main class="container my-4">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    {% include 'partials/footer.html' %}
    
    <!-- Bootstrap JS -->
    <script src="{{ url_for('static', filename='js/bootstrap.min.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### Form Structure
```html
<!-- Problem creation form -->
<form method="POST" action="{{ url_for('admin.add_problem') }}" class="needs-validation" novalidate>
    {{ csrf_token() }}
    
    <div class="row">
        <div class="col-md-8">
            <div class="mb-3">
                <label for="title" class="form-label">Problem Title</label>
                <input type="text" 
                       class="form-control" 
                       id="title" 
                       name="title" 
                       required
                       maxlength="100"
                       value="{{ request.form.get('title', '') }}">
                <div class="invalid-feedback">
                    Please provide a valid problem title.
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="mb-3">
                <label for="difficulty" class="form-label">Difficulty</label>
                <select class="form-select" id="difficulty" name="difficulty" required>
                    <option value="">Choose difficulty...</option>
                    <option value="Easy" {{ 'selected' if request.form.get('difficulty') == 'Easy' }}>Easy</option>
                    <option value="Medium" {{ 'selected' if request.form.get('difficulty') == 'Medium' }}>Medium</option>
                    <option value="Hard" {{ 'selected' if request.form.get('difficulty') == 'Hard' }}>Hard</option>
                </select>
                <div class="invalid-feedback">
                    Please select a difficulty level.
                </div>
            </div>
        </div>
    </div>
    
    <div class="mb-3">
        <label for="description" class="form-label">Problem Description</label>
        <textarea class="form-control" 
                  id="description" 
                  name="description" 
                  rows="8" 
                  required
                  placeholder="Describe the problem in detail...">{{ request.form.get('description', '') }}</textarea>
        <div class="invalid-feedback">
            Please provide a problem description.
        </div>
    </div>
    
    <div class="d-flex justify-content-between">
        <a href="{{ url_for('admin.dashboard') }}" class="btn btn-secondary">Cancel</a>
        <button type="submit" class="btn btn-primary">Create Problem</button>
    </div>
</form>
```

### CSS Standards

#### Custom Property Usage
```css
/* ALWAYS use CSS custom properties from ui_ux.md */
:root {
    /* Use established color system */
    --codexam-primary: #007bff;
    --codexam-success: #28a745;
    --codexam-danger: #dc3545;
    
    /* Use established spacing system */
    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-4: 1rem;
    --space-6: 1.5rem;
}

/* Component styles using custom properties */
.problem-card {
    background: var(--codexam-white);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: var(--space-6);
    margin-bottom: var(--space-4);
    transition: all 0.15s ease;
}

.problem-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
    border-color: var(--codexam-primary-light);
}

/* Difficulty badges */
.difficulty-easy {
    background-color: var(--difficulty-easy-bg);
    color: var(--difficulty-easy);
}

.difficulty-medium {
    background-color: var(--difficulty-medium-bg);
    color: var(--difficulty-medium);
}

.difficulty-hard {
    background-color: var(--difficulty-hard-bg);
    color: var(--difficulty-hard);
}
```

#### Responsive Design Patterns
```css
/* Mobile-first responsive design */
.problems-grid {
    display: grid;
    gap: var(--space-4);
    grid-template-columns: 1fr;
}

@media (min-width: 576px) {
    .problems-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (min-width: 992px) {
    .problems-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}

/* Code editor responsive behavior */
.code-editor-container {
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    overflow: hidden;
}

@media (max-width: 767.98px) {
    .code-editor-container {
        margin: 0 calc(-1 * var(--space-4));
        border-radius: 0;
        border-left: none;
        border-right: none;
    }
    
    .code-input {
        font-size: 16px; /* Prevent zoom on iOS */
        min-height: 250px;
    }
}
```

### JavaScript Standards

#### Module Organization
```javascript
// editor.js - Code editor functionality
const CodeEditor = {
    // Configuration
    config: {
        themes: ['light', 'dark'],
        languages: ['python', 'javascript', 'java', 'cpp'],
        defaultLanguage: 'python'
    },
    
    // State management
    state: {
        currentLanguage: 'python',
        currentTheme: 'light',
        isModified: false
    },
    
    // Initialization
    init: function() {
        this.setupLanguageSelector();
        this.setupEditor();
        this.setupEventListeners();
        this.loadUserPreferences();
    },
    
    // Language management
    setLanguage: function(language) {
        if (!this.config.languages.includes(language)) {
            console.error(`Unsupported language: ${language}`);
            return false;
        }
        
        this.state.currentLanguage = language;
        this.updateEditorTemplate();
        this.updateSyntaxHighlighting();
        this.saveUserPreferences();
        
        return true;
    },
    
    // Template management
    updateEditorTemplate: function() {
        const templates = {
            python: 'def solution(nums, target):\n    pass',
            javascript: 'function solution(nums, target) {\n    // Your code here\n}',
            java: 'public int[] solution(int[] nums, int target) {\n    // Your code here\n}',
            cpp: 'vector<int> solution(vector<int>& nums, int target) {\n    // Your code here\n}'
        };
        
        const template = templates[this.state.currentLanguage];
        if (template && !this.state.isModified) {
            document.getElementById('code-editor').value = template;
        }
    },
    
    // Event handling
    setupEventListeners: function() {
        // Language selector change
        document.getElementById('language-select').addEventListener('change', (e) => {
            this.setLanguage(e.target.value);
        });
        
        // Code editor change
        document.getElementById('code-editor').addEventListener('input', (e) => {
            this.state.isModified = true;
            this.updateLineCount();
        });
        
        // Submit button
        document.getElementById('submit-code').addEventListener('click', (e) => {
            e.preventDefault();
            this.submitCode();
        });
        
        // Reset button
        document.getElementById('reset-code').addEventListener('click', (e) => {
            e.preventDefault();
            this.resetCode();
        });
    },
    
    // Code submission
    submitCode: function() {
        const code = document.getElementById('code-editor').value.trim();
        const language = this.state.currentLanguage;
        const problemId = document.getElementById('problem-id').value;
        
        if (!code) {
            this.showError('Please write some code before submitting.');
            return;
        }
        
        // Show loading state
        this.setSubmitButtonLoading(true);
        
        // Submit via AJAX
        fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                problem_id: problemId,
                code: code,
                language: language
            })
        })
        .then(response => response.json())
        .then(data => {
            this.handleSubmissionResult(data);
        })
        .catch(error => {
            this.showError('Submission failed. Please try again.');
            console.error('Submission error:', error);
        })
        .finally(() => {
            this.setSubmitButtonLoading(false);
        });
    },
    
    // Result handling
    handleSubmissionResult: function(data) {
        const resultContainer = document.getElementById('result-container');
        
        // Clear previous results
        resultContainer.innerHTML = '';
        resultContainer.className = 'submission-result';
        
        if (data.status === 'PASS') {
            this.showPassResult(data, resultContainer);
        } else if (data.status === 'FAIL') {
            this.showFailResult(data, resultContainer);
        } else if (data.status === 'ERROR') {
            this.showErrorResult(data, resultContainer);
        }
        
        // Scroll to results
        resultContainer.scrollIntoView({ behavior: 'smooth' });
        
        // Announce to screen readers
        this.announceResult(data.status);
    },
    
    // Utility functions
    getCSRFToken: function() {
        return document.querySelector('meta[name=csrf-token]').getAttribute('content');
    },
    
    announceResult: function(status) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = `Submission result: ${status}`;
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    CodeEditor.init();
});
```

## File Organization Standards

### Directory Structure Compliance
```
CodeXam/
├── app.py                    # Main application entry point
├── routes.py                 # URL routing (keep under 500 lines)
├── models.py                 # Database models (keep under 400 lines)
├── judge.py                  # Code execution engine (keep under 300 lines)
├── config.py                 # Configuration (keep under 100 lines)
├── requirements.txt          # Dependencies (alphabetically sorted)
├── init_db.py               # Database initialization
├── seed_problems.py         # Sample data
├── reset_db.py              # Database reset utility
├── templates/               # Jinja2 templates
│   ├── base.html           # Base template
│   ├── index.html          # Landing page
│   ├── problems.html       # Problem list
│   ├── problem.html        # Problem detail
│   ├── submissions.html    # Submission history
│   ├── leaderboard.html    # User rankings
│   └── admin/              # Admin templates
│       └── add_problem.html
├── static/                  # Static assets
│   ├── css/
│   │   ├── bootstrap.min.css
│   │   └── style.css       # Custom styles (organized by component)
│   ├── js/
│   │   ├── bootstrap.min.js
│   │   └── editor.js       # Code editor functionality
│   └── img/                # Images and icons
└── tests/                   # Test suite
    ├── test_judge.py       # Judge engine tests
    ├── test_routes.py      # Route tests
    └── test_models.py      # Model tests
```

### File Size Limits
- **Python files**: Maximum 500 lines
- **Template files**: Maximum 300 lines
- **CSS files**: Maximum 1000 lines
- **JavaScript files**: Maximum 800 lines

### Code Organization Within Files
```python
# Standard file organization for Python modules

"""
Module docstring explaining purpose and usage.
"""

# Imports (organized as shown above)
import os
from typing import Dict, List

from flask import Flask
from models import Problem

# Constants
MAX_CODE_LENGTH = 10000
SUPPORTED_LANGUAGES = ['python', 'javascript', 'java', 'cpp']
DEFAULT_TIMEOUT = 5

# Classes (if any)
class SimpleJudge:
    """Code execution engine with security restrictions."""
    pass

# Functions (organized by functionality)
def validate_input(data):
    """Input validation functions."""
    pass

def process_submission(submission):
    """Submission processing functions."""
    pass

def format_result(result):
    """Result formatting functions."""
    pass

# Main execution (if applicable)
if __name__ == '__main__':
    main()
```

## Quality Assurance Checklist

### Before Committing Code
- [ ] **No autofix applied** to restricted file types
- [ ] **Manual formatting** follows project standards
- [ ] **File size limits** respected
- [ ] **Naming conventions** followed
- [ ] **Import organization** correct
- [ ] **Documentation** complete and accurate
- [ ] **Error handling** implemented
- [ ] **Tests written** and passing
- [ ] **Security considerations** addressed
- [ ] **Accessibility requirements** met (for UI components)

### Code Review Points
1. **Readability**: Is the code easy to understand?
2. **Maintainability**: Can it be easily modified later?
3. **Performance**: Are there any obvious inefficiencies?
4. **Security**: Are there any security vulnerabilities?
5. **Testing**: Is the code adequately tested?
6. **Documentation**: Is the code properly documented?
7. **Standards**: Does it follow project conventions?

Remember: **Consistency is key**. Follow established patterns and maintain the same style throughout the codebase.