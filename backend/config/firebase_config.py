"""
Firebase configuration and initialization
Handles Firestore database connection and service setup
"""

import firebase_admin
from firebase_admin import credentials, firestore
import logging
from config.settings import Config

# Global Firebase app instance
_firebase_app = None
_firestore_client = None

def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials"""
    global _firebase_app, _firestore_client

    try:
        # Check if Firebase is already initialized
        if _firebase_app is not None:
            return _firestore_client

        # Check if we have valid Firebase credentials
        if not _has_valid_firebase_config():
            logging.info("🔧 Backend running in DEVELOPMENT MODE - using mock database")
            logging.info("📋 To use real Firebase: Set up credentials in .env file")
            logging.info("💰 Firebase is FREE for development (50k reads/20k writes per day)")
            return None

        # Validate configuration
        Config.validate_config()

        # Get credentials
        cred_dict = Config.get_firebase_credentials()
        cred = credentials.Certificate(cred_dict)

        # Initialize Firebase app
        _firebase_app = firebase_admin.initialize_app(cred)

        # Initialize Firestore client
        _firestore_client = firestore.client()

        logging.info("Firebase initialized successfully")
        return _firestore_client

    except Exception as e:
        logging.error(f"Failed to initialize Firebase: {str(e)}")
        logging.warning("Running in development mode without Firebase")
        return None

def _has_valid_firebase_config():
    """Check if we have valid Firebase configuration"""
    try:
        # Check for placeholder values
        if (Config.FIREBASE_PROJECT_ID == "your-project-id" or
            Config.FIREBASE_CLIENT_EMAIL == "test@test.com" or
            Config.FIREBASE_PRIVATE_KEY == "test-key" or
            not Config.FIREBASE_PROJECT_ID or
            not Config.FIREBASE_CLIENT_EMAIL or
            not Config.FIREBASE_PRIVATE_KEY):
            return False
        return True
    except:
        return False

def get_firestore_client():
    """Get Firestore client instance"""
    global _firestore_client
    
    if _firestore_client is None:
        _firestore_client = initialize_firebase()
    
    return _firestore_client

def test_firebase_connection():
    """Test Firebase connection by attempting to read from a test collection"""
    try:
        db = get_firestore_client()
        
        # Try to access a test collection
        test_ref = db.collection('health_check').document('test')
        test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP, 'status': 'connected'})
        
        # Read it back
        doc = test_ref.get()
        if doc.exists:
            logging.info("Firebase connection test successful")
            return True
        else:
            logging.error("Firebase connection test failed - document not found")
            return False
            
    except Exception as e:
        logging.error(f"Firebase connection test failed: {str(e)}")
        return False

# Collection names - centralized for consistency
class Collections:
    """Firebase collection names"""
    USERS = 'users'
    INTERACTIONS = 'interactions'
    BOOKINGS = 'bookings'
    SYMPTOMS = 'symptoms'
    MENTAL_HEALTH = 'mental_health_assessments'
    DOCTORS = 'doctors'
    APPOINTMENTS = 'appointments'
    
    # System collections
    HEALTH_CHECK = 'health_check'
    LOGS = 'system_logs'
