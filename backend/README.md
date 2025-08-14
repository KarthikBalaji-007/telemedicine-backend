# AI Telemedicine Platform - Backend

A comprehensive Flask-based backend for an AI-powered telemedicine platform, designed for hackathon development with clear integration points for team collaboration.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Firebase project with Firestore enabled
- Virtual environment (recommended)

### Installation

1. **Clone and setup environment:**
```bash
cd ai-telemedicine-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your Firebase credentials and configuration
```

3. **Run the application:**
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Health Check
Visit `http://localhost:5000/health` to verify the server is running.

## 📋 API Endpoints

### Core Endpoints

#### Health Check
- **GET** `/health` - System health status

#### Symptom Assessment
- **POST** `/api/symptom-check` - AI-powered symptom assessment
- **GET** `/api/symptom-check/{interaction_id}` - Get assessment results
- **GET** `/api/symptoms/common` - List of common symptoms

#### Mental Health Assessment
- **POST** `/api/mental-health` - Mental health screening
- **GET** `/api/mental-health/{interaction_id}` - Get assessment results
- **GET** `/api/mental-health/resources` - Crisis resources and support

#### Doctor Booking
- **POST** `/api/book-doctor` - Book appointment with doctor
- **GET** `/api/bookings/{booking_id}` - Get booking details
- **POST** `/api/bookings/{booking_id}/cancel` - Cancel appointment
- **GET** `/api/users/{user_id}/bookings` - Get user's bookings

#### User Management
- **GET** `/api/user-history` - Get user interaction history
- **GET** `/api/user-profile` - Get user profile
- **POST** `/api/user-profile` - Create/update user profile
- **GET** `/api/system-stats` - System statistics

> **📖 Detailed API Documentation:** See `API_DOCUMENTATION.md` for complete request/response examples

## 🔧 Configuration

### Environment Variables

```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key
PORT=5000

# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# AI Service Configuration (Team Lead Integration)
AI_SERVICE_URL=http://localhost:8000
AI_SERVICE_API_KEY=your-ai-api-key
AI_SERVICE_TIMEOUT=30

# Frontend URLs (for CORS)
FRONTEND_URLS=http://localhost:3000,http://localhost:3001
```

## 🤝 Team Integration Points

### For Team Lead (AI Model Integration)

The backend is ready for AI model integration with placeholder functions in `services/ai_service.py`:

```python
# TODO: REQUEST FROM TEAM LEAD - Implement these functions:
def assess_symptoms(symptoms, severity_level, duration, additional_info, user_context)
def assess_mental_health(assessment_type, responses, symptoms, duration, triggers, user_context)
def get_model_health()
```

**Expected AI Response Format:**
```json
{
  "assessment": {
    "primary_condition": "string",
    "differential_diagnoses": ["condition1", "condition2"],
    "severity_assessment": "mild|moderate|severe"
  },
  "recommendations": [
    {
      "type": "immediate|short_term|long_term",
      "action": "string",
      "priority": "high|medium|low"
    }
  ],
  "urgency_level": "low|medium|high|emergency",
  "confidence_score": 0.0-1.0,
  "professional_referral_suggested": boolean
}
```

### For Frontend Team

All API endpoints are documented and ready for integration:

- **Base URL:** `http://localhost:5000`
- **Content-Type:** `application/json`
- **CORS:** Enabled for development
- **Response Format:** Standardized JSON responses

**Example API Call:**
```javascript
const response = await fetch('http://localhost:5000/api/symptom-check', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'user123',
    symptoms: ['fever', 'cough'],
    severity_level: 6,
    duration: '3 days'
  })
});

const result = await response.json();
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py
```

### Test Endpoints with curl

```bash
# Health check
curl http://localhost:5000/health

# Symptom check
curl -X POST http://localhost:5000/api/symptom-check \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test123","symptoms":["fever","cough"],"severity_level":5}'

# Get common symptoms
curl http://localhost:5000/api/symptoms/common
```

## 📁 Project Structure

```
ai-telemedicine-backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── config/               # Configuration files
│   ├── settings.py       # App configuration
│   └── firebase_config.py # Firebase setup
├── api/                  # API routes
│   ├── routes.py         # General API routes
│   ├── symptom_routes.py # Symptom assessment
│   ├── mental_health_routes.py # Mental health
│   ├── booking_routes.py # Doctor booking
│   └── utils.py          # API utilities
├── services/             # Business logic
│   ├── ai_service.py     # AI model integration
│   ├── firebase_service.py # Database operations
│   └── validation_service.py # Input validation
├── models/               # Data models
│   ├── user.py           # User model
│   ├── interaction.py    # Interaction model
│   └── booking.py        # Booking model
├── utils/                # Utilities
│   ├── helpers.py        # Helper functions
│   ├── decorators.py     # Flask decorators
│   └── constants.py      # Application constants
├── tests/                # Test files
│   └── test_api.py       # API tests
└── logs/                 # Application logs
```

## 🔒 Security Features

- Input validation and sanitization
- Error handling with safe error messages
- Request size limits
- CORS configuration
- Sensitive data masking in logs

## 📊 Monitoring & Logging

- Comprehensive request/response logging
- Error tracking and reporting
- Performance monitoring
- Health check endpoints

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production (with Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use the established error handling patterns
5. Follow the integration coordination comments

## 📞 Team Coordination

### TODO Items for Team Integration:

**Team Lead (AI Model):**
- [ ] Implement `assess_symptoms()` function
- [ ] Implement `assess_mental_health()` function
- [ ] Provide AI service endpoint details
- [ ] Define AI response format specifications

**Frontend Team:**
- [ ] Integrate with documented API endpoints
- [ ] Handle standardized response format
- [ ] Implement error handling for API failures
- [ ] Add loading states for AI processing

**General Team:**
- [ ] Set up Firebase project and credentials
- [ ] Configure video conferencing service
- [ ] Set up notification service (email/SMS)
- [ ] Define doctor availability system

## 📝 License

This project is developed for hackathon purposes.

---

**Ready for Integration!** 🎯

The backend is fully functional with mock AI responses and ready for team integration. All endpoints are tested and documented for immediate frontend development while AI model integration can happen in parallel.
