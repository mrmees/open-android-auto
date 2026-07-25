# Services Matrix

| Claim | Service | Question | Evidence anchors | Finding | Runtime status | Status | Canonical disposition |
|---|---|---|---|---|---|---|---|
| SVC-CI-DESCRIPTOR | CarIntent | Which descriptor member and service type identify the service? | `xlv.java:23-25,44-45`; `xgd.java:4-25`; `iix.java:12-26`; `rpq.java:27,82-83` | `ChannelDescriptor` field 18 is the empty `xgd` CarIntent marker. Its presence bit is `131072` (`0x20000`), and the accepted endpoint uses GAL service type 22 (`CAR_INTENT`). | Static APK evidence only; no framed descriptor capture. | confirmed-static | Carry field 18/service type 22 into the Task 10 manifest decision; do not create canonical CarIntent files before that gate. |
| SVC-CI-ENDPOINT | CarIntent | Which side parses the payload, and what happens after parsing? | `jnb.java:398-402`; `jae.java:133-158`; `iix.java:16-26`; `ixg.java:12-35` | The phone constructs the type-22 endpoint for an accepted field-18 descriptor. `ixg.a(...)` parses `xgc` from the incoming buffer, logs the field-2 value as NAVIGATE metadata, and invokes registered callbacks. Normalized direction: HU -> Phone. | Static receive-path evidence only; no runtime message capture or callback observation. | confirmed-static | Document the HU -> Phone receive/consumer chain as a manifest candidate; do not infer a response or acknowledgement. |
| SVC-CI-ID | CarIntent | What raw message ID carries the incoming payload? | `ixg.java:17-35`; bounded searches over all 17.3 `sources/defpackage/*.java`, then all 17.3 `resources` and `sources`, recorded below | The incoming raw-ID parameter is unused by `ixg.a(int, ByteBuffer)`. No sender-side enum, dispatcher comparison, numeric send call, or resource mapping ties `xgc`/CarIntent to a raw ID. | Runtime-unverified; no framed traffic is available to supply the ID. | deferred | Publish the raw message ID as unknown. Do not invent conventional `0x8001`. |
| SVC-CI-SCHEMA | CarIntent | Which payload fields are wire-proven? | `xgc.java:4-8,19-28`; repository RawMessageInfo decoder `analysis/tools/apk_indexer/extract.py:50-218`; `ixg.java:20-29` | The RawMessageInfo literal decodes as proto2 with one optional field: field 2, type `string` (protobuf wire type 2, tag byte `0x12`), assigned to member `b`. The consumer logs that member as NAVIGATE metadata. `NAVIGATE` is a fixed log label, not a decoded wire enum. | Static schema/consumer evidence only; payload bytes were not captured. | confirmed-static | Publish only an optional field-2 string payload at the manifest gate. Do not assign field 1, add an intent-type enum, acknowledgement, or response flow. |
| SVC-CI-GATE | CarIntent | What activates or suppresses endpoint construction? | `acla.java:8-21`; `acky.java:4-20`; `dme.java:1232-1233`; `jnb.java:398-402`; `jae.java:133-158`; `iix.java:16-21` | `AdasRouteInfoFeature__car_intent_enabled` is declared with default `false` and exposed by `acky.d()`, but the bounded factory path contains no read of that flag: `jnb` constructs `iix` unconditionally, `jae.a(...)` asks it to match discovered descriptors, and `iix.a(...)` accepts only when bit `0x20000` is present. Descriptor absence suppresses construction; descriptor presence accepts it. | Default and factory behavior are static decompile evidence; effective server-side flag value and live activation were not observed. | confirmed-static | Document both the false default and the actual descriptor-presence gate. Do not claim the named feature flag controls this factory path. |
| SVC-CLM-STATE5 | CarLocalMedia | What does playback-state numeric value 5 mean? | `xgh.java:8-12,30-32`; `syn.java:88-89`; `a.java:367-384`; `iiy.java:41-60`; complete bounded search over `syn`, `xgh`, `ixi`, `iiy`, and all 17.3 `sources/**/*.java`, recorded below | `xgh` field 1/member `d` accepts numeric values 1 through 5, and the phone passes the validated integer to `CarLocalMediaPlaybackStatus` unchanged. No unobfuscated enum or state-specific branch names value 5. The unrelated BufferedMedia `xkf` enum must not be borrowed. | Runtime-unverified; no framed value-5 payload or client interpretation was observed. | deferred | Keep the wire value as numeric `5`; do not publish a semantic label unless runtime or unobfuscated source evidence resolves it. |
| SVC-CLM-FLOW | CarLocalMedia | What are the endpoint IDs, payloads, actions, and directions? | `ixi.java:8-14,20-40,42-103,122-137`; `iiy.java:32-60,74-85,98-140,178-181`; `xgh.java:8-12,30-32`; `xgf.java:7-12,30-32`; `xgg.java:7-8,26-28`; `xge.java:4-33`; `rpq.java:25,78-81` | Service type 20 parses `0x8001` as `xgh` playback status and caches/notifies callbacks, parses `0x8002` as `xgf` playback metadata and caches/notifies callbacks, and builds `xgg` from a phone app's `CarLocalMediaPlaybackRequest` action for send as `0x8003`. Normalized directions: `0x8001`/`0x8002` HU -> Phone; `0x8003` Phone -> HU. An inbound `0x8003` is recognized but explicitly unexpected. | Static endpoint evidence only; runtime activation, frames, and callback delivery are unverified. | confirmed-static | Carry the three ID/payload/direction facts to the Task 10 manifest; retain the canonical files until that publication gate and do not infer acknowledgements. |
| SVC-BUF-DESCRIPTOR | BufferedMedia | Which descriptor member and service type identify the service? | `xlv.java:23-25,44-45`; `xfq.java:4-25`; `isi.java:8-18`; `jaz.java:7-12`; `rpq.java:26,80-81` | `ChannelDescriptor` field 17 is the empty `xfq` BufferedMedia marker. Its presence bit is `65536` (`0x10000`), and the endpoint uses GAL service type 21 (`BUFFERED_MEDIA_SINK`). | Static APK evidence only; no framed descriptor capture. | confirmed-static | Carry field 17/service type 21 into the Task 10 manifest decision; preserve the Task 6 historical-compatibility boundary. |
| SVC-BUF-ENDPOINT | BufferedMedia | Does the 17.3 phone endpoint only discard input? | `isi.java:21-24`; `jaz.java:14-25,26-87`; `xkg.java:4-13,31-32`; `xkf.java:4-34` | No. The phone endpoint directly accepts incoming raw message ID 4, parses the buffer as `xkg`, maps its state through `xkf`, and reads/logs all six payload fields. Normalized direction: HU -> Phone. The decompiled consumer then only loads values into locals; no response or completed media-transfer operation is proven. | Static parser/consumer evidence only; runtime receipt and successful downstream behavior are unverified. | confirmed-static | Supersede the cross-version “discard-only stub” characterization only for 17.3's implemented ID-4 parse branch. Do not characterize this as a complete or runtime-active transfer protocol. |
| SVC-BUF-IDS | BufferedMedia | Which raw IDs and outbound builders are directly observed? | `a.java:429-443`; `jaz.java:14-25`; exact bounded ID/builder search over `{isi,ise,isf,isg,isj,jaz,jnb}.java`, recorded below | `jaz` directly compares incoming raw ID 4 and parses it. Its validator admits numeric IDs 1 through 4, but IDs 1, 2, and 3 take only the unexpected-message path; the bounded service search contains no `.k(1, ...)` through `.k(4, ...)` send call or payload builder. Thus ID 4/HU -> Phone is confirmed, while meanings, payloads, directions, and any outbound use for IDs 1-3 are unobserved. | Runtime-unverified; no framed traffic establishes additional IDs or an outbound path. | confirmed-static (ID 4); deferred (IDs 1-3/outbound) | Publish only raw message ID 4 after the Task 10 manifest gate. Leave IDs 1-3 and all outbound pairing unknown; do not extrapolate from validator order. |
| SVC-BUF-SCHEMAS | BufferedMedia | What is the directly parsed ID-4 payload structure? | `xkg.java:4-13,24-33`; `xiq.java:15,57-59`; `xkf.java:4-34`; `jaz.java:26-63`; repository RawMessageInfo decoder `analysis/tools/apk_indexer/extract.py:50-218` | `xkg` is proto2 with six optional fields: field 1 `int32` session ID; field 2 `uint64` UID; field 3 `uint64` current position ms; field 4 enum playback state; field 5 `uint64` buffered position ms; field 6 `uint64` content duration ms. `xkf` proves state values UNKNOWN=0, PLAYING=1, PAUSED=2, STOPPED=3, BUFFERING=4. | Static schema and log-consumer evidence only; no captured payload bytes. | confirmed-static | Admit only this ID-4 schema to the Task 10 manifest. Do not invent URL, session lifecycle, transport, request, or response fields. |
| SVC-BUF-GATE | BufferedMedia | What constructs, discovers, and activates the endpoint? | `actl.java:4-10`; `actj.java:4-16`; `jnb.java:403-413`; `isi.java:11-23,46-53`; `ise.java:4-9` | The outer factory path runs only when long-valued `NeoplanFeature__enabled` equals magic value `834952858` (declared default `0`). It creates the named service dependencies and `isi`; `isi` separately requires descriptor bit `0x10000`, registers itself with the manager, and produces `jaz`; endpoint attachment separately starts `BUFFERED_MEDIA_WORKER`. These are distinct gates/lifecycle steps. | Defaults and branches are static decompile evidence; effective flag value, descriptor advertisement, endpoint opening, and worker execution are runtime-unverified. | confirmed-static | Document the exact gated construction chain, but do not claim the service is enabled in production or currently active at runtime. |

## CarIntent bounded contract

The complete static source chain is:

1. `xlv.java:23-25,44-45` assigns optional descriptor field 18 to the empty
   `xgd` marker.
2. `jnb.java:398-402` creates a `CarIntentService` factory candidate and hands
   it to `jae.a(...)`.
3. `jae.java:133-158` walks unclaimed discovered descriptors and retains a
   factory result only when `jad.a(xlv)` returns a non-null endpoint factory.
4. `iix.java:16-26` returns non-null only for presence bit `131072`
   (`0x20000`) and constructs `ixg`.
5. `ixg.java:12-14` binds that endpoint to service type 22, named
   `CAR_INTENT` by `rpq.java:27,82-83`.
6. `ixg.java:17-35` parses `xgc` from an incoming buffer on the phone, logs
   field 2 as NAVIGATE metadata, and notifies registered consumers. The
   normalized direction is **HU -> Phone**.

This is static endpoint construction and parse evidence, not runtime capture.
It proves neither successful live activation nor the raw message ID.

### Payload schema boundary

The repository RawMessageInfo decoder applied to `xgc.java:27` reports one
proto2 field: optional field 2, protobuf type `string` (type ID 8). Strings use
wire type 2 (length-delimited), so the encoded tag is `(2 << 3) | 2 = 0x12`.
The object array `{"d", "b"}` associates the presence word with `d` and the
string with member `b`; `ixg.java:29` reads `b` as the logged metadata value.

There is no field 1 in the decoded descriptor. The log's literal `NAVIGATE`
does not establish an intent-type field or enum. No distinct acknowledgement,
response branch, or response payload appears in the bounded source chain.

### Raw message ID boundary

The required searches were run over the sender/dispatcher/resource surface:

```text
rg -n 'xgc|CAR_INTENT|CarIntentService|Received an intent from the car' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage -g '*.java'

rg -n 'CAR_INTENT|CarIntent' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/resources \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources -g '*'
```

The first search returned only `iix`, `ixg`, `iya`, `jnb`, `rpq`, and `xgc`
identity/parse/log references. The resources-plus-sources search returned no
additional sender enum or raw-ID mapping. A focused numeric/send-call check of
`ixg`, `iix`, `xgc`, `rpq`, and `jnb` also returned no `0x8001`, `32769`-series
comparison, or numeric `.k(id, ...)` send. `ixg.a(int, ByteBuffer)` does not use
its integer parameter. Therefore the raw ID remains unknown and `0x8001` is
not publishable.

### Activation boundary

`acla.java:8-21` declares
`AdasRouteInfoFeature__car_intent_enabled` with a default of `false`;
`acky.java:12-13` exposes it and `dme.java:1232-1233` prints it for diagnostics.
The required bounded feature-name search finds no reference in `jnb` or `iix`.
Instead, `jnb.java:398-402` constructs `iix` without a flag branch, while
`iix.java:16-21` suppresses descriptors lacking bit `0x20000` and accepts those
that contain it. This supports documenting the nominal flag default and the
actual decompiled factory path separately; it does not support saying the flag
controls CarIntent endpoint construction.

## CarLocalMedia bounded flow

The phone-side service is type 20. Its three directly observed IDs are:

| Raw ID | Payload | Phone endpoint action | Normalized direction |
|---|---|---|---|
| `0x8001` / 32769 | `xgh` playback status | Parse, cache, and notify registered callbacks | HU -> Phone |
| `0x8002` / 32770 | `xgf` playback metadata | Parse, cache, and notify registered callbacks | HU -> Phone |
| `0x8003` / 32771 | `xgg` playback request | Build from the app request's `xge` action and send; reject an inbound copy as unexpected | Phone -> HU |

This closes the endpoint flow statically, including the asymmetry at `0x8003`.
It does not prove runtime service discovery, a framed message, callback delivery,
or any acknowledgement to the request.

### Playback-state value 5 boundary

The required search covered the four focused classes and every decompiled Java
source in the 17.3 tree:

```text
rg -n 'PLAYBACK|value 5|case 5|syn\.|xgh' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/{syn,xgh,ixi,iiy}.java \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources -g '*.java'
```

`xgh.java:31` associates the status field with validator `syn.q`;
`syn.java:88-89` delegates to `a.aB`, and `a.java:367-384` accepts values 1
through 5 without naming them. `iiy.java:44-60` passes that numeric result into
the public status object without a state-specific branch. No result in the
complete scope supplies an unobfuscated CarLocalMedia name for value 5.
Accordingly, value 5 is **deferred** and remains numeric. BufferedMedia's
separate `xkf` enum is not evidence for this CarLocalMedia value.

## BufferedMedia bounded classification

### Service, endpoint, and activation chain

Descriptor field 17/member `t` is the empty `xfq` marker. The factory path has
three independently visible conditions or lifecycle steps:

1. `actl.java:5-9` declares the long-valued `NeoplanFeature__enabled` default as
   0. `jnb.java:403-413` constructs the BufferedMedia dependencies and `isi`
   only when the effective value equals `834952858`.
2. `isi.java:11-18` accepts discovery only when field-17 presence bit `0x10000`
   is set; it then registers the service instance with `ise`.
3. `isi.java:21-23` creates `jaz`, whose constructor selects service type 21.
   When the endpoint is attached, `isi.java:46-53` starts a handler thread named
   `BUFFERED_MEDIA_WORKER`.

The equality branch, descriptor gate, and worker construction are proven
statically. The effective flag value, live descriptor, opened endpoint, and
running worker are all runtime-unverified.

### Directly parsed ID and schema

`jaz.java:18-25` admits numeric IDs 1 through 4 through its validator but
rejects every incoming value except raw message ID 4 as unexpected.
`jaz.java:26-63` parses ID 4 into `xkg` and labels the six consumed members as:

| Field | Proto2 type | Consumer meaning |
|---|---|---|
| 1 | optional `int32` | session ID |
| 2 | optional `uint64` | UID |
| 3 | optional `uint64` | current position ms |
| 4 | optional enum | playback state (`xkf`) |
| 5 | optional `uint64` | buffered position ms |
| 6 | optional `uint64` | content duration ms |

`xkf.java:4-34` directly names the state values: unknown 0, playing 1, paused
2, stopped 3, and buffering 4. The parser logs and reads the values, but the
remaining decompiled consumer only assigns locals. No response, transfer,
callback delivery, or successful media operation follows from this evidence.

### ID and publication boundary

The per-ID disposition is intentionally explicit:

| Raw ID | Direct receive evidence | Direct outbound builder/send | Disposition |
|---|---|---|---|
| 1 | Validator accepts it, then `jaz` logs it as unexpected | None in the bounded service search | deferred: name, payload, direction, and pairing unknown |
| 2 | Validator accepts it, then `jaz` logs it as unexpected | None in the bounded service search | deferred: name, payload, direction, and pairing unknown |
| 3 | Validator accepts it, then `jaz` logs it as unexpected | None in the bounded service search | deferred: name, payload, direction, and pairing unknown |
| 4 | `jaz` parses `xkg` HU -> Phone | None in the bounded service search | confirmed-static for the incoming playback-status payload; outbound use deferred |

The required bounded searches were:

```text
rg -n 'jaz|xkg|xkf|CAR.MEDIA.BUFFERED|BUFFERED_MEDIA_WORKER|Creating CarBufferedMediaSourceService|\.k\([1-4],' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/{isi,ise,isf,isg,isj,jaz,jnb}.java

rg -n '834952858|BufferedMedia|buffered_media' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage -g '*.java'
```

They find the incoming ID-4 comparison and `xkg` parser, but no direct outbound
`.k(1, ...)` through `.k(4, ...)` call and no payload builder in the bounded
service classes. IDs 1-3 therefore remain **deferred** for name, payload,
direction, and pairing, as does every BufferedMedia outbound path. The fact
that `a.aF` accepts the numeric range 1-4 is not sufficient to fill those gaps.

The old 16.1 statement that the phone handler only logs and discards input is
superseded for 17.3 only to this precise extent: 17.3 contains an implemented,
field-consuming parse branch for incoming ID 4. The 16.1 historical statement
remains version-specific, and 17.3 static code still does not prove runtime
activation or a complete media-transfer protocol. URL behavior, transport/data
plane, session lifecycle, request/response pairing, and runtime success remain
unproven and are not publication candidates.
