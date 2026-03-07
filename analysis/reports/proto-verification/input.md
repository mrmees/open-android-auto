# Input Channel Verification Report

**Channel:** Input (GAL type 8, tag `CAR.GAL.INPUT`)
**Handler:** `iae.java` (16.2)
**Helper:** `hlg.java` (16.2) — input injector, SDP processing, haptic feedback
**Verified:** 2026-03-06
**Status:** COMPLETE

## Message Catalog

| Msg ID | Direction | Proto Class (16.2) | Name | Confidence |
|--------|-----------|-------------------|------|------------|
| 0x8001 | HU→Phone | vxj | InputEventIndication | Gold |
| 0x8002 | Phone→HU | vxr | InputBindingRequest | Gold |
| 0x8003 | HU→Phone | vxs | InputBindingResponse | Gold |
| 0x8004 | Phone→HU | vxi | InputBindingNotification | Gold |

## Handler Details

- **GAL type 8** (iae constructor: `super(8, ...)`), tag `CAR.GAL.INPUT`
- **No msg ID offset** — unlike AV channels, input channel reads wire IDs directly
- **Receives:** 0x8001 (32769) and 0x8003 (32771) in `iae.mo18864a`
- **Sends:** 0x8002 (32770) via `hlg.mo18727r` and 0x8004 (32772) via `hlg.m18746o`

## Wire Messages (4 Gold)

### InputEventIndication (0x8001, vxj)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | timestamp | uint64 | optional |
| 3 | touch_event | TouchEvent (wbz) | optional |
| 4 | button_event | ButtonEvents (vxv) | optional |
| 5 | absolute_input_event | AbsoluteInputEvents (vuu) | optional |
| 6 | relative_input_event | RelativeInputEvents (wbc) | optional |
| 7 | touchpad_event | TouchEvent (wbz) | optional |

No field 2 (skipped in numbering). Fields 3 and 7 share the same proto type (wbz).
Phone differentiates touchscreen (field 3) vs touchpad (field 7) by field number.

### InputBindingRequest (0x8002, vxr)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | keycodes | int32 | repeated packed |

**REWRITTEN** — was incorrectly `display_id(1)+binding_type(2)`. Actual: phone echoes
back the supported keycodes from InputChannelConfig to acknowledge which it will handle.

### InputBindingResponse (0x8003, vxs)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | status | int32 | required |

**NEW** — no proto file previously existed. HU acknowledges binding request.

### InputBindingNotification (0x8004, vxi)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | feedback_type | HapticFeedbackType enum (vwy) | optional |

Phone requests haptic feedback. Only sent if type was in SDP supported_haptic_types.

## Sub-Messages (8 Gold)

### TouchEvent (wbz)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | touch_location | TouchLocation (wby) | repeated |
| 2 | action_index | uint32 | optional |
| 3 | touch_action | TouchAction enum | optional |

### TouchLocation (wby)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | x | uint32 | required |
| 2 | y | uint32 | required |
| 3 | pointer_id | uint32 | required |

**Fixed:** all 3 fields changed optional→required (DB + direct access pattern confirm).

### ButtonEvents (vxv)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | button_events | ButtonEvent (vxu) | repeated |

### ButtonEvent (vxu)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | keycode | uint32 | required |
| 2 | is_pressed | bool | required |
| 3 | meta_state | uint32 | required |
| 4 | long_press | bool | optional |

**Fixed:** renamed scan_code→keycode, meta→meta_state. Fields 1-3 optional→required.

### RelativeInputEvents (wbc)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | relative_input_events | RelativeInputEvent (wbb) | repeated |

### RelativeInputEvent (wbb)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | scan_code | uint32 | required |
| 2 | delta | int32 | required |

**Fixed:** both fields optional→required.

### AbsoluteInputEvents (vuu)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | absolute_input_events | AbsoluteInputEvent (vut) | repeated |

**Fixed:** removed non-existent fields 2 (display_id) and 3 (action). Only 1 field.

### AbsoluteInputEvent (vut)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | axis | uint32 | required |
| 2 | value | int32 | required |

**Fixed:** removed non-existent field 3 (pointer_id). Fixed field 2 type uint32→int32.

## SDP Config (3 Gold)

### InputChannelConfig (vxm)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | supported_keycodes | int32 | repeated packed |
| 2 | touch_screen_configs | TouchScreenConfig (vxl) | repeated |
| 3 | touchpad_configs | TouchPadConfig (vxk) | repeated |
| 4 | supported_haptic_types | HapticFeedbackType enum (vwy) | repeated |
| 5 | display_id | uint32 | optional |

**Fixed:** renamed input_type→supported_keycodes, key_configs→supported_haptic_types,
capabilities→display_id.

### TouchScreenConfig (vxl)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | width | int32 | required |
| 2 | height | int32 | required |
| 3 | display_type | DisplayType enum | optional |

**Fixed:** syntax proto3→proto2. Fields 1-2 optional→required.

### TouchPadConfig (vxk)

| Field | Name | Type | Modifier |
|-------|------|------|----------|
| 1 | width | int32 | required |
| 2 | height | int32 | required |
| 3 | ui_navigation | bool | optional |
| 4 | physical_width | int32 | optional |
| 5 | physical_height | int32 | optional |
| 6 | ui_absolute | bool | optional |
| 7 | tap_as_select | bool | optional |
| 8 | sensitivity | int32 | optional |

**Fixed:** syntax proto3→proto2. All unknown fields identified from hlg.java dump diagnostic.

## Enums (3 Gold)

### TouchAction

| Value | Name | Android Equivalent |
|-------|------|--------------------|
| 0 | PRESS | ACTION_DOWN |
| 1 | RELEASE | ACTION_UP |
| 2 | DRAG | ACTION_MOVE |
| 5 | POINTER_DOWN | ACTION_POINTER_DOWN |
| 6 | POINTER_UP | ACTION_POINTER_UP |

Values 3,4 not mapped (default to ACTION_DOWN). Confirmed via hlg.java static SparseIntArray.

### HapticFeedbackType (vwy)

| Value | Name |
|-------|------|
| 1 | FEEDBACK_SELECT |
| 2 | FEEDBACK_FOCUS_CHANGE |
| 3 | FEEDBACK_DRAG_SELECT |
| 4 | FEEDBACK_DRAG_START |
| 5 | FEEDBACK_DRAG_END |

Closed enum (no value 0). Verified via vve case 12 → vwy.m37362b.

### ButtonCode (vxt) — Reference Only

Not a wire protocol enum. ButtonEvent.keycode uses raw Android keycode integers.
This enum is a convenience reference. AA custom keycodes (65536-65544) verified via hlg.java.

## Retracted Protos (4)

| Proto | File | Reason |
|-------|------|--------|
| AbsInputEvent | InputEventIndicationMessage.proto (inline) | vvh in 16.2 is different proto (1 int32 field) |
| AbsoluteEvent | InputEventIndicationMessage.proto (inline) | vvi in 16.2 is BatteryStatus |
| KeyEvent | KeyEventData.proto | Duplicate of ButtonEvent (same class vxu/vyi) |
| TouchCoordinate | TouchCoordinateData.proto | Wrong class mapping (wbb = RelativeInputEvent) |

## Retracted Duplicates (2)

| Proto | File | Reason |
|-------|------|--------|
| InputChannel | InputChannelData.proto | Duplicate of InputChannelConfig, uses wrong sub-messages (TouchConfig=compass sensor) |
| TouchConfig | TouchConfigData.proto | Not input-related — compass/heading sensor data (CarSensorEvent type 5) |

## Key Discoveries

1. **InputBindingRequest is a keycode echo:** Phone echoes back the SDP keycodes as acknowledgment — NOT a display/binding request. The previous schema was completely wrong.

2. **AbsoluteInputEvent has only 2 fields:** The supposed pointer_id (field 3) doesn't exist. zzq descriptor confirms uint32(1) + int32(2) only.

3. **AbsoluteInputEvents has only 1 field:** Previous display_id(2) and action(3) were from wrong class mapping (wcj in 16.1 → different structure in 16.2).

4. **TouchPadConfig field names identified:** hlg.java diagnostic dump reveals ui_navigation(3), physical_width(4), physical_height(5), ui_absolute(6), tap_as_select(7), sensitivity(8).

5. **InputChannelConfig field 5 is display_id:** NOT capabilities or max_touchscreen_pointers. Matches CarDisplayId.f20666b for multi-display routing.

6. **TouchConfig (vwz) is compass sensor data:** Completely unrelated to input — used in CarSensorEvent type 5. Was incorrectly referenced by InputChannelData.proto.

7. **Triage tool class mapping errors:** Multiple audit yamls had wrong 16.2 class names due to obfuscation name reuse. AbsoluteInputEvent was mapped to wby (TouchLocation), AbsoluteInputEvents to wbz (TouchEvent), InputBindingRequest to wbb (RelativeInputEvent).
