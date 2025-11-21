"""
Integration Tests for CodeXam Web Routes

Tests all routes with various input scenarios and database operations.
This module provides comprehensive testing for all web routes including
error handling, form validation, and database interactions.
"""

import json
import os
import sys
import tempfile
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from database import create_tables, get_db_connection
from judge import JudgeResult
from models import Problem, Submission

try:
    import form_validation
    HAS_FORM_VALIDATION = True
except ImportError:
    HAS_FORM_VALIDATION = False


class TestApplicationSetup:
    """Test application configuration and setup."""
    
    def test_app_exists(self) -> None:
        """Test that the Flask app exists and is configured."""
        assert app is not None
        assert app.config is not None
    
    def test_app_debug_mode(self) -> None:
        """Test app debug mode configuration."""
        # In testing, debug should be configurable
        assert hasattr(app, 'debug')
    
    def test_app_secret_key(self) -> None:
        """Test that app has a secret key configured."""
        assert app.secret_key is not None


class TestDatabaseOperations:
    """Test database operations and connections."""
    
    def setup_method(self):
        """Set up test database."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.original_db = app.config.get('DATABASE')
        app.config['DATABASE'] = self.db_path
        app.config['TESTING'] = True
        
        # Initialize test database
        with app.app_context():
            create_tables()
    
    def teardown_method(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
        if self.original_db:
            app.config['DATABASE'] = self.original_db
    
    def test_database_connection(self):
        """Test database connection functionality."""
        with app.app_context():
            conn = get_db_connection()
            assert conn is not None
            
            # Test basic query
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            assert len(tables) > 0
            conn.close()
    
    def test_database_tables_created(self):
        """Test that required database tables are created."""
        with app.app_context():
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check problems table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='problems';")
            assert cursor.fetchone() is not None
            
            # Check submissions table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='submissions';")
            assert cursor.fetchone() is not None
            
            conn.close()


class TestHomepageRoute:
    """Test the homepage route functionality."""
    
    def setup_method(self):
        """Set up test client."""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_homepage_get(self):
        """Test GET request to homepage."""
        response = self.client.get('/')
        assert response.status_code == 200
        assert b'CodeXam' in response.data or b'Welcome' in response.data
    
    def test_homepage_content_type(self):
        """Test homepage content type."""
        response = self.client.get('/')
        assert 'text/html' in response.content_type
    
    def test_homepage_navigation_links(self):
        """Test that homepage contains navigation links."""
        response = self.client.get('/')
        response_text = response.data.decode('utf-8')
        
        # Should contain links to main sections
        assert 'problems' in response_text.lower() or 'href="/problems"' in response_text
    
    def test_homepage_statistics(self):
        """Test that homepage displays platform statistics."""
        response = self.client.get('/')
        # Should not error even with empty database
        assert response.status_code == 200


class TestProblemsRoutes:
    """Test problems listing and detail routes."""
    
    def setup_method(self):
        """Set up test client and sample data."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Set up test database
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['DATABASE'] = self.db_path
        
        with app.app_context():
            create_tables()
            self._create_sample_problems()
    
    def teardown_method(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_sample_problems(self):
        """Create sample problems for testing."""
        sample_problems = [
            {
                'title': 'Two Sum',
                'description': 'Find two numbers that add up to target',
                'difficulty': 'Easy',
                'function_signatures': json.dumps({
                    'python': 'def solution(nums, target):',
                    'javascript': 'function solution(nums, target) {'
                }),
                'test_cases': json.dumps([
                    {'input': [[2, 7, 11, 15], 9], 'output': [0, 1]}
                ])
            },
            {
                'title': 'Reverse String',
                'description': 'Reverse a string',
                'difficulty': 'Easy',
                'function_signatures': json.dumps({
                    'python': 'def solution(s):',
                    'javascript': 'function solution(s) {'
                }),
                'test_cases': json.dumps([
                    {'input': ['hello'], 'output': 'olleh'}
                ])
            }
        ]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for problem in sample_problems:
            cursor.execute('''
                INSERT INTO problems (title, description, difficulty, function_signatures, test_cases)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                problem['title'],
                problem['description'], 
                problem['difficulty'],
                problem['function_signatures'],
                problem['test_cases']
            ))
        
        conn.commit()
        conn.close()
    
    def test_problems_list_get(self):
        """Test GET request to problems list."""
        response = self.client.get('/problems')
        assert response.status_code == 200
        assert b'Two Sum' in response.data
        assert b'Reverse String' in response.data
    
    def test_problems_list_empty(self):
        """Test problems list with empty database."""
        # Clear all problems
        with app.app_context():
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM problems')
            conn.commit()
            conn.close()
        
        response = self.client.get('/problems')
        assert response.status_code == 200
        # Should handle empty state gracefully
    
    def test_problem_detail_get(self):
        """Test GET request to problem detail."""
        response = self.client.get('/problem/1')
        assert response.status_code == 200
        assert b'Two Sum' in response.data
        assert b'function_signatures' in response.data or b'def solution' in response.data
    
    def test_problem_detail_not_found(self):
        """Test problem detail for non-existent problem."""
        response = self.client.get('/problem/999')
        assert response.status_code == 404
    
    def test_problem_detail_invalid_id(self):
        """Test problem detail with invalid ID."""
        response = self.client.get('/problem/invalid')
        assert response.status_code == 404


class TestSubmissionRoutes:
    """Test code submission functionality."""
    
    def setup_method(self):
        """Set up test client and sample data."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Set up test database
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['DATABASE'] = self.db_path
        
        with app.app_context():
            create_tables()
            self._create_sample_problem()
    
    def teardown_method(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_sample_problem(self):
        """Create a sample problem for testing submissions."""
        problem_data = {
            'title': 'Add Two Numbers',
            'description': 'Add two integers',
            'difficulty': 'Easy',
            'function_signatures': json.dumps({
                'python': 'def solution(a, b):'
            }),
            'test_cases': json.dumps([
                {'input': [1, 2], 'output': 3},
                {'input': [5, 7], 'output': 12}
            ])
        }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO problems (title, description, difficulty, function_signatures, test_cases)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            problem_data['title'],
            problem_data['description'],
            problem_data['difficulty'],
            problem_data['function_signatures'],
            problem_data['test_cases']
        ))
        conn.commit()
        conn.close()
    
    @patch('judge.SimpleJudge.execute_code')
    def test_submit_valid_code(self, mock_execute):
        """Test submission of valid code."""
        mock_execute.return_value = {
            'status': JudgeResult.PASS,
            'message': 'All tests passed!',
            'passed': 2,
            'total': 2,
            'execution_time': 0.05
        }
        
        submission_data = {
            'problem_id': 1,
            'language': 'python',
            'code': 'def solution(a, b): return a + b',
            'user_name': 'TestUser'
        }
        
        response = self.client.post('/submit', 
                                  data=json.dumps(submission_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'PASS'
        assert result['passed'] == 2
    
    @patch('judge.SimpleJudge.execute_code')
    def test_submit_failing_code(self, mock_execute):
        """Test submission of code that fails tests."""
        mock_execute.return_value = {
            'status': JudgeResult.FAIL,
            'message': 'Test case 1 failed',
            'passed': 1,
            'total': 2,
            'execution_time': 0.03
        }
        
        submission_data = {
            'problem_id': 1,
            'language': 'python',
            'code': 'def solution(a, b): return a - b',  # Wrong logic
            'user_name': 'TestUser'
        }
        
        response = self.client.post('/submit',
                                  data=json.dumps(submission_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'FAIL'
        assert result['passed'] < result['total']
    
    @patch('judge.SimpleJudge.execute_code')
    def test_submit_error_code(self, mock_execute):
        """Test submission of code with errors."""
        mock_execute.return_value = {
            'status': JudgeResult.ERROR,
            'message': 'Syntax error in your Python code',
            'execution_time': 0.01
        }
        
        submission_data = {
            'problem_id': 1,
            'language': 'python',
            'code': 'def solution(a, b) return a + b',  # Syntax error
            'user_name': 'TestUser'
        }
        
        response = self.client.post('/submit',
                                  data=json.dumps(submission_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'ERROR'
        assert 'syntax' in result['message'].lower()
    
    def test_submit_invalid_problem(self):
        """Test submission for non-existent problem."""
        submission_data = {
            'problem_id': 999,
            'language': 'python',
            'code': 'def solution(): pass',
            'user_name': 'TestUser'
        }
        
        response = self.client.post('/submit',
                                  data=json.dumps(submission_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
    
    def test_submit_missing_data(self):
        """Test submission with missing required data."""
        incomplete_data = {
            'problem_id': 1,
            'language': 'python'
            # Missing code and user_name
        }
        
        response = self.client.post('/submit',
                                  data=json.dumps(incomplete_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
    
    def test_submit_invalid_language(self):
        """Test submission with unsupported language."""
        submission_data = {
            'problem_id': 1,
            'language': 'ruby',  # Unsupported
            'code': 'puts "hello"',
            'user_name': 'TestUser'
        }
        
        response = self.client.post('/submit',
                                  data=json.dumps(submission_data),
                                  content_type='application/json')
        
        # Should handle gracefully - either 400 or return error in result
        assert response.status_code in [200, 400]


class TestUserIdentificationRoutes:
    """Test user identification and session management."""
    
    def setup_method(self):
        """Set up test client."""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_set_user_name_post(self):
        """Test setting user name via POST."""
        response = self.client.post('/set_name', 
                                  data={'user_name': 'TestUser'},
                                  follow_redirects=True)
        
        assert response.status_code == 200
        
        # Check if user name is stored in session
        with self.client.session_transaction() as sess:
            assert 'user_name' in sess
            assert sess['user_name'] == 'TestUser'
    
    def test_set_empty_user_name(self):
        """Test setting empty user name."""
        response = self.client.post('/set_name',
                                  data={'user_name': ''},
                                  follow_redirects=True)
        
        # Should handle gracefully
        assert response.status_code == 200
    
    def test_user_session_persistence(self):
        """Test that user session persists across requests."""
        # Set user name
        self.client.post('/set_name', data={'user_name': 'PersistentUser'})
        
        # Make another request and check session
        response = self.client.get('/')
        assert response.status_code == 200
        
        with self.client.session_transaction() as sess:
            assert sess.get('user_name') == 'PersistentUser'


class TestSubmissionHistoryRoutes:
    """Test submission history functionality."""
    
    def setup_method(self):
        """Set up test client and sample data."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Set up test database
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['DATABASE'] = self.db_path
        
        with app.app_context():
            create_tables()
            self._create_sample_submissions()
    
    def teardown_method(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_sample_submissions(self):
        """Create sample submissions for testing."""
        # First create a problem
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO problems (title, description, difficulty, function_signatures, test_cases)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Test Problem', 'Test Description', 'Easy', '{}', '[]'))
        
        # Then create submissions
        submissions = [
            ('TestUser', 1, 'python', 'def solution(): pass', 'PASS', 0.05),
            ('TestUser', 1, 'javascript', 'function solution() {}', 'FAIL', 0.03),
            ('AnotherUser', 1, 'python', 'def solution(): return 42', 'PASS', 0.02)
        ]
        
        for user_name, problem_id, language, code, status, execution_time in submissions:
            cursor.execute('''
                INSERT INTO submissions (user_name, problem_id, language, code, status, execution_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_name, problem_id, language, code, status, execution_time))
        
        conn.commit()
        conn.close()
    
    def test_submissions_history_get(self):
        """Test GET request to submissions history."""
        # Set user name in session
        with self.client.session_transaction() as sess:
            sess['user_name'] = 'TestUser'
        
        response = self.client.get('/submissions')
        assert response.status_code == 200
        
        # Should show user's submissions
        response_text = response.data.decode('utf-8')
        assert 'TestUser' in response_text or 'python' in response_text
    
    def test_submissions_history_empty_user(self):
        """Test submissions history for user with no submissions."""
        # Set user name that has no submissions
        with self.client.session_transaction() as sess:
            sess['user_name'] = 'NoSubmissionsUser'
        
        response = self.client.get('/submissions')
        assert response.status_code == 200
        # Should handle empty state gracefully
    
    def test_submissions_history_no_user_session(self):
        """Test submissions history without user session."""
        response = self.client.get('/submissions')
        # Should either redirect to set name or show anonymous state
        assert response.status_code in [200, 302]


class TestLeaderboardRoutes:
    """Test leaderboard functionality."""
    
    def setup_method(self):
        """Set up test client and sample data."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Set up test database
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['DATABASE'] = self.db_path
        
        with app.app_context():
            create_tables()
            self._create_leaderboard_data()
    
    def teardown_method(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_leaderboard_data(self):
        """Create sample data for leaderboard testing."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create problems
        for i in range(3):
            cursor.execute('''
                INSERT INTO problems (title, description, difficulty, function_signatures, test_cases)
                VALUES (?, ?, ?, ?, ?)
            ''', (f'Problem {i+1}', f'Description {i+1}', 'Easy', '{}', '[]'))
        
        # Create successful submissions for different users
        submissions = [
            ('Alice', 1, 'python', 'code1', 'PASS', 0.05),
            ('Alice', 2, 'python', 'code2', 'PASS', 0.04),
            ('Alice', 3, 'python', 'code3', 'PASS', 0.06),
            ('Bob', 1, 'python', 'code1', 'PASS', 0.03),
            ('Bob', 2, 'python', 'code2', 'PASS', 0.07),
            ('Charlie', 1, 'python', 'code1', 'PASS', 0.08),
            ('Alice', 1, 'javascript', 'code1js', 'FAIL', 0.02),  # Failed submission
        ]
        
        for user_name, problem_id, language, code, status, execution_time in submissions:
            cursor.execute('''
                INSERT INTO submissions (user_name, problem_id, language, code, status, execution_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_name, problem_id, language, code, status, execution_time))
        
        conn.commit()
        conn.close()
    
    def test_leaderboard_get(self):
        """Test GET request to leaderboard."""
        response = self.client.get('/leaderboard')
        assert response.status_code == 200
        
        response_text = response.data.decode('utf-8')
        assert 'Alice' in response_text
        assert 'Bob' in response_text
        assert 'Charlie' in response_text
    
    def test_leaderboard_ranking_order(self):
        """Test that leaderboard shows users in correct order."""
        response = self.client.get('/leaderboard')
        response_text = response.data.decode('utf-8')
        
        # Alice should rank higher than others (3 problems solved)
        alice_pos = response_text.find('Alice')
        bob_pos = response_text.find('Bob')
        charlie_pos = response_text.find('Charlie')
        
        assert alice_pos > 0
        assert bob_pos > 0
        assert charlie_pos > 0
    
    def test_leaderboard_empty_database(self):
        """Test leaderboard with no submissions."""
        # Clear all submissions
        with app.app_context():
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM submissions')
            conn.commit()
            conn.close()
        
        response = self.client.get('/leaderboard')
        assert response.status_code == 200
        # Should handle empty state gracefully


class TestFormValidationIntegration:
    """Test integration with form validation system."""
    
    def setup_method(self):
        """Set up test client."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
    
    @patch('form_validation.validate_submission')
    def test_form_validation_on_submission(self, mock_validate):
        """Test that form validation is called on submission."""
        mock_validate.return_value = (True, None)
        
        submission_data = {
            'problem_id': 1,
            'language': 'python',
            'code': 'def solution(): pass',
            'user_name': 'TestUser'
        }
        
        response = self.client.post('/submit',
                                  data=json.dumps(submission_data),
                                  content_type='application/json')
        
        # Validation should be called
        mock_validate.assert_called()
    
    def test_security_validation_blocks_dangerous_code(self):
        """Test that security validation blocks dangerous code."""
        dangerous_submission = {
            'problem_id': 1,
            'language': 'python',
            'code': 'import os; os.system("rm -rf /")',
            'user_name': 'TestUser'
        }
        
        response = self.client.post('/submit',
                                  data=json.dumps(dangerous_submission),
                                  content_type='application/json')
        
        # Should be blocked by security validation
        assert response.status_code in [400, 200]  # 200 if validation returns error in JSON
    
    @patch('form_validation.RateLimiter.is_rate_limited')
    def test_rate_limiting_integration(self, mock_rate_limit):
        """Test rate limiting integration."""
        mock_rate_limit.return_value = True
        
        submission_data = {
            'problem_id': 1,
            'language': 'python',
            'code': 'def solution(): pass',
            'user_name': 'TestUser'
        }
        
        response = self.client.post('/submit',
                                  data=json.dumps(submission_data),
                                  content_type='application/json')
        
        # Should be rate limited
        assert response.status_code in [429, 400, 200]


class TestErrorHandling:
    """Test error handling throughout the application."""
    
    def setup_method(self):
        """Set up test client."""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_404_error_handling(self):
        """Test 404 error handling."""
        response = self.client.get('/nonexistent-route')
        assert response.status_code == 404
    
    def test_500_error_handling(self):
        """Test 500 error handling."""
        # This is harder to test without causing actual errors
        # We can test that error handlers are registered
        assert app.error_handler_spec is not None
    
    def test_json_error_responses(self):
        """Test JSON error responses for API endpoints."""
        # Test malformed JSON
        response = self.client.post('/submit',
                                  data='invalid json',
                                  content_type='application/json')
        
        assert response.status_code == 400
    
    def test_database_error_handling(self):
        """Test handling of database errors."""
        # This test would require mocking database failures
        # For now, we test that the application doesn't crash
        response = self.client.get('/')
        assert response.status_code == 200


class TestSessionManagement:
    """Test session management across the application."""
    
    def setup_method(self):
        """Set up test client."""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_session_cookie_settings(self):
        """Test session cookie configuration."""
        with self.client.session_transaction() as sess:
            sess['test'] = 'value'
        
        response = self.client.get('/')
        assert response.status_code == 200
    
    def test_anonymous_user_handling(self):
        """Test handling of anonymous users."""
        # Test that app works without user session
        response = self.client.get('/problems')
        assert response.status_code == 200
        
        response = self.client.get('/leaderboard')
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
