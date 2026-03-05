# Open Android Auto

The most complete open-source Android Auto protocol reference available. Protocol buffer definitions, protocol documentation, wireless Bluetooth setup guides, decompiled headunit firmware analysis, and APK analysis tools.

**223 `.proto` files** organized into 16 categories covering the full AA protocol surface: session control, audio/video streaming, input, sensors, navigation, Bluetooth, WiFi projection, car control, radio, and more.

## Origins

These definitions were reverse-engineered from Android Auto firmware (APK v16.1 and v16.2) and extended from [f1x.studio's aasdk](https://github.com/nicka-2/aasdk) (Michal Szwaj's original Android Auto SDK). The original aasdk provided a proto2 foundation; this collection upgrades to proto3, adds dozens of previously undocumented messages, and includes field-level annotations from live protocol captures.

This repository is the protocol definition layer used by [OpenAuto Prodigy](https://github.com/mrmees/openauto-prodigy), a clean-room open-source Android Auto head unit for Raspberry Pi.

## Directory Structure

All proto files live under `oaa/`:

| Category | Files | Description |
|----------|------:|-------------|
| `audio` | 10 | Audio channels: focus requests/responses, audio types, config |
| `av` | 18 | Shared audio/video channel types: setup, start/stop, media ack, codec types |
| `bluetooth` | 7 | Bluetooth channel: pairing requests/responses, methods, status |
| `carcontrol` | 3 | Car control: HVAC, door locks, mirrors, vehicle properties |
| `common` | 12 | Shared enums and base types: status codes, channel types, session info, error codes |
| `control` | 32 | Session lifecycle: service discovery, channel open/close, ping, auth, shutdown |
| `generic` | 1 | Generic channel message wrapper (channel open acknowledgement) |
| `input` | 22 | Input channel: touch events, buttons, absolute/relative input, haptics |
| `media` | 11 | Media status: playback status, metadata, browsing |
| `navigation` | 16 | Navigation status: turn events, distance, maneuvers, lane guidance |
| `notification` | 2 | Notification types and channel data |
| `phone` | 6 | Phone status: call state, capabilities, voice session |
| `radio` | 5 | Radio channel: tuner control, presets, station metadata, band/codec enums |
| `sensor` | 43 | Sensor channel: GPS, accel, gyro, speed, RPM, fuel, gear, HVAC, vehicle data |
| `video` | 13 | Video channel: resolution, FPS, focus negotiation, display config |
| `wifi` | 22 | WiFi projection: security, connection, version negotiation |

## Quick Start

### Compile with protoc

All commands assume you run from the repository root (the directory containing `oaa/`).

**C++:**

```bash
protoc --proto_path=. --cpp_out=generated/ \
  oaa/control/ServiceDiscoveryRequestMessage.proto \
  oaa/control/ServiceDiscoveryResponseMessage.proto
```

**Python:**

```bash
protoc --proto_path=. --python_out=generated/ \
  oaa/sensor/GPSLocationData.proto \
  oaa/sensor/SensorEventIndicationMessage.proto
```

**Go:**

```bash
protoc --proto_path=. --go_out=generated/ --go_opt=paths=source_relative \
  oaa/video/VideoConfigData.proto \
  oaa/video/VideoResolutionEnum.proto
```

**Compile everything:**

```bash
find oaa -name '*.proto' | xargs protoc --proto_path=. --cpp_out=generated/
```

### Use in a CMake project

```cmake
find_package(Protobuf REQUIRED)

file(GLOB_RECURSE PROTO_FILES "${CMAKE_CURRENT_SOURCE_DIR}/oaa/*.proto")

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${PROTO_FILES})
add_library(aa_proto ${PROTO_SRCS} ${PROTO_HDRS})
target_include_directories(aa_proto PUBLIC ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(aa_proto PUBLIC protobuf::libprotobuf)
```

## Package Namespaces

Files use a suffix-based naming convention that maps to four protobuf packages:

| Suffix | Package | Purpose |
|--------|---------|---------|
| `*Message.proto` | `oaa.proto.messages` | Request/response/indication messages |
| `*Data.proto` | `oaa.proto.data` | Structured data types (configs, events, payloads) |
| `*Enum.proto` | `oaa.proto.enums` | Enumeration definitions |
| `*IdsEnum.proto` | `oaa.proto.ids` | Channel-specific message ID enumerations |

Import paths use the `oaa/<category>/File.proto` format:

```protobuf
import "oaa/common/StatusEnum.proto";
import "oaa/control/ChannelDescriptorData.proto";
import "oaa/video/VideoConfigData.proto";
```

## Documentation

### Protocol Reference

- [Protocol Overview](docs/protocol-overview.md) — high-level AA protocol architecture
- [Protocol Reference](docs/protocol-reference.md) — auto-generated message catalog (86 messages, 8 enums)
- [Protocol Cross-Reference](docs/protocol-cross-reference.md) — cross-referencing phone-side (APK) and head-unit-side (firmware) protocol implementations
- [Channel Map](docs/channel-map.md) — channel IDs, message types, and data flow directions
- [Field Notes](docs/field-notes.md) — hard-won implementation knowledge and gotchas

### Implementation Guides

- [Wireless Bluetooth Setup](docs/wireless-bluetooth-setup.md) — complete guide to Bluetooth-based wireless AA discovery (SDP, HFP, WiFi handoff)
- [Video Resolution](docs/video-resolution.md) — AA video resolution negotiation and margin support
- [Display Rendering](docs/display-rendering.md) — rendering AA video on non-standard displays with letterboxing and sidebars
- [Phone-Side Debug](docs/phone-side-debug.md) — debugging AA from the phone's perspective
- [Troubleshooting](docs/troubleshooting.md) — common failure modes and diagnostic workflows

### Channel Specifications

Detailed protocol specs for each Android Auto channel:

- [Audio](docs/channels/audio.md) — codec negotiation, focus, PCM/AAC config
- [Bluetooth](docs/channels/bluetooth.md) — pairing, connection, status
- [Car Control](docs/channels/carcontrol.md) — HVAC, door locks, mirrors
- [Coolwalk Layout](docs/channels/coolwalk-layout.md) — UI layout engine and phenotype flags
- [Display Routing](docs/channels/display-routing.md) — multi-display content routing
- [Input](docs/channels/input.md) — touch, buttons, rotary, touchpad
- [Media](docs/channels/media.md) — playback status, metadata
- [Navigation](docs/channels/nav.md) — turn-by-turn, routing, lane guidance
- [Phone](docs/channels/phone.md) — call state, contacts, SIM
- [Radio](docs/channels/radio.md) — tuner, presets, station metadata
- [WiFi Projection](docs/channels/wifi-projection.md) — wireless AA setup and config

### Session Lifecycle

Step-by-step AA handshake and session lifecycle:

- [Transport Setup](docs/interactions/01-transport-setup.md) — TCP/AOA connection
- [Version & SSL Auth](docs/interactions/02-version-ssl-auth.md) — TLS negotiation
- [Service Discovery](docs/interactions/03-service-discovery.md) — SDP exchange
- [Channel Lifecycle](docs/interactions/04-channel-lifecycle.md) — open/close/teardown
- [Session Maintenance](docs/interactions/05-session-maintenance-teardown.md) — keep-alive, errors, disconnect

### Verification Framework

How discoveries are tracked and validated:

- [Confidence Tiers](docs/verification/01-confidence-tiers.md) — Gold/Silver/Bronze scoring
- [Audit Trail Format](docs/verification/02-audit-trail-format.md) — `.audit.yaml` sidecar spec
- [Verification Procedures](docs/verification/03-verification-procedures.md) — wire capture and APK validation
- [Source Provenance](docs/verification/04-source-provenance.md) — attribution tracking

### Decompiled Headunit Firmware

Protocol implementation details extracted from commercial AA head units:

- [Alpine Halo9](docs/decompiled_headunit_firmware/alpine-halo9.md)
- [Alpine ILX-W650BT](docs/decompiled_headunit_firmware/alpine-ilx-w650bt.md)
- [Kenwood DNX](docs/decompiled_headunit_firmware/kenwood-dnx.md)
- [Pioneer DMH](docs/decompiled_headunit_firmware/pioneer-dmh.md)
- [Sony XAV](docs/decompiled_headunit_firmware/sony-xav.md)

### Analysis Tools

- [APK Analysis](analysis/README.md) — Python indexer scripts and pre-built SQLite databases from Android Auto APK v16.1 and v16.2

### Research & Contributing

- [Research Archive](research/README.md) — reverse-engineering source material, tooling, and validation artifacts
- [Research Provenance](research/provenance.md) — exact source snapshot and import scope
- [Contributing](CONTRIBUTING.md) — how to add or improve definitions

## Workflow

- [AGENTS.md](AGENTS.md) — repository workflow loop and verification expectations
- [Current Roadmap](docs/roadmap-current.md) — `Now / Next / Later` priorities
- [Session Handoffs](docs/session-handoffs.md) — append-only continuity log between sessions

## License

GPLv3. See [LICENSE](LICENSE).

Original aasdk proto definitions copyright (C) 2018 f1x.studio (Michal Szwaj), licensed under GPLv3.

## Credits

- **Michal Szwaj / f1x.studio** -- original aasdk protobuf definitions that form the foundation of this collection
- **OpenAuto Prodigy community** -- protocol research, live capture analysis, and field annotation
- **SonOfGib** -- maintained aasdk fork with additional protocol work
