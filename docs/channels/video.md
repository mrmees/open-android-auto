# Video Channel (3)

> **Architecture context:** This channel is part of the Android Auto multiplexed
> protocol. For the overall architecture — framing, SDP binding, capability
> negotiation — see [Channel Architecture Reference](architecture.md).

## Proto Confidence Summary

| Message | Tier | Evidence | Audit File |
|---------|------|----------|------------|
| VideoFocusRequest | **Gold** | deep_trace, handler_verified | [VideoFocusRequestMessage.audit.yaml](../../oaa/video/VideoFocusRequestMessage.audit.yaml) |
| VideoFocusIndication | **Gold** | deep_trace, handler_verified | [VideoFocusIndicationMessage.audit.yaml](../../oaa/video/VideoFocusIndicationMessage.audit.yaml) |
| UpdateUiConfigRequest | **Gold** | deep_trace, handler_verified | [UpdateUiConfigRequestMessage.audit.yaml](../../oaa/video/UpdateUiConfigRequestMessage.audit.yaml) |
| UiConfigRequest | Bronze | one legacy deep trace; no qualifying primary `.java` anchor or exact cross-version entry | [UiConfigRequestMessage.audit.yaml](../../oaa/video/UiConfigRequestMessage.audit.yaml) |
| UpdateHuUiConfigResponse | **Gold** | deep_trace, handler_verified | -- |
| IntegratedOverlayStartNotification | **Gold** | deep_trace, handler_verified | [IntegratedOverlayStartNotification.audit.yaml](../../oaa/video/IntegratedOverlayStartNotification.audit.yaml) |
| IntegratedOverlayStopNotification | Bronze | 17.3 receive/callback trace; no reproducible cross-version entry | [IntegratedOverlayStopNotification.audit.yaml](../../oaa/video/IntegratedOverlayStopNotification.audit.yaml) |
| ~~VideoFocusNotification~~ | **Retracted** | Actually IntegratedOverlayStartNotification (0x800E) | -- |
| ~~VideoFocusModeMessage~~ | **Retracted** | Actually UpdateHuUiConfigResponse (0x8012) | -- |
| AudioUnderflowNotification | Bronze | 17.3-only endpoint trace | -- |
| ActionTakenNotification | Bronze | 17.3-only endpoint/descriptor trace | -- |
| IntegratedOverlayParametersNotification | Bronze | 17.3-only endpoint/descriptor trace | -- |
| AVChannelMediaOptions | Bronze | 17.3 apk_deep_trace; runtime-unverified | [AVChannelMediaOptionsMessage.audit.yaml](../../oaa/av/AVChannelMediaOptionsMessage.audit.yaml) |
| CriticalUiNotification | Bronze | 17.3 apk_deep_trace; runtime-unverified | [CriticalUiNotification.audit.yaml](../../oaa/video/CriticalUiNotification.audit.yaml) |
| VideoConfig | Silver | apk_static, cross_version, wire_capture | [VideoConfigData.audit.yaml](../../oaa/video/VideoConfigData.audit.yaml) |
| AdditionalVideoConfig | Silver | apk_static, cross_version | [AdditionalVideoConfigData.audit.yaml](../../oaa/video/AdditionalVideoConfigData.audit.yaml) |
| VideoFocusMode (enum) | **Gold** | deep_trace, handler_verified | -- |
| VideoFocusReason (enum) | **Gold** | deep_trace, handler_verified | -- |
| VideoResolution (enum) | **Gold** | deep_trace (full rewrite from aasdk) | -- |
| VideoFPS (enum) | **Gold** | deep_trace | -- |
| DisplayType (enum) | **Gold** | deep_trace | -- |
| ThemingTokensStatus (enum) | **Gold** | deep_trace | -- |
| AVChannelSetupRequest | Silver | apk_static, cross_version | [AVChannelSetupRequestMessage.audit.yaml](../../oaa/av/AVChannelSetupRequestMessage.audit.yaml) |
| AVChannelSetupResponse | Silver | apk_static, cross_version | [AVChannelSetupResponseMessage.audit.yaml](../../oaa/av/AVChannelSetupResponseMessage.audit.yaml) |
| AVChannelStartIndication | Silver | apk_static, cross_version | [AVChannelStartIndicationMessage.audit.yaml](../../oaa/av/AVChannelStartIndicationMessage.audit.yaml) |
| AVMediaAckIndication | Silver | apk_static, cross_version | [AVMediaAckIndicationMessage.audit.yaml](../../oaa/av/AVMediaAckIndicationMessage.audit.yaml) |

---

## Overview

> Confidence: Mixed -- established messages with qualifying primary and exact
> cross-version anchors are Gold; 17.3-only static claims remain Bronze.

The video channel carries the **projected display** from the phone to the head unit. The phone renders its entire Android Auto UI (Coolwalk layout, maps, media cards, assistant) into a video surface, encodes it as H.264 (or VP9/AV1/H.265), and streams the compressed frames to the HU over channel 3. The HU decodes and displays them.

Unlike audio, which uses three separate channels for different roles, there is only **one video channel per display**. Multi-display setups (main + cluster + auxiliary) each get their own video channel with separate `ChannelDescriptor` entries in the SDP, each with a distinct `display_type`.

The video channel is an **AV channel** (handler `ied.java` extends `icv.java` AV base, extends `iav.java`). It inherits the standard AV setup/start/stop/ack flow from `icv.java`, then adds video-specific messages for focus management, UI configuration, theming tokens, and overlay notifications.

**Video focus** is the mechanism that determines whether the phone's projected UI or the HU's native UI has control of the display. In 17.3 the phone sends focus requests and the HU reports the resulting state. This is conceptually similar to audio focus but operates on display ownership rather than audio streams.

**Prerequisite:** The video channel requires AV channel setup before any video data flows. See [04-channel-lifecycle.md](../interactions/04-channel-lifecycle.md) for the channel open and AV setup sequence.

---

## Message Catalog

### Video-Specific Messages (ch 3 -- raw wire IDs, no +1 offset)

> Confidence: Per-message tiers below. Accepted directions come from the 17.3
> `jdc`/`itt`/`its`/`jca` endpoint trace; the 16.2 `ied` trace is a historical
> schema baseline.

| Msg ID | Message | Direction | Purpose | Confidence |
|--------|---------|-----------|---------|:---:|
| 0x8007 | VideoFocusRequest | Phone -> HU | Request video focus transition (projected/native) | **Gold** |
| 0x8008 | VideoFocusIndication | HU -> Phone | Report current video focus state | **Gold** |
| 0x8009 | UpdateUiConfigRequest (inbound to phone) | HU -> Phone | Runtime UI config update (margins, theme) | **Gold** |
| 0x800A | UpdateUiConfigRequest (outbound from phone) | Phone -> HU | Runtime UI config update (margins, theme) | **Gold** |
| 0x800B | AudioUnderflowNotification | HU -> Phone | Audio underflow callback; no payload parsed | Bronze |
| 0x800C | ActionTakenNotification | Phone -> HU | ActionTaken wrapper with enum field 1; public action enum remains unpublished | Bronze |
| 0x800D | IntegratedOverlayParametersNotification | Phone -> HU | OverlayParameters wrapper with repeated overlay-options field 1; nested overlay-option semantics remain unpublished | Bronze |
| 0x800E | IntegratedOverlayStartNotification | HU -> Phone | Overlay projection session started | **Gold** |
| 0x800F | IntegratedOverlayStopNotification | HU -> Phone | OverlayStop notification; empty payload | Bronze |
| 0x8010 | Reserved | unknown | Name, payload, and direction unknown; deferred | deferred |
| 0x8011 | UiConfigRequest | Phone -> HU | Send theming tokens (Material Design key-value pairs) | Bronze |
| 0x8012 | UpdateHuUiConfigResponse | HU -> Phone | Accept/reject theming tokens | **Gold** |
| 0x8013 | MediaStats | HU -> Phone | Playback statistics (15 fields) | Silver |
| 0x8014 | MediaOptions | Phone -> HU | Exact 13-field wire envelope; field semantics unresolved | Bronze |
| 0x8015 | CriticalUiNotification | Phone -> HU | Critical-UI-focus enum field 1; no response implied | Bronze |

### MediaOptions wire envelope (0x8014)

Android Auto 17.3 `xig` raw message info proves 13 optional proto2 fields:

| Tags | Wire type |
|---|---|
| 1, 3, 4, 5, 6, 8, 10, 12, 13 | `PingConfiguration` message |
| 2, 9, 11 | `bool` |
| 7 | `uint32` |

The canonical field names deliberately encode only tag and type. Field
semantics remain unresolved; the schema does not promote feature-flag, timing,
or gating interpretations from the historical 16.2 report.

### Retracted Video Messages

> **Both messages retracted (2026-03-06)** -- misidentified from aasdk-era naming.

| Msg ID | Message | Direction | Purpose | Confidence |
|--------|---------|-----------|---------|:---:|
| ~~0x800E~~ | ~~VideoFocusNotification~~ | -- | **RETRACTED** -- actually IntegratedOverlayStartNotification | Retracted |
| ~~0x8012~~ | ~~VideoFocusModeMessage~~ | -- | **RETRACTED** -- actually UpdateHuUiConfigResponse (ThemingTokensStatus) | Retracted |

### Inherited AV Messages (icv.java -- +1 offset via vdp.m36513at)

> Confidence: Silver+ [apk_static, cross_version]

These shared AV messages are documented in detail in [04-channel-lifecycle.md](../interactions/04-channel-lifecycle.md). Summary for video context:

| Msg ID | Message | Direction | Purpose | Confidence |
|--------|---------|-----------|---------|:---:|
| 0x8000 | AVChannelSetupRequest | Phone -> HU | Select video codec configuration | Silver |
| 0x8001 | AVChannelStartIndication | Phone -> HU | Video stream begins | Silver |
| 0x8002 | AVChannelStopIndication | Phone -> HU | Video stream stops | Silver |
| 0x8003 | AVChannelSetupResponse | HU -> Phone | Accept/reject, set max_unacked | Silver |
| 0x8004 | AVMediaAckIndication | HU -> Phone | Flow control acknowledgment | Silver |

### Config Messages (Service Discovery)

> Confidence: Silver+ [apk_static, cross_version, wire_capture]

| Message | Purpose | Confidence |
|---------|---------|:---:|
| VideoConfig | Resolution, FPS, DPI, codec, margins, additional config | Silver |
| AdditionalVideoConfig | Resolution ranges, UI theme, hidden elements, resize actions, margin configs | **Gold** |
| VideoMargins | Top/bottom/side margin values | Silver |

---

## Video Focus -- State Machine

> Confidence: Gold [deep_trace, handler_verified] -- VideoFocusMode and VideoFocusReason enums fully verified

Video focus determines who controls the display surface: the phone's projected AA UI or the HU's native interface. The phone is the **initiator** of focus transitions (via VideoFocusRequest), and the HU **responds** with the resulting state (via VideoFocusIndication).

### VideoFocusMode (wcq, 16.2) -- Gold

| Value | Name | Semantics |
|:---:|------|-----------|
| 0 | NONE | Proto3 default sentinel only -- not defined in APK |
| 1 | PROJECTED | Phone's projected UI is active and has input focus |
| 2 | NATIVE | HU's native UI is active -- phone stops rendering |
| 3 | NATIVE_TRANSIENT | HU's native UI temporarily active -- phone keeps rendering but does not receive input |
| 4 | PROJECTED_NO_INPUT_FOCUS | Phone's projected UI is visible but does NOT have input focus |

> **Note:** PROJECTED_NO_INPUT_FOCUS (4) is stripped to PROJECTED (1) for video focus transitions in `ied.java` -- input focus is tracked separately. The phone renders identically for both; the distinction only affects whether touch/key events are forwarded.

### VideoFocusReason (wcs, 16.2) -- Gold

| Value | Name | Semantics |
|:---:|------|-----------|
| 0 | UNKNOWN | Default / unspecified |
| 1 | PHONE_SCREEN_OFF | Phone screen turned off |
| 2 | LAUNCH_NATIVE | HU launching its own native app |
| 3 | LAST_MODE | Restoring previous focus mode |
| 4 | USER_SELECTION | User explicitly selected native/projected |

### VideoFocusRequest (0x8007, Phone -> HU)

The phone sends this to request the focus mode it wants the HU to apply.

| Field | Type | Description |
|-------|------|-------------|
| 2 | enum (VideoFocusMode) | Requested focus mode |
| 3 | enum (VideoFocusReason) | Why the focus is changing |

**Note:** There is no field 1 -- field numbering starts at 2.

### VideoFocusIndication (0x8008, HU -> Phone)

The HU responds with the current focus state.

| Field | Type | Description |
|-------|------|-------------|
| 1 | enum (VideoFocusMode) | Current focus mode |
| 2 | bool | `unrequested` -- true if this indication was not prompted by a VideoFocusRequest |

### Sequence: HU Switches to Native UI

```
Phone                                        Head Unit
  |                                             |
  |  ... projected UI active (PROJECTED) ...    |
  |                                             |
  |--- VideoFocusRequest(NATIVE, LAUNCH_NATIVE)> |  Phone requests native UI
  |<-- VideoFocusIndication(NATIVE, false) ------|  HU acknowledges
  |                                             |  Phone stops video encoding
  |                                             |  HU shows native UI
  |                                             |
  |  ... native UI active ...                   |
  |                                             |
  |--- VideoFocusRequest(PROJECTED, USER_SEL) -->|  Phone requests projection
  |<-- VideoFocusIndication(PROJECTED, false) ---|  HU acknowledges
  |--- AVChannelStartIndication (ch 3) -------> |  Video stream begins
  |--- [H.264 frames] -----------------------> |
```

### Sequence: Transient Native Overlay

```
Phone                                        Head Unit
  |                                             |
  |  ... projected UI active ...                |
  |                                             |
  |--- VideoFocusRequest(NATIVE_TRANSIENT, ...) >|  Phone requests native overlay
  |<-- VideoFocusIndication(NATIVE_T, false) ----|  HU reports the state,
  |                                             |  but input goes to HU native UI
  |                                             |
  |  ... HU overlay active ...                  |
  |                                             |
  |--- VideoFocusRequest(PROJECTED, LAST_MODE) ->|  Overlay dismissed
  |<-- VideoFocusIndication(PROJECTED, false) ---|  HU reports projected focus
```

### Unrequested Focus Indications

The HU can send a VideoFocusIndication with `unrequested = true` when its focus state changes without a VideoFocusRequest. The phone handles this as an indication, not a request.

---

## UI Configuration

> Confidence: Start notification Gold; stop notification Bronze.

The video channel carries two distinct UI configuration mechanisms. They share similar names but serve different purposes:

### Theming Tokens (UiConfigRequest / UpdateHuUiConfigResponse)

Material Design theming tokens -- key-value pairs that define colors, typography, and visual style. The phone sends these to the HU.

**UiConfigRequest (0x8011, Phone -> HU):**

| Field | Type | Description |
|-------|------|-------------|
| 1 | UiConfigData | Container with two lists of UiConfigEntry |

**UiConfigData:**

| Field | Type | Description |
|-------|------|-------------|
| 1 | repeated UiConfigEntry | Primary config entries |
| 2 | repeated UiConfigEntry | Secondary config entries |

**UiConfigEntry:**

| Field | Type | Description |
|-------|------|-------------|
| 1 | string | Key (Material Design token name) |
| 2 | oneof: UiConfigValue | Value wrapper |

**UiConfigValue:**

| Field | Type | Description |
|-------|------|-------------|
| 1 | uint32 | Numeric value (color, dimension, etc.) |

The phone processes these through `hum.java` (UiStyle builder) -> `huz.java` -> `ied.java` send chain.

**UpdateHuUiConfigResponse (0x8012, HU -> Phone):**

| Field | Type | Description |
|-------|------|-------------|
| 1 | enum (ThemingTokensStatus) | Accept/reject result |

**ThemingTokensStatus:**

| Value | Name | Log String |
|:---:|------|------------|
| 0 | THEMING_TOKENS_ERROR | "Error providing theming tokens" |
| 1 | THEMING_TOKENS_ACCEPTED | "Theming tokens accepted" |
| 2 | THEMING_TOKENS_REJECTED | "Theming tokens rejected" |

### Runtime UI Config (UpdateUiConfigRequest)

Runtime changes to margins, theme (day/night), display UI features, and resize actions. This is **bidirectional** -- both the HU and the phone can initiate updates using the same message type.

**UpdateUiConfigRequest directions:**

- 0x8009 is HU -> Phone.
- 0x800A is Phone -> HU.

| Field | Type | Description |
|-------|------|-------------|
| 1 | AdditionalVideoConfig | Full UI config payload (required -- error if missing) |

The payload is an `AdditionalVideoConfig` message -- the same data structure used in `VideoConfig` field 11 for initial SDP setup. At runtime, this message pushes updates for:
- Day/night theme switching (`ui_theme` field)
- Margin/inset adjustments (`margin_configs` field)
- Display UI feature changes (`hidden_ui_elements` field; historical field
  name; AA 17.3 consumes it when the HU requested GAL version >= 4.3)
- Resize action updates (`resize_actions` field)

If field 1 is missing, the phone returns `PROTOCOL_WRONG_MESSAGE` / `INVALID_UI_CONFIG` error.

---

## Integrated Overlay Notifications

> Confidence: Gold [deep_trace, handler_verified]

Integrated overlays are phone-rendered UI layers displayed on top of the HU's native content. The HU notifies the phone when overlay sessions start and stop.

**IntegratedOverlayStartNotification (0x800E, HU -> Phone):**

| Field | Type | Description |
|-------|------|-------------|
| 1 | int32 | Display session ID |

The session ID is passed to `qdd.mo30156e(int)` -- a display callback in the `com.google.android.gms.car.display` package.

**IntegratedOverlayStopNotification (0x800F, HU -> Phone):**

Empty message -- no fields. On HU -> Phone arrival, the phone endpoint queues
handler message 9, whose handler invokes the registered phone-side stopped
callbacks. The direct evidence does not establish overlay-state mutation or
dismissal.

---

## Video Codec Negotiation

> Confidence: Gold [deep_trace, 16.2 codec enum fully verified]

### Supported Codecs -- MediaCodecType Enum

| Value | Name | Status |
|:---:|------|--------|
| 0 | MEDIA_CODEC_UNKNOWN | Default/fallback |
| 3 | MEDIA_CODEC_VIDEO_H264 | **Primary** -- universally supported, mandatory |
| 5 | MEDIA_CODEC_VIDEO_VP9 | Supported |
| 6 | MEDIA_CODEC_VIDEO_AV1 | Supported (newer devices) |
| 7 | MEDIA_CODEC_VIDEO_H265 | Supported |

Values 1, 2, 4 are audio codecs (PCM, AAC-LC, AAC-LC-ADTS) -- not relevant for video.

### How Codec Selection Works

The HU declares ONE codec per video channel in the SDP via `VideoConfig.codec` (field 10):

1. HU sets `VideoConfig.codec` to a `MediaCodecType` value in the SDP
2. Phone reads this value. If unrecognized or absent, defaults to H.264
3. Phone initializes its video encoder for the selected codec
4. Phone sends `AVChannelSetupRequest` (msg 0x8000) with the codec index
5. HU responds with `AVChannelSetupResponse` (msg 0x8003): status OK/FAIL, max_unacked buffer depth

**H.264 is mandatory.** Every HU implementation must support H.264 decoding at minimum. VP9, AV1, and H.265 are optional and may offer better compression at the cost of decode complexity.

---

## SDP Configuration

> Confidence: Silver-Gold [apk_static, cross_version, wire_capture; sub-messages Gold]

The HU advertises video capabilities in the ServiceDiscoveryResponse via one or more `VideoConfig` entries (one per display).

### VideoConfig (wcp, 16.2) -- 11 Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| 1 | enum (VideoResolution) | -- | Display resolution (see enum below) |
| 2 | enum (VideoFPS) | _60 (1) | Frame rate (60 or 30 FPS) |
| 3 | uint32 | 1 | Margin width (pixels) |
| 4 | uint32 | -- | Margin height (pixels) |
| 5 | uint32 | -- | DPI -- Android density bucket (120/160/240/320/480/640) |
| 6 | uint32 | -- | Decoder additional depth -- extra buffer frames beyond default (0 = none, buffer = value + 1) |
| 7 | uint32 | -- | Viewing distance -- driver-to-display distance in mm (typically ~500 = 20 inches) |
| 8 | uint32 | -- | Pixel aspect ratio x 10000 (10000 = 1.0 = square pixels) |
| 9 | uint32 | -- | Real density -- actual DPI before Android bucket quantization |
| 10 | enum (MediaCodecType) | PCM (1) | Video codec (H.264=3, VP9=5, AV1=6, H.265=7) |
| 11 | AdditionalVideoConfig | -- | Extended config (insets, theme, elements, margins) |

> **Note:** The default for `codec` (field 10) is `PCM (1)` per the proto default, which is an audio codec value. When the phone sees a non-video codec value, it falls back to H.264. Set this explicitly to 3 (H.264) or another video codec.

#### 17.3 static delta

The 17.3 class is `xmz`, reached directly from `AVChannel` (`xik`) field 4.
It retains fields 1-6 and 8-11 but no longer declares viewing distance at field
7. The canonical proto keeps that optional field so older 16.x configurations
remain decodable.

### VideoResolution Enum (wco, 16.2) -- Gold (Full Rewrite)

**WARNING:** Values 5-9 were completely wrong in aasdk-era definitions. The old names have been corrected.

| Value | Correct Name | Old (Wrong) Name | Pixels |
|:---:|------|------|--------|
| 0 | NONE | NONE | Proto3 default |
| 1 | VIDEO_800x480 | _480p | 800 x 480 |
| 2 | VIDEO_1280x720 | _720p | 1280 x 720 |
| 3 | VIDEO_1920x1080 | _1080p | 1920 x 1080 |
| 4 | VIDEO_2560x1440 | _1440p | 2560 x 1440 |
| 5 | VIDEO_3840x2160 | ~~_720p_p~~ | 3840 x 2160 (4K landscape) |
| 6 | VIDEO_720x1280 | ~~_1080pp~~ | 720 x 1280 (720p portrait) |
| 7 | VIDEO_1080x1920 | _1080p_p | 1080 x 1920 (1080p portrait) |
| 8 | VIDEO_1440x2560 | (new) | 1440 x 2560 (1440p portrait, NEW in 16.2) |
| 9 | VIDEO_2160x3840 | (new) | 2160 x 3840 (4K portrait, NEW in 16.2) |

Landscape resolutions (values 1-5) have width > height. Portrait resolutions (values 6-9) have height > width. The phone uses these to determine screen orientation and layout (see [coolwalk-layout.md](coolwalk-layout.md)).

### VideoFPS Enum (vdp, 16.2) -- Gold

| Value | Name | Frame Rate |
|:---:|------|-----------|
| 0 | NONE | Proto3 default |
| 1 | _60 | 60 FPS |
| 2 | _30 | 30 FPS |

### AdditionalVideoConfig (wcb, 16.2) -- Gold

Extended configuration for display insets, theming, HU-provided UI features, and resize behavior. Used both in `VideoConfig` field 11 (initial SDP setup) and as the payload of `UpdateUiConfigRequest` (runtime updates). Phone-side consumers in 17.1 and 17.3 prove that fields 1-3 are Rect-style insets; the older “minimum/maximum/preferred resolution” labels were incorrect. In 17.3, field 5 is consumed only when the HU-requested GAL version is at least 4.3.

| Field | Type | Description |
|-------|------|-------------|
| 1 | VideoInsets | Projected display insets |
| 2 | VideoInsets | Additional inset rectangle (semantic label not recovered) |
| 3 | VideoInsets | Additional inset rectangle (semantic label not recovered) |
| 4 | UITheme | Theme mode (auto=0, light=1, dark=2) |
| 5 | repeated UIElement | HU-provided UI features the phone should not duplicate; AA 17.3 consumes them when the HU requested GAL version >= 4.3 and ignores them for a lower request (`hidden_ui_elements` historical field name) |
| 6 | repeated VideoResizeAction | Supported resize behaviors |
| 7 | repeated VideoMarginConfig | Margin/inset configurations |
| 8 | BlendedUIConfig | Display corner radii and native UI element rectangles (17.1+) |

In 17.3 this graph is `xml` → `xfi`: `xfi` contains optional corner radii
(`xgs`) and repeated native UI elements (`xir`). Each element carries a Rect
position (`xlh`) and an enum whose accepted numeric domain is 1-3; the original
symbolic names are not present in the APK, so the proto intentionally keeps
neutral value names.

**VideoInsets (vxn, 16.2):**

| Field | Type | Description |
|-------|------|-------------|
| 1 | uint32 | Top inset |
| 2 | uint32 | Bottom inset |
| 3 | uint32 | Left inset |
| 4 | uint32 | Right inset |

**UITheme:**

| Value | Name |
|:---:|------|
| 0 | UI_THEME_AUTOMATIC |
| 1 | UI_THEME_LIGHT |
| 2 | UI_THEME_DARK |

**UIElement (HU-provided display features):**

| Value | Name | Description |
|:---:|------|-------------|
| 0 | UI_ELEMENT_UNKNOWN | Default |
| 1 | UI_ELEMENT_CLOCK | HU provides a clock; phone can avoid duplicating it |
| 2 | UI_ELEMENT_BATTERY_LEVEL | HU provides battery status |
| 3 | UI_ELEMENT_PHONE_SIGNAL | HU provides phone signal status |
| 4 | UI_ELEMENT_NATIVE_UI_AFFORDANCE | HU provides a native UI affordance |
| 5 | UI_ELEMENT_NAVIGATION_TURN_DATA_AVAILABLE | Maps to `hasClusterTurnCard` flag 16; CLUSTER passes the inverse as `EXTRA_SHOW_TURN_CARD` |

In AA 17.3 when the HU requested GAL version >= 4.3, these enum values are
converted to `CarDisplayUiFeatures` flags 1, 2, 4, 8, and 16. For a lower HU
request, that phone ignores this list and instead derives clock, battery, and
phone-signal flags from `ServiceDiscoveryResponse.session_configuration`
masks 1, 4, and 2, respectively. No value-16 session mask is consumed in
either branch. The reference capture in
[Phone-Side Debugging](../phone-side-debug.md) requested 1.1 and negotiated
1.7, so the requested value selected the legacy branch.

**ResizeActionType:**

| Value | Name |
|:---:|------|
| 0 | ACTION_UNKNOWN |
| 1 | ACTION_RESIZE_TO_SMALLER |
| 2 | ACTION_RESIZE_TO_LARGER |

### VideoMargins (xhg, 16.1 / xhg, 16.2) -- Silver

Legacy margin format (SDP-level). Distinct from `VideoMarginConfig`/`VideoInsets` in `AdditionalVideoConfig`.

| Field | Type | Description |
|-------|------|-------------|
| 1 | int32 | Top margin |
| 2 | int32 | Bottom margin |
| 3 | int32 | Side margin (left and right) |

### DisplayType Enum (vws, 16.2) -- Gold

Each video channel is associated with a display type. Multiple displays means multiple video channels.

| Value | Name | Description |
|:---:|------|-------------|
| 0 | MAIN | Primary head unit display -- full Coolwalk UI |
| 1 | CLUSTER | Instrument cluster -- behind steering wheel |
| 2 | AUXILIARY | Secondary display -- e.g., passenger screen |

Constraints: exactly one MAIN, at most one CLUSTER, additional displays are AUXILIARY. See [display-routing.md](display-routing.md) for content routing details.

---

## Multi-Display

> For full details, see [display-routing.md](display-routing.md) and [coolwalk-layout.md](coolwalk-layout.md).

Each physical display gets its own video channel instance (`ied.java`), each with its own:
- `VideoConfig` in the SDP (resolution, DPI, codec, display_type)
- AV setup handshake (AVChannelSetupRequest/Response)
- Video focus state (independent per display)
- Video data stream (separate H.264/VP9/AV1/H.265 encode per display)

The SDP munger (`ilf.java`) creates separate `AVChannel` proto objects for each display. The `ied.java` constructor takes a `DisplayType` parameter and sets a boolean `f36752e = (displayType == MAIN)` that gates main-display-specific behavior.

### What Each Display Gets

| Display Type | Video Content | Content Routing |
|-------------|---------------|-----------------|
| MAIN | Full Coolwalk UI (nav, media, phone, messaging, assistant) | All content categories |
| CLUSTER | Navigation map or turn card (priority fallback chain) | Nav only, with power-saving mode |
| AUXILIARY | Navigation map or turn card only | NAVIGATION or TURN_CARD only |

Auxiliary displays cannot show media, phone, or messaging UI. The phone decides auxiliary content from `display_type` alone -- the `widget_type` SDP field exists but is effectively dead.

### DPI and Layout Impact

The DPI advertised in `VideoConfig` field 5 directly controls the phone's Coolwalk layout decisions. Lower DPI = higher `screenWidthDp` = more widescreen layout with horizontal dashboard. Higher DPI = more compact layout. See [coolwalk-layout.md](coolwalk-layout.md) for the full breakpoint reference and DPI impact tables.

---

## Implementation Guide

> Confidence: Gold -- combines deep-trace verified messages with established AV setup patterns

### Video Channel Setup Sequence

```
Phone                                        Head Unit
  |                                             |
  |  ... SDP exchanged, video channel opened ... |
  |                                             |
  |--- AVChannelSetupRequest (0x8000) --------> |  Phone selects H.264 (codec=3)
  |<-- AVChannelSetupResponse (0x8003) -------- |  HU accepts, sets max_unacked
  |                                             |
  |--- VideoFocusRequest(PROJECTED, USER_SEL) -->|  Phone requests projected focus
  |<-- VideoFocusIndication(PROJECTED, false) ---|  HU confirms
  |                                             |
  |--- UiConfigRequest (0x8011) --------------->|  Phone sends theming tokens (optional)
  |<-- UpdateHuUiConfigResponse (0x8012) -------|  HU accepts/rejects
  |                                             |
  |--- AVChannelStartIndication (0x8001) ------> |  Video stream begins
  |--- [H.264 NAL units] --------------------> |  Compressed video frames
  |<-- AVMediaAckIndication (0x8004) ---------- |  Flow control ack
  |--- [more H.264 frames] ------------------> |
```

### Video Focus Handler (C/C++)

```c
// Minimal video focus management on the HU side.
// The phone requests focus changes; the HU responds.

void handle_video_focus_request(VideoFocusRequest *req) {
    current_focus = req->focus_mode;

    switch (req->focus_mode) {
    case PROJECTED:
        // Phone is rendering -- show video decoder output
        show_projected_surface();
        enable_touch_forwarding();
        break;

    case PROJECTED_NO_INPUT_FOCUS:
        // Phone is rendering but we keep input
        show_projected_surface();
        disable_touch_forwarding();
        break;

    case NATIVE:
        // Phone stopped rendering -- show native UI
        show_native_ui();
        break;

    case NATIVE_TRANSIENT:
        // Phone keeps rendering but input is ours
        // Useful for native overlays (settings, alerts)
        show_native_overlay();
        break;
    }

    VideoFocusIndication ind;
    ind.focus_mode = current_focus;
    ind.unrequested = false;
    send_message(VIDEO_CHANNEL, 0x8008, &ind);
}
```

### Day/Night Mode Switching

To switch the projected UI between day and night mode at runtime:

```c
void set_day_night_mode(UITheme theme) {
    AdditionalVideoConfig config;
    config.ui_theme = theme;  // 0=auto, 1=light, 2=dark

    UpdateUiConfigRequest req;
    req.config = &config;
    send_message(VIDEO_CHANNEL, 0x8009, &req);
}
```

The phone will apply the theme change to its projected rendering. No response message is expected for `UpdateUiConfigRequest` -- it is fire-and-forget.

### Advertising HU-provided UI Elements

For AA 17.3 after the HU requested GAL version 4.3 through the supported
maximum 6.1, if the HU renders its own clock, battery, or signal indicators,
advertise them so the phone can avoid duplicating them in the projected UI:

```c
AdditionalVideoConfig config;
config.hidden_ui_elements = { UI_ELEMENT_CLOCK, UI_ELEMENT_BATTERY_LEVEL };
// Set in VideoConfig field 11 during SDP, or send via UpdateUiConfigRequest at runtime
```

In AA 17.3 when the HU requested a version below 4.3, `hidden_ui_elements` is
ignored; the legacy `session_configuration` masks provide only clock, battery,
and phone-signal features and cannot advertise the cluster-turn-card flag.

---

## Gotchas

> **Gotcha:** Video-specific messages in `ied.java` use **raw wire IDs** (e.g., 0x8007 for VideoFocusRequest). Inherited AV messages in `icv.java` use a **+1 offset** via `vdp.m36513at()`. Do not apply the +1 offset to video-specific message IDs -- they are already the wire values. This is the opposite of audio channels, which only have the inherited AV messages.

> **Gotcha:** `UpdateUiConfigRequest` is bidirectional with different IDs.
> ID 0x8009 is HU -> Phone.
> ID 0x800A is Phone -> HU.
> Both use the same proto and field schema, so the HU must handle both dispatch paths.

> **Gotcha:** `UiConfigRequest` (0x8011, theming tokens) and `UpdateUiConfigRequest` (0x8009/0x800A, runtime UI config) are **completely different messages** despite similar names. UiConfigRequest carries Material Design key-value token pairs. UpdateUiConfigRequest carries AdditionalVideoConfig (margins, theme enum, display UI features). Don't confuse them.

> **Gotcha:** The `VideoConfig.codec` field defaults to `PCM (1)` in the proto definition, which is an **audio codec**. Always set this explicitly to a video codec value (3/5/6/7). The phone falls back to H.264 if it encounters a non-video value, but relying on the fallback is fragile.

> **Gotcha:** **VideoResolution values 5-9 were completely wrong in aasdk.** Value 5 was labeled "720p portrait" but is actually 3840x2160 (4K landscape). Value 6 was labeled "1080p portrait" but is actually 720x1280 (720p portrait). Any implementation based on aasdk enum names for values >= 5 will advertise the wrong resolution. Values 8 and 9 are new in 16.2 and did not exist in aasdk at all.

> **Gotcha:** **Obfuscated class name reuse across APK versions is rampant** on the video channel. In 16.1, `wct` = UiConfigRequest. In 16.2, `wct` = VideoFocusRequest (completely different message). Similarly: `wco` (16.1: UiConfigData, 16.2: VideoResolution enum), `wcq` (16.1: UiConfigEntry, 16.2: VideoFocusMode enum). Never match protos by obfuscated class name across versions -- use enum value fingerprints or field structure instead.

> **Gotcha:** **ThemingTokensStatus is NOT VideoFocusMode.** Both are single-enum-field messages at the same field position (field 1). Structure-only proto matching would incorrectly map UpdateHuUiConfigResponse to a focus message. The aasdk-era `VideoFocusModeMessage` was this exact mistake -- it has been retracted.

> **Gotcha:** **Multiple AVChannelSetupResponse = error.** If the HU sends a second setup response on the video channel, the phone terminates with `MULTIPLE_DISPLAY_CONFIGS` error. Send exactly one response per channel setup.

> **Gotcha:** `VideoFocusRequest` has **no field 1** -- fields start at 2 (`focus_mode`) and 3 (`focus_reason`). Implementations parsing from field 1 will read the wrong data.

> **Gotcha:** `IntegratedOverlayStartNotification` field 1 is an **int32 display session ID**, not a focus mode enum. The retracted `VideoFocusNotification` had the same field position but incorrectly typed it as VideoFocusMode.

---

## References

### Proto Files -- Video-Specific
- [VideoFocusRequestMessage.proto](../../oaa/video/VideoFocusRequestMessage.proto)
- [VideoFocusIndicationMessage.proto](../../oaa/video/VideoFocusIndicationMessage.proto)
- [VideoFocusModeEnum.proto](../../oaa/video/VideoFocusModeEnum.proto)
- [VideoFocusReasonEnum.proto](../../oaa/video/VideoFocusReasonEnum.proto)
- [VideoConfigData.proto](../../oaa/video/VideoConfigData.proto)
- [VideoResolutionEnum.proto](../../oaa/video/VideoResolutionEnum.proto)
- [VideoFPSEnum.proto](../../oaa/video/VideoFPSEnum.proto)
- [AdditionalVideoConfigData.proto](../../oaa/video/AdditionalVideoConfigData.proto)
- [VideoMarginsData.proto](../../oaa/video/VideoMarginsData.proto)
- [DisplayTypeEnum.proto](../../oaa/video/DisplayTypeEnum.proto)
- [UiConfigRequestMessage.proto](../../oaa/video/UiConfigRequestMessage.proto)
- [UpdateUiConfigRequestMessage.proto](../../oaa/video/UpdateUiConfigRequestMessage.proto)
- [UpdateHuUiConfigResponse.proto](../../oaa/video/UpdateHuUiConfigResponse.proto)
- [IntegratedOverlayStartNotification.proto](../../oaa/video/IntegratedOverlayStartNotification.proto)
- [IntegratedOverlayStopNotification.proto](../../oaa/video/IntegratedOverlayStopNotification.proto)

### Proto Files -- Shared AV / UI Config
- [AVChannelSetupRequestMessage.proto](../../oaa/av/AVChannelSetupRequestMessage.proto)
- [AVChannelSetupResponseMessage.proto](../../oaa/av/AVChannelSetupResponseMessage.proto)
- [AVChannelStartIndicationMessage.proto](../../oaa/av/AVChannelStartIndicationMessage.proto)
- [AVMediaAckIndicationMessage.proto](../../oaa/av/AVMediaAckIndicationMessage.proto)
- [AVChannelMediaOptionsMessage.proto](../../oaa/av/AVChannelMediaOptionsMessage.proto)
- [AVChannelMessageIdsEnum.proto](../../oaa/av/AVChannelMessageIdsEnum.proto)
- [UiConfigMessages.proto](../../oaa/av/UiConfigMessages.proto) (Silver -- legacy definitions, canonical versions in oaa/video/)

### APK Source References (17.3 accepted matrix)
- `jdc.java` -- direct phone receive/send branches for focus, UI config, overlays, and theming response
- `itt.java` -- phone send builders for ActionTaken, OverlayParameters, UiConfigRequest, and CriticalUi
- `its.java` -- phone callback handling for overlay and theming response branches
- `jca.java` -- shared AV normalization for AudioUnderflow and MediaStats
- `xig.java` -- exact 13-field MediaOptions raw message info

### APK Source References (16.2 historical baseline)
- `ied.java` -- Video endpoint handler (extends icv.java AV base)
- `icv.java` -- AV channel setup base (AVChannelSetupRequest/Response)
- `iav.java` -- Channel base class
- `vdp.java` -- AV message ID enum + m36513at (+1 offset dispatch)
- `wct.java` -- VideoFocusRequest proto (16.2; was UiConfigRequest in 16.1!)
- `wcr.java` -- VideoFocusIndication proto
- `wcq.java` -- VideoFocusMode enum (16.2; was UiConfigEntry in 16.1!)
- `wcs.java` -- VideoFocusReason enum
- `wco.java` -- VideoResolution enum (16.2; was UiConfigData in 16.1!)
- `wcp.java` -- VideoConfig proto
- `wcb.java` -- AdditionalVideoConfig proto
- `wci.java` -- UpdateUiConfigRequest proto (bidirectional)
- `wcj.java` -- UiConfigRequest proto (theming tokens)
- `wck.java` -- UpdateHuUiConfigResponse proto
- `vxq.java` -- IntegratedOverlayStartNotification proto
- `wce.java` -- UiConfigData (theming token data)
- `wcg.java` -- UiConfigEntry (theming token entry)
- `wcf.java` -- UiConfigValue (theming token value)
- `wcc.java` -- ThemingTokensStatus validator
- `vws.java` -- DisplayType enum
- `vxn.java` -- VideoInsets sub-message (historically mislabeled as a resolution range)
- `hum.java` -- UiStyle builder (theming token construction)
- `huz.java` -- Video channel manager (send chain for UiConfigRequest/UpdateUiConfig)
- `huy.java` -- Handler message processor (case 5/8/9/10)
- `ilf.java` -- SDP munger (per-display VideoConfig construction)
- `hnt.java` -- Decoder buffer depth, pixel aspect ratio usage
- `qdd.java` -- Display callbacks (overlay start/stop)

### Verification Report
- [Proto Verification: Video Channel](../../analysis/reports/proto-verification/video.md) -- full verification trace with retractions

### Cross-References
- [Display routing](display-routing.md) -- multi-display content routing architecture
- [Coolwalk layout](coolwalk-layout.md) -- responsive layout engine, DPI impact, dashboard sizing
- [Channel map](../channel-map.md) -- Channel ID reference for all AA channels
- [04-channel-lifecycle.md](../interactions/04-channel-lifecycle.md) -- AV setup flow, channel open sequence
- [01-confidence-tiers.md](../verification/01-confidence-tiers.md) -- Confidence tier definitions

> **Capture evidence boundary:** The VW capture cannot validate claims about this surface.
> The on-phone hook lives inside the AA framing layer; `channel_id`, `flags`, and outer
> frame header semantics are below the hook's observation point. See
> [06-capture-non-claim-boundary.md](../verification/06-capture-non-claim-boundary.md).
