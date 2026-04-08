# VW Capture: Coverage Manifest

**Capture:** `captures/oem-vw-mib3oi-2026-04-06/`
**Capture duration:** 60.0s

> **Loud caveat:** This is a heuristic stack over a lossy capture format. The on-phone
> hook lives inside the AA framing layer — `channel_id`, `flags`, and frame boundaries are
> not visible. Continuation fragments inside multi-frame messages are interpreted as
> standalone records by the wire format and must be filtered by the three-tier
> plausibility gate. Real ground truth requires the framing-hook capture work tracked as
> v2 CAP-01. Residual misclassifications will be visible in aggregate stats.

## Channel Kind Summary

| channel_kind | declared | observed | silent |
|--------------|---------:|---------:|-------:|
| `av_channel` | 5 | 5 | 0 |
| `av_input_channel` | 1 | 0 | 1 |
| `bluetooth_channel` | 1 | 0 | 1 |
| `input_channel` | 1 | 0 | 1 |
| `media_info_channel` | 1 | 0 | 1 |
| `navigation_channel` | 1 | 0 | 1 |
| `phone_status_channel` | 1 | 0 | 1 |
| `sensor_channel` | 1 | 0 | 1 |
| `wifi_channel` | 1 | 0 | 1 |

_Total declared channels: 13_

## Observed services

VW declared 13 channels; traffic seen on 5, silent on 8.

| channel_id | service | msg_types observed (first 10) |
|---:|---------|--------------------|
| 1 | `av_channel` | 0x8003, 0x8061 |
| 3 | `av_channel` | 0x8003, 0x8061 |
| 4 | `av_channel` | 0x8003, 0x8061 |
| 5 | `av_channel` | 0x8003, 0x8061 |
| 6 | `av_channel` | 0x8003, 0x8061 |

## Gaps — intrinsic (VW declared, no traffic — re-capturable)

| channel_id | service | observed_count | remediation |
|---:|---------|---------------:|-------------|
| 2 | `input_channel` | 0 | re-capture with scenario exercising this service |
| 7 | `av_input_channel` | 0 | re-capture with scenario exercising this service |
| 8 | `sensor_channel` | 0 | re-capture with scenario exercising this service |
| 9 | `bluetooth_channel` | 0 | re-capture with scenario exercising this service |
| 10 | `media_info_channel` | 0 | re-capture with scenario exercising this service |
| 11 | `phone_status_channel` | 0 | re-capture with scenario exercising this service |
| 12 | `navigation_channel` | 0 | re-capture with scenario exercising this service |
| 13 | `wifi_channel` | 0 | re-capture with scenario exercising this service |

## Gaps — comparative (seen in baselines, NOT declared by VW — capability gap)

| service | seen in baselines | remediation |
|---------|-------------------|-------------|
| `vendor_extension` | active-navigation, general, idle-baseline, music-playback | not promotable from this capture; use cross-capture data |

## Anomalies (observed but unattributed — investigate)

- `service_not_declared` records: 0
- `unattributed` records: 1

### Unattributed (top 20)

| msg_type | hex | direction | count |
|---------:|-----|-----------|------:|
| 32821 | 0x8035 | out | 1 |

## Gap analysis reproducibility

- baselines: captures/general, captures/idle-baseline, captures/music-playback, captures/active-navigation
- baseline_snapshot_hash: `ffb074e4f10974cee477f77e73784b75210ab22ae02ab44d0900e53806788381`
