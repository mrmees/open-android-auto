# Android Auto Protocol Overview

This document describes the Android Auto (AA) protocol as implemented between a phone (AA app) and a head unit (HU). The protocol is not publicly documented by Google; everything here is derived from reverse engineering, APK analysis, and live capture observation.

## Transport Layer

Android Auto uses a layered transport that differs between wired and wireless modes.

### Wireless Connection Sequence

1. **Bluetooth RFCOMM discovery** -- The HU advertises a Bluetooth SDP record with the AA UUID (`4de17a00-52cb-11e6-bdf4-0800200c9a66`). The phone discovers the HU via BT scanning and connects over RFCOMM.
2. **WiFi credential exchange** -- Over the RFCOMM channel, the HU sends its WiFi AP SSID, password, BSSID, and security type. The phone disconnects BT and connects to the HU's WiFi AP.
3. **TCP connection** -- The phone opens a TCP connection to the HU on port 5277. This becomes the primary data transport for the session.
4. **SSL handshake** -- The TCP connection is wrapped in SSL/TLS for encryption. The HU acts as the SSL server.

### Wired Connection (USB)

USB connections use AOA (Android Open Accessory) protocol. The phone enumerates as a USB accessory, and data flows over USB bulk endpoints. The framing layer above is identical.

## Framing

All data on the transport is wrapped in 8-byte frame headers:

```
Bytes 0-1: Channel ID (uint16, big-endian)
Bytes 2-3: Frame type + flags (uint8 each)
Bytes 4-7: Payload length (uint32, big-endian)
```

**Frame types:**

| Type | Value | Description |
|------|------:|-------------|
| First | 1 | First (or only) frame of a message |
| Middle | 2 | Continuation frame |
| Last | 3 | Final frame of a multi-frame message |
| Bulk | 0 | Complete single-frame message |

Large protobuf messages are split across multiple frames. The receiver reassembles them before parsing.

**Encryption:** After the SSL handshake, frame payloads are encrypted. The frame header itself is always plaintext.

## Message Types

Within each frame, the first two bytes of the payload indicate the message type:

| Type | Value | Used By |
|------|------:|---------|
| Control | 0 | Channel 0 (control channel) messages |
| Specific | 1 | ALL other service channel messages |

This distinction is critical. The control channel (channel 0) uses `MessageType::Control` for its messages. Every other channel (input, sensor, video, audio, etc.) uses `MessageType::Specific`. Getting this wrong causes the phone to silently ignore messages with no error feedback.

## Channel Multiplexing

A single TCP connection carries all data for all channels. Each frame's channel ID identifies which logical channel the data belongs to. See [channel-map.md](channel-map.md) for the full channel ID table.

## Session Lifecycle

### Service Discovery

1. **HU sends `ServiceDiscoveryRequest`** -- Contains the HU's device name, brand, and optional icons.
2. **Phone sends `ServiceDiscoveryResponse`** -- Contains an array of `ChannelDescriptor` entries, one per channel the phone supports. Each descriptor includes the channel type and channel-specific configuration data.

The service discovery response tells the HU what capabilities the phone offers (video codecs, sensor types, audio configs, etc.).

### Channel Lifecycle

Each channel follows this lifecycle:

```
ChannelOpenRequest (HU -> Phone)
    -> ChannelOpenResponse (Phone -> HU)
        -> Channel-specific setup (e.g., AVChannelSetupRequest)
            -> Channel-specific start (e.g., AVChannelStartIndication)
                -> Data exchange (bidirectional)
            -> Channel-specific stop
        -> ChannelClose
```

Not all channels require explicit setup/start. Some (like sensor, input) begin data exchange immediately after channel open.

### Keepalive

The HU sends periodic `PingRequest` messages on the control channel. The phone responds with `PingResponse`. If pings go unanswered, the connection is considered dead.

### Shutdown

Either side can initiate shutdown via `ShutdownRequest` with a reason code (user request, error, phone disconnected, etc.). The other side responds with `ShutdownResponse` and the TCP connection closes.

## Audio/Video Streaming

### Video

The phone encodes and sends video; the HU decodes and displays it.

1. HU advertises supported video configs (resolution, FPS, codec) in `ServiceDiscoveryRequest`.
2. Phone selects a config and sends `AVChannelSetupRequest`.
3. HU responds with `AVChannelSetupResponse`.
4. Phone sends `AVChannelStartIndication` followed by encoded video frames.
5. HU sends `AVMediaAckIndication` to acknowledge received data (flow control).

Supported codecs: H.264, H.265, VP9, AV1. Supported resolutions: 480p, 720p, 1080p (landscape and portrait variants).

### Audio

Three separate audio channels exist:

- **Media audio** (channel 4) -- Music, podcasts
- **Speech audio** (channel 5) -- Navigation prompts, assistant responses
- **Phone audio** (channel 6) -- Voice call audio

Each has independent focus management. The phone requests audio focus; the HU grants/denies based on what else is playing. Audio focus types map to Android's `AudioManager` focus modes (gain, transient, duck).

## Authentication

After the SSL handshake, the HU and phone exchange authentication messages:

1. HU sends `BindingRequest` with its public key.
2. Phone sends `BindingResponse`.
3. Phone sends `AuthCompleteIndication` when authentication succeeds.

On first connection, the phone may prompt the user to trust the HU. Subsequent connections use cached credentials.
