"""
Validation service for AI Telemedicine Platform
Handles input validation and data sanitization
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

class ValidationService:
    """Service class for data validation"""
    
    def __init__(self):
        # Email regex pattern
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # Phone regex pattern (supports various formats)
        self.phone_pattern = re.compile(r'^[\+]?[1-9][\d]{0,15}$')
        
        # Common validation rules
        self.max_string_length = 1000
        self.max_list_length = 50
    
    def validate_required_fields(self, data: Dict, required_fields: List[str]) -> Dict[str, Any]:
        """Validate that all required fields are present and not empty"""
        missing_fields = []
        
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
            elif isinstance(data[field], str) and not data[field].strip():
                missing_fields.append(field)
            elif isinstance(data[field], list) and len(data[field]) == 0:
                missing_fields.append(field)
        
        return {
            'valid': len(missing_fields) == 0,
            'message': f"Missing required fields: {', '.join(missing_fields)}" if missing_fields else "All required fields present"
        }
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        return bool(self.email_pattern.match(email.strip()))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        if not phone or not isinstance(phone, str):
            return False
        
        # Remove common separators
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        return bool(self.phone_pattern.match(cleaned_phone))
    
    def validate_date_string(self, date_string: str) -> Dict[str, Any]:
        """Validate ISO date string format"""
        try:
            if not date_string:
                return {'valid': False, 'message': 'Date string is required'}
            
            # Try to parse the date
            parsed_date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            
            return {
                'valid': True,
                'parsed_date': parsed_date,
                'message': 'Valid date format'
            }
        except ValueError as e:
            return {
                'valid': False,
                'message': f'Invalid date format: {str(e)}'
            }
    
    def validate_string_length(self, text: str, min_length: int = 0, max_length: int = None) -> Dict[str, Any]:
        """Validate string length"""
        if not isinstance(text, str):
            return {'valid': False, 'message': 'Input must be a string'}
        
        text_length = len(text.strip())
        max_len = max_length or self.max_string_length
        
        if text_length < min_length:
            return {'valid': False, 'message': f'Text must be at least {min_length} characters long'}
        
        if text_length > max_len:
            return {'valid': False, 'message': f'Text must be no more than {max_len} characters long'}
        
        return {'valid': True, 'message': 'Valid string length'}
    
    def validate_list_length(self, items: List, min_length: int = 0, max_length: int = None) -> Dict[str, Any]:
        """Validate list length"""
        if not isinstance(items, list):
            return {'valid': False, 'message': 'Input must be a list'}
        
        list_length = len(items)
        max_len = max_length or self.max_list_length
        
        if list_length < min_length:
            return {'valid': False, 'message': f'List must contain at least {min_length} items'}
        
        if list_length > max_len:
            return {'valid': False, 'message': f'List must contain no more than {max_len} items'}
        
        return {'valid': True, 'message': 'Valid list length'}
    
    def validate_numeric_range(self, value: Any, min_value: float = None, max_value: float = None) -> Dict[str, Any]:
        """Validate numeric value within range"""
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return {'valid': False, 'message': 'Value must be numeric'}
        
        if min_value is not None and numeric_value < min_value:
            return {'valid': False, 'message': f'Value must be at least {min_value}'}
        
        if max_value is not None and numeric_value > max_value:
            return {'valid': False, 'message': f'Value must be no more than {max_value}'}
        
        return {'valid': True, 'message': 'Valid numeric value', 'value': numeric_value}
    
    def validate_choice(self, value: str, valid_choices: List[str]) -> Dict[str, Any]:
        """Validate that value is one of the valid choices"""
        if not isinstance(value, str):
            return {'valid': False, 'message': 'Value must be a string'}
        
        if value not in valid_choices:
            return {'valid': False, 'message': f'Value must be one of: {", ".join(valid_choices)}'}
        
        return {'valid': True, 'message': 'Valid choice'}
    
    def sanitize_string(self, text: str) -> str:
        """Sanitize string input by removing potentially harmful content"""
        if not isinstance(text, str):
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove script tags and content
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove potentially harmful characters
        text = re.sub(r'[<>"\']', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def validate_symptoms_list(self, symptoms: List[str]) -> Dict[str, Any]:
        """Validate symptoms list specifically"""
        if not isinstance(symptoms, list):
            return {'valid': False, 'message': 'Symptoms must be provided as a list'}
        
        if len(symptoms) == 0:
            return {'valid': False, 'message': 'At least one symptom is required'}
        
        if len(symptoms) > 10:  # Reasonable limit for symptoms
            return {'valid': False, 'message': 'Maximum 10 symptoms allowed per assessment'}
        
        # Validate each symptom
        for i, symptom in enumerate(symptoms):
            if not isinstance(symptom, str):
                return {'valid': False, 'message': f'Symptom {i+1} must be a string'}
            
            if len(symptom.strip()) < 2:
                return {'valid': False, 'message': f'Symptom {i+1} must be at least 2 characters long'}
            
            if len(symptom.strip()) > 100:
                return {'valid': False, 'message': f'Symptom {i+1} must be no more than 100 characters long'}
        
        return {'valid': True, 'message': 'Valid symptoms list'}
    
    def validate_user_id(self, user_id: str) -> Dict[str, Any]:
        """Validate user ID format"""
        if not isinstance(user_id, str):
            return {'valid': False, 'message': 'User ID must be a string'}
        
        user_id = user_id.strip()
        
        if len(user_id) < 3:
            return {'valid': False, 'message': 'User ID must be at least 3 characters long'}
        
        if len(user_id) > 50:
            return {'valid': False, 'message': 'User ID must be no more than 50 characters long'}
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
            return {'valid': False, 'message': 'User ID can only contain letters, numbers, hyphens, and underscores'}
        
        return {'valid': True, 'message': 'Valid user ID'}
    
    def validate_severity_level(self, severity: Any) -> Dict[str, Any]:
        """Validate severity level (1-10 scale)"""
        try:
            severity_int = int(severity)
        except (ValueError, TypeError):
            return {'valid': False, 'message': 'Severity level must be an integer'}
        
        if severity_int < 1 or severity_int > 10:
            return {'valid': False, 'message': 'Severity level must be between 1 and 10'}
        
        return {'valid': True, 'message': 'Valid severity level', 'value': severity_int}
    
    def validate_json_structure(self, data: Dict, expected_structure: Dict) -> Dict[str, Any]:
        """Validate JSON structure against expected schema"""
        errors = []
        
        def check_structure(actual, expected, path=""):
            for key, expected_type in expected.items():
                current_path = f"{path}.{key}" if path else key
                
                if key not in actual:
                    if expected_type.get('required', True):
                        errors.append(f"Missing required field: {current_path}")
                    continue
                
                actual_value = actual[key]
                expected_type_class = expected_type.get('type')
                
                if expected_type_class and not isinstance(actual_value, expected_type_class):
                    errors.append(f"Field {current_path} must be of type {expected_type_class.__name__}")
                
                # Check nested structures
                if 'structure' in expected_type and isinstance(actual_value, dict):
                    check_structure(actual_value, expected_type['structure'], current_path)
        
        check_structure(data, expected_structure)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'message': 'Valid JSON structure' if len(errors) == 0 else f"Validation errors: {'; '.join(errors)}"
        }
