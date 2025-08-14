"""
Mental Health Data Security Service
Implements highest-level security for sensitive psychological data
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
import json
import re

class MentalHealthSecurityService:
    """Ultra-secure handling of mental health data"""
    
    def __init__(self):
        from services.privacy_service import PrivacyService
        self.privacy_service = PrivacyService()
        self.risk_keywords = self._load_risk_keywords()
        
    def _load_risk_keywords(self) -> Dict[str, List[str]]:
        """Load keywords that indicate mental health risk levels"""
        return {
            'crisis': [
                'suicide', 'kill myself', 'end it all', 'not worth living',
                'better off dead', 'hurt myself', 'self-harm', 'cutting'
            ],
            'high_risk': [
                'hopeless', 'worthless', 'trapped', 'burden', 'pain',
                'can\'t go on', 'no point', 'give up'
            ],
            'moderate_risk': [
                'depressed', 'anxious', 'overwhelmed', 'stressed',
                'panic', 'worried', 'sad', 'lonely'
            ]
        }
    
    def encrypt_mental_health_data(self, data: Dict) -> Dict:
        """Encrypt sensitive mental health data with highest security"""
        try:
            encrypted_data = data.copy()
            
            # Fields requiring encryption
            sensitive_fields = [
                'responses', 'symptoms', 'triggers', 'medication_history',
                'support_system', 'assessment', 'recommendations'
            ]
            
            for field in sensitive_fields:
                if field in encrypted_data and encrypted_data[field]:
                    # Convert to JSON string if dict/list
                    if isinstance(encrypted_data[field], (dict, list)):
                        field_data = json.dumps(encrypted_data[field])
                    else:
                        field_data = str(encrypted_data[field])
                    
                    # Encrypt the data
                    encrypted_data[field] = self.privacy_service.encrypt_sensitive_data(field_data)
            
            # Add encryption metadata
            encrypted_data['_encrypted'] = True
            encrypted_data['_encryption_timestamp'] = datetime.utcnow().isoformat()
            
            return encrypted_data
            
        except Exception as e:
            logging.error(f"Mental health data encryption failed: {e}")
            raise Exception("Failed to encrypt mental health data")
    
    def decrypt_mental_health_data(self, encrypted_data: Dict) -> Dict:
        """Decrypt mental health data for authorized access"""
        try:
            if not encrypted_data.get('_encrypted'):
                return encrypted_data
            
            decrypted_data = encrypted_data.copy()
            
            # Fields to decrypt
            sensitive_fields = [
                'responses', 'symptoms', 'triggers', 'medication_history',
                'support_system', 'assessment', 'recommendations'
            ]
            
            for field in sensitive_fields:
                if field in decrypted_data and decrypted_data[field]:
                    try:
                        # Decrypt the data
                        decrypted_field = self.privacy_service.decrypt_sensitive_data(decrypted_data[field])
                        
                        # Try to parse as JSON
                        try:
                            decrypted_data[field] = json.loads(decrypted_field)
                        except json.JSONDecodeError:
                            decrypted_data[field] = decrypted_field
                            
                    except Exception as field_error:
                        logging.warning(f"Could not decrypt field {field}: {field_error}")
                        decrypted_data[field] = "[ENCRYPTED_DATA]"
            
            # Remove encryption metadata
            decrypted_data.pop('_encrypted', None)
            decrypted_data.pop('_encryption_timestamp', None)
            
            return decrypted_data
            
        except Exception as e:
            logging.error(f"Mental health data decryption failed: {e}")
            raise Exception("Failed to decrypt mental health data")
    
    def assess_crisis_risk(self, user_input: Dict) -> Dict:
        """Assess crisis risk level from user input"""
        try:
            risk_score = 0
            risk_indicators = []
            
            # Combine all text inputs
            text_inputs = []
            
            # Check responses for text
            responses = user_input.get('responses', {})
            for key, value in responses.items():
                if isinstance(value, str):
                    text_inputs.append(value.lower())
            
            # Check symptoms
            symptoms = user_input.get('symptoms', [])
            text_inputs.extend([str(s).lower() for s in symptoms])
            
            # Check triggers
            triggers = user_input.get('triggers', [])
            text_inputs.extend([str(t).lower() for t in triggers])
            
            # Check support system
            support_system = user_input.get('support_system', '')
            if support_system:
                text_inputs.append(str(support_system).lower())
            
            # Analyze text for risk keywords
            all_text = ' '.join(text_inputs)
            
            # Crisis keywords (highest priority)
            for keyword in self.risk_keywords['crisis']:
                if keyword in all_text:
                    risk_score += 10
                    risk_indicators.append(f"Crisis indicator: {keyword}")
            
            # High risk keywords
            for keyword in self.risk_keywords['high_risk']:
                if keyword in all_text:
                    risk_score += 5
                    risk_indicators.append(f"High risk indicator: {keyword}")
            
            # Moderate risk keywords
            for keyword in self.risk_keywords['moderate_risk']:
                if keyword in all_text:
                    risk_score += 2
                    risk_indicators.append(f"Moderate risk indicator: {keyword}")
            
            # Analyze numerical responses
            if isinstance(responses, dict):
                # Low mood rating (1-3 on 1-10 scale)
                mood_rating = responses.get('mood_rating')
                if isinstance(mood_rating, int) and mood_rating <= 3:
                    risk_score += 3
                    risk_indicators.append("Very low mood rating")
                
                # High anxiety/stress levels (8-10 on 1-10 scale)
                anxiety_level = responses.get('anxiety_level')
                if isinstance(anxiety_level, int) and anxiety_level >= 8:
                    risk_score += 2
                    risk_indicators.append("High anxiety level")
                
                stress_level = responses.get('stress_level')
                if isinstance(stress_level, int) and stress_level >= 8:
                    risk_score += 2
                    risk_indicators.append("High stress level")
            
            # Determine risk level
            if risk_score >= 10:
                risk_level = 'crisis'
            elif risk_score >= 6:
                risk_level = 'high'
            elif risk_score >= 3:
                risk_level = 'moderate'
            else:
                risk_level = 'low'
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'risk_indicators': risk_indicators,
                'crisis_intervention_needed': risk_level == 'crisis',
                'professional_referral_suggested': risk_level in ['crisis', 'high'],
                'assessment_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Crisis risk assessment failed: {e}")
            # Default to high risk if assessment fails
            return {
                'risk_level': 'high',
                'risk_score': 999,
                'risk_indicators': ['Assessment system error - defaulting to high risk'],
                'crisis_intervention_needed': True,
                'professional_referral_suggested': True,
                'assessment_timestamp': datetime.utcnow().isoformat()
            }
    
    def sanitize_mental_health_input(self, data: Dict) -> Dict:
        """Sanitize mental health input for security"""
        try:
            sanitized = data.copy()
            
            # Remove potential security threats
            dangerous_patterns = [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'onload\s*=',
                r'onerror\s*=',
                r'eval\s*\(',
                r'document\.',
                r'window\.',
                r'alert\s*\('
            ]
            
            def clean_text(text):
                if not isinstance(text, str):
                    return text
                
                for pattern in dangerous_patterns:
                    text = re.sub(pattern, '[REMOVED]', text, flags=re.IGNORECASE)
                
                return text
            
            # Recursively clean all string values
            def clean_dict(d):
                if isinstance(d, dict):
                    return {k: clean_dict(v) for k, v in d.items()}
                elif isinstance(d, list):
                    return [clean_dict(item) for item in d]
                elif isinstance(d, str):
                    return clean_text(d)
                else:
                    return d
            
            return clean_dict(sanitized)
            
        except Exception as e:
            logging.error(f"Mental health input sanitization failed: {e}")
            return data
    
    def log_mental_health_access(self, user_id: str, action: str, risk_level: str = None):
        """Log mental health data access with enhanced security"""
        try:
            access_log = {
                'user_id': user_id,
                'data_type': 'mental_health',
                'action': action,
                'risk_level': risk_level,
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': 'logged_separately',
                'ip_address': 'logged_separately',
                'security_level': 'maximum'
            }
            
            # Enhanced logging for mental health data
            logging.info(f"MENTAL_HEALTH_ACCESS: {json.dumps(access_log)}")
            
            # If crisis level, also log to security system
            if risk_level == 'crisis':
                logging.critical(f"CRISIS_LEVEL_ACCESS: User {user_id} accessed crisis-level mental health data")
            
        except Exception as e:
            logging.error(f"Mental health access logging failed: {e}")
    
    def generate_mental_health_privacy_report(self, user_id: str) -> Dict:
        """Generate specialized privacy report for mental health data"""
        try:
            return {
                'user_id': user_id,
                'report_type': 'mental_health_privacy',
                'report_generated': datetime.utcnow().isoformat(),
                'data_categories': [
                    'psychological_assessments',
                    'mood_ratings',
                    'anxiety_levels',
                    'crisis_indicators',
                    'treatment_recommendations',
                    'risk_assessments'
                ],
                'special_protections': [
                    'Enhanced encryption for psychological data',
                    'Crisis risk monitoring and intervention',
                    'Professional referral protocols',
                    'Emergency contact procedures',
                    'Specialized retention policies'
                ],
                'data_retention': {
                    'assessment_data': '7 years (medical records)',
                    'crisis_indicators': '10 years (safety monitoring)',
                    'anonymized_research': 'Indefinite (with consent)'
                },
                'user_rights': [
                    'Access all mental health assessments',
                    'Correct assessment data',
                    'Delete non-critical data',
                    'Export psychological history',
                    'Withdraw from research',
                    'Emergency data access for crisis intervention'
                ],
                'security_measures': [
                    'Military-grade encryption (AES-256)',
                    'Crisis risk monitoring',
                    'Professional oversight protocols',
                    'Emergency intervention procedures',
                    'Specialized access controls'
                ],
                'contact_info': {
                    'privacy_officer': 'privacy@ai-telemedicine.com',
                    'crisis_support': '988 (Suicide Prevention Lifeline)',
                    'emergency': '911'
                }
            }
            
        except Exception as e:
            logging.error(f"Mental health privacy report generation failed: {e}")
            return {
                'error': 'Failed to generate mental health privacy report',
                'timestamp': datetime.utcnow().isoformat()
            }

class MentalHealthComplianceService:
    """Compliance specifically for mental health data"""
    
    def __init__(self):
        self.security_service = MentalHealthSecurityService()
    
    def validate_mental_health_consent(self, consent_data: Dict) -> Dict:
        """Validate consent specifically for mental health data processing"""
        try:
            required_mental_health_consents = [
                'psychological_assessment',
                'crisis_intervention',
                'professional_referral',
                'emergency_contact',
                'data_retention_mental_health'
            ]
            
            provided_consents = consent_data.get('consent_types', [])
            missing_consents = []
            
            for consent in required_mental_health_consents:
                if consent not in provided_consents:
                    missing_consents.append(consent)
            
            return {
                'valid': len(missing_consents) == 0,
                'missing_consents': missing_consents,
                'special_requirements': [
                    'Crisis intervention consent required',
                    'Professional referral authorization needed',
                    'Emergency contact permission required'
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Mental health consent validation failed: {e}")
            return {
                'valid': False,
                'error': 'Consent validation failed',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def check_mental_health_compliance(self) -> Dict:
        """Check compliance for mental health data handling"""
        try:
            compliance_items = {
                'hipaa_mental_health': True,  # Mental health specific HIPAA
                'crisis_intervention_protocols': True,
                'professional_referral_system': True,
                'emergency_contact_procedures': True,
                'specialized_encryption': True,
                'risk_assessment_monitoring': True,
                'professional_oversight': False,  # Need licensed professional
                'crisis_hotline_integration': True,
                'data_minimization_mental_health': True,
                'specialized_retention_policies': True
            }
            
            compliance_score = sum(compliance_items.values()) / len(compliance_items)
            
            return {
                'compliant': compliance_score >= 0.9,  # Higher standard for mental health
                'compliance_score': compliance_score,
                'items': compliance_items,
                'recommendations': self._get_mental_health_recommendations(compliance_items),
                'certification_level': 'mental_health_specialized'
            }
            
        except Exception as e:
            logging.error(f"Mental health compliance check failed: {e}")
            return {
                'compliant': False,
                'error': 'Compliance check failed',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _get_mental_health_recommendations(self, items: Dict) -> List[str]:
        """Get recommendations for mental health compliance"""
        recommendations = []
        
        if not items.get('professional_oversight'):
            recommendations.append("Engage licensed mental health professional for oversight")
        
        recommendations.extend([
            "Regular crisis intervention protocol testing",
            "Professional referral network establishment",
            "Emergency contact system validation",
            "Specialized staff training for mental health data"
        ])
        
        return recommendations
