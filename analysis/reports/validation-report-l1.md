# Proto Schema Validation Report

## Summary

- **Mapped protos:** 215
- **Validated (with APK class):** 203
- **Layer 1 (Schema vs APK):** 24 errors, 12 warnings

## Layer 1: Schema vs APK Database

### Issue Breakdown

| Issue Type | Count |
|---|---|
| missing_field | 19 |
| type_mismatch | 9 |
| extra_field | 5 |
| syntax_mismatch | 2 |
| modifier_mismatch | 1 |

### Per-Message Details

#### AbsInputEvent (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.messages.AbsInputEvent in compiled descriptor pool

#### AbsoluteInputEvent (1E / 1W)

- **[WARN]** `type_mismatch`: field 2 (value): ours=int32, APK=uint32 (same wire type)
- **[ERROR]** `missing_field`: field 3 in APK (uint32) but missing from our schema

#### AbsoluteInputEvents (2E / 0W)

- **[ERROR]** `missing_field`: field 2 in APK (uint32) but missing from our schema
- **[ERROR]** `missing_field`: field 3 in APK (enum) but missing from our schema

#### AudioFocusState (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.messages.AudioFocusState in compiled descriptor pool

#### AudioStreamType (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.messages.AudioStreamType in compiled descriptor pool

#### BluetoothPairingResponse (1E / 2W)

- **[WARN]** `type_mismatch`: field 1 (status): ours=enum, APK=bool (same wire type)
- **[WARN]** `type_mismatch`: field 2 (already_paired): ours=bool, APK=enum (same wire type)
- **[ERROR]** `missing_field`: field 3 in APK (enum repeated) but missing from our schema

#### CarLocalMediaPlayback (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.enums.CarLocalMediaPlayback in compiled descriptor pool

#### ChannelDescriptor (0E / 1W)

- **[WARN]** `extra_field`: field 18 (car_intent_channel: message) in our schema but not in APK DB

#### FloatValues (1E / 0W)

- **[ERROR]** `type_mismatch`: field 1 (values): ours=float, APK=int64 (DIFFERENT wire type!)

#### GalPingRequest (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.messages.GalPingRequest in compiled descriptor pool

#### GalPingResponse (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.messages.GalPingResponse in compiled descriptor pool

#### HeadUnitInfo (1E / 1W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3
- **[WARN]** `extra_field`: field 9 (vehicle_type: int32) in our schema but not in APK DB

#### InputBindingRequest (1E / 2W)

- **[WARN]** `type_mismatch`: field 1 (keycodes): ours=int32, APK=uint32 (same wire type)
- **[WARN]** `modifier_mismatch`: field 1 (keycodes): repeated: ours=True, APK=False; packed: ours=True, APK=False
- **[ERROR]** `missing_field`: field 2 in APK (int32) but missing from our schema

#### InputChannel (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.data.InputChannel in compiled descriptor pool

#### KeyEvent (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.data.KeyEvent in compiled descriptor pool

#### LongValues (1E / 0W)

- **[ERROR]** `type_mismatch`: field 1 (values): ours=int64, APK=float (DIFFERENT wire type!)

#### MediaEventIdWrapper (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.messages.MediaEventIdWrapper in compiled descriptor pool

#### MediaPlaybackMetadata (3E / 1W)

- **[ERROR]** `syntax_mismatch`: ours=proto2, APK=proto3
- **[ERROR]** `type_mismatch`: field 5 (unknown_5): ours=string, APK=bool (DIFFERENT wire type!)
- **[ERROR]** `type_mismatch`: field 6 (unknown_6): ours=uint32, APK=string (DIFFERENT wire type!)
- **[WARN]** `extra_field`: field 7 (unknown_7: int32) in our schema but not in APK DB

#### NavigationChannel (0E / 1W)

- **[WARN]** `type_mismatch`: field 2 (type): ours=enum, APK=int32 (same wire type)

#### NavigationFocusIndication (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.messages.NavigationFocusIndication in compiled descriptor pool

#### PingRequest (0E / 1W)

- **[WARN]** `extra_field`: field 3 (payload: bytes) in our schema but not in APK DB

#### PingResponse (0E / 1W)

- **[WARN]** `extra_field`: field 2 (payload: bytes) in our schema but not in APK DB

#### RadioBand (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.data.RadioBand in compiled descriptor pool

#### SensorErrorStatus (0E / 1W)

- **[WARN]** `missing_field`: APK class wbg has no fields in DB (may be empty message or missing descriptor)

#### TouchConfig (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.data.TouchConfig in compiled descriptor pool

#### TouchCoordinate (1E / 0W)

- **[ERROR]** `missing_field`: could not find oaa.proto.data.TouchCoordinate in compiled descriptor pool
