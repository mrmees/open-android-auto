# GAL Version Gates Above 4.3

Date: 2026-07-26

Target: Android Auto `17.3.662804-release` (`173662804`)

Evidence type: static phone-side source trace; runtime behavior remains to be
captured

## Decision

For Prodigy's cluster-turn-card work, request **GAL 4.3 first**, not 6.1.
Version 4.3 is the narrowest request that makes Android Auto consume
`AdditionalVideoConfig.hidden_ui_elements`, including the
`hasClusterTurnCard` signal. Higher requested versions activate unrelated audio,
navigation, and video behavior that the head unit must tolerate or implement.

Android Auto 17.3 supports a response ceiling of 6.1, but that response does
not replace the request as the feature selector. The phone:

1. stores the raw HU-requested version;
2. responds with 1.7 for requests through 1.7, otherwise 6.1; and
3. copies the raw requested major/minor into `CarInfo`, whose fields drive the
   gates below.

Consequently, a 4.3 request receives a 6.1 response while still selecting the
4.3 feature set in the inspected code. A request above 6.1 is not useful: the
phone logs that it exceeds the supported maximum, caps the response at 6.1,
and still retains the excessive raw request for feature comparisons.

Source anchors:

- `defpackage/iyk.java:24-26,123-148` — 1.6, 1.7, and 6.1 constants; raw
  request storage and response selection
- `defpackage/iyk.java:231-265` — raw request forwarded after SDP
- `defpackage/dsi.java:478-491` — raw version placed in `CarInfo.e/f`
- `defpackage/jaf.java:22-42` — lexicographic version comparison and `>=` helper

All source paths in this report are relative to
`analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/`.

## Gate matrix

| HU-requested GAL version | Phone-side behavior newly selected | Head-unit consequence |
|---|---|---|
| 4.3 | `AdditionalVideoConfig.resize_actions` and `hidden_ui_elements` become the display-policy inputs. The five UI values map to clock, battery, phone signal, native-UI affordance, and cluster-turn-card flags. The legacy `session_configuration` derivation is no longer used for those flags. | This is the required and sufficient gate for the current cluster-turn-card experiment. Advertise only UI elements the HU actually renders. `UpdateUiConfigRequest` also takes the 4.3+ handling path. |
| 4.5 | A `KEYCODE_TEL` press takes the newer direct dialer-launch path instead of the pre-4.5 call-state/recent-call suppression loop. | No new GAL wire message was found at this threshold, but phone-key UX changes. This does not help the cluster feature. |
| 5.0 | Audio becomes ackless; audio start indications add session type and media configuration/options; a feature-flagged validator rejects a display containing more than one video codec type. | Do not request 5.0 until Prodigy works without per-frame `AVMediaAckIndication`, accepts the extended `AVChannelStartIndication`, and advertises a single codec type per display. |
| 5.1 | Standalone audio `MediaOptions` updates (`0x8014`) are permitted, and navigation may send `VehicleEnergyForecast` (`0x8008`). | The channel dispatchers must accept these phone-to-HU message IDs and parse or safely ignore their payloads. This adds no known benefit to cluster turn-card selection. |
| 6.0 | The phone selects its PDK-6 media-options construction path; video start/focus can carry media options and video accepts standalone `MediaOptions` updates. The H.265 encoder-capability path is enabled when the HU advertises H.265. Additional frame-accounting and internal presentation feature paths also change. | Before requesting 6.0, make video handling tolerant of the 13-field media-options envelope and its updates. Advertise H.265 only if the decoder and the full video path support it. Do not treat H.265 as mandatory merely because 6.0 was requested. |
| 6.1 | No explicit requested-version feature branch at exactly 6.1 was found in the 17.3 source tree. It is the phone's maximum version response. | There is no evidenced Prodigy benefit over 6.0 yet. Treat 6.1 as a ceiling, not proof that every 6.x behavior is implemented. |

## Evidence by threshold

### GAL 4.3: display policy

- `defpackage/itt.java:277-299` branches on requested version 4.3 and maps
  `AdditionalVideoConfig` resize actions and hidden UI elements into
  `CarDisplayUiFeatures`.
- `defpackage/itt.java:796-867` branches runtime `UpdateUiConfigRequest`
  handling at 4.3.
- The detailed flag and cluster-service trace is in
  `analysis/reports/multi-display/android-auto-17.3-runtime-cluster-policy.md`.

### GAL 4.5: phone hardware key

- `defpackage/xbz.java:74-95` branches `KEYCODE_TEL` handling at 4.5. The
  4.5+ branch launches the dialer directly; the older branch first inspects
  active and very recent calls.

This is the main GAL version. A different 4.5 threshold also appears in the
wireless projection setup classes (`defpackage/peu.java` and `pef.java`). That
is a separate WPP/RFCOMM version namespace and must not be counted as a GAL 4.5
feature.

### GAL 5.0: audio transport and richer start indication

- `defpackage/ipq.java:154-164` enables ackless audio for requested major
  version 5 or newer.
- `defpackage/iom.java:95-109` enables the corresponding audio endpoint mode.
- `defpackage/ipe.java:371-400` and `ipt.java:118-145` add session type and
  media configuration/options to audio `AVChannelStartIndication` at major 5.
- `defpackage/itq.java:142-146` rejects multiple video codec types for 5.0+
  when its rollout flag is enabled.

Ackless mode means `AVMediaAckIndication` is no longer required for the phone
to continue streaming. A robust implementation may remain able to receive or
send legacy acknowledgements, but it must not depend on acknowledgement-driven
flow control after advertising 5.0+.

### GAL 5.1: asynchronous media and EV navigation messages

- `defpackage/ipe.java:541-551` suppresses audio `MediaOptions` below 5.1 and
  sends it at 5.1+.
- `defpackage/ipt.java:157-164` applies the same 5.1 gate in the alternate
  audio path.
- `defpackage/ija.java:1101-1117` suppresses `VehicleEnergyForecast` below
  5.1 and sends message `0x8008` at 5.1+.

`AVChannelMediaOptions` has a proven 13-field wire shape in
`oaa/av/AVChannelMediaOptionsMessage.proto`, but most field semantics remain
unresolved. `VehicleEnergyForecast` is documented in
`oaa/navigation/VehicleEnergyForecastMessage.proto`.

### GAL 6.0: video and modern media options

- `defpackage/iky.java:11-15,17-37,125-140` selects a different media-options
  builder at major 6 and adds fields not populated on the legacy path.
- `defpackage/itq.java:41-68,151-207` enables the PDK-6 H.265 encoder path and
  probes H.265 only when the HU's display configuration advertises it.
- `defpackage/iub.java:88-107` includes media options in a video start/focus
  indication at 6.0+.
- `defpackage/its.java:182-190` accepts standalone video `MediaOptions` updates
  only at 6.0+.
- `defpackage/ils.java:309,1005-1023` changes frame timing/accounting behavior
  at 6.0+.
- `defpackage/iwo.java:344-366` uses requested major 6 plus H.265 as one
  eligibility condition for a newer video-app path, subject to Android build
  and rollout flags.

The 6.0 gates are conditional as well as versioned. Phone capability, HU
advertisement, device build, and server-side/rollout flags can all prevent a
path from activating. Version 6.0 alone is therefore not a promise that H.265
or projected video apps will be used.

## Recommended Prodigy rollout

1. Change only the request from the current 1.1 to 4.3.
2. Advertise the exact `hidden_ui_elements` values Prodigy owns, including
   cluster turn-card value 5 only when the HU renders that card.
3. Capture the version request/response, SDP, video configuration, cluster
   launch state, and any protocol error.
4. Add 5.0 compatibility only after ackless audio and extended start-indication
   tests pass.
5. Add 5.1 and 6.0 in separate steps with unknown-message tolerance and media
   options coverage. Do not jump directly to 6.1.

## Confidence and limits

The listed gates are direct static branches in Android Auto 17.3. They prove
that the phone changes behavior based on the raw requested version; they do not
prove that every branch will run on every phone. Feature flags, phone codec
support, Android SDK level, vehicle identity, and the HU's advertised SDP
capabilities remain additional conditions. A framed runtime capture is still
required before calling any higher-version Prodigy path production-safe.
