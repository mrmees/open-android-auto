# Change Manifest

This is the frozen publication contract for Tasks 11-13. A later task may
modify only a file in its exact allowed-file set below, and only for the
semantic change attached to the cited change ID. `planned` means accepted for
static publication, not runtime-confirmed. `no canonical change` and
`deferred` rows are retained so closed evidence cannot disappear silently.

## Canonical change rows

| Change | Accepted evidence | Canonical files | Exact semantic change | Compatibility boundary | Verification command | Status |
|---|---|---|---|---|---|---|
| CHG-VID-8007 | DIR-VID-8007 | `oaa/video/VideoFocusRequestMessage.proto`; `oaa/video/VideoFocusRequestMessage.audit.yaml`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Keep ID/name/schema; publish Phone -> HU. | Direction-only correction; wire schema and ID stay stable. | `rg -n '0x8007' oaa/video/VideoFocusRequestMessage.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Tasks 11, 13) |
| CHG-VID-8008 | DIR-VID-8008 | `oaa/video/VideoFocusIndicationMessage.proto`; `oaa/video/VideoFocusIndicationMessage.audit.yaml`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Keep ID/name/schema; publish HU -> Phone. | Direction-only correction; wire schema and ID stay stable. | `rg -n '0x8008' oaa/video/VideoFocusIndicationMessage.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Tasks 11, 13) |
| CHG-VID-8009 | DIR-VID-8009 | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/av/UiConfigMessages.proto`; `oaa/av/UiConfigMessages.audit.yaml`; `oaa/video/UpdateUiConfigRequestMessage.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Name 0x8009 `UPDATE_UI_CONFIG_REQUEST` and publish its field-1 UI-config payload HU -> Phone. | Replaces the historical focus-notification label; no tag/type change. | `rg -n '0x8009' oaa/av/AVChannelMessageIdsEnum.proto oaa/av/UiConfigMessages.proto oaa/video/UpdateUiConfigRequestMessage.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Tasks 11, 13) |
| CHG-VID-800A | DIR-VID-800A | `oaa/av/UiConfigMessages.proto`; `oaa/video/UpdateUiConfigRequestMessage.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Keep name/payload; publish Phone -> HU. | Direction-only correction; 0x8009 and 0x800A remain the same payload in opposite directions. | `rg -n '0x800A' oaa/av/UiConfigMessages.proto oaa/video/UpdateUiConfigRequestMessage.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Task 11) |
| CHG-VID-800B | DIR-VID-800B | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/av/UiConfigMessages.proto`; `docs/channels/video.md`; `docs/channels/media.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x800B as no-payload-parsed `AUDIO_UNDERFLOW`, HU -> Phone; remove reply/heartbeat claims. | Do not infer an empty protobuf schema merely because the phone callback does not parse a payload. | `rg -n '0x800B' oaa/av/AVChannelMessageIdsEnum.proto oaa/av/UiConfigMessages.proto docs/channels/video.md docs/channels/media.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Tasks 11, 13) |
| CHG-VID-800C | DIR-VID-800C | `oaa/av/AVChannelMessageIdsEnum.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x800C as `ACTION_TAKEN`, Phone -> HU, with enum field 1 documented. | No public action enum is added in this release; only the proven wrapper boundary is documented. | `rg -n '0x800C' oaa/av/AVChannelMessageIdsEnum.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Task 11) |
| CHG-VID-800D | DIR-VID-800D | `oaa/av/AVChannelMessageIdsEnum.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x800D as `OVERLAY_PARAMETERS`, Phone -> HU, with repeated overlay-options field 1 documented. | Nested overlay-option semantics beyond the proven three-field shape remain unpublished. | `rg -n '0x800D' oaa/av/AVChannelMessageIdsEnum.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Task 11) |
| CHG-VID-800E | DIR-VID-800E | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/video/IntegratedOverlayStartNotification.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x800E as `OVERLAY_START`, HU -> Phone, with int32 display-session ID field 1. | Corrects name/direction only; field tag and type remain stable. | `rg -n '0x800E' oaa/av/AVChannelMessageIdsEnum.proto oaa/video/IntegratedOverlayStartNotification.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Task 11) |
| CHG-VID-800F | DIR-VID-800F | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/video/IntegratedOverlayStopNotification.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x800F as empty `OVERLAY_STOP`, HU -> Phone. | Corrects name/direction; preserves the empty message. | `rg -n '0x800F' oaa/av/AVChannelMessageIdsEnum.proto oaa/video/IntegratedOverlayStopNotification.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Task 11) |
| CHG-VID-8010 | DIR-VID-8010 | `oaa/av/AVChannelMessageIdsEnum.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Remove the unsupported `OVERLAY_STOP` assignment from 0x8010 and leave the slot unnamed/reserved. | Deferred: no name, payload, direction, or later-name shift is permitted. | `rg -n '0x8010' oaa/av/AVChannelMessageIdsEnum.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned reservation; evidence deferred (Task 11) |
| CHG-VID-8011 | DIR-VID-8011 | `oaa/av/AVChannelMessageIdsEnum.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Name 0x8011 `UI_CONFIG_REQUEST` and align docs/report to Phone -> HU. | Existing canonical payload is retained unchanged. | `rg -n '0x8011' oaa/av/AVChannelMessageIdsEnum.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Task 11) |
| CHG-VID-8012 | DIR-VID-8012 | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/av/UiConfigMessages.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Name 0x8012 `UPDATE_HU_UI_CONFIG_RESPONSE` and align docs/report to HU -> Phone. | Existing theming-token-status payload is retained unchanged. | `rg -n '0x8012' oaa/av/AVChannelMessageIdsEnum.proto oaa/av/UiConfigMessages.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Task 11) |
| CHG-VID-8013 | DIR-VID-8013 | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/av/UiConfigMessages.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x8013 as `MEDIA_STATS`, HU -> Phone, and remove the UI-config response assignment. | Existing media-stats schema is unchanged. | `rg -n '0x8013' oaa/av/AVChannelMessageIdsEnum.proto oaa/av/UiConfigMessages.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Task 11) |
| CHG-VID-8014 | DIR-VID-8014 | `oaa/av/AVChannelMessageIdsEnum.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x8014 as `MEDIA_OPTIONS`, Phone -> HU. | Existing 13-field media-options schema is unchanged. | `rg -n '0x8014' oaa/av/AVChannelMessageIdsEnum.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | planned (Task 11) |
| CHG-VID-8015 | DIR-VID-8015 | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/video/CriticalUiNotification.proto`; `oaa/video/CriticalUiNotification.audit.yaml`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x8015 as `CRITICAL_UI_NOTIFICATION`, Phone -> HU; add the proven field-1 critical-UI-focus enum payload. | New optional proto2 payload coverage; no acknowledgement or response is implied. | `protoc --proto_path=. --cpp_out=/tmp oaa/video/CriticalUiNotification.proto` | planned (Tasks 11, 13) |
| CHG-CC-8001 | DIR-CC-8001 | `oaa/carcontrol/CarControlMessages.proto`; `oaa/carcontrol/CarControlMessages.audit.yaml`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish Phone -> HU and phone-owned request correlation. | Direction/ownership correction only. | `rg -n '0x8001' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md docs/cross-version/carcontrol.md analysis/reports/proto-verification/carcontrol.md` | planned (Tasks 11, 13) |
| CHG-CC-8002 | DIR-CC-8002 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish HU -> Phone response and phone-side UUID matching. | Direction/ownership correction only. | `rg -n '0x8002' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md docs/cross-version/carcontrol.md analysis/reports/proto-verification/carcontrol.md` | planned (Task 11) |
| CHG-CC-8003 | DIR-CC-8003 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish Phone -> HU and note inbound copies are unexpected. | Direction correction only; no acknowledgement is inferred. | `rg -n '0x8003' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md docs/cross-version/carcontrol.md analysis/reports/proto-verification/carcontrol.md` | planned (Task 11) |
| CHG-CC-8004 | DIR-CC-8004 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish HU -> Phone and phone-side registration-state update. | Direction/ownership correction only. | `rg -n '0x8004' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md docs/cross-version/carcontrol.md analysis/reports/proto-verification/carcontrol.md` | planned (Task 11) |
| CHG-CC-8005 | DIR-CC-8005 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish HU -> Phone state change delivery. | Direction/ownership correction only. | `rg -n '0x8005' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md docs/cross-version/carcontrol.md analysis/reports/proto-verification/carcontrol.md` | planned (Task 11) |
| CHG-CC-8006 | DIR-CC-8006 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish Phone -> HU and note inbound copies are unexpected. | Direction correction only; no response is inferred. | `rg -n '0x8006' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md docs/cross-version/carcontrol.md analysis/reports/proto-verification/carcontrol.md` | planned (Task 11) |
| CHG-CC-8007 | DIR-CC-8007 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish HU -> Phone replacement-style group update. | Direction/ownership correction only. | `rg -n '0x8007' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md docs/cross-version/carcontrol.md analysis/reports/proto-verification/carcontrol.md` | planned (Task 11) |
| CHG-SEN-8001 | DIR-SEN-8001 | `analysis/reports/proto-verification/sensor.md` | Preserve canonical SensorRequest Phone -> HU; correct only the inverted verification row. | No proto or channel-doc change. | `rg -n 'SensorRequest' analysis/reports/proto-verification/sensor.md` | planned report correction (Task 11) |
| CHG-SEN-8002 | DIR-SEN-8002 | `analysis/reports/proto-verification/sensor.md` | Preserve canonical SensorStartResponse HU -> Phone; correct only the inverted verification row. | No proto or channel-doc change. | `rg -n 'SensorStartResponse' analysis/reports/proto-verification/sensor.md` | planned report correction (Task 11) |
| CHG-SEN-8003 | DIR-SEN-8003 | `analysis/reports/proto-verification/sensor.md` | Preserve canonical SensorEventIndication HU -> Phone; correct only the inverted verification row. | No proto or channel-doc change. | `rg -n 'SensorEventIndication' analysis/reports/proto-verification/sensor.md` | planned report correction (Task 11) |
| CHG-SEN-8004 | DIR-SEN-8004 | `analysis/reports/proto-verification/sensor.md` | Preserve canonical SensorError HU -> Phone; correct only the inverted verification row. | No proto or channel-doc change. | `rg -n 'SensorError' analysis/reports/proto-verification/sensor.md` | planned report correction (Task 11) |
| CHG-REPORT-RAD-801A | DIR-RAD-801A | `docs/channels/radio.md` | Keep the correct mapping; correct list-notification prose to HU -> Phone. | No radio proto/catalog/report mapping change. | `rg -n '0x801A' docs/channels/radio.md` | planned prose correction (Task 13) |
| CHG-REPORT-RAD-801B | DIR-RAD-801B | `docs/channels/radio.md` | Keep the correct mapping; correct program-info workflow prose to HU -> Phone. | No radio proto/catalog/report mapping change. | `rg -n '0x801B' docs/channels/radio.md` | planned prose correction (Task 13) |
| CHG-REPORT-RAD-801C | DIR-RAD-801C | `docs/channels/radio.md` | Keep the correct mapping; correct mute-request prose to Phone -> HU. | No radio proto/catalog/report mapping change. | `rg -n '0x801C' docs/channels/radio.md` | planned prose correction (Task 13) |
| CHG-REPORT-RAD-801D | DIR-RAD-801D | `docs/channels/radio.md` | Keep the correct mapping; correct mute-response prose to HU -> Phone. | No radio proto/catalog/report mapping change. | `rg -n '0x801D' docs/channels/radio.md` | planned prose correction (Task 13) |
| CHG-REPORT-RAD-801E | DIR-RAD-801E | `docs/channels/radio.md` | Keep the correct mapping; correct tune-request prose to Phone -> HU. | No radio proto/catalog/report mapping change. | `rg -n '0x801E' docs/channels/radio.md` | planned prose correction (Task 13) |
| CHG-REPORT-RAD-801F | DIR-RAD-801F | `docs/channels/radio.md` | Keep the correct mapping; correct tune-response/ownership prose to HU -> Phone. | No radio proto/catalog/report mapping change. | `rg -n '0x801F' docs/channels/radio.md` | planned prose correction (Task 13) |
| CHG-REPORT-RAD-8020 | DIR-RAD-8020 | `docs/channels/radio.md` | Keep the correct mapping; correct favorite-list workflow prose to HU -> Phone. | No radio proto/catalog/report mapping change. | `rg -n '0x8020' docs/channels/radio.md` | planned prose correction (Task 13) |
| CHG-REPORT-RAD-8021 | DIR-RAD-8021 | `docs/channels/radio.md` | Keep the correct mapping; correct favorite-toggle prose to Phone -> HU. | No radio proto/catalog/report mapping change. | `rg -n '0x8021' docs/channels/radio.md` | planned prose correction (Task 13) |
| CHG-REPORT-RAD-8022 | DIR-RAD-8022 | `docs/channels/radio.md` | Keep the correct mapping; correct tune-direction ownership to Phone -> HU. | No radio proto/catalog/report mapping change. | `rg -n '0x8022' docs/channels/radio.md` | planned prose correction (Task 13) |
| CHG-REPORT-RAD-8023 | DIR-RAD-8023 | none | Explicit no canonical change: retain ID, name, one-string schema, direction, and history. | Mapping is already correct. | `rg -n '0x8023' oaa/radio/RadioMessages.proto docs/channels/radio.md analysis/reports/proto-verification/radio.md` | no canonical change |
| CHG-ID-AV-F6 | ID-AV-F6 | `oaa/av/AVChannelData.proto`; `oaa/av/AVChannelData.audit.yaml`; `docs/channels/display-routing.md`; `docs/channels/architecture.md`; `docs/channel-map.md`; `analysis/reports/multi-display/prodigy-maintainer-handoff.md` | Rename AV field 6 from `channel_id` to `display_id`; document logical display identity. | Breaking generated-API rename only; tag 6 and uint32 wire type stay stable. | `rg -n 'display_id = 6' oaa/av/AVChannelData.proto` | planned (Tasks 12, 13) |
| CHG-ID-INPUT-F5 | ID-INPUT-F5 | `oaa/input/InputChannelConfigData.proto`; `oaa/input/InputChannelConfigData.audit.yaml`; `docs/channels/display-routing.md`; `docs/channels/architecture.md`; `docs/channel-map.md`; `analysis/reports/multi-display/prodigy-maintainer-handoff.md` | Preserve field-5 `display_id`; document it as the AV field-6 reference, distinct from transport channel ID and service type 8. | No tag/type/API rename. | `rg -n 'display_id = 5' oaa/input/InputChannelConfigData.proto` | planned documentation clarification (Tasks 12, 13) |
| CHG-ID-CD-F16 | ID-CD-F16 | `oaa/control/ChannelDescriptorData.proto`; `oaa/control/ChannelDescriptorData.audit.yaml`; `docs/channels/media.md`; `docs/channels/architecture.md`; `docs/channel-map.md`; `analysis/reports/proto-verification/sdp.md`; `analysis/reports/proto-verification/sdp-progress.md` | Publish field 16 as the 17.3 CarLocalMedia marker/service type 20. | Historical 16.2 `generic_notification` meaning is insufficient evidence; do not publish it as an alias or semantic reuse. | `rg -n 'car_local_media_channel = 16' oaa/control/ChannelDescriptorData.proto` | planned (Tasks 12, 13) |
| CHG-ID-CD-F17 | ID-CD-F17 | `oaa/control/ChannelDescriptorData.proto`; `oaa/control/ChannelDescriptorData.audit.yaml`; `docs/channels/media.md`; `docs/channels/architecture.md`; `docs/channel-map.md`; `analysis/reports/proto-verification/sdp.md`; `analysis/reports/proto-verification/sdp-progress.md` | Publish field 17 as the 17.3 BufferedMedia marker/service type 21. | Historical 16.2 `voice` meaning is insufficient evidence; do not publish it as an alias or semantic reuse. | `rg -n 'buffered_media_channel = 17' oaa/control/ChannelDescriptorData.proto` | planned (Tasks 12, 13) |
| CHG-ID-CD-F18 | ID-CD-F18 | `oaa/control/ChannelDescriptorData.proto`; `oaa/control/ChannelDescriptorData.audit.yaml`; `docs/channels/carintent.md`; `docs/channels/architecture.md`; `docs/channel-map.md`; `analysis/reports/proto-verification/sdp.md`; `analysis/reports/proto-verification/sdp-progress.md` | Publish optional field 18 as the CarIntent marker/service type 22. | Compatible optional addition in 17.3 relative to the available 16.2 descriptor ending at field 17. | `rg -n 'car_intent_channel = 18' oaa/control/ChannelDescriptorData.proto` | planned (Tasks 12, 13) |
| CHG-CI-DESCRIPTOR | SVC-CI-DESCRIPTOR | `oaa/control/ChannelDescriptorData.proto`; `docs/channels/carintent.md`; `docs/channels/architecture.md`; `docs/channel-map.md` | Document field 18, bit 0x20000, and GAL service type 22. | Static descriptor evidence only; no framed discovery capture. | `rg -n 'service type 22' docs/channels/carintent.md docs/channels/architecture.md docs/channel-map.md` | planned (Task 12) |
| CHG-CI-ENDPOINT | SVC-CI-ENDPOINT | `docs/channels/carintent.md` | Document the incoming HU -> Phone parse, log, and callback chain. | Do not add an acknowledgement, response, or runtime-delivery claim. | `rg -n 'HU -> Phone' docs/channels/carintent.md` | planned (Task 12) |
| CHG-CI-ID | SVC-CI-ID | `docs/channels/carintent.md` | Explicit no raw-ID assignment: publish the raw message ID as unknown. | Deferred; conventional 0x8001 is forbidden. | `rg -n 'unknown' docs/channels/carintent.md` | deferred; documentation-only (Task 12) |
| CHG-CI-SCHEMA | SVC-CI-SCHEMA | `oaa/carintent/CarIntentMessage.proto`; `oaa/carintent/CarIntentMessage.audit.yaml`; `docs/channels/carintent.md` | Add a proto2 payload containing only optional string field 2 and document its HU -> Phone use. | Field 1, intent-type enum, acknowledgement, and response are forbidden. | `protoc --proto_path=. --cpp_out=/tmp oaa/carintent/CarIntentMessage.proto` | planned (Tasks 12, 13) |
| CHG-CI-GATE | SVC-CI-GATE | `docs/channels/carintent.md` | Document the false named-flag default separately from the actual field-18 descriptor-presence factory gate. | Do not claim the named flag controls factory construction or that production activation was observed. | `rg -n 'AdasRouteInfoFeature__car_intent_enabled' docs/channels/carintent.md` | planned (Task 12) |
| CHG-CLM-STATE5 | SVC-CLM-STATE5 | `oaa/media/CarLocalMediaPlaybackStatusMessage.proto`; `oaa/media/CarLocalMediaPlaybackStatusMessage.audit.yaml`; `docs/channels/media.md` | Keep wire value 5 explicitly unnamed/unknown; publish no semantic state label. | Deferred until runtime or unobfuscated source resolves the value; BufferedMedia enum names are not transferable. | `rg -n 'UNKNOWN_5' oaa/media/CarLocalMediaPlaybackStatusMessage.proto docs/channels/media.md` | deferred; documentation/audit boundary only (Task 13) |
| CHG-CLM-FLOW | SVC-CLM-FLOW | `oaa/media/CarLocalMediaPlaybackStatusMessage.proto`; `oaa/media/CarLocalMediaPlaybackMetadataMessage.proto`; `oaa/media/CarLocalMediaPlaybackRequestMessage.proto`; `docs/channels/media.md`; `docs/channel-map.md`; `analysis/reports/proto-verification/media.md`; `analysis/reports/proto-verification/PROGRESS.md` | Publish service type 20: 0x8001/0x8002 HU -> Phone and 0x8003 Phone -> HU, with the three existing payloads. | Static endpoint flow only; no acknowledgement, runtime activation, frame, or callback-delivery claim. | `rg -n '0x8001' oaa/media/CarLocalMediaPlaybackStatusMessage.proto docs/channels/media.md analysis/reports/proto-verification/media.md` | planned (Task 12) |
| CHG-BUF-DESCRIPTOR | SVC-BUF-DESCRIPTOR | `oaa/control/ChannelDescriptorData.proto`; `oaa/media/BufferedMediaSinkMessage.proto`; `docs/channels/media.md`; `docs/channels/architecture.md`; `docs/channel-map.md` | Document field 17, bit 0x10000, and GAL service type 21. | Preserve the insufficient-evidence boundary for historical field-17 semantics. | `rg -n 'service type 21' oaa/media/BufferedMediaSinkMessage.proto docs/channels/media.md docs/channels/architecture.md docs/channel-map.md` | planned (Task 12) |
| CHG-BUF-ENDPOINT | SVC-BUF-ENDPOINT | `oaa/media/BufferedMediaSinkMessage.proto`; `docs/channels/media.md`; `analysis/reports/proto-verification/media.md`; `analysis/reports/proto-verification/PROGRESS.md` | Replace the universal discard-only claim with the bounded 17.3 incoming ID-4 parse/consume branch, HU -> Phone. | This does not establish a response, completed transfer, runtime activation, or downstream media operation. | `rg -n 'message ID 4' oaa/media/BufferedMediaSinkMessage.proto docs/channels/media.md analysis/reports/proto-verification/media.md` | planned (Task 12) |
| CHG-BUF-IDS | SVC-BUF-IDS | `oaa/media/BufferedMediaSinkMessage.proto`; `docs/channels/media.md`; `analysis/reports/proto-verification/media.md` | Publish only incoming raw ID 4; explicitly leave IDs 1-3 and every outbound path unknown. | Validator range acceptance is not endpoint meaning or send evidence. | `rg -n 'IDs 1-3' oaa/media/BufferedMediaSinkMessage.proto docs/channels/media.md analysis/reports/proto-verification/media.md` | planned ID 4; IDs 1-3/outbound deferred (Task 12) |
| CHG-BUF-SCHEMAS | SVC-BUF-SCHEMAS | `oaa/media/BufferedMediaSinkMessage.proto`; `oaa/media/BufferedMediaSinkMessage.audit.yaml`; `docs/channels/media.md`; `analysis/reports/proto-verification/media.md` | Add only the six optional ID-4 fields and state enum values 0-4 proven by the parser. | No URL, request/response, lifecycle, transport/data-plane, or session semantics beyond the six consumed fields. | `protoc --proto_path=. --cpp_out=/tmp oaa/media/BufferedMediaSinkMessage.proto` | planned (Tasks 12, 13) |
| CHG-BUF-GATE | SVC-BUF-GATE | `oaa/media/BufferedMediaSinkMessage.proto`; `docs/channels/media.md`; `docs/channels/architecture.md` | Document the distinct magic-value construction, descriptor-presence, registration, endpoint attachment, and worker-start gates. | Defaults/branches are static; do not claim production enablement, live descriptor advertisement, open endpoint, or running worker. | `rg -n '834952858' oaa/media/BufferedMediaSinkMessage.proto docs/channels/media.md docs/channels/architecture.md` | planned (Task 12) |
| CHG-REPORT-RT-ENV | RT-ENV | none | Explicit no canonical change: runtime environment validation was unavailable. | No device/version or capture-dependency claim can be promoted. | `rg -n 'RT-ENV' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |
| CHG-REPORT-RT-VIDEO-FOCUS | RT-VIDEO-FOCUS | none | Explicit no canonical change: no framed video-focus traffic was captured. | Static direction remains static, not runtime-confirmed. | `rg -n 'RT-VIDEO-FOCUS' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |
| CHG-REPORT-RT-VIDEO-UI | RT-VIDEO-UI | none | Explicit no canonical change: no framed video-UI transition was captured. | Static UI/overlay direction remains static, not runtime-confirmed. | `rg -n 'RT-VIDEO-UI' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |
| CHG-REPORT-RT-RADIO | RT-RADIO | none | Explicit no canonical change: no runtime radio activation or traffic was observed. | Static radio mappings are not runtime-confirmed. | `rg -n 'RT-RADIO' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |
| CHG-REPORT-RT-CARCONTROL | RT-CARCONTROL | none | Explicit no canonical change: no runtime car-control activation or traffic was observed. | Static car-control directions are not runtime-confirmed. | `rg -n 'RT-CARCONTROL' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |
| CHG-REPORT-RT-MULTIDISPLAY | RT-MULTIDISPLAY | none | Explicit no canonical change: no simultaneous multi-display discovery, streams, or focus were captured. | Static logical-display construction does not prove runtime concurrency. | `rg -n 'RT-MULTIDISPLAY' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |

## Exact allowed-file sets

These sets are closed. Files appearing in more than one set may be changed only
for the change IDs assigned to that task.

### Task 11: message IDs and directions

```text
analysis/reports/android-auto-17.3-update/README.md
analysis/reports/android-auto-17.3-update/change-manifest.md
analysis/reports/proto-verification/carcontrol.md
analysis/reports/proto-verification/sensor.md
analysis/reports/proto-verification/video.md
docs/channels/carcontrol.md
docs/channels/video.md
docs/cross-version/carcontrol.md
docs/cross-version/video.md
docs/session-handoffs.md
oaa/av/AVChannelMessageIdsEnum.proto
oaa/av/UiConfigMessages.proto
oaa/carcontrol/CarControlMessages.proto
oaa/video/CriticalUiNotification.proto
oaa/video/IntegratedOverlayStartNotification.proto
oaa/video/IntegratedOverlayStopNotification.proto
oaa/video/UpdateUiConfigRequestMessage.proto
oaa/video/VideoFocusIndicationMessage.proto
oaa/video/VideoFocusRequestMessage.proto
```

### Task 12: identity, compatibility, and new services

```text
analysis/reports/android-auto-17.3-update/README.md
analysis/reports/android-auto-17.3-update/change-manifest.md
analysis/reports/multi-display/prodigy-maintainer-handoff.md
analysis/reports/proto-verification/PROGRESS.md
analysis/reports/proto-verification/media.md
analysis/reports/proto-verification/sdp-progress.md
analysis/reports/proto-verification/sdp.md
docs/channel-map.md
docs/channels/architecture.md
docs/channels/carintent.md
docs/channels/display-routing.md
docs/channels/media.md
docs/session-handoffs.md
oaa/av/AVChannelData.proto
oaa/carintent/CarIntentMessage.proto
oaa/control/ChannelDescriptorData.proto
oaa/input/InputChannelConfigData.proto
oaa/media/BufferedMediaSinkMessage.proto
oaa/media/CarLocalMediaPlaybackMetadataMessage.proto
oaa/media/CarLocalMediaPlaybackRequestMessage.proto
oaa/media/CarLocalMediaPlaybackStatusMessage.proto
```

### Task 13: audits, reports, coverage, documentation, and handoff

```text
analysis/reports/android-auto-17.3-update/README.md
analysis/reports/android-auto-17.3-update/change-manifest.md
analysis/reports/coverage-dashboard/coverage-dashboard.json
analysis/reports/coverage-dashboard/coverage-dashboard.md
analysis/reports/multi-display/prodigy-maintainer-handoff.md
analysis/reports/proto-verification/PROGRESS.md
analysis/reports/proto-verification/carcontrol.md
analysis/reports/proto-verification/media.md
analysis/reports/proto-verification/sdp-progress.md
analysis/reports/proto-verification/sdp.md
analysis/reports/proto-verification/sensor.md
analysis/reports/proto-verification/video.md
docs/channel-map.md
docs/channels/architecture.md
docs/channels/carcontrol.md
docs/channels/carintent.md
docs/channels/display-routing.md
docs/channels/media.md
docs/channels/radio.md
docs/channels/video.md
docs/cross-version/carcontrol.md
docs/cross-version/video.md
docs/roadmap-current.md
docs/session-handoffs.md
oaa/av/AVChannelData.audit.yaml
oaa/av/UiConfigMessages.audit.yaml
oaa/carcontrol/CarControlMessages.audit.yaml
oaa/carintent/CarIntentMessage.audit.yaml
oaa/control/ChannelDescriptorData.audit.yaml
oaa/input/InputChannelConfigData.audit.yaml
oaa/media/BufferedMediaSinkMessage.audit.yaml
oaa/media/CarLocalMediaPlaybackStatusMessage.audit.yaml
oaa/video/CriticalUiNotification.audit.yaml
oaa/video/VideoFocusIndicationMessage.audit.yaml
oaa/video/VideoFocusRequestMessage.audit.yaml
```

The committed matcher baseline is intentionally verify-only and is not in an
allowed modification set: Task 1 retained
`analysis/reports/cross-version/17-3-schema-match.json` and
`analysis/reports/cross-version/17-3-schema-match.md` after rejecting promotion
of the three unreviewed fresh-delta rows. Task 13 must confirm both files remain
unchanged. Runtime validation is likewise not a publication target; its six
rows remain the explicit runtime-unverified boundary.
