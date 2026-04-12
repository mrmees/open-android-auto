# Media Channels

> **Architecture context:** This channel is part of the Android Auto multiplexed
> protocol. For the overall architecture — framing, SDP binding, capability
> negotiation — see [Channel Architecture Reference](architecture.md).

## Proto Confidence Summary

| Message | Tier | Evidence | Audit File |
|---------|------|----------|------------|
| MediaPlaybackStatus | **Gold** | apk_deep_trace (2026-03-06) | [MediaPlaybackStatusMessage.audit.yaml](../../oaa/media/MediaPlaybackStatusMessage.audit.yaml) |
| MediaPlaybackStatusEvent | **Gold** | apk_deep_trace (2026-03-06) — NEW | [MediaPlaybackStatusEventMessage.audit.yaml](../../oaa/media/MediaPlaybackStatusEventMessage.audit.yaml) |
| ~~MediaPlaybackCommand~~ | **Retracted** | class vuy misidentified — 0x8002 exists as MediaPlaybackStatusEvent (vxo) | [MediaPlaybackCommandMessage.audit.yaml](../../oaa/media/MediaPlaybackCommandMessage.audit.yaml) |
| MediaPlaybackMetadata | **Gold** | apk_deep_trace (2026-03-06) — CORRECTED fields 5-7 | [MediaPlaybackMetadataMessage.audit.yaml](../../oaa/media/MediaPlaybackMetadataMessage.audit.yaml) |
| MediaEventIdWrapper | Silver | apk_static + cross_version | [MediaPlaybackStatusMessage.audit.yaml](../../oaa/media/MediaPlaybackStatusMessage.audit.yaml) |
| MediaStatusList | Silver | apk_static + cross_version | [MediaStatusListData.audit.yaml](../../oaa/media/MediaStatusListData.audit.yaml) |
| MediaTrackIdentifier | Silver | apk_static + cross_version | [MediaTrackIdentifierData.audit.yaml](../../oaa/media/MediaTrackIdentifierData.audit.yaml) |
| CarLocalMediaPlaybackStatus | Silver | apk_static + cross_version | [CarLocalMediaPlaybackStatusMessage.audit.yaml](../../oaa/media/CarLocalMediaPlaybackStatusMessage.audit.yaml) |
| CarLocalMediaPlaybackMetadata | Silver | apk_static + cross_version | [CarLocalMediaPlaybackMetadataMessage.audit.yaml](../../oaa/media/CarLocalMediaPlaybackMetadataMessage.audit.yaml) |
| CarLocalMediaPlaybackRequest | Silver | apk_static + cross_version | [CarLocalMediaPlaybackRequestMessage.audit.yaml](../../oaa/media/CarLocalMediaPlaybackRequestMessage.audit.yaml) |
| CarLocalMediaPlaybackEnum | Bronze | apk_static | [CarLocalMediaPlaybackEnum.audit.yaml](../../oaa/media/CarLocalMediaPlaybackEnum.audit.yaml) |
| MediaInfoChannel | Unverified | -- | -- |
| BufferedMediaSinkMessage | Unverified | -- | -- |

---

## Overview

> Confidence: Gold [apk_deep_trace, 2026-03-06] -- core messages verified end-to-end via proto-verification pipeline

Android Auto carries media information across several channel types. Two are commonly confused:

| GAL Tag | GAL Type | Handler | Purpose | Status |
|---------|----------|---------|---------|--------|
| CAR.GAL.INST | 11 | iai.java / hvx.java | **Media info channel** — playback status, metadata, HU input events | Primary — active in all sessions |
| CAR.GAL.MEDIA | (AV) | qnf.java | **AV audio stream endpoint** — setup, config, ACKs for the audio pipe | AV infrastructure — not media status |
| CAR.GAL.CAR_LOCAL_MEDIA | 20 | (separate) | Car-local media: FM radio, USB, CD | Niche — most HUs don't implement |
| (n/a) | 21 | (stub) | Buffered media sink — stub, not implemented in AA v16.x | Inactive |

**Important:** `CAR.GAL.MEDIA` is the AV audio streaming endpoint (setup/ACK/config), NOT the media status channel. Media playback status and metadata flow through `CAR.GAL.INST` (GAL type 11). These are distinct channels with different handlers and message catalogs.

---

## Message Catalog

### Media Info Channel (CAR.GAL.INST, GAL Type 11)

> Confidence: Gold [apk_deep_trace, 2026-03-06]
> Handler: iai.java (channel endpoint), hvx.java (service implementation)
> AIDL: com.google.android.gms.car.ICarMediaPlaybackStatus

| Msg ID | Message | Direction | Purpose | Confidence |
|--------|---------|-----------|---------|:---:|
| 0x8001 | MediaPlaybackStatus | Phone -> HU | Current playback state, source app, position, shuffle/repeat | **Gold** |
| 0x8002 | MediaPlaybackStatusEvent | HU -> Phone | Input action from HU (instrument cluster interaction) | **Gold** |
| 0x8003 | MediaPlaybackMetadata | Phone -> HU | Track title, artist, album, album art | **Gold** |

> **CORRECTED (2026-03-06):** The previous retraction of 0x8002 was partially wrong. The APK class `vuy` was correctly retracted (it is ActionTakenNotification on the video channel). However, msg ID 0x8002 DOES exist on the CAR.GAL.INST channel — it uses a different proto class `vxo` (MediaPlaybackStatusEvent), received by `iai.mo18864a()` and dispatched to `ICarMediaPlaybackStatusEventListener`. This is an HU-to-phone input action, not a playback command.
>
> **Media playback control still goes through the input channel (ch 1) as button events** — keycodes MEDIA_PLAY_PAUSE (85), MEDIA_PLAY (126), MEDIA_PAUSE (127), MEDIA_NEXT (87), MEDIA_PREVIOUS (88). The 0x8002 MediaPlaybackStatusEvent is a separate mechanism for instrument cluster interactions.

### AV Audio Stream Endpoint (CAR.GAL.MEDIA)

> Handler: qnf.java (internal name: "AudioEndPoint")

This is the AV audio pipe, not the media status channel. It handles stream setup and flow control.

| Msg ID | Message | Direction | Purpose | Proto Class |
|--------|---------|-----------|---------|-------------|
| 0x8000 | AV Setup Request | Phone -> HU | Audio stream setup | wbs |
| 0x8004 | AV Config Response | HU -> Phone | Configuration / setup response | vwn |
| 0x8005 | AV ACK | HU -> Phone | Frame acknowledgment (session ID + count) | vuw |
| 0x800C | AV Signal | HU -> Phone | Signal (no proto, calls qnk.mo29257h()) | (none) |

Invalid msg IDs are logged: `"Received message with invalid type header: %d ch:%d"`.

---

#### MediaPlaybackStatus

```protobuf
// APK class: vyc (v16.2)
// confidence: gold [apk_deep_trace, 2026-03-06]
message MediaPlaybackStatus {
    optional PlaybackState playback_state = 1;  // UNKNOWN(0), STOPPED(1), PLAYING(2), PAUSED(3), ERROR(4)
    optional string source_app = 2;             // e.g. "YouTube Music", "Spotify"
    optional uint32 position_seconds = 3;       // Elapsed seconds in current track
    optional bool shuffle = 4;
    optional bool repeat = 5;                   // Note: GMS proxy hardcodes to false
    optional bool repeat_one = 6;               // Note: GMS proxy hardcodes to false
}
```

Wire-verified field values from capture: `playback_state=2 (PLAYING), source_app="YouTube Music", position_seconds=80, shuffle=false, repeat=false, repeat_one=false`.

The `PlaybackState` enum maps to Android `PlaybackStateCompat` constants:

| Value | Name | Android Equivalent |
|:---:|------|-------------------|
| 0 | UNKNOWN | STATE_NONE (0) |
| 1 | STOPPED | STATE_STOPPED (1) |
| 2 | PLAYING | STATE_PLAYING (3) |
| 3 | PAUSED | STATE_PAUSED (2) |
| 4 | ERROR | STATE_ERROR (7) |

#### MediaPlaybackStatusEvent (NEW)

```protobuf
// APK class: vxo (v16.2)
// confidence: gold [apk_deep_trace, 2026-03-06]
message MediaPlaybackStatusEvent {
    required MediaPlaybackStatusEventType event_type = 1;
}
```

HU sends this to the phone as an input action related to media playback on the instrument cluster. Received by `iai.mo18864a()`, dispatched to `ICarMediaPlaybackStatusEventListener.onInput(value - 1)`.

The enum values are not yet fully mapped (enum verifier index 17, `vve.f73609r`). Wire capture needed.

#### MediaPlaybackMetadata

```protobuf
// APK class: vyb (v16.2)
// confidence: gold [apk_deep_trace, 2026-03-06]
// CORRECTED: fields 5-7 fixed, syntax changed to proto2
message MediaPlaybackMetadata {
    optional string title = 1;
    optional string artist = 2;
    optional string album = 3;
    optional bytes album_art = 4;      // Image data
    optional string unknown_5 = 5;     // Always null from GMS proxy
    optional uint32 unknown_6 = 6;     // Could be duration, track number, etc.
    optional int32 unknown_7 = 7;      // Always 0 from GMS proxy
}
```

Sent by the phone when the track changes. Fields 5-7 exist in the proto schema and AIDL interface but are not populated by the current GMS car API client (pre.java hardcodes field 5 = null, field 7 = 0).

> **CORRECTED (2026-03-06):** Previous version had field 5 as `bool is_playing` and field 6 as `string album_art_url`. Deep trace proved field 5 is string, field 6 is uint32, and field 7 (int32) was missing entirely. Syntax was also wrong (proto3 should be proto2).

#### ~~MediaPlaybackCommand~~ (RETRACTED)

This message was retracted on 2026-03-06. The APK class `vuy` was misidentified — it is `ActionTakenNotification` on the video channel (0x800D), not a media playback command. See [MediaPlaybackCommandMessage.audit.yaml](../../oaa/media/MediaPlaybackCommandMessage.audit.yaml). The proto file is retained as a tombstone.

Note: msg ID 0x8002 on the media-info channel does exist as `MediaPlaybackStatusEvent` (above), which is a different proto class (`vxo`) serving a different purpose.

### Supporting Messages

> Confidence: Silver [apk_static, cross_version]

| Message | Purpose | Confidence |
|---------|---------|:---:|
| MediaEventIdWrapper | Event ID tracking -- contains a sub-message at field 13 (high field number suggests later addition) | Silver |
| MediaEventId | Placeholder sub-message for MediaEventIdWrapper | Silver |
| MediaStatusList | Repeated list of MediaStatusEntry items | Silver |
| MediaStatusEntry | Placeholder sub-message for list entries | Silver |
| MediaTrackIdentifier | Track identification with 3 message-type sub-fields (track_id, track_source, track_metadata) | Silver |
| MediaInfoChannel | Empty service discovery marker (same pattern as AudioFocusChannel) | Unverified |

MediaEventIdWrapper, MediaStatusList, and MediaTrackIdentifier are structurally verified (field numbers and types confirmed across 3 APK versions) but their sub-message contents are placeholder -- the internal structure of MediaEventId, MediaStatusEntry, and MediaTrackField is not yet decoded.

---

## State Machine

> Confidence: Gold [apk_deep_trace, 2026-03-06]

### Phone-Sourced Media Flow

```
Phone                                        Head Unit
  |                                             |
  |  [User starts Spotify on phone]             |
  |                                             |
  |--- MediaPlaybackStatus ------------------>  |  state=PLAYING, source="Spotify"
  |--- MediaPlaybackMetadata ----------------> |  title, artist, album, art
  |                                             |  HU displays now-playing info
  |                                             |
  |--- MediaPlaybackStatus ------------------>  |  position_seconds updates
  |--- MediaPlaybackStatus ------------------>  |  (periodic position updates)
  |                                             |
  |                  [User taps pause on HU]    |
  |<-- (Input ch1: KEYCODE_MEDIA_PAUSE=127) --- |  button press via input channel
  |--- MediaPlaybackStatus ------------------>  |  state=PAUSED
  |                                             |
  |                  [User taps play on HU]     |
  |<-- (Input ch1: KEYCODE_MEDIA_PLAY=126) ---- |  button press via input channel
  |--- MediaPlaybackStatus ------------------>  |  state=PLAYING
  |                                             |
  |  [Track changes on phone]                   |
  |--- MediaPlaybackMetadata ----------------> |  new title, artist, album, art
  |--- MediaPlaybackStatus ------------------>  |  position_seconds=0, state=PLAYING
  |                                             |
  |         [HU instrument cluster interaction] |
  |<-- MediaPlaybackStatusEvent (0x8002) ------ |  event on CAR.GAL.INST channel
  |                                             |
```

The phone pushes status updates continuously. The HU controls playback by sending button events on the **input channel (ch 1)**, not on the media status channel. There is no request/response handshake -- the phone sends status whenever it changes, and the HU renders it.

The MediaPlaybackStatusEvent (0x8002) is a separate mechanism for instrument cluster interactions, distinct from the input channel button presses.

---

## Phone-Side Context

> Confidence: Silver [apk_static, cross_version] -- mapping verified via APK analysis (qbw.java, AIDL interface prz.java)

Android Auto's media channel bridges the phone's `MediaBrowserService` / `MediaSession` framework to the wire protocol:

| Android Concept | Wire Message | Mapping |
|----------------|-------------|---------|
| `MediaSession.getPlaybackState()` | `MediaPlaybackStatus` | PlaybackState maps to `PlaybackStateCompat` constants |
| `MediaSession.getMetadata()` | `MediaPlaybackMetadata` | Title, artist, album, art extracted from `MediaMetadataCompat` |
| `MediaSession.Callback.onPlay/onPause` | Input ch1 button events | HU sends KEYCODE_MEDIA_PLAY/PAUSE via input channel |
| `PlaybackStateCompat.getActions()` | Not directly mapped | Action flags are not carried on media-info channel (CarLocalMedia uses them) |

The phone's `MediaBrowserService` controller (log tag `GH.MediaActiveContrConn`) monitors the active media session. When the session state changes, the phone serializes it into `MediaPlaybackStatus` and sends it on the media-info channel. The HU controls playback by sending button events on the input channel (ch 1), which the phone translates into `MediaSession.Callback` actions on the source app.

All media transport controls (play, pause, skip, previous, stop) flow through the input channel as Android KeyEvent button presses. The media status channel is receive-only from the HU's perspective (except for 0x8002 MediaPlaybackStatusEvent).

---

## CarLocalMediaPlayback (GAL Type 20)

> Confidence: Silver [apk_static, cross_version] -- CarLocalMediaPlaybackEnum is Bronze

CarLocalMediaPlayback is a separate channel for head units with built-in media sources (FM tuner, USB music, CD changer). It runs on GAL type 20 with its own handler (`hxu.java`, log tag not specified). This is a niche feature -- most AA head units rely solely on phone-sourced media.

### Messages

| Msg ID | Message | Direction | Purpose | Confidence |
|--------|---------|-----------|---------|:---:|
| 0x8001 | CarLocalMediaPlaybackStatus | Phone -> HU | Playback state, source, position, available actions | Silver |
| 0x8002 | CarLocalMediaPlaybackMetadata | Phone -> HU | Track title, artist, album, album art, duration | Silver |
| 0x8003 | CarLocalMediaPlaybackRequest | HU -> Phone | Transport action command (play/pause/skip/stop) | Silver |

#### CarLocalMediaPlaybackStatus

```protobuf
message CarLocalMediaPlaybackStatus {
    optional PlaybackState playback_state = 1;     // Shared enum with MediaPlaybackStatus
    optional string media_source = 2;              // e.g. "FM Radio", "USB"
    optional int32 playback_position = 3;          // Elapsed seconds
    repeated CarLocalMediaPlaybackAction actions = 4;  // Available transport actions
}
```

Unlike phone-sourced `MediaPlaybackStatus`, this message includes a list of available transport actions (PLAY, PAUSE, PREVIOUS, NEXT, STOP). The phone uses these to determine which media controls to display.

#### CarLocalMediaPlaybackMetadata

```protobuf
message CarLocalMediaPlaybackMetadata {
    optional string song = 1;              // Falls back to default "missing song" string
    optional string artist = 2;
    optional string album = 3;
    optional bytes album_art = 4;          // Image data (decoded via BitmapFactory)
    optional uint32 duration_seconds = 5;  // Total duration (-1 = unknown)
}
```

Similar to `MediaPlaybackMetadata` but includes explicit `duration_seconds` (the phone-sourced version does not carry duration in metadata). Album art is raw image bytes, not a URL.

#### CarLocalMediaPlaybackRequest

```protobuf
message CarLocalMediaPlaybackRequest {
    optional CarLocalMediaPlaybackAction action = 1;
}
```

The `CarLocalMediaPlaybackAction` enum maps to Android `PlaybackStateCompat.ACTION_*` flags:

| Value | Action | Android Flag |
|:---:|--------|-------------|
| 0 | PLAY | ACTION_PLAY (4L) |
| 1 | PAUSE | ACTION_PAUSE (2L) |
| 2 | PREVIOUS | ACTION_SKIP_TO_PREVIOUS (16L) |
| 3 | NEXT | ACTION_SKIP_TO_NEXT (32L) |
| 4 | STOP | ACTION_STOP (1L) |

The phone-side handler logs "Received unexpected car local media message CAR_LOCAL_MEDIA_PLAYBACK_REQUEST" and drops incoming 0x8003 messages -- this confirms it is an HU-to-phone outbound-only message.

---

## Gotchas

> **Gotcha:** The media-info channel (`CAR.GAL.INST`, GAL type 11) and `CAR.GAL.MEDIA` are DIFFERENT channels. `CAR.GAL.MEDIA` is the AV audio streaming endpoint (setup/ACK/config). Media playback status and metadata flow through `CAR.GAL.INST`. Do not confuse these.

> **Gotcha:** GAL type 11 (media-info) and GAL type 20 (CarLocalMedia) **both use msgId 0x8001** for their status messages, but with entirely different proto schemas. MediaPlaybackStatus has 6 fields (state, source, position, 3 booleans). CarLocalMediaPlaybackStatus has 4 fields (state, source, position, repeated actions). Deserializing with the wrong proto will silently produce garbage. Always check the GAL channel type, not just the message ID.

> **Gotcha:** Media playback control (pause, play, skip) goes through the **input channel (ch 1)** as Android KeyEvent button presses. Your SDP must advertise media keycodes (85, 86, 87, 88, 126, 127) in `supported_keycodes` for the phone to accept them. The 0x8002 MediaPlaybackStatusEvent is for instrument cluster input actions, not general playback control.

> **Gotcha:** `MediaEventIdWrapper` and `MediaTrackIdentifier` are structurally verified (Silver) but their sub-message content is not decoded. `MediaEventIdWrapper` uses field number 13 (unusually high, suggesting it was added later). `MediaTrackIdentifier` has 3 message-type fields whose internal structure is placeholder. Do not assume these sub-messages are empty at runtime -- they contain data, but we cannot yet describe its layout.

> **Gotcha:** `BufferedMediaSinkMessage` (GAL type 21) is a **stub channel**. The phone-side handler in AA v16.x logs receipt and discards all data. Do not invest implementation effort in this channel. It is feature-gated behind flag `abey` (834952858) and not active in current AA versions.

---

## References

### Proto Files
- [MediaPlaybackStatusMessage.proto](../../oaa/media/MediaPlaybackStatusMessage.proto)
- [MediaPlaybackStatusEventMessage.proto](../../oaa/media/MediaPlaybackStatusEventMessage.proto) **(NEW — 2026-03-06)**
- [MediaPlaybackCommandMessage.proto](../../oaa/media/MediaPlaybackCommandMessage.proto) **(RETRACTED — tombstone only)**
- [MediaPlaybackMetadataMessage.proto](../../oaa/media/MediaPlaybackMetadataMessage.proto) **(CORRECTED — 2026-03-06)**
- [MediaStatusListData.proto](../../oaa/media/MediaStatusListData.proto)
- [MediaTrackIdentifierData.proto](../../oaa/media/MediaTrackIdentifierData.proto)
- [MediaChannelData.proto](../../oaa/media/MediaChannelData.proto)
- [CarLocalMediaPlaybackStatusMessage.proto](../../oaa/media/CarLocalMediaPlaybackStatusMessage.proto)
- [CarLocalMediaPlaybackMetadataMessage.proto](../../oaa/media/CarLocalMediaPlaybackMetadataMessage.proto)
- [CarLocalMediaPlaybackRequestMessage.proto](../../oaa/media/CarLocalMediaPlaybackRequestMessage.proto)
- [CarLocalMediaPlaybackEnum.proto](../../oaa/media/CarLocalMediaPlaybackEnum.proto)
- [BufferedMediaSinkMessage.proto](../../oaa/media/BufferedMediaSinkMessage.proto)

### Verification Report
- [Proto Verification: Media Channel](../../analysis/reports/proto-verification/media.md) — full verification trace with handler analysis

### Cross-References
- [Media cross-version mapping](../cross-version/media.md) -- APK class mappings across versions 15.9, 16.1, 16.2
- [Channel map](../channel-map.md) -- Channel ID reference for all AA channels
- [01-confidence-tiers.md](../verification/01-confidence-tiers.md) -- Confidence tier definitions
