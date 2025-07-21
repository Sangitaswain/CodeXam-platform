# CodeXam Development Rules

## Primary Directive
You are implementing the CodeXam platform following established specifications. Maintain consistency, quality, and adherence to documented standards throughout the development process.

## Critical Rules - NEVER/ALWAYS

### Documentation Compliance
- **NEVER** skip documentation consultation before implementing any feature
- **NEVER** ignore project structure guidelines defined in design.md
- **NEVER** implement UI components without checking ui_ux.md specifications
- **NEVER** proceed with tasks without reading requirements.md context
- **ALWAYS** reference the specific requirement numbers when implementing features
- **ALWAYS** follow the established workflow process defined in tasks.md
- **ALWAYS** document errors and solutions for future reference

### Code Quality Standards
- **NEVER** write large monolithic code blocks (keep functions under 50 lines)
- **NEVER** create duplicate code - use DRY (Don't Repeat Yourself) principles
- **NEVER** implement features without proper error handling
- **NEVER** skip input validation and sanitization
- **ALWAYS** write modular, reusable code components
- **ALWAYS** include comprehensive docstrings and comments
- **ALWAYS** follow Python PEP 8 style guidelines

### Testing and Validation
- **NEVER** mark tasks complete without proper testing
- **NEVER** commit code that breaks existing functionality
- **NEVER** skip security validation for user inputs
- **ALWAYS** write unit tests for new functions
- **ALWAYS** test edge cases and error conditions
- **ALWAYS** validate against the original requirements

## Code Implementation Guidelines

### File Size and Complexity Management
```python
# GOOD: Small, focused functions
def validate_problem_difficulty(difficulty):
    """Validate problem difficulty level."""
    valid_levels = ['Easy', 'Medium', 'Hard']
    if difficulty not in valid_levels:
        raise ValueError(f"Invalid difficulty: {difficulty}")
    return difficulty

# BAD: Large, complex functions
def process_everything(data):
    # 100+ lines of mixed logic
    pass
```

### Modular Code Structure
- **Maximum function length**: 50 lines
- **Maximum file length**: 500 lines
- **Single responsibility**: Each function should do one thing well
- **Clear naming**: Use descriptive variable and function names

### Code Organization Principles
```python
# GOOD: Organized imports and clear structure
from flask import Flask, request, jsonify
from models import Problem, Submission
from judge import SimpleJudge

def create_submission(problem_id, code, language):
    """Create and evaluate a code submission."""
    # Validate inputs
    problem = Problem.get_by_id(problem_id)
    if not problem:
        raise ValueError("Problem not found")
    
    # Execute code
    judge = SimpleJudge()
    result = judge.execute_code(language, code, problem.test_cases)
    
    # Store submission
    submission = Submission.create(
        problem_id=problem_id,
        code=code,
        language=language,
        result=result
    )
    
    return submission

# BAD: Everything in one place
def handle_submission():
    # Mixed validation, execution, and storage logic
    pass
```

## Documentation Reference Workflow

### Before Starting Any Task
1. **Read the task description** in tasks.md thoroughly
2. **Check dependencies** - ensure prerequisite tasks are complete
3. **Review requirements** - understand which requirements are being addressed
4. **Consult design.md** - understand architectural decisions
5. **Check ui_ux.md** - if implementing UI components
6. **Verify project structure** - ensure files are placed correctly

### During Implementation
1. **Follow naming conventions** defined in design.md
2. **Use established patterns** from existing codebase
3. **Implement error handling** as specified in design.md
4. **Add appropriate logging** for debugging and monitoring
5. **Write tests** alongside implementation code

### After Implementation
1. **Test functionality** against requirements
2. **Verify UI matches** specifications in ui_ux.md
3. **Check code quality** against these rules
4. **Update documentation** if needed
5. **Mark task complete** only when fully tested

## Security and Validation Rules

### Input Validation (Critical for Judge Engine)
```python
# ALWAYS validate user inputs
def validate_code_submission(code, language):
    """Validate code submission before execution."""
    if not code or not code.strip():
        raise ValueError("Code cannot be empty")
    
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    
    if len(code) > MAX_CODE_LENGTH:
        raise ValueError("Code exceeds maximum length")
    
    return True

# NEVER trust user input directly
def execute_user_code(code, language):
    # BAD: Direct execution without validation
    exec(code)  # DANGEROUS!
    
    # GOOD: Validated and sandboxed execution
    validate_code_submission(code, language)
    return secure_execute(code, language)
```

### Database Security
```python
# ALWAYS use parameterized queries
def get_problem_by_id(problem_id):
    """Get problem by ID with SQL injection protection."""
    query = "SELECT * FROM problems WHERE id = ?"
    return db.execute(query, (problem_id,)).fetchone()

# NEVER use string formatting for SQL
def bad_query(problem_id):
    # BAD: SQL injection vulnerability
    query = f"SELECT * FROM problems WHERE id = {problem_id}"
    return db.execute(query).fetchone()
```

## Error Handling and Logging

### Comprehensive Error Handling
```python
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def safe_execute_code(code: str, language: str) -> Dict[str, Any]:
    """Safely execute user code with comprehensive error handling."""
    try:
        # Validate inputs
        validate_code_submission(code, language)
        
        # Execute with timeout and resource limits
        result = judge.execute_code(language, code, test_cases)
        
        logger.info(f"Code execution successful: {language}")
        return {"status": "success", "result": result}
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return {"status": "error", "message": str(e)}
        
    except TimeoutError as e:
        logger.warning(f"Code execution timeout: {e}")
        return {"status": "timeout", "message": "Code execution timed out"}
        
    except Exception as e:
        logger.error(f"Unexpected error in code execution: {e}")
        return {"status": "error", "message": "Internal server error"}
```

### Error Documentation
- **Log all errors** with appropriate severity levels
- **Include context** - what was being attempted when error occurred
- **Provide user-friendly messages** - don't expose internal details
- **Track error patterns** - for debugging and improvement

## UI/UX Implementation Rules

### Component Development
```html
<!-- ALWAYS follow ui_ux.md specifications -->
<div class="problem-card" role="article" aria-labelledby="problem-title-1">
  <div class="problem-header">
    <h3 class="problem-title" id="problem-title-1">
      <a href="/problem/1" class="problem-link">Two Sum</a>
    </h3>
    <span class="difficulty-badge difficulty-easy" aria-label="Difficulty: Easy">
      Easy
    </span>
  </div>
  <!-- Follow exact structure from ui_ux.md -->
</div>
```

### CSS Implementation
```css
/* ALWAYS use CSS custom properties from ui_ux.md */
.problem-card {
  background: var(--codexam-white);
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  padding: var(--space-6);
  /* Follow exact specifications */
}

/* NEVER hardcode colors or spacing */
.bad-card {
  background: #ffffff;  /* BAD: Should use var(--codexam-white) */
  padding: 24px;        /* BAD: Should use var(--space-6) */
}
```

### Accessibility Compliance
- **ALWAYS include ARIA labels** for screen readers
- **ALWAYS ensure keyboard navigation** works properly
- **ALWAYS test color contrast** meets WCAG 2.1 AA standards
- **ALWAYS provide alternative text** for images
- **NEVER rely solely on color** to convey information

## Testing Requirements

### Unit Testing Standards
```python
import pytest
from unittest.mock import Mock, patch

class TestProblemModel:
    """Test cases for Problem model."""
    
    def test_create_problem_valid_data(self):
        """Test creating problem with valid data."""
        problem_data = {
            'title': 'Two Sum',
            'difficulty': 'Easy',
            'description': 'Find two numbers that add up to target'
        }
        
        problem = Problem.create(**problem_data)
        
        assert problem.title == 'Two Sum'
        assert problem.difficulty == 'Easy'
        assert problem.id is not None
    
    def test_create_problem_invalid_difficulty(self):
        """Test creating problem with invalid difficulty."""
        problem_data = {
            'title': 'Test Problem',
            'difficulty': 'Invalid',  # Should raise error
            'description': 'Test description'
        }
        
        with pytest.raises(ValueError, match="Invalid difficulty"):
            Problem.create(**problem_data)
```

### Integration Testing
```python
def test_complete_submission_workflow(client):
    """Test complete user submission workflow."""
    # Create test problem
    problem = create_test_problem()
    
    # Submit code
    response = client.post('/submit', data={
        'problem_id': problem.id,
        'code': 'def solution(nums, target): return [0, 1]',
        'language': 'python'
    })
    
    # Verify response
    assert response.status_code == 200
    assert 'PASS' in response.get_json()['result']
    
    # Verify submission stored
    submissions = Submission.get_by_problem(problem.id)
    assert len(submissions) == 1
    assert submissions[0].result == 'PASS'
```

## Performance and Optimization Rules

### Database Optimization
```python
# ALWAYS use efficient queries
def get_leaderboard_efficient():
    """Get leaderboard with optimized query."""
    query = """
    SELECT user_name, COUNT(*) as problems_solved
    FROM submissions 
    WHERE result = 'PASS'
    GROUP BY user_name
    ORDER BY problems_solved DESC
    LIMIT 50
    """
    return db.execute(query).fetchall()

# NEVER use N+1 queries
def get_leaderboard_inefficient():
    """BAD: N+1 query problem."""
    users = get_all_users()
    leaderboard = []
    for user in users:  # This creates N additional queries
        count = get_user_solved_count(user.name)
        leaderboard.append((user.name, count))
    return leaderboard
```

### Memory Management
- **ALWAYS close database connections** properly
- **ALWAYS limit query results** with pagination
- **NEVER load entire datasets** into memory
- **ALWAYS use generators** for large data processing

## Deployment and Configuration Rules

### Environment Configuration
```python
# ALWAYS use environment variables for sensitive data
import os
from typing import Optional

class Config:
    """Application configuration."""
    
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DATABASE_URL: str = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    JUDGE_TIMEOUT: int = int(os.environ.get('JUDGE_TIMEOUT', '5'))
    DEBUG: bool = os.environ.get('FLASK_ENV') == 'development'
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration."""
        if cls.SECRET_KEY == 'dev-key-change-in-production' and not cls.DEBUG:
            raise ValueError("SECRET_KEY must be set in production")

# NEVER hardcode sensitive values
class BadConfig:
    SECRET_KEY = "hardcoded-secret"  # BAD: Security risk
    DATABASE_URL = "postgresql://user:pass@localhost/db"  # BAD: Exposed credentials
```

## Code Review Checklist

Before marking any task complete, verify:

### Functionality
- [ ] Feature works as specified in requirements
- [ ] All edge cases are handled
- [ ] Error conditions are properly managed
- [ ] User input is validated and sanitized

### Code Quality
- [ ] Functions are small and focused (< 50 lines)
- [ ] No duplicate code exists
- [ ] Naming is clear and descriptive
- [ ] Comments explain complex logic
- [ ] Code follows project structure guidelines

### Testing
- [ ] Unit tests cover main functionality
- [ ] Edge cases are tested
- [ ] Error conditions are tested
- [ ] Integration tests pass

### UI/UX (if applicable)
- [ ] Matches specifications in ui_ux.md
- [ ] Responsive design works on mobile
- [ ] Accessibility requirements met
- [ ] Color contrast meets WCAG standards

### Security
- [ ] User input is validated
- [ ] SQL injection prevention implemented
- [ ] XSS protection in place
- [ ] Sensitive data properly handled

### Documentation
- [ ] Code is properly documented
- [ ] API endpoints documented (if applicable)
- [ ] Error handling documented
- [ ] Configuration options documented

## Workflow Process

### Task Execution Steps
1. **Read task specification** completely
2. **Understand requirements** being addressed
3. **Check dependencies** and prerequisites
4. **Plan implementation** approach
5. **Write code** following these rules
6. **Write tests** for new functionality
7. **Test thoroughly** including edge cases
8. **Review against checklist** above
9. **Document any issues** encountered
10. **Mark task complete** only when fully validated

### Communication Guidelines
- **Be specific** about what was implemented
- **Mention any deviations** from specifications
- **Document any assumptions** made
- **Report any blockers** encountered
- **Suggest improvements** when appropriate

## Emergency Procedures

### When Things Go Wrong
1. **Stop immediately** - don't continue with broken code
2. **Document the issue** - what happened, when, why
3. **Revert changes** if necessary to restore working state
4. **Analyze root cause** - was it a rule violation?
5. **Fix properly** - don't just patch symptoms
6. **Test thoroughly** - ensure fix doesn't break other things
7. **Update rules** if needed to prevent recurrence

### Recovery Process
- **Backup frequently** - commit working code often
- **Use version control** - meaningful commit messages
- **Test incrementally** - don't accumulate untested changes
- **Document decisions** - why certain approaches were chosen

Remember: **Quality over speed**. It's better to implement features correctly and thoroughly than to rush and create technical debt or security vulnerabilities.