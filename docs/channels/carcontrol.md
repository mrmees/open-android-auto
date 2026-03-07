# Car Control Channel

## Overview

The Car Control channel (GAL Service 19, log tag `CAR.GAL.CAR_CONTROL`) provides vehicle property access via Android's VHAL (Vehicle Hardware Abstraction Layer). It covers HVAC controls, seat temperature, defrost, door locks, mirror heat, steering wheel heat, toll card status, and Hyundai/Kia vendor extensions.

The channel uses a **subscription model**: during setup the HU advertises its supported properties in the `CarControlChannelDescriptor` (part of the SDP), then registers listeners for the properties it cares about. The phone sends change events whenever a property value updates. The HU can also write property values (e.g., user changes temperature) and trigger car actions (e.g., launch HVAC app).

The pipeline on the phone: HU sends `RegisterCarPropertyListenersRequest` (0x8003) -> `hyc.java` (CAR.GAL.CAR_CONTROL handler) processes the registration -> phone subscribes to VHAL -> phone sends `CarPropertyChangeEvent` (0x8005) on each update. For writes: HU sends `SetCarPropertyValueRequest` (0x8001) -> phone sets the VHAL property -> phone responds with `SetCarPropertyValueResponse` (0x8002).

---

## Message Catalog

| Msg ID | Direction | Proto Class (16.2) | Name | Purpose |
|--------|-----------|-------------------|------|---------|
| 0x8001 | HU -> Phone | `wbq` | SetCarPropertyValueRequest | Set a vehicle property value |
| 0x8002 | Phone -> HU | `wbr` | SetCarPropertyValueResponse | Acknowledge property set with status |
| 0x8003 | HU -> Phone | `waz` | RegisterCarPropertyListenersRequest | Subscribe to property change events |
| 0x8004 | Phone -> HU | `wba` | RegisterCarPropertyListenersResponse | Per-property registration results |
| 0x8005 | Phone -> HU | `vwg` | CarPropertyChangeEvent | Property value changed notification |
| 0x8006 | HU -> Phone | `vvv` | CarActionNotification | Trigger a car action (app launch) |
| 0x8007 | Phone -> HU | `vvz` | CarControlGroupUpdate | Updated control group layout |

**Note:** The phone-side handler (`hyc.mo18864a()`) only processes 4 inbound messages: 0x8002, 0x8004, 0x8005, 0x8007. Message IDs 0x8001, 0x8003, and 0x8006 are send-only from the HU -- if the handler receives 0x8003 or 0x8006, it logs "Received unexpected car control message" and drops them.

---

## SetCarPropertyValueRequest (0x8001)

HU requests the phone to set a vehicle property. Correlated to the response by a UUID `request_id`.

```protobuf
message SetCarPropertyValueRequest {       // APK class: wbq (16.2) / wca (16.1)
    optional CarProperty car_property    = 1;  // property ID + area
    optional CarPropertyValue property_value = 2;  // value to set
    optional string request_id           = 3;  // UUID for correlating response
}
```

The HU generates a UUID, stores a UUID->callback mapping, sends the request, and matches the response by UUID when 0x8002 arrives.

---

## SetCarPropertyValueResponse (0x8002)

Phone acknowledges a property set request.

```protobuf
message SetCarPropertyValueResponse {      // APK class: wbr (16.2) / wcb (16.1)
    optional CarProperty car_property    = 1;  // property that was set
    optional int32 status                = 2;  // ProtocolStatus (vyh) — shared enum, not CarControlStatus
    optional string request_id           = 3;  // UUID matching the original request
    optional int32 error_code            = 4;  // CarPropertySetError code
}
```

---

## RegisterCarPropertyListenersRequest (0x8003)

HU subscribes to change events for a list of properties. Sent once on channel open.

```protobuf
message RegisterCarPropertyListenersRequest {  // APK class: waz (16.2) / wbk? (16.1)
    repeated CarProperty car_properties = 1;    // properties to subscribe to
}
```

The HU extracts all property references from its control groups, filters to only those present in the `CarPropertyConfig` list from the SDP, and sends this request.

---

## RegisterCarPropertyListenersResponse (0x8004)

Phone responds with per-property registration results and initial values.

```protobuf
message RegisterCarPropertyListenersResponse {  // APK class: wba (16.2) / wbk (16.1)
    repeated SetCarPropertyListenerResult results = 1;
}

message SetCarPropertyListenerResult {          // APK class: vwh (16.2) / vwv (16.1)
    optional CarProperty car_property = 1;      // property registered
    optional int32 status             = 2;      // ProtocolStatus (vyh) — shared enum
}
```

Failed registrations produce a `CarPropertyState` with status=2 (UNAVAILABLE) on the HU side.

---

## CarPropertyChangeEvent (0x8005)

Phone notifies the HU that a vehicle property value changed. This is the primary ongoing data flow.

```protobuf
message CarPropertyChangeEvent {            // APK class: vwg (16.2) / vwu (16.1)
    optional CarProperty car_property      = 1;  // which property changed
    optional CarPropertyValue property_value = 2;  // new value
    optional int32 status                  = 3;  // 1=AVAILABLE, 2=UNAVAILABLE
}
```

**Status field:** When status=1 (AVAILABLE), the value is valid. When status=2 (UNAVAILABLE), the property value is null and the HU should treat the control as inactive.

---

## CarActionNotification (0x8006)

HU tells the phone to trigger an application launch action.

```protobuf
message CarActionNotification {             // APK class: vvv (16.2) / vwj (16.1)
    optional CarAction action = 1;          // which action to trigger
}
```

These are not property changes -- they trigger app launches on the phone side. See [Car Action IDs](#car-action-ids) below.

---

## CarControlGroupUpdate (0x8007)

Phone sends an updated control group layout to the HU, replacing the existing group of the same type.

```protobuf
message CarControlGroupUpdate {             // APK class: vvz (16.2) / vwn (16.1)
    optional CarControlGroup car_control_group = 1;  // updated control layout
}
```

Used to dynamically enable/disable controls (e.g., disable AC when engine is off). The HU replaces its stored control group keyed by `group_type`.

---

## Core Sub-Messages

### CarProperty

Identifies a specific property in a specific vehicle area.

```protobuf
message CarProperty {                       // APK class: vuh (16.2) / vuv (16.1)
    CarPropertyId property_id = 1;          // which property (proto3)
    CarAreaId area_id         = 2;          // which zone
}
```

### CarAreaId

Identifies a vehicle zone. The repeated enum fields are bitmasks -- on the phone side, list elements are OR'd together into a single VHAL area bitmask.

```protobuf
message CarAreaId {                         // APK class: vui (16.2) / vuw (16.1)
    CarAreaType area_type                    = 1;  // GLOBAL, WINDOW, SEAT, MIRROR, WHEEL, DOOR
    repeated VehicleAreaWindow window_ids    = 2 [packed = true];
    repeated VehicleAreaSeat seat_ids        = 3 [packed = true];
    repeated VehicleAreaMirror mirror_ids    = 4 [packed = true];
    repeated VehicleAreaDoor door_ids        = 5 [packed = true];
    repeated VehicleAreaWheel wheel_ids      = 6 [packed = true];
}
```

Only one of fields 2-6 should be populated, matching the `area_type`. For GLOBAL properties, only field 1 is set.

### CarPropertyValue

A property value using a oneof for type discrimination.

```protobuf
message CarPropertyValue {                  // APK class: vup (16.2) / vvd (16.1), proto3
    oneof value {
        int32 int_value       = 1;          // HVAC_FAN_SPEED, HVAC_SEAT_TEMPERATURE, etc.
        float float_value     = 2;          // HVAC_TEMPERATURE_SET
        bool bool_value       = 3;          // HVAC_AC_ON, HVAC_POWER_ON, DOOR_LOCK, etc.
        int64 long_value      = 4;
        string string_value   = 5;
        IntValues int_array   = 6;          // repeated int32 (APK: vun)
        LongValues long_array = 7;          // repeated int64 (APK: vuo)
        FloatValues float_array = 8;        // repeated float (APK: vum)
    }
}

message IntValues {                         // APK class: vun (16.2) / vvb (16.1)
    repeated int32 values = 1 [packed = true];
}

message LongValues {                        // APK class: vuo (16.2) / vva (16.1)
    repeated int64 values = 1 [packed = true];
}

message FloatValues {                       // APK class: vum (16.2) / vvc (16.1)
    repeated float values = 1 [packed = true];
}
```

### CarAction

```protobuf
message CarAction {                         // APK class: vtz (16.2) / vun (16.1)
    CarActionId action_id = 1;
}
```

---

## Channel Setup: CarControlChannelDescriptor

Embedded in the SDP `ChannelDescriptorData` during service discovery. Tells the phone what properties, controls, and actions the HU supports.

```protobuf
message CarControlChannelDescriptor {       // APK class: vwa (16.2) / vwo (16.1)
    repeated CarPropertyConfig property_configs = 1;  // available VHAL properties
    repeated CarControl controls               = 2;  // UI control layout (vvx, NOT CarControlGroup)
    repeated CarActionEntry action_entries      = 3;  // available car actions
}
```

### CarPropertyConfig

Describes a property's type, access mode, and per-area value bounds.

```protobuf
message CarPropertyConfig {                 // APK class: vuj (16.2) / vux (16.1)
    CarPropertyId property_id            = 1;  // which property
    CarPropertyAccessMode access_mode    = 2;  // READ, WRITE, READ_WRITE
    CarPropertyChangeMode change_mode    = 3;  // STATIC, ON_CHANGE, CONTINUOUS
    repeated CarAreaId area_ids          = 4;  // area zones (16.2: bare CarAreaId)
    CarPropertyType property_type        = 5;  // value type
    repeated int32 config_array          = 6 [packed = true];  // property-specific config
    repeated CarPropertyAreaConfig area_configs = 7;  // area configs with min/max (16.2)
}
```

**16.1 -> 16.2 structural change:** In 16.1, field 4 was `repeated CarPropertyAreaConfig` (area + min/max bounds) and field 7 was `repeated CarPropertyValue` (supported values). In 16.2, field 4 became bare `repeated CarAreaId` (just zone identifiers) and field 7 became `repeated CarPropertyAreaConfig` (area configs with min/max bounds moved here).

### CarPropertyAreaConfig

Per-area value bounds for a property.

```protobuf
message CarPropertyAreaConfig {             // APK class: vty (16.2) / vum (16.1)
    CarAreaId area_id           = 1;        // which zone
    CarPropertyValue min_value  = 2;        // minimum allowed value
    CarPropertyValue max_value  = 3;        // maximum allowed value
}
```

### Control Layout Messages

The control layout is a tree structure sent in the SDP and updated dynamically via 0x8007.

```protobuf
message CarControlGroup {                   // APK class: vvy (16.2) / vwm (16.1)
    optional CarControlGroupType group_type = 1;  // UNKNOWN=0, PRIMARY=1
    repeated CarControl controls            = 2;  // child controls
}

message CarControl {                        // APK class: vvx (16.2) / vwl (16.1)
    oneof control {
        CarPropertyControl property_control = 1;  // property read/write control
        CarActionControl action_control     = 2;  // action button
        CarControlGroup control_group       = 3;  // nested group (recursive)
    }
    optional bool enabled                          = 4;  // is this control active?
    repeated CarControlMetadataType metadata       = 5;  // UI hints
    optional SideAffinity side_affinity            = 6;  // DRIVER or PASSENGER
}

message CarPropertyControl {               // APK class: vuk (16.2) / vuy (16.1)
    CarProperty property            = 1;   // the main property
    CarAction associated_action     = 2;   // action to trigger alongside
    CarProperty associated_property = 3;   // linked property (e.g., display units)
}

message CarActionControl {                 // APK class: vvu (16.2) / vwi (16.1)
    optional CarAction action = 1;         // the action
}

message CarActionEntry {                   // APK class: vua (16.2) / vuo (16.1)
    CarAction action = 1;                  // wrapper for SDP action list
}
```

---

## Enums

### ~~CarControlStatus~~ — RETRACTED

The original 3-value `CarControlStatus` enum has been **retracted**. The APK class `vyh` (16.2) is actually the shared **ProtocolStatus** enum with 34 values covering auth, BT, radio, sensors, car properties, and protocol errors. Status fields in `SetCarPropertyValueResponse` and `SetCarPropertyListenerResult` use `int32 status` (ProtocolStatus values), not a dedicated car control enum.

See [ProtocolStatus reference](../../analysis/reports/proto-verification/control.md) for the full 34-value enum.

### CarPropertyId

25 vehicle properties. **Values are raw VHAL IDs** (e.g., 358614275 = HVAC_TEMPERATURE_SET), NOT sequential 1-23 as previously documented.

| VHAL ID | Name | Area | Value Type | Description |
|---------|------|------|------------|-------------|
| 0 | UNKNOWN | - | - | Default |
| 358614275 | HVAC_TEMPERATURE_SET | SEAT | float | Target temperature per zone |
| 354419978 | HVAC_AUTO_ON | SEAT | bool | Auto climate mode |
| 354419977 | HVAC_DUAL_ON | SEAT | bool | Dual zone sync |
| 356517131 | HVAC_SEAT_TEMPERATURE | SEAT | int32 | Heated/cooled seat level |
| 356517120 | HVAC_FAN_SPEED | SEAT | int32 | Fan speed level |
| 356517121 | HVAC_FAN_DIRECTION | SEAT | int32 | Air direction (face/feet/defrost) |
| 356582673 | HVAC_FAN_DIRECTION_AVAILABLE | SEAT | int32 | Available direction bitmask |
| 289408270 | HVAC_TEMPERATURE_DISPLAY_UNITS | GLOBAL | int32 | 1=Celsius, 2=Fahrenheit |
| 354419973 | HVAC_AC_ON | SEAT | bool | A/C compressor |
| 354419974 | HVAC_MAX_AC_ON | SEAT | bool | Max A/C mode |
| 320865540 | HVAC_DEFROSTER | WINDOW | bool | Defroster per window zone |
| 354419975 | HVAC_MAX_DEFROST_ON | SEAT | bool | Max defrost mode |
| 354419984 | HVAC_POWER_ON | SEAT | bool | HVAC system on/off |
| 354419986 | HVAC_AUTO_RECIRC_ON | SEAT | bool | Auto recirculation |
| 354419976 | HVAC_RECIRC_ON | SEAT | bool | Manual recirculation |
| 356517139 | HVAC_SEAT_VENTILATION | SEAT | int32 | Ventilated seat level |
| 339739916 | HVAC_SIDE_MIRROR_HEAT | MIRROR | int32 | Mirror heater on/off/level |
| 289408269 | HVAC_STEERING_WHEEL_HEAT | GLOBAL | int32 | Steering wheel heater level |
| 289410874 | ELECTRONIC_TOLL_COLLECTION_CARD_STATUS | GLOBAL | int32 | Toll card reader status |
| 624984185 | HMG_HVAC_MTC_TEMPERATURE | SEAT | int32 | HMG multi-temp control |
| 557940737 | HMG_HVAC_TEMPERATURE_RANGE | SEAT | int32 | HMG temp range config |
| 627081341 | HMG_HVAC_TEMPERATURE_SET_CELSIUS | SEAT | float | HMG temperature (Celsius) |
| 627081339 | HMG_HVAC_TEMPERATURE_SET_FAHRENHEIT | SEAT | float | HMG temperature (Fahrenheit) |
| 371198722 | DOOR_LOCK | DOOR | bool | Per-door lock state (new in 16.2) |
| 34908672 | HMG_CAR_ALERTS_COUNT | GLOBAL | int32 | HMG vehicle alert count (new in 16.2) |

### Car Action IDs

| Value | Name | Purpose |
|-------|------|---------|
| 0 | UNKNOWN | Default |
| 3 | LAUNCH_HVAC | Open HVAC controls app |
| 4 | LAUNCH_CAR_MEDIA | Open car media app |
| 5 | LAUNCH_CONTROL_CENTER | Open control center |
| 6 | LAUNCH_CAR_ALERTS | Open car alerts |

**Note:** Values 1 and 2 are not defined. The enum jumps from 0 to 3.

### CarAreaType

| Value | Name | Used By |
|-------|------|---------|
| 0 | GLOBAL | Temperature display units, steering wheel heat, toll status |
| 2 | WINDOW | Defroster |
| 3 | SEAT | Most HVAC properties, seat heat/ventilation |
| 4 | MIRROR | Side mirror heat |
| 5 | WHEEL | (defined but no properties currently use it) |
| 6 | DOOR | Door lock (new in 16.2) |

### CarPropertyAccessMode

| Value | Name |
|-------|------|
| 0 | NONE |
| 1 | READ |
| 2 | WRITE |
| 3 | READ_WRITE |

### CarPropertyChangeMode

| Value | Name | Behavior |
|-------|------|----------|
| 0 | STATIC | Value never changes |
| 1 | ON_CHANGE | Phone sends 0x8005 when value changes |
| 2 | CONTINUOUS | Phone sends 0x8005 at a regular rate |

### CarPropertyType

| Value | Name | CarPropertyValue Field |
|-------|------|----------------------|
| 0 | UNKNOWN | - |
| 1 | BOOLEAN | bool_value (3) |
| 2 | INT32 | int_value (1) |
| 3 | INT64 | long_value (4) |
| 4 | FLOAT | float_value (2) |
| 5 | STRING | string_value (5) |
| 6 | BYTES | - |
| 7 | INT32_VEC | int_array (6) |
| 8 | INT64_VEC | long_array (7) |
| 9 | FLOAT_VEC | float_array (8) |
| 10 | MIXED | - |

### SideAffinity

| Value | Name |
|-------|------|
| 0 | NONE |
| 1 | DRIVER |
| 2 | PASSENGER |

### CarControlGroupType

| Value | Name |
|-------|------|
| 0 | UNKNOWN |
| 1 | PRIMARY |

### CarControlMetadataType

| Value | Name |
|-------|------|
| 0 | UNKNOWN |
| 1 | COMPACT_UI |
| 2 | PREFER_STATUS_BAR |

---

## Area Zone Bitmasks

All area enums are bitmask-based. The `CarAreaId` message uses repeated packed enum values -- on the phone side, these are OR'd together into a single bitmask for the VHAL API.

### VehicleAreaSeat

| Value | Bitmask | Position |
|-------|---------|----------|
| 0 | 0x0 | Unknown |
| 1 | 0x01 | Row 1 Left (Driver in LHD) |
| 2 | 0x02 | Row 1 Center |
| 4 | 0x04 | Row 1 Right (Passenger in LHD) |
| 16 | 0x10 | Row 2 Left |
| 32 | 0x20 | Row 2 Center |
| 64 | 0x40 | Row 2 Right |
| 256 | 0x100 | Row 3 Left |
| 1024 | 0x400 | Row 3 Right |

### VehicleAreaWindow

| Value | Bitmask | Position |
|-------|---------|----------|
| 0 | 0x0 | Unknown |
| 1 | 0x01 | Front Windshield |
| 2 | 0x02 | Rear Windshield |
| 16 | 0x10 | Row 1 Left |
| 64 | 0x40 | Row 1 Right |
| 256 | 0x100 | Row 2 Left |
| 1024 | 0x400 | Row 2 Right |
| 4096 | 0x1000 | Row 3 Left |
| 16384 | 0x4000 | Row 3 Right |
| 65536 | 0x10000 | Roof Top 1 |
| 131072 | 0x20000 | Roof Top 2 |

### VehicleAreaMirror

| Value | Bitmask | Position |
|-------|---------|----------|
| 0 | 0x0 | Unknown |
| 1 | 0x01 | Driver Left |
| 2 | 0x02 | Driver Right |
| 4 | 0x04 | Driver Center (rearview) |

### VehicleAreaDoor

| Value | Bitmask | Position |
|-------|---------|----------|
| 0 | 0x0 | Unknown |
| 1 | 0x01 | Row 1 Left |
| 4 | 0x04 | Row 1 Right |
| 16 | 0x10 | Row 2 Left |
| 64 | 0x40 | Row 2 Right |
| 256 | 0x100 | Row 3 Left |
| 1024 | 0x400 | Row 3 Right |
| 268435456 | 0x10000000 | Hood |
| 536870912 | 0x20000000 | Rear (trunk/liftgate) |

### VehicleAreaWheel

| Value | Bitmask | Position |
|-------|---------|----------|
| 0 | 0x0 | Unknown |
| 1 | 0x01 | Left Front |
| 2 | 0x02 | Right Front |
| 4 | 0x04 | Left Rear |
| 8 | 0x08 | Right Rear |

---

## Channel Lifecycle

### 1. Service Discovery

The `CarControlChannelDescriptor` is embedded in the SDP. It declares:
- **Property configs**: which VHAL properties are supported, their types, access modes, change modes, and per-area min/max bounds
- **Control groups**: a tree of `CarControl` entries defining the UI layout (property controls, action buttons, nested groups)
- **Action entries**: which car actions (app launches) are available

### 2. Channel Open and Subscription

When the channel opens (`hlb.mo18727r()`):
1. HU extracts all property references from control groups
2. Filters to only properties present in the supported configs
3. Sends 0x8003 (`RegisterCarPropertyListenersRequest`) with the filtered property list
4. Stores registered properties for later matching

### 3. Initial Values

Phone responds with 0x8004 (`RegisterCarPropertyListenersResponse`):
- Per-property status (SUCCESS or LISTENER_REGISTRATION_FAILED)
- Failed registrations produce UNAVAILABLE state on the HU

### 4. Ongoing Change Events

Phone sends 0x8005 (`CarPropertyChangeEvent`) whenever a VHAL property value changes:
- Contains property ID, area, new value, and availability status
- HU caches state and notifies its UI listeners

### 5. Dynamic Layout Updates

Phone may send 0x8007 (`CarControlGroupUpdate`) to update the control layout:
- Contains a new `CarControlGroup` replacing the existing one (keyed by `group_type`)
- Used to enable/disable controls dynamically

### 6. Property Writes

When the user changes a control:
1. HU sends 0x8001 (`SetCarPropertyValueRequest`) with a UUID
2. Phone sets the VHAL property
3. Phone responds with 0x8002 (`SetCarPropertyValueResponse`) with the same UUID and status

### 7. Car Actions

HU sends 0x8006 (`CarActionNotification`) for action buttons:
- Triggers app launches on the phone (HVAC, media, control center, alerts)
- Not property changes -- the phone handles these as intent launches

---

## Quirks and Gotchas

> **HMG temperature override**: If the car supports `HMG_HVAC_TEMPERATURE_SET_CELSIUS` (ID 22, VHAL 627081341), the phone transparently replaces `HVAC_TEMPERATURE_SET` (ID 1) with the HMG vendor property when setting temperature. Hyundai/Kia/Genesis vehicles use a vendor-specific VHAL property instead of the standard one. This happens in `hlb.m18711z()`.

> **SENSOR_HVAC_DATA (sensor type 12) is legacy**: The sensor channel defines an HVAC sensor type, but real HVAC data flows through this Car Control channel via property change events. Do not use the sensor channel for HVAC data.

> **CarPropertyConfig field 4/7 restructure (16.1 -> 16.2)**: In 16.1, field 4 was `repeated CarPropertyAreaConfig` (area + min/max) and field 7 was `repeated CarPropertyValue` (supported values). In 16.2, field 4 is bare `repeated CarAreaId` and field 7 is `repeated CarPropertyAreaConfig`. Implementations must handle both layouts.

> **What's NOT supported**: Despite VHAL covering a wide range of vehicle functions, the AA Car Control channel only supports: HVAC (temperature, fan, AC, defrost, recirculation, seat heat/vent, steering wheel heat), mirror heat (no fold or adjust), door lock (no child lock, new in 16.2), toll card status, and HMG vendor extensions. No window control, trunk, lights, or other body functions.

> **CarPropertyChangeEvent status values**: 1=AVAILABLE (value is valid), 2=UNAVAILABLE (value is null). When UNAVAILABLE, the HU should grey out or hide the control.

> **Request correlation**: 0x8001/0x8002 use UUID strings for request/response matching. The HU stores UUID->callback mappings in a `ConcurrentHashMap` and matches them when 0x8002 arrives.

> **Control group updates are replacements**: 0x8007 replaces the entire control group matching the given `group_type`. It is not a diff/patch -- the HU must replace its stored group wholesale.

> **Bitmask semantics**: `CarAreaId` repeated enum fields are OR'd on the phone side. Sending `[ROW_1_LEFT, ROW_1_RIGHT]` in `seat_ids` targets both front seats.

> **Proto2 vs proto3 split**: Top-level channel messages (`CarControlMessages.proto`) use proto2 syntax. Sub-messages (`CarPropertyData.proto`, `VehicleAreaEnums.proto`) use proto3 syntax, matching how the APK compiles them.

---

## APK Source References (16.2)

| Class | Role |
|-------|------|
| `hyc` | CAR.GAL.CAR_CONTROL -- channel handler, dispatches inbound messages |
| `hlb` | CAR.CarControlService -- manager, builds outbound messages, caches state |
| `vik` | Message ID enum (`m36843p`/`m36844q` methods) |
| `vyh` | CarControlStatus enum |
| `vul` | CarPropertyId enum (25 properties) |
| `wbq` | SetCarPropertyValueRequest proto (0x8001) |
| `wbr` | SetCarPropertyValueResponse proto (0x8002) |
| `waz` | RegisterCarPropertyListenersRequest proto (0x8003) |
| `wba` | RegisterCarPropertyListenersResponse proto (0x8004) |
| `vwg` | CarPropertyChangeEvent proto (0x8005) |
| `vvv` | CarActionNotification proto (0x8006) |
| `vvz` | CarControlGroupUpdate proto (0x8007) |
| `vuh` | CarProperty proto (property_id + area_id) |
| `vui` | CarAreaId proto (area_type + zone bitmasks) |
| `vup` | CarPropertyValue proto (oneof value) |
| `vtz` | CarAction proto (action_id) |
| `vuj` | CarPropertyConfig proto |
| `vty` | CarPropertyAreaConfig proto (area + min/max) |
| `vuk` | CarPropertyControl proto (property + associated action/property) |
| `vvu` | CarActionControl proto |
| `vvy` | CarControlGroup proto |
| `vvx` | CarControl proto (oneof: property/action/group) |
| `vwa` | CarControlChannelDescriptor proto (SDP) |
| `vua` | CarActionEntry proto |
| `vwh` | SetCarPropertyListenerResult proto |
| `vun` | IntValues proto (repeated int32) |
| `vuo` | LongValues proto (repeated int64) |
| `vum` | FloatValues proto (repeated float) |
| `vud` | VehicleAreaSeat enum |
| `vuf` | VehicleAreaWindow enum |
| `vub` | VehicleAreaDoor enum |
| `vuc` | VehicleAreaMirror enum |
| `vue` | VehicleAreaWheel enum |
