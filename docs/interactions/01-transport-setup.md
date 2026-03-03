# 01 — Transport Setup

## Overview

Establishing the data transport between phone and head unit. Two paths exist: wireless (BT → RFCOMM → WiFi → TCP) and wired (USB AOA → bulk endpoints). Both converge on the same upper-layer protocol at the TCP/data stream level.

## Wireless Path

The wireless path is thoroughly documented in [`wireless-bluetooth-setup.md`](../wireless-bluetooth-setup.md), including:
- SDP record registration (AA UUID `4de17a00-52cb-11e6-bdf4-0800200c9a66`)
- BlueZ configuration and UUID size compatibility issues
- HFP AG requirement (phone refuses wireless AA without it)
- RFCOMM WiFi credential exchange (5-stage handshake)
- WiFi AP configuration (hostapd, WPA2/WPA3)

### Wireless Connection Summary

```
Phone                              Head Unit
  |                                   |
  |--- BT Pair (DisplayYesNo) -----→ |
  |--- SDP Service Search ----------→ |  Returns AA UUID record
  |--- HFP AG Connect -------------→ |  Must accept and hold fd
  |--- RFCOMM Connect (ch 8) ------→ |
  |                                   |
  |←-- WifiStartRequest (msgId=1) -- |  ip + port (e.g. 10.0.0.1:5288)
  |--- WifiStartResponse (msgId=7) → |  status=SUCCESS
  |--- WifiInfoRequest (msgId=2) --→ |  empty or cached
  |←-- WifiInfoResponse (msgId=3) -- |  SSID, key, BSSID, security, AP type
  |                                   |
  |... phone joins WiFi AP ...        |
  |                                   |
  |--- WifiConnectStatus (msgId=6) → |  status=0 (SUCCESS)
  |--- TCP connect to ip:port -----→ |  AA protocol begins
```

### RFCOMM Packet Format

```
[length:uint16_be] [msg_id:uint16_be] [protobuf_payload]
```

### Timing (observed)

| Event | Elapsed |
|-------|---------|
| BT pair start | t+0s |
| RFCOMM connected | t+3s |
| WiFi credentials exchanged | t+3.5s |
| WiFi connected | t+5-11s |
| TCP socket open | t+11.3s |

## Wired Path (USB AOA)

### AOA Identification

The HU acts as USB host and sends AOA identification strings:

| Index | String |
|-------|--------|
| 0 (manufacturer) | `Android` |
| 1 (model) | `Android Auto` |
| 2 (description) | (varies by HU) |
| 3 (version) | `1.0` |
| 4 (URI) | (varies by HU) |
| 5 (serial) | (varies by HU) |

After identification, the phone re-enumerates as a Google accessory:
- VID: `0x18D1` (Google)
- PID: `0x2D00` (accessory) or `0x2D01` (accessory + ADB)

### USB Bulk Endpoints

Data flows over two USB bulk endpoints (IN and OUT). The framing layer above is identical to the TCP path.

## Postcondition

At the end of this phase:
- A bidirectional byte stream exists between phone and HU (TCP socket or USB bulk endpoints)
- No encryption, no authentication — raw bytes
- The stream is ready for [version exchange](02-version-ssl-auth.md)

## Log Tags

| Tag | What it shows |
|-----|--------------|
| `GH.WIRELESS.SETUP` | Wireless state machine transitions |
| `GH.WPP.RFCOMM` | RFCOMM socket connect/IO |
| `GH.WPP.TCP` | TCP socket initialization |
| `CAR.SETUP.WIFI` | TCP socket creation to HU |
| `CAR.BT.LITE` | Bluetooth state changes |
| `CAR.CONMAN.LITE` | Connection manager |

## References

- [`wireless-bluetooth-setup.md`](../wireless-bluetooth-setup.md) — full BT/WiFi setup guide with error solutions
- [`phone-side-debug.md`](../phone-side-debug.md) — captured session timeline (phases 1-4)
- `oaa/wifi/WifiStartRequestMessage.proto`
- `oaa/wifi/WifiSecurityRequestMessage.proto`
