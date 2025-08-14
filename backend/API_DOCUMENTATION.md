# AI Telemedicine Platform - API Documentation

Complete API documentation for frontend integration and team coordination.

## Base URL
- **Development:** `http://localhost:5000`
- **Production:** `https://your-domain.com`

## Authentication
Currently using user_id for identification. Future versions will implement JWT tokens.

## Response Format

All API responses follow this standardized format:

```json
{
  "success": boolean,
  "message": "string",
  "timestamp": "ISO datetime",
  "request_id": "uuid",
  "data": {} // Present on success
}
```

## Error Responses

```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "ISO datetime",
  "request_id": "uuid",
  "errors": ["detailed error messages"] // Optional
}
```

---

## 🏥 Health Check

### GET /health

Check system health and service status.

**Response:**
```json
{
  "success": true,
  "message": "System healthy",
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "version": "1.0.0",
    "services": {
      "flask": "running",
      "firebase": "connected",
      "ai_service": "available"
    }
  }
}
```

---

## 🩺 Symptom Assessment

### POST /api/symptom-check

Perform AI-powered symptom assessment.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "symptoms": ["symptom1", "symptom2"], // required, max 10 items
  "severity_level": 5, // optional, 1-10 scale
  "duration": "2 days", // optional
  "additional_info": "string", // optional
  "age": 30, // optional
  "gender": "male|female|other", // optional
  "medical_history": ["condition1"] // optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Symptom assessment completed successfully",
  "data": {
    "interaction_id": "uuid",
    "assessment": {
      "primary_condition": "Upper respiratory infection",
      "differential_diagnoses": ["Common cold", "Flu", "Allergies"],
      "severity_assessment": "moderate",
      "clinical_notes": "Patient presents with typical cold symptoms"
    },
    "recommendations": [
      {
        "type": "immediate",
        "action": "Rest and stay hydrated",
        "priority": "high"
      }
    ],
    "urgency_level": "medium",
    "confidence_score": 0.85,
    "follow_up_required": true,
    "follow_up_timeframe": "3-5 days",
    "doctor_referral_suggested": false,
    "processing_time": 2.3
  }
}
```

### GET /api/symptom-check/{interaction_id}

Get previous symptom assessment results.

**Response:** Same as POST response above.

### GET /api/symptoms/common

Get list of common symptoms for autocomplete.

**Response:**
```json
{
  "success": true,
  "message": "Common symptoms retrieved successfully",
  "data": {
    "symptoms": [
      "Fever", "Headache", "Cough", "Sore throat", "Runny nose",
      "Fatigue", "Body aches", "Nausea", "Vomiting", "Diarrhea"
    ]
  }
}
```

---

## 🧠 Mental Health Assessment

### POST /api/mental-health

Perform mental health screening and assessment.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "assessment_type": "screening|detailed|follow_up", // required
  "responses": { // required
    "mood_rating": 7, // 1-10 scale
    "anxiety_level": 4, // 1-10 scale
    "sleep_quality": 6, // 1-10 scale
    "stress_level": 5, // 1-10 scale
    "energy_level": 6, // 1-10 scale
    "social_interaction": 7, // 1-10 scale
    "concentration": 5, // 1-10 scale
    "appetite": 8 // 1-10 scale
  },
  "symptoms": ["anxiety", "insomnia"], // optional
  "duration": "2 weeks", // optional
  "triggers": ["work stress", "relationship issues"], // optional
  "previous_episodes": true, // optional
  "medication_history": ["sertraline"], // optional
  "support_system": "family and friends" // optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Mental health assessment completed successfully",
  "data": {
    "interaction_id": "uuid",
    "assessment_type": "screening",
    "assessment": {
      "risk_level": "moderate",
      "primary_concerns": ["Anxiety", "Sleep issues"],
      "severity_indicators": {
        "depression_score": 12,
        "anxiety_score": 8,
        "stress_level": "moderate"
      },
      "clinical_notes": "Moderate anxiety with sleep disturbances"
    },
    "risk_level": "moderate",
    "recommendations": [
      {
        "category": "therapy",
        "action": "Consider cognitive behavioral therapy",
        "priority": "high"
      },
      {
        "category": "lifestyle",
        "action": "Practice relaxation techniques",
        "priority": "medium"
      }
    ],
    "resources": [
      {
        "type": "website",
        "name": "Anxiety and Depression Association",
        "description": "Educational resources and support",
        "contact": "https://adaa.org"
      }
    ],
    "follow_up_required": true,
    "follow_up_timeframe": "1 week",
    "professional_referral_suggested": true,
    "crisis_intervention_needed": false,
    "confidence_score": 0.82,
    "processing_time": 1.8
  }
}
```

### GET /api/mental-health/{interaction_id}

Get previous mental health assessment results.

### GET /api/mental-health/resources

Get mental health resources and crisis information.

**Response:**
```json
{
  "success": true,
  "message": "Mental health resources retrieved successfully",
  "data": {
    "crisis_hotlines": {
      "national_suicide_prevention_lifeline": {
        "number": "988",
        "description": "24/7 crisis support and suicide prevention",
        "website": "https://suicidepreventionlifeline.org"
      },
      "crisis_text_line": {
        "number": "Text HOME to 741741",
        "description": "24/7 crisis support via text",
        "website": "https://www.crisistextline.org"
      }
    },
    "online_resources": [
      {
        "name": "Mental Health America",
        "url": "https://www.mhanational.org",
        "description": "Mental health information and screening tools"
      }
    ],
    "self_care_tips": [
      "Practice deep breathing exercises",
      "Maintain a regular sleep schedule",
      "Engage in physical activity"
    ]
  }
}
```

---

## 👨‍⚕️ Doctor Booking

### POST /api/book-doctor

Book an appointment with a doctor.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "doctor_id": "string (required)",
  "appointment_datetime": "2024-01-15T14:30:00Z", // required, ISO format
  "duration_minutes": 30, // optional, default 30, range 15-120
  "appointment_type": "consultation|follow_up|emergency", // required
  "consultation_mode": "video|phone|in_person", // required
  "reason_for_visit": "Follow-up on recent symptoms", // required, min 10 chars
  "symptoms_summary": ["fever", "cough"], // optional
  "urgency_level": "medium", // optional: low|medium|high|emergency
  "related_interaction_id": "uuid", // optional, link to symptom check
  "insurance_info": { // optional
    "provider": "Blue Cross",
    "policy_number": "12345"
  },
  "patient_notes": "Additional information" // optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Appointment booked successfully",
  "data": {
    "booking_id": "uuid",
    "appointment_datetime": "2024-01-15T14:30:00Z",
    "appointment_end_time": "2024-01-15T15:00:00Z",
    "doctor_info": {
      "doctor_id": "doc_001",
      "name": "Dr. Sarah Johnson",
      "specialty": "Family Medicine",
      "rating": 4.8,
      "experience_years": 12
    },
    "appointment_type": "consultation",
    "consultation_mode": "video",
    "status": "pending",
    "meeting_link": "https://telemedicine-platform.com/meeting/uuid", // for video
    "estimated_cost": 150
  }
}
```

### GET /api/bookings/{booking_id}

Get booking details by ID.

### POST /api/bookings/{booking_id}/cancel

Cancel an appointment (requires 24-hour notice).

**Response:**
```json
{
  "success": true,
  "message": "Booking cancelled successfully"
}
```

### GET /api/users/{user_id}/bookings

Get all bookings for a user.

**Query Parameters:**
- `status` (optional): Filter by status (pending|confirmed|cancelled|completed)

**Response:**
```json
{
  "success": true,
  "message": "User bookings retrieved successfully",
  "data": {
    "bookings": [
      {
        "booking_id": "uuid",
        "appointment_datetime": "2024-01-15T14:30:00Z",
        "doctor_info": {
          "name": "Dr. Sarah Johnson",
          "specialty": "Family Medicine"
        },
        "appointment_type": "consultation",
        "consultation_mode": "video",
        "status": "confirmed",
        "urgency_level": "medium"
      }
    ]
  }
}
```

---

## 👤 User Management

### GET /api/user-history

Get user interaction history with pagination.

**Query Parameters:**
- `user_id` (required): User identifier
- `limit` (optional): Number of records (default: 20, max: 50)
- `offset` (optional): Number of records to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "message": "User history retrieved successfully",
  "data": {
    "user_id": "user123",
    "history": [
      {
        "interaction_id": "uuid",
        "interaction_type": "symptom_check",
        "timestamp": "2024-01-01T12:00:00Z",
        "symptoms": ["fever", "cough"],
        "urgency_level": "medium",
        "status": "completed",
        "follow_up_required": true
      }
    ],
    "total_count": 25,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

### GET /api/user-profile

Get user profile information.

**Query Parameters:**
- `user_id` (required): User identifier

### POST /api/user-profile

Create or update user profile.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "name": "string (required)",
  "email": "string (required)",
  "phone": "string (optional)",
  "date_of_birth": "1990-01-01", // optional, ISO date
  "gender": "male|female|other", // optional
  "medical_history": ["diabetes", "hypertension"], // optional
  "emergency_contact": { // optional
    "name": "John Doe",
    "phone": "+1234567890",
    "relationship": "spouse"
  }
}
```

### GET /api/system-stats

Get system statistics (admin endpoint).

---

## 🚨 Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 503 | Service Unavailable |
| 504 | Gateway Timeout |

## 🔄 Rate Limiting

- **Default:** 60 requests per minute per IP
- **Headers:** Rate limit info in response headers
- **Exceeded:** Returns 429 status code

## 📝 Notes for Frontend Integration

1. **Content-Type:** Always use `application/json`
2. **Error Handling:** Check `success` field in response
3. **Loading States:** AI processing can take 2-5 seconds
4. **Validation:** Client-side validation recommended
5. **Retry Logic:** Implement for 503/504 errors
6. **Crisis Handling:** Special UI for crisis-level mental health assessments

## 🔗 Integration Examples

### JavaScript/React Example
```javascript
const assessSymptoms = async (symptoms, userId) => {
  try {
    const response = await fetch('/api/symptom-check', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        symptoms: symptoms,
        severity_level: 6
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      return result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('Symptom assessment failed:', error);
    throw error;
  }
};
```

### Python Example
```python
import requests

def assess_symptoms(symptoms, user_id):
    url = "http://localhost:5000/api/symptom-check"
    payload = {
        "user_id": user_id,
        "symptoms": symptoms,
        "severity_level": 6
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["success"]:
        return result["data"]
    else:
        raise Exception(result["message"])
```
