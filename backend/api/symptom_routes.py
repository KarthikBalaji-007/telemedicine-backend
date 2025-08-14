"""
Symptom check API routes for AI Telemedicine Platform
Handles symptom assessment and triage functionality
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import time
import logging

from services.firebase_service import FirebaseService
from services.ai_service import AIService
from services.validation_service import ValidationService
from utils.decorators import validate_json, handle_errors
from utils.helpers import generate_response
from models.interaction import Interaction

# Create blueprint
symptom_bp = Blueprint('symptom', __name__)

# Initialize services
firebase_service = FirebaseService()
ai_service = AIService()
validation_service = ValidationService()

@symptom_bp.route('/symptom-check', methods=['POST'])
@handle_errors
@validate_json
def symptom_check():
    """
    Perform AI-powered symptom assessment
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    
    Expected JSON payload:
    {
        "user_id": "string",
        "symptoms": ["symptom1", "symptom2"],
        "severity_level": 1-10,
        "duration": "string (e.g., '2 days', '1 week')",
        "additional_info": "string (optional)",
        "age": number (optional),
        "gender": "string (optional)",
        "medical_history": ["condition1", "condition2"] (optional),
        "vitals": {
            "heart_rate": 72 (optional),
            "blood_pressure_systolic": 120 (optional),
            "blood_pressure_diastolic": 80 (optional),
            "temperature_f": 98.6 (optional),
            "respiratory_rate": 16 (optional),
            "oxygen_saturation": 98 (optional)
        } (optional),
        "follow_up_context": "string (optional - for chaining questions)"
    }
    """
    try:
        data = request.get_json()
        start_time = time.time()
        
        # Validate required fields
        required_fields = ['user_id', 'symptoms']
        validation_result = validation_service.validate_required_fields(data, required_fields)
        
        if not validation_result['valid']:
            return generate_response(
                success=False,
                message=validation_result['message'],
                status_code=400
            )
        
        # Validate symptoms list
        symptoms = data.get('symptoms', [])
        if not isinstance(symptoms, list) or len(symptoms) == 0:
            return generate_response(
                success=False,
                message="At least one symptom is required",
                status_code=400
            )
        
        if len(symptoms) > current_app.config.get('MAX_SYMPTOMS_PER_REQUEST', 10):
            return generate_response(
                success=False,
                message=f"Maximum {current_app.config.get('MAX_SYMPTOMS_PER_REQUEST', 10)} symptoms allowed per request",
                status_code=400
            )
        
        # Validate severity level
        severity_level = data.get('severity_level')
        if severity_level and (not isinstance(severity_level, int) or severity_level < 1 or severity_level > 10):
            return generate_response(
                success=False,
                message="Severity level must be an integer between 1 and 10",
                status_code=400
            )
        
        # Create interaction record
        interaction_data = {
            'user_id': data['user_id'],
            'interaction_type': 'symptom_check',
            'symptoms': symptoms,
            'severity_level': severity_level,
            'duration': data.get('duration'),
            'user_input': {
                'additional_info': data.get('additional_info', ''),
                'age': data.get('age'),
                'gender': data.get('gender'),
                'medical_history': data.get('medical_history', [])
            },
            'status': 'processing'
        }
        
        interaction = Interaction.from_dict(interaction_data)
        
        # Save initial interaction to Firebase
        saved_interaction = firebase_service.save_interaction(interaction.to_dict())
        
        try:
            # Call AI service for symptom assessment
            # TODO: REQUEST FROM TEAM LEAD - Need assess_symptoms() function here
            ai_response = ai_service.assess_symptoms(
                symptoms=symptoms,
                severity_level=severity_level,
                duration=data.get('duration'),
                additional_info=data.get('additional_info', ''),
                user_context={
                    'age': data.get('age'),
                    'gender': data.get('gender'),
                    'medical_history': data.get('medical_history', [])
                }
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update interaction with AI response
            interaction.set_ai_response(ai_response, processing_time)
            interaction.update_status('completed')
            
            # Save updated interaction
            firebase_service.save_interaction(interaction.to_dict())
            
            # Prepare response
            response_data = {
                'interaction_id': interaction.interaction_id,
                'assessment': ai_response.get('assessment', {}),
                'recommendations': ai_response.get('recommendations', []),
                'urgency_level': ai_response.get('urgency_level', 'low'),
                'confidence_score': ai_response.get('confidence_score'),
                'follow_up_required': interaction.follow_up_required,
                'follow_up_timeframe': interaction.follow_up_timeframe,
                'doctor_referral_suggested': interaction.doctor_referral_suggested,
                'processing_time': processing_time
            }
            
            current_app.logger.info(f"Symptom check completed for user {data['user_id']}: {interaction.interaction_id}")
            
            return generate_response(
                success=True,
                data=response_data,
                message="Symptom assessment completed successfully"
            )
            
        except Exception as ai_error:
            # Update interaction status to error
            interaction.update_status('error', str(ai_error))
            firebase_service.save_interaction(interaction.to_dict())
            
            current_app.logger.error(f"AI service error during symptom check: {str(ai_error)}")
            
            # Return fallback response
            return generate_response(
                success=False,
                message="AI service temporarily unavailable. Please try again later.",
                data={'interaction_id': interaction.interaction_id},
                status_code=503
            )
            
    except Exception as e:
        current_app.logger.error(f"Error in symptom check: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to process symptom check",
            status_code=500
        )

@symptom_bp.route('/symptom-check/<interaction_id>', methods=['GET'])
@handle_errors
def get_symptom_check_result(interaction_id):
    """
    Get symptom check result by interaction ID
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    """
    try:
        # Get interaction from Firebase
        interaction_data = firebase_service.get_interaction(interaction_id)
        
        if not interaction_data:
            return generate_response(
                success=False,
                message="Symptom check result not found",
                status_code=404
            )
        
        # Check if it's a symptom check interaction
        if interaction_data.get('interaction_type') != 'symptom_check':
            return generate_response(
                success=False,
                message="Invalid interaction type",
                status_code=400
            )
        
        # Prepare response data
        response_data = {
            'interaction_id': interaction_data['interaction_id'],
            'timestamp': interaction_data['timestamp'],
            'symptoms': interaction_data.get('symptoms', []),
            'severity_level': interaction_data.get('severity_level'),
            'duration': interaction_data.get('duration'),
            'assessment': interaction_data.get('assessment_result', {}),
            'recommendations': interaction_data.get('recommendations', []),
            'urgency_level': interaction_data.get('urgency_level', 'low'),
            'confidence_score': interaction_data.get('confidence_score'),
            'follow_up_required': interaction_data.get('follow_up_required', False),
            'follow_up_timeframe': interaction_data.get('follow_up_timeframe'),
            'doctor_referral_suggested': interaction_data.get('doctor_referral_suggested', False),
            'status': interaction_data.get('status', 'unknown')
        }
        
        return generate_response(
            success=True,
            data=response_data,
            message="Symptom check result retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving symptom check result: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to retrieve symptom check result",
            status_code=500
        )

@symptom_bp.route('/symptoms/common', methods=['GET'])
@handle_errors
def get_common_symptoms():
    """
    Get list of common symptoms for frontend autocomplete
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    """
    try:
        # TODO: COORDINATE WITH TEAM - Consider moving this to a configuration file or database
        common_symptoms = [
            "Fever", "Headache", "Cough", "Sore throat", "Runny nose",
            "Fatigue", "Body aches", "Nausea", "Vomiting", "Diarrhea",
            "Shortness of breath", "Chest pain", "Dizziness", "Rash",
            "Abdominal pain", "Back pain", "Joint pain", "Muscle pain",
            "Loss of appetite", "Difficulty sleeping", "Anxiety", "Depression",
            "Confusion", "Memory problems", "Vision problems", "Hearing problems"
        ]
        
        # Sort alphabetically
        common_symptoms.sort()
        
        return generate_response(
            success=True,
            data={'symptoms': common_symptoms},
            message="Common symptoms retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving common symptoms: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to retrieve common symptoms",
            status_code=500
        )
