# 16.4 Cross-Version Delta Report

**Generated:** 2026-04-08
**Canonical build:** `16.4.661014`

> **Canonical 16.4 build for Phase 8 is 661014** (the indexed build). 16.4.661034 is referenced ONLY for the manual-JADX reproducibility-gap doc — all structural analysis runs exclusively against 661014.

For the 16.4.661034 build and the 5 salvaged manual-JADX classes, see [manual-jadx-reproducibility-gap.md](./manual-jadx-reproducibility-gap.md).

## 1. Summary

- **Total mappings analyzed:** 240
- **Eligible (≥1 pair compared):** 220
- **Consistent (no drift):** 220
- **With drift (suspicious or additive):** 0
- **All 6 pairs compared cleanly:** 94
- **Mappings with 16.4 pair included:** 96
- **Known indexer artifacts suppressed:** 4 (DriverPosition, HapticFeedbackType, SensorErrorStatus, CarLocalMediaPlayback)

## 2. New in 16.4

_No protos classified as 'new in 16.4' by the auto-matcher. A proto would be new here if it appeared in the 16.4 DB with a field-tuple that has no counterpart in any prior version's class_mapping.yaml — detecting that is out of scope for Phase 8 (would require scanning every unmapped 16.4 class against every existing mapping). Phase 9 / 10 may revisit._

## 3. Removed in 16.4

**143** mappings have a null 16.4 class — either truly removed from 16.4 or unresolved by the auto-matcher. See [16-4-mapping-candidates.md](./16-4-mapping-candidates.md) for the distinction.

| Proto | Last present in |
|-------|-----------------|
| `AudioConfig` | 16.2 |
| `AudioFocusState` | 16.2 |
| `AudioStreamType` | 16.2 |
| `AudioFocusChannel` | 16.2 |
| `AudioFocusRequest` | 16.2 |
| `AudioFocusResponse` | 16.2 |
| `AVChannelSetupRequest` | 16.2 |
| `AVInputChannel` | 16.2 |
| `AVInputOpenResponse` | 16.2 |
| `BluetoothChannel` | 16.2 |
| `CarAction` | 16.2 |
| `CarActionEntry` | 16.2 |
| `CarActionControl` | 16.2 |
| `CarActionNotification` | 16.2 |
| `CarControlChannelDescriptor` | 16.2 |
| `CarControlGroup` | 16.2 |
| `CarControlGroupUpdate` | 16.2 |
| `RegisterCarPropertyListenersResponse` | 16.1 |
| `FloatValues` | 16.2 |
| `IntValues` | 16.2 |
| `LongValues` | 16.2 |
| `Diagnostics` | 16.2 |
| `DriverPosition` | 16.2 |
| `VersionFeatureFlags` | 16.2 |
| `PingConfiguration` | 16.2 |
| `AuthCompleteIndication` | 16.2 |
| `ByeByeResponse` | 16.2 |
| `BindingRequest` | 16.2 |
| `BindingResponse` | 16.2 |
| `ChannelOpenAck` | 16.2 |
| … | _113 more — see JSON sidecar_ |

## 4. Schema Changes

_None._ After suppressing the 4 known spurious enum drifts (DriverPosition, HapticFeedbackType, SensorErrorStatus, CarLocalMediaPlayback), no mapping has any field-level drift issues across the 4 versions.

### Known Indexer Artifacts (Suppressed from Schema Changes)

The following enum mappings appear to drift but are spurious — they are artifacts of `proto_enum_classes` being present in the 15.9 and 16.4 DBs but absent in the 16.1 and 16.2 DBs. Schema evolution at the indexer layer, not the proto layer. These are suppressed from Section 4 above and listed here for transparency.

- `DriverPosition` — proto_enum_classes table absent in 16.1/16.2 but present in 15.9/16.4 — drift is a data-layer artifact, not a real 16.4 delta. (suppressed 8 issue(s))
- `HapticFeedbackType` — proto_enum_classes table absent in 16.1/16.2 but present in 15.9/16.4 — drift is a data-layer artifact, not a real 16.4 delta. (suppressed 10 issue(s))
- `SensorErrorStatus` — proto_enum_classes table absent in 16.1/16.2 but present in 15.9/16.4 — drift is a data-layer artifact, not a real 16.4 delta. (suppressed 6 issue(s))
- `CarLocalMediaPlayback` — proto_enum_classes table absent in 16.1/16.2 but present in 15.9/16.4 — drift is a data-layer artifact, not a real 16.4 delta. (suppressed 10 issue(s))

## 5. Promoted Bronze → Silver

_Populated by Plan 08-02 walker output._ The promotion walk runs AFTER this delta report has been validated; the walker consumes this report's JSON sidecar and appends promoted protos back into the `promoted_bronze_to_silver` key as part of its execution.

## 6. Drifted Silver/Gold

_None._ No Silver or Gold mapping has suspicious drift (FIELD_REMOVED or FIELD_TYPE_CHANGED) in any pair involving 16.4.

## 7. Unmappable Protos

**144** mappings have `'16.4': null`. Detailed reasoning per mapping is in [16-4-mapping-candidates.md](./16-4-mapping-candidates.md).

| Proto | File |
|-------|------|
| `AudioConfig` | `oaa/audio/AudioConfigData.proto` |
| `AudioFocusState` | `oaa/audio/AudioFocusStateMessage.proto` |
| `AudioStreamType` | `oaa/audio/AudioStreamTypeMessage.proto` |
| `AudioStreamTypeEnum` | `oaa/audio/AudioStreamTypeEnum.proto` |
| `AudioFocusChannel` | `oaa/audio/AudioFocusChannelData.proto` |
| `AudioFocusRequest` | `oaa/audio/AudioFocusRequestMessage.proto` |
| `AudioFocusResponse` | `oaa/audio/AudioFocusResponseMessage.proto` |
| `AVChannelSetupRequest` | `oaa/av/AVChannelSetupRequestMessage.proto` |
| `AVInputChannel` | `oaa/av/AVInputChannelData.proto` |
| `AVInputOpenResponse` | `oaa/av/AVInputOpenResponseMessage.proto` |
| `BluetoothChannel` | `oaa/bluetooth/BluetoothChannelData.proto` |
| `CarAction` | `oaa/carcontrol/CarPropertyData.proto` |
| `CarActionEntry` | `oaa/carcontrol/CarPropertyData.proto` |
| `CarActionControl` | `oaa/carcontrol/CarControlMessages.proto` |
| `CarActionNotification` | `oaa/carcontrol/CarControlMessages.proto` |
| `CarControlChannelDescriptor` | `oaa/carcontrol/CarControlMessages.proto` |
| `CarControlGroup` | `oaa/carcontrol/CarControlMessages.proto` |
| `CarControlGroupUpdate` | `oaa/carcontrol/CarControlMessages.proto` |
| `RegisterCarPropertyListenersResponse` | `oaa/carcontrol/CarControlMessages.proto` |
| `FloatValues` | `oaa/carcontrol/CarPropertyData.proto` |
| `IntValues` | `oaa/carcontrol/CarPropertyData.proto` |
| `LongValues` | `oaa/carcontrol/CarPropertyData.proto` |
| `Diagnostics` | `oaa/common/DiagnosticsData.proto` |
| `DriverPosition` | `oaa/common/DriverPositionEnum.proto` |
| `VersionFeatureFlags` | `oaa/common/FeatureFlagsData.proto` |
| `PingConfiguration` | `oaa/common/PingConfigurationData.proto` |
| `AuthCompleteIndication` | `oaa/control/AuthCompleteIndicationMessage.proto` |
| `ByeByeResponse` | `oaa/control/ByeByeResponseMessage.proto` |
| `BindingRequest` | `oaa/control/BindingRequestMessage.proto` |
| `BindingResponse` | `oaa/control/BindingResponseMessage.proto` |
| … | _114 more — see JSON sidecar_ |

## 8. Baseline Reproduction

**Command:** `PYTHONPATH=. python3 -m analysis.tools.cross_version.run`

**Run date:** 2026-04-08

**DB sha256 hashes:**

| Version | sha256 |
|---------|--------|
| `15.9` | `e2f03f39a64e8ee4a8671bb93ccc5a4c6ba27059dea20556598271ce992ad9ab` |
| `16.1` | `3aa7fd840579d65c6b57a69600ea1ba23b2b9ac5df3dc94dc1a78cb9a99517c5` |
| `16.2` | `ca3198ed6775920e73a88cef6ac7668f8f8621b7f8b2ea6680baa9668ef62345` |
| `16.4` | `37e9c019452dd5b16ec85eefc647d59c3771f43d7eac4e675487012bf693ec10` |

**Ambiguous matcher candidates:** see [16-4-mapping-candidates.md](./16-4-mapping-candidates.md).

