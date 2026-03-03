# 04 — Channel Lifecycle

## Overview

After service discovery, the HU opens individual channels for each advertised service. Each channel follows a lifecycle: open → setup → start → data exchange → stop → close. AV channels (video, audio) have additional setup negotiation and flow control. Audio channels also involve focus arbitration.

## Prerequisites

- Service discovery complete (from [03-service-discovery](03-service-discovery.md))
- Both sides know each other's capabilities
- All messages encrypted (TLS), using `MessageType::Specific` (NOT Control)
- Exception: channel open/close messages use `MessageType::Control` on channel 0

## Sequence Diagram — Channel Open

```
Phone                                        Head Unit
  |                                             |
  |  ── Per-channel, HU opens each one ───────  |
  |                                             |
  |←── CHANNEL_OPEN_REQUEST (0x0007) ────────── |  ch 0, Control msg type
  |─── CHANNEL_OPEN_RESPONSE (0x0008) ────────→ |  ch 0, Control msg type
  |                                             |
  |  ── For AV channels (video, audio): ──────  |
  |                                             |
  |─── SETUP_REQUEST (0x8000) ────────────────→ |  ch N, Specific msg type
  |←── SETUP_RESPONSE (0x8003) ────────────────│|  ch N, Specific msg type
  |─── START_INDICATION (0x8001) ─────────────→ |  ch N, Specific msg type
  |─── [AV data frames] ─────────────────────→ |
  |←── AV_MEDIA_ACK (0x8004) ─────────────────│|  Flow control
  |                                             |
  |  ── For non-AV channels (sensor, input): ─  |
  |                                             |
  |     Data exchange begins immediately         |
  |     after CHANNEL_OPEN_RESPONSE              |
```

---

## Channel Open/Close

### ChannelOpenRequest (0x0007) — HU → Phone

Sent on **channel 0** with `MessageType::Control`.

```protobuf
message ChannelOpenRequest {
    optional sint32 priority = 1;    // Channel priority (zigzag encoded)
    optional int32 channel_id = 2;   // Which channel to open
}
```

### ChannelOpenResponse (0x0008) — Phone → HU

```protobuf
message ChannelOpenResponse {
    optional Status status = 1;      // 0 = OK
}
```

### Channel Open Order (observed)

The HU opens channels in this order (from our captured session):

```
ch 0  — Control (implicit, always open)
ch 3  — Video
ch 4  — Media Audio
ch 5  — Speech Audio
ch 6  — System Audio
ch 7  — AV Input (microphone)
ch 1  — Input
ch 2  — Sensor
ch 8  — Bluetooth
ch 14 — WiFi
```

AV channels (3-7) are opened first because they require additional setup negotiation.

### ChannelCloseNotification (0x0009)

Either side can close a channel:

```
Message ID: 0x0009 on channel 0, MessageType::Control
```

---

## AV Channel Setup (Video & Audio)

All AV channels (video ch 3, audio ch 4/5/6, mic ch 7) share the same message IDs but on their respective channel numbers.

### AV Message IDs

| ID | Name | Direction |
|----|------|-----------|
| 0x0000 | AV_MEDIA_WITH_TIMESTAMP_INDICATION | Phone → HU |
| 0x0001 | AV_MEDIA_INDICATION | Phone → HU |
| 0x8000 | SETUP_REQUEST | Phone → HU |
| 0x8001 | START_INDICATION | Phone → HU |
| 0x8002 | STOP_INDICATION | Phone → HU |
| 0x8003 | SETUP_RESPONSE | HU → Phone |
| 0x8004 | AV_MEDIA_ACK_INDICATION | HU → Phone |
| 0x8005 | AV_INPUT_OPEN_REQUEST | Phone → HU |
| 0x8006 | AV_INPUT_OPEN_RESPONSE | HU → Phone |
| 0x8007 | VIDEO_FOCUS_REQUEST | Phone → HU |
| 0x8008 | VIDEO_FOCUS_INDICATION | HU → Phone |
| 0x800B | AUDIO_UNDERFLOW | HU → Phone |
| 0x8013 | MEDIA_STATS | Phone → HU |

**Critical:** These messages use `MessageType::Specific`, NOT `Control`. Getting this wrong causes the phone to silently ignore messages.

### SETUP_REQUEST (0x8000) — Phone → HU

The phone sends this after channel open to negotiate AV parameters. The payload is an `AVChannelSetupRequest` (config index selection).

### SETUP_RESPONSE (0x8003) — HU → Phone

```protobuf
message AVChannelSetupResponse {
    optional AVChannelSetupStatus media_status = 1;  // 0 = OK
    optional uint32 max_unacked = 2;                  // Flow control window
    repeated uint32 configs = 3;                      // Accepted config indices
}
```

**`max_unacked` is critical for flow control:**

| Channel | Typical max_unacked | Effect |
|---------|-------------------|--------|
| Video (ch 3) | 10 | Phone sends up to 10 frames before waiting for ACK |
| Audio (ch 4/5/6) | 1 | Phone sends 1 buffer, waits for ACK before next |

### START_INDICATION (0x8001) — Phone → HU

```protobuf
message AVChannelStartIndication {
    optional int32 session = 1;
    optional uint32 config = 2;                          // Selected config index
    optional AVChannelSessionType session_type = 3;
    optional AVChannelMediaConfig media_config = 4;
}
```

After this message, AV data frames begin flowing.

### STOP_INDICATION (0x8002) — Phone → HU

Empty message. Phone stops sending AV data for this channel.

---

## AV Data Frames

After START_INDICATION, the phone sends encoded media data:

- **0x0000 (AV_MEDIA_WITH_TIMESTAMP_INDICATION)** — includes timestamp
- **0x0001 (AV_MEDIA_INDICATION)** — raw data without timestamp

Large frames are fragmented using the standard frame header:
- FIRST frame: 6-byte size header (uint16 frame size + uint32 total size)
- MIDDLE frames: continuation data
- LAST frame: final fragment

### Flow Control — AV_MEDIA_ACK (0x8004)

```protobuf
message AVMediaAckIndication {
    optional int32 session = 1;
    optional uint32 value = 2;           // ACK counter
    repeated uint64 ack_timestamps = 3;
}
```

The HU **must** send ACKs or the phone stalls. The phone tracks unacked frames against `max_unacked` from setup and pauses when the limit is hit.

**Video:** With `max_unacked=10`, the HU can buffer up to 10 frames (~333ms at 30fps) before it must ACK. ACK after decoding each frame for lowest latency.

**Audio:** With `max_unacked=1`, every audio buffer must be ACKed before the next is sent. This keeps the audio pipeline tight but means any ACK delay causes audio gaps.

---

## Audio Focus (Channel 0)

Audio focus is managed on the **control channel** (ch 0), not on the audio channels themselves.

### AudioFocusRequest (0x0012) — Phone → HU

```protobuf
message AudioFocusRequest {
    optional AudioFocusType audio_focus_type = 1;
}
```

**Focus types** (from `vvf.java`):

| Value | Name | Usage |
|-------|------|-------|
| 1 | GAIN | Music playback — permanent focus |
| 2 | GAIN_TRANSIENT | Assistant/TTS — temporary focus |
| 3 | GAIN_TRANSIENT_MAY_DUCK | Navigation prompt — ducks media briefly |
| 4 | RELEASE | Release audio focus |

### AudioFocusResponse (0x0013) — HU → Phone

```protobuf
message AudioFocusResponse {
    optional AudioFocusState audio_focus_state = 1;
    optional bool granted = 2;
}
```

**Focus states:**

| Value | Name | Meaning |
|-------|------|---------|
| 1 | GAIN | Full focus granted |
| 2 | GAIN_TRANSIENT | Temporary focus granted |
| 3 | LOSS | Focus lost — stop playback |
| 4 | LOSS_TRANSIENT_CAN_DUCK | Focus lost — lower volume |
| 5 | LOSS_TRANSIENT | Focus lost temporarily — pause |
| 6 | GAIN_MEDIA_ONLY | Media focus only |
| 7 | GAIN_TRANSIENT_GUIDANCE_ONLY | Nav guidance focus only |

**The HU is the audio focus arbiter.** It must implement Android-compatible focus semantics:
- GAIN request during GAIN → grant (replace)
- GAIN_TRANSIENT_MAY_DUCK during GAIN → grant, duck media (LOSS_TRANSIENT_CAN_DUCK)
- RELEASE → acknowledge, no audio playing

---

## Video Focus (Channel 3)

### VideoFocusIndication (0x8008) — HU → Phone

```protobuf
message VideoFocusIndication {
    optional VideoFocusMode focus_mode = 1;
    optional bool unrequested = 2;
}
```

**Focus modes:**

| Value | Name | Meaning |
|-------|------|---------|
| 1 | VIDEO_FOCUS_PROJECTED | AA is active, full projection |
| 2 | VIDEO_FOCUS_NATIVE | HU's native UI is showing |
| 3 | VIDEO_FOCUS_NATIVE_TRANSIENT | Temporary native UI (e.g. reverse camera) |
| 4 | VIDEO_FOCUS_PROJECTED_NO_INPUT_FOCUS | AA visible but input goes to native UI |

The HU sends this to tell the phone whether AA is currently displayed. The phone adjusts encoding accordingly (may pause video when not focused).

---

## Sensor & Input Channels

These channels have no AV-style setup. Data flows immediately after channel open.

### Sensor Channel (ch 2)

Phone may send `SensorStartRequest` to subscribe to specific sensor types. HU sends `SensorEventIndication` with sensor data. See [03-service-discovery](03-service-discovery.md) for sensor types.

### Input Channel (ch 1)

HU sends `InputEventIndication` with touch/button/scroll events. No handshake needed — events flow immediately.

---

## Complete Session Timeline (Observed)

```
t+0.0s    TCP connected
t+0.1s    Version exchange (v1.1 → v1.7 MATCH)
t+0.2s    SSL handshake complete
t+0.3s    Auth complete, Service Discovery exchanged
t+0.4s    Channel opens begin (Video first)
           → Video: open, setup (480p H.264 30fps), start
           → Audio: open, setup (48kHz/16kHz), start
           → Input/Sensor: open (immediate data flow)
           → BT/WiFi: open
t+0.6s    Audio focus: GAIN requested and granted
t+0.7s    Video focus: PROJECTED — first video frame
t+1.0s    Projection fully active
           → 115 car connection listeners notified
           → PROJECTION_MODE_STARTED
```

Total: **~1 second** from TCP connect to fully projected AA display.

---

## Error Handling

| Error | Detection | Recovery |
|-------|-----------|---------|
| Channel open rejected | Status ≠ 0 in ChannelOpenResponse | Skip that channel, log warning |
| AV setup rejected | Status ≠ 0 in SetupResponse | Channel non-functional |
| No ACKs sent (video) | Phone pauses after max_unacked frames | Video freezes — must ACK |
| No ACKs sent (audio) | Phone stalls after 1 buffer | Audio silence — must ACK |
| Audio focus denied | Phone may not start playback | Grant focus to enable audio |
| Video focus stuck NATIVE | Phone doesn't send video frames | Send VIDEO_FOCUS_PROJECTED |

## Log Tags

| Tag | What it shows |
|-----|--------------|
| `CAR.GAL.GAL.LITE` | Channel opens, per-channel queue creation |
| `CAR.GAL.VIDEO.LITE` | Video flow control, frame ACKs |
| `CAR.GAL.AUDIO.LITE` | Audio focus messages |
| `CAR.AUDIO.CHANNEL` | Audio stream enable/disable |
| `CAR.AUDIO.FOCUS` | Audio focus arbitration |
| `CAR.AUDIO.MEDIA` | Media audio stream (ch 4) |
| `CAR.AUDIO.TTS` | TTS/speech stream (ch 5) |
| `CAR.AUDIO.SYSTEM` | System notification audio (ch 6) |
| `GH.CAR.ProxyEP.LITE` | Per-channel proxy endpoint activity |
| `CAR.PROJECTION.PRES` | Projection UI presenter state |

## Postcondition

At the end of this phase:
- All channels open and configured
- Video streaming (phone → HU)
- Audio streaming (phone → HU, per audio focus)
- Sensor data flowing (HU → phone)
- Input events flowing (HU → phone)
- **AA is fully projected and interactive**

## References

- `oaa/control/ChannelOpenRequestMessage.proto`, `ChannelOpenResponseMessage.proto`
- `oaa/av/AVChannelMessageIdsEnum.proto` — all AV message IDs
- `oaa/av/AVChannelSetupResponseMessage.proto`
- `oaa/av/AVChannelStartIndicationMessage.proto`
- `oaa/av/AVMediaAckIndicationMessage.proto`
- `oaa/audio/AudioFocusRequestMessage.proto`, `AudioFocusResponseMessage.proto`
- `oaa/audio/AudioFocusTypeEnum.proto`, `AudioFocusStateEnum.proto`
- `oaa/video/VideoFocusModeEnum.proto`
- [`phone-side-debug.md`](../phone-side-debug.md) — Phase 6-7 (channel setup, projection start)
