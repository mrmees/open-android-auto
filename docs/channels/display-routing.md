# Multi-Display Content Routing

> **Architecture context:** This channel is part of the Android Auto multiplexed
> protocol. For the overall architecture — framing, SDP binding, capability
> negotiation — see [Channel Architecture Reference](architecture.md).

## Overview

Android Auto supports up to three display types: MAIN, CLUSTER, and AUXILIARY. The phone controls what content is rendered on each — the HU advertises displays via ServiceDiscoveryResponse, but has **no mechanism to request specific content types** on secondary displays.

This document combines the established 16.2 content-policy trace with the 17.3
logical-display identity trace. Content policy and endpoint identity are separate
layers.

## 17.3 identity model

`AVChannel.display_id` field 6 is the logical display identity: Android Auto
17.3 reads it and immediately constructs `CarDisplayId`. The matching
`InputChannelConfig.display_id` field 5 references that AVChannel field 6 value.
Neither value is `ChannelDescriptor.channel_id`, which is the transport channel
ID used for multiplexed frame routing, nor GAL service type 8 (AV input).

For each accepted video-capable descriptor, static 17.3 code constructs a
separate logical display/endpoint pair with per-instance configuration, surface,
and focus state. Concurrent streams across MAIN, CLUSTER, and AUXILIARY remain
runtime-unverified because no simultaneous framed 17.3 capture is available.

---

## Display Types

From `qcw.java` (16.2 APK):

| Value | Name | Purpose |
|-------|------|---------|
| 0 | MAIN | Primary head unit display — full Coolwalk UI |
| 1 | CLUSTER | Instrument cluster — behind steering wheel |
| 2 | AUXILIARY | Secondary display — e.g., passenger screen |
| 3 | UNKNOWN | Fallback for invalid values |

The HU advertises displays by including multiple video `ChannelDescriptor` entries in the SDP, each with a different `display_type` field (field 7 of `vye` / AVChannel proto).

### Constraints (from `iom.java`)

- Exactly ONE display must be `DISPLAY_TYPE_MAIN`
- At most ONE `DISPLAY_TYPE_CLUSTER` allowed
- Additional displays become `DISPLAY_TYPE_AUXILIARY`
- Primary display (ID 0) must be MAIN

---

## Main Display Content Categories

The main display uses `lpj.java` — a content category enum that maps to Coolwalk "facets":

| Value | Name | Int | Description |
|-------|------|-----|-------------|
| 0 | OTHER | 0 | Uncategorized |
| 1 | NAVIGATION | 1 | Maps / nav apps |
| 2 | PHONE | 2 | Phone calls / dialer |
| 3 | MEDIA | 3 | Music / podcasts |
| 4 | PHONE_MEDIA | 8 | Combined phone+media |
| 5 | SYSTEM | 7 | System UI / settings |

These categories drive the Coolwalk rail — the bottom bar that switches between nav, media, phone, and messaging views on the primary display. Intent categories from `ncg.java`:

```
1 → NAVIGATION
2 → MEDIA
3 → TELEPHONE
4 → OEM
5 → MESSAGING
```

**Key point:** This rich content routing only exists for the main display. Secondary displays get a much more limited menu.

---

## Auxiliary Display Content Types

From `qcx.java` (16.2 APK):

| Ordinal | Name | Service Component |
|---------|------|-------------------|
| 0 | UNKNOWN | (error — not supported) |
| 1 | NAVIGATION | `PrototypeAuxiliaryDisplayNavigationCarActivityService` |
| 2 | TURN_CARD | `PrototypeAuxiliaryDisplayTurnCardCarActivityService` |

**That's it.** No MEDIA, no PHONE, no MESSAGING. The auxiliary display is nav-only in 16.2.

### Routing Logic (`loz.java`)

```
qcx content_type → ComponentName:
  NAVIGATION (1) → PrototypeAuxiliaryDisplayNavigationCarActivityService
  TURN_CARD  (2) → PrototypeAuxiliaryDisplayTurnCardCarActivityService
  other      → logs error, returns null
```

Non-prototype variants also exist (`AuxiliaryDisplayNavigationCarActivityService`, `AuxiliaryDisplayTurnCardCarActivityService`) — likely production vs. experimental paths.

### Content Type Assignment (`lpa.java`)

The `AuxiliaryDisplayConfiguration` class maintains a map of `CarDisplayId → qcx` (content type). This map is populated during initialization — the exact source of the content type decision was not traced to a wire field. It may be:
- Server-side flag (PhenotypeFlags / GMS config)
- Hardcoded default per display_type
- Derived from the display's capabilities

The `vtr.java` prototype activity confirms only two states:
- `"NAVIGATION AUXILIARY DISPLAY"` for ordinal 1
- `"TURN CARD AUXILIARY DISPLAY"` for ordinal 2
- `IllegalStateException` for anything else

---

## Cluster Display Routing

The 16.2 `lpc.java` path and the 17.3 `mnw.java` path use the same
priority-based fallback chain:

1. **Power saving + battery optimized** → `ClusterTurnCardCarActivityService` (lightweight)
2. **Default nav app has a cluster service** → use it (discovered via `CATEGORY_PROJECTION_NAVIGATION` intent)
3. **Google Maps fallback** → `GmmCarAuxiliaryProjectionService` (hardcoded GMM component)
4. **Ultimate fallback** → `ClusterTurnCardCarActivityService`

The 17.3 selector is `mnw.e()` (`mnw.java:15-42`). It reads phone-side power
settings and navigation-service availability only. It does not receive or
inspect the CLUSTER `VideoConfig`.

### Navigation App Discovery (`lak.java` / `lyu.java`)

The cluster/auxiliary navigation service discovery queries for:
```
Intent("android.intent.action.MAIN")
  .addCategory("com.google.android.gms.car.category.CATEGORY_PROJECTION_NAVIGATION")
```

For cluster specifically, it also checks:
```
.addCategory("com.google.android.gms.car.category.CATEGORY_SECONDARY_REGION")
```

This means third-party nav apps (Waze, etc.) can provide their own cluster rendering service. But only navigation apps — no media or phone equivalents.

---

## Phone-side Display Mode Policy

### Auxiliary Display Mode (`ieu.java` in 16.2, `jdr.java` in 17.3)

| Value | Name | Effect |
|-------|------|--------|
| 0 | OFF | Auxiliary display disabled |
| 1 | BATTERY_OPTIMIZED | Battery-saving mode |
| 2 | ON | Fully enabled |

### Cluster Display Mode (`iev.java` in 16.2, `jds.java` in 17.3)

| Value | Name | Effect |
|-------|------|--------|
| 0 | OFF | Cluster disabled |
| 1 | BATTERY_OPTIMIZED | Battery-saving mode (forces turn card only) |
| 2 | ON | Fully enabled |

The master power-saving state is `iex.java` in 16.2 and `jdu.java` in 17.3.
These values are stored through phone-side car-service keys:

- `"auxiliary_display_mode"` → `ieu` enum
- `"cluster_display_mode"` → `iev` enum
- `"power_saving_mode"` → `iex` enum

In 17.3, `mkg.java:29-67` reads and writes the keys through the phone car
service, `mks.java:92-112` maps the phone settings UI to `ON`,
`BATTERY_OPTIMIZED`, or `OFF`, and missing values use phone-side flag defaults.
The initial display factory also reads the phone's `carservice`
`SharedPreferences` (`ijs.java:20-23`, `itq.java:307-324`).

No `ChannelDescriptor`, `AVChannel`, `VideoConfig`, SDP scalar, or HU
capability is read in these mode lookups. The HU can advertise or omit a
CLUSTER display, but no supported HU wire signal is known to assign
`cluster_display_mode` or force `BATTERY_OPTIMIZED`.

---

## Video Endpoint Architecture

Each display gets its own video endpoint (`ied.java`):

```
display_type → video content type:
  MAIN      → idm.VIDEO
  CLUSTER   → idm.VIDEO_CLUSTER
  AUXILIARY  → idm.VIDEO_AUXILIARY
```

The `ied.java` constructor takes a `vws` (display type) parameter and sets `f36752e = (vwsVar == vws.DISPLAY_TYPE_MAIN)` — a boolean that gates main-display-specific behavior.

The SDP munger (`ilf.java`) creates separate `vye` (AVChannel) proto objects for each display, each with its own resolution, codec, and display_type field.

---

## Runtime Descriptor and Layout Updates

Control message 26 (`ServiceDiscoveryUpdate`) does not replace a live AV
descriptor in Android Auto 17.3. The phone matches the embedded descriptor to
an already registered transport channel ID. Only the input endpoint implements
the update interface; an existing AV/video endpoint is logged as not
updatable, and an unregistered channel ID is rejected.

`UpdateUiConfigRequest` on the existing video channel is a separate supported
path for changing `AdditionalVideoConfig` state such as insets, margins,
resize actions, and UI-feature flags. It does not carry the outer
`VideoConfig`, `AVChannel`, or `ChannelDescriptor`, so it cannot change
resolution, DPI/density, display ID, display type, or transport channel ID.

See [Android Auto 17.3 Runtime Cluster Policy](../../analysis/reports/multi-display/android-auto-17.3-runtime-cluster-policy.md)
for the complete call chains.

---

## `session_configuration` and Display UI Features

`ServiceDiscoveryResponse.session_configuration` field 13 is a four-bit
legacy session mask. Android Auto 17.3 reads it as `xlx.n` in both the
`dsi.java:478-487` and `ryu.java:260-269` `CarInfo` construction paths. Both
consume only:

| Value | Published name | Phone-side effect |
|-----:|------|-------------|
| 1 | `SESSION_UI_CONFIG_HIDE_CLOCK` | `CarInfo` clock/status capability |
| 2 | `SESSION_UI_CONFIG_HIDE_PHONE_SIGNAL` | `CarInfo` phone-signal capability |
| 4 | `SESSION_UI_CONFIG_HIDE_BATTERY_LEVEL` | `CarInfo` battery capability |
| 8 | `SESSION_CAN_PLAY_NATIVE_MEDIA_DURING_VR` | Native media during voice recognition |

There is no field-13 value-16 read in either 17.3 consumer.

The display-feature source then depends on the version requested by the HU in
`VersionRequest`, not the separately selected negotiated result. For an HU
request of 4.3 or newer, the phone maps
`VideoConfig.AdditionalVideoConfig.hidden_ui_elements` to
`CarDisplayUiFeatures` as follows:

| UIElement enum value | CarDisplayUiFeatures flag | Runtime name |
|---:|---:|---|
| 1 | 1 | `hasClock` |
| 2 | 2 | `hasBatteryLevel` |
| 3 | 4 | `hasPhoneSignal` |
| 4 | 8 | `hasNativeUiAffordance` |
| 5 | 16 | `hasClusterTurnCard` |

For an HU request below 4.3, `itt.java:288-299` ignores
`hidden_ui_elements`. It instead maps `session_configuration` mask 1 to clock
flag 1, mask 4 to battery flag 2, and mask 2 to phone-signal flag 4. That
legacy branch has no flag 16; mask 8 retains its separate
native-media-during-VR meaning.

For a CLUSTER controller whose HU requested 4.3 or newer, flag 16 is inverted
into `EXTRA_SHOW_TURN_CARD`: advertising `hasClusterTurnCard` causes the phone
to pass `false` for the phone-rendered turn-card extra. This can affect
turn-card presentation after service selection, but the flag is not consulted
by `mnw.e()` when choosing the cluster activity service.

---

## Implications for OpenAuto Prodigy

### What the phone will project to secondary displays
- Navigation map (full Google Maps / Waze projection)
- Turn card (maneuver icon + road name + distance)

### What the phone will NOT project to secondary displays
- Media player UI (album art, playback controls)
- Phone call UI (dialer, in-call screen)
- Messaging UI
- Any non-navigation content

### What we CAN do
The phone sends rich signaling data on dedicated channels that we can render ourselves:
- **MediaPlaybackStatus** (ch12): song title, artist, album, playback state, position — wire verified
- **PhoneStatusUpdate** (ch11): signal strength, call state — wire verified
- **NavigationNotification** (ch10): full turn-by-turn with multi-step lookahead — wire verified
- **NavigationNextTurnDistanceEvent** (ch10): distance to next turn — wire verified

A custom HU can build its own media/phone widgets from this channel data rather than relying on phone-projected video surfaces. This is actually more flexible — we control the layout, styling, and update rate.

### widget_type is dead
The `widget_type` field (AVChannel field 8 / vye field 9) exists in the proto but:
- Phone validates it as `AndroidKeycode` enum — 65538 ("navigation") fails silently
- Only "navigation" is defined — `"Unrecognized widget type %s, using navigation"`
- Phone decides auxiliary content from `display_type` alone

---

## APK Source References (16.2)

| Class | File | Role |
|-------|------|------|
| `qcw` | `p000/qcw.java` | Display type enum (MAIN/CLUSTER/AUXILIARY/UNKNOWN) |
| `qcx` | `p000/qcx.java` | Auxiliary content type enum (UNKNOWN/NAVIGATION/TURN_CARD) |
| `lpj` | `p000/lpj.java` | Main display content category (OTHER/NAVIGATION/PHONE/MEDIA/SYSTEM) |
| `lpa` | `p000/lpa.java` | AuxiliaryDisplayConfiguration — maps CarDisplayId → content type |
| `loz` | `p000/loz.java` | Auxiliary display routing — content type → ComponentName |
| `lpc` | `p000/lpc.java` | Cluster display routing — fallback chain logic |
| `lak` | `p000/lak.java` | Secondary display nav app discovery |
| `vye` | `p000/vye.java` | AVChannel proto — display_type + widget_type fields |
| `ied` | `p000/ied.java` | Video endpoint — per-display video stream |
| `ilf` | `p000/ilf.java` | SDP munger — creates per-display channel configs |
| `iom` | `p000/iom.java` | Display validation constraints |
| `mno` | `p000/mno.java` | DisplayLayout — per-display layout management |
| `hve` | `p000/hve.java` | AdditionalVideoConfig UI-element to display-feature mapping (historically misattributed to `session_configuration`) |
| `llp` | `p000/llp.java` | Power savings config manager |
| `vtr` | `p000/vtr.java` | Prototype auxiliary display activity |
| `lro` | `p000/lro.java` | ContextManagerImpl — display initialization |

Current 17.3 source anchors and the corrected cross-path trace are recorded in
[Android Auto 17.3 Runtime Cluster Policy](../../analysis/reports/multi-display/android-auto-17.3-runtime-cluster-policy.md).
