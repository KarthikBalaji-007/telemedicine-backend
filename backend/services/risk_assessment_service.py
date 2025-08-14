"""
Advanced Risk Assessment Service
Comprehensive risk level classification for medical symptoms
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class RiskAssessmentService:
    """Advanced risk assessment and classification service"""
    
    def __init__(self):
        self.emergency_keywords = [
            'chest pain', 'difficulty breathing', 'shortness of breath', 'severe bleeding',
            'unconscious', 'seizure', 'stroke symptoms', 'heart attack', 'severe allergic reaction',
            'poisoning', 'severe burns', 'broken bone', 'head injury', 'severe abdominal pain'
        ]
        
        self.high_risk_keywords = [
            'severe pain', 'high fever', 'persistent vomiting', 'dehydration',
            'severe headache', 'vision problems', 'severe dizziness', 'fainting',
            'blood in stool', 'blood in urine', 'severe rash', 'difficulty swallowing'
        ]
        
        self.moderate_risk_keywords = [
            'moderate pain', 'fever', 'nausea', 'vomiting', 'diarrhea', 'headache',
            'fatigue', 'muscle aches', 'sore throat', 'cough', 'runny nose'
        ]
        
        # Vital signs normal ranges
        self.vital_ranges = {
            'heart_rate': {'normal': (60, 100), 'concerning': (50, 120), 'critical': (40, 150)},
            'systolic_bp': {'normal': (90, 140), 'concerning': (80, 160), 'critical': (70, 180)},
            'diastolic_bp': {'normal': (60, 90), 'concerning': (50, 100), 'critical': (40, 110)},
            'temperature_f': {'normal': (97.0, 99.5), 'concerning': (96.0, 101.0), 'critical': (95.0, 103.0)},
            'respiratory_rate': {'normal': (12, 20), 'concerning': (10, 24), 'critical': (8, 30)},
            'oxygen_saturation': {'normal': (95, 100), 'concerning': (90, 94), 'critical': (0, 89)}
        }
    
    def assess_comprehensive_risk(self, symptoms: List[str], vitals: Dict = None, 
                                user_context: Dict = None, follow_up_data: Dict = None) -> Dict:
        """Comprehensive risk assessment combining all factors"""
        try:
            # Initialize risk assessment
            risk_assessment = {
                'overall_risk_level': 'LOW',
                'risk_score': 0,
                'risk_factors': [],
                'recommendations': [],
                'urgency_level': 'routine',
                'triage_category': 'non_urgent',
                'assessment_components': {}
            }
            
            # 1. Symptom-based risk assessment
            symptom_risk = self._assess_symptom_risk(symptoms)
            risk_assessment['risk_score'] += symptom_risk['score']
            risk_assessment['risk_factors'].extend(symptom_risk['factors'])
            risk_assessment['assessment_components']['symptoms'] = symptom_risk
            
            # 2. Vital signs assessment (if provided)
            if vitals:
                vital_risk = self._assess_vital_signs_risk(vitals)
                risk_assessment['risk_score'] += vital_risk['score']
                risk_assessment['risk_factors'].extend(vital_risk['factors'])
                risk_assessment['assessment_components']['vitals'] = vital_risk
            
            # 3. User context assessment (age, medical history, etc.)
            if user_context:
                context_risk = self._assess_context_risk(user_context)
                risk_assessment['risk_score'] += context_risk['score']
                risk_assessment['risk_factors'].extend(context_risk['factors'])
                risk_assessment['assessment_components']['context'] = context_risk
            
            # 4. Follow-up data assessment
            if follow_up_data:
                followup_risk = self._assess_followup_risk(follow_up_data)
                risk_assessment['risk_score'] += followup_risk['score']
                risk_assessment['risk_factors'].extend(followup_risk['factors'])
                risk_assessment['assessment_components']['follow_up'] = followup_risk
            
            # 5. Determine final risk level and recommendations
            final_assessment = self._determine_final_risk_level(risk_assessment['risk_score'])
            risk_assessment.update(final_assessment)
            
            # 6. Generate specific recommendations
            risk_assessment['recommendations'] = self._generate_recommendations(risk_assessment)
            
            # 7. Add timestamp and metadata
            risk_assessment['assessment_timestamp'] = datetime.utcnow().isoformat()
            risk_assessment['assessment_version'] = '2.0'
            
            return risk_assessment
            
        except Exception as e:
            logging.error(f"Error in comprehensive risk assessment: {e}")
            return {
                'overall_risk_level': 'HIGH',  # Default to high risk on error
                'risk_score': 10,
                'risk_factors': ['Assessment error - defaulting to high risk for safety'],
                'recommendations': ['Seek immediate medical attention due to assessment system error'],
                'urgency_level': 'urgent',
                'error': str(e)
            }
    
    def _assess_symptom_risk(self, symptoms: List[str]) -> Dict:
        """Assess risk based on symptoms"""
        try:
            symptom_text = ' '.join(symptoms).lower()
            risk_score = 0
            risk_factors = []
            
            # Check for emergency symptoms
            for emergency_symptom in self.emergency_keywords:
                if emergency_symptom in symptom_text:
                    risk_score += 8
                    risk_factors.append(f"Emergency symptom detected: {emergency_symptom}")
            
            # Check for high-risk symptoms
            for high_risk_symptom in self.high_risk_keywords:
                if high_risk_symptom in symptom_text:
                    risk_score += 5
                    risk_factors.append(f"High-risk symptom: {high_risk_symptom}")
            
            # Check for moderate-risk symptoms
            for moderate_risk_symptom in self.moderate_risk_keywords:
                if moderate_risk_symptom in symptom_text:
                    risk_score += 2
                    risk_factors.append(f"Moderate-risk symptom: {moderate_risk_symptom}")
            
            # Check for symptom combinations that increase risk
            if 'fever' in symptom_text and 'headache' in symptom_text:
                risk_score += 2
                risk_factors.append("Fever + headache combination increases risk")
            
            if 'chest pain' in symptom_text and 'shortness of breath' in symptom_text:
                risk_score += 6
                risk_factors.append("Chest pain + breathing difficulty - high risk combination")
            
            return {
                'score': min(risk_score, 10),  # Cap at 10
                'factors': risk_factors,
                'symptom_count': len(symptoms),
                'emergency_symptoms_detected': any(es in symptom_text for es in self.emergency_keywords)
            }
            
        except Exception as e:
            logging.error(f"Error assessing symptom risk: {e}")
            return {'score': 5, 'factors': ['Symptom assessment error'], 'symptom_count': 0}
    
    def _assess_vital_signs_risk(self, vitals: Dict) -> Dict:
        """Assess risk based on vital signs"""
        try:
            risk_score = 0
            risk_factors = []
            abnormal_vitals = []
            
            for vital_name, value in vitals.items():
                if value is None or value == '':
                    continue
                    
                try:
                    vital_value = float(value)
                    
                    if vital_name in self.vital_ranges:
                        ranges = self.vital_ranges[vital_name]
                        
                        # Check critical range
                        if not (ranges['critical'][0] <= vital_value <= ranges['critical'][1]):
                            risk_score += 6
                            risk_factors.append(f"Critical {vital_name}: {vital_value}")
                            abnormal_vitals.append(vital_name)
                        # Check concerning range
                        elif not (ranges['concerning'][0] <= vital_value <= ranges['concerning'][1]):
                            risk_score += 4
                            risk_factors.append(f"Concerning {vital_name}: {vital_value}")
                            abnormal_vitals.append(vital_name)
                        # Check normal range
                        elif not (ranges['normal'][0] <= vital_value <= ranges['normal'][1]):
                            risk_score += 2
                            risk_factors.append(f"Abnormal {vital_name}: {vital_value}")
                            abnormal_vitals.append(vital_name)
                            
                except ValueError:
                    risk_factors.append(f"Invalid {vital_name} value: {value}")
            
            return {
                'score': min(risk_score, 8),  # Cap at 8 for vitals
                'factors': risk_factors,
                'abnormal_vitals': abnormal_vitals,
                'vitals_provided': list(vitals.keys())
            }
            
        except Exception as e:
            logging.error(f"Error assessing vital signs risk: {e}")
            return {'score': 3, 'factors': ['Vital signs assessment error'], 'abnormal_vitals': []}
    
    def _assess_context_risk(self, context: Dict) -> Dict:
        """Assess risk based on user context (age, medical history, etc.)"""
        try:
            risk_score = 0
            risk_factors = []
            
            # Age-based risk
            age = context.get('age')
            if age:
                if age >= 65:
                    risk_score += 2
                    risk_factors.append("Age 65+ increases risk for complications")
                elif age <= 2:
                    risk_score += 3
                    risk_factors.append("Very young age increases risk")
                elif age <= 12:
                    risk_score += 1
                    risk_factors.append("Pediatric patient - increased monitoring needed")
            
            # Medical history risk
            medical_history = context.get('medical_history', [])
            high_risk_conditions = [
                'diabetes', 'heart disease', 'hypertension', 'asthma', 'copd',
                'cancer', 'immunocompromised', 'kidney disease', 'liver disease'
            ]
            
            for condition in medical_history:
                if any(risk_condition in condition.lower() for risk_condition in high_risk_conditions):
                    risk_score += 2
                    risk_factors.append(f"High-risk medical condition: {condition}")
            
            # Pregnancy
            if context.get('pregnant'):
                risk_score += 2
                risk_factors.append("Pregnancy requires special medical consideration")
            
            return {
                'score': min(risk_score, 6),  # Cap at 6 for context
                'factors': risk_factors,
                'age_category': self._get_age_category(age) if age else 'unknown'
            }
            
        except Exception as e:
            logging.error(f"Error assessing context risk: {e}")
            return {'score': 1, 'factors': ['Context assessment error'], 'age_category': 'unknown'}
    
    def _assess_followup_risk(self, follow_up_data: Dict) -> Dict:
        """Assess risk based on follow-up questions"""
        try:
            risk_score = 0
            risk_factors = []
            
            # Pain scale assessment
            pain_scale = follow_up_data.get('pain_scale')
            if pain_scale:
                pain_level = int(pain_scale)
                if pain_level >= 8:
                    risk_score += 3
                    risk_factors.append(f"Severe pain level: {pain_level}/10")
                elif pain_level >= 6:
                    risk_score += 2
                    risk_factors.append(f"Moderate-severe pain: {pain_level}/10")
            
            # Symptom progression
            progression = follow_up_data.get('symptom_progression')
            if progression == 'Getting worse':
                risk_score += 2
                risk_factors.append("Symptoms are worsening")
            elif progression == 'Fluctuating':
                risk_score += 1
                risk_factors.append("Symptoms are fluctuating")
            
            # Breathing difficulty
            if follow_up_data.get('breathing_difficulty') == 'yes':
                risk_score += 4
                risk_factors.append("Patient reports breathing difficulty")
            
            return {
                'score': min(risk_score, 5),  # Cap at 5 for follow-up
                'factors': risk_factors
            }
            
        except Exception as e:
            logging.error(f"Error assessing follow-up risk: {e}")
            return {'score': 1, 'factors': ['Follow-up assessment error']}
    
    def _determine_final_risk_level(self, total_score: int) -> Dict:
        """Determine final risk level based on total score"""
        if total_score >= 15:
            return {
                'overall_risk_level': 'CRITICAL',
                'urgency_level': 'emergency',
                'triage_category': 'immediate',
                'time_to_care': 'Immediate (0-15 minutes)'
            }
        elif total_score >= 10:
            return {
                'overall_risk_level': 'HIGH',
                'urgency_level': 'urgent',
                'triage_category': 'urgent',
                'time_to_care': 'Within 1 hour'
            }
        elif total_score >= 6:
            return {
                'overall_risk_level': 'MODERATE',
                'urgency_level': 'semi_urgent',
                'triage_category': 'semi_urgent',
                'time_to_care': 'Within 2-4 hours'
            }
        elif total_score >= 3:
            return {
                'overall_risk_level': 'LOW_MODERATE',
                'urgency_level': 'less_urgent',
                'triage_category': 'less_urgent',
                'time_to_care': 'Within 24 hours'
            }
        else:
            return {
                'overall_risk_level': 'LOW',
                'urgency_level': 'routine',
                'triage_category': 'non_urgent',
                'time_to_care': 'Routine care (1-7 days)'
            }
    
    def _generate_recommendations(self, risk_assessment: Dict) -> List[str]:
        """Generate specific recommendations based on risk assessment"""
        recommendations = []
        risk_level = risk_assessment['overall_risk_level']
        
        if risk_level == 'CRITICAL':
            recommendations.extend([
                "🚨 SEEK IMMEDIATE EMERGENCY CARE - Call 911 or go to nearest ER",
                "Do not drive yourself - call ambulance or have someone drive you",
                "If symptoms worsen while waiting, call 911 immediately"
            ])
        elif risk_level == 'HIGH':
            recommendations.extend([
                "⚠️ Seek urgent medical attention within 1 hour",
                "Go to urgent care center or emergency room",
                "Do not wait - this requires prompt medical evaluation"
            ])
        elif risk_level == 'MODERATE':
            recommendations.extend([
                "📞 Contact your healthcare provider within 2-4 hours",
                "Monitor symptoms closely for any worsening",
                "Consider urgent care if symptoms worsen"
            ])
        elif risk_level == 'LOW_MODERATE':
            recommendations.extend([
                "📅 Schedule appointment with healthcare provider within 24 hours",
                "Monitor symptoms and seek care if they worsen",
                "Rest, stay hydrated, and follow basic self-care measures"
            ])
        else:  # LOW
            recommendations.extend([
                "🏠 Home care and monitoring appropriate",
                "Schedule routine appointment if symptoms persist",
                "Rest, fluids, and over-the-counter remedies as appropriate"
            ])
        
        return recommendations
    
    def _get_age_category(self, age: int) -> str:
        """Get age category for risk assessment"""
        if age <= 2:
            return 'infant'
        elif age <= 12:
            return 'child'
        elif age <= 17:
            return 'adolescent'
        elif age <= 64:
            return 'adult'
        else:
            return 'senior'
