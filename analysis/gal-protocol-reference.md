# Google Automotive Link (GAL) Protocol Reference

Extracted from DHU 2.1 binary (`desktop-head-unit.exe`, Build 2022-12-15-495540972).
Protocol version: 1.7

## Internal Source Structure

```
wireless/android/auto/projection_protocol/v1_7/receiver_lib/
  AudioSource.cc
  Controller.cc
  InputSource.cc
  MediaPlaybackStatusEndpoint.cc
  MediaSinkBase.cc
  MessageRouter.cc
  NavigationStatusEndpoint.cc
  PhoneStatusEndpoint.cc
  SensorSource.cc
```

## Services (Channel Types)

```
gal.BluetoothService
gal.GenericNotificationService
gal.InputSourceService
gal.MediaBrowserService
gal.MediaPlaybackStatusService
gal.MediaSinkService
gal.MediaSourceService
gal.NavigationStatusService
gal.PhoneStatusService
gal.RadioService
gal.SensorSourceService
gal.VendorExtensionService
gal.WifiProjectionService
```

## All GAL Message Types (196 total)

### Connection / Channel Management
- Ack
- AuthResponse
- ByeByeRequest / ByeByeResponse
- ChannelCloseNotification
- ChannelOpenRequest / ChannelOpenResponse
- Config
- ConfigureChannelSpacingRequest / ConfigureChannelSpacingResponse
- ConnectionConfiguration
- PingConfiguration / PingRequest / PingResponse
- Service
- ServiceDiscoveryRequest / ServiceDiscoveryResponse / ServiceDiscoveryUpdate
- Setup
- Start / Stop
- StepChannelRequest / StepChannelResponse
- UiConfig / UpdateUiConfigReply / UpdateUiConfigRequest
- UserSwitchRequest / UserSwitchResponse
- VersionRequestOptions / VersionResponseOptions

### Sensor Data Messages
- AccelerometerData
- CompassData
- DeadReckoningData
- DiagnosticsData
- DoorData
- DrivingStatusData
- EnvironmentData
- FuelData
- GearData
- GpsSatellite / GpsSatelliteData
- GyroscopeData
- HvacData
- LightData
- LocationData / Location
- NightModeData
- OdometerData
- ParkingBrakeData
- PassengerData
- RpmData
- SpeedData
- TirePressureData
- TollCardData

### Sensor Service
- SensorBatch
- SensorError
- SensorRequest / SensorResponse
- SensorSourceService / SensorSourceService_Sensor
- GalVerificationSetSensor

### Input
- AbsoluteEvent / AbsoluteEvent_Abs
- InputFeedback
- InputReport
- InputSourceService / InputSourceService_TouchPad / InputSourceService_TouchScreen
- Insets
- InstrumentClusterInput
- KeyBindingRequest / KeyBindingResponse
- KeyEvent / KeyEvent_Key
- RelativeEvent / RelativeEvent_Rel
- TouchEvent / TouchEvent_Pointer

### Audio
- AudioConfiguration
- AudioFocusNotification / AudioFocusRequestNotification
- AudioUnderflowNotification
- MediaSinkService
- MediaSourceService
- MicrophoneRequest / MicrophoneResponse

### Video
- VideoConfiguration
- VideoFocusNotification / VideoFocusRequestNotification

### Media Browser / Playback
- MediaBrowserInput
- MediaBrowserService
- MediaGetNode
- MediaList / MediaListNode
- MediaPlaybackMetadata
- MediaPlaybackStatus / MediaPlaybackStatusService
- MediaRootNode
- MediaSong / MediaSongNode
- MediaSource / MediaSourceNode

### Navigation
- NavFocusNotification / NavFocusRequestNotification
- NavigationCue
- NavigationCurrentPosition
- NavigationDestination / NavigationDestinationDistance
- NavigationDistance
- NavigationLane / NavigationLane_LaneDirection
- NavigationManeuver
- NavigationNextTurnDistanceEvent / NavigationNextTurnEvent
- NavigationRoad
- NavigationState
- NavigationStatus / NavigationStatusService
- NavigationStatusService_ImageOptions
- NavigationStatusStart / NavigationStatusStop
- NavigationStep / NavigationStepDistance

### Phone
- CallAvailabilityStatus
- PhoneStatus / PhoneStatus_Call
- PhoneStatusInput / PhoneStatusService

### Bluetooth
- BluetoothAuthenticationData / BluetoothAuthenticationResult
- BluetoothPairingRequest / BluetoothPairingResponse
- BluetoothService

### WiFi Projection
- WifiCredentialsRequest / WifiCredentialsResponse
- WifiProjectionService
- WirelessTcpConfiguration

### Radio (FM/HD Radio)
- ActiveRadioNotification
- CancelRadioOperationsRequest / CancelRadioOperationsResponse
- GetProgramListRequest / GetProgramListResponse
- GetTrafficUpdateRequest / GetTrafficUpdateResponse
- HdRadioArtistExperience
- HdRadioComment / HdRadioCommercial
- HdRadioPsdData / HdRadioSisData
- HdRadioStationInfo
- MuteRadioRequest / MuteRadioResponse
- RadioProperties
- RadioService
- RadioSourceRequest / RadioSourceResponse
- RadioStateNotification
- RadioStationInfo / RadioStationInfoNotification / RadioStationMetaData
- Range
- RdsData
- ScanStationsRequest / ScanStationsResponse
- SeekStationRequest / SeekStationResponse
- SelectActiveRadioRequest
- StationPreset / StationPresetList / StationPresetsNotification
- TuneToStationRequest / TuneToStationResponse
- TrafficIncident

### Notifications
- BatteryStatusNotification
- GenericNotificationAck / GenericNotificationMessage
- GenericNotificationService
- GenericNotificationSubscribe / GenericNotificationUnsubscribe
- VoiceSessionNotification

### Diagnostics / Verification
- GalVerificationAudioFocus
- GalVerificationBugReportRequest / GalVerificationBugReportResponse
- GalVerificationDisplayInformationRequest / GalVerificationDisplayInformationResponse
- GalVerificationInjectInput
- GalVerificationMediaSinkStatus
- GalVerificationScreenCaptureRequest / GalVerificationScreenCaptureResponse
- GoogleDiagnosticsBugReportRequest / GoogleDiagnosticsBugReportResponse

### Vehicle Data (Extended)
- CarConnectedDevices / CarConnectedDevicesRequest / ConnectedDevice

### Vendor Extensions
- VendorExtensionService

## Status / Error Enums

### Connection Status
- STATUS_OK / STATUS_SUCCESS
- STATUS_BUSY
- STATUS_READY / STATUS_WAIT
- STATUS_INTERNAL_ERROR
- STATUS_OUT_OF_MEMORY
- STATUS_FRAMING_ERROR
- STATUS_NO_COMPATIBLE_VERSION
- STATUS_UNEXPECTED_MESSAGE / STATUS_UNSOLICITED_MESSAGE
- STATUS_COMMAND_NOT_SUPPORTED
- STATUS_PING_TIMEOUT

### Channel/Service Status
- STATUS_INVALID_CHANNEL
- STATUS_INVALID_INPUT
- STATUS_INVALID_PRIORITY
- STATUS_INVALID_SENSOR
- STATUS_INVALID_SERVICE
- CHANNEL_ID_NOT_P256
- CHANNEL_ID_SIGNATURE_INVALID

### Authentication
- STATUS_AUTHENTICATION_FAILURE
- STATUS_AUTHENTICATION_FAILURE_CERT_EXPIRED
- STATUS_AUTHENTICATION_FAILURE_CERT_NOT_YET_VALID
- STATUS_CERTIFICATE_ERROR

### Bluetooth
- STATUS_BLUETOOTH_AUTH_DATA_MISMATCH
- STATUS_BLUETOOTH_HFP_ANOTHER_CONNECTION
- STATUS_BLUETOOTH_HFP_CONNECTION_FAILURE
- STATUS_BLUETOOTH_INVALID_ADDRESS
- STATUS_BLUETOOTH_INVALID_AUTH_DATA
- STATUS_BLUETOOTH_INVALID_PAIRING_METHOD
- STATUS_BLUETOOTH_PAIRING_DELAYED
- STATUS_BLUETOOTH_UNAVAILABLE
- ERROR_BT_CLOSED_AFTER_START / ERROR_BT_CLOSED_BEFORE_START

### WiFi
- ERROR_PHONE_UNABLE_TO_CONNECT_WIFI
- ERROR_NO_RFCOMM_CONNECTION

### Media / Keycode
- STATUS_KEYCODE_NOT_BOUND
- STATUS_MEDIA_CONFIG_MISMATCH

### Radio
- STATUS_RADIO_COMM_ERROR
- STATUS_RADIO_INVALID_STATION
- STATUS_RADIO_STATION_PRESETS_NOT_SUPPORTED

### General Errors
- ERROR_HU_INTERNAL
- ERROR_INCOMPATIBLE_PHONE_PROTOCOL_VERSION
- ERROR_INVALID_REQUEST
- ERROR_MULTIPLE_USER_SWITCH_REQUEST
- ERROR_REQUEST_TIMEOUT

### Driving Status Flags
- DRIVE_STATUS_UNRESTRICTED
- DRIVE_STATUS_NO_CONFIG
- DRIVE_STATUS_NO_KEYBOARD_INPUT
- DRIVE_STATUS_NO_VIDEO
- DRIVE_STATUS_NO_VOICE_INPUT
- DRIVE_STATUS_LIMIT_MESSAGE_LEN

### Traffic
- NO_TRAFFIC_SERVICE / TMC_TRAFFIC_SERVICE

## DHU Config: Sensor Options

From `kitchen_sink.ini` — all sensors the DHU supports:

```ini
[sensors]
night_mode = true
driving_status = true
fuel = true
odometer = true
speed = true
toll_card = true
accelerometer = true
gyroscope = true
compass = true
location = true
parking_brake = true
gear = true
gps_satellite = true
```

Note: The binary contains data types for many more sensors (RPM, tire pressure, HVAC, doors, etc.)
that are not exposed through the DHU config. These may be Automotive OS-only or reserved for future use.

## DHU Console Commands

```
Day/Night:    night, day, daynight, nightday
Speed:        speed <value>
Fuel:         fuel, range, lowfuel
Location:     location <lat> <lon>
Odometer:     odometer
IMU:          accel, compass, gyro
Toll:         tollcard insert, tollcard remove
Gear:         gear <value>         (requires config)
Parking:      parking_brake        (requires config)
GPS:          gps_satellite        (requires config)
Restrictions: restrict none, restrict all
Focus:        focus audio, focus nav, focus video, focus video toggle
Keycode:      keycode home/back/call/endcall/search/media_*/navigation/tel
Mic:          mic begin/play/repeat/reject
D-pad:        dpad up/down/left/right/click/back/rotate/flick/0-9/*/#/+
Touch:        tap <x> <y>
System:       help, quit, exit, licenses, sleep, screenshot
```
