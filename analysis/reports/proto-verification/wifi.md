# WiFi Projection Channel Verification Report

**Channel:** WiFi Projection (#13)
**GAL Tag:** `CAR.GAL.WIFI_PROJ`
**Handler Class:** `ibr.java` (16.2), extends `iav`, service type 17
**Manager Class:** `hmf.java` (16.2), implements `ibq`, tag `CAR.WIFI_PROJ`
**Verified:** 2026-03-07
**Status:** COMPLETE

## Architecture

WiFi Projection is a minimal GAL channel used to deliver WiFi credentials from the HU to the phone so the phone can switch from USB/BT to a WiFi connection. The phone-side handler only **receives** — it does not send any messages on this channel.

### Important Distinction: GAL vs BT RFCOMM

Most existing WiFi protos in `oaa/wifi/` are **BT RFCOMM setup messages**, NOT GAL wire messages:

| Transport | Dispatcher | Messages |
|-----------|-----------|----------|
| **BT RFCOMM** | `ngh.java` (ordinal dispatch) | WifiStartRequest/Response, WifiInfoRequest/Response, WifiVersionRequest/Response, WifiConnectStatus, WifiPingRequest/Response, WifiConnectionRejection, WifiSetupInfo |
| **GAL wire** | `ibr.java` (msg ID dispatch) | WifiCredentialsResponse (0x8002) — **only message** |

The BT RFCOMM messages handle initial WiFi setup negotiation (version handshake, credentials exchange, connection status). Once the GAL session is established, the WiFi Projection channel carries only the WifiCredentialsResponse.

## GAL Wire Messages

### Handler Message Table (ibr.java)

| Msg ID | Proto | Direction | 16.2 Class | Confidence | Notes |
|--------|-------|-----------|------------|------------|-------|
| 0x8002 | WifiCredentialsResponse | HU→Phone | wcw | Gold | Only message handled |

The handler rejects any message that isn't 0x8002 with log: `"Wrong Wifi projection message type %d"`.

### WifiCredentialsResponse (0x8002, wcw) — Gold

| Field | Type | 16.2 Member | Usage |
|-------|------|-------------|-------|
| 1 | string | f75249b | SSID (inferred from CarInfoInternal storage pattern) |
| 2 | enum (0-11) | f75250c | Security mode (12 sequential values, validator `C0000a.m129bx`) |
| 3 | string | f75251d | Passphrase (inferred from CarInfoInternal storage pattern) |
| 5 | enum (0-1) | f75252e | Status (0=success, 1=failure; validator `C0000a.m91bL`) |

**Handler logic:**
- Parses wcw proto from ByteBuffer
- Extracts SSID (field 1), passphrase (field 3), security mode (field 2), status (field 5)
- If status == 1 (failure) or security mode == 0 (unknown), returns without storing
- Otherwise stores credentials in `CarInfoInternal` and triggers WiFi connection via executor

**Security mode enum (field 2):** Accepts values 0-11 sequentially. This is a re-indexed version of the WiFi security modes (not the non-sequential WifiSecurityMode enum used in BT RFCOMM messages). Mapping: 0=UNKNOWN, 1=OPEN, 2=WEP_64, 3=WEP_128, 4=WPA_PERSONAL, 5=WPA2_PERSONAL, 6=WPA_WPA2_PERSONAL, 7=WPA_ENTERPRISE, 8=WPA2_ENTERPRISE, 9=WPA_WPA2_ENTERPRISE, 10=WPA3_PERSONAL, 11=WPA2_WPA3_PERSONAL.

**Status enum (field 5):** 0=SUCCESS (proceed to connect), 1=FAILURE (abort credential storage).

### WifiCredentialsRequest (0x8001) — Not Found

`WifiChannelMessageIdsEnum.proto` lists `CREDENTIALS_REQUEST = 0x8001` but there is no evidence of the phone sending this message. The phone-side handler (`ibr.java`) only receives. The request may be HU-initiated or may not exist in the current protocol version.

## SDP Channel Data

### WiFiProjectionChannelData (wcx, ChannelDescriptor field 14) — Gold

| Field | Type | 16.2 Member | Description |
|-------|------|-------------|-------------|
| 1 | string | f75256b | **BSSID** (NOT SSID — confirmed by hmf.java log: "Car wifi BSSID is %s") |

**Key correction:** Existing proto had field 1 named `ssid`. Handler log explicitly says "Car wifi BSSID is %s". Renamed to `bssid`.

**SDP capability check:** `hmf.mo18712a()` checks `wbmVar.f74994b & 8192` (bit 13 = ChannelDescriptor field 14 presence). If WiFi Projection data is absent, the channel handler is not created.

## Changes Applied

### New Proto
- `WifiCredentialsResponseMessage.proto` — wcw, 0x8002, HU→Phone, 4 fields (string, enum, string, enum)

### Corrections
- `WifiChannelData.proto` — field 1 renamed `ssid` → `bssid`, 16.2 class updated wdh→wcx, confidence bronze→Gold
- `WifiProjectionChannelData.proto` — RETRACTED (duplicate of WifiChannelData, same structure at same ChannelDescriptor field 14)

### BT RFCOMM Protos (unchanged)
All BT RFCOMM WiFi setup protos remain at their existing confidence levels (silver/bronze/unverified). They are not GAL wire messages and cannot be verified through handler tracing. They may be verified separately through BT RFCOMM analysis.

## Totals

| Category | Count |
|----------|-------|
| Gold messages | 1 (WifiCredentialsResponse) |
| Gold SDP | 1 (WiFiProjectionChannelData/WifiChannel) |
| Gold enums | 2 (WifiCredentialSecurityMode, WifiCredentialStatus) |
| Retractions | 1 (WiFiProjectionChannelData duplicate) |
| Schema fixes | 1 (WifiChannelData field name ssid→bssid) |
