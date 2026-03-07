# Control Channel Verification Report

**Channel:** Control (ch 0, GAL type 1)
**Handler:** `hzh.java` (16.2), tag `CAR.GAL.GAL`
**Date:** 2026-03-06
**Status:** COMPLETE

## Handler Message Table (Ground Truth)

### Messages Received by Phone (hzh.mo18864a)

| Msg ID | Proto Class | Message | Direction |
|--------|-------------|---------|-----------|
| 1 | raw bytes | VERSION_REQUEST | HU→Phone |
| 3 | raw SSL | SSL_HANDSHAKE | Bidirectional |
| 4 | vvh | AUTH_COMPLETE | HU→Phone |
| 6 | wbo | SERVICE_DISCOVERY_RESPONSE | HU→Phone |
| 11 | vzv | PING_REQUEST | Bidirectional |
| 12 | vzw | PING_RESPONSE | Bidirectional |
| 14 | vyk | NAV_FOCUS_RESPONSE | HU→Phone |
| 15 | vvr | SHUTDOWN_REQUEST (ByeByeRequest) | Bidirectional |
| 16 | vvs | SHUTDOWN_RESPONSE (ByeByeResponse) | Bidirectional |
| 19 | vvc | AUDIO_FOCUS_RESPONSE | HU→Phone |
| 24 | vvt | CALL_AVAILABILITY_STATUS | HU→Phone |
| 26 | wbp | SERVICE_DISCOVERY_UPDATE | HU→Phone |

### Messages Sent by Phone

| Msg ID | Proto Class | Message | Sender |
|--------|-------------|---------|--------|
| 2 | raw + wcn | VERSION_RESPONSE | hzh inline |
| 5 | wbn | SERVICE_DISCOVERY_REQUEST | iod.java |
| 7 | vwj | CHANNEL_OPEN_REQUEST | hyr.java |
| 11 | vzv | PING_REQUEST | hzh.mo20032d |
| 12 | vzw | PING_RESPONSE | hzh.mo20033e |
| 15 | vvr | SHUTDOWN_REQUEST | hzh.mo20031c |
| 16 | vvs | SHUTDOWN_RESPONSE | hzh case 15 |
| 17 | wcu | VOICE_SESSION_REQUEST | hzh.mo20034f |
| 18 | vvd | AUDIO_FOCUS_REQUEST | hrc.java |
| 23 | vvi | BATTERY_STATUS_NOTIFICATION | hna.java |

### Enum-Only (No Implementation in 16.2)

| Msg ID | Message | Status |
|--------|---------|--------|
| 20 | CAR_CONNECTED_DEVICES_REQUEST | Bronze (enum only) |
| 21 | CAR_CONNECTED_DEVICES_RESPONSE | Bronze (enum only) |
| 22 | USER_SWITCH_REQUEST | Bronze (enum only) |
| 25 | USER_SWITCH_RESPONSE | Bronze (enum only) |

## Per-Proto Results

### Gold Verified

| Proto | Msg ID | Direction | 16.2 Class | Changes Made |
|-------|--------|-----------|------------|--------------|
| AuthCompleteIndication | 4 | HU→Phone | vvh | `optional`→`required` |
| PingRequest | 11 | Bidirectional | vzv | `optional`→`required`, field 2 `int32`→`bool bugreport_request`, added field 3 `bytes payload` |
| PingResponse | 12 | Bidirectional | vzw | `optional`→`required`, added field 2 `bytes payload` |
| ShutdownRequest | 15 | Bidirectional | vvr | `optional`→`required` |
| ByeByeResponse | 16 | Bidirectional | vvs | Promoted (was bronze) |
| VoiceSessionRequest | 17 | Phone→HU | wcu | No changes (already correct) |
| AudioFocusRequest | 18 | Phone→HU | vvd | No changes to proto (file in oaa/audio/) |
| AudioFocusResponse | 19 | HU→Phone | vvc | `optional`→`required` field 1 |
| CallAvailabilityStatus | 24 | HU→Phone | vvt | No changes (already correct, in oaa/phone/) |
| BatteryStatusNotification | 23 | Phone→HU | vvi | `proto3`→`proto2` |
| ServiceDiscoveryRequest | 5 | Phone→HU | wbn | No changes |
| ServiceDiscoveryResponse | 6 | HU→Phone | wbo | No changes (top-level) |
| ServiceDiscoveryUpdate | 26 | HU→Phone | wbp | No changes |
| ChannelOpenRequest | 7 | Phone→HU | vwj | `optional`→`required` both fields |
| ChannelOpenResponse | 8 | HU→Phone | vwk | `optional`→`required` |
| NavigationFocusRequest | 13 | Phone→HU | vyl | Already Gold (nav verification) |
| NavigationFocusResponse | 14 | HU→Phone | vyk | Already Gold (nav verification) |
| HeadUnitInfo (sub-msg) | — | — | vuq | Added field 9 (vehicle_type), `proto3`→`proto2` |

### Gold Enums

| Enum | 16.2 Class | Changes Made |
|------|------------|--------------|
| ProtocolStatus (was VersionResponseStatus) | vyh | Complete rewrite — 2 values → 34 values |
| ShutdownReason | vvq | Removed synthetic `NONE=0`, `proto3`→`proto2` |
| AudioFocusType | vvf | Renamed `GAIN_NAVI`→`GAIN_TRANSIENT_MAY_DUCK` |
| AudioFocusState | vvg | Renamed `NONE`→`INVALID` |
| NavigationFocusType | vyn | Already Gold |

### Retracted

| Proto | Reason |
|-------|--------|
| GalPingRequest | Duplicate of PingRequest (same msg 11, same class vzv) |
| GalPingResponse | Duplicate of PingResponse (same msg 12, same class vzw) |
| ShutdownResponse | Duplicate of ByeByeResponse (same msg 16, wrong proto3 syntax) |

### Relocated (Wrong Channel)

| Proto | Was | Should Be | Notes |
|-------|-----|-----------|-------|
| BindingRequest | oaa/control/ | oaa/input/ (msg 0x8002) | Actually KeyBindingRequest, class vxr. wbw audit mapping was WRONG (wbw=tire pressure) |
| BindingResponse | oaa/control/ | oaa/input/ (msg 0x8003) | Actually KeyBindingResponse, class vxs. vvn audit mapping was WRONG (vvn=BT pairing response) |

### Unverified / Possibly Removed

| Proto | Status | Notes |
|-------|--------|-------|
| ControlChannelConfigMessage | Unverified | 16.1 class wcx = WifiProjectionData in 16.2 |
| ControlChannelConfigData | Unverified | 16.1 classes vxc/wai = different protos in 16.2 |
| ConnectedDevicesMessages | Bronze | Msg IDs in enum but zero implementation code in 16.2 |

## Key Discoveries

1. **ProtocolStatus is universal:** `vyh` has 34 values covering auth, BT, radio, sensors, car properties — NOT just version response. Renamed from VersionResponseStatus.

2. **GalPing = Ping:** Same wire message. Confusion from obfuscated name reuse (waj/wak = ping in 16.1, radio in 16.2).

3. **PingRequest field 2 = bugreport trigger:** Not generic "ping_flags" — bool that triggers BugreporterReceiver via iau.m20103e.

4. **BindingRequest/Response are INPUT channel messages:** Located in oaa/control/ by mistake. BindingResponse audit yaml mapped to vvn which is actually BluetoothPairingResponse on BT channel.

5. **ControlChannelConfig restructured:** The three-layer nesting (wcx→vxc→wai) from 16.1 has different class assignments in 16.2. wcn (ControlChannelConfigWrapper) is now appended to VERSION_RESPONSE when protocol >= 1.6.

6. **ConnectedDevices/UserSwitch unimplemented:** Msg IDs 20/21/22/25 exist in the enum but have zero handler code in the 16.2 phone APK.
