# Bluetooth Channel Verification Report

**Channel:** BT (service 9, CAR.GAL.BT)
**Handler:** qlg.java (16.2), extends qnp
**Service:** plq.java (BT manager), qav.java (auth FSM)
**Verified:** 2026-03-07

## Message ID Table

| Msg ID | Direction | 16.2 Class | Proto Name | Confidence |
|--------|-----------|------------|------------|------------|
| 0x8001 | HU→Phone | kba | BluetoothPairingRequest | Gold |
| 0x8002 | HU→Phone | vvn | BluetoothPairingResponse | Gold |
| 0x8003 | HU→Phone | vvj | BluetoothAuthenticationData | Gold |
| 0x8004 | Phone→HU | vvk | BluetoothAuthenticationResult | Gold (NEW) |

## Critical Fixes Applied

### 1. BluetoothPairingResponse — Fields Swapped + Wrong Class

**Was (WRONG):**
- Class: xgb/xgq
- Field 1: bool already_paired
- Field 2: enum BluetoothPairingStatus
- Field 3: repeated packed enum error_codes

**Now (CORRECT):**
- Class: vvn
- Field 1: int32 status (shared AA StatusCode enum, vyh)
- Field 2: bool already_paired
- No field 3

The old class mapping (xgb) was a sub-message in xgh, unrelated to the BT wire protocol.

### 2. BluetoothPairingStatusEnum — RETRACTED

The old 3-value enum (NONE=0, OK=1, FAIL=2) was completely wrong. The actual status field uses the shared AA StatusCode enum (`vyh`) with 30+ values. BT-specific status codes range from -10 to -17.

Both BluetoothPairingResponse and BluetoothAuthenticationResult use `int32 status` directly with vyh values.

### 3. BluetoothAuthenticationData — NEW Proto

Previously had no standalone proto file. Wire message 0x8003 uses class `vvj`:
- 1 required string field (auth_data)
- Handler hex-encodes via vik.m36829ay() for logging

### 4. BluetoothAuthenticationResult — NEW Proto (DISCOVERED)

Wire message 0x8004, Phone→HU. Class `vvk`. Sent by qav.java (auth FSM):
- 1 required int32 field (status, vyh enum)
- Status values used: SUCCESS(0), UNSOLICITED(1), INVALID_METHOD(-13), INVALID_AUTH(-14), MISMATCH(-15)

### 5. BluetoothChannelData — Field Label Fix

Field 1 (adapter_address) changed from optional to required (confirmed in DB).

### 6. BluetoothChannelConfigData — SUPERSEDED

Duplicate of BluetoothChannelData with proto3 syntax. Tombstoned.

## No Changes Needed

| Proto | Status |
|-------|--------|
| BluetoothPairingRequest (kba) | Correct — 3 optional fields, proto3 |
| BluetoothPairingMethodEnum (vvl) | Correct — 5 values (0-4) |

## Cross-Version Class Mapping

| Proto | 16.1 Class | 16.2 Class |
|-------|-----------|-----------|
| BluetoothPairingRequest | kay | kba |
| BluetoothPairingResponse | — | vvn |
| BluetoothAuthenticationData | — | vvj |
| BluetoothAuthenticationResult | — | vvk |
| BluetoothChannelConfig (SDP) | vwc | vvo |
| BluetoothPairingMethod enum | vvz | vvl |
| AA StatusCode enum | — | vyh |

**WARNING:** In 16.1, vvn/vvj/vvk/vvo refer to COMPLETELY DIFFERENT protos. Always match by handler context, not obfuscated name.

## Shared AA StatusCode Enum (vyh) — BT-Relevant Values

| Value | Name |
|-------|------|
| 0 | STATUS_SUCCESS |
| 1 | STATUS_UNSOLICITED_MESSAGE |
| -10 | STATUS_BLUETOOTH_PAIRING_DELAYED |
| -11 | STATUS_BLUETOOTH_UNAVAILABLE |
| -12 | STATUS_BLUETOOTH_INVALID_ADDRESS |
| -13 | STATUS_BLUETOOTH_INVALID_PAIRING_METHOD |
| -14 | STATUS_BLUETOOTH_INVALID_AUTH_DATA |
| -15 | STATUS_BLUETOOTH_AUTH_DATA_MISMATCH |
| -16 | STATUS_BLUETOOTH_HFP_ANOTHER_CONNECTION |
| -17 | STATUS_BLUETOOTH_HFP_CONNECTION_FAILURE |
