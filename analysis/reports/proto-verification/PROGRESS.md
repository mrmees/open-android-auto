# Proto Verification Progress

**Design:** `docs/plans/2026-03-06-proto-verification-design.md`
**Started:** 2026-03-06
**Last updated:** 2026-03-06

## Summary

| Status | Count |
|--------|-------|
| Verified (Gold) | 127 |
| Schema Errors Found & Fixed | 62 |
| New Protos Discovered | 10 (MediaPlaybackStatusEvent, VehicleEnergyForecast, InputBindingResponse, IntegratedOverlayStart/Stop, UpdateHuUiConfigResponse, UpdateUiConfigRequest, AVChannelMediaOptions, MicrophoneOpenResponse, RadioSearchRequest) |
| Retracted / Removed | 23 |
| Relocated (wrong channel) | 4 (BindingRequest/Response → input, CallAvailability/VoiceSession → control) |
| Pending | remaining channels |

## Channel Verification Status

### Phase 1 — Priority Wire Channels

| # | Channel | GAL Tag | Handler Class | Status | Report | Notes |
|---|---------|---------|---------------|--------|--------|-------|
| 1a | Media Info | CAR.GAL.INST | iai/hvx | **COMPLETE** | [media.md](media.md) | 3 Gold msgs, 1 retraction (MediaEventIdWrapper) |
| 1b | Media AV Stream | CAR.GAL.MEDIA | qnf/icv | **COMPLETE** | [media.md](media.md) | 3 Gold msgs (wbs/vwn/vuw), msg IDs corrected |
| 1c | Car Local Media | CAR.GAL.CAR_LOCAL_MEDIA | hyh (16.2) | **COMPLETE** | [media.md](media.md) | 3 Gold msgs, direction corrected, own PlaybackState enum |
| 2 | Navigation | CAR.INST | ian/hlj (16.2) | **COMPLETE** | [navigation.md](navigation.md) | 7 Gold msgs, 2 retractions, 1 new proto, enum fixes |
| 3 | Control (ch 0) | CAR.GAL.GAL | hzh (16.2) | **COMPLETE** | [control.md](control.md) | 18 Gold msgs, 5 Gold enums, 3 retractions, 2 relocated |
| 4 | Input | CAR.GAL.INPUT | iae/hlg (16.2) | **COMPLETE** | [input.md](input.md) | 4 Gold msgs, 8 sub-msgs, 3 enums, 3 SDP configs, 6 retractions |
| 5 | Phone | CAR.GAL.INST | iat/hll (16.2) | **COMPLETE** | [phone.md](phone.md) | 2 Gold msgs, 1 enum, 1 sub-msg, 2 relocated to control, 2 retracted |
| 6 | Video | CAR.GAL.VIDEO | ied/icv (16.2) | **COMPLETE** | [video.md](video.md) | 8 Gold msgs, 2 Gold enums, 1 enum rewrite, 2 retractions, 4 new protos |
| 7 | Audio (output) | CAR.GAL.MEDIA | qnf (extends qnp) | **COMPLETE** | [audio.md](audio.md) | Shares AV protocol with video — no audio-specific msgs |
| 8 | Audio (mic) | CAR.GAL.MIC | ict/ial | **COMPLETE** | [audio.md](audio.md) | 1 Gold msg (MicrophoneOpenResponse), 3 retractions |
| 9 | Sensor | CAR.GAL.SENSOR | ibi (16.2) | **COMPLETE** | [sensor.md](sensor.md) | 4 Gold msgs, 26 Gold sub-msgs, 4 Gold enums, 2 Gold SDP, 1 retraction |
| 10 | Bluetooth | CAR.GAL.BT / CAR.BT | TBD | PENDING | | BT pairing |

### Phase 1 — Secondary Channels

| # | Channel | GAL Tag | Handler Class | Status | Report | Notes |
|---|---------|---------|---------------|--------|--------|-------|
| 11 | Radio | CAR.RADIO | TBD | PENDING | | Service 15 |
| 12 | Car Control | CAR.GAL.CAR_CONTROL | TBD | PENDING | | HVAC, doors |
| 13 | WiFi Projection | CAR.GAL.WIFI_PROJ | TBD | PENDING | | WiFi upgrade |
| 14 | Vendor Extension | CAR.VENDOR | TBD | PENDING | | Vendor passthrough |
| 15 | Diagnostics | CAR.GAL.DIAGNOSTICS | TBD | PENDING | | |

## Resume Pointer

**Next action:** Begin Bluetooth (#10) or Radio (#11) channel verification. Radio partially verified via audio pass — directions fixed, 16.2 class refs updated, RadioSearchRequest (0x8023) added. Full radio sub-message schema verification still needed.

## Completed — Sensor Channel (Wave 8)

### CAR.GAL.SENSOR (ibi.java, GAL type 7)

| Proto | Wire ID | Direction | 16.2 Class | Confidence | Result |
|-------|---------|-----------|------------|------------|--------|
| SensorRequest | 0x8001 | HU→Phone | wbh | Gold | Correct, updated 16.2 class |
| SensorStartResponse | 0x8002 | Phone→HU | wbi | Gold | optional→required on status field |
| SensorEventIndication | 0x8003 | Phone→HU | wbe | Gold | MAJOR FIX: fields 21-26 had wrong sub-message types |
| SensorError | 0x8004 | Phone→HU | wbf | Gold | Correct, updated 16.2 class |

### Sub-Messages (26 sensor data types, all Gold)

All 26 sensor data sub-messages verified against 16.2 DB. Key fixes:
- 9 fields changed optional→required (GPSLocation lat/lon, Compass bearing, Speed, RPM, Odometer, ParkingBrake, Gear, DrivingStatus)
- GpsSatelliteInfo filled with 5 fields from vxd (was empty placeholder)
- GearEnum syntax proto3→proto2 (closed enum)
- SensorEventIndication fields 21-26 type names completely wrong — replaced with correct types

### Enums (4 Gold, 2 Silver)

| Enum | 16.2 Class | Confidence |
|------|------------|------------|
| SensorType (26 values) | wbl | Gold |
| SensorErrorStatus (3 values) | wbg | Gold |
| Gear (14 values) | vxb closed | Gold |
| FuelType (13 values) | vxa | Gold |
| EVConnectorType (12 values) | vwx | Gold |
| HeadlightStatus (placeholder) | — | Silver |
| IndicatorStatus (placeholder) | — | Silver |

### SDP Config (2 Gold)

| Proto | 16.2 Class | Confidence |
|-------|------------|------------|
| SensorChannelConfig | wbk | Gold |
| SensorTypeEntry | wbj | Gold |

### Retracted

| Proto | Reason |
|-------|--------|
| SensorStartRequestMessage | Duplicate of SensorRequestMessage (wrong field modifiers: optional/uint64 vs required/int64) |

### SensorEventIndication Fields 21-26 — CORRECTED

| Field | Was (WRONG) | Now (CORRECT) | 16.2 Class |
|-------|------------|---------------|------------|
| 21 | TollRoad | GpsSatelliteData | vxe |
| 22 | RangeRemaining | TollCardData | wbx |
| 23 | FuelTypeInfo | VehicleEnergyModelData | vus |
| 24 | EVBatteryInfo | TrailerData | wca |
| 25 | EVChargeInfo | RawVehicleEnergyModel | wax |
| 26 | EVChargeStatus | RawEvTripSettings | wav |

Inline message definitions (TollRoad, TollRoadInfo, RangeRemaining, FuelTypeInfo, EVBatteryInfo, EVChargeInfo, EVChargeInfoData, EVChargeStatus, EVChargeStatusData) removed — replaced by imports of correct standalone proto files.

## Completed — Audio Channel (Wave 7)

### Audio AV Output (qnf.java, CAR.GAL.MEDIA)

Uses exact same AV protocol as video (wbs/vwn/vuw). No audio-specific wire messages. **Gold by inheritance.**

### Mic Input (ict/ial, CAR.GAL.MIC)

| Proto | Wire ID | Direction | 16.2 Class | Confidence | Result |
|-------|---------|-----------|------------|------------|--------|
| MicrophoneOpenResponse | 0x8006 | HU→Phone | vyj | Gold | NEW — 2 fields (status, session_config) |

Raw audio: wire 0x0000 (HU→Phone), wire 0x0001 (Phone→HU). No proto, raw PCM with 8-byte timestamp.

### Retracted (from oaa/audio/)

| Proto | Reason | Actually Is |
|-------|--------|-------------|
| AudioFocusStateMessage (waq) | Wrong channel, wrong name | RadioFavoriteToggleRequest (0x8021 on radio ch 15) |
| AudioStreamTypeMessage (war) | Wrong channel, wrong name | RadioTuneDirectionRequest (0x8022 on radio ch 15) |
| AudioStreamTypeEnum | Wrong semantics | RadioTuneDirection (UP=1, DOWN=2, not MEDIA/GUIDANCE) |

### Radio Channel Fixes (bonus from audio trace)

- All 10 message directions CORRECTED (were swapped)
- 16.2 class references added for all messages
- RadioSearchRequest (0x8023, wac) added — NEW in 16.2
- ibf extends iav directly — NO +1 msg ID offset (unlike video/audio AV channels)

### AdditionalVideoConfig Field 6 — RESOLVED

Deferred from video pass. ResizeActionType enum values (0-2) unchanged in 16.2. Only obfuscated validator class name changed (vvn→vve/vuz). No proto changes needed.

## Completed — Video Channel (Wave 6)

### CAR.GAL.VIDEO (Video Sink, ied.java / icv.java)

| Proto | Msg ID | Direction | 16.2 Class | Confidence | Result |
|-------|--------|-----------|------------|------------|--------|
| VideoFocusRequest | 0x8007 | HU→Phone | wct | Gold | Updated class refs |
| VideoFocusIndication | 0x8008 | Phone→HU | wcr | Gold | Confirmed correct |
| UpdateUiConfigRequest | 0x8009/0x800A | Bidirectional | wci | Gold | NEW — runtime UI config |
| IntegratedOverlayStartNotification | 0x800E | Phone→HU | vxq | Gold | NEW — was wrongly VideoFocusNotification |
| IntegratedOverlayStopNotification | 0x800F | Phone→HU | — | Gold | NEW — empty message |
| UiConfigRequest | 0x8011 | HU→Phone | wcj | Gold | Fixed class refs, added UiConfigValue field |
| UpdateHuUiConfigResponse | 0x8012 | Phone→HU | wck | Gold | NEW — was wrongly VideoFocusModeMessage |
| AVChannelMediaStats | 0x8013 | HU→Phone | vyg | Gold | Fixed wire ID (was 0x8014), updated class refs |

### Enums (all Gold)

| Enum | 16.2 Class | Values |
|------|------------|--------|
| VideoFocusMode | wcq | 4 values (1-4), NONE=0 is proto3 default only |
| VideoFocusReason | wcs | 5 values (0-4) |
| ThemingTokensStatus | — | 3 values (0-2: Error/Accepted/Rejected) |
| VideoResolution | wco | 9 values (1-9) — FULL REWRITE, values 5-9 changed |

### New Protos

| Proto | Msg ID | Direction | 16.2 Class | Notes |
|-------|--------|-----------|------------|-------|
| IntegratedOverlayStartNotification | 0x800E | Phone→HU | vxq | 1 field (int32 display_session_id) |
| IntegratedOverlayStopNotification | 0x800F | Phone→HU | — | Empty message |
| UpdateHuUiConfigResponse | 0x8012 | Phone→HU | wck | 1 field (ThemingTokensStatus enum) |
| UpdateUiConfigRequest | 0x8009/0x800A | Bidirectional | wci | Wraps AdditionalVideoConfig |
| AVChannelMediaOptions | 0x8014 | Phone→HU | vya | Silver — 13 fields, placeholder |

### Retracted

| Proto | Reason | Replacement |
|-------|--------|-------------|
| VideoFocusNotification | Actually IntegratedOverlayStartNotification | IntegratedOverlayStartNotification.proto |
| VideoFocusModeMessage | Actually UpdateHuUiConfigResponse | UpdateHuUiConfigResponse.proto |

### SDP Data Fixes

| Item | Change |
|------|--------|
| VideoResolution enum | Full rewrite — 9 values, explicit resolution naming, values 5-9 changed from aasdk |
| AdditionalVideoConfig field 6 | Enum validator changed (vvf in 16.2) — deferred to audio pass |

## Completed — Phone Channel (Wave 5)

### CAR.GAL.INST (Phone Status, GAL type 13)

| Proto | Msg ID | Direction | 16.2 Class | Confidence | Result |
|-------|--------|-----------|------------|------------|--------|
| PhoneStatusUpdate | 0x8001 | Phone->HU | vzr | Gold | Fixed direction (was HU->Phone), PhoneCall fields 1-2 optional→required |
| PhoneStatusInput | 0x8002 | HU->Phone | vzs | Gold | Fixed direction (was Phone->HU), updated 16.2 class refs |

### Sub-messages & Enums (all Gold)

| Item | 16.2 Class | Fields/Values |
|------|------------|---------------|
| PhoneCall | vzp | 6 fields (2 required, 4 optional) |
| PhoneCallState enum | vzq | 7 values (0-6: UNKNOWN through MUTED) |
| PhoneInputType | vxo | 1 field (enum) |
| PhoneInputAction enum | — | 8 values (0-7: UNKNOWN through CALL) |

### Relocated to Control Channel

| Proto | Old Location | Correct Channel | Msg ID | Direction | 16.2 Class |
|-------|-------------|----------------|--------|-----------|------------|
| CallAvailabilityStatus | oaa/phone/ | Control (GAL 1) | 24 | HU->Phone | vvt |
| VoiceSessionRequest | oaa/phone/ | Control (GAL 1) | 17 | Phone->HU | wcu |

### Retracted/Removed

| Proto | Reason |
|-------|--------|
| PhoneStatusChannelData | Empty marker, no fields — removed (SDP ChannelDescriptor field 10 has no config) |
| CallAvailabilityMessage (from phone) | Relocated to control channel |
| VoiceSessionRequestMessage (from phone) | Relocated to control channel |

## Completed — Navigation Channel (Wave 2)

### CAR.INST (Navigation/Instrument Cluster, GAL type 10)

| Proto | Msg ID | Direction | 16.2 Class | Confidence | Result |
|-------|--------|-----------|------------|------------|--------|
| InstrumentClusterStart | 0x8001 | HU->Phone | vze | Gold | Fixed direction (was Phone->HU), fixed syntax (proto2) |
| InstrumentClusterStop | 0x8002 | HU->Phone | vzf | Gold | Fixed direction (was Phone->HU), fixed syntax (proto2) |
| NavigationState | 0x8003 | Phone->HU | vzb | Gold | Fixed enum: UNKNOWN→UNAVAILABLE, ENDED→REROUTING |
| NavigationTurnEvent | 0x8004 | — | vzm (16.1) | Deprecated | Removed in 16.2. vzm reassigned to overlay param |
| LegacyNavigationTurnEvent | 0x8005 | Phone->HU | vyx | Gold | NEW identity — was wrongly InstrumentClusterInput (vzl) |
| NavigationNotification | 0x8006 | Phone->HU | vza | Gold | All 8 sub-msgs verified, 16.2 class refs updated |
| NavigationNextTurnDistanceEvent | 0x8007 | Phone->HU | vyp | Gold | Already verified (wire capture 2026-03-04) |
| VehicleEnergyForecast | 0x8008 | Phone->HU | waw | Gold | NEW — EV energy forecast, PDK >= 5.1 |

### NavigationNotification Sub-messages (all Gold)

| Sub-message | 16.2 Class | 16.1 Class | Fields |
|-------------|------------|------------|--------|
| NavigationStep | vzg | vzu | 4 |
| NavigationManeuver | vyw | vzk | 3 |
| NavigationText | vyz | vzn | 1 |
| NavigationLane | vyv | vzj | 1 |
| NavigationLaneDirection | vyu | vzi | 2 |
| NavigationRoadInfo | vyo | vzc | 1 |
| NavigationDestination | vyq | vze | 2 |
| ChargingStationDetails | vwl | vwz | 3 |

### VehicleEnergyForecast Sub-messages (all Gold)

| Sub-message | 16.2 Class | Fields |
|-------------|------------|--------|
| VehicleEnergyForecast (inner) | ysl | 6 |
| EnergyAtDistance | ysh | 3 (field 3 reserved) |
| EnergyChargingStationDetails | ysf | 3 |
| StopDetails | ysk | 2 |
| DataAuthorization | ysg | 1 |
| ForecastQuality enum | — | 3 values (0-2) |

### Retracted/Corrected Protos

| Proto | Reason | Actually Is |
|-------|--------|-------------|
| InstrumentClusterInput (vzl, 0x8005) | Wrong class | vzl = display OverlayParameters. Actual 0x8005 = vyx (LegacyNavigationTurnEvent) |
| NavigationFocusIndication (wbg) | Doesn't exist | wbg in 16.2 = SensorStatus enum. No "indication" message in protocol |
| NavigationTurnEvent (vzm, 0x8004) | Deprecated | Removed in 16.2. vzm in 16.2 = overlay parameter (2 fields) |

### NavigationFocus — Moved to Control Channel

| Proto | Msg ID | Channel | Direction | 16.2 Class |
|-------|--------|---------|-----------|------------|
| NavigationFocusRequest | 13 | Control (GAL type 1) | Phone->HU | vyl |
| NavigationFocusResponse | 14 | Control (GAL type 1) | HU->Phone | vyk |
| NavigationFocusType enum | — | — | — | vyn (was incorrectly vzb) |

### Other Fixes

| Item | Change |
|------|--------|
| LaneShape enum | Silver → Gold |
| ManeuverType enum | Confirmed values 0-50 (gap at 30-31) |
| NavigationFocusType enum class | vzb → vyn (vzb = NavigationState in 16.2) |

## Completed — Media Channel (Wave 1)

### CAR.GAL.INST (Media Info, GAL type 11)

| Proto | Msg ID | Direction | 16.2 Class | Confidence | Result |
|-------|--------|-----------|------------|------------|--------|
| MediaPlaybackStatus | 0x8001 | Phone->HU | vyc | Gold | Correct |
| MediaPlaybackStatusEvent | 0x8002 | HU->Phone | vxo | Gold | NEW — discovered during verification |
| MediaPlaybackMetadata | 0x8003 | Phone->HU | vyb | Gold | Fixed 3 field errors, syntax proto3->proto2 |
| MediaEventIdWrapper | — | — | xme | Retracted | Not wire protocol — internal MediaBrowserService |

### CAR.GAL.MEDIA (AV Stream, all AV channels)

| Proto | Wire ID | Direction | 16.2 Class | Confidence | Result |
|-------|---------|-----------|------------|------------|--------|
| AVChannelSetupRequest | 0x8000 | Phone->HU | wbs | Gold | Fixed optional->required, renamed field |
| AVChannelStartIndication | 0x8001 | Bidirectional | wbu | Gold | Fixed optional->required (fields 1,2) |
| AVChannelStopIndication | 0x8002 | Phone->HU | wbv | Gold | Confirmed empty, fixed syntax proto3->proto2 |
| AVChannelSetupResponse | 0x8003 | Bidirectional | vwn | Gold | Fixed optional->required, corrected msg ID |
| AVMediaAckIndication | 0x8004 | HU->Phone | vuw | Gold | Fixed optional->required, renamed fields |
| Signal/heartbeat | 0x800B | HU->Phone | — | — | No proto (raw signal) |

**CRITICAL FIX:** All AV msg IDs were off by one due to `vdp.m36513at()` adding +1 for internal dispatch. Previous docs had 0x8004/0x8005/0x800C, corrected to 0x8003/0x8004/0x800B.

### CAR_LOCAL_MEDIA (GAL type 20)

| Proto | Msg ID | Direction | 16.2 Class | Confidence | Result |
|-------|--------|-----------|------------|------------|--------|
| CarLocalMediaPlaybackStatus | 0x8001 | HU->Phone | vwe | Gold | Fixed direction, fixed PlaybackState enum |
| CarLocalMediaPlaybackMetadata | 0x8002 | HU->Phone | vwc | Gold | Fixed direction, updated class refs |
| CarLocalMediaPlaybackRequest | 0x8003 | Phone->HU | vwd | Gold | Updated class refs |
| CarLocalMediaPlaybackEnum | — | — | vwb | Superseded | Redundant with enum in status proto |

**CRITICAL FIX:** Direction reversed — status/metadata are HU->Phone (car tells phone what local media is playing), not Phone->HU. CarLocal PlaybackState is its own enum (values 1-5), NOT shared with MediaPlaybackStatus (values 0-4).

### All Retracted Protos

| Proto | Reason | Actually Is |
|-------|--------|-------------|
| MediaStatusList (vyd) | Wrong class mapping | 16.1: IntegratedOverlayParametersNotification (video 0x800D). 16.2: MediaInfoChannel (ChannelDescriptor field 9) |
| MediaTrackIdentifier (xma/xll) | Not wire protocol | Internal MediaBrowserService queue structure (oui -> xlm -> xll) |
| MediaEventIdWrapper (xme) | Not wire protocol | Internal MediaBrowserService structure, never in any GAL handler |
| CarLocalMediaPlaybackEnum | Redundant | Superseded by enum in CarLocalMediaPlaybackStatusMessage.proto |
| InstrumentClusterInput (vzl) | Wrong class | vzl = display OverlayParameters, not a nav channel message |
| NavigationFocusIndication (wbg) | Doesn't exist | wbg = SensorStatus enum in 16.2 |
| PhoneStatusChannelData | Empty marker | No config fields, removed |
| CallAvailabilityStatus (from phone) | Wrong channel | Control channel msg 24, relocated to oaa/control/ |
| VoiceSessionRequest (from phone) | Wrong channel | Control channel msg 17, relocated to oaa/control/ |

## Running Discoveries

1. **AV msg ID off-by-one:** `vdp.m36513at()` adds +1 for internal dispatch. Wire values are 1 less than what the handler switch cases show. BUT this does NOT apply to CAR_LOCAL_MEDIA — `iav.mo20009T()` reads wire IDs directly. Also does NOT apply to nav channel (`ian`) which uses raw msg IDs.

2. **CAR.GAL.MEDIA vs CAR.GAL.INST confusion:** `CAR.GAL.MEDIA` (qnf) is the AV audio stream endpoint. Media status/metadata lives on `CAR.GAL.INST` (iai/hvx, GAL type 11).

3. **0x8002 exists on INST channel:** MediaPlaybackStatusEvent (vxo), HU->Phone input action.

4. **AV channels share msg ID patterns:** qnf (audio) and icv/ied (video) use the same message IDs and proto classes. vwn/vuw are shared across all AV channels.

5. **GMS proxy strips fields:** `pre.java` hardcodes metadata field 5=null, field 7=0, status repeat/repeat_one=false.

6. **Obfuscated name reuse across versions:** Same class name (e.g., vyd, xma, vwq, vzm) can refer to completely different protos in different APK versions. Always verify by structure AND handler context, not just name. vzm=NavigationTurnEvent in 16.1, overlay param in 16.2.

7. **CarLocal direction is reversed:** Status/metadata are HU->Phone (car reports local media), request is Phone->HU. The +1 msg ID offset does NOT apply to this channel.

8. **NavigationFocus is on control channel (GAL type 1):** NOT on nav channel (GAL type 10). Msg IDs 13 (request) and 14 (response) on hzh.java. VoiceFocusRequest (msg 17, wcu) also discovered on control channel.

9. **Nav channel has legacy/modern split:** HUs with CarInfo PDK < 1.6 get legacy msgs (0x8005 vyx). Modern HUs get 0x8006/0x8007. VehicleEnergyForecast (0x8008) requires PDK >= 5.1.

10. **Double-encoding pattern:** VehicleEnergyForecast uses proto2 wrapper (waw) containing serialized proto3 inner message (ysl). Watch for this in other channels.
