#!/usr/bin/env python3
"""
Comprehensive Test Suite for System Info Modal
Tests all components, API endpoints, and functionality
"""

import pytest
import json
import time
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from init_db import initialize_database

# Import API helpers
from api_helpers import (
    get_real_system_info, get_mock_system_info, get_enhanced_platform_stats,
    perform_health_checks, format_ascii_table, format_ascii_chart
)
from routes import sanitize_system_info

class TestSystemInfoModalAPI:
    """Test suite for System Info Modal API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            with app.app_context():
                initialize_database(":memory:")
                yield client
    
    def test_system_info_endpoint(self, client):
        """Test /api/system-info endpoint."""
        response = client.get('/api/system-info')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'metadata' in data
        
        # Check required fields in system info
        system_data = data['data']
        assert 'platform' in system_data
        assert 'performance' in system_data
        assert 'database' in system_data
        assert 'timestamp' in system_data
        
        # Check platform info
        platform = system_data['platform']
        assert 'name' in platform
        assert 'version' in platform
        assert 'status' in platform
        assert 'uptime' in platform
        
        # Check performance info
        performance = system_data['performance']
        assert 'cpu_usage' in performance
        assert 'memory_usage' in performance
        assert 'disk_usage' in performance
        
        # Check database info
        database = system_data['database']
        assert 'status' in database
        assert 'response_time' in database
        assert 'health' in database
    
    def test_platform_stats_endpoint(self, client):
        """Test /api/platform-stats endpoint."""
        response = client.get('/api/platform-stats')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'metadata' in data
        
        # Check required fields in platform stats
        stats_data = data['data']
        assert 'basic' in stats_data
        assert 'languages' in stats_data
        assert 'problems' in stats_data
        assert 'activity' in stats_data
        
        # Check basic stats
        basic = stats_data['basic']
        assert 'total_problems' in basic
        assert 'total_submissions' in basic
        assert 'total_users' in basic
        assert 'success_rate' in basic
        
        # Check language stats
        languages = stats_data['languages']
        assert isinstance(languages, list)
        
        # Check difficulty distribution
        difficulty = stats_data['difficulty']
        assert 'Easy' in difficulty
        assert 'Medium' in difficulty
        assert 'Hard' in difficulty
    
    def test_health_check_endpoint(self, client):
        """Test /api/health-check endpoint."""
        response = client.get('/api/health-check')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'metadata' in data
        
        # Check health check data
        health_data = data['data']
        assert 'overall_status' in health_data
        assert 'checks' in health_data
        assert 'timestamp' in health_data
        
        # Check individual health checks
        checks = health_data['checks']
        assert 'database' in checks
        assert 'judge_engine' in checks
        assert 'file_system' in checks
        
        # Each check should have status and response_time
        for check_name, check_data in checks.items():
            assert 'status' in check_data
            assert 'response_time' in check_data
    
    def test_api_error_handling(self, client):
        """Test API error handling."""
        # Test non-existent endpoint
        response = client.get('/api/non-existent')
        assert response.status_code == 404
        
        # Test with invalid parameters (if applicable)
        response = client.get('/api/system-info?invalid=param')
        # Should still work but ignore invalid params
        assert response.status_code == 200
    
    def test_api_response_format(self, client):
        """Test consistent API response format."""
        endpoints = ['/api/system-info', '/api/platform-stats', '/api/health-check']
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            
            data = json.loads(response.data)
            
            # Check standard response structure
            assert 'status' in data
            assert 'data' in data
            assert 'metadata' in data
            
            # Check metadata structure
            metadata = data['metadata']
            assert 'timestamp' in metadata
            # Different endpoints may have different metadata fields
            # Just check that some version info exists
            has_version = 'version' in metadata or 'api_version' in metadata
            assert has_version, f"No version info in metadata: {metadata}"


class TestSystemInfoHelpers:
    """Test suite for system info helper functions."""
    
    def test_get_real_system_info(self):
        """Test real system info retrieval."""
        with patch('psutil.cpu_percent', return_value=25.5):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = 45.2
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value.percent = 12.8
                    with patch('psutil.boot_time', return_value=time.time() - 3600):
                        
                        info = get_real_system_info()
                        
                        assert 'platform' in info
                        assert 'performance' in info
                        assert 'database' in info
                        assert 'timestamp' in info
                        
                        # Check performance data
                        perf = info['performance']
                        assert perf['cpu_usage'] == 25.5
                        assert perf['memory_usage'] == 45.2
                        assert perf['disk_usage'] == 12.8
    
    def test_get_mock_system_info(self):
        """Test mock system info generation."""
        info = get_mock_system_info()
        
        assert 'platform' in info
        assert 'performance' in info
        assert 'database' in info
        assert 'timestamp' in info
        
        # Check that mock data has reasonable values
        perf = info['performance']
        assert 0 <= perf['cpu_usage'] <= 100
        assert 0 <= perf['memory_usage'] <= 100
        assert 0 <= perf['disk_usage'] <= 100
    
    def test_get_enhanced_platform_stats(self):
        """Test enhanced platform statistics."""
        with patch('models.Problem') as mock_problem:
            with patch('models.Submission') as mock_submission:
                # Mock database queries
                mock_problem.count.return_value = 150
                mock_submission.count.return_value = 8934
                
                stats = get_enhanced_platform_stats()
                
                assert 'basic' in stats
                assert 'languages' in stats
                assert 'problems' in stats
                assert 'activity' in stats
                
                # Check basic stats structure
                basic = stats['basic']
                assert 'total_problems' in basic
                assert 'total_submissions' in basic
                assert 'total_users' in basic
    
    def test_perform_health_checks(self):
        """Test health check functionality."""
        with patch('database.get_db') as mock_db:
            mock_db.return_value.execute.return_value.fetchone.return_value = (1,)
            
            health = perform_health_checks()
            
            assert 'overall_status' in health
            assert 'checks' in health
            assert 'timestamp' in health
            
            # Check individual health checks
            checks = health['checks']
            assert 'database' in checks
            # Note: Other checks may vary based on system configuration
    
    def test_sanitize_system_info(self):
        """Test system info sanitization."""
        raw_info = {
            'platform': {
                'name': 'CodeXam Elite Arena',
                'version': '2.1.0',
                'status': 'OPERATIONAL',
                'uptime': '72h 15m',
                'boot_time': '2025-01-01T00:00:00'  # Should be removed
            },
            'performance': {
                'cpu_usage': 25.5,
                'memory_usage': 45.2,
                'memory_total': 16.0,  # Should be removed
                'disk_total': 500.0    # Should be removed
            },
            'database': {
                'status': 'CONNECTED',
                'response_time': 2.5,
                'connections': 15,     # Should be removed
                'queries': 1247        # Should be removed
            },
            'timestamp': '2025-01-01T12:00:00'
        }
        
        sanitized = sanitize_system_info(raw_info)
        
        # Check that sensitive data is removed/sanitized
        assert 'boot_time' not in sanitized['platform']
        assert 'memory_total' not in sanitized['performance']
        assert 'disk_total' not in sanitized['performance']
        
        # Check that safe data is preserved
        assert sanitized['platform']['name'] == 'CodeXam Elite Arena'
        assert sanitized['platform']['status'] == 'OPERATIONAL'
        assert sanitized['database']['status'] == 'CONNECTED'
        assert 'timestamp' in sanitized
    
    def test_format_ascii_table(self):
        """Test ASCII table formatting."""
        headers = ['Language', 'Submissions', 'Success Rate']
        data = [
            ['Python', '3456', '72.3%'],
            ['JavaScript', '2134', '68.7%'],
            ['Java', '1876', '71.2%']
        ]
        
        table = format_ascii_table(data, headers)
        
        assert isinstance(table, str)
        assert 'Language' in table
        assert 'Python' in table
        assert '3456' in table
        assert '72.3%' in table
        
        # Check that table has proper formatting
        lines = table.split('\n')
        assert len(lines) >= 4  # Header + separator + data rows
    
    def test_format_ascii_chart(self):
        """Test ASCII chart formatting."""
        data = {
            'Easy': 45,
            'Medium': 35,
            'Hard': 20
        }
        
        chart = format_ascii_chart(data, title="Problem Difficulty Distribution")
        
        assert isinstance(chart, str)
        assert 'Problem Difficulty Distribution' in chart
        assert 'Easy' in chart
        assert 'Medium' in chart
        assert 'Hard' in chart
        
        # Check that chart has visual elements
        assert '█' in chart or '▓' in chart or '░' in chart


class TestSystemInfoModalIntegration:
    """Test suite for system info modal integration."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            with app.app_context():
                initialize_database(":memory:")
                yield client
    
    def test_modal_html_structure(self, client):
        """Test that modal HTML structure is present in templates."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for modal container
        assert 'systemInfoModal' in html_content
        assert 'system-info-modal' in html_content
        
        # Check for terminal container
        assert 'terminal-container' in html_content
        
        # Check for close button
        assert 'terminal-close-btn' in html_content
    
    def test_modal_css_inclusion(self, client):
        """Test that modal CSS is included."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        assert 'system-info-modal.css' in html_content
    
    def test_modal_js_inclusion(self, client):
        """Test that modal JavaScript is included."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        assert 'system-info-modal.js' in html_content
    
    def test_static_files_accessible(self, client):
        """Test that static files are accessible."""
        # Test CSS file
        response = client.get('/static/css/system-info-modal.css')
        assert response.status_code == 200
        assert 'text/css' in response.content_type
        
        # Test JavaScript file
        response = client.get('/static/js/system-info-modal.js')
        assert response.status_code == 200
        assert 'javascript' in response.content_type or 'text/plain' in response.content_type
    
    def test_system_info_button_integration(self, client):
        """Test that system info button is properly integrated."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for system info button
        assert 'showSystemInfoModal' in html_content or 'system-info-btn' in html_content
    
    def test_modal_accessibility_attributes(self, client):
        """Test that modal has proper accessibility attributes."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for ARIA attributes
        assert 'aria-hidden' in html_content
        assert 'role="dialog"' in html_content
        assert 'aria-modal' in html_content


class TestSystemInfoModalPerformance:
    """Test suite for system info modal performance."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            with app.app_context():
                initialize_database(":memory:")
                yield client
    
    def test_api_response_time(self, client):
        """Test that API endpoints respond within acceptable time."""
        endpoints = ['/api/system-info', '/api/platform-stats', '/api/health-check']
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = client.get('/api/system-info')
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        while not results.empty():
            result = results.get()
            assert result == 200
    
    def test_memory_usage(self, client):
        """Test that modal doesn't cause memory leaks."""
        import gc
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Make multiple requests
        for _ in range(10):
            response = client.get('/api/system-info')
            assert response.status_code == 200
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Check that object count hasn't grown significantly
        object_growth = final_objects - initial_objects
        assert object_growth < 100  # Allow some growth but not excessive


class TestSystemInfoModalSecurity:
    """Test suite for system info modal security."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            with app.app_context():
                initialize_database(":memory:")
                yield client
    
    def test_sensitive_data_filtering(self, client):
        """Test that sensitive data is filtered from responses."""
        response = client.get('/api/system-info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        response_text = json.dumps(data)
        
        # Check that sensitive keywords are not present
        sensitive_keywords = [
            'password', 'secret', 'key', 'token', 'credential',
            'SECRET_KEY', 'DATABASE_URL', 'API_KEY'
        ]
        
        for keyword in sensitive_keywords:
            assert keyword.lower() not in response_text.lower()
    
    def test_input_validation(self, client):
        """Test input validation for API endpoints."""
        # Test with malicious parameters
        malicious_params = [
            '?param=<script>alert("xss")</script>',
            '?param=../../etc/passwd',
            '?param=; DROP TABLE users; --',
            '?param=' + 'A' * 10000  # Very long parameter
        ]
        
        for param in malicious_params:
            response = client.get(f'/api/system-info{param}')
            # Should either ignore the parameter or return 400, but not crash
            assert response.status_code in [200, 400]
    
    def test_rate_limiting_simulation(self, client):
        """Test rate limiting behavior (simulated)."""
        # Make rapid requests
        responses = []
        for _ in range(20):
            response = client.get('/api/system-info')
            responses.append(response.status_code)
        
        # All requests should succeed in test environment
        # In production, rate limiting would kick in
        assert all(status == 200 for status in responses)
    
    def test_error_information_disclosure(self, client):
        """Test that errors don't disclose sensitive information."""
        # Try to trigger an error
        with patch('api_helpers.get_real_system_info', side_effect=Exception("Database connection failed")):
            response = client.get('/api/system-info')
            
            # Should return error but not expose internal details
            if response.status_code != 200:
                data = json.loads(response.data)
                error_message = data.get('message', '').lower()
                
                # Should not contain file paths or internal details
                assert '/home/' not in error_message
                assert 'traceback' not in error_message
                assert 'exception' not in error_message


class TestSystemInfoModalAccessibility:
    """Test suite for system info modal accessibility."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            with app.app_context():
                initialize_database(":memory:")
                yield client
    
    def test_aria_attributes(self, client):
        """Test that proper ARIA attributes are present."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for required ARIA attributes
        assert 'aria-hidden' in html_content
        assert 'role="dialog"' in html_content
        assert 'aria-modal="true"' in html_content
        assert 'aria-labelledby' in html_content or 'aria-label' in html_content
    
    def test_keyboard_navigation_support(self, client):
        """Test that keyboard navigation is supported."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for tabindex attributes
        assert 'tabindex' in html_content
        
        # Check for keyboard event handling
        assert 'keydown' in html_content or 'onkeydown' in html_content
    
    def test_screen_reader_support(self, client):
        """Test screen reader support elements."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for screen reader only content
        assert 'sr-only' in html_content or 'visually-hidden' in html_content
    
    def test_focus_management(self, client):
        """Test focus management in modal."""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.data.decode('utf-8')
        
        # Check for focusable elements
        focusable_elements = ['button', 'input', 'select', 'textarea', 'a href']
        has_focusable = any(element in html_content for element in focusable_elements)
        assert has_focusable


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])