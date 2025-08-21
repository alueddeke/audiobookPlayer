package com.antonilueddeke.androidapp2

import android.content.Intent
import android.content.IntentSender
import android.content.SharedPreferences
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.google.android.exoplayer2.ExoPlayer
import com.google.android.exoplayer2.MediaItem
import com.google.android.exoplayer2.Player
import com.google.android.exoplayer2.source.ProgressiveMediaSource
import com.google.android.exoplayer2.ui.PlayerView
import com.google.android.exoplayer2.upstream.DefaultHttpDataSource
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.android.gms.auth.api.signin.GoogleSignInStatusCodes
import com.google.android.gms.common.api.ApiException
import com.google.android.gms.common.api.Scope
import com.google.android.material.slider.Slider
import com.google.api.client.googleapis.extensions.android.gms.auth.GoogleAccountCredential
import com.google.api.client.http.javanet.NetHttpTransport
import com.google.api.client.json.gson.GsonFactory
import com.google.api.services.drive.Drive
import com.google.api.services.drive.DriveScopes
import com.google.api.services.drive.model.File
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.tasks.await
import com.google.android.exoplayer2.PlaybackException
import kotlinx.coroutines.delay
import com.google.android.gms.common.GoogleApiAvailability
import com.google.android.gms.common.ConnectionResult
import com.google.android.gms.auth.GoogleAuthUtil
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader

class MainActivity : AppCompatActivity() {

    private lateinit var mGoogleSignInClient: GoogleSignInClient
    private lateinit var driveService: Drive
    private lateinit var player: ExoPlayer
    private lateinit var playerView: PlayerView
    private lateinit var signInButton: Button
    private lateinit var playButton: Button
    private lateinit var nextButton: Button
    private lateinit var previousButton: Button
    private lateinit var skipForwardButton: Button
    private lateinit var skipBackwardButton: Button
    private lateinit var refreshButton: Button
    private lateinit var speedSlider: Slider
    private lateinit var statusText: TextView
    private lateinit var bookInfoText: TextView
    private var cachedAccessToken: String? = null
    private var tokenExpirationTime: Long = 0

    // Dynamic file management
    private var currentBook: BookInfo? = null
    private var currentSegmentIndex = 0
    private var availableBooks = mutableListOf<BookInfo>()
    private var isSigningIn = false

    // Position memory
    private lateinit var prefs: SharedPreferences
    private var positionUpdateHandler = Handler(Looper.getMainLooper())
    private var positionUpdateRunnable: Runnable? = null

    companion object {
        private const val RC_SIGN_IN = 9001
        private const val TAG = "MainActivity"
        private const val SKIP_DURATION = 30000L // 30 seconds in milliseconds
        private const val POSITION_UPDATE_INTERVAL = 5000L // 5 seconds
        private const val PREFS_NAME = "AudioBookPlayerPrefs"
        private const val KEY_LAST_BOOK_ID = "last_book_id"
        private const val KEY_LAST_SEGMENT_INDEX = "last_segment_index"
        private const val KEY_LAST_POSITION = "last_position"
        private const val KEY_LAST_SPEED = "last_speed"
    }

    data class BookInfo(
        val id: String,
        val name: String,
        val segments: List<SegmentInfo>,
        val tocFileId: String? = null
    )

    data class SegmentInfo(
        val fileId: String,
        val fileName: String,
        val durationMinutes: Double,
        val sizeMB: Double
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        
        initializeViews()
        setupGoogleSignIn()
        setupClickListeners()
        setupExoPlayer()
        setupSpeedControl()

        checkGooglePlayServices()
        
        // Try to resume from last position
        lifecycleScope.launch {
            tryResumeFromLastPosition()
        }
    }

    private fun checkGooglePlayServices() {
        val googleApiAvailability = GoogleApiAvailability.getInstance()
        val resultCode = googleApiAvailability.isGooglePlayServicesAvailable(this)
        if (resultCode != ConnectionResult.SUCCESS) {
            if (googleApiAvailability.isUserResolvableError(resultCode)) {
                googleApiAvailability.getErrorDialog(this, resultCode, 9000)?.show()
            } else {
                Toast.makeText(this, "This device is not supported", Toast.LENGTH_LONG).show()
                finish()
            }
        }
    }

    private fun initializeViews() {
        signInButton = findViewById(R.id.sign_in_button)
        playButton = findViewById(R.id.playButton)
        nextButton = findViewById(R.id.nextButton)
        previousButton = findViewById(R.id.previousButton)
        skipForwardButton = findViewById(R.id.skipForwardButton)
        skipBackwardButton = findViewById(R.id.skipBackwardButton)
        refreshButton = findViewById(R.id.refreshButton)
        speedSlider = findViewById(R.id.speedSlider)
        playerView = findViewById(R.id.player_view)
        statusText = findViewById(R.id.statusText)
        bookInfoText = findViewById(R.id.bookInfoText)
        
        // Set initial button state
        playButton.text = "Play"
    }

    private fun setupGoogleSignIn() {
        val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestEmail()
            .requestScopes(Scope(DriveScopes.DRIVE_READONLY))
            .build()

        mGoogleSignInClient = GoogleSignIn.getClient(this, gso)

        // Check for existing Google Sign In account
        val account = GoogleSignIn.getLastSignedInAccount(this)
        updateUI(account)
    }

    private fun setupClickListeners() {
        signInButton.setOnClickListener { signIn() }
        playButton.setOnClickListener { togglePlayPause() }
        nextButton.setOnClickListener { playNextSegment() }
        previousButton.setOnClickListener { playPreviousSegment() }
        skipForwardButton.setOnClickListener { skipForward() }
        skipBackwardButton.setOnClickListener { skipBackward() }
        refreshButton.setOnClickListener { refreshLibrary() }
    }

    private fun setupExoPlayer() {
        player = ExoPlayer.Builder(this).build()
        playerView.player = player
        updateButtonStates(false)

        player.addListener(object : Player.Listener {
            override fun onPlayerStateChanged(playWhenReady: Boolean, playbackState: Int) {
                when (playbackState) {
                    Player.STATE_IDLE -> Log.d(TAG, "ExoPlayer state: IDLE")
                    Player.STATE_BUFFERING -> {
                        Log.d(TAG, "ExoPlayer state: BUFFERING")
                        statusText.text = "Buffering..."
                    }
                    Player.STATE_READY -> {
                        Log.d(TAG, "ExoPlayer state: READY")
                        statusText.text = "Ready"
                        startPositionTracking()
                    }
                    Player.STATE_ENDED -> {
                        Log.d(TAG, "ExoPlayer state: ENDED")
                        statusText.text = "Ended"
                        stopPositionTracking()
                        // Auto-play next segment
                        playNextSegment()
                    }
                }
            }

            override fun onPlayerError(error: PlaybackException) {
                Log.e(TAG, "ExoPlayer error: ${error.message}", error)
                statusText.text = "Error: ${error.message}"
                
                // Try to reload or skip to next
                lifecycleScope.launch {
                    delay(2000) // Wait 2 seconds
                    if (currentBook != null && currentSegmentIndex < currentBook!!.segments.size - 1) {
                        Toast.makeText(this@MainActivity, "Skipping to next segment due to error", Toast.LENGTH_SHORT).show()
                        playNextSegment()
                    } else {
                        Toast.makeText(this@MainActivity, "Playback error. Please try again.", Toast.LENGTH_LONG).show()
                    }
                }
            }
        })
    }

    private fun setupSpeedControl() {
        // Enhanced speed control with 0.05x increments
        speedSlider.valueTo = 2.0f
        speedSlider.valueFrom = 0.5f
        speedSlider.value = prefs.getFloat(KEY_LAST_SPEED, 1.0f)
        speedSlider.stepSize = 0.05f // 0.05x increments
        speedSlider.addOnChangeListener { _, value, _ ->
            player.setPlaybackSpeed(value)
            prefs.edit().putFloat(KEY_LAST_SPEED, value).apply()
            updateSpeedDisplay(value)
        }
        updateSpeedDisplay(speedSlider.value)
    }

    private fun updateSpeedDisplay(speed: Float) {
        val speedText = findViewById<TextView>(R.id.speedText)
        speedText?.text = "${speed}x"
    }

    private fun signIn() {
        if (isSigningIn) {
            Log.d(TAG, "Sign-in already in progress")
            return
        }

        isSigningIn = true
        Log.d(TAG, "Starting sign-in process")

        lifecycleScope.launch {
            try {
                val account = withContext(Dispatchers.IO) {
                    mGoogleSignInClient.silentSignIn().await()
                }
                handleSignInResult(account)
            } catch (e: Exception) {
                Log.d(TAG, "Silent sign-in failed, starting interactive sign-in")
                startInteractiveSignIn()
            }
        }
    }

    private fun startInteractiveSignIn() {
        val signInIntent = mGoogleSignInClient.signInIntent
        startActivityForResult(signInIntent, RC_SIGN_IN)
    }

    private fun handleSignInResult(account: GoogleSignInAccount?) {
        isSigningIn = false
        if (account != null) {
            Log.d(TAG, "Sign-in successful: ${account.email}")
            updateUI(account)
            refreshLibrary()
        } else {
            Log.d(TAG, "Sign-in failed")
            updateUI(null)
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        if (requestCode == RC_SIGN_IN) {
            isSigningIn = false
            try {
                val task = GoogleSignIn.getSignedInAccountFromIntent(data)
                handleSignInResult(task.getResult(ApiException::class.java))
            } catch (e: ApiException) {
                Log.w(TAG, "Google Sign-In failed", e)
                when (e.statusCode) {
                    GoogleSignInStatusCodes.SIGN_IN_CANCELLED -> {
                        Log.d(TAG, "Sign-in cancelled")
                        Toast.makeText(this, "Sign-in cancelled", Toast.LENGTH_SHORT).show()
                    }
                    GoogleSignInStatusCodes.SIGN_IN_CURRENTLY_IN_PROGRESS -> {
                        Log.d(TAG, "Sign-in already in progress")
                        Handler(Looper.getMainLooper()).postDelayed({
                            signIn()
                        }, 1000)
                    }
                    12502 -> {
                        Log.e(TAG, "Sign-in failed due to 12502 error. Attempting to resolve.")
                        try {
                            e.status.startResolutionForResult(this, RC_SIGN_IN)
                        } catch (e2: IntentSender.SendIntentException) {
                            Log.e(TAG, "Couldn't start resolution for sign-in error", e2)
                            Toast.makeText(this, "Couldn't start resolution for sign-in error", Toast.LENGTH_LONG).show()
                            isSigningIn = false
                        }
                    }
                    else -> {
                        Log.e(TAG, "Sign-in failed with code: ${e.statusCode}")
                        Toast.makeText(this, "Sign-in failed: ${e.statusCode}", Toast.LENGTH_LONG).show()
                        handleSignInResult(null)
                    }
                }
            }
        }
    }

    private fun updateUI(account: GoogleSignInAccount?) {
        if (account != null) {
            Log.d(TAG, "Google Sign-In successful: ${account.email}")
            val credential = GoogleAccountCredential.usingOAuth2(
                this, listOf(DriveScopes.DRIVE_READONLY)
            )
            credential.selectedAccount = account.account

            driveService = Drive.Builder(
                NetHttpTransport(),
                GsonFactory(),
                credential
            )
                .setApplicationName("AudioBook Player")
                .build()

            updateButtonStates(true)
            statusText.text = "Signed in as ${account.email}"
        } else {
            Log.d(TAG, "Google Sign-In failed or not completed")
            updateButtonStates(false)
            statusText.text = "Please sign in"
        }
    }

    private fun updateButtonStates(enabled: Boolean) {
        playButton.isEnabled = enabled
        nextButton.isEnabled = enabled
        previousButton.isEnabled = enabled
        skipForwardButton.isEnabled = enabled
        skipBackwardButton.isEnabled = enabled
        speedSlider.isEnabled = enabled
        refreshButton.isEnabled = enabled
        signInButton.isEnabled = !enabled
    }

    private fun refreshLibrary() {
        lifecycleScope.launch {
            try {
                statusText.text = "Refreshing library..."
                availableBooks.clear()
                
                // Find audiobooks folder
                val audiobooksFolder = findAudiobooksFolder()
                if (audiobooksFolder != null) {
                    // Get all book folders
                    val bookFolders = getBookFolders(audiobooksFolder.id)
                    
                    for (bookFolder in bookFolders) {
                        val bookInfo = loadBookInfo(bookFolder)
                        if (bookInfo != null) {
                            availableBooks.add(bookInfo)
                        }
                    }
                    
                    statusText.text = "Found ${availableBooks.size} books"
                    updateBookDisplay()
                    
                    // If no current book is set, try to resume from last position
                    if (currentBook == null) {
                        tryResumeFromLastPosition()
                    }
                } else {
                    statusText.text = "No audiobooks folder found"
                    Toast.makeText(this@MainActivity, "Please create an 'audiobooks' folder in your Google Drive", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error refreshing library", e)
                statusText.text = "Error refreshing library"
                Toast.makeText(this@MainActivity, "Error refreshing library: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private suspend fun findAudiobooksFolder(): File? {
        return withContext(Dispatchers.IO) {
            try {
                val result = driveService.files().list()
                    .setQ("name='audiobooks' and mimeType='application/vnd.google-apps.folder' and trashed=false")
                    .setSpaces("drive")
                    .setFields("files(id, name)")
                    .execute()
                
                result.files.firstOrNull()
            } catch (e: Exception) {
                Log.e(TAG, "Error finding audiobooks folder", e)
                null
            }
        }
    }

    private suspend fun getBookFolders(audiobooksFolderId: String): List<File> {
        return withContext(Dispatchers.IO) {
            try {
                val result = driveService.files().list()
                    .setQ("'$audiobooksFolderId' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false")
                    .setSpaces("drive")
                    .setFields("files(id, name)")
                    .execute()
                
                result.files
            } catch (e: Exception) {
                Log.e(TAG, "Error getting book folders", e)
                emptyList()
            }
        }
    }

    private suspend fun loadBookInfo(bookFolder: File): BookInfo? {
        return withContext(Dispatchers.IO) {
            try {
                // Look for TOC file
                val tocResult = driveService.files().list()
                    .setQ("'${bookFolder.id}' in parents and name contains '_toc.json' and trashed=false")
                    .setSpaces("drive")
                    .setFields("files(id, name)")
                    .execute()
                
                val tocFile = tocResult.files.firstOrNull()
                
                // Get all MP3 files
                val mp3Result = driveService.files().list()
                    .setQ("'${bookFolder.id}' in parents and mimeType contains 'audio/' and trashed=false")
                    .setSpaces("drive")
                    .setFields("files(id, name, size)")
                    .execute()
                
                val segments = mp3Result.files.map { file ->
                    SegmentInfo(
                        fileId = file.id,
                        fileName = file.name,
                        durationMinutes = 0.0, // We'll estimate based on size
                        sizeMB = (file.size?.toDouble() ?: 0.0) / 1024 / 1024
                    )
                }.sortedBy { it.fileName }
                
                if (segments.isNotEmpty()) {
                    BookInfo(
                        id = bookFolder.id,
                        name = bookFolder.name,
                        segments = segments,
                        tocFileId = tocFile?.id
                    )
                } else {
                    null
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error loading book info for ${bookFolder.name}", e)
                null
            }
        }
    }

    private fun updateBookDisplay() {
        if (availableBooks.isNotEmpty()) {
            val bookNames = availableBooks.joinToString("\n") { "📚 ${it.name} (Tap to play)" }
            bookInfoText.text = "Available Books:\n$bookNames"
            
            // Make the text clickable
            bookInfoText.setOnClickListener {
                if (availableBooks.isNotEmpty()) {
                    // Select the first book for now (can be enhanced to show a picker)
                    selectBook(availableBooks[0])
                }
            }
            bookInfoText.isClickable = true
            bookInfoText.isFocusable = true
        } else {
            bookInfoText.text = "No books found"
            bookInfoText.setOnClickListener(null)
            bookInfoText.isClickable = false
            bookInfoText.isFocusable = false
        }
    }
    
    private fun selectBook(book: BookInfo) {
        currentBook = book
        currentSegmentIndex = 0
        playCurrentSegment()
        statusText.text = "Selected: ${book.name}"
        updateBookInfo()
    }

    private suspend fun tryResumeFromLastPosition() {
        val lastBookId = prefs.getString(KEY_LAST_BOOK_ID, null)
        val lastSegmentIndex = prefs.getInt(KEY_LAST_SEGMENT_INDEX, 0)
        val lastPosition = prefs.getLong(KEY_LAST_POSITION, 0)
        
        if (lastBookId != null) {
            val book = availableBooks.find { it.id == lastBookId }
            if (book != null && lastSegmentIndex < book.segments.size) {
                currentBook = book
                currentSegmentIndex = lastSegmentIndex
                
                // Load the file but don't auto-play
                playCurrentSegment()
                
                // Seek to the saved position
                if (lastPosition > 0) {
                    player.seekTo(lastPosition)
                }
                
                statusText.text = "Resumed ${book.name} - Segment ${lastSegmentIndex + 1}"
                updateBookInfo()
            }
        }
    }

    private fun playCurrentSegment() {
        if (currentBook != null && currentSegmentIndex < currentBook!!.segments.size) {
            val segment = currentBook!!.segments[currentSegmentIndex]
            playAudioFromDrive(segment.fileId)
            updateBookInfo()
        }
    }

    private fun playNextSegment() {
        if (currentBook != null && currentSegmentIndex < currentBook!!.segments.size - 1) {
            currentSegmentIndex++
            playCurrentSegment()
            saveCurrentPosition()
        } else {
            Toast.makeText(this, "End of book", Toast.LENGTH_SHORT).show()
        }
    }

    private fun playPreviousSegment() {
        if (currentBook != null && currentSegmentIndex > 0) {
            currentSegmentIndex--
            playCurrentSegment()
            saveCurrentPosition()
        } else {
            Toast.makeText(this, "Beginning of book", Toast.LENGTH_SHORT).show()
        }
    }

    private fun updateBookInfo() {
        if (currentBook != null) {
            val segment = currentBook!!.segments[currentSegmentIndex]
            val info = "${currentBook!!.name} - Segment ${currentSegmentIndex + 1} of ${currentBook!!.segments.size}"
            bookInfoText.text = info
        }
    }

    private fun skipForward() {
        player.seekTo(player.currentPosition + SKIP_DURATION)
    }

    private fun skipBackward() {
        player.seekTo((player.currentPosition - SKIP_DURATION).coerceAtLeast(0))
    }

    private var backoffTime = 1000L

    private fun playAudioFromDrive(fileId: String) {
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                Log.d(TAG, "Starting playAudioFromDrive with fileId: $fileId")

                val accessToken = getValidAccessToken()
                if (accessToken == null) {
                    Log.e(TAG, "Failed to get a valid access token")
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@MainActivity, "Failed to authenticate. Please try again.", Toast.LENGTH_LONG).show()
                    }
                    return@launch
                }

                Log.d(TAG, "Access token obtained successfully")

                val file = driveService.files().get(fileId)
                    .setFields("id, name, mimeType, webContentLink, webViewLink")
                    .execute()

                val audioUrl = "https://www.googleapis.com/drive/v3/files/${file.id}?alt=media"
                Log.d(TAG, "Audio URL: $audioUrl")
                Log.d(TAG, "File name: ${file.name}, MIME type: ${file.mimeType}")

                withContext(Dispatchers.Main) {
                    val dataSourceFactory = DefaultHttpDataSource.Factory()
                        .setDefaultRequestProperties(mapOf(
                            "Authorization" to "Bearer $accessToken"
                        ))

                    Log.d(TAG, "Creating media source")
                    val mediaSource = ProgressiveMediaSource.Factory(dataSourceFactory)
                        .createMediaSource(MediaItem.fromUri(audioUrl))

                    Log.d(TAG, "Setting media source to player")
                    player.setMediaSource(mediaSource)

                    Log.d(TAG, "Preparing player")
                    player.prepare()

                    Log.d(TAG, "Player ready - not auto-playing")
                    playButton.text = "Play"

                    Log.d(TAG, "Playback setup completed successfully")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error playing audio: ${e.message}")
                e.printStackTrace()
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Error playing audio: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private suspend fun getValidAccessToken(): String? {
        if (cachedAccessToken != null && System.currentTimeMillis() < tokenExpirationTime) {
            return cachedAccessToken
        }

        val account = GoogleSignIn.getLastSignedInAccount(this@MainActivity)
        if (account == null) {
            Log.e(TAG, "No signed-in account found")
            withContext(Dispatchers.Main) {
                signIn()
            }
            return null
        }

        val scopes = "oauth2:${DriveScopes.DRIVE_READONLY}"

        return try {
            val token = withContext(Dispatchers.IO) {
                GoogleAuthUtil.getToken(this@MainActivity, account.account!!, scopes)
            }

            cachedAccessToken = token
            tokenExpirationTime = System.currentTimeMillis() + 3600000 // Token typically valid for 1 hour
            backoffTime = 1000L // Reset backoff time on successful token refresh
            token
        } catch (e: Exception) {
            Log.e(TAG, "Failed to get token: ${e.message}")
            delay(backoffTime)
            backoffTime = (backoffTime * 2).coerceAtMost(60000L) // Max 1 minute
            null
        }
    }

    private fun togglePlayPause() {
        if (player.isPlaying) {
            player.pause()
            playButton.text = "Play"
            stopPositionTracking()
            Log.d(TAG, "Player paused")
        } else {
            if (player.mediaItemCount == 0) {
                Log.d(TAG, "No media item set, playing current segment")
                if (currentBook != null) {
                    playCurrentSegment()
                } else {
                    // If no book is selected, try to select the first available book
                    if (availableBooks.isNotEmpty()) {
                        selectBook(availableBooks[0])
                    } else {
                        Toast.makeText(this, "No book selected. Please refresh library first.", Toast.LENGTH_SHORT).show()
                        return
                    }
                }
            } else {
                if (player.playbackState == Player.STATE_ENDED) {
                    player.seekTo(0)
                }
                player.play()
            }
            playButton.text = "Pause"
            startPositionTracking()
            Log.d(TAG, "Player started")
        }
    }

    private fun startPositionTracking() {
        stopPositionTracking() // Stop any existing tracking
        
        positionUpdateRunnable = object : Runnable {
            override fun run() {
                if (player.isPlaying) {
                    saveCurrentPosition()
                    positionUpdateHandler.postDelayed(this, POSITION_UPDATE_INTERVAL)
                }
            }
        }
        positionUpdateHandler.post(positionUpdateRunnable!!)
    }

    private fun stopPositionTracking() {
        positionUpdateRunnable?.let {
            positionUpdateHandler.removeCallbacks(it)
            positionUpdateRunnable = null
        }
    }

    private fun saveCurrentPosition() {
        if (currentBook != null) {
            prefs.edit()
                .putString(KEY_LAST_BOOK_ID, currentBook!!.id)
                .putInt(KEY_LAST_SEGMENT_INDEX, currentSegmentIndex)
                .putLong(KEY_LAST_POSITION, player.currentPosition)
                .apply()
            
            Log.d(TAG, "Saved position: Book=${currentBook!!.name}, Segment=$currentSegmentIndex, Position=${player.currentPosition}")
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        stopPositionTracking()
        saveCurrentPosition()
        player.release()
    }
}