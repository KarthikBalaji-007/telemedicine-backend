"""
Booking data model for AI Telemedicine Platform
Defines structure for doctor appointment bookings
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class Booking:
    """Doctor appointment booking model"""
    
    def __init__(self, booking_id: str = None, **kwargs):
        self.booking_id = booking_id or str(uuid.uuid4())
        self.user_id = kwargs.get('user_id', '')
        self.doctor_id = kwargs.get('doctor_id', '')
        self.appointment_datetime = kwargs.get('appointment_datetime')
        self.duration_minutes = kwargs.get('duration_minutes', 30)
        
        # Booking details
        self.appointment_type = kwargs.get('appointment_type', 'consultation')  # 'consultation', 'follow_up', 'emergency'
        self.consultation_mode = kwargs.get('consultation_mode', 'video')  # 'video', 'phone', 'in_person'
        self.reason_for_visit = kwargs.get('reason_for_visit', '')
        self.symptoms_summary = kwargs.get('symptoms_summary', [])
        self.urgency_level = kwargs.get('urgency_level', 'medium')
        
        # Related interaction
        self.related_interaction_id = kwargs.get('related_interaction_id')  # Link to symptom check
        
        # Status tracking
        self.status = kwargs.get('status', 'pending')  # 'pending', 'confirmed', 'cancelled', 'completed', 'no_show'
        self.created_at = kwargs.get('created_at', datetime.utcnow().isoformat())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow().isoformat())
        
        # Doctor information (cached for quick access)
        self.doctor_info = kwargs.get('doctor_info', {})
        
        # Payment and insurance
        self.payment_status = kwargs.get('payment_status', 'pending')  # 'pending', 'paid', 'failed', 'refunded'
        self.payment_method = kwargs.get('payment_method')
        self.insurance_info = kwargs.get('insurance_info', {})
        self.estimated_cost = kwargs.get('estimated_cost')
        
        # Communication
        self.meeting_link = kwargs.get('meeting_link')  # For video consultations
        self.meeting_id = kwargs.get('meeting_id')
        self.meeting_password = kwargs.get('meeting_password')
        
        # Notifications
        self.reminder_sent = kwargs.get('reminder_sent', False)
        self.confirmation_sent = kwargs.get('confirmation_sent', False)
        
        # Notes and follow-up
        self.patient_notes = kwargs.get('patient_notes', '')
        self.doctor_notes = kwargs.get('doctor_notes', '')
        self.prescription = kwargs.get('prescription', [])
        self.follow_up_required = kwargs.get('follow_up_required', False)
        self.follow_up_date = kwargs.get('follow_up_date')
    
    def to_dict(self) -> Dict:
        """Convert booking object to dictionary for Firebase storage"""
        return {
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'doctor_id': self.doctor_id,
            'appointment_datetime': self.appointment_datetime,
            'duration_minutes': self.duration_minutes,
            'appointment_type': self.appointment_type,
            'consultation_mode': self.consultation_mode,
            'reason_for_visit': self.reason_for_visit,
            'symptoms_summary': self.symptoms_summary,
            'urgency_level': self.urgency_level,
            'related_interaction_id': self.related_interaction_id,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'doctor_info': self.doctor_info,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'insurance_info': self.insurance_info,
            'estimated_cost': self.estimated_cost,
            'meeting_link': self.meeting_link,
            'meeting_id': self.meeting_id,
            'meeting_password': self.meeting_password,
            'reminder_sent': self.reminder_sent,
            'confirmation_sent': self.confirmation_sent,
            'patient_notes': self.patient_notes,
            'doctor_notes': self.doctor_notes,
            'prescription': self.prescription,
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Booking':
        """Create Booking object from dictionary"""
        return cls(**data)
    
    def update_status(self, status: str, notes: str = None):
        """Update booking status"""
        self.status = status
        self.updated_at = datetime.utcnow().isoformat()
        
        if notes:
            self.doctor_notes = notes
    
    def set_meeting_details(self, meeting_link: str, meeting_id: str = None, password: str = None):
        """Set video meeting details"""
        self.meeting_link = meeting_link
        self.meeting_id = meeting_id
        self.meeting_password = password
    
    def validate(self) -> Dict[str, any]:
        """Validate booking data"""
        errors = []
        
        if not self.user_id:
            errors.append("User ID is required")
        
        if not self.doctor_id:
            errors.append("Doctor ID is required")
        
        if not self.appointment_datetime:
            errors.append("Appointment date and time is required")
        else:
            try:
                appointment_dt = datetime.fromisoformat(self.appointment_datetime.replace('Z', '+00:00'))
                if appointment_dt <= datetime.now():
                    errors.append("Appointment must be scheduled for a future date and time")
            except ValueError:
                errors.append("Invalid appointment date and time format")
        
        if self.duration_minutes < 15 or self.duration_minutes > 120:
            errors.append("Appointment duration must be between 15 and 120 minutes")
        
        if self.appointment_type not in ['consultation', 'follow_up', 'emergency']:
            errors.append("Invalid appointment type")
        
        if self.consultation_mode not in ['video', 'phone', 'in_person']:
            errors.append("Invalid consultation mode")
        
        if not self.reason_for_visit or len(self.reason_for_visit.strip()) < 10:
            errors.append("Reason for visit must be at least 10 characters")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_appointment_end_time(self) -> Optional[str]:
        """Calculate appointment end time"""
        if not self.appointment_datetime:
            return None
        
        try:
            start_time = datetime.fromisoformat(self.appointment_datetime.replace('Z', '+00:00'))
            end_time = start_time + timedelta(minutes=self.duration_minutes)
            return end_time.isoformat()
        except ValueError:
            return None
    
    def is_upcoming(self) -> bool:
        """Check if appointment is upcoming"""
        if not self.appointment_datetime:
            return False
        
        try:
            appointment_dt = datetime.fromisoformat(self.appointment_datetime.replace('Z', '+00:00'))
            return appointment_dt > datetime.now() and self.status in ['pending', 'confirmed']
        except ValueError:
            return False
    
    def get_summary(self) -> Dict:
        """Get booking summary for display"""
        return {
            'booking_id': self.booking_id,
            'appointment_datetime': self.appointment_datetime,
            'doctor_info': self.doctor_info,
            'appointment_type': self.appointment_type,
            'consultation_mode': self.consultation_mode,
            'status': self.status,
            'urgency_level': self.urgency_level,
            'duration_minutes': self.duration_minutes
        }
