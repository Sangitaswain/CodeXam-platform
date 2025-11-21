# CodeXam Testing Guide

This document provides comprehensive guidance for testing the CodeXam platform, including test structure, execution, and best practices.

## Table of Contents

1. [Testing Framework Overview](#testing-framework-overview)
2. [Test Categories](#test-categories)
3. [Running Tests](#running-tests)
4. [Test Structure](#test-structure)
5. [Writing Tests](#writing-tests)
6. [Coverage Requirements](#coverage-requirements)
7. [Continuous Integration](#continuous-integration)
8. [Troubleshooting](#troubleshooting)

## Testing Framework Overview

CodeXam uses **pytest** as the primary testing framework with the following key components:

- **pytest**: Core testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **pytest-xdist**: Parallel test execution
- **Custom fixtures**: Application-specific test utilities

### Key Features

- **Comprehensive test coverage**: Unit, integration, security, and performance tests
- **Automated fixtures**: Database setup, mock objects, and test utilities
- **Security testing**: XSS, SQL injection, CSRF, and other security vulnerabilities
- **Performance testing**: Load testing, memory usage, and response time validation
- **Coverage reporting**: HTML and terminal coverage reports with 80% minimum threshold

## Test Categories

### 1. Unit Tests (`@pytest.mark.unit`)

Test individual components in isolation:

- **Models**: Database operations, data validation
- **Judge System**: Code execution, security checks
- **Utilities**: Helper functions, data processing
- **Cache**: Caching mechanisms and performance

**Example:**
```python
@pytest.mark.unit
def test_problem_creation(test_db, test_utils):
    \"\"\"Test creating a new problem.\"\"\"
    problem_id = test_utils.create_test_problem(
        test_db,
        title="Test Problem",
        difficulty="Easy"
    )
    assert problem_id is not None
```

### 2. Integration Tests (`@pytest.mark.integration`)

Test component interactions and workflows:

- **Route handlers**: HTTP request/response cycles
- **Database integration**: Multi-table operations
- **Template rendering**: UI component integration
- **API endpoints**: Complete request workflows

**Example:**
```python
@pytest.mark.integration
def test_code_submission_workflow(authenticated_client, test_db, mock_judge):
    \"\"\"Test complete code submission workflow.\"\"\"
    response = authenticated_client.post('/submit', data={
        'problem_id': '1',
        'language': 'python',
        'code': 'def solution(): return "test"'
    })
    assert response.status_code == 200
```

### 3. Security Tests (`@pytest.mark.security`)

Test security measures and vulnerability prevention:

- **Input validation**: XSS, SQL injection prevention
- **Authentication**: Session management, CSRF protection
- **Authorization**: Access control, privilege escalation
- **Code execution**: Malicious code detection, sandboxing

**Example:**
```python
@pytest.mark.security
def test_xss_prevention(client):
    \"\"\"Test XSS prevention in user inputs.\"\"\"
    xss_payload = '<script>alert("xss")</script>'
    response = client.post('/set_name', data={'user_name': xss_payload})
    assert b'<script>' not in response.data
```

### 4. Performance Tests (`@pytest.mark.performance`)

Test system performance and scalability:

- **Response times**: Page load performance
- **Database queries**: Query optimization validation
- **Memory usage**: Memory leak detection
- **Concurrent load**: Multi-user scenarios

**Example:**
```python
@pytest.mark.performance
def test_problem_list_performance(test_db):
    \"\"\"Test that problem list loads quickly.\"\"\"
    start_time = time.time()
    problems = Problem.get_all()
    execution_time = time.time() - start_time
    assert execution_time < 0.1  # Should load within 100ms
```

### 5. Smoke Tests (`@pytest.mark.smoke`)

Quick validation tests for basic functionality:

- **Core routes**: Essential page loads
- **Database connectivity**: Basic CRUD operations
- **Critical features**: User registration, code submission

## Running Tests

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov pytest-mock pytest-xdist
   ```

2. **Set up test environment:**
   ```bash
   export FLASK_ENV=testing
   export DATABASE_URL=sqlite:///test_database.db
   ```

### Test Execution Options

#### Using the Test Runner Script

```bash
# Validate test environment
python scripts/run_tests.py --validate

# Run smoke tests (quick validation)
python scripts/run_tests.py --smoke

# Run specific test categories
python scripts/run_tests.py --unit
python scripts/run_tests.py --integration
python scripts/run_tests.py --security
python scripts/run_tests.py --performance

# Run all tests with coverage
python scripts/run_tests.py --all --coverage

# Run specific test file
python scripts/run_tests.py --specific tests/test_models.py

# Run tests in parallel
python scripts/run_tests.py --parallel --workers 4

# Re-run failed tests
python scripts/run_tests.py --failed

# Clean test artifacts
python scripts/run_tests.py --clean
```

#### Using pytest Directly

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m security
pytest -m performance

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run specific test function
pytest tests/test_models.py::TestProblem::test_problem_creation

# Run tests in parallel
pytest -n auto

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Test Configuration

The `pytest.ini` file contains comprehensive test configuration:

```ini
[tool:pytest]
testpaths = tests
markers =
    unit: Unit tests for individual components
    integration: Integration tests for component interactions
    security: Security-focused tests
    performance: Performance and load tests
    slow: Tests that take longer to run

addopts = 
    --verbose
    --tb=short
    --cov=.
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-fail-under=80
```

## Test Structure

### Directory Organization

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_models.py           # Model unit tests
├── test_routes.py           # Route integration tests
├── test_judge.py            # Judge system tests
├── test_security.py         # Security tests
├── test_performance.py      # Performance tests
└── test_cross_browser.py    # Browser compatibility tests
```

### Key Test Files

#### `conftest.py`
- **Application fixtures**: Test app, client, database
- **Mock objects**: Judge, external services
- **Test utilities**: Helper functions, custom assertions
- **Sample data**: Test problems, submissions, users

#### `test_models.py`
- **Problem model**: CRUD operations, validation
- **Submission model**: Creation, retrieval, statistics
- **Database integrity**: Constraints, relationships

#### `test_routes.py`
- **Route handlers**: Request/response validation
- **Form processing**: Input validation, error handling
- **Authentication**: Session management, access control

#### `test_judge.py`
- **Code execution**: Multi-language support
- **Security**: Malicious code detection
- **Performance**: Execution time, memory usage

#### `test_security.py`
- **Input validation**: XSS, SQL injection prevention
- **Authentication**: Session security, CSRF protection
- **Authorization**: Access control validation

#### `test_performance.py`
- **Response times**: Page load performance
- **Database performance**: Query optimization
- **Memory usage**: Leak detection, resource management

## Writing Tests

### Test Naming Conventions

- **Test files**: `test_*.py`
- **Test classes**: `Test*` (e.g., `TestProblemModel`)
- **Test functions**: `test_*` (e.g., `test_create_problem`)

### Test Structure Pattern

```python
class TestFeatureName:
    \"\"\"Test cases for specific feature.\"\"\"
    
    @pytest.mark.unit
    def test_normal_case(self, fixtures):
        \"\"\"Test normal operation.\"\"\"
        # Arrange
        setup_data = create_test_data()
        
        # Act
        result = function_under_test(setup_data)
        
        # Assert
        assert result.is_valid()
        assert result.value == expected_value
    
    @pytest.mark.unit
    def test_edge_case(self, fixtures):
        \"\"\"Test edge case handling.\"\"\"
        # Test boundary conditions
        pass
    
    @pytest.mark.unit
    def test_error_case(self, fixtures):
        \"\"\"Test error handling.\"\"\"
        with pytest.raises(ExpectedError):
            function_under_test(invalid_data)
```

### Using Fixtures

```python
def test_with_database(test_db, test_utils):
    \"\"\"Test using database fixture.\"\"\"
    # test_db provides clean database
    # test_utils provides helper functions
    problem_id = test_utils.create_test_problem(test_db, title="Test")
    assert problem_id is not None

def test_with_client(client, test_db):
    \"\"\"Test using client fixture.\"\"\"
    # client provides Flask test client
    response = client.get('/problems')
    assert response.status_code == 200

def test_with_mock(mock_judge, sample_code):
    \"\"\"Test using mock objects.\"\"\"
    # mock_judge provides mocked judge system
    # sample_code provides test code snippets
    result = mock_judge.execute_code('python', sample_code['valid_python'], [])
    assert result['result'] == 'PASS'
```

### Custom Assertions

```python
def test_with_custom_assertions(client, assert_helper):
    \"\"\"Test using custom assertion helpers.\"\"\"
    response = client.get('/problems')
    
    # Use custom assertion helper
    data = assert_helper.assert_valid_response(response, expected_status=200)
    assert 'problems' in data
```

### Mocking External Dependencies

```python
@patch('routes.SimpleJudge')
def test_code_submission_with_mock(mock_judge_class, authenticated_client):
    \"\"\"Test code submission with mocked judge.\"\"\"
    mock_judge = Mock()
    mock_judge.execute_code.return_value = {'result': 'PASS'}
    mock_judge_class.return_value = mock_judge
    
    response = authenticated_client.post('/submit', data={
        'problem_id': '1',
        'code': 'def solution(): return "test"'
    })
    
    assert response.status_code == 200
    mock_judge.execute_code.assert_called_once()
```

## Coverage Requirements

### Minimum Coverage Thresholds

- **Overall coverage**: 80% minimum
- **Critical modules**: 90% minimum (models, routes, judge)
- **Security functions**: 95% minimum
- **New code**: 85% minimum

### Coverage Reporting

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# View coverage in terminal
pytest --cov=. --cov-report=term-missing

# Generate XML coverage report (for CI)
pytest --cov=. --cov-report=xml

# Fail if coverage below threshold
pytest --cov=. --cov-fail-under=80
```

### Coverage Analysis

1. **View HTML report**: Open `htmlcov/index.html` in browser
2. **Identify gaps**: Look for uncovered lines in red
3. **Prioritize**: Focus on critical paths and error handling
4. **Add tests**: Write tests for uncovered code paths

## Continuous Integration

### GitHub Actions Configuration

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-xdist
    
    - name: Run tests
      run: |
        python scripts/run_tests.py --all --coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: Run tests
        entry: python scripts/run_tests.py --smoke
        language: system
        pass_filenames: false
        always_run: true
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Error: Database locked or not found
# Solution: Clean test artifacts and recreate database
python scripts/run_tests.py --clean
python init_db.py
```

#### 2. Import Errors

```bash
# Error: ModuleNotFoundError
# Solution: Ensure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 3. Fixture Errors

```bash
# Error: Fixture not found
# Solution: Check conftest.py and fixture definitions
pytest --fixtures  # List available fixtures
```

#### 4. Slow Test Execution

```bash
# Solution: Run tests in parallel
pytest -n auto  # Use all available cores
pytest -n 4     # Use 4 cores
```

#### 5. Memory Issues

```bash
# Solution: Run tests with memory monitoring
pytest --tb=short --maxfail=5  # Stop early on failures
```

### Debugging Tests

#### 1. Verbose Output

```bash
pytest -v -s  # Verbose with print statements
```

#### 2. Debug Specific Test

```bash
pytest tests/test_models.py::TestProblem::test_create_problem -v -s
```

#### 3. Drop into Debugger

```python
def test_debug_example():
    import pdb; pdb.set_trace()  # Debugger breakpoint
    # Test code here
```

#### 4. Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_logging():
    logger = logging.getLogger(__name__)
    logger.debug("Debug information")
    # Test code here
```

### Performance Optimization

#### 1. Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

#### 2. Test Selection

```bash
# Run only fast tests
pytest -m "not slow"

# Run specific test categories
pytest -m "unit or integration"
```

#### 3. Database Optimization

```python
# Use in-memory database for faster tests
@pytest.fixture
def fast_db():
    return create_in_memory_database()
```

## Best Practices

### 1. Test Organization

- **Group related tests** in classes
- **Use descriptive test names** that explain the scenario
- **Follow AAA pattern**: Arrange, Act, Assert
- **Keep tests independent** and isolated

### 2. Test Data Management

- **Use fixtures** for reusable test data
- **Create minimal test data** for each test
- **Clean up after tests** to avoid side effects
- **Use factories** for complex object creation

### 3. Mocking Strategy

- **Mock external dependencies** (APIs, file system)
- **Don't mock what you're testing**
- **Use realistic mock data**
- **Verify mock interactions** when relevant

### 4. Error Testing

- **Test both success and failure paths**
- **Test edge cases and boundary conditions**
- **Verify error messages and status codes**
- **Test exception handling**

### 5. Security Testing

- **Test all input validation**
- **Verify authentication and authorization**
- **Test for common vulnerabilities** (XSS, SQL injection)
- **Validate security headers and configurations**

### 6. Performance Testing

- **Set realistic performance expectations**
- **Test under various load conditions**
- **Monitor resource usage**
- **Test scalability limits**

This comprehensive testing framework ensures the CodeXam platform maintains high quality, security, and performance standards through automated testing and continuous validation.