# Proto Verification Progress

**Design:** `docs/plans/2026-03-06-proto-verification-design.md`
**Started:** 2026-03-06
**Last updated:** 2026-03-06

## Summary

| Status | Count |
|--------|-------|
| Verified (Gold) | 11 |
| Schema Errors Found & Fixed | 5 |
| New Protos Discovered | 1 (MediaPlaybackStatusEvent) |
| Retracted / Removed | 4 (MediaStatusList, MediaTrackIdentifier, MediaEventIdWrapper, CarLocalMediaPlaybackEnum) |
| Pending | all remaining channels |

## Channel Verification Status

### Phase 1 — Priority Wire Channels

| # | Channel | GAL Tag | Handler Class | Status | Report | Notes |
|---|---------|---------|---------------|--------|--------|-------|
| 1a | Media Info | CAR.GAL.INST | iai/hvx | **COMPLETE** | [media.md](media.md) | 3 Gold msgs, 1 retraction (MediaEventIdWrapper) |
| 1b | Media AV Stream | CAR.GAL.MEDIA | qnf/icv | **COMPLETE** | [media.md](media.md) | 3 Gold msgs (wbs/vwn/vuw), msg IDs corrected |
| 1c | Car Local Media | CAR.GAL.CAR_LOCAL_MEDIA | hyh (16.2) | **COMPLETE** | [media.md](media.md) | 3 Gold msgs, direction corrected, own PlaybackState enum |
| 2 | Navigation | TBD | TBD | PENDING | | Next up |
| 3 | Control (ch 0) | CAR.GAL.SERVICE | TBD | PENDING | | Session lifecycle |
| 4 | Input | CAR.GAL.INPUT | TBD | PENDING | | Touch/button |
| 5 | Phone | TBD | TBD | PENDING | | Phone status |
| 6 | Video | CAR.GAL.VIDEO | TBD | PENDING | | Video sink |
| 7 | Audio (media) | CAR.GAL.AUDIO | TBD | PENDING | | Multiple audio channels |
| 8 | Audio (mic) | CAR.GAL.MIC | TBD | PENDING | | AV input |
| 9 | Sensor | CAR.GAL.SENSOR | TBD | PENDING | | Sensor data |
| 10 | Bluetooth | CAR.GAL.BT / CAR.BT | TBD | PENDING | | BT pairing |

### Phase 1 — Secondary Channels

| # | Channel | GAL Tag | Handler Class | Status | Report | Notes |
|---|---------|---------|---------------|--------|--------|-------|
| 11 | Radio | CAR.RADIO | TBD | PENDING | | Service 15 |
| 12 | Car Control | CAR.GAL.CAR_CONTROL | TBD | PENDING | | HVAC, doors |
| 13 | WiFi Projection | CAR.GAL.WIFI_PROJ | TBD | PENDING | | WiFi upgrade |
| 14 | Vendor Extension | CAR.VENDOR | TBD | PENDING | | Vendor passthrough |
| 15 | Diagnostics | CAR.GAL.DIAGNOSTICS | TBD | PENDING | | |

## Resume Pointer

**Next action:** Begin navigation channel (#2) verification.

## Completed — Media Channel (Wave 1)

### CAR.GAL.INST (Media Info, GAL type 11)

| Proto | Msg ID | Direction | 16.2 Class | Confidence | Result |
|-------|--------|-----------|------------|------------|--------|
| MediaPlaybackStatus | 0x8001 | Phone->HU | vyc | Gold | Correct |
| MediaPlaybackStatusEvent | 0x8002 | HU->Phone | vxo | Gold | NEW — discovered during verification |
| MediaPlaybackMetadata | 0x8003 | Phone->HU | vyb | Gold | Fixed 3 field errors, syntax proto3->proto2 |
| MediaEventIdWrapper | — | — | xme | Retracted | Not wire protocol — internal MediaBrowserService |

### CAR.GAL.MEDIA (AV Stream, all AV channels)

| Proto | Wire ID | Direction | 16.2 Class | Confidence | Result |
|-------|---------|-----------|------------|------------|--------|
| AVChannelSetupRequest | 0x8000 | Phone->HU | wbs | Gold | Fixed optional->required, renamed field |
| AVChannelStartIndication | 0x8001 | Bidirectional | wbu | Gold | Fixed optional->required (fields 1,2) |
| AVChannelStopIndication | 0x8002 | Phone->HU | wbv | Gold | Confirmed empty, fixed syntax proto3->proto2 |
| AVChannelSetupResponse | 0x8003 | Bidirectional | vwn | Gold | Fixed optional->required, corrected msg ID |
| AVMediaAckIndication | 0x8004 | HU->Phone | vuw | Gold | Fixed optional->required, renamed fields |
| Signal/heartbeat | 0x800B | HU->Phone | — | — | No proto (raw signal) |

**CRITICAL FIX:** All AV msg IDs were off by one due to `vdp.m36513at()` adding +1 for internal dispatch. Previous docs had 0x8004/0x8005/0x800C, corrected to 0x8003/0x8004/0x800B.

### CAR_LOCAL_MEDIA (GAL type 20)

| Proto | Msg ID | Direction | 16.2 Class | Confidence | Result |
|-------|--------|-----------|------------|------------|--------|
| CarLocalMediaPlaybackStatus | 0x8001 | HU->Phone | vwe | Gold | Fixed direction, fixed PlaybackState enum |
| CarLocalMediaPlaybackMetadata | 0x8002 | HU->Phone | vwc | Gold | Fixed direction, updated class refs |
| CarLocalMediaPlaybackRequest | 0x8003 | Phone->HU | vwd | Gold | Updated class refs |
| CarLocalMediaPlaybackEnum | — | — | vwb | Superseded | Redundant with enum in status proto |

**CRITICAL FIX:** Direction reversed — status/metadata are HU->Phone (car tells phone what local media is playing), not Phone->HU. CarLocal PlaybackState is its own enum (values 1-5), NOT shared with MediaPlaybackStatus (values 0-4).

### Retracted Protos

| Proto | Reason | Actually Is |
|-------|--------|-------------|
| MediaStatusList (vyd) | Wrong class mapping | 16.1: IntegratedOverlayParametersNotification (video 0x800D). 16.2: MediaInfoChannel (ChannelDescriptor field 9) |
| MediaTrackIdentifier (xma/xll) | Not wire protocol | Internal MediaBrowserService queue structure (oui -> xlm -> xll) |
| MediaEventIdWrapper (xme) | Not wire protocol | Internal MediaBrowserService structure, never in any GAL handler |
| CarLocalMediaPlaybackEnum | Redundant | Superseded by enum in CarLocalMediaPlaybackStatusMessage.proto |

### Other Fixes

| Item | Change |
|------|--------|
| MediaInfoChannel | Syntax proto3->proto2, added class mapping (16.1:vyr, 16.2:vyd) |
| AVChannelSetupStatus enum | Upgraded to Gold, noted value 0 invalid |
| AVChannelMessageIds enum | Confirmed correct (already had right wire values) |
| BufferedMediaSinkMessage | No change — documented stub, no wire messages |

## Running Discoveries

1. **AV msg ID off-by-one:** `vdp.m36513at()` adds +1 for internal dispatch. Wire values are 1 less than what the handler switch cases show. BUT this does NOT apply to CAR_LOCAL_MEDIA — `iav.mo20009T()` reads wire IDs directly.

2. **CAR.GAL.MEDIA vs CAR.GAL.INST confusion:** `CAR.GAL.MEDIA` (qnf) is the AV audio stream endpoint. Media status/metadata lives on `CAR.GAL.INST` (iai/hvx, GAL type 11).

3. **0x8002 exists on INST channel:** MediaPlaybackStatusEvent (vxo), HU->Phone input action.

4. **AV channels share msg ID patterns:** qnf (audio) and icv/ied (video) use the same message IDs and proto classes. vwn/vuw are shared across all AV channels.

5. **GMS proxy strips fields:** `pre.java` hardcodes metadata field 5=null, field 7=0, status repeat/repeat_one=false.

6. **Obfuscated name reuse across versions:** Same class name (e.g., vyd, xma, vwq) can refer to completely different protos in different APK versions. Always verify by structure AND handler context, not just name.

7. **CarLocal direction is reversed:** Status/metadata are HU->Phone (car reports local media), request is Phone->HU. The +1 msg ID offset does NOT apply to this channel.
