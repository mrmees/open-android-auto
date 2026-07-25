# Video Channel Verification Report

**Channel:** Video (AV sink)
**GAL Tag:** `CAR.GAL.VIDEO`
**Updated:** 2026-07-25 from Android Auto `17.3.662804-release`

## Accepted Android Auto 17.3 evidence

The accepted directions and 17.3 class names below come from
`analysis/reports/android-auto-17.3-update/message-matrix.md` and the direct
phone endpoint sources under
`analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/`:
`jdc.java`, `itt.java`, `its.java`, and shared AV handler `jca.java`. Payload
descriptors are in the named `x*.java` file, including `xig.java:7-20,39` for
the exact MediaOptions shape. The later 16.2 sections are retained as a
historical schema baseline and do not supply the accepted 17.3 directions.

### Video-specific and shared AV messages

| Wire ID | Direction | 17.3 Class | Name | Confidence |
|---------|-----------|-------------------|------|------------|
| 0x8007 | Phone -> HU | xnd | VideoFocusRequest | Gold |
| 0x8008 | HU -> Phone | xnb | VideoFocusIndication | Gold |
| 0x8009 | HU -> Phone | xms | UpdateUiConfigRequest (inbound to phone) | Gold |
| 0x800A | Phone -> HU | xms | UpdateUiConfigRequest (outbound from phone) | Gold |
| 0x800B | HU -> Phone | — | AudioUnderflow; no payload parsed | Bronze (17.3-only trace) |
| 0x800C | Phone -> HU | xex | ActionTaken; enum field 1 and public action enum unpublished | Bronze (17.3-only trace) |
| 0x800D | Phone -> HU | xhv | OverlayParameters; repeated overlay-options field 1, nested semantics unpublished | Bronze (17.3-only trace) |
| 0x800E | HU -> Phone | xhw | IntegratedOverlayStartNotification | Gold |
| 0x800F | HU -> Phone | — | OverlayStop; empty payload | Bronze (17.3-only trace) |
| 0x8010 | unknown | — | reserved; name/payload/direction unknown and deferred | deferred |
| 0x8011 | Phone -> HU | xmt | UiConfigRequest (theming tokens) | Bronze (no qualifying primary anchor/cross-version entry) |
| 0x8012 | HU -> Phone | xmu | UpdateHuUiConfigResponse | Gold |
| 0x8013 | HU -> Phone | xim | MediaStats | Silver |
| 0x8014 | Phone -> HU | xig | MediaOptions | Bronze (17.3-only static trace) |
| 0x8015 | Phone -> HU | xgu | CriticalUiNotification | Bronze (17.3-only static trace) |

#### 0x8014 MediaOptions descriptor inventory

`xig.java:7-20,39` proves message fields 1, 3, 4, 5, 6, 8, 10, 12,
and 13 referencing 17.3 `abmh` (`oaa.proto.data.PingConfiguration`), bool
fields 2, 9, and 11, and uint32 field 7. The canonical neutral names expose
only tag and type; field semantics remain unresolved.

## Historical Android Auto 16.2 baseline

The remaining class names and trace attributions in this report are explicitly
the older 16.2 `ied`/`icv` baseline. They document prior schema work and the
cross-version conflict; they are not mislabeled as 17.3 evidence.

### Inherited AV Messages (`icv.java` — 16.2 baseline)

| Wire ID | Direction | Proto Class (16.2) | Name | Confidence |
|---------|-----------|-------------------|------|------------|
| 0x8000 | Phone→HU | wbs | AVChannelSetupRequest | Silver |
| 0x8001 | Phone→HU | wbu | AVChannelStartIndication | Silver |
| 0x8002 | Phone→HU | wbv | AVChannelStopIndication | Gold (media ch) |
| 0x8003 | HU→Phone | vwn | AVChannelSetupResponse | Silver |
| 0x8004 | HU→Phone | vuw | AVMediaAckIndication | Silver |

## Historical 16.2 per-proto verification results

### VideoFocusRequest (`wct`, historical 16.2) — Gold

Historical wire ID: 0x8007.
Historical direction: HU -> Phone.

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

### VideoFocusIndication (`wcr`, historical 16.2) — Gold

Historical wire ID: 0x8008.
Historical direction: Phone -> HU.

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

### IntegratedOverlayStartNotification (`vxq`, historical 16.2) — Gold

Historical wire ID: 0x800E.
Historical direction: Phone -> HU.

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

### IntegratedOverlayStopNotification (empty, historical 16.2) — Bronze

Historical wire ID: 0x800F.
Historical direction: Phone -> HU.

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

The earlier Gold label is superseded. The 16.2 checks and the 17.3 callback
trace are a single primary-trace evidence type; no `cross_version` entry names
exact version-to-class pairs for this empty wrapper.

### UpdateUiConfigRequest (`wci`, historical 16.2) — Gold

Historical wire IDs: 0x8009 and 0x800A.
Historical directions: Phone -> HU and HU -> Phone, respectively.

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

### UiConfigRequest (`wcj`, historical 16.2) — Gold

Historical wire ID: 0x8011.
Historical direction: HU -> Phone.

Existing proto structure confirmed correct. Updated class refs and added field to UiConfigValue.

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | Sent by huz.mo19796n → ied.m20106k(32785) |
| Message ID | PASS | m20106k(32785) = wire 0x8011 |
| Direction | PASS | Historical HU -> Phone send in the 16.2 endpoint |
| Field schema | CORRECTED | UiConfigValue was empty, now has `optional uint32 value = 1` |
| Cross-references | PASS | hum→huz→ied send chain, response at 0x8012 |
| Enum values | N/A | String key-value pairs |

**vdp name:** `MEDIA_MESSAGE_INTEGRATED_OVERLAY_SESSION_DATA_UPDATE`
**WARNING:** 16.1 class names (wct, wco, wcq) all refer to DIFFERENT protos in 16.2 (VideoFocusRequest, VideoResolution enum, VideoFocusMode enum respectively).

### UpdateHuUiConfigResponse (`wck`, historical 16.2) — Gold

Historical wire ID: 0x8012.
Historical direction: Phone -> HU.

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

## Historical 16.2 shared AV messages (`icv.java`)

### AVChannelMediaStats (`vyg`, 0x8013, HU -> Phone) — Silver

Existing proto structure confirmed correct (15 fields). Fixed:
- Wire msg ID: 0x8014 → 0x8013 (was dispatch value, not wire value)
- 16.2 class: vyu → vyg
- Sub-message class: vvo → vva (StatsEntry)

### AVChannelMediaOptions (`vya`, 0x8014, Phone -> HU) — historical Silver

The 16.2 pass established 13 fields but left their types approximate. Direct
17.3 `xig.java:7-20,39` evidence now proves nine PingConfiguration messages,
three bools, and one uint32. The canonical proto publishes that exact shape
with neutral names; application semantics for all 13 fields remain unresolved.

## Retracted Protos

| Proto | Reason | Replacement |
|-------|--------|-------------|
| VideoFocusNotification | Actually IntegratedOverlayStartNotification | IntegratedOverlayStartNotification.proto |
| VideoFocusModeMessage | Actually UpdateHuUiConfigResponse | UpdateHuUiConfigResponse.proto |

## Additional 17.3 message boundaries

| Wire ID | Direction | Name | Notes |
|---------|-----------|------|-------|
| 0x800B | HU -> Phone | AudioUnderflowNotification | Phone callback parses no payload; no additional signal semantics are inferred |
| 0x800C | Phone -> HU | ActionTakenNotification | Wrapper has enum field 1; public action enum is unpublished |
| 0x800D | Phone -> HU | IntegratedOverlayParametersNotification | Wrapper has repeated overlay-options field 1; nested overlay-option semantics are unpublished |
| 0x8010 | unknown | reserved | Name, payload, and direction are unknown; publication is deferred |
| 0x8015 | Phone -> HU | CriticalUiNotification | Optional critical-UI-focus enum field 1; no acknowledgement or response implied |

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
