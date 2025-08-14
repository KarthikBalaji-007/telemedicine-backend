"""
Authentication API routes for AI Telemedicine Platform
Handles user login, registration, and token management
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import logging

from services.firebase_service import FirebaseService
from services.auth_service import AuthService
from services.validation_service import ValidationService
from utils.decorators import validate_json, handle_errors
from utils.helpers import generate_response
from models.user import User

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize services
firebase_service = FirebaseService()
auth_service = AuthService()
validation_service = ValidationService()

@auth_bp.route('/register', methods=['POST'])
@handle_errors
@validate_json
def register_user():
    """
    Register new user
    
    Expected JSON payload:
    {
        "name": "string",
        "email": "string",
        "password": "string",
        "phone": "string" (optional),
        "date_of_birth": "YYYY-MM-DD" (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        validation_result = auth_service.validate_request_data(data, required_fields)
        
        if not validation_result['valid']:
            return generate_response(
                success=False,
                message=f"Missing required fields: {', '.join(validation_result['missing_fields'])}",
                status_code=400
            )
        
        # Sanitize inputs
        data['name'] = auth_service.sanitize_input(data['name'])
        data['email'] = auth_service.sanitize_input(data['email']).lower()
        
        # Validate email format
        if '@' not in data['email'] or '.' not in data['email']:
            return generate_response(
                success=False,
                message="Invalid email format",
                status_code=400
            )
        
        # Hash password
        data['password_hash'] = auth_service.hash_password(data['password'])
        del data['password']  # Remove plain password
        
        # Create user profile
        user_data = {
            'name': data['name'],
            'email': data['email'],
            'password_hash': data['password_hash'],
            'phone': data.get('phone'),
            'date_of_birth': data.get('date_of_birth'),
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True,
            'privacy_consent': True,
            'data_sharing_consent': False
        }
        
        # Save user to database
        saved_user = firebase_service.save_user_profile(user_data)
        
        # Generate JWT token
        token = auth_service.generate_jwt_token(
            saved_user['user_id'],
            {'name': saved_user['name'], 'email': saved_user['email']}
        )
        
        # Generate API key
        api_key = auth_service.generate_api_key(saved_user['user_id'])
        
        # Log security event
        auth_service.log_security_event('user_registered', saved_user['user_id'])
        
        return generate_response(
            success=True,
            message="User registered successfully",
            data={
                'user_id': saved_user['user_id'],
                'name': saved_user['name'],
                'email': saved_user['email'],
                'token': token,
                'api_key': api_key,
                'expires_in': '24 hours'
            },
            status_code=201
        )
        
    except Exception as e:
        logging.error(f"Error registering user: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to register user",
            status_code=500
        )

@auth_bp.route('/login', methods=['POST'])
@handle_errors
@validate_json
def login_user():
    """
    User login
    
    Expected JSON payload:
    {
        "email": "string",
        "password": "string"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password']
        validation_result = auth_service.validate_request_data(data, required_fields)
        
        if not validation_result['valid']:
            return generate_response(
                success=False,
                message=f"Missing required fields: {', '.join(validation_result['missing_fields'])}",
                status_code=400
            )
        
        email = auth_service.sanitize_input(data['email']).lower()
        password = data['password']
        
        # TODO: Get user by email from database
        # For development mode, create mock user
        mock_user = {
            'user_id': 'user_123',
            'name': 'Test User',
            'email': email,
            'password_hash': auth_service.hash_password('password123'),  # Mock password
            'is_active': True
        }
        
        # Verify password (in development, accept any password)
        # if not auth_service.verify_password(password, mock_user['password_hash']):
        #     return generate_response(
        #         success=False,
        #         message="Invalid email or password",
        #         status_code=401
        #     )
        
        # Generate JWT token
        token = auth_service.generate_jwt_token(
            mock_user['user_id'],
            {'name': mock_user['name'], 'email': mock_user['email']}
        )
        
        # Log security event
        auth_service.log_security_event('user_login', mock_user['user_id'])
        
        return generate_response(
            success=True,
            message="Login successful",
            data={
                'user_id': mock_user['user_id'],
                'name': mock_user['name'],
                'email': mock_user['email'],
                'token': token,
                'expires_in': '24 hours'
            }
        )
        
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")
        return generate_response(
            success=False,
            message="Login failed",
            status_code=500
        )

@auth_bp.route('/refresh-token', methods=['POST'])
@handle_errors
def refresh_token():
    """Refresh JWT token"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return generate_response(
                success=False,
                message="Authorization header required",
                status_code=401
            )
        
        token = auth_header.split(' ')[1]
        payload = auth_service.verify_jwt_token(token)
        
        if not payload:
            return generate_response(
                success=False,
                message="Invalid or expired token",
                status_code=401
            )
        
        # Generate new token
        new_token = auth_service.generate_jwt_token(
            payload['user_id'],
            payload.get('data', {})
        )
        
        return generate_response(
            success=True,
            message="Token refreshed successfully",
            data={
                'token': new_token,
                'expires_in': '24 hours'
            }
        )
        
    except Exception as e:
        logging.error(f"Error refreshing token: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to refresh token",
            status_code=500
        )
