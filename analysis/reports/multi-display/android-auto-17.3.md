# Android Auto 17.3 Multi-display Architecture

Date: 2026-07-24
Target: Android Auto `17.3.662804-release` (`173662804`)
APK bundle SHA-256:
`1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344`

## Conclusion

Android Auto models multiple screens as independent logical display instances.
It does **not** render one panoramic canvas and ask the head unit to crop a
section for each physical screen.

For each video-capable descriptor accepted by the static 17.3 construction
path, Android Auto constructs a distinct `CarDisplayId`, display type,
video-service object, Android `Surface`, video endpoint, video configuration
set, encoder state, focus state, and matching input route. The descriptor and
endpoint objects are separate; concurrent media-stream behavior is
runtime-unverified until framed runtime evidence is captured.

AA can still partition the UI *within one display*. Insets, margins, Coolwalk
regions, native UI elements, and blended-UI geometry modify a single display's
composition; they are not the mechanism for routing content to another display.

## Durable local artifacts

The complete bundle and decompile are preserved outside Git tracking at:

```text
analysis/aa_apk_17.3.662804_apkm/
  PROVENANCE.md
  input/android-auto-17.3.662804-release.apkm
  input/base.apk
  input/info.json
  jadx-output/resources/AndroidManifest.xml
  jadx-output/sources/
```

The ignored directory is intentionally version-scoped and contains enough
provenance to reproduce the analysis. This report preserves the findings in a
small reviewable artifact suitable for Git.

## 17.3 source trace

### 1. One factory result per accepted video descriptor

`defpackage/itq.java` consumes a `ChannelDescriptor` (`xlv`) containing an
`AVChannel` (`xik`). It validates the channel's `VideoConfig` list (`xmz`), then
reads:

- `xik.g` as the numeric display ID
- `xik.h` as `DisplayType` (`xgy`)

It constructs a new `CarDisplayId`, display bridge (`iti`), and video service
(`itt`) for that descriptor, then stores the pair in its display list.

Source anchors:

- `itq.java:86-111` — video-capable descriptor and config extraction
- `itq.java:213-238` — display ID/type conversion and `iti` construction
- `itq.java:286-312` — per-display `itt` construction and registration
- `itq.java:310-324` — independent CLUSTER/AUXILIARY power-saving policy

### 2. Each display service owns a surface and video state

`defpackage/itt.java` is instantiated once per display. Its fields include:

- `jdc f` — the display's video protocol endpoint
- `ydr i` — the display's video configuration list
- `xgy n` — the display type
- `int o` — the display ID
- `ivg g` — video encoder state
- `Surface v` — the display's composition/encoding surface
- per-instance focus and lifecycle state

`itt.b(...)` creates a `jdc` endpoint using this instance's display type and
configuration. `defpackage/its.java:26-39` receives and stores the `Surface` for
that specific `itt` instance; `its.java:77-86` enables that display independently.

Source anchors:

- `itt.java:25-62` — per-instance video/display fields
- `itt.java:65-102` — constructor captures configs, display type, and ID
- `itt.java:466-479` — endpoint factory passes the instance's display type
- `its.java:26-39` — per-instance surface delivery
- `its.java:77-86` — per-instance display enablement

### 3. Video endpoint and focus are display-scoped

`defpackage/jdc.java` receives a `DisplayType` in its constructor, records
whether that endpoint is MAIN, and owns its own video/input focus state. Its
endpoint type maps as:

```text
MAIN      -> VIDEO
CLUSTER   -> VIDEO_CLUSTER
AUXILIARY -> VIDEO_AUXILIARY
```

Source anchors:

- `jdc.java:19-25` — endpoint constructed with one display type
- `jdc.java:32-95` — endpoint-local input/video focus transitions
- `jdc.java:338-369` — focus gained for the endpoint's display type
- `jdc.java:372-377` — MAIN/CLUSTER/AUXILIARY endpoint mapping

Video focus selects projected versus native ownership of one logical display.
It does not select a crop from a combined framebuffer.

### 4. Composition is bound to one `CarDisplayId`

`defpackage/iti.java` stores one `CarDisplayId` and one `DisplayType`. When its
surface becomes available, it starts composition against that surface and
notifies the display manager using that same ID.

Source anchors:

- `iti.java:19-48` — display object fields and constructor
- `iti.java:124-160` — surface composition and display-ID notification

### 5. The phone validates a real display topology

`defpackage/jnb.java` validates the complete display set after the per-display
factory has run:

- at least one display must exist
- display IDs must be unique
- display ID `0` must exist and be MAIN
- exactly one MAIN is allowed
- at most one CLUSTER is allowed
- each display must resolve to exactly one matching input configuration

Source anchors:

- `jnb.java:223-250` — display existence, ID, MAIN, and CLUSTER constraints
- `jnb.java:251-308` — per-display registration and input matching
- `jnb.java:513` — at-most-one-CLUSTER failure

These checks would not make sense for a single panoramic stream with HU-side
cropping; they describe independent logical display objects.

### 6. Blended UI is intra-display composition

`AdditionalVideoConfig` (`xml`) still controls geometry within one display.
`itt.A()` converts its inset messages and blended-UI subtree into Android
`Rect`, `CarDisplayUiFeatures`, `CarDisplayCornerRadii`, and
`CarDisplayBlendedUiConfig` objects before creating that display's parameters.

Source anchors:

- `itt.java:139-150` — selected config and display bounds
- `itt.java:255-350` — insets, resize policy, native elements, corner radii,
  and blended-UI construction

This is the part of AA that can reserve native chrome or arrange multiple
Coolwalk regions on one screen. It should not be conflated with physical
multi-display routing.

The follow-up [runtime cluster policy report](android-auto-17.3-runtime-cluster-policy.md)
traces live descriptor-update limits, phone-side power policy, geometry versus
service selection, and the distinct cluster-turn-card UI-feature flag.

## Projected displays versus native semantic displays

Two useful architectures coexist:

1. **Projected display:** MAIN, CLUSTER, or AUXILIARY accepted by the static
   construction path gets its own video endpoint. Concurrent encoded
   media-stream behavior is runtime-unverified; cluster and auxiliary projection
   are primarily navigation/turn-card surfaces in the static evidence.
2. **Native HU widget:** the HU consumes navigation, media, and phone-status
   protobufs and renders its own cluster or secondary UI without a projected
   video stream.

The 17.3 manifest retains dedicated secondary, cluster, and auxiliary services:

- `SecondaryScreenTurnCardCarActivityService`
- `PrototypeAuxiliaryDisplayNavigationCarActivityService`
- `PrototypeAuxiliaryDisplayTurnCardCarActivityService`
- `AuxiliaryDisplayNavigationCarActivityService`
- `AuxiliaryDisplayTurnCardCarActivityService`
- `ClusterTurnCardCarActivityService`
- `TemplateClusterService`
- `TemplateAuxiliaryDisplayService`

See `jadx-output/resources/AndroidManifest.xml:565-640` and `:822-837`.

## OpenAuto Prodigy direction

Prodigy should use a display registry, not a panoramic framebuffer contract:

```text
DisplayRegistry
  DisplaySession(display_id=0, type=MAIN)
    VideoEndpoint + decoder + sink + focus + input route
  DisplaySession(display_id=N, type=CLUSTER)
    VideoEndpoint + decoder + sink + focus + input route
  DisplaySession(display_id=M, type=AUXILIARY)
    VideoEndpoint + decoder + sink + focus + input route
```

If several logical displays are physically regions of one Linux framebuffer,
Prodigy may composite their decoded surfaces locally. That remains a Prodigy
renderer choice; Android Auto must still see separate display IDs and channels.

A low-risk delivery sequence is:

1. Native semantic cluster widgets from existing navigation/media/phone data.
2. A `DisplayRegistry` and per-display SDP/input model.
3. A second independent video channel and decoder sink for CLUSTER.
4. AUXILIARY projection and independent focus/input handling.
5. Optional local composition of logical sinks onto shared physical hardware.

## Remaining verification work

Static 17.3 source now proves the phone-side object and endpoint model. The next
high-value tests are runtime/wire observations:

1. Capture MAIN + CLUSTER + AUXILIARY and record distinct channel IDs, AV setup
   handshakes, and media NAL streams.
2. Toggle focus independently and verify which encoder/stream pauses.
3. Record `CarDisplayId` and activity-service launches in logcat.
4. Capture the selected CLUSTER/AUXILIARY activity and navigation provider's
   response to `EXTRA_SHOW_TURN_CARD`; the static selection and UI-feature
   paths are now traced separately.
5. Measure Prodigy's concurrent decoder and compositor budget on target hardware.

The fresh durable-tree schema run also surfaced a small unrelated catalog delta:
176 resolved mappings/135 dispatch observations versus the committed
175/129 baseline. Its outputs are retained under the ignored local
`analysis/aa_apk_17.3.662804_apkm/validation/` directory for triage. They must
not replace the canonical report until the `BluetoothChannel`,
`PhoneConnectionConfig`, and `WifiInfoResponse` differences are reviewed.

## Reproduction

```bash
# Confirm artifact identity
sha256sum \
  analysis/aa_apk_17.3.662804_apkm/input/android-auto-17.3.662804-release.apkm \
  analysis/aa_apk_17.3.662804_apkm/input/base.apk

# Re-run schema extraction/matching from the durable JADX tree
PYTHONPATH=. python3 -m analysis.tools.proto_schema_matcher.run \
  --jadx-root analysis/aa_apk_17.3.662804_apkm/jadx-output \
  --version 17.3.662804-release \
  --apk-sha256 1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344 \
  --lineage-yaml analysis/lineage/android-auto-17.3.yaml \
  --output-json analysis/aa_apk_17.3.662804_apkm/validation/17-3-schema-match-fresh.json \
  --output-md analysis/aa_apk_17.3.662804_apkm/validation/17-3-schema-match-fresh.md
```
