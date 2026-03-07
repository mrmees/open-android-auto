# SDP Layer Verification Design

**Date:** 2026-03-07
**Status:** Approved
**Prerequisite:** GAL verification complete (194 Gold protos across 14 channels)

## Goal

Verify all Service Discovery Protocol (SDP) protobuf schemas against the 16.2 APK source code. The SDP layer is what enables connection negotiation — the HU advertises its capabilities via `ServiceDiscoveryResponse`, the phone advertises via `ServiceDiscoveryRequest`, and both sides use this to decide which channels to open and how to configure them.

This is the logical next step after GAL verification: we've confirmed what the messages **say** on each channel, now we confirm the handshake that **opens** those channels.

## Scope

- **Target:** All SDP-related protos in `oaa/control/`, `oaa/common/`, and channel-specific `*ChannelData.proto` files
- **Ground truth:** 16.2 APK (`analysis/android_auto_16.2.660604-release_162660604/`)
- **Depth:** Verify structure (field numbers, types, nesting, direction) against 16.2 classes. Placeholder sub-message **internals** (e.g., TuningParamsA fields) are marked TODO for future sessions.
- **Confidence target:** Gold for all verified structures
- **Method:** Same agent-based approach as GAL verification — agents research, main context applies changes

## What's Already Gold

8 SDP items verified during GAL sweep:

| Proto | Source |
|-------|--------|
| HeadUnitInfo (vuq) | Control channel verification |
| SensorChannelConfig (wbk) | Sensor verification |
| SensorTypeEntry (wbj) | Sensor verification |
| InputChannelConfig (vxm) | Input verification |
| TouchScreenConfig (vxl) | Input verification |
| TouchPadConfig (vxk) | Input verification |
| BluetoothChannelConfig (vvo) | Bluetooth verification |
| WifiChannel (wcx) | WiFi verification |

## Verification Waves

### Wave 1 — SDP Envelope

The top-level containers that everything else nests inside.

| Proto | File | 16.1 Class | Fields | Notes |
|-------|------|-----------|--------|-------|
| ServiceDiscoveryResponse | control/ServiceDiscoveryResponseMessage.proto | wby | 17 | Car identity, channel array, HU info |
| ServiceDiscoveryRequest | control/ServiceDiscoveryRequestMessage.proto | wbx | 6 | Phone icons, device name, session |
| ChannelDescriptor | control/ChannelDescriptorData.proto | wbw | 17 | Field-to-channel mapping, the spine of SDP |

Also verify: ServiceDiscoveryFeatureA/B/C/D (empty placeholders in SDR), ServiceDiscoveryUpdate (msg 26).

### Wave 2 — Phone Capabilities (parallel with Wave 3+)

What the phone sends about itself. Independent from HU-side, can run in parallel.

| Proto | File | 16.1 Class | Fields | Notes |
|-------|------|-----------|--------|-------|
| PhoneCapabilities | control/PhoneCapabilitiesMessage.proto | aagr | 6 | Top-level phone caps |
| DeviceInfo | control/PhoneCapabilitiesData.proto | vve | 9 | Manufacturer, model, Android ver |
| PhoneConnectionConfig | control/PhoneCapabilitiesData.proto | wdm | 5 | WiFi credentials |
| CapabilityFlag | control/CapabilityData.proto | aagh | 2 | Bool + name |
| CapabilityPair | control/CapabilityData.proto | aags | 2 | Bool pair |
| CapabilityEntry | control/CapabilityData.proto | aagv | 10 | Individual capability |
| PingConfigPair / PingConfigEntry | control/CapabilityData.proto | aaft | 2+4 | Ping config |
| PhoneIdentifierType enum | control/PhoneCapabilitiesMessage.proto | — | placeholder | |
| WifiSecurityMode enum | control/PhoneCapabilitiesData.proto | wdr | 11 values | |
| WifiAccessPointType enum | control/PhoneCapabilitiesData.proto | — | 2 values | |

### Wave 3 — AV + Video SDP Configs

Highest priority for rendering — controls video resolution, codec, FPS.

| Proto | File | 16.1 Class | Fields | Notes |
|-------|------|-----------|--------|-------|
| AVChannel | av/AVChannelData.proto | vys | 9 | Stream type, video/audio config, display |
| VideoConfig | video/VideoConfigData.proto | — | 11 | Resolution, FPS, margins, DPI, codec |
| AdditionalVideoConfig | video/AdditionalVideoConfigData.proto | — | ~6 | Extended video params |
| AVStreamType enum | av/AVStreamTypeEnum.proto | — | — | |

### Wave 4 — Audio + Mic SDP Configs

| Proto | File | 16.1 Class | Fields | Notes |
|-------|------|-----------|--------|-------|
| AVInputChannel | av/AVInputChannelData.proto | vyt | 3 | Mic input config |
| AudioConfig | audio/AudioConfigData.proto | — | 3 | Sample rate, bit depth, channels |
| AudioFocusChannel | audio/AudioFocusChannelData.proto | — | 0 | Empty presence marker |

### Wave 5 — Navigation + Sensor SDP Configs

Partially Gold already. Verify parent containers.

| Proto | File | 16.1 Class | Fields | Notes |
|-------|------|-----------|--------|-------|
| NavigationChannel | navigation/NavigationChannelData.proto | vzr | 3 | Min interval, type, image options |
| NavigationImageOptions | navigation/NavigationImageOptionsData.proto | — | — | Sub-msg of NavigationChannel |
| SensorChannel | sensor/SensorChannelData.proto | wbu | 4 | Already Gold children, verify parent |

### Wave 6 — Radio SDP (Full Rewrite)

Known stale. 16.1 RadioStation structure replaced in 16.2 with RadioChannelConfig -> RadioBands -> RadioBandGroup.

| Proto | File | 16.1 Class | Fields | Notes |
|-------|------|-----------|--------|-------|
| RadioChannel | control/RadioChannelData.proto | way | 1+nested | Container — needs full rewrite |
| RadioStation | control/RadioChannelData.proto | wax | 14 | GONE in 16.2 |
| RadioBand | control/RadioChannelData.proto | wbe | 2 | GONE in 16.2 |
| RadioChannelConfig (NEW) | — | wap | — | 16.2 replacement |
| RadioBands (NEW) | — | wab | — | 16.2 sub-message |
| RadioBandGroup (NEW) | — | waa | — | 16.2 sub-message |

### Wave 7 — Bluetooth + WiFi SDP

Already partially Gold. Confirm parent containers match.

| Proto | File | Fields | Notes |
|-------|------|--------|-------|
| BluetoothChannel | bluetooth/BluetoothChannelData.proto | 2 | Already Gold, confirm parent |
| WifiChannel | wifi/WifiChannelData.proto | 1 | Already Gold (bssid), confirm parent |

### Wave 8 — CarControl + Remaining Channels

| Proto | File | Fields | Notes |
|-------|------|--------|-------|
| CarControlChannel | control/ChannelDescriptorData.proto (inline) | 0 (placeholder) | vwo has 3 fields in 16.2 — fill in |
| VendorExtensionChannel | control/VendorExtensionChannelData.proto | 3 | Verify against 16.2 |
| MediaBrowserChannel | control/ChannelDescriptorData.proto (inline) | 0 | Verify still empty in 16.2 |
| NotificationChannel | notification/NotificationChannelData.proto | 0 | Verify still empty in 16.2 |
| GenericNotificationChannel | control/ChannelDescriptorData.proto (inline) | 0 | Verify still empty in 16.2 |
| VoiceChannel | control/ChannelDescriptorData.proto (inline) | 0 | Verify still empty in 16.2 |

### Wave 9 — Connection Config + Common Protos

| Proto | File | Fields | Notes |
|-------|------|--------|-------|
| ConnectionConfiguration | control/ConnectionConfigurationData.proto | big tree | Verify structure, TODO internals |
| ControlChannelConfigMessage | control/ControlChannelConfigMessage.proto | 1 | wcx->wcn class change in 16.2 |
| ControlChannelConfigData | control/ControlChannelConfigData.proto | nested | Three-layer nesting |
| PingConfiguration | common/PingConfigurationData.proto | 2 | Completely unverified |
| SessionInfo | common/SessionInfoData.proto | 4 | |
| FeatureFlags | common/FeatureFlagsData.proto | 2 | |
| AssistantFeatureFlags | common/AssistantFeatureFlagsData.proto | 14 | |
| InputModelData messages | control/InputModelData.proto | ~4 msgs | Handwriting config etc. |
| ConnectedDevicesMessages | control/ConnectedDevicesMessages.proto | — | Bronze, no implementation |

## Verification Checklist (per proto)

Same 6-check protocol as GAL verification:

1. **Channel binding** — confirm which SDP field or message carries this proto
2. **16.2 class mapping** — find the correct obfuscated class in 16.2 DB
3. **Field schema** — field numbers, types, required/optional, sub-message references
4. **Cross-references** — imports, enum references, shared types
5. **Enum values** — complete value lists from 16.2
6. **Confidence upgrade** — Silver/Bronze -> Gold with evidence

## Agent Strategy

Same proven approach from GAL verification:

- Group agents by functional area (1 agent per wave, or split large waves)
- Each agent: check DB -> read audit yaml -> trace jadx source -> 6-check -> report findings
- Agents do NOT modify files — they report findings, main context applies changes
- Key paths for agents:
  - DB: `analysis/android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db`
  - jadx: `analysis/aa-16.2/jadx-output/sources/p000/` (all classes under p000)
  - Protos: `oaa/` directory tree
- Warn agents about known pitfalls (obfuscated name reuse across versions, +1 msg ID offset on AV channels)
- Batch results per wave, review, apply changes, commit

## Out of Scope (future sessions)

- Filling in placeholder sub-message internals (TuningParamsA/B/C/D, TransportCapabilityEntry, TransportSecurityDetail, CapabilityValueMsg, CapabilityConnectionEntry)
- Wire capture validation (comparing proto output against actual SDP bytes from captures)
- VERSION_REQUEST/VERSION_RESPONSE raw binary format (not protobuf)
- SSL_HANDSHAKE message internals (raw TLS, not protobuf)

## Success Criteria

- All SDP protos verified to Gold confidence against 16.2 APK
- RadioChannelData rewritten for 16.2 structure
- CarControlChannel placeholder filled with actual fields
- All 16.2 class name comments updated
- Placeholder sub-messages marked with TODO comments
- Verification report at `analysis/reports/proto-verification/sdp.md`
