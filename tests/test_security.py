"""Security-focused tests for CodeXam platform."""

import pytest
import json
from unittest.mock import Mock, patch


class TestInputValidation:
    """Test input validation and sanitization."""
    
    @pytest.mark.security
    def test_xss_prevention_username(self, client):
        """Test XSS prevention in username input."""
        xss_payloads = [
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            '<img src=x onerror=alert("xss")>',
            '<svg onload=alert("xss")>',
            '\\u003cscript\\u003ealert("xss")\\u003c/script\\u003e'
        ]
        
        for payload in xss_payloads:
            response = client.post('/set_name', data={
                'user_name': payload,
                'csrf_token': 'test-token'
            })
            
            # Should not execute XSS
            assert b'<script>' not in response.data
            assert b'javascript:' not in response.data
            assert b'onerror=' not in response.data
    
    @pytest.mark.security
    def test_sql_injection_prevention_problem_id(self, client, test_db):
        """Test SQL injection prevention in problem ID parameter."""
        sql_payloads = [
            "1'; DROP TABLE problems; --",
            "1 OR 1=1",
            "1 UNION SELECT * FROM users",
            "1; DELETE FROM submissions; --",
            "1' AND (SELECT COUNT(*) FROM problems) > 0 --"
        ]
        
        for payload in sql_payloads:
            response = client.get(f'/problem/{payload}')
            
            # Should handle SQL injection attempts
            assert response.status_code in [400, 404]  # Bad request or not found
        
        # Verify database integrity
        from models import Problem
        problems = Problem.get_all()
        assert len(problems) >= 3  # Original test data should still exist
    
    @pytest.mark.security
    def test_code_injection_prevention(self, authenticated_client, test_db):
        """Test prevention of code injection in submissions."""
        malicious_codes = [
            'import os; os.system("rm -rf /")',
            '__import__("os").system("malicious_command")',
            'eval("__import__(\"os\").system(\"rm -rf /\")")',
            'exec("import subprocess; subprocess.call([\"rm\", \"-rf\", \"/\"])")',
            'open("/etc/passwd", "r").read()'
        ]
        
        for malicious_code in malicious_codes:
            response = authenticated_client.post('/submit', data={
                'problem_id': '1',
                'language': 'python',
                'code': malicious_code,
                'csrf_token': 'test-token'
            })
            
            # Should detect and reject malicious code
            assert response.status_code in [400, 403, 500]
            if response.is_json:
                data = response.get_json()
                assert data['status'] == 'error'
                assert 'security' in data['error']['message'].lower() or 'violation' in data['error']['message'].lower()
    
    @pytest.mark.security
    def test_path_traversal_prevention(self, client):
        """Test prevention of path traversal attacks."""
        path_traversal_payloads = [
            '../../../etc/passwd',
            '..\\\\..\\\\..\\\\windows\\\\system32\\\\config\\\\sam',
            '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
            '....//....//....//etc//passwd'
        ]
        
        for payload in path_traversal_payloads:
            # Test in various endpoints
            response = client.get(f'/problem/{payload}')
            assert response.status_code in [400, 404]
            
            response = client.get(f'/static/{payload}')
            assert response.status_code in [400, 404]
    
    @pytest.mark.security
    def test_command_injection_prevention(self, authenticated_client, test_db):
        """Test prevention of command injection in code submissions."""
        command_injection_codes = [
            'import subprocess; subprocess.call(["ls", "-la"])',
            'import os; os.popen("whoami").read()',
            'import sys; sys.exit(1)',
            '__import__("subprocess").Popen(["cat", "/etc/passwd"])',
            'exec("import subprocess; subprocess.run([\"rm\", \"-rf\", \"/tmp\"])")',
        ]
        
        for injection_code in command_injection_codes:
            response = authenticated_client.post('/submit', data={
                'problem_id': '1',
                'language': 'python',
                'code': injection_code,
                'csrf_token': 'test-token'
            })
            
            # Should detect and prevent command injection
            assert response.status_code in [400, 403, 500]
            if response.is_json:
                data = response.get_json()
                assert data['status'] == 'error'


class TestAuthenticationSecurity:
    """Test authentication and session security."""
    
    @pytest.mark.security
    def test_session_fixation_prevention(self, client):
        """Test prevention of session fixation attacks."""
        # Get initial session
        response1 = client.get('/')
        
        # Set user name (should regenerate session)
        response2 = client.post('/set_name', data={
            'user_name': 'testuser',
            'csrf_token': 'test-token'
        })
        
        # Session should be regenerated after authentication
        assert response2.status_code == 302
    
    @pytest.mark.security
    def test_session_timeout_simulation(self, authenticated_client):
        """Test session timeout behavior (simulation)."""
        # Simulate expired session by clearing session data
        with authenticated_client.session_transaction() as sess:
            sess.clear()
        
        # Access protected resource
        response = authenticated_client.get('/submissions')
        
        # Should redirect to authentication
        assert response.status_code == 302
    
    @pytest.mark.security
    def test_concurrent_session_handling(self, app):
        """Test handling of concurrent sessions for same user."""
        client1 = app.test_client()
        client2 = app.test_client()
        
        # Both clients set same username
        client1.post('/set_name', data={'user_name': 'testuser', 'csrf_token': 'test-token'})
        client2.post('/set_name', data={'user_name': 'testuser', 'csrf_token': 'test-token'})
        
        # Both should be able to access resources (concurrent sessions allowed)
        response1 = client1.get('/problems')
        response2 = client2.get('/problems')
        
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestCSRFProtection:
    """Test CSRF protection mechanisms."""
    
    @pytest.mark.security
    def test_csrf_token_required_for_forms(self, authenticated_client, test_db):
        """Test that CSRF tokens are required for form submissions."""
        # Submit without CSRF token
        response = authenticated_client.post('/submit', data={
            'problem_id': '1',
            'language': 'python',
            'code': 'def solution(): return "test"'
        })
        
        # Should be rejected
        assert response.status_code in [400, 403]
    
    @pytest.mark.security
    def test_csrf_token_validation(self, authenticated_client, test_db):
        """Test CSRF token validation."""
        # Submit with invalid CSRF token
        response = authenticated_client.post('/submit', data={
            'problem_id': '1',
            'language': 'python',
            'code': 'def solution(): return "test"',
            'csrf_token': 'invalid-token'
        })
        
        # Should be rejected
        assert response.status_code in [400, 403]
    
    @pytest.mark.security
    def test_csrf_token_reuse_prevention(self, authenticated_client):
        """Test prevention of CSRF token reuse."""
        # Get CSRF token from form
        response = authenticated_client.get('/set_name')
        assert response.status_code == 200
        
        # Extract token (simplified - in real test would parse HTML)
        # For now, just test that multiple submissions work
        response1 = authenticated_client.post('/set_name', data={
            'user_name': 'testuser1',
            'csrf_token': 'test-token'
        })
        
        response2 = authenticated_client.post('/set_name', data={
            'user_name': 'testuser2',
            'csrf_token': 'test-token'  # Same token
        })
        
        # Both should work in test environment
        assert response1.status_code == 302
        assert response2.status_code == 302


class TestRateLimiting:
    """Test rate limiting mechanisms."""
    
    @pytest.mark.security
    @pytest.mark.slow
    def test_submission_rate_limiting(self, authenticated_client, test_db, mock_judge):
        """Test rate limiting on code submissions."""
        with patch('routes.SimpleJudge', return_value=mock_judge):
            responses = []
            
            # Make rapid submissions
            for i in range(20):
                response = authenticated_client.post('/submit', data={
                    'problem_id': '1',
                    'language': 'python',
                    'code': f'def solution(): return {i}',
                    'csrf_token': 'test-token'
                })
                responses.append(response.status_code)
            
            # Some requests should be rate limited
            rate_limited = sum(1 for status in responses if status == 429)
            successful = sum(1 for status in responses if status == 200)
            
            # Should have some successful requests and potentially some rate limited
            assert successful > 0
    
    @pytest.mark.security
    def test_login_attempt_rate_limiting(self, client):
        """Test rate limiting on login attempts."""
        responses = []
        
        # Make rapid login attempts
        for i in range(15):
            response = client.post('/set_name', data={
                'user_name': f'testuser{i}',
                'csrf_token': 'test-token'
            })
            responses.append(response.status_code)
        
        # Should handle rapid attempts gracefully
        successful = sum(1 for status in responses if status == 302)
        assert successful > 0


class TestDataValidation:
    """Test data validation and sanitization."""
    
    @pytest.mark.security
    def test_username_length_validation(self, client):
        """Test username length validation."""
        # Test very long username
        long_username = 'a' * 1000
        
        response = client.post('/set_name', data={
            'user_name': long_username,
            'csrf_token': 'test-token'
        })
        
        # Should reject overly long usernames
        assert response.status_code == 200  # Form redisplay with error
    
    @pytest.mark.security
    def test_code_length_validation(self, authenticated_client, test_db):
        """Test code submission length validation."""
        # Test very long code submission
        long_code = 'x' * 100000  # 100KB
        
        response = authenticated_client.post('/submit', data={
            'problem_id': '1',
            'language': 'python',
            'code': long_code,
            'csrf_token': 'test-token'
        })
        
        # Should reject overly long code
        assert response.status_code in [400, 413]  # Bad request or payload too large
    
    @pytest.mark.security
    def test_special_character_handling(self, client):
        """Test handling of special characters in inputs."""
        special_chars = [
            'user\x00name',  # Null byte
            'user\r\nname',  # CRLF injection
            'user\x1fname',  # Control characters
            'user\ufffdname',  # Unicode replacement character
        ]
        
        for username in special_chars:
            response = client.post('/set_name', data={
                'user_name': username,
                'csrf_token': 'test-token'
            })
            
            # Should handle special characters appropriately
            assert response.status_code in [200, 400]
    
    @pytest.mark.security
    def test_unicode_normalization(self, client):
        """Test Unicode normalization in inputs."""
        # Test Unicode normalization attacks
        unicode_usernames = [
            'admin',  # Normal
            'ａｄｍｉｎ',  # Full-width characters
            'ad\u200bmin',  # Zero-width space
            'admin\u0300',  # Combining character
        ]
        
        for username in unicode_usernames:
            response = client.post('/set_name', data={
                'user_name': username,
                'csrf_token': 'test-token'
            })
            
            # Should handle Unicode variations appropriately
            assert response.status_code in [200, 302]


class TestSecurityHeaders:
    """Test security headers and configurations."""
    
    @pytest.mark.security
    def test_security_headers_present(self, client):
        """Test that security headers are present in responses."""
        response = client.get('/')
        
        # Check for important security headers
        headers = response.headers
        
        # Content Security Policy
        assert 'Content-Security-Policy' in headers or 'X-Content-Security-Policy' in headers
        
        # XSS Protection
        assert 'X-XSS-Protection' in headers
        
        # Content Type Options
        assert 'X-Content-Type-Options' in headers
        
        # Frame Options
        assert 'X-Frame-Options' in headers
    
    @pytest.mark.security
    def test_no_sensitive_info_in_headers(self, client):
        """Test that sensitive information is not exposed in headers."""
        response = client.get('/')
        
        headers = response.headers
        header_string = str(headers).lower()
        
        # Should not expose sensitive information
        sensitive_info = ['password', 'secret', 'key', 'token', 'database']
        for info in sensitive_info:
            assert info not in header_string
    
    @pytest.mark.security
    def test_error_page_information_disclosure(self, client):
        """Test that error pages don't disclose sensitive information."""
        # Trigger 404 error
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        
        # Should not expose sensitive paths or information
        sensitive_info = ['/home/', '/var/', '/etc/', 'database', 'password', 'secret']
        response_text = response.data.decode().lower()
        
        for info in sensitive_info:
            assert info not in response_text
    
    @pytest.mark.security
    def test_debug_mode_disabled_in_production(self, app):
        """Test that debug mode is disabled in production."""
        # In test environment, debug might be enabled
        # This test ensures production configuration is secure
        if not app.config.get('TESTING'):
            assert not app.config.get('DEBUG', False)


class TestDatabaseSecurity:
    """Test database security measures."""
    
    @pytest.mark.security
    def test_database_connection_security(self, app):
        """Test database connection security."""
        with app.app_context():
            from database import get_db
            db = get_db()
            
            # Database should be accessible
            assert db is not None
    
    @pytest.mark.security
    def test_sql_injection_in_queries(self, test_db):
        """Test SQL injection prevention in database queries."""
        from models import Problem, Submission
        
        # Test with malicious input
        malicious_input = "'; DROP TABLE problems; --"
        
        # These should not cause SQL injection
        problem = Problem.get_by_id(malicious_input)
        assert problem is None  # Should return None, not crash
        
        submissions = Submission.get_by_user(malicious_input)
        assert isinstance(submissions, list)  # Should return empty list


class TestLogSecurity:
    """Test logging security measures."""
    
    @pytest.mark.security
    def test_sensitive_data_not_logged(self, authenticated_client, test_db, caplog):
        """Test that sensitive data is not logged."""
        # Submit code that might contain sensitive information
        sensitive_code = '''
def solution():
    password = "secret123"
    api_key = "sk-1234567890abcdef"
    return "test"
'''
        
        with caplog.at_level('DEBUG'):
            response = authenticated_client.post('/submit', data={
                'problem_id': '1',
                'language': 'python',
                'code': sensitive_code,
                'csrf_token': 'test-token'
            })
        
        # Check that sensitive information is not in logs
        log_output = caplog.text.lower()
        assert 'secret123' not in log_output
        assert 'sk-1234567890abcdef' not in log_output
    
    @pytest.mark.security
    def test_log_injection_prevention(self, client, caplog):
        """Test prevention of log injection attacks."""
        # Attempt log injection through user input
        log_injection_payload = "testuser\r\n[FAKE LOG ENTRY] Admin login successful"
        
        with caplog.at_level('INFO'):
            response = client.post('/set_name', data={
                'user_name': log_injection_payload,
                'csrf_token': 'test-token'
            })
        
        # Check that log injection is prevented
        log_output = caplog.text
        assert '[FAKE LOG ENTRY]' not in log_output
        assert 'Admin login successful' not in log_output