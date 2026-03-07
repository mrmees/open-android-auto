# Input Channels

## Overview

The head unit sends user input (touch, buttons, rotary, touchpad) to the phone via input channels. Each display can have its own input channel, matched by `display_id` in the SDP `InputChannelConfig`.

The input pipeline on the phone: HU sends `InputEventIndication` (msg 0x8001) → `iae.java` (CAR.GAL.INPUT endpoint) parses the proto → dispatches to the appropriate handler based on which field is populated (touch, button, rotary, touchpad, or absolute).

---

## Message Catalog

| Msg ID | Direction | Proto Class (16.2) | Name | Purpose |
|--------|-----------|-------------------|------|---------|
| 0x8001 | HU → Phone | `vxj` | InputEventIndication | All input events (touch, button, rotary, touchpad) |
| 0x8002 | Phone → HU | `vxr` | InputBindingRequest | Phone tells HU which keycodes it wants to receive |
| 0x8003 | HU → Phone | `vxs` | InputBindingResponse | HU acknowledges binding request |
| 0x8004 | Phone → HU | `vxi` | InputBindingNotification | Haptic feedback requests |

---

## InputEventIndication (0x8001)

The main input message. Exactly one of fields 3-7 is populated per message.

```protobuf
message InputEventIndication {
    required uint64 timestamp       = 1;  // elapsedRealtime in microseconds
    // field 2 does NOT exist (skipped in proto numbering)
    optional TouchEvent touch_event     = 3;  // touchscreen input
    optional ButtonEvents button_event  = 4;  // hardware button press/release
    optional AbsoluteInputEvents abs_event = 5;  // touchpad primary click
    optional RelativeInputEvents rel_event = 6;  // rotary scroll
    optional TouchEvent touchpad_event  = 7;  // touchpad surface input
}
```

**Note:** Fields 3 and 7 use the **same message type** (`wbz` / TouchEvent). The phone differentiates touchscreen vs touchpad by field number, not by message structure. Touchscreen events get `SOURCE_TOUCHSCREEN` (0x1002) and `TOOL_TYPE_FINGER` (1); touchpad events get `SOURCE_TOUCHPAD` (0x100008) and `TOOL_TYPE_MOUSE` (3).

---

## Touch Events

### Coordinate Space

**Absolute pixel coordinates matching the video resolution.** No normalization (not 0.0–1.0), no DPI scaling. If the HU advertises 1024×600 video, touch coordinates must be in the range (0,0) to (1023,599).

The phone applies `+ offsetX/offsetY` when constructing the Android MotionEvent, but these are typically 0 for the main display.

### Pressure

**Not supported.** The phone hardcodes pressure to `0.8f` for all touch events. Do not send pressure data — it will be ignored.

### TouchEvent Message

```protobuf
message TouchEvent {             // APK class: wbz
    repeated TouchLocation locations = 1;  // one per active pointer
    optional uint32 action_index     = 2;  // which pointer triggered POINTER_DOWN/UP
    optional TouchAction action      = 3;  // touch action type
}

message TouchLocation {          // APK class: wby
    required uint32 x          = 1;  // pixel X coordinate
    required uint32 y          = 2;  // pixel Y coordinate
    required uint32 pointer_id = 3;  // multi-touch pointer ID
}
```

### Touch Actions

| Proto Value | Android MotionEvent | Name |
|:-----------:|:-------------------:|------|
| 0 | ACTION_DOWN (0) | First pointer down |
| 1 | ACTION_UP (1) | Last pointer up |
| 2 | ACTION_MOVE (2) | Pointer moved |
| 5 | ACTION_POINTER_DOWN (5) | Additional pointer down |
| 6 | ACTION_POINTER_UP (6) | Non-last pointer up |

Values 3 and 4 are not mapped (default to 0 / ACTION_DOWN).

### Multi-Touch

Supported via repeated `TouchLocation` entries. Each pointer has a unique `pointer_id`. For `POINTER_DOWN`/`POINTER_UP` actions, `action_index` specifies which pointer in the list triggered the event. The phone encodes this as `(action_index << 8) | action` for the Android MotionEvent.

Array starts at 8 pointers and doubles as needed — no hard limit in the protocol, though practical car touchscreens rarely exceed 5.

---

## Button Events

### Message Format

```protobuf
message ButtonEvents {           // APK class: vxv
    repeated ButtonEvent events = 1;
}

message ButtonEvent {            // APK class: vxu
    required uint32 keycode    = 1;  // Android keycode value
    required bool   is_pressed = 2;  // true = down, false = up
    required uint32 meta_state = 3;  // Android meta state flags
    optional bool   long_press = 4;  // fire-and-forget long press
}
```

### Long Press Behavior

When `long_press = true` AND `is_pressed = true`, the phone immediately generates a synthetic press+release pair. This is a "fire and forget" notification — the HU is telling the phone "this was a long press", not holding down a key.

### Key Repeat

Normal presses start a long-press timer (`ViewConfiguration.getLongPressTimeout()`). Additional presses before timeout increment a repeat count passed to the Android KeyEvent.

### AA-Specific Custom Keycodes

| Keycode | Hex | Name | Purpose |
|---------|-----|------|---------|
| 65535 | 0xFFFF | SENTINEL | Marker/boundary |
| 65536 | 0x10000 | ROTARY_CONTROLLER | Scroll wheel (also used in rotary events) |
| 65537 | 0x10001 | MEDIA | Media app shortcut |
| 65538 | 0x10002 | NAVIGATION | Nav app shortcut |
| 65539 | 0x10003 | RADIO | Radio app shortcut |
| 65540 | 0x10004 | TEL | Phone app shortcut |
| 65541 | 0x10005 | PRIMARY_BUTTON | Touchpad click |
| 65542 | 0x10006 | SECONDARY_BUTTON | Secondary click |
| 65543 | 0x10007 | TERTIARY_BUTTON | Tertiary click |
| 65544 | 0x10008 | TURN_CARD | Turn card display |

### Common Standard Android Keycodes

| Keycode | Name | Typical HW Button |
|---------|------|------------------|
| 3 | HOME | Home button |
| 4 | BACK | Back button |
| 5 | CALL | Answer call |
| 6 | ENDCALL | End call |
| 19–23 | DPAD_UP/DOWN/LEFT/RIGHT/CENTER | D-pad / rotary |
| 24–25 | VOLUME_UP/DOWN | Volume buttons |
| 79 | HEADSETHOOK | Steering wheel button |
| 82 | MENU | Menu button |
| 84 | SEARCH | Search/voice |
| **85** | **MEDIA_PLAY_PAUSE** | **Toggle play/pause** |
| **86** | **MEDIA_STOP** | **Stop playback** |
| **87** | **MEDIA_NEXT** | **Next track** |
| **88** | **MEDIA_PREVIOUS** | **Previous track** |
| **126** | **MEDIA_PLAY** | **Play (explicit)** |
| **127** | **MEDIA_PAUSE** | **Pause (explicit)** |
| 164 | VOLUME_MUTE | Mute |
| 219 | ASSIST | Google Assistant |
| 231 | VOICE_ASSIST | Voice assist |
| 260–263 | NAVIGATE_PREVIOUS/NEXT/IN/OUT | UI navigation |

### Media Playback Control

**The input channel is the ONLY way to control media playback.** There is no dedicated media command message on the media status channel (ch 10) — that channel is unidirectional phone → HU. All production head units send media controls as button events on this channel.

To control playback, send a `ButtonEvent` with `is_pressed=true` followed by `is_pressed=false` (press + release pair). The phone routes these keycodes to the active `MediaSession.Callback` (onPlay, onPause, onSkipToNext, etc.).

**SDP requirement:** The HU must advertise the media keycodes (85, 86, 87, 88, 126, 127) in the input channel's `supported_keycodes` in the ServiceDiscoveryResponse. The phone uses this list to determine which keycodes the HU can send.

### Special Key Handling

D-pad keys (19–22) and DPAD_CENTER (23) have their meta_state zeroed before being sent as KeyEvents. ROTARY_CONTROLLER (65536) also gets this treatment.

---

## Rotary / Scroll Input

### Message Format

```protobuf
message RelativeInputEvents {    // APK class: wbc
    repeated RelativeInputEvent events = 1;
}

message RelativeInputEvent {     // APK class: wbb
    required uint32 scan_code = 1;  // axis identifier (only 65536 recognized)
    required int32  delta     = 2;  // signed scroll amount
}
```

### Behavior

- Only `scan_code = 65536` (ROTARY_CONTROLLER) is recognized. Other values are logged and ignored.
- **Delta is signed**: positive = scroll forward/down, negative = scroll backward/up.
- **Zero delta is silently dropped** (logged as "Ignoring zero delta relative event").
- Generates an Android MotionEvent with `ACTION_SCROLL` (8), `AXIS_VSCROLL = delta`, and `SOURCE_ROTARY_ENCODER` (0x2002).
- Pointer ID is hardcoded to 31.

### Rotary vs Touchpad Conflict

If both ROTARY_CONTROLLER (65536) is in `supported_keycodes` AND a touchpad with `ui_navigation = true` is configured, the phone **disables rotary** and logs: "Rotary controller not supported when touchpad for UI navigation is present."

---

## Absolute Input Events

### Message Format

```protobuf
message AbsoluteInputEvents {   // APK class: vuu
    repeated AbsoluteInputEvent events = 1;
}

message AbsoluteInputEvent {    // APK class: vut
    required uint32 axis  = 1;  // scan code / axis
    required int32  value = 2;  // axis value
}
```

### Behavior

Only `axis = 65541` (PRIMARY_BUTTON / 0x10005) is handled. Generates a DPAD_CENTER (23) KeyEvent with `is_pressed = (value == 1)`. This is the "click" on a physical touchpad surface.

---

## SDP Input Configuration

### InputChannelConfig (vxm)

Advertised per input channel in the ServiceDiscoveryResponse:

```protobuf
message InputChannelConfig {
    repeated int32 supported_keycodes = 1 [packed = true];
    repeated TouchScreenConfig touch_screen_configs = 2;
    repeated TouchPadConfig touchpad_configs = 3;
    repeated HapticFeedbackType haptic_types = 4;  // enum values 1-5
    optional uint32 display_id = 5;  // matches VideoChannelDescriptor display
}
```

**Field 5 is `display_id`**, not capabilities. The phone matches input configs to displays by this field.

### TouchScreenConfig (vxl)

```protobuf
message TouchScreenConfig {
    required int32 width      = 1;  // touch area width in pixels
    required int32 height     = 2;  // touch area height in pixels
    optional DisplayType type = 3;  // MAIN=1, CLUSTER=2, AUXILIARY=3 (default=1)
}
```

Width and height must match the video resolution for that display.

### TouchPadConfig (vxk)

```protobuf
message TouchPadConfig {
    required int32 width           = 1;  // virtual touchpad width (pixels)
    required int32 height          = 2;  // virtual touchpad height (pixels)
    optional bool  ui_navigation   = 3;  // touchpad for focus navigation (DPAD mode)
    optional int32 physical_width  = 4;  // physical pad width in mm
    optional int32 physical_height = 5;  // physical pad height in mm
    optional bool  unknown_6       = 6;
    optional bool  absolute_mode   = 7;  // absolute positioning vs relative
    optional int32 sensitivity     = 8;  // 0-10 range (5 = neutral)
}
```

**Sensitivity formula**: `threshold × ((sensitivity - 5) × -0.5 / 5 + 1.0)`
- 0 = most sensitive (1.5× multiplier, smaller swipe threshold)
- 5 = neutral (1.0×)
- 10 = least sensitive (0.5×)

**Swipe threshold**: `min(width / 6, max(width/6, 4mm × width/physical_width)) × sensitivity_multiplier`

### Phone Response to SDP

From the input config, the phone determines:
- **Has rotary**: `supported_keycodes` contains 65536
- **Has d-pad**: UP + DOWN + LEFT + RIGHT + CENTER all present
- **Has touchpad**: `touchpad_configs` is non-empty
- **Has search**: `supported_keycodes` contains 84

### Virtual Touchpad (D-pad → swipe conversion)

If the car reports complete D-pad (19–23), no rotary, no touchpad, AND specific conditions (PhenotypeFlag + `CarInfo.f20450r == 3`), the phone synthesizes a virtual touchpad and converts D-pad keys to swipe gestures.

---

## Quirks and Gotchas

> **Coordinate space**: Touch coordinates are raw pixels matching the video resolution. No normalization, no DPI scaling. If you advertise 1024×600 video, send touch coordinates in that space.

> **No pressure**: All events get hardcoded 0.8f pressure on the phone. The protocol does not support pressure sensitivity.

> **Touchscreen and touchpad share the same proto type**: Both are `TouchEvent` (wbz). The phone differentiates by field number in `InputEventIndication` — field 3 = touchscreen, field 7 = touchpad.

> **Long press is fire-and-forget**: Setting `long_press = true` with `is_pressed = true` causes the phone to immediately generate press+release. The HU does NOT need to send a separate release event.

> **Rotary disabled by touchpad**: If both rotary and UI-navigation touchpad are configured, rotary is silently disabled. Pick one.

> **Display ID matching**: `InputChannelConfig.display_id` must match the `CarDisplayId` from the video channel descriptor. Each display needs its own input config in the SDP.

> **Action index shift**: For multi-touch pointer events, the phone encodes as `(action_index << 8) | action`. The HU must set `action_index` correctly for POINTER_DOWN/POINTER_UP.

---

## APK Source References (16.2)

| Class | Role |
|-------|------|
| `iae` | CAR.GAL.INPUT — input channel endpoint, dispatches all input types |
| `hlg` | Input injector — constructs MotionEvents and KeyEvents |
| `hxt` | Touch event builder — applies coordinates, pointer properties |
| `vxj` | InputEventIndication proto |
| `wbz` | TouchEvent proto (shared by touchscreen and touchpad) |
| `wby` | TouchLocation proto (x, y, pointer_id) |
| `vxv` | ButtonEvents proto (repeated ButtonEvent) |
| `vxu` | ButtonEvent proto (keycode, is_pressed, meta_state, long_press) |
| `vxt` | ButtonCode enum (full keycode mapping) |
| `wbc` | RelativeInputEvents proto (rotary/scroll) |
| `wbb` | RelativeInputEvent proto (scan_code, delta) |
| `vuu` | AbsoluteInputEvents proto (touchpad click) |
| `vut` | AbsoluteInputEvent proto (axis, value) |
| `vxm` | InputChannelConfig — SDP input capabilities per display |
| `vxl` | TouchScreenConfig — resolution per display |
| `vxk` | TouchPadConfig — touchpad dimensions, sensitivity, mode |
| `vxr` | InputBindingRequest — phone requests specific keycodes |
| `vxs` | InputBindingResponse — HU acknowledges keybindings |
| `vxi` | InputBindingNotification — haptic feedback |
