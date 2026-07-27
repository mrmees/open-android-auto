# Open Android Auto

The most complete open-source Android Auto protocol reference available. Protocol buffer definitions, protocol documentation, wireless Bluetooth setup guides, decompiled headunit firmware analysis, and APK analysis tools.

**248 `.proto` files** organized into 20 categories covering the full AA protocol surface: session control, audio/video streaming, input, sensors, navigation, Bluetooth, WiFi projection, car control, radio, and more.

> **Architecture overview:** These definitions describe services carried by the
> Android Auto multiplexed protocol. For framing, SDP binding, and capability
> negotiation, see the [Channel Architecture Reference](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/architecture.md).

## Origins

These definitions were reverse-engineered from Android Auto firmware (APK v16.1 through v17.3) and extended from [f1x.studio's aasdk](https://github.com/nicka-2/aasdk) (Michal Szwaj's original Android Auto SDK). The collection is predominantly proto2, with a proto3 subset for enum wrappers and newer types. Per-file `syntax` declarations are authoritative. The repository adds dozens of previously undocumented messages and field-level annotations from live protocol captures.

This repository is the protocol definition layer used by [OpenAuto Prodigy](https://github.com/mrmees/openauto-prodigy), a clean-room open-source Android Auto head unit for Raspberry Pi.

Version tags publish an orphan `dist` branch containing only this README,
`LICENSE`, and `oaa/**/*.proto`. Documentation links in this file point back to
the full `main` branch so they remain usable from that minimal snapshot.

## Changes since v1.3.1

- Added the audited Android Auto 17.3 protocol surface, including blended/multi-display UI configuration, modern media and service markers, car-intent support, critical-UI and integrated-overlay payloads, and newer navigation and vehicle-energy structures.
- Added GAL-gated behavior documented for downstream rollout: GAL 4.3 display/video additions; GAL 5.0 extended AV/audio start data; GAL 5.1 standalone audio `MediaOptions` and `VehicleEnergyForecast`; and GAL 6.0 video media options and optional modern codec paths.
- Renamed `AVChannel.channel_id` to `display_id` at the existing `uint32` field 6 and changed AV stream fields to the correct `MediaCodecType` enum. These preserve their wire tags and wire types but require regeneration and generated-source updates.
- Corrected `ChannelDescriptor` fields 16 and 17 to the audited car-local-media and buffered-media service markers and added car intent at field 18. The wire type remains length-delimited, but consumers of the earlier incorrect field meanings must update their service bindings.
- Corrected AV message-ID names and assignments through `0x8015`; `0x8010` remains reserved/unknown.

## Confidence annotations

Definitions carry `confidence:` comments. `gold`, `silver`, and `bronze` record
decreasing levels of corroboration; `unverified` marks a candidate awaiting
evidence; and `retracted` marks preserved research history that consumers must
not treat as supported Android Auto protocol. Find retracted definitions in a
distribution with:

```bash
grep -R -l -E 'confidence: retracted|RETRACTED' oaa --include='*.proto'
```

The complete methodology is in the [confidence-tier documentation](https://github.com/mrmees/open-android-auto/blob/main/docs/verification/01-confidence-tiers.md).

## Directory Structure

All proto files live under `oaa/`:

| Category | Files | Description |
|----------|------:|-------------|
| `audio` | 10 | Audio channels: focus requests/responses, audio types, config |
| `av` | 19 | Shared audio/video channel types: setup, start/stop, media ack, codec types |
| `bluetooth` | 9 | Bluetooth channel: pairing, authentication, methods, status |
| `carcontrol` | 3 | Car control: HVAC, door locks, mirrors, vehicle properties |
| `carintent` | 1 | Car intent service payloads |
| `common` | 16 | Shared enums and base types: status codes, channel types, session info, error codes |
| `control` | 35 | Session lifecycle: service discovery, channel open/close, ping, auth, shutdown |
| `generic` | 1 | Generic channel message wrapper (channel open acknowledgement) |
| `input` | 23 | Input channel: touch events, buttons, absolute/relative input, haptics |
| `media` | 12 | Media status: playback status, metadata, browsing, car local media |
| `mediabrowser` | 2 | Legacy media browser message IDs and payloads |
| `mic` | 1 | Microphone channel: mic open response |
| `navigation` | 17 | Navigation status: turn events, distance, maneuvers, lane guidance, energy forecast |
| `notification` | 2 | Notification types and channel data |
| `phone` | 3 | Phone status: call state, input actions |
| `radio` | 6 | Radio channel: tuner control, presets, station metadata, band/codec enums |
| `sensor` | 43 | Sensor channel: GPS, accel, gyro, speed, RPM, fuel, gear, HVAC, vehicle data |
| `verification` | 2 | GAL verification and diagnostics messages |
| `video` | 20 | Video channel: resolution, FPS, focus negotiation, display config, overlays |
| `wifi` | 23 | WiFi projection: security, connection, version negotiation |

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

### Verify a full repository checkout

The following verification tooling lives on `main` and is intentionally not
part of the minimal `dist` branch. In a full repository checkout, create a local
test environment and run the repository verification contract:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-test.txt
make PYTHON=.venv/bin/python verify
```

`make PYTHON=.venv/bin/python test-integration` runs the optional historical
APK-index checks. It prints explicit skips when the ignored local index
snapshots are unavailable.

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

Some newer notification, response, and buffered-media files retain audited APK
names that do not use these suffixes. Their per-file package declarations are
authoritative.

Import paths use the `oaa/<category>/File.proto` format:

```protobuf
import "oaa/common/StatusEnum.proto";
import "oaa/control/ChannelDescriptorData.proto";
import "oaa/video/VideoConfigData.proto";
```

## Documentation

### Protocol Reference

- [Channel Architecture Reference](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/architecture.md) — AA multiplexing, framing, SDP binding, capability negotiation
- [Protocol Reference](https://github.com/mrmees/open-android-auto/blob/main/docs/protocol-reference.md) — auto-generated message catalog
- [Protocol Cross-Reference](https://github.com/mrmees/open-android-auto/blob/main/docs/protocol-cross-reference.md) — cross-referencing phone-side (APK) and head-unit-side (firmware) protocol implementations
- [Channel Map](https://github.com/mrmees/open-android-auto/blob/main/docs/channel-map.md) — channel IDs, message types, and data flow directions
- [Field Notes](https://github.com/mrmees/open-android-auto/blob/main/docs/field-notes.md) — hard-won implementation knowledge and gotchas

### Implementation Guides

- [Wireless Bluetooth Setup](https://github.com/mrmees/open-android-auto/blob/main/docs/wireless-bluetooth-setup.md) — complete guide to Bluetooth-based wireless AA discovery (SDP, HFP, WiFi handoff)
- [Video Resolution](https://github.com/mrmees/open-android-auto/blob/main/docs/video-resolution.md) — AA video resolution negotiation and margin support
- [Display Rendering](https://github.com/mrmees/open-android-auto/blob/main/docs/display-rendering.md) — rendering AA video on non-standard displays with letterboxing and sidebars
- [Phone-Side Debug](https://github.com/mrmees/open-android-auto/blob/main/docs/phone-side-debug.md) — debugging AA from the phone's perspective
- [Troubleshooting](https://github.com/mrmees/open-android-auto/blob/main/docs/troubleshooting.md) — common failure modes and diagnostic workflows

### Channel Specifications

Detailed protocol specs for each Android Auto channel:

- [Audio](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/audio.md) — codec negotiation, focus, PCM/AAC config
- [Bluetooth](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/bluetooth.md) — pairing, connection, status
- [Car Control](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/carcontrol.md) — HVAC, door locks, mirrors
- [Coolwalk Layout](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/coolwalk-layout.md) — UI layout engine and phenotype flags
- [Display Routing](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/display-routing.md) — multi-display content routing
- [Input](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/input.md) — touch, buttons, rotary, touchpad
- [Media](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/media.md) — playback status, metadata
- [Navigation](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/nav.md) — turn-by-turn, routing, lane guidance
- [Phone](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/phone.md) — call state, contacts, SIM
- [Radio](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/radio.md) — tuner, presets, station metadata
- [Sensor](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/sensor.md) — GPS, speed, fuel, gear, accelerometer, 26 sensor types
- [Video](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/video.md) — projected display, focus modes, resolution, UI config
- [WiFi Projection](https://github.com/mrmees/open-android-auto/blob/main/docs/channels/wifi-projection.md) — wireless AA setup and config

### Session Lifecycle

Step-by-step AA handshake and session lifecycle:

- [Transport Setup](https://github.com/mrmees/open-android-auto/blob/main/docs/interactions/01-transport-setup.md) — TCP/AOA connection
- [Version & SSL Auth](https://github.com/mrmees/open-android-auto/blob/main/docs/interactions/02-version-ssl-auth.md) — TLS negotiation
- [Service Discovery](https://github.com/mrmees/open-android-auto/blob/main/docs/interactions/03-service-discovery.md) — SDP exchange
- [Channel Lifecycle](https://github.com/mrmees/open-android-auto/blob/main/docs/interactions/04-channel-lifecycle.md) — open/close/teardown
- [Session Maintenance](https://github.com/mrmees/open-android-auto/blob/main/docs/interactions/05-session-maintenance-teardown.md) — keep-alive, errors, disconnect

### Verification Framework

How discoveries are tracked and validated:

- [Confidence Tiers](https://github.com/mrmees/open-android-auto/blob/main/docs/verification/01-confidence-tiers.md) — Gold/Silver/Bronze scoring
- [Audit Trail Format](https://github.com/mrmees/open-android-auto/blob/main/docs/verification/02-audit-trail-format.md) — `.audit.yaml` sidecar spec
- [Verification Procedures](https://github.com/mrmees/open-android-auto/blob/main/docs/verification/03-verification-procedures.md) — wire capture and APK validation
- [Source Provenance](https://github.com/mrmees/open-android-auto/blob/main/docs/verification/04-source-provenance.md) — attribution tracking

### Decompiled Headunit Firmware

Protocol implementation details extracted from commercial AA head units:

- [Alpine Halo9](https://github.com/mrmees/open-android-auto/blob/main/docs/decompiled_headunit_firmware/alpine-halo9.md)
- [Alpine ILX-W650BT](https://github.com/mrmees/open-android-auto/blob/main/docs/decompiled_headunit_firmware/alpine-ilx-w650bt.md)
- [Kenwood DNX](https://github.com/mrmees/open-android-auto/blob/main/docs/decompiled_headunit_firmware/kenwood-dnx.md)
- [Pioneer DMH](https://github.com/mrmees/open-android-auto/blob/main/docs/decompiled_headunit_firmware/pioneer-dmh.md)
- [Sony XAV](https://github.com/mrmees/open-android-auto/blob/main/docs/decompiled_headunit_firmware/sony-xav.md)

### Analysis Tools

- [APK Analysis](https://github.com/mrmees/open-android-auto/blob/main/analysis/README.md) — Python indexer scripts and pre-built SQLite databases from Android Auto APK v16.1 and v16.2

### Research & Contributing

- [Research Archive](https://github.com/mrmees/open-android-auto/blob/main/research/README.md) — reverse-engineering source material, tooling, and validation artifacts
- [Research Provenance](https://github.com/mrmees/open-android-auto/blob/main/research/provenance.md) — exact source snapshot and import scope
- [Contributing](https://github.com/mrmees/open-android-auto/blob/main/CONTRIBUTING.md) — how to add or improve definitions

## Workflow

- [AGENTS.md](https://github.com/mrmees/open-android-auto/blob/main/AGENTS.md) — repository workflow loop and verification expectations
- [Current Roadmap](https://github.com/mrmees/open-android-auto/blob/main/docs/roadmap-current.md) — `Now / Next / Later` priorities
- [Session Handoffs](https://github.com/mrmees/open-android-auto/blob/main/docs/session-handoffs.md) — append-only continuity log between sessions

## License

GPLv3. See [LICENSE](LICENSE).

Original aasdk proto definitions copyright (C) 2018 f1x.studio (Michal Szwaj), licensed under GPLv3.

## Credits

- **Michal Szwaj / f1x.studio** -- original aasdk protobuf definitions that form the foundation of this collection
- **OpenAuto Prodigy community** -- protocol research, live capture analysis, and field annotation
- **SonOfGib** -- maintained aasdk fork with additional protocol work
