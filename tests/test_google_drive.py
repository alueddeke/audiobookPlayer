#!/usr/bin/env python3
"""
Google Drive Integration Test Script
Tests the Google Drive API connectivity and file access for the AudioBook Player 2 project.
"""

import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Hardcoded file IDs from the Android app
AUDIO_FILE_IDS = [
    "1vS8tpbb7UMQ2zCYvnL-Cqahp8c20yOJj",
    "1iikHnzproRpzdXDyiDDb6hmWJazI0ejr", 
    "1YbfJA76FkR-cNVWfAmqHUnEdW_33w-DG",
    "1PJgoQK3II1Tr8R0ei5-S-iCBRuFmklnC",
    "1kl55x-lfpIq_PEGh59kXa80d05-y1tXr",
    "1pCY_AZqMPpQnODsLWJMHRKEY7Cmmy0J9",
    "1yK-KPOIw1fh3E7dboU1WomucX_f7dCvp",
    "1k_ADXeNKDJ9DL5pzXdo2J07J5nslLqcW"
]

def authenticate_google_drive():
    """Authenticate with Google Drive API."""
    creds = None
    
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check if client_secret.json exists
            client_secret_path = 'AndroidApp2/app/client_secret.json'
            if not os.path.exists(client_secret_path):
                print(f"❌ Error: {client_secret_path} not found!")
                print("Please ensure the client_secret.json file exists in the AndroidApp2/app/ directory.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def test_drive_connection(service):
    """Test basic Google Drive API connection."""
    try:
        # Try to get user info
        about = service.about().get(fields="user").execute()
        user = about.get('user', {})
        print(f"✅ Successfully connected to Google Drive")
        print(f"   User: {user.get('displayName', 'Unknown')} ({user.get('emailAddress', 'Unknown')})")
        return True
    except HttpError as error:
        print(f"❌ Failed to connect to Google Drive: {error}")
        return False

def test_file_access(service, file_id):
    """Test access to a specific file."""
    try:
        file = service.files().get(fileId=file_id, fields="id,name,mimeType,size").execute()
        print(f"✅ File accessible: {file.get('name', 'Unknown')}")
        print(f"   ID: {file.get('id')}")
        print(f"   Type: {file.get('mimeType', 'Unknown')}")
        print(f"   Size: {file.get('size', 'Unknown')} bytes")
        return True
    except HttpError as error:
        if error.resp.status == 404:
            print(f"❌ File not found: {file_id}")
        elif error.resp.status == 403:
            print(f"❌ Access denied to file: {file_id}")
        else:
            print(f"❌ Error accessing file {file_id}: {error}")
        return False

def test_audio_streaming_url(service, file_id):
    """Test if we can generate a streaming URL for the file."""
    try:
        # This simulates what the Android app does
        file = service.files().get(fileId=file_id, fields="id,name,mimeType").execute()
        streaming_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        print(f"✅ Streaming URL generated: {streaming_url}")
        return True
    except HttpError as error:
        print(f"❌ Failed to generate streaming URL for {file_id}: {error}")
        return False

def main():
    """Main test function."""
    print("🔍 Testing Google Drive Integration for AudioBook Player 2")
    print("=" * 60)
    
    # Step 1: Authenticate
    print("\n1. Authenticating with Google Drive...")
    creds = authenticate_google_drive()
    if not creds:
        print("❌ Authentication failed. Exiting.")
        return
    
    # Step 2: Build service
    try:
        service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Failed to build Drive service: {e}")
        return
    
    # Step 3: Test connection
    print("\n2. Testing Drive connection...")
    if not test_drive_connection(service):
        print("❌ Drive connection failed. Exiting.")
        return
    
    # Step 4: Test file access
    print("\n3. Testing file access...")
    accessible_files = 0
    for i, file_id in enumerate(AUDIO_FILE_IDS, 1):
        print(f"\n   Testing file {i}/{len(AUDIO_FILE_IDS)}: {file_id}")
        if test_file_access(service, file_id):
            accessible_files += 1
            test_audio_streaming_url(service, file_id)
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print(f"   Total files tested: {len(AUDIO_FILE_IDS)}")
    print(f"   Accessible files: {accessible_files}")
    print(f"   Inaccessible files: {len(AUDIO_FILE_IDS) - accessible_files}")
    
    if accessible_files == len(AUDIO_FILE_IDS):
        print("✅ All files are accessible! The Android app should work correctly.")
    elif accessible_files > 0:
        print("⚠️  Some files are accessible. The app may work partially.")
    else:
        print("❌ No files are accessible. The Android app will not work.")
        print("\n💡 Suggestions:")
        print("   - Check if you have access to the Google Drive account that owns these files")
        print("   - Verify the file IDs are correct")
        print("   - Consider uploading your own audio files and updating the file IDs in the code")

if __name__ == '__main__':
    main() 