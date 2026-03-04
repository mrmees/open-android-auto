# Media Channels

## Proto Confidence Summary

| Message | Tier | Evidence | Audit File |
|---------|------|----------|------------|
| MediaPlaybackStatus | Silver | apk_static + cross_version | [MediaPlaybackStatusMessage.audit.yaml](../../oaa/media/MediaPlaybackStatusMessage.audit.yaml) |
| MediaPlaybackCommand | Silver | apk_static + cross_version | [MediaPlaybackCommandMessage.audit.yaml](../../oaa/media/MediaPlaybackCommandMessage.audit.yaml) |
| MediaPlaybackMetadata | Silver | apk_static + cross_version | [MediaPlaybackMetadataMessage.audit.yaml](../../oaa/media/MediaPlaybackMetadataMessage.audit.yaml) |
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

> Confidence: Silver [apk_static, cross_version] -- core MediaPlaybackStatus has wire verification (1993 messages captured)

Android Auto carries media information on two distinct channels:

| Channel | GAL Type | Purpose | Status |
|---------|----------|---------|--------|
| Channel 10 | MEDIA_PLAYBACK_STATUS (11) | Phone-sourced media: now-playing state, metadata, controls | Primary -- active in all sessions |
| (dynamic) | CAR_LOCAL_MEDIA (20) | Car-local media: FM radio, USB, CD -- status and control from HU-side sources | Niche -- most HUs do not implement |
| (dynamic) | BUFFERED_MEDIA_SINK (21) | Buffered media -- stub channel, not implemented in AA v16.x | Stub -- no runtime messages |

Channel 10 is the main media channel. It carries phone-sourced playback status and metadata from apps like Spotify, YouTube Music, or any app exposing an Android `MediaBrowserService`. The HU displays this information and sends playback commands (pause, resume) back to the phone.

CarLocalMediaPlayback is a separate channel for head units that have their own media sources (FM tuner, USB playback, CD changer). It uses different proto messages on a different GAL type, despite sharing some concepts with the phone-sourced flow.

BufferedMediaSink (GAL type 21) exists in the protocol definition but is a stub -- the phone-side handler logs receipt and discards all data. Feature-gated behind flag `abey` (834952858). A rich service discovery config exists (audio/video/metadata configs), suggesting future implementation.

---

## Message Catalog

### Phone-Sourced Media (Channel 10, GAL Type 11)

> Confidence: Silver [apk_static, cross_version] -- MediaPlaybackStatus wire-verified with 1993 captured messages

| Msg ID | Message | Direction | Purpose | Confidence |
|--------|---------|-----------|---------|:---:|
| 0x8001 | MediaPlaybackStatus | Phone -> HU | Current playback state, source app, position, shuffle/repeat | Silver |
| 0x8002 | MediaPlaybackCommand | HU -> Phone | Playback control (pause, resume) | Silver |
| 0x8003 | MediaPlaybackMetadata | Phone -> HU | Track title, artist, album, album art, is_playing | Silver |

#### MediaPlaybackStatus

```protobuf
message MediaPlaybackStatus {
    optional PlaybackState playback_state = 1;  // UNKNOWN(0), STOPPED(1), PLAYING(2), PAUSED(3), ERROR(4)
    optional string source_app = 2;             // e.g. "YouTube Music", "Spotify"
    optional uint32 position_seconds = 3;       // Elapsed seconds in current track
    optional bool shuffle = 4;
    optional bool repeat = 5;
    optional bool repeat_one = 6;
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

#### MediaPlaybackCommand

```protobuf
message MediaPlaybackCommand {
    optional PlaybackCommandType command = 1;  // UNKNOWN(0), PAUSE(1), RESUME(2)
}
```

Sent by the HU when the user taps play/pause controls. The validator accepts values 0, 1, and 2 only.

#### MediaPlaybackMetadata

```protobuf
message MediaPlaybackMetadata {
    optional string title = 1;
    optional string artist = 2;
    optional string album = 3;
    optional bytes album_art = 4;        // PNG image data
    optional bool is_playing = 5;
    optional string album_art_url = 6;   // URL alternative to embedded bytes
}
```

Sent by the phone when the track changes. Fields 5-6 were discovered via APK proto decoder (nmi.java, AA v16.1) -- not present in older aasdk definitions. The `album_art` field contains raw image bytes; `album_art_url` provides a URL alternative (both may be present).

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

> Confidence: Silver [apk_static, cross_version]

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
  |<-- MediaPlaybackCommand ------------------- |  command=PAUSE
  |--- MediaPlaybackStatus ------------------>  |  state=PAUSED
  |                                             |
  |                  [User taps play on HU]     |
  |<-- MediaPlaybackCommand ------------------- |  command=RESUME
  |--- MediaPlaybackStatus ------------------>  |  state=PLAYING
  |                                             |
  |  [Track changes on phone]                   |
  |--- MediaPlaybackMetadata ----------------> |  new title, artist, album, art
  |--- MediaPlaybackStatus ------------------>  |  position_seconds=0, state=PLAYING
```

The phone pushes status updates continuously. The HU only sends `MediaPlaybackCommand` when the user interacts with media controls. There is no request/response handshake -- the phone sends status whenever it changes, and the HU renders it.

---

## Phone-Side Context

> Confidence: Silver [apk_static, cross_version] -- mapping verified via APK analysis (qbw.java, AIDL interface prz.java)

Android Auto's media channel bridges the phone's `MediaBrowserService` / `MediaSession` framework to the wire protocol:

| Android Concept | Wire Message | Mapping |
|----------------|-------------|---------|
| `MediaSession.getPlaybackState()` | `MediaPlaybackStatus` | PlaybackState maps to `PlaybackStateCompat` constants |
| `MediaSession.getMetadata()` | `MediaPlaybackMetadata` | Title, artist, album, art extracted from `MediaMetadataCompat` |
| `MediaSession.Callback.onPlay/onPause` | `MediaPlaybackCommand` | HU pause/resume commands trigger these callbacks |
| `PlaybackStateCompat.getActions()` | Not directly mapped | Action flags are not carried on channel 10 (CarLocalMedia uses them) |

The phone's `MediaBrowserService` controller (log tag `GH.MediaActiveContrConn`) monitors the active media session. When the session state changes, the phone serializes it into `MediaPlaybackStatus` and sends it on channel 10. When the HU sends a `MediaPlaybackCommand`, the phone translates it into the corresponding `MediaSession.Callback` action on the source app.

Skip/previous/next controls are notably absent from `MediaPlaybackCommand` (which only has pause and resume). These controls may flow through the input channel (ch 1) as Android `KeyEvent` codes (KEYCODE_MEDIA_NEXT, KEYCODE_MEDIA_PREVIOUS) rather than through the media status channel.

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

> **Gotcha:** Channel 10 (GAL type 11, MEDIA_PLAYBACK_STATUS) and CarLocalMedia (GAL type 20) **both use msgId 0x8001** for their status messages, but with entirely different proto schemas. MediaPlaybackStatus has 6 fields (state, source, position, 3 booleans). CarLocalMediaPlaybackStatus has 4 fields (state, source, position, repeated actions). Deserializing with the wrong proto will silently produce garbage. Always check the GAL channel type, not just the message ID.

> **Gotcha:** `MediaPlaybackCommand` only supports PAUSE (1) and RESUME (2). There are no skip/previous/next commands on the media status channel. These controls likely flow through the **input channel (ch 1)** as Android KeyEvent codes. If your HU only listens on channel 10 for media transport, the user will not be able to skip tracks.

> **Gotcha:** `MediaEventIdWrapper` and `MediaTrackIdentifier` are structurally verified (Silver) but their sub-message content is not decoded. `MediaEventIdWrapper` uses field number 13 (unusually high, suggesting it was added later). `MediaTrackIdentifier` has 3 message-type fields whose internal structure is placeholder. Do not assume these sub-messages are empty at runtime -- they contain data, but we cannot yet describe its layout.

> **Gotcha:** `BufferedMediaSinkMessage` (GAL type 21) is a **stub channel**. The phone-side handler in AA v16.x logs receipt and discards all data. Do not invest implementation effort in this channel. It is feature-gated behind flag `abey` (834952858) and not active in current AA versions.

---

## References

### Proto Files
- [MediaPlaybackStatusMessage.proto](../../oaa/media/MediaPlaybackStatusMessage.proto)
- [MediaPlaybackCommandMessage.proto](../../oaa/media/MediaPlaybackCommandMessage.proto)
- [MediaPlaybackMetadataMessage.proto](../../oaa/media/MediaPlaybackMetadataMessage.proto)
- [MediaStatusListData.proto](../../oaa/media/MediaStatusListData.proto)
- [MediaTrackIdentifierData.proto](../../oaa/media/MediaTrackIdentifierData.proto)
- [MediaChannelData.proto](../../oaa/media/MediaChannelData.proto)
- [CarLocalMediaPlaybackStatusMessage.proto](../../oaa/media/CarLocalMediaPlaybackStatusMessage.proto)
- [CarLocalMediaPlaybackMetadataMessage.proto](../../oaa/media/CarLocalMediaPlaybackMetadataMessage.proto)
- [CarLocalMediaPlaybackRequestMessage.proto](../../oaa/media/CarLocalMediaPlaybackRequestMessage.proto)
- [CarLocalMediaPlaybackEnum.proto](../../oaa/media/CarLocalMediaPlaybackEnum.proto)
- [BufferedMediaSinkMessage.proto](../../oaa/media/BufferedMediaSinkMessage.proto)

### Cross-References
- [Media cross-version mapping](../cross-version/media.md) -- APK class mappings across versions 15.9, 16.1, 16.2
- [Channel map](../channel-map.md) -- Channel ID reference for all AA channels
- [01-confidence-tiers.md](../verification/01-confidence-tiers.md) -- Confidence tier definitions
