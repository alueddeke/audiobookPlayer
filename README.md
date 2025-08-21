# 🎧 AudioBookPlayer2 - Complete Audiobook Management System

A comprehensive audiobook management system that scrapes audio files from websites, processes them into optimal segments, uploads to Google Drive, and provides a feature-rich Android player with position memory and speed control.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Technical Architecture](#technical-architecture)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## 🎯 Overview

This project provides a complete workflow for audiobook management:

1. **URL Scraping**: Paste a URL to scrape MP3 files (20-70 files per book)
2. **Audio Processing**: Combine files into 60-120 minute segments (max 150MB)
3. **Google Drive Upload**: Upload to organized folder structure with TOC
4. **Android Player**: Feature-rich mobile app with position memory

## 📁 Project Structure

```
AudioBookPlayer2/
├── python/                    # Core Python workflow
│   ├── audiobook_scraper.py   # Main scraper & processor
│   ├── upload_to_drive.py     # Google Drive upload utility
│   ├── diagnose_google_config.py # OAuth diagnostics
│   ├── combine_existing.py    # Audio combining utility
│   ├── prepare_for_upload.py  # File preparation utility
│   ├── audiobook_scraper.log  # Processing logs
│   └── requirements.txt       # Python dependencies
├── mobile/                    # Android application
│   └── Haven/                 # "Haven" audiobook player
│       ├── app/
│       │   ├── src/main/java/com/antonilueddeke/androidapp2/
│       │   │   └── MainActivity.kt
│       │   ├── src/main/res/layout/
│       │   │   └── activity_main.xml
│       │   └── build.gradle.kts
│       └── gradle/
├── tests/                     # Test files
│   ├── test_integrated_workflow.py
│   ├── test_analysis.py
│   └── test_google_drive.py
├── docs/                      # Documentation
│   └── GOOGLE_SETUP_GUIDE.md
├── client_secret.json         # Google OAuth credentials
├── audiobookplayer.keystore   # Android app signing
├── token.json                 # OAuth tokens (auto-generated)
├── Haven-Signed.apk           # Signed Android APK
├── README.md                  # This file
└── .gitignore
```

## ✨ Features

### 🔍 Python Scraper (`python/audiobook_scraper.py`)
- **Smart URL Scraping**: Handles pagination automatically
- **Audio Analysis**: Analyzes file sizes/durations to optimize processing
- **Intelligent Combining**: Skips combining if files are already optimal size
- **Google Drive Integration**: Direct upload with progress tracking
- **Table of Contents**: Generates TOC for each book folder
- **Error Handling**: Comprehensive logging and retry logic

### 📱 Android App ("Haven")
- **Google Drive Integration**: Direct access to audiobooks folder
- **Position Memory**: Remembers exact position across app restarts
- **Speed Control**: 0.05x increments (1.3x, 1.35x, 1.4x, etc.)
- **Library Refresh**: Scan for new books on Drive
- **Error Recovery**: Automatic retry and skip on failures
- **Modern UI**: Material Design with intuitive controls

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Android Studio (for app development)
- Google Cloud Project with OAuth configured

### 1. Clone and Setup
```bash
git clone <repository-url>
cd AudioBookPlayer2
```

### 2. Python Dependencies
```bash
cd python
pip install -r requirements.txt
```

### 3. Google OAuth Setup
1. Follow the detailed guide in `docs/GOOGLE_SETUP_GUIDE.md`
2. Download `client_secret.json` to the project root
3. Run diagnostics: `python python/diagnose_google_config.py`

### 4. Android App Setup
```bash
cd mobile/Haven
./gradlew assembleRelease
```

## 📖 Usage

### Complete Workflow

#### 1. Scrape and Process Audiobook
```bash
cd python
python audiobook_scraper.py "https://cafeaudiobooks.net/book-url/"
```

**What happens:**
- Scrapes all pages for MP3 files
- Downloads files with retry logic
- Analyzes file sizes/durations
- Combines files if needed (or uses originals if already optimal)
- Uploads to Google Drive: `audiobooks/[book_name]/`
- Creates table of contents

#### 2. Install Android App
```bash
# Transfer Haven-Signed.apk to your Android device
# Or install via ADB:
adb install Haven-Signed.apk
```

#### 3. Use Android App
1. Open "Haven" app
2. Sign in with Google account
3. Tap "Refresh Library" to scan Drive
4. Tap book title to start playing
5. Use speed controls and position memory

### Individual Components

#### Audio Analysis Only
```bash
cd python
python audiobook_scraper.py "URL" --analyze-only
```

#### Upload Existing Files
```bash
cd python
python upload_to_drive.py
```

#### Test Google Drive Access
```bash
cd tests
python test_google_drive.py
```

## 🏗️ Technical Architecture

### Python Workflow
```
URL Input → Scrape Pages → Download Files → Analyze → Process → Upload → TOC
```

**Key Components:**
- `scrape_audio_urls()`: Handles pagination, extracts book title
- `analyze_audio_files()`: Determines if combining is needed
- `combine_audio_files()`: Creates optimal segments
- `upload_to_drive()`: Batch upload with progress

### Android Architecture
```
Google Sign-In → Drive API → File Discovery → ExoPlayer → SharedPreferences
```

**Key Features:**
- OAuth 2.0 authentication
- Google Drive API integration
- ExoPlayer for streaming
- SharedPreferences for persistence

### Data Flow
1. **Scraping**: HTML parsing → URL extraction → pagination handling
2. **Processing**: File analysis → conditional combining → metadata generation
3. **Upload**: OAuth → folder creation → batch upload → TOC generation
4. **Playback**: Authentication → file discovery → streaming → position tracking

## 🔧 Troubleshooting

### Common Issues

#### Python Scraper Issues
```bash
# Check dependencies
python python/diagnose_google_config.py

# Test Google Drive access
python tests/test_google_drive.py

# Dry run scraping
python python/audiobook_scraper.py "URL" --dry-run
```

#### Android App Issues
```bash
# Build issues
cd mobile/Haven
./gradlew clean assembleRelease

# Installation issues
adb uninstall com.antonilueddeke.androidapp2
adb install Haven-Signed.apk
```

#### Google OAuth Issues
1. Check `client_secret.json` is in root directory
2. Verify OAuth client type (Desktop app for Python, Android for app)
3. Ensure correct redirect URIs
4. Add SHA-1 fingerprints for Android signing

### Error Codes
- **"Sign in failed: 10"**: SHA-1 fingerprint mismatch
- **"invalid_request"**: Wrong OAuth client type
- **"No connected devices"**: ADB not installed/device not authorized

## 🛠️ Development

### Project Organization
- **`python/`**: All Python scripts and utilities
- **`mobile/Haven/`**: Android app with clean structure
- **`tests/`**: Isolated test files
- **`docs/`**: Documentation and guides
- **Root**: Configuration files and final artifacts

### Key Files
- **`python/audiobook_scraper.py`**: Main workflow orchestrator
- **`mobile/Haven/app/src/main/java/.../MainActivity.kt`**: Android app logic
- **`client_secret.json`**: OAuth credentials (root level)
- **`audiobookplayer.keystore`**: Android signing (root level)

### Build Process
1. **Python**: Install dependencies, run scraper
2. **Android**: `./gradlew assembleRelease` in `mobile/Haven/`
3. **Deploy**: Copy APK to root as `Haven-Signed.apk`

### Testing
```bash
# Test Python workflow
python tests/test_integrated_workflow.py

# Test Android build
cd mobile/Haven && ./gradlew test

# Test Google Drive
python tests/test_google_drive.py
```

## 📝 Notes

- **File Sizes**: Target 60-120 minutes, max 150MB per segment
- **Position Memory**: Stored locally on device, persists across restarts
- **Speed Control**: 0.05x increments for precise control
- **Error Handling**: Comprehensive logging and retry mechanisms
- **Security**: OAuth tokens cached locally, never committed to Git

## 🎯 Future Enhancements

- Cloud sync for position data
- Offline download capability
- Advanced audio processing options
- Multiple source support
- Enhanced UI/UX improvements

---

**Status**: ✅ MVP Complete - All functionality tested and working with clean project organization. 