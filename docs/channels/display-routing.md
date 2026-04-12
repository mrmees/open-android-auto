# Multi-Display Content Routing

> **Architecture context:** This channel is part of the Android Auto multiplexed
> protocol. For the overall architecture — framing, SDP binding, capability
> negotiation — see [Channel Architecture Reference](architecture.md).

## Overview

Android Auto supports up to three display types: MAIN, CLUSTER, and AUXILIARY. The phone controls what content is rendered on each — the HU advertises displays via ServiceDiscoveryResponse, but has **no mechanism to request specific content types** on secondary displays.

This document covers the phone-side content routing architecture as reverse-engineered from the AA 16.2 APK.

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

From `lpc.java` — the cluster has a priority-based fallback chain:

1. **Power saving + battery optimized** → `ClusterTurnCardCarActivityService` (lightweight)
2. **Default nav app has a cluster service** → use it (discovered via `CATEGORY_PROJECTION_NAVIGATION` intent)
3. **Google Maps fallback** → `GmmCarAuxiliaryProjectionService` (hardcoded GMM component)
4. **Ultimate fallback** → `ClusterTurnCardCarActivityService`

### Navigation App Discovery (`lak.java`)

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

## Display Mode Enums

### Auxiliary Display Mode (`ieu.java`)

| Value | Name | Effect |
|-------|------|--------|
| 0 | OFF | Auxiliary display disabled |
| 1 | BATTERY_OPTIMIZED | Battery-saving mode |
| 2 | ON | Fully enabled |

### Cluster Display Mode (`iev.java`)

| Value | Name | Effect |
|-------|------|--------|
| 0 | OFF | Cluster disabled |
| 1 | BATTERY_OPTIMIZED | Battery-saving mode (forces turn card only) |
| 2 | ON | Fully enabled |

Stored via car service keys:
- `"auxiliary_display_mode"` → `ieu` enum
- `"cluster_display_mode"` → `iev` enum
- `"power_saving_mode"` → `iex` enum

Managed by `llp.java` (Power Savings Configuration Manager).

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

## session_configuration Bitmask

From `hve.java` — the SDR `session_configuration` field (field 13) contains a bitmask of UI elements:

| Bit | Value | Name | Description |
|-----|-------|------|-------------|
| 0 | 1 | UI_ELEMENT_CLOCK | Show clock on phone |
| 1 | 2 | UI_ELEMENT_BATTERY_LEVEL | Show battery on phone |
| 2 | 4 | UI_ELEMENT_PHONE_SIGNAL | Show signal strength on phone |
| 3 | 8 | UI_ELEMENT_NATIVE_UI_AFFORDANCE | Native UI affordance |
| 4 | 16 | UI_ELEMENT_NAVIGATION_TURN_DATA_AVAILABLE | Turn data available for cluster |

Bit 4 (`NAVIGATION_TURN_DATA_AVAILABLE`) signals that the HU can receive turn-by-turn data — relevant for cluster turn card rendering.

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
| `hve` | `p000/hve.java` | session_configuration bitmask mapping |
| `llp` | `p000/llp.java` | Power savings config manager |
| `vtr` | `p000/vtr.java` | Prototype auxiliary display activity |
| `lro` | `p000/lro.java` | ContextManagerImpl — display initialization |
