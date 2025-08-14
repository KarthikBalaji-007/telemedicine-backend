"""
Backend Integration API Routes
Provides APIs for model management, conversation chaining, and advanced features
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import logging

from services.model_management_service import ModelManagementService
from services.conversation_service import ConversationService
from services.risk_assessment_service import RiskAssessmentService
from services.firebase_service import FirebaseService
from services.auth_service import require_auth
from utils.decorators import validate_json, handle_errors
from utils.helpers import generate_response

# Create blueprint
integration_bp = Blueprint('integration', __name__)

# Initialize services
model_service = ModelManagementService()
conversation_service = ConversationService()
risk_service = RiskAssessmentService()
firebase_service = FirebaseService()

# FEATURE 1: MODEL LOADING MANAGEMENT
@integration_bp.route('/model/status', methods=['GET'])
@handle_errors
def get_model_status():
    """Get current AI model loading status and information"""
    try:
        status = model_service.get_model_status()
        
        return generate_response(
            success=True,
            data=status,
            message="Model status retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error getting model status: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to get model status",
            status_code=500
        )

@integration_bp.route('/model/load', methods=['POST'])
@handle_errors
def load_model():
    """Start loading the AI model"""
    try:
        result = model_service.start_model_loading()
        
        return generate_response(
            success=result['success'],
            data=result,
            message=result['message'],
            status_code=200 if result['success'] else 400
        )
        
    except Exception as e:
        current_app.logger.error(f"Error loading model: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to start model loading",
            status_code=500
        )

@integration_bp.route('/model/unload', methods=['POST'])
@handle_errors
def unload_model():
    """Unload the AI model to free memory"""
    try:
        result = model_service.unload_model()
        
        return generate_response(
            success=result['success'],
            data=result,
            message=result['message']
        )
        
    except Exception as e:
        current_app.logger.error(f"Error unloading model: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to unload model",
            status_code=500
        )

@integration_bp.route('/model/requirements', methods=['GET'])
@handle_errors
def get_system_requirements():
    """Get system requirements for AI model"""
    try:
        requirements = model_service.get_system_requirements()
        
        return generate_response(
            success=True,
            data=requirements,
            message="System requirements retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error getting system requirements: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to get system requirements",
            status_code=500
        )

# FEATURE 4: CONVERSATION CHAINING & FOLLOW-UP QUESTIONS
@integration_bp.route('/conversation/follow-up', methods=['POST'])
@handle_errors
@validate_json
def generate_follow_up_questions():
    """Generate follow-up questions based on initial assessment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'assessment_id' not in data or 'symptoms' not in data:
            return generate_response(
                success=False,
                message="assessment_id and symptoms are required",
                status_code=400
            )
        
        initial_assessment = data.get('initial_assessment', {})
        symptoms = data.get('symptoms', [])
        
        # Generate follow-up questions
        follow_up_result = conversation_service.generate_follow_up_questions(
            initial_assessment, symptoms
        )
        
        return generate_response(
            success=follow_up_result['success'],
            data=follow_up_result,
            message="Follow-up questions generated successfully" if follow_up_result['success'] 
                   else "Failed to generate follow-up questions"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error generating follow-up questions: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to generate follow-up questions",
            status_code=500
        )

@integration_bp.route('/conversation/follow-up/answers', methods=['POST'])
@handle_errors
@validate_json
@require_auth
def process_follow_up_answers():
    """Process follow-up answers and generate enhanced assessment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'conversation_id' not in data or 'answers' not in data:
            return generate_response(
                success=False,
                message="conversation_id and answers are required",
                status_code=400
            )
        
        conversation_id = data['conversation_id']
        answers = data['answers']
        
        # Process follow-up answers
        result = conversation_service.process_follow_up_answers(conversation_id, answers)
        
        return generate_response(
            success=result['success'],
            data=result,
            message="Follow-up answers processed successfully" if result['success']
                   else "Failed to process follow-up answers"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error processing follow-up answers: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to process follow-up answers",
            status_code=500
        )

@integration_bp.route('/conversation/history/<user_id>', methods=['GET'])
@handle_errors
@require_auth
def get_conversation_history(user_id):
    """Get conversation history for a user"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        result = conversation_service.get_conversation_history(user_id, limit)
        
        return generate_response(
            success=result['success'],
            data=result,
            message="Conversation history retrieved successfully" if result['success']
                   else "Failed to get conversation history"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error getting conversation history: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to get conversation history",
            status_code=500
        )

# FEATURE 6: ADVANCED RISK ASSESSMENT
@integration_bp.route('/risk-assessment/comprehensive', methods=['POST'])
@handle_errors
@validate_json
def comprehensive_risk_assessment():
    """Perform comprehensive risk assessment with all factors"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'symptoms' not in data:
            return generate_response(
                success=False,
                message="symptoms are required",
                status_code=400
            )
        
        symptoms = data['symptoms']
        vitals = data.get('vitals', {})
        user_context = data.get('user_context', {})
        follow_up_data = data.get('follow_up_data', {})
        
        # Perform comprehensive risk assessment
        risk_assessment = risk_service.assess_comprehensive_risk(
            symptoms=symptoms,
            vitals=vitals,
            user_context=user_context,
            follow_up_data=follow_up_data
        )
        
        return generate_response(
            success=True,
            data=risk_assessment,
            message="Comprehensive risk assessment completed successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in comprehensive risk assessment: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to perform comprehensive risk assessment",
            status_code=500
        )

# FEATURE 2 & 3: ENHANCED SYMPTOM ASSESSMENT WITH VITALS
@integration_bp.route('/assessment/enhanced', methods=['POST'])
@handle_errors
@validate_json
@require_auth
def enhanced_symptom_assessment():
    """Enhanced symptom assessment with vitals integration"""
    try:
        data = request.get_json()
        user_id = request.user_id
        
        # Validate required fields
        required_fields = ['symptoms']
        for field in required_fields:
            if field not in data:
                return generate_response(
                    success=False,
                    message=f"{field} is required",
                    status_code=400
                )
        
        # Extract all assessment data
        symptoms = data['symptoms']
        vitals = data.get('vitals', {})
        severity = data.get('severity', 'moderate')
        duration = data.get('duration', 'unknown')
        user_context = {
            'age': data.get('age'),
            'gender': data.get('gender'),
            'medical_history': data.get('medical_history', []),
            'medications': data.get('medications', [])
        }
        
        # Perform comprehensive risk assessment
        risk_assessment = risk_service.assess_comprehensive_risk(
            symptoms=symptoms,
            vitals=vitals,
            user_context=user_context
        )
        
        # Create enhanced assessment record
        assessment_data = {
            'user_id': user_id,
            'assessment_type': 'enhanced_symptom_assessment',
            'input_data': {
                'symptoms': symptoms,
                'vitals': vitals,
                'severity': severity,
                'duration': duration,
                'user_context': user_context
            },
            'risk_assessment': risk_assessment,
            'timestamp': datetime.utcnow().isoformat(),
            'assessment_version': '2.0'
        }
        
        # Save assessment
        saved_assessment = firebase_service.save_enhanced_assessment(assessment_data)
        
        # Prepare response
        response_data = {
            'assessment_id': saved_assessment.get('assessment_id'),
            'risk_level': risk_assessment['overall_risk_level'],
            'risk_score': risk_assessment['risk_score'],
            'urgency_level': risk_assessment['urgency_level'],
            'recommendations': risk_assessment['recommendations'],
            'triage_category': risk_assessment['triage_category'],
            'time_to_care': risk_assessment['time_to_care'],
            'risk_factors': risk_assessment['risk_factors'],
            'vitals_analysis': risk_assessment['assessment_components'].get('vitals', {}),
            'next_steps': risk_assessment['recommendations'][:3]  # Top 3 recommendations
        }
        
        return generate_response(
            success=True,
            data=response_data,
            message="Enhanced symptom assessment completed successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in enhanced symptom assessment: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to perform enhanced symptom assessment",
            status_code=500
        )

# HEALTH CHECK FOR INTEGRATION SERVICES
@integration_bp.route('/health', methods=['GET'])
@handle_errors
def integration_health_check():
    """Health check for all integration services"""
    try:
        health_status = {
            'model_service': model_service.health_check(),
            'conversation_service': {'status': 'healthy', 'available': True},
            'risk_service': {'status': 'healthy', 'available': True},
            'firebase_service': firebase_service.health_check(),
            'overall_status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Check if any service is unhealthy
        unhealthy_services = []
        for service_name, status in health_status.items():
            if isinstance(status, dict) and not status.get('available', True):
                unhealthy_services.append(service_name)
        
        if unhealthy_services:
            health_status['overall_status'] = 'degraded'
            health_status['unhealthy_services'] = unhealthy_services
        
        return generate_response(
            success=True,
            data=health_status,
            message="Integration services health check completed"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in integration health check: {str(e)}")
        return generate_response(
            success=False,
            message="Integration health check failed",
            status_code=500
        )
