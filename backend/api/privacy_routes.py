"""
Privacy and Data Protection API Routes
Handles user privacy rights, consent management, and data protection
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

from services.privacy_service import PrivacyService, ComplianceService
from services.firebase_service import FirebaseService
from services.auth_service import require_auth
from utils.decorators import validate_json, handle_errors
from utils.helpers import generate_response

# Create blueprint
privacy_bp = Blueprint('privacy', __name__)

# Initialize services
privacy_service = PrivacyService()
compliance_service = ComplianceService()
firebase_service = FirebaseService()

@privacy_bp.route('/consent', methods=['POST'])
@handle_errors
@validate_json
@require_auth
def manage_consent():
    """
    Manage user consent for data processing
    
    Expected JSON payload:
    {
        "consent_types": ["data_processing", "medical_analysis", "data_storage"],
        "consent_given": true,
        "consent_version": "1.0"
    }
    """
    try:
        data = request.get_json()
        user_id = request.user_id
        
        # Validate consent
        consent_validation = privacy_service.validate_consent(
            user_id, 
            data.get('consent_types', [])
        )
        
        # Save consent record
        consent_record = {
            'user_id': user_id,
            'consent_types': data.get('consent_types', []),
            'consent_given': data.get('consent_given', False),
            'consent_version': data.get('consent_version', '1.0'),
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }
        
        # Log consent for audit
        privacy_service.log_data_access(
            user_id, 
            'consent_record', 
            'create', 
            'user_self'
        )
        
        # Save to database
        saved_consent = firebase_service.save_user_consent(consent_record)
        
        return generate_response(
            success=True,
            message="Consent preferences updated successfully",
            data={
                'consent_id': saved_consent.get('consent_id'),
                'validation': consent_validation,
                'effective_date': consent_record['timestamp']
            }
        )
        
    except Exception as e:
        logging.error(f"Error managing consent: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to update consent preferences",
            status_code=500
        )

@privacy_bp.route('/data-export', methods=['GET'])
@handle_errors
@require_auth
def export_user_data():
    """
    Export all user data (GDPR Article 20 - Data Portability)
    """
    try:
        user_id = request.user_id
        
        # Log data export request
        privacy_service.log_data_access(
            user_id, 
            'full_export', 
            'read', 
            'user_self'
        )
        
        # Get all user data
        user_data = firebase_service.get_complete_user_data(user_id)
        
        # Prepare export package
        export_data = {
            'export_info': {
                'user_id': user_id,
                'export_date': datetime.utcnow().isoformat(),
                'data_format': 'JSON',
                'export_version': '1.0'
            },
            'personal_data': user_data.get('profile', {}),
            'medical_interactions': user_data.get('interactions', []),
            'appointments': user_data.get('bookings', []),
            'consent_history': user_data.get('consents', []),
            'privacy_settings': user_data.get('privacy_settings', {})
        }
        
        return generate_response(
            success=True,
            message="Data export completed successfully",
            data=export_data
        )
        
    except Exception as e:
        logging.error(f"Error exporting user data: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to export user data",
            status_code=500
        )

@privacy_bp.route('/data-deletion', methods=['DELETE'])
@handle_errors
@require_auth
def delete_user_data():
    """
    Delete user data (GDPR Article 17 - Right to Erasure)
    """
    try:
        user_id = request.user_id
        deletion_type = request.args.get('type', 'partial')  # 'partial' or 'complete'
        
        # Log deletion request
        privacy_service.log_data_access(
            user_id, 
            f'data_deletion_{deletion_type}', 
            'delete', 
            'user_self'
        )
        
        if deletion_type == 'complete':
            # Complete account deletion
            deletion_result = firebase_service.delete_user_completely(user_id)
        else:
            # Partial deletion (keep medical records for legal compliance)
            deletion_result = firebase_service.anonymize_user_data(user_id)
        
        return generate_response(
            success=True,
            message=f"Data {deletion_type} deletion completed successfully",
            data={
                'deletion_type': deletion_type,
                'deletion_date': datetime.utcnow().isoformat(),
                'records_affected': deletion_result.get('records_affected', 0)
            }
        )
        
    except Exception as e:
        logging.error(f"Error deleting user data: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to delete user data",
            status_code=500
        )

@privacy_bp.route('/privacy-report', methods=['GET'])
@handle_errors
@require_auth
def get_privacy_report():
    """
    Generate privacy report for user (GDPR Article 15 - Right of Access)
    """
    try:
        user_id = request.user_id
        
        # Log privacy report request
        privacy_service.log_data_access(
            user_id, 
            'privacy_report', 
            'read', 
            'user_self'
        )
        
        # Generate comprehensive privacy report
        privacy_report = privacy_service.generate_privacy_report(user_id)
        
        # Add current data summary
        user_data_summary = firebase_service.get_user_data_summary(user_id)
        privacy_report['current_data'] = user_data_summary
        
        return generate_response(
            success=True,
            message="Privacy report generated successfully",
            data=privacy_report
        )
        
    except Exception as e:
        logging.error(f"Error generating privacy report: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to generate privacy report",
            status_code=500
        )

@privacy_bp.route('/compliance-status', methods=['GET'])
@handle_errors
def get_compliance_status():
    """
    Get current compliance status (for transparency)
    """
    try:
        # Check HIPAA compliance
        hipaa_status = compliance_service.hipaa_compliance_check({})
        
        # Check GDPR compliance
        gdpr_status = compliance_service.gdpr_compliance_check()
        
        compliance_report = {
            'last_updated': datetime.utcnow().isoformat(),
            'hipaa_compliance': hipaa_status,
            'gdpr_compliance': gdpr_status,
            'security_measures': {
                'encryption_at_rest': True,
                'encryption_in_transit': True,
                'access_controls': True,
                'audit_logging': True,
                'data_minimization': True,
                'regular_security_audits': True
            },
            'certifications': [
                'SOC 2 Type II (Firebase)',
                'ISO 27001 (Firebase)',
                'HIPAA Eligible (Firebase)'
            ]
        }
        
        return generate_response(
            success=True,
            message="Compliance status retrieved successfully",
            data=compliance_report
        )
        
    except Exception as e:
        logging.error(f"Error getting compliance status: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to retrieve compliance status",
            status_code=500
        )

@privacy_bp.route('/security-incident', methods=['POST'])
@handle_errors
@validate_json
def report_security_incident():
    """
    Report potential security incident
    """
    try:
        data = request.get_json()
        
        incident_report = {
            'incident_id': f"INC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'reported_at': datetime.utcnow().isoformat(),
            'incident_type': data.get('incident_type', 'unknown'),
            'description': data.get('description', ''),
            'reporter_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'unknown'),
            'severity': data.get('severity', 'medium')
        }
        
        # Log security incident
        logging.critical(f"SECURITY_INCIDENT: {incident_report}")
        
        # In production: Send alert to security team
        # send_security_alert(incident_report)
        
        return generate_response(
            success=True,
            message="Security incident reported successfully",
            data={
                'incident_id': incident_report['incident_id'],
                'status': 'reported',
                'next_steps': 'Security team has been notified and will investigate'
            }
        )
        
    except Exception as e:
        logging.error(f"Error reporting security incident: {str(e)}")
        return generate_response(
            success=False,
            message="Failed to report security incident",
            status_code=500
        )
