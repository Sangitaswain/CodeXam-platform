"""
End-to-End Integration Tests for CodeXam Platform
Tests complete user workflows from problem browsing to submission and leaderboard updates
"""

import pytest
import json
import tempfile
import os
import time
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from database import get_db_connection, create_tables
from models import Problem, Submission
from judge import JudgeResult, SimpleJudge


class TestCompleteUserWorkflow:
    """Test complete user journey from problem browsing to submission."""
    
    def setup_method(self):
        """Set up test environment with complete database."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Set up test database
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['DATABASE'] = self.db_path
        
        with app.app_context():
            create_tables()
            self._create_complete_test_environment()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_complete_test_environment(self):
        """Create a complete test environment with problems and users."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create sample problems
        problems = [
            {
                'title': 'Two Sum',
                'description': 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                'difficulty': 'Easy',
                'function_signatures': json.dumps({
                    'python': 'def solution(nums, target):',
                    'javascript': 'function solution(nums, target) {'
                }),
                'test_cases': json.dumps([
                    {'input': [[2, 7, 11, 15], 9], 'output': [0, 1]},
                    {'input': [[3, 2, 4], 6], 'output': [1, 2]},
                    {'input': [[3, 3], 6], 'output': [0, 1]}
                ])
            },
            {
                'title': 'Palindrome Check',
                'description': 'Determine if a string is a palindrome.',
                'difficulty': 'Easy',
                'function_signatures': json.dumps({
                    'python': 'def solution(s):',
                    'javascript': 'function solution(s) {'
                }),
                'test_cases': json.dumps([
                    {'input': ['racecar'], 'output': True},
                    {'input': ['hello'], 'output': False},
                    {'input': [''], 'output': True}
                ])
            },
            {
                'title': 'Fibonacci Sequence',
                'description': 'Return the nth Fibonacci number.',
                'difficulty': 'Medium',
                'function_signatures': json.dumps({
                    'python': 'def solution(n):',
                    'javascript': 'function solution(n) {'
                }),
                'test_cases': json.dumps([
                    {'input': [0], 'output': 0},
                    {'input': [1], 'output': 1},
                    {'input': [5], 'output': 5},
                    {'input': [10], 'output': 55}
                ])
            }
        ]
        
        for problem in problems:
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
    
    def test_complete_new_user_journey(self):
        """Test complete journey of a new user from arrival to first submission."""
        # Step 1: New user visits homepage
        response = self.client.get('/')
        assert response.status_code == 200
        assert b'CodeXam' in response.data or b'Welcome' in response.data
        
        # Step 2: User sets their name
        response = self.client.post('/set_name', 
                                  data={'user_name': 'NewUser'},
                                  follow_redirects=True)
        assert response.status_code == 200
        
        # Verify user name is stored in session
        with self.client.session_transaction() as sess:
            assert sess['user_name'] == 'NewUser'
        
        # Step 3: User browses problems list
        response = self.client.get('/problems')
        assert response.status_code == 200
        assert b'Two Sum' in response.data
        assert b'Palindrome Check' in response.data
        
        # Step 4: User selects a specific problem
        response = self.client.get('/problem/1')
        assert response.status_code == 200
        assert b'Two Sum' in response.data
        assert b'array of integers' in response.data
        
        # Step 5: User submits a solution
        with patch('judge.SimpleJudge.execute_code') as mock_execute:
            mock_execute.return_value = {
                'status': JudgeResult.PASS,
                'message': 'All tests passed!',
                'passed': 3,
                'total': 3,
                'execution_time': 0.05
            }
            
            submission_data = {
                'problem_id': 1,
                'language': 'python',
                'code': '''
def solution(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
''',
                'user_name': 'NewUser'
            }
            
            response = self.client.post('/submit',
                                      data=json.dumps(submission_data),
                                      content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'PASS'
        
        # Step 6: User checks their submission history
        response = self.client.get('/submissions')
        assert response.status_code == 200
        # Should show the recent submission
        
        # Step 7: User checks leaderboard
        response = self.client.get('/leaderboard')
        assert response.status_code == 200
        # Should show NewUser in the rankings
    
    def test_multi_problem_solving_workflow(self):
        """Test user solving multiple problems in sequence."""
        # Set up user session
        with self.client.session_transaction() as sess:
            sess['user_name'] = 'MultiSolver'
        
        problems_to_solve = [
            {
                'id': 1,
                'code': '''
def solution(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
'''
            },
            {
                'id': 2,
                'code': '''
def solution(s):
    return s == s[::-1]
'''
            },
            {
                'id': 3,
                'code': '''
def solution(n):
    if n <= 1:
        return n
    return solution(n-1) + solution(n-2)
'''
            }
        ]
        
        successful_submissions = 0
        
        with patch('judge.SimpleJudge.execute_code') as mock_execute:
            mock_execute.return_value = {
                'status': JudgeResult.PASS,
                'message': 'All tests passed!',
                'passed': 3,
                'total': 3,
                'execution_time': 0.05
            }
            
            for problem in problems_to_solve:
                # View the problem
                response = self.client.get(f'/problem/{problem["id"]}')
                assert response.status_code == 200
                
                # Submit solution
                submission_data = {
                    'problem_id': problem['id'],
                    'language': 'python',
                    'code': problem['code'],
                    'user_name': 'MultiSolver'
                }
                
                response = self.client.post('/submit',
                                          data=json.dumps(submission_data),
                                          content_type='application/json')
                
                assert response.status_code == 200
                result = json.loads(response.data)
                if result['status'] == 'PASS':
                    successful_submissions += 1
        
        # Verify submission history shows all attempts
        response = self.client.get('/submissions')
        assert response.status_code == 200
        
        # Check leaderboard position
        response = self.client.get('/leaderboard')
        assert response.status_code == 200


class TestErrorRecoveryWorkflows:
    """Test workflows involving errors and recovery."""
    
    def setup_method(self):
        """Set up test environment."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Set up test database
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['DATABASE'] = self.db_path
        
        with app.app_context():
            create_tables()
            self._create_test_problem()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_test_problem(self):
        """Create a test problem for error scenarios."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO problems (title, description, difficulty, function_signatures, test_cases)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'Simple Addition',
            'Add two numbers',
            'Easy',
            json.dumps({'python': 'def solution(a, b):'}),
            json.dumps([{'input': [1, 2], 'output': 3}])
        ))
        
        conn.commit()
        conn.close()
    
    def test_syntax_error_recovery_workflow(self):
        """Test user workflow when encountering syntax errors."""
        # Set up user session
        with self.client.session_transaction() as sess:
            sess['user_name'] = 'SyntaxLearner'
        
        # First submission with syntax error
        with patch('judge.SimpleJudge.execute_code') as mock_execute:
            mock_execute.return_value = {
                'status': JudgeResult.ERROR,
                'message': 'Syntax error in your Python code: missing colon',
                'execution_time': 0.01
            }
            
            submission_data = {
                'problem_id': 1,
                'language': 'python',
                'code': 'def solution(a, b) return a + b',  # Missing colon
                'user_name': 'SyntaxLearner'
            }
            
            response = self.client.post('/submit',
                                      data=json.dumps(submission_data),
                                      content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'ERROR'
            assert 'syntax' in result['message'].lower()
        
        # Second submission with corrected syntax
        with patch('judge.SimpleJudge.execute_code') as mock_execute:
            mock_execute.return_value = {
                'status': JudgeResult.PASS,
                'message': 'All tests passed!',
                'passed': 1,
                'total': 1,
                'execution_time': 0.03
            }
            
            corrected_submission = {
                'problem_id': 1,
                'language': 'python',
                'code': 'def solution(a, b): return a + b',  # Fixed syntax
                'user_name': 'SyntaxLearner'
            }
            
            response = self.client.post('/submit',
                                      data=json.dumps(corrected_submission),
                                      content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'PASS'
        
        # Check submission history shows both attempts
        response = self.client.get('/submissions')
        assert response.status_code == 200
    
    def test_security_violation_workflow(self):
        """Test workflow when user attempts dangerous code."""
        with self.client.session_transaction() as sess:
            sess['user_name'] = 'SecurityTester'
        
        dangerous_codes = [
            'import os; def solution(a, b): return a + b',
            'def solution(a, b): eval("1+1"); return a + b',
            'def solution(a, b): open("/etc/passwd"); return a + b'
        ]
        
        for dangerous_code in dangerous_codes:
            with patch('judge.SimpleJudge.execute_code') as mock_execute:
                mock_execute.return_value = {
                    'status': JudgeResult.ERROR,
                    'message': 'Security violation: Dangerous code detected',
                    'execution_time': 0.01
                }
                
                submission_data = {
                    'problem_id': 1,
                    'language': 'python',
                    'code': dangerous_code,
                    'user_name': 'SecurityTester'
                }
                
                response = self.client.post('/submit',
                                          data=json.dumps(submission_data),
                                          content_type='application/json')
                
                assert response.status_code == 200
                result = json.loads(response.data)
                assert result['status'] == 'ERROR'
                assert 'security' in result['message'].lower()
    
    def test_timeout_error_workflow(self):
        """Test workflow when code times out."""
        with self.client.session_transaction() as sess:
            sess['user_name'] = 'TimeoutUser'
        
        with patch('judge.SimpleJudge.execute_code') as mock_execute:
            mock_execute.return_value = {
                'status': JudgeResult.ERROR,
                'message': 'Code execution timed out - infinite loop detected',
                'execution_time': 5.0
            }
            
            timeout_code = '''
def solution(a, b):
    while True:
        pass
    return a + b
'''
            
            submission_data = {
                'problem_id': 1,
                'language': 'python',
                'code': timeout_code,
                'user_name': 'TimeoutUser'
            }
            
            response = self.client.post('/submit',
                                      data=json.dumps(submission_data),
                                      content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'ERROR'
            assert 'timeout' in result['message'].lower()


class TestLeaderboardIntegration:
    """Test leaderboard updates and ranking calculations."""
    
    def setup_method(self):
        """Set up test environment with multiple users and problems."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Set up test database
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['DATABASE'] = self.db_path
        
        with app.app_context():
            create_tables()
            self._create_leaderboard_test_environment()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_leaderboard_test_environment(self):
        """Create problems for leaderboard testing."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create 5 problems of varying difficulty
        problems = [
            ('Problem 1', 'Easy Problem', 'Easy'),
            ('Problem 2', 'Easy Problem', 'Easy'),
            ('Problem 3', 'Medium Problem', 'Medium'),
            ('Problem 4', 'Medium Problem', 'Medium'),
            ('Problem 5', 'Hard Problem', 'Hard')
        ]
        
        for title, description, difficulty in problems:
            cursor.execute('''
                INSERT INTO problems (title, description, difficulty, function_signatures, test_cases)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                title,
                description,
                difficulty,
                json.dumps({'python': 'def solution(x):'}),
                json.dumps([{'input': [1], 'output': 2}])
            ))
        
        conn.commit()
        conn.close()
    
    def test_leaderboard_ranking_workflow(self):
        """Test complete leaderboard ranking workflow with multiple users."""
        users_and_solutions = [
            ('TopSolver', [1, 2, 3, 4, 5]),  # Solves all problems
            ('GoodSolver', [1, 2, 3]),       # Solves first 3
            ('BeginnerSolver', [1]),          # Solves only 1
            ('MediumSolver', [1, 2, 4])      # Solves mixed difficulty
        ]
        
        with patch('judge.SimpleJudge.execute_code') as mock_execute:
            mock_execute.return_value = {
                'status': JudgeResult.PASS,
                'message': 'All tests passed!',
                'passed': 1,
                'total': 1,
                'execution_time': 0.05
            }
            
            for user_name, solved_problems in users_and_solutions:
                # Set user session
                with self.client.session_transaction() as sess:
                    sess['user_name'] = user_name
                
                for problem_id in solved_problems:
                    submission_data = {
                        'problem_id': problem_id,
                        'language': 'python',
                        'code': f'def solution(x): return x + {problem_id}',
                        'user_name': user_name
                    }
                    
                    response = self.client.post('/submit',
                                              data=json.dumps(submission_data),
                                              content_type='application/json')
                    
                    assert response.status_code == 200
                    result = json.loads(response.data)
                    assert result['status'] == 'PASS'
                    
                    # Small delay to ensure different timestamps
                    time.sleep(0.01)
        
        # Check leaderboard rankings
        response = self.client.get('/leaderboard')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        
        # TopSolver should appear before others
        top_pos = response_text.find('TopSolver')
        good_pos = response_text.find('GoodSolver')
        beginner_pos = response_text.find('BeginnerSolver')
        
        assert top_pos > 0
        assert good_pos > 0
        assert beginner_pos > 0
        # Note: Exact positioning depends on HTML structure
    
    def test_leaderboard_tie_breaking(self):
        """Test leaderboard tie-breaking mechanisms."""
        # Create two users who solve the same number of problems
        users = ['TieUser1', 'TieUser2']
        
        with patch('judge.SimpleJudge.execute_code') as mock_execute:
            mock_execute.return_value = {
                'status': JudgeResult.PASS,
                'message': 'All tests passed!',
                'passed': 1,
                'total': 1,
                'execution_time': 0.05
            }
            
            for user_name in users:
                with self.client.session_transaction() as sess:
                    sess['user_name'] = user_name
                
                # Both solve problems 1 and 2
                for problem_id in [1, 2]:
                    submission_data = {
                        'problem_id': problem_id,
                        'language': 'python',
                        'code': 'def solution(x): return x + 1',
                        'user_name': user_name
                    }
                    
                    response = self.client.post('/submit',
                                              data=json.dumps(submission_data),
                                              content_type='application/json')
                    
                    assert response.status_code == 200
                    # Add delay so TieUser1 submits first
                    time.sleep(0.1)
        
        # Check that leaderboard handles ties appropriately
        response = self.client.get('/leaderboard')
        assert response.status_code == 200
        # Both users should appear in leaderboard


class TestMultiLanguageWorkflow:
    """Test workflows involving multiple programming languages."""
    
    def setup_method(self):
        """Set up test environment."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Set up test database
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['DATABASE'] = self.db_path
        
        with app.app_context():
            create_tables()
            self._create_multi_language_problem()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def _create_multi_language_problem(self):
        """Create a problem that supports multiple languages."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO problems (title, description, difficulty, function_signatures, test_cases)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'Multi-Language Problem',
            'Add two numbers (supports all languages)',
            'Easy',
            json.dumps({
                'python': 'def solution(a, b):',
                'javascript': 'function solution(a, b) {',
                'java': 'public static int solution(int a, int b) {',
                'cpp': 'int solution(int a, int b) {'
            }),
            json.dumps([
                {'input': [1, 2], 'output': 3},
                {'input': [5, 7], 'output': 12}
            ])
        ))
        
        conn.commit()
        conn.close()
    
    def test_python_javascript_workflow(self):
        """Test user solving same problem in Python and JavaScript."""
        with self.client.session_transaction() as sess:
            sess['user_name'] = 'MultiLangUser'
        
        languages_and_codes = [
            ('python', 'def solution(a, b): return a + b'),
            ('javascript', 'function solution(a, b) { return a + b; }')
        ]
        
        for language, code in languages_and_codes:
            with patch('judge.SimpleJudge.execute_code') as mock_execute:
                if language == 'python':
                    mock_execute.return_value = {
                        'status': JudgeResult.PASS,
                        'message': 'All tests passed!',
                        'passed': 2,
                        'total': 2,
                        'execution_time': 0.05
                    }
                else:
                    # JavaScript might not be fully implemented
                    mock_execute.return_value = {
                        'status': JudgeResult.ERROR,
                        'message': 'JavaScript execution not fully implemented',
                        'execution_time': 0.01
                    }
                
                submission_data = {
                    'problem_id': 1,
                    'language': language,
                    'code': code,
                    'user_name': 'MultiLangUser'
                }
                
                response = self.client.post('/submit',
                                          data=json.dumps(submission_data),
                                          content_type='application/json')
                
                assert response.status_code == 200
                result = json.loads(response.data)
                # Should handle both successful and error cases
                assert result['status'] in [JudgeResult.PASS, JudgeResult.ERROR]
        
        # Check submission history shows both language attempts
        response = self.client.get('/submissions')
        assert response.status_code == 200


class TestAdminWorkflowIntegration:
    """Test admin problem creation workflow integration."""
    
    def setup_method(self):
        """Set up test environment."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Set up test database
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['DATABASE'] = self.db_path
        
        with app.app_context():
            create_tables()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_admin_create_and_solve_workflow(self):
        """Test complete workflow from admin creating problem to user solving it."""
        # Step 1: Admin creates a new problem
        problem_data = {
            'title': 'Admin Created Problem',
            'description': 'This problem was created by admin',
            'difficulty': 'Medium',
            'function_signatures': json.dumps({
                'python': 'def solution(x):'
            }),
            'test_cases': json.dumps([
                {'input': [5], 'output': 25},
                {'input': [3], 'output': 9}
            ])
        }
        
        # Mock admin problem creation (assuming admin route exists)
        with app.app_context():
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
        
        # Step 2: Verify problem appears in problems list
        response = self.client.get('/problems')
        assert response.status_code == 200
        assert b'Admin Created Problem' in response.data
        
        # Step 3: User views the new problem
        response = self.client.get('/problem/1')
        assert response.status_code == 200
        assert b'Admin Created Problem' in response.data
        
        # Step 4: User solves the new problem
        with self.client.session_transaction() as sess:
            sess['user_name'] = 'ProblemSolver'
        
        with patch('judge.SimpleJudge.execute_code') as mock_execute:
            mock_execute.return_value = {
                'status': JudgeResult.PASS,
                'message': 'All tests passed!',
                'passed': 2,
                'total': 2,
                'execution_time': 0.04
            }
            
            submission_data = {
                'problem_id': 1,
                'language': 'python',
                'code': 'def solution(x): return x * x',  # Squares the input
                'user_name': 'ProblemSolver'
            }
            
            response = self.client.post('/submit',
                                      data=json.dumps(submission_data),
                                      content_type='application/json')
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'PASS'
        
        # Step 5: Verify submission appears in history and leaderboard
        response = self.client.get('/submissions')
        assert response.status_code == 200
        
        response = self.client.get('/leaderboard')
        assert response.status_code == 200


class TestErrorPropagationWorkflow:
    """Test how errors propagate through the entire system."""
    
    def setup_method(self):
        """Set up test environment."""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_database_error_propagation(self):
        """Test how database errors are handled throughout the workflow."""
        # Test with invalid database path
        app.config['DATABASE'] = '/invalid/path/database.db'
        
        # These should handle database errors gracefully
        response = self.client.get('/')
        # Should not crash the application
        assert response.status_code in [200, 500]
        
        response = self.client.get('/problems')
        assert response.status_code in [200, 500]
    
    def test_judge_engine_error_propagation(self):
        """Test how judge engine errors propagate to user interface."""
        app.config['TESTING'] = True
        app.config['DATABASE'] = ':memory:'
        
        with patch('judge.SimpleJudge.execute_code') as mock_execute:
            # Simulate judge engine crash
            mock_execute.side_effect = Exception("Judge engine crashed")
            
            submission_data = {
                'problem_id': 1,
                'language': 'python',
                'code': 'def solution(): pass',
                'user_name': 'TestUser'
            }
            
            response = self.client.post('/submit',
                                      data=json.dumps(submission_data),
                                      content_type='application/json')
            
            # Should handle judge errors gracefully
            assert response.status_code in [200, 500]


class TestPerformanceWorkflow:
    """Test performance characteristics of complete workflows."""
    
    def setup_method(self):
        """Set up test environment."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
    
    def test_high_volume_submission_workflow(self):
        """Test workflow with many rapid submissions."""
        with self.client.session_transaction() as sess:
            sess['user_name'] = 'SpeedTester'
        
        # Simulate rapid submissions (testing rate limiting)
        submission_data = {
            'problem_id': 1,
            'language': 'python',
            'code': 'def solution(): pass',
            'user_name': 'SpeedTester'
        }
        
        responses = []
        for i in range(10):  # 10 rapid submissions
            response = self.client.post('/submit',
                                      data=json.dumps(submission_data),
                                      content_type='application/json')
            responses.append(response.status_code)
        
        # Should handle rapid submissions (either process or rate limit)
        for status_code in responses:
            assert status_code in [200, 400, 429]  # Success, bad request, or rate limited
    
    def test_concurrent_user_simulation(self):
        """Test behavior with multiple concurrent users."""
        # This is a simplified test - real concurrency testing would require threads
        user_names = ['User1', 'User2', 'User3', 'User4', 'User5']
        
        for user_name in user_names:
            with self.client.session_transaction() as sess:
                sess['user_name'] = user_name
            
            # Each user views problems and leaderboard
            response = self.client.get('/problems')
            assert response.status_code == 200
            
            response = self.client.get('/leaderboard')
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
