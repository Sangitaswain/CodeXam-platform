# CodeXam Naming Conventions Guide

## Overview

This document establishes consistent naming conventions across the CodeXam platform to improve code readability, maintainability, and developer experience.

## Python Naming Conventions

### Functions and Variables
- **Format**: `snake_case`
- **Examples**: `get_user_data()`, `submission_count`, `validate_input()`

### Classes
- **Format**: `PascalCase`
- **Examples**: `Problem`, `Submission`, `DatabaseConnection`

### Constants
- **Format**: `UPPER_SNAKE_CASE`
- **Examples**: `MAX_CODE_LENGTH`, `DEFAULT_TIMEOUT`, `SUPPORTED_LANGUAGES`

### Private Methods/Variables
- **Format**: `_snake_case` (single underscore prefix)
- **Examples**: `_validate_input()`, `_connection_pool`

### Module-Level Private
- **Format**: `__snake_case` (double underscore prefix)
- **Examples**: `__version__`, `__author__`

## Database Naming Conventions

### Table Names
- **Format**: `snake_case` (plural)
- **Examples**: `problems`, `submissions`, `user_analytics`

### Column Names
- **Format**: `snake_case`
- **Examples**: `user_name`, `created_at`, `execution_time`

### Foreign Keys
- **Format**: `{table_name}_id`
- **Examples**: `problem_id`, `user_id`, `submission_id`

### Indexes
- **Format**: `idx_{table}_{column(s)}`
- **Examples**: `idx_submissions_user_name`, `idx_problems_difficulty`

## HTML/CSS Naming Conventions

### CSS Classes
- **Format**: `kebab-case` with BEM methodology
- **Examples**: `nav-link`, `btn-cyber-primary`, `problem-card__title`

### HTML IDs
- **Format**: `kebab-case`
- **Examples**: `main-content`, `user-profile`, `code-editor`

### CSS Custom Properties
- **Format**: `--kebab-case`
- **Examples**: `--accent-primary`, `--bg-secondary`, `--text-muted`

## JavaScript Naming Conventions

### Variables and Functions
- **Format**: `camelCase`
- **Examples**: `getUserData()`, `submissionCount`, `validateInput()`

### Constants
- **Format**: `UPPER_SNAKE_CASE`
- **Examples**: `MAX_RETRIES`, `API_ENDPOINT`, `DEFAULT_CONFIG`

### Classes
- **Format**: `PascalCase`
- **Examples**: `CodeXamApp`, `SystemInfoModal`, `FormValidator`

### Private Methods/Properties
- **Format**: `_camelCase` (single underscore prefix)
- **Examples**: `_initializeComponents()`, `_apiKey`

## Template Naming Conventions

### Template Files
- **Format**: `snake_case.html`
- **Examples**: `problem_detail.html`, `user_profile.html`, `admin_panel.html`

### Template Variables
- **Format**: `snake_case`
- **Examples**: `{{ user_name }}`, `{{ problem_list }}`, `{{ submission_count }}`

### Template Blocks
- **Format**: `snake_case`
- **Examples**: `{% block page_title %}`, `{% block extra_css %}`

## URL and Route Naming Conventions

### URL Patterns
- **Format**: `kebab-case`
- **Examples**: `/user-profile`, `/problem-detail`, `/admin-panel`

### Route Function Names
- **Format**: `snake_case`
- **Examples**: `problem_detail()`, `user_profile()`, `admin_dashboard()`

### URL Parameters
- **Format**: `snake_case`
- **Examples**: `problem_id`, `user_name`, `submission_id`

## File and Directory Naming

### Python Files
- **Format**: `snake_case.py`
- **Examples**: `models.py`, `form_validation.py`, `api_helpers.py`

### Static Asset Files
- **Format**: `kebab-case`
- **Examples**: `main.css`, `system-info-modal.js`, `clean-nav.css`

### Template Directories
- **Format**: `snake_case`
- **Examples**: `admin/`, `user_profile/`, `error_pages/`

## API and JSON Naming Conventions

### JSON Keys
- **Format**: `snake_case`
- **Examples**: `user_name`, `problem_id`, `execution_time`

### API Endpoints
- **Format**: `kebab-case`
- **Examples**: `/api/user-profile`, `/api/problem-list`, `/api/submit-code`

### HTTP Headers
- **Format**: `Kebab-Case`
- **Examples**: `Content-Type`, `X-Request-ID`, `Cache-Control`

## Configuration and Environment Variables

### Environment Variables
- **Format**: `UPPER_SNAKE_CASE`
- **Examples**: `DATABASE_URL`, `SECRET_KEY`, `JUDGE_TIMEOUT`

### Configuration Keys
- **Format**: `UPPER_SNAKE_CASE` or `snake_case`
- **Examples**: `DEBUG`, `database_url`, `judge_timeout`

## Error and Exception Naming

### Exception Classes
- **Format**: `PascalCase` ending with `Error`
- **Examples**: `ValidationError`, `DatabaseError`, `SecurityError`

### Error Codes
- **Format**: `UPPER_SNAKE_CASE`
- **Examples**: `INVALID_INPUT`, `DATABASE_CONNECTION_FAILED`, `TIMEOUT_ERROR`

## Testing Naming Conventions

### Test Files
- **Format**: `test_{module_name}.py`
- **Examples**: `test_models.py`, `test_routes.py`, `test_judge.py`

### Test Functions
- **Format**: `test_{functionality}__{condition}`
- **Examples**: `test_create_problem__valid_data()`, `test_submit_code__invalid_language()`

### Test Classes
- **Format**: `Test{ClassName}`
- **Examples**: `TestProblem`, `TestSubmission`, `TestJudgeEngine`

## Documentation Naming

### Documentation Files
- **Format**: `UPPER_SNAKE_CASE.md`
- **Examples**: `README.md`, `DEPLOYMENT.md`, `API_REFERENCE.md`

### Section Headers
- **Format**: `Title Case`
- **Examples**: `## Getting Started`, `### Database Configuration`

## Logging and Monitoring

### Logger Names
- **Format**: Module name (`__name__`)
- **Examples**: `models`, `routes`, `judge`

### Log Messages
- **Format**: Descriptive with context
- **Examples**: `"User {user_name} submitted code for problem {problem_id}"`

### Metric Names
- **Format**: `snake_case`
- **Examples**: `request_count`, `response_time`, `error_rate`

## Examples of Standardized Names

### Before (Inconsistent)
```python
# Mixed naming conventions
def getUserData(userId):
    user-name = get_user_name(userId)
    UserSubmissions = get_submissions(userId)
    return {"userName": user-name, "submissions": UserSubmissions}

# CSS classes
.userProfile { }
.User_Card { }
.user-profile-header { }
```

### After (Consistent)
```python
# Consistent snake_case for Python
def get_user_data(user_id):
    user_name = get_user_name(user_id)
    user_submissions = get_submissions(user_id)
    return {"user_name": user_name, "submissions": user_submissions}

# CSS classes with BEM methodology
.user-profile { }
.user-card { }
.user-profile__header { }
```

## Implementation Checklist

### Python Code
- [ ] Function names use `snake_case`
- [ ] Class names use `PascalCase`
- [ ] Constants use `UPPER_SNAKE_CASE`
- [ ] Private methods use `_snake_case`

### Database
- [ ] Table names are `snake_case` and plural
- [ ] Column names use `snake_case`
- [ ] Foreign keys follow `{table}_id` pattern
- [ ] Indexes follow `idx_{table}_{column}` pattern

### Frontend
- [ ] CSS classes use `kebab-case` with BEM
- [ ] HTML IDs use `kebab-case`
- [ ] JavaScript variables use `camelCase`
- [ ] JavaScript constants use `UPPER_SNAKE_CASE`

### Templates
- [ ] Template files use `snake_case.html`
- [ ] Template variables use `snake_case`
- [ ] URL patterns use `kebab-case`

### Configuration
- [ ] Environment variables use `UPPER_SNAKE_CASE`
- [ ] Configuration keys are consistent
- [ ] Error codes use `UPPER_SNAKE_CASE`

## Tools and Automation

### Linting Rules
- **Python**: Use `flake8` with naming conventions plugin
- **JavaScript**: Use `ESLint` with naming rules
- **CSS**: Use `stylelint` with naming conventions

### Pre-commit Hooks
- Validate naming conventions before commits
- Automatically format code according to standards
- Check for naming consistency across files

### IDE Configuration
- Configure IDE to highlight naming violations
- Set up auto-completion with naming standards
- Use code templates with consistent naming

## Migration Strategy

### Phase 1: New Code
- Apply naming conventions to all new code
- Use consistent naming in new features
- Document naming decisions

### Phase 2: Critical Paths
- Update naming in frequently used modules
- Standardize API endpoints and responses
- Fix database naming inconsistencies

### Phase 3: Complete Migration
- Systematically update all existing code
- Update documentation and comments
- Verify naming consistency across codebase

## Benefits of Consistent Naming

### Developer Experience
- Easier code navigation and understanding
- Reduced cognitive load when switching contexts
- Improved code completion and IDE support

### Maintainability
- Consistent patterns reduce bugs
- Easier refactoring and code changes
- Better code review process

### Team Collaboration
- Clear expectations for all developers
- Reduced time spent on naming decisions
- Improved code quality and consistency

## Conclusion

Consistent naming conventions are essential for maintaining a professional, readable, and maintainable codebase. By following these guidelines, the CodeXam platform will have improved developer experience, better code quality, and easier long-term maintenance.