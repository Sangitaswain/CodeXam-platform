"""
Test cases for the main Flask application
"""

import pytest
import json
from app import create_app

class TestApp:
    """Test suite for main application functionality."""
    
    def test_app_creation(self):
        """Test that the Flask app can be created successfully."""
        app = create_app(testing=True)
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_app_config(self):
        """Test application configuration."""
        app = create_app(testing=True)
        
        # Test that required config keys exist
        assert 'SECRET_KEY' in app.config
        assert 'DATABASE_URL' in app.config
        assert 'JUDGE_TIMEOUT' in app.config
        assert 'JUDGE_MEMORY_LIMIT' in app.config
        
        # Test default values
        assert app.config['JUDGE_TIMEOUT'] == 5
        assert app.config['JUDGE_MEMORY_LIMIT'] == 128 * 1024 * 1024

class TestRoutes:
    """Test suite for application routes."""
    
    def test_index_route(self, client):
        """Test the index route returns successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'CodeXam' in response.data
        assert b'Welcome to CodeXam' in response.data
    
    def test_health_check_route(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'message' in data
        assert 'debug' in data
    
    def test_nonexistent_route(self, client):
        """Test that nonexistent routes return 404."""
        response = client.get('/nonexistent')
        assert response.status_code == 404

class TestTemplates:
    """Test suite for template rendering."""
    
    def test_base_template_elements(self, client):
        """Test that base template elements are present."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for essential HTML elements
        assert b'<!DOCTYPE html>' in response.data
        assert b'<html lang="en">' in response.data
        assert b'CodeXam' in response.data
        assert b'Bootstrap' in response.data or b'bootstrap' in response.data
    
    def test_index_template_content(self, client):
        """Test that index template has expected content."""
        response = client.get('/')
        assert response.status_code == 200
        
        # Check for key content elements
        assert b'Welcome to CodeXam' in response.data
        assert b'Multi-Language Support' in response.data
        assert b'Instant Feedback' in response.data
        assert b'Track Progress' in response.data