"""
Conversation Service for Follow-up Questions and Chaining
Handles multi-turn conversations for better medical assessment
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from services.firebase_service import FirebaseService

class ConversationService:
    """Service for managing conversation chains and follow-up questions"""
    
    def __init__(self):
        self.firebase_service = FirebaseService()
        
    def generate_follow_up_questions(self, initial_assessment: Dict, symptoms: List[str]) -> Dict:
        """Generate follow-up questions based on initial assessment"""
        try:
            # Analyze symptoms to determine what follow-up questions to ask
            follow_up_questions = []
            question_context = {
                'assessment_id': initial_assessment.get('assessment_id'),
                'symptoms_analyzed': symptoms,
                'question_round': 1
            }
            
            # Pain-related follow-ups
            pain_symptoms = ['pain', 'ache', 'hurt', 'sore', 'tender', 'sharp', 'dull']
            if any(pain in ' '.join(symptoms).lower() for pain in pain_symptoms):
                follow_up_questions.extend([
                    {
                        'id': 'pain_scale',
                        'question': 'On a scale of 1-10, how would you rate your pain level?',
                        'type': 'scale',
                        'options': list(range(1, 11)),
                        'required': True
                    },
                    {
                        'id': 'pain_type',
                        'question': 'How would you describe the pain?',
                        'type': 'multiple_choice',
                        'options': ['Sharp/stabbing', 'Dull/aching', 'Burning', 'Throbbing', 'Cramping'],
                        'required': True
                    },
                    {
                        'id': 'pain_triggers',
                        'question': 'What makes the pain worse?',
                        'type': 'multiple_choice',
                        'options': ['Movement', 'Rest', 'Eating', 'Breathing', 'Touch', 'Nothing specific'],
                        'required': False
                    }
                ])
            
            # Fever-related follow-ups
            fever_symptoms = ['fever', 'temperature', 'hot', 'chills', 'sweating']
            if any(fever in ' '.join(symptoms).lower() for fever in fever_symptoms):
                follow_up_questions.extend([
                    {
                        'id': 'temperature_reading',
                        'question': 'What is your current temperature (if measured)?',
                        'type': 'number',
                        'unit': '°F',
                        'required': False
                    },
                    {
                        'id': 'fever_duration',
                        'question': 'How long have you had the fever?',
                        'type': 'multiple_choice',
                        'options': ['Less than 24 hours', '1-2 days', '3-5 days', 'More than 5 days'],
                        'required': True
                    }
                ])
            
            # Respiratory symptoms follow-ups
            respiratory_symptoms = ['cough', 'breathing', 'shortness', 'wheeze', 'chest']
            if any(resp in ' '.join(symptoms).lower() for resp in respiratory_symptoms):
                follow_up_questions.extend([
                    {
                        'id': 'breathing_difficulty',
                        'question': 'Are you having difficulty breathing?',
                        'type': 'yes_no',
                        'required': True
                    },
                    {
                        'id': 'cough_type',
                        'question': 'If you have a cough, is it:',
                        'type': 'multiple_choice',
                        'options': ['Dry cough', 'Cough with phlegm', 'Cough with blood', 'No cough'],
                        'required': False
                    }
                ])
            
            # Digestive symptoms follow-ups
            digestive_symptoms = ['nausea', 'vomit', 'stomach', 'abdominal', 'diarrhea', 'constipation']
            if any(digest in ' '.join(symptoms).lower() for digest in digestive_symptoms):
                follow_up_questions.extend([
                    {
                        'id': 'last_meal',
                        'question': 'When did you last eat, and what did you eat?',
                        'type': 'text',
                        'required': False
                    },
                    {
                        'id': 'digestive_frequency',
                        'question': 'How often are you experiencing these symptoms?',
                        'type': 'multiple_choice',
                        'options': ['Constantly', 'Several times a day', 'Once a day', 'Occasionally'],
                        'required': True
                    }
                ])
            
            # General follow-ups for all cases
            follow_up_questions.extend([
                {
                    'id': 'recent_travel',
                    'question': 'Have you traveled recently or been exposed to anyone who is sick?',
                    'type': 'yes_no_text',
                    'required': False
                },
                {
                    'id': 'medications',
                    'question': 'Are you currently taking any medications?',
                    'type': 'yes_no_text',
                    'required': False
                },
                {
                    'id': 'symptom_progression',
                    'question': 'Are your symptoms getting better, worse, or staying the same?',
                    'type': 'multiple_choice',
                    'options': ['Getting better', 'Getting worse', 'Staying the same', 'Fluctuating'],
                    'required': True
                }
            ])
            
            # Limit to most relevant questions (max 5 to avoid overwhelming user)
            prioritized_questions = follow_up_questions[:5]
            
            return {
                'success': True,
                'has_follow_up': len(prioritized_questions) > 0,
                'questions': prioritized_questions,
                'context': question_context,
                'total_questions': len(prioritized_questions),
                'estimated_time_minutes': len(prioritized_questions) * 0.5  # 30 seconds per question
            }
            
        except Exception as e:
            logging.error(f"Error generating follow-up questions: {e}")
            return {
                'success': False,
                'has_follow_up': False,
                'questions': [],
                'error': str(e)
            }
    
    def process_follow_up_answers(self, conversation_id: str, answers: Dict) -> Dict:
        """Process follow-up answers and generate enhanced assessment"""
        try:
            # Get original conversation context
            conversation = self.firebase_service.get_conversation(conversation_id)
            if not conversation:
                return {
                    'success': False,
                    'error': 'Conversation not found'
                }
            
            # Combine original symptoms with follow-up answers
            enhanced_context = {
                'original_symptoms': conversation.get('symptoms', []),
                'original_assessment': conversation.get('initial_assessment', {}),
                'follow_up_answers': answers,
                'enhanced_assessment_requested': True
            }
            
            # Analyze follow-up answers for risk escalation
            risk_factors = self._analyze_follow_up_risk(answers)
            
            # Generate enhanced assessment
            enhanced_assessment = {
                'assessment_id': f"enhanced_{conversation_id}",
                'original_risk_level': conversation.get('initial_assessment', {}).get('risk_level', 'unknown'),
                'enhanced_risk_level': risk_factors['risk_level'],
                'risk_escalation': risk_factors['escalated'],
                'additional_insights': risk_factors['insights'],
                'follow_up_summary': self._summarize_follow_up(answers),
                'updated_recommendations': risk_factors['recommendations'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save enhanced assessment
            conversation['enhanced_assessment'] = enhanced_assessment
            conversation['follow_up_completed'] = True
            self.firebase_service.save_conversation(conversation)
            
            return {
                'success': True,
                'enhanced_assessment': enhanced_assessment,
                'conversation_complete': True,
                'next_steps': enhanced_assessment['updated_recommendations']
            }
            
        except Exception as e:
            logging.error(f"Error processing follow-up answers: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _analyze_follow_up_risk(self, answers: Dict) -> Dict:
        """Analyze follow-up answers for risk level changes"""
        try:
            risk_score = 0
            insights = []
            recommendations = []
            escalated = False
            
            # Analyze pain scale
            pain_scale = answers.get('pain_scale')
            if pain_scale:
                if int(pain_scale) >= 8:
                    risk_score += 3
                    insights.append(f"Severe pain level ({pain_scale}/10) indicates significant discomfort")
                    recommendations.append("Consider immediate medical attention for severe pain")
                    escalated = True
                elif int(pain_scale) >= 6:
                    risk_score += 2
                    insights.append(f"Moderate to severe pain ({pain_scale}/10)")
                
            # Analyze breathing difficulty
            if answers.get('breathing_difficulty') == 'yes':
                risk_score += 4
                insights.append("Breathing difficulty is a serious symptom")
                recommendations.append("URGENT: Seek immediate medical attention for breathing problems")
                escalated = True
            
            # Analyze temperature
            temperature = answers.get('temperature_reading')
            if temperature:
                temp_float = float(temperature)
                if temp_float >= 103:
                    risk_score += 3
                    insights.append(f"High fever ({temp_float}°F) requires medical attention")
                    recommendations.append("High fever - see doctor or go to ER")
                    escalated = True
                elif temp_float >= 101:
                    risk_score += 2
                    insights.append(f"Moderate fever ({temp_float}°F)")
            
            # Analyze symptom progression
            progression = answers.get('symptom_progression')
            if progression == 'Getting worse':
                risk_score += 2
                insights.append("Worsening symptoms indicate need for medical evaluation")
                recommendations.append("Symptoms are worsening - consider seeing a healthcare provider")
            
            # Determine final risk level
            if risk_score >= 6:
                risk_level = 'HIGH'
            elif risk_score >= 3:
                risk_level = 'MODERATE'
            else:
                risk_level = 'LOW'
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'escalated': escalated,
                'insights': insights,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logging.error(f"Error analyzing follow-up risk: {e}")
            return {
                'risk_level': 'MODERATE',
                'risk_score': 3,
                'escalated': True,
                'insights': ['Error in risk analysis - defaulting to moderate risk'],
                'recommendations': ['Consult healthcare provider due to assessment error']
            }
    
    def _summarize_follow_up(self, answers: Dict) -> str:
        """Create a summary of follow-up answers"""
        try:
            summary_parts = []
            
            for key, value in answers.items():
                if value and str(value).strip():
                    # Convert key to readable format
                    readable_key = key.replace('_', ' ').title()
                    summary_parts.append(f"{readable_key}: {value}")
            
            return "; ".join(summary_parts) if summary_parts else "No additional information provided"
            
        except Exception as e:
            logging.error(f"Error creating follow-up summary: {e}")
            return "Summary unavailable due to processing error"
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> Dict:
        """Get conversation history for a user"""
        try:
            conversations = self.firebase_service.get_user_conversations(user_id, limit)
            
            return {
                'success': True,
                'conversations': conversations,
                'total_count': len(conversations)
            }
            
        except Exception as e:
            logging.error(f"Error getting conversation history: {e}")
            return {
                'success': False,
                'error': str(e),
                'conversations': []
            }
