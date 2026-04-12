# Channel Architecture Reference

This document describes the multiplexed channel architecture of the Android Auto (AA)
protocol. It covers transport, framing, fragmentation, channel-to-service binding via
SDP, and capability negotiation. Every factual claim is cited with inline evidence.

For per-message field tables and msg IDs, see [protocol-reference.md](../protocol-reference.md).
For the full channel ID table, see [channel-map.md](../channel-map.md).

## Transport

AA runs over a single bidirectional byte stream. Two transport modes exist:

- **Wired (USB AOA):** Phone enumerates as a USB accessory via Android Open Accessory
  protocol. Data flows over USB bulk endpoints
  ([transport-setup.md](../interactions/01-transport-setup.md)).
- **Wireless (BT + WiFi):** HU advertises a Bluetooth SDP record with the AA UUID
  (`4de17a00-52cb-11e6-bdf4-0800200c9a66`). Phone connects via RFCOMM, receives WiFi
  credentials, disconnects BT, joins the HU's WiFi AP, and opens a TCP connection on
  port 5277 ([transport-setup.md](../interactions/01-transport-setup.md),
  [wifi-projection.md](wifi-projection.md)).

In both modes, all channels are multiplexed onto this single transport. The framing
layer is identical regardless of physical medium.

After transport establishment, a TLS 1.2 handshake (BoringSSL) wraps the byte stream.
Frame headers remain plaintext; payloads are encrypted after auth completes
([version-ssl-auth.md](../interactions/02-version-ssl-auth.md)).

## Framing

Every unit of data on the wire is wrapped in a frame consisting of a **structural
header** followed by a **size field** and then the payload.

### Frame Layout

The structural frame header is **2 bytes**: channel ID and flags
([aasdk: FrameHeader.hpp:46](https://github.com/f1xpl/aasdk/blob/046b3b3/include/f1x/aasdk/Messenger/FrameHeader.hpp#L46),
`getSizeOf() { return 2; }`). The commonly cited "4-byte header" includes the 2-byte
frame size that immediately follows. For FIRST frames (fragmented messages), the size
region extends to 6 bytes.

```
BULK / MIDDLE / LAST frames (4 bytes + payload):
+----------+----------+----------+----------+----------+---
| channel  |  flags   | len_hi   | len_lo   | payload ...
| (1 byte) | (1 byte) | (1 byte) | (1 byte) |
+----------+----------+----------+----------+----------+---
  Byte 0     Byte 1     Byte 2     Byte 3

FIRST frames (8 bytes + payload):
+----------+----------+----------+----------+----------+----------+----------+----------+----------+---
| channel  |  flags   | frag_hi  | frag_lo  | total[3] | total[2] | total[1] | total[0] | payload ...
| (1 byte) | (1 byte) | (1 byte) | (1 byte) | (1 byte) | (1 byte) | (1 byte) | (1 byte) |
+----------+----------+----------+----------+----------+----------+----------+----------+----------+---
  Byte 0     Byte 1     Byte 2     Byte 3     Byte 4     Byte 5     Byte 6     Byte 7
                        |--frame size (BE)--|  |-------total message size (BE, uint32)--------|
```

([aasdk: FrameSize.cpp:46-58](https://github.com/f1xpl/aasdk/blob/046b3b3/src/Messenger/FrameSize.cpp#L46),
[aasdk: MessageInStream.cpp:80](https://github.com/f1xpl/aasdk/blob/046b3b3/src/Messenger/MessageInStream.cpp#L80))

**Practical read pattern:** always read 4 bytes first. Byte 0 = channel, byte 1 = flags.
If FrameType is FIRST (bits 0-1 of flags = `01`), read 4 more bytes for the total
message size. Otherwise, bytes 2-3 give the frame's payload length (uint16 BE).

### Flags Byte

The flags byte encodes three fields in its low nibble
([aasdk: FrameHeader.cpp:29-34](https://github.com/f1xpl/aasdk/blob/046b3b3/src/Messenger/FrameHeader.cpp#L29)):

```
Flags byte (1 byte = 8 bits):
+---+---+---+---+---+---+---+---+
| 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
+---+---+---+---+---+---+---+---+
|  (unused)     | E | M |  FT   |
+---+---+---+---+---+---+---+---+
```

| Field | Bits | Values |
|-------|------|--------|
| **FT** (FrameType) | 0-1 | `00`=MIDDLE, `01`=FIRST, `10`=LAST, `11`=BULK ([aasdk: FrameType.hpp:30-36](https://github.com/f1xpl/aasdk/blob/046b3b3/include/f1x/aasdk/Messenger/FrameType.hpp#L30)) |
| **M** (MessageType) | 2 | `0`=SPECIFIC, `1`=CONTROL ([aasdk: MessageType.hpp:33-35](https://github.com/f1xpl/aasdk/blob/046b3b3/include/f1x/aasdk/Messenger/MessageType.hpp#L33)) |
| **E** (EncryptionType) | 3 | `0`=PLAIN, `1`=ENCRYPTED ([aasdk: EncryptionType.hpp:30-31](https://github.com/f1xpl/aasdk/blob/046b3b3/include/f1x/aasdk/Messenger/EncryptionType.hpp#L30)) |

**Common flag values:**

| Hex | Binary | Meaning |
|----:|-------:|---------|
| `0x03` | `0000 0011` | PLAIN + SPECIFIC + BULK (plaintext unfragmented data) |
| `0x07` | `0000 0111` | PLAIN + CONTROL + BULK (plaintext control message) |
| `0x09` | `0000 1001` | ENCRYPTED + SPECIFIC + FIRST (encrypted first fragment) |
| `0x08` | `0000 1000` | ENCRYPTED + SPECIFIC + MIDDLE (encrypted continuation) |
| `0x0a` | `0000 1010` | ENCRYPTED + SPECIFIC + LAST (encrypted last fragment) |
| `0x0b` | `0000 1011` | ENCRYPTED + SPECIFIC + BULK (encrypted unfragmented) |
| `0x0f` | `0000 1111` | ENCRYPTED + CONTROL + BULK (encrypted control message) |

Only the control channel (channel 0) uses `MessageType::CONTROL` (bit 2 set). All
other channels use `MessageType::SPECIFIC`
([channel-map.md](../channel-map.md)).

### Message ID

After the frame header and size, the payload begins with a **2-byte message ID**
(uint16 BE). This ID is channel-scoped: the same numeric ID means different things on
different channels. For example, msg ID `0x8001` on the input channel is
`InputEventIndication`, while `0x8001` on the bluetooth channel is
`BluetoothPairingRequest`
([protocol-reference.md](../protocol-reference.md)).

## Fragmentation

Messages that exceed the transport's frame size limit are split across multiple frames
using the FrameType bits.

| FrameType | Value | Role |
|-----------|------:|------|
| BULK | `11` | Unfragmented -- complete message in one frame |
| FIRST | `01` | First fragment; extended header includes total message size |
| MIDDLE | `00` | Continuation fragment |
| LAST | `10` | Final fragment; triggers reassembly |

**Reassembly rules:**

1. BULK or LAST completes a message; FIRST or MIDDLE means more fragments follow
   ([aasdk: MessageInStream.cpp:134-153](https://github.com/f1xpl/aasdk/blob/046b3b3/src/Messenger/MessageInStream.cpp#L134)).
2. Fragments on a single channel MUST arrive in order. A FIRST frame on channel N
   while a previous message on channel N is still being assembled is an error
   ([aasdk: MessageInStream.cpp:68-77](https://github.com/f1xpl/aasdk/blob/046b3b3/src/Messenger/MessageInStream.cpp#L68)).
3. Fragments from different channels CAN interleave. Channel 3 (video) fragments may
   be interspersed with channel 0 (control) messages.
4. The receiver concatenates all fragment payloads (FIRST + MIDDLE... + LAST) and
   parses the result as a single protobuf message (or raw media frame).

In practice, most protobuf messages fit in a single BULK frame. Fragmentation is
common for video I-frames (H.264 IDR NAL units) and large SDP responses.

## Channels

AA multiplexes all communication over a single transport using channel IDs. Each
channel handles a specific protocol domain.

### Channel Overview

| GAL Type | aasdk Name | Service | SDP `channel_kind` | Direction |
|---------:|------------|---------|--------------------:|-----------|
| 0 | CONTROL | Control | (implicit) | Bidirectional |
| 1 | INPUT | Input | `input_channel` | HU -> Phone |
| 3 | VIDEO | Video | `av_channel` (MAIN) | Phone -> HU (stream), HU -> Phone (focus) |
| 4 | MEDIA_AUDIO | Media Audio | `av_channel` (MEDIA) | Phone -> HU |
| 5 | SPEECH_AUDIO | Speech Audio | `av_channel` (SPEECH) | Phone -> HU |
| 6 | SYSTEM_AUDIO | Phone Audio | `av_channel` (SYSTEM) | Bidirectional |
| 7 | SENSOR | Sensor | `sensor_channel` | HU -> Phone (data), Phone -> HU (subscribe) |
| 8 | AV_INPUT | Mic Input | `av_input_channel` | HU -> Phone |
| 9 | BLUETOOTH | Bluetooth | `bluetooth_channel` | HU -> Phone (pairing), Phone -> HU (auth) |
| 10 | -- | Navigation | `navigation_channel` | Bidirectional |
| 11 | -- | Media Info | `media_info_channel` | Phone -> HU (metadata) |
| 13 | -- | Phone Status | `phone_status_channel` | Bidirectional |
| 15 | -- | Radio | (not in SDP captures) | Bidirectional |
| 17 | -- | WiFi Projection | `wifi_channel` | HU -> Phone |
| 19 | -- | Car Control | (not in SDP captures) | Bidirectional |
| 20 | -- | Car Local Media | (not in SDP captures) | HU -> Phone (status), Phone -> HU (request) |

([aasdk: ChannelId.hpp:30-42](https://github.com/f1xpl/aasdk/blob/046b3b3/include/f1x/aasdk/Messenger/ChannelId.hpp#L30),
[channel-map.md](../channel-map.md),
VW MIB3 OI + DHU SDP captures)

### Key Observations

- **Control channel (type 0)** is implicit: not declared in SDP, always present on
  wire channel 0. It uses `MessageType::CONTROL`; all other channels use
  `MessageType::SPECIFIC`.
- **aasdk defines 9 channels** (CONTROL through BLUETOOTH,
  [ChannelId.hpp](https://github.com/f1xpl/aasdk/blob/046b3b3/include/f1x/aasdk/Messenger/ChannelId.hpp#L30)).
  Modern AA has 15+ GAL service types. Channels 10-20 are post-aasdk additions
  discovered via APK analysis (APK 16.2).
- **GAL service type is the stable identifier.** Wire channel IDs are assigned
  dynamically per-session by the HU based on SDP response order. A given service
  (e.g., media audio) might be wire channel 4 in one session and 7 in another.
- **Radio (15), Car Control (19), and Car Local Media (20)** exist in the APK handler
  code but were not declared in either the VW or DHU SDP captures. They likely require
  specific HU hardware (radio tuner, VHAL interface, local media source).

### Direction Semantics

Most channels have a dominant data flow direction:

- **HU -> Phone:** Input events, sensor data, mic audio, Bluetooth pairing
- **Phone -> HU:** Video stream, audio streams, nav turn data, media metadata
- **Bidirectional:** Control channel, phone audio (call audio both ways), car control

Within a channel, individual message types may flow in either direction. For example,
the video channel streams Phone -> HU but receives focus/config requests HU -> Phone.
See per-channel docs ([audio.md](audio.md), [video.md](video.md), etc.) for
message-level direction tables.

## Service Discovery and Binding

After TLS authentication, the HU and phone exchange Service Discovery Protocol (SDP)
messages to declare their capabilities and bind channels to services.

### SDP Exchange Sequence

```
Phone                                    Head Unit
  |                                         |
  |    <--- ServiceDiscoveryRequest ---     |  (msg ID 5)
  |    --- ServiceDiscoveryResponse --->    |  (msg ID 6)
  |                                         |
  |    (for each needed channel:)           |
  |    <--- ChannelOpenRequest ---          |  (msg ID 7)
  |    --- ChannelOpenResponse --->         |  (msg ID 8)
  |                                         |
```

The HU sends `ServiceDiscoveryRequest` containing its device name, brand, model, and
HU-side capabilities. The phone responds with `ServiceDiscoveryResponse` containing an
array of `ChannelDescriptor` entries -- one per channel the phone supports
([aasdk: ControlMessageIdsEnum.proto:24-45](https://github.com/f1xpl/aasdk/blob/046b3b3/aasdk_proto/ControlMessageIdsEnum.proto#L24),
[service-discovery.md](../interactions/03-service-discovery.md)).

### ChannelDescriptor Structure

Each service in the SDP response is a `ChannelDescriptor` with:

- **`channel_id`** -- assigned by the phone per-session (ephemeral wire ID)
- **`channel_kind`** oneof -- determines channel type and carries type-specific config
  (e.g., `av_channel` for video/audio, `sensor_channel` for sensors,
  `input_channel` for input)

The `channel_kind` field is the binding mechanism: it tells the HU what type of
service this channel provides and includes the channel-specific configuration
(supported codecs, sensor types, input capabilities, etc.).

14 channels were observed across VW MIB3 OI and DHU 2.1 SDP captures. The control
channel is implicit (always channel 0, not in SDP).

### Service ID Assignment

Channel IDs in the SDP are **dynamic per-session**. The GAL service type (an integer
like 1 for input, 3 for video) is the stable cross-session identifier. When
implementing a head unit, use the GAL service type to locate a channel in the SDP
response -- never hardcode wire channel IDs.

### Channel Lifecycle

```
CLOSED --[ChannelOpenRequest]--> OPEN
  OPEN --[channel-specific setup]--> SETUP
  SETUP --[channel-specific start]--> ACTIVE
  ACTIVE --[data exchange]--> ACTIVE
  ACTIVE --[ChannelCloseNotification | ByeBye]--> CLOSED
```

Not all channels require explicit setup/start phases. Input, sensor, and phone status
channels begin data exchange immediately after channel open. AV channels (video, audio)
require an `AVChannelSetupRequest`/`Response` exchange before streaming begins
([channel-lifecycle.md](../interactions/04-channel-lifecycle.md)).

**Keepalive:** The HU sends periodic `PingRequest` (msg ID 11) on the control channel;
the phone responds with `PingResponse` (msg ID 12). Unanswered pings indicate a dead
connection
([session-maintenance.md](../interactions/05-session-maintenance-teardown.md)).

**Shutdown:** Either side sends `ByeByeRequest` (msg ID 15) with a reason code. The
other side responds with `ByeByeResponse` (msg ID 16) and the transport closes.

## Capability Negotiation

Channels negotiate capabilities at multiple points in the session lifecycle. Three
concrete examples illustrate the patterns.

### Version Exchange

The first messages after TLS are `VERSION_REQUEST` (msg ID 1) and `VERSION_RESPONSE`
(msg ID 2) on the control channel. These establish the protocol version (v1.7 observed
in DHU captures) and gate all subsequent communication. If versions are incompatible,
the session terminates before SDP exchange begins
([aasdk: ControlMessageIdsEnum.proto](https://github.com/f1xpl/aasdk/blob/046b3b3/aasdk_proto/ControlMessageIdsEnum.proto#L24),
[version-ssl-auth.md](../interactions/02-version-ssl-auth.md)).

### Video Resolution and Codec Negotiation

The SDP `av_channel` descriptor for the MAIN display lists the HU's supported
resolutions, frame rates, and codecs. The phone selects from the HU's offered set
during `AVChannelSetupRequest`.

| Parameter | VW MIB3 OI | DHU 2.1 |
|-----------|-----------|---------|
| Resolutions | 1920x1080, 1280x720, 800x480 | 1280x720 only |
| FPS | 60 | 30 |
| Codec | H.264 Baseline Profile | H.264 Baseline Profile |
| DPI (at 720p) | 142 | 160 |

(VW data: [sdp-values.json](../../analysis/reports/oem-vw/sdp-values.json);
DHU data: DHU 2.1 SDP baseline)

The SDP proto schema defines H.264, H.265, VP9, and AV1 codec types, but all observed
captures use H.264 BP exclusively.

**Resolution changes require a full session restart.** The HU sends
`ShutdownRequest { reason: DEVICE_SWITCH }`, waits for `ByeByeResponse`, then
reconnects with a new `VideoConfig` in the SDP. No mid-session renegotiation is
possible.

### Material You Theming (ColorSchemeSupport)

`AVChannel` field 9 in the SDP descriptor gates Material You theming delivery:

| Value | Meaning |
|------:|---------|
| 0 | Basic (no theming) |
| 2 | Material You v2 |
| 3 | Material You v3 |

When set to 2 or higher on the MAIN display channel, the phone sends 16 ARGB color
tokens (light + dark variants) on palette change. The phone-side gates are:
`HeroFeature__theming_enabled`, `HERO_THEMING` feature set, and
`setThemingUpdatesEnabled` flag.

The wire messages are `UiConfigRequest` (msg ID 0x8011, Phone -> HU) carrying the
color tokens, and `UpdateHuUiConfigResponse` (msg ID 0x8012, HU -> Phone) for
accept/reject (APK 16.2, [video.md](video.md) theming section).

v2 and v3 use identical token names and wire format; only the seed color processing
algorithm differs (v2 = identity passthrough, v3 = complex color remap).

For channel-specific negotiation details, see the individual
[channel docs](.). For per-message field tables and msg IDs, see
[protocol-reference.md](../protocol-reference.md).

## VW-vs-DHU Comparison

The same AA protocol produces different SDP configurations depending on the head unit
implementation. Below are concrete examples comparing a production VW MIB3 OI 2024
(AA 16.4) against Google's Desktop Head Unit 2.1 (development tool). For the full
divergence analysis, see
[dhu-divergence.md](../../analysis/reports/oem-vw/dhu-divergence.md).

### Service-Presence Divergence

Not every HU declares the same set of channels. The VW and DHU SDP responses differ
in which services they advertise:

| Service | VW MIB3 OI | DHU 2.1 |
|---------|------------|---------|
| Total SDP services | 13 | 14 |
| `bluetooth_channel` | Present (adapter `84:96:90:8C:34:0B`) | Absent |
| `wifi_channel` | Present (bssid `86:96:90:8C:77:EF`) | Absent |
| `vendor_extension_channel` | Absent | Present (`EchoVendorExtension`) |

SDP declarations vary by implementation. A channel the protocol supports may not be
declared by every HU. Implementers must handle absent channels gracefully
([dhu-divergence.json](../../analysis/reports/oem-vw/dhu-divergence.json),
[sdp-values.json](../../analysis/reports/oem-vw/sdp-values.json)).

### HeadUnitInfo Identity Fields

The SDP request carries identity fields that distinguish the OEM (vehicle manufacturer)
from the HU manufacturer (tier-1 supplier):

| Field | VW MIB3 OI | DHU 2.1 |
|-------|------------|---------|
| `make` | Volkswagen | Google |
| `model` | VW3363 | Desktop Head Unit |
| `year` | 2024 | 2015 |
| `head_unit_make` | LGE | Google |
| `head_unit_model` | COCKPIT_MIB3OI_GP | Desktop Head Unit |
| `software_version` | 2756.04 | 2.1-windows |
| `software_build` | C sample | 2022-12-15-495540972 |
| `car_model` | VW3363 | (not set) |

`make` vs `head_unit_make` shows VW separates OEM (Volkswagen) from HU manufacturer
(LGE). The phone uses these fields for logging, analytics, and feature gating
([sdp-values.json](../../analysis/reports/oem-vw/sdp-values.json)).

### Video Configuration

| Field | VW MIB3 OI (MAIN) | DHU 2.1 (MAIN) |
|-------|-------------------|-----------------|
| Resolutions | 1920x1080, 1280x720, 800x480 | 1280x720 only |
| FPS | 60 | 30 |
| Codec | H264 BP | H264 BP |
| DPI (primary) | 213 (1080p) | 160 (720p) |
| `margin_height` | 240 / 160 / 130 | 0 |
| `viewing_distance` | 900 | 500 |
| Additional displays | None | CLUSTER + AUXILIARY |

VW offers 3 resolutions at 60 FPS (phone picks best match); DHU offers 1 resolution
at 30 FPS but declares all 3 display types (MAIN + CLUSTER + AUXILIARY). Capability
negotiation adapts the phone's rendering pipeline to each HU's declared capabilities
([sdp-values.json](../../analysis/reports/oem-vw/sdp-values.json),
[video.md](video.md)).

### Sensor Configuration

| Dimension | VW MIB3 OI | DHU 2.1 |
|-----------|------------|---------|
| Sensor count | 10 | 13 |
| DHU-only sensors | -- | COMPASS, ODOMETER, TOLL_CARD |
| Fuel types | UNLEADED | UNLEADED, ELECTRIC |

DHU is a test harness that advertises kitchen-sink capabilities (including EV features
on a non-EV). Real OEMs advertise only what their hardware actually supports
([sdp-values.json](../../analysis/reports/oem-vw/sdp-values.json),
[sensor.md](sensor.md)).

### Audio Configuration

| Dimension | VW MIB3 OI | DHU 2.1 |
|-----------|------------|---------|
| Media audio | 48kHz stereo 16-bit | 48kHz stereo 16-bit |
| Speech audio | 48kHz mono 16-bit | 16kHz + 48kHz mono (2 configs) |
| Mic input | 16kHz mono 16-bit | 16kHz mono 16-bit |

Multiple configs give the phone a choice. VW offers one speech config at 48kHz mono;
DHU offers two (16kHz + 48kHz). The phone selects based on its own capability
([sdp-values.json](../../analysis/reports/oem-vw/sdp-values.json),
[audio.md](audio.md)).

For the complete divergence analysis including version-alignment attribution, see
[dhu-divergence.md](../../analysis/reports/oem-vw/dhu-divergence.md).

## Further Reading

- [Protocol Reference](../protocol-reference.md) -- per-message field tables and msg ID catalog
- [Channel Map](../channel-map.md) -- full channel ID table with message listings
- [Confidence Tiers](../verification/01-confidence-tiers.md) -- Platinum/Gold/Silver/Bronze tier system
- [Capture Non-Claim Boundary](../verification/06-capture-non-claim-boundary.md) -- what wire captures can and cannot prove
- [VW-vs-DHU Divergence Report](../../analysis/reports/oem-vw/dhu-divergence.md) -- full OEM divergence analysis
