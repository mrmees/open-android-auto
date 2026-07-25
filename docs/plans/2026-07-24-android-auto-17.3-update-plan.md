# Android Auto 17.3 Evidence-Gated Protocol Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a verified, wire-compatible Android Auto 16.x/17.3 protocol-reference update with corrected message directions and IDs, unambiguous display/service identities, bounded new-service schemas, current reports, and a Prodigy maintainer handoff.

**Architecture:** Evidence moves through a tracked 17.3 release dossier before it changes canonical protobufs or channel documentation. Seven release gates are implemented as 14 narrow tasks: preserve the baseline, build and close evidence matrices, attempt conditional runtime probes, freeze a change manifest, publish accepted changes, regenerate reports, and run a final release verification gate.

**Tech Stack:** proto2/proto3, `protoc`, Python 3, `pytest`, PyYAML, jsonschema, JADX 1.5.5 output, shell/`rg`/`jq`, Android `adb`, Frida capture tooling when a compatible phone and head unit are available.

## Global Constraints

- Keep all behavior-changing work inside protobuf definitions, protocol documentation, evidence reports, and analysis tooling in this repository.
- Treat historical docs and comments as comparison inputs, not authority. Direct 17.3 endpoint behavior, decoded protobuf-lite descriptors, and correctly framed wire evidence take precedence.
- Do not treat the model's inference as evidence. Every correction must cite reproducible APK source, trusted lineage, or framed runtime traffic.
- Normalize all directions to `Phone -> HU` or `HU -> Phone`; explicitly invert phone-side `send`/`receive` observations into that wire perspective.
- Preserve a wire-compatible 16.x/17.3 superset when field numbers and wire types permit it, with version-specific semantics documented.
- Generated API compatibility is not a constraint. Proven misleading identifiers, including `AVChannel.channel_id`, may be cleanly renamed.
- Runtime validation is conditional. Attempt it, record the exact limitation when unavailable, and label unconfirmed behavior `runtime-unverified`.
- Fully trace CarIntent; close or defer the targeted CarLocalMedia semantic; classify BufferedMedia without inventing unreachable schemas.
- Do not expand this release to all unresolved matcher collisions, low-value placeholder enums, or a broad repository reorganization.
- Update `docs/roadmap-current.md` only when actual sequencing or priority changes.
- Append `docs/session-handoffs.md` after every task with what changed, why, status, next one to three steps, and fresh verification output.
- Stage only files named by the current task. Preserve unrelated user changes.

## Evidence Priority

Use this order when sources disagree:

1. Correctly framed and decrypted runtime traffic tied to a known channel and Android Auto version.
2. Direct endpoint send/receive code plus the decoded protobuf-lite message descriptor used at that branch.
3. Trusted-parent or curated cross-version lineage with an exact structural edge.
4. Current canonical protos, audit sidecars, verification reports, and channel docs.
5. Historical external projects or archived documents.

Lower-ranked evidence may corroborate a claim but may not override contradictory higher-ranked evidence.

## File Responsibility Map

### Release dossier created by this plan

| File | Responsibility |
|---|---|
| `analysis/reports/android-auto-17.3-update/README.md` | Release status, APK identity, gate table, evidence policy, artifact index, and resume pointer. |
| `analysis/reports/android-auto-17.3-update/message-matrix.md` | IDs, protobuf identities, endpoint actions, normalized directions, source anchors, version deltas, and canonical disposition. |
| `analysis/reports/android-auto-17.3-update/services.md` | CarIntent reconstruction and bounded CarLocalMedia/BufferedMedia findings. |
| `analysis/reports/android-auto-17.3-update/runtime-validation.md` | Probe definitions, environment preflight, commands, captures/logs, results, and runtime-unverified explanations. |
| `analysis/reports/android-auto-17.3-update/change-manifest.md` | Accepted evidence-to-file mapping and publication checklist. |

### Primary static evidence

| Area | Durable 17.3 source files |
|---|---|
| Video and focus | `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jdc.java`, `itt.java`, `its.java`, `jca.java` |
| Multi-display identity | `itq.java`, `iti.java`, `itt.java`, `jnb.java`, `xik.java`, `xhs.java`, `xlv.java` |
| Car control | `ixb.java`, `iip.java`, `xma.java`, `xlj.java`, `xgj.java`, `xga.java`, `xlz.java`, `xli.java`, `xfw.java` |
| Sensors | `jal.java`, `ijm.java`, `xlq.java`, `xlr.java`, `xln.java`, `xlo.java` |
| Radio | `jai.java`, `iji.java`, `xku.java`, `xkt.java`, `xkp.java`, `xlc.java`, `xkl.java` |
| CarIntent | `ixg.java`, `ixf.java`, `iix.java`, `xgc.java`, `rpq.java`, `acla.java`, `jnb.java` |
| CarLocalMedia | `ixi.java`, `iiy.java`, `xgh.java`, `xgg.java`, `syn.java` |
| BufferedMedia | `isi.java`, `jaz.java`, `ise.java`, `isf.java`, `isg.java`, `isj.java`, `xkg.java`, `xkf.java`, `rpq.java`, `jnb.java` |

### Candidate canonical publication files

The exact changed set is frozen in Task 10. Candidate files are:

- `oaa/av/AVChannelMessageIdsEnum.proto`
- `oaa/av/AVChannelData.proto`
- `oaa/av/AVChannelData.audit.yaml`
- `oaa/av/UiConfigMessages.proto`
- `oaa/video/*.proto`
- `oaa/video/*.audit.yaml`
- `oaa/carcontrol/CarControlMessages.proto`
- `oaa/carcontrol/CarControlMessages.audit.yaml`
- `oaa/sensor/SensorRequestMessage.proto`
- `oaa/sensor/SensorStartResponseMessage.proto`
- `oaa/sensor/SensorEventIndicationMessage.proto`
- `oaa/sensor/SensorErrorMessage.proto`
- matching sensor audit sidecars
- `oaa/radio/RadioMessages.proto`
- `oaa/radio/RadioMessages.audit.yaml`
- `oaa/control/ChannelDescriptorData.proto`
- `oaa/control/ChannelDescriptorData.audit.yaml`
- `oaa/input/InputChannelConfigData.proto`
- `oaa/input/InputChannelConfigData.audit.yaml`
- `oaa/media/BufferedMediaSinkMessage.proto`
- `oaa/media/CarLocalMediaPlaybackStatusMessage.proto`
- matching media audit sidecars
- `oaa/carintent/CarIntentMessage.proto` and audit sidecar only if Task 7 confirms a publishable payload
- `docs/channels/video.md`
- `docs/channels/carcontrol.md`
- `docs/channels/sensor.md`
- `docs/channels/radio.md`
- `docs/channels/media.md`
- `docs/channels/display-routing.md`
- `docs/channels/architecture.md`
- `docs/channels/carintent.md` only if Task 7 confirms a publishable service contract
- `docs/channel-map.md`
- relevant `docs/cross-version/*.md`
- `analysis/reports/proto-verification/*.md`
- `analysis/reports/cross-version/17-3-schema-match.{json,md}` only after the Task 1 delta review
- `analysis/reports/coverage-dashboard/coverage-dashboard.{json,md}`
- `analysis/reports/multi-display/prodigy-maintainer-handoff.md`

## Execution Discipline

- Task 1 runs in the current checkout because it owns the already-uncommitted 17.3 evidence. Do not create a worktree before that evidence is committed.
- After Task 1, later tasks may run in an isolated worktree created from the updated branch.
- At the end of each task, update the dossier `README.md` resume pointer once that file exists.
- A task with contradictory evidence ends with the affected claim marked `blocked`; dependent publication rows remain excluded from the change manifest.
- A task may mark a bounded claim `deferred`, but no in-scope claim may remain `open` when Task 10 freezes the manifest.

## Initial Resume Pointer

- Last completed item: approved design committed as `d1d883f`.
- Current worktree state: uncommitted 17.3 provenance, schema-matcher README, roadmap/handoff, and multi-display reports.
- Next task: Task 1, preserve and commit the current 17.3 evidence baseline.
- First command: `git status --short`.

---

### Task 1: Preserve the Existing 17.3 Baseline

**Files:**

- Modify: `analysis/tools/proto_schema_matcher/README.md`
- Modify: `docs/roadmap-current.md`
- Modify: `docs/session-handoffs.md`
- Create: `analysis/reports/multi-display/README.md`
- Create: `analysis/reports/multi-display/android-auto-17.3.md`
- Create: `analysis/reports/multi-display/prodigy-maintainer-handoff.md`
- Verify: `analysis/aa_apk_17.3.662804_apkm/PROVENANCE.md`
- Verify: `analysis/aa_apk_17.3.662804_apkm/validation/17-3-schema-match-fresh.{json,md}`
- Compare: `analysis/reports/cross-version/17-3-schema-match.{json,md}`

**Produces:** A committed, reproducible 17.3 evidence checkpoint; a reviewed disposition for the three fresh-matcher delta rows; no new canonical proto claims.

- [ ] **Step 1: Confirm the dirty scope before staging anything**

Run:

```bash
git status --short
git diff --stat
git diff -- analysis/tools/proto_schema_matcher/README.md docs/roadmap-current.md docs/session-handoffs.md
```

Expected: only the three tracked documentation files and `analysis/reports/multi-display/` are dirty. Stop and preserve any additional user files separately.

- [ ] **Step 2: Verify the durable artifact identities**

Run:

```bash
sha256sum \
  analysis/aa_apk_17.3.662804_apkm/input/android-auto-17.3.662804-release.apkm \
  analysis/aa_apk_17.3.662804_apkm/input/base.apk

find analysis/aa_apk_17.3.662804_apkm/jadx-output/sources -type f -name '*.java' | wc -l

for source_file in jdc itt itq iti its jnb; do
  test -f "analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/${source_file}.java"
done
```

Expected hashes:

- APKM: `1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344`
- base APK: `5557827f259898bdab97b489e1a0aef937fd6ec711d87361cf25d51af6f48619`
- Java source count: `26115`

- [ ] **Step 3: Re-run the documented matcher smoke command**

Run:

```bash
PYTHONPATH=. python3 -m analysis.tools.proto_schema_matcher.run \
  --jadx-root analysis/aa_apk_17.3.662804_apkm/jadx-output \
  --version 17.3.662804-release \
  --apk-sha256 1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344 \
  --lineage-yaml analysis/lineage/android-auto-17.3.yaml \
  --output-json analysis/aa_apk_17.3.662804_apkm/validation/17-3-schema-match-fresh.json \
  --output-md analysis/aa_apk_17.3.662804_apkm/validation/17-3-schema-match-fresh.md
```

Expected: command exits zero and writes 176 resolved mappings with 135 dispatch observations for the current durable JADX tree.

- [ ] **Step 4: Review the known matcher deltas without promoting them**

Run:

```bash
jq -r '.matches[] | select(.canonical_name | test("BluetoothChannel|PhoneConnectionConfig|WifiInfoResponse")) | [.canonical_name, .status, (.resolved_apk_class // "-"), .confidence] | @tsv' \
  analysis/reports/cross-version/17-3-schema-match.json

jq -r '.matches[] | select(.canonical_name | test("BluetoothChannel|PhoneConnectionConfig|WifiInfoResponse")) | [.canonical_name, .status, (.resolved_apk_class // "-"), .confidence] | @tsv' \
  analysis/aa_apk_17.3.662804_apkm/validation/17-3-schema-match-fresh.json
```

Expected: the fresh report differs at those three canonical rows. Record the exact differences in the existing multi-display handoff and retain the committed report as canonical during this task.

- [ ] **Step 5: Run documentation and path sanity checks**

Run:

```bash
rg -n '/tmp/android-auto-17.3-jadx' analysis/tools/proto_schema_matcher docs analysis/reports/multi-display

rg -n 'analysis/aa_apk_17.3.662804_apkm|17.3.662804-release|CarDisplayId|DisplayRegistry' \
  analysis/tools/proto_schema_matcher/README.md \
  docs/roadmap-current.md \
  docs/session-handoffs.md \
  analysis/reports/multi-display

git diff --check
```

Expected: no active smoke command points to `/tmp`; durable paths and required display concepts are present; diff check exits zero.

- [ ] **Step 6: Append the Task 1 verification result to the handoff**

Add a new `docs/session-handoffs.md` entry recording the two hashes, Java count, matcher summary, three-row delta disposition, path checks, status, and Task 2 as the next step.

- [ ] **Step 7: Commit only the baseline evidence**

Run:

```bash
git add \
  analysis/tools/proto_schema_matcher/README.md \
  analysis/reports/multi-display/README.md \
  analysis/reports/multi-display/android-auto-17.3.md \
  analysis/reports/multi-display/prodigy-maintainer-handoff.md \
  docs/roadmap-current.md \
  docs/session-handoffs.md

git diff --cached --check
git commit -m "docs(analysis): preserve Android Auto 17.3 display evidence"
```

---

### Task 2: Establish the 17.3 Release Dossier

**Files:**

- Create: `analysis/reports/android-auto-17.3-update/README.md`
- Create: `analysis/reports/android-auto-17.3-update/message-matrix.md`
- Create: `analysis/reports/android-auto-17.3-update/services.md`
- Create: `analysis/reports/android-auto-17.3-update/runtime-validation.md`
- Create: `analysis/reports/android-auto-17.3-update/change-manifest.md`
- Modify: `docs/session-handoffs.md`

**Produces:** One stable entry point and four focused matrices. Later tasks update rows rather than creating new report formats.

- [ ] **Step 1: Create the dossier index with fixed metadata**

The index must contain:

```markdown
# Android Auto 17.3 Protocol Update Dossier

- Version: `17.3.662804-release`
- APKM SHA-256: `1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344`
- base.apk SHA-256: `5557827f259898bdab97b489e1a0aef937fd6ec711d87361cf25d51af6f48619`
- Design: `docs/plans/2026-07-24-android-auto-17.3-update-design.md`
- Execution plan: `docs/plans/2026-07-24-android-auto-17.3-update-plan.md`

## Gate Status

| Gate | Status | Exit evidence |
|---|---|---|
| Baseline preservation | confirmed-static | Durable provenance and matcher smoke recorded in Task 1 handoff. |
| Direction and video-ID audit | open | `message-matrix.md` DIR rows |
| Identity and compatibility | open | `message-matrix.md` ID rows |
| New services | open | `services.md` SVC rows |
| Runtime validation | open | `runtime-validation.md` RT rows |
| Canonical publication | open | `change-manifest.md` accepted rows |
| Final verification and handoff | open | final handoff entry |

## Resume Here

- Last completed task: Task 1
- Next task: Task 3, video message direction and ID audit
- Next command: `rg -n "k\\(327|i == 327|case 327" analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/{jdc,itt,its,jca}.java`
```

- [ ] **Step 2: Create the message matrix with stable claim IDs**

Use this exact column set:

```markdown
| Claim | Area | Raw ID | Canonical name | APK class | Phone endpoint action | Normalized direction | Source anchors | 16.x delta | Status | Canonical disposition |
|---|---|---:|---|---|---|---|---|---|---|---|
```

Pre-create rows `DIR-VID-8007` through `DIR-VID-8015`, `DIR-CC-8001` through `DIR-CC-8007`, `DIR-SEN-8001` through `DIR-SEN-8004`, and `DIR-RAD-801A` through `DIR-RAD-8023` with status `open`. Add identity rows `ID-AV-F6`, `ID-INPUT-F5`, `ID-CD-F16`, `ID-CD-F17`, and `ID-CD-F18`.

- [ ] **Step 3: Create the service matrix with stable claim IDs**

Use this exact column set:

```markdown
| Claim | Service | Question | Evidence anchors | Finding | Runtime status | Status | Canonical disposition |
|---|---|---|---|---|---|---|---|
```

Pre-create `SVC-CI-DESCRIPTOR`, `SVC-CI-ENDPOINT`, `SVC-CI-ID`, `SVC-CI-SCHEMA`, `SVC-CI-GATE`, `SVC-CLM-STATE5`, `SVC-CLM-FLOW`, `SVC-BUF-DESCRIPTOR`, `SVC-BUF-ENDPOINT`, `SVC-BUF-IDS`, `SVC-BUF-SCHEMAS`, and `SVC-BUF-GATE` with status `open`.

- [ ] **Step 4: Create the runtime validation matrix**

Use this exact column set:

```markdown
| Probe | Required capability | Setup and command | Expected protocol event | Result | Evidence path | Status |
|---|---|---|---|---|---|---|
```

Pre-create `RT-ENV`, `RT-VIDEO-FOCUS`, `RT-VIDEO-UI`, `RT-RADIO`, `RT-CARCONTROL`, and `RT-MULTIDISPLAY` with status `open`.

- [ ] **Step 5: Create the change manifest contract**

Use this exact column set:

```markdown
| Change | Accepted evidence | Canonical files | Exact change | Compatibility note | Verification | Status |
|---|---|---|---|---|---|---|
```

Start with no change rows. State that Task 10 may add a row only from `confirmed-static`, `confirmed-runtime`, or explicit `no canonical change` dossier claims.

- [ ] **Step 6: Verify the dossier structure**

Run:

```bash
for dossier_file in README.md message-matrix.md services.md runtime-validation.md change-manifest.md; do
  test -s "analysis/reports/android-auto-17.3-update/${dossier_file}"
done

rg -n 'DIR-VID-8007|DIR-CC-8001|DIR-SEN-8001|DIR-RAD-801A|ID-AV-F6' \
  analysis/reports/android-auto-17.3-update/message-matrix.md

rg -n 'SVC-CI-SCHEMA|SVC-CLM-STATE5|SVC-BUF-SCHEMAS' \
  analysis/reports/android-auto-17.3-update/services.md

rg -n 'RT-ENV|RT-VIDEO-FOCUS|RT-RADIO|RT-CARCONTROL|RT-MULTIDISPLAY' \
  analysis/reports/android-auto-17.3-update/runtime-validation.md

git diff --check
```

Expected: all files and required claim IDs exist; diff check exits zero.

- [ ] **Step 7: Append the Task 2 handoff and commit**

Record the dossier layout, stable claim IDs, current resume pointer, and verification results in `docs/session-handoffs.md`.

Run:

```bash
git add analysis/reports/android-auto-17.3-update docs/session-handoffs.md
git diff --cached --check
git commit -m "docs(analysis): establish Android Auto 17.3 release dossier"
```

---

### Task 3: Close the Video Direction and Message-ID Matrix

**Files:**

- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jdc.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/itt.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/its.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jca.java`
- Modify: `analysis/reports/android-auto-17.3-update/message-matrix.md`
- Modify: `analysis/reports/android-auto-17.3-update/README.md`
- Modify: `docs/session-handoffs.md`

**Produces:** A complete 17.3 video control table for `0x8007` through `0x8015`, with each ID classified as send, receive, unused, or unresolved-with-bounded-search.

- [ ] **Step 1: Extract all direct numeric sends and receive branches**

Run:

```bash
rg -n '\bk\(327|i == 327|case 327' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jdc.java \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/itt.java \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/its.java \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jca.java
```

Expected anchors include sends `32775`, `32778`, `32780`, `32781`, `32785`, `32789` and receives `32776`, `32777`, `32782`, `32783`.

- [ ] **Step 2: Tie every branch to its protobuf-lite class**

Read the complete builder or parser block surrounding every anchor. For each class, record its descriptor source file and field structure. Do not infer a message name solely from the current enum.

Run:

```bash
sed -n '90,330p' analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jdc.java
sed -n '520,675p' analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/itt.java
```

Expected: `32775` sends `xnd`; `32776` parses `xnb`; `32777` parses `xms`; `32778` sends `xms`; later IDs expose action, overlay, UI-token, and critical-UI payloads.

- [ ] **Step 3: Bound missing IDs with a repository-wide source search**

Run:

```bash
for decimal_id in 32779 32784 32786 32787 32788; do
  rg -n "${decimal_id}" analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage -g '*.java'
done
```

For any ID without a result, record the exact source root and numeric searches in the matrix. Mark it `deferred` rather than assigning the historical name.

- [ ] **Step 4: Compare against every active canonical video table**

Run:

```bash
rg -n '0x800[7-9A-F]|0x801[0-5]|VIDEO_FOCUS|UPDATE_UI|OVERLAY|MEDIA_STATS|MEDIA_OPTIONS|ACTION_TAKEN' \
  oaa/av/AVChannelMessageIdsEnum.proto \
  oaa/av/UiConfigMessages.proto \
  oaa/video \
  docs/channels/video.md \
  docs/cross-version/video.md \
  analysis/reports/proto-verification/video.md
```

Record every conflict as the exact old claim and its higher-ranked 17.3 replacement.

- [ ] **Step 5: Close the DIR-VID rows**

Update `DIR-VID-8007` through `DIR-VID-8015` so none remain `open`. Use `confirmed-static`, `rejected`, or `deferred`; include exact source line anchors and canonical disposition.

- [ ] **Step 6: Verify and checkpoint**

Run:

```bash
if rg -n '^\| DIR-VID-.*\| open \|' analysis/reports/android-auto-17.3-update/message-matrix.md; then
  exit 1
fi

rg -n '32775|32776|32777|32778|32780|32781|32782|32783|32785|32789' \
  analysis/reports/android-auto-17.3-update/message-matrix.md

git diff --check
```

Update the dossier resume pointer to Task 4, append the handoff entry, and commit:

```bash
git add \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/message-matrix.md \
  docs/session-handoffs.md
git commit -m "docs(video): close Android Auto 17.3 message matrix"
```

---

### Task 4: Close the Car-Control Direction Matrix

**Files:**

- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/ixb.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/iip.java`
- Verify: protobuf-lite classes referenced by those endpoints
- Modify: `analysis/reports/android-auto-17.3-update/message-matrix.md`
- Modify: `analysis/reports/android-auto-17.3-update/README.md`
- Modify: `docs/session-handoffs.md`

**Produces:** A source-backed `0x8001` through `0x8007` car-control matrix that corrects historical HU/phone perspective inversions.

- [ ] **Step 1: Extract phone receive branches**

Run:

```bash
rg -n 'case 3276|case 3277|Received unexpected car control|\.q\(\)' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/ixb.java
```

Expected receives: `32770`, `32772`, `32773`, and `32775`; explicitly record absent/unexpected cases `32771` and `32774`.

- [ ] **Step 2: Extract phone sends and their builders**

Run:

```bash
rg -n 'ixbVar\.k\(327|Sending CarActionNotification|requestSetCarPropertyValue|registerCarProperty' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/iip.java
```

Expected sends include `32769`, `32771`, and `32774`. Read the complete surrounding builder blocks and record their payload classes.

- [ ] **Step 3: Compare current canonical directions**

Run:

```bash
rg -n '0x800[1-7]|HU.?Phone|Phone.?HU|SetCarProperty|RegisterCarProperty|CarAction|CarControlGroup' \
  oaa/carcontrol/CarControlMessages.proto \
  docs/channels/carcontrol.md \
  docs/cross-version/carcontrol.md \
  analysis/reports/proto-verification/carcontrol.md
```

Record each inverted historical claim as a conflict row; do not preserve it because it was previously labeled Gold.

- [ ] **Step 4: Close and verify all car-control rows**

Run after editing:

```bash
if rg -n '^\| DIR-CC-.*\| open \|' analysis/reports/android-auto-17.3-update/message-matrix.md; then
  exit 1
fi

rg -n 'DIR-CC-800[1-7].*(Phone -> HU|HU -> Phone)' \
  analysis/reports/android-auto-17.3-update/message-matrix.md

git diff --check
```

Expected normalized directions:

- Phone -> HU: `0x8001`, `0x8003`, `0x8006`
- HU -> Phone: `0x8002`, `0x8004`, `0x8005`, `0x8007`

- [ ] **Step 5: Checkpoint and commit**

Update the resume pointer to Task 5, append exact source anchors and verification to the handoff, then run:

```bash
git add \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/message-matrix.md \
  docs/session-handoffs.md
git commit -m "docs(carcontrol): correct 17.3 endpoint direction evidence"
```

---

### Task 5: Confirm Sensor and Radio Directions

**Files:**

- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jal.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/ijm.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jai.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/iji.java`
- Modify: `analysis/reports/android-auto-17.3-update/message-matrix.md`
- Modify: `analysis/reports/android-auto-17.3-update/README.md`
- Modify: `docs/session-handoffs.md`

**Produces:** Closed sensor and radio direction rows, including explicit `no canonical change` findings where current radio documentation already agrees.

- [ ] **Step 1: Trace sensor request and receive paths**

Run:

```bash
rg -n 'private static final int|sendSensorRequest|k\(i2|handleSensorResponse|sensor error|xln|xlo' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jal.java
```

Expected: the phone sends the sensor request and receives response, event, and error messages. Resolve constants `32769` through `32772` from declarations and branch use.

- [ ] **Step 2: Trace radio sends and receives**

Run:

```bash
rg -n 'case 3279[4-9]|case 3280[0-3]' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jai.java

rg -n 'jaiVar\.k\(3279[4-9]|jaiVar\.k\(3280[0-3]' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/iji.java
```

Expected: notifications and responses are received by the phone; mute/tune/favorite/direction/search requests are sent by the phone.

- [ ] **Step 3: Compare current sensor and radio claims**

Run:

```bash
rg -n '0x800[1-4]|HU.?Phone|Phone.?HU' \
  oaa/sensor/SensorRequestMessage.proto \
  oaa/sensor/SensorStartResponseMessage.proto \
  oaa/sensor/SensorEventIndicationMessage.proto \
  oaa/sensor/SensorErrorMessage.proto \
  docs/channels/sensor.md \
  analysis/reports/proto-verification/sensor.md

rg -n '0x801[A-F]|0x802[0-3]|HU.?Phone|Phone.?HU' \
  oaa/radio/RadioMessages.proto \
  docs/channels/radio.md \
  analysis/reports/proto-verification/radio.md
```

Record sensor conflicts for correction. Mark radio rows `no canonical change` where all active sources agree.

- [ ] **Step 4: Close, verify, and commit**

Run:

```bash
if rg -n '^\| DIR-(SEN|RAD)-.*\| open \|' analysis/reports/android-auto-17.3-update/message-matrix.md; then
  exit 1
fi

git diff --check
```

Update the resume pointer to Task 6, append the handoff, then commit:

```bash
git add \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/message-matrix.md \
  docs/session-handoffs.md
git commit -m "docs(protocol): close sensor and radio direction matrix"
```

---

### Task 6: Close Display, Channel, and Descriptor Identity

**Files:**

- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/itq.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jnb.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/xik.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/xhs.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/xlv.java`
- Compare: 16.2 source and verification reports for `ChannelDescriptor` fields 16 and 17
- Modify: `analysis/reports/android-auto-17.3-update/message-matrix.md`
- Modify: `analysis/reports/android-auto-17.3-update/README.md`
- Modify: `docs/session-handoffs.md`

**Produces:** Proven semantic boundaries for transport channel ID, service type, display ID, and input binding; a version disposition for descriptor fields 16-18.

- [ ] **Step 1: Reconfirm AV field 6 consumption as a display ID**

Run:

```bash
rg -n 'CarDisplayId|xik\.|new iti|new itt|display' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/itq.java

sed -n '190,235p' analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/itq.java
```

Record the exact `xik` member read before `new CarDisplayId(...)` and the corresponding protobuf field number from `xik.java`.

- [ ] **Step 2: Reconfirm input binding and topology constraints**

Run:

```bash
rg -n 'display ID|displayId|Display ID|MAIN|CLUSTER|AUXILIARY|input' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jnb.java

sed -n '1,120p' analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/xhs.java
```

Record the matching of input field 5 to AV field 6 and the distinction from `ChannelDescriptor.channel_id` field 1.

- [ ] **Step 3: Classify descriptor fields 16-18 across versions**

Run:

```bash
rg -n 'field.?16|field.?17|generic_notification|voice|car_local_media|buffered_media|car_intent|xgi|xfq|xgd' \
  oaa/control/ChannelDescriptorData.proto \
  analysis/reports/proto-verification/sdp.md \
  analysis/reports/proto-verification/sdp-progress.md \
  analysis/reports/cross-version/17-3-schema-match.md \
  analysis/lineage/android-auto-17.3.yaml

rg -n 'xgi|xfq|xgd|65536|131072|32768' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/{xlv,jnb,isi,iix}.java
```

For each field, choose one disposition from the design: prior mapping incorrect, compatible addition/removal, semantic reuse, or insufficient evidence. Cite the exact source chain.

- [ ] **Step 4: Close identity rows and verify terminology**

Run after editing:

```bash
if rg -n '^\| ID-.*\| open \|' analysis/reports/android-auto-17.3-update/message-matrix.md; then
  exit 1
fi

rg -n 'transport channel ID|service type|display ID|input.*display' \
  analysis/reports/android-auto-17.3-update/message-matrix.md

git diff --check
```

- [ ] **Step 5: Checkpoint and commit**

Update the resume pointer to Task 7 and append the handoff. Commit:

```bash
git add \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/message-matrix.md \
  docs/session-handoffs.md
git commit -m "docs(display): close 17.3 protocol identity matrix"
```

---

### Task 7: Reconstruct the CarIntent Service

**Files:**

- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/ixg.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/iix.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/xgc.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/rpq.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/acla.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jnb.java`
- Modify: `analysis/reports/android-auto-17.3-update/services.md`
- Modify: `analysis/reports/android-auto-17.3-update/README.md`
- Modify: `docs/session-handoffs.md`

**Produces:** A bounded CarIntent contract: service type, descriptor field, direction, payload schema, activation gate, message-ID evidence, and publication decision.

- [ ] **Step 1: Confirm descriptor acceptance and service type**

Run:

```bash
rg -n 'CAR_INTENT\(22\)|case 22|131072|CarIntentService discovered' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/{rpq,iix,jnb}.java
```

Expected: service type 22 and descriptor presence bit `131072` are tied to CarIntent.

- [ ] **Step 2: Confirm endpoint direction and payload use**

Run:

```bash
sed -n '1,120p' analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/ixg.java
sed -n '1,100p' analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/xgc.java
```

Expected: the phone endpoint parses `xgc` from an incoming HU message and logs NAVIGATE metadata from protobuf field 2, a string.

- [ ] **Step 3: Bound the message-ID question**

Run:

```bash
rg -n 'xgc|CAR_INTENT|CarIntentService|Received an intent from the car' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage -g '*.java'

rg -n 'CAR_INTENT|CarIntent' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/resources \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources -g '*'
```

If no sender-side enum or dispatch comparison identifies the raw ID, mark `SVC-CI-ID` `deferred` with these searches. Do not invent `0x8001` from convention.

- [ ] **Step 4: Confirm the activation gate**

Run:

```bash
rg -n 'AdasRouteInfoFeature__car_intent_enabled|car_intent_enabled' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/{acla,dme,jnb,iix}.java
```

Record the default value and the factory path that accepts or suppresses the service.

- [ ] **Step 5: Close every CarIntent row**

The publication disposition is:

- publish the payload schema if field 2 string identity and HU -> Phone use remain non-contradictory;
- document the raw message ID as unknown if no direct ID evidence exists;
- do not add an acknowledgement or intent-type enum unless a distinct wire field is found.

Run:

```bash
if rg -n '^\| SVC-CI-.*\| open \|' analysis/reports/android-auto-17.3-update/services.md; then
  exit 1
fi

rg -n 'service type 22|field 2|HU -> Phone|NAVIGATE|AdasRouteInfoFeature' \
  analysis/reports/android-auto-17.3-update/services.md

git diff --check
```

- [ ] **Step 6: Checkpoint and commit**

Update the resume pointer to Task 8, append the handoff, and commit:

```bash
git add \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/services.md \
  docs/session-handoffs.md
git commit -m "docs(carintent): reconstruct Android Auto 17.3 service"
```

---

### Task 8: Close CarLocalMedia and Classify BufferedMedia

**Files:**

- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/ixi.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/iiy.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/xgh.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/syn.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/isi.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jaz.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/xkg.java`
- Verify: `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/xkf.java`
- Modify: `analysis/reports/android-auto-17.3-update/services.md`
- Modify: `analysis/reports/android-auto-17.3-update/README.md`
- Modify: `docs/session-handoffs.md`

**Produces:** A closed local-media state/flow disposition and a source-backed BufferedMedia classification that supersedes the 16.1 “stub only” claim where 17.3 proves active parsing.

- [ ] **Step 1: Trace all CarLocalMedia endpoint directions**

Run:

```bash
rg -n 'case 32769|case 32770|case 32771|ixiVar\.k\(327|playback' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/{ixi,iiy}.java
```

Record `0x8001` through `0x8003`, payload classes, phone endpoint action, and normalized direction.

- [ ] **Step 2: Resolve or bound playback-state value 5**

Run:

```bash
rg -n 'PLAYBACK|value 5|case 5|syn\.|xgh' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/{syn,xgh,ixi,iiy}.java \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources -g '*.java'
```

If an unobfuscated enum name or semantic branch exists, record it. Otherwise mark `SVC-CLM-STATE5` `deferred` with the complete search scope; keep the numeric value without assigning a guessed label.

- [ ] **Step 3: Prove BufferedMedia is no longer a discard-only stub**

Run:

```bash
sed -n '1,180p' analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/jaz.java
sed -n '1,180p' analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/xkg.java
sed -n '1,160p' analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/xkf.java
```

Expected: service type 21 parses message ID `4` as `xkg` playback status with session, UID, state, position, buffered position, and duration fields.

- [ ] **Step 4: Trace BufferedMedia outbound IDs and activation**

Run:

```bash
rg -n 'jaz|xkg|xkf|CAR.MEDIA.BUFFERED|BUFFERED_MEDIA_WORKER|Creating CarBufferedMediaSourceService|\.k\([1-4],' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/{isi,ise,isf,isg,isj,jaz,jnb}.java

rg -n '834952858|BufferedMedia|buffered_media' \
  analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage -g '*.java'
```

Record every direct ID and payload. Mark any unobserved IDs `deferred` after the bounded search; do not extrapolate from an enum sequence.

- [ ] **Step 5: Close service rows and verify**

Run:

```bash
if rg -n '^\| SVC-(CLM|BUF)-.*\| open \|' analysis/reports/android-auto-17.3-update/services.md; then
  exit 1
fi

rg -n 'message ID 4|xkg|service type 21|service type 20|runtime-unverified|deferred' \
  analysis/reports/android-auto-17.3-update/services.md

git diff --check
```

- [ ] **Step 6: Checkpoint and commit**

Update the resume pointer to Task 9, append the handoff, and commit:

```bash
git add \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/services.md \
  docs/session-handoffs.md
git commit -m "docs(media): classify 17.3 local and buffered media services"
```

---

### Task 9: Attempt Focused Runtime Validation

**Files:**

- Modify: `analysis/reports/android-auto-17.3-update/runtime-validation.md`
- Modify: `analysis/reports/android-auto-17.3-update/README.md`
- Modify: `docs/session-handoffs.md`
- Local output: `analysis/aa_apk_17.3.662804_apkm/runtime-validation/`
- External capture tool: `/mnt/e/claude/personal/android-auto-dhu/phone_full_capture.py`
- External methodology: `/mnt/e/claude/personal/android-auto-dhu/docs/phone-capture-pipeline.md`

**Produces:** Runtime-confirmed evidence or explicit environment-unavailable records for video focus/UI, radio, car control, and multi-display.

- [ ] **Step 1: Run the environment preflight**

Run:

```bash
adb devices -l
adb shell dumpsys package com.google.android.projection.gearhead | rg 'versionName|longVersionCode'
python3 -c 'import frida, cryptography; print("capture dependencies present")'
python3 /mnt/e/claude/personal/android-auto-dhu/phone_full_capture.py --help
```

Branch rule:

- If no `device` row appears, mark `RT-ENV` `deferred` with the command output and mark all scenario rows `runtime-unverified: no ADB device available during execution`.
- If the connected package is not `17.3.662804-release`, record the actual version and do not use its traffic to confirm 17.3 claims.
- If the dependency import fails, mark `RT-ENV` `deferred` with the missing module and mark the scenario rows `runtime-unverified: validated capture Python environment unavailable`.
- If both checks pass, continue with Steps 2-5.

- [ ] **Step 2: Create the ignored runtime evidence directory**

Run:

```bash
mkdir -p analysis/aa_apk_17.3.662804_apkm/runtime-validation
adb logcat -c
```

Expected: the ignored local directory exists and the phone log buffer is cleared.

- [ ] **Step 3: Capture video focus and UI configuration**

Run from the capture-tool repository:

```bash
cd /mnt/e/claude/personal/android-auto-dhu
python3 phone_full_capture.py --duration 90 --scenario aa-17.3-video-focus-ui
mkdir -p /mnt/e/claude/personal/github/open-android-auto-clean/analysis/aa_apk_17.3.662804_apkm/runtime-validation/video-focus-ui
cp captures/phone_aa_capture.pcap captures/phone_sslkeylog.txt captures/phone_cr.hex captures/phone_sr.hex \
  captures/aa_messages_aa-17.3-video-focus-ui.jsonl \
  captures/channel_map_aa-17.3-video-focus-ui.json \
  captures/sdp_response_aa-17.3-video-focus-ui.bin \
  /mnt/e/claude/personal/github/open-android-auto-clean/analysis/aa_apk_17.3.662804_apkm/runtime-validation/video-focus-ui/
```

The capture is stored under:

```text
analysis/aa_apk_17.3.662804_apkm/runtime-validation/video-focus-ui/
```

Exercise native, native-transient, projected, and projected-without-input focus when the DHU exposes them; trigger a day/night or blended-UI configuration update. Record whether IDs `0x8007`, `0x8008`, `0x8009`, `0x800A`, and the overlay/UI-token IDs appear with the direction predicted by Task 3.

- [ ] **Step 4: Capture radio and car-control activation**

Run two independent captures so service activation failures remain separable:

```bash
cd /mnt/e/claude/personal/android-auto-dhu
python3 phone_full_capture.py --duration 120 --scenario aa-17.3-radio
mkdir -p /mnt/e/claude/personal/github/open-android-auto-clean/analysis/aa_apk_17.3.662804_apkm/runtime-validation/radio
cp captures/phone_aa_capture.pcap captures/phone_sslkeylog.txt \
  captures/aa_messages_aa-17.3-radio.jsonl \
  captures/channel_map_aa-17.3-radio.json \
  captures/sdp_response_aa-17.3-radio.bin \
  /mnt/e/claude/personal/github/open-android-auto-clean/analysis/aa_apk_17.3.662804_apkm/runtime-validation/radio/

python3 phone_full_capture.py --duration 120 --scenario aa-17.3-car-control
mkdir -p /mnt/e/claude/personal/github/open-android-auto-clean/analysis/aa_apk_17.3.662804_apkm/runtime-validation/car-control
cp captures/phone_aa_capture.pcap captures/phone_sslkeylog.txt \
  captures/aa_messages_aa-17.3-car-control.jsonl \
  captures/channel_map_aa-17.3-car-control.json \
  captures/sdp_response_aa-17.3-car-control.bin \
  /mnt/e/claude/personal/github/open-android-auto-clean/analysis/aa_apk_17.3.662804_apkm/runtime-validation/car-control/
```

The capture sets live under:

```text
analysis/aa_apk_17.3.662804_apkm/runtime-validation/radio/
analysis/aa_apk_17.3.662804_apkm/runtime-validation/car-control/
```

For radio, record discovery, initial list/info notifications, one tune request/response, and mute when available. For car control, record discovery, listener registration, state report, one set request/result, and one action when available. An unavailable service is a runtime activation result, not evidence that the protocol is absent.

- [ ] **Step 5: Capture MAIN, CLUSTER, and AUXILIARY topology**

Run:

```bash
cd /mnt/e/claude/personal/android-auto-dhu
python3 phone_full_capture.py --duration 120 --scenario aa-17.3-multi-display
mkdir -p /mnt/e/claude/personal/github/open-android-auto-clean/analysis/aa_apk_17.3.662804_apkm/runtime-validation/multi-display
cp captures/phone_aa_capture.pcap captures/phone_sslkeylog.txt \
  captures/aa_messages_aa-17.3-multi-display.jsonl \
  captures/channel_map_aa-17.3-multi-display.json \
  captures/sdp_response_aa-17.3-multi-display.bin \
  /mnt/e/claude/personal/github/open-android-auto-clean/analysis/aa_apk_17.3.662804_apkm/runtime-validation/multi-display/
```

The capture set lives under:

```text
analysis/aa_apk_17.3.662804_apkm/runtime-validation/multi-display/
```

Record service discovery descriptors, transport channel IDs, AV setup/open messages, display IDs, input display IDs, distinct media streams, and focus changes. If the simulator cannot advertise all three simultaneously, record the exact supported topology and configuration limitation.

- [ ] **Step 6: Convert any usable capture and validate framing**

Convert each produced JSONL into validator format, create an ignored task-local decode baseline, then rerun validation:

```bash
repo_root=/mnt/e/claude/personal/github/open-android-auto-clean
runtime_root="$repo_root/analysis/aa_apk_17.3.662804_apkm/runtime-validation"

for scenario in video-focus-ui radio car-control multi-display; do
  capture_dir="$runtime_root/$scenario"
  raw_capture="$capture_dir/aa_messages_aa-17.3-${scenario}.jsonl"
  channel_map="$capture_dir/channel_map_aa-17.3-${scenario}.json"
  converted_capture="$capture_dir/validator-input.jsonl"
  local_baseline="$capture_dir/validator-baseline.normalized.json"

  if test ! -f "$raw_capture"; then
    continue
  fi

  PYTHONPATH="$repo_root" python3 "$repo_root/analysis/tools/proto_stream_validator/convert_capture.py" \
    "$raw_capture" "$converted_capture" --channel-map "$channel_map"

  PYTHONPATH="$repo_root" python3 "$repo_root/analysis/tools/proto_stream_validator/run.py" \
    --capture "$converted_capture" \
    --baseline "$local_baseline" \
    --bless \
    --reason "task-local Android Auto 17.3 framing and decode check"

  PYTHONPATH="$repo_root" python3 "$repo_root/analysis/tools/proto_stream_validator/run.py" \
    --capture "$converted_capture" \
    --baseline "$local_baseline"
done
```

Do not copy these task-local baselines into `analysis/baselines/`. Record channel ID, message ID, direction, and payload decode for every frame cited in the dossier.

- [ ] **Step 7: Close runtime rows and commit the tracked findings**

No `RT-*` row may remain `open`. Allowed outcomes are `confirmed-runtime`, `rejected`, or `runtime-unverified` with a concrete limitation.

Run:

```bash
if rg -n '^\| RT-.*\| open \|' analysis/reports/android-auto-17.3-update/runtime-validation.md; then
  exit 1
fi

git check-ignore -q analysis/aa_apk_17.3.662804_apkm/runtime-validation
git diff --check
```

Update the resume pointer to Task 10, append the handoff with every attempted command and result, then commit only tracked reports:

```bash
git add \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/runtime-validation.md \
  docs/session-handoffs.md
git commit -m "docs(capture): record 17.3 runtime validation attempt"
```

---

### Task 10: Freeze the Canonical Change Manifest

**Files:**

- Modify: `analysis/reports/android-auto-17.3-update/change-manifest.md`
- Modify: `analysis/reports/android-auto-17.3-update/README.md`
- Modify: `docs/session-handoffs.md`
- Review: all other dossier files

**Produces:** The exact publication contract. Tasks 11-13 may modify only canonical files named here.

- [ ] **Step 1: Confirm all in-scope research claims are closed**

Run:

```bash
rg -n '\| open \|' analysis/reports/android-auto-17.3-update
```

Expected: no `DIR-*`, `ID-*`, `SVC-*`, or `RT-*` row remains open. Gate table rows for publication and final verification may still be open.

- [ ] **Step 2: Add one manifest row per accepted correction**

Create stable change IDs in these groups:

- `CHG-VID-*` for video IDs, directions, and schemas;
- `CHG-CC-*` for car-control directions;
- `CHG-SEN-*` for sensor directions;
- `CHG-ID-*` for display/channel/service naming and descriptor compatibility;
- `CHG-CI-*` for CarIntent payload/docs when accepted;
- `CHG-CLM-*` and `CHG-BUF-*` for media findings;
- `CHG-REPORT-*` for audit, coverage, matcher, and handoff regeneration.

Every row must name exact files, exact semantic change, compatibility note, and verification command. Add `no canonical change` rows for confirmed radio claims and deferred findings so evidence is not silently dropped.

- [ ] **Step 3: Cross-check both directions of traceability**

Run:

```bash
rg -o 'DIR-[A-Z0-9-]+|ID-[A-Z0-9-]+|SVC-[A-Z0-9-]+|RT-[A-Z0-9-]+' \
  analysis/reports/android-auto-17.3-update/change-manifest.md | sort -u

rg -n 'confirmed-static|confirmed-runtime|rejected|deferred|runtime-unverified' \
  analysis/reports/android-auto-17.3-update/{message-matrix,services,runtime-validation}.md
```

Manually verify every accepted claim appears in a manifest row and every manifest evidence ID exists in exactly one dossier source file.

- [ ] **Step 4: Mark research gates complete and verify**

Update the dossier gate table: direction/ID, identity/compatibility, new services, and runtime validation become closed with links to their exit evidence. Canonical publication remains open.

Run:

```bash
rg -n 'CHG-VID-|CHG-CC-|CHG-SEN-|CHG-ID-|CHG-CI-|CHG-CLM-|CHG-BUF-|CHG-REPORT-' \
  analysis/reports/android-auto-17.3-update/change-manifest.md

git diff --check
```

- [ ] **Step 5: Checkpoint and commit**

Set the resume pointer to Task 11, append the handoff, and commit:

```bash
git add \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/change-manifest.md \
  docs/session-handoffs.md
git commit -m "docs(protocol): freeze Android Auto 17.3 change manifest"
```

---

### Task 11: Publish Message-ID and Direction Corrections

**Files:**

- Modify only `CHG-VID-*`, `CHG-CC-*`, and `CHG-SEN-*` files named by Task 10
- Expected proto candidates: `oaa/av/AVChannelMessageIdsEnum.proto`, `oaa/av/UiConfigMessages.proto`, `oaa/video/*.proto`, `oaa/carcontrol/CarControlMessages.proto`, four sensor message protos
- Expected docs: `docs/channels/video.md`, `docs/channels/carcontrol.md`, `docs/channels/sensor.md`, related cross-version docs
- Modify: `analysis/reports/android-auto-17.3-update/change-manifest.md`
- Modify: `analysis/reports/android-auto-17.3-update/README.md`
- Modify: `docs/session-handoffs.md`

**Produces:** Canonical IDs and directions that agree with the accepted 17.3 endpoint matrix.

- [ ] **Step 1: Capture the pre-change stale claims**

Run:

```bash
rg -n 'VIDEO_FOCUS_NOTIFICATION = 0x8009|UPDATE_UI_CONFIG_REQUEST = 0x800A|Phone.?HU|HU.?Phone' \
  oaa/av/AVChannelMessageIdsEnum.proto \
  oaa/av/UiConfigMessages.proto \
  oaa/video \
  oaa/carcontrol/CarControlMessages.proto \
  oaa/sensor \
  docs/channels/{video,carcontrol,sensor}.md
```

Expected: output includes claims rejected by Tasks 3-5. Preserve this command output in the Task 11 handoff as the red-state evidence.

- [ ] **Step 2: Apply the accepted video table exactly**

Update the AV message enum, video message comments, message names, and video documentation from `CHG-VID-*`. Remove historical names for IDs that Task 3 rejected. Keep an ID unnamed or explicitly reserved when Task 3 deferred it; do not shift a later name into an unproven slot.

- [ ] **Step 3: Apply accepted car-control and sensor directions**

Update proto comments, channel tables, cross-version notes, and verification reports from `CHG-CC-*` and `CHG-SEN-*`. All direction text must use the normalized perspective.

- [ ] **Step 4: Run targeted stale-claim checks**

Run:

```bash
rg -n 'VIDEO_FOCUS_NOTIFICATION = 0x8009|SetCarPropertyValueRequest.*HU.?Phone|SensorRequest.*HU.?Phone' \
  oaa docs/channels docs/cross-version analysis/reports/proto-verification
```

Expected: no active canonical hit. Historical archived material is outside this task.

- [ ] **Step 5: Compile all changed proto files**

Run:

```bash
mkdir -p /tmp/oaa-17-3-direction-check
protoc --proto_path=. --cpp_out=/tmp/oaa-17-3-direction-check \
  oaa/av/AVChannelMessageIdsEnum.proto \
  oaa/av/UiConfigMessages.proto \
  oaa/carcontrol/CarControlMessages.proto \
  oaa/sensor/SensorRequestMessage.proto \
  oaa/sensor/SensorStartResponseMessage.proto \
  oaa/sensor/SensorEventIndicationMessage.proto \
  oaa/sensor/SensorErrorMessage.proto \
  $(find oaa/video -name '*.proto' -print | sort)
```

Expected: exit zero.

- [ ] **Step 6: Mark manifest rows applied and commit**

Mark only the implemented `CHG-VID-*`, `CHG-CC-*`, and `CHG-SEN-*` rows `applied`. Update the resume pointer to Task 12 and append fresh verification to the handoff.

Run:

```bash
git diff --check
git add \
  oaa/av/AVChannelMessageIdsEnum.proto \
  oaa/av/UiConfigMessages.proto \
  oaa/video \
  oaa/carcontrol/CarControlMessages.proto \
  oaa/sensor/SensorRequestMessage.proto \
  oaa/sensor/SensorStartResponseMessage.proto \
  oaa/sensor/SensorEventIndicationMessage.proto \
  oaa/sensor/SensorErrorMessage.proto \
  docs/channels/video.md \
  docs/channels/carcontrol.md \
  docs/channels/sensor.md \
  docs/cross-version/video.md \
  docs/cross-version/carcontrol.md \
  docs/cross-version/sensor.md \
  analysis/reports/proto-verification/video.md \
  analysis/reports/proto-verification/carcontrol.md \
  analysis/reports/proto-verification/sensor.md \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/change-manifest.md \
  docs/session-handoffs.md
git commit -m "fix(proto): correct Android Auto 17.3 message directions"
```

Before staging, omit any listed candidate file not named by the frozen manifest.

---

### Task 12: Publish Identity, Compatibility, and New-Service Changes

**Files:**

- Modify only `CHG-ID-*`, `CHG-CI-*`, `CHG-CLM-*`, and `CHG-BUF-*` files named by Task 10
- Expected: `oaa/av/AVChannelData.proto`, `oaa/input/InputChannelConfigData.proto`, `oaa/control/ChannelDescriptorData.proto`, media protos, associated docs/audits
- Conditional create: `oaa/carintent/CarIntentMessage.proto`, `oaa/carintent/CarIntentMessage.audit.yaml`, `docs/channels/carintent.md`
- Modify: dossier manifest/index and handoff

**Produces:** Clean display/service API names, explicit 16.x/17.3 descriptor compatibility, and only the new-service schemas supported by the dossier.

- [ ] **Step 1: Capture the pre-change identity ambiguity**

Run:

```bash
rg -n 'channel_id = 6|Display/channel identifier|generic_notification|voice|fields 16-18|STUB CHANNEL|discards all data|UNKNOWN_5|needs wire capture' \
  oaa/av/AVChannelData.proto \
  oaa/control/ChannelDescriptorData.proto \
  oaa/media \
  docs/channels \
  analysis/reports/proto-verification
```

Preserve the output in the Task 12 handoff as the red-state evidence.

- [ ] **Step 2: Rename AV field 6 and update active consumers**

Rename proto field 6 to `display_id` without changing tag number or wire type. Update active docs, audit evidence, tooling references, and the Prodigy handoff. Keep `ChannelDescriptor.channel_id` unchanged as the transport channel ID.

- [ ] **Step 3: Apply the descriptor compatibility disposition**

Update fields 16-18 and surrounding comments from `CHG-ID-*`. Preserve 16.x compatibility only where the Task 6 classification supports it. Do not describe old field names as simultaneously valid 17.3 semantics.

- [ ] **Step 4: Publish the accepted CarIntent boundary**

If `CHG-CI-*` accepts the payload, create a proto2 message whose only proven payload field is the field-2 metadata string from `xgc`; document HU -> Phone use, service type 22, descriptor field 18, feature gate, and unknown raw message ID when still deferred. Do not create an intent-type enum or acknowledgement message without a confirmed wire field.

If Task 10 records `no public payload`, update descriptor and service documentation only and do not create `oaa/carintent/`.

- [ ] **Step 5: Update CarLocalMedia and BufferedMedia narrowly**

Replace the 16.1 “discard-only stub” statement with the accepted 17.3 endpoint facts. Define only BufferedMedia message ID 4 and `xkg` fields accepted by `CHG-BUF-*`; leave unproven IDs undocumented or explicitly unknown. Rename CarLocalMedia state value 5 only if `SVC-CLM-STATE5` was confirmed.

- [ ] **Step 6: Run naming and stale-claim checks**

Run:

```bash
rg -n 'channel_id = 6|Display/channel identifier|STUB CHANNEL|discards all data|needs wire capture' \
  oaa docs/channels analysis/reports/proto-verification analysis/reports/multi-display

rg -n 'display_id = 6|transport channel ID|service type 22|service type 21' \
  oaa docs/channels analysis/reports/multi-display
```

Expected: no active stale identifier/stub claim; new terminology is present.

- [ ] **Step 7: Compile the full proto tree**

Run:

```bash
mkdir -p /tmp/oaa-17-3-identity-check
protoc --proto_path=. --descriptor_set_out=/tmp/oaa-17-3-identity-check/all.pb \
  $(find oaa -name '*.proto' -print | sort)
```

Expected: exit zero with a non-empty descriptor set.

- [ ] **Step 8: Mark manifest rows applied and commit**

Update the resume pointer to Task 13 and append the exact changed set and verification to the handoff.

Stage only files named by the frozen manifest. Use the following candidate set, which is intentionally limited to this task:

```bash
git add \
  oaa/av/AVChannelData.proto \
  oaa/av/AVChannelData.audit.yaml \
  oaa/input/InputChannelConfigData.proto \
  oaa/input/InputChannelConfigData.audit.yaml \
  oaa/control/ChannelDescriptorData.proto \
  oaa/control/ChannelDescriptorData.audit.yaml \
  oaa/media/BufferedMediaSinkMessage.proto \
  oaa/media/CarLocalMediaPlaybackStatusMessage.proto \
  oaa/media/CarLocalMediaPlaybackStatusMessage.audit.yaml \
  docs/channels/media.md \
  docs/channels/display-routing.md \
  docs/channels/architecture.md \
  docs/channel-map.md \
  analysis/reports/multi-display/prodigy-maintainer-handoff.md \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/change-manifest.md \
  docs/session-handoffs.md

if test -d oaa/carintent; then
  git add oaa/carintent
fi
if test -f docs/channels/carintent.md; then
  git add docs/channels/carintent.md
fi
```

Omit a candidate path if the manifest marks it `no canonical change`. Then run:

```bash
git diff --cached --check
git commit -m "feat(proto): publish Android Auto 17.3 service identities"
```

---

### Task 13: Synchronize Audits, Reports, Coverage, and Prodigy Handoff

**Files:**

- Modify: audit sidecars associated with changed protos
- Modify: `analysis/reports/cross-version/17-3-schema-match.{json,md}` only if Task 1 accepted the fresh delta
- Modify: `analysis/reports/coverage-dashboard/coverage-dashboard.{json,md}`
- Modify: affected `analysis/reports/proto-verification/*.md`
- Modify: affected `docs/channels/*.md`, `docs/cross-version/*.md`, `docs/channel-map.md`
- Modify: `analysis/reports/multi-display/prodigy-maintainer-handoff.md`
- Modify: `docs/roadmap-current.md`
- Modify: dossier manifest/index and `docs/session-handoffs.md`

**Produces:** One consistent repository view of the new canonical contract and its evidence level.

- [ ] **Step 1: Validate all audit sidecars before editing**

Run:

```bash
PYTHONPATH=. pytest analysis/tools/seed_import/tests/test_audit_yaml_schema_validation.py -q
```

Expected: current audit suite passes. Record this pre-change result.

- [ ] **Step 2: Update changed audit sidecars from accepted evidence**

For each changed proto, add or replace evidence entries with version `17.3.662804-release`, APK hash, exact JADX class/method anchors, and runtime evidence when available. Do not retain a Gold direction claim contradicted by Task 3, 4, or 5.

- [ ] **Step 3: Decide the canonical matcher report from the Task 1 delta**

If Task 1 accepted all fresh rows, regenerate the committed report using the documented matcher command with committed output paths. If any of the three rows remains conflicted, retain the conservative committed report and document the reason in the dossier and handoff.

- [ ] **Step 4: Regenerate the coverage dashboard**

Run:

```bash
PYTHONPATH=. python3 -m analysis.tools.coverage_dashboard.run --repo-root .
```

Expected: both coverage dashboard files are rewritten with the current commit and sidecar counts.

- [ ] **Step 5: Synchronize documentation and the Prodigy handoff**

Ensure the handoff calls out:

- `AVChannel.display_id` as a breaking generated API rename;
- corrected video/car-control/sensor directions;
- corrected or reserved video IDs;
- CarIntent publication boundary;
- BufferedMedia's 17.3 active parsing versus its earlier stub state;
- per-display video/input routing; and
- every runtime-unverified behavior.

- [ ] **Step 6: Run audit, report, and reference checks**

Run:

```bash
PYTHONPATH=. pytest \
  analysis/tools/seed_import/tests/test_audit_yaml_schema_validation.py \
  analysis/tools/coverage_dashboard/tests \
  analysis/tools/arch_link_walker/tests \
  analysis/tools/cross_link_walker/tests -q

PYTHONPATH=. python3 -m analysis.tools.cross_link_walker.run --repo-root . --dry-run

rg -n 'channel_id = 6|VIDEO_FOCUS_NOTIFICATION = 0x8009|SetCarPropertyValueRequest.*HU.?Phone|SensorRequest.*HU.?Phone|STUB CHANNEL' \
  README.md oaa docs analysis/reports \
  -g '!research/archive/**' \
  -g '!docs/session-handoffs-archive.md'

git diff --check
```

Expected: tests pass; dry-run reports no required edits after synchronization; stale active claims return no hits except quoted historical-conflict evidence inside the new dossier.

- [ ] **Step 7: Mark report rows applied and commit**

Update `CHG-REPORT-*`, mark canonical publication closed in the dossier index, set the resume pointer to Task 14, and append the handoff. Stage the bounded report/documentation set:

```bash
git add \
  oaa/av/*.audit.yaml \
  oaa/video/*.audit.yaml \
  oaa/carcontrol/*.audit.yaml \
  oaa/sensor/*.audit.yaml \
  oaa/control/ChannelDescriptorData.audit.yaml \
  oaa/input/InputChannelConfigData.audit.yaml \
  oaa/media/*.audit.yaml \
  analysis/reports/android-auto-17.3-update \
  analysis/reports/coverage-dashboard/coverage-dashboard.json \
  analysis/reports/coverage-dashboard/coverage-dashboard.md \
  analysis/reports/proto-verification \
  analysis/reports/multi-display/prodigy-maintainer-handoff.md \
  docs/channels \
  docs/cross-version \
  docs/channel-map.md \
  docs/roadmap-current.md \
  docs/session-handoffs.md

if ! git diff --quiet -- analysis/reports/cross-version/17-3-schema-match.json analysis/reports/cross-version/17-3-schema-match.md; then
  git add analysis/reports/cross-version/17-3-schema-match.json analysis/reports/cross-version/17-3-schema-match.md
fi
if test -d oaa/carintent; then
  git add oaa/carintent/*.audit.yaml
fi
```

Commit only the report/documentation set:

```bash
git diff --cached --check
git commit -m "docs(protocol): synchronize Android Auto 17.3 evidence"
```

---

### Task 14: Run the Final Release Gate and Complete the Handoff

**Files:**

- Modify: `analysis/reports/android-auto-17.3-update/README.md`
- Modify: `analysis/reports/android-auto-17.3-update/change-manifest.md`
- Modify: `docs/session-handoffs.md`
- Modify: `docs/roadmap-current.md` only if execution changed priorities or sequencing

**Produces:** Fresh, recorded verification proving the release is internally consistent and ready for downstream consumption.

- [ ] **Step 1: Compile every active proto**

Run:

```bash
mkdir -p /tmp/oaa-17-3-release
protoc --proto_path=. --descriptor_set_out=/tmp/oaa-17-3-release/all.pb \
  $(find oaa -name '*.proto' -print | sort)
test -s /tmp/oaa-17-3-release/all.pb
```

Expected: exit zero and non-empty descriptor set.

- [ ] **Step 2: Run the complete relevant analysis-tool suite**

Run:

```bash
PYTHONPATH=. pytest \
  analysis/tools/apk_indexer/tests \
  analysis/tools/proto_schema_matcher/tests \
  analysis/tools/proto_schema_validator/tests \
  analysis/tools/proto_stream_validator/tests \
  analysis/tools/coverage_dashboard/tests \
  analysis/tools/arch_link_walker/tests \
  analysis/tools/cross_link_walker/tests \
  analysis/tools/seed_import/tests/test_audit_yaml_schema_validation.py -q
```

Expected: zero failures.

- [ ] **Step 3: Re-run the durable 17.3 schema matcher**

Run:

```bash
PYTHONPATH=. python3 -m analysis.tools.proto_schema_matcher.run \
  --jadx-root analysis/aa_apk_17.3.662804_apkm/jadx-output \
  --version 17.3.662804-release \
  --apk-sha256 1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344 \
  --lineage-yaml analysis/lineage/android-auto-17.3.yaml \
  --output-json analysis/aa_apk_17.3.662804_apkm/validation/17-3-schema-match-release.json \
  --output-md analysis/aa_apk_17.3.662804_apkm/validation/17-3-schema-match-release.md
```

Expected: no dispatch/schema conflicts introduced by the release. Review any count change against the frozen manifest before proceeding.

- [ ] **Step 4: Validate all committed non-media capture baselines**

Run:

```bash
PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py \
  --capture analysis/captures/non_media/2026-02-28-s25-cleanbuild.jsonl \
  --baseline analysis/baselines/non_media/2026-02-28-s25-cleanbuild.normalized.json

for scenario in general idle-baseline music-playback active-navigation; do
  PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py \
    --capture "analysis/captures/non_media/${scenario}.converted.jsonl" \
    --baseline "analysis/baselines/non_media/${scenario}.normalized.json"
done
```

Expected: every baseline validates. If a deliberate rename changes normalized output, review the exact diff and bless only with a specific reason tied to a `CHG-*` row.

- [ ] **Step 5: Run final stale-reference and traceability checks**

Run:

```bash
if rg -n '\| open \|' analysis/reports/android-auto-17.3-update; then
  exit 1
fi

if rg -n '\| (accepted|pending) \|' analysis/reports/android-auto-17.3-update/change-manifest.md; then
  exit 1
fi

rg -n 'channel_id = 6|VIDEO_FOCUS_NOTIFICATION = 0x8009|SetCarPropertyValueRequest.*HU.?Phone|SensorRequest.*HU.?Phone|STUB CHANNEL' \
  README.md oaa docs analysis/reports \
  -g '!research/archive/**' \
  -g '!docs/session-handoffs-archive.md'

git diff --check
git status --short
```

Expected: dossier contains no open claims, manifest contains no unapplied accepted rows, stale active claims are absent except conflict quotations in the dossier, diff check passes, and only the final dossier/handoff edits are dirty.

- [ ] **Step 6: Record the final handoff and release status**

Append a handoff entry containing:

- exact commits produced by Tasks 1-13;
- changed proto and generated API names;
- static-confirmed, runtime-confirmed, deferred, and runtime-unverified claim counts;
- every verification command and result from Tasks 14.1-14.5;
- the Prodigy handoff path; and
- the next one to three downstream implementation steps.

Mark final verification closed in the dossier index and set its resume pointer to `Release complete; next work is downstream Prodigy integration or a future capture-confidence pass.`

- [ ] **Step 7: Commit the release gate**

Run:

```bash
git add \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/change-manifest.md \
  docs/session-handoffs.md

if ! git diff --quiet -- docs/roadmap-current.md; then
  git add docs/roadmap-current.md
fi

git diff --cached --check
git commit -m "chore(protocol): verify Android Auto 17.3 release"
git status --short
```

Expected: commit succeeds and the worktree is clean.
