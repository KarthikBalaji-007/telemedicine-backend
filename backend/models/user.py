"""
User data model for AI Telemedicine Platform
Defines user profile structure and validation
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid

class User:
    """User profile model"""
    
    def __init__(self, user_id: str = None, **kwargs):
        self.user_id = user_id or str(uuid.uuid4())
        self.name = kwargs.get('name', '')
        self.email = kwargs.get('email', '')
        self.phone = kwargs.get('phone')
        self.date_of_birth = kwargs.get('date_of_birth')
        self.gender = kwargs.get('gender')
        self.medical_history = kwargs.get('medical_history', [])
        self.emergency_contact = kwargs.get('emergency_contact', {})
        self.created_at = kwargs.get('created_at', datetime.utcnow().isoformat())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow().isoformat())
        self.is_active = kwargs.get('is_active', True)
        
        # Privacy and consent
        self.privacy_consent = kwargs.get('privacy_consent', False)
        self.data_sharing_consent = kwargs.get('data_sharing_consent', False)
        
        # Preferences
        self.notification_preferences = kwargs.get('notification_preferences', {
            'email': True,
            'sms': False,
            'push': True
        })
        
        # Medical information
        self.allergies = kwargs.get('allergies', [])
        self.current_medications = kwargs.get('current_medications', [])
        self.chronic_conditions = kwargs.get('chronic_conditions', [])
    
    def to_dict(self) -> Dict:
        """Convert user object to dictionary for Firebase storage"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender,
            'medical_history': self.medical_history,
            'emergency_contact': self.emergency_contact,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'privacy_consent': self.privacy_consent,
            'data_sharing_consent': self.data_sharing_consent,
            'notification_preferences': self.notification_preferences,
            'allergies': self.allergies,
            'current_medications': self.current_medications,
            'chronic_conditions': self.chronic_conditions
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create User object from dictionary"""
        return cls(**data)
    
    def update(self, **kwargs):
        """Update user attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat()
    
    def validate(self) -> Dict[str, any]:
        """Validate user data"""
        errors = []
        
        if not self.name or len(self.name.strip()) < 2:
            errors.append("Name must be at least 2 characters long")
        
        if not self.email or '@' not in self.email:
            errors.append("Valid email address is required")
        
        if self.phone and len(self.phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) < 10:
            errors.append("Phone number must be at least 10 digits")
        
        if self.date_of_birth:
            try:
                birth_date = datetime.fromisoformat(self.date_of_birth.replace('Z', '+00:00'))
                if birth_date > datetime.now():
                    errors.append("Date of birth cannot be in the future")
            except ValueError:
                errors.append("Invalid date of birth format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_age(self) -> Optional[int]:
        """Calculate user age from date of birth"""
        if not self.date_of_birth:
            return None
        
        try:
            birth_date = datetime.fromisoformat(self.date_of_birth.replace('Z', '+00:00'))
            today = datetime.now()
            age = today.year - birth_date.year
            
            # Adjust if birthday hasn't occurred this year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            
            return age
        except ValueError:
            return None
    
    def get_public_profile(self) -> Dict:
        """Get public profile information (excluding sensitive data)"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'age': self.get_age(),
            'gender': self.gender,
            'created_at': self.created_at
        }
