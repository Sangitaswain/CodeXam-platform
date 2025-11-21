"""
CodeXam Configuration Management
Environment-specific configuration for different deployment scenarios
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    
    # Judge Engine Configuration
    JUDGE_TIMEOUT = int(os.environ.get('JUDGE_TIMEOUT', '5'))
    JUDGE_MEMORY_LIMIT = int(os.environ.get('JUDGE_MEMORY_LIMIT', str(128 * 1024 * 1024)))
    
    # Performance Monitoring
    ENABLE_PERFORMANCE_MONITORING = os.environ.get('ENABLE_PERFORMANCE_MONITORING', 'True').lower() == 'true'
    PERFORMANCE_LOG_LEVEL = os.environ.get('PERFORMANCE_LOG_LEVEL', 'INFO')
    
    # Cache Configuration
    CACHE_TTL_DEFAULT = int(os.environ.get('CACHE_TTL_DEFAULT', '300'))
    CACHE_TTL_PLATFORM_STATS = int(os.environ.get('CACHE_TTL_PLATFORM_STATS', '300'))
    CACHE_TTL_LEADERBOARD = int(os.environ.get('CACHE_TTL_LEADERBOARD', '120'))
    CACHE_TTL_USER_SUBMISSIONS = int(os.environ.get('CACHE_TTL_USER_SUBMISSIONS', '60'))
    CACHE_TTL_PROBLEMS = int(os.environ.get('CACHE_TTL_PROBLEMS', '600'))
    
    # Security Configuration
    CSRF_ENABLED = os.environ.get('CSRF_ENABLED', 'True').lower() == 'true'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Admin Configuration
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-this-password')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'codexam.log')
    LOG_MAX_SIZE = int(os.environ.get('LOG_MAX_SIZE', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', '5'))
    
    # Asset Optimization
    MINIFY_ASSETS = os.environ.get('MINIFY_ASSETS', 'True').lower() == 'true'
    ENABLE_GZIP = os.environ.get('ENABLE_GZIP', 'True').lower() == 'true'
    STATIC_URL_PATH = os.environ.get('STATIC_URL_PATH', '/static')
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE', '60'))
    RATE_LIMIT_BURST = int(os.environ.get('RATE_LIMIT_BURST', '10'))
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration."""
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production' and not cls.DEBUG:
            raise ValueError("SECRET_KEY must be set in production")
        
        if cls.ADMIN_PASSWORD == 'change-this-password' and not cls.DEBUG:
            raise ValueError("ADMIN_PASSWORD must be set in production")

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'
    PERFORMANCE_LOG_LEVEL = 'DEBUG'
    
    # Shorter cache TTLs for development
    CACHE_TTL_DEFAULT = 60
    CACHE_TTL_PLATFORM_STATS = 60
    CACHE_TTL_LEADERBOARD = 30
    CACHE_TTL_USER_SUBMISSIONS = 30
    CACHE_TTL_PROBLEMS = 120
    
    # Development tools
    ENABLE_DEBUG_TOOLBAR = os.environ.get('ENABLE_DEBUG_TOOLBAR', 'False').lower() == 'true'
    ENABLE_PROFILER = os.environ.get('ENABLE_PROFILER', 'False').lower() == 'true'

class TestingConfig(Config):
    """Testing configuration."""
    
    DEBUG = False
    TESTING = True
    
    # Use in-memory database for testing
    DATABASE_URL = 'sqlite:///:memory:'
    
    # Disable performance monitoring in tests
    ENABLE_PERFORMANCE_MONITORING = False
    
    # Shorter timeouts for faster tests
    JUDGE_TIMEOUT = 2
    
    # Disable caching in tests
    CACHE_TTL_DEFAULT = 0
    CACHE_TTL_PLATFORM_STATS = 0
    CACHE_TTL_LEADERBOARD = 0
    CACHE_TTL_USER_SUBMISSIONS = 0
    CACHE_TTL_PROBLEMS = 0
    
    # Disable rate limiting in tests
    RATE_LIMIT_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Enhanced security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    PERFORMANCE_LOG_LEVEL = 'INFO'
    
    # Longer cache TTLs for production
    CACHE_TTL_DEFAULT = 600
    CACHE_TTL_PLATFORM_STATS = 600
    CACHE_TTL_LEADERBOARD = 300
    CACHE_TTL_USER_SUBMISSIONS = 120
    CACHE_TTL_PROBLEMS = 1800
    
    # Enable all optimizations
    MINIFY_ASSETS = True
    ENABLE_GZIP = True
    
    @classmethod
    def validate(cls) -> None:
        """Validate production configuration."""
        super().validate()
        
        # Additional production validations
        if not cls.DATABASE_URL.startswith(('postgresql://', 'mysql://', 'sqlite:///')):
            raise ValueError("Invalid DATABASE_URL format")
        
        if cls.DATABASE_URL.startswith('sqlite:///') and not cls.DATABASE_URL.endswith('.db'):
            raise ValueError("SQLite database should have .db extension")

class StagingConfig(ProductionConfig):
    """Staging configuration (similar to production but with some debug features)."""
    
    # Allow some debugging in staging
    LOG_LEVEL = 'INFO'
    PERFORMANCE_LOG_LEVEL = 'DEBUG'
    
    # Shorter cache TTLs for testing
    CACHE_TTL_DEFAULT = 300
    CACHE_TTL_PLATFORM_STATS = 300
    CACHE_TTL_LEADERBOARD = 120
    CACHE_TTL_USER_SUBMISSIONS = 60
    CACHE_TTL_PROBLEMS = 600

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> Config:
    """Get configuration class based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = config_map.get(config_name, config_map['default'])
    
    # Validate configuration
    config_class.validate()
    
    return config_class

# Export current configuration
current_config = get_config()

# Configuration utilities
def get_database_url() -> str:
    """Get properly formatted database URL."""
    url = current_config.DATABASE_URL
    
    # Handle SQLite URL format
    if url.startswith('sqlite:///'):
        return url[10:]  # Remove 'sqlite:///'
    elif url.startswith('sqlite://'):
        return url[9:]   # Remove 'sqlite://'
    
    return url

def is_production() -> bool:
    """Check if running in production mode."""
    return isinstance(current_config, ProductionConfig)

def is_development() -> bool:
    """Check if running in development mode."""
    return isinstance(current_config, DevelopmentConfig)

def is_testing() -> bool:
    """Check if running in testing mode."""
    return isinstance(current_config, TestingConfig)

# Example usage and testing
if __name__ == "__main__":
    print("🔧 Testing configuration...")
    
    try:
        # Test different configurations
        dev_config = get_config('development')
        prod_config = get_config('production')
        test_config = get_config('testing')
        
        print(f"✅ Development config: DEBUG={dev_config.DEBUG}")
        print(f"✅ Production config: DEBUG={prod_config.DEBUG}")
        print(f"✅ Testing config: TESTING={test_config.TESTING}")
        
        print(f"✅ Database URL: {get_database_url()}")
        print(f"✅ Is production: {is_production()}")
        print(f"✅ Is development: {is_development()}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")