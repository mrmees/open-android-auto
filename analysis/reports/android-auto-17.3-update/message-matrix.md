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
| DIR-SEN-8001 | | | | | | | | | open | |
| DIR-SEN-8002 | | | | | | | | | open | |
| DIR-SEN-8003 | | | | | | | | | open | |
| DIR-SEN-8004 | | | | | | | | | open | |
| DIR-RAD-801A | | | | | | | | | open | |
| DIR-RAD-801B | | | | | | | | | open | |
| DIR-RAD-801C | | | | | | | | | open | |
| DIR-RAD-801D | | | | | | | | | open | |
| DIR-RAD-801E | | | | | | | | | open | |
| DIR-RAD-801F | | | | | | | | | open | |
| DIR-RAD-8020 | | | | | | | | | open | |
| DIR-RAD-8021 | | | | | | | | | open | |
| DIR-RAD-8022 | | | | | | | | | open | |
| DIR-RAD-8023 | | | | | | | | | open | |
| ID-AV-F6 | | | | | | | | | open | |
| ID-INPUT-F5 | | | | | | | | | open | |
| ID-CD-F16 | | | | | | | | | open | |
| ID-CD-F17 | | | | | | | | | open | |
| ID-CD-F18 | | | | | | | | | open | |

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

| Raw ID | Exact active old conflict | Higher-ranked 17.3 replacement |
|---|---|---|
| 0x8001 | `oaa/carcontrol/CarControlMessages.proto:14,109-115`, `docs/channels/carcontrol.md:13,21,29`, and `analysis/reports/proto-verification/carcontrol.md:14,26` say HU -> Phone | `iip.java:904-935` builds `xlz` and calls `ixb.k(32769, ...)`; Phone -> HU |
| 0x8002 | proto lines `15,118-125`, channel-doc line `22`, and verification-report lines `15,27` say Phone -> HU | `ixb.java:31-75` parses `xma` and matches its request UUID; HU -> Phone |
| 0x8003 | proto lines `16,128-133`, channel-doc lines `13,23,29`, and verification-report lines `16,28` say HU -> Phone | `iip.java:251-268` builds and sends `xli`; `ixb.java:95-99` separately rejects an inbound copy as unexpected; Phone -> HU |
| 0x8004 | proto lines `17,135-146`, channel-doc line `24`, and verification-report lines `17,29` say Phone -> HU | `ixb.java:100-112` parses `xlj`; `iip.java:727-746` handles the response from the HU; HU -> Phone |
| 0x8005 | proto lines `18,149-155`, channel-doc lines `13,25`, and verification-report lines `18,30` say Phone -> HU | `ixb.java:131-143` parses `xgj`, then `iip.java:603-694` updates phone-side state; HU -> Phone |
| 0x8006 | proto lines `19,158-162`, channel-doc lines `26,29`, and verification-report lines `19,31` say HU -> Phone | `iip.java:568-591` builds and sends `xfw`; `ixb.java:95-99` separately rejects an inbound copy as unexpected; Phone -> HU |
| 0x8007 | proto lines `20,165-169`, channel-doc line `27`, and verification-report lines `20,32` say Phone -> HU | `ixb.java:162-178` parses `xga`, then `iip.java:594-600` replaces phone-side group state; HU -> Phone |
