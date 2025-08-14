"""
Configuration settings for AI Telemedicine Platform
Environment-based configuration for development and production
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # Firebase configuration
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    FIREBASE_PRIVATE_KEY_ID = os.environ.get('FIREBASE_PRIVATE_KEY_ID')
    FIREBASE_PRIVATE_KEY = os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
    FIREBASE_CLIENT_EMAIL = os.environ.get('FIREBASE_CLIENT_EMAIL')
    FIREBASE_CLIENT_ID = os.environ.get('FIREBASE_CLIENT_ID')
    FIREBASE_AUTH_URI = os.environ.get('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth')
    FIREBASE_TOKEN_URI = os.environ.get('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token')
    
    # AI Service configuration (for Team Lead integration)
    # TODO: REQUEST FROM TEAM LEAD - Need AI service endpoint and authentication details
    AI_SERVICE_URL = os.environ.get('AI_SERVICE_URL', 'http://localhost:8000')  # Placeholder
    AI_SERVICE_API_KEY = os.environ.get('AI_SERVICE_API_KEY')
    AI_SERVICE_TIMEOUT = int(os.environ.get('AI_SERVICE_TIMEOUT', '30'))

    # Speech-to-Text Service configuration (for voice input processing)
    SPEECH_SERVICE_URL = os.environ.get('SPEECH_SERVICE_URL', 'https://speech.googleapis.com/v1/speech:recognize')
    SPEECH_API_KEY = os.environ.get('SPEECH_API_KEY')
    SPEECH_SERVICE_TIMEOUT = int(os.environ.get('SPEECH_SERVICE_TIMEOUT', '30'))

    # Multilingual Support Configuration
    SUPPORTED_LANGUAGES = os.environ.get('SUPPORTED_LANGUAGES', 'en,es,fr,de,pt,it,zh,ja,ar,hi').split(',')
    DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'en')
    
    # Frontend URLs for CORS (production)
    FRONTEND_URLS = os.environ.get('FRONTEND_URLS', '').split(',') if os.environ.get('FRONTEND_URLS') else []
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')  # For potential SQL database if needed
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Rate limiting (for future implementation)
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', '60'))
    
    # Validation settings
    MAX_SYMPTOMS_PER_REQUEST = int(os.environ.get('MAX_SYMPTOMS_PER_REQUEST', '10'))
    MAX_HISTORY_ITEMS = int(os.environ.get('MAX_HISTORY_ITEMS', '50'))
    
    @staticmethod
    def get_firebase_credentials():
        """Get Firebase credentials as dictionary for service account"""
        return {
            "type": "service_account",
            "project_id": Config.FIREBASE_PROJECT_ID,
            "private_key_id": Config.FIREBASE_PRIVATE_KEY_ID,
            "private_key": Config.FIREBASE_PRIVATE_KEY,
            "client_email": Config.FIREBASE_CLIENT_EMAIL,
            "client_id": Config.FIREBASE_CLIENT_ID,
            "auth_uri": Config.FIREBASE_AUTH_URI,
            "token_uri": Config.FIREBASE_TOKEN_URI,
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{Config.FIREBASE_CLIENT_EMAIL}"
        }
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration values"""
        required_vars = []
        
        # Check Firebase configuration
        if not cls.FIREBASE_PROJECT_ID:
            required_vars.append('FIREBASE_PROJECT_ID')
        if not cls.FIREBASE_CLIENT_EMAIL:
            required_vars.append('FIREBASE_CLIENT_EMAIL')
        if not cls.FIREBASE_PRIVATE_KEY:
            required_vars.append('FIREBASE_PRIVATE_KEY')
        
        if required_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(required_vars)}")
        
        return True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    @classmethod
    def validate_config(cls):
        """Additional validation for production"""
        super().validate_config()
        
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("SECRET_KEY must be set for production")
        
        return True

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
