#!/usr/bin/env python3
"""
Test runner for AI Telemedicine Platform
Runs all tests and generates coverage reports
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main test runner"""
    print("🧪 AI Telemedicine Platform - Test Runner")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not running in a virtual environment")
        print("   Consider activating your virtual environment first")
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✅ pytest version: {pytest.__version__}")
    except ImportError:
        print("❌ pytest not found. Installing...")
        if not run_command("pip install pytest pytest-cov", "Installing pytest"):
            return False
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print("📁 Created logs directory")
    
    # Run basic tests
    if not run_command("python -m pytest tests/ -v", "Running basic tests"):
        print("❌ Basic tests failed")
        return False
    
    # Run tests with coverage
    if not run_command("python -m pytest tests/ --cov=. --cov-report=html --cov-report=term", "Running tests with coverage"):
        print("⚠️  Coverage report generation failed, but tests may have passed")
    
    # Run specific API tests
    if not run_command("python -m pytest tests/test_api.py -v", "Running API tests"):
        print("❌ API tests failed")
        return False
    
    # Test health endpoint manually
    print("\n🔄 Testing health endpoint...")
    try:
        import requests
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint is responding")
        else:
            print(f"⚠️  Health endpoint returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running - health endpoint test skipped")
    except ImportError:
        print("⚠️  requests library not found - health endpoint test skipped")
    except Exception as e:
        print(f"⚠️  Health endpoint test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test run completed!")
    print("\n📊 Coverage report generated in htmlcov/index.html")
    print("🔍 View detailed results above")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
