# Navigation Channel

## Proto Confidence Summary

| Message | Tier | Evidence | Audit File |
|---------|------|----------|------------|
| NavigationTurnEvent | Silver | apk_static + cross_version | [NavigationTurnEventMessage.audit.yaml](../../oaa/navigation/NavigationTurnEventMessage.audit.yaml) |
| NavigationNotification | Gold | apk_static + cross_version + **wire_verified** | [NavigationNotificationMessage.audit.yaml](../../oaa/navigation/NavigationNotificationMessage.audit.yaml) |
| NavigationNextTurnDistanceEvent | Gold | apk_static + cross_version + **wire_verified** | [NavigationTurnEventMessage.audit.yaml](../../oaa/navigation/NavigationTurnEventMessage.audit.yaml) |
| NavigationDistance | Silver | apk_static + cross_version | [NavigationDistanceMessage.audit.yaml](../../oaa/navigation/NavigationDistanceMessage.audit.yaml) |
| NavigationDistanceDisplay | Silver | apk_static + cross_version | [NavigationDistanceDisplayData.audit.yaml](../../oaa/navigation/NavigationDistanceDisplayData.audit.yaml) |
| NavigationState | Gold | apk_static + cross_version + **wire_verified** | [NavigationStateMessage.audit.yaml](../../oaa/navigation/NavigationStateMessage.audit.yaml) |
| NavigationFocusRequest | Silver | apk_static + cross_version | [NavigationFocusRequestMessage.audit.yaml](../../oaa/navigation/NavigationFocusRequestMessage.audit.yaml) |
| NavigationFocusResponse | Silver | apk_static + cross_version | [NavigationFocusResponseMessage.audit.yaml](../../oaa/navigation/NavigationFocusResponseMessage.audit.yaml) |
| NavigationFocusIndication | Silver | apk_static + cross_version | [NavigationFocusIndicationMessage.audit.yaml](../../oaa/navigation/NavigationFocusIndicationMessage.audit.yaml) |
| NavigationChannelConfig | Silver | apk_static + cross_version | [NavigationChannelConfigData.audit.yaml](../../oaa/navigation/NavigationChannelConfigData.audit.yaml) |
| NavigationChannel | Silver | apk_static + cross_version | [NavigationChannelData.audit.yaml](../../oaa/navigation/NavigationChannelData.audit.yaml) |
| NavigationImageOptions | Silver | apk_static + cross_version | [NavigationImageOptionsData.audit.yaml](../../oaa/navigation/NavigationImageOptionsData.audit.yaml) |
| LaneShape (enum) | Silver | apk_static + cross_version | [LaneShapeEnum.audit.yaml](../../oaa/navigation/LaneShapeEnum.audit.yaml) |
| ManeuverType (enum) | Unverified | -- | -- |
| TurnSide (enum) | Unverified | -- | -- |
| NavigationType (enum) | Unverified | -- | -- |
| InstrumentClusterStart | Unverified | -- | -- |
| InstrumentClusterStop | Unverified | -- | -- |
| InstrumentClusterInput | Unverified | -- | -- |
| InstrumentClusterAction (enum) | Unverified | -- | -- |

## Overview

Channel 11 (`NAVIGATION_STATUS`) carries turn-by-turn navigation guidance from the phone to the head unit. When a user starts navigation in Google Maps, Waze, or another navigation app on the phone, this channel delivers real-time turn events, distance updates, and navigation state changes so the HU can display guidance without projecting the full map.

**NavigationTurnEvent** is the primary message, observed firing at ~1Hz during active navigation via DHU 2.1 testing. It contains the next turn's maneuver type, road name, distance, and optionally a turn icon. **NavigationNotification** carries the same information in a richer hierarchical format with multi-step lookahead, lane guidance, and destination/ETA data.

The navigation channel also carries distance data via **NavigationNextTurnDistanceEvent** (0x8007) and navigation state transitions via **NavigationState** (active/inactive/ended). Focus negotiation (**NavigationFocusRequest/Response/Indication**) tells the HU when a navigation app is active, separate from audio focus which is negotiated on the audio channels (4/5/6).

This is the deepest channel in the protocol: 14 proto files, 31 cross-version mappings, and the richest sub-message hierarchy. See [cross-version mapping table](../cross-version/navigation.md) for version stability across 15.9, 16.1, and 16.2.

---

## Message Catalog

### Turn Guidance

> Confidence: NavigationNotification and NavigationNextTurnDistanceEvent are **Gold** [apk_static, cross_version, wire_verified — 2026-03-04 decrypted capture]; NavigationTurnEvent is Silver; ManeuverType and TurnSide enums are Unverified but values map 1:1 to Android `Maneuver.TYPE_*` constants

| MsgID | Message | Direction | Purpose |
|-------|---------|-----------|---------|
| 0x8004 | NavigationTurnEvent | Phone -> HU | Next turn: maneuver type, road name, distance, turn icon |
| 0x8006 | NavigationNotification | Phone -> HU | Rich turn-by-turn with steps, lanes, destinations, ETA |
| 0x8007 | NavigationNextTurnDistanceEvent | Phone -> HU | Distance to next turn with display text and unit |

**NavigationTurnEvent** is the simplified, flat representation:

```protobuf
message NavigationTurnEvent {
    optional string road_name = 1;
    optional ManeuverType.Enum maneuver_type = 2;
    optional TurnSide.Enum turn_direction = 3;
    optional bytes turn_icon = 4;           // PNG image data
    optional int32 distance_meters = 5;
    optional int32 distance_unit = 6;       // DistanceDisplayUnit enum
}
```

**NavigationNotification** carries the full hierarchical version with multi-step lookahead. See [Message Hierarchy](#message-hierarchy) below for the nesting relationship.

### Navigation State

> Confidence: NavigationState is **Gold** [apk_static, cross_version, wire_verified — 2026-03-04]; focus messages are Silver

| MsgID | Message | Direction | Purpose |
|-------|---------|-----------|---------|
| 0x8003 | NavigationState | Phone -> HU | Navigation session active/inactive/ended |
| -- | NavigationFocusRequest | Phone -> HU | Request nav display focus |
| -- | NavigationFocusResponse | HU -> Phone | Grant/deny nav focus |
| -- | NavigationFocusIndication | Phone -> HU | Current focus state indication |

**NavigationStateType** values:

| Value | Name | Meaning |
|-------|------|---------|
| 0 | UNKNOWN | Default/unset |
| 1 | ACTIVE | Navigation in progress |
| 2 | INACTIVE | Navigation paused or not started |
| 3 | ENDED | Navigation session completed |

### Channel Configuration

> Confidence: Silver [apk_static, cross_version] -- NavigationChannel, NavigationChannelConfig, NavigationImageOptions all Silver; NavigationType enum Unverified

| Message | Direction | Purpose |
|---------|-----------|---------|
| NavigationChannel | Service Discovery | Channel config: interval, type, image options |
| NavigationChannelConfig | Service Discovery | Alt config: interval, type, image dimensions |
| NavigationImageOptions | Service Discovery | Turn icon size constraints (width, height, color depth) |

These messages are exchanged during service discovery to configure the navigation channel. `NavigationImageOptions` tells the phone what icon dimensions the HU supports, which affects the `turn_icon` bytes in NavigationTurnEvent.

### Instrument Cluster

> Confidence: Unverified -- no audit sidecars exist for InstrumentCluster messages

| MsgID | Message | Direction | Purpose |
|-------|---------|-----------|---------|
| 0x8001 | InstrumentClusterStart | Phone -> HU | Signal cluster display is ready |
| 0x8002 | InstrumentClusterStop | Phone -> HU | Signal cluster session ended |
| 0x8005 | InstrumentClusterInput | HU -> Phone | D-pad input from cluster controls |

See [Instrument Cluster](#instrument-cluster-1) section below for details.

### Enums

> Confidence: Unverified (ManeuverType, TurnSide, NavigationType) / Silver (LaneShape)

| Enum | Values | Used In |
|------|--------|---------|
| ManeuverType | 51 values (0-50) | NavigationTurnEvent, NavigationManeuver |
| TurnSide | 3 values (0-2) | NavigationTurnEvent |
| LaneShape | 10 values (0-9) | NavigationLaneDirection |
| NavigationType | 3 values (0-2) | NavigationChannel config |
| DistanceDisplayUnit | 7 values (0-6) | NavigationTurnEvent, NavigationNextTurnDistanceEvent |

See [ManeuverType Reference](#maneuvertype-reference) and [LaneShape Reference](#laneshape-reference) for grouped summaries.

---

## Message Hierarchy

Navigation has the deepest sub-message nesting in the protocol. Understanding this hierarchy is essential for parsing NavigationNotification correctly.

```
NavigationNotification
  |-- steps: repeated NavigationStep
  |     |-- maneuver: NavigationManeuver
  |     |     |-- type: ManeuverType.Enum (51 values)
  |     |     |-- roundabout_exit_number: int32
  |     |     |-- roundabout_turn_angle: int32
  |     |-- instruction: NavigationText
  |     |     |-- text: string
  |     |-- lanes: repeated NavigationLane
  |     |     |-- directions: repeated NavigationLaneDirection
  |     |           |-- shape: LaneShape.Enum (10 values)
  |     |           |-- is_recommended: bool
  |     |-- road_info: NavigationRoadInfo
  |           |-- road_names: repeated string
  |-- destinations: repeated NavigationDestination
        |-- address: string
        |-- charging_station: ChargingStationDetails
              |-- connector_count: int32
              |-- available_count: int32
              |-- max_power_kw: int32
```

**NavigationTurnEvent vs NavigationNotification:** NavigationTurnEvent is the flat, simplified representation containing a single turn's maneuver type, road name, distance, and icon. NavigationNotification carries the same conceptual data in a hierarchical form with multi-step lookahead, lane-level guidance, and destination details including EV charging station information. Both messages are sent on the same channel -- the phone sends both, and the HU can use whichever level of detail it supports.

> **Gotcha:** Do not confuse NavigationTurnEvent (flat, 6 fields, ~1Hz) with NavigationNotification (hierarchical, multi-step). A minimal HU implementation can ignore NavigationNotification entirely and render guidance from NavigationTurnEvent alone. The richer hierarchy is for HUs that want lane guidance, multi-step lookahead, and destination details.

---

## State Machine

```
Phone                                    Head Unit
  |                                         |
  |  User starts navigation                 |
  |                                         |
  |--- NavigationFocusRequest ----------->  |  Request nav display focus
  |<-- NavigationFocusResponse -----------  |  HU grants focus
  |                                         |
  |--- NavigationState (ACTIVE) --------->  |  Nav session active
  |                                         |
  |--- NavigationTurnEvent -------------->  |  ~1Hz turn guidance
  |--- NavigationTurnEvent -------------->  |
  |--- NavigationNextTurnDistanceEvent -->  |  Distance to next turn
  |--- NavigationNotification ----------->  |  Rich turn-by-turn (periodic)
  |--- NavigationTurnEvent -------------->  |
  |                                         |
  |  User arrives / cancels navigation      |
  |                                         |
  |--- NavigationState (ENDED) ---------->  |  Nav session ended
  |--- NavigationFocusIndication -------->  |  Focus released
  |                                         |
```

The phone drives all state transitions. The HU is a passive receiver of navigation data -- it does not initiate navigation or request specific guidance. The only HU-initiated message is NavigationFocusResponse (granting or denying focus) and InstrumentClusterInput (d-pad events).

---

## Focus Model

> Confidence: Silver [apk_static, cross_version] -- NavigationFocusRequest, Response, and Indication all Silver

Navigation focus tells the HU that a navigation app is active and the HU should display navigation UI (turn cards, distance overlay, etc.). This is separate from audio focus, which is negotiated on channels 4/5/6 for speech/guidance audio.

**NavigationFocusType** values:

| Value | Name | Meaning |
|-------|------|---------|
| 1 | NAV_FOCUS_NATIVE | Focus for native (HU-side) navigation |
| 2 | NAV_FOCUS_PROJECTED | Focus for projected (phone-side) navigation |

The focus flow:

1. Phone sends **NavigationFocusRequest** with `type = NAV_FOCUS_PROJECTED` when a nav app starts
2. HU responds with **NavigationFocusResponse** granting focus
3. Navigation data flows (TurnEvent, Distance, Notification, State)
4. When navigation ends, phone sends **NavigationFocusIndication** with updated state
5. HU can dismiss navigation UI

**NavigationFocusIndication** carries an opaque `focus_data` bytes field. The exact encoding is not documented beyond the proto structure -- it may contain serialized state or metadata about the current focus holder.

> **Gotcha:** Navigation focus is NOT audio focus. A navigation app holds nav focus on channel 11 and simultaneously requests audio focus on channel 5 (speech audio) for voice prompts. Granting nav focus does not imply granting audio focus or vice versa. The two must be handled independently.

---

## ManeuverType Reference

> Confidence: Unverified -- ManeuverType has no audit sidecar, but values map 1:1 to Android `Maneuver.TYPE_*` constants which are well-documented

ManeuverType has 51 values (0-50). Rather than listing all values, here they are grouped by category. See [ManeuverTypeEnum.proto](../../oaa/navigation/ManeuverTypeEnum.proto) for the complete list.

**Turns (values 5-12):**
`TURN_SLIGHT_LEFT/RIGHT`, `TURN_NORMAL_LEFT/RIGHT`, `TURN_SHARP_LEFT/RIGHT`, `U_TURN_LEFT/RIGHT`

**On-Ramps (values 13-20):**
`ON_RAMP_SLIGHT_LEFT/RIGHT`, `ON_RAMP_NORMAL_LEFT/RIGHT`, `ON_RAMP_SHARP_LEFT/RIGHT`, `ON_RAMP_U_TURN_LEFT/RIGHT`

**Off-Ramps (values 21-24):**
`OFF_RAMP_SLIGHT_LEFT/RIGHT`, `OFF_RAMP_NORMAL_LEFT/RIGHT`

**Merge/Fork (values 25-29):**
`FORK_LEFT/RIGHT`, `MERGE_LEFT/RIGHT`, `MERGE_SIDE_UNSPECIFIED`

**Roundabouts (values 32-35, 43-46):**
`ROUNDABOUT_ENTER_AND_EXIT_CW/CCW` (with and without angle), `ROUNDABOUT_ENTER_CW/CCW`, `ROUNDABOUT_EXIT_CW/CCW`

**Ferry (values 37-38, 47-50):**
`FERRY_BOAT`, `FERRY_TRAIN`, `FERRY_BOAT_LEFT/RIGHT`, `FERRY_TRAIN_LEFT/RIGHT`

**Destination (values 39-42):**
`DESTINATION`, `DESTINATION_STRAIGHT`, `DESTINATION_LEFT`, `DESTINATION_RIGHT`

**Other (values 0-4, 36):**
`UNKNOWN` (0), `DEPART` (1), `NAME_CHANGE` (2), `KEEP_LEFT` (3), `KEEP_RIGHT` (4), `STRAIGHT` (36)

Note: values 30-31 are not defined in the enum (gap between MERGE and ROUNDABOUT groups).

---

## LaneShape Reference

> Confidence: Silver [apk_static, cross_version] -- LaneShape has an audit sidecar

LaneShape has 10 values used in NavigationLaneDirection to indicate what directions a lane supports. See [LaneShapeEnum.proto](../../oaa/navigation/LaneShapeEnum.proto).

| Value | Name | Description |
|-------|------|-------------|
| 0 | UNKNOWN | Default/unset |
| 1 | STRAIGHT | Lane goes straight |
| 2 | SLIGHT_LEFT | Slight left curve |
| 3 | SLIGHT_RIGHT | Slight right curve |
| 4 | NORMAL_LEFT | Standard left turn |
| 5 | NORMAL_RIGHT | Standard right turn |
| 6 | SHARP_LEFT | Sharp left turn |
| 7 | SHARP_RIGHT | Sharp right turn |
| 8 | U_TURN_LEFT | U-turn to the left |
| 9 | U_TURN_RIGHT | U-turn to the right |

Each lane can have multiple LaneDirection entries (e.g., a lane that allows both straight and right turn). The `is_recommended` field indicates which direction the navigation is suggesting for the current maneuver.

---

## Worked Example: Live Navigation Data

From DHU 2.1 kitchen sink capture during Google Maps navigation (2026-02-28):

| Field | Observed Value | Notes |
|-------|---------------|-------|
| road_name | "Interstate 5 N" | Current road segment |
| maneuver_type | `TURN_NORMAL_RIGHT` (8) | Next maneuver |
| turn_direction | `RIGHT` (2) | TurnSide enum |
| distance_meters | 450 | Distance to next turn |

> Confidence: Silver [apk_static, cross_version] -- proto field structure verified; DHU values are illustrative, not normative

The DHU cluster display also showed structured navigation data:

| Data | Description |
|------|-------------|
| Maneuver icon | Visual turn indicator matching maneuver_type |
| Road name | Current and next road names |
| Distance + unit | "450 m" or "0.3 mi" depending on locale |
| Step distance + time | Remaining time to next step |
| Destination | Final destination address and ETA |

These observations confirm that NavigationTurnEvent fires at approximately 1Hz during active navigation and that the phone populates all six fields with meaningful data.

> **Gotcha:** NavigationTurnEvent observed at ~1Hz in DHU testing, but this rate is not guaranteed. The `minimum_interval_ms` field in NavigationChannel/NavigationChannelConfig (service discovery) configures the minimum update interval. An HU that sets a high interval may receive updates less frequently. The phone controls the actual rate within the negotiated bounds.

---

## Instrument Cluster

> Confidence: Unverified -- InstrumentClusterMessages.proto has no audit sidecar. Structural information derived from APK analysis only.

The instrument cluster is a secondary navigation display, typically behind the steering wheel. These messages manage the cluster session lifecycle, not the navigation data itself -- turn events and state flow through NavigationTurnEvent/NavigationState/NavigationNotification on the same channel.

**InstrumentClusterStart** (0x8001) and **InstrumentClusterStop** (0x8002) are empty signal messages -- no payload. On receiving InstrumentClusterStart, the HU reads cached cluster configuration (populated from service discovery) containing:

- `min_interval` -- minimum update interval
- `cluster_type` -- display type
- `width`, `height` -- cluster display dimensions
- `color_depth` -- bits per pixel

**InstrumentClusterInput** (0x8005) carries user input from steering wheel controls to the phone:

```protobuf
message InstrumentClusterInput {
    optional int32 input_source = 1;
    optional int32 key_code = 2;
    optional int32 key_action = 3;
    optional InstrumentClusterAction action_type = 4;  // 0-7 d-pad values
}
```

> **Gotcha:** The InstrumentClusterAction enum (values 0-7) is the same d-pad navigation model used by PhoneStatusInput on the phone channel (channel 12). Both use handler log tag `CAR.GAL.INST`. This strongly suggests shared input infrastructure between the instrument cluster and phone status displays. See [phone.md](phone.md) for the phone-side equivalent.

> **Gotcha:** The APK applies a 1-based to 0-based conversion on the action_type: `vzl.f = i4 - 1`. If your HU generates 1-based action values (1-8), the phone expects them stored as 0-based (0-7) in the proto. If you send raw button codes without this offset, the phone will interpret UP as UNKNOWN.

---

## Implementation Guide

### Handling NavigationTurnEvent (~1Hz)

NavigationTurnEvent is the most common navigation message and the minimum viable implementation target. A basic HU needs to:

1. **Extract maneuver type** -- map `ManeuverType.Enum` to a turn icon or text description
2. **Display road name** -- the `road_name` field contains the target road (the road you're turning onto)
3. **Show distance** -- `distance_meters` with `distance_unit` for formatting
4. **Render turn icon** -- if `turn_icon` (bytes) is present, decode as PNG image. Size is constrained by `NavigationImageOptions` negotiated during service discovery

```c
// Minimal NavigationTurnEvent handler
void handle_turn_event(const NavigationTurnEvent* event) {
    // Update turn card UI
    if (event->has_road_name())
        ui_set_road_name(event->road_name());

    if (event->has_maneuver_type())
        ui_set_turn_icon(maneuver_to_icon(event->maneuver_type()));

    if (event->has_distance_meters()) {
        const char* unit = format_distance_unit(event->distance_unit());
        ui_set_distance(event->distance_meters(), unit);
    }

    // Optional: render phone-provided turn icon
    if (event->has_turn_icon())
        ui_set_turn_image(event->turn_icon().data(),
                          event->turn_icon().size());
}
```

### Navigation Session Lifecycle

Track `NavigationState` to know when to show/hide navigation UI:

1. Watch for `NavigationFocusRequest` -- show navigation UI frame
2. On `NavigationState(ACTIVE)` -- begin processing turn events
3. On `NavigationState(ENDED)` -- clear guidance display, show idle state
4. On `NavigationFocusIndication` -- hide navigation UI frame

---

## Gotchas

> **Gotcha:** NavigationImageOptionsData specifies width, height, and colour_depth_bits for turn icons. If you don't report these in service discovery, the phone may send icons at a default size that doesn't match your display. Always populate NavigationImageOptions in your service discovery response.

> **Gotcha:** ManeuverType `UNKNOWN` (0) is the default value. If the phone can't determine the maneuver type, it sends 0. Your icon mapping must handle this case -- don't crash or show a blank on UNKNOWN. A generic "continue" arrow is the standard fallback.

> **Gotcha:** NavigationNextTurnDistanceEvent (0x8007) and NavigationTurnEvent (0x8004) both contain distance information but in different formats. NavigationTurnEvent has a simple `distance_meters` int, while NavigationNextTurnDistanceEvent carries `NavigationRemainingDistance` with display text and a `DistanceDisplayUnit` enum for localized formatting. Use NavigationTurnEvent for basic distance display; use NavigationNextTurnDistanceEvent for pre-formatted distance strings. **Note:** NavigationDistance (APK class xnb) was previously assigned to 0x8007 but wire capture analysis (2026-03-04) proved this wrong — NavigationDistance's field 1 expects int64, but wire data has a nested submessage matching NavigationNextTurnDistanceEvent. NavigationDistance's actual message ID is unknown; it may not be sent on the nav channel at all.

---

## References

### Proto Files
- [NavigationTurnEventMessage.proto](../../oaa/navigation/NavigationTurnEventMessage.proto)
- [NavigationNotificationMessage.proto](../../oaa/navigation/NavigationNotificationMessage.proto)
- [NavigationDistanceMessage.proto](../../oaa/navigation/NavigationDistanceMessage.proto)
- [NavigationDistanceDisplayData.proto](../../oaa/navigation/NavigationDistanceDisplayData.proto)
- [NavigationStateMessage.proto](../../oaa/navigation/NavigationStateMessage.proto)
- [NavigationFocusRequestMessage.proto](../../oaa/navigation/NavigationFocusRequestMessage.proto)
- [NavigationFocusResponseMessage.proto](../../oaa/navigation/NavigationFocusResponseMessage.proto)
- [NavigationFocusIndicationMessage.proto](../../oaa/navigation/NavigationFocusIndicationMessage.proto)
- [NavigationChannelConfigData.proto](../../oaa/navigation/NavigationChannelConfigData.proto)
- [NavigationChannelData.proto](../../oaa/navigation/NavigationChannelData.proto)
- [NavigationImageOptionsData.proto](../../oaa/navigation/NavigationImageOptionsData.proto)
- [ManeuverTypeEnum.proto](../../oaa/navigation/ManeuverTypeEnum.proto)
- [LaneShapeEnum.proto](../../oaa/navigation/LaneShapeEnum.proto)
- [TurnSideEnum.proto](../../oaa/navigation/TurnSideEnum.proto)
- [NavigationTypeEnum.proto](../../oaa/navigation/NavigationTypeEnum.proto)
- [InstrumentClusterMessages.proto](../../oaa/navigation/InstrumentClusterMessages.proto)

### Audit Sidecars
- [NavigationTurnEventMessage.audit.yaml](../../oaa/navigation/NavigationTurnEventMessage.audit.yaml)
- [NavigationNotificationMessage.audit.yaml](../../oaa/navigation/NavigationNotificationMessage.audit.yaml)
- [NavigationDistanceMessage.audit.yaml](../../oaa/navigation/NavigationDistanceMessage.audit.yaml)
- [NavigationDistanceDisplayData.audit.yaml](../../oaa/navigation/NavigationDistanceDisplayData.audit.yaml)
- [NavigationStateMessage.audit.yaml](../../oaa/navigation/NavigationStateMessage.audit.yaml)
- [NavigationFocusRequestMessage.audit.yaml](../../oaa/navigation/NavigationFocusRequestMessage.audit.yaml)
- [NavigationFocusResponseMessage.audit.yaml](../../oaa/navigation/NavigationFocusResponseMessage.audit.yaml)
- [NavigationFocusIndicationMessage.audit.yaml](../../oaa/navigation/NavigationFocusIndicationMessage.audit.yaml)
- [NavigationChannelConfigData.audit.yaml](../../oaa/navigation/NavigationChannelConfigData.audit.yaml)
- [NavigationChannelData.audit.yaml](../../oaa/navigation/NavigationChannelData.audit.yaml)
- [NavigationImageOptionsData.audit.yaml](../../oaa/navigation/NavigationImageOptionsData.audit.yaml)
- [LaneShapeEnum.audit.yaml](../../oaa/navigation/LaneShapeEnum.audit.yaml)

### Cross-References
- [Navigation Cross-Version Mapping](../cross-version/navigation.md) (31 mappings across v15.9, v16.1, v16.2)
- [Channel Map](../channel-map.md) (Channel 11: Navigation Status)
- [Channel Lifecycle](../interactions/04-channel-lifecycle.md) (channel open/close flow)
- [Confidence Tiers](../verification/01-confidence-tiers.md) (tier definitions)
