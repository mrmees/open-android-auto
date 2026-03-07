# Frida Capture Spec for AA Proto Validation

**Context:** We have 234 verified proto definitions and a validator pipeline on claude-dev. We need phone-side captures to validate field schemas and discover unknown message types. The phone is rooted (Samsung S25 Ultra, Android 16). Target app is Google Android Auto (com.google.android.projection.gearhead).

## What to capture per message

| Field | Type | Description |
|-------|------|-------------|
| `ts_ms` | int | Timestamp in milliseconds |
| `direction` | string | `send` or `receive` |
| `java_class` | string | Full class name, e.g. `p000.vzb` — maps to jadx decompilation |
| `msg_id` | int | The message ID (e.g. 0x8001 = 32769) from GAL dispatch, if available |
| `service_type` | int | GAL service number (see table below), if available |
| `channel_id` | int | Runtime channel number, if available |
| `proto_hex` | string | Raw serialized protobuf bytes, hex-encoded |
| `to_string` | string | Java `.toString()` output — reveals field names from obfuscated code |

`msg_id`, `service_type`, and `channel_id` are nice-to-have. The critical fields are `java_class`, `proto_hex`, `to_string`, and `direction`.

## GAL service types (for reference)

| Service | Number | Description |
|---------|--------|-------------|
| Sensor | 1 | Sensor data (night mode, GPS, speed, etc.) |
| Media AV | 3 | Audio/video streaming |
| Input | 4 | Touch, buttons, rotary |
| WiFi Projection | 17 | WiFi credential exchange |
| Bluetooth | 9 | Pairing |
| Navigation | 10 | Nav state, turn events, distance |
| Media Info | 11 | Playback status, metadata |
| Phone | 13 | Call state |
| Radio | 15 | AM/FM/DAB radio |
| Car Control | 19 | HVAC, doors, mirrors |

## Where to hook

### Primary: Protobuf serialization layer

This is the best approach — stable API, catches ALL protos including ones we don't know about.

**Outgoing (phone → HU):**
- `com.google.protobuf.AbstractMessageLite.toByteArray()`
- OR `com.google.protobuf.AbstractMessageLite.writeTo(CodedOutputStream)`
- Capture: `this.getClass().getName()`, return value (the bytes), `this.toString()`

**Incoming (HU → phone):**
- `com.google.protobuf.AbstractParser.parseFrom(byte[])`
- OR `com.google.protobuf.GeneratedMessageLite.mergeFrom()`
- Capture: return value's `.getClass().getName()`, the input bytes, return value's `.toString()`

These hooks catch every protobuf serialized/deserialized by the AA app. Unknown message types show up automatically.

**Warning:** These are high-volume hooks. The AA app serializes a LOT of protos (including internal non-wire protos). Consider filtering by package prefix — all AA wire protos are in obfuscated classes under `p000.*` (in APK 16.2). You may also want to debounce or sample to avoid performance issues.

### Secondary: GAL message dispatch

From jadx analysis of AA 16.2 (obfuscated names):

- **`ian.m20106k(int msgId, MessageLite proto)`** — message send/register. Hooking on entry gives `(msg_id, proto.getClass(), proto.toString())` for every message sent on a GAL channel.
- **`iat`** subclass handlers — each channel's `onMessage` switch statement. The dispatch table maps msg_id → handler method.
- **`iav`** — AV channel base handler.

This gives msg_id and channel binding context that the protobuf-layer hook doesn't.

### Tertiary: TLS layer (least useful from phone)

We already have this from the DHU side. Phone-side TLS capture would be redundant unless you need to correlate timestamps.

## Output format

One JSONL line per message:

```json
{"ts_ms": 1709831234567, "direction": "send", "java_class": "p000.vzb", "msg_id": 32771, "service_type": 10, "channel_id": 12, "proto_hex": "0801", "to_string": "navigation_state: ACTIVE"}
```

## What we're trying to validate/discover

| Gap | What to look for | Obfuscated class (16.2) |
|-----|-----------------|------------------------|
| InputEventIndication field 2 | Touch/key event data — field 2 is empty in wire captures, may be a display channel ID or input event union | `p000.vxs` |
| MediaPlaybackMetadata schema | Verification found 3 field errors — need `.toString()` to confirm correct field layout | `p000.vyb` |
| Car Control properties | HVAC, door locks, mirrors — needs vehicle or VHAL emulator | `p000.hyc` handler |
| Radio messages | Station lists, seek, tune — needs radio source | `p000.ibf` handler |
| Unknown message types | Any proto class we haven't mapped yet | Anything new under `p000.*` |
| SensorEventIndication data | Always decodes as `{}` in wire captures — might be populated differently from phone side | `p000.wae` |

## Important notes

- **APK version matters.** Obfuscated class names change between versions. Our analysis is against 16.2.660604-release. Check `adb shell dumpsys package com.google.android.projection.gearhead | grep versionName`.
- **`toString()` is the prize.** It reveals field names from the obfuscated source that we can't see on the wire. A single `.toString()` dump of an unknown proto is worth more than 100 wire captures of it.
- **Filter aggressively.** The AA app uses protobufs internally for config, IPC, etc. We only care about wire protocol messages. If you can hook at the GAL dispatch layer (`ian.m20106k`) instead of the raw protobuf layer, the signal-to-noise ratio is much better.
- **Session scenarios to exercise:** Idle, music playback, navigation, phone call (if possible). Each exercises different channels and message types.
