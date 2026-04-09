# Audio Channels (4, 5, 6)

## Proto Confidence Summary

| Message | Tier | Evidence | Audit File |
|---------|------|----------|------------|
| AudioFocusRequest | Silver | apk_static + cross_version | [AudioFocusRequestMessage.audit.yaml](../../oaa/audio/AudioFocusRequestMessage.audit.yaml) |
| AudioFocusResponse | Silver | apk_static + cross_version | [AudioFocusResponseMessage.audit.yaml](../../oaa/audio/AudioFocusResponseMessage.audit.yaml) |
| ~~AudioFocusState (message)~~ | **Retracted** | Actually RadioFavoriteToggleRequest (0x8021 on radio ch 15) | [AudioFocusStateMessage.audit.yaml](../../oaa/audio/AudioFocusStateMessage.audit.yaml) |
| AudioConfig | Silver | apk_static + cross_version | [AudioConfigData.audit.yaml](../../oaa/audio/AudioConfigData.audit.yaml) |
| ~~AudioStreamType (message)~~ | **Retracted** | Actually RadioTuneDirectionRequest (0x8022 on radio ch 15) | [AudioStreamTypeMessage.audit.yaml](../../oaa/audio/AudioStreamTypeMessage.audit.yaml) |
| AudioFocusChannel | Bronze | apk_static | [AudioFocusChannelData.audit.yaml](../../oaa/audio/AudioFocusChannelData.audit.yaml) |
| ~~AudioStreamType (enum)~~ | **Retracted** | Actually RadioTuneDirection enum on radio ch 15 | [AudioStreamTypeEnum.audit.yaml](../../oaa/audio/AudioStreamTypeEnum.audit.yaml) |
| MicrophoneOpenResponse | **Gold** | apk_deep_trace (2026-03-06) — NEW | (mic channel, 0x8006) |
| AudioFocusState (enum) | Unverified | -- | -- |
| AudioFocusType (enum) | Unverified | -- | -- |
| AudioType (enum) | Unverified | -- | -- |
| AVChannelSetupRequest | Silver | apk_static + cross_version | [AVChannelSetupRequestMessage.audit.yaml](../../oaa/av/AVChannelSetupRequestMessage.audit.yaml) |
| AVChannelSetupResponse | Silver | apk_static + cross_version | [AVChannelSetupResponseMessage.audit.yaml](../../oaa/av/AVChannelSetupResponseMessage.audit.yaml) |
| AVChannelStartIndication | Silver | apk_static + cross_version | [AVChannelStartIndicationMessage.audit.yaml](../../oaa/av/AVChannelStartIndicationMessage.audit.yaml) |
| AVMediaAckIndication | Silver | apk_static + cross_version | [AVMediaAckIndicationMessage.audit.yaml](../../oaa/av/AVMediaAckIndicationMessage.audit.yaml) |

---

## Overview

> Confidence: Unverified -- section references AudioType enum (Unverified) alongside Silver messages

Android Auto uses three separate audio channels that share identical wire-level messages but serve different audio roles:

| Channel ID | AudioType | Role | Bidirectional |
|:---:|-----------|------|:---:|
| 4 | MEDIA (3) | Music, podcasts, other media playback | No (phone -> HU) |
| 5 | SPEECH (1) | Navigation prompts, assistant voice, TTS | No (phone -> HU) |
| 6 | SYSTEM (2) | Phone call audio | Yes (bidirectional) |

All three channels use the same proto messages from `oaa/audio/` and the shared AV messages from `oaa/av/`. The channel ID determines which audio role a stream serves, not the message type. The `AudioType` enum value is configured during service discovery -- the wire messages themselves are identical across channels.

Audio focus is the arbitration mechanism that coordinates between these three channels. When the phone needs to play navigation audio over music, or a phone call interrupts everything, audio focus negotiation determines which channel gets priority and how others respond (duck volume, pause, or stop). Focus messages flow on the **control channel (ch 0)**, not on the audio channels themselves.

**Prerequisite:** Audio channels require AV channel setup before any audio data flows. See [04-channel-lifecycle.md](../interactions/04-channel-lifecycle.md) for the channel open and AV setup sequence.

---

## Message Catalog

### Focus Messages (Control Channel, ch 0)

> Confidence: Silver [apk_static, cross_version] -- AudioFocusRequest and AudioFocusResponse are Silver; AudioFocusType and AudioFocusState enums are Unverified but values well-established in aasdk and OEM firmware

| Msg ID | Message | Direction | Purpose | Confidence |
|--------|---------|-----------|---------|:---:|
| 0x0012 | AudioFocusRequest | Phone -> HU | Request audio focus (gain, transient, release) | Silver |
| 0x0013 | AudioFocusResponse | HU -> Phone | Grant or deny focus, report resulting state | Silver |

### Audio-Specific Messages (Per-Channel, ch 4/5/6)

> **Both messages retracted (2026-03-06)** — AudioFocusState and AudioStreamType were misidentified radio channel messages. No audio-specific per-channel messages exist beyond the shared AV set.

| Msg ID | Message | Direction | Purpose | Confidence |
|--------|---------|-----------|---------|:---:|
| ~~0x8021~~ | ~~AudioFocusState~~ | — | **RETRACTED** — actually RadioFavoriteToggleRequest on radio channel (service 15) | Retracted |
| ~~0x8022~~ | ~~AudioStreamType~~ | — | **RETRACTED** — actually RadioTuneDirectionRequest on radio channel (service 15) | Retracted |

### Microphone Input (ch 6, mic direction)

| Msg ID | Message | Direction | Purpose | Confidence |
|--------|---------|-----------|---------|:---:|
| 0x8006 | MicrophoneOpenResponse | HU -> Phone | Mic session opened (status + session_config) | **Gold** |

Raw mic audio uses wire IDs 0x0000 (HU→Phone) and 0x0001 (Phone→HU) — raw PCM with 8-byte timestamp header, no protobuf.

### AV Setup Messages (Per-Channel, ch 4/5/6)

> Confidence: Silver [apk_static, cross_version]

These shared AV messages are documented in detail in [04-channel-lifecycle.md](../interactions/04-channel-lifecycle.md). Summary for audio context:

| Msg ID | Message | Direction | Purpose | Confidence |
|--------|---------|-----------|---------|:---:|
| 0x8000 | AVChannelSetupRequest | Phone -> HU | Select audio codec configuration | Silver |
| 0x8003 | AVChannelSetupResponse | HU -> Phone | Accept/reject, set max_unacked | Silver |
| 0x8001 | AVChannelStartIndication | Phone -> HU | Audio stream begins | Silver |
| 0x8002 | AVChannelStopIndication | Phone -> HU | Audio stream stops | Silver |
| 0x8004 | AVMediaAckIndication | HU -> Phone | Flow control acknowledgment | Silver |

### Config Messages (Service Discovery)

> Confidence: Silver [apk_static, cross_version]

| Message | Purpose | Confidence |
|---------|---------|:---:|
| AudioConfig | Sample rate, bit depth, channel count for audio setup | Silver |
| AudioFocusChannel | Empty marker message advertising audio focus support in service discovery | Bronze |

---

## Focus Negotiation -- State Machine

> Confidence: Unverified -- section combines Silver messages (AudioFocusRequest/Response) with Unverified enums (AudioFocusType, AudioFocusState)

Audio focus flows on the **control channel (ch 0)**, not on the audio channels. The phone requests focus; the HU is the sole arbiter that grants or denies it.

### Sequence: Normal Playback with Nav Prompt

```
Phone                                        Head Unit
  |                                             |
  |--- AudioFocusRequest (GAIN, 1) -----------> |  Phone wants media focus (ch 4)
  |<-- AudioFocusResponse (GAIN, granted) ----- |  HU grants full focus
  |--- AVChannelStartIndication (ch 4) -------> |  Audio stream begins
  |--- [PCM audio data] ---------------------> |
  |                                             |
  |  ... music playing ...                      |
  |                                             |
  |--- AudioFocusRequest (GAIN_NAVI, 3) ------> |  Nav prompt needs focus (ch 5)
  |<-- AudioFocusResponse (GAIN_T, granted) --- |  HU grants transient focus
  |                                             |  HU ducks ch 4 volume
  |--- AVChannelStartIndication (ch 5) -------> |  Nav audio stream begins
  |--- [nav prompt audio] -------------------> |
  |--- AudioFocusRequest (RELEASE, 4) --------> |  Nav prompt done (ch 5)
  |                                             |  HU restores ch 4 volume
  |                                             |
  |  ... music resumes full volume ...          |
```

### Sequence: Phone Call Interrupts Music

```
Phone                                        Head Unit
  |                                             |
  |  ... music playing on ch 4 ...              |
  |                                             |
  |--- AudioFocusRequest (GAIN, 1) -----------> |  Phone call needs exclusive focus (ch 6)
  |<-- AudioFocusResponse (GAIN, granted) ----- |  HU grants full focus
  |                                             |  HU pauses/mutes ch 4
  |--- AVChannelStartIndication (ch 6) -------> |  Call audio begins (bidirectional)
  |<-- [microphone audio from HU] ------------- |  Ch 6 is bidirectional
  |                                             |
  |  ... call in progress ...                   |
  |                                             |
  |--- AudioFocusRequest (RELEASE, 4) --------> |  Call ended
  |                                             |  HU restores ch 4
```

---

## Focus / Priority Model

> Confidence: Unverified -- AudioFocusType and AudioFocusState enums have no audit sidecars; values are well-established in aasdk and confirmed in OEM firmware decompilations (Alpine, Kenwood, Sony)

### AudioFocusType (Request Types)

The phone sends one of these values in `AudioFocusRequest.audio_focus_type`:

| Value | Name | Semantics |
|:---:|------|-----------|
| 0 | NONE | No focus requested |
| 1 | GAIN | Permanent focus -- music, call audio. Other channels should stop or pause. |
| 2 | GAIN_TRANSIENT | Temporary focus -- assistant, TTS. Other channels should pause but expect to resume. |
| 3 | GAIN_NAVI | Navigation prompt focus. Other channels should duck (lower volume) but continue playing. |
| 4 | RELEASE | Relinquish focus. Channel is done producing audio. |

> **Gotcha:** The proto enum names `GAIN_NAVI` at value 3. OEM firmware and some references call this `GAIN_TRANSIENT_MAY_DUCK`. Both refer to the same wire value. The semantics are duck-compatible: the HU should lower other audio but not stop it. Nav prompts (channel 5) typically use this value, but the protocol does not enforce channel-specific restrictions on focus types.

### AudioFocusState (Response States)

The HU sends one of these values in `AudioFocusResponse.audio_focus_state`:

| Value | Name | Semantics |
|:---:|------|-----------|
| 0 | NONE | No focus state |
| 1 | GAIN | Full focus granted |
| 2 | GAIN_TRANSIENT | Temporary focus granted |
| 3 | LOSS | Focus lost -- stop/pause playback |
| 4 | LOSS_TRANSIENT_CAN_DUCK | Focus lost to duck-compatible request -- lower volume |
| 5 | LOSS_TRANSIENT | Focus lost temporarily -- pause, expect to resume |
| 6 | GAIN_MEDIA_ONLY | Media-only focus (other audio types unaffected) |
| 7 | GAIN_TRANSIENT_GUIDANCE_ONLY | Guidance-only focus (only nav guidance affected) |

This model mirrors Android's `AudioManager.OnAudioFocusChangeListener` callbacks. The HU must implement compatible semantics -- the phone-side `AudioFocusManager` (log tag `CAR.AUDIO.AFM`) expects standard Android focus behavior.

### Focus Arbitration Rules

The HU is the sole focus arbiter. Recommended behavior:

| Incoming Request | Current State | HU Action |
|-----------------|---------------|-----------|
| GAIN | No active focus | Grant GAIN |
| GAIN | Another channel has GAIN | Grant new GAIN, send LOSS to previous |
| GAIN_TRANSIENT | GAIN active on another channel | Grant GAIN_TRANSIENT, send LOSS_TRANSIENT to other |
| GAIN_NAVI | GAIN active on another channel | Grant, send LOSS_TRANSIENT_CAN_DUCK to other |
| RELEASE | Any | Acknowledge, restore previous focus holder if any |

---

## Implementation Guide

> Confidence: Unverified -- guidance combines Silver proto structure with Unverified enum semantics

### Audio Focus Handler (C/C++)

```c
// Minimal audio focus arbitration on the HU side.
// Called when AudioFocusRequest (0x0012) arrives on control channel (ch 0).

void handle_audio_focus_request(int channel_id, AudioFocusType type) {
    switch (type) {
    case GAIN:
        // Permanent focus -- stop/pause all other audio channels
        for (int ch = 4; ch <= 6; ch++) {
            if (ch != channel_id && has_focus[ch]) {
                send_focus_loss(ch, LOSS);
                set_volume(ch, 0);
            }
        }
        has_focus[channel_id] = true;
        send_audio_focus_response(GAIN, /*granted=*/true);
        break;

    case GAIN_NAVI:  // aka GAIN_TRANSIENT_MAY_DUCK
        // Duck other channels to ~20% volume, don't stop them
        for (int ch = 4; ch <= 6; ch++) {
            if (ch != channel_id && has_focus[ch]) {
                send_focus_loss(ch, LOSS_TRANSIENT_CAN_DUCK);
                set_volume(ch, DUCKED_VOLUME);
            }
        }
        has_focus[channel_id] = true;
        send_audio_focus_response(GAIN_TRANSIENT, /*granted=*/true);
        break;

    case RELEASE:
        has_focus[channel_id] = false;
        // Restore previous focus holder
        restore_previous_focus();
        break;
    }
}
```

### Volume Ducking

When the HU receives a GAIN_NAVI (duck) focus request, it should:

1. Lower media audio (ch 4) volume to approximately 20% (exact level is implementation-defined)
2. Continue playing the ducked audio -- do NOT pause or stop it
3. When the nav prompt channel (ch 5) sends RELEASE, restore media volume to 100%

The ducking response time should be under 200ms to avoid audible artifacts where both streams play at full volume simultaneously.

---

## Codec Negotiation

> Confidence: Silver [apk_static, 16.2 deep trace] -- codec selection algorithm fully traced through APK

### Supported Codecs — MediaCodecType Enum

| Value | Name | Status |
|:-----:|------|--------|
| 0 | MEDIA_CODEC_UNKNOWN | Default/fallback |
| 1 | MEDIA_CODEC_AUDIO_PCM | **Mandatory** — always supported, universal fallback |
| 2 | MEDIA_CODEC_AUDIO_AAC_LC | Supported — AAC-LC without framing |
| 4 | MEDIA_CODEC_AUDIO_AAC_LC_ADTS | Supported — AAC-LC with ADTS framing headers |

**There is no Opus codec.** The string "opus" does not appear anywhere in the AA 16.2 APK. Audio is strictly PCM or AAC-LC.

Values 3, 5, 6, 7 are video codecs (H.264, VP9, AV1, H.265) — not relevant for audio.

### AudioConfig Constraints

The phone validates these hard limits (`C0000a.m3D()` in 16.2):

| Parameter | Accepted Values |
|-----------|----------------|
| Sample rate | 48000 Hz or 16000 Hz only |
| Bit depth | 16 only |
| Channel count | 1 (mono) or 2 (stereo) only |

Any config not matching these constraints is rejected.

### How Codec Selection Works

There is **no multi-codec negotiation**. The HU declares ONE codec per channel:

1. HU sets `AVChannel.audio_type` (field 2 of `vye`) to a `MediaCodecType` value in the SDP
2. Phone reads this value. If unrecognized, falls back to `MEDIA_CODEC_AUDIO_PCM`
3. If AAC (value 2 or 4): phone initializes an AAC encoder (`hsk` class). For AAC-LC-ADTS (value 4), ADTS framing headers are added
4. If PCM (value 1): no encoder — raw PCM samples sent directly
5. Phone sends `AVChannelSetupRequest` (msg 0x8000) with `config_index = codec_enum_value`
6. HU responds with `AVChannelSetupResponse` (msg 0x8003): status OK/FAIL, max_unacked buffer depth

The `repeated AudioConfig` field in `AVChannel` (field 4) specifies **format parameters** (sample rate, channels), NOT alternative codecs. Multiple AudioConfig entries = different sample rate/channel combinations the HU supports.

### Per-Channel Defaults

| Channel | Type | Default Format | Sample Rate | Channels |
|---------|------|---------------|-------------|----------|
| 4 | Media | 48000_STEREO | 48000 Hz | Stereo |
| 5 | Guidance/TTS | 16000_MONO or 48000_MONO | 16000 or 48000 Hz | Mono |
| 6 | Phone call | 16000_MONO or 48000_MONO | 16000 or 48000 Hz | Mono |

Selection logic from `hqh.java:160-166`:
- Media channel → always 48kHz stereo
- Other channels → 16kHz mono if HU supports it, otherwise 48kHz mono

### Audio Format Priority

From `hrf.java:127-141`, the phone uses priority lists:
- **Default**: [STEREO_48000, MONO_16000, MONO_48000] — prefers stereo
- **Alternative**: [MONO_16000, MONO_48000, STEREO_48000] — prefers mono (used for guidance/system)

### Audio Buffer Sizing

From `ibt.m20149r()`:

| Codec | Sample Rate | Buffer Size | Buffer Duration |
|-------|-------------|-------------|-----------------|
| PCM | 48000 Hz | 2048 samples | ~42.7 ms |
| PCM | 16000 Hz | 1024 samples | 64 ms |
| AAC | any | 1024 samples | varies |

### AVChannelSetupRequest/Response Details

**AVChannelSetupRequest** (0x8000, Phone → HU):

| Field | Type | Description |
|-------|------|-------------|
| 1 | enum (MediaCodecType) | Codec the phone will use |

**AVChannelSetupResponse** (0x8003, HU → Phone):

| Field | Type | Description |
|-------|------|-------------|
| 1 | enum | Status: NONE=0, FAIL=1, OK=2 |
| 2 | uint32 | max_unacked — flow control buffer depth |
| 3 | repeated uint32 | configs — accepted configuration indices |

**AVChannelStartIndication** (0x8001, Phone → HU):

| Field | Type | Description |
|-------|------|-------------|
| 1 | int32 | session ID (monotonically incrementing) |
| 2 | uint32 | config — internal format index (1-4, not codec enum) |
| 3 | enum | Session type: UNKNOWN=0, NORMAL=1, ALTERNATE=2 |
| 4 | message | AVChannelMediaConfig (timing/ping parameters) |

### Microphone Input (HU → Phone)

For channel 6 (phone call), the HU sends mic audio TO the phone. Configured via `AVInputChannel` (`vyf`) in the SDP:

| Field | Type | Description |
|-------|------|-------------|
| 2 | enum (MediaCodecType) | Codec (default: PCM) |
| 3 | AudioConfig | Single config (not repeated) — sample rate, bit depth, channels |

### Ackless Audio (PDK 5.0+)

When `CarInfo.f20437e >= 5` (PDK version 5+), ackless mode is enabled — the phone streams audio without waiting for `AVMediaAckIndication` between frames. This reduces latency on modern head units. From `hrf.java:221`.

### Car-Specific Quirks

Certain vehicles have force-single-channel (mono) capturing enabled via a hardcoded list at `pli.java:91`. Known affected: KIA, HYUNDAI (daudio), Ford SYNC.

---

## Gotchas

> **Gotcha:** Focus messages go on **channel 0** (control), not on the audio channels themselves. Sending AudioFocusRequest on channel 4/5/6 will be ignored. The phone always sends focus requests on the control channel, and the HU must handle them there. The `channel_id` context for which audio channel is requesting focus comes from the session state, not from the message routing.

> **Gotcha:** Channels 4, 5, and 6 use **identical wire messages** from `oaa/audio/` and `oaa/av/`. The AudioType enum configured during service discovery determines each channel's role, not any field in the audio messages themselves. If you parse an AVChannelSetupRequest on channel 5, it looks exactly like one on channel 4 -- only the channel ID differs.

> **Gotcha:** AV channel setup (AVChannelSetupRequest/Response, AVChannelStartIndication) is a **prerequisite** for audio data flow. The phone will not send PCM data until the AV setup handshake completes on each channel. Audio focus must also be granted before the phone starts streaming. Both conditions must be met. See [04-channel-lifecycle.md](../interactions/04-channel-lifecycle.md) for the full setup sequence.

> **Gotcha:** Channel 6 (phone call audio) is **bidirectional** -- the HU must send microphone PCM data back to the phone for the caller to hear the driver. Channels 4 and 5 are phone-to-HU only.

> **Gotcha:** There is **no Opus codec** in Android Auto. Despite being common in other protocols, AA only supports PCM and AAC-LC. The HU cannot negotiate Opus.

> **Gotcha:** **PCM is mandatory.** If the HU doesn't set a codec or sends an unrecognized value, the phone falls back to PCM. Every HU must handle raw PCM audio at minimum.

> **Gotcha:** **AAC-LC vs AAC-LC-ADTS** are two distinct codec values (2 vs 4). The ADTS variant wraps each AAC frame in an ADTS header for easier framing. Choose one — don't mix them on the same channel.

> **Gotcha:** The `config` field in `AVChannelStartIndication` carries the **internal format index** (1=stereo 48k, 2=mono 16k, 3=mono 48k), NOT the MediaCodecType enum. Don't confuse the two.

> **Gotcha:** **Multiple AVChannelSetupResponse = error.** If the HU sends a second setup response on the same channel, the phone terminates with `MULTIPLE_DISPLAY_CONFIGS` error.

> **Gotcha:** **16-bit only.** The phone rejects any AudioConfig with bit_depth != 16. Do not advertise 24-bit or 32-bit audio.

---

## References

### Proto Files
- [AudioFocusRequestMessage.proto](../../oaa/audio/AudioFocusRequestMessage.proto)
- [AudioFocusResponseMessage.proto](../../oaa/audio/AudioFocusResponseMessage.proto)
- [AudioFocusStateMessage.proto](../../oaa/audio/AudioFocusStateMessage.proto) **(RETRACTED — tombstone only)**
- [AudioFocusTypeEnum.proto](../../oaa/audio/AudioFocusTypeEnum.proto)
- [AudioFocusStateEnum.proto](../../oaa/audio/AudioFocusStateEnum.proto)
- [AudioConfigData.proto](../../oaa/audio/AudioConfigData.proto)
- [AudioStreamTypeMessage.proto](../../oaa/audio/AudioStreamTypeMessage.proto) **(RETRACTED — tombstone only)**
- [AudioStreamTypeEnum.proto](../../oaa/audio/AudioStreamTypeEnum.proto) **(RETRACTED — tombstone only)**
- [AudioTypeEnum.proto](../../oaa/audio/AudioTypeEnum.proto)
- [AudioFocusChannelData.proto](../../oaa/audio/AudioFocusChannelData.proto)

### Shared AV Protos
- [AVChannelSetupRequestMessage.proto](../../oaa/av/AVChannelSetupRequestMessage.proto)
- [AVChannelSetupResponseMessage.proto](../../oaa/av/AVChannelSetupResponseMessage.proto)
- [AVChannelStartIndicationMessage.proto](../../oaa/av/AVChannelStartIndicationMessage.proto)
- [AVMediaAckIndicationMessage.proto](../../oaa/av/AVMediaAckIndicationMessage.proto)
- [AVChannelMessageIdsEnum.proto](../../oaa/av/AVChannelMessageIdsEnum.proto)

### Codec Negotiation Classes (16.2)
- `vxz.java` — MediaCodecType enum (PCM=1, AAC_LC=2, AAC_LC_ADTS=4)
- `vye.java` — AVChannel / ChannelDescriptor with audio_type and audio_configs
- `vyf.java` — AVInputChannel (mic input config)
- `vvb.java` — AudioConfig proto (sample_rate, bit_depth, channel_count)
- `hqh.java` — Audio format selection per channel type
- `hrf.java` — Audio format priority lists, ackless mode (PDK 5+)
- `hsk.java` — AAC encoder wrapper
- `hsz.java` — AAC codec detection helper
- `ibt.java` — Audio buffer sizing, channel type mapping
- `icv.java` — AVChannelSetup request/response handling
- `gnq.java` — Internal audio format enum (48k stereo, 16k mono, 48k mono)
- `nnv.java` — AudioStreamType diagnostics enum
- `pli.java` — Car-specific force-mono list (KIA, HYUNDAI, SYNC)
- `wbs.java` — AVChannelSetupRequest proto (single codec field)
- `vwn.java` — AVChannelSetupResponse proto (status, max_unacked, configs)

### Verification Report
- [Proto Verification: Audio Channel](../../analysis/reports/proto-verification/audio.md) — full verification trace with retractions

### Cross-References
- [Audio cross-version mapping](../cross-version/audio.md) -- APK class mappings across versions 15.9, 16.1, 16.2
- [Channel map](../channel-map.md) -- Channel ID reference for all AA channels
- [04-channel-lifecycle.md](../interactions/04-channel-lifecycle.md) -- AV setup flow, focus model overview, MVC checklist
- [01-confidence-tiers.md](../verification/01-confidence-tiers.md) -- Confidence tier definitions

> **Capture evidence boundary:** The VW capture cannot validate claims about this surface.
> The on-phone hook lives inside the AA framing layer; `channel_id`, `flags`, and outer
> frame header semantics are below the hook's observation point. See
> [06-capture-non-claim-boundary.md](../verification/06-capture-non-claim-boundary.md).
