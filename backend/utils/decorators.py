"""
Decorators for AI Telemedicine Platform
Common decorators for request handling, validation, and error management
"""

from functools import wraps
from flask import request, current_app, jsonify
import logging
import time
from typing import Callable, Any

from utils.helpers import generate_response

def validate_json(f: Callable) -> Callable:
    """Decorator to validate that request contains valid JSON"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return generate_response(
                success=False,
                message="Request must contain valid JSON",
                status_code=400
            )
        
        try:
            request.get_json()
        except Exception as e:
            return generate_response(
                success=False,
                message=f"Invalid JSON format: {str(e)}",
                status_code=400
            )
        
        return f(*args, **kwargs)
    
    return decorated_function

def handle_errors(f: Callable) -> Callable:
    """Decorator to handle common errors and provide consistent error responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            current_app.logger.warning(f"Validation error in {f.__name__}: {str(e)}")
            return generate_response(
                success=False,
                message=str(e),
                status_code=400
            )
        except PermissionError as e:
            current_app.logger.warning(f"Permission error in {f.__name__}: {str(e)}")
            return generate_response(
                success=False,
                message="Insufficient permissions",
                status_code=403
            )
        except FileNotFoundError as e:
            current_app.logger.warning(f"Not found error in {f.__name__}: {str(e)}")
            return generate_response(
                success=False,
                message="Resource not found",
                status_code=404
            )
        except ConnectionError as e:
            current_app.logger.error(f"Connection error in {f.__name__}: {str(e)}")
            return generate_response(
                success=False,
                message="Service temporarily unavailable",
                status_code=503
            )
        except TimeoutError as e:
            current_app.logger.error(f"Timeout error in {f.__name__}: {str(e)}")
            return generate_response(
                success=False,
                message="Request timeout - please try again",
                status_code=504
            )
        except Exception as e:
            current_app.logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            return generate_response(
                success=False,
                message="An unexpected error occurred",
                status_code=500
            )
    
    return decorated_function

def log_execution_time(f: Callable) -> Callable:
    """Decorator to log function execution time"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        execution_time = time.time() - start_time
        
        current_app.logger.info(f"{f.__name__} executed in {execution_time:.3f} seconds")
        return result
    
    return decorated_function

def require_fields(*required_fields):
    """Decorator to validate required fields in JSON request"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return generate_response(
                    success=False,
                    message="Request must contain valid JSON",
                    status_code=400
                )
            
            data = request.get_json()
            missing_fields = []
            
            for field in required_fields:
                if field not in data or data[field] is None:
                    missing_fields.append(field)
                elif isinstance(data[field], str) and not data[field].strip():
                    missing_fields.append(field)
            
            if missing_fields:
                return generate_response(
                    success=False,
                    message=f"Missing required fields: {', '.join(missing_fields)}",
                    status_code=400
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def validate_user_id(f: Callable) -> Callable:
    """Decorator to validate user_id parameter"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user_id is in URL parameters
        user_id = kwargs.get('user_id')
        
        # If not in URL, check JSON body
        if not user_id and request.is_json:
            data = request.get_json()
            user_id = data.get('user_id')
        
        # If not in JSON, check query parameters
        if not user_id:
            user_id = request.args.get('user_id')
        
        if not user_id:
            return generate_response(
                success=False,
                message="user_id is required",
                status_code=400
            )
        
        # Basic validation
        if not isinstance(user_id, str) or len(user_id.strip()) < 3:
            return generate_response(
                success=False,
                message="Invalid user_id format",
                status_code=400
            )
        
        return f(*args, **kwargs)
    
    return decorated_function

def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """
    Simple rate limiting decorator
    TODO: COORDINATE WITH TEAM - Consider using Redis for distributed rate limiting
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple in-memory rate limiting (not suitable for production with multiple instances)
            # TODO: Implement proper rate limiting with Redis or similar
            
            client_ip = request.remote_addr
            current_time = time.time()
            
            # For now, just log the rate limit check
            current_app.logger.debug(f"Rate limit check for {client_ip}: {max_requests} requests per {window_seconds} seconds")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def cache_response(timeout: int = 300):
    """
    Simple response caching decorator
    TODO: COORDINATE WITH TEAM - Implement proper caching with Redis
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple caching placeholder
            # TODO: Implement actual caching mechanism
            
            cache_key = f"{f.__name__}:{request.url}:{request.method}"
            current_app.logger.debug(f"Cache check for key: {cache_key}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_content_type(content_type: str = 'application/json'):
    """Decorator to validate request content type"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.content_type != content_type:
                return generate_response(
                    success=False,
                    message=f"Content-Type must be {content_type}",
                    status_code=415
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def log_request_response(f: Callable) -> Callable:
    """Decorator to log request and response details"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log request
        current_app.logger.info(f"Request: {request.method} {request.url}")
        
        if request.is_json:
            # Log request body (be careful with sensitive data)
            data = request.get_json()
            # Mask sensitive fields
            safe_data = {k: v if k not in ['password', 'token', 'api_key'] else '***' 
                        for k, v in data.items()}
            current_app.logger.debug(f"Request body: {safe_data}")
        
        # Execute function
        start_time = time.time()
        result = f(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log response
        if isinstance(result, tuple):
            response, status_code = result
            current_app.logger.info(f"Response: {status_code} in {execution_time:.3f}s")
        else:
            current_app.logger.info(f"Response in {execution_time:.3f}s")
        
        return result
    
    return decorated_function

def validate_api_version(supported_versions: list = ['v1']):
    """Decorator to validate API version"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check version in header
            api_version = request.headers.get('API-Version', 'v1')
            
            if api_version not in supported_versions:
                return generate_response(
                    success=False,
                    message=f"Unsupported API version. Supported versions: {', '.join(supported_versions)}",
                    status_code=400
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
