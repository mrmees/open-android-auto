# Services Matrix

| Claim | Service | Question | Evidence anchors | Finding | Runtime status | Status | Canonical disposition |
|---|---|---|---|---|---|---|---|
| SVC-CI-DESCRIPTOR | CarIntent | Which descriptor member and service type identify the service? | `xlv.java:23-25,44-45`; `xgd.java:4-25`; `iix.java:12-26`; `rpq.java:27,82-83` | `ChannelDescriptor` field 18 is the empty `xgd` CarIntent marker. Its presence bit is `131072` (`0x20000`), and the accepted endpoint uses GAL service type 22 (`CAR_INTENT`). | Static APK evidence only; no framed descriptor capture. | confirmed-static | Carry field 18/service type 22 into the Task 10 manifest decision; do not create canonical CarIntent files before that gate. |
| SVC-CI-ENDPOINT | CarIntent | Which side parses the payload, and what happens after parsing? | `jnb.java:398-402`; `jae.java:133-158`; `iix.java:16-26`; `ixg.java:12-35` | The phone constructs the type-22 endpoint for an accepted field-18 descriptor. `ixg.a(...)` parses `xgc` from the incoming buffer, logs the field-2 value as NAVIGATE metadata, and invokes registered callbacks. Normalized direction: HU -> Phone. | Static receive-path evidence only; no runtime message capture or callback observation. | confirmed-static | Document the HU -> Phone receive/consumer chain as a manifest candidate; do not infer a response or acknowledgement. |
| SVC-CI-ID | CarIntent | What raw message ID carries the incoming payload? | `ixg.java:17-35`; bounded searches over all 17.3 `sources/defpackage/*.java`, then all 17.3 `resources` and `sources`, recorded below | The incoming raw-ID parameter is unused by `ixg.a(int, ByteBuffer)`. No sender-side enum, dispatcher comparison, numeric send call, or resource mapping ties `xgc`/CarIntent to a raw ID. | Runtime-unverified; no framed traffic is available to supply the ID. | deferred | Publish the raw message ID as unknown. Do not invent conventional `0x8001`. |
| SVC-CI-SCHEMA | CarIntent | Which payload fields are wire-proven? | `xgc.java:4-8,19-28`; repository RawMessageInfo decoder `analysis/tools/apk_indexer/extract.py:50-218`; `ixg.java:20-29` | The RawMessageInfo literal decodes as proto2 with one optional field: field 2, type `string` (protobuf wire type 2, tag byte `0x12`), assigned to member `b`. The consumer logs that member as NAVIGATE metadata. `NAVIGATE` is a fixed log label, not a decoded wire enum. | Static schema/consumer evidence only; payload bytes were not captured. | confirmed-static | Publish only an optional field-2 string payload at the manifest gate. Do not assign field 1, add an intent-type enum, acknowledgement, or response flow. |
| SVC-CI-GATE | CarIntent | What activates or suppresses endpoint construction? | `acla.java:8-21`; `acky.java:4-20`; `dme.java:1232-1233`; `jnb.java:398-402`; `jae.java:133-158`; `iix.java:16-21` | `AdasRouteInfoFeature__car_intent_enabled` is declared with default `false` and exposed by `acky.d()`, but the bounded factory path contains no read of that flag: `jnb` constructs `iix` unconditionally, `jae.a(...)` asks it to match discovered descriptors, and `iix.a(...)` accepts only when bit `0x20000` is present. Descriptor absence suppresses construction; descriptor presence accepts it. | Default and factory behavior are static decompile evidence; effective server-side flag value and live activation were not observed. | confirmed-static | Document both the false default and the actual descriptor-presence gate. Do not claim the named feature flag controls this factory path. |
| SVC-CLM-STATE5 | | | | | | open | |
| SVC-CLM-FLOW | | | | | | open | |
| SVC-BUF-DESCRIPTOR | | | | | | open | |
| SVC-BUF-ENDPOINT | | | | | | open | |
| SVC-BUF-IDS | | | | | | open | |
| SVC-BUF-SCHEMAS | | | | | | open | |
| SVC-BUF-GATE | | | | | | open | |

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
