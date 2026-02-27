# AA Troubleshooting Runbook

Living troubleshooting guide for Android Auto head unit sessions. Covers tools, debug workflows, failure modes, and observations. Originally developed for a Raspberry Pi 4 head unit but applicable to any Linux-based AA implementation.

**Protocol reference:** `protocol-reference.md` (wire format, message IDs, channels)
**Phone-side logging:** `phone-side-debug.md` (logcat tags, dev settings, process architecture)
**Protocol cross-reference:** `protocol-cross-reference.md` (Sony HU + APK mapped together)

---

## Table of Contents

1. [Tool Inventory](#tool-inventory)
2. [Debug Workflows](#debug-workflows)
3. [Failure Mode Playbooks](#failure-mode-playbooks)
   - [Session Establishment Failures](#session-establishment-failures)
   - [Post-Handshake Stalls](#post-handshake-stalls)
   - [Video Issues](#video-issues)
   - [Audio Issues](#audio-issues)
   - [Touch Issues](#touch-issues)
   - [App Crash / Restart Issues](#app-crash--restart-issues)
4. [Protocol Logger Reference](#protocol-logger-reference)
5. [Phone-Side Debug Quick Reference](#phone-side-debug-quick-reference)
6. [Capture Data Index](#capture-data-index)
7. [Deployment Checklist](#deployment-checklist)
8. [Notes & Observations](#notes--observations)

---

## Tool Inventory

### Session Reset Script Pattern

A typical test reconnect sequence:
1. HU BT disconnect + phone WiFi off (via ADB)
2. Kill AA app on HU (graceful then SIGKILL)
3. Wait for clean state (configurable, default 10s)
4. Restart app on HU (waits 8s for RFCOMM listener registration)
5. BT connect with A2DP UUID (retry loop: 6 attempts, 10s timeout each, 5s between)
6. Wait 20s for AA session, validate with VIDEO frame count

**Common pitfalls:**
- `PHONE_MAC` must not be hardcoded — BT MACs randomize, discover dynamically via `bluetoothctl devices Paired`
- `svc wifi disable` via ADB is unreliable for dropping the phone's AA connection
- VIDEO grep validation patterns may differ between AA protocol libraries

### Protocol Capture

When capturing protocol data, collect:
- HU protocol log — TSV protocol messages from protocol logger
- Phone logcat (raw) — Full phone logcat dump
- Phone logcat (filtered) — Filtered for AA tags (CAR.*, GH.*, WIRELESS, PROJECTION, WPP)

### Timeline Merging

Merging HU protocol log + phone logcat into a single chronological timeline is invaluable for debugging.

**Approach:**
- HU log: TSV with float seconds (from protocol logger)
- Phone log: logcat timestamps (MM-DD HH:MM:SS.mmm)
- Alignment: find `VERSION_REQUEST` on HU side and `Socket connected` on phone side
- Clock offset calculated and applied to phone timestamps
- Output: markdown with `[HU]` / `[PHONE]` annotations, sorted by time

---

## Debug Workflows

### Workflow: "Something broke, where do I start?"

1. **Is the app actually running?**
   ```bash
   pgrep -f <your-aa-app>
   ps -o pid,lstart,cmd -p $(pgrep -f <your-aa-app>)
   ```

2. **What's on screen right now?** (Wayland example)
   ```bash
   WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000 grim /tmp/screenshot.png
   ```

3. **Are you looking at current logs?**
   Check your app's log output and protocol log.

4. **Check phone logcat (AA-filtered):**
   ```bash
   adb logcat -d | grep -E 'CAR\.|GH\.|WIRELESS|PROJECTION|WPP' | tail -50
   ```

5. **If needed, do a full capture** of both HU and phone logs for timeline analysis.

### Workflow: "I changed code, now test it"

1. **Build locally (sanity check):**
   ```bash
   cd build && cmake --build . -j$(nproc) && ctest --output-on-failure
   ```

2. **Deploy to target** (source only, never cross-architecture binaries)
   **WARNING:** Never rsync build artifacts from a different architecture — x86 .so files will overwrite ARM64 builds.

3. **Build on target:**
   ```bash
   cd build && cmake --build . -j3
   ```

4. **Restart the app** and reconnect the phone.

### Workflow: "I need a screenshot of the HU display"

For Wayland-based systems:
```bash
WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000 grim /tmp/screenshot.png
```

---

## Failure Mode Playbooks

> **Step 0 for ALL failure modes:** Confirm the app is running and visible first.

### Session Establishment Failures

**Symptom:** Phone never connects to AA. No protocol log entries. App running but idle.

**Check BT pairing:**
```bash
# Find paired phone (don't hardcode MAC — BT MACs randomize)
bluetoothctl devices Paired

# Check specific device info
bluetoothctl info <PHONE_MAC>
```
- Look for `Paired: yes`, `Connected: yes`
- If not paired: `bluetoothctl pair <PHONE_MAC>`
- If "key-missing" error: phone BT MAC changed (randomization, factory reset). Remove old pairing and re-pair.

**Check WiFi AP:**
```bash
ip addr show wlan0
```
- Must show the expected AP IP (e.g., `10.0.0.1`) — if missing, the WiFi AP IP didn't survive reboot
- Check hostapd: `systemctl status hostapd`
- WiFi SSID/password in app config must match `hostapd.conf` exactly

**Check RFCOMM listener:**
```bash
ss -tlnp | grep <your-aa-app>
```
- App needs ~8s after launch to register RFCOMM listener
- If no listener: check app log for BT initialization errors

**Check phone side:**
- Phone Settings → Connected devices → Connection preferences → Android Auto
- Should show your HU name with "Wireless Android Auto available"
- If not listed: phone hasn't discovered the HU via BT. Check BT pairing.

### Post-Handshake Stalls

**Symptom:** Protocol log shows VERSION → TLS → AUTH → SERVICE_DISCOVERY, channels open, but phone won't start video projection.

This was a **known blocker under the old aasdk stack** (as of 2026-02-23). The phone entered `STATE_WAITING_FOR_USER_AUTHORIZATION` and never progressed. Status under open-androidauto is unknown — needs revalidation.

**What to check in protocol log:**
1. All 9 channels should open (3,4,5,6,1,2,8,14,7)
2. `AV_SETUP_REQUEST` should arrive for video/audio channels
3. `AV_SETUP_RESPONSE` should be sent for each
4. `SENSOR_START_REQUEST` × 3 should arrive and be responded to
5. `INPUT_BINDING_REQUEST` should arrive
6. Pings should be flowing (session alive)

**What to check in phone logcat:**
```bash
./platform-tools/adb logcat -d | grep -E 'AUTHORIZATION|WirelessStartup|FirstActivity|consent'
```
- `STATE_WAITING_FOR_USER_AUTHORIZATION` — phone waiting for user to accept
- `AUTHORIZATION_COMPLETE` — fires but setup may tear down anyway
- `sendSensorRequest timed-out` — likely symptom, not cause
- No consent dialog appearing = the phone's AA UI never fully launches

**Known observations (from aasdk era — revalidate):**
- Phone "Connected vehicles" page shows: Accepted=None, Rejected=None
- `WirelessStartupActivity` and `FirstActivityImpl` launch then immediately self-destruct
- Phone shows "Connecting to Android Auto" notification indefinitely

### Video Issues

**Symptom:** AA session active (pings flowing) but no video on display.

**Black screen — check decoder pixel format:**
- Some phones output `AV_PIX_FMT_YUVJ420P` (fmt=12) instead of `AV_PIX_FMT_YUV420P` (fmt=0)
- Must accept both formats or frames are silently discarded
- Moto G Play 2024 → YUVJ420P; Samsung S25 Ultra → YUV420P

**No video frames at all:**
1. Check `VIDEO_FOCUS_INDICATION(FOCUSED)` was sent after `AV_SETUP_RESPONSE`
2. Check `max_unacked` in video flow control (should be ≥10)
3. Check protocol log for `AV_MEDIA_INDICATION` on channel 3 (video)
4. Verify video resolution config: 720p is default, 1080p works but may need more CPU

**Choppy/stuttering video:**
- FFmpeg `thread_count` must be 1 for real-time AA decode — `thread_count=2` causes internal buffering that breaks small P-frame phones
- Check CPU usage: `top -bn1 | head -5`

**Video focus gotcha:**
- Phone aggressively re-requests `VIDEO_FOCUS_INDICATION(FOCUSED)`
- Sending `UNFOCUSED` is treated as an exit signal — don't suppress focus requests

### Audio Issues

**Symptom:** AA active with video but no sound, or choppy audio.

**Check PipeWire (if using PipeWire audio):**
```bash
pw-cli ls Node        # list audio nodes
wpctl status          # WirePlumber status
```

**Check audio device config:**
- App config must specify valid PipeWire device
- "Default" device label shows first registry device, not PipeWire's actual default
- Audio device switching requires app restart

**Choppy audio:**
- PipeWire `d.chunk->size` must report actual bytes read, not `maxSize` with zero-fill
- Check ring buffer utilization in audio service

**Audio channels:**
| Channel | Content | Sample Rate |
|---------|---------|-------------|
| 4 | Media (music) | 48kHz stereo |
| 5 | Speech (TTS nav) | 48kHz mono (was 16kHz, upgraded in probe-2) |
| 6 | System sounds | 16kHz mono |
| 7 | Microphone input | ≥16kHz mono (HU → phone) |

### Touch Issues

**Symptom:** Touch doesn't work during AA, or touches land in wrong place.

**EVIOCGRAB state:**
- During AA: evdev device should be grabbed (touch routed to AA, not Wayland)
- When AA disconnects: ungrab must happen (return touch to Wayland/libinput)
- Permanent grab = launcher UI unresponsive
- Check app log for EVIOCGRAB/UNGRAB messages around AA connect/disconnect

**Touch misalignment:**
- `touch_screen_config` MUST be set to video resolution (e.g., 1280x720), NOT physical display resolution
- Touch coordinates are sent in video resolution space
- On Linux, evdev range is typically 0-4095, mapped to the video resolution

**Touch device not found:**
- Your AA app should scan for `INPUT_PROP_DIRECT` devices on startup
- Example: DFRobot USB Multi Touch (vendor 3343:5710, 10 points, MT Type B)
- Check: `cat /proc/bus/input/devices`

**Sidebar touch during AA:**
- UI framework touch handlers don't work during EVIOCGRAB — visual only
- Sidebar touch handled via evdev hit zones in the touch reader
- Sidebar config changes require app restart (margins locked at AA session start)

### App Crash / Restart Issues

**Symptom:** App crashes or won't restart cleanly.

**Port bind failure after restart:**
- TCP sockets may not set `SOCK_CLOEXEC` — forked processes (e.g. spawned restart process) inherit the acceptor FD, preventing port rebind
- Fix: `fcntl(fd, F_SETFD, FD_CLOEXEC)` after socket open
- Or: `SO_REUSEADDR` must be set before bind (not after)

**UI view crash during navigation:**
- Destroying a UI view from within its own event handler can crash (click handler still on stack when view is destroyed)
- Fix: defer the view change to the next event loop iteration

**Phone won't reconnect after restart:**
- Phone doesn't cleanly reconnect after app restart
- User must manually cycle BT/WiFi on phone
- TODO: Find reliable method to drop/re-establish AA connection on phone side

**`pkill` silently fails:**
- Process names >15 chars truncated in procfs
- Must use `pkill -f '<full-binary-path>'` (full command match)

---

## Protocol Logger Reference

The ProtocolLogger hooks into the Messenger layer and logs every protobuf message exchanged.

**Output location:** Typically a temp file (e.g., `/tmp/protocol.log`)

**Format:** TSV (tab-separated values)
```
TIME    SOURCE          CHANNEL    MESSAGE              PAYLOAD
0.000   HU->Phone       0          VERSION_REQUEST      major=1 minor=7
0.015   Phone->HU       0          VERSION_RESPONSE     major=1 minor=7 status=MATCH
...
```

**Fields:**
- `TIME` — seconds since session start (float)
- `SOURCE` — `HU->Phone` or `Phone->HU`
- `CHANNEL` — channel ID (0-14)
- `MESSAGE` — human-readable message name
- `PAYLOAD` — protobuf summary (truncated to 500 chars for AV data)

**Key messages to look for:**
- `VERSION_REQUEST/RESPONSE` — protocol version negotiation
- `SSL_HANDSHAKE` — TLS setup (multiple rounds)
- `AUTH_COMPLETE` — authentication done
- `SERVICE_DISCOVERY_REQUEST/RESPONSE` — capability exchange
- `CHANNEL_OPEN_REQUEST/RESPONSE` — per-channel setup
- `AV_SETUP_REQUEST/RESPONSE` — audio/video stream config
- `VIDEO_FOCUS_INDICATION` — video projection state
- `PING_REQUEST/RESPONSE` — keepalive (should be regular)
- `SHUTDOWN_REQUEST/RESPONSE` — graceful disconnect

---

## Phone-Side Debug Quick Reference

Full details in `phone-side-debug.md`. Key points:

**Enable AA Developer Settings:**
1. Phone Settings → Apps → Android Auto
2. Tap version number 10 times
3. Three-dot menu → Developer Settings appears

**Useful dev toggles:**
- Force debug logging (verbose protocol logs)
- Save video/audio/mic capture to disk
- Audio codec selector (PCM vs AAC-LC)

**Key logcat tags:**

| Tag | What it shows |
|-----|---------------|
| `CAR.GAL.LITE` | Core protocol (GAL) |
| `CAR.BT.LITE` | Bluetooth state |
| `GH.WPP.CONN` / `GH.WPP.TCP` | WiFi Projection Protocol |
| `GH.WIRELESS.SETUP` | Wireless setup state machine |
| `GH.ConnLoggerV2` | Session event timeline |
| `GH.CarClientManager` | Car client lifecycle |

**Phone AA processes:**
- `:projection` — main projection UI
- `:car` — protocol engine
- `:shared` — shared services
- `:watchdog` — health monitoring
- `:provider` — content provider

**Filtering:**
```bash
# Live AA-only logcat
./platform-tools/adb logcat | grep -E 'CAR\.|GH\.|WIRELESS|PROJECTION|WPP'

# Dump and filter
./platform-tools/adb logcat -d | grep -E 'CAR\.|GH\.|WIRELESS|PROJECTION|WPP'

# Clear before test
./platform-tools/adb logcat -c
```

---

## Capture Data Index

**HISTORICAL — captured under old aasdk stack.** Protocol behavior at the wire level should still be valid, but HU-side log formats and message names may differ between AA library implementations.

Each capture directory typically contains:
- `protocol.log` — TSV protocol messages
- `phone-logcat-raw.log` — Full logcat
- `phone-logcat.log` — AA-filtered logcat
- `findings.md` (probes only) — Observations and conclusions
- `timeline.md` (if merged) — Chronological merged view

### Example Probe Results

| Probe | What Was Tested | Outcome |
|-------|-----------------|---------|
| Protocol v1.7 negotiation | Bumped advertised version to 1.7 | Phone responds v1.7, stores HU version |
| 48kHz speech audio | Upgraded TTS from 16kHz to 48kHz | Works — frame size doubles, phone captures at 48kHz |
| Night mode sensor push | Sent night mode sensor event | Phone correctly reads sensor event |
| Material You (theme v2) | Advertised palette version 2 | **BLOCKED** — required field number undiscovered |
| hide_clock + extra sensors | COMPASS/ACCEL/GYRO sensors | hide_clock dead; phone requests COMPASS+ACCEL, ignores GYRO |
| 1920x1080 video | Advertised 1080p resolution | Works — phone renders full res, triggers xlrg layout |

---

## Deployment Checklist

Before testing changes on target hardware:

- [ ] Local build passes (`cmake --build . -j$(nproc)`)
- [ ] Unit tests pass (`ctest --output-on-failure`)
- [ ] Deploy **source files only** (never cross-architecture build artifacts or `.so` files)
- [ ] Target build succeeds
- [ ] Old app instance killed before launching new one
- [ ] 8s wait after launch before attempting BT connect (RFCOMM registration time)
- [ ] WiFi AP up (`ip addr show wlan0` shows expected AP IP)
- [ ] Phone BT paired and discoverable

---

## Notes & Observations

*This section is for observations, hunches, and things noticed during testing that aren't captured elsewhere. Add freely.*

### Authorization State Issue (2026-02-23, aasdk era — needs revalidation)

Under the old aasdk stack, the phone completed the entire handshake (VERSION → TLS → AUTH → SERVICE_DISCOVERY → all channels open → AV setup → sensors → input binding → WiFi credentials → pings flowing) but entered `STATE_WAITING_FOR_USER_AUTHORIZATION` and never progressed to video projection.

**What we observed (aasdk stack):**
- `AUTHORIZATION_COMPLETE` fires in logcat, but BT FSM enters auth-wait state AFTER
- `WirelessStartupActivity` and `FirstActivityImpl` launch then immediately self-destruct
- No consent dialog ever appears for user to tap Accept
- Phone "Connected vehicles" shows: Accepted=None, Rejected=None
- `sendSensorRequest timed-out` × 3 in phone logcat (likely symptom, not cause)

**Protocol fixes applied during aasdk Pi validation:**
- MessageType: ch0 → Specific(0x00), non-zero → Control(0x04)
- AASession: auto-respond audio/nav focus, intercept CHANNEL_OPEN_REQUEST on non-zero channels
- VideoChannelHandler: VIDEO_FOCUS_INDICATION(FOCUSED) after AV_SETUP_RESPONSE, max_unacked=10
- TCPTransport: hex dump logging for writes

**Open questions (carry forward to open-androidauto testing):**
- Is this a cert/identity issue? Phone may not trust the HU certificate.
- Is the phone expecting something in SERVICE_DISCOVERY_RESPONSE that we're not providing?
- Could this be an Android version-specific behavior? (Test phone: Moto G Play 2024, Android 14)
- Does DHU (Desktop Head Unit, Google's reference tool, USB-only) exhibit the same state machine? Worth comparing.

---

*Last updated: 2026-02-23*
