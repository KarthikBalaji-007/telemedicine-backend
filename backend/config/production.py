"""
Production configuration for AI Telemedicine Platform
Settings for production deployment
"""

import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration settings"""
    
    # Flask settings
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
    
    # Database settings
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    FIREBASE_PRIVATE_KEY = os.environ.get('FIREBASE_PRIVATE_KEY')
    FIREBASE_CLIENT_EMAIL = os.environ.get('FIREBASE_CLIENT_EMAIL')
    
    # Security settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'change-this-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_EXPIRY_HOURS', 24)))
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('FRONTEND_URLS', '').split(',')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = os.environ.get('RATE_LIMIT_PER_MINUTE', '60/minute')
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/production.log'
    
    # AI Service settings
    AI_SERVICE_URL = os.environ.get('AI_SERVICE_URL')
    AI_SERVICE_API_KEY = os.environ.get('AI_SERVICE_API_KEY')
    AI_SERVICE_TIMEOUT = int(os.environ.get('AI_SERVICE_TIMEOUT', 30))
    
    # Performance settings
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))
    
    # Health check settings
    HEALTH_CHECK_ENABLED = True
    HEALTH_CHECK_ENDPOINT = '/health'
    
    @staticmethod
    def validate_production_config():
        """Validate that all required production settings are configured"""
        required_vars = [
            'SECRET_KEY',
            'FIREBASE_PROJECT_ID',
            'FIREBASE_PRIVATE_KEY',
            'FIREBASE_CLIENT_EMAIL',
            'JWT_SECRET_KEY',
            'AI_SERVICE_URL',
            'AI_SERVICE_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var) or os.environ.get(var) in ['your-', 'change-this']:
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required production environment variables: {', '.join(missing_vars)}")
        
        return True

class DevelopmentConfig:
    """Development configuration settings"""
    
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'dev-secret-key'
    
    # Development database (mock mode)
    FIREBASE_PROJECT_ID = 'dev-project'
    
    # Development security (less strict)
    JWT_SECRET_KEY = 'dev-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Development CORS (allow all)
    CORS_ORIGINS = ['*']
    
    # Development rate limiting (more permissive)
    RATELIMIT_DEFAULT = '1000/minute'
    
    # Development logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'logs/development.log'
    
    # Mock AI service
    AI_SERVICE_URL = 'http://localhost:8000'
    AI_SERVICE_API_KEY = 'dev-api-key'
    AI_SERVICE_TIMEOUT = 30

class TestingConfig:
    """Testing configuration settings"""
    
    DEBUG = False
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    
    # Test database (mock mode)
    FIREBASE_PROJECT_ID = 'test-project'
    
    # Test security
    JWT_SECRET_KEY = 'test-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)  # Short expiry for tests
    
    # Test CORS
    CORS_ORIGINS = ['http://localhost:3000']
    
    # Test rate limiting (disabled)
    RATELIMIT_DEFAULT = '10000/minute'
    
    # Test logging
    LOG_LEVEL = 'WARNING'
    LOG_FILE = 'logs/testing.log'
    
    # Mock AI service for tests
    AI_SERVICE_URL = 'http://localhost:8000'
    AI_SERVICE_API_KEY = 'test-api-key'
    AI_SERVICE_TIMEOUT = 5

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
