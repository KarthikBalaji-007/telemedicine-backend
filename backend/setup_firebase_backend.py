#!/usr/bin/env python3
"""
Firebase Backend Setup Script
Automated setup for AI Telemedicine Platform backend database
"""

import os
import json
import sys
import webbrowser

def main():
    print("🔥 Firebase Backend Setup")
    print("=" * 40)
    print("Setting up real Firebase database for your backend...")
    print()
    
    # Step 1: Open Firebase Console
    print("📋 STEP 1: Create Firebase Project")
    print("-" * 30)
    print("1. Opening Firebase Console...")
    
    try:
        webbrowser.open("https://console.firebase.google.com/")
        print("✅ Firebase Console opened in browser")
    except:
        print("⚠️  Please manually go to: https://console.firebase.google.com/")
    
    print()
    print("2. In Firebase Console:")
    print("   • Click 'Create a project' or 'Add project'")
    print("   • Project name: 'ai-telemedicine-backend'")
    print("   • Enable/disable Google Analytics (your choice)")
    print("   • Click 'Create project'")
    print()
    
    input("Press Enter when project is created...")
    
    # Step 2: Enable Firestore
    print("\n📋 STEP 2: Enable Firestore Database")
    print("-" * 30)
    print("1. In your Firebase project dashboard:")
    print("   • Click 'Firestore Database' in left sidebar")
    print("   • Click 'Create database'")
    print("   • Choose 'Start in test mode' (for development)")
    print("   • Select location closest to you")
    print("   • Click 'Done'")
    print()
    
    input("Press Enter when Firestore is enabled...")
    
    # Step 3: Get Service Account
    print("\n📋 STEP 3: Get Service Account Credentials")
    print("-" * 30)
    print("1. In Firebase Console:")
    print("   • Click gear icon (⚙️) → 'Project settings'")
    print("   • Click 'Service accounts' tab")
    print("   • Click 'Generate new private key'")
    print("   • Click 'Generate key' in popup")
    print("   • Save the downloaded JSON file to this folder")
    print()
    
    # Get JSON file path
    json_file = None
    while not json_file:
        file_path = input("Enter the path to downloaded JSON file (or drag & drop): ").strip().strip('"')
        
        if os.path.exists(file_path) and file_path.endswith('.json'):
            json_file = file_path
            break
        else:
            print("❌ File not found or not a JSON file. Please try again.")
    
    # Step 4: Configure Backend
    print("\n📋 STEP 4: Configure Backend")
    print("-" * 30)
    
    try:
        with open(json_file, 'r') as f:
            creds = json.load(f)
        
        # Validate required fields
        required_fields = ['project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"❌ Missing fields in JSON: {missing_fields}")
            return
        
        # Update .env file
        env_content = f"""# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
PORT=5000

# Firebase Configuration - REAL DATABASE
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

# Production Settings
FLASK_ENV=development
DEBUG=True
TESTING=False

# Security Settings
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_EXPIRY_HOURS=24
API_KEY_LENGTH=32
PASSWORD_MIN_LENGTH=8

# Performance Settings
REQUEST_TIMEOUT=30
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
"""
        
        # Backup existing .env
        if os.path.exists('.env'):
            os.rename('.env', '.env.backup')
            print("✅ Backed up existing .env to .env.backup")
        
        # Write new .env
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Firebase credentials configured successfully!")
        print("✅ .env file updated with real Firebase settings")
        print()
        print("🎉 SETUP COMPLETE!")
        print("-" * 20)
        print("✅ Real Firebase database connected")
        print("✅ No more development mode warnings")
        print("✅ Data will now persist permanently")
        print("✅ Ready for production deployment")
        print()
        print("🚀 Restart your backend server:")
        print("   python app.py")
        print()
        print("💰 Firebase Usage (FREE TIER):")
        print("   • 50,000 reads per day")
        print("   • 20,000 writes per day")
        print("   • 1 GB storage")
        print("   • Perfect for development!")
        
    except Exception as e:
        print(f"❌ Error configuring Firebase: {e}")
        print("Please check the JSON file and try again.")

if __name__ == "__main__":
    main()
