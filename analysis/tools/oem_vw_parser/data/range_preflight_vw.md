# Pre-flight: Prodigy-derived msg_type range hints vs VW MIB3 OI capture

**Capture:** `captures/oem-vw-mib3oi-2026-04-06/` (7,954 records, 60s window)
**Performed:** 2026-04-07
**Purpose:** Per [07-CONTEXT.md](../../../.planning/phases/07-vw-capture-analysis/07-CONTEXT.md) § "Range matching is DOWNGRADED to tiebreaker only" — cross-check every Prodigy-derived msg_type range against the actual VW capture BEFORE allowing any range-based attribution.

## VW SDP-declared services

Direct decode of `sdp_response.bin`:

```
av_channel, av_input_channel, bluetooth_channel, input_channel,
media_info_channel, navigation_channel, phone_status_channel,
sensor_channel, wifi_channel
```

Notably absent: `radio_channel`, `car_control_channel`, `vendor_extension_channel`, `media_browser_channel`, `notification_channel`, `generic_notification_channel`, `voice_channel`.

## Hypotheses checked

| Range | Hex | Claimed service | Observed count in VW | Declared by VW SDP? | Verdict | Evidence |
|-------|-----|-----------------|---------------------:|--------------------|---------|----------|
| 32794–32803 | `0x801A-0x8023` | radio_channel | 0 | No | `dropped_no_declared_service` | VW SDP does not declare radio_channel; 0 records observed in this range. The Prodigy hypothesis cannot be applied to a session that has no radio service at all. |
| 32769–32775 | `0x8001-0x8007` | car_control_channel | 3,880 | No | `dropped_no_declared_service` | VW SDP does not declare car_control_channel, but 3,880 records fall in this range. They belong to other declared services (sensor, navigation, av_input). Per CONTEXT.md, channel-scoped IDs (`0x8000+`) are PER-CHANNEL namespaces — same numeric ID, different proto on different channels. Applying this hint would mis-attribute every sensor record. |
| 32769–32772 | `0x8001-0x8004` | sensor_channel | 3,788 | Yes | `dropped_ambiguous` | VW DOES declare sensor_channel, and 95% of the 0x8001–0x8007 traffic falls here. Prodigy hypothesis is consistent with VW reality, but the same IDs are also used by `input_source`, `media_sink`, etc. in the validator message_map. SDP narrowing via structural fingerprinting (Task 3) handles this correctly without needing a range hint. |
| 32774–32775 | `0x8006-0x8007` | navigation_channel | 92 | Yes | `dropped_ambiguous` | 46 records on each of 0x8006/0x8007 (out direction). Prodigy hypothesis is consistent, but the same IDs are also used by `media_sink/AVInputOpenRequest` in the validator message_map. Conflicts with AV channel attribution if forced. |
| 32772 | `0x8004` (single) | (open question) | 2,752 | — | `open_question_documented` | The dominant HU→phone stream (35% of all traffic). Not in the 16.2 validator message_map for any service. Possibly `SensorEventIndication`, but the binding can NOT be forced via range hint alone. Attribution pipeline must leave this as Tier B `sdp_narrowed` (or `sdp_candidates`), never falsely claim deterministic attribution. |

## Surviving hints

**None.** Every Prodigy-derived range hint is either inapplicable for VW (radio, car_control — services VW does not declare) or ambiguous (sensor, navigation — IDs collide with other declared services in the validator message_map).

## Dropped hints

1. `radio_range` — VW declares no radio_channel.
2. `car_control_range` — VW declares no car_control_channel; traffic in the range belongs to other services.
3. `sensor_range` — Ambiguous; structural fingerprinting via SDP narrowing handles this without a range hint.
4. `navigation_range` — Ambiguous; conflicts with AV channel attribution.

## Why range matching is tiebreaker only

From `07-CONTEXT.md` § "Range matching is DOWNGRADED to tiebreaker only":

> Never a primary or standalone signal. Only used when structural fingerprinting leaves >1 candidate AND a previously-observed range hint narrows it to 1 → accept as `low_confidence` with `attribution_method: inferred_by_range`. **Never overrides SDP constraints or descriptor matches.**

The Prodigy ranges came from APK GAL handler verification — they're correct for the *channel handlers in the APK*, but the VW capture has no `channel_id` (the on-phone Frida hook lives inside the AA framing layer). Without `channel_id`, range hints assume one msg_type maps to one service, which is FALSE for `0x8000+` IDs. The whole reason `attribution_method: inferred_by_range` is `low_confidence` is that the underlying assumption is unsafe.

## Downstream consumption

`attribution.py` reads `range_hints.json` at module load time:

```python
RANGE_HINTS = _load_range_hints()
```

It only consults `surviving_hints` as a tiebreaker when SDP narrowing returns multiple candidates. With `surviving_hints = []` for VW, the attribution module falls back to pure SDP narrowing — exactly what CONTEXT.md prescribes.

If a future capture surfaces a clean range that VW didn't (e.g., a non-VW OEM that DOES declare radio_channel), this file gets re-derived against that capture and the surviving_hints list grows. The attribution code path needs no changes.
