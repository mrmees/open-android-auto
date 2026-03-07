# Navigation Channel Verification Report

**Channel:** Navigation / Instrument Cluster (GAL type 10)
**Endpoint:** `ian.java` (16.2), constructor `super(10, ...)`
**Service:** `hlj.java` (16.2), log tag `CAR.INST`
**Verified:** 2026-03-06
**Status:** COMPLETE

## Ground Truth Message Table

Extracted from `ian.mo18864a()` (receive) and `hlj.*` + `ian.m20073h()` (send):

| Msg ID | Direction | 16.2 Class | Message Name | Confidence | Notes |
|--------|-----------|------------|--------------|------------|-------|
| 0x8001 | HU→Phone | vze | InstrumentClusterStart | Gold | Empty message |
| 0x8002 | HU→Phone | vzf | InstrumentClusterStop | Gold | Empty message |
| 0x8003 | Phone→HU | vzb | NavigationState | Gold | 1 enum field |
| 0x8004 | — | — | *Removed* | — | Existed in 16.1 (vzm), removed in 16.2 |
| 0x8005 | Phone→HU | vyx | LegacyNavigationTurnEvent | Gold | @Deprecated, legacy HUs only (PDK < 1.6) |
| 0x8006 | Phone→HU | vza | NavigationNotification | Gold | Modern replacement for 0x8004/0x8005 |
| 0x8007 | Phone→HU | vyp | NavigationNextTurnDistanceEvent | Gold | Already verified (wire capture) |
| 0x8008 | Phone→HU | waw | VehicleEnergyForecast | Gold | NEW — EV data, PDK >= 5.1 |

## NavigationState (vzb, 0x8003)

| Check | Result | Evidence |
|-------|--------|----------|
| Channel binding | PASS | hlj.mo18763i() → ian.m20106k(32771, vzb) |
| Message ID | PASS | bytecode line 880: `r0 = 32771` |
| Direction | PASS | Phone→HU — hlj builds and sends |
| Field schema | PASS | 1 field: enum, proto2 optional |
| Cross-references | PASS | 7 files, all nav pipeline |
| Enum values | **FIXED** | 0=UNAVAILABLE (was UNKNOWN), 3=REROUTING (was ENDED) |

**Corrections applied:**
- `NAV_STATE_UNKNOWN` → `NAV_STATE_UNAVAILABLE` (log: "Using UNAVAILABLE")
- `NAV_STATE_ENDED` → `NAV_STATE_REROUTING` (log: "Suppressing REROUTING")
- REROUTING suppressed on HUs with CarInfo PDK < 1.6

## NavigationNotification (vza, 0x8006)

| Check | Result | Evidence |
|-------|--------|----------|
| Channel binding | PASS | hlj.mo18762h() → ian.m20106k(32774, vza) |
| Message ID | PASS | line 635: `m20106k(32774, ...)` |
| Direction | PASS | Phone→HU |
| Field schema | PASS | All 8 sub-messages verified field-by-field |
| Cross-references | PASS | 5 files, all nav pipeline |
| Enum values | PASS | LaneShape (0-9) and ManeuverType (0-50) match exactly |

**No schema errors found.** All sub-messages verified:

| Sub-message | 16.2 Class | Fields | Status |
|-------------|------------|--------|--------|
| NavigationStep | vzg | 4 (maneuver, instruction, lanes, road_info) | Gold |
| NavigationManeuver | vyw | 3 (type, exit_number, turn_angle) | Gold |
| NavigationText | vyz | 1 (text) | Gold |
| NavigationLane | vyv | 1 (repeated directions) | Gold |
| NavigationLaneDirection | vyu | 2 (shape, is_recommended) | Gold |
| NavigationRoadInfo | vyo | 1 (repeated road_names) | Gold |
| NavigationDestination | vyq | 2 (address, charging_station) | Gold |
| ChargingStationDetails | vwl | 3 (connector, available, power) | Gold |

## InstrumentCluster Start/Stop (0x8001/0x8002)

| Check | Result | Evidence |
|-------|--------|----------|
| Channel binding | PASS | ian.mo18864a() cases 32769/32770 |
| Message ID | PASS | 0x8001, 0x8002 |
| Direction | **FIXED** | HU→Phone (was incorrectly marked Phone→HU) |
| Field schema | PASS | Both empty messages |
| Syntax | **FIXED** | proto2 (was incorrectly proto3) |

## LegacyNavigationTurnEvent (vyx, 0x8005)

| Check | Result |
|-------|--------|
| Channel binding | PASS — ian.m20073h() sends 32773 |
| Message ID | PASS — 0x8005 (NOT 0x8004) |
| Direction | PASS — Phone→HU |
| Field schema | PASS — 4 int fields + enum |
| Annotation | @Deprecated in APK source |

**CRITICAL DISCOVERY**: Our previous proto had `InstrumentClusterInput (vzl)` at 0x8005. This was **WRONG** — `vzl` is a display overlay parameters proto (`OverlayParameters`), not a wire message on this channel. The actual 0x8005 is `vyx` (legacy turn event).

## NavigationTurnEvent (vzm, 0x8004) — DEPRECATED

- **16.1**: msg ID 0x8004, class vzm (6 fields: road_name, maneuver_type, turn_direction, turn_icon, distance_meters, distance_unit)
- **16.2**: 0x8004 removed. Class name `vzm` reassigned to unrelated overlay parameter (2 fields: int + float). Zero references from nav handler.
- **Replacement**: Modern HUs use NavigationNotification (0x8006) which contains NavigationStep sub-messages with all the same data. Legacy HUs use LegacyNavigationTurnEvent (0x8005, vyx) with simplified 4 fields.

## VehicleEnergyForecast (waw, 0x8008) — NEW

| Check | Result |
|-------|--------|
| Channel binding | PASS — hlj.mo18768o() → ian.m20106k(32776, waw) |
| Message ID | PASS — 0x8008 |
| Direction | PASS — Phone→HU |
| PDK gating | PDK >= 5.1 required |

**Proto structure**: Double-encoded — proto2 wrapper (`waw`, 1 bytes field) containing serialized proto3 inner message (`ysl`, 6 fields).

Inner message fields:
1. `EnergyAtDistance energy_at_next_stop` (ysh: distance_meters, battery_wh, time_seconds)
2. `EnergyAtDistance distance_to_empty`
3. `ForecastQuality forecast_quality` (enum: UNKNOWN=0, LOW=1, HIGH=2)
4. `EnergyChargingStationDetails next_charging_stop` (ysf: min_departure_wh, max_power_watts, charging_time_seconds)
5. `repeated StopDetails stop_details` (ysk: arrival_energy + charging_info)
6. `repeated DataAuthorization data_authorizations` (ysg: id string)

## NavigationFocus — MOVED TO CONTROL CHANNEL

**NavigationFocusRequest and NavigationFocusResponse are NOT on the navigation channel.** They are control channel messages (GAL service type 1, `hzh.java`):

| Msg ID | Direction | 16.2 Class | Message |
|--------|-----------|------------|---------|
| 13 | Phone→HU | vyl | NavigationFocusRequest |
| 14 | HU→Phone | vyk | NavigationFocusResponse |

**Enum**: `vyn` (16.2) — NavigationFocusType (NAV_FOCUS_NATIVE=1, NAV_FOCUS_PROJECTED=2). Previous audit incorrectly said enum was `vzb` — that's NavigationState in 16.2.

### NavigationFocusIndication — RETRACTED

Does not exist. Previous mapping `wbg` (16.1) is actually SensorStatus enum in 16.2 (SENSOR_OK=1, SENSOR_ERROR_TRANSIENT=2, SENSOR_ERROR_PERMANENT=3). No "indication" message exists — the protocol uses only Request (13) + Response (14).

### Bonus: Control Channel Message Table (partial, from hzh.java)

| Msg ID | Direction | 16.2 Class | Message |
|--------|-----------|------------|---------|
| 13 | Phone→HU | vyl | NavigationFocusRequest |
| 14 | HU→Phone | vyk | NavigationFocusResponse |
| 17 | Phone→HU | wcu | VoiceFocusRequest (NEW discovery) |

## Corrections Applied

| Item | Change |
|------|--------|
| NavigationStateType enum | UNKNOWN→UNAVAILABLE, ENDED→REROUTING |
| NavigationState confidence | Silver → Gold |
| NavigationNotification + all sub-msgs | Silver → Gold, 16.2 class refs added |
| LaneShape enum | Silver → Gold |
| InstrumentClusterMessages syntax | proto3 → proto2 |
| InstrumentCluster direction | Phone→HU → HU→Phone |
| InstrumentClusterInput (0x8005) | Retracted — was vzl (overlay), actual is vyx (legacy turn) |
| NavigationTurnEvent (0x8004) | Marked deprecated (16.1 only, removed in 16.2) |
| VehicleEnergyForecast | NEW proto file created |
| NavigationFocusIndication | Retracted — doesn't exist |
| NavigationFocusRequest/Response | Channel corrected: control (type 1), not navigation (type 10) |
| NavigationFocusType enum class | vzb → vyn (16.2) |
