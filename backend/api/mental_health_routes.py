"""
Mental health assessment API routes for AI Telemedicine Platform
Handles mental health screening and assessment functionality
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
mental_health_bp = Blueprint('mental_health', __name__)

# Initialize services
firebase_service = FirebaseService()
ai_service = AIService()
validation_service = ValidationService()

@mental_health_bp.route('/mental-health', methods=['POST'])
@handle_errors
@validate_json
def mental_health_assessment():
    """
    Perform AI-powered mental health assessment
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    
    Expected JSON payload:
    {
        "user_id": "string",
        "assessment_type": "screening|detailed|follow_up",
        "responses": {
            "mood_rating": 1-10,
            "anxiety_level": 1-10,
            "sleep_quality": 1-10,
            "stress_level": 1-10,
            "energy_level": 1-10,
            "social_interaction": 1-10,
            "concentration": 1-10,
            "appetite": 1-10
        },
        "symptoms": ["symptom1", "symptom2"] (optional),
        "duration": "string (e.g., '2 weeks', '1 month')",
        "triggers": ["trigger1", "trigger2"] (optional),
        "previous_episodes": boolean (optional),
        "medication_history": ["med1", "med2"] (optional),
        "support_system": "string" (optional)
    }
    """
    try:
        data = request.get_json()
        start_time = time.time()
        
        # Validate required fields
        required_fields = ['user_id', 'assessment_type', 'responses']
        validation_result = validation_service.validate_required_fields(data, required_fields)
        
        if not validation_result['valid']:
            return generate_response(
                success=False,
                message=validation_result['message'],
                status_code=400
            )
        
        # Validate assessment type
        assessment_type = data.get('assessment_type')
        if assessment_type not in ['screening', 'detailed', 'follow_up']:
            return generate_response(
                success=False,
                message="Assessment type must be 'screening', 'detailed', or 'follow_up'",
                status_code=400
            )

        # Handle multilingual input
        user_language = data.get('language', 'en')  # Default to English

        # Detect language from symptoms if provided
        symptoms_text = ' '.join(data.get('symptoms', []))
        support_system_text = data.get('support_system', '')
        combined_text = f"{symptoms_text} {support_system_text}".strip()

        if combined_text:
            from services.speech_service import SpeechService
            speech_service = SpeechService()
            detected_language = speech_service.detect_language(combined_text)
        else:
            detected_language = user_language
        
        # Validate responses
        responses = data.get('responses', {})
        if not isinstance(responses, dict):
            return generate_response(
                success=False,
                message="Responses must be a dictionary",
                status_code=400
            )
        
        # Validate rating scales (1-10)
        rating_fields = ['mood_rating', 'anxiety_level', 'sleep_quality', 'stress_level', 
                        'energy_level', 'social_interaction', 'concentration', 'appetite']
        
        for field in rating_fields:
            if field in responses:
                value = responses[field]
                if not isinstance(value, int) or value < 1 or value > 10:
                    return generate_response(
                        success=False,
                        message=f"{field} must be an integer between 1 and 10",
                        status_code=400
                    )
        
        # Create interaction record
        interaction_data = {
            'user_id': data['user_id'],
            'interaction_type': 'mental_health',
            'user_input': {
                'assessment_type': assessment_type,
                'responses': responses,
                'symptoms': data.get('symptoms', []),
                'duration': data.get('duration'),
                'triggers': data.get('triggers', []),
                'previous_episodes': data.get('previous_episodes'),
                'medication_history': data.get('medication_history', []),
                'support_system': data.get('support_system')
            },
            'status': 'processing'
        }
        
        interaction = Interaction.from_dict(interaction_data)
        
        # Save initial interaction to Firebase
        saved_interaction = firebase_service.save_interaction(interaction.to_dict())
        
        try:
            # Call AI service for mental health assessment
            # TODO: REQUEST FROM TEAM LEAD - Need assess_mental_health() function here
            ai_response = ai_service.assess_mental_health(
                assessment_type=assessment_type,
                responses=responses,
                symptoms=data.get('symptoms', []),
                duration=data.get('duration'),
                triggers=data.get('triggers', []),
                user_context={
                    'previous_episodes': data.get('previous_episodes'),
                    'medication_history': data.get('medication_history', []),
                    'support_system': data.get('support_system')
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
                'assessment_type': assessment_type,
                'assessment': ai_response.get('assessment', {}),
                'risk_level': ai_response.get('risk_level', 'low'),  # low, moderate, high, crisis
                'recommendations': ai_response.get('recommendations', []),
                'resources': ai_response.get('resources', []),
                'follow_up_required': interaction.follow_up_required,
                'follow_up_timeframe': interaction.follow_up_timeframe,
                'professional_referral_suggested': ai_response.get('professional_referral_suggested', False),
                'crisis_intervention_needed': ai_response.get('crisis_intervention_needed', False),
                'confidence_score': ai_response.get('confidence_score'),
                'processing_time': processing_time
            }
            
            # Add crisis hotline information if needed
            if ai_response.get('crisis_intervention_needed', False):
                response_data['crisis_resources'] = {
                    'national_suicide_prevention_lifeline': '988',
                    'crisis_text_line': 'Text HOME to 741741',
                    'emergency_services': '911'
                }
            
            current_app.logger.info(f"Mental health assessment completed for user {data['user_id']}: {interaction.interaction_id}")
            
            return generate_response(
                success=True,
                data=response_data,
                message="Mental health assessment completed successfully"
            )
            
        except Exception as ai_error:
            # Update interaction status to error
            interaction.update_status('error', str(ai_error))
            firebase_service.save_interaction(interaction.to_dict())
            
            current_app.logger.error(f"AI service error during mental health assessment: {str(ai_error)}")
            
            # Return fallback response with crisis resources
            fallback_response = {
                'interaction_id': interaction.interaction_id,
                'message': 'AI service temporarily unavailable. If you are in crisis, please contact emergency services.',
                'crisis_resources': {
                    'national_suicide_prevention_lifeline': '988',
                    'crisis_text_line': 'Text HOME to 741741',
                    'emergency_services': '911'
                }
            }
            
            return generate_response(
                success=False,
                message="AI service temporarily unavailable. Please try again later.",
                data=fallback_response,
                status_code=503
            )
            
    except Exception as e:
        current_app.logger.error(f"Error in mental health assessment: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to process mental health assessment",
            status_code=500
        )

@mental_health_bp.route('/mental-health/<interaction_id>', methods=['GET'])
@handle_errors
def get_mental_health_result(interaction_id):
    """
    Get mental health assessment result by interaction ID
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    """
    try:
        # Get interaction from Firebase
        interaction_data = firebase_service.get_interaction(interaction_id)
        
        if not interaction_data:
            return generate_response(
                success=False,
                message="Mental health assessment result not found",
                status_code=404
            )
        
        # Check if it's a mental health interaction
        if interaction_data.get('interaction_type') != 'mental_health':
            return generate_response(
                success=False,
                message="Invalid interaction type",
                status_code=400
            )
        
        # Prepare response data
        user_input = interaction_data.get('user_input', {})
        ai_response = interaction_data.get('ai_response', {})
        
        response_data = {
            'interaction_id': interaction_data['interaction_id'],
            'timestamp': interaction_data['timestamp'],
            'assessment_type': user_input.get('assessment_type'),
            'responses': user_input.get('responses', {}),
            'assessment': interaction_data.get('assessment_result', {}),
            'risk_level': ai_response.get('risk_level', 'unknown'),
            'recommendations': interaction_data.get('recommendations', []),
            'resources': ai_response.get('resources', []),
            'follow_up_required': interaction_data.get('follow_up_required', False),
            'follow_up_timeframe': interaction_data.get('follow_up_timeframe'),
            'professional_referral_suggested': ai_response.get('professional_referral_suggested', False),
            'crisis_intervention_needed': ai_response.get('crisis_intervention_needed', False),
            'confidence_score': interaction_data.get('confidence_score'),
            'status': interaction_data.get('status', 'unknown')
        }
        
        return generate_response(
            success=True,
            data=response_data,
            message="Mental health assessment result retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving mental health assessment result: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to retrieve mental health assessment result",
            status_code=500
        )

@mental_health_bp.route('/mental-health/voice', methods=['POST'])
@handle_errors
def process_voice_symptoms():
    """
    Process voice input for mental health symptoms
    Converts audio to text then processes like regular symptoms
    """
    try:
        from services.speech_service import SpeechService
        speech_service = SpeechService()

        # Check if audio file is provided
        if 'audio' not in request.files:
            return generate_response(
                success=False,
                message="No audio file provided",
                status_code=400
            )

        audio_file = request.files['audio']

        # Validate audio file
        validation = speech_service.validate_audio_file(audio_file)
        if not validation['valid']:
            return generate_response(
                success=False,
                message=validation['error'],
                status_code=400
            )

        # Convert speech to text
        speech_result = speech_service.convert_audio_to_text(audio_file)

        if not speech_result['success']:
            return generate_response(
                success=False,
                message=speech_result['error'],
                status_code=400
            )

        # Extract medical terms from transcribed text
        medical_analysis = speech_service.extract_medical_terms(speech_result['text'])

        # Get additional data from request
        user_id = request.form.get('user_id')
        assessment_type = request.form.get('assessment_type', 'screening')
        language_preference = request.form.get('language', 'en')  # User's preferred language

        if not user_id:
            return generate_response(
                success=False,
                message="user_id is required",
                status_code=400
            )

        # Detect language from transcribed text
        detected_language = speech_service.detect_language(speech_result['text'])

        # Use detected language or user preference
        final_language = detected_language if detected_language != 'en' else language_preference

        # Process as mental health assessment with voice-derived symptoms
        voice_data = {
            'user_id': user_id,
            'assessment_type': assessment_type,
            'responses': {
                'mood_rating': 5,  # Default - can be overridden by form data
                'anxiety_level': 5
            },
            'symptoms': medical_analysis['extracted_symptoms'],
            'duration': 'mentioned in voice input',
            'support_system': speech_result['text']  # Full transcription
        }

        # Create interaction record
        interaction_data = {
            'user_id': user_id,
            'interaction_type': 'mental_health_voice',
            'user_input': voice_data,
            'voice_metadata': {
                'transcription': speech_result['text'],
                'confidence': speech_result['confidence'],
                'medical_terms_found': medical_analysis['medical_terms_found'],
                'audio_duration': speech_result.get('duration', 0),
                'detected_language': detected_language,
                'user_language_preference': language_preference
            },
            'status': 'processing'
        }

        interaction = Interaction.from_dict(interaction_data)

        # Save initial interaction
        firebase_service.save_interaction(interaction.to_dict())

        # Call AI service for assessment (same as text input)
        try:
            ai_response = ai_service.assess_mental_health(
                assessment_type=assessment_type,
                responses=voice_data['responses'],
                symptoms=voice_data['symptoms'],
                duration=voice_data['duration'],
                triggers=[],
                user_context={'voice_input': True, 'transcription_confidence': speech_result['confidence']}
            )

            # Update interaction with AI response
            interaction.set_ai_response(ai_response, 0)
            interaction.update_status('completed')
            firebase_service.save_interaction(interaction.to_dict())

            # Prepare response
            response_data = {
                'interaction_id': interaction.interaction_id,
                'voice_processing': {
                    'transcription': speech_result['text'],
                    'confidence': speech_result['confidence'],
                    'medical_terms_detected': medical_analysis['medical_terms_found']
                },
                'assessment': ai_response.get('assessment', {}),
                'risk_level': ai_response.get('risk_level', 'low'),
                'recommendations': ai_response.get('recommendations', []),
                'crisis_intervention_needed': ai_response.get('crisis_intervention_needed', False)
            }

            # Add crisis resources if needed
            if ai_response.get('crisis_intervention_needed', False):
                response_data['crisis_resources'] = {
                    'national_suicide_prevention_lifeline': '988',
                    'crisis_text_line': 'Text HOME to 741741',
                    'emergency_services': '911'
                }

            return generate_response(
                success=True,
                data=response_data,
                message="Voice mental health assessment completed successfully"
            )

        except Exception as ai_error:
            # AI service failed - update interaction and return fallback
            interaction.update_status('error', str(ai_error))
            firebase_service.save_interaction(interaction.to_dict())

            fallback_response = {
                'interaction_id': interaction.interaction_id,
                'voice_processing': {
                    'transcription': speech_result['text'],
                    'confidence': speech_result['confidence']
                },
                'message': 'Voice processed successfully, but AI assessment temporarily unavailable',
                'crisis_resources': {
                    'national_suicide_prevention_lifeline': '988',
                    'crisis_text_line': 'Text HOME to 741741',
                    'emergency_services': '911'
                }
            }

            return generate_response(
                success=True,  # Voice processing succeeded
                data=fallback_response,
                message="Voice processed, AI assessment temporarily unavailable"
            )

    except Exception as e:
        current_app.logger.error(f"Error processing voice input: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to process voice input",
            status_code=500
        )

@mental_health_bp.route('/speech/health', methods=['GET'])
@handle_errors
def check_speech_service():
    """Check speech-to-text service health"""
    try:
        from services.speech_service import SpeechService
        speech_service = SpeechService()

        health_status = speech_service.health_check()

        return generate_response(
            success=health_status['available'],
            data=health_status,
            message=health_status['message']
        )

    except Exception as e:
        current_app.logger.error(f"Speech service health check failed: {str(e)}")
        return generate_response(
            success=False,
            message="Speech service health check failed",
            status_code=500
        )

@mental_health_bp.route('/mental-health/resources', methods=['GET'])
@handle_errors
def get_mental_health_resources():
    """
    Get mental health resources and crisis information
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    """
    try:
        resources = {
            'crisis_hotlines': {
                'national_suicide_prevention_lifeline': {
                    'number': '988',
                    'description': '24/7 crisis support and suicide prevention',
                    'website': 'https://suicidepreventionlifeline.org'
                },
                'crisis_text_line': {
                    'number': 'Text HOME to 741741',
                    'description': '24/7 crisis support via text',
                    'website': 'https://www.crisistextline.org'
                },
                'samhsa_helpline': {
                    'number': '1-800-662-4357',
                    'description': 'Substance abuse and mental health services',
                    'website': 'https://www.samhsa.gov'
                }
            },
            'online_resources': [
                {
                    'name': 'Mental Health America',
                    'url': 'https://www.mhanational.org',
                    'description': 'Mental health information and screening tools'
                },
                {
                    'name': 'National Alliance on Mental Illness (NAMI)',
                    'url': 'https://www.nami.org',
                    'description': 'Support groups and educational resources'
                },
                {
                    'name': 'Anxiety and Depression Association of America',
                    'url': 'https://adaa.org',
                    'description': 'Resources for anxiety and depression'
                }
            ],
            'self_care_tips': [
                'Practice deep breathing exercises',
                'Maintain a regular sleep schedule',
                'Engage in physical activity',
                'Connect with supportive friends and family',
                'Limit alcohol and substance use',
                'Practice mindfulness or meditation',
                'Seek professional help when needed'
            ]
        }
        
        return generate_response(
            success=True,
            data=resources,
            message="Mental health resources retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving mental health resources: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to retrieve mental health resources",
            status_code=500
        )
