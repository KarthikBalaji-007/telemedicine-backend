"""
Comprehensive API endpoint tests for AI Telemedicine Platform
Tests all backend API endpoints for functionality and validation
"""

import unittest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

class TestAPIEndpoints(unittest.TestCase):
    """Test all API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Test data
        self.test_user_id = 'test_user_123'
        self.test_doctor_id = 'doc_001'
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('services', data)
    
    def test_symptom_check_endpoint(self):
        """Test symptom check endpoint"""
        payload = {
            'user_id': self.test_user_id,
            'symptoms': ['fever', 'headache', 'fatigue'],
            'severity': 'moderate',
            'duration': '2 days'
        }
        
        response = self.client.post('/api/symptom-check', 
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('interaction_id', data['data'])
        self.assertIn('assessment', data['data'])
    
    def test_mental_health_endpoint(self):
        """Test mental health assessment endpoint"""
        payload = {
            'user_id': self.test_user_id,
            'assessment_type': 'screening',
            'responses': {
                'mood_rating': 3,
                'anxiety_level': 6,
                'sleep_quality': 4,
                'stress_level': 7,
                'energy_level': 3,
                'social_interaction': 5,
                'concentration': 4,
                'appetite': 6
            },
            'duration': '2 weeks'
        }
        
        response = self.client.post('/api/mental-health',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('interaction_id', data['data'])
        self.assertIn('assessment', data['data'])
    
    def test_book_doctor_endpoint(self):
        """Test book doctor appointment endpoint"""
        payload = {
            'user_id': self.test_user_id,
            'doctor_id': self.test_doctor_id,
            'appointment_datetime': '2025-08-15T10:00:00',
            'appointment_type': 'consultation',
            'consultation_mode': 'video',
            'reason_for_visit': 'Follow-up consultation for test',
            'symptoms_summary': ['fever', 'headache'],
            'urgency_level': 'medium'
        }
        
        response = self.client.post('/api/book-doctor',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('booking_id', data['data'])
        self.assertIn('appointment_datetime', data['data'])
    
    def test_user_history_endpoint(self):
        """Test user history endpoint"""
        response = self.client.get(f'/api/user-history?user_id={self.test_user_id}&limit=5')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('history', data['data'])
        self.assertIn('total_count', data['data'])
    
    def test_user_profile_get_endpoint(self):
        """Test get user profile endpoint"""
        response = self.client.get(f'/api/user-profile?user_id={self.test_user_id}')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
    
    def test_system_stats_endpoint(self):
        """Test system statistics endpoint"""
        response = self.client.get('/api/system-stats')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('total_users', data['data'])
    
    def test_auth_register_endpoint(self):
        """Test user registration endpoint"""
        payload = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'phone': '+1234567890'
        }
        
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('token', data['data'])
        self.assertIn('user_id', data['data'])
    
    def test_auth_login_endpoint(self):
        """Test user login endpoint"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('token', data['data'])
    
    def test_invalid_json_request(self):
        """Test invalid JSON request handling"""
        response = self.client.post('/api/symptom-check',
                                  data='invalid json',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
    
    def test_missing_required_fields(self):
        """Test missing required fields validation"""
        payload = {
            'user_id': self.test_user_id
            # Missing required fields
        }
        
        response = self.client.post('/api/symptom-check',
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Missing required fields', data['message'])
    
    def test_404_endpoint(self):
        """Test 404 error handling"""
        response = self.client.get('/api/nonexistent-endpoint')
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Not Found')

def run_tests():
    """Run all tests and return results"""
    print("🧪 Running Backend API Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAPIEndpoints)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"🧪 Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if success else '❌ SOME TESTS FAILED'}")
    
    return success

if __name__ == '__main__':
    run_tests()
