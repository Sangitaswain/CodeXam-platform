"""
pytest configuration and fixtures for CodeXam tests
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Try to import app and database modules
try:
    from app import app
    APP_AVAILABLE = True
except ImportError:
    APP_AVAILABLE = False
    app = None

try:
    from database import create_tables, get_db_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    create_tables = None
    get_db_connection = None

@pytest.fixture
def app_instance():
    """Create and configure a test Flask application."""
    if not APP_AVAILABLE:
        pytest.skip("Flask app not available")
    
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure app for testing
    app.config['DATABASE'] = db_path
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    if DATABASE_AVAILABLE and create_tables:
        with app.app_context():
            try:
                create_tables()
            except Exception:
                # If database creation fails, still provide app for basic tests
                pass
    
    yield app
    
    # Clean up
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass

@pytest.fixture
def test_client(app_instance):
    """Create a test client for the Flask application."""
    return app_instance.test_client()

@pytest.fixture
def sample_problem_data():
    """Provide sample problem data for testing."""
    return {
        'title': 'Test Problem',
        'description': 'A simple test problem',
        'difficulty': 'Easy',
        'function_signatures': '{"python": "def solution(x):"}',
        'test_cases': '[{"input": [1], "output": 2}]'
    }

@pytest.fixture
def mock_judge():
    """Provide a mock judge engine for testing."""
    mock = Mock()
    mock.execute_code.return_value = {
        'status': 'PASS',
        'message': 'All tests passed!',
        'passed': 1,
        'total': 1,
        'execution_time': 0.05
    }
    return mock

@pytest.fixture
def test_database():
    """Provide a temporary test database."""
    db_fd, db_path = tempfile.mkstemp()
    
    # Set up database
    original_db = None
    if APP_AVAILABLE and app:
        original_db = app.config.get('DATABASE')
        app.config['DATABASE'] = db_path
        
        if DATABASE_AVAILABLE and create_tables:
            with app.app_context():
                try:
                    create_tables()
                except Exception:
                    pass
    
    yield db_path
    
    # Clean up
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass
    
    # Restore original database
    if APP_AVAILABLE and app and original_db:
        app.config['DATABASE'] = original_db

@pytest.fixture
def sample_code():
    """Provide sample code snippets for testing."""
    return {
        'valid_python': """
def solution(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
""",
        'invalid_python': """
def solution(nums, target):
    for i in range(len(nums))  # Missing colon
        return nums[i]
""",
        'timeout_python': """
def solution(nums, target):
    while True:  # Infinite loop
        pass
    return []
""",
        'malicious_python': """
import os
def solution(nums, target):
    os.system('rm -rf /')  # Malicious code
    return []
""",
        'memory_intensive_python': """
def solution(nums, target):
    # Create large data structure
    big_list = [0] * (10**8)
    return [0, 1]
""",
        'valid_javascript': """
function solution(nums, target) {
    for (let i = 0; i < nums.length; i++) {
        for (let j = i + 1; j < nums.length; j++) {
            if (nums[i] + nums[j] === target) {
                return [i, j];
            }
        }
    }
    return [];
}
""",
        'invalid_javascript': """
function solution(nums, target) {
    for (let i = 0; i < nums.length; i++  // Missing closing parenthesis
        return [i];
}
"""
    }

@pytest.fixture
def mock_error_handler():
    """Mock the error handling system for testing."""
    with patch('error_handler.handle_execution_error') as mock_handle:
        mock_handle.return_value = {
            'status': 'ERROR',
            'message': 'Test error message',
            'error_type': 'SYNTAX_ERROR'
        }
        yield mock_handle

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "unit: marks unit tests")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add markers based on test file names
        if "test_judge" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_routes" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            
        # Mark slow tests
        if "timeout" in item.name.lower() or "performance" in item.name.lower():
            item.add_marker(pytest.mark.slow)

@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test runner for the Flask application."""
    return app.test_cli_runner()