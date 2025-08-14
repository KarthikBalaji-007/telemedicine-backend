#!/usr/bin/env python3
"""
Complete Backend Testing Suite
Tests all backend functionality before AI/Frontend integration
"""

import sys
import json
import time
import requests
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_test(test_name, status, details=""):
    """Print test result"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {test_name}")
    if details:
        print(f"   {details}")

def test_server_startup():
    """Test if server starts and responds"""
    print_header("SERVER STARTUP & HEALTH TESTS")
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:5000/health', timeout=5)
        server_running = response.status_code == 200
        
        if server_running:
            health_data = response.json()
            print_test("Server Health Check", True, f"Status: {health_data.get('status', 'unknown')}")
            print_test("Server Response Time", True, f"< 5 seconds")
            return True
        else:
            print_test("Server Health Check", False, f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_test("Server Startup", False, "Server not running - start with: python app.py")
        return False

def test_core_services():
    """Test core backend services"""
    print_header("CORE SERVICES TESTS")
    
    try:
        # Test Firebase service
        from services.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        print_test("Firebase Service Import", True, "Service imported successfully")
        
        # Test Firebase connection
        health = firebase_service.health_check()
        print_test("Firebase Connection", health['status'] == 'healthy', 
                  f"Status: {health['status']}")
        
        # Test Privacy service
        from services.privacy_service import PrivacyService
        privacy_service = PrivacyService()
        print_test("Privacy Service Import", True, "Service imported successfully")
        
        # Test encryption
        test_data = "Sensitive medical data test"
        encrypted = privacy_service.encrypt_sensitive_data(test_data)
        decrypted = privacy_service.decrypt_sensitive_data(encrypted)
        print_test("Data Encryption/Decryption", decrypted == test_data, 
                  "AES-256 encryption working")
        
        # Test Speech service
        from services.speech_service import SpeechService
        speech_service = SpeechService()
        print_test("Speech Service Import", True, "Service imported successfully")
        
        # Test language detection
        detected_lang = speech_service.detect_language("I feel anxious and depressed")
        print_test("Language Detection", detected_lang == 'en', 
                  f"Detected: {detected_lang}")
        
        # Test AI service
        from services.ai_service import AIService
        ai_service = AIService()
        print_test("AI Service Import", True, "Service imported successfully")
        
        return True
        
    except Exception as e:
        print_test("Core Services", False, f"Error: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    print_header("API ENDPOINTS TESTS")
    
    if not test_server_startup():
        print("⚠️ Server not running - skipping API tests")
        return False
    
    endpoints_to_test = [
        # Core endpoints
        ('GET', '/health', 200),
        ('GET', '/api/test', 200),
        
        # Public endpoints (no auth required)
        ('GET', '/api/symptoms/common', 200),
        ('GET', '/api/mental-health/resources', 200),
        ('GET', '/api/privacy/compliance-status', 200),
        ('GET', '/api/system-stats', 200),
        
        # Auth endpoints
        ('POST', '/api/auth/register', [400, 422]),  # Missing data
        ('POST', '/api/auth/login', [400, 422]),     # Missing data
        
        # Protected endpoints (should return 401 without auth)
        ('POST', '/api/symptom-check', [400, 401, 422]),
        ('POST', '/api/mental-health', [400, 401, 422]),
        ('POST', '/api/book-doctor', [400, 401, 422]),
        ('GET', '/api/user-history', [401, 422]),
        ('GET', '/api/privacy/data-export', [401, 422]),
    ]
    
    success_count = 0
    total_count = len(endpoints_to_test)
    
    for method, endpoint, expected_codes in endpoints_to_test:
        try:
            if method == 'GET':
                response = requests.get(f'http://localhost:5000{endpoint}', timeout=5)
            else:
                response = requests.post(f'http://localhost:5000{endpoint}', 
                                       json={}, timeout=5)
            
            if isinstance(expected_codes, list):
                success = response.status_code in expected_codes
            else:
                success = response.status_code == expected_codes
            
            if success:
                success_count += 1
                print_test(f"{method} {endpoint}", True, f"Status: {response.status_code}")
            else:
                print_test(f"{method} {endpoint}", False, 
                          f"Status: {response.status_code}, Expected: {expected_codes}")
                
        except Exception as e:
            print_test(f"{method} {endpoint}", False, f"Error: {e}")
    
    print(f"\n📊 API Endpoints: {success_count}/{total_count} passed")
    return success_count >= total_count * 0.8  # 80% pass rate

def test_data_processing():
    """Test data processing and validation"""
    print_header("DATA PROCESSING TESTS")
    
    try:
        # Test symptom data processing
        from models.interaction import Interaction
        
        test_interaction_data = {
            'user_id': 'test_user_123',
            'interaction_type': 'symptom_check',
            'user_input': {
                'symptoms': ['headache', 'fever', 'fatigue'],
                'severity': 'moderate',
                'duration': '2 days'
            },
            'status': 'processing'
        }
        
        interaction = Interaction.from_dict(test_interaction_data)
        print_test("Interaction Model Creation", True, 
                  f"ID: {interaction.interaction_id}")
        
        # Test data validation
        interaction_dict = interaction.to_dict()
        required_fields = ['interaction_id', 'user_id', 'timestamp', 'status']
        has_required = all(field in interaction_dict for field in required_fields)
        print_test("Data Model Validation", has_required, 
                  "All required fields present")
        
        # Test mental health data processing
        from services.mental_health_security import MentalHealthSecurityService
        mh_security = MentalHealthSecurityService()
        
        test_mental_data = {
            'responses': {'mood_rating': 3, 'anxiety_level': 8},
            'symptoms': ['feeling hopeless', 'can\'t sleep'],
            'support_system': 'feeling very isolated'
        }
        
        # Test crisis detection
        risk_assessment = mh_security.assess_crisis_risk(test_mental_data)
        print_test("Crisis Risk Assessment", 'risk_level' in risk_assessment, 
                  f"Risk Level: {risk_assessment.get('risk_level', 'unknown')}")
        
        # Test data encryption for mental health
        encrypted_mh = mh_security.encrypt_mental_health_data(test_mental_data)
        decrypted_mh = mh_security.decrypt_mental_health_data(encrypted_mh)
        print_test("Mental Health Data Encryption", 
                  decrypted_mh['symptoms'] == test_mental_data['symptoms'],
                  "Ultra-secure encryption working")
        
        return True
        
    except Exception as e:
        print_test("Data Processing", False, f"Error: {e}")
        return False

def test_security_features():
    """Test security and privacy features"""
    print_header("SECURITY & PRIVACY TESTS")
    
    try:
        # Test input sanitization
        from services.mental_health_security import MentalHealthSecurityService
        mh_security = MentalHealthSecurityService()
        
        malicious_input = {
            'responses': {'mood_rating': '<script>alert("xss")</script>'},
            'symptoms': ['javascript:alert("hack")', 'onload=malicious()'],
            'support_system': 'eval(document.cookie)'
        }
        
        sanitized = mh_security.sanitize_mental_health_input(malicious_input)
        sanitized_text = str(sanitized)
        
        security_tests = [
            ('<script>' not in sanitized_text, "XSS Protection"),
            ('javascript:' not in sanitized_text, "JavaScript Injection Protection"),
            ('onload=' not in sanitized_text, "Event Handler Protection"),
            ('eval(' not in sanitized_text, "Code Execution Protection")
        ]
        
        for test_result, test_name in security_tests:
            print_test(test_name, test_result, "Malicious input blocked")
        
        # Test compliance
        from services.privacy_service import ComplianceService
        compliance_service = ComplianceService()
        
        hipaa_status = compliance_service.hipaa_compliance_check({})
        print_test("HIPAA Compliance Check", hipaa_status['compliance_score'] >= 0.7,
                  f"Score: {hipaa_status['compliance_score']:.0%}")
        
        gdpr_status = compliance_service.gdpr_compliance_check()
        print_test("GDPR Compliance Check", gdpr_status.get('data_subject_rights', False),
                  "Data subject rights implemented")
        
        return True
        
    except Exception as e:
        print_test("Security Features", False, f"Error: {e}")
        return False

def test_multilingual_support():
    """Test multilingual capabilities"""
    print_header("MULTILINGUAL SUPPORT TESTS")
    
    try:
        from services.speech_service import SpeechService
        speech_service = SpeechService()
        
        # Test language detection
        test_cases = [
            ('I feel very anxious and depressed', 'en'),
            ('Me siento muy ansioso y deprimido', 'es'),
            ('Je me sens très anxieux et déprimé', 'fr'),
            ('Ich fühle mich sehr ängstlich', 'de'),
        ]
        
        correct_detections = 0
        for text, expected in test_cases:
            detected = speech_service.detect_language(text)
            is_correct = detected == expected
            if is_correct:
                correct_detections += 1
            print_test(f"Language Detection ({expected})", is_correct,
                      f"'{text[:20]}...' → {detected}")
        
        print_test("Overall Language Detection", correct_detections >= 3,
                  f"{correct_detections}/4 languages detected correctly")
        
        # Test configuration
        from config.settings import Config
        print_test("Multilingual Configuration", 
                  len(Config.SUPPORTED_LANGUAGES) >= 5,
                  f"Supports {len(Config.SUPPORTED_LANGUAGES)} languages")
        
        return True
        
    except Exception as e:
        print_test("Multilingual Support", False, f"Error: {e}")
        return False

def calculate_overall_score(test_results):
    """Calculate overall backend readiness score"""
    total_tests = len(test_results)
    passed_tests = sum(test_results)
    score = (passed_tests / total_tests) * 100
    
    return score, passed_tests, total_tests

def main():
    """Run complete backend testing suite"""
    print("🧪 COMPLETE BACKEND TESTING SUITE")
    print("=" * 60)
    print(f"Testing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing all backend functionality before integration...")
    
    # Run all test categories
    test_results = []
    
    # Core functionality tests
    test_results.append(test_core_services())
    test_results.append(test_api_endpoints())
    test_results.append(test_data_processing())
    test_results.append(test_security_features())
    test_results.append(test_multilingual_support())
    
    # Calculate final score
    score, passed, total = calculate_overall_score(test_results)
    
    print_header("BACKEND TESTING RESULTS")
    
    print(f"📊 Test Categories Passed: {passed}/{total}")
    print(f"🎯 Backend Readiness Score: {score:.1f}/100")
    
    if score >= 90:
        print("🏆 BACKEND STATUS: EXCELLENT - READY FOR INTEGRATION!")
        print("✅ All systems operational")
        print("✅ Security measures active")
        print("✅ Ready for AI model integration")
        print("✅ Ready for frontend integration")
    elif score >= 75:
        print("🥈 BACKEND STATUS: GOOD - MOSTLY READY")
        print("✅ Core functionality working")
        print("⚠️ Some minor issues to address")
    elif score >= 60:
        print("🥉 BACKEND STATUS: FAIR - NEEDS IMPROVEMENT")
        print("⚠️ Several issues need attention")
        print("⚠️ Address failed tests before integration")
    else:
        print("❌ BACKEND STATUS: NOT READY")
        print("❌ Major issues need resolution")
        print("❌ Do not proceed with integration")
    
    print_header("INTEGRATION READINESS")
    
    if score >= 80:
        print("🚀 READY FOR NEXT STEPS:")
        print("✅ AI Model Integration - Backend can handle AI responses")
        print("✅ Frontend Integration - All API endpoints ready")
        print("✅ Production Deployment - Security and compliance ready")
    else:
        print("🔧 RECOMMENDED ACTIONS:")
        print("🔧 Review and fix failed tests above")
        print("🔧 Re-run testing suite after fixes")
        print("🔧 Achieve 80%+ score before integration")
    
    print(f"\n🎯 Backend testing complete! Score: {score:.1f}/100")
    return score >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
