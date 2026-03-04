# 01 — Transport Setup

## Proto Confidence Summary

| Message | Tier | Evidence | Audit File |
|---------|------|----------|------------|
| WifiStartResponse | Silver | apk_static + cross_version | [WifiStartResponseMessage.audit.yaml](../../oaa/wifi/WifiStartResponseMessage.audit.yaml) |
| WifiInfoRequest | Bronze | apk_static | [WifiInfoRequestMessage.audit.yaml](../../oaa/wifi/WifiInfoRequestMessage.audit.yaml) |
| WifiInfoResponse | Silver | apk_static + cross_version | [WifiInfoResponseMessage.audit.yaml](../../oaa/wifi/WifiInfoResponseMessage.audit.yaml) |
| WifiSecurityRequest | Unverified | -- | -- |
| WifiSecurityResponse | Silver | apk_static + cross_version | [WifiSecurityResponseMessage.audit.yaml](../../oaa/wifi/WifiSecurityResponseMessage.audit.yaml) |
| WifiConnectStatus | Silver | apk_static + cross_version | [WifiConnectStatusMessage.audit.yaml](../../oaa/wifi/WifiConnectStatusMessage.audit.yaml) |
| WifiStartRequest | Unverified | -- | -- |

## Overview

Establishing the data transport between phone and head unit. Two paths exist: wireless (BT -> RFCOMM -> WiFi -> TCP) and wired (USB AOA -> bulk endpoints). Both converge on the same upper-layer protocol at the TCP/data stream level.

## Wireless Path

The wireless path is thoroughly documented in [`wireless-bluetooth-setup.md`](../wireless-bluetooth-setup.md), including:
- SDP record registration (AA UUID `4de17a00-52cb-11e6-bdf4-0800200c9a66`)
- BlueZ configuration and UUID size compatibility issues
- HFP AG requirement (phone refuses wireless AA without it)
- RFCOMM WiFi credential exchange (5-stage handshake)
- WiFi AP configuration (hostapd, WPA2/WPA3)

### Wireless Connection Summary

> Confidence: Bronze [apk_static] -- see [WifiInfoRequestMessage.audit.yaml](../../oaa/wifi/WifiInfoRequestMessage.audit.yaml)
>
> Lowest tier in this section: Bronze (WifiInfoRequest has only apk_static evidence; other messages are Silver)

```
Phone                              Head Unit
  |                                   |
  |--- BT Pair (DisplayYesNo) ------> |
  |--- SDP Service Search ----------> |  Returns AA UUID record
  |--- HFP AG Connect -------------> |  Must accept and hold fd
  |--- RFCOMM Connect (ch 8) ------> |
  |                                   |
  |<-- WifiStartRequest (msgId=1) -- |  ip + port (e.g. 10.0.0.1:5288)
  |--- WifiStartResponse (msgId=7) > |  status=SUCCESS
  |--- WifiInfoRequest (msgId=2) --> |  empty or cached
  |<-- WifiInfoResponse (msgId=3) -- |  SSID, key, BSSID, security, AP type
  |                                   |
  |... phone joins WiFi AP ...        |
  |                                   |
  |--- WifiConnectStatus (msgId=6) > |  status=0 (SUCCESS)
  |--- TCP connect to ip:port -----> |  AA protocol begins
```

### RFCOMM Packet Format

```
[length:uint16_be] [msg_id:uint16_be] [protobuf_payload]
```

### Timing (Observed)

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

> **Gotcha:** The manufacturer string (index 0) must be exactly `"Android"` -- case-sensitive. Some implementations use `"android"` or the HU's actual brand name, which causes the phone to reject the AOA identification silently. The PID changes after re-enumeration (from the device's native PID to `0x2D00`/`0x2D01`), so the HU must re-open the USB device after sending the accessory start control transfer.

After identification, the phone re-enumerates as a Google accessory:
- VID: `0x18D1` (Google)
- PID: `0x2D00` (accessory) or `0x2D01` (accessory + ADB)

### USB Bulk Endpoints

Data flows over two USB bulk endpoints (IN and OUT). The framing layer above is identical to the TCP path.

### Implementation Guidance -- USB AOA Setup

```c
#include <libusb-1.0/libusb.h>

// AOA identification strings
static const char *aoa_strings[] = {
    "Android",       // 0: manufacturer (MUST be exactly "Android")
    "Android Auto",  // 1: model
    "HU Description",// 2: description
    "1.0",           // 3: version
    "",              // 4: URI
    ""               // 5: serial
};

int setup_aoa(libusb_device_handle *dev) {
    // Step 1: Check AOA protocol version
    uint8_t aoa_version[2];
    int ret = libusb_control_transfer(dev,
        LIBUSB_ENDPOINT_IN | LIBUSB_REQUEST_TYPE_VENDOR,
        51,   // AOA_GET_PROTOCOL
        0, 0, aoa_version, 2, 1000);
    if (ret < 0 || (aoa_version[0] | aoa_version[1] << 8) < 1)
        return -1;  // AOA not supported

    // Step 2: Send identification strings (indices 0-5)
    for (int i = 0; i < 6; i++) {
        ret = libusb_control_transfer(dev,
            LIBUSB_ENDPOINT_OUT | LIBUSB_REQUEST_TYPE_VENDOR,
            52,  // AOA_SEND_STRING
            0, i,
            (uint8_t *)aoa_strings[i],
            strlen(aoa_strings[i]) + 1,  // include null terminator
            1000);
        if (ret < 0) return -1;
    }

    // Step 3: Start accessory mode
    ret = libusb_control_transfer(dev,
        LIBUSB_ENDPOINT_OUT | LIBUSB_REQUEST_TYPE_VENDOR,
        53,  // AOA_START_ACCESSORY
        0, 0, NULL, 0, 1000);
    if (ret < 0) return -1;

    // Step 4: Device re-enumerates -- close handle, wait, re-open
    libusb_close(dev);
    // Wait ~1s for re-enumeration, then find device with:
    //   VID=0x18D1, PID=0x2D00 (accessory) or 0x2D01 (accessory+ADB)
    // Claim interface 0, find bulk IN and OUT endpoints
    return 0;
}
```

## Postcondition

At the end of this phase:
- A bidirectional byte stream exists between phone and HU (TCP socket or USB bulk endpoints)
- No encryption, no authentication -- raw bytes
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

- [`wireless-bluetooth-setup.md`](../wireless-bluetooth-setup.md) -- full BT/WiFi setup guide with error solutions
- [`phone-side-debug.md`](../phone-side-debug.md) -- captured session timeline (phases 1-4)
- `oaa/wifi/WifiStartRequestMessage.proto`
- `oaa/wifi/WifiSecurityRequestMessage.proto`
