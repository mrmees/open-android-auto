# Issue #8 Media Codec Type Fix Design

Date: 2026-07-25
Status: Approved

## Context

GitHub issue #8 reports that field 1 of `AVChannel` is typed as
`AVStreamType.Enum` even though the field identifies the channel codec. The
same stale type is present on field 1 of `AVInputChannel`.

Android Auto 17.3 provides a direct static discriminator for both fields:

- `xik.java` (`AVChannel`) assigns field 1 the enum validator `orw.u`;
- `xil.java` (`AVInputChannel`) assigns field 1 the same validator `orw.u`;
- `orw.u` dispatches to `xif.b(int)`; and
- `xif.b(int)` accepts the codec values PCM=1, AAC=2, H264=3, AAC_ADTS=4,
  VP9=5, AV1=6, and H265=7.

Those values match `MediaCodecType.Enum`. `AVStreamType.Enum` contains only
NONE=0, AUDIO=1, and VIDEO=3. The existing declaration therefore appears to
work for PCM and H264 only because their numeric values coincide. It gives
generated clients the wrong type and cannot represent the other valid codec
values symbolically.

The service-discovery documentation already describes both fields as
`MediaCodecType`, so the canonical protobuf descriptors currently contradict
the documented contract.

## Goals

1. Type field 1 of both `AVChannel` and `AVInputChannel` as
   `MediaCodecType.Enum`.
2. Preserve protobuf tags, cardinality, packages, and enum numeric values.
3. Add a compiled-descriptor regression test covering both fields.
4. Record the Android Auto 17.3 validator evidence in both audit sidecars.
5. Keep the repository verification and confidence-annotation gates green.

## Non-goals

- Do not change any protobuf field number, wire type, message package, or enum
  numeric value.
- Do not remove `AVStreamTypeEnum.proto`; its historical or external use is a
  separate compatibility decision.
- Do not refactor unrelated AV schemas or analysis tools.
- Do not change issue #10 conclusions or documentation as part of this fix.
- Do not publish, comment on, or close GitHub issue #8 without a separate
  integration decision.

## Approaches Considered

### 1. Change only the two protobuf declarations

This is the smallest edit, but it leaves no executable contract preventing the
same semantic mismatch from returning. It is rejected.

### 2. Focused schema correction with descriptor regression coverage — selected

Correct both descriptors, update their evidence records, and assert the
compiled enum targets in a focused test. This provides a narrow fix with a
durable check and no unrelated schema cleanup.

### 3. Remove `AVStreamTypeEnum.proto` and migrate every reference

Only the two affected active messages currently consume the enum, but deleting
the file would turn a verified bug fix into a broader generated-API and
historical-reference decision. It is rejected for this issue.

## Design

### 1. Canonical protobuf changes

In `oaa/av/AVChannelData.proto` and `oaa/av/AVInputChannelData.proto`:

- replace the `AVStreamTypeEnum.proto` import with
  `MediaCodecTypeEnum.proto`; and
- change field 1 from `enums.AVStreamType.Enum` to
  `enums.MediaCodecType.Enum`.

Keep the existing field name `stream_type` to avoid combining the enum-type
fix with a generated accessor rename. Keep tag 1 and the `optional` cardinality
unchanged. The enum remains encoded as a protobuf varint, so existing PCM=1 and
H264=3 payloads are wire-compatible while generated clients gain symbolic
access to codecs 2, 4, 5, 6, and 7.

Update the comment in `MediaCodecTypeEnum.proto` so its active uses include
field 1 of `AVChannel` and `AVInputChannel`.

### 2. Descriptor regression test

Add
`analysis/tools/proto_stream_validator/tests/test_av_channel_descriptor_contracts.py`.
The test will build the repository descriptor bundle through the existing
`build_descriptor_bundle` helper and inspect field 1 of:

- `oaa.proto.data.AVChannel`; and
- `oaa.proto.data.AVInputChannel`.

For each message, the test will require:

- field number 1 to exist;
- protobuf type to remain `enum`; and
- `enum_type.full_name` to equal
  `oaa.proto.enums.MediaCodecType.Enum`.

The test must be written and run before the protobuf declarations change. Its
initial failure must show the current `AVStreamType.Enum` target, establishing
that it detects the reported bug.

### 3. Audit evidence

Append an `apk_deep_trace` entry to both
`oaa/av/AVChannelData.audit.yaml` and
`oaa/av/AVInputChannelData.audit.yaml`. Each entry will cite the exact 17.3 APK
identity already recorded by the repository and the relevant
`xik`/`xil` -> `orw.u` -> `xif.b` trace.

The entry will distinguish semantic enum identity from protobuf wire type:
cross-version structural checks correctly saw an enum varint at field 1, but
did not prove which enum namespace the field uses. The new deep trace resolves
that semantic ambiguity.

After editing sidecars, run the annotation repair for `oaa/av` if the canonical
renderer changes the confidence comments, then require `--check` to report no
drift.

### 4. Repository workflow records

Update `docs/roadmap-current.md` only to record the immediate issue #8 schema
correction ahead of further issue #10 investigation; do not reorder unrelated
milestones. Append a handoff entry to `docs/session-handoffs.md` containing the
change rationale, status, next steps, and exact verification results.

## Error Handling and Stop Conditions

Stop and investigate rather than expanding the patch if:

- either 17.3 field resolves to a different validator than `orw.u`;
- `orw.u` accepts values that do not match `MediaCodecType.Enum`;
- the descriptor test fails for a reason other than the current enum target;
- `protoc` reports an import, package, or duplicate-symbol error;
- annotation repair changes unrelated AV files; or
- full verification exposes a failure outside the bounded descriptor change.

## Verification

The fix is ready for integration only after fresh evidence shows:

1. the new descriptor test fails against the pre-fix schemas because both
   fields target `oaa.proto.enums.AVStreamType.Enum`;
2. the same test passes after the schema correction;
3. `protoc --proto_path=. --cpp_out=/tmp` succeeds for both changed message
   files;
4. the audit schema and tier-consistency tests pass;
5. annotation `--check` reports zero changes;
6. `make PYTHON=.venv/bin/python verify` exits zero;
7. `git diff --check` exits zero; and
8. `docs/session-handoffs.md` records the commands and outcomes.

## Issue #10 Investigation Boundary

Issue #10 remains a separate evidence task. The Digital Trends Chevrolet
example establishes that a driver can cycle between full-map and turn-card
cluster presentations, but the vehicle runs Android Automotive and can combine
native cluster layout controls with phone-projected content.

The next investigation will first test the narrower dual-feed hypothesis:
Android Auto can deliver CLUSTER video while simultaneously sending semantic
`NavigationNotification` and `NavigationNextTurnDistanceEvent` messages, and
the vehicle may select which feed to show without requesting a renderer change
from the phone. A matching Google Maps APK will be acquired and decompiled only
if the Android Auto and captured-wire paths do not identify the provider-side
control boundary.
