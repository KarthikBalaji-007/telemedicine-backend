"""
Firebase service for AI Telemedicine Platform
Handles all Firestore database operations
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from firebase_admin import firestore

from config.firebase_config import get_firestore_client, Collections
from models.user import User
from models.interaction import Interaction
from models.booking import Booking

class FirebaseService:
    """Service class for Firebase Firestore operations"""
    
    def __init__(self):
        self.db = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Firestore client"""
        try:
            self.db = get_firestore_client()
            if self.db is None:
                logging.info("🔧 Firebase service: DEVELOPMENT MODE (mock database)")
                logging.info("📊 Data operations will use mock responses for testing")
            else:
                logging.info("Firebase service initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Firebase service: {str(e)}")
            logging.warning("Firebase service running in development mode - data will not be persisted")
            self.db = None
    
    # User operations
    def save_user_profile(self, user_data: Dict) -> Dict:
        """Save or update user profile"""
        try:
            user = User.from_dict(user_data)
            validation_result = user.validate()

            if not validation_result['valid']:
                raise ValueError(f"Invalid user data: {validation_result['errors']}")

            if self.db is None:
                # Development mode - return mock response
                logging.info(f"[DEV MODE] User profile saved: {user.user_id}")
                return user.to_dict()

            user_ref = self.db.collection(Collections.USERS).document(user.user_id)
            user_ref.set(user.to_dict(), merge=True)

            logging.info(f"User profile saved: {user.user_id}")
            return user.to_dict()

        except Exception as e:
            logging.error(f"Error saving user profile: {str(e)}")
            raise
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile by ID"""
        try:
            if self.db is None:
                # Development mode - return mock response
                logging.info(f"[DEV MODE] Getting user profile: {user_id}")
                return {
                    'user_id': user_id,
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'created_at': datetime.utcnow().isoformat()
                }

            user_ref = self.db.collection(Collections.USERS).document(user_id)
            doc = user_ref.get()

            if doc.exists:
                return doc.to_dict()
            return None

        except Exception as e:
            logging.error(f"Error retrieving user profile: {str(e)}")
            raise
    
    # Interaction operations
    def save_interaction(self, interaction_data: Dict) -> Dict:
        """Save user interaction"""
        try:
            interaction = Interaction.from_dict(interaction_data)
            validation_result = interaction.validate()

            if not validation_result['valid']:
                raise ValueError(f"Invalid interaction data: {validation_result['errors']}")

            if self.db is None:
                # Development mode - return mock response
                logging.info(f"[DEV MODE] Interaction saved: {interaction.interaction_id}")
                return interaction.to_dict()

            interaction_ref = self.db.collection(Collections.INTERACTIONS).document(interaction.interaction_id)
            interaction_ref.set(interaction.to_dict())

            logging.info(f"Interaction saved: {interaction.interaction_id}")
            return interaction.to_dict()

        except Exception as e:
            logging.error(f"Error saving interaction: {str(e)}")
            raise
    
    def get_interaction(self, interaction_id: str) -> Optional[Dict]:
        """Get interaction by ID"""
        try:
            interaction_ref = self.db.collection(Collections.INTERACTIONS).document(interaction_id)
            doc = interaction_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logging.error(f"Error retrieving interaction: {str(e)}")
            raise
    
    def get_user_history(self, user_id: str, limit: int = 20, offset: int = 0) -> Dict:
        """Get user interaction history with pagination"""
        try:
            if self.db is None:
                # Development mode - return mock response
                logging.info(f"[DEV MODE] Getting user history: {user_id}")
                mock_interactions = [
                    {
                        'interaction_id': 'mock-interaction-1',
                        'user_id': user_id,
                        'interaction_type': 'symptom_check',
                        'timestamp': datetime.utcnow().isoformat(),
                        'symptoms': ['fever', 'cough'],
                        'urgency_level': 'medium',
                        'status': 'completed'
                    }
                ]
                return {
                    'interactions': mock_interactions,
                    'total_count': 1,
                    'has_more': False
                }

            # Query interactions for user, ordered by timestamp (newest first)
            query = (self.db.collection(Collections.INTERACTIONS)
                    .where('user_id', '==', user_id)
                    .order_by('timestamp', direction=firestore.Query.DESCENDING)
                    .limit(limit + 1)  # Get one extra to check if there are more
                    .offset(offset))

            docs = query.stream()
            interactions = []

            for doc in docs:
                interactions.append(doc.to_dict())

            # Check if there are more results
            has_more = len(interactions) > limit
            if has_more:
                interactions = interactions[:limit]  # Remove the extra item

            # Get total count (this is expensive, consider caching in production)
            total_count_query = (self.db.collection(Collections.INTERACTIONS)
                               .where('user_id', '==', user_id))
            total_count = len(list(total_count_query.stream()))

            return {
                'interactions': interactions,
                'total_count': total_count,
                'has_more': has_more
            }

        except Exception as e:
            logging.error(f"Error retrieving user history: {str(e)}")
            raise
    
    # Booking operations
    def save_booking(self, booking_data: Dict) -> Dict:
        """Save appointment booking"""
        try:
            booking = Booking.from_dict(booking_data)
            validation_result = booking.validate()

            if not validation_result['valid']:
                raise ValueError(f"Invalid booking data: {validation_result['errors']}")

            if self.db is None:
                # Development mode - return mock response
                logging.info(f"[DEV MODE] Booking saved: {booking.booking_id}")
                return booking.to_dict()

            booking_ref = self.db.collection(Collections.BOOKINGS).document(booking.booking_id)
            booking_ref.set(booking.to_dict())

            logging.info(f"Booking saved: {booking.booking_id}")
            return booking.to_dict()

        except Exception as e:
            logging.error(f"Error saving booking: {str(e)}")
            raise
    
    def get_booking(self, booking_id: str) -> Optional[Dict]:
        """Get booking by ID"""
        try:
            if self.db is None:
                # Development mode - return mock response
                logging.info(f"[DEV MODE] Getting booking: {booking_id}")
                return {
                    'booking_id': booking_id,
                    'user_id': 'test123',
                    'doctor_id': 'doc_001',
                    'appointment_datetime': '2025-08-15T10:00:00',
                    'status': 'confirmed',
                    'appointment_type': 'consultation',
                    'consultation_mode': 'video'
                }

            booking_ref = self.db.collection(Collections.BOOKINGS).document(booking_id)
            doc = booking_ref.get()

            if doc.exists:
                return doc.to_dict()
            return None

        except Exception as e:
            logging.error(f"Error retrieving booking: {str(e)}")
            raise
    
    def get_user_bookings(self, user_id: str, status: str = None) -> List[Dict]:
        """Get user bookings, optionally filtered by status"""
        try:
            if self.db is None:
                # Development mode - return mock response
                logging.info(f"[DEV MODE] Getting bookings for user: {user_id}")
                return [{
                    'booking_id': 'booking_001',
                    'user_id': user_id,
                    'doctor_id': 'doc_001',
                    'appointment_datetime': '2025-08-15T10:00:00',
                    'status': status or 'confirmed',
                    'appointment_type': 'consultation',
                    'consultation_mode': 'video'
                }]

            query = (self.db.collection(Collections.BOOKINGS)
                    .where('user_id', '==', user_id)
                    .order_by('appointment_datetime', direction=firestore.Query.DESCENDING))

            if status:
                query = query.where('status', '==', status)

            docs = query.stream()
            bookings = []
            
            for doc in docs:
                bookings.append(doc.to_dict())
            
            return bookings
            
        except Exception as e:
            logging.error(f"Error retrieving user bookings: {str(e)}")
            raise
    
    def update_booking_status(self, booking_id: str, status: str, notes: str = None) -> bool:
        """Update booking status"""
        try:
            booking_ref = self.db.collection(Collections.BOOKINGS).document(booking_id)
            
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if notes:
                update_data['doctor_notes'] = notes
            
            booking_ref.update(update_data)
            
            logging.info(f"Booking status updated: {booking_id} -> {status}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating booking status: {str(e)}")
            raise
    
    # System operations
    def get_system_statistics(self) -> Dict:
        """Get basic system statistics"""
        try:
            stats = {}
            
            # Count users
            users_count = len(list(self.db.collection(Collections.USERS).stream()))
            stats['total_users'] = users_count
            
            # Count interactions (last 30 days)
            thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
            recent_interactions = (self.db.collection(Collections.INTERACTIONS)
                                 .where('timestamp', '>=', thirty_days_ago))
            stats['interactions_last_30_days'] = len(list(recent_interactions.stream()))
            
            # Count bookings (upcoming)
            now = datetime.utcnow().isoformat()
            upcoming_bookings = (self.db.collection(Collections.BOOKINGS)
                                .where('appointment_datetime', '>=', now)
                                .where('status', 'in', ['pending', 'confirmed']))
            stats['upcoming_bookings'] = len(list(upcoming_bookings.stream()))
            
            return stats
            
        except Exception as e:
            logging.error(f"Error retrieving system statistics: {str(e)}")
            return {
                'total_users': 0,
                'interactions_last_30_days': 0,
                'upcoming_bookings': 0,
                'error': str(e)
            }

    # Additional utility methods for backend completeness
    def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data (GDPR compliance)"""
        try:
            if self.db is None:
                logging.info(f"[DEV MODE] Would delete all data for user: {user_id}")
                return True

            # Delete user profile
            user_ref = self.db.collection(Collections.USERS).document(user_id)
            user_ref.delete()

            # Delete user interactions
            interactions_query = self.db.collection(Collections.INTERACTIONS).where('user_id', '==', user_id)
            for doc in interactions_query.stream():
                doc.reference.delete()

            # Delete user bookings
            bookings_query = self.db.collection(Collections.BOOKINGS).where('user_id', '==', user_id)
            for doc in bookings_query.stream():
                doc.reference.delete()

            logging.info(f"Successfully deleted all data for user: {user_id}")
            return True

        except Exception as e:
            logging.error(f"Error deleting user data: {str(e)}")
            raise

    def cleanup_old_interactions(self, days_old: int = 365) -> int:
        """Clean up interactions older than specified days"""
        try:
            if self.db is None:
                logging.info(f"[DEV MODE] Would cleanup interactions older than {days_old} days")
                return 0

            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            cutoff_timestamp = cutoff_date.isoformat()

            query = (self.db.collection(Collections.INTERACTIONS)
                    .where('timestamp', '<', cutoff_timestamp))

            deleted_count = 0
            for doc in query.stream():
                doc.reference.delete()
                deleted_count += 1

            logging.info(f"Cleaned up {deleted_count} old interactions")
            return deleted_count

        except Exception as e:
            logging.error(f"Error cleaning up old interactions: {str(e)}")
            raise

    def health_check(self) -> Dict:
        """Check Firebase service health"""
        try:
            if self.db is None:
                return {
                    'status': 'development_mode',
                    'firebase_connected': False,
                    'message': 'Running in development mode without Firebase'
                }

            # Try to read from a collection to test connectivity
            test_query = self.db.collection(Collections.USERS).limit(1)
            list(test_query.stream())

            return {
                'status': 'healthy',
                'firebase_connected': True,
                'message': 'Firebase service is operational'
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'firebase_connected': False,
                'error': str(e),
                'message': 'Firebase service is not operational'
            }

    # Privacy and Compliance Methods
    def save_user_consent(self, consent_data: Dict) -> Dict:
        """Save user consent record for compliance"""
        try:
            if self.db is None:
                # Mock response for development
                return {
                    'consent_id': f"consent_{secrets.token_hex(8)}",
                    'status': 'saved',
                    'timestamp': datetime.utcnow().isoformat()
                }

            consent_data['consent_id'] = f"consent_{secrets.token_hex(8)}"
            doc_ref = self.db.collection('user_consents').document(consent_data['consent_id'])
            doc_ref.set(consent_data)

            return consent_data

        except Exception as e:
            logging.error(f"Error saving user consent: {str(e)}")
            raise Exception("Failed to save consent record")

    def get_complete_user_data(self, user_id: str) -> Dict:
        """Get all user data for export (GDPR compliance)"""
        try:
            if self.db is None:
                # Mock complete user data for development
                return {
                    'profile': {
                        'user_id': user_id,
                        'name': 'Test User',
                        'email': 'test@example.com',
                        'created_at': datetime.utcnow().isoformat()
                    },
                    'interactions': [
                        {
                            'interaction_id': 'int_001',
                            'type': 'symptom_check',
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    ],
                    'bookings': [
                        {
                            'booking_id': 'book_001',
                            'doctor_id': 'doc_001',
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    ],
                    'consents': [
                        {
                            'consent_id': 'consent_001',
                            'consent_types': ['data_processing'],
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    ]
                }

            # Real implementation would query all user-related collections
            user_data = {
                'profile': {},
                'interactions': [],
                'bookings': [],
                'consents': []
            }

            return user_data

        except Exception as e:
            logging.error(f"Error getting complete user data: {str(e)}")
            raise Exception("Failed to retrieve user data")

    def delete_user_completely(self, user_id: str) -> Dict:
        """Completely delete user data (GDPR right to erasure)"""
        try:
            if self.db is None:
                return {
                    'status': 'deleted',
                    'records_affected': 5,
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Delete from all collections
            collections_to_clean = ['users', 'interactions', 'bookings', 'user_consents']
            records_affected = 0

            for collection_name in collections_to_clean:
                docs = self.db.collection(collection_name).where('user_id', '==', user_id).get()
                for doc in docs:
                    doc.reference.delete()
                    records_affected += 1

            return {
                'status': 'deleted',
                'records_affected': records_affected,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logging.error(f"Error deleting user data: {str(e)}")
            raise Exception("Failed to delete user data")

    def anonymize_user_data(self, user_id: str) -> Dict:
        """Anonymize user data (partial deletion)"""
        try:
            if self.db is None:
                return {
                    'status': 'anonymized',
                    'records_affected': 3,
                    'timestamp': datetime.utcnow().isoformat()
                }

            # Anonymize personal data while keeping medical records for compliance
            from services.privacy_service import PrivacyService
            privacy_service = PrivacyService()

            # Get user data and anonymize
            user_docs = self.db.collection('users').where('user_id', '==', user_id).get()
            records_affected = 0

            for doc in user_docs:
                anonymized_data = privacy_service.anonymize_user_data(doc.to_dict())
                doc.reference.update(anonymized_data)
                records_affected += 1

            return {
                'status': 'anonymized',
                'records_affected': records_affected,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logging.error(f"Error anonymizing user data: {str(e)}")
            raise Exception("Failed to anonymize user data")

    def get_user_data_summary(self, user_id: str) -> Dict:
        """Get summary of user data for privacy report"""
        try:
            if self.db is None:
                return {
                    'data_categories': ['profile', 'medical_interactions', 'appointments'],
                    'total_records': 15,
                    'oldest_record': '2024-01-15T10:00:00Z',
                    'newest_record': datetime.utcnow().isoformat(),
                    'storage_size_mb': 2.5
                }

            # Real implementation would calculate actual data summary
            return {
                'data_categories': [],
                'total_records': 0,
                'oldest_record': None,
                'newest_record': None,
                'storage_size_mb': 0
            }

        except Exception as e:
            logging.error(f"Error getting user data summary: {str(e)}")
            return {
                'error': 'Failed to retrieve data summary',
                'timestamp': datetime.utcnow().isoformat()
            }
