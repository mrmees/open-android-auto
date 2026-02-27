# Open Android Auto

The most complete open-source Android Auto protocol reference available. Protocol buffer definitions, protocol documentation, wireless Bluetooth setup guides, decompiled headunit firmware analysis, and APK analysis tools.

**164 `.proto` files** organized into 13 categories covering the full AA protocol surface: session control, audio/video streaming, input, sensors, navigation, Bluetooth, WiFi projection, and more.

## Origins

These definitions were reverse-engineered from Android Auto firmware (APK v16.1) and extended from [f1x.studio's aasdk](https://github.com/nicka-2/aasdk) (Michal Szwaj's original Android Auto SDK). The original aasdk provided a proto2 foundation; this collection upgrades to proto3, adds dozens of previously undocumented messages, and includes field-level annotations from live protocol captures.

This repository is the protocol definition layer used by [OpenAuto Prodigy](https://github.com/mrmees/openauto-prodigy), a clean-room open-source Android Auto head unit for Raspberry Pi.

## Directory Structure

All proto files live under `proto/oaa/`:

| Category | Files | Description |
|----------|------:|-------------|
| `common` | 11 | Shared enums and base types: status codes, channel types, session info, error codes |
| `control` | 20 | Session lifecycle: service discovery, channel open/close, ping, auth, shutdown |
| `av` | 15 | Shared audio/video channel types: setup, start/stop, media ack, codec types |
| `video` | 9 | Video channel: resolution, FPS, focus negotiation, display config |
| `audio` | 7 | Audio channels: focus requests/responses, audio types, config |
| `input` | 20 | Input channel: touch events, buttons, absolute/relative input, haptics |
| `sensor` | 33 | Sensor channel: GPS, accel, gyro, speed, RPM, fuel, gear, HVAC, vehicle data |
| `bluetooth` | 7 | Bluetooth channel: pairing requests/responses, methods, status |
| `wifi` | 18 | WiFi projection: security, connection, version negotiation |
| `navigation` | 14 | Navigation status: turn events, distance, maneuvers, lane guidance |
| `phone` | 5 | Phone status: call state, capabilities, voice session |
| `media` | 3 | Media status: playback status, metadata |
| `notification` | 2 | Notification types and channel data |

## Quick Start

### Compile with protoc

All commands assume you run from the repository root with `proto/` as the import path.

**C++:**

```bash
protoc --proto_path=proto --cpp_out=generated/ \
  proto/oaa/control/ServiceDiscoveryRequestMessage.proto \
  proto/oaa/control/ServiceDiscoveryResponseMessage.proto
```

**Python:**

```bash
protoc --proto_path=proto --python_out=generated/ \
  proto/oaa/sensor/GPSLocationData.proto \
  proto/oaa/sensor/SensorEventIndicationMessage.proto
```

**Go:**

```bash
protoc --proto_path=proto --go_out=generated/ --go_opt=paths=source_relative \
  proto/oaa/video/VideoConfigData.proto \
  proto/oaa/video/VideoResolutionEnum.proto
```

**Compile everything:**

```bash
find proto -name '*.proto' | xargs protoc --proto_path=proto --cpp_out=generated/
```

### Use in a CMake project

```cmake
find_package(Protobuf REQUIRED)

file(GLOB_RECURSE PROTO_FILES "${CMAKE_CURRENT_SOURCE_DIR}/proto/oaa/*.proto")

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
- [Protocol Reference](docs/protocol-reference.md) — auto-generated message catalog (80 messages, 8 enums from APK v16.1)
- [Protocol Cross-Reference](docs/protocol-cross-reference.md) — cross-referencing phone-side (APK) and head-unit-side (firmware) protocol implementations
- [Channel Map](docs/channel-map.md) — channel IDs, message types, and data flow directions
- [Field Notes](docs/field-notes.md) — hard-won implementation knowledge and gotchas

### Implementation Guides

- [Wireless Bluetooth Setup](docs/wireless-bluetooth-setup.md) — complete guide to Bluetooth-based wireless AA discovery (SDP, HFP, WiFi handoff)
- [Video Resolution](docs/video-resolution.md) — AA video resolution negotiation and margin support
- [Display Rendering](docs/display-rendering.md) — rendering AA video on non-standard displays with letterboxing and sidebars
- [Phone-Side Debug](docs/phone-side-debug.md) — debugging AA from the phone's perspective
- [Troubleshooting](docs/troubleshooting.md) — common failure modes and diagnostic workflows

### Decompiled Headunit Firmware

Protocol implementation details extracted from commercial AA head units:

- [Alpine Halo9](docs/decompiled_headunit_firmware/alpine-halo9.md)
- [Alpine ILX-W650BT](docs/decompiled_headunit_firmware/alpine-ilx-w650bt.md)
- [Kenwood DNX](docs/decompiled_headunit_firmware/kenwood-dnx.md)
- [Pioneer DMH](docs/decompiled_headunit_firmware/pioneer-dmh.md)
- [Sony XAV](docs/decompiled_headunit_firmware/sony-xav.md)

### Analysis Tools

- [APK Analysis](analysis/README.md) — Python indexer scripts and pre-built SQLite database from Android Auto APK v16.1

### Research & Contributing

- [Research Archive](research/README.md) — reverse-engineering source material, tooling, and validation artifacts
- [Research Provenance](research/provenance.md) — exact source snapshot and import scope
- [Contributing](CONTRIBUTING.md) — how to add or improve definitions

## License

GPLv3. See [LICENSE](LICENSE).

Original aasdk proto definitions copyright (C) 2018 f1x.studio (Michal Szwaj), licensed under GPLv3.

## Credits

- **Michal Szwaj / f1x.studio** -- original aasdk protobuf definitions that form the foundation of this collection
- **OpenAuto Prodigy community** -- protocol research, live capture analysis, and field annotation
- **SonOfGib** -- maintained aasdk fork with additional protocol work
