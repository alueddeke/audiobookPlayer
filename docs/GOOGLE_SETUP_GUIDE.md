# Google Cloud Setup Guide for AudioBook Player 2

## Current Issue
You're getting "invalid_request" error because the Google Cloud Project isn't properly configured for OAuth authentication.

## Step-by-Step Setup

### 1. Access Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account (antonilueddeke@gmail.com)
3. Select your project: `audiobookplayer-436611`

### 2. Enable Required APIs
1. Go to **APIs & Services** > **Library**
2. Search for and enable these APIs:
   - **Google Drive API**
   - **Google+ API** (if available)
   - **Google OAuth2 API**

### 3. Configure OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type
3. Fill in the required information:
   - **App name**: AudioBook Player 2
   - **User support email**: antonilueddeke@gmail.com
   - **Developer contact information**: antonilueddeke@gmail.com
   - **App description**: Audiobook player with Google Drive integration
4. Add scopes:
   - `https://www.googleapis.com/auth/drive.readonly`
   - `https://www.googleapis.com/auth/drive.file`
5. Add test users:
   - Add your email: antonilueddeke@gmail.com
6. Save and continue

### 4. Configure OAuth 2.0 Client
1. Go to **APIs & Services** > **Credentials**
2. Find your existing OAuth 2.0 client or create a new one
3. Click on the client ID to edit
4. Add these **Authorized redirect URIs**:
   ```
   http://localhost:8080/
   http://localhost:8090/
   http://localhost:55571/
   http://localhost:55572/
   http://localhost:55573/
   http://localhost:55574/
   http://localhost:55575/
   ```
5. Add these **Authorized JavaScript origins**:
   ```
   http://localhost:8080
   http://localhost:8090
   ```
6. Save the changes

### 5. Download Updated Credentials
1. After making changes, download the updated `client_secret.json`
2. Replace the existing file in `AndroidApp2/app/client_secret.json`
3. Make sure the file is in the correct location

### 6. Test the Configuration
Run the test script again:
```bash
python test_google_drive.py
```

## Alternative: Create New OAuth Client

If the above doesn't work, create a new OAuth client:

### 1. Create New Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Choose **Desktop application**
4. Name it: "AudioBook Player Desktop"
5. Download the new `client_secret.json`

### 2. Update the Project
1. Replace `AndroidApp2/app/client_secret.json` with the new file
2. Update the scraper to use the new credentials

## Troubleshooting

### Common Issues:
1. **"invalid_request"**: OAuth consent screen not configured
2. **"redirect_uri_mismatch"**: Redirect URIs not properly set
3. **"access_denied"**: Test users not added to consent screen

### Verification Steps:
1. Check that all APIs are enabled
2. Verify OAuth consent screen is published
3. Confirm redirect URIs are correct
4. Ensure you're using the right client_secret.json file

## Security Notes
- Keep `client_secret.json` secure and never commit it to Git
- The file is already in `.gitignore` to prevent accidental commits
- For production, consider using service accounts instead of OAuth

## Next Steps
After proper configuration:
1. Test with `python test_google_drive.py`
2. Test the scraper with `python audiobook_scraper.py "URL" --dry-run`
3. Build and test the Android app
