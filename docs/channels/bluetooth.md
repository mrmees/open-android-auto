# Bluetooth Channel

## Overview

The Bluetooth channel (GAL service type 9) handles **BT pairing orchestration only**. It coordinates the initial Bluetooth bonding between the phone and the head unit so that HFP (Hands-Free Profile) can subsequently carry call audio. The channel itself carries no audio data.

Call audio during AA projection uses a dual-path architecture:

- **Signaling (AA protocol):** Phone call state (caller ID, call state, duration, contact photo) flows through the Phone Status channel (GAL type 13) as protobuf messages.
- **Audio (BT HFP):** Actual voice audio flows through standard Bluetooth HFP over SCO (Synchronous Connection-Oriented), which is an OS-level Bluetooth audio path managed by the Android `BluetoothHeadset` API, completely independent of the AA data connection.

The pairing pipeline: HU advertises BT adapter address in SDP (`BluetoothChannelDescriptor`, field 6) -> HU sends `BluetoothPairingRequest` (0x8001) to phone -> HU sends `BluetoothPairingResponse` (0x8002) -> HU sends `BluetoothAuthenticationData` (0x8003) -> phone confirms via OS BT stack + sends `BluetoothAuthenticationResult` (0x8004) -> HFP connects at OS level -> steady-state monitoring.

---

## Message Catalog

| Msg ID | Direction | Proto Class (16.2) | Name | Purpose |
|--------|-----------|-------------------|------|---------|
| 0x8001 | HU -> Phone | `kba` | BluetoothPairingRequest | HU requests phone to initiate BT pairing |
| 0x8002 | HU -> Phone | `vvn` | BluetoothPairingResponse | HU accepts/rejects pairing request |
| 0x8003 | HU -> Phone | `vvj` | BluetoothAuthenticationData | HU sends auth data (PIN or passkey) |
| 0x8004 | Phone -> HU | `vvk` | BluetoothAuthenticationResult | Phone reports auth success/failure |

---

## BluetoothPairingRequest (0x8001)

Sent by the HU to the phone to initiate BT pairing.

```protobuf
message BluetoothPairingRequest {   // APK class: kba (16.2)
    required string phone_address    = 1;  // phone's BT MAC address
    required BluetoothPairingMethod pairing_method = 2;  // chosen pairing method
    optional string phone_name       = 3;  // human-readable phone name
}
```

The pairing method is selected from the intersection of capabilities and the HU's `supported_pairing_methods` advertised in the SDP. Priority order is hardcoded: `NUMERIC_COMPARISON` > `PIN`.

---

## BluetoothPairingResponse (0x8002)

HU's response to the pairing request.

```protobuf
message BluetoothPairingResponse {  // APK class: vvn (16.2)
    required int32 status            = 1;  // ProtocolStatus (vyh) — shared AA status enum
    optional bool already_paired     = 2;  // true if devices already bonded
}
```

> **Verification fix (2026-03-06):** Fields were previously documented as swapped (field 1=already_paired, field 2=status). The status field uses the shared ProtocolStatus enum (vyh, 34 values), NOT the old 3-value BluetoothPairingStatus which was retracted.

If `already_paired = true`, the phone skips the authentication exchange and proceeds directly to HFP connection.

---

## BluetoothAuthenticationData (0x8003)

HU sends authentication data for the pairing process.

```protobuf
message BluetoothAuthenticationData {  // APK class: vvj
    required string auth_data        = 1;  // PIN or passkey string
}
```

The phone stores this data and waits for the Android OS `PAIRING_REQUEST` broadcast to arrive. When both the AA auth data and the OS broadcast are available, `authenticateIfReady()` fires:

- **PIN method (0):** Calls `BluetoothDevice.setPin(authData)`
- **NUMERIC_COMPARISON method (2):** Compares the intent passkey with the auth data from the HU, then calls `BluetoothDevice.setPairingConfirmation()`

---

## BluetoothAuthenticationResult (0x8004)

Phone reports the outcome of the authentication attempt back to the HU.

```protobuf
message BluetoothAuthenticationResult {  // APK class: vvk (16.2)
    required int32 status            = 1;  // ProtocolStatus (vyh) — shared AA status enum
}
```

---

## SDP Configuration

### BluetoothChannelDescriptor (SDP field 6)

The BT channel is **optional** in the SDP. The HU must include a `BluetoothChannelDescriptor` at field 6 of a `ChannelDescriptor` in the `ServiceDiscoveryResponse` for BT pairing to be available.

```protobuf
message BluetoothChannelDescriptor {  // APK class: vvo
    required string adapter_address  = 1;  // HU's BT MAC address
    repeated BluetoothPairingMethod supported_pairing_methods = 2 [packed = true];
}
```

**Service availability check:** The phone checks `(service_flags & 32) != 0` (bit 5) to determine if the BT service is available. If the bit is not set: "No bluetooth service available" — BT is skipped entirely.

**Special address values:**
- Empty string: "Bluetooth address is empty" — BT skipped, initialized with SKIP state
- `"SKIP_THIS_BLUETOOTH"`: explicitly skip BT pairing

**DHU note:** The DHU 2.1 wire capture contains NO bluetooth channel in the SDP, because the DHU runs on a desktop PC without a BT adapter the HU firmware can address. Real car HUs include this descriptor.

---

## Enums

### BluetoothPairingMethod (vvl)

| Value | Name | Description |
|:-----:|------|-------------|
| -1 | BLUETOOTH_PAIRING_UNAVAILABLE | Internal sentinel — not on wire |
| 0 | BLUETOOTH_PAIRING_NONE | Default/unset |
| 1 | BLUETOOTH_PAIRING_OOB | Out-Of-Band pairing |
| 2 | BLUETOOTH_PAIRING_NUMERIC_COMPARISON | Numeric comparison (preferred) |
| 3 | BLUETOOTH_PAIRING_PASSKEY_ENTRY | Passkey entry |
| 4 | BLUETOOTH_PAIRING_PIN | Legacy PIN code |

### ProtocolStatus — BT-specific codes (vyh, shared AA status enum)

The BT channel uses the shared ProtocolStatus enum (vyh, 34 values total). BT-specific codes:

| Value | Name | Description |
|:-----:|------|-------------|
| -10 | STATUS_BLUETOOTH_PAIRING_DELAYED | Pairing delayed |
| -11 | STATUS_BLUETOOTH_UNAVAILABLE | BT adapter unavailable |
| -12 | STATUS_BLUETOOTH_INVALID_ADDRESS | Invalid BT MAC address |
| -13 | STATUS_BLUETOOTH_INVALID_PAIRING_METHOD | Unsupported pairing method |
| -14 | STATUS_BLUETOOTH_INVALID_AUTH_DATA | Invalid authentication data |
| -15 | STATUS_BLUETOOTH_AUTH_DATA_MISMATCH | Auth data does not match |
| -16 | STATUS_BLUETOOTH_HFP_ANOTHER_CONNECTION | HFP already connected to another device |
| -17 | STATUS_BLUETOOTH_HFP_CONNECTION_FAILURE | HFP connection failed |

These codes appear in `BluetoothPairingResponse` (0x8002) and `BluetoothAuthenticationResult` (0x8004) as `int32 status` fields. The old 3-value `BluetoothPairingStatus` enum was **retracted** — the wire protocol uses this shared enum instead.

---

## BT State Machine

The phone runs an 18-state state machine (`qah.java`, log tag `CAR.BT`) that drives the entire BT lifecycle from initial setup through HFP steady-state monitoring.

### States (qae)

```
STATE_INITIAL
  -> STATE_WAITING_FOR_ENDPOINT_READY        (5s timeout)
  -> STATE_WAITING_FOR_USER_AUTHORIZATION    (2min timeout, API 30+)
  -> STATE_ENABLING                          (4s timeout — enables BT adapter if off)
  -> STATE_WAITING_FOR_BLUETOOTH_PROFILE_UTIL (4s timeout)
  -> STATE_REQUESTING_CAR_PAIRING_PREPARATION (2min timeout)
  -> STATE_HFP_CONNECTION_CHECKING           (1min timeout)
  -> STATE_PREPARING_FOR_PAIRING             (10s timeout)
  -> STATE_PAIRING                           (1min on API 30+, 10s otherwise)
  -> STATE_BLUETOOTH_CONNECTING              (1min timeout)
  -> STATE_HFP_CONNECTING                    (1min timeout)
  -> STATE_HFP_CONNECTED                     (3s timeout)
  -> STATE_HFP_MONITORING                    (10s timeout — steady state)

Error states:
  -> STATE_UNPAIRING
  -> STATE_UNPAIRED
  -> STATE_FAILED
```

### Events (qad)

| Value | Event | Description |
|:-----:|-------|-------------|
| 8 | EVENT_ENABLED | BT adapter enabled |
| 13 | EVENT_PAIRED | BT bonding completed |
| 14 | EVENT_HFP_CONNECTED | HFP profile connected |
| 15 | EVENT_DISABLED | BT adapter disabled |
| 16 | EVENT_UNPAIRED | BT bond removed |
| 17 | EVENT_HFP_DISCONNECTED | HFP profile disconnected |

### Retry Logic

If HFP fails to connect **3 times** in `STATE_HFP_CONNECTING`, the phone:
1. Sets an internal flag (`f58233j`)
2. Unpairs with reason `BLUETOOTH_UNPAIR_HFP_CONNECTING_EXCEEDS_MAX_COUNT`
3. Re-attempts the full pairing cycle from scratch

### Unpair Reasons (qau)

| Reason | Trigger |
|--------|---------|
| BLUETOOTH_UNPAIR_DEFAULT | Generic unpair |
| BLUETOOTH_UNPAIR_HFP_CONNECTING_EXCEEDS_MAX_COUNT | 3 HFP connection failures |
| BLUETOOTH_UNPAIR_ALREADY_PAIRING_CANCELLING | Conflicting pairing in progress |
| BLUETOOTH_UNPAIR_PHONE_CAR_OUT_OF_SYNC | Bond state mismatch |
| BLUETOOTH_UNPAIR_AUTHENTICATION_FAILED | Auth exchange failed |
| BLUETOOTH_UNPAIR_KEY_MISSING | Missing BT link key (API 35+) |

---

## BroadcastReceivers

The BT service (`plq.java`) registers receivers for OS-level BT events at priority 999 for the pairing request:

| Intent Action | Receiver | Purpose |
|---------------|----------|---------|
| `android.bluetooth.adapter.action.STATE_CHANGED` | `qao` | BT adapter on/off |
| `android.bluetooth.device.action.PAIRING_REQUEST` | `qat` | OS pairing prompt (priority 999) |
| `android.bluetooth.device.action.BOND_STATE_CHANGED` | `qap` | Bond creation/removal |
| `android.bluetooth.headset.profile.action.CONNECTION_STATE_CHANGED` | `qar` | HFP connect/disconnect |
| `android.bluetooth.a2dp.profile.action.CONNECTION_STATE_CHANGED` | `qan` | A2DP state changes |
| `android.bluetooth.device.action.UUID` | `qaq` | SDP UUID discovery |
| `android.bluetooth.device.action.KEY_MISSING` | `qas` | Missing link key (API 35+) |

---

## HFP Profile Details

### HeadsetWrapper (qaj)

Wraps `android.bluetooth.BluetoothHeadset` for HFP management:

- `connect()` — reflective call to `BluetoothHeadset.connect()`
- `setConnectionPolicy(device, 100)` — sets high priority for auto-reconnect
- `getConnectionState()` — polls connection state (0=disconnected, 2=connected)

### HFP UUID

Standard HFP UUID: `0000111e-0000-1000-8000-00805f9b34fb`

The phone checks if the HU's BT device supports HFP before attempting connection.

### Audio Focus During Calls

When a phone call starts:
1. Android telephony sets audio mode to `MODE_IN_CALL` / `MODE_IN_COMMUNICATION`
2. The phone's audio focus manager (`plf.java`, tag `CAR.AUDIO.FOCUS`) detects this
3. AA sends `AUDIO_FOCUS_STATE_LOSS_TRANSIENT` to the HU
4. HU should pause/duck media audio
5. Call audio flows through BT HFP SCO — completely independent of AA
6. When the call ends, the phone restores audio focus after a **5-second delay**
7. HU resumes media playback

---

## Quirks and Gotchas

> **BT channel is optional.** If omitted from SDP, phone calls still work on the phone itself — just not through the car's speakers/microphone. If the HU wants HFP call audio, it MUST advertise a `BluetoothChannelDescriptor` with a valid BT MAC address.

> **Call audio never touches the AA protocol.** Once BT HFP is established, call audio is entirely OS-level. The AA protocol only carries call metadata (caller ID, state, photo) via the Phone Status channel (GAL type 13). The HU must render its own call UI from that data.

> **Pairing request receiver runs at priority 999.** The phone intercepts `PAIRING_REQUEST` at high priority to handle auth automatically. Other apps listening for pairing events may not see it.

> **API 30+ adds user authorization.** On Android 11+, there is a `STATE_WAITING_FOR_USER_AUTHORIZATION` step with a 2-minute timeout before BT operations proceed.

> **API 35+ key missing handling.** On Android 15+, a `KEY_MISSING` broadcast receiver (`qas`) handles the case where the BT link key is lost, triggering an unpair with reason `BLUETOOTH_UNPAIR_KEY_MISSING`.

> **NUMERIC_COMPARISON preferred over PIN.** The pairing method priority is hardcoded. If the HU supports both, the phone will always choose numeric comparison.

> **"SKIP_THIS_BLUETOOTH" magic string.** Setting the BT adapter address to this literal string in the SDP explicitly tells the phone to skip all BT pairing. Useful for HUs that handle BT through a separate system.

> **3 strikes and re-pair.** If HFP connection fails 3 times, the phone fully unpairs and retries the entire pairing cycle from scratch. This is not configurable.

> **5-second audio focus delay.** After a call ends, the phone waits 5 seconds before restoring AA audio focus. The HU should expect a brief silence after call termination.

---

## Implementation Notes for OpenAuto Prodigy

1. **Pi needs a BT adapter with HFP support.** The Pi 4's built-in BT works but a USB dongle may provide better range and HFP-AG (Audio Gateway) compatibility.

2. **BlueZ configuration required.** BlueZ must be configured for the HFP Audio Gateway role. The `ofono` or `hsphfpd` backend in PipeWire handles SCO audio routing.

3. **SDP must include BT descriptor.** The HU must advertise its BT MAC address and supported pairing methods in the `BluetoothChannelDescriptor` at SDP field 6. Without this, the phone will never attempt BT pairing.

4. **Handle the 4-message exchange.** The HU must:
   - Send `BluetoothPairingRequest` (0x8001) to the phone with the HU's BT MAC and pairing method
   - Send `BluetoothPairingResponse` (0x8002) with status
   - Send `BluetoothAuthenticationData` (0x8003) with the correct PIN/passkey from the OS BT stack
   - Receive `BluetoothAuthenticationResult` (0x8004) from the phone to confirm success

5. **Audio routing is OS-level after pairing.** Once HFP is established, PipeWire/PulseAudio handles SCO audio. The AA BT channel's job is done — it just bootstraps the pairing.

6. **Call UI from Phone Status channel.** Call metadata (caller ID, state, duration, contact photo) comes through the Phone Status channel (GAL type 13), not the BT channel. The HU must render its own call screen from `PhoneStatusUpdate` (0x8001 on the phone status channel).

---

## APK Source References (16.2)

| Class | Log Tag | Role |
|-------|---------|------|
| `qlg` | CAR.GAL.BT | BT channel endpoint handler — receives 0x8002/0x8003, sends 0x8004 |
| `plq` | CAR.BT.SVC | BT service — SDP processing, pairing logic, state machine owner |
| `qah` | CAR.BT | BT state machine — 18 states, event-driven transitions |
| `qav` | CAR.BT | BT utility — adapter management, authentication, BroadcastReceivers |
| `qaj` | CAR.BT.HeadsetWrapper | BluetoothHeadset wrapper — connect, policy, state polling |
| `qam` | CAR.BT | BT profile util — isConnected/isConnecting via qaj |
| `qal` | — | HFP ServiceListener |
| `qar` | — | Headset connection state receiver (HFP connect/disconnect) |
| `qao` | — | BT adapter state receiver (on/off) |
| `qap` | — | Bond state receiver (paired/unpaired) |
| `qat` | — | Pairing request receiver (priority 999) |
| `qan` | — | A2DP state receiver |
| `qaq` | — | UUID discovery receiver |
| `qas` | — | Key missing receiver (API 35+) |
| `kba` | — | BluetoothPairingRequest proto (0x8001) |
| `vvn` | — | BluetoothPairingResponse proto (0x8002) |
| `vvj` | — | BluetoothAuthenticationData proto (0x8003) |
| `vvk` | — | BluetoothAuthenticationResult proto (0x8004) |
| `vvo` | — | BluetoothChannelDescriptor proto (SDP field 6) |
| `vvl` | — | BluetoothPairingMethod enum |
| `vyh` | — | Global status enum (includes BT-specific codes) |
| `qae` | — | BT state machine states enum |
| `qad` | — | BT state machine events enum |
| `qau` | — | BT unpair reasons enum |
| `plf` | CAR.AUDIO.FOCUS | Audio focus manager — detects MODE_IN_CALL |
| `pzq` | CAR.AUDIO | TelephonyManager call state monitor |
| `pzp` | — | PhoneStateListener — call start/end detection |
