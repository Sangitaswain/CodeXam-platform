"""
CodeXam - Coding Challenge Platform
Main Flask application entry point

This module provides the main Flask application factory and configuration
for the CodeXam coding challenge platform with enhanced error handling,
security features, and comprehensive monitoring.
"""

import logging
import os
import sys
from typing import Optional

from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException

from database import init_app
from performance_monitor import init_performance_monitoring

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('codexam.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when application configuration is invalid."""
    pass


def validate_configuration(config: dict) -> None:
    """
    Validate application configuration for security and correctness.
    
    Args:
        config: Flask application configuration dictionary
        
    Raises:
        ConfigurationError: If configuration is invalid or insecure
    """
    # Validate secret key in production
    if not config.get('TESTING', False) and not config.get('DEBUG', False):
        secret_key = config.get('SECRET_KEY', '')
        if not secret_key or secret_key == 'dev-secret-key-change-in-production':
            raise ConfigurationError(
                "SECRET_KEY must be set to a secure value in production"
            )
        if len(secret_key) < 32:
            raise ConfigurationError(
                "SECRET_KEY must be at least 32 characters long"
            )
    
    # Validate judge configuration
    judge_timeout = config.get('JUDGE_TIMEOUT', 0)
    if judge_timeout <= 0 or judge_timeout > 60:
        raise ConfigurationError(
            f"JUDGE_TIMEOUT must be between 1 and 60 seconds, got {judge_timeout}"
        )
    
    judge_memory_limit = config.get('JUDGE_MEMORY_LIMIT', 0)
    if judge_memory_limit <= 0 or judge_memory_limit > 1024 * 1024 * 1024:  # 1GB max
        raise ConfigurationError(
            f"JUDGE_MEMORY_LIMIT must be between 1 and 1GB, got {judge_memory_limit}"
        )


def configure_security_headers(app: Flask) -> None:
    """
    Configure security headers for the Flask application.
    
    Args:
        app: Flask application instance
    """
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (basic)
        if not app.config.get('DEBUG', False):
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "img-src 'self' data:; "
                "connect-src 'self';"
            )
        
        return response


def configure_error_handlers(app: Flask) -> None:
    """
    Configure comprehensive error handlers for the Flask application.
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors."""
        logger.warning(f"Bad request: {request.url} - {error}")
        if request.is_json:
            return jsonify({
                'error': 'Bad Request',
                'message': 'The request could not be understood by the server',
                'status_code': 400
            }), 400
        return render_template('error.html', 
                             error={'message': 'Bad Request', 'code': 400}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle not found errors."""
        logger.info(f"Page not found: {request.url}")
        if request.is_json:
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found',
                'status_code': 404
            }), 404
        return render_template('error.html', 
                             error={'message': 'Page Not Found', 'code': 404}), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle rate limit exceeded errors."""
        logger.warning(f"Rate limit exceeded: {request.remote_addr}")
        if request.is_json:
            return jsonify({
                'error': 'Rate Limit Exceeded',
                'message': 'Too many requests. Please try again later.',
                'status_code': 429,
                'retry_after': 60
            }), 429
        return render_template('error.html', 
                             error={'message': 'Too Many Requests', 'code': 429}), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle internal server errors."""
        logger.error(f"Internal server error: {error}", exc_info=True)
        if request.is_json:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred',
                'status_code': 500
            }), 500
        return render_template('error.html', 
                             error={'message': 'Internal Server Error', 'code': 500}), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle all other HTTP exceptions."""
        logger.warning(f"HTTP exception: {error.code} - {error.description}")
        if request.is_json:
            return jsonify({
                'error': error.name,
                'message': error.description,
                'status_code': error.code
            }), error.code
        return render_template('error.html', 
                             error={'message': error.description, 'code': error.code}), error.code


def configure_logging(app: Flask) -> None:
    """
    Configure application logging with proper handlers and formatters.
    
    Args:
        app: Flask application instance
    """
    if not app.config.get('DEBUG', False):
        # Production logging configuration
        file_handler = logging.FileHandler('codexam.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('CodeXam application startup')
    
    # Request logging
    @app.before_request
    def log_request_info():
        """Log request information for monitoring."""
        if not app.config.get('DEBUG', False):
            app.logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")
    
    @app.after_request
    def log_response_info(response):
        """Log response information for monitoring."""
        if not app.config.get('DEBUG', False):
            app.logger.info(f"Response: {response.status_code} for {request.url}")
        return response


def create_app(testing: bool = False) -> Flask:
    """
    Create and configure the Flask application with enhanced security and error handling.
    
    Args:
        testing: Whether to configure the app for testing mode
        
    Returns:
        Configured Flask application instance
        
    Raises:
        ConfigurationError: If configuration values are invalid
        RuntimeError: If application initialization fails
    """
    try:
        app = Flask(__name__)
        
        # Basic configuration
        app.config['SECRET_KEY'] = os.environ.get(
            'SECRET_KEY', 
            'dev-secret-key-change-in-production'
        )
        app.config['DEBUG'] = os.environ.get('FLASK_ENV') == 'development'
        app.config['TESTING'] = testing
        
        # Database configuration
        if testing:
            app.config['DATABASE_URL'] = 'sqlite:///:memory:'
        else:
            app.config['DATABASE_URL'] = os.environ.get(
                'DATABASE_URL', 
                'sqlite:///database.db'
            )
        
        # Judge engine configuration with validation
        try:
            app.config['JUDGE_TIMEOUT'] = int(os.environ.get('JUDGE_TIMEOUT', '5'))
            app.config['JUDGE_MEMORY_LIMIT'] = int(
                os.environ.get('JUDGE_MEMORY_LIMIT', str(128 * 1024 * 1024))
            )
        except ValueError as e:
            raise ConfigurationError(f"Invalid judge configuration: {e}")
        
        # Additional security configuration
        app.config['SESSION_COOKIE_SECURE'] = not app.config['DEBUG']
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
        
        # Rate limiting configuration
        app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
        app.config['RATELIMIT_DEFAULT'] = '100 per hour'
        
        # Validate configuration
        validate_configuration(app.config)
        
        # Configure security headers
        configure_security_headers(app)
        
        # Configure error handlers
        configure_error_handlers(app)
        
        # Configure logging
        configure_logging(app)
        
        # Initialize database
        try:
            init_app(app)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise RuntimeError(f"Database initialization failed: {e}")
        
        # Initialize performance monitoring
        try:
            init_performance_monitoring(app)
            logger.info("Performance monitoring initialized successfully")
        except Exception as e:
            logger.warning(f"Performance monitoring initialization failed: {e}")
            # Continue without performance monitoring
        
        # Register routes
        try:
            from routes import register_routes
            register_routes(app)
            logger.info("Routes registered successfully")
        except Exception as e:
            logger.error(f"Route registration failed: {e}")
            raise RuntimeError(f"Route registration failed: {e}")
        
        # Register template filters and functions
        register_template_helpers(app)
        
        logger.info("CodeXam application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Application creation failed: {e}", exc_info=True)
        raise


def register_template_helpers(app: Flask) -> None:
    """
    Register template filters and helper functions.
    
    Args:
        app: Flask application instance
    """
    @app.template_filter('nl2br')
    def nl2br_filter(text: Optional[str]) -> str:
        """
        Convert newlines to HTML line breaks.
        
        Args:
            text: Input text with potential newlines
            
        Returns:
            Text with newlines converted to <br> tags
        """
        if not text:
            return text or ''
        return text.replace('\n', '<br>')
    
    @app.template_filter('truncate_code')
    def truncate_code_filter(code: str, max_length: int = 100) -> str:
        """
        Truncate code for display purposes.
        
        Args:
            code: Source code to truncate
            max_length: Maximum length before truncation
            
        Returns:
            Truncated code with ellipsis if needed
        """
        if not code:
            return ''
        if len(code) <= max_length:
            return code
        return code[:max_length] + '...'
    
    @app.template_filter('format_time')
    def format_time_filter(seconds: Optional[float]) -> str:
        """
        Format execution time for display.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        if seconds is None:
            return 'N/A'
        if seconds < 0.001:
            return '<1ms'
        elif seconds < 1:
            return f'{seconds*1000:.0f}ms'
        else:
            return f'{seconds:.2f}s'
    
    @app.template_filter('format_memory')
    def format_memory_filter(bytes_used: Optional[int]) -> str:
        """
        Format memory usage for display.
        
        Args:
            bytes_used: Memory usage in bytes
            
        Returns:
            Formatted memory string
        """
        if bytes_used is None or bytes_used <= 0:
            return 'N/A'
        
        if bytes_used < 1024:
            return f'{bytes_used}B'
        elif bytes_used < 1024 * 1024:
            return f'{bytes_used/1024:.1f}KB'
        else:
            return f'{bytes_used/(1024*1024):.1f}MB'
    
    @app.context_processor
    def inject_global_vars():
        """Inject global variables into all templates."""
        return {
            'app_name': 'CodeXam',
            'app_version': '2.0.0',
            'current_year': 2024
        }

# Create the application instance
app = create_app()


def validate_environment() -> bool:
    """
    Validate environment variables and system requirements.
    
    Returns:
        True if environment is valid, False otherwise
    """
    required_vars = []
    missing_vars = []
    
    # Check for required environment variables in production
    if os.environ.get('FLASK_ENV') != 'development':
        required_vars = ['SECRET_KEY']
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Validate port number
    try:
        port = int(os.environ.get('PORT', '5000'))
        if port < 1 or port > 65535:
            logger.error(f"Invalid port number: {port}")
            return False
    except ValueError:
        logger.error("PORT environment variable must be a valid integer")
        return False
    
    return True


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown."""
    import signal
    
    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        # Perform cleanup operations here
        from database import close_db
        close_db()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main() -> None:
    """
    Main entry point for development server with enhanced error handling.
    
    Raises:
        SystemExit: If environment validation fails or server startup fails
    """
    try:
        # Validate environment
        if not validate_environment():
            logger.error("Environment validation failed")
            sys.exit(1)
        
        # Set up signal handlers
        setup_signal_handlers()
        
        # Development server configuration
        debug_mode = os.environ.get('FLASK_ENV') == 'development'
        
        try:
            port = int(os.environ.get('PORT', '5000'))
        except ValueError:
            logger.warning("Invalid PORT environment variable, using default 5000")
            port = 5000
        
        # Server startup logging
        logger.info("Starting CodeXam server...")
        logger.info(f"Debug mode: {debug_mode}")
        logger.info(f"Port: {port}")
        logger.info(f"Database: {app.config.get('DATABASE_URL', 'Not configured')}")
        
        if debug_mode:
            print("=" * 50)
            print("🚀 CodeXam Development Server")
            print("=" * 50)
            print(f"Debug mode: {debug_mode}")
            print(f"Port: {port}")
            print(f"Access the application at: http://localhost:{port}")
            print("Press Ctrl+C to stop the server")
            print("=" * 50)
        
        # Start the Flask development server
        app.run(
            debug=debug_mode,
            host='0.0.0.0',
            port=port,
            threaded=True,
            use_reloader=debug_mode,
            use_debugger=debug_mode
        )
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server startup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()