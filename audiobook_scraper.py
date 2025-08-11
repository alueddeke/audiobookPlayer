#!/usr/bin/env python3
"""
Audiobook Scraper and Processor
Downloads audiobook files from web pages, combines them into segments, and uploads to Google Drive.
"""

import requests
import os
import re
import json
import time
from urllib.parse import urljoin, unquote
from bs4 import BeautifulSoup
from pydub import AudioSegment
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import argparse
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('audiobook_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class AudiobookScraper:
    def __init__(self, client_secret_path='AndroidApp2/app/client_secret.json'):
        self.client_secret_path = client_secret_path
        self.drive_service = None
        self.failed_downloads = []
        self.download_stats = {
            'total_files': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_size': 0,
            'start_time': None,
            'end_time': None
        }
        
    def authenticate_google_drive(self):
        """Authenticate with Google Drive API."""
        creds = None
        
        # Load existing credentials
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.client_secret_path):
                    raise FileNotFoundError(f"Client secret file not found: {self.client_secret_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.drive_service = build('drive', 'v3', credentials=creds)
        logger.info("✅ Successfully authenticated with Google Drive")
        
    def scrape_audio_urls(self, url):
        """Scrape audio file URLs from a web page."""
        logger.info(f"🔍 Scraping audio URLs from: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all audio elements
            audio_elements = soup.find_all('audio')
            audio_urls = []
            
            for audio in audio_elements:
                src = audio.get('src')
                if src and 'ipaudio.club' in src:
                    audio_urls.append(src)
                    logger.info(f"Found audio URL: {src}")
            
            if not audio_urls:
                logger.warning("No audio URLs found on the page")
                return [], None
            
            # Extract book title from first URL
            if audio_urls:
                first_url = audio_urls[0]
                # Extract book title from URL path
                match = re.search(r'/([^/]+)/\d+\.mp3', first_url)
                if match:
                    book_title = unquote(match.group(1))
                    logger.info(f"📚 Detected book title: {book_title}")
                else:
                    book_title = "Unknown Book"
            
            return audio_urls, book_title
            
        except Exception as e:
            logger.error(f"❌ Error scraping URLs: {e}")
            return [], None
    
    def download_file(self, url, filename, max_retries=3):
        """Download a file with retry logic."""
        for attempt in range(max_retries):
            try:
                logger.info(f"📥 Downloading {filename} (attempt {attempt + 1}/{max_retries})")
                response = requests.get(url, timeout=60, stream=True)
                response.raise_for_status()
                
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(filename)
                self.download_stats['total_size'] += file_size
                self.download_stats['successful_downloads'] += 1
                logger.info(f"✅ Downloaded {filename} ({file_size / 1024 / 1024:.1f} MB)")
                return True
                
            except Exception as e:
                logger.warning(f"⚠️ Download attempt {attempt + 1} failed for {filename}: {e}")
                if attempt == max_retries - 1:
                    self.failed_downloads.append({
                        'url': url,
                        'filename': filename,
                        'error': str(e)
                    })
                    self.download_stats['failed_downloads'] += 1
                    logger.error(f"❌ Failed to download {filename} after {max_retries} attempts")
                    return False
                time.sleep(2)  # Wait before retry
    
    def get_audio_duration(self, filepath):
        """Get audio duration using pydub."""
        try:
            audio = AudioSegment.from_mp3(filepath)
            return len(audio) / 1000  # Convert to seconds
        except Exception as e:
            logger.warning(f"Could not get duration for {filepath}: {e}")
            return None
    
    def combine_audio_files(self, input_files, output_file, target_duration_minutes=60, max_size_mb=150):
        """Combine audio files into segments based on duration and size."""
        logger.info(f"🔧 Combining {len(input_files)} files into segments")
        
        combined = AudioSegment.empty()
        current_segment = 1
        segment_files = []
        segment_info = []
        
        for i, file in enumerate(input_files):
            try:
                logger.info(f"Adding {file} to segment {current_segment}")
                audio = AudioSegment.from_mp3(file)
                combined += audio
                
                # Check if we should create a new segment
                duration_minutes = len(combined) / 1000 / 60
                size_mb = len(combined.raw_data) / 1024 / 1024
                
                should_split = (
                    duration_minutes >= target_duration_minutes or 
                    size_mb >= max_size_mb or 
                    i == len(input_files) - 1  # Last file
                )
                
                if should_split:
                    segment_filename = f"{output_file}_segment_{current_segment:02d}.mp3"
                    logger.info(f"Creating segment {current_segment}: {segment_filename}")
                    
                    # Export with optimized settings
                    combined.export(
                        segment_filename, 
                        format="mp3", 
                        bitrate="128k",
                        parameters=["-q:a", "2"]  # VBR quality setting
                    )
                    
                    segment_files.append(segment_filename)
                    
                    # Record segment info
                    final_duration = len(combined) / 1000 / 60
                    final_size = os.path.getsize(segment_filename) / 1024 / 1024
                    
                    segment_info.append({
                        "segment": current_segment,
                        "file": segment_filename,
                        "duration_minutes": round(final_duration, 2),
                        "size_mb": round(final_size, 2),
                        "original_files": [f.split('_')[-1].replace('.mp3', '') for f in input_files[max(0, i-len(combined)/len(audio)):i+1]]
                    })
                    
                    # Start new segment
                    combined = AudioSegment.empty()
                    current_segment += 1
                    
            except Exception as e:
                logger.error(f"❌ Error processing {file}: {e}")
                self.failed_downloads.append({
                    'url': 'N/A',
                    'filename': file,
                    'error': f'Processing error: {e}'
                })
        
        return segment_files, segment_info
    
    def create_table_of_contents(self, book_title, segment_info):
        """Create table of contents JSON file."""
        toc = {
            "book_title": book_title,
            "created_date": datetime.now().isoformat(),
            "total_segments": len(segment_info),
            "segments": segment_info
        }
        
        toc_filename = f"{book_title.lower().replace(' ', '_')}_toc.json"
        with open(toc_filename, 'w') as f:
            json.dump(toc, f, indent=2)
        
        logger.info(f"📋 Created table of contents: {toc_filename}")
        return toc_filename
    
    def find_or_create_audiobooks_folder(self):
        """Find or create the audiobooks folder in Google Drive."""
        try:
            # Search for audiobooks folder
            results = self.drive_service.files().list(
                q="name='audiobooks' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            if results['files']:
                folder_id = results['files'][0]['id']
                logger.info("📁 Found existing audiobooks folder")
                return folder_id
            else:
                # Create new folder
                folder_metadata = {
                    'name': 'audiobooks',
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.drive_service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                logger.info("📁 Created new audiobooks folder")
                return folder['id']
                
        except Exception as e:
            logger.error(f"❌ Error with audiobooks folder: {e}")
            raise
    
    def create_book_folder(self, audiobooks_folder_id, book_title):
        """Create a folder for the specific book."""
        try:
            # Sanitize book title for folder name
            safe_title = re.sub(r'[^\w\s-]', '', book_title).strip()
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            
            folder_metadata = {
                'name': safe_title,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [audiobooks_folder_id]
            }
            
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            logger.info(f"📁 Created book folder: {safe_title}")
            return folder['id']
            
        except Exception as e:
            logger.error(f"❌ Error creating book folder: {e}")
            raise
    
    def upload_file_to_drive(self, file_path, folder_id, filename=None):
        """Upload a file to Google Drive."""
        try:
            if filename is None:
                filename = os.path.basename(file_path)
            
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, size'
            ).execute()
            
            size_mb = int(file.get('size', 0)) / 1024 / 1024
            logger.info(f"☁️ Uploaded {filename} ({size_mb:.1f} MB)")
            return file['id']
            
        except Exception as e:
            logger.error(f"❌ Error uploading {file_path}: {e}")
            raise
    
    def process_audiobook(self, url, dry_run=False):
        """Main processing function."""
        self.download_stats['start_time'] = datetime.now()
        logger.info("🚀 Starting audiobook processing")
        
        try:
            # Step 1: Scrape audio URLs
            audio_urls, book_title = self.scrape_audio_urls(url)
            if not audio_urls:
                logger.error("❌ No audio URLs found")
                return False
            
            if dry_run:
                logger.info(f"🔍 DRY RUN: Found {len(audio_urls)} audio files for '{book_title}'")
                return True
            
            # Step 2: Download files in batches
            temp_dir = f"temp_{book_title.lower().replace(' ', '_')}"
            os.makedirs(temp_dir, exist_ok=True)
            
            downloaded_files = []
            batch_size = 10
            
            for i in range(0, len(audio_urls), batch_size):
                batch_urls = audio_urls[i:i+batch_size]
                logger.info(f"📦 Processing batch {i//batch_size + 1}/{(len(audio_urls)-1)//batch_size + 1}")
                
                for j, audio_url in enumerate(batch_urls):
                    filename = f"audio_{i+j+1:02d}.mp3"
                    filepath = os.path.join(temp_dir, filename)
                    
                    if self.download_file(audio_url, filepath):
                        downloaded_files.append(filepath)
                    
                    # Progress update
                    progress = (i + j + 1) / len(audio_urls) * 100
                    logger.info(f"📊 Progress: {progress:.1f}% ({i+j+1}/{len(audio_urls)})")
            
            self.download_stats['total_files'] = len(audio_urls)
            
            # Step 3: Combine files into segments
            if downloaded_files:
                output_base = book_title.lower().replace(' ', '_')
                segment_files, segment_info = self.combine_audio_files(
                    downloaded_files, 
                    output_base,
                    target_duration_minutes=60,
                    max_size_mb=150
                )
                
                # Step 4: Create table of contents
                toc_file = self.create_table_of_contents(book_title, segment_info)
                
                # Step 5: Upload to Google Drive
                if self.drive_service:
                    logger.info("☁️ Starting Google Drive upload")
                    
                    # Find or create audiobooks folder
                    audiobooks_folder_id = self.find_or_create_audiobooks_folder()
                    
                    # Create book folder
                    book_folder_id = self.create_book_folder(audiobooks_folder_id, book_title)
                    
                    # Upload segments
                    uploaded_files = []
                    for i, segment_file in enumerate(segment_files):
                        logger.info(f"☁️ Uploading segment {i+1}/{len(segment_files)}")
                        file_id = self.upload_file_to_drive(segment_file, book_folder_id)
                        uploaded_files.append(file_id)
                    
                    # Upload table of contents
                    toc_id = self.upload_file_to_drive(toc_file, book_folder_id)
                    
                    logger.info("✅ All files uploaded successfully")
                
                # Step 6: Cleanup
                logger.info("🧹 Cleaning up temporary files")
                for file in downloaded_files:
                    os.remove(file)
                os.rmdir(temp_dir)
                
                # Step 7: Generate summary
                self.download_stats['end_time'] = datetime.now()
                self.generate_summary()
                
                return True
            else:
                logger.error("❌ No files were downloaded successfully")
                return False
                
        except Exception as e:
            logger.error(f"❌ Processing failed: {e}")
            return False
    
    def generate_summary(self):
        """Generate processing summary."""
        duration = self.download_stats['end_time'] - self.download_stats['start_time']
        
        logger.info("=" * 60)
        logger.info("📊 PROCESSING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total files found: {self.download_stats['total_files']}")
        logger.info(f"Successful downloads: {self.download_stats['successful_downloads']}")
        logger.info(f"Failed downloads: {self.download_stats['failed_downloads']}")
        logger.info(f"Total size downloaded: {self.download_stats['total_size'] / 1024 / 1024:.1f} MB")
        logger.info(f"Processing time: {duration}")
        
        if self.failed_downloads:
            logger.info("\n❌ FAILED DOWNLOADS:")
            with open('failed_downloads.txt', 'w') as f:
                f.write(f"Audiobook Scraper - Failed Downloads Report\n")
                f.write(f"Generated: {datetime.now()}\n\n")
                
                for failure in self.failed_downloads:
                    error_msg = f"File: {failure['filename']}\nURL: {failure['url']}\nError: {failure['error']}\n"
                    logger.info(error_msg)
                    f.write(error_msg + "\n")
            
            logger.info("📝 Failed downloads logged to 'failed_downloads.txt'")
        
        logger.info("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Audiobook Scraper and Processor")
    parser.add_argument("url", help="URL of the audiobook page")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be downloaded without actually doing it")
    parser.add_argument("--client-secret", default="AndroidApp2/app/client_secret.json", 
                       help="Path to Google OAuth client secret file")
    
    args = parser.parse_args()
    
    scraper = AudiobookScraper(args.client_secret)
    
    if not args.dry_run:
        scraper.authenticate_google_drive()
    
    success = scraper.process_audiobook(args.url, dry_run=args.dry_run)
    
    if success:
        logger.info("🎉 Processing completed successfully!")
    else:
        logger.error("💥 Processing failed!")
        exit(1)

if __name__ == "__main__":
    main() 