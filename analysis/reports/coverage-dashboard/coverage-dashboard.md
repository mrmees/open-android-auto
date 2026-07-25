# Coverage Dashboard

## Summary

168 sidecars covering 247 protos (68% coverage). 3 Platinum / single-OEM, 46 Gold, 93 Silver, 13 Bronze.

21 protos awaiting deep-trace for Platinum promotion (oem_match_pending_gold).

## Per-Channel Tier Counts

| Channel | Bronze | Silver | Gold | Platinum (s-OEM) | Retracted | Superseded | Total |
|---------|--------|--------|------|------------------|-----------|------------|-------|
| audio | 2 | 5 | 0 | 0 | 0 | 0 | 7 |
| av | 1 | 9 | 3 | 0 | 0 | 0 | 13 |
| bluetooth | 0 | 2 | 1 | 0 | 0 | 0 | 3 |
| carcontrol | 0 | 0 | 2 | 0 | 0 | 0 | 2 |
| carintent | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| common | 1 | 4 | 0 | 0 | 0 | 0 | 5 |
| control | 1 | 18 | 4 | 0 | 4 | 0 | 27 |
| generic | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| input | 0 | 4 | 13 | 0 | 0 | 0 | 17 |
| media | 1 | 0 | 4 | 2 | 4 | 0 | 11 |
| mediabrowser | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| mic | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| navigation | 0 | 10 | 2 | 0 | 0 | 0 | 12 |
| notification | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| phone | 0 | 0 | 3 | 0 | 0 | 0 | 3 |
| radio | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| sensor | 2 | 30 | 4 | 0 | 1 | 0 | 37 |
| verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| video | 1 | 3 | 5 | 1 | 2 | 0 | 12 |
| wifi | 1 | 7 | 4 | 0 | 2 | 0 | 14 |
| **Total** | **13** | **93** | **46** | **3** | **13** | **0** | **168** |

## Evidence Type Breakdown

| Tier | apk_deep_trace | apk_static | cross_version | deep_trace | dhu_observation | platinum_evidence | Total |
|------|----------------|------------|---------------|------------|-----------------|-------------------|-------|
| Bronze | 4 | 9 | 9 | 0 | 0 | 0 | 22 |
| Silver | 0 | 137 | 185 | 0 | 0 | 0 | 322 |
| Gold | 30 | 48 | 39 | 20 | 1 | 0 | 138 |
| Platinum | 3 | 4 | 3 | 1 | 0 | 3 | 14 |
| Retracted | 8 | 23 | 14 | 1 | 0 | 0 | 46 |

## Missing Sidecars

79 proto files without audit sidecars:

### audio (3 missing)

- AudioFocusStateEnum.proto
- AudioFocusTypeEnum.proto
- AudioTypeEnum.proto

### av (6 missing)

- AVChannelSessionTypeEnum.proto
- AVChannelSetupStatusEnum.proto
- AVChannelStopIndicationMessage.proto
- AVStreamTypeEnum.proto
- AndroidKeycodeEnum.proto
- MediaCodecTypeEnum.proto

### bluetooth (6 missing)

- BluetoothAuthenticationDataMessage.proto
- BluetoothAuthenticationResultMessage.proto
- BluetoothChannelConfigData.proto
- BluetoothChannelMessageIdsEnum.proto
- BluetoothPairingMethodEnum.proto
- BluetoothPairingStatusEnum.proto

### carcontrol (1 missing)

- VehicleAreaEnums.proto

### common (11 missing)

- ChannelErrorCodeEnum.proto
- ChannelTypeEnum.proto
- ConnectionStateEnum.proto
- DisconnectReasonEnum.proto
- FragInfoEnum.proto
- LocationCharacterizationEnum.proto
- PingConfigurationData.proto
- SessionConfigurationEnum.proto
- SessionErrorEnum.proto
- StatusEnum.proto
- WirelessTcpConfigurationData.proto

### control (8 missing)

- BatteryStatusMessage.proto
- ChannelCloseNotificationMessage.proto
- ConnectedDevicesMessages.proto
- ControlMessageIdsEnum.proto
- ShutdownReasonEnum.proto
- ShutdownResponseMessage.proto
- VendorExtensionChannel.proto
- VersionResponseStatusEnum.proto

### input (6 missing)

- ButtonCodeEnum.proto
- HapticFeedbackTypeEnum.proto
- InputChannelMessageIdsEnum.proto
- TouchActionEnum.proto
- TouchPadConfigData.proto
- TouchScreenConfigData.proto

### media (1 missing)

- MediaChannelData.proto

### mediabrowser (2 missing)

- MediaBrowserMessageIdsEnum.proto
- MediaBrowserMessages.proto

### navigation (5 missing)

- InstrumentClusterMessages.proto
- ManeuverTypeEnum.proto
- NavigationTypeEnum.proto
- TurnSideEnum.proto
- VehicleEnergyForecastMessage.proto

### notification (1 missing)

- NotificationTypeEnum.proto

### radio (5 missing)

- LegacyRadioMessages.proto
- RadioBandTypeEnum.proto
- RadioCodecTypeEnum.proto
- RadioProgramTypeSchemaEnum.proto
- RadioRegionEnum.proto

### sensor (6 missing)

- DrivingStatusEnum.proto
- GearEnum.proto
- HeadlightStatusEnum.proto
- IndicatorStatusEnum.proto
- SensorChannelMessageIdsEnum.proto
- SensorTypeEnum.proto

### verification (2 missing)

- GalVerificationMessages.proto
- GoogleDiagnosticsMessages.proto

### video (7 missing)

- ColorSchemeSupportEnum.proto
- DisplayTypeEnum.proto
- UpdateHuUiConfigResponse.proto
- VideoFPSEnum.proto
- VideoFocusModeEnum.proto
- VideoFocusReasonEnum.proto
- VideoResolutionEnum.proto

### wifi (9 missing)

- WifiAccessPointTypeEnum.proto
- WifiChannelMessageIdsEnum.proto
- WifiChannelTypeEnum.proto
- WifiConnectionRejectionReasonEnum.proto
- WifiPingMessage.proto
- WifiSecurityModeEnum.proto
- WifiSecurityRequestMessage.proto
- WifiStartRequestMessage.proto
- WifiVersionStatusEnum.proto

## Orphan Sidecars

No orphan sidecars found.

## Dashboard Metadata

- **Run date:** 2026-07-25T17:51:00Z
- **Tool version:** 1.0.0
- **Total protos:** 247
- **Total sidecars:** 168
- **Sidecar directory:** oaa/
- **Git HEAD:** e11bdd6c227a61523dc4eac4fd1706304c3d4393
