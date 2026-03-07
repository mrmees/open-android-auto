# SDP Verification Progress

**Design:** `docs/plans/2026-03-07-sdp-verification-design.md`
**Started:** 2026-03-07

## Summary

| Status | Count |
|--------|-------|
| Already Gold (from GAL) | 8 |
| Verified (new Gold) | 38 |
| Schema Errors Found & Fixed | 1 |
| New Protos Discovered | 0 |
| Retracted / Removed | 0 |
| Pending | ~20 |

## Wave Status

| Wave | Scope | Status | Notes |
|------|-------|--------|-------|
| 1 | SDP Envelope (SDR, SDReq, ChannelDescriptor) | **COMPLETE** | 8 Gold (SDR, SDReq, ChannelDesc, SDUpdate, 4 features). No schema changes, class names updated. |
| 2 | Phone Capabilities | **COMPLETE** | 12 Gold. PingConfigEntry fixed: 4→2 fields (int64+int32). PhoneConnectionConfig @Deprecated in 16.2. |
| 3 | AV + Video SDP Configs | **COMPLETE** | 11 Gold (AVChannel, VideoConfig, AdditionalVideoConfig, 4 sub-msgs, 4 enums). No schema changes. |
| 4 | Audio + Mic SDP Configs | **COMPLETE** | 3 Gold (AVInputChannel=vyf, AudioConfig=vvb, AudioFocusChannel=vxc). No schema changes. |
| 5 | Navigation + Sensor SDP | **COMPLETE** | 4 Gold (NavigationChannel=vzd, NavigationImageOptions, SensorChannel=wbk). No schema changes. |
| 6 | Radio SDP (full rewrite) | PENDING | |
| 7 | Bluetooth + WiFi SDP | PENDING | |
| 8 | CarControl + Remaining Channels | PENDING | |
| 9 | Connection Config + Common Protos | PENDING | |

## Resume Pointer

Waves 1-5 complete. Start at Wave 6.
