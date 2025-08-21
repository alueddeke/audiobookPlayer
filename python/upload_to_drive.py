#!/usr/bin/env python3
"""
Simple script to upload prepared audio files to Google Drive.
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_google_drive():
    """Authenticate with Google Drive API."""
    creds = None
    
    # Load existing credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Failed to refresh token: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists('../client_secret.json'):
                raise FileNotFoundError("Client secret file not found: ../client_secret.json")
            
            flow = InstalledAppFlow.from_client_secrets_file('../client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0, prompt='consent')
        
        # Save credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def find_or_create_audiobooks_folder(service):
    """Find or create the audiobooks folder in Google Drive."""
    try:
        # Search for audiobooks folder
        results = service.files().list(
            q="name='audiobooks' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        
        if files:
            folder_id = files[0]['id']
            logger.info(f"✅ Found existing audiobooks folder: {folder_id}")
            return folder_id
        else:
            # Create new folder
            folder_metadata = {
                'name': 'audiobooks',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"✅ Created new audiobooks folder: {folder_id}")
            return folder_id
            
    except Exception as e:
        logger.error(f"❌ Error finding/creating audiobooks folder: {e}")
        raise

def create_book_folder(service, parent_folder_id, book_title):
    """Create a folder for the book."""
    try:
        # Check if book folder already exists
        results = service.files().list(
            q=f"name='{book_title}' and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        
        if files:
            folder_id = files[0]['id']
            logger.info(f"✅ Found existing book folder: {folder_id}")
            return folder_id
        else:
            # Create new folder
            folder_metadata = {
                'name': book_title,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            
            folder = service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"✅ Created new book folder: {folder_id}")
            return folder_id
            
    except Exception as e:
        logger.error(f"❌ Error creating book folder: {e}")
        raise

def upload_file_to_drive(service, file_path, folder_id, filename=None):
    """Upload a file to Google Drive."""
    try:
        if not filename:
            filename = os.path.basename(file_path)
        
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = file.get('id')
        logger.info(f"✅ Uploaded {filename}: {file_id}")
        return file_id
        
    except Exception as e:
        logger.error(f"❌ Error uploading {file_path}: {e}")
        raise

def main():
    """Main upload function."""
    try:
        logger.info("🚀 Starting Google Drive upload")
        
        # Authenticate
        service = authenticate_google_drive()
        logger.info("✅ Successfully authenticated with Google Drive")
        
        # Find or create audiobooks folder
        audiobooks_folder_id = find_or_create_audiobooks_folder(service)
        
        # Create book folder
        book_title = "Well Of Ascension"
        book_folder_id = create_book_folder(service, audiobooks_folder_id, book_title)
        
        # Upload segment files
        segment_files = []
        for i in range(1, 27):
            filename = f"well_of_ascension_segment_{i:02d}.mp3"
            if os.path.exists(filename):
                segment_files.append(filename)
        
        logger.info(f"📁 Found {len(segment_files)} segment files to upload")
        
        # Upload segments
        uploaded_files = []
        for i, segment_file in enumerate(segment_files):
            logger.info(f"☁️ Uploading segment {i+1}/{len(segment_files)}: {segment_file}")
            file_id = upload_file_to_drive(service, segment_file, book_folder_id)
            uploaded_files.append(file_id)
        
        # Upload table of contents
        toc_file = "well_of_ascension_toc.json"
        if os.path.exists(toc_file):
            logger.info(f"📋 Uploading table of contents: {toc_file}")
            toc_id = upload_file_to_drive(service, toc_file, book_folder_id)
        
        logger.info("🎉 All files uploaded successfully!")
        logger.info(f"📊 Uploaded {len(uploaded_files)} segment files and 1 TOC file")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        return False

if __name__ == "__main__":
    main()
