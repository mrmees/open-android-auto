# Media Channel Verification Report

**Date:** 2026-07-25
**APK baseline:** Android Auto 16.2.660604-release
**Publication supplement:** Android Auto 17.3.662804-release
**Status:** COMPLETE — 17.3 services synchronized; historical findings retained

## Accepted Android Auto 17.3 service evidence

### CarLocalMedia — service type 20

Direct phone endpoint evidence establishes this bounded static flow:

| Raw ID | Payload | Direction | Phone endpoint action |
|---:|---|---|---|
| 0x8001 | CarLocalMediaPlaybackStatus | HU -> Phone | parse/cache/callback path |
| 0x8002 | CarLocalMediaPlaybackMetadata | HU -> Phone | parse/cache/callback path |
| 0x8003 | CarLocalMediaPlaybackRequest | Phone -> HU | build/send; inbound copy rejected |

The synchronized audit is
`oaa/media/CarLocalMediaPlaybackStatusMessage.audit.yaml`. Numeric playback
state 5 remains unknown and deferred; BufferedMedia's enum is not transferable
evidence. This static flow does not establish an acknowledgement, runtime
service activation, framed traffic, or callback delivery.

### BufferedMedia — service type 21

Android Auto 17.3 incoming raw ID 4 is HU -> Phone: `jaz` parses and consumes
the six-field `BufferedMediaSinkMessage` (`session_id`, `uid`, current position,
state, buffered position, and content duration). State values are exactly
UNKNOWN=0, PLAYING=1, PAUSED=2, STOPPED=3, BUFFERING=4. IDs 1-3 are unknown,
and every outbound path is unknown.

The parser does not establish a response or completed transfer and is runtime-unverified.
It also proves no downstream media operation or production endpoint execution.
URL, request/response, lifecycle, transport/data-plane, and
session semantics beyond the six consumed fields remain unpublished.

## Historical Android Auto 16.2 verification

## Critical Discovery: Two Separate Channels

Our documentation conflated two distinct channels under "media":

### Channel A: `CAR.GAL.MEDIA` — AV Audio Stream Endpoint

**Handler class:** `qnf.java`
**Internal name:** `"AudioEndPoint"` (line 76)
**Purpose:** Audio/video media stream flow control — setup, config, ACKs. This is the AV pipe, not the status/metadata channel.

| Msg ID | Hex | Direction | Proto Class | Description |
|--------|-----|-----------|-------------|-------------|
| 32768 | 0x8000 | Phone -> HU | `wbs` | AV setup request |
| 32772 | 0x8004 | HU -> Phone | `vwn` | Config/setup response |
| 32773 | 0x8005 | HU -> Phone | `vuw` | ACK (session ID + frame count) |
| 32780 | 0x800C | HU -> Phone | (none) | Signal — calls `qnk.mo29257h()` |

**Default handler (line 231-234):** Logs `"Received message with invalid type header: %d ch:%d"` for any other msg ID.

### Channel B: `CAR.GAL.INST` — Media Info / Instrument Cluster

**Handler class:** `iai.java` (channel endpoint), `hvx.java` (service implementation)
**GAL type:** 11 (from `iai` constructor: `super(11, ...)`)
**AIDL interface:** `com.google.android.gms.car.ICarMediaPlaybackStatus`

| Msg ID | Hex | Direction | Proto Class | Description |
|--------|-----|-----------|-------------|-------------|
| 32769 | 0x8001 | Phone -> HU | `vyc` | MediaPlaybackStatus |
| 32770 | 0x8002 | HU -> Phone | `vxo` | MediaPlaybackStatusEvent (input action) |
| 32771 | 0x8003 | Phone -> HU | `vyb` | MediaPlaybackMetadata |

**Callback interface:** `com.google.android.gms.car.ICarMediaPlaybackStatusEventListener` — receives 0x8002 events.

## Verification Results

### MediaPlaybackStatus (0x8001, `vyc`) — PASS with notes

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | `vyc` created in `hvx.mo19832g()`, sent via `iai.m20106k()` on GAL type 11 |
| Message ID | PASS | `iai.f36385a = 32769` (0x8001) |
| Direction | PASS | Phone -> HU (serialized and sent by phone) |
| Field schema | PASS | 6 fields: enum, string, uint32, bool, bool, bool — matches our proto |
| Cross-references | PASS | Only referenced from `hvx.java` (CAR.INST) |
| Enum values | NOTE | Enum verifier index 20 (`vve.f73612u`). Default value = 1 (STOPPED). Values 0-4 match our definition. |

**Notes:**
- Proxy `pre.java` hardcodes repeat (field 5) and repeat_one (field 6) to false. The fields exist but are not populated by current GMS client.
- Our proto correctly uses proto2 syntax.

**Confidence: GOLD**

### MediaPlaybackMetadata (0x8003, `vyb`) — FAIL (3 errors)

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | `vyb` created in `hvx.mo19831f()`, sent via `iai.m20106k()` on GAL type 11 |
| Message ID | PASS | `iai.f36386b = 32771` (0x8003) |
| Direction | PASS | Phone -> HU (serialized and sent by phone) |
| Field schema | **FAIL** | 3 field type errors — see below |
| Cross-references | PASS | Only referenced from `hvx.java` (CAR.INST) |
| Enum values | N/A | No enums in this message |

**Field errors:**

| Field | Our Proto | Actual (DB + AIDL confirmed) | Error |
|-------|-----------|------------------------------|-------|
| 5 | `bool is_playing` | `string` (AIDL param `str4`, always null from proxy) | Wrong type AND wrong name |
| 6 | `string album_art_url` | `uint32` (AIDL param `int i`) | Wrong type AND wrong name |
| 7 | (missing) | `int32` (AIDL param `int i2`, always 0 from proxy) | Missing field |

**Additional error:** Our proto uses `proto3` syntax but the APK uses `proto2`.

**Proxy behavior (pre.java):** Field 5 is always written as null, field 7 is always written as 0. These fields are defined but not actively populated.

**Confidence: Must fix before promoting to GOLD**

### MediaPlaybackStatusEvent (0x8002, `vxo`) — NEW DISCOVERY

This message was **not in our proto definitions at all**. The 0x8002 retraction was based on checking the wrong handler class (`qnf.java` / `CAR.GAL.MEDIA`), which indeed has no 0x8002. But `iai.java` / `CAR.GAL.INST` does handle 0x8002.

| Field | Type | Modifier | Notes |
|-------|------|----------|-------|
| 1 | enum | required | Enum verifier index 17 (`vve.f73609r`). Dispatched via ICarMediaPlaybackStatusEventListener.onInput(value-1) |

**Direction:** HU -> Phone (deserialized and dispatched to listener)
**AIDL callback:** `prj.mo29613e(int)` = `ICarMediaPlaybackStatusEventListener`

This is an **input action** message — the HU sends it to tell the phone about a media-related event on the instrument cluster. The enum values need further investigation.

**Note on vuy retraction:** The retraction of `vuy` as MediaPlaybackCommand was **correct** — `vuy` really is ActionTakenNotification on the video channel. But the conclusion that "0x8002 on the media channel doesn't exist" was **wrong** — it exists on `CAR.GAL.INST`, just with a different proto class (`vxo`).

## Errors in Previous Documentation

1. **qnf.java is NOT the media status handler** — it's the AV audio stream endpoint (`CAR.GAL.MEDIA`). Media status lives on `CAR.GAL.INST` via `iai.java`/`hvx.java`.
2. **0x800D was never in qnf.java** — the actual msg ID is 0x800C (32780). Previous memory notes had wrong hex conversion or confused channels.
3. **MediaPlaybackMetadata has wrong field types** for fields 5-7.
4. **MediaPlaybackMetadata uses wrong proto syntax** (proto3 should be proto2).
5. **0x8002 on the media-info channel exists** — it's `vxo` (MediaPlaybackStatusEvent), a new proto we need to add.

## Action Items

- [ ] Fix MediaPlaybackMetadata proto (fields 5-7, syntax)
- [ ] Add MediaPlaybackStatusEvent proto (0x8002, `vxo`)
- [ ] Update media.md channel docs to distinguish CAR.GAL.MEDIA (AV stream) from CAR.GAL.INST (media info)
- [ ] Correct retraction note — 0x8002 exists, just not as vuy/MediaPlaybackCommand
- [ ] Update audit.yaml files
- [ ] Investigate vxo enum values (what actions does the HU send?)
