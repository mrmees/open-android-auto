# Coolwalk Layout Engine

## Overview

Coolwalk is Android Auto's responsive layout system for the main display. It adapts the UI based on screen dimensions, aspect ratio, and DPI — all computed **phone-side** from the display configuration the HU advertises in the ServiceDiscoveryResponse.

The HU's only lever is the **resolution and DPI** it advertises. Everything else — card placement, rail orientation, dashboard mode — is decided by the phone using PhenotypeFlags (server-pushed Google config) with hardcoded defaults.

This document covers the layout decision chain as reverse-engineered from the AA 16.2 APK.

---

## PhenotypeFlag Breakpoints

These are the layout-related PhenotypeFlags with their default values (from `abgu.java`):

| Flag | Default | Unit | Purpose |
|------|---------|------|---------|
| `SystemUi__horizontal_rail_canonical_breakpoint_dp` | 450 | dp | Width below which the vertical rail collapses |
| `SystemUi__short_portrait_breakpoint_dp` | 680 | dp | Height threshold for short portrait layout |
| `SystemUi__portrait_breakpoint_dp` | 900 | dp | Height threshold for full portrait mode |
| `SystemUi__semi_widescreen_breakpoint_dp` | 880 | dp | Width threshold for semi-widescreen layout |
| `SystemUi__widescreen_breakpoint_dp` | 1240 | dp | Width threshold for full widescreen layout |
| `SystemUi__widescreen_aspect_ratio_breakpoint` | 1.67 | ratio | Aspect ratio (w/h) above which layout is "widescreen" |

These flags are pushed via Google Play Services PhenotypeFlags and cached on the phone. A custom HU cannot change them — they're server-side configuration. The defaults above are baked into the APK as fallbacks.

---

## Layout Type Classification

The phone classifies each display into a layout type (enum values 1-15+) based on width, height, and aspect ratio. The layout type drives which system UI layout XML is inflated and how regions are arranged.

### Layout Type → Layout Mode Mapping (`m26337k`)

From `mno.java`:

| Layout Type (f48900h - 1) | Mode (mnu) | Description |
|---------------------------|------------|-------------|
| 1, 2, 3, 6, 12, 13, 14, 15 | `mnu.a` | CANONICAL — Standard Coolwalk |
| 4, 5 | `mnu.e` | WIDESCREEN — Wide aspect ratio layout |
| 7 | `mnu.b` | CLUSTER — Instrument cluster display |
| 8 | `mnu.c` | CLUSTER_WITH_LAUNCHER — Cluster with app launcher |
| 9 | `mnu.d` | AUXILIARY — Secondary display (nav-only) |
| 10 | `mnu.f` | PORTRAIT — Tall display layout |
| 11 | `mnu.g` | PORTRAIT_SHORT — Short portrait layout |

**Note:** Cielo (Material 3 theme) is NOT a layout type — it's a visual theme overlay applied on top of any layout mode. See [Cielo Theme](#cielo-theme-material-3) below.

### System UI Layout Variants (`m26305M`, `m26306N`)

Each layout type resolves to one of 8 possible XML layouts combining:
- **LHD** (left-hand drive) vs **RHD** (right-hand drive)
- **Vertical rail** present or absent
- **Driver-aligned dashboard** on or off

Standard Coolwalk layouts:
```
sys_ui_layout_canonical_lhd
sys_ui_layout_canonical_vertical_rail_lhd
sys_ui_layout_canonical_lhd_driver_aligned_dashboard
sys_ui_layout_canonical_vertical_rail_lhd_driver_aligned_dashboard
(same set with _rhd suffix)
```

Cielo layouts (Material You):
```
sys_ui_cielo_layout_canonical_lhd
sys_ui_cielo_layout_canonical_vertical_rail_lhd
sys_ui_cielo_layout_canonical_lhd_driver_aligned_dashboard
sys_ui_cielo_layout_canonical_vertical_rail_lhd_driver_aligned_dashboard
(same set with _rhd suffix)
```

---

## Dashboard Layout Decision

### Horizontal vs Vertical Dashboard

The critical decision — whether to show dashboard cards **side-by-side** (horizontal) or **stacked** (vertical).

**Decision point** (`mno.m26328K`):
```java
// If layout mode is NOT standard Coolwalk, always horizontal
if (layoutMode != mnu.a) return true;

// Otherwise, width threshold:
if (layoutType == 2) {  // landscape
    return displayWidthDp >= 730;
} else {
    return displayWidthDp >= 800;
}
```

The `IS_HORIZONTAL` flag is set on the `DashboardFragment` arguments (line 238-244 of `lti.java`):
```java
String args = region.getString(mno.arguments_key);
boolean isHorizontal = (args != null) ? args.contains("horizontal") : false;
dashboardFragment.setArguments(bundle("IS_HORIZONTAL", isHorizontal));
```

### Dashboard Sizing Formula

From `mno.m26307O` (line 183-200):

```
Input:
  screenWidthDp     = Android Configuration.screenWidthDp
  density           = DisplayMetrics.density
  gutter            = coolwalk_gutter_padding (10dp default)
  rail_width        = coolwalk_vertical_rail_width (80dp default)
  guideline_ratio   = dashboard_guideline_ratio (3.2 default)
  ime_min_width     = car_ime_min_width
  isDriverAligned   = user setting

Calculate:
  available_px = screenWidthDp × density
  if (isHeroLayout && hasVerticalRail):
      available_px -= 2 × rail_width
  available_px -= content_inset_width

  dashboard_px = (available_px / guideline_ratio) + 2 × gutter

  if (isDriverAligned):
      dashboard_px += rail_width - gutter

  max_dashboard_px = available_px - rail_width - gutter - ime_min_width
  return min(max_dashboard_px, dashboard_px)
```

### Dashboard Width Resource Overrides

| Width Qualifier | `dashboard_width` |
|----------------|-------------------|
| Default | 320dp |
| w734dp+ | 324dp |

---

## Rail (Navigation Bar) Configuration

The rail is the left-side (or bottom) navigation bar with facets for nav, media, phone, messaging.

### Rail Width by Screen Width

| Width Qualifier | `coolwalk_vertical_rail_width` | `floating_vertical_rail_width` |
|----------------|-------------------------------|-------------------------------|
| Default | 80dp | 96dp |
| w1376dp+ | 92dp | 108dp |

### Rail Orientation

- **Vertical rail** (left side): when `displayWidthDp >= horizontal_rail_canonical_breakpoint_dp` (default: 450dp)
- **Horizontal rail** (bottom): when narrower than the breakpoint

### Height Threshold

From `mno.m26315W`:
```java
screenHeightDp >= SystemUi__portrait_breakpoint_dp  // default: 900dp
```

This gates whether certain tall-display features are enabled.

---

## Screen Regions

The Coolwalk layout defines these named regions (`mnn` enum, from `mno.m26310R`):

| Region ID | Name | Purpose |
|-----------|------|---------|
| activity | Main activity | Primary projected content |
| demand | Demand | Active task / turn-by-turn |
| demand_rail | Demand Rail | Compact demand in rail |
| dashboard | Dashboard | Card container (media, messaging, etc.) |
| map | Map | Navigation map background |
| map_compat | Map Compat | Backward-compatible map region |
| rail | Rail | Navigation bar (facets) |
| status_bar | Status Bar | Clock, signal, battery |
| notification | Notification | Toast/HUN area |
| notification_center | Notification Center | Expanded notification list |
| ime | IME | Keyboard overlay |
| map_ime | Map IME | Keyboard over map |
| immersive | Immersive | Full-screen content |
| immersive_toolbar | Immersive Toolbar | Toolbar in immersive mode |
| fullscreen | Fullscreen | True full-screen (no chrome) |
| frx | FRX | First-run experience |
| sliver | Sliver | Thin notification strip |
| cluster_launcher | Cluster Launcher | Cluster display launcher |
| assistant_immersive_fullscreen | Assistant FS | Google Assistant full-screen |
| assistant_immersive_partial | Assistant Partial | Google Assistant partial |
| integrated_overlay | Integrated Overlay | Overlay UI layer |
| passenger_rail | Passenger Rail | Right-side rail (passenger display) |
| driver_rail | Driver Rail | Left-side rail (driver display) |
| ui_overlay_decorations | UI Overlay | Visual decorations |
| rounded_corner_mask | Corner Mask | Rounded corner overlays |

---

## DPI Impact on Layout — Reference Table

For a **1024×600** physical pixel display (typical car head unit):

| DPI | Density | screenWidthDp | screenHeightDp | Aspect | Dashboard | Rail |
|-----|---------|---------------|----------------|--------|-----------|------|
| 120 | 0.75 | 1365 | 800 | 1.71 | Horizontal | Vertical (92dp at w1376) |
| 140 | 0.875 | 1170 | 685 | 1.71 | Horizontal | Vertical |
| 160 | 1.0 | 1024 | 600 | 1.71 | Horizontal | Vertical |
| 200 | 1.25 | 819 | 480 | 1.71 | Horizontal (barely) | Vertical |
| 213 | 1.33 | 770 | 451 | 1.71 | Horizontal (730+ landscape) | Vertical |
| 240 | 1.5 | 682 | 400 | 1.71 | **Vertical** | Vertical |
| 280 | 1.75 | 585 | 342 | 1.71 | **Vertical** | Vertical |
| 320 | 2.0 | 512 | 300 | 1.71 | **Vertical** | Vertical |

**Notes:**
- All 1024×600 configs exceed the 1.67 widescreen aspect ratio breakpoint
- The horizontal dashboard cutoff is between **213 DPI** (770dp, landscape threshold 730dp) and **240 DPI** (682dp, below both thresholds)
- At 160 DPI, the layout comfortably lands in widescreen horizontal dashboard territory
- At 120 DPI, text and UI elements render smaller but you get the widest layout with the most card space

For a **1280×720** display:

| DPI | Density | screenWidthDp | screenHeightDp | Dashboard | Rail |
|-----|---------|---------------|----------------|-----------|------|
| 120 | 0.75 | 1706 | 960 | Horizontal + widescreen | Vertical (92dp) |
| 160 | 1.0 | 1280 | 720 | Horizontal + widescreen | Vertical (92dp at w1376) |
| 240 | 1.5 | 853 | 480 | Horizontal | Vertical |
| 320 | 2.0 | 640 | 360 | **Vertical** | Vertical |

---

## How the HU Controls This

The HU advertises display capabilities in the ServiceDiscoveryResponse:

1. **VideoChannelDescriptor** (`vye.java`) contains resolution and DPI per display
2. **SDP Munger** (`ilf.java`) on the phone processes these values
3. The phone creates an Android `Configuration` with `screenWidthDp` and `screenHeightDp` derived from the advertised resolution and DPI
4. The Coolwalk layout engine reads `Configuration.screenWidthDp`, `DisplayMetrics.density`, and the PhenotypeFlag breakpoints to select layout

**The HU cannot:**
- Change PhenotypeFlags (they're server-pushed)
- Request specific layout modes
- Control which cards appear in the dashboard
- Force horizontal or vertical dashboard mode directly

**The HU can:**
- Advertise a specific DPI in the SDP to influence the `screenWidthDp` calculation
- This indirectly controls which breakpoints are triggered
- Lower DPI → higher `screenWidthDp` → more widescreen-like layout
- Higher DPI → lower `screenWidthDp` → more compact/vertical layout

---

## Dashboard Card System

### Card Types

The dashboard supports 6 card types, implemented as `lsf` subclasses:

| Card | Class | Fragment | Swipeable |
|------|-------|----------|-----------|
| Blank/Placeholder | `lry` | `ltj` | Yes (default) |
| Navigation/CarPlay | `lrz` | `ity` | **No** — can't dismiss active nav |
| Media | `lsa` | `lyl` | **No** — can't dismiss now playing |
| Navigation Suggestions | `lsb` | `lzv` | Yes |
| Notification | `lsc` | `mbb` | Yes |
| TelecomCall (active) | `lsd` | `mbh` | **No** — can't dismiss active call |
| Phone (idle) | `lse` | `mcd` | Conditional (layout mode) |

All 6 card types can appear in the dashboard. The `mo25633a()` method controls **swipe-to-dismiss** behavior (argument key: `.swipable`), not card visibility. Media, nav, and active calls are pinned — the user can't swipe them away.

**No weather card exists.** Weather info shown on Coolwalk comes from Google Assistant proactive suggestions rendered as notifications, or from phone weather app notifications.

### Card Selection Logic

Cards are **not** priority-ranked. Selection is **reactive stream-based**:

- The ViewModel (`ltc.java`) subscribes to observable data streams for each card source
- **Primary card slot** (`f46271f`): Driven by whichever observable most recently emits valid content
- **Secondary card slot** (`f46272g`): Phone call state takes priority if available; otherwise falls back to secondary stream
- **300ms debounce** (`f46269d` frozen state): Prevents rapid card flipping when multiple sources update simultaneously

### Card Slot Layout

**Vertical dashboard** (narrow displays):
- `dashboard_top` — primary card (hidden by default, `visibility=gone`)
- `dashboard_top_second` — overlay card (layered above)
- `dashboard_bottom` — main visible card

**Horizontal dashboard** (wide displays):
- `dashboard_top` — left card
- `dashboard_top_second` — overlay card
- `dashboard_bottom` — right card

### Card Trigger Sources

| Card | Trigger | Observable Source |
|------|---------|------------------|
| Media | MediaBrowserService playback state | `lwk` (Media ViewModel) |
| Nav Suggestions | Suggestion list updates | `mae` / `lzx` |
| Notification | Android notification posted/updated/canceled | `mpe` (NotificationStore) + `RankingMap` |
| Phone | Phone call state changes | `mcd` (Phone ViewModel) |
| Navigation | Nav channel events | Suppressed — nav is background map |

### Card Rendering

Card rendering dispatches through `lou.m25520l()`:
```
Blank     → no-op
Navigation → CarPlay fragment (ity)
Media     → lwk.m25739o() media fragment
Nav Sugg  → lzm.m25826c() suggestions fragment
Notification → map.m25857b() notification fragment
Phone     → jfz.m22303h() phone fragment
```

### Swipe-to-Dismiss Behavior

The `mo25633a()` method on each card type returns whether the card is **swipeable** (dismissable by user swipe gesture). The result is passed to the fragment as a `.swipable` boolean argument (`luc.f46368a`).

- **Pinned cards** (not swipeable): media, navigation, active calls — these represent ongoing activities the user initiated
- **Dismissable cards** (swipeable): notifications, nav suggestions — contextual info that can be cleared
- **Phone card** (`lse`): conditionally swipeable — disabled for layout modes 5-6 (specific vehicle display types)

### Implications

All card types can appear in the dashboard. The "random" appearance of different content is stream-based — whichever observable fires most recently with valid content fills the slot, with 300ms debounce to prevent flicker. Cards representing ongoing activities (media, nav, calls) are pinned and can't be dismissed by the user.

---

## Hero Layout — Integrated Panel Displays

Hero layouts are for vehicles where Android Auto shares a single large screen with native car UI (BMW iDrive, Mercedes MBUX, etc.). The AA content occupies a cutout region within the larger display.

### POIP (Picture on Integrated Panel)

- **Landscape** integrated panel
- Cutout: ~1280dp wide
- **Three rails**: driver rail (left), main vertical rail, passenger rail (right)
- Layout: `sys_ui_layout_hero_poip_lhd.xml` / `_rhd.xml`
- The `isHeroLayout` flag in `mnj.java` reduces available dashboard width by `2 × rail_width` to account for the extra rails

### SOIP (Second on Integrated Panel)

- **Portrait-ish** integrated panel
- Cutout: ~768×1244dp
- **Horizontal bottom rail** (no vertical side rails)
- Layout: `sys_ui_layout_hero_soip.xml`

### Dashboard Width Impact

When `isHeroLayout` is true and a vertical rail is present, the dashboard sizing formula subtracts `2 × rail_width` from available pixels before computing dashboard width:

```
if (isHeroLayout && hasVerticalRail):
    available_px -= 2 × rail_width
```

This prevents the dashboard from overlapping the driver/passenger rails in POIP mode.

### Relevance to OpenAuto Prodigy

Hero layouts target OEM-integrated displays — not relevant for aftermarket head units. Our 1024×600 and 1280×720 displays will always use standard CANONICAL or WIDESCREEN modes. Documented here for protocol completeness.

---

## Cielo Theme (Material 3)

Cielo is Google's Material 3 / Material You visual theme for Android Auto. It is a **theme overlay**, not a structural layout change — the layout regions and dashboard logic are identical to standard Coolwalk.

### How It Works

- Enabled via PhenotypeFlag `pus.CIELO` (index 53 in the PhenotypeFlag enum)
- Legacy flags: `CieloFeature__cielo_status`, `CieloFeature__earth_enabled`
- Theme selection in `jzm.java`: switches between Coolwalk and Cielo resource overlays
- `jlf.java` manages the Cielo component singleton

### Layout XML Variants

Cielo has its own set of structurally identical layout XMLs with a `cielo` prefix:

```
sys_ui_cielo_layout_canonical_lhd
sys_ui_cielo_layout_canonical_vertical_rail_lhd
sys_ui_cielo_layout_canonical_lhd_driver_aligned_dashboard
sys_ui_cielo_layout_canonical_vertical_rail_lhd_driver_aligned_dashboard
(same set with _rhd suffix)
```

These use the same region structure as standard Coolwalk but with different visual styling (colors, typography, corner radii, etc.).

### Relevance to OpenAuto Prodigy

Cielo is entirely phone-side rendering. The HU cannot control whether Cielo is active — it depends on the phone's PhenotypeFlags from Google Play Services. The projected video output will simply look different (Material 3 styling). No HU-side changes needed.

---

## Demand Region — Voice/Assistant UI

The demand region is **NOT** turn-by-turn navigation. It is the Google Assistant / voice interaction overlay that appears when the user activates voice input.

### Triggers

- Steering wheel voice button (hardware input)
- "Hey Google" voice activation
- Google Maps microphone button
- Assistant proactive suggestions

### Layout Behavior

- Demand occupies its own named region (`demand` in the `mnn` enum)
- Coexists with the dashboard — does **not** replace or hide cards
- Compact variant available in the rail region (`demand_rail`)
- Templates: `demand_voice_plate.xml`, `demand_space_search_suggestion.xml`, etc.

### Relevance to OpenAuto Prodigy

The HU needs to forward microphone audio and voice button events for the demand region to work. The visual rendering is entirely phone-side (projected video). No custom rendering needed.

---

## Driver-Aligned Dashboard

A user-configurable setting that repositions the dashboard closer to the driver's side of the display.

### Settings

- Key: `key_settings_driver_aligned_dashboard`
- Enum class: `llk.java`
- User toggles this in AA settings on the phone

### Layout Impact

| Setting | Dashboard Position (LHD) | Guideline Ratio |
|---------|--------------------------|-----------------|
| Off (default) | Right side, 31.25% width | 3.2 |
| On | Left side (driver-near), wider | 4.0 |

When enabled:
- Dashboard position flips from the default side to the driver side
- Dashboard gets a wider allocation (`guideline_ratio` changes from 3.2 to 4.0)
- Extra width: `rail_width - gutter` added to dashboard pixels
- Separate layout XMLs with `_driver_aligned_dashboard` suffix are inflated

### Layout XMLs

```
sys_ui_layout_canonical_lhd_driver_aligned_dashboard
sys_ui_layout_canonical_vertical_rail_lhd_driver_aligned_dashboard
(same with _rhd, and Cielo variants)
```

### Relevance to OpenAuto Prodigy

This is a phone-side setting that affects projected video layout. The HU doesn't need to know about it — the phone handles repositioning within the projected video surface. However, knowing the dashboard ratio changes (3.2 → 4.0) is useful if we ever render our own dashboard widgets overlaying the projected content.

---

## Facet Switching — Wire Protocol Implications

The Coolwalk rail has facets for navigation, media, phone, and home/launcher. A key question for HU implementors: **does the phone notify the HU when the user switches facets?**

### Answer: No (with one exception)

Facet switching is **entirely phone-internal UI routing**. Tapping a facet starts an Android activity within GMS — no wire message is sent to the HU. The exceptions:

| Facet | Wire Event? | Details |
|-------|:-----------:|---------|
| Navigation | **Indirect** | Nav app's `startNavigation()` triggers `NavigationFocusRequest` (msg 13, channel 0) — but this fires from the app lifecycle, not from the facet tap |
| Media | No | Starts media app activity internally |
| Phone | No | Starts phone app activity internally |
| Home | No | Starts launcher activity internally |

### NavigationFocusRequest (msg 13, channel 0)

The only facet-related wire message. Fires when a nav app calls `startNavigation()` (focus acquisition) or `abandonFocus()` (release).

```protobuf
message NavigationFocusRequest {    // APK class: vyl
    optional NavigationFocusType type = 1;  // vyn enum
}

enum NavigationFocusType {
    NAV_FOCUS_NATIVE = 1;      // HU providing own navigation
    NAV_FOCUS_PROJECTED = 2;   // Phone requesting projected nav focus
}
```

Response: `NavigationFocusNotification` (msg 14, channel 0) — HU acknowledges.

**Kill switch**: PhenotypeFlag `SystemUi__send_nav_focus_to_car_when_abandoned_kill_switch` (index 43, default `true`). When `false`, the phone skips sending focus-abandon to HU.

### CarFacet — HU-to-Phone Direction

The protocol supports facet switching in the **reverse** direction: an OEM HU can tell the phone to switch facets via `mo18979ax(CarFacet)`. The phone logs telemetry (`FACET_NAVIGATION_START/END`, `FACET_MUSIC_START/END`, `FACET_PHONE_START/END`) but there's no phone→HU equivalent.

### Implications for OpenAuto Prodigy

The HU cannot know which facet is active from wire events alone. To infer active content:
- **Navigation active**: `NavigationNotification` / `NavigationState` messages flowing on nav channel, or legacy flat turn-event variants on older HU paths
- **Media active**: `MediaPlaybackStatus` updates on media channel
- **Phone active**: `PhoneStatusUpdate` on phone channel
- **Idle**: No channel actively sending content-specific messages

This is inference, not notification — there's a latency gap between facet switch and first data message. For custom secondary-display widgets, this is good enough; the widget shows whatever data is most recently received.

---

## APK Source References (16.2)

| Class | Role |
|-------|------|
| `mno` | DisplayLayout — main layout engine, dashboard sizing, region management |
| `mnj` | LayoutInfo — immutable layout configuration (displayWidthDp, layoutType, etc.) |
| `mnn` | Region enum (activity, dashboard, rail, etc.) |
| `mnu` | Layout mode enum (standard, compact, narrow, cielo, etc.) |
| `lti` | Dashboard window controller — sets IS_HORIZONTAL on DashboardFragment |
| `lsu` | DashboardFragment — inflates horizontal or vertical dashboard layout |
| `lrw` | Base fragment — reads IS_HORIZONTAL from arguments |
| `kgf` | Synthetic delegate — case 17 reads IS_HORIZONTAL bundle arg |
| `ltc` | DashboardViewModel — card visibility state and debounce |
| `abgu` | PhenotypeFlag implementation — all breakpoint defaults |
| `abgt` | PhenotypeFlag interface — method signatures for breakpoints |
| `ilf` | SDP munger — processes HU-advertised display resolution/DPI |
| `ltc` | DashboardViewModel — card visibility observables, debounce |
| `lou` | Card rendering dispatch — switches on card type to fragment |
| `lry`-`lse` | Card type classes (blank, nav, media, suggestions, notification, phone) |
| `lyl` | Media card fragment |
| `lzv` | Navigation suggestions card fragment |
| `mbb` | Notification card fragment |
| `mcd` | Phone/telecom card fragment |
| `mpe` | NotificationStore — notification data + ranking |
| `lwk` | Media ViewModel — playback state observable |
| `jlf` | Cielo component singleton |
| `jzm` | Theme overlay selection — Coolwalk vs Cielo resource switching |
| `pus` | PhenotypeFlag enum — CIELO at index 53 |
| `llk` | Driver-aligned dashboard enum |
| `mfx` | GH.GhRailFrg — rail fragment (driver side) |
| `mgk` | Rail fragment (passenger side) |
| `mgw` | GH.RailHotseatLD — builds hotseat items with onClick lambdas |
| `miw` | HotseatItem — icon, componentName, onClick lambda per facet |
| `lor` | GH.ProjectionContext — starts car activities (phone-internal, no wire) |
| `lai` | GH.GhNavFocusManager — navigation focus state machine → msg 13 |
| `hwm` | CAR.MSG — sends NavigationFocusRequest (msg 13) to HU |
| `vyl` | NavigationFocusRequest proto |
| `vyn` | NavigationFocusType enum (NATIVE=1, PROJECTED=2) |

**Layout resources:**
- `res/layout/horizontal_dashboard_root.xml` — two-column card layout
- `res/layout/vertical_dashboard_root.xml` — stacked card layout
- `res/values/dimens.xml` — base dashboard/rail dimensions
- `res/values-w734dp/dimens.xml` — dashboard_width override (324dp)
- `res/values-w1376dp/dimens.xml` — rail width increase (92dp)
- `sys_ui_layout_hero_poip_lhd.xml` / `_rhd.xml` — Hero POIP (landscape integrated panel)
- `sys_ui_layout_hero_soip.xml` — Hero SOIP (portrait integrated panel)
