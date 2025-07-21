"""
CodeXam - Coding Challenge Platform
Main Flask application entry point
"""

import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
from database import init_app, get_platform_stats

# Load environment variables
load_dotenv()

def create_app(testing=False):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = os.environ.get('FLASK_ENV') == 'development'
    app.config['TESTING'] = testing
    
    # Database configuration
    if testing:
        app.config['DATABASE_URL'] = 'sqlite:///:memory:'
    else:
        app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    
    # Judge engine configuration
    app.config['JUDGE_TIMEOUT'] = int(os.environ.get('JUDGE_TIMEOUT', '5'))
    app.config['JUDGE_MEMORY_LIMIT'] = int(os.environ.get('JUDGE_MEMORY_LIMIT', str(128 * 1024 * 1024)))
    
    # Initialize database
    init_app(app)
    
    # Basic route for testing
    @app.route('/')
    def index():
        """Landing page route."""
        try:
            stats = get_platform_stats()
            return render_template('index.html', stats=stats)
        except Exception as e:
            # Fallback if database is not available
            stats = {
                'total_problems': 0,
                'total_submissions': 0,
                'total_users': 0,
                'last_updated': 'N/A'
            }
            return render_template('index.html', stats=stats)
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for testing."""
        try:
            stats = get_platform_stats()
            return jsonify({
                'status': 'healthy',
                'message': 'CodeXam Flask application is running',
                'debug': app.config['DEBUG'],
                'database': 'connected',
                'stats': stats
            })
        except Exception as e:
            return jsonify({
                'status': 'degraded',
                'message': 'CodeXam Flask application is running',
                'debug': app.config['DEBUG'],
                'database': 'error',
                'error': str(e)
            })
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Development server configuration
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting CodeXam server...")
    print(f"Debug mode: {debug_mode}")
    print(f"Port: {port}")
    print(f"Access the application at: http://localhost:{port}")
    
    app.run(
        debug=debug_mode,
        host='0.0.0.0',
        port=port
    )