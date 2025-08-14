"""
Interaction data model for AI Telemedicine Platform
Defines structure for user interactions with AI system
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid

class Interaction:
    """User interaction model for symptom checks and assessments"""
    
    def __init__(self, interaction_id: str = None, **kwargs):
        self.interaction_id = interaction_id or str(uuid.uuid4())
        self.user_id = kwargs.get('user_id', '')
        self.interaction_type = kwargs.get('interaction_type', '')  # 'symptom_check', 'mental_health', 'general'
        self.timestamp = kwargs.get('timestamp', datetime.utcnow().isoformat())
        
        # Input data
        self.user_input = kwargs.get('user_input', {})
        self.symptoms = kwargs.get('symptoms', [])
        self.severity_level = kwargs.get('severity_level')  # 1-10 scale
        self.duration = kwargs.get('duration')  # How long symptoms have persisted
        
        # AI Response data
        # TODO: REQUEST FROM TEAM LEAD - Define AI response structure
        self.ai_response = kwargs.get('ai_response', {})
        self.assessment_result = kwargs.get('assessment_result', {})
        self.recommendations = kwargs.get('recommendations', [])
        self.urgency_level = kwargs.get('urgency_level')  # 'low', 'medium', 'high', 'emergency'
        
        # Processing metadata
        self.processing_time = kwargs.get('processing_time')  # Time taken for AI processing
        self.confidence_score = kwargs.get('confidence_score')  # AI confidence in assessment
        self.model_version = kwargs.get('model_version')  # AI model version used
        
        # Follow-up information
        self.follow_up_required = kwargs.get('follow_up_required', False)
        self.follow_up_timeframe = kwargs.get('follow_up_timeframe')
        self.doctor_referral_suggested = kwargs.get('doctor_referral_suggested', False)
        
        # Status tracking
        self.status = kwargs.get('status', 'completed')  # 'pending', 'processing', 'completed', 'error'
        self.error_message = kwargs.get('error_message')
        
        # Privacy and consent
        self.data_retention_consent = kwargs.get('data_retention_consent', True)
        self.research_consent = kwargs.get('research_consent', False)
    
    def to_dict(self) -> Dict:
        """Convert interaction object to dictionary for Firebase storage"""
        return {
            'interaction_id': self.interaction_id,
            'user_id': self.user_id,
            'interaction_type': self.interaction_type,
            'timestamp': self.timestamp,
            'user_input': self.user_input,
            'symptoms': self.symptoms,
            'severity_level': self.severity_level,
            'duration': self.duration,
            'ai_response': self.ai_response,
            'assessment_result': self.assessment_result,
            'recommendations': self.recommendations,
            'urgency_level': self.urgency_level,
            'processing_time': self.processing_time,
            'confidence_score': self.confidence_score,
            'model_version': self.model_version,
            'follow_up_required': self.follow_up_required,
            'follow_up_timeframe': self.follow_up_timeframe,
            'doctor_referral_suggested': self.doctor_referral_suggested,
            'status': self.status,
            'error_message': self.error_message,
            'data_retention_consent': self.data_retention_consent,
            'research_consent': self.research_consent
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Interaction':
        """Create Interaction object from dictionary"""
        return cls(**data)
    
    def update_status(self, status: str, error_message: str = None):
        """Update interaction status"""
        self.status = status
        if error_message:
            self.error_message = error_message
    
    def set_ai_response(self, ai_response: Dict, processing_time: float = None):
        """Set AI response data"""
        self.ai_response = ai_response
        self.assessment_result = ai_response.get('assessment', {})
        self.recommendations = ai_response.get('recommendations', [])
        self.urgency_level = ai_response.get('urgency_level', 'low')
        self.confidence_score = ai_response.get('confidence_score')
        self.model_version = ai_response.get('model_version')
        
        if processing_time:
            self.processing_time = processing_time
        
        # Determine follow-up requirements based on urgency
        if self.urgency_level in ['high', 'emergency']:
            self.follow_up_required = True
            self.doctor_referral_suggested = True
            self.follow_up_timeframe = '24 hours' if self.urgency_level == 'high' else 'immediate'
        elif self.urgency_level == 'medium':
            self.follow_up_required = True
            self.follow_up_timeframe = '1 week'
    
    def validate(self) -> Dict[str, any]:
        """Validate interaction data"""
        errors = []
        
        if not self.user_id:
            errors.append("User ID is required")
        
        if not self.interaction_type:
            errors.append("Interaction type is required")
        
        if self.interaction_type not in ['symptom_check', 'mental_health', 'general']:
            errors.append("Invalid interaction type")
        
        if self.severity_level and (self.severity_level < 1 or self.severity_level > 10):
            errors.append("Severity level must be between 1 and 10")
        
        if self.urgency_level and self.urgency_level not in ['low', 'medium', 'high', 'emergency']:
            errors.append("Invalid urgency level")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_summary(self) -> Dict:
        """Get interaction summary for history display"""
        return {
            'interaction_id': self.interaction_id,
            'interaction_type': self.interaction_type,
            'timestamp': self.timestamp,
            'symptoms': self.symptoms[:3] if self.symptoms else [],  # First 3 symptoms
            'urgency_level': self.urgency_level,
            'status': self.status,
            'follow_up_required': self.follow_up_required
        }
