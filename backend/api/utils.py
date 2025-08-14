"""
API utilities for AI Telemedicine Platform
Common utilities specific to API operations
"""

from flask import request, current_app
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List, Tuple

from utils.helpers import generate_response
from utils.constants import StatusCodes, Messages

def validate_pagination_params() -> Tuple[int, int, Dict]:
    """
    Validate and extract pagination parameters from request
    
    Returns:
        Tuple of (limit, offset, validation_result)
    """
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Validate limits
        if limit < 1:
            return 0, 0, {
                'valid': False,
                'message': 'Limit must be at least 1'
            }
        
        if limit > 100:
            return 0, 0, {
                'valid': False,
                'message': 'Limit cannot exceed 100'
            }
        
        if offset < 0:
            return 0, 0, {
                'valid': False,
                'message': 'Offset cannot be negative'
            }
        
        return limit, offset, {'valid': True}
        
    except ValueError:
        return 0, 0, {
            'valid': False,
            'message': 'Limit and offset must be valid integers'
        }

def extract_user_context() -> Dict[str, Any]:
    """
    Extract user context from request headers and parameters
    
    Returns:
        Dictionary containing user context information
    """
    context = {
        'user_agent': request.headers.get('User-Agent', ''),
        'ip_address': request.remote_addr,
        'timestamp': datetime.utcnow().isoformat(),
        'endpoint': request.endpoint,
        'method': request.method,
        'url': request.url
    }
    
    # Extract user ID from various sources
    user_id = None
    
    # Check URL parameters
    if 'user_id' in request.view_args:
        user_id = request.view_args['user_id']
    
    # Check query parameters
    if not user_id:
        user_id = request.args.get('user_id')
    
    # Check JSON body
    if not user_id and request.is_json:
        try:
            data = request.get_json()
            user_id = data.get('user_id')
        except:
            pass
    
    # Check authorization header (if implementing auth tokens)
    auth_header = request.headers.get('Authorization')
    if auth_header:
        context['has_auth'] = True
        # TODO: COORDINATE WITH TEAM - Extract user info from auth token
    
    if user_id:
        context['user_id'] = user_id
    
    return context

def log_api_request(additional_info: Dict = None):
    """
    Log API request with context information
    
    Args:
        additional_info: Additional information to include in log
    """
    context = extract_user_context()
    
    if additional_info:
        context.update(additional_info)
    
    # Log request
    current_app.logger.info(f"API Request: {context}")
    
    # Log request body for debugging (be careful with sensitive data)
    if request.is_json and current_app.debug:
        try:
            data = request.get_json()
            # Mask sensitive fields
            safe_data = mask_sensitive_fields(data)
            current_app.logger.debug(f"Request body: {safe_data}")
        except:
            pass

def mask_sensitive_fields(data: Dict, sensitive_fields: List[str] = None) -> Dict:
    """
    Mask sensitive fields in data dictionary
    
    Args:
        data: Dictionary to mask
        sensitive_fields: List of field names to mask
    
    Returns:
        Dictionary with sensitive fields masked
    """
    if sensitive_fields is None:
        sensitive_fields = [
            'password', 'token', 'api_key', 'secret', 'private_key',
            'ssn', 'social_security', 'credit_card', 'bank_account'
        ]
    
    if not isinstance(data, dict):
        return data
    
    masked_data = {}
    
    for key, value in data.items():
        if key.lower() in [field.lower() for field in sensitive_fields]:
            masked_data[key] = '***MASKED***'
        elif isinstance(value, dict):
            masked_data[key] = mask_sensitive_fields(value, sensitive_fields)
        elif isinstance(value, list):
            masked_data[key] = [
                mask_sensitive_fields(item, sensitive_fields) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            masked_data[key] = value
    
    return masked_data

def validate_request_size():
    """
    Validate request content length
    
    Returns:
        Validation result dictionary
    """
    max_content_length = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB default
    
    content_length = request.content_length
    
    if content_length and content_length > max_content_length:
        return {
            'valid': False,
            'message': f'Request too large. Maximum size: {max_content_length} bytes'
        }
    
    return {'valid': True}

def create_error_response(error_type: str, message: str = None, 
                         status_code: int = None, details: Dict = None) -> Tuple:
    """
    Create standardized error response
    
    Args:
        error_type: Type of error (validation, not_found, etc.)
        message: Custom error message
        status_code: HTTP status code
        details: Additional error details
    
    Returns:
        Tuple of (response, status_code)
    """
    error_mappings = {
        'validation': (Messages.ERROR_VALIDATION, StatusCodes.BAD_REQUEST),
        'not_found': (Messages.ERROR_NOT_FOUND, StatusCodes.NOT_FOUND),
        'unauthorized': (Messages.ERROR_UNAUTHORIZED, StatusCodes.UNAUTHORIZED),
        'forbidden': (Messages.ERROR_FORBIDDEN, StatusCodes.FORBIDDEN),
        'conflict': (Messages.ERROR_CONFLICT, StatusCodes.CONFLICT),
        'service_unavailable': (Messages.ERROR_SERVICE_UNAVAILABLE, StatusCodes.SERVICE_UNAVAILABLE),
        'timeout': (Messages.ERROR_TIMEOUT, StatusCodes.GATEWAY_TIMEOUT),
        'general': (Messages.ERROR_GENERAL, StatusCodes.INTERNAL_SERVER_ERROR)
    }
    
    default_message, default_status = error_mappings.get(error_type, error_mappings['general'])
    
    final_message = message or default_message
    final_status = status_code or default_status
    
    response_data = {
        'error_type': error_type,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if details:
        response_data['details'] = details
    
    return generate_response(
        success=False,
        message=final_message,
        data=response_data,
        status_code=final_status
    )

def validate_content_type(expected_type: str = 'application/json') -> Dict:
    """
    Validate request content type
    
    Args:
        expected_type: Expected content type
    
    Returns:
        Validation result dictionary
    """
    if request.content_type != expected_type:
        return {
            'valid': False,
            'message': f'Content-Type must be {expected_type}'
        }
    
    return {'valid': True}

def extract_filters_from_query() -> Dict[str, Any]:
    """
    Extract filter parameters from query string
    
    Returns:
        Dictionary of filter parameters
    """
    filters = {}
    
    # Common filter parameters
    filter_params = [
        'status', 'type', 'urgency_level', 'risk_level',
        'appointment_type', 'consultation_mode', 'date_from', 'date_to'
    ]
    
    for param in filter_params:
        value = request.args.get(param)
        if value:
            filters[param] = value
    
    return filters

def validate_date_range(date_from: str = None, date_to: str = None) -> Dict:
    """
    Validate date range parameters
    
    Args:
        date_from: Start date string
        date_to: End date string
    
    Returns:
        Validation result dictionary
    """
    try:
        if date_from:
            from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        else:
            from_dt = None
        
        if date_to:
            to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        else:
            to_dt = None
        
        if from_dt and to_dt and from_dt > to_dt:
            return {
                'valid': False,
                'message': 'date_from must be before date_to'
            }
        
        return {
            'valid': True,
            'date_from': from_dt,
            'date_to': to_dt
        }
        
    except ValueError as e:
        return {
            'valid': False,
            'message': f'Invalid date format: {str(e)}'
        }

def create_success_response(message: str, data: Any = None, 
                          status_code: int = StatusCodes.OK) -> Tuple:
    """
    Create standardized success response
    
    Args:
        message: Success message
        data: Response data
        status_code: HTTP status code
    
    Returns:
        Tuple of (response, status_code)
    """
    return generate_response(
        success=True,
        message=message,
        data=data,
        status_code=status_code
    )

def handle_ai_service_error(error: Exception) -> Tuple:
    """
    Handle AI service errors with appropriate fallback responses
    
    Args:
        error: Exception from AI service
    
    Returns:
        Tuple of (response, status_code)
    """
    error_message = str(error)
    
    # Log the error
    current_app.logger.error(f"AI Service Error: {error_message}")
    
    # Determine error type and response
    if 'timeout' in error_message.lower():
        return create_error_response(
            'timeout',
            'AI service timeout - please try again',
            StatusCodes.GATEWAY_TIMEOUT
        )
    elif 'connection' in error_message.lower():
        return create_error_response(
            'service_unavailable',
            'AI service temporarily unavailable',
            StatusCodes.SERVICE_UNAVAILABLE
        )
    else:
        return create_error_response(
            'service_unavailable',
            'AI service error - please try again later',
            StatusCodes.SERVICE_UNAVAILABLE
        )

def validate_interaction_type(interaction_type: str) -> Dict:
    """
    Validate interaction type parameter
    
    Args:
        interaction_type: Type of interaction
    
    Returns:
        Validation result dictionary
    """
    from utils.constants import Medical
    
    if interaction_type not in Medical.INTERACTION_TYPES:
        return {
            'valid': False,
            'message': f'Invalid interaction type. Must be one of: {", ".join(Medical.INTERACTION_TYPES)}'
        }
    
    return {'valid': True}

def format_api_response_for_logging(response_data: Dict) -> Dict:
    """
    Format API response data for logging (remove sensitive information)
    
    Args:
        response_data: Response data dictionary
    
    Returns:
        Sanitized response data for logging
    """
    if not isinstance(response_data, dict):
        return response_data
    
    # Create a copy to avoid modifying original
    log_data = response_data.copy()
    
    # Remove or mask sensitive fields
    sensitive_fields = ['meeting_password', 'api_key', 'token']
    
    for field in sensitive_fields:
        if field in log_data:
            log_data[field] = '***MASKED***'
    
    return log_data
