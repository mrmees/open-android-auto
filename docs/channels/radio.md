# Radio Channel

## Overview

The radio channel (GAL Service 15, log tag `CAR.GAL.RADIO-EP`) enables the phone to control the car's broadcast radio tuner. The HU reports its radio hardware capabilities via the SDP; the phone provides the UI, station lists, metadata display, and user control.

The radio pipeline on the phone: HU advertises `RadioChannel` config in SDP with `RadioStation` entries describing tuner capabilities -> `ibf.java` (`CAR.GAL.RADIO-EP` endpoint) receives Phone->HU messages and dispatches via Handler to -> `hlr.java` (`CAR.RADIO` service) which manages radio state and sends HU->Phone commands -> `RadioMediaBrowserService` (`GH.Radio`) exposes the radio as an Android MediaBrowser for the projection UI.

**Supported bands:** AM, FM (with optional HD Radio / RDS), and DAB/DAB+/DMB. There is **no SiriusXM/satellite radio support** -- the channel covers terrestrial broadcast only.

---

## Architecture

| Component | 16.2 Class | Log Tag | Role |
|-----------|-----------|---------|------|
| Endpoint Handler | `ibf.java` | `CAR.GAL.RADIO-EP` | Wire protocol: receives Phone->HU messages, dispatches to service |
| Radio Service | `hlr.java` | `CAR.RADIO` | Business logic: manages state, sends HU->Phone messages |
| Handler Callback | `ibd.java` | -- | Routes handler messages (1-5) to service callbacks |
| MediaBrowserService | `RadioMediaBrowserService.java` | `GH.Radio` | Exposes radio as Android MediaBrowser for UI integration |
| ICarRadio (AIDL) | `psn.java` / `psm.java` | -- | `com.google.android.gms.car.ICarRadio` |
| ICarRadioCallback (AIDL) | `psq.java` / `psp.java` | -- | `com.google.android.gms.car.ICarRadioCallback` |
| Manager | `pmm.java` | `CAR.RADIO` | Client-side proxy for ICarRadio |

---

## Message Catalog

### Phone -> HU (5 messages, received by `ibf.mo18864a()`)

| Msg ID | Direction | Proto Class (16.2) | Name | Purpose |
|--------|-----------|-------------------|------|---------|
| 0x801A | Phone -> HU | `wam` | RadioProgramListNotification | Full list of available stations |
| 0x801B | Phone -> HU | `wal` | RadioProgramInfoNotification | Current station info, mute state, audio focus |
| 0x801D | Phone -> HU | `wah` | RadioMuteResponse | Confirms mute state change |
| 0x801F | Phone -> HU | `wau` | RadioTuneResponse | Tune result status |
| 0x8020 | Phone -> HU | `wad` | RadioFavoriteListNotification | Full favorites list |

### HU -> Phone (5 messages, sent by `hlr.java`)

| Msg ID | Direction | Proto Class (16.2) | Name | Purpose |
|--------|-----------|-------------------|------|---------|
| 0x801C | HU -> Phone | `wag` | RadioMuteRequest | Mute/unmute radio |
| 0x801E | HU -> Phone | `wat` | RadioTuneRequest | Tune to specific station by selector |
| 0x8021 | HU -> Phone | `waq` | RadioFavoriteToggleRequest | Toggle current station as favorite |
| 0x8022 | HU -> Phone | `war` | RadioTuneDirectionRequest | Seek up/down to next station |
| 0x8023 | HU -> Phone | `wac` | RadioCustomActionRequest | Forward MediaBrowser custom action |

**Note:** Message IDs 0x801C (32796) and 0x801E (32798) fall through to the default case in the endpoint handler switch -- they are HU->Phone messages and are never received by the handler.

---

## RadioProgramListNotification (0x801A)

Full list of available radio programs sent by the phone on connection and when the station list changes.

```protobuf
message RadioProgramListNotification {  // APK class: wam (16.2), wau (16.1)
    repeated RadioProgramInfo programs = 1;
}
```

Handler dispatches as `what=4` with `List<RadioProgramInfo>`.

---

## RadioProgramInfoNotification (0x801B)

Current station update. Sent when the station changes, metadata updates, or mute/focus state changes.

```protobuf
message RadioProgramInfoNotification {  // APK class: wal (16.2), wat (16.1)
    optional RadioProgramInfo program_info = 1;
    optional bool is_muted = 2;
    optional bool has_audio_focus = 3;
}
```

Handler dispatches as `what=3`, `arg1=is_muted`, `arg2=has_audio_focus`, `obj=RadioProgramInfo`.

---

## RadioMuteRequest (0x801C)

HU tells the phone to mute or unmute the radio.

```protobuf
message RadioMuteRequest {  // APK class: wag (16.2), wao (16.1)
    optional bool mute = 1;
}
```

Sent by `hlr.mo18788h(boolean z)`.

---

## RadioMuteResponse (0x801D)

Phone confirms the new mute state.

```protobuf
message RadioMuteResponse {  // APK class: wah (16.2), wap (16.1)
    optional bool is_muted = 1;
}
```

Handler dispatches as `what=1`, `obj=Boolean(is_muted)`.

---

## RadioTuneRequest (0x801E)

HU requests tuning to a specific station identified by a program selector.

```protobuf
message RadioTuneRequest {  // APK class: wat (16.2), wbc (16.1)
    optional RadioProgramSelector program_selector = 1;
}
```

Sent by `hlr.mo18794o(RadioProgramSelector)`. Builds a `RadioProgramSelector` with primary identifier (type + frequency/station ID) and optional secondary identifiers, wraps in `RadioTuneRequest`.

---

## RadioTuneResponse (0x801F)

Phone reports the result of a tune operation.

```protobuf
message RadioTuneResponse {  // APK class: wau (16.2), wbd (16.1)
    optional RadioTuneStatus status = 1;
}
```

Handler dispatches as `what=2`, `arg1=status`. If the status value is 0 (unset), it defaults to 1 (SUCCESS).

---

## RadioFavoriteListNotification (0x8020)

Full list of favorited stations. Sent on connection and whenever favorites change.

```protobuf
message RadioFavoriteListNotification {  // APK class: wad (16.2), wal (16.1)
    repeated RadioProgramInfo favorites = 1;
}
```

Handler dispatches as `what=5` with `List<RadioProgramInfo>`.

---

## RadioFavoriteToggleRequest (0x8021)

HU tells the phone to add or remove the **currently tuned** station from favorites.

```protobuf
message RadioFavoriteToggleRequest {  // APK class: waq (16.2), waz (16.1)
    optional bool is_favorite = 1;
}
```

Sent by `hlr.mo18792l(boolean z)`.

---

## RadioTuneDirectionRequest (0x8022)

HU requests a seek (scan) in a given direction.

```protobuf
message RadioTuneDirectionRequest {  // APK class: war (16.2), wba (16.1)
    optional RadioTuneDirection direction = 1;
}
```

Sent by `hlr.mo18793n(int i)`.

---

## RadioCustomActionRequest (0x8023)

HU forwards a MediaBrowser custom action to the phone's radio service. This was **added in 16.2** and is not present in the 16.1 proto definitions.

```protobuf
message RadioCustomActionRequest {  // APK class: wac (16.2)
    optional string action_id = 1;
}
```

Sent by `hlr.mo18789i(String str)`. Called from `RadioMediaBrowserService.mo11226m()` which logs `"onCustomAction()"`. The `action_id` is a string identifying the action (e.g., a band scan action from `RadioConfiguration.bandScanAction`).

---

## Sub-Messages

### RadioProgramInfo

A radio program entry combining a selector with metadata.

```protobuf
message RadioProgramInfo {  // APK class: wak (16.2), was (16.1)
    optional RadioProgramSelector program_selector = 1;
    optional RadioMetadata metadata = 2;
}
```

### RadioProgramSelector

Selects a program via a primary identifier and optional secondary identifiers.

```protobuf
message RadioProgramSelector {  // APK class: wan (16.2), wav (16.1)
    optional RadioProgramIdentifier primary_identifier = 1;
    repeated RadioProgramIdentifier secondary_identifiers = 2;
}
```

### RadioProgramIdentifier

Identifies a specific radio program/station by type and value.

```protobuf
message RadioProgramIdentifier {  // APK class: waj (16.2), war (16.1)
    optional RadioIdentifierType type = 1;
    optional uint64 value = 2;  // frequency in kHz for AM/FM, or station ID for HD/DAB
}
```

### RadioMetadata

Full station metadata including HD Radio and DAB fields.

```protobuf
message RadioMetadata {  // APK class: waf (16.2), wan (16.1)
    optional string station_name = 1;          // station call sign
    optional string station_name_short = 2;    // abbreviated name
    optional string station_name_long = 3;     // full name
    optional RadioProgramType program_type = 4; // RDS PTY or ITU program type
    optional RadioImage station_icon = 5;      // station logo (raw bytes)
    optional RadioSongMetadata song_metadata = 6; // currently playing song
    optional string message = 7;               // RDS RadioText / station text
    optional string service_name = 8;          // DAB service name
    optional uint32 hd_sub_channels_available = 9; // number of HD Radio subchannels
    optional bool hd_signal_acquired = 10;     // HD Radio signal locked
    optional bool hd_audio_acquired = 11;      // HD Radio audio decoding
    optional string dab_component_name = 12;   // DAB component name
    optional bool dts_autostage_enriched = 13; // DTS AutoStage audio enhancement flag
}
```

### RadioSongMetadata

Currently playing song information.

```protobuf
message RadioSongMetadata {  // APK class: was (16.2), wbb (16.1)
    optional string title = 1;
    optional string artist = 2;
    optional string album = 3;
    optional string genre = 4;
    optional RadioImage album_art = 5;     // raw image bytes
    optional uint64 duration_seconds = 6;
}
```

### RadioImage

Station icon or album art image data.

```protobuf
message RadioImage {  // APK class: wao (16.2), wam (16.1)
    optional bytes image_data = 1;
}
```

### RadioProgramType

Program type classification using RDS PTY or ITU schema.

```protobuf
message RadioProgramType {  // APK class: waw (16.2)
    optional RadioProgramTypeSchema schema = 1;  // 1=RDS_PTY, 2=ITU
    optional uint32 code = 2;                    // program type code (0-31)
}
```

---

## Enums

### RadioIdentifierType

Identifies the type of radio program selector.

| Value | Name | Used For |
|-------|------|----------|
| 0 | IDENTIFIER_TYPE_INVALID | Default/error |
| 1 | IDENTIFIER_TYPE_AMFM_FREQUENCY | AM/FM tuning by frequency (kHz) |
| 2 | IDENTIFIER_TYPE_RDS_PI | RDS Program Identification code |
| 3 | IDENTIFIER_TYPE_HD_STATION_ID_EXT | HD Radio extended station ID (encodes subchannel in bits 32-33) |
| 4 | IDENTIFIER_TYPE_HD_STATION_NAME | HD Radio station name lookup |
| 5 | IDENTIFIER_TYPE_DAB_DMB_SID_EXT | DAB/DMB Service ID extended |
| 6 | IDENTIFIER_TYPE_DAB_ENSEMBLE | DAB ensemble identifier |
| 7 | IDENTIFIER_TYPE_DAB_SCID | DAB Service Component ID |
| 8 | IDENTIFIER_TYPE_DAB_FREQUENCY | DAB frequency in kHz |
| 9 | IDENTIFIER_TYPE_DAB_SID_EXT | DAB Service ID extended (alternate) |

### RadioTuneStatus

| Value | Name |
|-------|------|
| 0 | RADIO_TUNE_STATUS_UNKNOWN |
| 1 | RADIO_TUNE_STATUS_SUCCESS |
| 2 | RADIO_TUNE_STATUS_FAILURE |
| 3 | RADIO_TUNE_STATUS_TIMEOUT |
| 4 | RADIO_TUNE_STATUS_CANCELLED |

### RadioTuneDirection

| Value | Name |
|-------|------|
| 0 | RADIO_TUNE_DIRECTION_UNKNOWN |
| 1 | RADIO_TUNE_DIRECTION_UP |
| 2 | RADIO_TUNE_DIRECTION_DOWN |

### RadioBandType

| Value | Name | Notes |
|-------|------|-------|
| 0 | BAND_TYPE_UNKNOWN | |
| 1 | BAND_TYPE_AM | |
| 2 | BAND_TYPE_FM | |
| 3 | BAND_TYPE_DAB | DAB/DAB+/DMB digital radio |

### RadioCodecType

| Value | Name |
|-------|------|
| 0 | RADIO_CODEC_UNKNOWN |
| 1 | RADIO_CODEC_ANALOG |
| 2 | RADIO_CODEC_HD |
| 3 | RADIO_CODEC_DAB |
| 4 | RADIO_CODEC_DAB_PLUS |
| 5 | RADIO_CODEC_DMB |

### RadioProgramTypeSchema

| Value | Name | Notes |
|-------|------|-------|
| 0 | SCHEMA_UNKNOWN | |
| 1 | SCHEMA_RDS_PTY | European RDS standard, 31 program types (News through Alarm) |
| 2 | SCHEMA_ITU | North American RBDS, 31 program types (News through Emergency) |

### RadioRegion

| Value | Name |
|-------|------|
| 0 | REGION_UNKNOWN |
| 1 | REGION_ITU_1 |

---

## Frequency Ranges and Band Classification

Frequency classification logic from `ljg.java`:

| Band | Range | Unit | Display Format |
|------|-------|------|----------------|
| AM | 150 < freq <= 30,000 | kHz | `"%d kHz"` |
| FM | 60,000 < freq < 110,000 | kHz | `"%.1f MHz"` (freq/1000) |
| DAB | Per DAB_FREQUENCY identifier | kHz | `"%.1f MHz"` (freq/1000) |

### HD Radio Subchannel Decoding

HD Radio station ID extended (identifier type 3) encodes subchannel index in bits 32-33 and frequency in bits 36+:

```java
int subchannel = (int)((value >>> 32) & 3);     // 0-3, displayed as subchannel+1
long freq = (value >>> 36) & 262143;             // 18-bit frequency in kHz
```

---

## Radio State Machine

The radio state is managed in `hlr.java` with these cached fields:

| Field | Type | Purpose |
|-------|------|---------|
| `f34243f` | Boolean | Mute state (from RadioProgramInfoNotification and RadioMuteResponse) |
| `f34244g` | RadioProgramInfo | Current station (from RadioProgramInfoNotification) |
| `f34245h` | List | Program list (from RadioProgramListNotification) |
| `f34246i` | List | Favorites list (from RadioFavoriteListNotification) |
| `f34247j` | Boolean | Audio focus (from RadioProgramInfoNotification) |
| `f34251n` | RadioConfiguration | Band config (parsed from SDR during channel setup) |

### Tune Flow

1. HU sends `RadioTuneRequest` (0x801E) with `RadioProgramSelector` containing primary identifier (type + frequency/station ID) and optional secondary identifiers
2. Phone tunes the radio hardware and responds with `RadioTuneResponse` (0x801F) with status (SUCCESS/FAILURE/TIMEOUT/CANCELLED)
3. Phone follows up with `RadioProgramInfoNotification` (0x801B) containing the new station info, mute state, and audio focus state
4. `RadioMediaBrowserService` has a **6-second timeout** on tune operations

### Seek Flow

1. HU sends `RadioTuneDirectionRequest` (0x8022) with direction (UP=1 or DOWN=2)
2. Phone seeks to next station and responds with the same RadioTuneResponse + RadioProgramInfoNotification sequence

### Mute Flow

1. HU sends `RadioMuteRequest` (0x801C) with `mute=true/false`
2. Phone responds with `RadioMuteResponse` (0x801D) confirming new mute state

### Favorite Toggle Flow

1. HU sends `RadioFavoriteToggleRequest` (0x8021) with `is_favorite=true/false`
2. Phone updates favorites and sends `RadioFavoriteListNotification` (0x8020) with full updated list

### State Recovery on Reconnect

When a new callback is registered (`hlr.mo18791k()`), the service replays cached state in order:
1. Sends cached mute state (if available)
2. Sends cached program info + mute + audio focus (if all available)
3. Sends cached program list (if available)
4. Sends cached favorites list (if available)

---

## Service Discovery (SDP) Configuration

The radio channel's capabilities are declared in the ServiceDiscoveryResponse via `RadioChannel` in `ChannelDescriptorData`:

```protobuf
message RadioChannel {             // APK class: way (16.2)
    repeated RadioStation stations = 1;
}

message RadioStation {             // APK class: wax (16.2)
    optional int32 station_id = 1;
    optional int32 identifier_type = 2;
    repeated RadioBand bands = 3;         // frequency ranges
    repeated int32 channel_list = 4;
    optional int32 tuner_type = 5;
    optional bool enabled = 6;
    optional RadioCodecType codec_type = 7;
    optional RadioBandType band_type = 8;
    optional bool supports_rds = 9;
    optional bool supports_hd = 10;
    optional RadioRegion region = 11;
    optional bool dab_capable = 12;
    optional bool drm_capable = 13;
    optional int32 priority = 14;
}

message RadioBand {                // APK class: wbe (16.2)
    optional int32 lower_bound = 1;  // lower frequency limit (kHz)
    optional int32 upper_bound = 2;  // upper frequency limit (kHz)
}
```

The `hlr.mo18712a()` method parses this at channel setup and creates a `RadioConfiguration` containing `RadioBandGroup` entries. Each band group has:
- List of band type integers (1=AM, 2=FM, 3=DAB)
- `hideEmptyGroup` flag (whether to hide the browse node if no stations found)
- `bandScanAction` string (optional custom action ID for band scanning via 0x8023)

---

## MediaBrowserService Integration

`RadioMediaBrowserService` (`GH.Radio` tag) bridges the AA radio channel to Android's MediaBrowser framework.

**Package access:** Only `com.google.android.projection.gearhead` and approved NOW_PACKAGE clients can browse the radio tree.

### Browse Tree Structure

```
"AAPRadioRoot"
  +-- "favorites"              (always present, even if empty)
  +-- "bands:am"               (one per band group from RadioConfiguration)
  +-- "bands:fm"
  +-- "bands:dab"
  +-- "bands:am-fm"            (combined groups possible)
```

Empty band groups can be hidden via the `hideEmptyGroup` flag from RadioConfiguration.

### Supported Operations

| Method | AIDL Transaction | Wire Message | Action |
|--------|-----------------|--------------|--------|
| `mo11224k()` (tune) | 3 | 0x801E | Tune to RadioProgramSelector |
| `mo11228o()` (mute) | 4 | 0x801C | Set mute state |
| `mo11227n()` (favorite) | 6 | 0x8021 | Toggle favorite |
| `mo11229p()` (skip) | 7 | 0x8022 | Seek up/down |
| `mo11226m()` (custom action) | 8 | 0x8023 | Send custom action string |

### Custom Browser Actions

The RadioMediaBrowserService supports `androidx.media.utils.extras.CUSTOM_BROWSER_ACTION_ROOT_LIST` and per-item `CUSTOM_BROWSER_ACTION_ID_LIST`. These are forwarded to the phone as `RadioCustomActionRequest` (0x8023). The `bandScanAction` string from RadioConfiguration band groups is one such action ID.

---

## Metadata Delivery

Metadata flows through `RadioProgramInfoNotification` (0x801B) containing a `RadioProgramInfo` which nests `RadioMetadata` and `RadioSongMetadata`.

### Program Type Classification

Two schemas are supported:
- **SCHEMA_RDS_PTY (1):** European RDS standard, 31 program types (News through Alarm)
- **SCHEMA_ITU (2):** North American RBDS, 31 program types (News through Emergency)

The `lif.m25125h()` method contains complete string maps for both schemas with localized resource strings.

### Image Delivery

Station icons and album art are delivered as raw bytes in `RadioImage.image_data`. The service converts these to `Bitmap` objects and can also serve them as content URIs. For stations without icons, `lif.m25126r()` generates deterministic fallback icons from drawable resources using a seeded random based on frequency hash.

---

## Quirks and Gotchas

> **No satellite radio:** There is zero SiriusXM/XM support. The identifier types, band types, and codec types cover AM, FM (with HD Radio/RDS), and DAB/DAB+/DMB only. Terrestrial broadcast only.

> **Tune timeout:** `RadioMediaBrowserService` enforces a 6-second timeout on tune operations. If the phone's radio hardware doesn't respond within 6 seconds, the tune is considered failed.

> **TuneResponse defaults to SUCCESS:** If the `RadioTuneStatus` value is 0 (unset/unknown), the handler defaults it to 1 (SUCCESS). This means an empty `RadioTuneResponse` is treated as successful.

> **Favorite toggle is contextual:** `RadioFavoriteToggleRequest` does not specify which station to toggle -- it always applies to the **currently tuned** station. There is no way to favorite an arbitrary station without first tuning to it.

> **State replay on reconnect:** The radio service caches all state and replays it when a new callback registers. Implementers should expect to receive the full program list, favorites list, and current station info immediately after connection.

> **Custom actions are new in 16.2:** `RadioCustomActionRequest` (0x8023) was added in the 16.2 APK. It is not present in the 16.1 proto definitions. The 16.1 channel only had 9 message types.

> **DTS AutoStage:** `RadioMetadata.dts_autostage_enriched` (field 13) indicates DTS audio enhancement is active. This is a post-processing feature, not a radio standard -- it signals that DTS AutoStage is enhancing the audio output.

> **Class name drift:** Proto class names shifted between 16.1 and 16.2. The 16.1 names (wau, wat, wao, etc.) are in the proto file headers; the 16.2 names (wam, wal, wag, etc.) are from the current APK analysis. Match by enum value fingerprints, not class names.

---

## APK Source References (16.2)

| Class | Role |
|-------|------|
| `ibf` | `CAR.GAL.RADIO-EP` -- radio channel endpoint, handles incoming Phone->HU messages |
| `hlr` | `CAR.RADIO` -- radio service, manages state and sends HU->Phone messages |
| `ibd` | Handler callback -- routes handler messages (1-5) to service callbacks |
| `RadioMediaBrowserService` | `GH.Radio` -- MediaBrowser integration for radio UI |
| `psn` / `psm` | `ICarRadio` AIDL interface |
| `psq` / `psp` | `ICarRadioCallback` AIDL interface |
| `pmm` | `CAR.RADIO` -- client-side proxy for ICarRadio |
| `wam` | RadioProgramListNotification proto (0x801A) |
| `wal` | RadioProgramInfoNotification proto (0x801B) |
| `wag` | RadioMuteRequest proto (0x801C) |
| `wah` | RadioMuteResponse proto (0x801D) |
| `wat` | RadioTuneRequest proto (0x801E) |
| `wau` | RadioTuneResponse proto (0x801F) |
| `wad` | RadioFavoriteListNotification proto (0x8020) |
| `waq` | RadioFavoriteToggleRequest proto (0x8021) |
| `war` | RadioTuneDirectionRequest proto (0x8022) |
| `wac` | RadioCustomActionRequest proto (0x8023) |
| `wak` | RadioProgramInfo proto |
| `wan` | RadioProgramSelector proto |
| `waj` | RadioProgramIdentifier proto |
| `waf` | RadioMetadata proto |
| `was` | RadioSongMetadata proto |
| `wai` | RadioIdentifierType enum |
| `vzz` | RadioBandType runtime enum |
| `ljg` | Frequency/band classification utilities |
| `lif` | UI station display, program type strings, fallback icon generation |
| `lhw` | Browse node builder (band groups, favorites) |
