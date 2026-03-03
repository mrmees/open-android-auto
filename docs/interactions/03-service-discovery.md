# 03 — Service Discovery

## Overview

After authentication, the HU and phone exchange capability advertisements. The HU sends a `ServiceDiscoveryResponse` describing all channels it supports (video, audio, sensors, input, etc.). The phone responds with a `ServiceDiscoveryRequest` containing device info. This exchange determines what features the session will use.

## Prerequisites

- TLS session established, device authenticated (from [02-version-ssl-auth](02-version-ssl-auth.md))
- All messages in this phase are encrypted (wrapped in TLS)
- Messages use `MessageType::Control` (not `Specific`)

## Sequence Diagram

```
Phone                                        Head Unit
  |                                             |
  |←── SERVICE_DISCOVERY_RESPONSE (0x0006) ──── |  HU advertises capabilities
  |                                             |
  |─── SERVICE_DISCOVERY_REQUEST (0x0005) ────→ |  Phone sends device info
  |                                             |
  |     Phone parses HU capabilities,           |
  |     determines which channels to open        |
  |                                             |
  |     → continues to channel opens (doc 04)    |
```

**Note:** Despite the names, the HU sends the Response first. The "response" is the HU responding to the implicit question "what do you support?" The phone's "request" is it providing its own info. This naming comes from aasdk and is confusing but established.

---

## Step 1: ServiceDiscoveryResponse (0x0006) — HU → Phone

This is the most important message the HU sends. It defines the entire session's capabilities.

### Message Structure

```protobuf
message ServiceDiscoveryResponse {
    repeated ChannelDescriptor channels = 1;     // What the HU supports
    optional string head_unit_name = 2;           // Display name
    optional string car_model = 3;
    optional string car_year = 4;
    optional string car_serial = 5;
    optional DriverPosition driver_position = 6;  // LEFT/RIGHT/CENTER
    optional string headunit_manufacturer = 7;
    optional string headunit_model = 8;
    optional string sw_build = 9;
    optional string sw_version = 10;
    optional bool can_play_native_media_during_vr = 11;
    optional int32 session_configuration = 13;
    optional string display_name = 14;
    optional bool probe_for_support = 15;
    optional HeadUnitInfo headunit_info = 17;     // Extended info
}
```

### Example (from our captured session)

```
head_unit_name: "OpenAuto Prodigy"
car_model: "Universal"
car_year: "2026"
car_serial: "e29d78b9cfad803b"
driver_position: LEFT (0)
headunit_manufacturer: "OpenAuto Project"
headunit_model: "Raspberry Pi 4"
sw_build: "b6a5995"
sw_version: "0.3.0"
can_play_native_media_during_vr: false
```

### Channel Descriptors

Each `ChannelDescriptor` advertises one channel the HU supports:

```protobuf
message ChannelDescriptor {
    optional int32 channel_id = 1;
    optional SensorChannel sensor_channel = 2;
    optional AVChannel av_channel = 3;
    optional InputChannel input_channel = 4;
    optional AVInputChannel av_input_channel = 5;
    optional BluetoothChannel bluetooth_channel = 6;
    optional RadioChannel radio_channel = 7;
    optional NavigationChannel navigation_channel = 8;
    optional MediaInfoChannel media_info_channel = 9;
    optional PhoneStatusChannel phone_status_channel = 10;
    optional MediaBrowserChannel media_browser_channel = 11;
    optional VendorExtensionChannel vendor_extension_channel = 12;
    optional NotificationChannel notification_channel = 13;
    optional WifiChannel wifi_channel = 14;
    optional CarControlChannel car_control_channel = 15;
    optional GenericNotificationChannel generic_notification_channel = 16;
    optional VoiceChannel voice_channel = 17;
}
```

Only ONE of the channel-type fields is set per descriptor. The `channel_id` determines the channel number used in frame headers.

### Minimum Viable HU Configuration

The phone enforces minimum requirements. An HU MUST advertise:

| Channel | ID | Why Required |
|---------|----|-------------|
| Video | 3 | Phone needs somewhere to send the projected display |
| Media Audio | 4 | Music/media playback |
| Input | 1 | Touch/button input (phone needs to know screen dimensions) |
| Sensor | 2 | At minimum: driving status + night mode |

**Mandatory sensor types:**
- `DRIVING_STATUS` (type 13) — always added by SDK even if not configured
- `NIGHT_DATA` (type 10) — strongly recommended; without it AA stays in day mode permanently

**Mandatory video resolution:**
- 480p (800x480) — always added by SDK even if higher resolutions are configured

### Channel Configuration Details

#### Video Channel (ch 3)

```protobuf
message AVChannel {
    optional MediaCodecType stream_type = 1;  // H264_BP=3, VP9=5, AV1=6, H265=7
    optional AudioStreamType audio_type = 2;  // (not used for video)
    repeated AudioConfig audio_configs = 3;   // (not used for video)
    repeated VideoConfig video_configs = 4;   // Resolution/fps/dpi options
    optional uint32 channel_id = 6;
    optional DisplayType display_type = 7;    // MAIN=0, CLUSTER=1, AUXILIARY=2
}

message VideoConfig {
    optional VideoResolution video_resolution = 1;  // 800x480=1, 1280x720=2, etc.
    optional VideoFPS video_fps = 2;                // _60=1, _30=2
    optional uint32 margin_width = 3;
    optional uint32 margin_height = 4;
    optional uint32 dpi = 5;
    optional uint32 additional_depth = 6;
    optional MediaCodecType codec = 10;             // Codec per-config
}
```

**Example (our HU):**
```
channel_id: 3
stream_type: H264_BP (3)
video_configs: [{
    video_resolution: VIDEO_800x480 (1)
    video_fps: _30 (2)
    margin_width: 0
    margin_height: 70      // 35px top + bottom black bars
    dpi: 140
}]
display_type: MAIN (0)
```

**Video resolution enum:**

| Value | Resolution | Orientation |
|-------|-----------|-------------|
| 1 | 800x480 | Landscape |
| 2 | 1280x720 | Landscape |
| 3 | 1920x1080 | Landscape |
| 4 | 2560x1440 | Landscape |
| 5 | 3840x2160 | Landscape |
| 6 | 720x1280 | Portrait |
| 7 | 1080x1920 | Portrait |
| 8 | 1440x2560 | Portrait |
| 9 | 2160x3840 | Portrait |

#### Audio Channels (ch 4, 5, 6)

Three separate audio channels, each with its own `ChannelDescriptor`:

```protobuf
message AudioConfig {
    required uint32 sample_rate = 1;   // Hz (48000 or 16000)
    required uint32 bit_depth = 2;     // 16
    required uint32 channel_count = 3; // 1 (mono) or 2 (stereo)
}
```

| Channel | ID | Audio Type | Typical Config |
|---------|-----|-----------|---------------|
| Media | 4 | MEDIA (3) | 48kHz, 16-bit, stereo |
| Speech/TTS | 5 | GUIDANCE (5) | 16kHz, 16-bit, mono |
| System/Notification | 6 | SYSTEM_AUDIO (1) | 16kHz, 16-bit, mono |

**Codec options:** PCM (1), AAC-LC (2), AAC-LC with ADTS (4). Phone has developer setting to prefer specific codec.

#### Microphone Input (ch 7)

```protobuf
message AVInputChannel {
    optional MediaCodecType stream_type = 1;  // PCM (1)
    optional AudioConfig audio_config = 2;    // ≥16kHz, mono
}
```

Phone will request mic open via `AVInputOpenRequest` when Google Assistant activates.

#### Sensor Channel (ch 2)

```protobuf
message SensorChannel {
    repeated SensorType sensor_types = 1;
}
```

**Sensor type enum (commonly advertised):**

| Value | Name | Data Message |
|-------|------|-------------|
| 1 | LOCATION | GPSLocation (lat, lng, accuracy, altitude, speed, bearing) |
| 3 | CAR_SPEED | Speed (int32, speed in m/s × 100) |
| 5 | ODOMETER | Odometer (total_mileage) |
| 6 | FUEL_LEVEL | FuelLevel (level, range, low_fuel) |
| 7 | PARKING_BRAKE | ParkingBrake (bool) |
| 8 | GEAR | Gear (enum) |
| 9 | DIAGNOSTICS | Diagnostics (bytes) |
| 10 | NIGHT_DATA | NightMode (is_night bool) |
| 11 | ENVIRONMENT | Environment (temp, pressure, rain) |
| 13 | DRIVING_STATUS | DrivingStatus (restrictions enum) |

**Our HU advertises:** `[NIGHT_DATA (10), DRIVING_STATUS (13), LOCATION (1)]`

#### Input Channel (ch 1)

```protobuf
message InputChannel {
    optional InputChannelConfig supported_keycodes = 1;
    optional InputChannelConfig touch_screen_config = 2;
    optional InputChannelConfig touch_pad_config = 3;
}
```

Touch screen config includes width/height matching the video resolution. Keycodes are Android `KeyEvent` codes — at minimum `HOME (3)`, `BACK (4)`, and `SEARCH (84)`.

**Our HU:** touch screen 800x410, keycodes [3, 4, 84]

#### Bluetooth Channel (ch 8)

```protobuf
message BluetoothChannel {
    optional string car_address = 1;         // HU's BT MAC
    repeated int32 pairing_methods = 2;      // [4] = numeric comparison
}
```

#### WiFi Channel (ch 14)

```protobuf
message WifiChannel {
    optional string ssid = 1;
}
```

---

## Step 2: ServiceDiscoveryRequest (0x0005) — Phone → HU

The phone sends its device info after receiving the HU's capabilities.

```protobuf
message ServiceDiscoveryRequest {
    optional bytes phone_icon_small = 1;     // 32x32 PNG
    optional bytes phone_icon_medium = 2;    // 64x64 PNG
    optional bytes phone_icon_large = 3;     // 128x128 PNG
    optional string device_name = 4;         // e.g. "Android"
    optional string device_brand = 5;        // e.g. "samsung SM-S938U"
    optional SessionInfo session_info = 6;   // UUID for session tracking
}
```

**Example (from our captured session):**
```
device_name: "Android"
device_brand: "samsung SM-S938U"
phone_icon_small: (32x32 green PNG, ~1KB)
phone_icon_medium: (64x64 green PNG, ~2KB)
phone_icon_large: (128x128 green PNG, ~5KB)
```

The HU can display these icons in its native UI to show the connected phone.

---

## What the Phone Does With HU Capabilities

After parsing the `ServiceDiscoveryResponse`, the phone:

1. **Selects video config** — picks the highest resolution/fps the phone can encode (usually constrained by hardware encoder capability)
2. **Configures audio pipelines** — sets up per-channel encoding based on sample rates
3. **Registers sensor listeners** — subscribes to advertised sensor types
4. **Evaluates features** — checks `CarModuleFeatures` for things like Coolwalk, multi-display, theming
5. **Begins channel opens** — see [04-channel-lifecycle](04-channel-lifecycle.md)

The phone is tolerant of missing optional channels. It logs warnings but doesn't fail if radio, notification, or other extended channels are absent.

---

## Error Handling

| Error | Detection | Impact |
|-------|-----------|--------|
| No video channel | Phone sends ShutdownRequest | Fatal — can't project without video |
| No 480p video config | SDK adds it automatically | Non-issue if using SDK correctly |
| No driving status sensor | SDK adds it automatically | Non-issue if using SDK correctly |
| No night mode sensor | AA stays in day mode permanently | UX issue, not fatal |
| No audio channels | Phone can't play media | Severely degraded but may still project |
| Invalid channel_id | Phone ignores the descriptor | Channel won't be opened |

## Log Tags

| Tag | What it shows |
|-----|--------------|
| `CAR.GAL.GAL.LITE` | "SDP_REQUEST_SENT", "SDP_RESPONSE_RECEIVED (9 services)" |
| `GH.ConnLoggerV2` | `SDP_REQUEST_SENT`, `SDP_RESPONSE_RECEIVED_WIFI` / `_USB` |
| `CAR.CLIENT` | CarModuleFeatures cache — what features the phone detected |
| `CAR.WM` | Display params after video config selection |
| `GH.ThemingManager` | Theme/palette version negotiation |

## Postcondition

At the end of this phase:
- Both sides know each other's capabilities
- Phone has selected video/audio configurations
- The session is ready for [channel opens](04-channel-lifecycle.md)

## References

- `oaa/control/ServiceDiscoveryRequestMessage.proto`
- `oaa/control/ServiceDiscoveryResponseMessage.proto`
- `oaa/control/ChannelDescriptorData.proto`
- `oaa/av/AVChannelData.proto`, `oaa/av/AVInputChannelData.proto`
- `oaa/sensor/SensorChannelData.proto`, `oaa/sensor/SensorTypeEnum.proto`
- `oaa/input/InputChannelData.proto`
- `oaa/bluetooth/BluetoothChannelData.proto`
- [`phone-side-debug.md`](../phone-side-debug.md) — Pi-Side Correlation section
- [`protocol-reference.md`](../protocol-reference.md) — full proto field catalog
