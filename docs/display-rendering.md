# AA Display Rendering Pipeline

Technical reference for how an AA head unit renders Android Auto video on a non-standard display with an optional sidebar. Covers all 4 sidebar positions (left, right, top, bottom). Examples use a 1024x600 display as reference.

## The Problem

Android Auto only supports fixed video resolutions: 800x480 (480p), 1280x720 (720p), 1920x1080 (1080p). A 1024x600 display (common for car touchscreens) doesn't match any of these natively. When a sidebar is enabled, the available video area shrinks further. The rendering pipeline must:

1. Tell the phone to render its UI into an appropriately-sized sub-region (margins)
2. Display the received video frames correctly on the physical display (QML crop/fit)
3. Map touch coordinates from the physical touchscreen back to AA coordinate space (evdev mapping)
4. Handle sidebar touch zones for volume and home (evdev hit detection)

## The Margin Trick

The AA protocol's `VideoConfig` message (sent inside `ServiceDiscoveryResponse`) includes `margin_width` and `margin_height` fields. These tell the phone: "render your UI into a centered rectangle that is `(resolution_width - margin_width)` x `(resolution_height - margin_height)`, and fill the rest with black."

The phone still sends full-resolution video frames (e.g., 1280x720), but the actual UI content occupies a smaller centered rectangle within that frame. The surrounding area is black bars.

**Key constraint:** Margins are locked at session start. They are set during `ServiceDiscoveryResponse` and cannot be changed mid-session. Changing sidebar config requires an app restart.

### Where margins are set

In your AA implementation, margins are typically computed during service discovery setup and set on each `VideoConfig` entry (primary resolution + 480p fallback) before sending the `ServiceDiscoveryResponse`.

## Margin Calculation

Given:
- `displayW` x `displayH` = physical display pixels (e.g., 1024 x 600)
- `sidebarW` = sidebar width in pixels (e.g., 150), 0 if disabled
- `position` = sidebar position: "left", "right", "top", or "bottom"
- `rW` x `rH` = AA resolution (e.g., 1280 x 720)

```
horizontal = (position == "top" || position == "bottom")

aaViewportW = horizontal ? displayW : (displayW - sidebarW)
aaViewportH = horizontal ? (displayH - sidebarW) : displayH
screenRatio = aaViewportW / aaViewportH
remoteRatio = rW / rH

if screenRatio < remoteRatio:
    marginW = round(rW - (rH * screenRatio))
    marginH = 0
else:
    marginW = 0
    marginH = round(rH - (rW / screenRatio))
```

For **vertical sidebars** (left/right), the sidebar subtracts from display width → typically produces `marginW` (X-crop mode). For **horizontal sidebars** (top/bottom), the sidebar subtracts from display height → typically produces `marginH` (Y-crop mode).

### Worked Example: Right Sidebar, 150px, 720p

```
aaViewportW = 1024 - 150 = 874
aaViewportH = 600
screenRatio = 874 / 600 = 1.4567
remoteRatio = 1280 / 720 = 1.7778

screenRatio < remoteRatio → X-crop:
  marginW = round(1280 - (720 * 1.4567)) = round(231.2) = 231
  marginH = 0
```

Phone renders UI into centered 1049x720 sub-region. ~116px black bars per side.

### Worked Example: Bottom Sidebar, 75px, 720p

```
aaViewportW = 1024
aaViewportH = 600 - 75 = 525
screenRatio = 1024 / 525 = 1.9505
remoteRatio = 1280 / 720 = 1.7778

screenRatio > remoteRatio → Y-crop:
  marginW = 0
  marginH = round(720 - (1280 / 1.9505)) = round(720 - 656.3) = 64
```

Phone renders UI into centered 1280x656 sub-region. ~32px black bars top and bottom.

### Worked Example: No Sidebar, 720p

```
aaViewportW = 1024
aaViewportH = 600
screenRatio = 1024 / 600 = 1.7067
remoteRatio = 1280 / 720 = 1.7778

screenRatio < remoteRatio → X-crop:
  marginW = round(1280 - (720 * 1.7067)) = round(51.2) = 51
  marginH = 0
```

Small 51px total horizontal margin (~26px per side). AA UI nearly fills the frame.

## Content-Space Touch Mapping

**Critical concept:** The head unit sends touch coordinates in **content space** — the sub-region the phone actually uses for its UI — NOT full-frame (1280x720) space. The `touch_screen_config` field in `ServiceDiscoveryResponse` is set to match the content dimensions so the phone maps coordinates correctly.

### touch_screen_config

Set during service factory initialization. Computed identically to the margin calculation:

```
touchW = 1280, touchH = 720

if sidebar enabled:
    compute margins same way as VideoService
    if marginW > 0:
        touchW -= marginW    (e.g., 1280 - 231 = 1049 for side sidebar)
    else if marginH > 0:
        touchH -= marginH    (e.g., 720 - 64 = 656 for top/bottom sidebar)
```

This tells the phone: "touch coordinates range from 0 to `touchW` x 0 to `touchH`." The phone applies its own mapping from these coordinates to the content region within its rendered frame.

### Why content-space, not frame-space

If coordinates were sent in full 1280x720 space, you'd need to compute `cropAAOffsetX/Y` and add it to every coordinate. Instead, by setting `touch_screen_config` to the content dimensions, the phone handles the offset mapping internally. The head unit's touch mapping simply maps from 0 to `visibleAAWidth`/`visibleAAHeight`.

## Display Modes

Two video fill modes are relevant:

### No Sidebar: Aspect Fit

Video frame (1280x720) scaled to fit entirely within the display (1024x600), preserving aspect ratio. Small letterbox bars at top/bottom since 720p is slightly wider than the display.

### With Sidebar: Aspect Crop

Video frame scaled to fill the available area, with overflow cropped. This crops away the phone's black margin bars, leaving only the actual AA UI content visible.

### Layout Concept

The video area and sidebar are positioned absolutely to support all 4 sidebar positions:

```
Container {
    VideoArea {
        x: (position == "left" && showSidebar) ? sidebarWidth : 0
        y: (position == "top" && showSidebar) ? sidebarWidth : 0
        width: containerWidth - (isVertical && showSidebar ? sidebarWidth : 0)
        height: containerHeight - (isHorizontal && showSidebar ? sidebarWidth : 0)
    }

    Sidebar {
        x: based on position (right edge, left edge, or 0 for top/bottom)
        y: based on position (bottom edge, top edge, or videoArea.y for left/right)
        width: isVertical ? sidebarWidth : containerWidth
        height: isVertical ? videoArea.height : sidebarWidth
    }
}
```

## Crop Modes: X-Crop vs Y-Crop

### X-Crop (Side Sidebar — left/right)

Video fills display height, X overflow cropped. Used when `marginW > 0`.

```
effectiveDisplayW = displayW - sidebarW
scale = displayH / aaHeight                         = 600 / 720 = 0.8333
totalVideoWidthPx = aaWidth * scale                 = 1280 * 0.8333 = 1066.7
cropPx = (totalVideoWidthPx - effectiveDisplayW) / 2 = (1066.7 - 874) / 2 = 96.3

cropAAOffsetX = cropPx / scale                      = 96.3 / 0.8333 = 115.6
visibleAAWidth = effectiveDisplayW / scale           = 874 / 0.8333 = 1048.8
visibleAAHeight = aaHeight                           = 720

videoEvdev spans effectiveDisplayW in X, full displayH in Y
```

Touch mapping: `mapX(rawX) = clamp((rawX - videoEvdevX0) / videoEvdevW, 0, 1) * visibleAAWidth`

### Y-Crop (Horizontal Sidebar — top/bottom)

Video fills display width, Y overflow cropped. Used when `marginH > 0`.

```
effectiveDisplayH = displayH - sidebarW
scale = displayW / aaWidth                          = 1024 / 1280 = 0.8
totalVideoHeightPx = aaHeight * scale               = 720 * 0.8 = 576
cropPx = (totalVideoHeightPx - effectiveDisplayH) / 2 = (576 - 525) / 2 = 25.5

cropAAOffsetY = cropPx / scale                      = 25.5 / 0.8 = 31.9
visibleAAWidth = aaWidth                             = 1280
visibleAAHeight = effectiveDisplayH / scale          = 525 / 0.8 = 656.3

videoEvdev spans full displayW in X, effectiveDisplayH in Y
```

Touch mapping: `mapY(rawY) = clamp((rawY - videoEvdevY0) / videoEvdevH, 0, 1) * visibleAAHeight`

### Fit Mode (No Sidebar)

Video is aspect-fit into full display. Typically produces small letterbox bars. `visibleAAWidth = aaWidth`, `visibleAAHeight = aaHeight`. Touch maps linearly from video's evdev region to full AA range.

## Sidebar Touch Zones

When a sidebar is active, the head unit's touch handler defines exclusion zones in the touch coordinate space. Touches in the sidebar region are consumed locally (not forwarded to AA). The sidebar has two functional zones: **volume** (continuous drag) and **home** (tap).

**Important:** On Linux with evdev, `EVIOCGRAB` routes all touch exclusively through the evdev reader during AA. UI framework touch handlers receive no events. All sidebar interaction must be handled by hit-zone detection in the touch reader.

### Vertical Sidebar (left/right)

Detection: touch X falls within sidebar X-band (`sidebarEvdevX0` to `sidebarEvdevX1`).

Sub-zones divided by Y position within the X-band:

| Zone | Y Range | Function |
|------|---------|----------|
| Volume | Top 70% of display | Drag maps Y → 0-100% volume (top=100%) |
| Gap | 70%-75% | Dead zone between controls |
| Home | Bottom 25% | Tap triggers `sidebarHome()` |

Left sidebar: X-band is `[0, sidebarW * evdevPerPixelX]`.
Right sidebar: X-band is `[(displayW - sidebarW) * evdevPerPixelX, screenWidth]`.

### Horizontal Sidebar (top/bottom)

Detection: touch Y falls within sidebar Y-band (`sidebarEvdevY0` to `sidebarEvdevY1`).

Sub-zones divided by X position within the Y-band:

| Zone | X Range | Function |
|------|---------|----------|
| Volume | Left edge to ~100px from right edge | Drag maps X → 0-100% volume (right=100%) |
| Home | Rightmost ~80px | Tap triggers `sidebarHome()` |

Top sidebar: Y-band is `[0, sidebarW * evdevPerPixelY]`.
Bottom sidebar: Y-band is `[(displayH - sidebarW) * evdevPerPixelY, screenHeight]`.

### Volume Mapping

Vertical: `volume = (1.0 - relY) * 100` (top = max)
Horizontal: `volume = relX * 100` (right = max)

Supports continuous drag — slot tracked via `sidebarDragSlot_`, updates sent as `sidebarVolumeSet()` signals.

### Touch Routing Logic

On each `SYN_REPORT`, for every active dirty slot:
1. Check if touch falls in sidebar zone (X-band for vertical, Y-band for horizontal)
2. Sidebar touches are processed (volume/home) and their dirty flag cleared
3. If ALL touches are sidebar touches, AA processing is skipped entirely
4. If some touches are on video and some on sidebar, only non-sidebar touches forwarded to AA

## Debug Touch Overlay

A debug overlay that draws crosshairs at each active touch point is useful for validating touch mapping. The overlay should map content-space coordinates back to screen position accounting for sidebar margins and crop mode.

**Note:** The phone also draws its own touch indicators (if "Show taps" is enabled in Developer Options). These are drawn in full-frame space and may appear misaligned with actual content — that's a phone-side rendering artifact.

## Gotchas

- **Margins are locked at session start.** The phone negotiates video config once during `ServiceDiscoveryResponse`. Changing sidebar settings requires restarting the app.

- **EVIOCGRAB blocks all UI framework touch input.** During AA on Linux, sidebar interaction is purely evdev hit-zone detection. UI framework sidebar controls are visual only.

- **Aspect crop must match crop touch mapping.** If the display uses crop but touch mapping uses fit-mode math (or vice versa), touches will land at wrong positions. The sidebar-enabled flag in the letterbox computation gates which branch executes.

- **Touch coordinates are content-space, not frame-space.** Touch mapping returns values in `[0, visibleAAWidth]`/`[0, visibleAAHeight]`, NOT `[0, 1280]`/`[0, 720]`. The `cropAAOffsetX/Y` values are computed but NOT added to mapped coordinates — the phone handles offset mapping because `touch_screen_config` is set to content dimensions.

- **Sidebar position affects video origin in touch space.** A left sidebar shifts the video area rightward; a top sidebar shifts it downward. The letterbox computation accounts for this via effective display origin offsets.

- **The 480p fallback gets its own margin calculation.** Margins must be computed separately for each resolution config in the service discovery response.

- **Phone's `config_index` in `AVChannelSetupRequest` may not match advertised config list indices.** The phone may send a `config_index` value higher than expected even with fewer advertised configs. Responding with `add_configs(0)` works regardless.

- **Horizontal sidebar touch zones must match visual layout.** The home button in horizontal layout is a small icon (~56px) at the right end. If the home zone is too wide (e.g., 25% of screen), volume drags near the right side trigger home instead. Recommended zones: volume extends to ~100px from right edge, home is rightmost ~80px.

## Implementation Components

Any AA head unit implementing this pipeline needs these components:

| Component | Role |
|-----------|------|
| Video service config | Margin calculation, `ServiceDiscoveryResponse` video config |
| Service factory | `touch_screen_config` dimensions (content-space) |
| Touch reader | Touch mapping (fit/X-crop/Y-crop), sidebar hit zones, input I/O |
| Touch handler | Touch-to-AA protobuf bridge, content dimensions, debug overlay |
| Video display layout | Video area + sidebar positioning, fill mode selection |
