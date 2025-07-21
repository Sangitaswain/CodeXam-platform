# CodeXam Development Workflow

## Workflow Overview

This document defines the step-by-step process for implementing CodeXam platform features. Follow this workflow religiously to ensure consistency, quality, and adherence to specifications.

## Pre-Implementation Phase

### 1. Task Analysis and Planning
Before writing any code, complete these steps:

```markdown
## Task Preparation Checklist
- [ ] Read the complete task description in tasks.md
- [ ] Identify which requirements (1-9) are being addressed
- [ ] Check task dependencies and prerequisites
- [ ] Verify all prerequisite tasks are marked complete
- [ ] Understand the expected deliverable
- [ ] Note any risks or complexity warnings
- [ ] Estimate actual time needed vs. provided estimate
```

### 2. Documentation Review
Systematically review relevant documentation:

```markdown
## Documentation Review Checklist
- [ ] requirements.md - Understand the specific requirements being implemented
- [ ] design.md - Review architectural decisions and project structure
- [ ] ui_ux.md - Check UI/UX specifications (if implementing UI components)
- [ ] development-rules.md - Review coding standards and rules
- [ ] code-formatting.md - Understand formatting requirements
```

### 3. Environment Preparation
Set up your development environment:

```bash
# Verify project structure
ls -la  # Should match structure in design.md

# Check dependencies
pip list  # Verify required packages are installed

# Test database connection
python -c "import sqlite3; print('Database accessible')"

# Verify Flask app runs
python app.py  # Should start without errors
```

## Implementation Phase

### 4. Code Implementation Process

#### Step 4.1: Create Implementation Plan
Before coding, create a mini-plan:

```markdown
## Implementation Plan for Task X.Y
### Files to Create/Modify:
- [ ] app.py - Add new route
- [ ] models.py - Add new model class
- [ ] templates/new_template.html - Create UI template

### Implementation Order:
1. Database model changes
2. Backend logic implementation
3. Route handlers
4. Template creation
5. Static assets (CSS/JS)
6. Testing

### Potential Challenges:
- Security considerations for user input
- Database migration requirements
- UI responsiveness requirements
```

#### Step 4.2: Implement in Small Increments
Follow the "Red-Green-Refactor" approach:

```python
# Example: Implementing Problem model

# Step 1: Write failing test first
def test_create_problem():
    """Test problem creation with valid data."""
    problem = Problem.create(
        title="Two Sum",
        difficulty="Easy", 
        description="Find two numbers that add up to target"
    )
    assert problem.id is not None
    assert problem.title == "Two Sum"

# Step 2: Implement minimal code to pass test
class Problem:
    def __init__(self, title, difficulty, description):
        self.title = title
        self.difficulty = difficulty
        self.description = description
        self.id = None
    
    @classmethod
    def create(cls, title, difficulty, description):
        # Minimal implementation
        problem = cls(title, difficulty, description)
        problem.id = 1  # Temporary
        return problem

# Step 3: Refactor and improve
class Problem:
    def __init__(self, title, difficulty, description):
        self.title = title
        self.difficulty = difficulty
        self.description = description
        self.id = None
        self.created_at = None
    
    @classmethod
    def create(cls, title, difficulty, description):
        # Validate inputs
        cls._validate_difficulty(difficulty)
        cls._validate_title(title)
        
        # Create and save to database
        problem = cls(title, difficulty, description)
        problem._save_to_db()
        return problem
    
    @staticmethod
    def _validate_difficulty(difficulty):
        valid_levels = ['Easy', 'Medium', 'Hard']
        if difficulty not in valid_levels:
            raise ValueError(f"Invalid difficulty: {difficulty}")
    
    def _save_to_db(self):
        # Database implementation
        pass
```

#### Step 4.3: Follow Security-First Development
Always implement security measures from the start:

```python
# Example: Secure code submission handling

def handle_code_submission(request_data):
    """Handle code submission with security validation."""
    
    # Step 1: Input validation
    try:
        problem_id = int(request_data.get('problem_id'))
        code = request_data.get('code', '').strip()
        language = request_data.get('language', '').lower()
    except (ValueError, TypeError):
        raise ValidationError("Invalid input data")
    
    # Step 2: Security checks
    if len(code) > MAX_CODE_LENGTH:
        raise ValidationError("Code exceeds maximum length")
    
    if language not in SUPPORTED_LANGUAGES:
        raise ValidationError(f"Unsupported language: {language}")
    
    # Step 3: Sanitization
    code = sanitize_code_input(code)
    
    # Step 4: Rate limiting check
    if not check_rate_limit(get_user_id()):
        raise RateLimitError("Too many submissions")
    
    # Step 5: Execute with restrictions
    result = execute_code_safely(code, language, problem_id)
    
    return result

def sanitize_code_input(code):
    """Sanitize code input to prevent injection attacks."""
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        'import os',
        'import sys', 
        'import subprocess',
        '__import__',
        'eval(',
        'exec(',
        'open(',
        'file('
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code.lower():
            raise SecurityError(f"Dangerous pattern detected: {pattern}")
    
    return code
```

### 5. Testing Implementation

#### Step 5.1: Unit Testing
Write comprehensive unit tests:

```python
# test_problem_model.py
import pytest
from models import Problem
from exceptions import ValidationError

class TestProblemModel:
    """Test suite for Problem model."""
    
    def test_create_problem_valid_data(self):
        """Test creating problem with valid data."""
        problem = Problem.create(
            title="Two Sum",
            difficulty="Easy",
            description="Find two numbers that add up to target"
        )
        
        assert problem.id is not None
        assert problem.title == "Two Sum"
        assert problem.difficulty == "Easy"
        assert problem.created_at is not None
    
    def test_create_problem_invalid_difficulty(self):
        """Test creating problem with invalid difficulty."""
        with pytest.raises(ValidationError, match="Invalid difficulty"):
            Problem.create(
                title="Test Problem",
                difficulty="Invalid",
                description="Test description"
            )
    
    def test_create_problem_empty_title(self):
        """Test creating problem with empty title."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            Problem.create(
                title="",
                difficulty="Easy",
                description="Test description"
            )
    
    def test_create_problem_long_title(self):
        """Test creating problem with overly long title."""
        long_title = "x" * 101  # Assuming 100 char limit
        
        with pytest.raises(ValidationError, match="Title too long"):
            Problem.create(
                title=long_title,
                difficulty="Easy",
                description="Test description"
            )
```

#### Step 5.2: Integration Testing
Test component interactions:

```python
# test_problem_routes.py
import pytest
from app import create_app
from models import Problem

class TestProblemRoutes:
    """Test suite for problem-related routes."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app(testing=True)
        with app.test_client() as client:
            yield client
    
    def test_get_problems_list(self, client):
        """Test GET /problems returns problem list."""
        # Create test problems
        Problem.create("Problem 1", "Easy", "Description 1")
        Problem.create("Problem 2", "Medium", "Description 2")
        
        response = client.get('/problems')
        
        assert response.status_code == 200
        assert b'Problem 1' in response.data
        assert b'Problem 2' in response.data
        assert b'Easy' in response.data
        assert b'Medium' in response.data
    
    def test_get_problem_detail(self, client):
        """Test GET /problem/<id> returns problem details."""
        problem = Problem.create("Two Sum", "Easy", "Find two numbers...")
        
        response = client.get(f'/problem/{problem.id}')
        
        assert response.status_code == 200
        assert b'Two Sum' in response.data
        assert b'Easy' in response.data
        assert b'Find two numbers' in response.data
    
    def test_get_nonexistent_problem(self, client):
        """Test GET /problem/<id> with invalid ID returns 404."""
        response = client.get('/problem/99999')
        
        assert response.status_code == 404
```

#### Step 5.3: UI Testing (if applicable)
Test user interface components:

```python
# test_ui_components.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestProblemUI:
    """Test UI components for problem functionality."""
    
    @pytest.fixture
    def driver(self):
        """Create web driver for testing."""
        driver = webdriver.Chrome()  # Or Firefox, etc.
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_problem_card_display(self, driver):
        """Test problem card displays correctly."""
        driver.get('http://localhost:5000/problems')
        
        # Wait for problem cards to load
        problem_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "problem-card"))
        )
        
        assert len(problem_cards) > 0
        
        # Check first card structure
        first_card = problem_cards[0]
        title = first_card.find_element(By.CLASS_NAME, "problem-title")
        difficulty = first_card.find_element(By.CLASS_NAME, "difficulty-badge")
        
        assert title.text != ""
        assert difficulty.text in ["Easy", "Medium", "Hard"]
    
    def test_problem_card_click_navigation(self, driver):
        """Test clicking problem card navigates to detail page."""
        driver.get('http://localhost:5000/problems')
        
        # Click first problem card
        first_card = driver.find_element(By.CLASS_NAME, "problem-card")
        problem_link = first_card.find_element(By.CLASS_NAME, "problem-link")
        problem_title = problem_link.text
        
        problem_link.click()
        
        # Verify navigation to problem detail page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "problem-detail"))
        )
        
        page_title = driver.find_element(By.TAG_NAME, "h1").text
        assert page_title == problem_title
```

## Post-Implementation Phase

### 6. Code Review and Quality Assurance

#### Step 6.1: Self-Review Checklist
Before marking task complete, review your own code:

```markdown
## Self-Review Checklist
### Functionality
- [ ] Feature works as specified in requirements
- [ ] All edge cases are handled properly
- [ ] Error conditions return appropriate messages
- [ ] User input is validated and sanitized
- [ ] Security measures are implemented

### Code Quality
- [ ] Functions are small and focused (< 50 lines)
- [ ] No duplicate code exists
- [ ] Variable and function names are descriptive
- [ ] Code is properly commented
- [ ] Follows project structure guidelines

### Testing
- [ ] Unit tests cover main functionality
- [ ] Edge cases are tested
- [ ] Error conditions are tested
- [ ] Integration tests pass
- [ ] UI tests pass (if applicable)

### Documentation
- [ ] Code is properly documented
- [ ] Complex logic is explained
- [ ] API changes are documented
- [ ] README updated if needed

### UI/UX (if applicable)
- [ ] Matches specifications in ui_ux.md
- [ ] Responsive design works on mobile
- [ ] Accessibility requirements met
- [ ] Color contrast meets WCAG standards
- [ ] Keyboard navigation works properly
```

#### Step 6.2: Performance Review
Check for performance issues:

```python
# Example: Performance testing for database queries

import time
import pytest
from models import Problem, Submission

def test_problem_list_performance():
    """Test that problem list loads quickly even with many problems."""
    # Create many test problems
    for i in range(1000):
        Problem.create(f"Problem {i}", "Easy", f"Description {i}")
    
    start_time = time.time()
    problems = Problem.get_all()
    end_time = time.time()
    
    # Should load within 100ms
    assert (end_time - start_time) < 0.1
    assert len(problems) == 1000

def test_leaderboard_performance():
    """Test leaderboard calculation performance."""
    # Create test data
    for i in range(100):
        for j in range(10):
            Submission.create(
                problem_id=j+1,
                user_name=f"User{i}",
                code="test code",
                language="python",
                result="PASS"
            )
    
    start_time = time.time()
    leaderboard = Submission.get_leaderboard()
    end_time = time.time()
    
    # Should calculate within 200ms
    assert (end_time - start_time) < 0.2
    assert len(leaderboard) == 100
```

### 7. Documentation and Deployment Preparation

#### Step 7.1: Update Documentation
Ensure all documentation is current:

```markdown
## Documentation Update Checklist
- [ ] API documentation updated (if applicable)
- [ ] Database schema changes documented
- [ ] Configuration changes documented
- [ ] Deployment notes updated
- [ ] User guide updated (if applicable)
```

#### Step 7.2: Deployment Readiness
Prepare for deployment:

```bash
# Check requirements.txt is up to date
pip freeze > requirements.txt

# Run full test suite
python -m pytest tests/ -v

# Check for security vulnerabilities
pip audit

# Verify database migrations work
python init_db.py --test

# Test production configuration
FLASK_ENV=production python app.py --test
```

## Task Completion Protocol

### 8. Final Validation

#### Step 8.1: Requirement Verification
Verify each requirement is fully met:

```markdown
## Requirement Verification for Task X.Y
### Requirements Addressed: [List requirement numbers]

For each requirement:
- [ ] Requirement X.Y: [Description]
  - [ ] Acceptance criteria 1: [Status]
  - [ ] Acceptance criteria 2: [Status]
  - [ ] Acceptance criteria 3: [Status]
  - [ ] Testing: [Test coverage details]
  - [ ] Documentation: [Documentation status]
```

#### Step 8.2: Integration Testing
Test with existing system:

```python
# Example: Integration test for new feature
def test_complete_user_workflow():
    """Test complete user workflow with new feature."""
    # Test user can browse problems
    response = client.get('/problems')
    assert response.status_code == 200
    
    # Test user can view problem detail
    response = client.get('/problem/1')
    assert response.status_code == 200
    
    # Test user can submit code
    response = client.post('/submit', data={
        'problem_id': 1,
        'code': 'def solution(nums, target): return [0, 1]',
        'language': 'python'
    })
    assert response.status_code == 200
    
    # Test submission appears in history
    response = client.get('/submissions')
    assert response.status_code == 200
    assert b'PASS' in response.data
    
    # Test leaderboard is updated
    response = client.get('/leaderboard')
    assert response.status_code == 200
```

### 9. Task Completion

#### Step 9.1: Final Checklist
Complete this checklist before marking task as done:

```markdown
## Task Completion Checklist
- [ ] All functionality implemented as specified
- [ ] All tests pass (unit, integration, UI)
- [ ] Code follows project standards and rules
- [ ] Documentation is complete and accurate
- [ ] Security measures are implemented
- [ ] Performance requirements are met
- [ ] UI/UX matches specifications (if applicable)
- [ ] No regressions introduced
- [ ] Ready for production deployment
```

#### Step 9.2: Handoff Documentation
Create handoff documentation:

```markdown
## Task X.Y Completion Report

### Summary
Brief description of what was implemented.

### Files Modified/Created
- app.py: Added route for [functionality]
- models.py: Added [Model] class
- templates/[template].html: Created UI for [feature]

### Testing
- Unit tests: X tests added, all passing
- Integration tests: Y tests added, all passing
- Manual testing: Completed successfully

### Known Issues
- None / [List any known limitations]

### Next Steps
- [Any follow-up tasks or recommendations]

### Deployment Notes
- [Any special deployment considerations]
```

## Emergency Procedures

### When Things Go Wrong

#### Immediate Response
1. **Stop development** - Don't continue with broken code
2. **Document the issue** - What happened, when, why
3. **Assess impact** - What's broken, what still works
4. **Communicate** - Inform team of the issue

#### Recovery Process
1. **Revert to last working state** if necessary
2. **Analyze root cause** - Was it a rule violation?
3. **Plan fix** - How to resolve properly
4. **Implement fix** - Following all rules and procedures
5. **Test thoroughly** - Ensure fix doesn't break other things
6. **Document lessons learned** - Update rules if needed

#### Prevention
- **Commit frequently** - Small, working increments
- **Test continuously** - Don't accumulate untested changes
- **Follow rules strictly** - They exist to prevent problems
- **Ask for help** - When unsure about approach

Remember: **Quality over speed**. It's better to implement features correctly and thoroughly than to rush and create problems that require extensive debugging and rework later.