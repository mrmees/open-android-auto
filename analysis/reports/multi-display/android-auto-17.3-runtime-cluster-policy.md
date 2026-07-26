# Android Auto 17.3 Runtime Cluster Policy

Date: 2026-07-25
Target: Android Auto `17.3.662804-release` (`173662804`)
APKM SHA-256:
`1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344`
Base APK SHA-256:
`5557827f259898bdab97b489e1a0aef937fd6ec711d87361cf25d51af6f48619`

## Scope and confidence

This report answers the static-analysis questions from GitHub issue #10:

1. whether control message 26 can replace a live CLUSTER AV descriptor;
2. whether the HU can select the phone's cluster power mode;
3. whether video geometry selects the cluster renderer; and
4. whether `session_configuration` gained a cluster-turn-card bit at value 16.

The conclusions are confirmed against the versioned 17.3 JADX tree described
in `analysis/aa_apk_17.3.662804_apkm/PROVENANCE.md`. They describe reachable
phone-side static paths. No 17.3 framed runtime capture was available, so wire
traffic, activity launches, and vendor-specific behavior remain
runtime-unverified.

### Compatibility assessment

This correction does not change any field tag, type, cardinality, package,
direction, or message ID. The affected `.proto` edits only narrow comments;
their generated descriptors remain identical to the feature base. Evidence
sidecars are extended with the 17.3 consumer traces rather than increasing a
confidence tier.

## Conclusions

| Question | 17.3 conclusion | Prodigy consequence |
|---|---|---|
| Live AV replacement through `ServiceDiscoveryUpdate` | Not supported by the phone consumer. Updates match an already registered transport channel ID, and the only updatable endpoint implementation is the input endpoint. | Apply resolution, DPI, display type, or AV-channel changes in a fresh SDP after reconnecting the AA protocol session. |
| HU selection of `BATTERY_OPTIMIZED` | No HU protobuf or capability read was found in the selection path. The values are phone-side car-service settings with phone-side defaults. | Treat map-versus-turn-card selection as phone policy. |
| Geometry-driven renderer choice | Not present. Cluster service selection checks phone power policy and navigation-app compatibility; geometry is validated and consumed later by display construction. | Do not expect resolution, DPI, margins, or insets to force the turn-card service. |
| `session_configuration` value 16 | Not consumed. Field 13 still feeds only bits 1, 2, 4, and 8. Value 16 belongs to a different path: `AdditionalVideoConfig.hidden_ui_elements` enum value 5 becomes `CarDisplayUiFeatures.hasClusterTurnCard`. | Do not add value 16 to `SessionConfigurationEnum`. Advertise the UI element inside the CLUSTER video config when appropriate. |

## 1. `ServiceDiscoveryUpdate` cannot replace a live AV descriptor

### Receive and identity path

The control endpoint parses raw message ID 26 as `xly`, whose only payload is
one `xlv` `ChannelDescriptor`, and posts it to the service manager:

- `iyk.java:386-409` — parse message 26 and post the update;
- `img.java:193-198` — pass the embedded descriptor to `jae.d(...)`;
- `xly.java:4-35` — one-field update wrapper; and
- `xlv.java` — descriptor field `c` is field 1, the transport channel ID.

`jae.d(...)` matches `rsw.a == xlv.c` at `jae.java:225-250`. Therefore update
identity is the already registered transport channel ID. It is not
`AVChannel.display_id`, display type, or another display identity.

The same method establishes three hard boundaries:

- a descriptor for an unregistered channel throws
  `IllegalArgumentException`;
- a registered but not-yet-created service may be queued until discovery
  completes; and
- an existing service is updated only when its endpoint implements `ixj`.

There is no add-new-channel path after the original SDP topology has been
registered.

### Only the input endpoint is updatable

`ixj` has one method, `k(xlv)`. In the complete 17.3 source tree, `iiv` is the
only class that implements it (`iiv.java:27`). `iiv` is the input endpoint. Its
implementation at `iiv.java:380-403` reads the updated input descriptor and
copies touchpad field `xhq.j` when present, then recomputes `CarUiInfo`.

The AV/video endpoint does not implement `ixj`. Passing an existing AV
descriptor reaches the `jae.java:237-239` branch, logs that the service is not
updatable, and leaves the existing endpoint in place. Consequently the phone
does not close the old video channel, issue a new channel-open, or repeat AV
setup/start for a replacement descriptor.

### Supported same-channel UI updates are a different message

Video message `UpdateUiConfigRequest` (`0x8009`, HU -> Phone) is the supported
runtime path for changing `AdditionalVideoConfig` on an existing endpoint.
`itt.y(...)` merges that payload, rebuilds display parameters, updates encoder
ROI/bitrate state, and notifies the display surface (`itt.java:796-856`).

That message can update insets, margin configs, resize actions, UI-feature
flags, and version-dependent theme state. It does not carry or replace the
outer `VideoConfig`, `AVChannel`, or `ChannelDescriptor`; it therefore cannot
change the advertised resolution enum, density/DPI, display ID, display type,
or transport channel ID.

## 2. Cluster power mode is phone policy

Two phone-side stores feed the 17.3 policy:

- During display construction, `itq.b(...)` reads
  `power_saving_mode`, `auxiliary_display_mode`, and `cluster_display_mode`
  from the phone's `carservice` `SharedPreferences` through `ijs`
  (`itq.java:45-63`, `ijs.java:20-23`, and `itq.java:307-324`).
- The settings/configuration manager reads and writes the same logical keys
  through the phone car-service API (`mkg.java:29-67`). The phone settings UI
  maps its three choices to `ON`, `BATTERY_OPTIMIZED`, or `OFF`
  (`mks.java:92-112`). Missing auxiliary/cluster values fall back to phone-side
  flag defaults in `jdr` and `jds`.

No `ChannelDescriptor`, `AVChannel`, `VideoConfig`, SDP scalar, or HU
capability is read in those mode lookups. The HU controls whether it advertises
a CLUSTER descriptor, but no supported HU wire signal was found that assigns
the phone's `cluster_display_mode` or intentionally selects
`BATTERY_OPTIMIZED`.

`mnw.e()` uses the phone settings as policy. When multi-display configuration
is enabled, the master power-saving mode is `ON`, and the cluster mode is
`BATTERY_OPTIMIZED`, it selects `ClusterTurnCardCarActivityService`
(`mnw.java:15-22`). Otherwise it tries the default navigation application's
cluster service, the hard-coded Google Maps cluster service, and finally the
Gearhead turn-card service (`mnw.java:26-41`).

## 3. Service selection does not inspect video geometry

The complete cluster selection function is `mnw.e()` at `mnw.java:15-41`. Its
inputs are phone power settings and navigation-service discovery. It does not
receive a display descriptor and does not inspect resolution, density, legacy
margins, `AdditionalVideoConfig`, or display bounds.

Geometry has separate consumers after the descriptor has been accepted:

- `itq.java:118-140` validates the initial resolution, FPS, density, and codec;
- `itt.java:138-153` selects one `VideoConfig` and computes display bounds;
- `itt.java:274-305` converts `AdditionalVideoConfig` into insets, resize
  policy, and `CarDisplayUiFeatures`; and
- `itt.java:796-856` applies later `UpdateUiConfigRequest` layout changes to
  the existing display endpoint.

These paths configure the renderer that policy already selected. No call from
them into `mnw.e()` or another cluster service-selection branch was found.

## 4. Value 16 is a display UI feature, not an SDP session bit

### `session_configuration` remains four consumed bits

In 17.3, `ServiceDiscoveryResponse` is class `xlx`; field 13 is `xlx.n`.
`dsi.W(...)` reads it at `dsi.java:478-487` and constructs `CarInfo` from
values 1, 2, 4, and 8.

There is no value-16 check in that consumer or another read of `xlx.n` in the
17.3 Gearhead path. The published four-value `SessionConfigurationEnum`
therefore remains the supported static model.

### The distinct `AdditionalVideoConfig` path

`AdditionalVideoConfig.hidden_ui_elements` is a repeated `UIElement` enum in
each video configuration. In 17.3 it is `xml.h`. The conversion path is:

```text
AVChannel.VideoConfig.AdditionalVideoConfig.hidden_ui_elements
  -> xml.h / xmm.UI_ELEMENT_NAVIGATION_TURN_DATA_AVAILABLE (enum value 5)
  -> ity.d lookup (CarDisplayUiFeatures flag 16)
  -> itv.applyAsInt + bitwise OR
  -> CarDisplayUiFeatures.hasClusterTurnCard
```

Source anchors:

- `ity.java:14` — maps the five UI-element enum values to flags 1, 2, 4, 8,
  and 16;
- `itv.java:6-12` and `itt.java:280-287` — convert the repeated enum list into
  a `CarDisplayUiFeatures` bitmask;
- `CarDisplayUiFeatures.java:40-41` — names flag 16 `hasClusterTurnCard`;
- `ovw.java:24-29` — sets `EXTRA_SHOW_TURN_CARD` to the inverse of flag 16;
- `ovv.java:23-34` — reapplies that extra when UI features change; and
- `owa.java:6-27` — binds this behavior to the CLUSTER display controller.

Value 16 therefore does affect cluster turn-card presentation, but it does not
select the cluster activity service. `mnw.e()` selects the service; `ovw`
passes the `EXTRA_SHOW_TURN_CARD` state to the selected and fallback intents.
When `hasClusterTurnCard` is true, the phone passes `false` for
`EXTRA_SHOW_TURN_CARD`. That behavior is consistent with avoiding a duplicate
phone-rendered turn card, but the navigation provider's reaction remains
runtime-unverified.

## Harness guidance

For deterministic experiments:

1. Apply a validated resolution/DPI/display-type profile before connection.
2. Disconnect the AA protocol session and let wireless AA reconnect with a
   fresh SDP.
3. Use `UpdateUiConfigRequest` only for same-endpoint UI-layout experiments;
   do not treat it as descriptor replacement.
4. Record message 26 if observed, but expect only an existing input endpoint
   to accept the update in 17.3.
5. Treat projected map-versus-turn-card service choice as phone policy. Render
   a deterministic native turn summary from semantic navigation messages when
   the product requires HU-controlled behavior.

Runtime capture remains useful to confirm the absence or presence of message
26 in real sessions, the exact activity launch, and how navigation providers
react to `EXTRA_SHOW_TURN_CARD`; it is not required to establish the static
consumer boundaries above.
