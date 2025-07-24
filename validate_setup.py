#!/usr/bin/env python3
"""
Setup Validation Script for Perplexity AI GUI Client
Enhanced Edition v2.0

This script validates the complete setup including API connectivity.
"""

import sys
import os
import requests
import json

def check_api_key():
    """Check if API key is valid by making a test request."""
    print("🔑 Testing API key...")
    
    # Try to read API key from file
    api_key = None
    try:
        with open("pplx_api_key.txt", "r") as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        api_key = os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        print("  ⚠️  No API key found")
        return False
    
    # Test the API key
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sonar",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 1
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("  ✅ API key is valid and working")
            return True
        elif response.status_code == 401:
            print("  ❌ API key is invalid")
            return False
        else:
            print(f"  ⚠️  API returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Network error testing API: {e}")
        return False

def check_files():
    """Check if all required files exist."""
    print("\n📁 Checking required files...")
    
    required_files = [
        "App1.py",
        "config.py", 
        "launch.py",
        "requirements.txt",
        "test_app.py"
    ]
    
    optional_files = [
        "pplx_api_key.txt",
        "settings.json",
        "launch.bat"
    ]
    
    all_good = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (required)")
            all_good = False
    
    for file in optional_files:
        if os.path.exists(file):
            print(f"  ✅ {file} (optional)")
        else:
            print(f"  ⚠️  {file} (optional - missing)")
    
    return all_good

def check_directories():
    """Check and create necessary directories."""
    print("\n📂 Checking directories...")
    
    directories = [
        "auto_saves",
        "exports", 
        "logs"
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/")
        else:
            try:
                os.makedirs(directory)
                print(f"  ✅ {directory}/ (created)")
            except OSError as e:
                print(f"  ❌ Failed to create {directory}/: {e}")

def main():
    """Run all validation checks."""
    print("🔍 Perplexity AI GUI Client - Setup Validation")
    print("=" * 55)
    
    # Run all checks
    files_ok = check_files()
    check_directories()
    api_ok = check_api_key()
    
    print("\n" + "=" * 55)
    
    if files_ok and api_ok:
        print("🎉 Setup validation completed successfully!")
        print("   Your Perplexity AI GUI Client is ready to use.")
        return 0
    elif files_ok:
        print("⚠️  Setup mostly complete, but API key needs attention.")
        print("   You can still run the application and set the API key in the GUI.")
        return 0
    else:
        print("❌ Setup validation failed.")
        print("   Please check the errors above before running the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main())