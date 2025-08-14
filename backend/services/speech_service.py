"""
Speech-to-Text Service for AI Telemedicine Platform
Converts voice input to text for symptom processing
"""

import requests
import base64
import logging
import json
from typing import Dict, Optional
from config.settings import Config

class SpeechService:
    """Service for converting speech to text"""
    
    def __init__(self):
        self.api_key = Config.SPEECH_API_KEY
        self.service_url = Config.SPEECH_SERVICE_URL
        self.timeout = Config.SPEECH_SERVICE_TIMEOUT
        
    def detect_language(self, text: str) -> str:
        """Detect language from text input"""
        try:
            # Simple language detection based on common words
            language_indicators = {
                'en': ['i', 'am', 'feel', 'have', 'pain', 'hurt', 'sick', 'tired'],
                'es': ['yo', 'soy', 'siento', 'tengo', 'dolor', 'duele', 'enfermo', 'cansado'],
                'fr': ['je', 'suis', 'sens', 'ai', 'douleur', 'mal', 'malade', 'fatigué'],
                'de': ['ich', 'bin', 'fühle', 'habe', 'schmerz', 'weh', 'krank', 'müde'],
                'pt': ['eu', 'sou', 'sinto', 'tenho', 'dor', 'dói', 'doente', 'cansado'],
                'it': ['io', 'sono', 'sento', 'ho', 'dolore', 'male', 'malato', 'stanco'],
                'zh': ['我', '是', '感觉', '有', '疼痛', '痛', '生病', '累'],
                'ja': ['私', 'です', '感じ', 'ある', '痛み', '痛い', '病気', '疲れ'],
                'ar': ['أنا', 'أشعر', 'لدي', 'ألم', 'يؤلم', 'مريض', 'متعب'],
                'hi': ['मैं', 'हूं', 'महसूस', 'है', 'दर्द', 'दुखता', 'बीमार', 'थका']
            }

            text_lower = text.lower()
            language_scores = {}

            for lang, indicators in language_indicators.items():
                score = 0
                for indicator in indicators:
                    if indicator in text_lower:
                        score += 1
                language_scores[lang] = score

            # Return language with highest score, default to English
            detected_lang = max(language_scores, key=language_scores.get) if max(language_scores.values()) > 0 else 'en'

            return detected_lang

        except Exception as e:
            logging.error(f"Language detection failed: {e}")
            return 'en'  # Default to English

    def convert_audio_to_text(self, audio_file, language_code: str = 'en-US') -> Dict:
        """
        Convert audio file to text using Google Speech-to-Text API
        
        Args:
            audio_file: Audio file from request.files
            
        Returns:
            Dict with transcribed text and confidence
        """
        try:
            if not self.api_key or self.api_key == 'your-speech-to-text-api-key':
                # Development mode - return mock response
                logging.info("[DEV MODE] Speech-to-Text: Using mock response")
                return {
                    'success': True,
                    'text': 'I have been feeling anxious and depressed lately',
                    'confidence': 0.95,
                    'language': 'en-US',
                    'duration': 3.2
                }
            
            # Read audio file
            audio_content = audio_file.read()
            
            # Encode audio to base64
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            # Prepare request payload for Google Speech-to-Text
            payload = {
                'config': {
                    'encoding': 'WEBM_OPUS',  # Common web audio format
                    'sampleRateHertz': 48000,
                    'languageCode': language_code,  # Support multiple languages
                    'alternativeLanguageCodes': ['en-US', 'es-ES', 'fr-FR', 'de-DE', 'pt-BR', 'it-IT'],  # Fallback languages
                    'enableAutomaticPunctuation': True,
                    'model': 'medical_conversation',  # Optimized for medical terms
                    'useEnhanced': True
                },
                'audio': {
                    'content': audio_base64
                }
            }
            
            # Make API request
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': self.api_key
            }
            
            response = requests.post(
                self.service_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract transcription
                if 'results' in result and len(result['results']) > 0:
                    transcript = result['results'][0]['alternatives'][0]['transcript']
                    confidence = result['results'][0]['alternatives'][0].get('confidence', 0.0)
                    
                    return {
                        'success': True,
                        'text': transcript.strip(),
                        'confidence': confidence,
                        'language': 'en-US',
                        'raw_response': result
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No speech detected in audio',
                        'text': '',
                        'confidence': 0.0
                    }
            else:
                logging.error(f"Speech API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Speech service error: {response.status_code}',
                    'text': '',
                    'confidence': 0.0
                }
                
        except Exception as e:
            logging.error(f"Speech-to-text conversion failed: {str(e)}")
            return {
                'success': False,
                'error': f'Speech processing failed: {str(e)}',
                'text': '',
                'confidence': 0.0
            }
    
    def validate_audio_file(self, audio_file) -> Dict:
        """Validate audio file format and size"""
        try:
            # Check file size (max 10MB)
            audio_file.seek(0, 2)  # Seek to end
            file_size = audio_file.tell()
            audio_file.seek(0)  # Reset to beginning
            
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                return {
                    'valid': False,
                    'error': 'Audio file too large (max 10MB)'
                }
            
            if file_size == 0:
                return {
                    'valid': False,
                    'error': 'Audio file is empty'
                }
            
            # Check file type
            filename = audio_file.filename.lower() if audio_file.filename else ''
            allowed_extensions = ['.wav', '.mp3', '.webm', '.ogg', '.m4a']
            
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                return {
                    'valid': False,
                    'error': f'Unsupported audio format. Allowed: {", ".join(allowed_extensions)}'
                }
            
            return {
                'valid': True,
                'file_size': file_size,
                'filename': filename
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Audio validation failed: {str(e)}'
            }
    
    def extract_medical_terms(self, text: str) -> Dict:
        """Extract and validate medical terms from transcribed text"""
        try:
            # Common medical symptom keywords
            medical_keywords = [
                'pain', 'ache', 'hurt', 'sore', 'tender',
                'fever', 'temperature', 'hot', 'chills',
                'nausea', 'vomit', 'sick', 'dizzy',
                'tired', 'fatigue', 'exhausted', 'weak',
                'anxious', 'anxiety', 'worried', 'stress',
                'depressed', 'depression', 'sad', 'hopeless',
                'headache', 'migraine', 'head pain',
                'chest pain', 'breathing', 'shortness of breath',
                'stomach', 'abdominal', 'belly',
                'cough', 'sneeze', 'runny nose', 'congestion'
            ]
            
            text_lower = text.lower()
            found_terms = []
            
            for term in medical_keywords:
                if term in text_lower:
                    found_terms.append(term)
            
            # Extract potential symptoms using simple patterns
            symptoms = []
            if 'feel' in text_lower or 'feeling' in text_lower:
                # Extract what comes after "feel/feeling"
                words = text_lower.split()
                for i, word in enumerate(words):
                    if word in ['feel', 'feeling'] and i + 1 < len(words):
                        next_words = ' '.join(words[i+1:i+4])  # Get next 3 words
                        symptoms.append(next_words)
            
            return {
                'medical_terms_found': found_terms,
                'extracted_symptoms': symptoms,
                'confidence_medical': len(found_terms) > 0,
                'processed_text': text
            }
            
        except Exception as e:
            logging.error(f"Medical term extraction failed: {str(e)}")
            return {
                'medical_terms_found': [],
                'extracted_symptoms': [text],  # Fallback to full text
                'confidence_medical': False,
                'processed_text': text
            }
    
    def health_check(self) -> Dict:
        """Check if speech service is available"""
        try:
            if not self.api_key or self.api_key == 'your-speech-to-text-api-key':
                return {
                    'status': 'development_mode',
                    'available': True,
                    'message': 'Running in development mode with mock responses'
                }
            
            # Simple health check - just verify API key format
            if len(self.api_key) > 10:  # Basic validation
                return {
                    'status': 'ready',
                    'available': True,
                    'message': 'Speech service configured and ready'
                }
            else:
                return {
                    'status': 'configuration_error',
                    'available': False,
                    'message': 'Invalid API key configuration'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'available': False,
                'message': f'Speech service health check failed: {str(e)}'
            }
