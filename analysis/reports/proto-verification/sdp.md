# SDP Layer Verification Report

**Date:** 2026-03-07
**APK:** Android Auto 16.2.660604-release
**Method:** DB-driven structure matching + jadx source trace
**Waves:** 9 (all complete)

## Final Totals

| Metric | Count |
|--------|-------|
| Gold (inherited from GAL) | 8 |
| Gold (newly verified) | 104 |
| **Total Gold** | **112** |
| Schema errors fixed | 12 |
| New protos added | 24 |
| Messages retracted | 3 |
| Bronze (unverified) | ~5 (ConnectedDevices msgs, deepest sub-message placeholders) |

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

## Resolved TODOs

1. **TuningParamsA/B/C** — All three reference the SAME class (aaik): 3 fields (enum, uint32, string). Consolidated into shared `TuningEntry` message.
2. **TransportCapabilityEntry (aaix)** — 2 string fields (key + value). Filled.
3. **TransportSecurityEntry/Detail** — Full chain resolved: aajj → aaji → aajh → aajg (5 strings) + aajf (repeated aaje). All Gold.
4. **CapabilityConnectionEntry (aafl)** — NOT empty! Has oneof with 6 message alternatives. CapabilityConnectionConfig field 2 is actually InputModelDescriptor (not same type as field 1).
5. **InputModelEnum** — Gold. Wire encoder m85bF() decoded: values 0, 2-5 valid, value 1 throws. Semantic names unknown.
6. **ConnectedDevices** — Definitively Bronze. Zero proto classes AND zero handler code in 16.2 phone APK. Message IDs are enum-only stubs.
7. **TuningEntryType enum** — Gold. Wire decoder m131bz() decoded: values 0, 2-5. Semantic names unknown.
8. **CapabilityConnectionEntry (aafl)** — Full tree decoded 6 levels deep. 5 different oneof types (aafk empty, aafi 2-msg, aafb bool, aafh complex with nested oneof, aafj empty). Leaf type aaff = enum+uint32+string (same shape as TuningEntry).
9. **TransportSecurityParamEntry (aaje)** — Gold. 2 string fields (key/value pair).
10. **CapConnTuningType enum** — Silver. Same shape as TuningEntryType but separate class; values not yet decoded via code trace.

## Remaining

- **CapConnTuningType enum** — values not decoded (Silver)
- **ConnectedDevices** — aa-proxy-rs schemas assumed correct but unverifiable (Bronze, no APK implementation)

## Key Learnings

1. **Radio SDP was the biggest surprise** — completely restructured between 16.1 and 16.2
2. **TuningParams were not empty** — 16.1 analysis incorrectly marked them as empty placeholders
3. **ConnectedDevices is phone-side unimplemented** — HU-side only feature
4. **Class name collision trap confirmed again** — wcx means ControlChannelConfigWrapper in 16.1 but WifiProjectionData in 16.2
