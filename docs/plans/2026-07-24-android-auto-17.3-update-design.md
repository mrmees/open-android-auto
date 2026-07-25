# Android Auto 17.3 Evidence-Gated Protocol Update Design

**Date:** 2026-07-24

**Status:** Approved design

**Scope:** Protocol definitions, protocol documentation, evidence reports, and analysis tooling in this repository

## Objective

Produce one cohesive Android Auto 17.3 protocol-reference update that:

- preserves useful Android Auto 16.x wire compatibility;
- corrects message IDs, directions, field semantics, and generated API names where the 17.3 phone implementation provides defensible evidence;
- closes the highest-value new-service questions before publication;
- attempts targeted runtime validation without making unavailable hardware an unconditional release blocker; and
- leaves a concise, implementation-oriented handoff for OpenAuto Prodigy.

The update is evidence-gated. Research conclusions must pass through a tracked release dossier before they alter canonical protobuf definitions or channel documentation.

## Context

The repository already contains a strong Android Auto 16.2 verification baseline and a partially reconstructed 17.3 schema baseline. The current 17.3 work adds durable APK/JADX provenance, trusted-parent schema matching, blended-UI schemas, and a static multi-display model. It also exposes several publication risks:

- direct 17.3 endpoint behavior appears to contradict existing message-direction comments for video and car control;
- the video message-ID sequence after video focus may contain stale or shifted labels;
- `AVChannel` field 6 is treated as a logical display ID by the phone implementation despite its historical `channel_id` name;
- `ChannelDescriptor` fields added or reidentified in 17.3 need an explicit cross-version compatibility policy;
- CarIntent, BufferedMedia, and CarLocalMedia have different evidence and reachability levels; and
- simultaneous MAIN, CLUSTER, and AUXILIARY behavior is statically supported but not yet confirmed by a live session.

Wire capture is valuable but cannot be the only route to publication. Many features require special head-unit capabilities, simulator configuration, feature flags, or hardware that may be unavailable. The repository therefore needs a repeatable way to distinguish a source-proven schema from runtime-confirmed behavior.

## Approved Decisions

| Decision | Policy |
|---|---|
| Release endpoint | Include research, canonical proto/documentation changes, verification, and downstream handoff in one program. |
| Execution shape | Use a sequential evidence-gated release train with narrow checkpoints. |
| Runtime captures | Conditional gate: attempt focused captures, but permit publication of defensible static findings with explicit runtime-unverified labels. |
| Cross-version compatibility | Maintain a wire-compatible 16.x/17.3 superset when field numbers and wire types permit it; document version-specific presence and semantics. |
| Generated API compatibility | Not a constraint for this release. Proven misleading identifiers may be cleanly renamed. |
| New services | Fully trace CarIntent; validate remaining CarLocalMedia semantics; classify BufferedMedia reachability and gating without requiring a full implementation. |
| Repository restructuring | Keep the change narrow. Add one 17.3 release dossier and do not reorganize historical reports. |

## Non-Goals

- Implementing Android Auto runtime behavior or Prodigy features in this repository.
- Resolving every remaining structural collision in the 17.3 schema matcher.
- Filling every low-value placeholder enum or undocumented media option.
- Proving all supported display topologies on physical hardware before publication.
- Reorganizing the existing research archive or rewriting the repository's complete confidence framework.
- Treating an obfuscated class-name match or a globally unique protobuf shape as sufficient semantic proof by itself.

## Release Architecture

The program has seven sequential gates. A gate may defer an individual claim, but unresolved contradictions may not flow into canonical definitions.

### Gate 1: Preserve the Current 17.3 Baseline

Review and preserve the existing uncommitted 17.3 work as a distinct checkpoint:

- durable APKM/APK/JADX provenance;
- multi-display evidence and Prodigy maintainer handoff;
- schema-matcher documentation changes;
- roadmap and session-handoff updates; and
- the fresh matcher delta relative to the committed 17.3 report.

The fresh matcher differences involving `BluetoothChannel`, `PhoneConnectionConfig`, and `WifiInfoResponse` must be reviewed before replacing the committed report. Baseline preservation must not silently promote those rows.

**Exit condition:** the current evidence is reproducible, internally referenced, verified with documentation sanity checks and the matcher smoke command, and committed independently of new conclusions.

### Gate 2: Audit Message Directions and Video IDs

Build an endpoint-derived message matrix for the high-risk channels:

- video;
- car control;
- sensor;
- radio; and
- any control-channel messages needed to interpret their lifecycle.

For each message, record the raw ID, phone endpoint, phone action (`send` or `receive`), canonical message, current documented direction, corrected direction, protobuf class, and exact source anchors. The video sequence beginning with focus messages `0x8007` and `0x8008` must be traced far enough to settle Update UI Config, action-taken, overlay, UI-token, media-stats, and related message labels.

Direction is always written from the head-unit perspective as `HU -> Phone` or `Phone -> HU`. Phone endpoint send/receive evidence is converted explicitly rather than copied without perspective normalization.

**Exit condition:** every direction or message-ID change proposed for publication has a non-contradictory endpoint trace, and stale canonical rows are listed in the change manifest.

### Gate 3: Normalize Protocol Identity and Compatibility

Define and apply distinct meanings for:

- transport channel ID;
- GAL service type;
- logical display ID; and
- input-to-display binding ID.

Rename `AVChannel` field 6 from `channel_id` to `display_id` if the complete 17.3 construction and consumption trace remains consistent. Review related generated API names and documentation for the same ambiguity.

For fields whose 16.x and 17.3 interpretations differ, classify the situation as one of:

1. previous mapping was incorrect;
2. optional field was added or removed while retaining its meaning;
3. semantic field reuse occurred across versions; or
4. evidence is insufficient.

Cases 1 and 2 may use the canonical superset policy. Case 3 requires an explicit compatibility representation or version note that avoids pretending one identifier has a single universal meaning. Case 4 is deferred.

**Exit condition:** all identifiers changed by the release have one documented semantic domain, and every retained compatibility field has an explicit version note.

### Gate 4: Close the New-Service Frontier

#### CarIntent

Trace the service-type 22 endpoint from descriptor acceptance through message dispatch and payload use. Recover, when evidence permits:

- message IDs and directions;
- the `xgc` payload schema and child types;
- intent type values;
- navigation or ADAS metadata semantics;
- capability and feature-flag activation; and
- error or acknowledgement behavior.

CarIntent receives a public schema only if identity and field structure are independently defensible. Otherwise, the dossier records the service marker and bounded unknowns without inventing a payload.

#### CarLocalMedia

Confirm the remaining playback-state value and the endpoint's initial state, subscription, and update behavior where static or runtime evidence is available. Existing correct definitions should not be rewritten merely for stylistic consistency.

#### BufferedMedia

Determine whether service type 21 has a reachable GAL control protocol in the target build or is a feature-gated experiment centered on a separate data plane. Record its factory gate, endpoint lifecycle, messages, and dependencies that can be proven. A full BufferedMedia protocol is not a release requirement when reachability or semantic identity remains unproven.

**Exit condition:** CarIntent is either publication-ready or explicitly excluded with bounded evidence; CarLocalMedia's targeted unknown is closed or deferred; BufferedMedia is classified without speculative schemas.

### Gate 5: Attempt Focused Runtime Validation

Attempt the smallest practical probes for:

- video focus and Update UI Config traffic;
- integrated-overlay or blended-UI negotiation;
- radio service activation and initial state;
- car-control registration, state report, set request, and result; and
- concurrent MAIN, CLUSTER, and AUXILIARY discovery, channel opening, media streams, focus, and input routing.

Each probe records the intended setup, exact commands or simulator configuration, outcome, captured frames or logs, and why a probe could not run. Runtime evidence may confirm behavior or reveal contradictions. It may not be used to assign a schema when framing or message identity is ambiguous.

**Exit condition:** all practical probes were attempted; contradictions are returned to the relevant static gate; unavailable environments are labeled `runtime-unverified` in the dossier and downstream documentation.

### Gate 6: Publish the Canonical Update

Apply the accepted change manifest to:

- `oaa/**/*.proto` definitions and enums;
- message-ID enums and direction comments;
- audit sidecars and confidence/provenance metadata;
- `docs/channels/` and cross-version documentation;
- schema-match and coverage reports where their inputs are current;
- generated or consolidated reference documents that expose changed claims; and
- the Prodigy-facing handoff.

Publication is one coherent release, but commits remain narrow enough to review. Recommended commit boundaries are baseline preservation, direction/ID corrections, identity/compatibility changes, new-service schemas, documentation/audit synchronization, and final generated-report refresh.

**Exit condition:** every accepted dossier row is either represented in canonical files or marked `no canonical change`, and every canonical change maps back to an accepted evidence row.

### Gate 7: Verify and Hand Off

Run the smallest complete verification set for all changed surfaces, record fresh evidence in `docs/session-handoffs.md`, and prepare a concise Prodigy handoff covering:

- breaking generated API renames;
- corrected head-unit message directions;
- corrected video IDs;
- newly exposed or deliberately excluded services;
- display routing semantics; and
- runtime-confirmed versus runtime-unverified behavior.

**Exit condition:** all required verification passes, or the release remains incomplete with the failing gate and next action recorded.

## Durable Artifact Structure

The release adds one focused directory rather than reorganizing existing research:

```text
analysis/reports/android-auto-17.3-update/
├── README.md
├── message-matrix.md
├── services.md
├── runtime-validation.md
└── change-manifest.md
```

### `README.md`

The only required entry point. It contains release status, gate status, APK identity, tool versions, primary evidence locations, artifact links, and a resume pointer.

### `message-matrix.md`

Contains endpoint-derived IDs, directions, payload identities, version differences, evidence anchors, and disposition for video, car control, sensor, radio, and required control messages.

### `services.md`

Contains the CarIntent reconstruction and the bounded CarLocalMedia and BufferedMedia investigations. It separates descriptor presence, endpoint reachability, schema identity, activation conditions, and runtime confirmation.

### `runtime-validation.md`

Defines each probe before execution and records whether it passed, contradicted static findings, could not be activated, or could not be attempted. It links captures and logs without duplicating raw evidence in Git.

### `change-manifest.md`

Maps accepted evidence rows to exact canonical files and intended changes. It is the publication checklist and the final completeness cross-check.

The ignored versioned APK/JADX directory remains the primary-source workspace. Git tracks its provenance, reproducible commands, conclusions, and narrowly relevant excerpts or hashes—not the full decompile.

## Evidence Model

Each claim row records:

- stable claim ID;
- Android Auto version and APK hash;
- protocol area and message/service name;
- raw message or service ID;
- canonical protobuf identity;
- phone endpoint and method;
- phone action and normalized wire direction;
- exact source anchors;
- schema or semantic finding;
- runtime result;
- confidence and status; and
- canonical disposition.

Allowed statuses are:

- `open` — question is defined but not yet investigated;
- `confirmed-static` — direct source evidence is non-contradictory;
- `confirmed-runtime` — framed runtime traffic confirms the claim;
- `rejected` — evidence disproves the candidate interpretation;
- `deferred` — bounded outside this release with a reason; and
- `blocked` — contradictory evidence prevents publication.

Static and runtime confidence are separate dimensions. A schema can be source-proven but runtime-unverified; an observed frame can be runtime-real while its field semantics remain unknown.

## Evidence Flow

1. APK source, matcher output, or framed capture creates a candidate claim.
2. The relevant dossier matrix records the candidate and exact provenance.
3. Cross-version lineage, trusted-parent structure, endpoint use, and runtime traffic are compared.
4. Contradictions return the claim to investigation; absence of practical runtime access is recorded but does not erase static evidence.
5. Accepted claims enter the change manifest.
6. Canonical files are updated from the manifest.
7. Compilation, tool tests, report regeneration, and reference checks validate the published result.

No canonical direction, message ID, semantic field name, or new payload schema should bypass this flow.

## Failure and Uncertainty Handling

- A contradiction blocks only the affected claim and dependent changes.
- A decompiler failure triggers a bounded fallback such as simple JADX, bytecode inspection, alternate class lineage, or runtime capture; the fallback and its limitations are recorded.
- Failure to find a sender or receiver is not proof of absence unless searched files, symbols, and activation paths are documented.
- A runtime activation failure records the attempted configuration and observed behavior rather than being converted into a protocol claim.
- Gated, unreachable, or marker-only services remain research findings unless their wire schema is independently established.
- The update does not expand to unrelated collisions merely because they are nearby in the matcher report.
- Every meaningful checkpoint refreshes the dossier resume pointer and appends a repository handoff entry.

## Verification Strategy

The implementation plan will name exact commands for changed files. At minimum, the final release verifies:

1. All active protobuf files compile with `protoc`.
2. Changed proto audit sidecars validate against `docs/verification/audit-schema.json`.
3. Relevant schema matcher, schema validator, APK indexer, and stream validator tests pass.
4. A fresh 17.3 schema matcher run completes from the durable JADX tree and its delta is reviewed before promotion.
5. Coverage and generated reports are regenerated only from current inputs.
6. Renamed proto identifiers have no stale references in active documentation or tooling.
7. Direction and message-ID tables agree across protos, channel docs, reports, and the Prodigy handoff.
8. Documentation path and link sanity checks pass.
9. `git diff --check` passes.
10. `docs/session-handoffs.md` records commands, results, remaining runtime-unverified claims, and the next one to three steps.

## Release Acceptance Criteria

The Android Auto 17.3 protocol update is complete when:

- the pre-existing 17.3 baseline is preserved separately;
- the high-risk direction and video-ID audit has no unresolved contradiction in published rows;
- transport channel IDs, service types, display IDs, and input bindings are consistently named;
- the approved clean API renames are applied and documented;
- 16.x compatibility fields retained in the canonical superset carry accurate version notes;
- CarIntent is published only to the extent supported by evidence;
- CarLocalMedia and BufferedMedia have explicit, bounded dispositions;
- focused runtime validation has been attempted and its limits are visible;
- every canonical change is traceable through the change manifest;
- all required verification passes with fresh recorded output; and
- the Prodigy maintainer can identify breaking API changes, required handler-direction changes, display-routing implications, and unverified runtime behavior without consulting chat history.
