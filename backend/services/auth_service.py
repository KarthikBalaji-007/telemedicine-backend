"""
Authentication and Security Service for AI Telemedicine Platform
Handles user authentication, API key validation, and security measures
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
from functools import wraps
from flask import request, jsonify, current_app

class AuthService:
    """Authentication and security service"""
    
    def __init__(self):
        self.secret_key = "dev-secret-key-change-in-production"  # From config
        self.algorithm = "HS256"
        self.token_expiry_hours = 24
    
    def generate_api_key(self, user_id: str) -> str:
        """Generate API key for user"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        raw_key = f"{user_id}:{timestamp}:{secrets.token_hex(16)}"
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    def generate_jwt_token(self, user_id: str, user_data: Dict = None) -> str:
        """Generate JWT token for user session"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow(),
            'data': user_data or {}
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logging.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logging.warning("Invalid JWT token")
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            salt, password_hash = hashed.split(':')
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == password_hash
        except:
            return False
    
    def validate_request_data(self, data: Dict, required_fields: list) -> Dict:
        """Validate request data has required fields"""
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        return {
            'valid': len(missing_fields) == 0,
            'missing_fields': missing_fields
        }
    
    def sanitize_input(self, text: str) -> str:
        """Basic input sanitization"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        return text.strip()
    
    def rate_limit_check(self, user_id: str, endpoint: str) -> bool:
        """Basic rate limiting check (mock implementation)"""
        # TODO: Implement with Redis or database
        # For now, always allow (development mode)
        return True
    
    def log_security_event(self, event_type: str, user_id: str = None, details: Dict = None):
        """Log security events"""
        log_data = {
            'event_type': event_type,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        logging.info(f"Security Event: {log_data}")

# Authentication decorators
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'message': 'Authorization header required',
                'status_code': 401
            }), 401
        
        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
            auth_service = AuthService()
            payload = auth_service.verify_jwt_token(token)
            
            if not payload:
                return jsonify({
                    'success': False,
                    'message': 'Invalid or expired token',
                    'status_code': 401
                }), 401
            
            # Add user info to request context
            request.user_id = payload['user_id']
            request.user_data = payload.get('data', {})
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Authentication failed',
                'status_code': 401
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_api_key(f):
    """Decorator to require API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'success': False,
                'message': 'API key required',
                'status_code': 401
            }), 401
        
        # TODO: Validate API key against database
        # For development, accept any non-empty key
        if len(api_key) < 10:
            return jsonify({
                'success': False,
                'message': 'Invalid API key',
                'status_code': 401
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function
