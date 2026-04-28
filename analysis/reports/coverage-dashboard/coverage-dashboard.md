# Coverage Dashboard

## Summary

160 sidecars covering 245 protos (65% coverage). 3 Platinum / single-OEM, 29 Gold, 111 Silver, 10 Bronze.

21 protos awaiting deep-trace for Platinum promotion (oem_match_pending_gold).

## Per-Channel Tier Counts

| Channel | Bronze | Silver | Gold | Platinum (s-OEM) | Retracted | Superseded | Total |
|---------|--------|--------|------|------------------|-----------|------------|-------|
| audio | 2 | 5 | 0 | 0 | 0 | 0 | 7 |
| av | 0 | 11 | 0 | 0 | 0 | 0 | 11 |
| bluetooth | 0 | 3 | 0 | 0 | 0 | 0 | 3 |
| carcontrol | 0 | 0 | 2 | 0 | 0 | 0 | 2 |
| common | 1 | 4 | 0 | 0 | 0 | 0 | 5 |
| control | 1 | 24 | 2 | 0 | 0 | 0 | 27 |
| generic | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| input | 0 | 4 | 13 | 0 | 0 | 0 | 17 |
| media | 0 | 0 | 4 | 2 | 3 | 1 | 10 |
| mediabrowser | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| mic | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| navigation | 0 | 12 | 0 | 0 | 0 | 0 | 12 |
| notification | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| phone | 0 | 0 | 3 | 0 | 0 | 0 | 3 |
| radio | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| sensor | 3 | 34 | 0 | 0 | 0 | 0 | 37 |
| verification | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| video | 0 | 3 | 2 | 1 | 2 | 0 | 8 |
| wifi | 1 | 10 | 2 | 0 | 1 | 0 | 14 |
| **Total** | **10** | **111** | **29** | **3** | **6** | **1** | **160** |

## Evidence Type Breakdown

| Tier | apk_deep_trace | apk_static | cross_version | deep_trace | handler_trace | platinum_evidence | Total |
|------|----------------|------------|---------------|------------|---------------|-------------------|-------|
| Bronze | 0 | 10 | 10 | 0 | 0 | 0 | 20 |
| Silver | 0 | 167 | 221 | 0 | 0 | 0 | 388 |
| Gold | 5 | 21 | 10 | 20 | 13 | 0 | 69 |
| Platinum | 2 | 4 | 3 | 1 | 0 | 3 | 13 |
| Retracted | 2 | 3 | 2 | 1 | 0 | 0 | 8 |
| Superseded | 1 | 1 | 0 | 0 | 0 | 0 | 2 |

## Missing Sidecars

85 proto files without audit sidecars:

### audio (3 missing)

- AudioFocusStateEnum.proto
- AudioFocusTypeEnum.proto
- AudioTypeEnum.proto

### av (8 missing)

- AVChannelMediaOptionsMessage.proto
- AVChannelMessageIdsEnum.proto
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

### media (2 missing)

- BufferedMediaSinkMessage.proto
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

### video (10 missing)

- ColorSchemeSupportEnum.proto
- DisplayTypeEnum.proto
- IntegratedOverlayStartNotification.proto
- IntegratedOverlayStopNotification.proto
- UpdateHuUiConfigResponse.proto
- UpdateUiConfigRequestMessage.proto
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

- **Run date:** 2026-04-12T16:59:26Z
- **Tool version:** 1.0.0
- **Total protos:** 245
- **Total sidecars:** 160
- **Sidecar directory:** oaa/
- **Git HEAD:** 4e9dadd69ce00100c07ae73bf116f2f868643f44
