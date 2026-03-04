# 05 — Session Maintenance and Teardown

## Proto Confidence Summary

| Message | Tier | Evidence | Audit File |
|---------|------|----------|------------|
| PingRequest | Silver | apk_static + cross_version | [PingRequestMessage.audit.yaml](../../oaa/control/PingRequestMessage.audit.yaml) |
| PingResponse | Silver | apk_static + cross_version | [PingResponseMessage.audit.yaml](../../oaa/control/PingResponseMessage.audit.yaml) |
| GalPingRequest | Silver | apk_static + cross_version | [GalPingRequestMessage.audit.yaml](../../oaa/control/GalPingRequestMessage.audit.yaml) |
| GalPingResponse | Silver | apk_static + cross_version | [GalPingResponseMessage.audit.yaml](../../oaa/control/GalPingResponseMessage.audit.yaml) |
| ShutdownRequest | Silver | apk_static + cross_version | [ShutdownRequestMessage.audit.yaml](../../oaa/control/ShutdownRequestMessage.audit.yaml) |
| ShutdownResponse | Unverified | -- | -- |
| ShutdownReason | Unverified | -- | -- |
| ByeByeResponse | Bronze | apk_static | [ByeByeResponseMessage.audit.yaml](../../oaa/control/ByeByeResponseMessage.audit.yaml) |
| PingConfiguration | Unverified | -- | -- |
| DisconnectReason | Unverified | -- | -- |

## Overview

After channels are open and AV data is flowing (see [04-channel-lifecycle](04-channel-lifecycle.md)), two mechanisms keep the session alive: AA-level ping/pong messages and TCP-level keepalive probes. When either side wants to end the session, a shutdown handshake provides graceful teardown.

Two distinct ping mechanisms operate at different protocol layers. Understanding which is which is critical for a correct implementation.

## Prerequisites

- All channels open and configured (from [04-channel-lifecycle](04-channel-lifecycle.md))
- AV streaming active (video, audio flowing)
- TLS encryption established on the AA protocol channel
- Service discovery complete (ping configuration received)

---

## Session Maintenance (Keepalive)

### Ping Mechanism Comparison

| Property | PingRequest / PingResponse | GalPingRequest / GalPingResponse |
|----------|---------------------------|----------------------------------|
| Message IDs | 0x000b / 0x000c | 0x000b / 0x000c |
| Protocol layer | AA control channel (encrypted via TLS) | GAL transport layer (plaintext) |
| Timestamp field | `optional int64` | `required int64` |
| Additional fields | `ping_flags` (int32, observed always 0) | `flag` (optional bool), `payload` (optional bytes) |
| Proto syntax | proto2 | proto2 |
| Differentiation | Sent inside the TLS tunnel | Sent outside the TLS tunnel, at the GAL framing layer |

> **Gotcha:** Both ping mechanisms share message IDs 0x000b and 0x000c. They are distinguished by protocol layer:
> PingRequest/Response travel inside the encrypted AA control channel, while GalPingRequest/Response
> travel at the plaintext GAL transport layer. Parse the correct proto structure based on which layer
> the message arrives on.

---

### PingRequest / PingResponse (AA Control Channel)

> Confidence: Silver [apk_static + cross_version] -- see [PingRequestMessage.audit.yaml](../../oaa/control/PingRequestMessage.audit.yaml)

These messages travel on the AA control channel (channel 0) inside the TLS tunnel. Either side may initiate a ping.

#### Message Structure

```protobuf
// oaa/control/PingRequestMessage.proto
// confidence: silver [apk_static, cross_version]
message PingRequest {
    optional int64 timestamp = 1;
    optional int32 ping_flags = 2;  // enum verifier (0-19 values); observed always 0
}
```

```protobuf
// oaa/control/PingResponseMessage.proto
// confidence: silver [apk_static, cross_version]
message PingResponse {
    optional int64 timestamp = 1;
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `PingRequest.timestamp` | optional int64 | Timestamp for round-trip latency measurement. Echoed in response. |
| `PingRequest.ping_flags` | optional int32 | APK defines an enum verifier with values 0-19. In all observed captures, this field is 0. Purpose unknown. |
| `PingResponse.timestamp` | optional int64 | Echo of the request timestamp. |

#### Wire Format

- **Message ID:** 0x000b (PING_REQUEST), 0x000c (PING_RESPONSE)
- **Channel:** 0 (control)
- **Message type:** Control
- **Encryption:** Yes (inside TLS tunnel)

---

### GalPingRequest / GalPingResponse (GAL Transport Layer)

> Confidence: Silver [apk_static + cross_version] -- see [GalPingRequestMessage.audit.yaml](../../oaa/control/GalPingRequestMessage.audit.yaml)

These messages operate at the GAL (Google Automotive Link) transport layer, outside the TLS tunnel. They serve as a lower-level keepalive that monitors the underlying transport connection.

#### Message Structure

```protobuf
// oaa/control/GalPingRequestMessage.proto
// confidence: silver [apk_static, cross_version]
message GalPingRequest {
    required int64 timestamp = 1;
    optional bool flag = 2;
    optional bytes payload = 3;
}
```

```protobuf
// oaa/control/GalPingResponseMessage.proto
// confidence: silver [apk_static, cross_version]
message GalPingResponse {
    required int64 timestamp = 1;
    optional bytes payload = 2;
}
```

> **Gotcha:** `GalPingRequest.timestamp` is `required` (not `optional`), which is unusual for AA messages.
> Most AA proto fields are optional. Omitting the timestamp will cause a parse error on the phone side.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `GalPingRequest.timestamp` | required int64 | Timestamp for latency measurement. Must be present. |
| `GalPingRequest.flag` | optional bool | Purpose not yet determined from APK analysis. |
| `GalPingRequest.payload` | optional bytes | May carry diagnostic data. Not observed in practice. |
| `GalPingResponse.timestamp` | required int64 | Echo of the request timestamp. Must be present. |
| `GalPingResponse.payload` | optional bytes | May echo request payload or carry diagnostic data. |

#### Wire Format

- **Message ID:** 0x000b (PING_REQUEST), 0x000c (PING_RESPONSE)
- **Layer:** GAL transport framing
- **Encryption:** No (plaintext, outside TLS)

---

### PingConfiguration

> Confidence: Unverified

Ping timing parameters are delivered during service discovery, embedded in `ConnectionConfiguration` (field 1 of `ConnectionConfiguration`, which is field 16 of `ServiceDiscoveryResponse`).

```protobuf
// oaa/common/PingConfigurationData.proto
// confidence: unverified
message PingConfiguration {
    optional int64 ping_interval_ns = 1;  // Interval between pings, in nanoseconds
    optional int32 ping_timeout_ms = 2;   // Timeout for ping response, in milliseconds
}
```

These fields define the expected ping cadence and timeout threshold. The exact values sent by production phones have not been verified. Implementations should read these values from the service discovery response and use them to configure their ping timer and timeout detection.

> **Note:** The field names suggest nanosecond precision for the interval and millisecond precision for the timeout. The disparity in units is present in the APK source.

---

### TCP Keepalive

Independent of the AA-level ping mechanisms, the TCP transport layer uses OS-level keepalive probes:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `TCP_KEEPIDLE` | 5 seconds | Time before first keepalive probe after idle |
| `TCP_KEEPINTVL` | 3 seconds | Interval between subsequent probes |
| `TCP_KEEPCNT` | 3 | Number of failed probes before connection drop |

These are transport-level parameters observed in captured sessions. They detect dead TCP connections independently of the AA protocol. A failed TCP keepalive results in the OS closing the socket, which the application detects as a connection error.

---

### Implementation Guidance -- Ping Handling

```c
// Respond to an incoming PingRequest by echoing the timestamp
void handle_ping_request(const PingRequest* request) {
    PingResponse response = PING_RESPONSE__INIT;

    if (request->has_timestamp) {
        response.has_timestamp = 1;
        response.timestamp = request->timestamp;
    }

    send_control_message(CONTROL_MSG_PING_RESPONSE, &response);
}

// Respond to an incoming GalPingRequest (GAL transport layer)
void handle_gal_ping_request(const GalPingRequest* request) {
    GalPingResponse response = GAL_PING_RESPONSE__INIT;

    // timestamp is required -- always echo it
    response.timestamp = request->timestamp;

    if (request->has_payload) {
        response.has_payload = 1;
        response.payload = request->payload;
    }

    send_gal_message(GAL_MSG_PING_RESPONSE, &response);
}

// Proactive ping with timeout detection
void send_ping(int64_t now_ns) {
    PingRequest request = PING_REQUEST__INIT;
    request.has_timestamp = 1;
    request.timestamp = now_ns;

    send_control_message(CONTROL_MSG_PING_REQUEST, &request);

    // Start timeout timer using PingConfiguration values
    // If no PingResponse arrives within ping_timeout_ms, consider the
    // session unresponsive and initiate shutdown.
}
```

---

## Session Teardown (Shutdown)

### Sequence Diagram

```
Initiator (Phone or HU)              Responder (Phone or HU)
  |                                     |
  |--- ShutdownRequest (0x000f) ------->|  Contains: ShutdownReason
  |<-- ShutdownResponse (0x0010) -------|  Empty acknowledgment
  |                                     |
  |     [ Close TLS session ]           |
  |     [ Close transport (TCP/USB) ]   |
  |                                     |
```

Either side may initiate shutdown. The initiator sends `ShutdownRequest` with a reason, the responder acknowledges with `ShutdownResponse`, and both sides tear down the connection.

---

### ShutdownRequest (0x000f)

> Confidence: Silver [apk_static + cross_version] -- see [ShutdownRequestMessage.audit.yaml](../../oaa/control/ShutdownRequestMessage.audit.yaml)

```protobuf
// oaa/control/ShutdownRequestMessage.proto
// confidence: silver [apk_static, cross_version]
message ShutdownRequest {
    optional enums.ShutdownReason.Enum reason = 1;
}
```

Sent on channel 0 with `MessageType::Control`. The `reason` field indicates why the session is being terminated.

---

### ShutdownReason Enum

> Confidence: Unverified

```protobuf
// oaa/control/ShutdownReasonEnum.proto
// confidence: unverified
message ShutdownReason {
    enum Enum {
        NONE = 0;
        USER_SELECTION = 1;
        DEVICE_SWITCH = 2;
        NOT_SUPPORTED = 3;
        NOT_CURRENTLY_SUPPORTED = 4;
        PROBE_SUPPORTED = 5;
        WIRELESS_PROJECTION_DISABLED = 6;
        POWER_DOWN = 7;
        USER_PROFILE_SWITCH = 8;
    }
}
```

| Value | Name | Description |
|-------|------|-------------|
| 0 | `NONE` | No specific reason provided. Default value. |
| 1 | `USER_SELECTION` | User explicitly ended the AA session (e.g., tapped "Exit" in the HU UI). |
| 2 | `DEVICE_SWITCH` | Switching to a different connected device. |
| 3 | `NOT_SUPPORTED` | The connected device or feature is not supported. |
| 4 | `NOT_CURRENTLY_SUPPORTED` | The feature is known but not available at this time. |
| 5 | `PROBE_SUPPORTED` | Present in APK, not observed in practice. Suggests a capability probing mechanism. |
| 6 | `WIRELESS_PROJECTION_DISABLED` | Wireless projection has been disabled (settings change or policy). |
| 7 | `POWER_DOWN` | The HU or device is powering down (e.g., ignition off). |
| 8 | `USER_PROFILE_SWITCH` | User profile switch on the HU (multi-user support). |

Values 0-4 and 7 represent common shutdown scenarios. Values 5, 6, and 8 suggest features beyond basic AA (wireless projection management, multi-user HU support) and have not been observed in captured sessions.

> **Note:** The plan frontmatter originally referenced QUIT_APPLICATION, USB_REMOVED, and POWER_DOWN as values 1-4.
> The actual proto enum uses USER_SELECTION, DEVICE_SWITCH, NOT_SUPPORTED, NOT_CURRENTLY_SUPPORTED.
> The values documented here are taken directly from `ShutdownReasonEnum.proto`.

---

### ShutdownResponse / ByeByeResponse (0x0010)

> Confidence: Unverified (ShutdownResponse) / Bronze (ByeByeResponse)

```protobuf
// oaa/control/ShutdownResponseMessage.proto
// confidence: unverified
message ShutdownResponse {
    // Empty message -- presence is the acknowledgment
}
```

```protobuf
// oaa/control/ByeByeResponseMessage.proto
// confidence: bronze [apk_static]
message ByeByeResponse {
    // Empty message -- presence is the acknowledgment
}
```

These appear to be the same message (both empty, both on message ID 0x0010). `ByeByeResponse` is the historical APK class name, first appearing in v16.1 (absent in v15.9). `ShutdownResponse` is the canonical name used in this project.

The response carries no payload. Receipt of the message is the acknowledgment signal.

See also: [ByeByeResponseMessage.audit.yaml](../../oaa/control/ByeByeResponseMessage.audit.yaml)

---

### DisconnectReason (Phone-Internal)

> Confidence: Unverified -- **Phone-internal enum, not sent on the wire**

The phone maintains an internal `DisconnectReason` enum with 16 values for tracking why a session ended. This enum is NOT part of the AA wire protocol -- it is used internally by the Android Auto app for diagnostics and telemetry.

```protobuf
// oaa/common/DisconnectReasonEnum.proto
// confidence: unverified
message DisconnectReason {
    enum Enum {
        UNKNOWN = 0;
        INCOMPATIBLE_VERSION = 1;
        WRONG_CONFIGURATION = 2;
        IO_ERROR = 3;
        BYEBYE_REQUESTED_BY_CAR = 4;
        BYEBYE_REQUESTED_BY_USER = 5;
        WRONG_MESSAGE = 6;
        AUTH_FAILED = 7;
        AUTH_FAILED_BY_CAR = 8;
        TIMEOUT = 9;
        CAR_NOT_RESPONDING = 12;
        AUTH_CERT_NOT_YET_VALID = 13;
        AUTH_CERT_EXPIRED = 14;
        AUDIO_ERROR = 24;
        PROJECTION_PROCESS_CRASH_LOOP = 26;
    }
}
```

Notable values for understanding phone-side behavior:
- `BYEBYE_REQUESTED_BY_CAR` (4): The phone received a ShutdownRequest from the HU
- `TIMEOUT` (9) / `CAR_NOT_RESPONDING` (12): The phone detected a keepalive failure
- `AUTH_FAILED` (7) / `AUTH_FAILED_BY_CAR` (8): Authentication rejected (see [02-version-ssl-auth](02-version-ssl-auth.md))

Head unit implementers do not need to send or parse this enum, but awareness of these values helps diagnose connection issues from phone-side logs.

---

### Graceful Shutdown Flow

A clean session teardown follows this sequence:

**Step 1: Stop AV streams**
- Send STOP_INDICATION (0x8002) on active AV channels, or allow the phone to stop them
- Cease sending AV_MEDIA_ACK messages

**Step 2: Close individual channels**
- Send CHANNEL_CLOSE_NOTIFICATION (0x0009) for each open channel
- Alternatively, proceed directly to shutdown (the phone handles channel cleanup)

**Step 3: Send ShutdownRequest**
- Serialize `ShutdownRequest` with the appropriate `ShutdownReason`
- Send on channel 0 with `MessageType::Control`

**Step 4: Await ShutdownResponse**
- The responder sends an empty `ShutdownResponse` (0x0010)
- If no response arrives within a reasonable timeout, proceed with teardown anyway

**Step 5: Close TLS session**
- Perform TLS shutdown (send `close_notify` alert)

**Step 6: Close transport**
- Close the TCP socket (WiFi) or release the USB AOA interface
- For wireless connections, the WiFi AP may remain active for potential reconnection

> **Note:** The timeout for Step 4 (awaiting ShutdownResponse) is not specified in the APK evidence.
> Implementations should choose a reasonable value. If no response arrives, proceed with teardown
> to avoid hanging indefinitely.

---

### Implementation Guidance -- Shutdown

```c
// Initiate graceful shutdown
void initiate_shutdown(ShutdownReason__Enum reason) {
    ShutdownRequest request = SHUTDOWN_REQUEST__INIT;
    request.has_reason = 1;
    request.reason = reason;

    send_control_message(CONTROL_MSG_SHUTDOWN_REQUEST, &request);

    // Start a timeout timer for the response.
    // If ShutdownResponse is not received, proceed with teardown.
    start_shutdown_timer();
}

// Handle incoming ShutdownRequest from the phone
void handle_shutdown_request(const ShutdownRequest* request) {
    if (request->has_reason) {
        log_info("Shutdown requested, reason: %d", request->reason);
    }

    // Send acknowledgment
    ShutdownResponse response = SHUTDOWN_RESPONSE__INIT;
    send_control_message(CONTROL_MSG_SHUTDOWN_RESPONSE, &response);

    // Begin teardown sequence
    stop_av_streams();
    close_all_channels();
    close_tls_session();
    close_transport();
}

// Full graceful cleanup sequence (HU-initiated)
void graceful_shutdown(ShutdownReason__Enum reason) {
    // 1. Stop AV streams
    stop_av_streams();

    // 2. Close channels (optional -- shutdown implies channel closure)
    close_all_channels();

    // 3. Send ShutdownRequest and wait for response
    initiate_shutdown(reason);

    // 4. On response (or timeout): close TLS, close transport
    // Handled by shutdown response callback or timer expiry
}
```

---

## Error Handling

| Condition | Behavior | Evidence |
|-----------|----------|----------|
| No PingResponse received | Not specified. Suggest: treat as unresponsive after `ping_timeout_ms` from PingConfiguration. | PingConfiguration: Unverified |
| No ShutdownResponse received | Not specified. Suggest: timeout and proceed with teardown. | Unverified |
| Invalid ShutdownReason value | Unknown behavior. The enum is exhaustive (0-8) in the current APK. | Unverified |
| GalPingRequest missing timestamp | Parse error on receiver. The `required` modifier enforces presence. | Silver (proto structure) |
| TCP keepalive failure | OS closes socket. Application detects as I/O error. | Observed in captures |
| Unexpected disconnect (no ShutdownRequest) | Phone records as `CAR_NOT_RESPONDING` or `IO_ERROR` in DisconnectReason. | Unverified (phone-internal) |

## Log Tags

| Tag | What it shows |
|-----|--------------|
| `CAR.GAL.GAL` | GAL transport-level messages including GalPing |
| `CAR.GAL.GAL.LITE` | GAL transport activity (lightweight) |
| `CAR.CONN` | Connection state transitions, shutdown events |
| `CAR.CONN.LITE` | Connection state (lightweight) |
| `GH.ProjectionSvc` | Projection service lifecycle, session start/stop |
| `GH.CarDisconnect` | Disconnect reason logging |

## Postcondition

At the end of this phase:
- The AA session is closed
- TLS session is terminated
- Transport (TCP socket or USB AOA interface) is torn down
- For wireless connections, the WiFi Direct group or AP may remain active to allow reconnection without full re-pairing
- The phone records a `DisconnectReason` internally for diagnostics

This is the final stage of the connection lifecycle. To establish a new session, return to [01-transport-setup](01-transport-setup.md).

## References

- [PingRequestMessage.proto](../../oaa/control/PingRequestMessage.proto) + [audit](../../oaa/control/PingRequestMessage.audit.yaml) -- Silver
- [PingResponseMessage.proto](../../oaa/control/PingResponseMessage.proto) + [audit](../../oaa/control/PingResponseMessage.audit.yaml) -- Silver
- [GalPingRequestMessage.proto](../../oaa/control/GalPingRequestMessage.proto) + [audit](../../oaa/control/GalPingRequestMessage.audit.yaml) -- Silver
- [GalPingResponseMessage.proto](../../oaa/control/GalPingResponseMessage.proto) + [audit](../../oaa/control/GalPingResponseMessage.audit.yaml) -- Silver
- [ShutdownRequestMessage.proto](../../oaa/control/ShutdownRequestMessage.proto) + [audit](../../oaa/control/ShutdownRequestMessage.audit.yaml) -- Silver
- [ShutdownResponseMessage.proto](../../oaa/control/ShutdownResponseMessage.proto) -- Unverified
- [ShutdownReasonEnum.proto](../../oaa/control/ShutdownReasonEnum.proto) -- Unverified
- [ByeByeResponseMessage.proto](../../oaa/control/ByeByeResponseMessage.proto) + [audit](../../oaa/control/ByeByeResponseMessage.audit.yaml) -- Bronze
- [DisconnectReasonEnum.proto](../../oaa/common/DisconnectReasonEnum.proto) -- Unverified (phone-internal)
- [PingConfigurationData.proto](../../oaa/common/PingConfigurationData.proto) -- Unverified
- [ConnectionConfigurationData.proto](../../oaa/control/ConnectionConfigurationData.proto) -- Silver
- [ControlMessageIdsEnum.proto](../../oaa/control/ControlMessageIdsEnum.proto) -- Unverified
- [04-channel-lifecycle](04-channel-lifecycle.md) -- prerequisite document
- [01-transport-setup](01-transport-setup.md) -- start of lifecycle chain
