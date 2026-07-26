# Issue #8 Media Codec Type Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct field 1 of `AVChannel` and `AVInputChannel` to use the verified `MediaCodecType.Enum` contract and prevent regression at the compiled-descriptor boundary.

**Architecture:** Keep the wire schema stable while changing the generated enum identity in the two canonical AV descriptors. A focused descriptor-pool test proves the semantic type, Android Auto 17.3 validator traces update the audit sidecars, and the repository's existing annotation and verification gates validate the complete change.

**Tech Stack:** protobuf 2/3 schemas, `protoc`, Python 3.13, pytest 9, Python protobuf runtime 6, YAML audit sidecars, Make.

## Global Constraints

- Preserve every protobuf tag, cardinality, package, wire type, and enum numeric value.
- Keep the generated field name `stream_type` unchanged.
- Keep `oaa/av/AVStreamTypeEnum.proto`; deletion is outside issue #8.
- Limit behavior-changing work to protobuf definitions, protocol evidence, and analysis tests.
- Update `docs/roadmap-current.md` because issue #8 is now the immediate repository priority.
- Append exact commands and outcomes to `docs/session-handoffs.md` before completion.
- Do not publish, comment on, or close GitHub issue #8 in this plan.
- Treat issue #10 as a separate investigation; do not mix its conclusions into this patch.

---

## Plan Review Gate

Before Task 1, commit this plan and send the committed plan plus its approved
design to Opus for a bounded read-only review. The reviewer must check test
fidelity, protobuf wire-compatibility claims, audit-tier effects, verification
coverage, and unintended scope. Apply only concrete corrections supported by
the repository, amend the plan commit if necessary, and run `git diff --check`
before implementation.

---

### Task 1: Add the failing descriptor contract

**Files:**
- Create: `analysis/tools/proto_stream_validator/tests/test_av_channel_descriptor_contracts.py`
- Reference: `analysis/tools/proto_stream_validator/descriptors.py:32-67`
- Reference: `oaa/av/AVChannelData.proto:6-18`
- Reference: `oaa/av/AVInputChannelData.proto:6-14`

**Interfaces:**
- Consumes: `build_descriptor_bundle(repo_root: Path, out_dir: Path) -> DescriptorBundle`.
- Produces: two parametrized regression cases asserting that AV field 1 resolves to `oaa.proto.enums.MediaCodecType.Enum`.

- [ ] **Step 1: Create the descriptor contract test**

```python
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("google.protobuf")

from google.protobuf.descriptor import FieldDescriptor

from analysis.tools.proto_stream_validator.descriptors import (
    build_descriptor_bundle,
)

REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture(scope="module")
def descriptor_bundle(tmp_path_factory):
    return build_descriptor_bundle(
        repo_root=REPO_ROOT,
        out_dir=tmp_path_factory.mktemp("av-codec-descriptors"),
    )


@pytest.mark.parametrize(
    "message_name",
    [
        "oaa.proto.data.AVChannel",
        "oaa.proto.data.AVInputChannel",
    ],
    ids=["AVChannel", "AVInputChannel"],
)
def test_stream_type_uses_media_codec_enum(descriptor_bundle, message_name):
    message = descriptor_bundle.pool.FindMessageTypeByName(message_name)
    field = message.fields_by_number[1]

    assert field.type == FieldDescriptor.TYPE_ENUM
    assert field.enum_type.full_name == "oaa.proto.enums.MediaCodecType.Enum"
```

- [ ] **Step 2: Run the test and verify the expected RED result**

Run:

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q \
  analysis/tools/proto_stream_validator/tests/test_av_channel_descriptor_contracts.py
```

Expected: two failures. Each failure must report the actual enum target as
`oaa.proto.enums.AVStreamType.Enum`, proving the test detects both reported
schema defects. Any import, descriptor-build, or missing-field error is an
invalid RED result and must be fixed in the test before proceeding.

---

### Task 2: Correct the schemas and evidence

**Files:**
- Modify: `oaa/av/AVChannelData.proto:6-18`
- Modify: `oaa/av/AVInputChannelData.proto:6-14`
- Modify: `oaa/av/MediaCodecTypeEnum.proto:9-10`
- Modify: `oaa/av/AVChannelData.audit.yaml`
- Modify: `oaa/av/AVInputChannelData.audit.yaml`
- Test: `analysis/tools/proto_stream_validator/tests/test_av_channel_descriptor_contracts.py`

**Interfaces:**
- Consumes: the failing field-1 descriptor contract from Task 1 and the 17.3 `xik`/`xil` -> `orw.u` -> `xif.b` validator trace.
- Produces: both field-1 descriptors targeting `oaa.proto.enums.MediaCodecType.Enum`; AVInputChannel retains Silver confidence while adding the newly proven deep-trace evidence type.

- [ ] **Step 1: Replace the two imports and field types**

In both AV message files, replace:

```protobuf
import "oaa/av/AVStreamTypeEnum.proto";
```

with:

```protobuf
import "oaa/av/MediaCodecTypeEnum.proto";
```

Replace each field-1 declaration with:

```protobuf
optional enums.MediaCodecType.Enum stream_type = 1;
```

Retain the existing confidence comment on the same line until the annotation
renderer is run in Step 4.

- [ ] **Step 2: Update the MediaCodecType usage comment**

Replace the comment at `oaa/av/MediaCodecTypeEnum.proto:9` with:

```protobuf
// Media codec types for AVChannel field 1, AVInputChannel field 1,
// AVChannelSetupRequest field 1, and VideoConfig field 10.
```

- [ ] **Step 3: Append the 17.3 semantic validator evidence**

Append this entry to `oaa/av/AVChannelData.audit.yaml`:

```yaml
- type: apk_deep_trace
  method: semantic_enum_validator_trace
  source: >-
    Android Auto 17.3.662804-release; APKM SHA-256
    1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344;
    base.apk SHA-256
    5557827f259898bdab97b489e1a0aef937fd6ec711d87361cf25d51af6f48619;
    JADX xik.java:38 -> orw.java:6,79-82 -> xif.java:4-37
  date: '2026-07-25'
  description: >
    AVChannel field 1 uses validator orw.u, which dispatches to xif.b and
    accepts the codec domain 1-7 (PCM, AAC, H264, AAC_ADTS, VP9, AV1, H265).
    This proves MediaCodecType rather than the numerically overlapping
    AVStreamType enum; tag 1 remains an enum varint on the wire.
```

Append this entry to `oaa/av/AVInputChannelData.audit.yaml` and keep its
top-level `confidence` at `silver`:

```yaml
- type: apk_deep_trace
  method: semantic_enum_validator_trace
  source: >-
    Android Auto 17.3.662804-release; APKM SHA-256
    1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344;
    base.apk SHA-256
    5557827f259898bdab97b489e1a0aef937fd6ec711d87361cf25d51af6f48619;
    JADX xil.java:29 -> orw.java:6,79-82 -> xif.java:4-37
  date: '2026-07-25'
  description: >
    AVInputChannel field 1 uses validator orw.u, which dispatches to xif.b and
    accepts the codec domain 1-7. This proves MediaCodecType while the existing
    cross-version evidence remains structural and does not independently meet
    the repository's machine-readable Gold prerequisite.
```

- [ ] **Step 4: Synchronize and check AV confidence annotations**

Run:

```bash
PYTHONPATH=. .venv/bin/python -m analysis.tools.seed_import.annotate oaa/av
PYTHONPATH=. .venv/bin/python -m analysis.tools.seed_import.annotate --check oaa/av
```

Expected: repair changes only `AVInputChannelData.proto` confidence evidence
labels to `silver [apk_deep_trace, apk_static, cross_version]`; the check
reports `Changed: 0`. If the tier changes or any unrelated AV file changes,
stop and inspect the sidecar/renderer boundary.

- [ ] **Step 5: Run the descriptor contract and verify GREEN**

Run:

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q \
  analysis/tools/proto_stream_validator/tests/test_av_channel_descriptor_contracts.py
```

Expected: `2 passed`.

- [ ] **Step 6: Compile both changed message schemas**

Run:

```bash
issue8_cpp_dir="$(mktemp -d)"
trap 'rm -rf "$issue8_cpp_dir"' EXIT
protoc --proto_path=. --cpp_out="$issue8_cpp_dir" \
  oaa/av/AVChannelData.proto \
  oaa/av/AVInputChannelData.proto
test -s "$issue8_cpp_dir/oaa/av/AVChannelData.pb.cc"
test -s "$issue8_cpp_dir/oaa/av/AVInputChannelData.pb.cc"
```

Expected: exit 0 and generated C++ files under
the task-scoped temporary directory.

- [ ] **Step 7: Validate both audit sidecars and canonical tiers**

Run:

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q \
  analysis/tools/seed_import/tests/test_audit_yaml_schema_validation.py \
  analysis/tools/seed_import/tests/test_audit_yaml_tier_consistency.py \
  analysis/tools/seed_import/tests/test_proto_annotations_match_sidecars.py
```

Expected: all selected tests pass with no confidence drift.

- [ ] **Step 8: Re-bless and revalidate all affected decoded baselines**

Run:

```bash
issue8_pairs=(
  "analysis/captures/non_media/2026-02-28-s25-cleanbuild.jsonl|analysis/baselines/non_media/2026-02-28-s25-cleanbuild.normalized.json"
  "analysis/captures/non_media/active-navigation.converted.jsonl|analysis/baselines/non_media/active-navigation.normalized.json"
  "analysis/captures/non_media/general.converted.jsonl|analysis/baselines/non_media/general.normalized.json"
  "analysis/captures/non_media/idle-baseline.converted.jsonl|analysis/baselines/non_media/idle-baseline.normalized.json"
  "analysis/captures/non_media/music-playback.converted.jsonl|analysis/baselines/non_media/music-playback.normalized.json"
)
for issue8_pair in "${issue8_pairs[@]}"; do
  issue8_capture="${issue8_pair%%|*}"
  issue8_baseline="${issue8_pair#*|}"
  PYTHONPATH=. .venv/bin/python analysis/tools/proto_stream_validator/run.py \
    --capture "$issue8_capture" \
    --baseline "$issue8_baseline" \
    --repo-root . \
    --bless \
    --reason "issue #8: correct AV stream_type enum identity to MediaCodecType"
  PYTHONPATH=. .venv/bin/python analysis/tools/proto_stream_validator/run.py \
    --capture "$issue8_capture" \
    --baseline "$issue8_baseline" \
    --repo-root .
done
```

Expected: every bless and validation command exits 0. The five baseline diffs
contain only `stream_type` label replacements: `VIDEO` becomes
`MEDIA_CODEC_VIDEO_H264_BP`, and `AUDIO` becomes
`MEDIA_CODEC_AUDIO_PCM`.

- [ ] **Step 9: Commit the verified schema correction**

Run:

```bash
git diff --check
git add \
  analysis/tools/proto_stream_validator/tests/test_av_channel_descriptor_contracts.py \
  oaa/av/AVChannelData.proto \
  oaa/av/AVInputChannelData.proto \
  oaa/av/MediaCodecTypeEnum.proto \
  oaa/av/AVChannelData.audit.yaml \
  oaa/av/AVInputChannelData.audit.yaml \
  analysis/baselines/non_media/2026-02-28-s25-cleanbuild.normalized.json \
  analysis/baselines/non_media/active-navigation.normalized.json \
  analysis/baselines/non_media/general.normalized.json \
  analysis/baselines/non_media/idle-baseline.normalized.json \
  analysis/baselines/non_media/music-playback.normalized.json
git commit -m "fix(proto): use media codec type for AV channels"
```

Expected: one commit containing only the focused descriptor contract, the two
schema corrections, the codec usage comment, their evidence sidecars, and the
five directly affected decoded baselines.

---

### Task 3: Record priority and handoff

**Files:**
- Modify: `docs/roadmap-current.md:17-53`
- Modify: `docs/session-handoffs.md` (append only)

**Interfaces:**
- Consumes: the verified schema commit from Task 2 and exact command outcomes from this task.
- Produces: a current roadmap that separates issue #8 completion from issue #10 investigation, plus the repository-required session handoff.

- [ ] **Step 1: Update the roadmap without reordering unrelated work**

Add this first bullet under `## Now`:

```markdown
- Issue #8's AV codec enum identity is corrected in both `AVChannel` and
  `AVInputChannel`, with Android Auto 17.3 validator evidence and a compiled-
  descriptor regression contract.
```

Replace the generic open-issue triage bullet under `## Next` with:

```markdown
- Investigate issue #10's Chevrolet cluster-view evidence by testing whether
  CLUSTER video and semantic navigation guidance are simultaneous feeds selected
  locally by the vehicle before acquiring a matching Google Maps APK.
```

- [ ] **Step 2: Run the complete verification gate**

Run:

```bash
make PYTHON=.venv/bin/python verify
```

Expected: exit 0; `1,812 passed`, 3 explicitly asset-dependent integration
skips, all 247 protos compile, and annotation checking reports `Changed: 0`.
If the collected test count differs only because pytest counts the two
parametrized cases differently, record the exact observed count instead of
forcing this expectation.

- [ ] **Step 3: Append the required handoff entry**

Append this structure to `docs/session-handoffs.md`, replacing the aggregate
test count only if Step 2 produced a different exact value:

```markdown
## 2026-07-25 — Fix issue #8 AV codec enum identity

What changed:
- Changed field 1 of `AVChannel` and `AVInputChannel` from
  `AVStreamType.Enum` to `MediaCodecType.Enum` without changing tag,
  cardinality, package, or wire encoding
- Added a compiled-descriptor regression covering both messages
- Added Android Auto 17.3 semantic validator traces to both audit sidecars
  while retaining `AVInputChannel` at policy-derived Silver confidence
- Re-blessed and revalidated the five tracked non-media baselines whose
  `stream_type` enum labels changed

Why:
- Android Auto uses the MediaCodecType validator for both fields. The old type
  appeared functional only for PCM=1 and H264=3 because those values overlap
  with AVStreamType, while valid codec values 2 and 4-7 had no symbolic type

Status:
- The focused regression, changed-proto compilation, audit policy checks, and
  full repository verification pass
- Issue #10 remains a separate investigation into vehicle-local selection
  between projected CLUSTER video and semantic turn guidance

Next steps:
1. Review and integrate the focused issue #8 branch
2. Report the verified fix on GitHub issue #8 after integration
3. Continue issue #10 with the dual-feed hypothesis before Maps APK acquisition

Verification:
- RED descriptor contract -> 2 failed; both fields resolved to
  `oaa.proto.enums.AVStreamType.Enum`
- GREEN descriptor contract -> 2 passed
- `protoc --proto_path=. --cpp_out="$issue8_cpp_dir"
  oaa/av/AVChannelData.proto oaa/av/AVInputChannelData.proto` -> exit 0 using
  task-scoped temporary output
- Audit schema, tier, and annotation policy slice -> all selected tests passed
- All five tracked non-media captures -> refreshed with an explicit issue #8
  reason, then validated with no baseline diffs
- `make PYTHON=.venv/bin/python verify` -> exit 0; 1,812 passed, 3 expected
  APK-index integration skips; all 247 protos compiled; annotation check
  reported `Changed: 0`
- `git diff --check` -> exit 0
```

- [ ] **Step 4: Re-run final checks after documentation changes**

Run:

```bash
make PYTHON=.venv/bin/python verify
rg -n "issue #8|issue #10|AVInputChannel|MediaCodecType" \
  docs/roadmap-current.md docs/session-handoffs.md
git diff --check
git status --short
```

Expected: full verification remains green; the path/reference scan shows the
new roadmap and handoff records; diff checking exits 0; status lists only the
two intended documentation files.

- [ ] **Step 5: Commit the workflow records**

Run:

```bash
git add docs/roadmap-current.md docs/session-handoffs.md
git commit -m "docs: record issue 8 codec type fix"
```

Expected: a documentation-only commit following the focused schema commit.

---

### Task 4: Final requirements audit

**Files:**
- Verify: all files changed since `aa691cd`
- Reference: `docs/superpowers/specs/2026-07-25-issue-8-media-codec-type-fix-design.md`

**Interfaces:**
- Consumes: the approved design and Tasks 1-3 commits.
- Produces: evidence that every approved requirement is implemented and no issue #10 behavior or GitHub state was changed.

- [ ] **Step 1: Inspect the complete branch delta**

Run:

```bash
git diff --stat aa691cd..HEAD
git diff --check aa691cd..HEAD
git status --short --branch
```

Expected: the branch contains the corrected design and implementation plan,
the descriptor test, two corrected AV schemas, one codec comment, two updated
audit sidecars, five refreshed decoded baselines, roadmap, and handoff; the
worktree is clean.

- [ ] **Step 2: Confirm the obsolete enum has no active message consumers**

Run:

```bash
rg -n "AVStreamType" oaa --glob '*.proto'
```

Expected: only the declaration in `oaa/av/AVStreamTypeEnum.proto` remains; no
active message imports or field references remain.

- [ ] **Step 3: Confirm no GitHub or issue #10 mutation occurred**

Run:

```bash
if git diff --name-only aa691cd..HEAD \
  | rg -q '^(docs/channels/display-routing\.md|analysis/reports/multi-display/)'; then
  exit 1
fi
```

Expected: exit 0 with no matching changed path. GitHub issue comments, labels,
and state remain untouched by this local implementation plan.
