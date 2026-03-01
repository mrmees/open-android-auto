# Proto Schema Validation Report

## Summary

- **Mapped protos:** 171
- **Validated (with APK class):** 171
- **Layer 1 (Schema vs APK):** 0 errors, 60 warnings

## Layer 1: Schema vs APK Database

### Issue Breakdown

| Issue Type | Count |
|---|---|
| modifier_mismatch | 31 |
| type_mismatch | 17 |
| missing_field | 11 |
| extra_field | 1 |

### Per-Message Details

#### AVChannelSetupRequest (0E / 1W)

- **[WARN]** `type_mismatch`: field 1 (config_index): ours=uint32, APK=enum (same wire type)

#### AudioFocusChannel (0E / 1W)

- **[WARN]** `missing_field`: APK class vxq has no fields in DB (may be empty message or missing descriptor)

#### AuthCompleteIndication (0E / 1W)

- **[WARN]** `type_mismatch`: field 1 (status): ours=enum, APK=int32 (same wire type)

#### BluetoothPairingRequest (0E / 3W)

- **[WARN]** `modifier_mismatch`: field 1 (phone_address): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (pairing_method): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (phone_name): oneof: ours=True, APK=False

#### CarAreaId (0E / 5W)

- **[WARN]** `type_mismatch`: field 2 (window_ids): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 3 (seat_ids): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 4 (mirror_ids): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 5 (door_ids): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 6 (wheel_ids): ours=int32, APK=enum (same wire type)

#### CarControl (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 5 (metadata): packed: ours=True, APK=False

#### CarLocalMediaPlaybackStatus (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 4 (actions): packed: ours=True, APK=False

#### ConnectionConfiguration (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (ping_configuration): oneof: ours=True, APK=False

#### ConnectionFeatureFlags (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (enabled): oneof: ours=True, APK=False

#### ConnectionReservedConfig (0E / 1W)

- **[WARN]** `missing_field`: APK class aaji has no fields in DB (may be empty message or missing descriptor)

#### ConnectionSecurityConfig (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (security_mode): oneof: ours=True, APK=False

#### ConnectionTransportConfig (0E / 2W)

- **[WARN]** `modifier_mismatch`: field 2 (transport_params_a): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (transport_params_b): oneof: ours=True, APK=False

#### ConnectionTuningConfig (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (timeout_ms): oneof: ours=True, APK=False

#### DriverPosition (0E / 1W)

- **[WARN]** `missing_field`: APK class vxi has no fields in DB (may be empty message or missing descriptor)

#### EVConnectorType (0E / 1W)

- **[WARN]** `missing_field`: APK class vxl has no fields in DB (may be empty message or missing descriptor)

#### FuelType (0E / 1W)

- **[WARN]** `missing_field`: APK class vxo has no fields in DB (may be empty message or missing descriptor)

#### HapticFeedbackType (0E / 1W)

- **[WARN]** `missing_field`: APK class vxm has no fields in DB (may be empty message or missing descriptor)

#### HeadUnitInfo (0E / 8W)

- **[WARN]** `modifier_mismatch`: field 1 (make): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (model): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (year): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 4 (vehicle_id): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 5 (head_unit_make): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 6 (head_unit_model): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 7 (head_unit_software_build): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 8 (head_unit_software_version): oneof: ours=True, APK=False

#### InputChannelConfig (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (input_type): packed: ours=False, APK=True

#### LaneShape (0E / 1W)

- **[WARN]** `missing_field`: APK class vzh has no fields in DB (may be empty message or missing descriptor)

#### MediaPlaybackMetadata (0E / 6W)

- **[WARN]** `modifier_mismatch`: field 1 (title): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (artist): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (album): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 4 (album_art): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 5 (is_playing): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 6 (album_art_url): oneof: ours=True, APK=False

#### NavigationChannel (0E / 1W)

- **[WARN]** `type_mismatch`: field 2 (type): ours=enum, APK=int32 (same wire type)

#### NavigationChannelConfig (0E / 1W)

- **[WARN]** `type_mismatch`: field 2 (type): ours=int32, APK=enum (same wire type)

#### NavigationDistanceDisplay (0E / 1W)

- **[WARN]** `type_mismatch`: field 4 (labels): ours=message, APK=group (DIFFERENT wire type!) [known limitation]

#### NavigationDistanceEntry (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 3 (metadata): repeated: ours=False, APK=True; packed: ours=False, APK=True

#### NavigationDistanceInfo (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 4 (oneof_display): oneof: ours=False, APK=True

#### NotificationChannel (0E / 1W)

- **[WARN]** `missing_field`: APK class wah has no fields in DB (may be empty message or missing descriptor)

#### PhoneCallState (0E / 1W)

- **[WARN]** `missing_field`: APK class wae has no fields in DB (may be empty message or missing descriptor)

#### PingConfiguration (0E / 2W)

- **[WARN]** `modifier_mismatch`: field 1 (ping_interval_ns): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (ping_timeout_ms): oneof: ours=True, APK=False

#### RadioStation (0E / 1W)

- **[WARN]** `type_mismatch`: field 2 (identifier_type): ours=int32, APK=enum (same wire type)

#### TouchCoordinate (0E / 1W)

- **[WARN]** `extra_field`: field 3 (pointer_id: uint32) in our schema but not in APK DB

#### WiFiProjectionChannel (0E / 2W)

- **[WARN]** `type_mismatch`: field 1 (ssid): ours=string, APK=message (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (ssid): repeated: ours=False, APK=True

#### WifiConnectStatus (0E / 1W)

- **[WARN]** `type_mismatch`: field 1 (state): ours=sint32, APK=enum (same wire type)

#### WifiInfoRequest (0E / 1W)

- **[WARN]** `missing_field`: APK class wdl has no fields in DB (may be empty message or missing descriptor)

#### WifiSecurityResponse (0E / 2W)

- **[WARN]** `type_mismatch`: field 4 (security_mode): ours=enum, APK=message (DIFFERENT wire type!) [known limitation]
- **[WARN]** `type_mismatch`: field 5 (access_point_type): ours=enum, APK=message (DIFFERENT wire type!) [known limitation]

#### WifiSetupMessage (0E / 1W)

- **[WARN]** `missing_field`: APK class wdn has no fields in DB (may be empty message or missing descriptor)

#### WifiStartResponse (0E / 1W)

- **[WARN]** `type_mismatch`: field 3 (status): ours=sint32, APK=enum (same wire type)

#### WifiVersionResponse (0E / 1W)

- **[WARN]** `type_mismatch`: field 4 (version_status): ours=sint32, APK=enum (same wire type)
