"""
API tests for AI Telemedicine Platform
Test cases for all API endpoints
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app import create_app
from config.settings import Config

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    DEBUG = True
    FIREBASE_PROJECT_ID = "test-project"
    FIREBASE_CLIENT_EMAIL = "test@test.com"
    FIREBASE_PRIVATE_KEY = "test-key"

@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config.from_object(TestConfig)
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def mock_firebase():
    """Mock Firebase service"""
    with patch('services.firebase_service.FirebaseService') as mock:
        yield mock

@pytest.fixture
def mock_ai_service():
    """Mock AI service"""
    with patch('services.ai_service.AIService') as mock:
        yield mock

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
        assert 'services' in data

class TestSymptomRoutes:
    """Test symptom check endpoints"""
    
    def test_symptom_check_success(self, client, mock_firebase, mock_ai_service):
        """Test successful symptom check"""
        # Mock Firebase save
        mock_firebase.return_value.save_interaction.return_value = {
            'interaction_id': 'test-interaction-id'
        }
        
        # Mock AI service response
        mock_ai_service.return_value.assess_symptoms.return_value = {
            'assessment': {'primary_condition': 'Common cold'},
            'recommendations': [{'action': 'Rest and hydrate'}],
            'urgency_level': 'low',
            'confidence_score': 0.85
        }
        
        payload = {
            'user_id': 'test-user-123',
            'symptoms': ['cough', 'fever'],
            'severity_level': 5,
            'duration': '2 days'
        }
        
        response = client.post('/api/symptom-check', 
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'interaction_id' in data['data']
        assert 'assessment' in data['data']
    
    def test_symptom_check_missing_required_fields(self, client):
        """Test symptom check with missing required fields"""
        payload = {
            'user_id': 'test-user-123'
            # Missing symptoms
        }
        
        response = client.post('/api/symptom-check',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'symptoms' in data['message']
    
    def test_symptom_check_invalid_severity(self, client):
        """Test symptom check with invalid severity level"""
        payload = {
            'user_id': 'test-user-123',
            'symptoms': ['cough'],
            'severity_level': 15  # Invalid - should be 1-10
        }
        
        response = client.post('/api/symptom-check',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'severity level' in data['message'].lower()
    
    def test_get_common_symptoms(self, client):
        """Test getting common symptoms list"""
        response = client.get('/api/symptoms/common')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'symptoms' in data['data']
        assert isinstance(data['data']['symptoms'], list)
        assert len(data['data']['symptoms']) > 0

class TestMentalHealthRoutes:
    """Test mental health assessment endpoints"""
    
    def test_mental_health_assessment_success(self, client, mock_firebase, mock_ai_service):
        """Test successful mental health assessment"""
        # Mock Firebase save
        mock_firebase.return_value.save_interaction.return_value = {
            'interaction_id': 'test-mental-health-id'
        }
        
        # Mock AI service response
        mock_ai_service.return_value.assess_mental_health.return_value = {
            'assessment': {'risk_level': 'low'},
            'recommendations': [{'action': 'Practice mindfulness'}],
            'risk_level': 'low',
            'confidence_score': 0.80
        }
        
        payload = {
            'user_id': 'test-user-123',
            'assessment_type': 'screening',
            'responses': {
                'mood_rating': 7,
                'anxiety_level': 4,
                'sleep_quality': 6
            }
        }
        
        response = client.post('/api/mental-health',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'interaction_id' in data['data']
        assert 'risk_level' in data['data']
    
    def test_mental_health_invalid_assessment_type(self, client):
        """Test mental health assessment with invalid type"""
        payload = {
            'user_id': 'test-user-123',
            'assessment_type': 'invalid_type',
            'responses': {'mood_rating': 5}
        }
        
        response = client.post('/api/mental-health',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_mental_health_resources(self, client):
        """Test getting mental health resources"""
        response = client.get('/api/mental-health/resources')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'crisis_hotlines' in data['data']
        assert 'online_resources' in data['data']

class TestBookingRoutes:
    """Test booking endpoints"""
    
    def test_book_doctor_success(self, client, mock_firebase):
        """Test successful doctor booking"""
        # Mock Firebase save
        mock_firebase.return_value.save_booking.return_value = {
            'booking_id': 'test-booking-id'
        }
        
        future_date = (datetime.now() + timedelta(days=1)).isoformat()
        
        payload = {
            'user_id': 'test-user-123',
            'doctor_id': 'doc_001',
            'appointment_datetime': future_date,
            'appointment_type': 'consultation',
            'consultation_mode': 'video',
            'reason_for_visit': 'Follow-up on recent symptoms'
        }
        
        response = client.post('/api/book-doctor',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'booking_id' in data['data']
    
    def test_book_doctor_past_date(self, client):
        """Test booking with past date"""
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        
        payload = {
            'user_id': 'test-user-123',
            'doctor_id': 'doc_001',
            'appointment_datetime': past_date,
            'appointment_type': 'consultation',
            'consultation_mode': 'video',
            'reason_for_visit': 'Test appointment'
        }
        
        response = client.post('/api/book-doctor',
                             data=json.dumps(payload),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'future' in data['message'].lower()

class TestUserRoutes:
    """Test user-related endpoints"""
    
    def test_get_user_history_success(self, client, mock_firebase):
        """Test getting user history"""
        # Mock Firebase response
        mock_firebase.return_value.get_user_history.return_value = {
            'interactions': [
                {
                    'interaction_id': 'test-1',
                    'interaction_type': 'symptom_check',
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'total_count': 1,
            'has_more': False
        }
        
        response = client.get('/api/user-history?user_id=test-user-123')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'history' in data['data']
    
    def test_get_user_history_missing_user_id(self, client):
        """Test getting user history without user_id"""
        response = client.get('/api/user-history')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'user_id' in data['message']

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/api/nonexistent-endpoint')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Not Found'
    
    def test_invalid_json(self, client):
        """Test invalid JSON handling"""
        response = client.post('/api/symptom-check',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_missing_content_type(self, client):
        """Test missing content type"""
        response = client.post('/api/symptom-check',
                             data=json.dumps({'test': 'data'}))
        
        assert response.status_code == 400

if __name__ == '__main__':
    pytest.main([__file__])
