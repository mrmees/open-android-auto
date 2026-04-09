---
phase: 09-oem-methodology-divergence-report
plan: 01
subsystem: verification-methodology
tags: [jsonschema, yaml, pytest, tier-ladder, platinum-tier, oem-evidence, cross-link-walker]

requires:
  - phase: 07-vw-capture-analysis
    provides: "VW SDP parser (oem_vw_parser), coverage.json, msg-type-classification.json, OEM-01 label taxonomy"
  - phase: 08-16-4-cross-version-validation
    provides: "16-4-delta-report.json (Phase 10 attribution source), schema migration precedent for additive evolution, append-only walker semantics, test_promoted_sidecars.py baseline"
provides:
  - "audit-schema.json v3 — platinum + retracted tiers, platinum_evidence type, 10 scope fields, closed MATCH/NOMATCH enums, sidecar-level platinum_scope + oem_match_pending_gold"
  - "01-confidence-tiers.md rewrite — Platinum strictly above Gold, Gold redefinition matches existing 32 Gold sidecars, retracted non-ordinal state, Platinum / single-OEM badge rule"
  - "05-oem-match-policy.md — 8 MATCH + 4 NOMATCH rules with definitions, examples, Phase 10 citation format"
  - "06-capture-non-claim-boundary.md — single source of truth for 5 non-claim surfaces (channel_id, flags, outer frame headers, fragmentation, encryption)"
  - "cross_link_walker package — byte-idempotent sentinel walker with self-exclusion; inserted TIER-05 callouts into 5 channel docs"
  - "dhu_divergence test scaffold package — 9 schema tests + 3 match policy tests + 2 tier doc tests + 1 non-claim doc test + 1 example sidecar test + 1 requirements text test + 6 retracted sidecar backstop tests"
  - "VideoFocusRequestMessage.audit.yaml — first committed Gold→Platinum promotion, MATCH-08 SDP descriptor match citation"
  - "REQUIREMENTS.md TIER-01 text correction — oem_evidence → platinum_evidence"
affects: [phase-10-gold-promotion-walk, phase-11-channel-architecture-reference, phase-12-coverage-dashboard]

tech-stack:
  added: [jsonschema 2020-12 if/then/else conditionals, closed-enum items validation]
  patterns: [sentinel-based idempotent walker with path-suffix self-exclusion, cross-file integrity tests asserting schema enum equals doc heading set, parametric backstop over legacy-state sidecar inventory]

key-files:
  created:
    - docs/verification/05-oem-match-policy.md
    - docs/verification/06-capture-non-claim-boundary.md
    - analysis/tools/dhu_divergence/__init__.py
    - analysis/tools/dhu_divergence/tests/conftest.py
    - analysis/tools/dhu_divergence/tests/test_schema_migration.py
    - analysis/tools/dhu_divergence/tests/test_example_sidecar.py
    - analysis/tools/dhu_divergence/tests/test_requirements_text.py
    - analysis/tools/dhu_divergence/tests/test_tier_docs.py
    - analysis/tools/dhu_divergence/tests/test_match_policy_doc.py
    - analysis/tools/dhu_divergence/tests/test_non_claim_doc.py
    - analysis/tools/dhu_divergence/tests/test_retracted_sidecars.py
    - analysis/tools/dhu_divergence/tests/fixtures/example_platinum_sidecar.audit.yaml
    - analysis/tools/cross_link_walker/__init__.py
    - analysis/tools/cross_link_walker/walker.py
    - analysis/tools/cross_link_walker/run.py
    - analysis/tools/cross_link_walker/tests/conftest.py
    - analysis/tools/cross_link_walker/tests/test_walker.py
    - analysis/tools/cross_link_walker/tests/test_idempotency.py
    - analysis/tools/cross_link_walker/tests/fixtures/channel_doc_clean.md
    - analysis/tools/cross_link_walker/tests/fixtures/channel_doc_with_link.md
    - analysis/tools/cross_link_walker/tests/fixtures/non_claim_doc.md
  modified:
    - docs/verification/audit-schema.json
    - docs/verification/01-confidence-tiers.md
    - docs/verification/02-audit-trail-format.md
    - docs/verification/03-verification-procedures.md
    - docs/channels/wifi-projection.md
    - docs/channels/audio.md
    - docs/channels/video.md
    - docs/channels/sensor.md
    - docs/channel-map.md
    - oaa/video/VideoFocusRequestMessage.audit.yaml
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Tier ladder locked at unverified → bronze → silver → gold → platinum, with retracted as a non-ordinal state outside the ordering"
  - "Gold redefined as deep-trace APK + cross-version verified — matches the 32 existing Gold sidecars, no migration required"
  - "Platinum is strictly above Gold — Silver protos matched in OEM capture cannot jump directly; they receive oem_match_pending_gold: true and wait for Gold prerequisites"
  - "Badge rendering locked at Platinum / single-OEM and Platinum / multi-OEM — readers never see bare Platinum, naming the single-OEM trap on the badge instead of in a prose footnote"
  - "8 MATCH rules (MATCH-01..08) + 4 NOMATCH rules (NOMATCH-01..04) as closed enum in the schema, cross-file integrity test asserts schema enum exactly equals doc MATCH headings"
  - "MATCH-03 (reassembled multi-fragment) kept in the closed enum despite zero v1.5 usage — removing later would be a breaking schema change"
  - "Walker uses sentinel-substring detection for idempotency and path-suffix matching for self-exclusion — SENTINEL is the first non-blank line of the callout block, comparison is byte-equality"
  - "Walker target list is explicit (5 files) not glob-discovered — keeps the scope tight and audit-trail clear"
  - "Rule 1 auto-fix: whitelisted 10 legacy top-level sidecar fields (wire_msg_id, direction, channel, handler, class_mapping, retraction, retraction_reason, replaced_by, previous_evidence, retracted) and 2 legacy evidence types (deep_trace, apk_deep_trace) so the 6 retracted sidecars + VideoFocusRequestMessage validate cleanly. Plan assumed only the tier enum addition would be needed; reality required the legacy field whitelist too."
  - "Phase 8 baseline was 334 passed / 1 pre-existing failure (NavigationDistanceMessage), not 110/1 as the plan's <interfaces> block stated. Baseline preserved exactly."

patterns-established:
  - "JSON Schema draft 2020-12 if/then/else for discriminator-based required fields — platinum_evidence entries trigger one set of required fields, applicability=fields triggers another, all while keeping additionalProperties: false on the outer evidence_entry"
  - "Cross-file integrity test pattern: assert that a schema enum exactly equals the set of level-3 heading IDs in a companion doc, prevents silent drift between machine-readable schema and human-readable reference"
  - "Sentinel-based idempotent walker: first non-blank line of the inserted block is the idempotency key; second run produces zero git diff; file write happens only if sentinel substring is absent"
  - "Parametric backstop over a small legacy-state inventory: enumerate every known pre-Phase-N sidecar that must continue to validate, run schema validation on each, fail loud if any drops out"

requirements-completed: [TIER-01, TIER-02, TIER-03, TIER-05]

duration: 19min
completed: 2026-04-09
---

# Phase 9 Plan 01: OEM Methodology Surface Summary

**Audit schema v3 with Platinum tier strictly above Gold, closed-enum MATCH/NOMATCH rules, TIER-05 non-claim doc, byte-idempotent cross-link walker, and first committed Gold→Platinum promotion citing MATCH-08.**

## Performance

- **Duration:** 19 min
- **Started:** 2026-04-09T11:53:05Z
- **Completed:** 2026-04-09T12:12:19Z
- **Tasks:** 8
- **Files created:** 20
- **Files modified:** 11
- **Tests added:** 30 (all green, zero failures, zero skips)

## Accomplishments

- **Schema migration landed first** with the Phase 8 backward-compat gate
  preserved at 334 passed / 1 pre-existing failure. The 6 retracted sidecars
  (not 1, as CONTEXT.md assumed) now validate cleanly against the migrated
  schema via a parametric backstop test.
- **Platinum tier introduced strictly above Gold** with Gold redefined as
  "deep-trace APK + cross-version verified" — matches the 32 existing Gold
  sidecars with zero migration. Retracted added as a non-ordinal state,
  closing a pre-existing schema leak.
- **8+4 match rule set published** in `05-oem-match-policy.md` with closed
  enum enforcement in `audit-schema.json`. A cross-file integrity test asserts
  the schema enum exactly equals the doc's MATCH-NN level-3 headings — future
  drift between the doc and schema is caught at test collection time.
- **TIER-05 non-claim boundary centralized** in a new doc that names the 5
  surfaces the on-phone hook cannot validate and cross-links NOMATCH-01.
  Byte-idempotent sentinel walker inserted the locked callout block into
  5 channel docs with correct relative paths per file (`../verification/`
  vs `verification/` based on depth).
- **First Gold→Platinum promotion committed:** `VideoFocusRequestMessage`
  cites MATCH-08 (SDP descriptor match) with placeholder msg_seq/ts_ms for
  Phase 10 to overwrite after deep inspection.
- **REQUIREMENTS.md TIER-01 text correction:** `oem_evidence` →
  `platinum_evidence`. Caught by a negative-grep test that will fail if a
  future edit reintroduces the old wording.

## Task Commits

Each task was committed atomically, in strict dependency order:

1. **Task 1: Schema migration (MANDATORY FIRST)** — `a89d84c` (feat)
2. **Task 2: Package + test scaffolds** — `aec2d7d` (chore)
3. **Task 3: Schema migration unit tests (9 tests)** — `5730173` (test)
4. **Task 4: 05-oem-match-policy.md + 3 tests** — `02f6486` (docs)
5. **Task 5: 06-capture-non-claim-boundary.md + test** — `29fd281` (docs)
6. **Task 6: 01/02/03 rewrites + 2 tier doc tests** — `9f6b9f8` (docs)
7. **Task 7: Walker impl + 7 tests + live insert** — `f8b1e3d` (feat)
8. **Task 8: Example sidecar promotion + REQUIREMENTS fix + 2 tests** — `03bcd73` (feat)

## Schema Migration Details

**Fields added to `audit-schema.json`:**

- `$defs.confidence_tier.enum`: added `platinum`, `retracted` (total enum now 6 values)
- `$defs.evidence_entry.properties.type.enum`: added `platinum_evidence`, `apk_deep_trace`, `deep_trace` (Rule 1 auto-fix for retracted backward compat)
- `$defs.evidence_entry.properties`: added 10 platinum_evidence scope fields
  (`capture_path`, `vehicle_metadata`, `msg_seq`, `ts_ms`, `message_completeness`,
  `attribution_method`, `oem_scope`, `applicability`, `fields`, `match_rules`)
  plus optional `nomatch_rules`
- `$defs.evidence_entry.allOf`: 3 conditional `if/then` blocks enforcing
  platinum_evidence required fields, `applicability=fields → fields required`,
  `applicability=message → fields forbidden`
- Top-level `properties`: added `platinum_scope`, `oem_match_pending_gold`, plus
  10 legacy whitelist fields (`wire_msg_id`, `direction`, `channel`, `handler`,
  `class_mapping`, `retraction`, `retraction_reason`, `replaced_by`,
  `previous_evidence`, `retracted`) — Rule 1 auto-fix
- Top-level `allOf`: 1 conditional enforcing `confidence=platinum → platinum_scope required`

`additionalProperties: false` is preserved on both the outer root object and
`evidence_entry` — no relaxation of the strict-schema contract.

**Backward compat gate:** `PYTHONPATH=. pytest analysis/tools/cross_version/tests/test_promoted_sidecars.py`
holds at **334 passed / 1 failed** (NavigationDistanceMessage, pre-existing,
documented in Phase 8 `deferred-items.md`, unrelated). The Phase 9 migration
introduced zero regressions.

## Match Policy Rule Count and Live Usage

| Rule | Name | v1.5 live usage |
|------|------|------------------|
| MATCH-01 | Message presence | Used by Phase 10 as baseline for every promotion with any observation |
| MATCH-02 | Standalone full payload | Used whenever `label=standalone` per OEM-01; ~4147 records eligible |
| MATCH-03 | Reassembled multi-fragment | **Zero usage in v1.5** — Phase 7 classifier reports `reassembled=0`. Kept in enum for forward-compat |
| MATCH-04 | Field-level value match | Used whenever Phase 10 cites specific `fields` |
| MATCH-05 | Enum value match | Used for enum-field verifications |
| MATCH-06 | Repeat observation | Used when `(msg_type, direction)` observed N≥2 times |
| MATCH-07 | Cross-direction observation | Used when both phone→HU and HU→phone observed |
| MATCH-08 | SDP descriptor match | **Used by the first Platinum promotion** (VideoFocusRequestMessage) — the minimum honest citation when only SDP-level evidence is available |

NOMATCH rules (all 4 documented for Phase 10 / 11 consumption; NOMATCH-01 is
the primary TIER-05 citation):

| Rule | Name | Role |
|------|------|------|
| NOMATCH-01 | Below framing layer | TIER-05 operationalized — claims about channel_id / flags / outer frame headers / fragmentation / encryption |
| NOMATCH-02 | Not observed | Honest absence, does not demote |
| NOMATCH-03 | Ambiguous attribution | msg_type collision across services |
| NOMATCH-04 | Fragment-only observation | OEM-01 `continuation_or_garbage` label |

## Cross-Link Walker Target List

All 5 target docs were clean (no pre-existing sentinel) before the walker run.
Each received the locked callout block once; a second walker run is a
byte-perfect no-op.

| Target | Variant | Pre-walk sentinel? | Post-walk? | Line of insertion |
|--------|---------|---------------------|------------|--------------------|
| `docs/channels/wifi-projection.md` | `channels` (`../verification/`) | No | Inserted | end of file |
| `docs/channels/audio.md` | `channels` | No | Inserted | end of file |
| `docs/channels/video.md` | `channels` | No | Inserted | end of file |
| `docs/channels/sensor.md` | `channels` | No | Inserted | end of file |
| `docs/channel-map.md` | `channel_map` (`verification/`) | No | Inserted | end of file |

The walker self-excludes `docs/verification/06-capture-non-claim-boundary.md`
— a test (`test_self_exclusion`) verifies the walker raises `ValueError` when
pointed at that path via a fixture, and the file remains unchanged after the
refused call.

## Example Sidecar: VideoFocusRequestMessage (Gold → Platinum)

**Rationale:** planner locked this as the target because (a) it was already
`confidence: gold` with deep-trace APK evidence through `ied.java m20258P`,
(b) video is an av_channel kind and VW exercised all 5 av_channels heavily,
and (c) MATCH-08 (SDP descriptor match) is always citable for any proto
bound to a service that appears in VW's SDP response.

**Platinum promotion shape:**

```yaml
confidence: platinum
platinum_scope: single_oem
evidence:
  - type: deep_trace          # pre-existing, kept
  - type: apk_static          # pre-existing, kept (description added by Rule 1 auto-fix)
  - type: cross_version       # pre-existing, kept (description added by Rule 1 auto-fix)
  - type: platinum_evidence   # NEW — Phase 9 Plan 01 addition
    capture_path: captures/oem-vw-mib3oi-2026-04-06/
    vehicle_metadata: { make: Volkswagen, model: MIB3 OI, year: '2024', aa_version: '16.4.661034' }
    msg_seq: [0]              # PLACEHOLDER — Phase 10 overwrites after deep inspection
    ts_ms: [0]                # PLACEHOLDER
    message_completeness: full
    attribution_method: sdp_service_id
    oem_scope: single
    applicability: message    # whole-message citation; no fields list
    match_rules: [MATCH-08]   # honest minimum — SDP descriptor match
```

## `oem_match_pending_gold` Contract for Phase 10

The flag is a **sidecar-level boolean** (not inside the evidence array) with
exactly one semantic: `true` means a Silver or Bronze proto was matched in an
OEM capture but lacks Gold prerequisites (deep-trace APK + cross-version), so
it cannot be promoted to Platinum directly — the ladder is strict. Phase 10's
walker SHOULD:

1. Filter sidecars by `confidence ∈ {silver, bronze}` first.
2. For each match attempt against the VW capture that produces a hit, check
   if the proto has an existing `deep_trace` / `apk_deep_trace` evidence
   entry.
3. If yes → promote to Gold (Phase 10's Gold walk is out of scope for this
   plan); if no → set `oem_match_pending_gold: true` at the sidecar top level
   and emit a worklist row.
4. Phase 11+ consumes the worklist and prioritizes deep-trace work.

The flag is documented in both `01-confidence-tiers.md` and
`03-verification-procedures.md § 5. Platinum Evidence`. Phase 9 Plan 01 does
NOT execute the walk — only the methodology surface is delivered here.

## Files Created/Modified

**Created (20 files):** 2 verification docs (05, 06), full `dhu_divergence/`
test package (13 files), full `cross_link_walker/` package including
implementation, CLI, and 5 test/fixture files.

**Modified (11 files):** `audit-schema.json`, 3 existing verification docs
(01 rewrite, 02 touch-up, 03 append), 5 channel docs (walker-inserted callout),
1 sidecar (Gold→Platinum promotion), `REQUIREMENTS.md` (TIER-01 text fix).

## Decisions Made

All captured in `key-decisions` frontmatter. Highlights worth surfacing:

- **Platinum strictly above Gold** — the single most important tier-model
  decision. It keeps the honest ladder visible and defeats the temptation to
  let a single-OEM match promote a Silver directly.
- **`Platinum / single-OEM` badge verbatim** — naming the trap on the badge
  instead of in a footnote. If a future Phase 12 renderer is tempted to strip
  the `/ single-OEM` suffix for visual cleanliness, the doc explicitly calls
  that out as NOT allowed.
- **Match rule closed enum** — `match_rules` is a closed enum in the JSON
  Schema and the schema enum must match the doc headings exactly (enforced
  by test_schema_enum_matches_doc). The cross-file integrity test is the
  long-term guarantee against silent drift between the doc and the schema.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Legacy top-level fields needed whitelisting for retracted sidecars and VideoFocusRequestMessage to validate**

- **Found during:** Task 1 (schema migration verification), Task 8 (example sidecar validation)
- **Issue:** CONTEXT.md assumed the 6 retracted sidecars would validate cleanly after adding `platinum` and `retracted` to the confidence enum. Direct testing revealed each retracted sidecar used one or more of `retraction`, `retraction_reason`, `replaced_by`, `previous_evidence`, `retracted`, `class_mapping` as top-level fields. Similarly, `VideoFocusRequestMessage` (the locked example target) used `wire_msg_id`, `direction`, `channel`, `handler`, `class_mapping` — all rejected by `additionalProperties: false`. The plan's <interfaces> block said these files would just work post-migration, but every single one was broken.
- **Fix:** Added 10 legacy top-level optional fields to the schema's `properties` with non-restrictive types (`wire_msg_id: string|integer`, `direction/channel/handler/retraction_reason/replaced_by: string`, `class_mapping/retraction: object`, `retracted: boolean`, `previous_evidence: array of evidence_entry`). Also added `apk_deep_trace` and `deep_trace` to the `evidence_entry.type` enum (used by 3 of the 6 retracted sidecars and the pre-existing `VideoFocusRequestMessage` deep_trace entry). `additionalProperties: false` stays intact on both the outer object and `evidence_entry` — the schema contract is preserved.
- **Files modified:** `docs/verification/audit-schema.json`
- **Verification:** All 6 retracted sidecars validate via the parametric backstop test (6 passed), VideoFocusRequestMessage validates via `test_example_sidecar_validates`, backward-compat gate holds at 334/1.
- **Committed in:** `a89d84c` (Task 1 schema migration) and `03bcd73` (Task 8 example sidecar promotion where the deep_trace entry also needed the enum addition)

**2. [Rule 1 - Bug] VideoFocusRequestMessage evidence entries 1 and 2 were missing required `description` field**

- **Found during:** Task 8 (example sidecar validation after schema migration)
- **Issue:** The current `apk_static` and `cross_version` evidence entries in `VideoFocusRequestMessage.audit.yaml` had `type`, `method`, `source`, `date` but no `description`. The schema requires `description` as a non-empty string on every evidence entry. Without descriptions these entries failed validation, and the Task 8 acceptance criterion explicitly requires the sidecar to validate.
- **Fix:** Added substantive descriptions to both entries — the apk_static description summarizes the class-mapping binding evidence, and the cross_version description summarizes the structural-comparison check. No evidence was removed or rewritten beyond adding the missing descriptions; the existing `deep_trace` entry's description was unchanged.
- **Files modified:** `oaa/video/VideoFocusRequestMessage.audit.yaml`
- **Verification:** `test_example_sidecar_validates` passes; full sidecar round-trips through the schema validator.
- **Committed in:** `03bcd73` (Task 8)

**3. [Rule 3 - Blocking] Baseline count was 334/1, not 110/1**

- **Found during:** Task 1 (pre-migration baseline verification)
- **Issue:** The plan's `<interfaces>` block stated the baseline was "110 passed, 1 failed" — this was stale data. The actual pre-migration baseline was **334 passed, 1 failed** (NavigationDistanceMessage). The parametric test collects all Silver sidecars into 4 test functions (`test_silver_sidecar_validates_against_schema`, `test_silver_sidecar_has_cross_version_evidence`, `test_silver_sidecar_cross_version_entry_has_required_fields`, plus one singleton count test), and Phase 8's walker landed 111 Silver sidecars, so the total is 111 × 3 + 1 = 334 parameterized tests.
- **Fix:** Treated 334/1 as the true baseline to preserve. Post-migration, the suite still shows 334 passed / 1 failed — no regression. Documented the actual baseline in this summary so Phase 10 knows what number to expect.
- **Verification:** `PYTHONPATH=. pytest analysis/tools/cross_version/tests/test_promoted_sidecars.py` after every doc or schema edit throughout the plan returned the same 334/1 tally.
- **Committed in:** No code fix needed; this is a metadata correction recorded in SUMMARY.md

**4. [Rule 3 - Blocking] audio.md and wifi-projection.md had CRLF line endings**

- **Found during:** Task 7 (walker execution against live docs tree)
- **Issue:** The walker's `Path.write_text()` reads and rewrites the file as UTF-8 text. Two target files (`audio.md`, `wifi-projection.md`) had CRLF line endings in the repo (different from all other markdown files). The walker's write normalized them to LF, causing a large diff on the first commit (879 and 1197 line changes respectively).
- **Fix:** Accepted the normalization as a data-cleanup side effect (all other markdown files in the repo are LF). Post-commit, git's `ls-files --eol` reports both files as `i/lf w/lf` — they're now consistent with the rest of the tree.
- **Files modified:** `docs/channels/audio.md`, `docs/channels/wifi-projection.md`
- **Verification:** Second walker run is a pure no-op; git status stays clean across re-runs.
- **Committed in:** `f8b1e3d` (Task 7)

**5. [Rule 1 - Bug] Initial 05-oem-match-policy.md draft contained "MATCH-09" string that broke test_eight_match_rules**

- **Found during:** Task 4 (first test run)
- **Issue:** My first draft of `05-oem-match-policy.md` included the sentence "a future contributor cannot invent a `MATCH-09` or pass an empty list without the schema validator catching it" in the closed-enum enforcement section. The `test_eight_match_rules` test asserts `"MATCH-09" not in text`, which caught this immediately.
- **Fix:** Replaced "invent a `MATCH-09`" with "invent an out-of-enum rule ID" — same meaning, no literal rule ID that would trip the enum-boundary test.
- **Files modified:** `docs/verification/05-oem-match-policy.md`
- **Verification:** `test_eight_match_rules` passes on re-run.
- **Committed in:** `02f6486` (Task 4 commit includes the fix)

---

**Total deviations:** 5 auto-fixed (4 Rule 1 bug-class, 1 Rule 3 metadata correction / blocking fix)
**Impact on plan:** All 5 auto-fixes were required to meet the plan's own acceptance criteria. No scope creep — the legacy-field whitelist is the minimum needed to satisfy "all 6 retracted sidecars validate" and "example sidecar validates," both of which were hard acceptance criteria. The baseline correction and CRLF normalization were metadata / data-hygiene fixes that didn't change functional scope.

## Issues Encountered

No additional issues beyond the 5 deviations above. Each task committed atomically on first attempt after handling its deviation. No checkpoint was hit; the plan ran end-to-end autonomously.

## User Setup Required

None — no external service configuration needed for this plan's deliverables. All work is schema / docs / tests / sidecar edits, all of which run locally with the existing pytest + jsonschema + PyYAML stack.

## Next Phase Readiness

**Phase 10 (Gold-tier promotion walk, TIER-04) is unblocked.** It has everything it needs from this plan:

- Migrated schema accepts `platinum_evidence` entries with closed-enum rule citations.
- `05-oem-match-policy.md` defines the rule IDs Phase 10 must cite.
- `06-capture-non-claim-boundary.md` defines what Phase 10 CANNOT claim.
- `VideoFocusRequestMessage.audit.yaml` is the reference example — Phase 10 can use it as a template for the shape of a Platinum promotion.
- `oem_match_pending_gold` flag contract is documented for the case where an OEM match lacks Gold prerequisites.
- Parametric backstop (`test_retracted_sidecars.py`) and cross-file integrity test (`test_schema_enum_matches_doc`) will catch future drift between docs and schema.

**Phase 9 Plan 02 (divergence report, OEM-04) is also unblocked.** The
`dhu_divergence` package scaffold has the `schema` and `repo_root` fixtures
ready; Plan 02 can start filling in the real baseline merge / divergence /
attribution modules on top of the existing skeleton.

**Deferred for Phase 10+:** Phase 10 will overwrite `VideoFocusRequestMessage`'s `msg_seq: [0]` and `ts_ms: [0]` placeholders with real indices after deep inspection of `messages.jsonl`. Phase 10 will also expand the MATCH rule citation list beyond `MATCH-08` if the wire-level inspection reveals standalone payloads (MATCH-01 / MATCH-02) or field-level verification opportunities (MATCH-04 / MATCH-05).

## Self-Check: PASSED

All 32 files referenced in this summary exist at their stated paths (verified via filesystem check). All 8 task commits exist in git history (verified via `git log --oneline --all | grep`). Full Phase 9 Plan 01 test suite runs 30 passed / 0 failed / 0 skipped. Backward-compat gate holds at 334/1. Walker live-idempotent (second run shows 0/5 modified). Zero uncommitted changes on the plan's deliverable files.

---
*Phase: 09-oem-methodology-divergence-report*
*Completed: 2026-04-09*
