"""
CodeXam Configuration
Application configuration for different environments
"""

import os
from typing import Optional

class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = False
    TESTING: bool = False
    
    # Database Configuration
    DATABASE_URL: str = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    
    # Judge Engine Configuration
    JUDGE_TIMEOUT: int = int(os.environ.get('JUDGE_TIMEOUT', '5'))
    JUDGE_MEMORY_LIMIT: int = int(os.environ.get('JUDGE_MEMORY_LIMIT', str(128 * 1024 * 1024)))
    SUPPORTED_LANGUAGES: list = ['python', 'javascript', 'java', 'cpp']
    
    # Security Configuration
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_TIME_LIMIT: int = 3600  # 1 hour
    
    # Application Limits
    MAX_CODE_LENGTH: int = int(os.environ.get('MAX_CODE_LENGTH', '10000'))
    MAX_SUBMISSIONS_PER_HOUR: int = int(os.environ.get('MAX_SUBMISSIONS_PER_HOUR', '100'))
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings."""
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production' and not cls.DEBUG:
            raise ValueError("SECRET_KEY must be set in production")
        
        if cls.JUDGE_TIMEOUT <= 0:
            raise ValueError("JUDGE_TIMEOUT must be positive")
        
        if cls.JUDGE_MEMORY_LIMIT <= 0:
            raise ValueError("JUDGE_MEMORY_LIMIT must be positive")

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///database.db')

class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    JUDGE_TIMEOUT = 2  # Shorter timeout for tests

class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    @classmethod
    def validate(cls) -> None:
        """Additional production validation."""
        super().validate()
        
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in production")

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration class based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])