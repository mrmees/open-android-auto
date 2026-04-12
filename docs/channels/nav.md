# Navigation Channel

> **Architecture context:** This channel is part of the Android Auto multiplexed
> protocol. For the overall architecture — framing, SDP binding, capability
> negotiation — see [Channel Architecture Reference](architecture.md).

## Proto Confidence Summary

| Message | Tier | Evidence | Audit File |
|---------|------|----------|------------|
| NavigationTurnEvent | Silver | Deprecated flat turn event; legacy image-bearing `0x8004` / `32772` path remains source-backed in 16.2 | [NavigationTurnEventMessage.audit.yaml](../../oaa/navigation/NavigationTurnEventMessage.audit.yaml) |
| LegacyNavigationTurnEvent | **Gold** | apk_deep_trace (2026-03-06) — NEW | (0x8005, vyx in 16.2) |
| VehicleEnergyForecast | **Gold** | apk_deep_trace (2026-03-06) — NEW | (0x8008, waw wrapper, PDK >= 5.1) |
| NavigationNotification | Gold | apk_static + cross_version + **wire_verified** | [NavigationNotificationMessage.audit.yaml](../../oaa/navigation/NavigationNotificationMessage.audit.yaml) |
| NavigationNextTurnDistanceEvent | Gold | apk_static + cross_version + **wire_verified** | [NavigationTurnEventMessage.audit.yaml](../../oaa/navigation/NavigationTurnEventMessage.audit.yaml) |
| NavigationDistance | Silver | apk_static + cross_version | [NavigationDistanceMessage.audit.yaml](../../oaa/navigation/NavigationDistanceMessage.audit.yaml) |
| NavigationDistanceDisplay | Silver | apk_static + cross_version | [NavigationDistanceDisplayData.audit.yaml](../../oaa/navigation/NavigationDistanceDisplayData.audit.yaml) |
| NavigationState | Gold | apk_static + cross_version + **wire_verified** | [NavigationStateMessage.audit.yaml](../../oaa/navigation/NavigationStateMessage.audit.yaml) |
| NavigationFocusRequest | Silver | apk_static + cross_version | [NavigationFocusRequestMessage.audit.yaml](../../oaa/navigation/NavigationFocusRequestMessage.audit.yaml) |
| NavigationFocusResponse | Silver | apk_static + cross_version | [NavigationFocusResponseMessage.audit.yaml](../../oaa/navigation/NavigationFocusResponseMessage.audit.yaml) |
| ~~NavigationFocusIndication~~ | **Retracted** | wbg=SensorErrorStatus in 16.2, not a focus message | [NavigationFocusIndicationMessage.audit.yaml](../../oaa/navigation/NavigationFocusIndicationMessage.audit.yaml) |
| NavigationChannelConfig | Silver | apk_static + cross_version | [NavigationChannelConfigData.audit.yaml](../../oaa/navigation/NavigationChannelConfigData.audit.yaml) |
| NavigationChannel | Silver | apk_static + cross_version | [NavigationChannelData.audit.yaml](../../oaa/navigation/NavigationChannelData.audit.yaml) |
| NavigationImageOptions | Silver | apk_static + cross_version | [NavigationImageOptionsData.audit.yaml](../../oaa/navigation/NavigationImageOptionsData.audit.yaml) |
| LaneShape (enum) | Silver | apk_static + cross_version | [LaneShapeEnum.audit.yaml](../../oaa/navigation/LaneShapeEnum.audit.yaml) |
| ManeuverType (enum) | Unverified | -- | -- |
| TurnSide (enum) | Unverified | -- | -- |
| NavigationType (enum) | Unverified | -- | -- |
| InstrumentClusterStart | **Gold** | apk_deep_trace (2026-03-06) — direction fixed (HU→Phone) | (0x8001, vze in 16.2) |
| InstrumentClusterStop | **Gold** | apk_deep_trace (2026-03-06) — direction fixed (HU→Phone) | (0x8002, vzf in 16.2) |
| ~~InstrumentClusterInput~~ | **Retracted** | Wrong class — vzl is OverlayParameters, not a wire message | See LegacyNavigationTurnEvent (0x8005) |
| InstrumentClusterAction (enum) | Unverified | -- | -- |

## Overview

Channel 11 (`NAVIGATION_STATUS`) carries turn-by-turn navigation guidance from the phone to the head unit. When a user starts navigation in Google Maps, Waze, or another navigation app on the phone, this channel delivers real-time turn events, distance updates, and navigation state changes so the HU can display guidance without projecting the full map.

**NavigationNotification** is the primary message for modern HUs, carrying rich hierarchical turn-by-turn with multi-step lookahead, lane guidance, and destination/ETA data. **NavigationTurnEvent** (0x8004, deprecated but still source-backed on the legacy `32772` path in 16.2) and **LegacyNavigationTurnEvent** (0x8005) are simplified flat representations for legacy HUs (CarInfo PDK < 1.6).

The navigation channel also carries distance data via **NavigationNextTurnDistanceEvent** (0x8007) and navigation state transitions via **NavigationState** (active/inactive/rerouting). Navigation focus negotiation (NavigationFocusRequest/Response) happens on the **control channel** (msg IDs 13/14), not here.

This is the deepest channel in the protocol: 14 proto files, 31 cross-version mappings, and the richest sub-message hierarchy. See [cross-version mapping table](../cross-version/navigation.md) for version stability across 15.9, 16.1, and 16.2.

---

## Message Catalog

### Turn Guidance

> Confidence: NavigationNotification and NavigationNextTurnDistanceEvent are **Gold** [apk_static, cross_version, wire_verified — 2026-03-04 decrypted capture]; NavigationTurnEvent is Silver; ManeuverType and TurnSide enums are Unverified but values map 1:1 to Android `Maneuver.TYPE_*` constants

| MsgID | Message | Direction | Purpose |
|-------|---------|-----------|---------|
| 0x8004 | NavigationTurnEvent | Phone -> HU | Next turn: maneuver type, road name, distance, optional legacy turn-image bytes |
| 0x8006 | NavigationNotification | Phone -> HU | Rich turn-by-turn with steps, lanes, destinations, ETA |
| 0x8007 | NavigationNextTurnDistanceEvent | Phone -> HU | Distance to next turn with display text and unit |

**NavigationTurnEvent** is the simplified, flat representation:

```protobuf
message NavigationTurnEvent {
    optional string road_name = 1;
    optional ManeuverType.Enum maneuver_type = 2;
    optional TurnSide.Enum turn_direction = 3;
    optional bytes turn_icon = 4;           // legacy turn-image bytes on deprecated native 0x8004 / 32772 path
    optional int32 distance_meters = 5;
    optional int32 distance_unit = 6;       // DistanceDisplayUnit enum
}
```

**NavigationNotification** carries the full hierarchical version with multi-step lookahead. See [Message Hierarchy](#message-hierarchy) below for the nesting relationship.

Source-backed note: native `NavigationNotification` / `32774` remains semantic-only in both 16.1 and 16.2. Separately, fallback JADX over 16.2 `classes.dex` recovered `hlj.mo18767n(...)`, which still builds deprecated `vyy` and sends `NavigationTurnEvent` on `32772` / `0x8004` under the legacy `z(carInfo)` gate. The 16.2 projected models expose `Maneuver.icon`, `Step.lanesImage`, and `RoutingInfo.junctionImage`, but those `CarIcon` assets feed projected UI rendering, not the native nav-wire payload.

### Navigation State

> Confidence: NavigationState is **Gold** [apk_static, cross_version, wire_verified — 2026-03-04]; focus messages are Silver

| MsgID | Message | Direction | Purpose |
|-------|---------|-----------|---------|
| 0x8003 | NavigationState | Phone -> HU | Navigation session active/inactive/rerouting |

> **Note:** NavigationFocusRequest (msg 13) and NavigationFocusResponse (msg 14) are on the **control channel** (GAL type 1, `hzh.java`), NOT on this navigation channel. NavigationFocusIndication has been **retracted** — the class `wbg` is actually `SensorErrorStatus` in 16.2, not a focus indication message.

**NavigationStateType** values:

| Value | Name | Meaning |
|-------|------|---------|
| 0 | UNAVAILABLE | Navigation not available (was UNKNOWN pre-verification) |
| 1 | ACTIVE | Navigation in progress |
| 2 | INACTIVE | Navigation paused or not started |
| 3 | REROUTING | Navigation rerouting (was ENDED pre-verification; suppressed on HUs with CarInfo PDK < 1.6) |

### Channel Configuration

> Confidence: Silver [apk_static, cross_version] -- NavigationChannel, NavigationChannelConfig, NavigationImageOptions all Silver; NavigationType enum Unverified

| Message | Direction | Purpose |
|---------|-----------|---------|
| NavigationChannel | Service Discovery | Channel config: interval, type, proto-defined image option hooks |
| NavigationChannelConfig | Service Discovery | Alt config: interval, type, image dimensions |
| NavigationImageOptions | Service Discovery | Proto-defined turn-image size/depth hints; live 16.2 use remains unproven |

These protos exist in service discovery, but current 16.2 source work did not find a reachable `NEXT_TURN_IMAGE`, `NavigationImageOptions`, or `colour_depth` sender path in the native nav stack. Treat them as proto-defined config surfaces, not proof that modern native nav delivery negotiates live turn-image payloads.

### Instrument Cluster

> Confidence: InstrumentClusterStart and InstrumentClusterStop are **Gold** [apk_deep_trace — 2026-03-06]; ~~InstrumentClusterInput~~ **retracted** (vzl is OverlayParameters, not a wire message)

| MsgID | Message | Direction | Purpose |
|-------|---------|-----------|---------|
| 0x8001 | InstrumentClusterStart | HU -> Phone | Signal cluster display is ready |
| 0x8002 | InstrumentClusterStop | HU -> Phone | Signal cluster session ended |
| 0x8005 | LegacyNavigationTurnEvent | Phone -> HU | Simplified turn data for legacy HUs (PDK < 1.6) |
| 0x8008 | VehicleEnergyForecast | Phone -> HU | EV energy/range forecast (PDK >= 5.1, NEW) |

See [Instrument Cluster](#instrument-cluster-1) section below for details.

### Enums

> Confidence: Unverified (ManeuverType, TurnSide, NavigationType) / Silver (LaneShape)

| Enum | Values | Used In |
|------|--------|---------|
| ManeuverType | 51 values (0-50) | NavigationTurnEvent, NavigationManeuver |
| TurnSide | 3 values (0-2) | NavigationTurnEvent |
| LaneShape | 10 values (0-9) | NavigationLaneDirection |
| NavigationType | 3 values (0-2) | NavigationChannel config |
| DistanceDisplayUnit | 8 values (0-7) | NavigationTurnEvent, LegacyNavigationTurnEvent, NavigationNextTurnDistanceEvent |

See [ManeuverType Reference](#maneuvertype-reference) and [LaneShape Reference](#laneshape-reference) for grouped summaries.

---

## DistanceDisplayUnit Reference

`DistanceDisplayUnit` mirrors the nav `Distance.displayUnit` codes used inside AA before serialization. Values `3` and `5` are precision variants, not separate physical units: they render kilometers or miles with one decimal place.

| Value | Name | Render As | Notes |
|-------|------|-----------|-------|
| 0 | UNKNOWN | -- | Unset / unknown |
| 1 | METERS | `m` | Whole-unit display |
| 2 | KILOMETERS | `km` | Whole-unit display |
| 3 | KILOMETERS_P1 | `km` | One-decimal display variant |
| 4 | MILES | `mi` | Whole-unit display |
| 5 | MILES_P1 | `mi` | One-decimal display variant |
| 6 | FEET | `ft` | Previously mislabeled as unknown in this repo |
| 7 | YARDS | `yd` | Validated by APK-side unit formatter |

Evidence for this mapping comes from the 16.2 APK distance formatters: AndroidX `Distance` defines the constants, Gearhead groups `2/3` as kilometers and `4/5` as miles, and formats only `3` and `5` with one decimal place.

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

**NavigationTurnEvent vs NavigationNotification:** NavigationTurnEvent is the flat legacy representation containing a single turn's maneuver type, road name, distance, and optional image bytes. NavigationNotification carries the same conceptual data in a hierarchical form with multi-step lookahead, lane-level guidance, and destination details including EV charging station information. They share the channel, but they are not a blanket "phone always sends both" pair: 16.1 source shows a gated native `32774` semantic path plus a separate `32772` legacy image-bearing path, while 16.2 keeps the native `32774` path semantic-only and still routes deprecated `32772` / `0x8004` through recovered `mo18767n(...)`; `32773` / `0x8005` remains the separate simplified flat event.

> **Gotcha:** Do not confuse NavigationTurnEvent (flat, 6 fields, ~1Hz) with NavigationNotification (hierarchical, multi-step). A minimal HU implementation can ignore NavigationNotification entirely and render guidance from NavigationTurnEvent alone. The richer hierarchy is for HUs that want lane guidance, multi-step lookahead, and destination details.

---

## State Machine

```
Phone                                    Head Unit
  |                                         |
  |  User starts navigation                 |
  |                                         |
  |  (NavigationFocusRequest on CONTROL ch)  |  Focus negotiation is on control channel
  |  (NavigationFocusResponse on CONTROL ch) |  (msg IDs 13/14), not this channel
  |                                         |
  |--- NavigationState (ACTIVE) --------->  |  Nav session active
  |                                         |
  |--- NavigationNotification ----------->  |  Rich turn-by-turn (periodic)
  |--- NavigationNextTurnDistanceEvent -->  |  Distance to next turn
  |--- NavigationNotification ----------->  |
  |                                         |
  |  User arrives / cancels navigation      |
  |                                         |
  |--- NavigationState (INACTIVE) ------->  |  Nav session ended
  |                                         |
```

The phone drives all state transitions. The HU is a passive receiver of navigation data -- it does not initiate navigation or request specific guidance. The only HU-initiated messages on this channel are InstrumentClusterStart/Stop (0x8001/0x8002). Navigation focus negotiation happens on the control channel (msg IDs 13/14).

---

## Focus Model

> **IMPORTANT:** Navigation focus negotiation happens on the **control channel** (GAL type 1, `hzh.java`), NOT on this navigation channel. NavigationFocusRequest is control msg 13, NavigationFocusResponse is control msg 14.

> ~~NavigationFocusIndication~~ has been **retracted** — the 16.2 class `wbg` is actually `SensorErrorStatus` enum, not a focus indication message. There is no "indication" message in the focus protocol.

Navigation focus tells the HU that a navigation app is active and the HU should display navigation UI (turn cards, distance overlay, etc.). This is separate from audio focus, which is negotiated on channels 4/5/6 for speech/guidance audio.

**NavigationFocusType** values:

| Value | Name | Meaning |
|-------|------|---------|
| 1 | NAV_FOCUS_NATIVE | Focus for native (HU-side) navigation |
| 2 | NAV_FOCUS_PROJECTED | Focus for projected (phone-side) navigation |

The focus flow:

1. Phone sends **NavigationFocusRequest** (control channel msg 13) with `type = NAV_FOCUS_PROJECTED` when a nav app starts
2. HU responds with **NavigationFocusResponse** (control channel msg 14) granting focus
3. Navigation data flows (Notification, Distance, State) on this channel
4. When navigation ends, phone sends **NavigationState (INACTIVE)** on this channel
5. HU can dismiss navigation UI

> **Gotcha:** Navigation focus is NOT audio focus. A navigation app holds nav focus (control channel) and simultaneously requests audio focus on channel 5 (speech audio) for voice prompts. Granting nav focus does not imply granting audio focus or vice versa. The two must be handled independently.

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

> Confidence: **Gold** [apk_deep_trace — 2026-03-06] — InstrumentClusterStart and InstrumentClusterStop verified; ~~InstrumentClusterInput~~ retracted

The instrument cluster is a secondary navigation display, typically behind the steering wheel. These messages manage the cluster session lifecycle, not the navigation data itself -- turn events and state flow through NavigationNotification/NavigationState on the same channel.

**InstrumentClusterStart** (0x8001) and **InstrumentClusterStop** (0x8002) are empty signal messages sent **HU → Phone** -- no payload. On receiving InstrumentClusterStart, the phone begins sending navigation data to the cluster display. The cluster configuration (dimensions, type, interval, and proto-defined image options) is populated from service discovery, not from these messages; current 16.2 source work does not prove that those image-option protos drive live native icon delivery.

**~~InstrumentClusterInput~~ (0x8005) — RETRACTED:** The class previously assigned here (`vzl`) is actually `OverlayParameters` (a display overlay parameters proto), not a wire message on this channel. The actual 0x8005 is **LegacyNavigationTurnEvent** (`vyx`), a simplified turn data message for legacy HUs with CarInfo PDK < 1.6. It is marked `@Deprecated` in the APK source.

**VehicleEnergyForecast** (0x8008, NEW) is sent Phone → HU on this channel for HUs with CarInfo PDK >= 5.1. It uses a proto2 wrapper (`waw`) containing a serialized proto3 inner message (`ysl`) with EV energy/range forecast data including energy-at-distance, charging station details, and forecast quality. See [verification report](../../analysis/reports/proto-verification/navigation.md) for full sub-message hierarchy.

---

## Implementation Guide

### Handling NavigationTurnEvent (~1Hz)

NavigationTurnEvent is the most common navigation message and the minimum viable implementation target. A basic HU needs to:

1. **Extract maneuver type** -- map `ManeuverType.Enum` to a turn icon or text description
2. **Display road name** -- the `road_name` field contains the target road (the road you're turning onto)
3. **Show distance** -- `distance_meters` with `distance_unit` for formatting
4. **Render optional legacy image bytes** -- if `turn_icon` is present on deprecated `0x8004` / `32772`, treat it as a legacy gated path that remains source-backed in 16.2; modern native `32774` delivery is still semantic-only

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

    // Optional 16.1 compatibility path: render legacy turn-image bytes
    if (event->has_turn_icon())
        ui_set_turn_image(event->turn_icon().data(),
                          event->turn_icon().size());
}
```

### Navigation Session Lifecycle

Track `NavigationState` to know when to show/hide navigation UI:

1. Watch for `NavigationFocusRequest` -- show navigation UI frame
2. On `NavigationState(ACTIVE)` -- begin processing navigation notifications
3. On `NavigationState(INACTIVE)` -- clear guidance display, show idle state (note: `REROUTING` (3) means navigation is recalculating, not ended)

---

## Gotchas

> **Gotcha:** `NavigationImageOptionsData` still defines width, height, and `colour_depth_bits`, but current 16.2 source work did not find a reachable `NEXT_TURN_IMAGE` / `NavigationImageOptions` sender path. Treat these fields as unclosed service-discovery metadata, not proven live native icon negotiation.

> **Gotcha:** ManeuverType `UNKNOWN` (0) is the default value. If the phone can't determine the maneuver type, it sends 0. Your icon mapping must handle this case -- don't crash or show a blank on UNKNOWN. A generic "continue" arrow is the standard fallback.

> **Gotcha:** NavigationNextTurnDistanceEvent (0x8007) and NavigationTurnEvent (0x8004) both contain distance information but in different formats. NavigationTurnEvent has a simple `distance_meters` int, while NavigationNextTurnDistanceEvent carries `NavigationRemainingDistance` with display text and a `DistanceDisplayUnit` enum for localized formatting. Use NavigationTurnEvent for basic distance display; use NavigationNextTurnDistanceEvent for pre-formatted distance strings. When rendering units, group `2/3` as kilometers and `4/5` as miles — values `3` and `5` are one-decimal precision variants, not distinct units. **Note:** NavigationDistance (APK class xnb) was previously assigned to 0x8007 but wire capture analysis (2026-03-04) proved this wrong — NavigationDistance's field 1 expects int64, but wire data has a nested submessage matching NavigationNextTurnDistanceEvent. NavigationDistance's actual message ID is unknown; it may not be sent on the nav channel at all.

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
- [Navigation Verification Report](../../analysis/reports/proto-verification/navigation.md) (Gold verification — 2026-03-06)
- [Navigation Cross-Version Mapping](../cross-version/navigation.md) (31 mappings across v15.9, v16.1, v16.2)
- [Channel Map](../channel-map.md) (Channel 11: Navigation Status)
- [Channel Lifecycle](../interactions/04-channel-lifecycle.md) (channel open/close flow)
- [Confidence Tiers](../verification/01-confidence-tiers.md) (tier definitions)
