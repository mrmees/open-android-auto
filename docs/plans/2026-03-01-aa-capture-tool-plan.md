# AA Capture Tool Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a standalone Android app that captures AA-relevant logcat output during real-world car sessions, with selectable filter groups and shareable output.

**Architecture:** Single-activity Compose app with a foreground service that runs a `logcat` child process. Filter groups are hardcoded objects. Output is raw log + JSON sidecar, shared via Android share sheet as a zip.

**Tech Stack:** Kotlin, Jetpack Compose, Material 3, Gradle 8.11, AGP 8.7.3, min SDK 29, target SDK 35.

**Design doc:** `docs/plans/2026-03-01-aa-capture-tool-design.md`

---

### Task 1: Scaffold the Android Project

**Files:**
- Create: `aa-capture/settings.gradle.kts`
- Create: `aa-capture/build.gradle.kts`
- Create: `aa-capture/gradle.properties`
- Create: `aa-capture/app/build.gradle.kts`
- Create: `aa-capture/app/src/main/AndroidManifest.xml`
- Create: `aa-capture/app/src/main/java/org/openauto/aacapture/AACaptureApp.kt`
- Create: `aa-capture/app/src/main/java/org/openauto/aacapture/ui/MainActivity.kt`
- Create: `aa-capture/gradlew`, `aa-capture/gradlew.bat`, `aa-capture/gradle/wrapper/*`

**Step 1: Create project root files**

`settings.gradle.kts`:
```kotlin
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "AACaptureApp"
include(":app")
```

`build.gradle.kts`:
```kotlin
plugins {
    id("com.android.application") version "8.7.3" apply false
    id("org.jetbrains.kotlin.android") version "2.1.0" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.1.0" apply false
}
```

`gradle.properties`:
```properties
android.useAndroidX=true
org.gradle.jvmargs=-Xmx2048m
```

**Step 2: Create app/build.gradle.kts**

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "org.openauto.aacapture"
    compileSdk = 35

    defaultConfig {
        applicationId = "org.openauto.aacapture"
        minSdk = 29
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0"
    }

    buildFeatures {
        compose = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation(platform("androidx.compose:compose-bom:2024.12.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.compose.ui:ui-tooling-preview")
    debugImplementation("androidx.compose.ui:ui-tooling")

    testImplementation("junit:junit:4.13.2")
}
```

**Step 3: Create AndroidManifest.xml**

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.READ_LOGS" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_SPECIAL_USE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <application
        android:name=".AACaptureApp"
        android:label="AA Capture"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">

        <activity
            android:name=".ui.MainActivity"
            android:exported="true"
            android:theme="@android:style/Theme.Material.Light.NoActionBar">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".service.CaptureService"
            android:foregroundServiceType="specialUse"
            android:exported="false" />

    </application>
</manifest>
```

**Step 4: Create Application class**

`AACaptureApp.kt`:
```kotlin
package org.openauto.aacapture

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager

class AACaptureApp : Application() {
    override fun onCreate() {
        super.onCreate()
        val channel = NotificationChannel(
            CHANNEL_ID,
            "AA Capture",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Shows capture status"
        }
        getSystemService(NotificationManager::class.java)
            .createNotificationChannel(channel)
    }

    companion object {
        const val CHANNEL_ID = "aa_capture_channel"
    }
}
```

**Step 5: Create minimal MainActivity**

`MainActivity.kt`:
```kotlin
package org.openauto.aacapture.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface {
                    Text("AA Capture — scaffold works")
                }
            }
        }
    }
}
```

**Step 6: Copy Gradle wrapper from companion app**

```bash
cp -r ../companion-app/gradle aa-capture/gradle
cp ../companion-app/gradlew aa-capture/gradlew
cp ../companion-app/gradlew.bat aa-capture/gradlew.bat
chmod +x aa-capture/gradlew
```

**Step 7: Create default launcher icons**

Use Android's default ic_launcher resources (placeholder — replace later with a proper icon).

**Step 8: Build to verify scaffold**

```bash
cd aa-capture && ./gradlew assembleDebug
```
Expected: BUILD SUCCESSFUL

**Step 9: Commit**

```bash
git add -A
git commit -m "feat: scaffold aa-capture Android project"
```

---

### Task 2: Filter Groups Model

**Files:**
- Create: `app/src/main/java/org/openauto/aacapture/model/FilterGroup.kt`
- Create: `app/src/test/java/org/openauto/aacapture/model/FilterGroupTest.kt`

**Step 1: Write the test**

```kotlin
package org.openauto.aacapture.model

import org.junit.Assert.*
import org.junit.Test

class FilterGroupTest {

    @Test
    fun `default filters include expected groups`() {
        val defaults = FilterGroups.all.filter { it.enabledByDefault }
        val defaultIds = defaults.map { it.id }.toSet()
        assertTrue("sensors" in defaultIds)
        assertTrue("radio" in defaultIds)
        assertTrue("navigation" in defaultIds)
        assertTrue("car_control" in defaultIds)
        assertTrue("session" in defaultIds)
    }

    @Test
    fun `verbose is not enabled by default`() {
        val verbose = FilterGroups.all.first { it.id == "verbose" }
        assertFalse(verbose.enabledByDefault)
    }

    @Test
    fun `buildLogcatArgs produces correct tag filters`() {
        val selected = FilterGroups.all.filter { it.id == "sensors" }
        val args = FilterGroups.buildLogcatArgs(selected)
        // Should contain each tag with :V suffix and *:S to silence everything else
        assertTrue(args.contains("CAR.SENSOR.LITE:V"))
        assertTrue(args.contains("CAR.SENSOR:V"))
        assertTrue(args.last() == "*:S")
    }

    @Test
    fun `buildLogcatArgs with verbose omits tag filters`() {
        val selected = FilterGroups.all.filter { it.id == "verbose" }
        val args = FilterGroups.buildLogcatArgs(selected)
        // Verbose = no tag filters, just -v threadtime
        assertFalse(args.contains("*:S"))
    }

    @Test
    fun `all groups have unique ids`() {
        val ids = FilterGroups.all.map { it.id }
        assertEquals(ids.size, ids.toSet().size)
    }
}
```

**Step 2: Run test to verify it fails**

```bash
./gradlew test
```
Expected: FAIL — FilterGroups not found

**Step 3: Implement FilterGroups**

```kotlin
package org.openauto.aacapture.model

data class FilterGroup(
    val id: String,
    val name: String,
    val description: String,
    val tags: List<String>,
    val enabledByDefault: Boolean
)

object FilterGroups {
    val all = listOf(
        FilterGroup(
            id = "session",
            name = "Session & Control",
            description = "Connection handshake, channel opens, shutdown",
            tags = listOf("AASession", "AATransport", "CarLifecycle"),
            enabledByDefault = true
        ),
        FilterGroup(
            id = "sensors",
            name = "Sensors",
            description = "Speed, fuel, GPS, night mode, gear, HVAC",
            tags = listOf("CAR.SENSOR.LITE", "CAR.SENSOR"),
            enabledByDefault = true
        ),
        FilterGroup(
            id = "video",
            name = "Video",
            description = "Video stream setup, focus, resolution",
            tags = listOf("CAR.GAL.VIDEO"),
            enabledByDefault = false
        ),
        FilterGroup(
            id = "audio",
            name = "Audio",
            description = "Audio channel setup, focus transitions",
            tags = listOf("CAR.AUDIO", "AudioFocus"),
            enabledByDefault = false
        ),
        FilterGroup(
            id = "radio",
            name = "Radio",
            description = "Radio channel, MediaBrowserService",
            tags = listOf("CAR.GAL.RADIO-EP", "GH.Radio", "CAR.RADIO"),
            enabledByDefault = true
        ),
        FilterGroup(
            id = "navigation",
            name = "Navigation",
            description = "Turn events, nav focus, cluster nav data",
            tags = listOf("GH.NDirector", "NAV"),
            enabledByDefault = true
        ),
        FilterGroup(
            id = "car_control",
            name = "Car Control",
            description = "HVAC, door locks, vehicle properties",
            tags = listOf("CAR.GAL.CAR_CONTROL"),
            enabledByDefault = true
        ),
        FilterGroup(
            id = "media",
            name = "Media",
            description = "Media metadata, browsing",
            tags = listOf("GH.MediaActiveContrConn", "MediaBrowser"),
            enabledByDefault = false
        ),
        FilterGroup(
            id = "verbose",
            name = "All (verbose)",
            description = "Everything — large files, but nothing missed",
            tags = emptyList(),
            enabledByDefault = false
        )
    )

    fun buildLogcatArgs(selected: List<FilterGroup>): List<String> {
        if (selected.any { it.id == "verbose" }) {
            return listOf("-v", "threadtime")
        }
        val args = mutableListOf("-v", "threadtime")
        for (group in selected) {
            for (tag in group.tags) {
                args.add("$tag:V")
            }
        }
        args.add("*:S")
        return args
    }
}
```

**Step 4: Run tests**

```bash
./gradlew test
```
Expected: ALL PASS

**Step 5: Commit**

```bash
git add app/src/main/java/org/openauto/aacapture/model/FilterGroup.kt \
       app/src/test/java/org/openauto/aacapture/model/FilterGroupTest.kt
git commit -m "feat: add FilterGroup model with AA log tag definitions"
```

---

### Task 3: CaptureSession Data Model

**Files:**
- Create: `app/src/main/java/org/openauto/aacapture/model/CaptureSession.kt`
- Create: `app/src/test/java/org/openauto/aacapture/model/CaptureSessionTest.kt`

**Step 1: Write the test**

```kotlin
package org.openauto.aacapture.model

import org.junit.Assert.*
import org.junit.Test
import org.json.JSONObject

class CaptureSessionTest {

    @Test
    fun `toJson includes all metadata fields`() {
        val session = CaptureSession(
            device = "Pixel 7",
            androidVersion = "14",
            aaVersion = "16.1.660414",
            filters = listOf("sensors", "radio"),
            notes = "Test session",
            startTime = "2026-03-01T14:30:00Z",
            endTime = "2026-03-01T15:00:00Z",
            markers = mutableListOf("14:32:05", "14:38:12"),
            lineCount = 1000,
            fileSizeBytes = 50000
        )
        val json = JSONObject(session.toJson())
        assertEquals("Pixel 7", json.getString("device"))
        assertEquals("16.1.660414", json.getString("aa_version"))
        assertEquals(2, json.getJSONArray("filters").length())
        assertEquals(2, json.getJSONArray("markers").length())
        assertEquals(1000, json.getInt("line_count"))
    }

    @Test
    fun `toJson handles empty markers and notes`() {
        val session = CaptureSession(
            device = "Test",
            androidVersion = "14",
            aaVersion = "unknown",
            filters = emptyList(),
            notes = "",
            startTime = "2026-03-01T14:30:00Z"
        )
        val json = JSONObject(session.toJson())
        assertEquals(0, json.getJSONArray("markers").length())
        assertEquals("", json.getString("notes"))
    }
}
```

**Step 2: Run test to verify it fails**

```bash
./gradlew test
```
Expected: FAIL — CaptureSession not found

**Step 3: Implement CaptureSession**

```kotlin
package org.openauto.aacapture.model

import org.json.JSONArray
import org.json.JSONObject

data class CaptureSession(
    val device: String,
    val androidVersion: String,
    val aaVersion: String,
    val filters: List<String>,
    val notes: String,
    val startTime: String,
    val endTime: String? = null,
    val markers: MutableList<String> = mutableListOf(),
    val lineCount: Int = 0,
    val fileSizeBytes: Long = 0
) {
    fun toJson(): String {
        return JSONObject().apply {
            put("device", device)
            put("android_version", androidVersion)
            put("aa_version", aaVersion)
            put("filters", JSONArray(filters))
            put("notes", notes)
            put("start_time", startTime)
            put("end_time", endTime ?: "")
            put("markers", JSONArray(markers))
            put("line_count", lineCount)
            put("file_size_bytes", fileSizeBytes)
        }.toString(2)
    }
}
```

**Step 4: Run tests**

```bash
./gradlew test
```
Expected: ALL PASS

**Step 5: Commit**

```bash
git add app/src/main/java/org/openauto/aacapture/model/CaptureSession.kt \
       app/src/test/java/org/openauto/aacapture/model/CaptureSessionTest.kt
git commit -m "feat: add CaptureSession data model with JSON serialization"
```

---

### Task 4: CaptureService — Foreground Service with Logcat Process

**Files:**
- Create: `app/src/main/java/org/openauto/aacapture/service/CaptureService.kt`

**Step 1: Implement CaptureService**

```kotlin
package org.openauto.aacapture.service

import android.app.Notification
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import org.openauto.aacapture.AACaptureApp
import org.openauto.aacapture.R
import org.openauto.aacapture.model.CaptureSession
import org.openauto.aacapture.model.FilterGroups
import org.openauto.aacapture.ui.MainActivity
import java.io.BufferedReader
import java.io.File
import java.io.FileOutputStream
import java.io.InputStreamReader
import java.text.SimpleDateFormat
import java.util.*

class CaptureService : Service() {

    private var logcatProcess: Process? = null
    private var captureJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var outputFile: File? = null
    private var sessionData: CaptureSession? = null
    private var lineCount = 0

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> {
                val filterIds = intent.getStringArrayListExtra(EXTRA_FILTER_IDS) ?: arrayListOf()
                val notes = intent.getStringExtra(EXTRA_NOTES) ?: ""
                startCapture(filterIds, notes)
            }
            ACTION_STOP -> stopCapture()
            ACTION_MARK -> insertMarker()
        }
        return START_NOT_STICKY
    }

    private fun startCapture(filterIds: List<String>, notes: String) {
        if (_capturing.value) return

        // Create output file
        val timestamp = SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.US).format(Date())
        val capturesDir = File(getExternalFilesDir(null), "captures").apply { mkdirs() }
        outputFile = File(capturesDir, "aa-capture_$timestamp.log")

        // Detect device info
        val aaVersion = try {
            packageManager.getPackageInfo("com.google.android.projection.gearhead", 0)
                .versionName ?: "unknown"
        } catch (_: PackageManager.NameNotFoundException) {
            "not installed"
        }

        sessionData = CaptureSession(
            device = "${Build.MANUFACTURER} ${Build.MODEL}",
            androidVersion = Build.VERSION.RELEASE,
            aaVersion = aaVersion,
            filters = filterIds,
            notes = notes,
            startTime = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
                .apply { timeZone = TimeZone.getTimeZone("UTC") }
                .format(Date())
        )

        // Build logcat command
        val selectedGroups = FilterGroups.all.filter { it.id in filterIds }
        val logcatArgs = FilterGroups.buildLogcatArgs(selectedGroups)
        val cmd = mutableListOf("logcat", "-c") // Clear buffer first

        // Start foreground
        startForeground(
            NOTIFICATION_ID,
            buildNotification("Capturing... (0 lines)"),
            ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE
        )
        _capturing.value = true
        lineCount = 0
        _lineCount.value = 0
        _startTimeMillis.value = System.currentTimeMillis()

        // Clear logcat buffer, then start capture
        captureJob = scope.launch {
            try {
                Runtime.getRuntime().exec(arrayOf("logcat", "-c")).waitFor()

                val fullCmd = mutableListOf("logcat")
                fullCmd.addAll(logcatArgs)
                logcatProcess = Runtime.getRuntime().exec(fullCmd.toTypedArray())

                val reader = BufferedReader(InputStreamReader(logcatProcess!!.inputStream))
                FileOutputStream(outputFile!!, true).bufferedWriter().use { writer ->
                    var line = reader.readLine()
                    while (line != null && isActive) {
                        writer.appendLine(line)
                        lineCount++
                        if (lineCount % 100 == 0) {
                            writer.flush()
                            _lineCount.value = lineCount
                            withContext(Dispatchers.Main) {
                                updateNotification("Capturing... ($lineCount lines)")
                            }
                        }
                        line = reader.readLine()
                    }
                    writer.flush()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Capture error", e)
            }
        }
    }

    private fun stopCapture() {
        if (!_capturing.value) return

        captureJob?.cancel()
        logcatProcess?.destroy()
        logcatProcess = null

        // Write JSON sidecar
        val file = outputFile
        if (file != null && sessionData != null) {
            val finalSession = sessionData!!.copy(
                endTime = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US)
                    .apply { timeZone = TimeZone.getTimeZone("UTC") }
                    .format(Date()),
                lineCount = lineCount,
                fileSizeBytes = file.length()
            )
            val jsonFile = File(file.parent, file.nameWithoutExtension + ".json")
            jsonFile.writeText(finalSession.toJson())
        }

        _capturing.value = false
        _lineCount.value = lineCount
        _startTimeMillis.value = 0L
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun insertMarker() {
        val now = SimpleDateFormat("HH:mm:ss", Locale.US).format(Date())
        val markerLine = "===== MARKER $now ====="
        sessionData?.markers?.add(now)

        // Append marker to the log file directly
        outputFile?.let { file ->
            scope.launch {
                file.appendText("\n$markerLine\n")
            }
        }
        updateNotification("Capturing... ($lineCount lines) [Marked $now]")
    }

    private fun buildNotification(text: String): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )

        val markIntent = Intent(this, CaptureService::class.java).apply {
            action = ACTION_MARK
        }
        val markPending = PendingIntent.getService(
            this, 1, markIntent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        val stopIntent = Intent(this, CaptureService::class.java).apply {
            action = ACTION_STOP
        }
        val stopPending = PendingIntent.getService(
            this, 2, stopIntent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        return NotificationCompat.Builder(this, AACaptureApp.CHANNEL_ID)
            .setContentTitle("AA Capture")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_menu_save)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .addAction(0, "Mark Event", markPending)
            .addAction(0, "Stop", stopPending)
            .build()
    }

    private fun updateNotification(text: String) {
        val nm = getSystemService(android.app.NotificationManager::class.java)
        nm.notify(NOTIFICATION_ID, buildNotification(text))
    }

    override fun onDestroy() {
        if (_capturing.value) stopCapture()
        scope.cancel()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        private const val TAG = "CaptureService"
        private const val NOTIFICATION_ID = 2001
        const val ACTION_START = "org.openauto.aacapture.START"
        const val ACTION_STOP = "org.openauto.aacapture.STOP"
        const val ACTION_MARK = "org.openauto.aacapture.MARK"
        const val EXTRA_FILTER_IDS = "filter_ids"
        const val EXTRA_NOTES = "notes"

        private val _capturing = MutableStateFlow(false)
        val capturing: StateFlow<Boolean> = _capturing.asStateFlow()

        private val _lineCount = MutableStateFlow(0)
        val lineCount: StateFlow<Int> = _lineCount.asStateFlow()

        private val _startTimeMillis = MutableStateFlow(0L)
        val startTimeMillis: StateFlow<Long> = _startTimeMillis.asStateFlow()
    }
}
```

**Step 2: Build to verify compilation**

```bash
./gradlew assembleDebug
```
Expected: BUILD SUCCESSFUL

**Step 3: Commit**

```bash
git add app/src/main/java/org/openauto/aacapture/service/CaptureService.kt
git commit -m "feat: add CaptureService foreground service with logcat capture"
```

---

### Task 5: Permission Check Utility

**Files:**
- Create: `app/src/main/java/org/openauto/aacapture/util/PermissionChecker.kt`

**Step 1: Implement PermissionChecker**

```kotlin
package org.openauto.aacapture.util

import android.content.Context
import android.content.pm.PackageManager

object PermissionChecker {
    fun hasReadLogs(context: Context): Boolean {
        return context.checkSelfPermission("android.permission.READ_LOGS") ==
            PackageManager.PERMISSION_GRANTED
    }

    fun hasNotificationPermission(context: Context): Boolean {
        return if (android.os.Build.VERSION.SDK_INT >= 33) {
            context.checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) ==
                PackageManager.PERMISSION_GRANTED
        } else true
    }

    const val ADB_GRANT_COMMAND = "adb shell pm grant org.openauto.aacapture android.permission.READ_LOGS"
}
```

**Step 2: Build**

```bash
./gradlew assembleDebug
```
Expected: BUILD SUCCESSFUL

**Step 3: Commit**

```bash
git add app/src/main/java/org/openauto/aacapture/util/PermissionChecker.kt
git commit -m "feat: add permission check utility for READ_LOGS"
```

---

### Task 6: Capture File Manager (list, share, delete)

**Files:**
- Create: `app/src/main/java/org/openauto/aacapture/util/CaptureFileManager.kt`
- Create: `app/src/test/java/org/openauto/aacapture/util/CaptureFileManagerTest.kt`

**Step 1: Write the test**

```kotlin
package org.openauto.aacapture.util

import org.junit.Assert.*
import org.junit.Test
import org.junit.Rule
import org.junit.rules.TemporaryFolder

class CaptureFileManagerTest {

    @get:Rule
    val tempDir = TemporaryFolder()

    @Test
    fun `listCaptures finds paired log and json files`() {
        val dir = tempDir.root
        dir.resolve("aa-capture_2026-03-01_14-30-00.log").writeText("log content")
        dir.resolve("aa-capture_2026-03-01_14-30-00.json").writeText("""{"device":"test"}""")
        dir.resolve("random.txt").writeText("noise")

        val captures = CaptureFileManager.listCaptures(dir)
        assertEquals(1, captures.size)
        assertEquals("aa-capture_2026-03-01_14-30-00", captures[0].baseName)
        assertNotNull(captures[0].jsonFile)
    }

    @Test
    fun `listCaptures handles log without json sidecar`() {
        val dir = tempDir.root
        dir.resolve("aa-capture_2026-03-01_14-30-00.log").writeText("log content")

        val captures = CaptureFileManager.listCaptures(dir)
        assertEquals(1, captures.size)
        assertNull(captures[0].jsonFile)
    }

    @Test
    fun `listCaptures returns empty for empty directory`() {
        val captures = CaptureFileManager.listCaptures(tempDir.root)
        assertTrue(captures.isEmpty())
    }

    @Test
    fun `deleteCapture removes both log and json files`() {
        val dir = tempDir.root
        val log = dir.resolve("aa-capture_test.log").apply { writeText("log") }
        val json = dir.resolve("aa-capture_test.json").apply { writeText("json") }

        val entry = CaptureEntry("aa-capture_test", log, json)
        CaptureFileManager.deleteCapture(entry)

        assertFalse(log.exists())
        assertFalse(json.exists())
    }
}
```

**Step 2: Run test to verify it fails**

```bash
./gradlew test
```
Expected: FAIL — CaptureFileManager not found

**Step 3: Implement CaptureFileManager**

```kotlin
package org.openauto.aacapture.util

import android.content.Context
import android.content.Intent
import androidx.core.content.FileProvider
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

data class CaptureEntry(
    val baseName: String,
    val logFile: File,
    val jsonFile: File?
) {
    val sizeBytes: Long get() = logFile.length() + (jsonFile?.length() ?: 0)
    val lastModified: Long get() = logFile.lastModified()
}

object CaptureFileManager {

    fun listCaptures(dir: File): List<CaptureEntry> {
        if (!dir.exists()) return emptyList()
        val logFiles = dir.listFiles { f -> f.extension == "log" && f.name.startsWith("aa-capture_") }
            ?: return emptyList()
        return logFiles
            .sortedByDescending { it.lastModified() }
            .map { log ->
                val baseName = log.nameWithoutExtension
                val json = File(dir, "$baseName.json").takeIf { it.exists() }
                CaptureEntry(baseName, log, json)
            }
    }

    fun deleteCapture(entry: CaptureEntry) {
        entry.logFile.delete()
        entry.jsonFile?.delete()
    }

    fun createZip(entry: CaptureEntry, outputDir: File): File {
        val zipFile = File(outputDir, "${entry.baseName}.zip")
        ZipOutputStream(FileOutputStream(zipFile)).use { zos ->
            addToZip(zos, entry.logFile)
            entry.jsonFile?.let { addToZip(zos, it) }
        }
        return zipFile
    }

    private fun addToZip(zos: ZipOutputStream, file: File) {
        zos.putNextEntry(ZipEntry(file.name))
        FileInputStream(file).use { it.copyTo(zos) }
        zos.closeEntry()
    }

    fun getShareIntent(context: Context, entry: CaptureEntry): Intent {
        val cacheDir = File(context.cacheDir, "share").apply { mkdirs() }
        val zipFile = createZip(entry, cacheDir)
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", zipFile)
        return Intent(Intent.ACTION_SEND).apply {
            type = "application/zip"
            putExtra(Intent.EXTRA_STREAM, uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
    }
}
```

**Step 4: Add FileProvider to AndroidManifest.xml**

Add inside `<application>`:
```xml
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

**Step 5: Create file_paths.xml**

Create `app/src/main/res/xml/file_paths.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<paths>
    <cache-path name="share" path="share/" />
</paths>
```

**Step 6: Run tests**

```bash
./gradlew test
```
Expected: ALL PASS

**Step 7: Commit**

```bash
git add app/src/main/java/org/openauto/aacapture/util/CaptureFileManager.kt \
       app/src/test/java/org/openauto/aacapture/util/CaptureFileManagerTest.kt \
       app/src/main/AndroidManifest.xml \
       app/src/main/res/xml/file_paths.xml
git commit -m "feat: add CaptureFileManager with list, delete, zip, and share"
```

---

### Task 7: Main UI — Complete Compose Screen

**Files:**
- Modify: `app/src/main/java/org/openauto/aacapture/ui/MainActivity.kt`
- Create: `app/src/main/java/org/openauto/aacapture/ui/CaptureScreen.kt`
- Create: `app/src/main/java/org/openauto/aacapture/ui/FilterSelector.kt`
- Create: `app/src/main/java/org/openauto/aacapture/ui/CaptureListSection.kt`
- Create: `app/src/main/java/org/openauto/aacapture/ui/PermissionBanner.kt`

**Step 1: Create PermissionBanner composable**

`PermissionBanner.kt`:
```kotlin
package org.openauto.aacapture.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import org.openauto.aacapture.util.PermissionChecker

@Composable
fun PermissionBanner(hasReadLogs: Boolean) {
    if (hasReadLogs) return

    val clipboardManager = LocalClipboardManager.current

    Card(
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer
        ),
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                "READ_LOGS permission required",
                style = MaterialTheme.typography.titleSmall,
                color = MaterialTheme.colorScheme.onErrorContainer
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                "Connect your phone to a computer via USB and run:",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onErrorContainer
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                PermissionChecker.ADB_GRANT_COMMAND,
                style = MaterialTheme.typography.bodySmall.copy(fontFamily = FontFamily.Monospace),
                color = MaterialTheme.colorScheme.onErrorContainer
            )
            Spacer(modifier = Modifier.height(8.dp))
            TextButton(onClick = {
                clipboardManager.setText(AnnotatedString(PermissionChecker.ADB_GRANT_COMMAND))
            }) {
                Text("Copy command")
            }
        }
    }
}
```

**Step 2: Create FilterSelector composable**

`FilterSelector.kt`:
```kotlin
package org.openauto.aacapture.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import org.openauto.aacapture.model.FilterGroup

@Composable
fun FilterSelector(
    groups: List<FilterGroup>,
    selectedIds: Set<String>,
    onToggle: (String) -> Unit
) {
    Column(modifier = Modifier.padding(horizontal = 16.dp)) {
        Text(
            "Log Filters",
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.padding(bottom = 8.dp)
        )
        groups.forEach { group ->
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 2.dp)
            ) {
                Checkbox(
                    checked = group.id in selectedIds,
                    onCheckedChange = { onToggle(group.id) }
                )
                Column(modifier = Modifier.padding(start = 8.dp)) {
                    Text(group.name, style = MaterialTheme.typography.bodyMedium)
                    Text(
                        group.description,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}
```

**Step 3: Create CaptureListSection composable**

`CaptureListSection.kt`:
```kotlin
package org.openauto.aacapture.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import org.openauto.aacapture.util.CaptureEntry
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun CaptureListSection(
    captures: List<CaptureEntry>,
    onShare: (CaptureEntry) -> Unit,
    onDelete: (CaptureEntry) -> Unit
) {
    if (captures.isEmpty()) return

    Column(modifier = Modifier.padding(16.dp)) {
        Text(
            "Past Captures",
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.padding(bottom = 8.dp)
        )
        captures.forEach { entry ->
            CaptureRow(entry, onShare, onDelete)
        }
    }
}

@Composable
private fun CaptureRow(
    entry: CaptureEntry,
    onShare: (CaptureEntry) -> Unit,
    onDelete: (CaptureEntry) -> Unit
) {
    val dateFormat = remember { SimpleDateFormat("MMM d, HH:mm", Locale.US) }
    val sizeKb = entry.sizeBytes / 1024

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(12.dp)
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    dateFormat.format(Date(entry.lastModified)),
                    style = MaterialTheme.typography.bodyMedium
                )
                Text(
                    "${sizeKb}KB",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            IconButton(onClick = { onShare(entry) }) {
                Icon(Icons.Default.Share, contentDescription = "Share")
            }
            IconButton(onClick = { onDelete(entry) }) {
                Icon(Icons.Default.Delete, contentDescription = "Delete")
            }
        }
    }
}
```

**Step 4: Create CaptureScreen composable**

`CaptureScreen.kt`:
```kotlin
package org.openauto.aacapture.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import org.openauto.aacapture.model.FilterGroups
import org.openauto.aacapture.service.CaptureService
import org.openauto.aacapture.util.CaptureEntry
import org.openauto.aacapture.util.PermissionChecker

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CaptureScreen(
    hasReadLogs: Boolean,
    capturing: Boolean,
    lineCount: Int,
    startTimeMillis: Long,
    captures: List<CaptureEntry>,
    onStartCapture: (selectedFilterIds: List<String>, notes: String) -> Unit,
    onStopCapture: () -> Unit,
    onShare: (CaptureEntry) -> Unit,
    onDelete: (CaptureEntry) -> Unit
) {
    val selectedIds = remember {
        mutableStateOf(
            FilterGroups.all.filter { it.enabledByDefault }.map { it.id }.toSet()
        )
    }
    var notes by remember { mutableStateOf("") }

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("AA Capture") })
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .verticalScroll(rememberScrollState())
        ) {
            PermissionBanner(hasReadLogs)

            if (capturing) {
                // Live capture status
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    ),
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            "Capturing...",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            "$lineCount lines captured",
                            style = MaterialTheme.typography.headlineMedium
                        )
                        if (startTimeMillis > 0) {
                            val elapsed = (System.currentTimeMillis() - startTimeMillis) / 1000
                            Text(
                                "${elapsed / 60}m ${elapsed % 60}s",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(
                            onClick = onStopCapture,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = MaterialTheme.colorScheme.error
                            )
                        ) {
                            Text("Stop Capture")
                        }
                    }
                }
            } else {
                // Setup controls
                FilterSelector(
                    groups = FilterGroups.all,
                    selectedIds = selectedIds.value,
                    onToggle = { id ->
                        selectedIds.value = if (id in selectedIds.value) {
                            selectedIds.value - id
                        } else {
                            selectedIds.value + id
                        }
                    }
                )

                Spacer(modifier = Modifier.height(16.dp))

                OutlinedTextField(
                    value = notes,
                    onValueChange = { notes = it },
                    label = { Text("Session notes (optional)") },
                    placeholder = { Text("e.g., 2025 Tucson Hybrid, wireless AA") },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                    maxLines = 3
                )

                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = {
                        onStartCapture(selectedIds.value.toList(), notes)
                    },
                    enabled = hasReadLogs && selectedIds.value.isNotEmpty(),
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .height(56.dp)
                ) {
                    Text("Start Capture", style = MaterialTheme.typography.titleMedium)
                }
            }

            Spacer(modifier = Modifier.height(16.dp))
            HorizontalDivider(modifier = Modifier.padding(horizontal = 16.dp))

            CaptureListSection(
                captures = captures,
                onShare = onShare,
                onDelete = onDelete
            )
        }
    }
}
```

**Step 5: Update MainActivity to wire everything together**

```kotlin
package org.openauto.aacapture.ui

import android.Manifest
import android.content.Intent
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.*
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import org.openauto.aacapture.service.CaptureService
import org.openauto.aacapture.util.CaptureFileManager
import org.openauto.aacapture.util.PermissionChecker
import java.io.File

class MainActivity : ComponentActivity() {

    private val notificationPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { /* no-op, we just need to ask */ }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (Build.VERSION.SDK_INT >= 33) {
            notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        }

        setContent {
            MaterialTheme {
                val hasReadLogs = PermissionChecker.hasReadLogs(this)
                val capturing by CaptureService.capturing.collectAsStateWithLifecycle()
                val lineCount by CaptureService.lineCount.collectAsStateWithLifecycle()
                val startTimeMillis by CaptureService.startTimeMillis.collectAsStateWithLifecycle()

                val capturesDir = File(getExternalFilesDir(null), "captures")
                var captures by remember { mutableStateOf(CaptureFileManager.listCaptures(capturesDir)) }

                // Refresh capture list when capture stops
                LaunchedEffect(capturing) {
                    if (!capturing) {
                        captures = CaptureFileManager.listCaptures(capturesDir)
                    }
                }

                CaptureScreen(
                    hasReadLogs = hasReadLogs,
                    capturing = capturing,
                    lineCount = lineCount,
                    startTimeMillis = startTimeMillis,
                    captures = captures,
                    onStartCapture = { filterIds, notes ->
                        val intent = Intent(this, CaptureService::class.java).apply {
                            action = CaptureService.ACTION_START
                            putStringArrayListExtra(CaptureService.EXTRA_FILTER_IDS, ArrayList(filterIds))
                            putExtra(CaptureService.EXTRA_NOTES, notes)
                        }
                        startForegroundService(intent)
                    },
                    onStopCapture = {
                        val intent = Intent(this, CaptureService::class.java).apply {
                            action = CaptureService.ACTION_STOP
                        }
                        startService(intent)
                    },
                    onShare = { entry ->
                        startActivity(
                            Intent.createChooser(
                                CaptureFileManager.getShareIntent(this, entry),
                                "Share capture"
                            )
                        )
                    },
                    onDelete = { entry ->
                        CaptureFileManager.deleteCapture(entry)
                        captures = CaptureFileManager.listCaptures(capturesDir)
                    }
                )
            }
        }
    }
}
```

**Step 6: Build**

```bash
./gradlew assembleDebug
```
Expected: BUILD SUCCESSFUL

**Step 7: Commit**

```bash
git add app/src/main/java/org/openauto/aacapture/ui/
git commit -m "feat: add complete Compose UI with filter selection, capture controls, and history"
```

---

### Task 8: README and Final Polish

**Files:**
- Create: `README.md`
- Create: `LICENSE` (GPLv3)

**Step 1: Write README**

```markdown
# AA Capture

A standalone Android app for capturing Android Auto protocol debug logs during
real-world sessions with production head units. Built for the
[open-android-auto](https://github.com/mrmees/open-android-auto) community.

## What It Does

- Captures filtered logcat output while Android Auto is running
- Selectable filter groups for different protocol areas (sensors, radio, navigation, etc.)
- Runs as a foreground service — works while AA has focus
- Event markers let you annotate what you were doing at specific times
- Exports captures as `.zip` (log + JSON metadata) via Android share sheet

## Setup

### One-Time Permission Grant

The app needs `READ_LOGS` permission to read system logcat. This requires a
one-time ADB command from a computer:

```bash
adb shell pm grant org.openauto.aacapture android.permission.READ_LOGS
```

This persists across reboots. You only need to do it once.

### Install

Build from source or grab an APK from
[Releases](https://github.com/mrmees/aa-logcat/releases).

## Usage

1. Open AA Capture
2. Select which log filter groups you want (defaults are pre-selected)
3. Add optional session notes (car model, wired/wireless, etc.)
4. Tap **Start Capture**
5. Connect to Android Auto and use features normally
6. Use the **Mark Event** notification button when switching activities
7. Tap **Stop** in the notification when done
8. Share the capture via the history list

## Filter Groups

| Group | What It Captures | Default |
|-------|-----------------|---------|
| Session & Control | Connection handshake, channel opens, shutdown | On |
| Sensors | Speed, fuel, GPS, night mode, gear, HVAC | On |
| Video | Video stream setup, focus, resolution | Off |
| Audio | Audio channel setup, focus transitions | Off |
| Radio | Radio channel, MediaBrowserService | On |
| Navigation | Turn events, nav focus, cluster nav data | On |
| Car Control | HVAC, door locks, vehicle properties | On |
| Media | Media metadata, browsing | Off |
| All (verbose) | Everything — large files, nothing missed | Off |

## Output Format

Each capture produces two files:

- `aa-capture_YYYY-MM-DD_HH-mm-ss.log` — raw logcat output
- `aa-capture_YYYY-MM-DD_HH-mm-ss.json` — session metadata

The JSON sidecar contains device info, AA version, selected filters, session
notes, timestamps, and event markers.

## Building

```bash
./gradlew assembleDebug
```

APK output: `app/build/outputs/apk/debug/app-debug.apk`

## Contributing

Captures from different car manufacturers are extremely valuable for protocol
research. If you capture data from a car, please share it with the community
via the open-android-auto project.

## License

GPLv3 — see [LICENSE](LICENSE).
```

**Step 2: Copy GPLv3 LICENSE**

```bash
# Use the LICENSE from open-android-auto or download standard GPLv3
cp ../LICENSE ./LICENSE
```

**Step 3: Full build verification**

```bash
./gradlew clean assembleDebug test
```
Expected: BUILD SUCCESSFUL, all tests pass

**Step 4: Commit**

```bash
git add README.md LICENSE
git commit -m "docs: add README with setup instructions and usage guide"
```

---

## Summary

| Task | What | Files | Tests |
|------|------|-------|-------|
| 1 | Project scaffold | 8+ files (gradle, manifest, app class, activity) | Build check |
| 2 | FilterGroup model | 2 files | 5 unit tests |
| 3 | CaptureSession model | 2 files | 2 unit tests |
| 4 | CaptureService | 1 file | Build check |
| 5 | PermissionChecker | 1 file | Build check |
| 6 | CaptureFileManager | 4 files | 4 unit tests |
| 7 | Compose UI | 5 files | Build check |
| 8 | README + LICENSE | 2 files | Full build + test |

**Total: ~20 files, 11 unit tests, 8 commits**
