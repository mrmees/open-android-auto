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
| 1 | string | f75249b | **Passphrase** — DB column "wifipassword" (ijx.java:41) |
| 2 | enum (0-11) | f75250c | Security mode (12 sequential values, validator `C0000a.m129bx`) |
| 3 | string | f75251d | **SSID** — DB column "wifissid" (ijx.java:39) |
| 5 | enum (0-1) | f75252e | Status (0=success, 1=failure; validator `C0000a.m91bL`) |

**Handler logic:**
- Parses wcw proto from ByteBuffer
- Extracts passphrase (field 1), SSID (field 3), security mode (field 2), status (field 5)
- NOTE: field ordering is unusual (passphrase=1, ssid=3) — confirmed by ijx.java DB column names
- If status == 1 (failure) or security mode == 0 (unknown), returns without storing
- Otherwise stores credentials in `CarInfoInternal` and triggers WiFi connection via executor

**Security mode enum (field 2):** Accepts values 0-11 sequentially (validator `C0000a.m129bx`). Same 12 security modes as `wdh.java` enum (UNKNOWN_SECURITY_MODE through WPA2_WPA3_PERSONAL), but re-indexed sequentially instead of using `wdh`'s non-sequential values (0,1,2,3,4,8,12,20,24,28,32,40). Stored as raw int in DB column "wifisecurity".

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
