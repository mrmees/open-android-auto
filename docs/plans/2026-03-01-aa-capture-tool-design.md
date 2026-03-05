# AA Capture Tool — Design Document

**Date:** 2026-03-01
**Status:** Approved
**Repo:** New standalone repo (`aa-logcat` or similar)

## Purpose

A standalone Android app that captures Android Auto protocol-relevant logcat output during real-world sessions with production head units. Designed for the open-android-auto community to collect protocol data from cars they don't own (dealership visits, rentals, friends' cars) without needing root, a laptop, or any hardware beyond the phone itself.

The captured data feeds into our existing analysis pipeline for proto discovery, sensor verification, and channel mapping.

## Constraints

- **Unrooted phone** — the only elevated permission is `READ_LOGS`, granted once via ADB at home
- **No laptop required** — the app is fully self-contained on the phone
- **Phone is busy running AA** — capture must work while AA has focus via foreground service
- **Community-facing** — needs clear setup instructions and a polished-enough UX

## App Identity

| Field | Value |
|-------|-------|
| App name | AA Capture |
| Package | `org.openauto.aacapture` |
| Repo | New standalone GitHub repo |
| Stack | Kotlin, Jetpack Compose, Material 3 |
| Min SDK | 29 (Android 10) |
| Target SDK | 35 |
| License | GPLv3 |

## Architecture

```
MainActivity (Compose)
├── PermissionCheck — READ_LOGS status + ADB instructions
├── FilterSelector — checkbox grid of filter groups
├── CaptureControls — start/stop, session notes input
├── LiveStatus — line count, elapsed time, file size
└── CaptureList — past captures with share/delete

CaptureService (Foreground Service)
├── runs logcat process via Runtime.exec()
├── writes to file on IO dispatcher
├── inserts marker lines on notification action
└── builds JSON sidecar on stop

CaptureSession (data class)
├── metadata (device, AA version, filters, notes)
├── markers list
└── file paths (log + json)

FilterGroups (hardcoded object)
└── list of FilterGroup(name, tags[], enabledByDefault)
```

### Intentional omissions

- No database — file list from scanning captures directory
- No dependency injection — small app, not needed
- No network — sharing uses Android's built-in share sheet
- No background capture — foreground service only, explicit start/stop
- No real-time parsing — post-processing happens on PC with existing Python tools

## Filter Groups

Users select which log tag groups to capture before starting a session. Defaults are pre-selected to cover the most-needed protocol areas.

| Filter Group | Tags | Default | Purpose |
|---|---|---|---|
| Session & Control | `AASession`, `AATransport`, `CarLifecycle` | On | Connection handshake, channel opens, shutdown |
| Sensors | `CAR.SENSOR.LITE`, `CAR.SENSOR` | On | Speed, fuel, GPS, night mode, gear, HVAC |
| Video | `CAR.GAL.VIDEO` | Off | Video stream setup, focus, resolution |
| Audio | `CAR.AUDIO`, `AudioFocus` | Off | Audio channel setup, focus transitions |
| Radio | `CAR.GAL.RADIO-EP`, `GH.Radio`, `CAR.RADIO` | On | Radio channel, MediaBrowserService |
| Navigation | `GH.NDirector`, `NAV` | On | Turn events, nav focus, cluster nav data |
| Car Control | `CAR.GAL.CAR_CONTROL` | On | HVAC, door locks, vehicle properties |
| Media | `GH.MediaActiveContrConn`, `MediaBrowser` | Off | Media metadata, browsing |
| All (verbose) | `*:V` | Off | Everything — large files, nothing missed |

Tags are hardcoded in v1; new tags ship with app updates as we discover them.

## Capture Flow

### Pre-capture

1. App checks `READ_LOGS` permission, shows ADB grant instructions if missing
2. User selects filter groups via checkboxes
3. User enters optional session notes (e.g., "2025 Tucson Hybrid, wireless AA")
4. Taps "Start Capture"

### During capture

- Foreground service starts with persistent notification
- Notification actions: **Mark Event** and **Stop**
- Mark Event inserts a timestamped marker into the log file (`===== MARKER 14:32:05 =====`)
- Main UI shows: live line count, elapsed time, file size
- Logcat runs filtered by selected tags, writes directly to file
- Service survives AA taking focus, screen off, etc.

### Post-capture

- Stop writes a JSON sidecar alongside the log file:

```json
{
  "device": "Pixel 7",
  "android_version": "14",
  "aa_version": "16.1.xxxxx",
  "filters": ["sensors", "radio", "car_control"],
  "notes": "2025 Tucson Hybrid, wireless AA",
  "start_time": "2026-03-01T14:30:00Z",
  "end_time": "2026-03-01T15:15:00Z",
  "markers": ["14:32:05", "14:38:12", "14:45:30"],
  "line_count": 48230,
  "file_size_bytes": 2841600
}
```

- Files stored in `Android/data/org.openauto.aacapture/files/captures/`
- Past captures listed with date, duration, size, notes preview
- Share button zips `.log` + `.json` and opens Android share sheet
- Delete button for cleanup

### Auto-detected metadata

- AA version: from `PackageManager` for `com.google.android.projection.gearhead`
- Device model: `Build.MODEL`
- Android version: `Build.VERSION.RELEASE`
- SDK level: `Build.VERSION.SDK_INT`

## Permissions

| Permission | Source | Purpose |
|---|---|---|
| `READ_LOGS` | ADB grant (one-time) | Read system logcat |
| `FOREGROUND_SERVICE` | Manifest | Keep capture alive |
| `POST_NOTIFICATIONS` | Runtime (API 33+) | Foreground service notification |

## Setup Instructions (for README)

```bash
# One-time setup: connect phone via USB, run:
adb shell pm grant org.openauto.aacapture android.permission.READ_LOGS

# That's it. Permission persists across reboots.
# Now open AA Capture, select your filters, and tap Start before connecting to a car.
```
