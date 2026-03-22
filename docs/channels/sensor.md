# Sensor Channel (7)

## Proto Confidence Summary

| Message | Tier | Evidence | Audit File |
|---------|------|----------|------------|
| SensorRequest | **Gold** | deep_trace (ibi.java handler, wbh) | [SensorRequestMessage.audit.yaml](../../oaa/sensor/SensorRequestMessage.audit.yaml) |
| SensorStartResponse | **Gold** | deep_trace (ibi.java, vyh status) | [SensorStartResponseMessage.audit.yaml](../../oaa/sensor/SensorStartResponseMessage.audit.yaml) |
| SensorEventIndication | **Gold** | deep_trace (ibi.java + wbe zzq descriptor, 26 fields) | [SensorEventIndicationMessage.audit.yaml](../../oaa/sensor/SensorEventIndicationMessage.audit.yaml) |
| SensorError | **Gold** | deep_trace (ibi.java, wbf + wbg enum) | [SensorErrorMessage.audit.yaml](../../oaa/sensor/SensorErrorMessage.audit.yaml) |
| SensorType (enum) | **Gold** | deep_trace (wbl.java + ibi.java dispatch) | [SensorTypeEnum.audit.yaml](../../oaa/sensor/SensorTypeEnum.audit.yaml) |
| SensorErrorStatus (enum) | **Gold** | deep_trace (wbg.java) | [SensorErrorStatusEnum.audit.yaml](../../oaa/sensor/SensorErrorStatusEnum.audit.yaml) |
| Gear (enum) | **Gold** | deep_trace (vxb closed enum, 14 values) | [GearEnum.audit.yaml](../../oaa/sensor/GearEnum.audit.yaml) |
| FuelType (enum) | Silver | apk_static + cross_version | [FuelTypeEnum.audit.yaml](../../oaa/sensor/FuelTypeEnum.audit.yaml) |
| EVConnectorType (enum) | Silver | apk_static + cross_version | [EVConnectorTypeEnum.audit.yaml](../../oaa/sensor/EVConnectorTypeEnum.audit.yaml) |
| DrivingStatus (enum) | Gold | bitmask flags, well-established | [DrivingStatusEnum.audit.yaml](../../oaa/sensor/DrivingStatusEnum.audit.yaml) |
| HeadlightStatus (enum) | Silver | placeholder (0-3), no named APK class | [HeadlightStatusEnum.audit.yaml](../../oaa/sensor/HeadlightStatusEnum.audit.yaml) |
| IndicatorStatus (enum) | Silver | placeholder (0-3), no named APK class | [IndicatorStatusEnum.audit.yaml](../../oaa/sensor/IndicatorStatusEnum.audit.yaml) |
| All 26 sensor data sub-messages | **Gold** | deep_trace (16.2 DB + handler) | Individual .audit.yaml files in oaa/sensor/ |
| SensorChannelConfig (SDP) | **Gold** | deep_trace (wbk, 4 fields) | [SensorChannelConfigData.audit.yaml](../../oaa/sensor/SensorChannelConfigData.audit.yaml) |
| SensorTypeEntry (SDP) | **Gold** | deep_trace (wbj, 1 field) | [SensorChannelConfigData.audit.yaml](../../oaa/sensor/SensorChannelConfigData.audit.yaml) |
| ~~SensorStartRequest~~ | **Retracted** | Duplicate of SensorRequest with wrong field modifiers | [SensorStartRequestMessage.audit.yaml](../../oaa/sensor/SensorStartRequestMessage.audit.yaml) |

**Totals:** 36 Gold, 1 retraction.

---

## Overview

> Confidence: Gold [deep_trace, 16.2 handler ibi.java fully traced]

The sensor channel delivers vehicle and environmental data from the head unit to the phone. It carries everything Android Auto needs to know about the physical world: GPS position, vehicle speed, gear state, driving restrictions, ambient light, tire pressures, and more.

| Property | Value |
|----------|-------|
| Channel ID | 7 |
| GAL Type | 7 |
| Handler Class | `ibi.java` (16.2), extends `iav` |
| Log Tag | `CAR.SENSOR.LITE`, `CAR.SENSOR` |
| Msg ID Offset | None -- raw wire IDs used directly |
| Wire Messages | 4 (0x8001-0x8004) |
| Sensor Types | 26 |
| Direction | Phone subscribes; HU supplies sensor data |

The protocol is subscription-based. The phone sends a `SensorRequest` for each sensor type it wants, specifying a refresh interval. The HU acknowledges with `SensorStartResponse`, then delivers periodic `SensorEventIndication` messages containing the requested data. If a sensor is unavailable or fails, the HU sends `SensorError` instead.

This direction is supported by the phone-side sensor endpoint (`qnz.java` / `ibi.java`) issuing `sendSensorRequest(...)` and handling `SensorStartResponse`, `SensorEventIndication`, and `SensorError` as inbound messages. DHU injection evidence also shows HU-provided `LOCATION` moves Maps on the phone.

All 26 sensor types share the same wire protocol -- the sensor type is identified by which field is populated in `SensorEventIndication`, where field numbers correspond directly to `SensorType` enum values (field 1 = LOCATION, field 2 = COMPASS, etc.).

---

## Message Catalog

> Confidence: Gold [deep_trace, 16.2 handler ibi.java constants verified]

| Msg ID | Message | Direction | Purpose | Confidence |
|--------|---------|-----------|---------|:---:|
| 0x8001 | SensorRequest | Phone -> HU | Subscribe to a sensor at a given refresh interval | **Gold** |
| 0x8002 | SensorStartResponse | HU -> Phone | Acknowledge sensor subscription (status) | **Gold** |
| 0x8003 | SensorEventIndication | HU -> Phone | Deliver sensor data (one or more sensor types per message) | **Gold** |
| 0x8004 | SensorError | HU -> Phone | Report sensor failure or unavailability | **Gold** |

### SensorRequest (0x8001, Phone -> HU)

The phone sends one request per sensor type it wants to subscribe to. Sent after channel setup during session initialization.

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | enum SensorType | required | Which sensor to subscribe to |
| 2 | int64 | required | Refresh interval in milliseconds |

### SensorStartResponse (0x8002, HU -> Phone)

Acknowledgment from the HU indicating whether the requested sensor subscription was accepted.

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | enum Status (ProtocolStatus) | required | Shared 34-value status enum (vyh) |

The status field uses the shared `ProtocolStatus` enum (`vyh`), the same enum used across bluetooth, radio, and other channels. For sensor responses, the relevant values are typically OK or the appropriate error code.

### SensorEventIndication (0x8003, HU -> Phone)

The main data-carrying message. Contains 26 repeated message fields, one per sensor type. Field numbers map directly to `SensorType` enum values. Each field is `repeated` to allow batching multiple readings in a single message.

A single `SensorEventIndication` can carry data for multiple sensor types simultaneously -- the HU may bundle readings that share the same polling cycle.

### SensorError (0x8004, HU -> Phone)

Sent by the HU when a sensor request fails or a previously-working sensor becomes unavailable.

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | enum SensorType | required | Which sensor errored |
| 2 | enum SensorErrorStatus | required | Error severity |

**SensorErrorStatus values:**

| Value | Name | Meaning |
|:---:|------|---------|
| 1 | SENSOR_OK | Sensor recovered (error cleared) |
| 2 | SENSOR_ERROR_TRANSIENT | Temporary failure -- may recover |
| 3 | SENSOR_ERROR_PERMANENT | Sensor permanently unavailable |

---

## SensorType Enum

> Confidence: Gold [deep_trace, wbl.java + ibi.java handler dispatch, all 26 values confirmed]

| Value | Name | Data Proto | Key Fields | Category |
|:---:|------|-----------|------------|----------|
| 1 | LOCATION | GPSLocation | lat, lon, accuracy, altitude, speed, bearing | Location |
| 2 | COMPASS | Compass | bearing, pitch, roll | Location |
| 3 | CAR_SPEED | Speed | speed, cruise_engaged | Vehicle Dynamics |
| 4 | RPM | RPM | rpm | Vehicle Dynamics |
| 5 | ODOMETER | Odometer | total_mileage, trip_mileage | Vehicle State |
| 6 | FUEL_LEVEL | FuelLevel | fuel_level, range, low_fuel | Energy |
| 7 | PARKING_BRAKE | ParkingBrake | parking_brake (bool) | Vehicle State |
| 8 | GEAR | Gear | gear (enum, 14 values) | Vehicle Dynamics |
| 9 | DIAGNOSTICS | Diagnostics | diagnostics (bytes) | Vehicle State |
| 10 | NIGHT_DATA | NightMode | is_night (bool) | Environment |
| 11 | ENVIRONMENT | Environment | temperature, pressure, rain | Environment |
| 12 | HVAC | HVAC | target_temperature, current_temperature | Environment |
| 13 | DRIVING_STATUS | DrivingStatus | status (bitmask) | Driver |
| 14 | DEAD_RECONING | SteeringWheel | steering_angle, wheel_speed[] | Vehicle Dynamics |
| 15 | PASSENGER | Passenger | passenger_present (bool) | Driver |
| 16 | DOOR | Door | hood_open, boot_open, door_open[] | Vehicle State |
| 17 | LIGHT | Light | headlight, indicator, hazard_light_on | Vehicle State |
| 18 | TIRE | TirePressure | tire_pressures[] | Vehicle State |
| 19 | ACCEL | Accel | acceleration_x/y/z | Vehicle Dynamics |
| 20 | GYRO | Gyro | rotation_speed_x/y/z | Vehicle Dynamics |
| 21 | GPS | GpsSatelliteData | satellite_count, satellites_used, satellites[] | Location |
| 22 | TOLL_CARD | TollCardData | toll_card_present (bool) | Vehicle State |
| 23 | VEHICLE_ENERGY_MODEL | VehicleEnergyModelData | (empty message) | Energy/EV |
| 24 | TRAILER | TrailerData | (empty message) | Vehicle State |
| 25 | RAW_VEHICLE_ENERGY_MODEL | RawVehicleEnergyModel | raw_data (bytes) | Energy/EV |
| 26 | RAW_EV_TRIP_SETTINGS | RawEvTripSettings | raw_data (bytes) | Energy/EV |

---

## Sensor Data Sub-Messages

All 26 sub-messages are Gold confidence (deep_trace, 16.2 DB verified). Grouped by functional category.

### Location (Types 1, 2, 21)

**GPSLocation** (type 1, `vxx`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 2 | int32 | required | Latitude (microdegrees) |
| 3 | int32 | required | Longitude (microdegrees) |
| 4 | uint32 | optional | Accuracy |
| 5 | int32 | optional | Altitude |
| 6 | int32 | optional | Speed |
| 7 | int32 | optional | Bearing |

Note: no field 1 (timestamp) exists in the APK. Field numbering starts at 2.

**Compass** (type 2, `vwm`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | required | Bearing |
| 2 | int32 | optional | Pitch |
| 3 | int32 | optional | Roll |

**GpsSatelliteData** (type 21, `vxe`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | required | Total satellite count |
| 2 | int32 | optional | Satellites used in fix |
| 3 | repeated GpsSatelliteInfo | -- | Per-satellite details |

**GpsSatelliteInfo** sub-message (`vxd`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | required | PRN (satellite ID) |
| 2 | int32 | required | SNR (signal-to-noise ratio) |
| 3 | bool | required | In use (contributing to fix) |
| 4 | int32 | optional | Azimuth (degrees) |
| 5 | int32 | optional | Elevation (degrees) |

### Vehicle Dynamics (Types 3, 4, 8, 14, 19, 20)

**Speed** (type 3, `wbt`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | required | Speed |
| 2 | bool | optional | Cruise control engaged |
| 4 | int32 | optional | Unknown (no field 3) |

**RPM** (type 4, `wbd`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | required | Engine RPM |

**Gear** (type 8, `vxb`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | enum Gear | required | Current gear (closed enum) |

Gear enum values (14 total):

| Value | Name | Value | Name |
|:---:|------|:---:|------|
| 0 | NEUTRAL | 7 | SEVENTH |
| 1 | FIRST | 8 | EIGHTH |
| 2 | SECOND | 9 | NINTH |
| 3 | THIRD | 10 | TENTH |
| 4 | FOURTH | 100 | DRIVE |
| 5 | FIFTH | 101 | PARK |
| 6 | SIXTH | 102 | REVERSE |

**SteeringWheel** (type 14, `vwq`) -- dead reckoning:

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | optional | Steering angle |
| 2 | repeated int32 | -- | Wheel speed ticks (per wheel) |

**Accel** (type 19, `vuv`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | optional | Acceleration X |
| 2 | int32 | optional | Acceleration Y |
| 3 | int32 | optional | Acceleration Z |

**Gyro** (type 20, `vxf`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | optional | Rotation speed X |
| 2 | int32 | optional | Rotation speed Y |
| 3 | int32 | optional | Rotation speed Z |

### Vehicle State (Types 5, 7, 9, 16, 17, 18, 22, 24)

**Odometer** (type 5, `vzj`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | required | Total mileage |
| 2 | int32 | optional | Trip mileage |

**ParkingBrake** (type 7, `vzn`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | bool | required | Parking brake engaged |

**Diagnostics** (type 9, `vwr`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | bytes | optional | Opaque diagnostics blob |

**Door** (type 16, `vwt`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | bool | optional | Hood open |
| 2 | bool | optional | Boot/trunk open |
| 3 | repeated bool | -- | Individual door states |

**Light** (type 17, `vxw`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | enum HeadlightStatus | optional | Headlight state (0-3) |
| 2 | enum IndicatorStatus | optional | Turn signal state (0-3) |
| 3 | bool | optional | Hazard lights on |

HeadlightStatus and IndicatorStatus are placeholder enums (Silver) with values 0-3 but no named constants in the APK. Fields 2 and 3 default to 1 in the APK, which may mean default=ON.

**TirePressure** (type 18, `wbw`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | repeated int32 | -- | Per-tire pressures |

**TollCardData** (type 22, `wbx`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | bool | required | Toll card present |

**TrailerData** (type 24, `wca`):

Empty message (0 fields). Trailer presence may be indicated by the message's existence alone.

### Energy / EV (Types 6, 23, 25, 26)

**FuelLevel** (type 6, `vwz`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | optional | Fuel level |
| 2 | int32 | optional | Range |
| 3 | bool | optional | Low fuel warning |

**VehicleEnergyModelData** (type 23, `vus`):

Empty message (0 fields). Structured energy model -- fields TBD from wire captures.

**RawVehicleEnergyModel** (type 25, `wax`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | bytes | optional | Opaque raw energy model data |

**RawEvTripSettings** (type 26, `wav`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | bytes | optional | Opaque raw EV trip settings data |

### Driver / Environment (Types 10, 11, 12, 13, 15)

**NightMode** (type 10, `vzi`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | bool | optional | Is night mode active |

Fully verified via DHU 2.1 injection: triggers `CAR.SENSOR` -> `CAR.SYS` (night mode) -> `CAR.WM` (video config update) pipeline.

**Environment** (type 11, `vww`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | optional | Temperature |
| 2 | int32 | optional | Barometric pressure |
| 3 | int32 | optional | Rain |

**HVAC** (type 12, `vxh`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | optional | Target temperature |
| 2 | int32 | optional | Current temperature |

Note: HVAC sensor data (type 12) is legacy. In newer AA versions, detailed HVAC control and status uses the [Car Control channel (service 19)](./car-control.md) with VHAL property IDs.

**DrivingStatus** (type 13, `vwv`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | int32 | required | Status bitmask |

DrivingStatus is a bitmask, not a single enum value. Flags are OR'd together:

| Value | Flag | Effect |
|:---:|------|--------|
| 0 | UNRESTRICTED | No driving restrictions |
| 1 | NO_VIDEO | Video playback blocked |
| 2 | NO_KEYBOARD_INPUT | Keyboard input blocked |
| 4 | NO_VOICE_INPUT | Voice input blocked |
| 8 | NO_CONFIG | Configuration changes blocked |
| 16 | LIMIT_MESSAGE_LEN | Long messages truncated |
| 31 | FULLY_RESTRICTED | All restrictions active (1+2+4+8+16) |

**Passenger** (type 15, `vzo`):

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | bool | optional | Passenger present in front seat |

---

## SDP Configuration

> Confidence: Gold [deep_trace, 16.2 DB verified]

The HU advertises sensor support via `SensorChannelConfig` in the ChannelDescriptor during service discovery (field 2 of the sensor channel's descriptor).

### SensorChannelConfig (`wbk`)

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | repeated SensorTypeEntry | -- | List of supported sensor types |
| 2 | uint32 | optional | Default update interval (ms) |
| 3 | repeated FuelType | -- | Fuel types the vehicle uses |
| 4 | repeated EVConnectorType | -- | EV connector types the vehicle supports |

### SensorTypeEntry (`wbj`)

| Field | Type | Modifier | Description |
|:---:|------|----------|-------------|
| 1 | enum SensorType | optional | A sensor type this HU can provide |

### FuelType Enum (Silver)

| Value | Name | Value | Name |
|:---:|------|:---:|------|
| 0 | UNKNOWN | 7 | LPG |
| 1 | UNLEADED | 8 | CNG |
| 2 | LEADED | 9 | LNG |
| 3 | DIESEL_1 | 10 | ELECTRIC |
| 4 | DIESEL_2 | 11 | HYDROGEN |
| 5 | BIODIESEL | 12 | OTHER |
| 6 | E85 | | |

### EVConnectorType Enum (Silver)

| Value | Name | Value | Name |
|:---:|------|:---:|------|
| 0 | UNKNOWN | 7 | TESLA_HPWC |
| 1 | J1772 | 8 | TESLA_SUPERCHARGER |
| 2 | MENNEKES | 9 | GBT |
| 3 | CHADEMO | 10 | GBT_DC |
| 4 | COMBO_1 | 11 | LECCS |
| 5 | COMBO_2 | 14 | NACS |
| 6 | TESLA_ROADSTER | | |

Note the gap: values 12-13 are not defined. NACS (value 14) was likely added later.

---

## Implementation Guide

> Confidence: Gold -- based on fully traced handler flow in ibi.java

### Sensor Subscription Flow

```
Phone                                        Head Unit
  |                                            |
  |--- SensorRequest (LOCATION, 1000ms) -----> |  Subscribe to GPS at 1Hz
  |<-- SensorStartResponse (OK) -------------- |  HU accepts
  |                                            |
  |--- SensorRequest (CAR_SPEED, 500ms) -----> |  Subscribe to speed at 2Hz
  |<-- SensorStartResponse (OK) -------------- |  HU accepts
  |                                            |
  |--- SensorRequest (NIGHT_DATA, 0ms) ------> |  Subscribe to night mode (event-driven)
  |<-- SensorStartResponse (OK) -------------- |  HU accepts
  |                                            |
  |  ... sensors running ...                   |
  |                                            |
  |<---------------- SensorEventIndication {   |
  |             gps_location: [lat, lon, ...]  |  Batched sensor data
  |             speed: [85]                    |
  |  } -------------------------------------- |
  |                                            |
  |<---------------- SensorEventIndication {   |
  |             night_mode: [is_night: true]   |  Event-driven update
  |  } -------------------------------------- |
  |                                            |
  |<---------- SensorError (GPS, TRANSIENT) -- |  GPS lost signal
  |                                            |
  |<----------------- SensorError (GPS, OK) -- |  GPS recovered
```

### Building SensorRequest Messages (Phone Side)

```c
// Subscribe to the HU sensors Android Auto wants.
// Called after channel setup completes.

void subscribe_sensors(int channel_id) {
    // Core sensors -- fast refresh for navigation
    send_sensor_request(channel_id, SENSOR_LOCATION, 1000);    // GPS at 1Hz
    send_sensor_request(channel_id, SENSOR_CAR_SPEED, 500);    // Speed at 2Hz
    send_sensor_request(channel_id, SENSOR_COMPASS, 1000);     // Compass at 1Hz

    // Vehicle state -- slower refresh is fine
    send_sensor_request(channel_id, SENSOR_GEAR, 200);         // Gear at 5Hz
    send_sensor_request(channel_id, SENSOR_FUEL_LEVEL, 10000); // Fuel every 10s
    send_sensor_request(channel_id, SENSOR_PARKING_BRAKE, 500);

    // Event-driven sensors -- 0ms = send on change only
    send_sensor_request(channel_id, SENSOR_NIGHT_DATA, 0);
    send_sensor_request(channel_id, SENSOR_DRIVING_STATUS, 0);
}
```

### Handling SensorEventIndication (Phone Side)

```c
// Process incoming sensor data.
// Multiple sensor types can arrive in a single message.

void handle_sensor_event(SensorEventIndication *msg) {
    // Check each field -- populated fields indicate which sensors have data
    if (msg->gps_location_count > 0) {
        GPSLocation *loc = &msg->gps_location[0];
        update_position(loc->latitude, loc->longitude);
        if (loc->has_accuracy)
            update_gps_accuracy(loc->accuracy);
    }

    if (msg->speed_count > 0) {
        update_speedometer(msg->speed[0].speed);
    }

    if (msg->night_mode_count > 0) {
        set_day_night_mode(msg->night_mode[0].is_night);
    }

    if (msg->driving_status_count > 0) {
        int flags = msg->driving_status[0].status;
        update_driving_restrictions(
            flags & 0x01,  // NO_VIDEO
            flags & 0x02,  // NO_KEYBOARD_INPUT
            flags & 0x10   // LIMIT_MESSAGE_LEN
        );
    }

    if (msg->gear_count > 0) {
        update_gear_indicator(msg->gear[0].gear);
    }
}
```

### Handling SensorError (Phone Side)

```c
void handle_sensor_error(SensorError *msg) {
    switch (msg->error_status) {
    case SENSOR_OK:
        // Sensor recovered -- resume displaying its data
        mark_sensor_available(msg->sensor_type);
        break;
    case SENSOR_ERROR_TRANSIENT:
        // Temporary failure -- show stale data with warning indicator
        mark_sensor_degraded(msg->sensor_type);
        break;
    case SENSOR_ERROR_PERMANENT:
        // Sensor gone -- hide its UI element
        mark_sensor_unavailable(msg->sensor_type);
        break;
    }
}
```

---

## Gotchas

> **Gotcha:** The `SensorEventIndication` field numbers **are** the `SensorType` enum values. Field 1 = LOCATION (type 1), field 8 = GEAR (type 8), field 21 = GPS_SATELLITE (type 21). This is by design -- the proto schema encodes the type dispatch directly in the field numbering.

> **Gotcha:** All fields in `SensorEventIndication` are `repeated`. Even for singleton sensors like NIGHT_DATA (one boolean), the data arrives as a repeated field. Always index into the array (`msg->night_mode[0]`), not access it as a scalar.

> **Gotcha:** `GPSLocation` has **no field 1**. Fields start at 2 (latitude). This is deliberate -- field 1 (likely a timestamp) does not exist in the APK. Do not add a field 1 to your proto definition.

> **Gotcha:** The `Gear` enum uses **non-contiguous values**: 0-10 for individual gears, then jumps to 100-102 for DRIVE/PARK/REVERSE. This is a closed enum (`enum_closed=1` in DB) -- unknown values must be rejected, not silently accepted. Use proto2 syntax, not proto3.

> **Gotcha:** `DrivingStatus.status` is a **bitmask**, not an enum. Multiple flags can be set simultaneously (e.g., `NO_VIDEO | NO_KEYBOARD_INPUT = 3`). The value `FULLY_RESTRICTED = 31` is all five flags OR'd together, not a separate state.

> **Gotcha:** `SensorStartResponse` uses the **shared ProtocolStatus enum** (`vyh`, 34 values) -- the same enum used by bluetooth, radio, and other channels. Do not define a sensor-specific status enum.

> **Gotcha:** The `refresh_interval` field in `SensorRequest` is `int64` (signed), not `uint64`. A value of 0 typically means event-driven delivery (send on change only). The units are milliseconds.

> **Gotcha:** `HVAC` sensor data (type 12) is **legacy**. In AA 16.2, detailed HVAC control uses the Car Control channel (service 19) with VHAL property IDs. The sensor channel HVAC type provides only basic target/current temperature.

> **Gotcha:** `Speed` data has **no field 3** -- it jumps from field 2 to field 4. This is not an error; field 3 was likely removed or never used.

> **Gotcha:** `Light` data fields 2 and 3 **default to 1** in the APK, which is unusual. This may mean indicator/hazard default to ON. Verify with wire captures before assuming default behavior.

> **Gotcha:** Obfuscated class names **collide across APK versions**. `wbh` is `RawVehicleEnergyModel` in 16.1 but `SensorRequest` in 16.2. `wbf` is `RawEvTripSettings` in 16.1 but `SensorError` in 16.2. `wbt` is `SensorTypeEntry` in 16.1 but `Speed` in 16.2. Always match by field structure, not by class name.

> **Gotcha:** Sensor types 23 (`VehicleEnergyModelData`) and 24 (`TrailerData`) are **empty messages** with zero fields. Types 25 and 26 carry opaque `bytes` blobs. These EV/energy-related types have no structured data yet -- their internal formats are unknown.

---

## References

### Proto Files -- Wire Messages
- [SensorRequestMessage.proto](../../oaa/sensor/SensorRequestMessage.proto)
- [SensorStartResponseMessage.proto](../../oaa/sensor/SensorStartResponseMessage.proto)
- [SensorEventIndicationMessage.proto](../../oaa/sensor/SensorEventIndicationMessage.proto)
- [SensorErrorMessage.proto](../../oaa/sensor/SensorErrorMessage.proto)
- [SensorStartRequestMessage.proto](../../oaa/sensor/SensorStartRequestMessage.proto) **(RETRACTED -- duplicate)**

### Proto Files -- Enums
- [SensorTypeEnum.proto](../../oaa/sensor/SensorTypeEnum.proto)
- [SensorErrorStatusEnum.proto](../../oaa/sensor/SensorErrorStatusEnum.proto)
- [SensorChannelMessageIdsEnum.proto](../../oaa/sensor/SensorChannelMessageIdsEnum.proto)
- [GearEnum.proto](../../oaa/sensor/GearEnum.proto)
- [DrivingStatusEnum.proto](../../oaa/sensor/DrivingStatusEnum.proto)
- [FuelTypeEnum.proto](../../oaa/sensor/FuelTypeEnum.proto)
- [EVConnectorTypeEnum.proto](../../oaa/sensor/EVConnectorTypeEnum.proto)
- [HeadlightStatusEnum.proto](../../oaa/sensor/HeadlightStatusEnum.proto) (Silver -- placeholder values)
- [IndicatorStatusEnum.proto](../../oaa/sensor/IndicatorStatusEnum.proto) (Silver -- placeholder values)

### Proto Files -- Sensor Data Sub-Messages
- [GPSLocationData.proto](../../oaa/sensor/GPSLocationData.proto)
- [CompassData.proto](../../oaa/sensor/CompassData.proto)
- [SpeedData.proto](../../oaa/sensor/SpeedData.proto)
- [RPMData.proto](../../oaa/sensor/RPMData.proto)
- [OdometerData.proto](../../oaa/sensor/OdometerData.proto)
- [FuelLevelData.proto](../../oaa/sensor/FuelLevelData.proto)
- [ParkingBrakeData.proto](../../oaa/sensor/ParkingBrakeData.proto)
- [GearData.proto](../../oaa/sensor/GearData.proto)
- [DiagnosticsData.proto](../../oaa/common/DiagnosticsData.proto) (in oaa/common/)
- [NightModeData.proto](../../oaa/sensor/NightModeData.proto)
- [EnvironmentData.proto](../../oaa/sensor/EnvironmentData.proto)
- [HVACData.proto](../../oaa/sensor/HVACData.proto)
- [DrivingStatusData.proto](../../oaa/sensor/DrivingStatusData.proto)
- [SteeringWheelData.proto](../../oaa/sensor/SteeringWheelData.proto)
- [PassengerData.proto](../../oaa/sensor/PassengerData.proto)
- [DoorData.proto](../../oaa/sensor/DoorData.proto)
- [LightData.proto](../../oaa/sensor/LightData.proto)
- [TirePressureData.proto](../../oaa/sensor/TirePressureData.proto)
- [AccelData.proto](../../oaa/sensor/AccelData.proto)
- [GyroData.proto](../../oaa/sensor/GyroData.proto)
- [GpsSatelliteData.proto](../../oaa/sensor/GpsSatelliteData.proto)
- [TollCardData.proto](../../oaa/sensor/TollCardData.proto)
- [VehicleEnergyModelData.proto](../../oaa/sensor/VehicleEnergyModelData.proto)
- [TrailerData.proto](../../oaa/sensor/TrailerData.proto)
- [RawVehicleEnergyModelData.proto](../../oaa/sensor/RawVehicleEnergyModelData.proto)
- [RawEvTripSettingsData.proto](../../oaa/sensor/RawEvTripSettingsData.proto)

### SDP Configuration
- [SensorChannelConfigData.proto](../../oaa/sensor/SensorChannelConfigData.proto)

### Handler Classes (16.2)
- `ibi.java` -- Sensor GAL handler (extends `iav`), dispatches all 4 message types
- `wbe.java` -- SensorEventIndication proto (26 fields, zzq descriptor)
- `wbh.java` -- SensorRequest proto
- `wbi.java` -- SensorStartResponse proto
- `wbf.java` -- SensorError proto
- `wbl.java` -- SensorType enum (26 values)
- `wbg.java` -- SensorErrorStatus enum (3 values)
- `wbk.java` -- SensorChannelConfig (SDP)
- `wbj.java` -- SensorTypeEntry (SDP)

### Verification Report
- [Proto Verification: Sensor Channel](../../analysis/reports/proto-verification/sensor.md) -- full verification trace with fixes and retractions

### Cross-References
- [Channel map](../channel-map.md) -- Channel ID reference for all AA channels
- [01-confidence-tiers.md](../verification/01-confidence-tiers.md) -- Confidence tier definitions
