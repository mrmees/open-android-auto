# VW vs DHU SDP Divergence Report

Generated: 2026-04-09
VW capture: `captures/oem-vw-mib3oi-2026-04-06/`
VW AA version: `2756.04`

## 1. Summary

- Total divergences: **3**
- By attribution: {"ambiguous": 1, "oem": 2, "version": 0}
- By service: {"bluetooth_channel": 1, "vendor_extension_channel": 1, "wifi_channel": 1}

## 2. Version-attributed divergences

_(none)_

## 3. OEM-attributed divergences

### bluetooth_channel (service_only_in_vw)

- Attribution: **oem**
- Reason: Not listed in Phase 8 16-4-delta-report.new_in_16_4. Present in VW SDP but absent from all DHU baselines — attributed to OEM divergence.

### wifi_channel (service_only_in_vw)

- Attribution: **oem**
- Reason: Not listed in Phase 8 16-4-delta-report.new_in_16_4. Present in VW SDP but absent from all DHU baselines — attributed to OEM divergence.


## 4. Ambiguous divergences

### vendor_extension_channel (service_only_in_dhu)

- Attribution: **ambiguous**
- Reason: Present in DHU but not VW; not listed in Phase 8 removed_in_16_4. Could be DHU test harness infrastructure or a version change not captured in the delta report.
- Baselines matched: ['active-navigation', 'general', 'idle-baseline', 'music-playback']


## 5. Services in VW but not DHU

- `bluetooth_channel`
- `wifi_channel`

## 6. Services in DHU but not VW

- `vendor_extension_channel`

## 7. Per-baseline observation summary

- **active-navigation**: 14 channels, 8 distinct kinds
- **general**: 14 channels, 8 distinct kinds
- **idle-baseline**: 14 channels, 8 distinct kinds
- **music-playback**: 14 channels, 8 distinct kinds

## 8. Baseline reproduction

```bash
PYTHONPATH=. python3 -m analysis.tools.dhu_divergence.run --vw-sdp-json analysis/reports/oem-vw/sdp-values.json --dhu captures/general --dhu captures/idle-baseline --dhu captures/music-playback --dhu captures/active-navigation --delta-report analysis/reports/cross-version/16-4-delta-report.json --out analysis/reports/oem-vw/
```

**Run date:** 2026-04-09

### DHU baselines

- `general`: `captures/general/sdp_response.bin` — sha256 `a4f2bc3465b00efd6d2b3c420578272fb275d310b6c13c99a7d0ed42f90ee704`
- `idle-baseline`: `captures/idle-baseline/sdp_response.bin` — sha256 `a4f2bc3465b00efd6d2b3c420578272fb275d310b6c13c99a7d0ed42f90ee704`
- `music-playback`: `captures/music-playback/sdp_response.bin` — sha256 `a4f2bc3465b00efd6d2b3c420578272fb275d310b6c13c99a7d0ed42f90ee704`
- `active-navigation`: `captures/active-navigation/sdp_response.bin` — sha256 `a4f2bc3465b00efd6d2b3c420578272fb275d310b6c13c99a7d0ed42f90ee704`

**Phase 8 delta report sha256:** `b4a46158dc22686c1b5543b1cc3e2da0d0c2d5e72e9f96ff8358e19eabcb74ce`
