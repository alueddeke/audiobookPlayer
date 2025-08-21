# AudioBook Player - Complete Audiobook Management System

A comprehensive audiobook management system that scrapes audiobooks from web sources, processes them into optimal segments, uploads to Google Drive, and provides a feature-rich Android player with position memory and speed control.

## 🎯 Overview

This system provides a complete workflow from audiobook discovery to playback:

1. **Web Scraping**: Automatically finds and downloads audiobook files from supported websites
2. **Smart Processing**: Analyzes files and either combines small segments or uses files directly based on size/duration
3. **Google Drive Integration**: Uploads processed audiobooks to organized folder structure
4. **Android Player**: Feature-rich mobile app with position memory, speed control, and library management

## 🚀 Features

### Python Scraper & Processor
- **Intelligent URL Scraping**: Handles pagination and multiple audio file formats
- **Smart File Analysis**: Automatically determines if files need combining based on size/duration
- **Optimized Processing**: Creates 60-120 minute segments with 150MB size limits
- **Google Drive Upload**: Batch uploads with progress tracking and organized folder structure
- **Table of Contents**: Generates metadata files for each audiobook

### Android App
- **Google Sign-In**: Secure authentication with Google Drive access
- **Dynamic Library**: Automatically discovers and loads audiobooks from Drive
- **Position Memory**: Remembers exact playback position across app restarts
- **Precise Speed Control**: 0.05x increments (1.15x, 1.20x, 1.25x, etc.)
- **Segment Navigation**: Easy previous/next segment controls
- **Error Recovery**: Automatic retry and skip functionality for failed segments
- **Offline Capable**: Works independently once installed

## 📁 Project Structure

```
AudioBookPlayer2/
├── audiobook_scraper.py          # Main scraper and processor
├── upload_to_drive.py            # Standalone upload utility
├── requirements.txt              # Python dependencies
├── client_secret.json            # Google OAuth credentials (Desktop)
├── token.json                    # OAuth tokens (auto-generated)
├── audiobookplayer.keystore      # Android app signing key
├── AndroidApp2/                  # Android application
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/com/antonilueddeke/androidapp2/
│   │   │   │   └── MainActivity.kt    # Main app logic
│   │   │   ├── res/layout/
│   │   │   │   └── activity_main.xml  # UI layout
│   │   │   └── AndroidManifest.xml    # App configuration
│   │   ├── client_secret.json         # Google OAuth credentials (Android)
│   │   └── build.gradle.kts           # Build configuration
│   └── build.gradle.kts
├── GOOGLE_SETUP_GUIDE.md         # OAuth configuration guide
├── diagnose_google_config.py     # OAuth troubleshooting tool
└── README.md                     # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Android Studio / Android SDK
- Google Cloud Project with OAuth configured
- Google Drive account

### Python Dependencies
```bash
pip install -r requirements.txt
```

### Google OAuth Setup
1. **Create Google Cloud Project** (if not exists)
2. **Enable APIs**: Google Drive API, Google+ API
3. **Configure OAuth Consent Screen**:
   - User Type: External
   - Scopes: `drive.readonly`, `drive.file`
   - Test Users: Add your email
4. **Create OAuth Clients**:
   - **Desktop Application**: For Python scraper
   - **Android Application**: For Android app
5. **Download credentials**:
   - Desktop: `client_secret.json` (for Python)
   - Android: `client_secret.json` (for Android app)

### Android App Setup
1. **Configure signing** (already done):
   ```bash
   # Keystore created with:
   keytool -genkey -v -keystore audiobookplayer.keystore -alias audiobookplayer -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Add SHA-1 fingerprints** to Google Cloud Console:
   - **Release SHA-1**: `E7:DF:E9:5D:81:77:F0:74:04:DB:05:7C:F9:9E:5A:5E:B1:84:F3:03`
   - **Package name**: `com.antonilueddeke.androidapp2`

3. **Build and install**:
   ```bash
   cd AndroidApp2
   ./gradlew assembleRelease
   # APK: app/build/outputs/apk/release/app-release.apk
   ```

## 📖 Usage

### 1. Scraping and Processing Audiobooks

#### Basic Usage
```bash
python audiobook_scraper.py "https://cafeaudiobooks.net/book-url/"
```

#### Dry Run (Test Only)
```bash
python audiobook_scraper.py "https://cafeaudiobooks.net/book-url/" --dry-run
```

#### Standalone Upload (if files already prepared)
```bash
python upload_to_drive.py
```

### 2. Android App Usage

#### Installation
1. **Install APK**: `AudioBookPlayer-Signed.apk`
2. **Sign in with Google**: Grant Drive access permissions
3. **Refresh Library**: Tap "Refresh Library" button
4. **Select Book**: Tap book title to select
5. **Start Playing**: Tap "Play" button

#### Features
- **Speed Control**: Use slider for 0.05x increments
- **Position Memory**: App remembers position across restarts
- **Segment Navigation**: Previous/Next buttons
- **Error Recovery**: Automatic retry and skip on failures

## 🔄 Complete Workflow

### Step 1: Audiobook Discovery
```bash
# Scrape audiobook URLs from website
python audiobook_scraper.py "https://cafeaudiobooks.net/brandon-sanderson-the-well-of-ascension-audiobook/"
```

**What happens:**
- Scrapes all pages for audio URLs
- Downloads 26 audio files (~72 minutes each)
- Analyzes file sizes and durations
- Determines no combining needed (files already optimal)

### Step 2: Processing
**Smart Analysis:**
- Files: ~72 minutes, ~364MB each
- Decision: Use files directly (no combining)
- Creates properly named segments
- Generates table of contents

### Step 3: Google Drive Upload
**Folder Structure Created:**
```
audiobooks/
└── Well Of Ascension/
    ├── well_of_ascension_segment_01.mp3
    ├── well_of_ascension_segment_02.mp3
    ├── ...
    ├── well_of_ascension_segment_26.mp3
    └── well_of_ascension_toc.json
```

### Step 4: Android Playback
1. **Sign in** with Google account
2. **Refresh library** to discover books
3. **Select book** by tapping title
4. **Start playback** with full controls

## 🔧 Technical Details

### Python Scraper Architecture
- **URL Scraping**: Handles pagination, multiple file formats
- **File Analysis**: Automatic size/duration assessment
- **Smart Processing**: Combines only when necessary
- **Drive Integration**: OAuth2 authentication, batch uploads
- **Error Handling**: Retry logic, failure logging

### Android App Architecture
- **Google Sign-In**: OAuth2 with Drive scope
- **ExoPlayer**: Audio playback engine
- **SharedPreferences**: Position and settings persistence
- **Coroutines**: Asynchronous operations
- **Material Design**: Modern UI components

### Key Data Structures
```kotlin
data class BookInfo(
    val id: String,
    val name: String,
    val segments: List<SegmentInfo>
)

data class SegmentInfo(
    val fileId: String,
    val name: String,
    val duration: Long,
    val size: Long
)
```

### Persistence
- **Last Book ID**: `KEY_LAST_BOOK_ID`
- **Last Segment**: `KEY_LAST_SEGMENT_INDEX`
- **Last Position**: `KEY_LAST_POSITION`
- **Last Speed**: `KEY_LAST_SPEED`

## 🐛 Troubleshooting

### Common Issues

#### Google Sign-In Error 10
**Cause**: SHA-1 fingerprint mismatch
**Solution**: Add release SHA-1 to Google Cloud Console OAuth client

#### "Package appears to be invalid"
**Cause**: Unsigned APK
**Solution**: Use `AudioBookPlayer-Signed.apk` (properly signed)

#### "No books found"
**Cause**: Library not refreshed or Drive access issues
**Solution**: 
1. Ensure signed in with Google
2. Tap "Refresh Library"
3. Check Drive permissions

#### Scraper Analysis Issues
**Cause**: Files already optimal size
**Solution**: This is normal - files are used directly without combining

### Debug Tools
- **OAuth Diagnosis**: `python diagnose_google_config.py`
- **Drive Test**: `python test_google_drive.py`
- **Analysis Test**: `python test_analysis.py`

## 📱 App Features Deep Dive

### Position Memory System
- **Saves every 5 seconds** during playback
- **Persists across app restarts**
- **Auto-resumes** at exact position
- **Handles segment boundaries**

### Speed Control
- **Range**: 0.5x to 2.0x
- **Increments**: 0.05x (1.15x, 1.20x, 1.25x)
- **Persistent**: Remembers last used speed
- **Real-time**: Changes apply immediately

### Error Recovery
- **Automatic retry**: Failed segments retry once
- **Skip on failure**: Moves to next segment if retry fails
- **User notification**: Clear error messages
- **Graceful degradation**: Continues playback

### Library Management
- **Dynamic discovery**: Scans Drive for new books
- **Automatic updates**: Refresh button updates library
- **Book selection**: Tap to select and prepare
- **Segment navigation**: Easy previous/next controls

## 🔒 Security & Permissions

### Required Permissions
- **Internet**: Drive access and audio streaming
- **Storage**: Local file caching
- **Google Sign-In**: OAuth2 authentication

### OAuth Scopes
- **Drive Read-Only**: `https://www.googleapis.com/auth/drive.readonly`
- **Drive File**: `https://www.googleapis.com/auth/drive.file`

### Data Privacy
- **No data collection**: App doesn't send data to external servers
- **Local storage**: All preferences stored locally
- **Google Drive**: Only accesses user's own Drive files

## 🚀 Future Enhancements

### Potential Improvements
- **Multiple source support**: Add more audiobook websites
- **Offline caching**: Download segments for offline use
- **Playlist support**: Create custom playlists
- **Cloud sync**: Sync preferences across devices
- **Advanced filtering**: Search and filter library
- **Background playback**: Continue playing when app minimized

### Technical Improvements
- **Modern ExoPlayer**: Update to latest version
- **Jetpack Compose**: Modern UI framework
- **Dependency injection**: Better architecture
- **Unit tests**: Comprehensive testing
- **CI/CD**: Automated builds and deployment

## 📄 License

This project is for personal use and educational purposes. Please respect copyright laws and only download content you have permission to access.

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome. The codebase is designed to be extensible and well-documented for future development.

---

**Last Updated**: August 21, 2025  
**Status**: MVP Complete - Fully Functional  
**Version**: 1.0 (Signed Release) 