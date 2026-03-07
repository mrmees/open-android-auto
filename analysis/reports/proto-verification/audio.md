# Audio Channel Verification Report

**Date:** 2026-03-06
**Wave:** 7
**Status:** COMPLETE

## Channels Covered

| Channel | GAL Tag | Handler Class | Service Type |
|---------|---------|---------------|-------------|
| Audio AV Output | CAR.GAL.MEDIA | qnf.java (extends qnp) | 3, 4, 5 |
| Mic Input | CAR.GAL.MIC | ict.java / ial.java (extends iav) | 6 |

## Audio AV Output (qnf.java)

### Finding: Shares exact AV protocol with video

`qnf.java` extends `qnp` (same base as video's `ied/icv`). Its `mo30512d()` handles:

| Dispatch | Wire ID | Proto Class | Message | Direction |
|----------|---------|-------------|---------|-----------|
| 0x8004 | 0x8003 | vwn | AVChannelSetupResponse | HU→Phone |
| 0x8005 | 0x8004 | vuw | AVMediaAckIndication | HU→Phone |
| 0x800C | 0x800B | — | Signal/heartbeat | HU→Phone |

On channel open (`mo30515v`), sends `wbs` (AVChannelSetupRequest) at wire ID 0x8000.

**All messages are the shared AV protocol — already verified Gold in Media AV Stream wave.**

No audio-specific wire messages exist beyond the shared AV set. The `vdp.m36513at()` +1 offset applies (same as video).

Service types for audio output (from `iav.mo20105j`):
- Type 3, 4 → AUDIO_GUIDANCE priority
- Type 5 → AUDIO_MEDIA priority
- Type 2 → VIDEO priority (for comparison)

### Verification: Gold (by inheritance)

No new protos needed — audio output channels use the exact same wire protocol as video.

## Mic Input Channel (ict.java / ial.java)

### Handler: ict.java (extends iav, service type 6)

Constructor: `super(6, hyjVar, iazVar, 4)` — service type 6, maxUnacked 4.

`ict.mo18864a()` handles incoming messages via `vdp.m36513at()` (+1 offset):

| Dispatch | Wire ID | Proto Class | Message | Direction |
|----------|---------|-------------|---------|-----------|
| 1 | 0x0000 | — | Raw audio data (8-byte timestamp + PCM) | HU→Phone |
| 0x8007 | 0x8006 | vyj | MicrophoneOpenResponse | HU→Phone |

Outbound: raw audio sent via `iav.m20112q()` at msg type 0x0001 (Phone→HU).

### MicrophoneOpenResponse (vyj, 0x8006) — NEW

| Field | Type | Modifier | Description |
|-------|------|----------|-------------|
| 1 | int32 | required | status (0 = success, non-zero = error) |
| 2 | int32 | optional | session config (stored in ict.f36646d) |

Evidence from `ial.mo20071h(vyj)`:
- `vyjVar.f74462c != 0` → error path, logs "onMicrophoneStateChange not ok" and "onOpenMicError()"
- `vyjVar.f74463d` → stored as session config when field 2 present

Proto syntax: proto2 (byte 0 of RawMessageInfo = 1, via `f74464f = 2` init).

### Verification: Gold

## Audio SDP Data Structures

### AudioConfig (vvb in 16.2)

| Field | Type | Modifier | Match |
|-------|------|----------|-------|
| 1 | uint32 | optional | sample_rate — correct |
| 2 | uint32 | optional | bit_depth — correct |
| 3 | uint32 | optional | channel_count — correct |

16.2 class: vvb (was vvp in 16.1). Structure unchanged. **Silver — matches.**

### AudioFocusChannel (vxc in 16.2)

Empty message (presence marker in ChannelDescriptor). 16.2 class: vxc (was vxq in 16.1). **Bronze — matches.**

### AudioType Enum (unverified)

Used in AVChannelData.proto field 2 (`audio_type`). SDP-level only — not a wire message. Values (SPEECH=1, SYSTEM=2, MEDIA=3, ALARM=4) are inferred from Android AudioAttributes. No APK enum class found to verify exact values.

**Stays at unverified confidence.** Will be verified when AVChannel SDP data is traced.

## Retractions

### AudioFocusStateMessage — RETRACT (duplicate of RadioFavoriteToggleRequest)

The message at 0x8021 with `bool has_focus` is actually **RadioFavoriteToggleRequest** on the radio channel (service 15, CAR.GAL.RADIO-EP). Evidence:

- `hlr.java` (radio service, CAR.RADIO) line 410: `ibfVar.m20106k(32801, waq)` — sends waq at 0x8021
- `ibf.java` (radio endpoint) service type 15
- waq has 1 field: bool (f74830c)
- The `hlr.mo18792l(boolean z)` method is on the `psn` radio manager interface
- The bool represents "is favorite" (toggle favorite), NOT "has audio focus"
- Structurally identical (1 bool field) but semantically different from audio focus

The msg ID 0x8021 does NOT appear on any audio channel — only on radio (service 15).

### AudioStreamTypeMessage — RETRACT (duplicate of RadioTuneDirectionRequest)

The message at 0x8022 with `enum stream_type` is actually **RadioTuneDirectionRequest** on the radio channel. Evidence:

- `hlr.java` line 437: `ibfVar.m20106k(32802, war)` — sends war at 0x8022
- war has 1 field: enum (f74834c), validated by vuz (ResizeActionType values? No — validated by vym case 16 → vdp.m36491X)
- The `hlr.mo18793n(int i)` method is on the `psn` radio manager interface
- Values 1, 2 represent tune UP/DOWN, NOT media/guidance stream type
- The existing RadioMessages.proto already has this as RadioTuneDirectionRequest

### AudioStreamTypeEnum — RETRACT (duplicate of RadioTuneDirection)

The enum with values MEDIA=1, GUIDANCE=2 was incorrectly named. On the radio channel, values 1, 2 mean UP/DOWN (RadioTuneDirection). Same integer values, different semantics.

## Radio Channel Discoveries (bonus)

While tracing audio messages, the complete radio channel (service 15) was mapped from 16.2 APK:

### ibf.java (Radio Endpoint, CAR.GAL.RADIO-EP)

NOTE: ibf extends iav directly — NO `vdp.m36513at()` offset. Wire IDs = switch case values.

**Received (HU→Phone) — ibf.mo18864a switch:**

| Wire ID | Proto (16.2) | Proto (16.1) | Message |
|---------|-------------|-------------|---------|
| 0x801A | wam | wau | RadioProgramListNotification |
| 0x801B | wal | wat | RadioProgramInfoNotification |
| 0x801D | wah | wap | RadioMuteResponse |
| 0x801F | wau | wbd | RadioTuneResponse |
| 0x8020 | wad | wal | RadioFavoriteListNotification |

**Sent (Phone→HU) — hlr.java sends via ibf.m20106k:**

| Wire ID | Proto (16.2) | Proto (16.1) | Message |
|---------|-------------|-------------|---------|
| 0x801C | wag | wao | RadioMuteRequest |
| 0x801E | wat | wbc | RadioTuneRequest |
| 0x8021 | waq | waz | RadioFavoriteToggleRequest |
| 0x8022 | war | wba | RadioTuneDirectionRequest |
| 0x8023 | wac | — | RadioSearchRequest (NEW in 16.2) |

### Direction Corrections in RadioMessages.proto

The existing proto header has ALL directions SWAPPED:
- Notifications were listed as "Phone→HU" but are actually "HU→Phone" (received by ibf)
- Requests were listed as "HU→Phone" but are actually "Phone→HU" (sent by hlr)

### RadioSearchRequest (0x8023) — NEW

| Field | Type | Modifier |
|-------|------|----------|
| 1 | string | optional |

Sent by `hlr.mo18789i(String str)` at wire ID 32803 = 0x8023. Direction: Phone→HU.

### Obfuscated Class Name Shuffle

Massive name collision between 16.1 and 16.2. Examples:
- `wal` in 16.1 = RadioFavoriteListNotification; in 16.2 = RadioProgramInfoNotification
- `wau` in 16.1 = RadioProgramListNotification; in 16.2 = RadioTuneResponse
- `war` in 16.1 = RadioProgramIdentifier; in 16.2 = RadioTuneDirectionRequest (wire msg)

## AdditionalVideoConfig Field 6 — RESOLVED

Deferred from video channel verification. The ResizeActionType enum (field 1 of VideoResizeAction, which is field 6 of AdditionalVideoConfig):

- 16.2 class: vux (VideoResizeAction), vuz (ResizeActionType enum)
- Values: ACTION_UNKNOWN(0), ACTION_RESIZE_TO_SMALLER(1), ACTION_RESIZE_TO_LARGER(2)
- **Identical to existing proto.** Only the obfuscated validator class name changed (vvn→vve/vuz).
- No proto changes needed.

## Summary

| Action | Count |
|--------|-------|
| Gold (verified) | 1 new (MicrophoneOpenResponse) |
| Gold (inherited) | Audio AV output (shares verified AV protocol) |
| Retracted | 3 (AudioFocusStateMessage, AudioStreamTypeMessage, AudioStreamTypeEnum) |
| SDP confirmed | 2 (AudioConfig, AudioFocusChannel) |
| Radio directions fixed | 10 messages (all swapped) |
| New radio msg | 1 (RadioSearchRequest 0x8023) |
| Deferred resolved | 1 (AdditionalVideoConfig field 6) |
