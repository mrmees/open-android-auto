# Proto Verification Progress

**Design:** `docs/plans/2026-03-06-proto-verification-design.md`
**Started:** 2026-03-06
**Last updated:** 2026-03-06

## Summary

| Status | Count |
|--------|-------|
| Verified (Gold) | 1 (MediaPlaybackStatus) |
| Schema Errors Found | 1 (MediaPlaybackMetadata — 3 field errors) |
| New Protos Discovered | 1 (MediaPlaybackStatusEvent — 0x8002 on INST) |
| Retraction Corrected | 1 (0x8002 exists, just not as vuy) |
| Pending | all remaining channels |

## Channel Verification Status

### Phase 1 — Priority Wire Channels

| # | Channel | GAL Tag | Handler Class | Status | Report | Notes |
|---|---------|---------|---------------|--------|--------|-------|
| 1a | Media Info | CAR.GAL.INST | iai/hvx | **PARTIAL** | [media.md](media.md) | Core msgs verified; supporting + CarLocal remaining |
| 1b | Media AV Stream | CAR.GAL.MEDIA | qnf | **PARTIAL** | [media.md](media.md) | Handler msg IDs mapped; AV protos (wbs/vwn/vuw) not schema-checked |
| 2 | Navigation | TBD | TBD | PENDING | | NavigationDistance reclassified |
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
| 14 | Car Local Media | CAR.GAL.CAR_LOCAL_MEDIA | TBD | PENDING | | FM/USB/CD |
| 15 | Vendor Extension | CAR.VENDOR | TBD | PENDING | | Vendor passthrough |
| 16 | Diagnostics | CAR.GAL.DIAGNOSTICS | TBD | PENDING | | |

## Resume Pointer

**Next action:** Finish media channel — verify remaining protos listed below, THEN proceed to navigation (#2).

### Media channel — remaining protos to verify

| Proto | Current Tier | Channel | Notes |
|-------|-------------|---------|-------|
| MediaEventIdWrapper | Silver | INST (type 11) | Sub-message at field 13, placeholder internals |
| MediaEventId | Silver | INST (type 11) | Sub-message of MediaEventIdWrapper |
| MediaStatusList | Silver | INST (type 11) | Repeated list structure |
| MediaTrackIdentifier | Silver | INST (type 11) | 3 message-type sub-fields |
| MediaInfoChannel | Unverified | SDP data | Service discovery marker |
| wbs (AV setup request) | Unverified | MEDIA (AV) | 0x8000 outbound — need schema check |
| vwn (AV config response) | Unverified | MEDIA (AV) | 0x8004 inbound — need schema check |
| vuw (AV ACK) | Unverified | MEDIA (AV) | 0x8005 inbound — need schema check |
| CarLocalMediaPlaybackStatus | Silver | CAR_LOCAL_MEDIA (type 20) | Need handler trace |
| CarLocalMediaPlaybackMetadata | Silver | CAR_LOCAL_MEDIA (type 20) | Need handler trace |
| CarLocalMediaPlaybackRequest | Silver | CAR_LOCAL_MEDIA (type 20) | Need handler trace |
| CarLocalMediaPlaybackEnum | Bronze | CAR_LOCAL_MEDIA (type 20) | Enum values |
| BufferedMediaSinkMessage | Unverified | type 21 | Stub channel |

## Running Discoveries

1. **CAR.GAL.MEDIA vs CAR.GAL.INST confusion:** `CAR.GAL.MEDIA` (qnf) is the AV audio stream endpoint. Media status/metadata lives on `CAR.GAL.INST` (iai/hvx, GAL type 11). Our docs conflated these.

2. **0x800C not 0x800D:** qnf.java handles 0x800C (32780), not 0x800D as previously documented. The memory notes were wrong.

3. **0x8002 exists on INST channel:** The MediaPlaybackCommand retraction was correct about `vuy` being misidentified, but incorrect about 0x8002 not existing. Proto class `vxo` handles it as `MediaPlaybackStatusEvent` (HU -> Phone input action).

4. **AV channels share msg ID patterns:** qnf (audio) uses 0x8000/0x8004/0x8005/0x800C — same pattern likely applies to video sink. Need to verify when we reach video channel.

5. **GMS proxy strips fields:** `pre.java` hardcodes metadata field 5 = null, field 7 = 0, status repeat/repeat_one = false. Fields exist in proto but are not populated by current API client.
