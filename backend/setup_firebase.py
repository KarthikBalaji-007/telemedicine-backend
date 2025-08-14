#!/usr/bin/env python3
"""
Firebase Setup Script for AI Telemedicine Backend
Run this script to set up Firebase credentials for your backend
"""

import os
import json
import sys

def main():
    print("🔥 Firebase Setup for AI Telemedicine Backend")
    print("=" * 50)
    print()
    
    print("📋 STEP 1: Create Firebase Project")
    print("1. Go to: https://console.firebase.google.com/")
    print("2. Click 'Create a project'")
    print("3. Project name: 'ai-telemedicine-backend'")
    print("4. Enable/disable Google Analytics (your choice)")
    print("5. Click 'Create project'")
    print()
    
    print("📋 STEP 2: Enable Firestore Database")
    print("1. In your Firebase project dashboard")
    print("2. Click 'Firestore Database'")
    print("3. Click 'Create database'")
    print("4. Choose 'Start in test mode' (for development)")
    print("5. Select location closest to you")
    print()
    
    print("📋 STEP 3: Get Service Account Credentials")
    print("1. Go to Project Settings (gear icon)")
    print("2. Click 'Service accounts' tab")
    print("3. Click 'Generate new private key'")
    print("4. Download the JSON file")
    print()
    
    print("📋 STEP 4: Configure Backend")
    json_file = input("Enter path to downloaded JSON file (or press Enter to skip): ").strip()
    
    if json_file and os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                creds = json.load(f)
            
            # Update .env file
            env_content = f"""# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
PORT=5000

# Firebase Configuration - Backend Database Setup
FIREBASE_PROJECT_ID={creds['project_id']}
FIREBASE_PRIVATE_KEY_ID={creds['private_key_id']}
FIREBASE_PRIVATE_KEY="{creds['private_key']}"
FIREBASE_CLIENT_EMAIL={creds['client_email']}
FIREBASE_CLIENT_ID={creds['client_id']}

# AI Service Configuration (Team Lead Integration)
AI_SERVICE_URL=http://localhost:8000
AI_SERVICE_API_KEY=your-ai-service-api-key
AI_SERVICE_TIMEOUT=30

# Frontend URLs (for CORS in production)
FRONTEND_URLS=http://localhost:3000,http://localhost:3001

# Application Settings
LOG_LEVEL=DEBUG
RATE_LIMIT_PER_MINUTE=60
MAX_SYMPTOMS_PER_REQUEST=10
MAX_HISTORY_ITEMS=50
"""
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            print("✅ Firebase credentials configured successfully!")
            print("✅ .env file updated")
            print()
            print("🚀 Your backend is now ready with real Firebase database!")
            print("💰 Firebase free tier: 50k reads + 20k writes per day")
            
        except Exception as e:
            print(f"❌ Error processing JSON file: {e}")
            print("Please check the file path and try again")
    
    else:
        print("⚠️  Skipping automatic configuration")
        print("📝 Manual setup:")
        print("1. Open the downloaded JSON file")
        print("2. Copy values to .env file:")
        print("   - project_id -> FIREBASE_PROJECT_ID")
        print("   - private_key_id -> FIREBASE_PRIVATE_KEY_ID")
        print("   - private_key -> FIREBASE_PRIVATE_KEY")
        print("   - client_email -> FIREBASE_CLIENT_EMAIL")
        print("   - client_id -> FIREBASE_CLIENT_ID")
    
    print()
    print("🔄 After setup, restart your backend server:")
    print("   python app.py")
    print()
    print("✅ Your backend will then use real Firebase database!")

if __name__ == "__main__":
    main()
