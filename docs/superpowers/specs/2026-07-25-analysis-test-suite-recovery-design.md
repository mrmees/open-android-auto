# Analysis Test Suite Recovery Design

Date: 2026-07-25
Status: Approved

## Context

The Android Auto 17.3 release branch passes its documented release gate: 736
relevant analysis-tool tests pass and all 247 active protos compile. The wider
`analysis/tools` test collection does not provide a trustworthy repository-wide
gate, however. A fresh aggregate run collected 1,726 tests and reported 1,484
passed, 241 failed, and 1 skipped.

The failures reproduce when the affected suites run independently, so they are
not test-order contamination. They fall into six bounded root-cause groups:

| Root cause | Failures |
| --- | ---: |
| Confidence-comment drift and obsolete confidence assumptions | 226 |
| Protobuf 4.21 `GetMessageClass` incompatibility | 9 |
| Hard dependency on ignored Android Auto 16.4 SQLite indexes | 2 |
| Obsolete multi-message sidecar heuristics | 2 |
| Mutable real-sidecar Platinum expectation | 1 |
| Missing cross-version category documentation | 1 |

This debt blocks merging `dev/android-auto-17.3-analysis` into `main`. The
cleanup must restore a green, reproducible aggregate gate without weakening
evidence policy or changing protocol schemas.

## Goals

1. Make the maintained `analysis/tools` suite pass in a clean checkout without
   ignored APK/JADX/index artifacts.
2. Keep audit YAML sidecars and
   `analysis/tools/seed_import/tier_policy.py` canonical for confidence.
3. Preserve the regression intent of existing tests instead of deleting tests
   to improve the pass count.
4. Support the repository-validated protobuf runtime, 4.21.12.
5. Provide one documented local verification entrypoint and an equivalent
   GitHub Actions check.
6. Prove that confidence-comment synchronization does not change protobuf wire
   descriptors.

## Non-goals

- No proto field-number, field-type, cardinality, enum-value, package, or
  message-semantics changes.
- No promotion of confidence tiers and no invention of audit evidence.
- No inclusion of private or ignored APK-derived databases in the repository.
- No changes to the `dist` publication contract.
- No cleanup of unrelated historical planning documents.

## Approaches Considered

### 1. Repair the aggregate suite in place — selected

Preserve the test inventory, update stale contracts to current policy, isolate
asset-heavy integration tests, and add a reproducible root gate.

This requires more care than narrowing the gate, but it retains the strongest
regression coverage and exposes genuine documentation drift.

### 2. Keep only the 736-test release gate

This is faster, but it would hide confidence-comment drift, protobuf runtime
incompatibility, and missing cross-version documentation. It is rejected.

### 3. Delete and rewrite the legacy suites

This would remove accumulated assumptions, but would also discard useful
fixtures and behavioral checks. It is rejected.

## Design

### 1. Canonical verification contract

Add a small root verification surface:

- a test dependency manifest covering pytest, PyYAML, jsonschema, and a
  protobuf range that includes 4.21.12;
- pytest marker configuration for asset-heavy integration checks;
- a root command that compiles every active proto and runs the maintained
  aggregate suite; and
- a GitHub Actions workflow that invokes the same command on a clean checkout.

The default command must not download or assume private Android Auto artifacts.
Optional integration checks must be separately named and must skip with a
specific missing-artifact reason when their local prerequisites are absent.

### 2. Confidence sidecar/comment consistency

The audit YAML sidecar remains the source of truth. Proto confidence comments
are a generated convenience mirror.

Enhance `analysis.tools.seed_import.annotate` so it can render expected content
without writing and expose a `--check` mode. The check must:

- derive the tier and evidence labels from the sidecar;
- treat a proto without a sidecar as `unverified` rather than preserving an
  unsupported historical tier label;
- report the exact files that differ;
- return nonzero on drift; and
- leave the worktree unchanged.

The repair mode will synchronize comments across `oaa/` using the same render
path. It must be idempotent. Existing confidence tests will assert against the
canonical renderer and executable tier policy rather than hard-coding that all
Silver evidence has one particular pair of evidence types.

Before and after synchronization, compile all active protos to descriptor sets
and require byte-identical descriptor output. Any descriptor change is a hard
stop because this work is documentation-only at the proto layer.

### 3. Protobuf runtime compatibility

Centralize message-class construction behind one compatibility helper. The
helper will use module-level `message_factory.GetMessageClass` when available
and fall back to `MessageFactory().GetPrototype` for protobuf 4.21.12.

The existing compatibility behavior in the stream validator is the reference
pattern. DHU-divergence and OEM-VW decoding must consume the same helper so the
runtime boundary is tested once rather than reimplemented.

### 4. APK-index-dependent checks

Tests of ordinary matching logic must use committed, minimal fixtures. Tests
that validate a complete historical Android Auto database snapshot remain
integration checks and must skip explicitly when the ignored database is not
present.

The default aggregate gate will still collect these tests, making their skipped
state visible. A separate integration command will run them when the documented
local assets exist. Missing assets must never be reported as a passing snapshot
comparison.

### 5. Current sidecar contracts

Update two legacy contracts without reducing coverage:

- Multi-message sidecar tests will validate the structured composite sidecar
  shape and covered schema messages, not parse an old `Mapped ...` prose prefix
  or reject the current `... (all)` message label.
- Platinum schema validation will use the committed Platinum fixture. It will
  not require a mutable production sidecar to remain Platinum after the
  canonical tier policy recalculates it.

### 6. Cross-version documentation coverage

The failing category check exposed real documentation gaps. Add cross-version
tables for `carintent`, `mediabrowser`, `mic`, and `verification`, following the
existing table format and citing only committed mappings. Do not add empty
placeholder tables or invent class names.

The test will continue requiring a table for every `oaa/` category containing
active `.proto` files. Categories may be aliased to another table only through
an explicit, documented mapping checked by the test.

### 7. Repository workflow records

Update `docs/roadmap-current.md` to put aggregate-suite recovery before the
17.3 analysis-to-main merge. Append implementation results and exact commands
to `docs/session-handoffs.md` before completion.

## Implementation Order

1. Establish the dependency manifest, pytest markers, and root verification
   command while preserving the current red baseline.
2. Add protobuf 4.21 compatibility tests, then centralize the helper.
3. Add annotation check/idempotence tests, harden the renderer, and synchronize
   proto comments under descriptor-equivalence protection.
4. Convert APK-index-dependent tests to fixture-backed unit checks plus explicit
   optional integration checks.
5. Update the grouping and Platinum contracts.
6. Add the four missing cross-version documentation tables and verify paths.
7. Run the aggregate gate, the original 736-test release gate, proto
   compilation, annotation check, and documentation sanity checks.
8. Add CI only after the exact local command is green, then record the handoff.

## Error Handling and Stop Conditions

Stop implementation and investigate if any of the following occurs:

- the compiled descriptor set changes during confidence synchronization;
- a proposed test change would accept evidence that `tier_policy.py` rejects;
- a fixture cannot represent the behavior without copying ignored/private
  artifacts;
- an integration test passes without executing its asserted snapshot;
- a cross-version table would require an unsupported class mapping; or
- the green aggregate gate depends on test deletion, broad `xfail`, or an
  unexplained skip.

## Verification

The implementation is ready for branch integration only when fresh evidence
shows:

1. the documented root verification command exits zero;
2. every maintained `analysis/tools` unit/repository test passes, with only
   explicitly asset-dependent integration checks skipped;
3. the original 736-test Android Auto 17.3 release gate remains green;
4. all 247 active protos compile;
5. pre/post confidence-sync descriptor sets are byte-identical;
6. annotation `--check` is clean and a second repair run is a no-op;
7. cross-version documentation paths and tables pass sanity checks;
8. `git diff --check` succeeds; and
9. `docs/session-handoffs.md` records the commands and results.

Only after these gates pass should `dev/android-auto-17.3-analysis` be merged
into `main` and removed.

## Advisor Note

An Opus review was requested through the local Claude advisor. One read-only
job stalled after launching internal reviewers, and two bounded read-only
workers plus a concise advice pass exhausted their turn limits without
returning a verdict. No advisor output was treated as evidence, and no advisor
made workspace changes.
