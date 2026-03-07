# Car Control Channel Verification Report

**Channel:** CAR.GAL.CAR_CONTROL (GAL type 19)
**Handler:** hyc.java (16.2) / hxp.java (16.1)
**Service manager:** hlb.java (CAR.CarControlService)
**Msg ID enum:** vik.m36843p/m36844q (no offset — maps IDs unchanged)
**Verified:** 2026-03-07
**Status:** COMPLETE

## Message Dispatch Table

| Wire ID | Internal ID | Name | Direction | 16.2 Class | Handler Action |
|---------|-------------|------|-----------|------------|----------------|
| 0x8001 | 32769 | SET_CAR_PROPERTY_VALUE_REQUEST | HU→Phone | wbq | Send-only |
| 0x8002 | 32770 | SET_CAR_PROPERTY_VALUE_RESPONSE | Phone→HU | wbr | Parsed, UUID-matched callback |
| 0x8003 | 32771 | REGISTER_CAR_PROPERTY_LISTENERS_REQUEST | HU→Phone | waz | Send-only (logs "unexpected" if received) |
| 0x8004 | 32772 | REGISTER_CAR_PROPERTY_LISTENERS_RESPONSE | Phone→HU | wba | Parsed, per-property results |
| 0x8005 | 32773 | CAR_PROPERTY_CHANGE_EVENT | Phone→HU | vwg | Parsed, updates cached property state |
| 0x8006 | 32774 | CAR_ACTION_NOTIFICATION | HU→Phone | vvv | Send-only (logs "unexpected" if received) |
| 0x8007 | 32775 | CAR_CONTROL_GROUP_UPDATE | Phone→HU | vvz | Parsed, replaces control group by type |

## Top-Level Messages (7 Gold)

| Proto | Wire ID | Direction | 16.2 Class | Confidence | Result |
|-------|---------|-----------|------------|------------|--------|
| SetCarPropertyValueRequest | 0x8001 | HU→Phone | wbq | Gold | Correct (3 fields) |
| SetCarPropertyValueResponse | 0x8002 | Phone→HU | wbr | Gold | **FIX**: status field uses vyh (ProtocolStatus), not CarControlStatus |
| RegisterCarPropertyListenersRequest | 0x8003 | HU→Phone | waz | Gold | **NEW** — was missing from proto |
| RegisterCarPropertyListenersResponse | 0x8004 | Phone→HU | wba | Gold | Correct (1 field) |
| CarPropertyChangeEvent | 0x8005 | Phone→HU | vwg | Gold | Correct (3 fields) |
| CarActionNotification | 0x8006 | HU→Phone | vvv | Gold | Correct (1 field) |
| CarControlGroupUpdate | 0x8007 | Phone→HU | vvz | Gold | Correct (1 field) |

## Sub-Messages (12 Gold)

| Proto | 16.2 Class | 16.1 Class | Confidence | Result |
|-------|-----------|-----------|------------|--------|
| CarProperty | vuh | vuv | Gold | Correct (2 fields) |
| CarAreaId | vui | vuw | Gold | Correct (6 fields) |
| CarPropertyValue | vup | vvd | Gold | **FIX**: oneof 6-8 are IntValues/LongValues/FloatValues, not empty |
| CarAction | vtz | vun | Gold | Correct (1 field) |
| CarActionEntry | vua | vuo | Gold | Correct (1 field, sub_ref vtz) |
| IntValues | vun | vvb | Gold | Correct (packed int32) |
| FloatValues | vum | vvc | Gold | Correct (packed float) |
| LongValues | vuo | vva | Gold | Correct (packed int64) |
| CarPropertyAreaConfig | vty | vum | Gold | Correct (3 fields) |
| CarPropertyConfig | vuj | vux | Gold | **FIX**: fields 4/7 restructured in 16.2 |
| CarPropertyControl | vuk | vuy | Gold | Correct (3 fields) |
| SetCarPropertyListenerResult | vwh | vwv | Gold | **FIX**: status field uses vyh |

## Layout Sub-Messages (4 Gold)

| Proto | 16.2 Class | 16.1 Class | Confidence | Result |
|-------|-----------|-----------|------------|--------|
| CarControl | vvx | vwl | Gold | Correct (6 fields, oneof + 3 optional) |
| CarControlGroup | vvy | vwm | Gold | Correct (2 fields) |
| CarActionControl | vvu | vwi | Gold | Correct (1 field) |
| CarControlChannelDescriptor | vwa | vwo | Gold | **FIX**: field 2 is CarControl, not CarControlGroup |

## Enums (3 Gold, 8 Silver)

| Enum | 16.2 Class | Values | Confidence | Result |
|------|-----------|--------|------------|--------|
| CarPropertyId | vul | 26 (VHAL IDs) | Gold | **CRITICAL FIX**: values are VHAL IDs, not sequential 1-23 |
| CarControlMetadataType | vug | 3 | Gold | **FIX**: METADATA_PREFER_STATUS_BAR=2 added |
| VehicleAreaSeat | vud | 9 | Gold | **FIX**: ROW_3_CENTER (512) removed — not in APK |
| VehicleAreaWindow | vuf | 11 | Gold | Correct |
| VehicleAreaDoor | vub | 9 | Gold | Correct |
| VehicleAreaMirror | vuc | 4 | Gold | Correct |
| VehicleAreaWheel | vue | 5 | Gold | Correct |
| CarActionId | — | 5 (0,3-6) | Silver | No named enum class in DB |
| CarAreaType | — | 6 (0,2-6) | Silver | No named enum class in DB |
| CarPropertyAccessMode | — | 4 (0-3) | Silver | No named enum class in DB |
| CarPropertyChangeMode | — | 3 (0-2) | Silver | No named enum class in DB |
| CarPropertyType | — | 11 (0-10) | Silver | No named enum class in DB |
| SideAffinity | — | 3 (0-2) | Silver | No named enum class in DB |
| CarControlGroupType | — | 2 (0-1) | Silver | No named enum class in DB |
| CarControlStatus | — | — | RETRACTED | Wire uses shared ProtocolStatus (vyh) |

## Critical Fixes Applied

### 1. CarPropertyId enum values — ALL WRONG (sequential → VHAL IDs)

The proto had sequential values (1=HVAC_TEMPERATURE_SET, 2=HVAC_AUTO_ON, etc.) but the actual APK enum (vul) uses raw Android VHAL property IDs:

| Name | Was (WRONG) | Now (CORRECT) |
|------|------------|---------------|
| HVAC_TEMPERATURE_SET | 1 | 358614275 |
| HVAC_AUTO_ON | 2 | 354419978 |
| HVAC_FAN_SPEED | 5 | 356517120 |
| DOOR_LOCK | 24 | 371198722 |
| ... | ... | (all 25 values changed) |

### 2. CarPropertyValue oneof 6-8 — empty placeholders → real types

Source `vup.java` descriptor constructor passes `vun.class, vuo.class, vum.class` for fields 6-8:
- Field 6: `IntValues int_array` (was `CarPropertyValueMsg msg_value_6`)
- Field 7: `LongValues long_array` (was `CarPropertyValueMsg msg_value_7`)
- Field 8: `FloatValues float_array` (was `CarPropertyValueMsg msg_value_8`)

`CarPropertyValueMsg` (empty placeholder message) **REMOVED**.

### 3. CarControlChannelDescriptor field 2 — wrong type

SDP descriptor field 2 references `vvx.class` (CarControl), NOT `vvy.class` (CarControlGroup).
- Was: `repeated CarControlGroup control_groups = 2;`
- Now: `repeated CarControl controls = 2;`

### 4. CarPropertyConfig fields 4/7 restructured (16.1 → 16.2)

| Field | 16.1 Type | 16.2 Type |
|-------|-----------|-----------|
| 4 | `repeated CarPropertyAreaConfig` (area + min/max) | `repeated CarAreaId` (bare area IDs) |
| 7 | `repeated CarPropertyValue` (supported values) | `repeated CarPropertyAreaConfig` (area + min/max moved here) |

### 5. Status fields use shared ProtocolStatus (vyh)

Both `SetCarPropertyValueResponse.status` and `SetCarPropertyListenerResult.status` use the shared AA ProtocolStatus enum (vyh, 34 values), NOT the 3-value `CarControlStatus`. Confirmed via `vyh.m37369b()` calls in handler and `vik.m36848u()` builder.

`CarControlStatus` enum **RETRACTED**.

### 6. RegisterCarPropertyListenersRequest — NEW proto

Class `waz` exists in 16.2 DB with 1 field (repeated CarProperty). Was missing from proto file.

### 7. CarControlMetadataType — missing value

`vug` enum has 3 values: METADATA_PREFER_STATUS_BAR=2 was missing.

### 8. VehicleAreaSeat — extra value

ROW_3_CENTER (512) is in AOSP spec but NOT in AA's proto enum (vud). Removed.

## Bonus Findings

- **DriverPosition enum (vwu):** Discovered `vwu` has LEFT/RIGHT/CENTER/UNKNOWN values — not currently in our protos. May be referenced elsewhere.
- **Cross-version doc errors:** `docs/cross-version/carcontrol.md` has FloatValues/LongValues 16.2 class names SWAPPED (vuo↔vum). RegisterCarPropertyListenersResponse listed as `--` for 16.2 but is actually `wba`.

## Totals

| Category | Count |
|----------|-------|
| Gold messages | 7 |
| Gold sub-messages | 16 (12 property + 4 layout) |
| Gold enums | 7 |
| Silver enums | 8 |
| Retracted | 2 (CarControlStatus, CarPropertyValueMsg) |
| New protos | 1 (RegisterCarPropertyListenersRequest) |
| Schema errors fixed | 8 (CarPropertyId values, CarPropertyValue oneof 6-8, CarControlChannelDescriptor field 2, CarPropertyConfig fields 4/7, status×2, metadata enum, seat enum) |
