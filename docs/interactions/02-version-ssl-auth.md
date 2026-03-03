# 02 — Version Exchange, SSL Handshake & Authentication

## Overview

Once a raw byte stream exists (TCP or USB), three sequential handshakes establish the secure, authenticated session: binary version negotiation, app-layer TLS 1.2, and device binding/authentication. All three must complete before any protobuf service messages are exchanged.

## Prerequisites

- Bidirectional byte stream between phone and HU (from [01-transport-setup](01-transport-setup.md))
- No encryption active — all bytes in this phase start as plaintext
- HU has an SSL certificate and private key loaded (see [SSL Certificates](#ssl-certificates))

## Sequence Diagram

```
Phone                                    Head Unit
  |                                         |
  |  ──────── Version Exchange ──────────   |
  |                                         |
  |←── VERSION_REQUEST (0x0001) ────────── |  HU sends first, raw binary
  |─── VERSION_RESPONSE (0x0002) ────────→ |  Phone responds with negotiated version
  |                                         |
  |  ──────── SSL Handshake ─────────────   |
  |                                         |
  |←── SSL_HANDSHAKE (0x0003) ──────────── |  HU sends ServerHello (HU = TLS server)
  |─── SSL_HANDSHAKE (0x0003) ──────────→  |  Phone sends ClientHello
  |←── SSL_HANDSHAKE (0x0003) ──────────── |  (multiple round-trips)
  |─── SSL_HANDSHAKE (0x0003) ──────────→  |  ...until TLS FINISHED
  |                                         |
  |  ──── All further messages encrypted ── |
  |                                         |
  |  ──────── Authentication ────────────   |
  |                                         |
  |←── AUTH_COMPLETE (0x0004) ──────────── |  HU signals auth success
  |                                         |
  |  ──── Ready for Service Discovery ───   |
```

**Important:** The HU initiates all three phases. The phone is reactive throughout.

---

## Step 1: Version Exchange

### Format

The version exchange uses a **raw binary format** — it is NOT protobuf. This is the only non-protobuf message pair in the entire protocol (aside from raw AV data frames).

**Note:** Do not confuse this with the WiFi projection version exchange (RFCOMM msgId 1/7, which IS protobuf). The GAL version exchange happens over the main data stream after TCP connect.

### Frame Structure

Version messages use the standard AA frame header but contain raw bytes, not protobuf:

```
┌─────────────────────── Frame Header (2 bytes) ──────────────────────┐
│ Byte 0: Channel ID (0x00 = control)                                 │
│ Byte 1: Flags (0x00 = BULK frame, MessageType CONTROL, PLAINTEXT)   │
├─────────────────────── Frame Payload ───────────────────────────────┤
│ Byte 0-1: Message ID (uint16 BE) — 0x0001 or 0x0002                │
│ Byte 2-3: Major version (uint16 BE)                                 │
│ Byte 4-5: Minor version (uint16 BE)                                 │
│ Byte 6-7: Status (uint16 BE) — response only                       │
└─────────────────────────────────────────────────────────────────────┘
```

### VERSION_REQUEST (0x0001) — HU → Phone

The HU sends first, immediately after the byte stream is established.

```
Offset  Bytes         Meaning
0x00    00 01         Message ID: VERSION_REQUEST
0x02    00 01         Major version (1)
0x04    00 01         Minor version (1)
```

Total: **6 bytes** (message ID + 2 version shorts)

**Example from captured session:**
```
HU sends: 00 01 00 01 00 01    (requesting v1.1)
```

The HU advertises the **minimum version it supports.** The phone will negotiate up.

### VERSION_RESPONSE (0x0002) — Phone → HU

```
Offset  Bytes         Meaning
0x00    00 02         Message ID: VERSION_RESPONSE
0x02    00 01         Major version (1)
0x04    00 07         Minor version (7)
0x06    00 00         Status: MATCH (0x0000)
```

Total: **8 bytes** (message ID + 2 version shorts + status)

**Version Response Status:**

| Value | Name | Meaning |
|-------|------|---------|
| 0x0000 | MATCH | Compatible version found |
| 0xFFFF | MISMATCH | No compatible version — connection will close |

**Example from captured session:**
```
Phone responds: 00 02 00 01 00 07 00 00    (negotiated v1.7, MATCH)
```

### Version Negotiation Behavior

- The phone supports v1.0 through v1.7 (as of AA 16.2)
- The HU sends its minimum supported version
- The phone responds with the **highest version it supports** that is compatible
- If the phone's major version differs from the HU's → MISMATCH
- Protocol version affects feature availability:

| Min Version | Feature Unlocked |
|-------------|-----------------|
| v1.5 | 48kHz TTS/guidance audio |
| v1.6 | WireConfig in version exchange |
| v1.7 | (current, full feature set) |

### Implementation Notes

- aasdk hardcodes v1.1. Bumping to v1.7 is safe — the phone already negotiates 1.7 regardless.
- The version exchange MUST complete before any other message is sent.
- If MISMATCH is received, the connection must be torn down immediately.

---

## Step 2: SSL Handshake

### Overview

After version negotiation succeeds, the HU initiates an **application-layer TLS 1.2 handshake.** This is NOT socket-level TLS — the SSL bytes are wrapped in AA control messages and processed through in-memory BIO pairs (OpenSSL) or SSLEngine (Java/Android).

### Frame Structure

SSL handshake bytes are wrapped as control channel messages:

```
┌─────────────────────── Frame Header ────────────────────────────────┐
│ Channel: 0x00 (control)                                             │
│ Flags: BULK/FIRST/LAST, MessageType CONTROL, PLAINTEXT              │
├─────────────────────── Payload ─────────────────────────────────────┤
│ Byte 0-1: Message ID 0x0003 (SSL_HANDSHAKE)                        │
│ Byte 2+:  Raw TLS handshake bytes                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### TLS Configuration

| Parameter | Value |
|-----------|-------|
| Protocol | TLS 1.2 (hardcoded, not negotiable) |
| Cipher | AES/CBC/PKCS5Padding (from APK) |
| HU Role | **Server** (phone connects as client) |
| Client Auth | Required (mutual TLS) |
| Provider | GmsCore_OpenSSL (phone side) |

### Handshake Flow

The HU acts as TLS server. The handshake follows standard TLS 1.2:

```
Phone (TLS Client)                   Head Unit (TLS Server)
  |                                     |
  |                          beginHandshake()
  |                          SSLEngine NEED_WRAP
  |←─── ServerHello + Cert ─────────── |  (wrapped in 0x0003 msg)
  |                                     |
  |──── ClientHello + Cert ──────────→  |  (wrapped in 0x0003 msg)
  |                                     |
  |←─── ServerKeyExchange ───────────── |
  |──── ClientKeyExchange ───────────→  |
  |                                     |
  |←─── ChangeCipherSpec + Finished ─── |
  |──── ChangeCipherSpec + Finished ──→ |
  |                                     |
  |     TLS session established         |
```

Multiple round-trips occur. The exact number depends on the cipher suite negotiated. From our captured session: **2348 bytes from phone, 51 bytes back** during the handshake.

### SSL Certificates

The HU must have a valid certificate. In practice:

- The JVC Kenwood certificate bundled with aasdk works (expires 2045)
- The phone uses `SSL_VERIFY_NONE` equivalent — it does NOT validate the HU cert against a CA
- However, the phone **logs** the certificate details and **rejects** certain subject names:
  - Rejects subject containing "CarService"
  - Rejects subject containing "Google Automotive Link"

**Certificate from our captured session:**
```
Subject:  OU=01, O=JVC Kenwood, L=Hachioji, ST=Tokyo, C=JP
Serial:   27 (0x1b)
NotBefore: 2014-07-03
NotAfter:  2045-04-29
```

### Post-Handshake Encryption

After the TLS handshake completes:
- **All subsequent message payloads are encrypted** through the TLS layer
- **Frame headers remain plaintext** (channel ID + flags are always readable)
- **Ping messages (0x000b/0x000c) stay PLAINTEXT** — they bypass the TLS layer entirely
- The encryption/decryption happens in memory (BIO pairs), not at the socket level

### Implementation Guidance

**OpenSSL (C/C++) approach:**
```
// Create BIO pair (not socket BIO)
BIO_new_bio_pair(&internal_bio, 0, &network_bio, 0);
SSL_set_bio(ssl, internal_bio, internal_bio);
SSL_set_accept_state(ssl);  // HU is server

// Handshake loop:
// 1. Read 0x0003 message from phone → write to network_bio
// 2. Call SSL_do_handshake()
// 3. Read from network_bio → send as 0x0003 message to phone
// 4. Repeat until SSL_is_init_finished()
```

**Java/Android (SSLEngine) approach:**
```java
SSLEngine engine = SSLContext.getInstance("TLSv1.2")
    .createSSLEngine();
engine.setUseClientMode(false);      // HU is server
engine.setNeedClientAuth(true);      // Require phone cert
engine.beginHandshake();

// Loop through HandshakeStatus:
//   NEED_WRAP → encrypt and send as 0x0003
//   NEED_UNWRAP → receive 0x0003, decrypt
//   NEED_TASK → run delegated tasks
//   FINISHED → done
```

---

## Step 3: Authentication / Binding

### Overview

After TLS is established, the HU sends an `AUTH_COMPLETE` indication. In the aasdk/open-source implementations, this is a simple signal. Production Google SDKs may perform additional binding (BindingRequest/BindingResponse with key exchange), but the minimal flow that works is:

### Minimal Flow (aasdk-compatible)

```
Phone                                    Head Unit
  |                                         |
  |←── AUTH_COMPLETE (0x0004) ──────────── |  Encrypted, protobuf
  |                                         |
  |     Phone accepts, session is           |
  |     authenticated                       |
```

### AUTH_COMPLETE (0x0004) — HU → Phone

```protobuf
// oaa/control/AuthCompleteIndicationMessage.proto
message AuthCompleteIndication {
    optional int32 status = 1;    // 0 = success
}
```

**Wire format (after TLS encryption):**
```
Message ID: 00 04
Payload:    08 00        (field 1 = 0, status SUCCESS)
```

### Extended Binding Flow (Production SDKs)

Production head units (Kenwood, Sony, Alpine) may perform a fuller binding exchange. This is optional — the phone accepts either flow:

```
Phone                                    Head Unit
  |                                         |
  |←── BindingRequest (encrypted) ──────── |
  |─── BindingResponse (encrypted) ──────→ |
  |←── AUTH_COMPLETE (0x0004) ──────────── |
```

**BindingRequest (no dedicated message ID — uses 0x0004 flow):**
```protobuf
message BindingRequest {
    repeated int32 scan_codes = 1;  // Keycodes the HU supports
}
```

**BindingResponse:**
```protobuf
message BindingResponse {
    optional Status status = 1;       // 0 = OK
    optional bool already_paired = 2; // true if previously paired
}
```

### First-Time Pairing

On first connection to a new HU, the phone may:
1. Display a "Trust this car?" prompt to the user
2. Cache the HU's certificate fingerprint for future sessions
3. Subsequent connections skip the prompt (silent auth)

This pairing state is stored on the phone. Clearing AA app data resets it.

---

## Error Handling

| Error | Detection | Recovery |
|-------|-----------|---------|
| Version MISMATCH | Response status = 0xFFFF | Connection must close. HU needs to support a version the phone accepts. |
| SSL handshake timeout | No SSL_HANDSHAKE message within ~5s | Phone disconnects. Check certificate loading and BIO setup. |
| SSL cert rejected | Phone drops connection after receiving cert | Check cert subject — must not contain "CarService" or "Google Automotive Link". |
| SSL handshake failure | `SSL_do_handshake()` returns error | Check cert/key pair match, TLS 1.2 support, cipher suite compatibility. |
| Auth rejected | Phone sends ShutdownRequest after AUTH_COMPLETE | Check BindingRequest content. May need user confirmation on phone. |

## Timing (Observed)

| Event | Time from TCP connect |
|-------|----------------------|
| Version exchange complete | ~100ms |
| SSL handshake complete | ~200ms |
| Auth complete | ~300ms |
| Ready for service discovery | ~300ms |

Total phase duration: **~300ms** — this phase is fast.

## Log Tags

| Tag | What it shows |
|-----|--------------|
| `CAR.GAL.GAL.LITE` | Version negotiation: "Car requests protocol version v1.1" / "Negotiated protocol version v1.7" |
| `CAR.GAL.SECURITY.LITE` | SSL handshake progress, certificate details, TLS provider |
| `CAR.AUTH` | Auth/binding state machine |
| `GH.ConnLoggerV2` | High-level events: `VERSION_NEGOTIATION_*`, `SSL_*`, `AUTHORIZATION_*` |

## Postcondition

At the end of this phase:
- TLS 1.2 session is established (all further messages encrypted except pings)
- Device is authenticated (phone trusts the HU)
- The session is ready for [service discovery](03-service-discovery.md)

## References

- `oaa/control/ControlMessageIdsEnum.proto` — message ID definitions
- `oaa/control/VersionResponseStatusEnum.proto` — MATCH/MISMATCH enum
- `oaa/control/AuthCompleteIndicationMessage.proto` — auth complete message
- `oaa/control/BindingRequestMessage.proto` — binding request (optional)
- `oaa/control/BindingResponseMessage.proto` — binding response (optional)
- [`phone-side-debug.md`](../phone-side-debug.md) — captured session (Phase 5: TCP + GAL Handshake)
- APK classes: `hzh.java` (version handler), `ibm.java` (SSL engine), `iod.java` (auth flow)
