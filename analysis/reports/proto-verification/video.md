# Video Channel Verification Report

**Channel:** Video (AV sink)
**GAL Tag:** `CAR.GAL.VIDEO`
**Handler:** `ied.java` (16.2) extends `icv.java` (AV base) extends `iav.java`
**Date:** 2026-03-06

## Complete Message ID Table (Ground Truth)

### Video-Specific Messages (ied.java — raw wire IDs, no +1 offset)

| Wire ID | Direction | Proto Class (16.2) | Name | Confidence |
|---------|-----------|-------------------|------|------------|
| 0x8007 | HU→Phone | wct | VideoFocusRequest | Gold |
| 0x8008 | Phone→HU | wcr | VideoFocusIndication | Gold |
| 0x8009 | Phone→HU | wci | UpdateUiConfigRequest (inbound) | Gold |
| 0x800A | HU→Phone | wci | UpdateUiConfigRequest (outbound) | Gold |
| 0x800C | HU→Phone | vuy | AudioUnderflowNotification | Bronze |
| 0x800D | HU→Phone | vxp | ActionTakenNotification | Bronze |
| 0x800E | Phone→HU | vxq | IntegratedOverlayStartNotification | Gold |
| 0x800F | Phone→HU | — | IntegratedOverlayStopNotification (empty) | Gold |
| 0x8011 | HU→Phone | wcj | UiConfigRequest (theming tokens) | Gold |
| 0x8012 | Phone→HU | wck | UpdateHuUiConfigResponse | Gold |

### Inherited AV Messages (icv.java — +1 offset via vdp.m36513at)

| Wire ID | Direction | Proto Class (16.2) | Name | Confidence |
|---------|-----------|-------------------|------|------------|
| 0x8000 | Phone→HU | wbs | AVChannelSetupRequest | Gold (media ch) |
| 0x8001 | Phone→HU | wbu | AVChannelStartIndication | Gold (media ch) |
| 0x8002 | Phone→HU | wbv | AVChannelStopIndication | Gold (media ch) |
| 0x8003 | HU→Phone | vwn | AVChannelSetupResponse | Gold (media ch) |
| 0x8004 | HU→Phone | vuw | AVMediaAckIndication | Gold (media ch) |
| 0x800B | — | — | Signal/heartbeat (no proto) | Gold (media ch) |
| 0x8013 | HU→Phone | vyg | AVChannelMediaStats | Gold |
| 0x8014 | Phone→HU | vya | AVChannelMediaOptions | Silver |

## Per-Proto Verification Results

### VideoFocusRequest (wct, 0x8007, HU→Phone) — Gold

All 6 checks pass. No changes needed to field schema.

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | Built and sent in `ied.m20258P` |
| Message ID | PASS | `m20106k(32775)` = wire 0x8007 |
| Direction | PASS | Serialized and sent (outbound) |
| Field schema | PASS | field 2 = wcq enum (VideoFocusMode), field 3 = wcs enum (VideoFocusReason), no field 1 |
| Cross-references | PASS | ied.java, ilj.java (clustersim), qfd.java (logger) |
| Enum values | PASS | See enum sections below |

**Changes:** Updated 16.2 class from wdd→wct, upgraded to Gold.

### VideoFocusIndication (wcr, 0x8008, Phone→HU) — Gold

All 6 checks pass. No changes needed to field schema.

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | Deserialized in `ied.mo18864a` case 32776 |
| Message ID | PASS | `i == 32776` = wire 0x8008 |
| Direction | PASS | Deserialized from ByteBuffer (inbound) |
| Field schema | PASS | field 1 = wcq enum (wcrVar.f75227c), field 2 = bool (wcrVar.f75228d) |
| Cross-references | PASS | ied.java, ikj.java (sender), qfd.java (logger) |
| Enum values | PASS | Uses VideoFocusMode (wcq) |

**Note:** vdp internal name is `MEDIA_MESSAGE_VIDEO_FOCUS_NOTIFICATION`, but we use "Indication" to match aasdk convention. Both are valid.

### IntegratedOverlayStartNotification (vxq, 0x800E, Phone→HU) — Gold

**Previously misidentified as VideoFocusNotification.**

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | Deserialized in `ied.mo18864a` case 32782 |
| Message ID | PASS | `i == 32782` = wire 0x800E |
| Direction | PASS | Deserialized from ByteBuffer (inbound) |
| Field schema | CORRECTED | field 1 = int32 (display session ID, NOT focus_mode) |
| Cross-references | PASS | Passed to huy case 8 → qdd.mo30156e(int) display callback |
| Enum values | N/A | Plain int32, not an enum |

**vdp name:** `MEDIA_MESSAGE_INTEGRATED_OVERLAY_START_NOTIFICATION`
**Retracted:** VideoFocusNotificationMessage.proto (field 1 was wrongly called focus_mode)
**Created:** IntegratedOverlayStartNotification.proto

### IntegratedOverlayStopNotification (empty, 0x800F, Phone→HU) — Gold

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | Handled in `ied.mo18864a` case 32783 |
| Message ID | PASS | `i == 32783` = wire 0x800F |
| Direction | PASS | No deserialization (empty) |
| Field schema | PASS | Empty — no payload |
| Cross-references | PASS | Sends handler msg 9 → qdd.mo30157f() callback |
| Enum values | N/A | Empty |

**vdp name:** `MEDIA_MESSAGE_INTEGRATED_OVERLAY_STOP_NOTIFICATION`
**Created:** IntegratedOverlayStopNotification.proto

### UpdateUiConfigRequest (wci, 0x8009/0x800A, bidirectional) — Gold

**New discovery — not in any previous proto.**

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | ied.java lines 149-160 (outbound) and 217-261 (inbound) |
| Message ID | PASS | Inbound 0x8009 (case 32777), outbound 0x800A (m20106k 32778) |
| Direction | PASS | Bidirectional |
| Field schema | PASS | field 1 = AdditionalVideoConfig/wcb (required — error if missing) |
| Cross-references | PASS | huz.mo19808w receives, huy case 5 processes |
| Enum values | N/A | Sub-message reference |

**vdp name:** `MEDIA_MESSAGE_UPDATE_UI_CONFIG`
**Created:** UpdateUiConfigRequestMessage.proto (references existing AdditionalVideoConfig)

### UiConfigRequest (wcj, 0x8011, HU→Phone) — Gold

Existing proto structure confirmed correct. Updated class refs and added field to UiConfigValue.

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | Sent by huz.mo19796n → ied.m20106k(32785) |
| Message ID | PASS | m20106k(32785) = wire 0x8011 |
| Direction | PASS | HU→Phone only (built from UiStyle by hum.java) |
| Field schema | CORRECTED | UiConfigValue was empty, now has `optional uint32 value = 1` |
| Cross-references | PASS | hum→huz→ied send chain, response at 0x8012 |
| Enum values | N/A | String key-value pairs |

**vdp name:** `MEDIA_MESSAGE_INTEGRATED_OVERLAY_SESSION_DATA_UPDATE`
**WARNING:** 16.1 class names (wct, wco, wcq) all refer to DIFFERENT protos in 16.2 (VideoFocusRequest, VideoResolution enum, VideoFocusMode enum respectively).

### UpdateHuUiConfigResponse (wck, 0x8012, Phone→HU) — Gold

**Previously misidentified as VideoFocusModeMessage.**

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | Deserialized in `ied.mo18864a` case 32786 |
| Message ID | PASS | `i != 32786` inverted check = wire 0x8012 |
| Direction | PASS | Deserialized from ByteBuffer (inbound) |
| Field schema | CORRECTED | field 1 = ThemingTokensStatus enum (NOT VideoFocusMode) |
| Cross-references | PASS | huy case 10: "Theming tokens accepted/rejected/Error" |
| Enum values | CORRECTED | 3 values: ERROR=0, ACCEPTED=1, REJECTED=2 |

**vdp name:** `MEDIA_MESSAGE_UPDATE_HU_UI_CONFIG_RESPONSE`
**Retracted:** VideoFocusModeMessage.proto (field 1 was wrongly VideoFocusMode)
**Created:** UpdateHuUiConfigResponse.proto with ThemingTokensStatus enum

## Enum Verification

### VideoFocusMode (wcq) — Gold

| Value | Name | APK Name | Status |
|-------|------|----------|--------|
| 0 | NONE | (not in APK) | Proto3 default sentinel only |
| 1 | PROJECTED | VIDEO_FOCUS_PROJECTED | PASS |
| 2 | NATIVE | VIDEO_FOCUS_NATIVE | PASS |
| 3 | NATIVE_TRANSIENT | VIDEO_FOCUS_NATIVE_TRANSIENT | PASS |
| 4 | PROJECTED_NO_INPUT_FOCUS | VIDEO_FOCUS_PROJECTED_NO_INPUT_FOCUS | PASS |

All 4 APK values used in ied.java switch logic. PROJECTED_NO_INPUT_FOCUS stripped to PROJECTED for video focus transitions, input focus tracked separately.

### VideoFocusReason (wcs) — Gold

| Value | Name | APK Name | Status |
|-------|------|----------|--------|
| 0 | UNKNOWN | UNKNOWN | PASS |
| 1 | PHONE_SCREEN_OFF | PHONE_SCREEN_OFF | PASS |
| 2 | LAUNCH_NATIVE | LAUNCH_NATIVE | PASS |
| 3 | LAST_MODE | VIDEO_FOCUS_REASON_LAST_MODE | PASS |
| 4 | USER_SELECTION | VIDEO_FOCUS_REASON_USER_SELECTION | PASS |

### ThemingTokensStatus (new) — Gold

| Value | Name | Log String |
|-------|------|------------|
| 0 | THEMING_TOKENS_ERROR | "Error providing theming tokens" |
| 1 | THEMING_TOKENS_ACCEPTED | "Theming tokens accepted" |
| 2 | THEMING_TOKENS_REJECTED | "Theming tokens rejected" |

### VideoResolution (wco) — Gold (full rewrite)

| Value | Old Name | New Name | Status |
|-------|----------|----------|--------|
| 0 | NONE | NONE | Proto3 default |
| 1 | _480p | VIDEO_800x480 | Renamed |
| 2 | _720p | VIDEO_1280x720 | Renamed |
| 3 | _1080p | VIDEO_1920x1080 | Renamed |
| 4 | _1440p | VIDEO_2560x1440 | Renamed |
| 5 | _720p_p | VIDEO_3840x2160 | **WRONG** — was 720p portrait, actually 4K |
| 6 | _1080pp | VIDEO_720x1280 | **WRONG** — was 1080p, actually 720p portrait |
| 7 | _1080p_p | VIDEO_1080x1920 | Renamed |
| 8 | — | VIDEO_1440x2560 | NEW in 16.2 |
| 9 | — | VIDEO_2160x3840 | NEW in 16.2 |

## SDP Data Proto Verification

### VideoConfig (wcp) — confirmed, no changes

All 11 fields match. Defaults: fps=1 (_60), margin_width=1, codec=1 (PCM).

### AdditionalVideoConfig (wcb) — field 6 enum needs investigation

7 fields structurally match. Field 6 sub-message (vux in 16.2) uses an enum validator pointing to vvf (AudioFocusType values 1-4), not our ResizeActionType (values 0-2). Obfuscated name reuse likely — needs deeper investigation in audio channel pass.

### VideoMargins (xhg) — confirmed, no changes

3 fields (int32 top, bottom, side), exact match.

### DisplayType (vws) — confirmed, no changes

3 values (MAIN=0, CLUSTER=1, AUXILIARY=2), exact match.

### VideoFPS — confirmed, no changes

2 values (_60=1, _30=2), exact match.

## Shared AV Messages (icv.java)

### AVChannelMediaStats (vyg, 0x8013, HU→Phone) — Gold

Existing proto structure confirmed correct (15 fields). Fixed:
- Wire msg ID: 0x8014 → 0x8013 (was dispatch value, not wire value)
- 16.2 class: vyu → vyg
- Sub-message class: vvo → vva (StatsEntry)

### AVChannelMediaOptions (vya, 0x8014, Phone→HU) — Silver

New discovery. 13 fields (mostly PhenotypeFlag wrappers). Built by hnc.java from feature flags. Gated by PDK version (>= 5.0/5.1/6.0). Placeholder proto created — full field schema deferred to audio channel pass.

## Retracted Protos

| Proto | Reason | Replacement |
|-------|--------|-------------|
| VideoFocusNotification | Actually IntegratedOverlayStartNotification | IntegratedOverlayStartNotification.proto |
| VideoFocusModeMessage | Actually UpdateHuUiConfigResponse | UpdateHuUiConfigResponse.proto |

## Additional Messages Not Fully Verified

| Wire ID | Direction | Name | Notes |
|---------|-----------|------|-------|
| 0x800C | HU→Phone | AudioUnderflowNotification (vuy) | From huz.java, Bronze |
| 0x800D | HU→Phone | ActionTakenNotification (vxp) | From huz.java, Bronze |

## Key Discoveries

1. **ied.java uses raw wire IDs** — unlike icv's receive handler which applies +1 via vdp.m36513at(), ied's video-specific message checks use the raw wire value directly. This means video-specific msg IDs in ied.mo18864a ARE the wire values.

2. **AdditionalVideoConfig (wcb) is shared** — used both in VideoConfig field 11 (initial setup) and as the payload of UpdateUiConfigRequest (runtime UI updates). Same data structure, two uses.

3. **Obfuscated name reuse is rampant** — 16.1→16.2 class name changes in this channel:
   - wct: UiConfigRequest → VideoFocusRequest
   - wco: UiConfigData → VideoResolution enum
   - wcq: UiConfigEntry → VideoFocusMode enum
   - wcu: VideoFocusModeMessage → VoiceSessionRequest (control channel!)

4. **VideoResolution values 5-9 completely changed** — aasdk-era names were wrong. Value 5 was labeled "720p portrait" but is actually 3840x2160 (4K).

5. **ThemingTokensStatus is NOT VideoFocusMode** — same field type (1x enum) but completely different semantics. Structure-only matching is dangerous.
