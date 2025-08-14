from flask import Flask, request, jsonify
from flask_cors import CORS
import symptom_checker  # Your existing file
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/api/symptom-check', methods=['POST'])
def symptom_check():
    try:
        data = request.get_json()
        symptoms_text = data.get('symptoms', '')
        severity = data.get('severity', 'moderate')

        # Use your existing symptom checker
        result = symptom_checker.assess_symptoms(symptoms_text, severity)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mental-health', methods=['POST'])
def mental_health():
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', '')

        # Simple mental health triage
        crisis_keywords = ["suicide", "kill myself", "end it all", "harm myself"]
        stress_keywords = ["anxious", "panic", "stressed", "overwhelmed", "depressed"]

        symptoms_lower = symptoms.lower()

        if any(word in symptoms_lower for word in crisis_keywords):
            return jsonify({
                "risk_level": "CRISIS",
                "message": "Please seek immediate help",
                "resources": ["988 Suicide Hotline", "Emergency: 911"],
                "action": "CRISIS_INTERVENTION",
                "color": "red"
            })
        elif any(word in symptoms_lower for word in stress_keywords):
            return jsonify({
                "risk_level": "MODERATE",
                "message": "Consider talking to a mental health professional",
                "resources": ["Crisis Text Line: Text HOME to 741741"],
                "action": "MENTAL_HEALTH_SUPPORT",
                "color": "orange"
            })
        else:
            return jsonify({
                "risk_level": "LOW",
                "message": "Continue monitoring your mental health",
                "resources": ["National Mental Health: 1-800-662-4357"],
                "action": "SELF_CARE",
                "color": "green"
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/book-doctor', methods=['POST'])
def book_doctor():
    try:
        data = request.get_json()
        booking_info = {
            'name': data.get('name'),
            'contact': data.get('contact'),
            'urgency': data.get('urgency'),
            'symptoms': data.get('symptoms'),
            'timestamp': str(datetime.now())
        }

        # Generate booking ID
        booking_id = f"BOOK_{int(time.time())}"

        return jsonify({
            'booking_id': booking_id,
            'status': 'confirmed',
            'message': 'Doctor will contact you within 24 hours',
            'next_steps': ['Keep phone available', 'Monitor symptoms', 'Call 911 if emergency'],
            'booking_info': booking_info
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'API is running', 'version': '1.0'})

@app.route('/api/health-resources', methods=['GET'])
def health_resources():
    return jsonify({
        'emergency': {
            'phone': '911',
            'message': 'For life-threatening emergencies'
        },
        'mental_health': {
            'suicide_hotline': '988',
            'crisis_text': 'Text HOME to 741741'
        },
        'general_resources': [
            'Stay hydrated',
            'Get adequate rest',
            'Monitor symptoms',
            'Contact doctor if symptoms worsen'
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
