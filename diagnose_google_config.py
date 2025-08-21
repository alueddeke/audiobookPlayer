#!/usr/bin/env python3
"""
Google Cloud Configuration Diagnostic Tool
Helps identify issues with Google OAuth setup.
"""

import json
import os
import sys

def check_client_secret():
    """Check if client_secret.json exists and is valid."""
    print("🔍 Checking client_secret.json...")
    
    client_secret_path = "AndroidApp2/app/client_secret.json"
    
    if not os.path.exists(client_secret_path):
        print("❌ client_secret.json not found!")
        print(f"   Expected location: {client_secret_path}")
        return False
    
    try:
        with open(client_secret_path, 'r') as f:
            config = json.load(f)
        
        if 'installed' not in config:
            print("❌ Invalid client_secret.json format!")
            print("   Expected 'installed' key not found")
            return False
        
        client_id = config['installed'].get('client_id', '')
        project_id = config['installed'].get('project_id', '')
        
        print(f"✅ client_secret.json found")
        print(f"   Client ID: {client_id[:20]}...")
        print(f"   Project ID: {project_id}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in client_secret.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading client_secret.json: {e}")
        return False

def check_required_files():
    """Check if all required files exist."""
    print("\n📁 Checking required files...")
    
    required_files = [
        "AndroidApp2/app/client_secret.json",
        "audiobook_scraper.py",
        "test_google_drive.py",
        "requirements.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def check_python_dependencies():
    """Check if required Python packages are installed."""
    print("\n🐍 Checking Python dependencies...")
    
    required_packages = [
        'google.auth',
        'google_auth_oauthlib',
        'googleapiclient',
        'requests',
        'beautifulsoup4',
        'pydub'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def provide_setup_instructions():
    """Provide setup instructions based on findings."""
    print("\n" + "="*60)
    print("🔧 SETUP INSTRUCTIONS")
    print("="*60)
    
    print("""
1. GO TO GOOGLE CLOUD CONSOLE:
   https://console.cloud.google.com/
   
2. SELECT YOUR PROJECT:
   audiobookplayer-436611
   
3. ENABLE APIS:
   - Go to APIs & Services > Library
   - Search for and enable:
     * Google Drive API
     * Google+ API (if available)
   
4. CONFIGURE OAUTH CONSENT SCREEN:
   - Go to APIs & Services > OAuth consent screen
   - Choose "External" user type
   - Fill in app details
   - Add scopes:
     * https://www.googleapis.com/auth/drive.readonly
     * https://www.googleapis.com/auth/drive.file
   - Add test users (your email)
   
5. CONFIGURE OAUTH CLIENT:
   - Go to APIs & Services > Credentials
   - Edit your OAuth 2.0 client
   - Add redirect URIs:
     * http://localhost:8080/
     * http://localhost:8090/
     * http://localhost:55571/
     * http://localhost:55572/
     * http://localhost:55573/
     * http://localhost:55574/
     * http://localhost:55575/
   
6. DOWNLOAD UPDATED CREDENTIALS:
   - Download new client_secret.json
   - Replace AndroidApp2/app/client_secret.json
   
7. TEST AGAIN:
   python test_google_drive.py
""")

def main():
    print("🔍 Google Cloud Configuration Diagnostic")
    print("="*50)
    
    # Run checks
    client_secret_ok = check_client_secret()
    files_ok = check_required_files()
    deps_ok = check_python_dependencies()
    
    print("\n" + "="*50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*50)
    
    if client_secret_ok and files_ok and deps_ok:
        print("✅ All basic checks passed!")
        print("💡 The issue is likely in Google Cloud Console configuration.")
        print("   Follow the setup instructions below.")
    else:
        print("❌ Some issues found. Fix them before proceeding.")
    
    provide_setup_instructions()

if __name__ == "__main__":
    main()
