---
phase: 10-gold-tier-promotion-walk
plan: 01
subsystem: verification-methodology
tags: [jsonschema, yaml, pytest, tier-ladder, platinum-tier, promotion-walker, schema-migration]

requires:
  - phase: 09-oem-methodology-divergence-report
    provides: "audit-schema.json v3 with Platinum tier, closed MATCH/NOMATCH enums, platinum_evidence type, 10 legacy whitelist fields, additionalProperties: false discipline"
  - phase: 08-16-4-cross-version-validation
    provides: "test_promoted_sidecars.py baseline (334 passed / 1 failed), cross_version sidecar_walker append-only pattern, content-hash dedupe"
provides:
  - "audit-schema.json v4 with pending_platinum_evidence top-level array ($ref evidence_entry) and corrections whitelist at both top-level and evidence_entry scope (Option B)"
  - "ROADMAP.md Phase 10 section corrected: oem_evidence -> platinum_evidence, Gold / single-OEM -> Platinum / single-OEM (6 replacements across 4 sections)"
  - "analysis/tools/promotion_walker/ package scaffold: 6 source modules (stubs), 8 test files, 11 fixture files, conftest.py"
  - "12 passing tests (8 schema migration + 4 roadmap terminology) + 25 skip-marked stubs for Plan 10-02"
affects: [phase-10-plan-02-walker-implementation, phase-11-channel-architecture-reference, phase-12-coverage-dashboard]

tech-stack:
  added: []
  patterns: [dual-location schema whitelist for evidence-entry-level and top-level corrections field]

key-files:
  created:
    - analysis/tools/promotion_walker/__init__.py
    - analysis/tools/promotion_walker/index.py
    - analysis/tools/promotion_walker/verdict.py
    - analysis/tools/promotion_walker/rule_eval.py
    - analysis/tools/promotion_walker/report.py
    - analysis/tools/promotion_walker/run.py
    - analysis/tools/promotion_walker/tests/__init__.py
    - analysis/tools/promotion_walker/tests/conftest.py
    - analysis/tools/promotion_walker/tests/test_schema_migration.py
    - analysis/tools/promotion_walker/tests/test_roadmap_terminology.py
    - analysis/tools/promotion_walker/tests/test_verdict.py
    - analysis/tools/promotion_walker/tests/test_rule_eval.py
    - analysis/tools/promotion_walker/tests/test_index.py
    - analysis/tools/promotion_walker/tests/test_idempotency.py
    - analysis/tools/promotion_walker/tests/test_dry_run.py
    - analysis/tools/promotion_walker/tests/test_walk_report.py
    - analysis/tools/promotion_walker/tests/test_live_walk_snapshot.py
    - analysis/tools/promotion_walker/tests/fixtures/sidecar_gold_clean.audit.yaml
    - analysis/tools/promotion_walker/tests/fixtures/sidecar_gold_no_cv.audit.yaml
    - analysis/tools/promotion_walker/tests/fixtures/sidecar_silver_clean.audit.yaml
    - analysis/tools/promotion_walker/tests/fixtures/sidecar_bronze_clean.audit.yaml
    - analysis/tools/promotion_walker/tests/fixtures/sidecar_retracted.audit.yaml
    - analysis/tools/promotion_walker/tests/fixtures/sidecar_already_platinum.audit.yaml
    - analysis/tools/promotion_walker/tests/fixtures/sidecar_schema_invalid_corrections.audit.yaml
    - analysis/tools/promotion_walker/tests/fixtures/sidecar_out_of_sdp_scope.audit.yaml
    - analysis/tools/promotion_walker/tests/fixtures/mock_coverage.json
    - analysis/tools/promotion_walker/tests/fixtures/mock_messages.jsonl
    - analysis/tools/promotion_walker/tests/fixtures/mock_sdp_values.json
  modified:
    - docs/verification/audit-schema.json
    - .planning/ROADMAP.md

key-decisions:
  - "Option B corrections whitelist applied at BOTH evidence_entry AND top-level scope (Rule 1 auto-fix: real sidecars carry corrections inside evidence entries, not at top level as plan stated)"
  - "ROADMAP.md terminology fix spans all sections mentioning oem_evidence or Gold / single-OEM, not just Phase 10 section -- 6 replacements across Phase 9 summary line, Phase 9 success criteria, Phase 10 success criteria, Phase 12 success criteria, and overview paragraph"
  - "Fixture sidecar_schema_invalid_corrections.audit.yaml uses TOP-level corrections (matching the plan's locked fixture shape) for testing the top-level whitelist; real sidecars have corrections inside evidence entries (tested by test_all_36_in_scope_sidecars_validate)"

patterns-established:
  - "Dual-location schema whitelist: when a legacy field appears at multiple depths (evidence_entry.corrections AND root.corrections), add it to both locations rather than picking one -- the real data determines where the whitelist goes"
  - "Fixture + real-sidecar dual validation: fixture tests the planned shape, test_all_36_in_scope_sidecars_validate tests the real shape -- both must pass for the migration to be correct"

requirements-completed: [TIER-04]

duration: 9min
completed: 2026-04-11
---

# Phase 10 Plan 01: Schema Migration + Walker Scaffold Summary

**Audit schema v4 with pending_platinum_evidence + corrections Option B whitelist, ROADMAP terminology fix (6 replacements), and promotion_walker package scaffold with 6 source stubs, 8 test files, and 11 fixtures.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-11T15:28:14Z
- **Completed:** 2026-04-11T15:37:20Z
- **Tasks:** 2
- **Files created:** 30
- **Files modified:** 2
- **Tests added:** 37 (12 passing real assertions, 25 skip-marked stubs)

## Accomplishments

- **Schema migration landed first** with Option B (corrections whitelist). The `pending_platinum_evidence` top-level array references the existing `evidence_entry` definition. The `corrections` array is whitelisted at BOTH the top level (for future use) AND inside `evidence_entry` properties (to fix the 4 real oaa/media/ Gold sidecars that carry corrections on their `apk_deep_trace` entries). Phase 8 baseline preserved at 334 passed / 1 failed.

- **33 of 36 in-scope sidecars now validate cleanly.** The 5 corrections-blocked Gold sidecars are unblocked. The 3 remaining holdouts are documented: `MediaPlaybackStatusEventMessage` (top-level `notes`), `CarLocalMediaPlaybackEnum` (confidence: superseded), `VideoFocusIndicationMessage` (missing `description` on apk_static evidence entry).

- **ROADMAP.md terminology corrected** across 4 sections -- not just Phase 10's section but also the overview paragraph, Phase 9 summary line, and Phase 12 success criteria. All 6 replacements verified by negative grep (0 oem_evidence, 0 Gold/single-OEM) and positive grep (5 Platinum / single-OEM).

- **promotion_walker package scaffold complete** with 6 source module stubs (all importable, all raise NotImplementedError), 8 fixture sidecars (all schema-valid), 3 mock data files, conftest.py with session-scoped fixtures, and 7 test stub files with skip markers. Plan 10-02 can focus 100% on walker logic.

## Task Commits

Each task was committed atomically:

1. **Task 1: Schema migration + ROADMAP terminology fix** -- `2d89b4c` (feat)
2. **Task 2: Walker package scaffold** -- `4034fad` (chore)

## Schema Migration Details

**Fields added to `docs/verification/audit-schema.json`:**

- Top-level `properties.pending_platinum_evidence`: `{ type: array, default: [], items: { $ref: evidence_entry } }` -- draft platinum_evidence entries for Silver/Bronze protos blocked by Gold-prerequisite rule
- Top-level `properties.corrections`: `{ type: array, default: [], items: { type: string } }` -- legacy corrections array whitelist (Option B)
- `$defs.evidence_entry.properties.corrections`: `{ type: array, items: { type: string } }` -- Rule 1 auto-fix: the 4 real sidecars carry corrections INSIDE evidence entries

`additionalProperties: false` preserved on both root object and `evidence_entry`. No changes to confidence enum (superseded deferred). Phase 8 baseline holds at 334/1.

## Walker Package Layout

```
analysis/tools/promotion_walker/
  __init__.py          # empty package marker
  index.py             # build_index, build_sdp_kinds stubs
  verdict.py           # VerdictKind(10 variants), Verdict(11 fields), walker_decide stub
  rule_eval.py         # ALLOWED/EXCLUDED/FORBIDDEN rule tuples, eval_match/nomatch stubs
  report.py            # MAIN_REPORT_SECTION_HEADERS(8), MAIN_REPORT_JSON_KEYS(9), 4 stubs
  run.py               # argparse --dry-run/--scope-dir/--capture/--coverage/--sdp/--classification/--out
  tests/
    __init__.py
    conftest.py        # repo_root, schema, mock_coverage, mock_sdp, mock_messages_jsonl, temp_oaa_tree
    test_schema_migration.py     # 8 real assertions (PASSING)
    test_roadmap_terminology.py  # 4 real assertions (PASSING)
    test_verdict.py              # 8 stubs (skip)
    test_rule_eval.py            # 4 stubs (skip)
    test_index.py                # 2 stubs (skip)
    test_idempotency.py          # 1 stub (skip)
    test_dry_run.py              # 1 stub (skip)
    test_walk_report.py          # 3 stubs (skip)
    test_live_walk_snapshot.py   # 6 stubs (skip)
    fixtures/
      sidecar_gold_clean.audit.yaml
      sidecar_gold_no_cv.audit.yaml
      sidecar_silver_clean.audit.yaml
      sidecar_bronze_clean.audit.yaml
      sidecar_retracted.audit.yaml
      sidecar_already_platinum.audit.yaml
      sidecar_schema_invalid_corrections.audit.yaml
      sidecar_out_of_sdp_scope.audit.yaml
      mock_coverage.json
      mock_messages.jsonl
      mock_sdp_values.json
```

## Decisions Made

All captured in `key-decisions` frontmatter. Highlights:

- **Corrections whitelist location (Rule 1 auto-fix):** The plan stated corrections was a top-level sidecar field. Live verification proved it is inside `evidence_entry` objects (on `apk_deep_trace` entries). Added the whitelist to BOTH locations -- evidence_entry (fixes real sidecars) and top-level (validates the fixture and future top-level usage). Both `test_all_36_in_scope_sidecars_validate` (real data) and `test_fixture_schema_invalid_corrections_validates` (fixture) must pass.

- **ROADMAP scope broader than plan specified:** The plan said "Phase 10 section (lines 111-125)." Grep checks against the full file revealed 3 additional `oem_evidence` occurrences and 3 additional `Gold / single-OEM` occurrences in Phase 9 summary, Phase 9 success criteria, Phase 12 success criteria, and the overview paragraph. All replaced to satisfy the `grep -c` acceptance criteria.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] corrections field is inside evidence_entry, not at the top level**
- **Found during:** Task 1 (schema migration verification)
- **Issue:** Plan stated "the corrections field these sidecars carry is at the TOP LEVEL of the sidecar, not inside an evidence item." Live verification showed the opposite: all 4 corrections-blocked sidecars carry `corrections` inside their `apk_deep_trace` evidence entries at `evidence[2]`. Schema error path was `['evidence', 2]` not `[]`.
- **Fix:** Added `corrections` to `$defs/evidence_entry/properties` in addition to the top-level whitelist. Both locations are necessary: evidence_entry for real sidecars, top-level for the fixture and future direct use.
- **Files modified:** `docs/verification/audit-schema.json`
- **Verification:** All 4 previously-blocked Gold sidecars now validate. `test_all_36_in_scope_sidecars_validate` passes with 33/36 (3 expected holdouts).
- **Committed in:** `2d89b4c` (Task 1)

**2. [Rule 1 - Bug] ROADMAP terminology occurrences outside Phase 10 section**
- **Found during:** Task 1 (ROADMAP grep verification)
- **Issue:** Plan said "Edit .planning/ROADMAP.md Phase 10 section (currently lines 111-125). Three substitutions." After those substitutions, `grep -c "oem_evidence"` still returned 3 and `grep -cE "Gold/single-OEM|Gold / single-OEM"` still returned 3. The stale terminology existed in the overview paragraph (line 7), Phase 9 summary bullet (line 41), Phase 9 success criteria (lines 100-101), and Phase 12 success criteria (line 148).
- **Fix:** Replaced all 6 additional occurrences across the file to meet the acceptance criteria.
- **Files modified:** `.planning/ROADMAP.md`
- **Verification:** `grep -c "oem_evidence"` returns 0. `grep -cE "Gold/single-OEM|Gold / single-OEM"` returns 0.
- **Committed in:** `2d89b4c` (Task 1)

---

**Total deviations:** 2 auto-fixed (both Rule 1 bug-class)
**Impact on plan:** Both auto-fixes were required to meet the plan's own acceptance criteria. The corrections location fix is the more significant one -- without it, only 29 of 36 sidecars would validate instead of 33. No scope creep.

## Issues Encountered

None beyond the 2 deviations above. Both tasks committed atomically on first attempt.

## User Setup Required

None -- all work is schema/docs/tests/fixture edits running locally with existing pytest + jsonschema + PyYAML stack.

## Next Phase Readiness

**Plan 10-02 (walker implementation, TIER-04 Wave 2) is unblocked.** It has everything it needs:

- Migrated schema accepts `pending_platinum_evidence` entries and `corrections` at both levels
- 33 of 36 in-scope sidecars validate cleanly (3 expected holdouts documented)
- Phase 8 baseline preserved at 334/1
- ROADMAP terminology corrected (negative grep verified)
- 6 source module stubs with locked function signatures, VerdictKind enum, and Verdict dataclass
- 8 fixture sidecars all schema-valid, covering every verdict path
- 3 mock data files with locked content
- 25 skip-marked test stubs with canonical function names from VALIDATION.md
- conftest.py with session-scoped `repo_root`, `schema`, and per-test `temp_oaa_tree` fixtures

**Key fact for Plan 10-02:** The corrections field lives INSIDE evidence entries (not at the top level) on the real sidecars. Plan 10-02's walker should not assume top-level corrections -- the schema handles both locations, but the real data is at `evidence[N].corrections`.

## Self-Check: PASSED

All 30 created files exist at their stated paths (verified via filesystem check). Both task commits exist in git history. Full Phase 10 Plan 01 test suite runs 12 passed / 25 skipped / 0 failed. Backward-compat gate holds at 334/1. All 8 fixture sidecars validate against the migrated schema. Zero uncommitted changes on the plan's deliverable files. oem_vw_parser untouched.

---
*Phase: 10-gold-tier-promotion-walk*
*Completed: 2026-04-11*
