# 04 — Channel Lifecycle

## Proto Confidence Summary

| Message | Tier | Evidence | Audit File |
|---------|------|----------|------------|
| ChannelOpenRequest | Silver | apk_static + cross_version | [ChannelOpenRequestMessage.audit.yaml](../../oaa/control/ChannelOpenRequestMessage.audit.yaml) |
| ChannelOpenResponse | Silver | apk_static + cross_version | [ChannelOpenResponseMessage.audit.yaml](../../oaa/control/ChannelOpenResponseMessage.audit.yaml) |
| AVChannelSetupRequest | Silver | apk_static + cross_version | [AVChannelSetupRequestMessage.audit.yaml](../../oaa/av/AVChannelSetupRequestMessage.audit.yaml) |
| AVChannelSetupResponse | Silver | apk_static + cross_version | [AVChannelSetupResponseMessage.audit.yaml](../../oaa/av/AVChannelSetupResponseMessage.audit.yaml) |
| AVChannelStartIndication | Silver | apk_static + cross_version | [AVChannelStartIndicationMessage.audit.yaml](../../oaa/av/AVChannelStartIndicationMessage.audit.yaml) |
| AVMediaAckIndication | Silver | apk_static + cross_version | [AVMediaAckIndicationMessage.audit.yaml](../../oaa/av/AVMediaAckIndicationMessage.audit.yaml) |
| AVInputOpenRequest | Silver | apk_static + cross_version | [AVInputOpenRequestMessage.audit.yaml](../../oaa/av/AVInputOpenRequestMessage.audit.yaml) |
| AVInputOpenResponse | Silver | apk_static + cross_version | [AVInputOpenResponseMessage.audit.yaml](../../oaa/av/AVInputOpenResponseMessage.audit.yaml) |
| AVChannelMessageIds (enum) | Unverified | -- | -- |
| AudioFocusRequest | Silver | apk_static + cross_version | [AudioFocusRequestMessage.audit.yaml](../../oaa/audio/AudioFocusRequestMessage.audit.yaml) |
| AudioFocusResponse | Silver | apk_static + cross_version | [AudioFocusResponseMessage.audit.yaml](../../oaa/audio/AudioFocusResponseMessage.audit.yaml) |
| AudioFocusType (enum) | Unverified | -- | -- |
| AudioFocusState (enum) | Unverified | -- | -- |
| VideoFocusIndication | Silver | apk_static + cross_version | [VideoFocusIndicationMessage.audit.yaml](../../oaa/video/VideoFocusIndicationMessage.audit.yaml) |
| VideoFocusRequest | Silver | apk_static + cross_version | [VideoFocusRequestMessage.audit.yaml](../../oaa/video/VideoFocusRequestMessage.audit.yaml) |
| VideoFocusMode (enum) | Unverified | -- | -- |

## Overview

After service discovery, the HU opens individual channels for each advertised service. Each channel follows a lifecycle: open -> setup -> start -> data exchange -> stop -> close. AV channels (video, audio) have additional setup negotiation and flow control. Audio channels also involve focus arbitration.

## Prerequisites

- Service discovery complete (from [03-service-discovery](03-service-discovery.md))
- Both sides know each other's capabilities
- All messages encrypted (TLS), using `MessageType::Specific` (NOT Control)
- Exception: channel open/close messages use `MessageType::Control` on channel 0

## Sequence Diagram -- Channel Open

```
Phone                                        Head Unit
  |                                             |
  |  -- Per-channel, HU opens each one -------  |
  |                                             |
  |<-- CHANNEL_OPEN_REQUEST (0x0007) ---------- |  ch 0, Control msg type
  |--- CHANNEL_OPEN_RESPONSE (0x0008) -------> |  ch 0, Control msg type
  |                                             |
  |  -- For AV channels (video, audio): ------  |
  |                                             |
  |--- SETUP_REQUEST (0x8000) ---------------> |  ch N, Specific msg type
  |<-- SETUP_RESPONSE (0x8003) --------------- |  ch N, Specific msg type
  |--- START_INDICATION (0x8001) ------------> |  ch N, Specific msg type
  |--- [AV data frames] --------------------> |
  |<-- AV_MEDIA_ACK (0x8004) ---------------- |  Flow control
  |                                             |
  |  -- For non-AV channels (sensor, input): -  |
  |                                             |
  |     Data exchange begins immediately        |
  |     after CHANNEL_OPEN_RESPONSE             |
```

> **Gotcha:** Channel open requests go on channel 0 with `MessageType::Control`, but all subsequent per-channel messages use `MessageType::Specific` on the channel's own ID. Mixing these up causes the phone to silently ignore messages with no error response. This is the single most common implementation mistake.

---

## Channel Open/Close

> Confidence: Silver [apk_static + cross_version] -- see [ChannelOpenRequestMessage.audit.yaml](../../oaa/control/ChannelOpenRequestMessage.audit.yaml)

### ChannelOpenRequest (0x0007) -- HU -> Phone

Sent on **channel 0** with `MessageType::Control`.

```protobuf
message ChannelOpenRequest {
    optional sint32 priority = 1;    // Channel priority (zigzag encoded)
    optional int32 channel_id = 2;   // Which channel to open
}
```

### ChannelOpenResponse (0x0008) -- Phone -> HU

```protobuf
message ChannelOpenResponse {
    optional Status status = 1;      // 0 = OK
}
```

### Channel Open Order (Observed)

The HU opens channels in this order:

```
ch 0  -- Control (implicit, always open)
ch 3  -- Video
ch 4  -- Media Audio
ch 5  -- Speech Audio
ch 6  -- System Audio
ch 7  -- AV Input (microphone)
ch 1  -- Input
ch 2  -- Sensor
ch 8  -- Bluetooth
ch 14 -- WiFi
```

AV channels (3-7) are opened first because they require additional setup negotiation.

### Implementation Guidance -- Channel Open Sequence

```c
// Open channels in the correct order: AV first, then non-AV
typedef struct {
    int channel_id;
    const char *name;
    bool is_av;  // true = needs AV setup after open
} ChannelDef;

static const ChannelDef channels[] = {
    {3, "Video",        true},
    {4, "Media Audio",  true},
    {5, "Speech Audio", true},
    {6, "System Audio", true},
    {7, "AV Input",     true},
    {1, "Input",        false},
    {2, "Sensor",       false},
    {8, "Bluetooth",    false},
    {14, "WiFi",        false},
};

void open_all_channels(Session *session) {
    for (int i = 0; i < sizeof(channels)/sizeof(channels[0]); i++) {
        // ChannelOpenRequest is sent on channel 0, MessageType::Control
        ChannelOpenRequest req = {0};
        req.priority = 0;
        req.channel_id = channels[i].channel_id;
        send_control_message(session, 0, CHANNEL_OPEN_REQUEST, &req);

        // Wait for ChannelOpenResponse
        ChannelOpenResponse resp;
        recv_control_message(session, 0, CHANNEL_OPEN_RESPONSE, &resp);
        if (resp.status != 0) {
            log_warn("Channel %d (%s) rejected", channels[i].channel_id,
                     channels[i].name);
            continue;
        }

        // AV channels need setup negotiation (handled by phone)
        // Non-AV channels are ready for data immediately
    }
}
```

### ChannelCloseNotification (0x0009)

Either side can close a channel:

```
Message ID: 0x0009 on channel 0, MessageType::Control
```

---

## AV Channel Setup (Video & Audio)

> Confidence: Silver [apk_static + cross_version] -- see [AVChannelSetupRequestMessage.audit.yaml](../../oaa/av/AVChannelSetupRequestMessage.audit.yaml)

All AV channels (video ch 3, audio ch 4/5/6, mic ch 7) share the same message IDs but on their respective channel numbers.

### AV Message IDs

| ID | Name | Direction |
|----|------|-----------|
| 0x0000 | AV_MEDIA_WITH_TIMESTAMP_INDICATION | Phone -> HU |
| 0x0001 | AV_MEDIA_INDICATION | Phone -> HU |
| 0x8000 | SETUP_REQUEST | Phone -> HU |
| 0x8001 | START_INDICATION | Phone -> HU |
| 0x8002 | STOP_INDICATION | Phone -> HU |
| 0x8003 | SETUP_RESPONSE | HU -> Phone |
| 0x8004 | AV_MEDIA_ACK_INDICATION | HU -> Phone |
| 0x8005 | AV_INPUT_OPEN_REQUEST | Phone -> HU |
| 0x8006 | AV_INPUT_OPEN_RESPONSE | HU -> Phone |
| 0x8007 | VIDEO_FOCUS_REQUEST | Phone -> HU |
| 0x8008 | VIDEO_FOCUS_INDICATION | HU -> Phone |
| 0x800B | AUDIO_UNDERFLOW | HU -> Phone |
| 0x8013 | MEDIA_STATS | Phone -> HU |

> **Gotcha:** `MessageType` must be `Specific` (not `Control`) for AV messages on channels 3-7. Using `Control` causes the phone to silently ignore the message with no error response. This applies to ALL messages in the table above -- setup, ACK, focus, everything. Only channel open/close on channel 0 uses `Control`.

### SETUP_REQUEST (0x8000) -- Phone -> HU

The phone sends this after channel open to negotiate AV parameters. The payload is an `AVChannelSetupRequest` (config index selection).

### SETUP_RESPONSE (0x8003) -- HU -> Phone

> Confidence: Silver [apk_static + cross_version] -- see [AVChannelSetupResponseMessage.audit.yaml](../../oaa/av/AVChannelSetupResponseMessage.audit.yaml)

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

### START_INDICATION (0x8001) -- Phone -> HU

> Confidence: Silver [apk_static + cross_version] -- see [AVChannelStartIndicationMessage.audit.yaml](../../oaa/av/AVChannelStartIndicationMessage.audit.yaml)

```protobuf
message AVChannelStartIndication {
    optional int32 session = 1;
    optional uint32 config = 2;                          // Selected config index
    optional AVChannelSessionType session_type = 3;
    optional AVChannelMediaConfig media_config = 4;
}
```

After this message, AV data frames begin flowing.

### STOP_INDICATION (0x8002) -- Phone -> HU

Empty message. Phone stops sending AV data for this channel.

---

## AV Data Frames

After START_INDICATION, the phone sends encoded media data:

- **0x0000 (AV_MEDIA_WITH_TIMESTAMP_INDICATION)** -- includes timestamp
- **0x0001 (AV_MEDIA_INDICATION)** -- raw data without timestamp

Large frames are fragmented using the standard frame header:
- FIRST frame: 6-byte size header (uint16 frame size + uint32 total size)
- MIDDLE frames: continuation data
- LAST frame: final fragment

### Flow Control -- AV_MEDIA_ACK (0x8004)

> Confidence: Silver [apk_static + cross_version] -- see [AVMediaAckIndicationMessage.audit.yaml](../../oaa/av/AVMediaAckIndicationMessage.audit.yaml)

```protobuf
message AVMediaAckIndication {
    optional int32 session = 1;
    optional uint32 value = 2;           // ACK counter
    repeated uint64 ack_timestamps = 3;
}
```

> **Gotcha:** AVMediaAck is critical for flow control -- without it, the phone stops sending AV frames after the initial burst. The phone tracks unacked frames against `max_unacked` from setup and pauses when the limit is hit. If the HU never ACKs, the phone will stall permanently after `max_unacked` frames. There is no timeout-based recovery -- the phone waits indefinitely.

The HU **must** send ACKs or the phone stalls. The phone tracks unacked frames against `max_unacked` from setup and pauses when the limit is hit.

**Video:** With `max_unacked=10`, the HU can buffer up to 10 frames (~333ms at 30fps) before it must ACK. ACK after decoding each frame for lowest latency.

**Audio:** With `max_unacked=1`, every audio buffer must be ACKed before the next is sent. This keeps the audio pipeline tight but means any ACK delay causes audio gaps.

### Implementation Guidance -- AV ACK Flow Control

```c
// Track received bytes per AV channel and send ACKs periodically
typedef struct {
    int channel_id;
    int session;
    uint32_t ack_counter;
    uint32_t frames_since_ack;
    uint32_t max_unacked;
} AVFlowState;

void on_av_data_received(AVFlowState *state, const uint8_t *data, size_t len) {
    // Decode/render the frame...
    decode_frame(state->channel_id, data, len);

    state->frames_since_ack++;

    // ACK after each frame for lowest latency (video)
    // or after each buffer (audio, where max_unacked=1)
    if (state->frames_since_ack >= 1) {
        AVMediaAckIndication ack = {0};
        ack.session = state->session;
        ack.value = ++state->ack_counter;

        // MUST use MessageType::Specific on the channel's own ID
        send_specific_message(state->channel_id,
                              AV_MEDIA_ACK_INDICATION, &ack);
        state->frames_since_ack = 0;
    }
}

// Example main loop for video channel
void video_recv_loop(Session *session) {
    AVFlowState video = {
        .channel_id = 3,
        .session = 0,       // Set from START_INDICATION
        .ack_counter = 0,
        .frames_since_ack = 0,
        .max_unacked = 10,  // Set from SETUP_RESPONSE
    };

    while (session->running) {
        Message msg = recv_message(session, video.channel_id);
        switch (msg.id) {
            case AV_MEDIA_WITH_TIMESTAMP:
            case AV_MEDIA:
                on_av_data_received(&video, msg.data, msg.len);
                break;
            case AV_CHANNEL_START:
                video.session = parse_start_indication(msg).session;
                break;
            case AV_CHANNEL_STOP:
                // Phone stopped sending -- reset state
                video.frames_since_ack = 0;
                break;
        }
    }
}
```

---

## Audio Focus (Channel 0)

> Confidence: Silver [apk_static + cross_version] -- see [AudioFocusRequestMessage.audit.yaml](../../oaa/audio/AudioFocusRequestMessage.audit.yaml)

Audio focus is managed on the **control channel** (ch 0), not on the audio channels themselves.

> **Gotcha:** Audio focus must be requested BEFORE starting audio playback -- the phone will not send audio data without a focus grant. If the HU opens audio channels but never grants audio focus, the phone's audio pipeline remains paused. The HU must respond to `AudioFocusRequest` messages promptly.

### AudioFocusRequest (0x0012) -- Phone -> HU

```protobuf
message AudioFocusRequest {
    optional AudioFocusType audio_focus_type = 1;
}
```

**Focus types** (from `vvf.java`):

| Value | Name | Usage |
|-------|------|-------|
| 1 | GAIN | Music playback -- permanent focus |
| 2 | GAIN_TRANSIENT | Assistant/TTS -- temporary focus |
| 3 | GAIN_TRANSIENT_MAY_DUCK | Navigation prompt -- ducks media briefly |
| 4 | RELEASE | Release audio focus |

### AudioFocusResponse (0x0013) -- HU -> Phone

> Confidence: Silver [apk_static + cross_version] -- see [AudioFocusResponseMessage.audit.yaml](../../oaa/audio/AudioFocusResponseMessage.audit.yaml)

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
| 3 | LOSS | Focus lost -- stop playback |
| 4 | LOSS_TRANSIENT_CAN_DUCK | Focus lost -- lower volume |
| 5 | LOSS_TRANSIENT | Focus lost temporarily -- pause |
| 6 | GAIN_MEDIA_ONLY | Media focus only |
| 7 | GAIN_TRANSIENT_GUIDANCE_ONLY | Nav guidance focus only |

**The HU is the audio focus arbiter.** It must implement Android-compatible focus semantics:
- GAIN request during GAIN -> grant (replace)
- GAIN_TRANSIENT_MAY_DUCK during GAIN -> grant, duck media (LOSS_TRANSIENT_CAN_DUCK)
- RELEASE -> acknowledge, no audio playing

---

## Video Focus (Channel 3)

> Confidence: Silver [apk_static + cross_version] -- see [VideoFocusIndicationMessage.audit.yaml](../../oaa/video/VideoFocusIndicationMessage.audit.yaml)

### VideoFocusIndication (0x8008) -- HU -> Phone

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

HU sends `InputEventIndication` with touch/button/scroll events. No handshake needed -- events flow immediately.

---

## Complete Session Timeline (Observed)

```
t+0.0s    TCP connected
t+0.1s    Version exchange (v1.1 -> v1.7 MATCH)
t+0.2s    SSL handshake complete
t+0.3s    Auth complete, Service Discovery exchanged
t+0.4s    Channel opens begin (Video first)
           -> Video: open, setup (480p H.264 30fps), start
           -> Audio: open, setup (48kHz/16kHz), start
           -> Input/Sensor: open (immediate data flow)
           -> BT/WiFi: open
t+0.6s    Audio focus: GAIN requested and granted
t+0.7s    Video focus: PROJECTED -- first video frame
t+1.0s    Projection fully active
           -> 115 car connection listeners notified
           -> PROJECTION_MODE_STARTED
```

Total: **~1 second** from TCP connect to fully projected AA display.

---

## Minimum Viable Connection Checklist

A concise verification aid covering every required step from transport through active session. Each item links to the relevant documentation section.

1. **Establish transport** -- TCP socket (wireless) or USB bulk endpoints (wired) providing a bidirectional byte stream. See [01 -- Transport Setup](01-transport-setup.md).

2. **Send VERSION_REQUEST** -- HU sends 6-byte binary version request (v1.1 minimum) on channel 0. See [02 -- Version Exchange](02-version-ssl-auth.md#step-1-version-exchange).

3. **Receive VERSION_RESPONSE** -- Verify status is MATCH (0x0000). If MISMATCH, tear down. See [02 -- Version Exchange](02-version-ssl-auth.md#step-1-version-exchange).

4. **Perform TLS 1.2 handshake** -- HU is TLS client, phone is TLS server. Use in-memory BIO pairs, not socket-level TLS. HU must present a valid certificate. See [02 -- SSL Handshake](02-version-ssl-auth.md#step-2-ssl-handshake).

5. **Send AUTH_COMPLETE** -- Encrypted protobuf with status=0. All subsequent messages are encrypted. See [02 -- Authentication](02-version-ssl-auth.md#step-3-authentication--binding).

6. **Send ServiceDiscoveryResponse** -- Advertise all supported channels (minimum: video, media audio, input, sensor). Parse and store PingConfiguration from phone's response. See [03 -- Service Discovery](03-service-discovery.md#step-1-servicediscoveryresponse-0x0006----hu--phone).

7. **Receive ServiceDiscoveryRequest** -- Phone sends device info and icons. See [03 -- Service Discovery](03-service-discovery.md#step-2-servicediscoveryrequest-0x0005----phone--hu).

8. **Open channels** -- Send ChannelOpenRequest for each channel on channel 0 with `MessageType::Control`. Open AV channels first (3-7), then non-AV (1, 2, 8, 14). See [Channel Open/Close](#channel-openclose).

9. **Handle AV setup** -- For each AV channel: receive SETUP_REQUEST, respond with SETUP_RESPONSE (set `max_unacked`), receive START_INDICATION. See [AV Channel Setup](#av-channel-setup-video--audio).

10. **Send AVMediaAck** -- ACK received AV frames to maintain flow control. Without ACKs, the phone stalls after `max_unacked` frames. See [Flow Control](#flow-control----av_media_ack-0x8004).

11. **Grant audio focus** -- Respond to AudioFocusRequest with appropriate AudioFocusResponse. Phone will not send audio data without focus. See [Audio Focus](#audio-focus-channel-0).

12. **Send VideoFocusIndication** -- Set `VIDEO_FOCUS_PROJECTED` to start receiving video frames. See [Video Focus](#video-focus-channel-3).

---

## Error Handling

| Error | Detection | Recovery |
|-------|-----------|---------|
| Channel open rejected | Status != 0 in ChannelOpenResponse | Skip that channel, log warning |
| AV setup rejected | Status != 0 in SetupResponse | Channel non-functional |
| No ACKs sent (video) | Phone pauses after max_unacked frames | Video freezes -- must ACK |
| No ACKs sent (audio) | Phone stalls after 1 buffer | Audio silence -- must ACK |
| Audio focus denied | Phone may not start playback | Grant focus to enable audio |
| Video focus stuck NATIVE | Phone does not send video frames | Send VIDEO_FOCUS_PROJECTED |

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
- Video streaming (phone -> HU)
- Audio streaming (phone -> HU, per audio focus)
- Sensor data flowing (HU -> phone)
- Input events flowing (HU -> phone)
- **AA is fully projected and interactive**

Session is active. See [Session Maintenance and Teardown](05-session-maintenance-teardown.md) for keepalive and shutdown.

## References

- `oaa/control/ChannelOpenRequestMessage.proto`, `ChannelOpenResponseMessage.proto`
- `oaa/av/AVChannelMessageIdsEnum.proto` -- all AV message IDs
- `oaa/av/AVChannelSetupResponseMessage.proto`
- `oaa/av/AVChannelStartIndicationMessage.proto`
- `oaa/av/AVMediaAckIndicationMessage.proto`
- `oaa/audio/AudioFocusRequestMessage.proto`, `AudioFocusResponseMessage.proto`
- `oaa/audio/AudioFocusTypeEnum.proto`, `AudioFocusStateEnum.proto`
- `oaa/video/VideoFocusModeEnum.proto`
- [`phone-side-debug.md`](../phone-side-debug.md) -- Phase 6-7 (channel setup, projection start)
