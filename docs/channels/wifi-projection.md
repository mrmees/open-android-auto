# WiFi Projection Protocol (WPP)

## Overview

Wireless Android Auto uses a two-channel architecture to establish projection over WiFi. The phone discovers the head unit via Bluetooth SDP (not mDNS), negotiates WiFi credentials over an RFCOMM link, then transitions to a TCP connection for the actual AA session.

The connection pipeline: BT pair → SDP discovery (UUID `4de17a00-52cb-11e6-bdf4-0800200c9a66`) → RFCOMM connect → WPP version negotiation → WiFi credential exchange → phone joins HU's AP → TCP connect → TLS handshake (phone=server, HU=client) → normal AA framing begins.

WPP defines 11 message types (3 deprecated) with its own wire format distinct from the normal AA 4-byte header. After the WPP handshake completes and the TCP+TLS socket is established, the protocol transitions to standard AA framing and the rest of the session is identical to USB.

---

## Message Catalog

| Msg ID | Direction | Proto Class (16.2) | Name | Purpose |
|--------|-----------|-------------------|------|---------|
| 1 | HU → Phone | `wdj` | WifiStartRequest | HU tells phone its IP/port and start reason |
| 2 | Phone → HU | `wdb` | WifiInfoRequest | Phone requests WiFi AP credentials (DEPRECATED) |
| 3 | HU → Phone | `wdc` | WifiInfoResponse | HU sends WiFi SSID/password/security (DEPRECATED) |
| 4 | HU → Phone | `wdl` | WifiVersionRequest | HU sends WPP version and device info |
| 5 | Phone → HU | `wdm` | WifiVersionResponse | Phone replies with version status and device info |
| 6 | Phone → HU | `wcz` | WifiConnectStatus | Phone reports WiFi connection status (DEPRECATED) |
| 7 | HU → Phone | `wdk` | WifiStartResponse | HU confirms start with IP/port and status |
| 8 | Phone → HU | `wde` | WifiPingRequest | Phone sends keepalive ping with timestamp |
| 9 | HU → Phone | `wdf` | WifiPingResponse | HU echoes timestamp back |
| 10 | HU → Phone | `wda` | WifiConnectionRejection | HU rejects connection (TCP only) |
| 11 | HU → Phone | `wdi` | WifiSetupInfo | HU sends WiFi AP info (replaces deprecated msgs 2/3) |

---

## Wire Format

WPP uses its own framing, distinct from the normal AA wire protocol:

```
[2 bytes: payload_length (big-endian)] [2 bytes: message_type (big-endian)] [protobuf payload]
```

Compare to normal AA framing: `[1B channel][1B flags][2B length][payload]`.

The same WPP wire format is used on both RFCOMM and TCP channels. After the WPP handshake completes and projection launches, the TCP socket transitions to standard AA framing.

Ping messages (types 8/9) are exempt from fault injection monitoring.

---

## Connection Flow

### Phase 0: Bluetooth Discovery

The phone does NOT use mDNS/NSD for wireless AA. Discovery is purely via Bluetooth SDP.

1. Phone pairs with HU via standard Bluetooth (HFP/A2DP profiles)
2. `WifiBluetoothReceiver` listens for ACL_CONNECTED, HFP/A2DP state changes, bond state changes, and the `START_WIRELESS_PROJECTION` intent
3. SDP manager (`nsf`) checks if the paired device advertises UUID `4de17a00-52cb-11e6-bdf4-0800200c9a66`
4. If UUID found: starts `WirelessSetupSharedService`

### Phase 1: RFCOMM Connection

Phone creates an RFCOMM socket to the HU using `createRfcommSocketToServiceRecord(UUID)`. Bluetooth discovery is cancelled first. State transitions: `CONNECTING_RFCOMM` → `CONNECTED_RFCOMM`.

### Phase 2: Version Negotiation (over RFCOMM)

```
HU  ──MSG 4: WifiVersionRequest──▷  Phone
    (majorVersion, minorVersion, supportedWifiChannels, headUnitDeviceInfo, wifiDirectGroupInfo)

Phone  ──MSG 5: WifiVersionResponse──▷  HU
    (majorVersion, minorVersion, deviceSerial, versionStatus=SUCCESS, selectedWifiChannelType, mobileDeviceInfo)
```

Phone validates version compatibility and determines status: `COMPATIBLE`, `COMPATIBLE_WITH_CHANNELS`, or `INCOMPATIBLE`. State → `VERSION_CHECK_COMPLETE`.

### Phase 3: WiFi Credential Exchange (over RFCOMM)

**Current path** — HU sends SetupInfo:

```
HU  ──MSG 11: WifiSetupInfo──▷  Phone
    (majorVersion, minorVersion, wifiDirectGroupInfo, accessPointInfo with SSID/password/security/channels)
```

**Legacy path** (deprecated, used when SetupInfo not supported):

```
Phone  ──MSG 2: WifiInfoRequest──▷  HU     (empty message)
HU     ──MSG 3: WifiInfoResponse──▷  Phone  (ssid, bssid, password, securityMode, accessPointType)
```

### Phase 4: Start Request (over RFCOMM)

```
HU  ──MSG 1: WifiStartRequest──▷  Phone
    (ipAddress, port, start_reason)
```

Phone stores the HU's TCP endpoint. State → `WIFI_PROJECTION_START_REQUESTED`.

### Phase 5: WiFi Network Connection

Phone connects to the HU's WiFi AP using credentials from Phase 3. On Android 11+ (SDK 30), uses `ConnectivityManager.requestNetwork()` with the full WiFi config (SSID, password, security). On older versions, expects the phone to already be connected. State transitions: `CONNECTING_WIFI` → `CONNECTED_WIFI`.

### Phase 6: Start Response (over RFCOMM or TCP)

```
HU  ──MSG 7: WifiStartResponse──▷  Phone
    (ipAddress, port, messageStatus=SUCCESS)
```

On `ALREADY_STARTED` or `NOT_YET_STARTED`: schedules retry with exponential backoff.
On `WIFI_DISABLED`: transitions to `START_WIFI_REQUEST_FAILED_WIFI_DISABLED`.

### Phase 7: TCP + TLS Connection

1. Phone opens TCP socket to HU at `ipAddress:port` (10s connect timeout)
2. Socket is wrapped in SSL/TLS:
   - **Phone acts as TLS SERVER** (`setUseClientMode(false)`)
   - **Mutual TLS** (`setNeedClientAuth(true)`) — both sides present certificates
   - Uses GmsCore OpenSSL provider
3. WPP read/write threads start on the TCP socket
4. WPP ping monitoring begins

**Key insight**: The TLS roles are reversed from what you might expect. The phone initiated the TCP connection but acts as the TLS server. The HU is the TLS client.

### Phase 8: Projection Launch

After TCP+TLS is established, `WirelessStartupActivity` launches with action `com.google.android.gms.car.WIFI_ACTION_BRIDGE`. From this point, normal AA framing (`[1B channel][1B flags][2B length][payload]`) begins over the TCP+TLS socket. The session is identical to USB from here on.

WPP ping messages continue alongside AA data for connection health monitoring.

---

## WifiVersionRequest (msg 4)

```protobuf
message WifiVersionRequest {          // APK class: wdl
    optional int32 majorVersion                  = 2;
    optional int32 minorVersion                  = 3;
    optional WifiChannelType selectedWifiChannelType = 4;  // enum
    repeated bytes supportedWifiChannels          = 5;
    optional HeadUnitDeviceInfo headUnitDeviceInfo = 6;
    optional WifiDirectGroupInfo wifiDirectGroupInfo = 7;
}
```

---

## WifiVersionResponse (msg 5)

```protobuf
message WifiVersionResponse {         // APK class: wdm
    optional int32 majorVersion                  = 2;
    optional int32 minorVersion                  = 3;
    optional string deviceSerial                 = 4;
    optional WppStatus versionStatus             = 5;  // enum
    optional WifiChannelType selectedWifiChannelType = 6;  // enum
    optional MobileDeviceInfo mobileDeviceInfo   = 7;
    optional bytes unknown_field_8               = 8;
}
```

---

## WifiSetupInfo (msg 11)

Replaces the deprecated WifiInfoRequest/WifiInfoResponse pair.

```protobuf
message WifiSetupInfo {               // APK class: wdi
    optional int32 majorVersion                  = 2;
    optional int32 minorVersion                  = 3;
    optional bytes unknown_field_4               = 4;
    optional WifiDirectGroupInfo wifiDirectGroupInfo = 5;
    optional AccessPointInfo accessPointInfo      = 6;
}
```

---

## WifiStartRequest (msg 1)

```protobuf
message WifiStartRequest {            // APK class: wdj
    optional string ipAddress    = 2;  // HU's IP for TCP connection
    optional int32  port         = 3;  // TCP port for AA projection
    optional StartReason start_reason = 4;  // enum
}
```

---

## WifiStartResponse (msg 7)

```protobuf
message WifiStartResponse {           // APK class: wdk
    optional string ipAddress    = 2;  // HU's IP for TCP connection
    optional int32  port         = 3;  // TCP port
    optional WppStatus messageStatus = 4;  // enum
}
```

---

## WifiPingRequest (msg 8)

```protobuf
message WifiPingRequest {             // APK class: wde
    optional int64 timestampMs   = 2;  // epoch millis when sent
}
```

---

## WifiPingResponse (msg 9)

```protobuf
message WifiPingResponse {            // APK class: wdf
    optional int64 timestampMs   = 2;  // echoed back from request
}
```

Phone calculates RTT from the echoed timestamp. Warns if latency is high. After 10 missed ping responses, the connection is considered dead (`WPP_PING_TIMEOUT`).

---

## WifiConnectionRejection (msg 10)

**Sent over TCP only.** Attempting to send this over RFCOMM throws `IllegalStateException`.

```protobuf
message WifiConnectionRejection {     // APK class: wda
    optional ConnectionRejectionReason rejectionReason = 2;  // enum
}
```

---

## Deprecated Messages

### WifiInfoRequest (msg 2)

```protobuf
message WifiInfoRequest {             // APK class: wdb
    // empty message — phone requests HU's WiFi AP info
}
```

### WifiInfoResponse (msg 3)

```protobuf
message WifiInfoResponse {            // APK class: wdc
    optional string wifiSsid             = 2;
    optional string wifiBssid            = 3;
    optional string wifiPassword         = 4;
    optional WifiSecurityMode wifiSecurityMode = 5;  // enum
    optional AccessPointType accessPointType   = 6;  // enum
}
```

### WifiConnectStatus (msg 6)

```protobuf
message WifiConnectStatus {           // APK class: wcz
    optional WppStatus connectStatus     = 2;  // enum (default: 1)
    optional string errorMessageHint     = 3;
}
```

---

## Sub-Messages

### HeadUnitDeviceInfo

```protobuf
message HeadUnitDeviceInfo {          // APK class: vuq
    optional int32  unknown_int_1    = 1;   // possibly device_type
    optional string device_string_1  = 2;   // likely manufacturer, model, HW version,
    optional string device_string_2  = 3;   //   SW version, serial, etc.
    optional string device_string_3  = 4;   //   9 string fields — exact semantics
    optional string device_string_4  = 5;   //   not confirmed from APK alone
    optional string device_string_5  = 6;
    optional string device_string_6  = 7;
    optional string device_string_7  = 8;
    optional string device_string_8  = 9;
    optional int32  unknown_int_2    = 10;
}
```

### MobileDeviceInfo

```protobuf
message MobileDeviceInfo {            // APK class: vur
    optional int32  unknown_int_1    = 1;   // possibly device_type
    optional string device_string_1  = 2;
    optional string device_string_2  = 3;
    optional string device_string_3  = 4;
    optional string device_string_4  = 5;
}
```

### WifiDirectGroupInfo

```protobuf
message WifiDirectGroupInfo {         // APK class: wdg
    optional string group_name       = 2;   // group name / SSID
    optional int32  group_channel    = 3;   // channel or frequency
}
```

### AccessPointInfo

```protobuf
message AccessPointInfo {             // APK class: wcy
    optional string ssid                         = 2;
    optional string bssid                        = 3;
    optional string password                     = 4;
    optional WifiSecurityMode wifiSecurityMode   = 5;   // enum
    repeated bytes supportedWifiChannels          = 6;
}
```

---

## Enums

### WppStatus (shared across multiple messages)

| Value | Name |
|:-----:|------|
| 0/13 | UNKNOWN |
| 6 | START_WIFI_NOT_YET_STARTED |
| 7 | START_WIFI_DISABLED |
| 8 | START_WIFI_ALREADY_STARTED |
| 12 | SUCCESS |

### WifiSecurityMode (`wdh`)

| Value | Name |
|:-----:|------|
| 0 | UNKNOWN_SECURITY_MODE |
| 1 | OPEN |
| 2 | WEP_64 |
| 3 | WEP_128 |
| 4 | WPA_PERSONAL |
| 8 | WPA2_PERSONAL |
| 12 | WPA_WPA2_PERSONAL |
| 20 | WPA_ENTERPRISE |
| 24 | WPA2_ENTERPRISE |
| 28 | WPA_WPA2_ENTERPRISE |
| 32 | WPA3_PERSONAL |
| 40 | WPA2_WPA3_PERSONAL |

### WifiChannelType

| Value | Name |
|:-----:|------|
| 0/1 | CHANNELS_5GHZ_ONLY |
| 2 | CHANNELS_24GHZ_ONLY |
| 3 | CHANNELS_DUAL_BAND |
| else | NO_CHANNELS_SUPPORTED |

### StartReason

| Value | Name |
|:-----:|------|
| 0/1 | USER_REQUEST |
| 2 | AUTO_LAUNCH |
| 3 | AUTOMATIC_RESTART |

### AccessPointType

| Value | Name |
|:-----:|------|
| 0/1 | STATIC |
| 2 | DYNAMIC |

### ConnectionRejectionReason

| Value | Name |
|:-----:|------|
| 0/1 | UNKNOWN |
| 2 | MOBILE_DEVICE_ID_NOT_FOUND |
| 3 | INVALID_SETUP_TOKEN |

---

## Connection State Machine (`nud`)

35 states total. Negative = error, 0 = idle, positive = progress. States marked `(active)` keep the service alive.

### Progress States

| Value | Name | Active |
|:-----:|------|:------:|
| 0 | IDLE | |
| 1 | BT_HFP_A2DP_CONNECTED | |
| 3 | CONNECTING_RFCOMM | |
| 5 | CONNECTED_RFCOMM | yes |
| 6 | CONNECTING_WIFI | yes |
| 7 | CONNECTED_WIFI | yes |
| 8 | PROJECTION_INITIATED | yes |
| 9 | VERSION_CHECK_COMPLETE | yes |
| 10 | SHUTDOWN | |
| 11 | FOUND_COMPATIBLE_WIFI_NETWORK | yes |
| 12 | PROJECTION_IN_PROGRESS | yes |
| 14 | WIFI_CONNECT_TIMED_OUT | |
| 15 | PROJECTION_START_TIMED_OUT | |
| 16 | PROJECTION_ENDED | |
| 17 | START_WIFI_REQUEST_SUCCESS | yes |
| 18 | START_WIFI_REQUEST_FAILED_ALREADY_STARTED | |
| 19 | START_WIFI_REQUEST_FAILED_WIFI_DISABLED | |
| 20 | START_WIFI_REQUEST_FAILED_WIFI_NOT_YET_STARTED | |
| 21 | START_WIFI_REQUEST_FAILED_INVALID_CREDENTIALS | |
| 22 | PROJECTION_CONNECTED | yes |
| 23 | PROJECTION_DISCONNECTED | |
| 24 | WIFI_PROJECTION_START_REQUESTED | yes |
| 25 | WIFI_AUTOMATICALLY_ENABLED | |
| 26 | WIFI_PROJECTION_RESTART_REQUESTED | yes |
| 32 | MD_USER_REQUEST_BYE_BYE_INITIATED_WIFI_DISCONNECT | |
| 33 | USER_REJECT_WIFI_UNAVAILABLE | |
| 34 | USER_DISCONNECTED_ANOTHER_NETWORK_CONNECTED | |
| 35 | USER_DISCONNECTED_FROM_WIFI_NETWORK | |
| 36 | USER_DISCONNECTED_MD_WIFI_ADAPTER_OFF | |

### Error States

| Value | Name |
|:-----:|------|
| -20 | WIFI_INVALID_PROJECTION_ENDPOINT |
| -19 | WIFI_INVALID_WPP_ENDPOINT |
| -18 | WIFI_CONNECTION_SETUP_FAILED |
| -17 | WIFI_INVALID_SSID |
| -16 | WIFI_INVALID_BSSID |
| -15 | WIFI_INVALID_PASSWORD |
| -14 | WIFI_INACCESSIBLE_CHANNEL |
| -13 | NO_COMPATIBLE_WIFI_VERSION_FOUND |
| -12 | NO_COMPATIBLE_WIFI_CHANNEL_FOUND |
| -11 | DISCONNECTED_BT |
| -10 | ABORTED_WIFI |
| -9 | RECONNECTION_PREVENTED |
| -8 | BT_HFP_A2DP_DISCONNECTED |
| -7 | CONNECTION_LOST_BT |
| -5 | RFCOMM_READ_WRITE_FAILURE |
| -3 | WIFI_INVALID_CREDENTIALS |
| -2 | WIFI_SECURITY_NOT_SUPPORTED |
| -1 | WIFI_FAILED_TO_AUTOMATICALLY_ENABLE |

---

## Connection Failure Reasons (`ntl`)

29 failure codes used by the retry logic. Most trigger a retry with configurable delay; some are terminal.

### Transport Failures

| ID | Name | Retry Delay |
|:--:|------|-------------|
| 0 | RFCOMM_SOCKET_CONNECTION_FAILED | configurable |
| 1 | TCP_SOCKET_CONNECTION_FAILED | immediate |
| 2 | GAL_SOCKET_CONNECTION_FAILED | configurable |

### WPP Protocol Failures

| ID | Name | Retry Delay |
|:--:|------|-------------|
| 3 | WPP_SOCKET_IO_EXCEPTION | configurable |
| 4 | WPP_SOCKET_CLOSED_BY_PEER | configurable |
| 5 | WPP_CONNECTION_MISSING_WIFI_INFO_RESPONSE | configurable |
| 6 | WPP_CONNECTION_MISSING_WIFI_START_RESPONSE | configurable |
| 7 | WPP_CONNECTION_FIRST_MESSAGE_TIMEOUT | configurable |
| 8 | WPP_PING_TIMEOUT | configurable |

### WiFi Direct / Local-Only Failures

| ID | Name | Retry Delay |
|:--:|------|-------------|
| 9 | LOCAL_ONLY_CONNECTION_FAILURE_REASON_UNKNOWN | configurable (separate) |
| 10 | LOCAL_ONLY_CONNECTION_FAILURE_REASON_ASSOCIATION | configurable (separate) |
| 11 | LOCAL_ONLY_CONNECTION_FAILURE_REASON_AUTHENTICATION | configurable (separate) |
| 12 | LOCAL_ONLY_CONNECTION_FAILURE_REASON_IP_PROVISIONING | configurable (separate) |
| 13 | LOCAL_ONLY_CONNECTION_FAILURE_REASON_NOT_FOUND | configurable (separate) |
| 14 | LOCAL_ONLY_CONNECTION_FAILURE_REASON_NO_RESPONSE | configurable (separate) |
| 15 | LOCAL_ONLY_CONNECTION_FAILURE_REASON_USER_REJECT | configurable (separate) |

### Network Failures

| ID | Name | Retry Delay |
|:--:|------|-------------|
| 16 | NETWORK_UNAVAILABLE_HANDSHAKE_FAILED | configurable |
| 17 | NETWORK_UNAVAILABLE_NETWORK_NOT_FOUND | configurable |
| 18 | NETWORK_UNAVAILABLE_WIFI_ADAPTER_FAILED_TO_ENABLE | configurable |
| 19 | NETWORK_UNAVAILABLE_OTHER | configurable |
| 20 | NETWORK_LOST | configurable |

### HU Rejection

| ID | Name | Retry Delay |
|:--:|------|-------------|
| 21 | HEAD_UNIT_REJECTED_CONNECTION_MOBILE_DEVICE_ID_NOT_FOUND | immediate |
| 22 | HEAD_UNIT_REJECTED_CONNECTION_INVALID_TOKEN | immediate |
| 23 | RECEIVED_WIFI_SETUP_INFO | immediate (triggers reconnect) |

### WiFi Direct Disconnection

| ID | Name |
|:--:|------|
| 24 | LOCAL_ONLY_DISCONNECTION_REASON_UNKNOWN |
| 25 | LOCAL_ONLY_DISCONNECTION_REASON_DISCONNECT_API |
| 26 | LOCAL_ONLY_DISCONNECTION_REASON_NEW_CONNECTION |
| 27 | LOCAL_ONLY_DISCONNECTION_REASON_DISABLE_WIFI |
| 28 | LOCAL_ONLY_DISCONNECTION_REASON_AIRPLANE_MODE_ON |

---

## Quirks and Gotchas

> **No mDNS**: The Google AA implementation discovers wireless HUs exclusively via Bluetooth SDP. Some third-party dongles (e.g., AAWireless) use mDNS, but the phone-side code does not.

> **TLS roles are reversed**: Despite the phone initiating the TCP connection, the phone acts as the TLS server (`setUseClientMode(false)`) and the HU acts as the TLS client. Mutual TLS is required — both sides present certificates.

> **Wire format changes mid-session**: WPP messages use `[2B length][2B msg_type][payload]`. After the WPP handshake completes and projection launches, the same TCP socket transitions to standard AA framing `[1B channel][1B flags][2B length][payload]`. WPP pings continue alongside AA data using the WPP format.

> **WifiConnectionRejection is TCP-only**: Sending msg 10 over RFCOMM throws `IllegalStateException`. The HU must only send rejections after the TCP connection is established.

> **3 deprecated messages**: WifiInfoRequest (2), WifiInfoResponse (3), and WifiConnectStatus (6) are from an older protocol version. The current path uses WifiVersionRequest/Response + WifiSetupInfo. An HU implementation should support both paths for compatibility with older phones.

> **WiFi Direct is an alternative**: `WifiDirectGroupInfo` in WifiVersionRequest and WifiSetupInfo indicates the HU can operate as a WiFi Direct Group Owner instead of a standard WiFi AP. The `LOCAL_ONLY_*` failure codes in `ntl` handle WiFi Direct-specific failure modes.

> **Ping timeout threshold**: 10 missed ping responses triggers `WPP_PING_TIMEOUT`. First message timeout is 10 seconds by default (configurable).

> **RFCOMM sleep-instead-of-flush**: On SDK 30+, the RFCOMM socket has an optional mode where it sleeps for a configurable delay instead of flushing the output stream.

> **Phone-side analysis only**: This research is from the phone APK. The HU must: advertise the AA UUID in BT SDP, accept RFCOMM connections, implement WPP message handling, create a WiFi AP (or WiFi Direct group), listen on a TCP port, act as TLS CLIENT, and transition to normal AA protocol after the bridge is established.

---

## Log Tags

| Tag | Class | Role |
|-----|-------|------|
| `GH.WirelessShared` | WirelessSetupSharedService | Top-level service |
| `GH.WirelessFSM` | WirelessStartupActivity | Launches projection |
| `GH.WIRELESS.BT` | `nxz` | RFCOMM BT connection manager |
| `GH.WPP.RFCOMM` | `oci` | RFCOMM socket/transport |
| `GH.WPP.TCP` | `nzl` | TCP connection manager |
| `GH.WPP.SOCKET` | `ocn` | TCP socket/transport |
| `GH.WPP.TRANSPORT` | `oco` | Shared transport (read/write loop) |
| `GH.WPP.SSL` | `ocp` | SSL certificate provider/verifier |
| `GH.WirelessNetRequest` | `nww` | WiFi network request manager |
| `GH.WSR` | WirelessStartupReceiver | Intent receiver |
| `Wifi.GalMonitor` | — | GAL fault injection monitor |

---

## APK Source References (16.2)

| Class | Role |
|-------|------|
| `obe` | WirelessSetupEventManager — core state machine |
| `oap` | WPP message handler (inner class of `obe`) |
| `oas` | Network callback handler (WiFi connected → launch TCP) |
| `nzl` | WifiProjectionProtocolOnTcpManager (TCP connection manager) |
| `nzg` | Main Runnable dispatcher (20 case switch) |
| `nxz` | Bluetooth RFCOMM connection manager |
| `oci` | RFCOMM socket wrapper (BluetoothSocket) |
| `ocn` | TCP socket wrapper (java.net.Socket) |
| `oce` | WifiProjectionProtocolBaseConnection (manages r/w threads) |
| `oco` | WifiProjectionProtocolTransportImpl (read/write loop) |
| `nww` | LegacyNetworkRequestManager (WiFi via ConnectivityManager) |
| `nwe` | Network availability monitor (SDK 29+) |
| `nbw` | Utility class (message defaults, SSL creation, logging) |
| `wdd` | WPP message type enum (11 values) |
| `nud` | Connection state enum (35 values) |
| `ntl` | Connection failure reason enum (29 values) |
| `wdh` | WifiSecurityMode enum |
| `wcc` | Enum verifier registry |
| `ijz` | AA UUID constant |
| `nsf` | SDP manager (checks for AA UUID in BT SDP records) |
| `wdj` | WifiStartRequest proto (msg 1) |
| `wdb` | WifiInfoRequest proto (msg 2, deprecated) |
| `wdc` | WifiInfoResponse proto (msg 3, deprecated) |
| `wdl` | WifiVersionRequest proto (msg 4) |
| `wdm` | WifiVersionResponse proto (msg 5) |
| `wcz` | WifiConnectStatus proto (msg 6, deprecated) |
| `wdk` | WifiStartResponse proto (msg 7) |
| `wde` | WifiPingRequest proto (msg 8) |
| `wdf` | WifiPingResponse proto (msg 9) |
| `wda` | WifiConnectionRejection proto (msg 10) |
| `wdi` | WifiSetupInfo proto (msg 11) |
| `vuq` | HeadUnitDeviceInfo sub-message |
| `vur` | MobileDeviceInfo sub-message |
| `wdg` | WifiDirectGroupInfo sub-message |
| `wcy` | AccessPointInfo sub-message |
