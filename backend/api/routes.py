"""
Main API routes for AI Telemedicine Platform
General endpoints and user history functionality
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import logging

from services.firebase_service import FirebaseService
from services.validation_service import ValidationService
from utils.decorators import validate_json, handle_errors
from utils.helpers import generate_response

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize services
firebase_service = FirebaseService()
validation_service = ValidationService()

@api_bp.route('/user-history', methods=['GET'])
@handle_errors
def get_user_history():
    """
    Get user interaction history
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    
    Query Parameters:
    - user_id (required): User identifier
    - limit (optional): Number of records to return (default: 20, max: 50)
    - offset (optional): Number of records to skip (default: 0)
    """
    try:
        # Get query parameters
        user_id = request.args.get('user_id')
        limit = min(int(request.args.get('limit', 20)), 50)  # Cap at 50
        offset = int(request.args.get('offset', 0))
        
        # Validate required parameters
        if not user_id:
            return generate_response(
                success=False,
                message="user_id is required",
                status_code=400
            )
        
        # Get user history from Firebase
        history_data = firebase_service.get_user_history(user_id, limit, offset)
        
        # Format response
        response_data = {
            'user_id': user_id,
            'history': history_data.get('interactions', []),
            'total_count': history_data.get('total_count', 0),
            'limit': limit,
            'offset': offset,
            'has_more': history_data.get('has_more', False)
        }
        
        current_app.logger.info(f"Retrieved {len(response_data['history'])} history items for user {user_id}")
        
        return generate_response(
            success=True,
            data=response_data,
            message="User history retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving user history: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to retrieve user history",
            status_code=500
        )

@api_bp.route('/user-profile', methods=['GET'])
@handle_errors
def get_user_profile():
    """
    Get user profile information
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return generate_response(
                success=False,
                message="user_id is required",
                status_code=400
            )
        
        # Get user profile from Firebase
        user_profile = firebase_service.get_user_profile(user_id)
        
        if not user_profile:
            return generate_response(
                success=False,
                message="User not found",
                status_code=404
            )
        
        return generate_response(
            success=True,
            data=user_profile,
            message="User profile retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving user profile: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to retrieve user profile",
            status_code=500
        )

@api_bp.route('/user-profile', methods=['POST'])
@handle_errors
@validate_json
def create_or_update_user_profile():
    """
    Create or update user profile
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'name', 'email']
        validation_result = validation_service.validate_required_fields(data, required_fields)
        
        if not validation_result['valid']:
            return generate_response(
                success=False,
                message=validation_result['message'],
                status_code=400
            )
        
        # Validate email format
        if not validation_service.validate_email(data['email']):
            return generate_response(
                success=False,
                message="Invalid email format",
                status_code=400
            )
        
        # Create/update user profile
        user_data = {
            'user_id': data['user_id'],
            'name': data['name'],
            'email': data['email'],
            'phone': data.get('phone'),
            'date_of_birth': data.get('date_of_birth'),
            'gender': data.get('gender'),
            'medical_history': data.get('medical_history', []),
            'emergency_contact': data.get('emergency_contact'),
            'updated_at': datetime.utcnow().isoformat(),
            'created_at': data.get('created_at', datetime.utcnow().isoformat())
        }
        
        # Save to Firebase
        result = firebase_service.save_user_profile(user_data)
        
        return generate_response(
            success=True,
            data=result,
            message="User profile saved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error saving user profile: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to save user profile",
            status_code=500
        )

@api_bp.route('/system-stats', methods=['GET'])
@handle_errors
def get_system_stats():
    """
    Get system statistics for admin dashboard
    TODO: COORDINATE WITH TEAM - Determine what stats are needed
    """
    try:
        # Get basic system statistics
        stats = firebase_service.get_system_statistics()
        
        # Add current timestamp
        stats['timestamp'] = datetime.utcnow().isoformat()
        stats['uptime'] = 'Available in production'  # TODO: Implement actual uptime tracking
        
        return generate_response(
            success=True,
            data=stats,
            message="System statistics retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving system stats: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to retrieve system statistics",
            status_code=500
        )
