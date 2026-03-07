# SDP Layer Verification Report

**Date:** 2026-03-07
**APK:** Android Auto 16.2.660604-release
**Method:** DB-driven structure matching + jadx source trace
**Waves:** 9 (all complete)

## Final Totals

| Metric | Count |
|--------|-------|
| Gold (inherited from GAL) | 8 |
| Gold (newly verified) | 76 |
| **Total Gold** | **84** |
| Schema errors fixed | 5 |
| New protos added | 3 |
| Messages retracted | 3 |
| Bronze (unverified) | ~6 (ConnectedDevices msgs, placeholder sub-messages) |

## Wave Summary

### Wave 1 — SDP Envelope
ServiceDiscoveryResponse, ServiceDiscoveryRequest, ChannelDescriptor, ServiceDiscoveryUpdate, 4 feature placeholders. All Gold, no schema changes. Class names updated for 16.2.

### Wave 2 — Phone Capabilities
12 protos Gold. **PingConfigEntry fixed:** 4 uint32 fields → 2 fields (int64 + int32). PhoneConnectionConfig marked @Deprecated in 16.2.

### Wave 3 — AV + Video SDP
11 Gold (AVChannel, VideoConfig, AdditionalVideoConfig, 4 sub-messages, 4 enums). No schema changes needed.

### Wave 4 — Audio + Mic SDP
3 Gold (AVInputChannel, AudioConfig, AudioFocusChannel). No schema changes.

### Wave 5 — Navigation + Sensor SDP
4 Gold (NavigationChannel, NavigationImageOptions, SensorChannel). No schema changes.

### Wave 6 — Radio SDP (Full Rewrite)
**Largest change.** Old RadioStation (14 fields) and RadioBand (2 fields) completely removed. Replaced with new 3-level hierarchy: RadioChannelConfig(wap) → RadioBands(wab) → RadioBandGroup(waa). 3 messages retracted, 3 new messages added.

### Wave 7 — Bluetooth + WiFi SDP
Quick confirmation. Both already Gold from GAL verification. No changes needed.

### Wave 8 — CarControl + Remaining Channels
CarControlChannel filled (was empty → 3 repeated fields: CarPropertyConfig, CarControl, CarActionEntry). NotificationChannel filled (was empty → 1 bool). VendorExtension verified. 4 empty channel placeholders confirmed still empty.

### Wave 9 — Connection Config + Common Protos
21 protos verified. Key findings:
- **ConnectionConfiguration tree:** All Gold. 24 class names remapped for 16.2.
- **TuningParamsA-D:** Were empty placeholders, now have 1 field each (message/repeated message/message/string).
- **ControlChannelConfig:** 3-layer nesting confirmed (Wrapper→Config→Params). All Gold.
- **Common protos:** PingConfiguration, SessionInfo, VersionFeatureFlags, AssistantFeatureFlags — all Gold, no schema changes. No new fields in 16.2.
- **InputModel:** All 4 messages Gold, no schema changes.
- **ConnectedDevices:** Bronze — message IDs exist in enum registry but no handler implementation in phone APK.
- **TransportSecurityEntry/Detail:** 16.2 class names not resolved (Silver/Bronze).

## Remaining TODO

These items have correct field schemas but need deeper analysis:

1. **TuningParamsADetail, TuningParamsBEntry, TuningParamsCDetail** — internal field schemas unknown
2. **TransportCapabilityEntry** — internal fields unknown
3. **TransportSecurityEntry/Detail** — 16.2 class names not resolved
4. **CapabilityConnectionEntry** — confirmed empty placeholder
5. **InputModelEnum** — only default value 0, full enum values unknown
6. **ConnectedDevices messages** — schemas from aa-proxy-rs, not independently verified against APK

These are all low-priority items that would require wire captures or deeper reverse engineering to resolve.

## Key Learnings

1. **Radio SDP was the biggest surprise** — completely restructured between 16.1 and 16.2
2. **TuningParams were not empty** — 16.1 analysis incorrectly marked them as empty placeholders
3. **ConnectedDevices is phone-side unimplemented** — HU-side only feature
4. **Class name collision trap confirmed again** — wcx means ControlChannelConfigWrapper in 16.1 but WifiProjectionData in 16.2
