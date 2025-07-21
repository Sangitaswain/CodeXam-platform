# Project Structure

## Directory Organization

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
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── editor.js     # Code editor functionality
│   └── img/              # Images and icons
├── tests/                # Test suite
│   ├── test_judge.py     # Judge engine tests
│   ├── test_routes.py    # Web route tests
│   └── test_models.py    # Database model tests
└── .kiro/                # Kiro configuration
    ├── specs/            # Project specifications
    └── steering/         # AI assistant guidance
```

## Key File Responsibilities

### Core Application Files
- **app.py**: Flask app initialization, configuration, and startup
- **routes.py**: All URL endpoints and request handling logic
- **models.py**: Database schema and data access methods
- **judge.py**: Secure code execution for multiple languages
- **config.py**: Environment-specific settings and constants

### Database Files
- **init_db.py**: Creates database schema and tables
- **seed_problems.py**: Populates database with sample problems
- **reset_db.py**: Development utility to reset database state
- **database.db**: SQLite file (excluded from version control)

### Frontend Structure
- **templates/**: Server-rendered HTML with Jinja2 templating
- **static/css/**: Bootstrap + custom styles for responsive design
- **static/js/**: Client-side JavaScript for code editor and interactions

### Testing Organization
- **tests/**: Comprehensive test suite covering all components
- Unit tests for judge engine security and functionality
- Integration tests for web routes and database operations
- End-to-end tests for complete user workflows

## Naming Conventions

### Files and Directories
- Use lowercase with underscores: `test_judge.py`, `add_problem.html`
- Template files use descriptive names: `problem.html`, `submissions.html`
- Static assets organized by type: `css/`, `js/`, `img/`

### Python Code
- Classes use PascalCase: `Problem`, `SimpleJudge`, `SubmissionResult`
- Functions and variables use snake_case: `execute_code()`, `user_name`
- Constants use UPPER_CASE: `EXECUTION_TIMEOUT`, `SUPPORTED_LANGUAGES`

### Database
- Table names are lowercase plural: `problems`, `submissions`
- Column names use snake_case: `problem_id`, `submitted_at`
- Foreign keys follow pattern: `{table}_id`

### Templates and Routes
- Route names match template names: `/problems` → `problems.html`
- Template blocks use descriptive names: `{% block content %}`, `{% block scripts %}`
- CSS classes follow Bootstrap conventions with custom prefixes: `codexam-*`

## Configuration Management

### Environment-Specific Settings
- Development: SQLite database, debug mode enabled
- Testing: In-memory database, isolated test environment  
- Production: PostgreSQL, security headers, error logging

### Security Considerations
- Database files excluded from version control
- Secret keys stored in environment variables
- Code execution sandboxed with resource limits
- Input validation on all user-submitted data