# AudioBook Player 2

A cross-platform audiobook player application with Google Drive integration and advanced playback controls.

## 📱 Features

### Android App
- **Google Drive Integration**: Stream audiobooks directly from your Google Drive
- **Advanced Playback Controls**: Play/pause, next/previous track, skip forward/backward (30 seconds)
- **Playback Speed Control**: Adjustable speed from 0.5x to 2.0x
- **Google Sign-In Authentication**: Secure access to your Google Drive files
- **Professional Media Player**: Built with ExoPlayer for robust audio playback

### Python Utilities
- **Audio Downloader**: Download and combine MP3 files from web sources
- **Local Server**: Serve audiobook files locally for testing
- **Audio Processing**: Combine multiple audio files into larger segments

## 🏗️ Project Structure

```
AudioBookPlayer2/
├── AndroidApp2/                 # Android application
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/com/antonilueddeke/androidapp2/
│   │   │   │   └── MainActivity.kt    # Main Android app logic
│   │   │   └── res/layout/
│   │   │       └── activity_main.xml  # App UI layout
│   │   └── build.gradle.kts           # Android build configuration
│   └── build.gradle.kts
├── python_scripts/              # Python utilities
│   ├── downloader.py            # Audio download and processing script
│   ├── server.py                # Local HTTP server
│   └── audio_*.mp3              # Individual audio segments
├── audiobook_server/            # Combined audio files
│   └── combined_audio_part*.mp3 # Large audio segments
└── venv/                        # Python virtual environment
```

## 🚀 Quick Start

### Prerequisites

#### For Android App
- Android Studio (latest version)
- Android device or emulator (API level 24+)
- Google account with Google Drive access

#### For Python Scripts
- Python 3.7+
- FFmpeg installed on your system
- Required Python packages (see setup below)

### Setup Instructions

#### 1. Android App Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AudioBookPlayer2
   ```

2. **Open in Android Studio**
   - Open Android Studio
   - Select "Open an existing project"
   - Navigate to `AndroidApp2/` folder and open it

3. **Configure Google Sign-In**
   - The app uses Google Sign-In for Drive access
   - No additional configuration needed for basic functionality

4. **Build and Run**
   - Connect an Android device or start an emulator
   - Click "Run" in Android Studio
   - The app will install and launch on your device

#### 2. Python Scripts Setup

1. **Install FFmpeg**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

2. **Setup Python environment**
   ```bash
   cd AudioBookPlayer2
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install requests pydub
   ```

## 📖 Usage Guide

### Android App Usage

1. **Launch the App**
   - Open the AudioBook Player 2 app on your Android device

2. **Sign In**
   - Tap "Sign in with Google"
   - Grant necessary permissions for Google Drive access

3. **Play Audio**
   - The app automatically loads audiobook files from Google Drive
   - Use the playback controls:
     - **Play/Pause**: Start or pause playback
     - **Previous/Next**: Navigate between audio files
     - **Skip Forward/Backward**: Jump 30 seconds ahead or back
     - **Speed Slider**: Adjust playback speed (0.5x - 2.0x)

### Python Scripts Usage

#### Download and Process Audio Files

1. **Download audio files**
   ```bash
   cd python_scripts
   python downloader.py
   ```
   This will download MP3 files from the configured URL and combine them.

2. **Combine existing files only**
   ```bash
   python downloader.py --combine-only
   ```

#### Serve Audio Files Locally

1. **Start the local server**
   ```bash
   python server.py
   ```
   The server will start on `http://localhost:8000`

2. **Access files**
   - Open your web browser
   - Navigate to `http://localhost:8000`
   - Browse and download audio files

## 🔧 Configuration

### Android App Configuration

The app is pre-configured with:
- **Google Drive API**: Read-only access to Drive files
- **Audio File IDs**: Hardcoded Google Drive file IDs for specific audiobooks
- **Playback Settings**: Default skip duration (30 seconds), speed range (0.5x-2.0x)

### Python Scripts Configuration

#### downloader.py Configuration
- **Base URL**: Configured for specific audiobook source
- **File Format**: Supports numbered MP3 files (audio_00.mp3, audio_01.mp3, etc.)
- **Output**: Combines files into 1GB segments to avoid file size limits

#### server.py Configuration
- **Port**: Default port 8000
- **Directory**: Serves files from `audiobook_server/` directory

## 🛠️ Development

### Android Development

- **Language**: Kotlin
- **Minimum SDK**: 24 (Android 7.0)
- **Target SDK**: 34 (Android 14)
- **Key Dependencies**:
  - ExoPlayer for media playback
  - Google Sign-In API
  - Google Drive API
  - Material Design components

### Python Development

- **Dependencies**: `requests`, `pydub`
- **Audio Processing**: Uses FFmpeg for audio manipulation
- **File Management**: Downloads, combines, and serves audio files

## 📁 File Organization

### Audio Files
- **Individual segments**: `python_scripts/audio_*.mp3`
- **Combined parts**: `audiobook_server/combined_audio_part*.mp3`
- **Total size**: Multiple GB of audiobook content

### Source Code
- **Android**: Complete Android application with UI and business logic
- **Python**: Utility scripts for audio processing and serving

## 🔒 Security & Permissions

### Android Permissions
- **Internet**: Required for Google Drive access and audio streaming
- **Storage**: Required for temporary file caching
- **Google Sign-In**: Required for Drive authentication

### Google API Access
- **Drive API**: Read-only access to user's Google Drive
- **OAuth 2.0**: Secure authentication flow
- **Token Management**: Automatic token refresh and caching

## 🐛 Troubleshooting

### Common Issues

1. **Google Sign-In fails**
   - Ensure Google Play Services is installed and updated
   - Check internet connection
   - Verify Google account has Drive access

2. **Audio playback issues**
   - Check internet connection for streaming
   - Verify Google Drive file permissions
   - Ensure audio files are in supported format (MP3)

3. **Python script errors**
   - Verify FFmpeg is installed and in PATH
   - Check Python dependencies are installed
   - Ensure sufficient disk space for audio processing

### Debug Information

The Android app includes comprehensive logging:
- Check Android Studio Logcat for detailed error messages
- Look for tags: "MainActivity", "ExoPlayer", "Google Sign-In"

## 📄 License

This project is for educational and personal use. Please respect copyright laws when downloading and using audio content.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Android Studio logs for error details
3. Ensure all prerequisites are properly installed

---

**Note**: This project is designed for personal use and educational purposes. Ensure you have proper rights to any audio content you download or stream. 