# Coverage Dashboard

## Summary

169 sidecars covering 248 protos (68% coverage). 0 Platinum / single-OEM, 15 Gold, 118 Silver, 23 Bronze.

## Per-Channel Tier Counts

| Channel | Bronze | Silver | Gold | Platinum (s-OEM) | Retracted | Superseded | Total |
|---------|--------|--------|------|------------------|-----------|------------|-------|
| audio | 2 | 5 | 0 | 0 | 0 | 0 | 7 |
| av | 2 | 9 | 2 | 0 | 0 | 0 | 13 |
| bluetooth | 0 | 3 | 0 | 0 | 0 | 0 | 3 |
| carcontrol | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| carintent | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| common | 1 | 4 | 0 | 0 | 0 | 0 | 5 |
| control | 1 | 19 | 3 | 0 | 4 | 0 | 27 |
| generic | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| input | 4 | 12 | 1 | 0 | 0 | 0 | 17 |
| media | 1 | 5 | 1 | 0 | 4 | 0 | 11 |
| mediabrowser | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| mic | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| navigation | 0 | 12 | 0 | 0 | 0 | 0 | 12 |
| notification | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| phone | 0 | 0 | 3 | 0 | 0 | 0 | 3 |
| radio | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| sensor | 3 | 33 | 0 | 0 | 1 | 0 | 37 |
| verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| video | 3 | 3 | 5 | 0 | 2 | 0 | 13 |
| wifi | 2 | 10 | 0 | 0 | 2 | 0 | 14 |
| **Total** | **23** | **118** | **15** | **0** | **13** | **0** | **169** |

## Evidence Type Breakdown

| Tier | apk_deep_trace | apk_static | cross_version | deep_trace | dhu_observation | Total |
|------|----------------|------------|---------------|------------|-----------------|-------|
| Bronze | 11 | 11 | 10 | 2 | 0 | 34 |
| Silver | 16 | 175 | 207 | 12 | 1 | 411 |
| Gold | 13 | 15 | 18 | 7 | 0 | 53 |
| Retracted | 8 | 23 | 14 | 1 | 0 | 46 |

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

- **Run date:** 2026-07-26T14:47:47Z
- **Tool version:** 1.0.0
- **Total protos:** 248
- **Total sidecars:** 169
- **Sidecar directory:** oaa/
- **Git HEAD:** 7a924e1c2df86e24ad3db0415c5e0c91aa7edfad
