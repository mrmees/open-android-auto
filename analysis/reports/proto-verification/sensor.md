# Sensor Channel Verification Report

**Channel:** Sensor (CAR.GAL.SENSOR)
**GAL type:** 7
**Handler class:** `ibi.java` (16.2), extends `iav`
**No +1 msg ID offset** — raw constants used directly
**Verified:** 2026-03-06

## Wire Messages

| Proto | Wire ID | Direction | 16.1 Class | 16.2 Class | Confidence | Notes |
|-------|---------|-----------|------------|------------|------------|-------|
| SensorRequest | 0x8001 | HU→Phone | wbr | wbh | **Gold** | 2 fields: required enum SensorType, required int64 refresh_interval |
| SensorStartResponse | 0x8002 | Phone→HU | — | wbi | **Gold** | 1 field: required enum Status (vyh) |
| SensorEventIndication | 0x8003 | Phone→HU | wbo | wbe | **Gold** | 26 repeated message fields, one per sensor type |
| SensorError | 0x8004 | Phone→HU | wbp | wbf | **Gold** | 2 fields: required enum SensorType, required enum SensorErrorStatus |

## Enums

| Enum | 16.1 Class | 16.2 Class | Values | Confidence |
|------|------------|------------|--------|------------|
| SensorType | wbv | wbl | 26 values (1-26) | **Gold** |
| SensorErrorStatus | wbq | wbg | 3 values (1-3) | **Gold** |
| SensorChannelMessageIds | — | — | 4 IDs (0x8001-0x8004) | **Gold** |
| Gear | — | vxb closed enum | 14 values (0-10, 100-102) | **Gold** |
| DrivingStatus | — | — | Bitmask flags (0-31) | **Gold** |
| FuelType | vxo | vxa | 13 values (0-12) | **Gold** |
| EVConnectorType | vxl | vwx | 12 values (0-11, 14) | **Gold** |
| HeadlightStatus | — | — | Placeholder (0-3), no named enum class in APK | Silver |
| IndicatorStatus | — | — | Placeholder (0-3), no named enum class in APK | Silver |

## Sensor Data Sub-Messages (all Gold)

| Field | Sensor Type | 16.2 Class | Proto File | Fields | Issues Fixed |
|-------|-------------|------------|------------|--------|-------------|
| 1 | LOCATION | vxx | GPSLocationData.proto | 6 (f2-f7) | latitude/longitude → required |
| 2 | COMPASS | vwm | CompassData.proto | 3 | bearing → required |
| 3 | SPEED | wbt | SpeedData.proto | 3 (f1,f2,f4) | speed → required, 16.2 class updated |
| 4 | RPM | wbd | RPMData.proto | 1 | rpm → required |
| 5 | ODOMETER | vzj | OdometerData.proto | 2 | total_mileage → required |
| 6 | FUEL | vwz | FuelLevelData.proto | 3 | — |
| 7 | PARKING_BRAKE | vzn | ParkingBrakeData.proto | 1 | parking_brake → required |
| 8 | GEAR | vxb | GearData.proto | 1 enum | gear → required, GearEnum syntax proto3→proto2 |
| 9 | DIAGNOSTICS | vwr | DiagnosticsData.proto | 1 bytes | 16.2 class updated (was vxf) |
| 10 | NIGHT_MODE | vzi | NightModeData.proto | 1 bool | — |
| 11 | ENVIRONMENT | vww | EnvironmentData.proto | 3 | — |
| 12 | HVAC | vxh | HVACData.proto | 2 | — |
| 13 | DRIVING_STATUS | vwv | DrivingStatusData.proto | 1 int32 | status → required |
| 14 | DEAD_RECKONING | vwq | SteeringWheelData.proto | 2 | — |
| 15 | PASSENGER | vzo | PassengerData.proto | 1 bool | — |
| 16 | DOOR | vwt | DoorData.proto | 3 | — |
| 17 | LIGHT | vxw | LightData.proto | 3 | Note: fields 2,3 default to 1 |
| 18 | TIRE_PRESSURE | wbw | TirePressureData.proto | 1 repeated | 16.2 class updated (was wcg) |
| 19 | ACCELEROMETER | vuv | AccelData.proto | 3 | — |
| 20 | GYROSCOPE | vxf | GyroData.proto | 3 | — |
| 21 | GPS_SATELLITE | vxe | GpsSatelliteData.proto | 3 + sub-msg | GpsSatelliteInfo filled (5 fields from vxd) |
| 22 | TOLL_CARD | wbx | TollCardData.proto | 1 bool | 16.2 class updated |
| 23 | VEHICLE_ENERGY_MODEL | vus | VehicleEnergyModelData.proto | 0 (empty) | 16.2 class updated |
| 24 | TRAILER | wca | TrailerData.proto | 0 (empty) | 16.2 class updated |
| 25 | RAW_VEHICLE_ENERGY_MODEL | wax | RawVehicleEnergyModelData.proto | 1 bytes | 16.2 class updated (16.1 was wbh — name collision!) |
| 26 | RAW_EV_TRIP_SETTINGS | wav | RawEvTripSettingsData.proto | 1 bytes | 16.2 class updated (16.1 was wbf — name collision!) |

## SDP Config

| Proto | 16.1 Class | 16.2 Class | Confidence | Notes |
|-------|------------|------------|------------|-------|
| SensorChannelConfig | wbu | wbk | **Gold** | 4 fields: repeated SensorTypeEntry, uint32, repeated FuelType, repeated EVConnectorType |
| SensorTypeEntry | wbt | wbj | **Gold** | 1 field: SensorType enum |

## Retracted

| Proto | Reason |
|-------|--------|
| SensorStartRequestMessage | Duplicate of SensorRequestMessage with wrong field modifiers (optional/uint64 vs required/int64) |

## Major Fixes Applied

### 1. SensorEventIndication Fields 21-26 — WRONG Sub-Message Types

The existing proto had inline message definitions (TollRoad, RangeRemaining, FuelTypeInfo, EVBatteryInfo, EVChargeInfo, EVChargeStatus) for fields 21-26. These were based on incorrect 16.1 analysis. The 16.2 handler and zzq descriptor confirmed the actual types match the individual sensor data proto files that already existed:

| Field | Was (wrong) | Now (correct) |
|-------|------------|---------------|
| 21 | TollRoad (vxs) | GpsSatelliteData (vxe) |
| 22 | RangeRemaining (wch) | TollCardData (wbx) |
| 23 | FuelTypeInfo (vvg) | VehicleEnergyModelData (vus) |
| 24 | EVBatteryInfo (wcl) | TrailerData (wca) |
| 25 | EVChargeInfo (wbh) | RawVehicleEnergyModel (wax) |
| 26 | EVChargeStatus (wbf) | RawEvTripSettings (wav) |

All inline message definitions removed. Correct types imported from existing separate proto files.

### 2. "Fields 12-20 Removed" Comment — WRONG

The comment claimed fields 12-20 were "Removed in AA v16.1 APK (wbo.java only has fields 1-11)." The 16.2 handler (`ibi.java`) explicitly dispatches ALL 26 sensor types from `wbe.java`. Comment removed.

### 3. Optional → Required (9 fields across 7 protos)

GPSLocation.latitude/longitude, Compass.bearing, Speed.speed, RPM.rpm, Odometer.total_mileage, ParkingBrake.parking_brake, Gear.gear, DrivingStatus.status — all confirmed `required` in 16.2 DB.

### 4. GpsSatelliteInfo — Filled from Empty

Was an empty placeholder. 16.2 class `vxd` has 5 fields: required int32 prn, required int32 snr, required bool in_use, optional int32 azimuth, optional int32 elevation.

### 5. GearEnum Syntax Fix

Changed from `syntax="proto3"` to `syntax="proto2"` to match closed enum semantics (`enum_closed=1` in DB).

### 6. Obfuscated Name Collisions Documented

- `wbh` = RawVehicleEnergyModel in 16.1, SensorRequest in 16.2
- `wbf` = RawEvTripSettings in 16.1, SensorError in 16.2
- `wbt` = SensorTypeEntry in 16.1, Speed sub-message in 16.2

## Statistics

- **4 Gold wire messages** + **4 Gold enums** + **26 Gold sub-messages** + **2 Gold SDP configs** = **36 Gold total**
- **1 retraction** (SensorStartRequestMessage)
- **9 optional→required fixes**
- **5 new fields** (GpsSatelliteInfo)
- **6 field type corrections** (SensorEventIndication fields 21-26)
- **2 enums remaining at Silver** (HeadlightStatus, IndicatorStatus — no named APK classes found)
