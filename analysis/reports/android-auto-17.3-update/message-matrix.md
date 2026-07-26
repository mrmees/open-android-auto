# Message Matrix

| Claim | Area | Raw ID | Canonical name | APK class | Phone endpoint action | Normalized direction | Source anchors | 16.x delta | Status | Canonical disposition |
|---|---|---:|---|---|---|---|---|---|---|---|
| DIR-VID-8007 | video | 0x8007 / 32775 | VideoFocusRequest | `xnd` | send: builds focus mode and reason | Phone -> HU | `jdc.java:97-118`; `xnd.java:7-9,28` | 16.x tables say HU -> Phone; 17.3 directly sends. | confirmed-static | Keep name; reverse canonical direction to Phone -> HU. |
| DIR-VID-8008 | video | 0x8008 / 32776 | VideoFocusIndication | `xnb` | receive/parse: applies focus mode and unsolicited flag | HU -> Phone | `jdc.java:73-88,149-170`; `xnb.java:7-9,28` | 16.x tables say Phone -> HU; 17.3 directly parses. | confirmed-static | Keep name; reverse canonical direction to HU -> Phone. |
| DIR-VID-8009 | video | 0x8009 / 32777 | UpdateUiConfigRequest | `xms` | receive/parse: requires field 1 UI config | HU -> Phone | `jdc.java:191-215`; `xms.java:7-8,27`; `xml.java:8-16,38` | Enum calls this `VIDEO_FOCUS_NOTIFICATION`; 16.x video tables use the payload name but say Phone -> HU. | confirmed-static | Replace enum name with `UPDATE_UI_CONFIG_REQUEST`; reverse docs to HU -> Phone. |
| DIR-VID-800A | video | 0x800A / 32778 | UpdateUiConfigRequest | `xms` | send: wraps `xml` UI config in field 1 | Phone -> HU | `jdc.java:125-135`; `xms.java:7-8,27`; `xml.java:8-16,38` | 16.x tables say HU -> Phone; 17.3 directly sends. | confirmed-static | Keep payload/name; reverse canonical direction to Phone -> HU. |
| DIR-VID-800B | video/shared AV | 0x800B / 32779 | AudioUnderflowNotification | none (no payload parsed) | receive: inherited raw ID is shifted to internal 32780 and invokes callback | HU -> Phone | `jca.java:285-286,450-452`; `wru.java:236-237,263-294`; bounded numeric search below | 16.x docs call 0x800B a signal/heartbeat and place AudioUnderflow at 0x800C. | confirmed-static | Move `AUDIO_UNDERFLOW` to 0x800B; remove the heartbeat interpretation. |
| DIR-VID-800C | video | 0x800C / 32780 | ActionTakenNotification | `xex` | send: builds action-type enum field 1 | Phone -> HU | `itt.java:532-553`; `xex.java:7-8,27` | 16.x enum/docs call this AudioUnderflow, HU -> Phone. | confirmed-static | Replace with `ACTION_TAKEN`, Phone -> HU. |
| DIR-VID-800D | video | 0x800D / 32781 | IntegratedOverlayParametersNotification | `xhv` | send: builds repeated overlay-options field 1 | Phone -> HU | `itt.java:625-642`; `xhv.java:7,26`; `xjs.java:7-10,29` | 16.x enum/docs call this ActionTaken, HU -> Phone. | confirmed-static | Replace with `OVERLAY_PARAMETERS`, Phone -> HU. |
| DIR-VID-800E | video | 0x800E / 32782 | IntegratedOverlayStartNotification | `xhw` | receive/parse: forwards display-session ID field 1 to started callbacks | HU -> Phone | `jdc.java:236-253`; `its.java:132-146`; `xhw.java:7-8,27` | Enum says OverlayParameters; 16.x docs say OverlayStart but Phone -> HU. | confirmed-static | Use `OVERLAY_START`; reverse docs to HU -> Phone. |
| DIR-VID-800F | video | 0x800F / 32783 | IntegratedOverlayStopNotification | none (empty payload) | receive: triggers stopped callbacks without parsing payload | HU -> Phone | `jdc.java:273-276`; `its.java:148-160` | Enum says OverlayStart; 16.x docs say OverlayStop but Phone -> HU. | confirmed-static | Use `OVERLAY_STOP`; reverse docs to HU -> Phone. |
| DIR-VID-8010 | video | 0x8010 / 32784 | unresolved-with-bounded-search | none proven | unresolved-with-bounded-search; inherited receive path rejects internal 32785 | — | `jdc.java:278-280`; `jca.java:285-286,454-469`; `wru.java:244-245,301-304`; bounded numeric search below | 16.x enum assigns OverlayStop; 17.3 has only enum/offset bookkeeping and rejects the shifted value in the endpoint path. | deferred | Do not publish the historical name for this slot; leave unnamed/reserved pending direct endpoint or framed evidence. |
| DIR-VID-8011 | video | 0x8011 / 32785 | UiConfigRequest | `xmt` | send: sends theming-token container in field 1 | Phone -> HU | `itt.java:646-650`; `xmt.java:7-8,27`; `xmn.java:7-8,30` | Enum says OverlaySessionUpdate; 16.x docs/report say UiConfigRequest HU -> Phone, while the canonical message proto already says Phone -> HU. | confirmed-static | Use `UI_CONFIG_REQUEST`, Phone -> HU; align docs/report to the existing message proto. |
| DIR-VID-8012 | video | 0x8012 / 32786 | UpdateHuUiConfigResponse | `xmu` | receive/parse: handles theming-token accepted/error/rejected enum | HU -> Phone | `jdc.java:278-297`; `its.java:162-179`; `xmu.java:7-8,27` | Enum says UpdateHuUiConfigRequest; 16.x docs/report say response Phone -> HU, while the canonical response proto already says HU -> Phone. | confirmed-static | Use `UPDATE_HU_UI_CONFIG_RESPONSE`, HU -> Phone; align docs/report to the existing response proto. |
| DIR-VID-8013 | video/shared AV | 0x8013 / 32787 | AVChannelMediaStats | `xim` | receive/parse: inherited raw ID is shifted to internal 32788 and records stats | HU -> Phone | `jca.java:285-286,454-485`; `wru.java:252-253,263-310`; `jer.java:91-124,187-188`; `xim.java:7-22,41` | 16.x video docs/report already use MediaStats HU -> Phone; enum and `UiConfigMessages.proto` instead assign UpdateHuUiConfigResponse here. | confirmed-static | Keep MediaStats and direction; replace conflicting enum/UI-config claims. |
| DIR-VID-8014 | video/shared AV | 0x8014 / 32788 | AVChannelMediaOptions | `xig` | send: PDK-gated 13-field media-options update | Phone -> HU | `jca.java:190-191`; `itt.java:748-755`; `its.java:182-190`; `xig.java:7-20,39` | 16.x video docs/report already use MediaOptions Phone -> HU; enum calls this MediaStats. | confirmed-static | Keep MediaOptions and direction; fix enum name. |
| DIR-VID-8015 | video | 0x8015 / 32789 | CriticalUiNotification | `xgu` | send: builds critical-UI focus enum field 1 | Phone -> HU | `itt.java:609-621`; `xgu.java:7-8,27`; `xgt.java:4-7` | 16.x enum calls this MediaOptions and active video tables omit the critical-UI message. | confirmed-static | Replace with `CRITICAL_UI_NOTIFICATION`, Phone -> HU; add canonical payload/docs coverage. |
| DIR-CC-8001 | car control | 0x8001 / 32769 | SetCarPropertyValueRequest | `xlz` | send: builds property, value, and request UUID | Phone -> HU | `iip.java:904-935`; `xlz.java:7-10,29` | Canonical proto/docs/report say HU -> Phone (Gold in the report); 17.3 directly sends from the phone endpoint. | confirmed-static | Keep ID, name, and schema; reverse canonical direction to Phone -> HU. |
| DIR-CC-8002 | car control | 0x8002 / 32770 | SetCarPropertyValueResponse | `xma` | receive/parse: matches request UUID and dispatches success or error callback | HU -> Phone | `ixb.java:31-75`; `xma.java:7-11,30` | Canonical proto/docs/report say Phone -> HU (Gold in the report); 17.3 directly parses on the phone. | confirmed-static | Keep ID, name, and schema; reverse canonical direction to HU -> Phone. |
| DIR-CC-8003 | car control | 0x8003 / 32771 | RegisterCarPropertyListenersRequest | `xli` | send: builds repeated property subscription; an inbound copy is explicitly unexpected | Phone -> HU | `iip.java:251-268`; `ixb.java:95-99`; `xli.java:7,26` | Canonical proto/docs/report say HU -> Phone (Gold in the report); 17.3 directly sends, while its phone receive branch rejects the ID as unexpected. | confirmed-static | Keep ID, name, and schema; reverse canonical direction to Phone -> HU. |
| DIR-CC-8004 | car control | 0x8004 / 32772 | RegisterCarPropertyListenersResponse | `xlj` | receive/parse: forwards repeated per-property results to registration state | HU -> Phone | `ixb.java:100-112`; `iip.java:727-746`; `xlj.java:7,26`; `xgk.java:7-9,28` | Canonical proto/docs/report say Phone -> HU (Gold in the report); 17.3 directly parses on the phone. | confirmed-static | Keep ID, name, and schema; reverse canonical direction to HU -> Phone. |
| DIR-CC-8005 | car control | 0x8005 / 32773 | CarPropertyChangeEvent | `xgj` | receive/parse: converts and caches property state, then notifies listeners | HU -> Phone | `ixb.java:131-143`; `iip.java:603-694`; `xgj.java:7-10,29` | Canonical proto/docs/report say Phone -> HU (Gold in the report); 17.3 directly parses on the phone. | confirmed-static | Keep ID, name, and schema; reverse canonical direction to HU -> Phone. |
| DIR-CC-8006 | car control | 0x8006 / 32774 | CarActionNotification | `xfw` | send: wraps a car-action ID; an inbound copy is explicitly unexpected | Phone -> HU | `iip.java:568-591`; `ixb.java:95-99`; `xfw.java:7-8,27`; `xdw.java:7-8,27` | Canonical proto/docs/report say HU -> Phone (Gold in the report); 17.3 directly sends, while its phone receive branch rejects the ID as unexpected. | confirmed-static | Keep ID, name, and schema; reverse canonical direction to Phone -> HU. |
| DIR-CC-8007 | car control | 0x8007 / 32775 | CarControlGroupUpdate | `xga` | receive/parse: replaces the group by type and notifies group listeners | HU -> Phone | `ixb.java:162-178`; `iip.java:216-225,594-600`; `xga.java:7-8,27`; `xfz.java:7-9,28` | Canonical proto/docs/report say Phone -> HU (Gold in the report); 17.3 directly parses on the phone. | confirmed-static | Keep ID, name, and schema; reverse canonical direction to HU -> Phone. |
| DIR-SEN-8001 | sensor | 0x8001 / 32769 | SensorRequest | `xlq` | send: builds sensor-type enum and refresh interval, then waits for response | Phone -> HU | `jal.java:15-18,545-597`; `ijm.java:128-149`; `ijl.java:97-106`; `xlq.java:7-10,29` | Canonical proto/channel already agree; the 16.x verification report says HU -> Phone. | confirmed-static | Keep ID, name, schema, and Phone -> HU direction; correct the inverted verification-report row. |
| DIR-SEN-8002 | sensor | 0x8002 / 32770 | SensorStartResponse | `xlr` | receive/parse: consumes status and releases the pending request semaphore | HU -> Phone | `jal.java:15-18,190-226`; `xlr.java:7-9,28` | Canonical proto/channel already agree; the 16.x verification report says Phone -> HU. | confirmed-static | Keep ID, name, schema, and HU -> Phone direction; correct the inverted verification-report row. |
| DIR-SEN-8003 | sensor | 0x8003 / 32771 | SensorEventIndication | `xln` | receive/parse: dispatches 26 repeated sensor-data fields by sensor type | HU -> Phone | `jal.java:15-18,248-252,308-428`; `xln.java:7-33,78-79` | Canonical proto/channel already agree; the 16.x verification report says Phone -> HU. | confirmed-static | Keep ID, name, schema, and HU -> Phone direction; correct the inverted verification-report row. |
| DIR-SEN-8004 | sensor | 0x8004 / 32772 | SensorError | `xlo` | receive/parse: logs sensor type and sensor-error status | HU -> Phone | `jal.java:15-18,253-284`; `xlo.java:7-10,29` | Canonical proto/channel already agree; the 16.x verification report says Phone -> HU. | confirmed-static | Keep ID, name, schema, and HU -> Phone direction; correct the inverted verification-report row. |
| DIR-RAD-801A | radio | 0x801A / 32794 | RadioProgramListNotification | `xku` | receive/parse: dispatches repeated program-info entries | HU -> Phone | `jai.java:23-43`; `xku.java:7,26`; `xks.java:7-10,28` | Canonical proto, catalog, and verification table agree; 17.3 class is `xku` rather than 16.2 `wam`. Channel prose at `docs/channels/radio.md:59` reverses the sender. | confirmed-static | No canonical change to the mapping: keep ID, name, schema, and HU -> Phone; correct the contradictory channel prose. |
| DIR-RAD-801B | radio | 0x801B / 32795 | RadioProgramInfoNotification | `xkt` | receive/parse: dispatches program info, mute state, and audio-focus state | HU -> Phone | `jai.java:63-87`; `xkt.java:7-10,29`; `xks.java:7-10,28` | Canonical proto, catalog, and verification table agree; 17.3 class is `xkt` rather than 16.2 `wal`. Tune/seek prose at `docs/channels/radio.md:406,412` reverses the sender. | confirmed-static | No canonical change to the mapping: keep ID, name, schema, and HU -> Phone; correct the contradictory workflow prose. |
| DIR-RAD-801C | radio | 0x801C / 32796 | RadioMuteRequest | `xko` | send: builds requested mute boolean; inbound copy is unhandled | Phone -> HU | `iji.java:274-287`; `jai.java:106-110`; `xko.java:7-8,27` | Canonical proto, catalog, and verification table agree; 17.3 class is `xko` rather than 16.2 `wag`. Narrative at `docs/channels/radio.md:89,416` reverses the sender. | confirmed-static | No canonical change to the mapping: keep ID, name, schema, and Phone -> HU; correct the contradictory channel prose. |
| DIR-RAD-801D | radio | 0x801D / 32797 | RadioMuteResponse | `xkp` | receive/parse: dispatches confirmed mute state | HU -> Phone | `jai.java:111-130`; `xkp.java:7-8,27` | Canonical proto, catalog, and verification table agree; 17.3 class is `xkp` rather than 16.2 `wah`. Narrative at `docs/channels/radio.md:103,417` reverses the sender. | confirmed-static | No canonical change to the mapping: keep ID, name, schema, and HU -> Phone; correct the contradictory channel prose. |
| DIR-RAD-801E | radio | 0x801E / 32798 | RadioTuneRequest | `xlb` | send: builds program selector with primary and repeated secondary identifiers; inbound copy is unhandled | Phone -> HU | `iji.java:390-415`; `jai.java:106-110`; `xlb.java:7-8,27`; `xkv.java:7-9,28`; `xkr.java:7-10,28` | Canonical proto, catalog, and verification table agree; 17.3 class is `xlb` rather than 16.2 `wat`. Narrative at `docs/channels/radio.md:117,404` reverses the sender. | confirmed-static | No canonical change to the mapping: keep ID, name, schema, and Phone -> HU; correct the contradictory channel prose. |
| DIR-RAD-801F | radio | 0x801F / 32799 | RadioTuneResponse | `xlc` | receive/parse: dispatches tune-status enum, defaulting unset to success | HU -> Phone | `jai.java:149-168`; `xlc.java:7-8,27` | Canonical proto, catalog, and verification table agree; 17.3 class is `xlc` rather than 16.2 `wau`. Narrative at `docs/channels/radio.md:131,405,412` reverses the sender and assigns tuner execution to the phone. | confirmed-static | No canonical change to the mapping: keep ID, name, schema, and HU -> Phone; correct the contradictory workflow/ownership prose. |
| DIR-RAD-8020 | radio | 0x8020 / 32800 | RadioFavoriteListNotification | `xkl` | receive/parse: dispatches repeated favorite program-info entries | HU -> Phone | `jai.java:187-205`; `xkl.java:7,26`; `xks.java:7-10,28` | Canonical proto, catalog, and verification table agree; 17.3 class is `xkl` rather than 16.2 `wad`. Favorite-flow prose at `docs/channels/radio.md:422` reverses the sender. | confirmed-static | No canonical change to the mapping: keep ID, name, schema, and HU -> Phone; correct the contradictory workflow prose. |
| DIR-RAD-8021 | radio | 0x8021 / 32801 | RadioFavoriteToggleRequest | `xky` | send: builds requested favorite boolean | Phone -> HU | `iji.java:349-362`; `xky.java:7-8,27` | Canonical proto, catalog, and verification table agree; 17.3 class is `xky` rather than 16.2 `waq`. Narrative at `docs/channels/radio.md:159,421` reverses the sender. | confirmed-static | No canonical change to the mapping: keep ID, name, schema, and Phone -> HU; correct the contradictory channel prose. |
| DIR-RAD-8022 | radio | 0x8022 / 32802 | RadioTuneDirectionRequest | `xkz` | send: builds tune-direction enum | Phone -> HU | `iji.java:370-387`; `xkz.java:7-8,27` | Canonical proto, catalog, and verification table agree; 17.3 class is `xkz` rather than 16.2 `war`. Narrative at `docs/channels/radio.md:173,411-412` reverses endpoint ownership. | confirmed-static | No canonical change to the mapping: keep ID, name, schema, and Phone -> HU; correct the contradictory workflow prose. |
| DIR-RAD-8023 | radio | 0x8023 / 32803 | RadioSearchRequest | `xkk` | send: builds field-1 search/custom-action string | Phone -> HU | `iji.java:290-303`; `xkk.java:7-8,27` | Canonical ID, name, one-string schema, direction, and search action agree; 17.3 class is `xkk` rather than 16.2 `wac`. | confirmed-static | No canonical change: keep ID, name, schema, Phone -> HU direction, and added-in-16.2 history. |
| ID-AV-F6 | identity / video | field 6 | logical display ID (`display_id`) | `xik.g` | consume: constructs `CarDisplayId`, then one accepted display/video object pair | — | `xik.java:7-17,38`; decoded descriptor proof below; `itq.java:95-111,213-238,286-312` | Canonical field name is `channel_id`, which collides with the separate transport channel ID at `ChannelDescriptor` field 1. | confirmed-static | Rename AV field 6 to `display_id` without changing tag or wire type; it is the logical display ID, not a transport channel ID or GAL service type. |
| ID-INPUT-F5 | identity / input | field 5 | input-to-display binding ID (`display_id`) | `xhs.g` | accept only when field 5 equals the target `CarDisplayId`; topology requires exactly one match per accepted display | — | `xhs.java:7-17,39`; decoded descriptor proof below; `jnb.java:263-308`; `iiv.java:70-76,163-171,254-258` | Canonical input field 5 already says it matches the video display ID. | confirmed-static | Keep `display_id` at tag 5; document it as a reference to AV field 6, distinct from the input descriptor's transport channel ID and service type 8. |
| ID-CD-F16 | descriptor identity | field 16 | CarLocalMedia service marker | `xgi` | presence bit `0x8000` selects `CarLocalMediaService`; endpoint uses GAL service type 20 | — | `xlv.java:7-25,44-45`; `xgi.java:4-25`; `jnb.java:394-397`; `iiy.java:17-29,74-80`; `ixi.java:7-14`; `rpq.java:25,78-79` | The 16.2 `wbm` descriptor has a message field 16, but available indexed evidence does not prove the historical `generic_notification` meaning or a trusted marker lineage. | confirmed-static | **Insufficient evidence** for the 16.2→17.3 compatibility relationship. Keep the source-proven 17.3 CarLocalMedia meaning; do not publish the historical field-16 label as a universal alias or assert semantic reuse. |
| ID-CD-F17 | descriptor identity | field 17 | BufferedMedia service marker | `xfq` | presence bit `0x10000` selects `CAR.MEDIA.BUFFERED`; endpoint uses GAL service type 21 | — | `xlv.java:7-25,44-45`; `xfq.java:4-25`; `jnb.java:403-413`; `isi.java:8-18,47-52`; `jaz.java:7-12`; `rpq.java:26,80-81` | The 16.2 `wbm` descriptor has a message field 17, but available indexed evidence does not prove the historical `voice` meaning or a trusted marker lineage. | confirmed-static | **Insufficient evidence** for the 16.2→17.3 compatibility relationship. Keep the source-proven 17.3 BufferedMedia meaning; do not publish the historical field-17 label as a universal alias or assert semantic reuse. |
| ID-CD-F18 | descriptor identity | field 18 | CarIntent service marker | `xgd` | presence bit `0x20000` selects `CarIntentService`; endpoint uses GAL service type 22 | — | `xlv.java:7-25,44-45`; `xgd.java:4-25`; `jnb.java:398-402`; `iix.java:8-21`; `ixg.java:7-14`; `rpq.java:27,82-83` | The decoded 16.2 `wbm` descriptor ends at field 17; 17.3 `xlv` adds optional message field 18. | confirmed-static | **Compatible addition/removal**: retain CarIntent at tag 18 and document it as added by 17.3 relative to the available 16.2 descriptor. |

## Display, channel, and service identity boundaries

The four numeric domains are independent even when values happen to be equal:

| Domain | Wire/source location | Proven meaning |
|---|---|---|
| Transport channel ID | `ChannelDescriptor` (`xlv`) field 1, member `c` | Required multiplexed service/channel number. `iya.java:116-121` logs it as `Service id`, and `jae.java:231` uses it to identify an existing registered service. It routes framed traffic; it is not a display ID. |
| GAL service type | Endpoint constructor / `rpq` | Semantic endpoint kind carried by `izy.u`: video is 2 (`jdc.java:19-23`), input is 8 (`izh.java:16-18`), CarLocalMedia is 20, BufferedMedia is 21, and CarIntent is 22 (`rpq.java:5-27`). `jae.java:388-391` converts that value through `rpq` when opening the transport channel. It is neither a descriptor tag nor the transport channel ID. |
| Logical display ID | `AVChannel` (`xik`) field 6, member `g` | Stable per-session display identity. The phone constructs `new CarDisplayId(xik.g)` and uses it for the accepted logical display/endpoint objects. |
| Input-to-display binding ID | `InputChannelConfig` (`xhs`) field 5, member `g` | Reference that selects which logical display receives an input descriptor. It must equal the corresponding AV field-6 display ID. |

For video, `itq.java:95-111` first accepts a descriptor with an AV service and
non-empty video configurations. It then reads `xik.g`, constructs
`CarDisplayId`, and builds separate `iti` and `itt` objects for that accepted
video-capable descriptor (`itq.java:213-238,286-312`). This is static logical
display/endpoint construction evidence only. It does not show framed
simultaneous media streams; runtime concurrency remains unobserved.

## Exact AV and input field-number proof

The `xik` protobuf-lite descriptor at `xik.java:38` decodes to fields
`1,2,3,4,6,7,8,9`. Its field-6 entry is optional `uint32`; the descriptor
object order assigns it to member `g`. `itq.java:213-220` reads that exact
member into `i4` immediately before `new CarDisplayId(i4)`. Therefore AV field
6 is the logical display ID despite the current canonical `channel_id` name.

The `xhs` descriptor at `xhs.java:39` decodes to fields `1,2,3,4,5`; its
field-5 entry is optional `uint32` assigned to member `g`. `jnb.java:263-304`
passes each accepted AV `CarDisplayId` into a dedicated `iiv` matcher, and
`iiv.java:163-171` accepts an input descriptor only when `xhs.g` equals that
ID. `jnb.java:305-308` rejects zero or multiple matches. This proves field 5
is an input-to-display binding rather than the descriptor's field-1 transport
channel ID; the successful log prints both values separately at
`iiv.java:254`.

## ChannelDescriptor fields 16–18 across 16.2 and 17.3

| Field | 16.2 evidence | Direct 17.3 chain | Disposition |
|---:|---|---|---|
| 16 | `proto_classes.json` decodes `wbm` as a 17-field descriptor with optional message field 16. The historical canonical comment calls it `generic_notification`/`vwf`, but `proto_unknowns.json` marks `vwf` `insufficient_evidence`, while `16-4-mapping-candidates.md:151` finds no marker lineage. No 16.2 semantic consumer is available. | `xlv` field 16/member `s` is `xgi`; presence bit `32768` is accepted by `iiy`, whose class/import/log semantics are CarLocalMedia; `ixi` constructs endpoint service type 20. | **Insufficient evidence** for the cross-version relationship; 17.3 CarLocalMedia is confirmed. |
| 17 | `proto_classes.json` decodes the same `wbm` descriptor with optional message field 17. The historical comment calls it `voice`/`vvp`, but `proto_unknowns.json` marks `vvp` `insufficient_evidence`, while `16-4-mapping-candidates.md:152` finds no marker lineage. No 16.2 semantic consumer is available. | `xlv` field 17/member `t` is `xfq`; presence bit `65536` is accepted by `isi`, which logs `CAR.MEDIA.BUFFERED` and starts `BUFFERED_MEDIA_WORKER`; `jaz` constructs endpoint service type 21. | **Insufficient evidence** for the cross-version relationship; 17.3 BufferedMedia is confirmed. |
| 18 | The decoded `wbm` descriptor has maximum field 17, so field 18 is absent from the available 16.2 schema. | `xlv` field 18/member `u` is `xgd`; presence bit `131072` is accepted by `iix`/`CarIntentService`; `ixg` constructs endpoint service type 22. | **Compatible addition/removal**: optional CarIntent marker added in 17.3 relative to 16.2. |

The 16.2 evidence paths used above are
`analysis/android_auto_16.2.660604-release_162660604/apk-index/json/proto_classes.json`
(`wbm`, `vwf`, and `vvp` entries), `proto_unknowns.json` (`vwf`/`vvp`), and
`analysis/reports/cross-version/16-4-mapping-candidates.md:151-152`. The older
canonical comments and SDP verification summaries are comparison inputs, not
authority for marker semantics. In particular, an empty-message shape cannot
establish lineage or semantic reuse by itself.

## Video protobuf-lite descriptor evidence

The payload names above come from complete endpoint builder/parser blocks and
the protobuf-lite descriptors, not from `wru` or the current canonical enum.

| Raw ID(s) | APK class | Descriptor field structure |
|---|---|---|
| 32775 | `xnd` | fields 2-3: enum `xna` focus mode, enum `xnc` focus reason (`xnd.java:7-9,28`) |
| 32776 | `xnb` | fields 1-2: enum `xna` focus mode, bool unsolicited (`xnb.java:7-9,28`) |
| 32777, 32778 | `xms` | field 1: message `xml` UI config (`xms.java:7-8,27`); `xml` has eight fields (`xml.java:8-16,38`) |
| 32780 | `xex` | field 1: enum `xey` action type (`xex.java:7-8,27`) |
| 32781 | `xhv` | field 1: repeated message `xjs` overlay options (`xhv.java:7,26`); `xjs` has int32 field 1 and message fields 2-3 (`xjs.java:7-10,29`) |
| 32782 | `xhw` | field 1: int32 display-session ID (`xhw.java:7-8,27`) |
| 32783 | none | empty notification; the endpoint does not parse the supplied `ByteBuffer` (`jdc.java:273-276`) |
| 32785 | `xmt` | field 1: message `xmn`; `xmn` has repeated `xmp` fields 1-2 (`xmt.java:7-8,27`; `xmn.java:7-8,30`) |
| 32786 | `xmu` | field 1: enum theming-token status (`xmu.java:7-8,27`; semantic branches at `its.java:162-179`) |
| raw 32787 -> internal 32788 | `xim` | 15 fields: message field 1; int64 fields 2-4, 9-10, 14-15; message fields 5-8 and 11-13 (`xim.java:7-22,41`) |
| 32788 | `xig` | 13 fields: message fields 1, 3-6, 8, 10, 12-13; bool fields 2, 9, 11; uint32 field 7 (`xig.java:7-20,39`) |
| 32789 | `xgu` | field 1: enum `xgt` critical-UI focus (`xgu.java:7-8,27`; `xgt.java:4-7`) |

## Video bounded search and inherited-ID normalization

The bounded search was one exact decimal search per candidate over
`analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage`, limited to
`*.java`:

```bash
for decimal_id in 32779 32784 32786 32787 32788; do
  rg -n "${decimal_id}" analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage -g '*.java'
done
```

- `32779` occurs only in `wru.java:234,292-293`; `wru.S(32779)` returns the
  internal value `32780`, which `jca.java:450-452` receives as the no-payload
  AudioUnderflow callback.
- `32784` occurs only in `wru.java:244,302-303`. The video handler delegates it
  to the inherited path (`jdc.java:278-280`); after `wru.S` returns internal
  `32785`, `jca.java:454-469` rejects it. No 17.3 endpoint send or payload parser
  was found, so the raw ID is `deferred` rather than assigned the historical
  OverlayStop name.
- `32786` occurs in the direct `jdc.java:278` receive branch and in
  `wru.java:248,306-307`.
- `32787` occurs only in `wru.java:250,308-309`; `wru.S(32787)` returns internal
  `32788`, which selects the `xim` parser at `jca.java:454-485`.
- `32788` occurs in the direct send at `jca.java:191`, the internal receive
  comparison at `jca.java:454`, `wru.java:252,310-311`, and as an unrelated
  substring in negative constant `-1404132788` at `kdv.java:160`.

## Video canonical conflict ledger

Direct 17.3 endpoint evidence outranks the historical enum labels and 16.x
documentation below. These are publication inputs for Task 10; no canonical
proto or channel document is changed in this task.

| Raw ID | Active old claim(s) | Higher-ranked 17.3 replacement |
|---|---|---|
| 0x8007 | `docs/channels/video.md:61` and `analysis/reports/proto-verification/video.md:14`: VideoFocusRequest, HU -> Phone | `jdc.java:97-118`: phone sends `xnd`; Phone -> HU |
| 0x8008 | `docs/channels/video.md:62` and verification report line 15: VideoFocusIndication, Phone -> HU | `jdc.java:149-170`: phone parses `xnb`; HU -> Phone |
| 0x8009 | `AVChannelMessageIdsEnum.proto:25`: VideoFocusNotification; video docs/report lines 63/16: UpdateUiConfigRequest, Phone -> HU | `jdc.java:191-215`: phone parses `xms`; UpdateUiConfigRequest, HU -> Phone |
| 0x800A | video docs/report lines 64/17: UpdateUiConfigRequest, HU -> Phone | `jdc.java:125-135`: phone sends `xms`; Phone -> HU |
| 0x800B | enum/UI-config sources call it UpdateUiConfigReply; video docs/report lines 94/34 call it signal/heartbeat | `wru.S` plus `jca.java:450-452`: received no-payload AudioUnderflowNotification, HU -> Phone |
| 0x800C | enum/video docs/report lines 28/65/18: AudioUnderflow, HU -> Phone | `itt.java:532-553`: phone sends `xex`; ActionTakenNotification, Phone -> HU |
| 0x800D | enum/video docs/report lines 29/66/19: ActionTaken, HU -> Phone | `itt.java:625-642`: phone sends `xhv`; IntegratedOverlayParametersNotification, Phone -> HU |
| 0x800E | enum line 30: OverlayParameters; video docs/report lines 67/20: OverlayStart, Phone -> HU | `jdc.java:236-253`: phone parses `xhw`; OverlayStart, HU -> Phone |
| 0x800F | enum line 31: OverlayStart; video docs/report lines 68/21: OverlayStop, Phone -> HU | `jdc.java:273-276`: phone receives empty OverlayStop, HU -> Phone |
| 0x8010 | enum line 32: OverlayStop | no endpoint branch after the bounded search; deferred and unnamed |
| 0x8011 | enum line 33: OverlaySessionUpdate; video docs/report lines 69/22: UiConfigRequest, HU -> Phone | `itt.java:646-650`: phone sends `xmt`; UiConfigRequest, Phone -> HU (matching `UiConfigRequestMessage.proto:27`) |
| 0x8012 | enum/UI-config sources call it UpdateHuUiConfigRequest; video docs/report lines 70/23 say UpdateHuUiConfigResponse, Phone -> HU | `jdc.java:278-297`: phone parses `xmu`; UpdateHuUiConfigResponse, HU -> Phone (matching `UpdateHuUiConfigResponse.proto:9`) |
| 0x8013 | enum/UI-config sources call it UpdateHuUiConfigResponse, Phone -> HU | `wru.S` plus `jca.java:454-485`: phone parses `xim`; AVChannelMediaStats, HU -> Phone, matching video docs/report lines 95/35 |
| 0x8014 | enum line 36 calls it MediaStats | `jca.java:190-191`: phone sends `xig`; AVChannelMediaOptions, Phone -> HU, matching video docs/report lines 96/36 |
| 0x8015 | enum line 37 calls it MediaOptions | `itt.java:609-621`: phone sends `xgu`; CriticalUiNotification, Phone -> HU |

## Car-control protobuf-lite descriptor evidence

The car-control payload names and directions above come from the complete
builder/parser blocks in the Android Auto 17.3 phone endpoints and the concrete
protobuf-lite descriptors. They are static APK findings, not runtime-capture
claims.

| Raw ID | APK class | Descriptor field structure |
|---|---|---|
| 0x8001 / 32769 | `xlz` | fields 1-3: message `xee` car property, message `xem` property value, string request ID (`xlz.java:7-10,29`) |
| 0x8002 / 32770 | `xma` | fields 1-4: message `xee` car property, enum validated by `xjj.b`/`xin` status, string request ID, int32 error code (`xma.java:7-11,30`; `xjj.java:22,34-35`; `xin.java:6-40,48-125`) |
| 0x8003 / 32771 | `xli` | field 1: repeated message `xee` car properties (`xli.java:7,26`) |
| 0x8004 / 32772 | `xlj` | field 1: repeated message `xgk` listener results (`xlj.java:7,26`); `xgk` contains message `xee` field 1 and `xin` status field 2 (`xgk.java:7-9,28`) |
| 0x8005 / 32773 | `xgj` | fields 1-3: message `xee` car property, message `xem` property value, int32 availability status (`xgj.java:7-10,29`) |
| 0x8006 / 32774 | `xfw` | field 1: message `xdw` car action (`xfw.java:7-8,27`); `xdw` contains enum action ID field 1 (`xdw.java:7-8,27`) |
| 0x8007 / 32775 | `xga` | field 1: message `xfz` control group (`xga.java:7-8,27`); `xfz` contains enum group type field 1 and repeated message `xfy` controls field 2 (`xfz.java:7-9,28`) |

## Car-control phone-endpoint normalization

`ixb.java` is the phone receive/parser endpoint. It directly parses `32770`,
`32772`, `32773`, and `32775`, so those raw messages normalize as HU -> Phone.
The builders in `iip.java` directly call `ixb.k(...)` with `32769`, `32771`,
and `32774`, so those raw messages normalize as Phone -> HU.

The explicit `ixb.java:95-99` receive cases for `32771` and `32774` log
"Received unexpected car control message." Those branches describe unexpected
inbound copies at the phone endpoint; they do not make the direct phone sends
missing wire messages or weaken their Phone -> HU classification.

## Car-control canonical conflict ledger

Direct Android Auto 17.3 endpoint and descriptor evidence outranks the active
16.x comments, documentation, and prior Gold labels below. These dispositions
are inputs for Task 10; this task does not modify canonical car-control files.
The bounded canonical search was reviewed with each matching narrative block;
every stale direction or endpoint-perspective claim is mapped to its affected
ID below. Name/schema-only hits and the direction-free cross-version class
table are not conflicts.

| Raw ID | Exact active old conflict | Higher-ranked 17.3 replacement |
|---|---|---|
| 0x8001 | Proto overview/direction/handler-section/request comments at `oaa/carcontrol/CarControlMessages.proto:10-14,106,109-115`; channel overview, catalog, handler note, request narrative, lifecycle, and correlation note at `docs/channels/carcontrol.md:11,13,21,29,35,45,518-523,545`; verification dispatch/Gold rows at `analysis/reports/proto-verification/carcontrol.md:14,26` say or imply HU -> Phone and HU-owned correlation/state | `iip.java:904-938` builds `xlz`, stores the phone-side callback, and calls `ixb.k(32769, ...)`; Phone -> HU |
| 0x8002 | Proto direction/handler/response comments at `oaa/carcontrol/CarControlMessages.proto:15,23,118-125`; channel pipeline, catalog, handler note, response/correlation narrative, lifecycle, and correlation note at `docs/channels/carcontrol.md:13,22,29,45,49-58,518-523,545`; verification dispatch/Gold rows at `analysis/reports/proto-verification/carcontrol.md:15,27` say or imply Phone -> HU and HU-owned correlation | `ixb.java:31-75` parses `xma` and matches its request UUID in the phone-side callback map; HU -> Phone |
| 0x8003 | Proto overview/direction/unexpected-handler/handler-section/request comments at `oaa/carcontrol/CarControlMessages.proto:10-11,16,24,106,128-133`; channel overview, pipeline, catalog, handler note, request narrative, and subscription workflow at `docs/channels/carcontrol.md:11,13,23,29,64-74,492-498`; verification dispatch/Gold rows at `analysis/reports/proto-verification/carcontrol.md:16,28` say or imply HU -> Phone | `iip.java:251-268` builds and sends `xli`; `ixb.java:95-99` separately rejects an inbound copy as unexpected; Phone -> HU |
| 0x8004 | Proto direction/handler/response comments at `oaa/carcontrol/CarControlMessages.proto:17,23,135-146`; channel catalog, handler note, response/state narrative, and initial-values workflow at `docs/channels/carcontrol.md:24,29,78-93,500-504`; verification dispatch/Gold rows at `analysis/reports/proto-verification/carcontrol.md:17,29` say or imply Phone -> HU and HU-owned registration state | `ixb.java:100-112` parses `xlj`; `iip.java:727-746` handles the response from the HU and updates phone-side registration state; HU -> Phone |
| 0x8005 | Proto overview/direction/handler/event comments at `oaa/carcontrol/CarControlMessages.proto:10-11,18,23,149-155`; channel overview, pipeline, catalog, handler note, event/status narrative, change-mode table, lifecycle, and status note at `docs/channels/carcontrol.md:11,13,25,29,97-109,365-371,506-510,543`; verification dispatch/Gold rows at `analysis/reports/proto-verification/carcontrol.md:18,30` say or imply Phone -> HU and HU-owned event state | `ixb.java:131-143` parses `xgj`, then `iip.java:603-694` updates phone-side state and listeners; HU -> Phone |
| 0x8006 | Proto direction/unexpected-handler/handler-section/action comments at `oaa/carcontrol/CarControlMessages.proto:19,24,106,158-162`; channel overview, catalog, handler note, action narrative, and car-action workflow at `docs/channels/carcontrol.md:11,26,29,113-123,525-529`; verification dispatch/Gold rows at `analysis/reports/proto-verification/carcontrol.md:19,31` say or imply HU -> Phone and phone-side action handling | `iip.java:568-591` builds and sends `xfw`; `ixb.java:95-99` separately rejects an inbound copy as unexpected; Phone -> HU |
| 0x8007 | Proto direction/handler/update comments at `oaa/carcontrol/CarControlMessages.proto:20,23,165-169`; channel catalog, handler note, update/state narrative, dynamic-layout workflow, and replacement note at `docs/channels/carcontrol.md:27,29,127-137,512-516,547`; verification dispatch/Gold rows at `analysis/reports/proto-verification/carcontrol.md:20,32` say or imply Phone -> HU and HU-owned group state | `ixb.java:162-178` parses `xga`, then `iip.java:594-600` replaces phone-side group state; HU -> Phone |

## Sensor protobuf-lite descriptor evidence

The four constants are declared together at `jal.java:15-18`. Their use in the
phone endpoint proves one send and three receive paths without relying on the
older direction labels. `ijm.java:128-149` initiates sensor subscriptions,
`ijl.java:97-106` forwards them to `jal.s(...)`, and `jal.java:545-597` builds
and sends the request before waiting for the response semaphore.

| Raw ID | APK class | Descriptor field structure |
|---|---|---|
| 0x8001 / 32769 | `xlq` | required enum sensor type field 1 and required int64 refresh interval field 2 (`xlq.java:7-10,29`) |
| 0x8002 / 32770 | `xlr` | required status enum field 1 (`xlr.java:7-9,28`) |
| 0x8003 / 32771 | `xln` | 26 repeated message fields: `xid`, `xgp`, `xmc`, `xlm`, `xjq`, `xhf`, `xju`, `xhh`, `xgx`, `xjp`, `xhc`, `xhn`, `xhb`, `xgw`, `xjv`, `xgz`, `xic`, `xmf`, `xeu`, `xhl`, `xhk`, `xmg`, `xeq`, `xmj`, `xlg`, and `xle` (`xln.java:7-33,41-68,78-79`) |
| 0x8004 / 32772 | `xlo` | required sensor-type enum field 1 and required sensor-error-status enum field 2 (`xlo.java:7-10,29`) |

## Sensor phone-endpoint normalization and conflicts

`jal.java:545-591` calls the inherited endpoint send with constant `h = 32769`,
so SensorRequest is Phone -> HU. The same phone endpoint parses
constant `g = 32770` as `xlr` (`jal.java:192-226`), constant `i = 32771` as
`xln` (`jal.java:248-252,308-428`), and constant `j = 32772` as `xlo`
(`jal.java:253-284`), so those three messages are HU -> Phone.

The message proto comments and channel documentation already express the 17.3
directions: `SensorRequestMessage.proto:6-12`,
`SensorStartResponseMessage.proto:6-12`,
`SensorEventIndicationMessage.proto:6-14`,
`SensorErrorMessage.proto:6-14`, and `docs/channels/sensor.md:47-51,61-95`.
Only the active verification table is inverted:

| Raw ID | Exact active old conflict | Higher-ranked 17.3 replacement |
|---|---|---|
| 0x8001 | `analysis/reports/proto-verification/sensor.md:13` says SensorRequest is HU -> Phone | `jal.java:545-591` builds `xlq` and sends it; Phone -> HU |
| 0x8002 | verification report line 14 says SensorStartResponse is Phone -> HU | `jal.java:192-226` parses `xlr` and releases the phone's waiter; HU -> Phone |
| 0x8003 | verification report line 15 says SensorEventIndication is Phone -> HU | `jal.java:308-428` parses `xln` and dispatches all 26 sensor fields; HU -> Phone |
| 0x8004 | verification report line 16 says SensorError is Phone -> HU | `jal.java:253-284` parses `xlo` and logs its sensor/error enums; HU -> Phone |

## Radio protobuf-lite descriptor evidence

The radio names come from the endpoint's named parser failures and structural
matches to the current schemas. The five request builders in `iji.java` send
through `jai.k(...)`; the five notification/response branches in `jai.java`
parse the supplied `ByteBuffer` on the phone.

| Raw ID | APK class | Descriptor field structure |
|---|---|---|
| 0x801A / 32794 | `xku` | repeated `xks` RadioProgramInfo field 1 (`xku.java:7,26`); `xks` has selector and metadata message fields 1-2 (`xks.java:7-10,28`) |
| 0x801B / 32795 | `xkt` | `xks` program-info field 1, bool mute field 2, bool audio-focus field 3 (`xkt.java:7-10,29`) |
| 0x801C / 32796 | `xko` | bool mute field 1 (`xko.java:7-8,27`) |
| 0x801D / 32797 | `xkp` | bool mute-state field 1 (`xkp.java:7-8,27`) |
| 0x801E / 32798 | `xlb` | `xkv` program-selector field 1 (`xlb.java:7-8,27`); selector has `xkr` primary field 1 and repeated `xkr` secondary field 2 (`xkv.java:7-9,28`); identifier has enum type field 1 and uint64 value field 2 (`xkr.java:7-10,28`) |
| 0x801F / 32799 | `xlc` | tune-status enum field 1 (`xlc.java:7-8,27`) |
| 0x8020 / 32800 | `xkl` | repeated `xks` RadioProgramInfo field 1 (`xkl.java:7,26`) |
| 0x8021 / 32801 | `xky` | bool favorite-state field 1 (`xky.java:7-8,27`) |
| 0x8022 / 32802 | `xkz` | tune-direction enum field 1 (`xkz.java:7-8,27`) |
| 0x8023 / 32803 | `xkk` | string search/custom-action field 1 (`xkk.java:7-8,27`) |

## Radio phone-endpoint normalization

`jai.java:23-205` parses `32794`, `32795`, `32797`, `32799`, and `32800`,
normalizing RadioProgramListNotification, RadioProgramInfoNotification,
RadioMuteResponse, RadioTuneResponse, and RadioFavoriteListNotification as HU
-> Phone. Its `32796` and `32798` receive cases fall through to the unhandled
branch (`jai.java:106-110`), consistent with the direct phone sends.

`iji.java:274-302,349-415` builds and sends `32796`, `32798`, and `32801`
through `32803`, normalizing RadioMuteRequest, RadioTuneRequest,
RadioFavoriteToggleRequest, RadioTuneDirectionRequest, and RadioSearchRequest
as Phone -> HU. This is evidence for an Android Auto control/status bridge to
HU-managed radio functionality. It does not establish an RF tuner
implementation on the phone and says nothing about backup-camera behavior.

## Radio canonical agreement and prose-conflict ledger

The active protocol mapping agrees with 17.3 for all ten rows: the IDs, names,
directions, and top-level wire shapes at
`oaa/radio/RadioMessages.proto:19-28,158-233`, the catalog at
`docs/channels/radio.md:31-53`, and the verification table at
`analysis/reports/proto-verification/radio.md:8-29` are mutually consistent.
Therefore every radio row records **no canonical mapping change**; the `x*`
class names are 17.3 obfuscation drift, not protocol changes.

The same channel document contains later endpoint-perspective prose that does
not agree with its own catalog. Task 10 must correct these narrative conflicts
without reversing the already-correct canonical mapping:

| Raw ID(s) | Exact active prose conflict | 17.3 disposition |
|---|---|---|
| 0x801A | `docs/channels/radio.md:59` says the phone sends the program list | HU sends; phone parses `xku` at `jai.java:25-43` |
| 0x801B | tune/seek flow at channel-doc lines 406 and 412 says the phone sends program-info updates | HU sends; phone parses `xkt` at `jai.java:63-87` |
| 0x801C / 0x801D | message prose and mute flow at channel-doc lines 89, 103, and 416-417 reverse both request and response | phone sends `xko` (`iji.java:274-287`); phone parses HU response `xkp` (`jai.java:111-130`) |
| 0x801E / 0x801F | message prose and tune/seek flow at channel-doc lines 117, 131, 404-405, and 411-412 reverse request/response ownership and claim the phone tunes radio hardware | phone sends `xlb` (`iji.java:390-415`); phone parses HU status `xlc` (`jai.java:149-168`); remove the unsupported phone-RF implementation claim |
| 0x8020 / 0x8021 | favorite prose/flow at channel-doc lines 159 and 421-422 reverses toggle and list senders | phone sends `xky` (`iji.java:349-362`); phone parses HU list `xkl` (`jai.java:187-205`) |
| 0x8022 | seek prose/flow at channel-doc lines 173 and 411-412 says the HU sends the direction request and the phone performs the seek | phone sends `xkz` (`iji.java:370-387`); the static endpoint evidence does not prove a particular response pairing |
| 0x8023 | Catalog and payload narrative at channel-doc lines 51 and 185-195 agree with the phone send; line 494 is a separate UI/service forwarding statement and must not be read as the wire direction | no canonical change; phone sends field-1 string in `xkk` (`iji.java:290-303`) |

The separate timeout wording at `docs/channels/radio.md:520` also refers to
"the phone's radio hardware". The endpoint evidence supports only a timeout in
the phone-side service while awaiting the HU-managed radio result; it does not
support phone-owned RF hardware.
