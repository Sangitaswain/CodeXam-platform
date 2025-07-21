# Design Document

## Overview

CodeXam is designed as a cost-conscious, scalable coding challenge platform that starts completely free for development and can grow incrementally. The architecture follows a progressive enhancement approach - beginning with simple, local solutions and evolving to production-grade infrastructure as needed.

**Design Philosophy:**
- Start simple and free ($0 cost)
- Build with scalability in mind
- Progressive enhancement approach
- Minimize external dependencies initially

## Architecture

### Phase 1: Free MVP Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Flask Server   │◄──►│  SQLite Database│
│                 │    │                  │    │                 │
│ - HTML/CSS/JS   │    │ - Routes         │    │ - Problems      │
│ - Code Editor   │    │ - Judge Engine   │    │ - Submissions   │
│ - Results UI    │    │ - Session Mgmt   │    │ - Users         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Phase 2: Scalable Production Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Flask Server   │◄──►│  PostgreSQL DB  │
│                 │    │                  │    │                 │
│ - React/Vue     │    │ - API Routes     │    │ - Normalized    │
│ - Monaco Editor │    │ - Auth System    │    │   Schema        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Judge Service   │
                       │                  │
                       │ - Docker/Judge0  │
                       │ - Multi-language │
                       │ - Sandboxing     │
                       └──────────────────┘
```

## Components and Interfaces

### 1. Web Application Layer

**Technology Stack (Phase 1):**
- **Backend**: Flask (Python) - lightweight, free
- **Frontend**: HTML + Jinja2 templates + Bootstrap CSS
- **Code Editor**: HTML textarea (Phase 1) → CodeMirror (Phase 2)

**Key Components:**
- `app.py`: Main Flask application
- `routes.py`: URL routing and view logic
- `templates/`: HTML templates with Jinja2
- `static/`: CSS, JavaScript, and assets

**Route Structure:**
```python
# Core routes addressing requirements
@app.route('/')                    # Landing page with platform introduction
@app.route('/problems')            # Problem list (Req 1)
@app.route('/problem/<int:id>')    # Problem details (Req 2)
@app.route('/submit', methods=['POST'])  # Code submission (Req 4)
@app.route('/submissions')         # Submission history (Req 5)
@app.route('/leaderboard')         # User rankings (Req 8)
@app.route('/set_name', methods=['POST'])  # User identification (Req 7)
@app.route('/admin/add_problem', methods=['GET', 'POST'])  # Problem management (Req 9)
```

**Frontend Components:**
- **Problem List Page**: Displays all problems with title, difficulty, and brief description (Req 1)
- **Problem Detail Page**: Shows complete problem description, examples, and code editor (Req 2, 3)
- **Code Editor Interface**: Multi-language support with syntax highlighting and templates (Req 3)
- **Submission Results**: Instant feedback display with PASS/FAIL/ERROR status (Req 4)
- **Submission History**: User's past attempts with timestamps and results (Req 5)
- **Leaderboard**: Rankings based on problems solved (Req 8)
- **User Name Prompt**: Simple identification system (Req 7)
- **Admin Interface**: Problem creation and management (Req 9)

### 2. Judge Engine

**Design Rationale**: The judge engine is designed with a two-phase approach to balance cost and security. Phase 1 uses restricted execution for development while Phase 2 implements proper sandboxing for production use.

**Phase 1 Implementation (Development - Addresses Req 6 basic security):**
```python
class SimpleJudge:
    SUPPORTED_LANGUAGES = ['python', 'javascript', 'java', 'cpp']
    EXECUTION_TIMEOUT = 5  # seconds
    MEMORY_LIMIT = 128 * 1024 * 1024  # 128MB
    
    def execute_code(self, language, code, test_cases):
        """Execute code with basic security restrictions (Req 6)"""
        if language == 'python':
            return self._execute_python(code, test_cases)
        elif language == 'javascript':
            return self._execute_javascript(code, test_cases)
        # Add other languages as needed
        
    def _execute_python(self, code, test_cases):
        """Python execution with restricted globals (Req 6)"""
        # Restricted environment prevents file/network access
        safe_globals = self._get_safe_python_globals()
        # Enforce time and memory limits
        return self._run_with_limits(code, test_cases, safe_globals)
        
    def _execute_javascript(self, code, test_cases):
        """JavaScript execution via subprocess (Req 6)"""
        # Use Node.js with restricted permissions
        # Timeout and resource limits enforced
```

**Phase 2 Implementation (Production - Full Req 6 compliance):**
```python
class ProductionJudge:
    def execute_code(self, language, code, test_cases):
        """Secure multi-language execution (Req 6)"""
        # Option A: Docker containers with resource limits
        # Option B: Judge0 API integration
        # Option C: AWS Lambda functions with sandboxing
        
        container_config = {
            'memory_limit': '128m',
            'cpu_limit': '0.5',
            'network': 'none',  # No network access
            'read_only': True,  # Read-only filesystem
            'timeout': 5
        }
        
        return self._execute_in_container(language, code, test_cases, container_config)
```

### 3. Database Layer

**Phase 1: SQLite (Free)**
```sql
-- Simple, file-based database
-- Perfect for development and small deployments
-- No server setup required
```

**Phase 2: PostgreSQL (Scalable)**
```sql
-- Managed database service
-- Better performance and concurrent access
-- Backup and scaling features
```

### 4. User Management

**Phase 1: Session-based (Simple)**
- Store username in browser session
- No passwords or authentication
- Perfect for MVP and demos

**Phase 2: Full Authentication (Optional)**
- User registration and login
- Password hashing
- Session management
- OAuth integration (GitHub, Google)

## Data Models

### Core Entities

```python
# Problem Model
class Problem:
    id: int
    title: str
    description: str
    difficulty: str  # Easy, Medium, Hard
    function_signature: dict  # Per language
    test_cases: list
    sample_input: str
    sample_output: str
    created_at: datetime

# Submission Model  
class Submission:
    id: int
    problem_id: int
    user_name: str
    language: str
    code: str
    result: str  # PASS, FAIL, ERROR
    execution_time: float
    memory_used: int
    submitted_at: datetime

# User Model (Phase 2)
class User:
    id: int
    username: str
    display_name: str
    problems_solved: int
    total_submissions: int
    created_at: datetime
```

### Database Schema (SQLite → PostgreSQL)

```sql
-- Problems table
CREATE TABLE problems (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    function_signatures TEXT, -- JSON string
    test_cases TEXT,          -- JSON string
    sample_input TEXT,
    sample_output TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Submissions table
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER REFERENCES problems(id),
    user_name TEXT NOT NULL,
    language TEXT NOT NULL,
    code TEXT NOT NULL,
    result TEXT NOT NULL,
    execution_time REAL,
    memory_used INTEGER,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Error Handling

### Code Execution Errors

```python
class JudgeResult:
    PASS = "PASS"
    FAIL = "FAIL" 
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"

def handle_execution_error(error):
    if isinstance(error, SyntaxError):
        return f"🛑 ERROR: Syntax error - {error.msg}"
    elif isinstance(error, TimeoutError):
        return f"🛑 ERROR: Code execution timed out"
    elif isinstance(error, MemoryError):
        return f"🛑 ERROR: Memory limit exceeded"
    else:
        return f"🛑 ERROR: {str(error)}"
```

### Web Application Errors

- 404: Problem not found
- 500: Server execution errors
- 400: Invalid code submission
- 429: Rate limiting (Phase 2)

## Testing Strategy

### Phase 1: Basic Testing
```python
# Unit tests for judge engine
def test_simple_addition():
    code = "def solution(a, b): return a + b"
    result = judge.execute_python(code, [(2, 3)], [5])
    assert result == "PASS"

# Integration tests for web routes
def test_problem_submission():
    response = client.post('/submit', data={
        'problem_id': 1,
        'code': 'def solution(a, b): return a + b',
        'language': 'python'
    })
    assert response.status_code == 200
```

### Phase 2: Comprehensive Testing
- Load testing with multiple concurrent users
- Security testing for code injection
- Performance testing for different languages
- End-to-end browser testing

## Security Considerations

### Phase 1: Basic Security (Development)
```python
# Restricted globals for Python exec()
SAFE_GLOBALS = {
    '__builtins__': {
        'len': len,
        'range': range,
        'int': int,
        'str': str,
        'list': list,
        'dict': dict,
        # No file operations, imports, etc.
    }
}

def execute_python_safely(code, test_cases):
    local_vars = {}
    exec(code, SAFE_GLOBALS, local_vars)
    # Execute with limited scope
```

### Phase 2: Production Security
- Docker containers with resource limits
- Network isolation for code execution
- Input sanitization and validation
- Rate limiting and abuse prevention
- HTTPS encryption
- SQL injection prevention

## Deployment Strategy

### Phase 1: Free Deployment Options

**Option A: Local Development**
```bash
# Run locally for development and demos
python app.py
# Access at http://localhost:5000
```

**Option B: Heroku Free Tier**
```bash
# Deploy to Heroku for free hosting
git push heroku main
# Includes PostgreSQL addon (free tier)
```

**Option C: Vercel/Netlify**
```bash
# Static site deployment for frontend
# Backend API on separate service
```

### Phase 2: Production Deployment

**Option A: DigitalOcean Droplet ($5/month)**
- Single server deployment
- Docker containers for isolation
- Managed PostgreSQL database

**Option B: AWS/GCP with Auto-scaling**
- Elastic Beanstalk or App Engine
- Managed database services
- CDN for static assets

## Performance Optimization

### Phase 1: Basic Optimization
- SQLite with proper indexing
- Simple caching for problem data
- Minimal JavaScript for better loading

### Phase 2: Advanced Optimization
- Database connection pooling
- Redis caching layer
- CDN for static assets
- Horizontal scaling with load balancers

## Cost Progression Plan

### Development Phase: $0/month
- Local SQLite database
- Python exec() for code execution
- Basic HTML/CSS interface
- GitHub for version control

### MVP Phase: $0-5/month
- Heroku free tier or DigitalOcean droplet
- PostgreSQL (managed or self-hosted)
- Simple Docker containers

### Growth Phase: $20-50/month
- Dedicated hosting with auto-scaling
- Judge0 API or advanced sandboxing
- Monitoring and analytics tools
- Custom domain and SSL

## Project Structure and Organization

### Root Directory Structure

```
CodeXam/
├── app.py                 # Main Flask application entry point
├── routes.py              # URL routing and view logic
├── models.py              # Database models (Problem, Submission)
├── judge.py               # Code execution engine
├── config.py              # Application configuration
├── requirements.txt       # Python dependencies
├── init_db.py            # Database initialization script
├── seed_problems.py      # Sample problem data loader
├── reset_db.py           # Database reset utility
├── database.db           # SQLite database file (gitignored)
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Landing page
│   ├── problems.html     # Problem list page
│   ├── problem.html      # Problem detail with code editor
│   ├── submissions.html  # Submission history
│   ├── leaderboard.html  # User rankings
│   └── admin/
│       └── add_problem.html  # Admin problem creation
├── static/               # Static assets
│   ├── css/
│   │   ├── bootstrap.min.css  # Bootstrap framework
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   ├── bootstrap.min.js   # Bootstrap JavaScript
│   │   ├── codemirror.min.js  # Code editor library
│   │   └── editor.js     # Code editor functionality
│   └── img/              # Images and icons
│       ├── logo.png      # Platform logo
│       └── favicon.ico   # Browser favicon
├── tests/                # Test suite
│   ├── __init__.py       # Test package initialization
│   ├── conftest.py       # pytest configuration and fixtures
│   ├── test_judge.py     # Judge engine tests
│   ├── test_routes.py    # Web route tests
│   ├── test_models.py    # Database model tests
│   └── test_integration.py # End-to-end tests
├── .gitignore            # Git ignore patterns
├── .env.example          # Environment variables template
└── README.md             # Project documentation
```

### Core Application Files

#### `app.py` - Application Entry Point
- Flask application initialization and configuration
- Database connection setup
- Route registration and middleware configuration
- Development server startup logic
- Environment-specific settings loading

#### `routes.py` - URL Routing and Views
- All HTTP endpoint definitions
- Request handling and response generation
- Session management for user identification
- Form processing and validation
- Integration with models and judge engine

#### `models.py` - Database Models
- Problem class with CRUD operations
- Submission class for tracking attempts
- Database schema definitions
- Data validation and serialization methods
- Query helpers and relationship management

#### `judge.py` - Code Execution Engine
- Multi-language code execution (Python, JavaScript, Java, C++)
- Security restrictions and sandboxing
- Resource limit enforcement (memory, time)
- Test case evaluation and result generation
- Error handling and logging

#### `config.py` - Application Configuration
- Environment-specific settings (development, testing, production)
- Database connection strings
- Security configurations (secret keys, CORS)
- Judge engine parameters (timeouts, memory limits)
- Feature flags and toggles

### Database Files

#### `init_db.py` - Database Initialization
- Creates database schema and tables
- Sets up indexes for performance
- Initializes default data if needed
- Handles database migrations

#### `seed_problems.py` - Sample Data Loader
- Populates database with sample coding problems
- Creates test cases and expected outputs
- Sets up initial user data for demonstration
- Configurable data sets for different environments

#### `reset_db.py` - Development Utility
- Drops and recreates database tables
- Useful for development and testing
- Includes safety checks to prevent accidental production use

### Frontend Structure

#### Templates Directory (`templates/`)
- **Base Template (`base.html`)**:
  - Common HTML structure and navigation
  - Bootstrap CSS and JavaScript includes
  - Responsive meta tags and viewport settings
  - Flash message display system

- **Landing Page (`index.html`)**:
  - Hero section with platform introduction
  - Feature highlights and call-to-action
  - Platform statistics display
  - Getting started guide

- **Problem List (`problems.html`)**:
  - Filterable and sortable problem list
  - Difficulty level indicators
  - Problem completion status
  - Search functionality

- **Problem Detail (`problem.html`)**:
  - Problem description and examples
  - Multi-language code editor
  - Language selection dropdown
  - Submit button and result display

- **Submission History (`submissions.html`)**:
  - User's past submission attempts
  - Filterable by problem and result
  - Code preview and expandable details
  - Performance metrics

- **Leaderboard (`leaderboard.html`)**:
  - User rankings by problems solved
  - Pagination for large user bases
  - Achievement badges and statistics
  - User profile links

- **Admin Templates (`admin/`)**:
  - Problem creation and editing forms
  - Test case management interface
  - User management tools
  - System statistics dashboard

#### Static Assets (`static/`)

**CSS Directory (`css/`)**:
- `bootstrap.min.css`: Bootstrap framework for responsive design
- `style.css`: Custom styles for CodeXam branding and components
- Organized with CSS custom properties for theming
- Mobile-first responsive design principles

**JavaScript Directory (`js/`)**:
- `bootstrap.min.js`: Bootstrap interactive components
- `codemirror.min.js`: Code editor with syntax highlighting
- `editor.js`: Custom code editor functionality and language switching
- AJAX submission handling and real-time feedback

**Images Directory (`img/`)**:
- `logo.png`: Platform logo in multiple sizes
- `favicon.ico`: Browser tab icon
- Difficulty level icons and status indicators
- Optimized for web performance

### Testing Organization

#### Test Structure (`tests/`)
- **`conftest.py`**: pytest configuration, fixtures, and test database setup
- **`test_judge.py`**: Unit tests for code execution engine
  - Security restriction testing
  - Multi-language execution verification
  - Resource limit enforcement
  - Error handling scenarios

- **`test_routes.py`**: Integration tests for web endpoints
  - HTTP request/response testing
  - Session management verification
  - Form submission handling
  - Authentication and authorization

- **`test_models.py`**: Database model testing
  - CRUD operation verification
  - Data validation testing
  - Relationship integrity checks
  - Query performance testing

- **`test_integration.py`**: End-to-end workflow testing
  - Complete user journey testing
  - Cross-component integration
  - Performance and load testing
  - Browser automation tests

## File Naming Conventions

### Python Files
- **Modules**: lowercase with underscores (`test_judge.py`, `seed_problems.py`)
- **Classes**: PascalCase (`Problem`, `SimpleJudge`, `SubmissionResult`)
- **Functions**: snake_case (`execute_code()`, `get_user_submissions()`)
- **Constants**: UPPER_CASE (`EXECUTION_TIMEOUT`, `SUPPORTED_LANGUAGES`)

### Templates and Static Files
- **Templates**: lowercase with descriptive names (`problem.html`, `submissions.html`)
- **CSS Classes**: kebab-case with prefixes (`codexam-header`, `problem-card`)
- **JavaScript**: camelCase for functions (`submitCode()`, `updateEditor()`)
- **Images**: descriptive names with size indicators (`logo-small.png`)

### Database Conventions
- **Tables**: lowercase plural (`problems`, `submissions`, `users`)
- **Columns**: snake_case (`problem_id`, `submitted_at`, `execution_time`)
- **Indexes**: descriptive with table prefix (`idx_problems_difficulty`)
- **Foreign Keys**: `{table}_id` pattern (`problem_id`, `user_id`)

## Configuration Management

### Environment-Specific Settings

#### Development Environment
```python
# config.py - Development
DEBUG = True
DATABASE_URL = 'sqlite:///database.db'
SECRET_KEY = 'dev-secret-key'
JUDGE_TIMEOUT = 5
JUDGE_MEMORY_LIMIT = 128 * 1024 * 1024
```

#### Testing Environment
```python
# config.py - Testing
TESTING = True
DATABASE_URL = 'sqlite:///:memory:'
WTF_CSRF_ENABLED = False
JUDGE_TIMEOUT = 2
```

#### Production Environment
```python
# config.py - Production
DEBUG = False
DATABASE_URL = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')
JUDGE_TIMEOUT = 10
SECURITY_HEADERS = True
```

### Asset Organization

#### CSS Architecture
```css
/* style.css organization */
:root {
  /* CSS Custom Properties */
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
}

/* Base styles */
/* Component styles */
/* Utility classes */
/* Responsive overrides */
```

#### JavaScript Module Organization
```javascript
// editor.js - Code editor functionality
const CodeEditor = {
  init: function() { /* Initialize editor */ },
  setLanguage: function(lang) { /* Switch language */ },
  submit: function() { /* Submit code */ },
  showResult: function(result) { /* Display result */ }
};
```

## Build and Deployment Structure

### Development Setup
```bash
# Local development commands
pip install -r requirements.txt
python init_db.py
python seed_problems.py
python app.py
```

### Testing Commands
```bash
# Test execution
python -m pytest tests/
python -m pytest --cov=app tests/
python -m pytest tests/test_judge.py -v
```

### Deployment Preparation
```bash
# Production deployment
pip freeze > requirements.txt
python -m pytest
python init_db.py --production
gunicorn app:app
```

### Environment Variables
```bash
# .env file structure
FLASK_ENV=development
DATABASE_URL=sqlite:///database.db
SECRET_KEY=your-secret-key-here
JUDGE_TIMEOUT=5
JUDGE_MEMORY_LIMIT=134217728
```

## Security Considerations

### File Permissions
- Database files: Read/write for application only
- Configuration files: Restricted access to sensitive data
- Static assets: Public read access
- Log files: Restricted access with rotation

### Code Organization Security
- Sensitive configuration in environment variables
- Database credentials never in source code
- Judge engine isolated from main application
- Input validation at multiple layers

### Deployment Security
- HTTPS enforcement in production
- Security headers configuration
- Database connection encryption
- Regular dependency updates

This comprehensive design supports both rapid development and production scalability while maintaining clear separation of concerns and following Flask best practices. The project structure enables immediate development start with zero cost while providing a clear path to scale as the platform grows and generates value.