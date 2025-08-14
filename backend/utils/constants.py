"""
Constants for AI Telemedicine Platform
Application-wide constants and configuration values
"""

# API Response Messages
class Messages:
    """Standard API response messages"""
    
    # Success messages
    SUCCESS_GENERAL = "Operation completed successfully"
    SUCCESS_CREATED = "Resource created successfully"
    SUCCESS_UPDATED = "Resource updated successfully"
    SUCCESS_DELETED = "Resource deleted successfully"
    SUCCESS_RETRIEVED = "Resource retrieved successfully"
    
    # Error messages
    ERROR_GENERAL = "An error occurred while processing your request"
    ERROR_NOT_FOUND = "Resource not found"
    ERROR_INVALID_INPUT = "Invalid input provided"
    ERROR_UNAUTHORIZED = "Unauthorized access"
    ERROR_FORBIDDEN = "Access forbidden"
    ERROR_CONFLICT = "Resource conflict"
    ERROR_VALIDATION = "Validation failed"
    ERROR_SERVICE_UNAVAILABLE = "Service temporarily unavailable"
    ERROR_TIMEOUT = "Request timeout"
    
    # Specific messages
    USER_NOT_FOUND = "User not found"
    USER_CREATED = "User profile created successfully"
    USER_UPDATED = "User profile updated successfully"
    
    INTERACTION_SAVED = "Interaction saved successfully"
    INTERACTION_NOT_FOUND = "Interaction not found"
    
    BOOKING_CREATED = "Appointment booked successfully"
    BOOKING_CANCELLED = "Appointment cancelled successfully"
    BOOKING_NOT_FOUND = "Booking not found"
    
    AI_SERVICE_ERROR = "AI service temporarily unavailable"
    AI_PROCESSING_ERROR = "Error processing AI request"

# HTTP Status Codes
class StatusCodes:
    """HTTP status codes"""
    
    # Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # Client errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    
    # Server errors
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504

# Validation Constants
class Validation:
    """Validation rules and limits"""
    
    # String lengths
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_NOTES_LENGTH = 2000
    
    # List limits
    MAX_SYMPTOMS_PER_REQUEST = 10
    MAX_HISTORY_ITEMS = 50
    MAX_RECOMMENDATIONS = 20
    
    # Numeric ranges
    MIN_SEVERITY_LEVEL = 1
    MAX_SEVERITY_LEVEL = 10
    MIN_APPOINTMENT_DURATION = 15  # minutes
    MAX_APPOINTMENT_DURATION = 120  # minutes
    
    # File upload
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
    ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'txt']

# Medical Constants
class Medical:
    """Medical-related constants"""
    
    # Urgency levels
    URGENCY_LOW = "low"
    URGENCY_MEDIUM = "medium"
    URGENCY_HIGH = "high"
    URGENCY_EMERGENCY = "emergency"
    
    URGENCY_LEVELS = [URGENCY_LOW, URGENCY_MEDIUM, URGENCY_HIGH, URGENCY_EMERGENCY]
    
    # Severity levels
    SEVERITY_MILD = "mild"
    SEVERITY_MODERATE = "moderate"
    SEVERITY_SEVERE = "severe"
    
    SEVERITY_LEVELS = [SEVERITY_MILD, SEVERITY_MODERATE, SEVERITY_SEVERE]
    
    # Appointment types
    APPOINTMENT_CONSULTATION = "consultation"
    APPOINTMENT_FOLLOW_UP = "follow_up"
    APPOINTMENT_EMERGENCY = "emergency"
    
    APPOINTMENT_TYPES = [APPOINTMENT_CONSULTATION, APPOINTMENT_FOLLOW_UP, APPOINTMENT_EMERGENCY]
    
    # Consultation modes
    CONSULTATION_VIDEO = "video"
    CONSULTATION_PHONE = "phone"
    CONSULTATION_IN_PERSON = "in_person"
    
    CONSULTATION_MODES = [CONSULTATION_VIDEO, CONSULTATION_PHONE, CONSULTATION_IN_PERSON]
    
    # Interaction types
    INTERACTION_SYMPTOM_CHECK = "symptom_check"
    INTERACTION_MENTAL_HEALTH = "mental_health"
    INTERACTION_GENERAL = "general"
    
    INTERACTION_TYPES = [INTERACTION_SYMPTOM_CHECK, INTERACTION_MENTAL_HEALTH, INTERACTION_GENERAL]
    
    # Mental health risk levels
    RISK_LOW = "low"
    RISK_MODERATE = "moderate"
    RISK_HIGH = "high"
    RISK_CRISIS = "crisis"
    
    RISK_LEVELS = [RISK_LOW, RISK_MODERATE, RISK_HIGH, RISK_CRISIS]

# Booking Constants
class Booking:
    """Booking-related constants"""
    
    # Booking statuses
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_COMPLETED = "completed"
    STATUS_NO_SHOW = "no_show"
    
    BOOKING_STATUSES = [STATUS_PENDING, STATUS_CONFIRMED, STATUS_CANCELLED, STATUS_COMPLETED, STATUS_NO_SHOW]
    
    # Payment statuses
    PAYMENT_PENDING = "pending"
    PAYMENT_PAID = "paid"
    PAYMENT_FAILED = "failed"
    PAYMENT_REFUNDED = "refunded"
    
    PAYMENT_STATUSES = [PAYMENT_PENDING, PAYMENT_PAID, PAYMENT_FAILED, PAYMENT_REFUNDED]
    
    # Cancellation policy
    MIN_CANCELLATION_HOURS = 24

# AI Service Constants
class AIService:
    """AI service related constants"""
    
    # Model configurations
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 1000
    DEFAULT_TIMEOUT = 30
    
    # Confidence thresholds
    MIN_CONFIDENCE_THRESHOLD = 0.6
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    
    # Assessment types
    ASSESSMENT_SCREENING = "screening"
    ASSESSMENT_DETAILED = "detailed"
    ASSESSMENT_FOLLOW_UP = "follow_up"
    
    ASSESSMENT_TYPES = [ASSESSMENT_SCREENING, ASSESSMENT_DETAILED, ASSESSMENT_FOLLOW_UP]

# Time Constants
class Time:
    """Time-related constants"""
    
    # Cache timeouts (seconds)
    CACHE_SHORT = 300  # 5 minutes
    CACHE_MEDIUM = 1800  # 30 minutes
    CACHE_LONG = 3600  # 1 hour
    CACHE_VERY_LONG = 86400  # 24 hours
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 60
    RATE_LIMIT_WINDOW = 60  # seconds
    
    # Business hours
    BUSINESS_START_HOUR = 9
    BUSINESS_END_HOUR = 17
    
    # Timezone
    DEFAULT_TIMEZONE = "UTC"

# Crisis Resources
class CrisisResources:
    """Crisis intervention resources"""
    
    SUICIDE_PREVENTION_LIFELINE = {
        'name': 'National Suicide Prevention Lifeline',
        'number': '988',
        'description': '24/7 crisis support and suicide prevention',
        'website': 'https://suicidepreventionlifeline.org'
    }
    
    CRISIS_TEXT_LINE = {
        'name': 'Crisis Text Line',
        'number': 'Text HOME to 741741',
        'description': '24/7 crisis support via text',
        'website': 'https://www.crisistextline.org'
    }
    
    EMERGENCY_SERVICES = {
        'name': 'Emergency Services',
        'number': '911',
        'description': 'Emergency medical, fire, and police services'
    }
    
    SAMHSA_HELPLINE = {
        'name': 'SAMHSA National Helpline',
        'number': '1-800-662-4357',
        'description': 'Substance abuse and mental health services',
        'website': 'https://www.samhsa.gov'
    }

# Common Symptoms List
class CommonSymptoms:
    """Common symptoms for autocomplete and validation"""
    
    PHYSICAL_SYMPTOMS = [
        "Fever", "Headache", "Cough", "Sore throat", "Runny nose",
        "Fatigue", "Body aches", "Nausea", "Vomiting", "Diarrhea",
        "Shortness of breath", "Chest pain", "Dizziness", "Rash",
        "Abdominal pain", "Back pain", "Joint pain", "Muscle pain",
        "Loss of appetite", "Difficulty sleeping", "Chills", "Sweating"
    ]
    
    MENTAL_HEALTH_SYMPTOMS = [
        "Anxiety", "Depression", "Mood swings", "Irritability",
        "Confusion", "Memory problems", "Concentration difficulties",
        "Panic attacks", "Social withdrawal", "Hopelessness",
        "Restlessness", "Guilt", "Worthlessness", "Suicidal thoughts"
    ]
    
    NEUROLOGICAL_SYMPTOMS = [
        "Vision problems", "Hearing problems", "Balance problems",
        "Numbness", "Tingling", "Weakness", "Tremors", "Seizures",
        "Speech difficulties", "Coordination problems"
    ]
    
    ALL_SYMPTOMS = PHYSICAL_SYMPTOMS + MENTAL_HEALTH_SYMPTOMS + NEUROLOGICAL_SYMPTOMS

# Environment Constants
class Environment:
    """Environment-related constants"""
    
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    
    ENVIRONMENTS = [DEVELOPMENT, TESTING, STAGING, PRODUCTION]
