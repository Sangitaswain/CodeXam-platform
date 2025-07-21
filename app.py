"""
CodeXam - Coding Challenge Platform
Main Flask application entry point
"""

import os
from flask import Flask
from dotenv import load_dotenv
from database import init_app

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
    
    # Register routes
    from routes import register_routes
    register_routes(app)
    
    # Register template filters
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks."""
        if not text:
            return text
        return text.replace('\n', '<br>')
    
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