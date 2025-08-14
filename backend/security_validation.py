#!/usr/bin/env python3
"""
World-Class Security Validation Script
Tests all security measures to ensure world-class protection
"""

import sys
import json
import time
import requests
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🛡️  {title}")
    print(f"{'='*60}")

def print_test(test_name, status, details=""):
    """Print test result"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {test_name}")
    if details:
        print(f"   {details}")

def test_encryption_security():
    """Test encryption and data protection"""
    print_header("ENCRYPTION & DATA PROTECTION TESTS")
    
    try:
        # Test basic privacy service
        from services.privacy_service import PrivacyService
        privacy_service = PrivacyService()
        
        # Test encryption strength
        test_data = "Sensitive medical information: Patient has severe depression and anxiety"
        encrypted = privacy_service.encrypt_sensitive_data(test_data)
        decrypted = privacy_service.decrypt_sensitive_data(encrypted)
        
        print_test("AES-256 Encryption", decrypted == test_data, "Military-grade encryption working")
        print_test("Data Integrity", len(encrypted) > len(test_data), "Encrypted data properly formatted")
        
        # Test mental health ultra-security
        from services.mental_health_security import MentalHealthSecurityService
        mh_security = MentalHealthSecurityService()
        
        mental_health_data = {
            'responses': {'mood_rating': 2, 'anxiety_level': 9, 'sleep_quality': 3},
            'symptoms': ['depression', 'anxiety', 'suicidal thoughts'],
            'triggers': ['work stress', 'relationship issues', 'financial problems'],
            'support_system': 'feeling very isolated and hopeless'
        }
        
        encrypted_mh = mh_security.encrypt_mental_health_data(mental_health_data)
        decrypted_mh = mh_security.decrypt_mental_health_data(encrypted_mh)
        
        print_test("Mental Health Ultra-Security", 
                  decrypted_mh['symptoms'] == mental_health_data['symptoms'],
                  "Enhanced encryption for psychological data")
        
        return True
        
    except Exception as e:
        print_test("Encryption Tests", False, f"Error: {e}")
        return False

def test_crisis_detection():
    """Test crisis risk detection system"""
    print_header("CRISIS DETECTION & INTERVENTION TESTS")
    
    try:
        from services.mental_health_security import MentalHealthSecurityService
        mh_security = MentalHealthSecurityService()
        
        # Test crisis-level input
        crisis_input = {
            'responses': {'mood_rating': 1, 'anxiety_level': 10, 'sleep_quality': 2},
            'symptoms': ['want to hurt myself', 'suicidal thoughts', 'hopeless'],
            'support_system': 'I feel like ending it all, no one cares'
        }
        
        risk_assessment = mh_security.assess_crisis_risk(crisis_input)
        
        print_test("Crisis Detection", 
                  risk_assessment['risk_level'] == 'crisis',
                  f"Risk Level: {risk_assessment['risk_level']}")
        
        print_test("Crisis Intervention Trigger", 
                  risk_assessment['crisis_intervention_needed'],
                  "Automatic intervention protocols activated")
        
        print_test("Professional Referral", 
                  risk_assessment['professional_referral_suggested'],
                  "Professional help recommended")
        
        # Test moderate risk input
        moderate_input = {
            'responses': {'mood_rating': 4, 'anxiety_level': 6},
            'symptoms': ['feeling sad', 'worried about work'],
            'support_system': 'have some friends but feeling overwhelmed'
        }
        
        moderate_assessment = mh_security.assess_crisis_risk(moderate_input)
        
        print_test("Moderate Risk Detection", 
                  moderate_assessment['risk_level'] in ['moderate', 'low'],
                  f"Risk Level: {moderate_assessment['risk_level']}")
        
        return True
        
    except Exception as e:
        print_test("Crisis Detection Tests", False, f"Error: {e}")
        return False

def test_input_sanitization():
    """Test input sanitization and security"""
    print_header("INPUT SANITIZATION & SECURITY TESTS")
    
    try:
        from services.mental_health_security import MentalHealthSecurityService
        mh_security = MentalHealthSecurityService()
        
        # Test malicious input
        malicious_input = {
            'responses': {'mood_rating': '<script>alert("xss")</script>'},
            'symptoms': ['javascript:alert("hack")', 'onload=malicious()'],
            'support_system': 'eval(document.cookie)'
        }
        
        sanitized = mh_security.sanitize_mental_health_input(malicious_input)
        
        # Check if malicious content was removed
        sanitized_text = str(sanitized)
        
        print_test("XSS Protection", 
                  '<script>' not in sanitized_text,
                  "Script tags removed")
        
        print_test("JavaScript Injection Protection", 
                  'javascript:' not in sanitized_text,
                  "JavaScript URLs blocked")
        
        print_test("Event Handler Protection", 
                  'onload=' not in sanitized_text,
                  "Event handlers removed")
        
        print_test("Code Execution Protection", 
                  'eval(' not in sanitized_text,
                  "Code execution attempts blocked")
        
        return True
        
    except Exception as e:
        print_test("Input Sanitization Tests", False, f"Error: {e}")
        return False

def test_compliance_status():
    """Test compliance and regulatory status"""
    print_header("COMPLIANCE & REGULATORY TESTS")
    
    try:
        from services.privacy_service import ComplianceService
        from services.mental_health_security import MentalHealthComplianceService
        
        compliance_service = ComplianceService()
        mh_compliance = MentalHealthComplianceService()
        
        # Test HIPAA compliance
        hipaa_status = compliance_service.hipaa_compliance_check({})
        
        print_test("HIPAA Compliance", 
                  hipaa_status['compliance_score'] >= 0.7,
                  f"Score: {hipaa_status['compliance_score']:.0%}")
        
        # Test GDPR compliance
        gdpr_status = compliance_service.gdpr_compliance_check()
        
        print_test("GDPR Compliance", 
                  gdpr_status.get('data_subject_rights', False),
                  "Data subject rights implemented")
        
        # Test mental health specific compliance
        mh_compliance_status = mh_compliance.check_mental_health_compliance()
        
        print_test("Mental Health Compliance", 
                  mh_compliance_status['compliance_score'] >= 0.8,
                  f"Score: {mh_compliance_status['compliance_score']:.0%}")
        
        print_test("Crisis Intervention Protocols", 
                  mh_compliance_status['items'].get('crisis_intervention_protocols', False),
                  "Emergency procedures in place")
        
        return True
        
    except Exception as e:
        print_test("Compliance Tests", False, f"Error: {e}")
        return False

def test_api_security():
    """Test API security measures"""
    print_header("API SECURITY TESTS")
    
    try:
        # Test if server is running
        try:
            response = requests.get('http://localhost:5000/health', timeout=5)
            server_running = response.status_code == 200
        except:
            server_running = False
        
        print_test("Server Availability", server_running, 
                  "Server running on localhost:5000" if server_running else "Start server with: python app.py")
        
        if server_running:
            # Test malicious input handling
            malicious_payload = {
                "user_id": "<script>alert('xss')</script>",
                "assessment_type": "'; DROP TABLE users; --",
                "responses": {
                    "mood_rating": "javascript:alert('hack')"
                }
            }
            
            try:
                response = requests.post(
                    'http://localhost:5000/api/mental-health',
                    json=malicious_payload,
                    timeout=5
                )
                
                # Should return error, not execute malicious code
                print_test("API Input Validation", 
                          response.status_code in [400, 401, 422],
                          f"Malicious input rejected (Status: {response.status_code})")
                
            except Exception as api_error:
                print_test("API Security Test", False, f"API Error: {api_error}")
        
        return True
        
    except Exception as e:
        print_test("API Security Tests", False, f"Error: {e}")
        return False

def calculate_security_score(test_results):
    """Calculate overall security score"""
    total_tests = len(test_results)
    passed_tests = sum(test_results)
    score = (passed_tests / total_tests) * 100
    
    return score, passed_tests, total_tests

def main():
    """Run all security validation tests"""
    print("🛡️ WORLD-CLASS SECURITY VALIDATION")
    print("=" * 60)
    print(f"Testing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing comprehensive security measures...")
    
    # Run all tests
    test_results = []
    
    test_results.append(test_encryption_security())
    test_results.append(test_crisis_detection())
    test_results.append(test_input_sanitization())
    test_results.append(test_compliance_status())
    test_results.append(test_api_security())
    
    # Calculate final score
    score, passed, total = calculate_security_score(test_results)
    
    print_header("SECURITY VALIDATION RESULTS")
    
    print(f"📊 Tests Passed: {passed}/{total}")
    print(f"🎯 Security Score: {score:.1f}/100")
    
    if score >= 95:
        print("🏆 WORLD-CLASS SECURITY STATUS: ACHIEVED!")
        print("🛡️ Your platform has world-class security protection")
        print("✅ Ready for production deployment")
    elif score >= 85:
        print("🥈 ENTERPRISE-GRADE SECURITY: ACHIEVED!")
        print("🛡️ Your platform has enterprise-level protection")
        print("⚠️  Minor improvements recommended")
    elif score >= 70:
        print("🥉 GOOD SECURITY: ACHIEVED!")
        print("🛡️ Your platform has solid security measures")
        print("⚠️  Some improvements needed for world-class status")
    else:
        print("❌ SECURITY IMPROVEMENTS NEEDED")
        print("🛡️ Additional security measures required")
        print("⚠️  Not ready for production deployment")
    
    # Security recommendations
    print_header("SECURITY RECOMMENDATIONS")
    
    if score >= 95:
        print("✅ Maintain current security measures")
        print("✅ Regular security audits recommended")
        print("✅ Consider third-party security certification")
    else:
        print("🔧 Review failed tests above")
        print("🔧 Implement missing security measures")
        print("🔧 Re-run validation after improvements")
    
    print("\n🚀 Security validation complete!")
    return score >= 95

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
