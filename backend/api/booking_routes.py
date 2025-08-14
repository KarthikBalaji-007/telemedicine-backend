"""
Doctor booking API routes for AI Telemedicine Platform
Handles appointment booking and management functionality
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timedelta
import logging

from services.firebase_service import FirebaseService
from services.validation_service import ValidationService
from utils.decorators import validate_json, handle_errors
from utils.helpers import generate_response
from models.booking import Booking

# Create blueprint
booking_bp = Blueprint('booking', __name__)

# Initialize services
firebase_service = FirebaseService()
validation_service = ValidationService()

@booking_bp.route('/book-doctor', methods=['POST'])
@handle_errors
@validate_json
def book_doctor_appointment():
    """
    Book a doctor appointment
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    
    Expected JSON payload:
    {
        "user_id": "string",
        "doctor_id": "string",
        "appointment_datetime": "ISO datetime string",
        "duration_minutes": number (optional, default: 30),
        "appointment_type": "consultation|follow_up|emergency",
        "consultation_mode": "video|phone|in_person",
        "reason_for_visit": "string",
        "symptoms_summary": ["symptom1", "symptom2"] (optional),
        "urgency_level": "low|medium|high|emergency" (optional),
        "related_interaction_id": "string" (optional),
        "insurance_info": {} (optional),
        "patient_notes": "string" (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'doctor_id', 'appointment_datetime', 'appointment_type', 
                          'consultation_mode', 'reason_for_visit']
        validation_result = validation_service.validate_required_fields(data, required_fields)
        
        if not validation_result['valid']:
            return generate_response(
                success=False,
                message=validation_result['message'],
                status_code=400
            )
        
        # Validate appointment datetime
        try:
            appointment_dt = datetime.fromisoformat(data['appointment_datetime'].replace('Z', '+00:00'))
            if appointment_dt <= datetime.now():
                return generate_response(
                    success=False,
                    message="Appointment must be scheduled for a future date and time",
                    status_code=400
                )
        except ValueError:
            return generate_response(
                success=False,
                message="Invalid appointment datetime format. Use ISO format.",
                status_code=400
            )
        
        # Validate appointment type
        if data['appointment_type'] not in ['consultation', 'follow_up', 'emergency']:
            return generate_response(
                success=False,
                message="Invalid appointment type",
                status_code=400
            )
        
        # Validate consultation mode
        if data['consultation_mode'] not in ['video', 'phone', 'in_person']:
            return generate_response(
                success=False,
                message="Invalid consultation mode",
                status_code=400
            )
        
        # Validate duration
        duration_minutes = data.get('duration_minutes', 30)
        if duration_minutes < 15 or duration_minutes > 120:
            return generate_response(
                success=False,
                message="Duration must be between 15 and 120 minutes",
                status_code=400
            )
        
        # Validate reason for visit
        if len(data['reason_for_visit'].strip()) < 10:
            return generate_response(
                success=False,
                message="Reason for visit must be at least 10 characters",
                status_code=400
            )
        
        # TODO: COORDINATE WITH TEAM - Add doctor availability check
        # Check if doctor is available at the requested time
        # This would require a doctor schedule service
        
        # TODO: COORDINATE WITH TEAM - Add conflict checking
        # Check for existing appointments at the same time
        
        # Get doctor information (mock data for backend testing)
        # TODO: COORDINATE WITH TEAM - Implement actual doctor service
        doctor_info = get_doctor_info(data['doctor_id'])
        if not doctor_info:
            # For backend development, create mock doctor info for any doctor_id
            doctor_info = {
                'doctor_id': data['doctor_id'],
                'name': f'Dr. Mock Doctor ({data["doctor_id"]})',
                'specialty': 'General Practice',
                'rating': 4.5,
                'experience_years': 10,
                'consultation_fee': 150,
                'available_modes': ['video', 'phone', 'in_person']
            }
        
        # Create booking
        booking_data = {
            'user_id': data['user_id'],
            'doctor_id': data['doctor_id'],
            'appointment_datetime': data['appointment_datetime'],
            'duration_minutes': duration_minutes,
            'appointment_type': data['appointment_type'],
            'consultation_mode': data['consultation_mode'],
            'reason_for_visit': data['reason_for_visit'],
            'symptoms_summary': data.get('symptoms_summary', []),
            'urgency_level': data.get('urgency_level', 'medium'),
            'related_interaction_id': data.get('related_interaction_id'),
            'doctor_info': doctor_info,
            'insurance_info': data.get('insurance_info', {}),
            'patient_notes': data.get('patient_notes', ''),
            'status': 'pending'
        }
        
        booking = Booking.from_dict(booking_data)
        validation_result = booking.validate()
        
        if not validation_result['valid']:
            return generate_response(
                success=False,
                message=f"Invalid booking data: {', '.join(validation_result['errors'])}",
                status_code=400
            )
        
        # Save booking to Firebase
        saved_booking = firebase_service.save_booking(booking.to_dict())
        
        # TODO: COORDINATE WITH TEAM - Add notification service
        # Send confirmation email/SMS to user
        # Notify doctor of new appointment request
        
        # Generate meeting link for video consultations
        if data['consultation_mode'] == 'video':
            # TODO: COORDINATE WITH TEAM - Integrate with video conferencing service
            meeting_link = generate_meeting_link(booking.booking_id)
            booking.set_meeting_details(meeting_link)
            firebase_service.save_booking(booking.to_dict())
        
        # Prepare response
        response_data = {
            'booking_id': booking.booking_id,
            'appointment_datetime': booking.appointment_datetime,
            'appointment_end_time': booking.get_appointment_end_time(),
            'doctor_info': booking.doctor_info,
            'appointment_type': booking.appointment_type,
            'consultation_mode': booking.consultation_mode,
            'status': booking.status,
            'meeting_link': booking.meeting_link if booking.consultation_mode == 'video' else None,
            'estimated_cost': booking.estimated_cost
        }
        
        current_app.logger.info(f"Appointment booked: {booking.booking_id} for user {data['user_id']}")
        
        return generate_response(
            success=True,
            data=response_data,
            message="Appointment booked successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error booking appointment: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to book appointment",
            status_code=500
        )

@booking_bp.route('/bookings/<booking_id>', methods=['GET'])
@handle_errors
def get_booking_details(booking_id):
    """
    Get booking details by ID
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    """
    try:
        booking_data = firebase_service.get_booking(booking_id)
        
        if not booking_data:
            return generate_response(
                success=False,
                message="Booking not found",
                status_code=404
            )
        
        # Prepare response data
        response_data = {
            'booking_id': booking_data['booking_id'],
            'appointment_datetime': booking_data['appointment_datetime'],
            'duration_minutes': booking_data['duration_minutes'],
            'appointment_type': booking_data['appointment_type'],
            'consultation_mode': booking_data['consultation_mode'],
            'reason_for_visit': booking_data['reason_for_visit'],
            'status': booking_data['status'],
            'doctor_info': booking_data.get('doctor_info', {}),
            'meeting_link': booking_data.get('meeting_link'),
            'patient_notes': booking_data.get('patient_notes', ''),
            'doctor_notes': booking_data.get('doctor_notes', ''),
            'created_at': booking_data['created_at'],
            'updated_at': booking_data['updated_at']
        }
        
        return generate_response(
            success=True,
            data=response_data,
            message="Booking details retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving booking details: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to retrieve booking details",
            status_code=500
        )

@booking_bp.route('/bookings/<booking_id>/cancel', methods=['POST'])
@handle_errors
def cancel_booking(booking_id):
    """
    Cancel a booking
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    """
    try:
        # Get booking
        booking_data = firebase_service.get_booking(booking_id)
        
        if not booking_data:
            return generate_response(
                success=False,
                message="Booking not found",
                status_code=404
            )
        
        # Check if booking can be cancelled
        if booking_data['status'] in ['cancelled', 'completed']:
            return generate_response(
                success=False,
                message=f"Cannot cancel booking with status: {booking_data['status']}",
                status_code=400
            )
        
        # Check cancellation policy (24 hours notice)
        appointment_dt = datetime.fromisoformat(booking_data['appointment_datetime'].replace('Z', '+00:00'))
        if appointment_dt - datetime.now() < timedelta(hours=24):
            return generate_response(
                success=False,
                message="Appointments must be cancelled at least 24 hours in advance",
                status_code=400
            )
        
        # Update booking status
        firebase_service.update_booking_status(booking_id, 'cancelled', 'Cancelled by patient')
        
        # TODO: COORDINATE WITH TEAM - Add notification service
        # Notify doctor of cancellation
        # Send cancellation confirmation to patient
        
        current_app.logger.info(f"Booking cancelled: {booking_id}")
        
        return generate_response(
            success=True,
            message="Booking cancelled successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error cancelling booking: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to cancel booking",
            status_code=500
        )

@booking_bp.route('/users/<user_id>/bookings', methods=['GET'])
@handle_errors
def get_user_bookings(user_id):
    """
    Get all bookings for a user
    TODO: NOTIFY FRONTEND TEAM - This endpoint ready for integration
    """
    try:
        status_filter = request.args.get('status')
        bookings = firebase_service.get_user_bookings(user_id, status_filter)
        
        # Format bookings for response
        formatted_bookings = []
        for booking in bookings:
            formatted_booking = {
                'booking_id': booking['booking_id'],
                'appointment_datetime': booking['appointment_datetime'],
                'doctor_info': booking.get('doctor_info', {}),
                'appointment_type': booking['appointment_type'],
                'consultation_mode': booking['consultation_mode'],
                'status': booking['status'],
                'urgency_level': booking.get('urgency_level', 'medium')
            }
            formatted_bookings.append(formatted_booking)
        
        return generate_response(
            success=True,
            data={'bookings': formatted_bookings},
            message="User bookings retrieved successfully"
        )
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving user bookings: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to retrieve user bookings",
            status_code=500
        )

def get_doctor_info(doctor_id):
    """
    Get doctor information (mock implementation)
    TODO: COORDINATE WITH TEAM - Implement actual doctor service
    """
    # Mock doctor data
    mock_doctors = {
        'doc_001': {
            'doctor_id': 'doc_001',
            'name': 'Dr. Sarah Johnson',
            'specialty': 'Family Medicine',
            'rating': 4.8,
            'experience_years': 12,
            'consultation_fee': 150,
            'available_modes': ['video', 'phone', 'in_person']
        },
        'doc_002': {
            'doctor_id': 'doc_002',
            'name': 'Dr. Michael Chen',
            'specialty': 'Internal Medicine',
            'rating': 4.9,
            'experience_years': 15,
            'consultation_fee': 175,
            'available_modes': ['video', 'phone']
        }
    }
    
    return mock_doctors.get(doctor_id)

def generate_meeting_link(booking_id):
    """
    Generate video meeting link (mock implementation)
    TODO: COORDINATE WITH TEAM - Integrate with actual video service (Zoom, Teams, etc.)
    """
    return f"https://telemedicine-platform.com/meeting/{booking_id}"
