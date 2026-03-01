# Proto Schema Validation Report

## Summary

- **Mapped protos:** 171
- **Validated (with APK class):** 171
- **Layer 1 (Schema vs APK):** 155 errors, 320 warnings

## Layer 1: Schema vs APK Database

### Issue Breakdown

| Issue Type | Count |
|---|---|
| modifier_mismatch | 217 |
| type_mismatch | 98 |
| missing_field | 96 |
| syntax_mismatch | 60 |
| extra_field | 4 |

### Per-Message Details

#### AVChannel (1E / 7W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (stream_type): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (audio_type): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 6 (channel_id): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 7 (display_type): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 8 (keycode): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 8 (keycode): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 9 (focus_reason): oneof: ours=True, APK=False

#### AVChannelMediaConfig (1E / 14W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (timing_1): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (feature_flag_1): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (timing_2): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 4 (timing_3): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 5 (timing_4): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 6 (timing_5): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 7 (config_value): ours=int32, APK=uint32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 7 (config_value): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 8 (timing_6): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 9 (feature_flag_2): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 10 (timing_7): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 11 (feature_flag_3): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 12 (timing_8): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 13 (timing_9): oneof: ours=True, APK=False

#### AVChannelSetupRequest (3E / 2W)

- **[WARN]** `type_mismatch`: field 1 (config_index): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (config_index): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (enum repeated) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (enum) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (enum) but missing from our schema

#### AVChannelStartIndication (1E / 6W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (session): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (config): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (unknown_3): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (unknown_3): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 4 (media_config): ours=bytes, APK=message (same wire type)
- **[WARN]** `modifier_mismatch`: field 4 (media_config): oneof: ours=True, APK=False

#### AVInputChannel (2E / 2W)

- **[WARN]** `modifier_mismatch`: field 1 (stream_type): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (audio_config): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 3 in APK (string) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (string) but missing from our schema

#### AVInputOpenResponse (2E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (session): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 2 (value): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 2 (value): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 3 in APK (bool) but missing from our schema

#### AbsoluteInputEvent (1E / 5W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (scan_code): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (scan_code): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (value): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (pointer_id): ours=uint32, APK=bool (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (pointer_id): oneof: ours=True, APK=False

#### AbsoluteInputEvents (1E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 2 (display_id): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (action): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (action): oneof: ours=True, APK=False

#### Accel (2E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (acceleration_x): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (acceleration_y): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (acceleration_z): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 4 in APK (int32) but missing from our schema

#### AssistantFeatureFlags (3E / 1W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3
- **[ERROR]** `missing_field`: field 4 in APK (bool) but missing from our schema
- **[ERROR]** `missing_field`: field 9 in APK (bool) but missing from our schema
- **[WARN]** `extra_field`: field 15 (field_15: bool) in our schema but not in APK DB

#### AudioConfig (2E / 6W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (sample_rate): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (sample_rate): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 2 (bit_depth): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 2 (bit_depth): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (channel_count): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (channel_count): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 4 in APK (int32) but missing from our schema

#### AudioFocusChannel (1E / 1W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `missing_field`: APK class vxq has no fields in DB (may be empty message or missing descriptor)

#### AudioFocusRequest (3E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (audio_focus_type): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (string) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (string) but missing from our schema

#### AuthCompleteIndication (3E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (status): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (string) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (string) but missing from our schema

#### BluetoothChannel (3E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (adapter_address): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 2 (supported_pairing_methods): ours=enum, APK=int64 (same wire type)
- **[WARN]** `modifier_mismatch`: field 2 (supported_pairing_methods): repeated: ours=True, APK=False; packed: ours=True, APK=False
- **[ERROR]** `missing_field`: field 3 in APK (int64) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (int64) but missing from our schema

#### BluetoothPairingRequest (0E / 3W)

- **[WARN]** `modifier_mismatch`: field 1 (phone_address): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (pairing_method): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (phone_name): oneof: ours=True, APK=False

#### BluetoothPairingResponse (1E / 4W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (already_paired): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (status): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (error_code): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (error_code): repeated: ours=False, APK=True; packed: ours=False, APK=True; oneof: ours=True, APK=False

#### ButtonEvents (2E / 0W)

- **[ERROR]** `missing_field`: field 2 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (enum) but missing from our schema

#### CallAvailabilityStatus (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (call_available): oneof: ours=True, APK=False

#### CapabilityEntry (8E / 2W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3
- **[ERROR]** `type_mismatch`: field 3 (capability_data): ours=bytes, APK=enum (DIFFERENT wire type!)
- **[ERROR]** `missing_field`: field 4 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 5 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 6 in APK (message) but missing from our schema
- **[WARN]** `type_mismatch`: field 7 (capability_config): ours=bytes, APK=message (same wire type)
- **[WARN]** `modifier_mismatch`: field 7 (capability_config): oneof: ours=False, APK=True
- **[ERROR]** `missing_field`: field 8 in APK (bool) but missing from our schema
- **[ERROR]** `missing_field`: field 9 in APK (string) but missing from our schema
- **[ERROR]** `missing_field`: field 10 in APK (message repeated) but missing from our schema

#### CapabilityFlag (1E / 0W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3

#### CapabilityPair (1E / 0W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3

#### CarAction (1E / 1W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3
- **[WARN]** `type_mismatch`: field 1 (action_id): ours=int32, APK=enum (same wire type)

#### CarAreaId (1E / 6W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3
- **[WARN]** `type_mismatch`: field 1 (area_type): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 2 (window_ids): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 3 (seat_ids): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 4 (mirror_ids): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 5 (door_ids): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 6 (wheel_ids): ours=int32, APK=enum (same wire type)

#### CarControl (0E / 2W)

- **[WARN]** `modifier_mismatch`: field 5 (metadata): packed: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 6 (side_affinity): ours=int32, APK=enum (same wire type)

#### CarControlGroup (0E / 1W)

- **[WARN]** `type_mismatch`: field 1 (group_type): ours=int32, APK=enum (same wire type)

#### CarLocalMediaPlaybackMetadata (1E / 6W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (song): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (artist): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (album): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 4 (album_art): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 5 (duration_seconds): ours=int32, APK=uint32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 5 (duration_seconds): oneof: ours=True, APK=False

#### CarLocalMediaPlaybackStatus (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 4 (actions): packed: ours=True, APK=False

#### CarProperty (1E / 1W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3
- **[WARN]** `type_mismatch`: field 1 (property_id): ours=int32, APK=enum (same wire type)

#### CarPropertyControl (1E / 0W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3

#### CarPropertyValue (1E / 0W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3

#### ChannelDescriptor (1E / 22W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (channel_id): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (channel_id): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (sensor_channel): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (av_channel): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 4 (input_channel): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 5 (av_input_channel): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 6 (bluetooth_channel): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 7 (radio_channel): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 8 (navigation_channel): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 9 (media_info_channel): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 10 (phone_status_channel): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 11 (media_browser_channel): ours=bytes, APK=message (same wire type)
- **[WARN]** `modifier_mismatch`: field 11 (media_browser_channel): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 12 (vendor_extension_channel): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 13 (notification_channel): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 14 (wifi_channel): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 15 (car_control_channel): ours=bytes, APK=message (same wire type)
- **[WARN]** `modifier_mismatch`: field 15 (car_control_channel): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 16 (generic_notification_channel): ours=bytes, APK=message (same wire type)
- **[WARN]** `modifier_mismatch`: field 16 (generic_notification_channel): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 17 (voice_channel): ours=bytes, APK=message (same wire type)
- **[WARN]** `modifier_mismatch`: field 17 (voice_channel): oneof: ours=True, APK=False

#### ChannelOpenRequest (2E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (priority): ours=sint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (priority): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (channel_id): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 3 in APK (bool) but missing from our schema

#### ChannelOpenResponse (3E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (status): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (string) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (string) but missing from our schema

#### Compass (2E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (bearing): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (pitch): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (roll): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 4 in APK (int32) but missing from our schema

#### ConnectionConfiguration (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (ping_configuration): oneof: ours=True, APK=False

#### ConnectionFeatureFlags (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (enabled): oneof: ours=True, APK=False

#### ConnectionReservedConfig (0E / 1W)

- **[WARN]** `missing_field`: APK class aaji has no fields in DB (may be empty message or missing descriptor)

#### ConnectionSecurityConfig (0E / 2W)

- **[WARN]** `type_mismatch`: field 1 (security_mode): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (security_mode): oneof: ours=True, APK=False

#### ConnectionTransportConfig (0E / 4W)

- **[WARN]** `type_mismatch`: field 2 (transport_params_a): ours=bytes, APK=message (same wire type)
- **[WARN]** `modifier_mismatch`: field 2 (transport_params_a): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (transport_params_b): ours=bytes, APK=message (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (transport_params_b): oneof: ours=True, APK=False

#### ConnectionTuningConfig (0E / 5W)

- **[WARN]** `modifier_mismatch`: field 1 (timeout_ms): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 2 (tuning_a): ours=bytes, APK=message (same wire type)
- **[WARN]** `type_mismatch`: field 3 (tuning_b): ours=bytes, APK=message (same wire type)
- **[WARN]** `type_mismatch`: field 4 (tuning_c): ours=bytes, APK=message (same wire type)
- **[WARN]** `type_mismatch`: field 5 (tuning_d): ours=bytes, APK=message (same wire type)

#### DriverPosition (0E / 1W)

- **[WARN]** `missing_field`: APK class vxi has no fields in DB (may be empty message or missing descriptor)

#### DrivingStatus (3E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (status): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (enum repeated) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (enum) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (enum) but missing from our schema

#### EVConnectorType (0E / 1W)

- **[WARN]** `missing_field`: APK class vxl has no fields in DB (may be empty message or missing descriptor)

#### Environment (2E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (temperature): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (pressure): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (rain): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 4 in APK (int32) but missing from our schema

#### FloatValues (1E / 0W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3

#### FuelType (0E / 1W)

- **[WARN]** `missing_field`: APK class vxo has no fields in DB (may be empty message or missing descriptor)

#### Gear (3E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (gear): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (string) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (string) but missing from our schema

#### Gyro (2E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (rotation_speed_x): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (rotation_speed_y): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (rotation_speed_z): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 4 in APK (int32) but missing from our schema

#### HVAC (2E / 2W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (target_temperature): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (current_temperature): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 3 in APK (bool) but missing from our schema

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

#### InputChannelConfig (1E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 4 (key_configs): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 4 (key_configs): packed: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 5 (capabilities): oneof: ours=True, APK=False

#### IntValues (1E / 0W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3

#### LaneShape (0E / 1W)

- **[WARN]** `missing_field`: APK class vzh has no fields in DB (may be empty message or missing descriptor)

#### LongValues (1E / 0W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3

#### MediaPlaybackMetadata (0E / 6W)

- **[WARN]** `modifier_mismatch`: field 1 (title): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (artist): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (album): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 4 (album_art): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 5 (is_playing): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 6 (album_art_url): oneof: ours=True, APK=False

#### MediaPlaybackStatus (1E / 7W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (playback_state): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (source_app): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (position_seconds): ours=int32, APK=uint32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (position_seconds): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 4 (shuffle): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 5 (repeat): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 6 (repeat_one): oneof: ours=True, APK=False

#### NavigationChannel (1E / 4W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (minimum_interval_ms): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 2 (type): ours=enum, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 2 (type): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (image_options): oneof: ours=True, APK=False

#### NavigationChannelConfig (0E / 1W)

- **[WARN]** `type_mismatch`: field 2 (type): ours=int32, APK=enum (same wire type)

#### NavigationDistanceDisplay (1E / 0W)

- **[ERROR]** `type_mismatch`: field 4 (labels): ours=message, APK=group (DIFFERENT wire type!)

#### NavigationDistanceEntry (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 3 (metadata): repeated: ours=False, APK=True; packed: ours=False, APK=True

#### NavigationDistanceInfo (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 4 (oneof_display): oneof: ours=False, APK=True

#### NavigationFocusRequest (3E / 2W)

- **[WARN]** `type_mismatch`: field 1 (type): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (type): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (enum repeated) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (enum) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (enum) but missing from our schema

#### NavigationFocusResponse (3E / 2W)

- **[WARN]** `type_mismatch`: field 1 (type): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (type): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (enum repeated) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (enum) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (enum) but missing from our schema

#### NavigationImageOptions (2E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (width): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (height): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (colour_depth_bits): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 4 in APK (int32) but missing from our schema

#### NavigationState (3E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (state): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (enum repeated) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (enum) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (enum) but missing from our schema

#### NightMode (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (is_night): oneof: ours=True, APK=False

#### NotificationChannel (1E / 1W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `missing_field`: APK class wah has no fields in DB (may be empty message or missing descriptor)

#### Odometer (2E / 2W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (total_mileage): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (trip_mileage): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 3 in APK (bool) but missing from our schema

#### ParkingBrake (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (parking_brake): oneof: ours=True, APK=False

#### Passenger (0E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (passenger_present): oneof: ours=True, APK=False

#### PhoneCallState (0E / 1W)

- **[WARN]** `missing_field`: APK class wae has no fields in DB (may be empty message or missing descriptor)

#### PhoneConnectionConfig (0E / 2W)

- **[WARN]** `type_mismatch`: field 4 (security_mode): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 5 (ap_type): ours=int32, APK=enum (same wire type)

#### PhoneInputType (3E / 0W)

- **[ERROR]** `type_mismatch`: field 1 (action): ours=enum, APK=message (DIFFERENT wire type!)
- **[ERROR]** `missing_field`: field 2 in APK (string) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (string) but missing from our schema

#### PingConfigPair (1E / 0W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3

#### PingConfiguration (0E / 3W)

- **[WARN]** `modifier_mismatch`: field 1 (ping_interval_ns): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 2 (ping_timeout_ms): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 2 (ping_timeout_ms): oneof: ours=True, APK=False

#### PingRequest (0E / 2W)

- **[WARN]** `type_mismatch`: field 1 (timestamp): ours=int64, APK=uint64 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (timestamp): oneof: ours=True, APK=False

#### PingResponse (0E / 2W)

- **[WARN]** `type_mismatch`: field 1 (timestamp): ours=int64, APK=uint64 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (timestamp): oneof: ours=True, APK=False

#### RPM (3E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (rpm): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (enum repeated) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (enum) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (enum) but missing from our schema

#### RadioMetadata (0E / 1W)

- **[WARN]** `type_mismatch`: field 9 (hd_sub_channels_available): ours=int32, APK=uint32 (same wire type)

#### RadioProgramIdentifier (0E / 1W)

- **[WARN]** `type_mismatch`: field 2 (value): ours=int64, APK=uint64 (same wire type)

#### RadioProgramType (0E / 2W)

- **[WARN]** `type_mismatch`: field 1 (schema): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 2 (code): ours=int32, APK=uint32 (same wire type)

#### RadioSongMetadata (0E / 1W)

- **[WARN]** `type_mismatch`: field 6 (duration_seconds): ours=int64, APK=uint64 (same wire type)

#### RadioStation (0E / 4W)

- **[WARN]** `type_mismatch`: field 2 (identifier_type): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 7 (codec_type): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 8 (band_type): ours=int32, APK=enum (same wire type)
- **[WARN]** `type_mismatch`: field 11 (region): ours=int32, APK=enum (same wire type)

#### RelativeInputEvent (2E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (scan_code): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (scan_code): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (delta): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 3 in APK (bool) but missing from our schema

#### RelativeInputEvents (2E / 0W)

- **[ERROR]** `missing_field`: field 2 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (enum) but missing from our schema

#### Sensor (3E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (type): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (string) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (string) but missing from our schema

#### SensorChannel (1E / 3W)

- **[ERROR]** `type_mismatch`: field 2 (location_characterization): ours=uint32, APK=message (DIFFERENT wire type!)
- **[WARN]** `modifier_mismatch`: field 2 (location_characterization): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (fuel_types): repeated: ours=True, APK=False; packed: ours=True, APK=False
- **[WARN]** `extra_field`: field 4 (ev_connectors: enum) in our schema but not in APK DB

#### SensorChannelConfig (1E / 5W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 2 (update_interval_ms): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (fuel_types): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (fuel_types): packed: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 4 (ev_connector_types): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 4 (ev_connector_types): packed: ours=True, APK=False

#### SensorEventIndication (1E / 6W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 21 (toll_road): ours=bytes, APK=message (same wire type)
- **[WARN]** `type_mismatch`: field 22 (range_remaining): ours=bytes, APK=message (same wire type)
- **[WARN]** `type_mismatch`: field 23 (fuel_type_info): ours=bytes, APK=message (same wire type)
- **[WARN]** `type_mismatch`: field 24 (ev_battery_info): ours=bytes, APK=message (same wire type)
- **[WARN]** `type_mismatch`: field 25 (ev_charge_info): ours=bytes, APK=message (same wire type)
- **[WARN]** `type_mismatch`: field 26 (ev_charge_status): ours=bytes, APK=message (same wire type)

#### SensorStartRequestMessage (1E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (sensor_type): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 2 (refresh_interval): ours=int64, APK=uint64 (same wire type)
- **[WARN]** `modifier_mismatch`: field 2 (refresh_interval): oneof: ours=True, APK=False

#### SensorStartResponseMessage (3E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (status): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (string) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (string) but missing from our schema

#### SensorTypeEntry (1E / 2W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (sensor_type): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (sensor_type): oneof: ours=True, APK=False

#### SetCarPropertyListenerResult (0E / 1W)

- **[WARN]** `type_mismatch`: field 2 (status): ours=int32, APK=enum (same wire type)

#### ShutdownRequest (3E / 1W)

- **[WARN]** `modifier_mismatch`: field 1 (reason): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (string) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (string) but missing from our schema

#### StatsEntry (13E / 4W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[ERROR]** `type_mismatch`: field 1 (average): ours=int64, APK=message (DIFFERENT wire type!)
- **[WARN]** `modifier_mismatch`: field 1 (average): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (minimum): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (maximum): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 4 (count): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 5 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 6 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 7 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 8 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 9 in APK (int64) but missing from our schema
- **[ERROR]** `missing_field`: field 10 in APK (int64) but missing from our schema
- **[ERROR]** `missing_field`: field 11 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 12 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 13 in APK (message) but missing from our schema
- **[ERROR]** `missing_field`: field 14 in APK (int64) but missing from our schema
- **[ERROR]** `missing_field`: field 15 in APK (int64) but missing from our schema

#### SteeringWheel (2E / 2W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (steering_angle): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (wheel_speed): repeated: ours=True, APK=False; packed: ours=True, APK=False
- **[ERROR]** `missing_field`: field 3 in APK (bool) but missing from our schema

#### TouchConfig (1E / 5W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (width): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (width): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 2 (height): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 2 (height): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (unknown_3): oneof: ours=True, APK=False

#### TouchCoordinate (1E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (x): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (y): oneof: ours=True, APK=False
- **[WARN]** `extra_field`: field 3 (pointer_id: uint32) in our schema but not in APK DB

#### TouchLocation (2E / 6W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (x): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (x): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 2 (y): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 2 (y): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (pointer_id): ours=uint32, APK=int32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (pointer_id): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 4 in APK (int32) but missing from our schema

#### VoiceSessionRequest (1E / 2W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (session_type): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (session_type): oneof: ours=True, APK=False

#### WiFiProjectionChannel (1E / 2W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (ssid): ours=string, APK=message (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (ssid): repeated: ours=False, APK=True; oneof: ours=True, APK=False

#### WifiChannel (4E / 1W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (ssid): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (int64) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (int64) but missing from our schema
- **[ERROR]** `missing_field`: field 4 in APK (int64) but missing from our schema

#### WifiConnectStatus (1E / 3W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (state): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (state): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (status_text): oneof: ours=True, APK=False

#### WifiConnectionRejection (1E / 2W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `type_mismatch`: field 1 (reason): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (reason): oneof: ours=True, APK=False

#### WifiDirectConfig (1E / 7W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (device_name): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (device_address): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (ssid): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 4 (passphrase): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 5 (group_owner_info): ours=bytes, APK=message (same wire type)
- **[WARN]** `modifier_mismatch`: field 5 (group_owner_info): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 6 (frequency): oneof: ours=True, APK=False

#### WifiInfoRequest (1E / 1W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `missing_field`: APK class wdl has no fields in DB (may be empty message or missing descriptor)

#### WifiInfoResponse (1E / 7W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (ssid): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (bssid): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (passphrase): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 4 (security_mode): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 4 (security_mode): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 5 (ap_type): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 5 (ap_type): oneof: ours=True, APK=False

#### WifiNetworkInfo (5E / 6W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[ERROR]** `type_mismatch`: field 1 (ssid): ours=string, APK=int32 (DIFFERENT wire type!)
- **[WARN]** `modifier_mismatch`: field 1 (ssid): oneof: ours=True, APK=False
- **[ERROR]** `type_mismatch`: field 2 (bssid): ours=string, APK=int32 (DIFFERENT wire type!)
- **[WARN]** `modifier_mismatch`: field 2 (bssid): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (passphrase): ours=string, APK=bytes (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (passphrase): oneof: ours=True, APK=False
- **[ERROR]** `type_mismatch`: field 4 (security_mode): ours=int32, APK=message (DIFFERENT wire type!)
- **[WARN]** `modifier_mismatch`: field 4 (security_mode): oneof: ours=True, APK=False
- **[ERROR]** `missing_field`: field 5 in APK (message) but missing from our schema
- **[WARN]** `extra_field`: field 6 (supported_channels: int32) in our schema but not in APK DB

#### WifiSecurityResponse (3E / 13W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (ssid): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (key): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (bssid): oneof: ours=True, APK=False
- **[ERROR]** `type_mismatch`: field 4 (security_mode): ours=enum, APK=message (DIFFERENT wire type!)
- **[WARN]** `modifier_mismatch`: field 4 (security_mode): oneof: ours=True, APK=False
- **[ERROR]** `type_mismatch`: field 5 (access_point_type): ours=enum, APK=message (DIFFERENT wire type!)
- **[WARN]** `modifier_mismatch`: field 5 (access_point_type): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 6 (wifi_direct_config): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 7 (ip_address): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 8 (gateway): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 9 (prefix_length): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 10 (hidden_network): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 11 (band_5ghz): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 12 (unknown_12): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 13 (unknown_13): oneof: ours=True, APK=False

#### WifiSetupMessage (0E / 1W)

- **[WARN]** `missing_field`: APK class wdn has no fields in DB (may be empty message or missing descriptor)

#### WifiStartResponse (1E / 4W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (ip_address): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (port): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (status): ours=sint32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (status): oneof: ours=True, APK=False

#### WifiVersionRequest (1E / 7W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (major_version): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (minor_version): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 3 (wifi_channel_preference): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 3 (wifi_channel_preference): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 4 (supported_channels): packed: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 5 (device_info): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 6 (feature_flags): oneof: ours=True, APK=False

#### WifiVersionResponse (1E / 9W)

- **[ERROR]** `syntax_mismatch`: ours=proto3, APK=proto2
- **[WARN]** `modifier_mismatch`: field 1 (major_version): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 2 (minor_version): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 3 (device_serial): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 4 (version_status): ours=sint32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 4 (version_status): oneof: ours=True, APK=False
- **[WARN]** `type_mismatch`: field 5 (selected_wifi_channel_type): ours=int32, APK=enum (same wire type)
- **[WARN]** `modifier_mismatch`: field 5 (selected_wifi_channel_type): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 6 (session_info): oneof: ours=True, APK=False
- **[WARN]** `modifier_mismatch`: field 7 (extra_data): oneof: ours=True, APK=False
