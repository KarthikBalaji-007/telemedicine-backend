def assess_symptoms(symptoms_text, severity_level="moderate"):
    """
    Enhanced symptom assessment with explainability
    """
    symptoms_lower = symptoms_text.lower()

    # Enhanced keyword lists
    emergency_keywords = [
        "chest pain", "difficulty breathing", "can't breathe",
        "severe headache", "unconscious", "heavy bleeding",
        "severe bleeding", "chest tightness", "heart racing",
        "can't move", "severe burns", "poisoning"
    ]

    moderate_keywords = [
        "fever", "persistent cough", "nausea", "vomiting",
        "dizziness", "headache", "stomach pain", "sore throat",
        "back pain", "joint pain", "rash", "swelling"
    ]

    mild_keywords = [
        "runny nose", "sneezing", "tired", "fatigue",
        "mild headache", "slight cough", "minor cut",
        "bruise", "muscle soreness"
    ]

    # Track matched symptoms for explainability
    matched_emergency = []
    matched_moderate = []
    matched_mild = []

    # Check emergency symptoms
    for symptom in emergency_keywords:
        if symptom in symptoms_lower:
            matched_emergency.append(symptom)

    # Check moderate symptoms
    for symptom in moderate_keywords:
        if symptom in symptoms_lower:
            matched_moderate.append(symptom)

    # Check mild symptoms
    for symptom in mild_keywords:
        if symptom in symptoms_lower:
            matched_mild.append(symptom)

    # Decision logic with explainability
    if matched_emergency:
        return {
            "risk_level": "HIGH",
            "message": "Seek immediate medical attention",
            "explanation": f"You mentioned serious symptoms that may require urgent care",
            "matched_symptoms": matched_emergency,
            "explanation_details": [f"'{symptom}' indicates potential emergency" for symptom in matched_emergency],
            "action": "EMERGENCY",
            "color": "red",
            "confidence": "high",
            "reasoning": "Emergency symptoms detected requiring immediate medical evaluation"
        }

    elif matched_moderate:
        return {
            "risk_level": "MODERATE",
            "message": "Consider talking to a doctor within 24-48 hours",
            "explanation": f"You mentioned symptoms that should be evaluated by a professional",
            "matched_symptoms": matched_moderate,
            "explanation_details": [f"'{symptom}' suggests medical consultation needed" for symptom in matched_moderate],
            "action": "CONSULT_DOCTOR",
            "color": "orange",
            "confidence": "medium",
            "reasoning": "Moderate symptoms that benefit from professional medical assessment"
        }

    elif matched_mild:
        return {
            "risk_level": "LOW",
            "message": "Monitor symptoms and try home care",
            "explanation": f"You mentioned symptoms that are usually manageable with self-care",
            "matched_symptoms": matched_mild,
            "explanation_details": [f"'{symptom}' typically improves with rest and care" for symptom in matched_mild],
            "action": "HOME_CARE",
            "color": "green",
            "confidence": "medium",
            "reasoning": "Mild symptoms that can often be managed at home"
        }

    else:
        return {
            "risk_level": "UNCLEAR",
            "message": "Please provide more specific symptoms",
            "explanation": "We need more details to give you proper guidance",
            "matched_symptoms": [],
            "explanation_details": ["No specific medical keywords detected"],
            "action": "GATHER_MORE_INFO",
            "color": "gray",
            "confidence": "low",
            "reasoning": "Insufficient symptom information for reliable assessment"
        }

# Test the enhanced function
if __name__ == "__main__":
    test_cases = [
        "I have severe chest pain and can't breathe",
        "I have a fever and persistent headache",
        "Just feeling tired with a runny nose",
        "I feel unwell but can't describe it"
    ]

    for test in test_cases:
        result = assess_symptoms(test)
        print(f"Input: {test}")
        print(f"Risk: {result['risk_level']}")
        print(f"Matched: {result['matched_symptoms']}")
        print(f"Reasoning: {result['reasoning']}")
        print("---")
