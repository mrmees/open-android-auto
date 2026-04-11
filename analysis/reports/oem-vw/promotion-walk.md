# Phase 10 Promotion Walk Report

**Walker run date:** 2026-04-11
**Capture:** captures/oem-vw-mib3oi-2026-04-06
**Capture sha256:** `b66645c9a8a55eb466e9edf00715441af1a135edc1de057756b01882d0130408`

## Summary

- **Gold-counts delta (in scope):** Gold 6 → 6; Platinum 3 → 3 (+0 promoted)
- **Total verdicts:** 36
- **Platinum promotions:** 0
- **oem_match_pending_gold flags:** 21
- **Skipped sidecars:** 15

**Single-OEM trap reminder:** All promotions in this walk cite single-OEM VW MIB3 OI 2024 evidence. Every Platinum badge renders as `Platinum / single-OEM` per TIER-02. Multi-OEM corroboration is a v2 problem.

## Platinum promotions

_No promotions in this walk._

## oem_match_pending_gold (Silver + Bronze flagged)

See the companion worklist at `oem-match-pending-gold-worklist.md` for the full deep-trace guidance.

| Sidecar | Tier | Rules |
|---------|------|-------|
| `oaa/audio/AudioConfigData.audit.yaml` | silver | MATCH-08 |
| `oaa/audio/AudioFocusChannelData.audit.yaml` | bronze | MATCH-08 |
| `oaa/audio/AudioFocusRequestMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/audio/AudioFocusResponseMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/audio/AudioFocusStateMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/audio/AudioStreamTypeEnum.audit.yaml` | bronze | MATCH-08 |
| `oaa/audio/AudioStreamTypeMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/av/AVChannelData.audit.yaml` | silver | MATCH-08 |
| `oaa/av/AVChannelMediaConfigMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/av/AVChannelMediaStatsMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/av/AVChannelSetupRequestMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/av/AVChannelSetupResponseMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/av/AVChannelStartIndicationMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/av/AVInputChannelData.audit.yaml` | silver | MATCH-08 |
| `oaa/av/AVInputOpenRequestMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/av/AVInputOpenResponseMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/av/AVMediaAckIndicationMessage.audit.yaml` | silver | MATCH-08 |
| `oaa/av/UiConfigMessages.audit.yaml` | silver | MATCH-08 |
| `oaa/video/AdditionalVideoConfigData.audit.yaml` | silver | MATCH-08 |
| `oaa/video/VideoConfigData.audit.yaml` | silver | MATCH-08 |
| `oaa/video/VideoMarginsData.audit.yaml` | silver | MATCH-08 |

## Explicitly unmatched (Silver in observed service, not seen)

_No explicitly unmatched entries in this walk._

## Retraction review queue

_No contradictions surfaced in this walk._

## Skipped sidecars

| Sidecar | Verdict | Reason |
|---------|---------|--------|
| `oaa/media/CarLocalMediaPlaybackEnum.audit.yaml` | skip_superseded | confidence: superseded |
| `oaa/media/CarLocalMediaPlaybackMetadataMessage.audit.yaml` | skip_out_of_sdp_scope | channel_kind_not_in_vw_sdp: car_local_media_channel |
| `oaa/media/CarLocalMediaPlaybackRequestMessage.audit.yaml` | skip_out_of_sdp_scope | channel_kind_not_in_vw_sdp: car_local_media_channel |
| `oaa/media/CarLocalMediaPlaybackStatusMessage.audit.yaml` | skip_out_of_sdp_scope | channel_kind_not_in_vw_sdp: car_local_media_channel |
| `oaa/media/MediaPlaybackCommandMessage.audit.yaml` | skip_retracted | confidence: retracted |
| `oaa/media/MediaPlaybackMetadataMessage.audit.yaml` | skip_already_platinum | already_platinum |
| `oaa/media/MediaPlaybackStatusEventMessage.audit.yaml` | skip_schema_invalid | pre_existing_invalid: Additional properties are not allowed ('notes' was unexpected) |
| `oaa/media/MediaPlaybackStatusMessage.audit.yaml` | skip_already_platinum | already_platinum |
| `oaa/media/MediaStatusListData.audit.yaml` | skip_retracted | confidence: retracted |
| `oaa/media/MediaTrackIdentifierData.audit.yaml` | skip_retracted | confidence: retracted |
| `oaa/video/UiConfigRequestMessage.audit.yaml` | skip_missing_gold_prereq | static=True, cross_version=False |
| `oaa/video/VideoFocusIndicationMessage.audit.yaml` | skip_schema_invalid | pre_existing_invalid: 'description' is a required property |
| `oaa/video/VideoFocusModeMessage.audit.yaml` | skip_retracted | confidence: retracted |
| `oaa/video/VideoFocusNotificationMessage.audit.yaml` | skip_retracted | confidence: retracted |
| `oaa/video/VideoFocusRequestMessage.audit.yaml` | skip_already_platinum | already_platinum |

## Unobserved services — no claim either way

| Directory | Count | Breakdown |
|-----------|-------|-----------|
| `oaa/bluetooth` | 3 | silver: 3 |
| `oaa/carcontrol` | 2 | gold: 2 |
| `oaa/common` | 5 | bronze: 1, silver: 4 |
| `oaa/control` | 27 | bronze: 1, gold: 2, silver: 24 |
| `oaa/generic` | 1 | bronze: 1 |
| `oaa/input` | 17 | gold: 13, silver: 4 |
| `oaa/mic` | 1 | gold: 1 |
| `oaa/navigation` | 12 | silver: 12 |
| `oaa/notification` | 1 | bronze: 1 |
| `oaa/phone` | 3 | gold: 3 |
| `oaa/radio` | 1 | silver: 1 |
| `oaa/sensor` | 37 | bronze: 3, silver: 34 |
| `oaa/wifi` | 14 | bronze: 1, gold: 2, retracted: 1, silver: 10 |

## Walker run metadata

- **capture_path:** `captures/oem-vw-mib3oi-2026-04-06`
- **capture_sha256:** `b66645c9a8a55eb466e9edf00715441af1a135edc1de057756b01882d0130408`
- **messages_jsonl_line_count:** `7954`
- **scope_dirs:** `['oaa/av', 'oaa/media', 'oaa/video', 'oaa/audio']`
- **walker_run_date:** `2026-04-11`
- **walker_version:** `10.02`

