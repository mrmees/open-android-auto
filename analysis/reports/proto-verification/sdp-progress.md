# SDP Verification Progress

**Design:** `docs/plans/2026-03-07-sdp-verification-design.md`
**Started:** 2026-03-07
**Completed:** 2026-03-07

## Summary

| Status | Count |
|--------|-------|
| Already Gold (from GAL) | 8 |
| Verified (new Gold) | 76 |
| Schema Errors Found & Fixed | 4 |
| New Protos Discovered | 3 |
| Retracted / Removed | 3 |
| Pending | 0 |

## Wave Status

| Wave | Scope | Status | Notes |
|------|-------|--------|-------|
| 1 | SDP Envelope (SDR, SDReq, ChannelDescriptor) | **COMPLETE** | 8 Gold (SDR, SDReq, ChannelDesc, SDUpdate, 4 features). No schema changes, class names updated. |
| 2 | Phone Capabilities | **COMPLETE** | 12 Gold. PingConfigEntry fixed: 4->2 fields (int64+int32). PhoneConnectionConfig @Deprecated in 16.2. |
| 3 | AV + Video SDP Configs | **COMPLETE** | 11 Gold (AVChannel, VideoConfig, AdditionalVideoConfig, 4 sub-msgs, 4 enums). No schema changes. |
| 4 | Audio + Mic SDP Configs | **COMPLETE** | 3 Gold (AVInputChannel=vyf, AudioConfig=vvb, AudioFocusChannel=vxc). No schema changes. |
| 5 | Navigation + Sensor SDP | **COMPLETE** | 4 Gold (NavigationChannel=vzd, NavigationImageOptions, SensorChannel=wbk). No schema changes. |
| 6 | Radio SDP (full rewrite) | **COMPLETE** | FULL REWRITE: RadioStation/RadioBand removed. New: RadioChannelConfig(wap)->RadioBands(wab)->RadioBandGroup(waa). 3 old msgs removed, 3 new msgs added. |
| 7 | Bluetooth + WiFi SDP | **COMPLETE** | Confirmed Gold. No changes needed. |
| 8 | CarControl + Remaining Channels | **COMPLETE** | CarControlChannel filled (3 fields: CarPropertyConfig, CarControl, CarActionEntry). NotificationChannel filled (1 bool). VendorExt verified. 4 empties confirmed. |
| 9 | Connection Config + Common Protos | **COMPLETE** | 21 Gold. TuningParamsA-D filled (were empty). ConnectedDevices: Bronze (unimplemented). 3 new sub-msg placeholders added. |

## Schema Fixes Applied

1. **PingConfigEntry** (Wave 2): 4 uint32 fields -> 2 fields (int64 timeout_ms, int32 interval_ms)
2. **RadioChannelData.proto** (Wave 6): Complete rewrite — old RadioStation(14 fields)/RadioBand(2 fields) removed, replaced by RadioChannelConfig/RadioBands/RadioBandGroup
3. **NotificationChannel** (Wave 8): Was empty placeholder, actually has 1 bool field in 16.2
4. **CarControlChannel** (Wave 8): Empty placeholder filled with 3 repeated fields
5. **TuningParamsA-D** (Wave 9): Were empty placeholders — A has 1 optional msg, B has 1 repeated msg, C has 1 optional msg, D has 1 string

## New Protos Added (Wave 9)

1. **TuningParamsADetail** — placeholder for TuningParamsA sub-message
2. **TuningParamsBEntry** — placeholder for TuningParamsB sub-message
3. **TuningParamsCDetail** — placeholder for TuningParamsC sub-message

## 16.1 → 16.2 Class Mapping (Wave 9)

| Proto | 16.1 | 16.2 |
|-------|------|------|
| ConnectionConfiguration | aajk | aaiq |
| ConnectionSecurityConfig | aajj | aaip |
| ConnectionTransportConfig | aajh | aain |
| ConnectionFeatureFlags | aaja | aaig |
| ConnectionTuningConfig | aajg | aaim |
| ConnectionReservedConfig | aaji | aaio |
| TransportMetadata | aajt | aaiz |
| TransportCapabilities | aajs | aaiy |
| TransportSecurityConfig | aakd | aajj |
| TuningParamsA | aajf | aail |
| TuningParamsB | aajb | aaih |
| TuningParamsC | aajd | aaij |
| TuningParamsD | aajc | aaii |
| ControlChannelConfigWrapper | wcx | wcn |
| ControlChannelConfig | vxc | vwo |
| ControlChannelParams | wai | vzu |
| PingConfiguration | zyd | aaac |
| SessionInfo | vvf | vur |
| VersionFeatureFlags | wdq | aact |
| AssistantFeatureFlags | nll | nkw |
| CapabilityConnectionConfig | aahf | aagl |
| InputModelDescriptor | aahd | aagj |
| InputModelEntry | aafs | aaey |
| HandwritingInputModelConfig | aahi | aago |

## All Waves Complete
