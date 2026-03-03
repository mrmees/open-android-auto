---
phase: 03-cross-version-validation
plan: 02
subsystem: analysis
tags: [cross-version, proto, audit-sidecar, promotion, confidence-annotation, mapping-tables]

requires:
  - phase: 03-cross-version-validation
    provides: "Cross-version comparison tool, 15.9/16.1/16.2 DB paths, promote/tables/report modules"
  - phase: 02-seed-import-proto-foundation
    provides: "156 audit sidecars, 223 proto files, annotate.py, class_mapping.yaml"
provides:
  - "16 per-category mapping tables in docs/cross-version/"
  - "Consistency report with zero unexplained discrepancies"
  - "143 silver-tier audit sidecars (promoted from bronze)"
  - "Updated proto confidence annotations across all 223 proto files"
affects: [04-feature-channel-docs]

tech-stack:
  added: []
  patterns: ["Cross-version report with explained discrepancy classification"]

key-files:
  created:
    - docs/cross-version/sensor.md
    - docs/cross-version/audio.md
    - docs/cross-version/navigation.md
    - docs/cross-version/common.md
    - docs/cross-version/control.md
    - docs/cross-version/media.md
    - docs/cross-version/phone.md
    - docs/cross-version/radio.md
    - docs/cross-version/video.md
    - docs/cross-version/consistency-report.md
  modified:
    - analysis/tools/proto_schema_validator/mapping.py
    - oaa/**/*.audit.yaml (143 promoted)
    - oaa/**/*.proto (223 re-annotated)

key-decisions:
  - "All 4 discrepancies explained as 16.1 DB missing proto_enum_classes table -- verified identical values in 15.9 and 16.2"
  - "143 of 220 eligible sidecars promoted (77 skipped: no sidecar file or already had cross_version evidence)"

patterns-established:
  - "Discrepancy analysis with manual verification when automated checker flags false positives"

requirements-completed: [PROTO-03, TOOL-02]

duration: 3min
completed: 2026-03-03
---

# Phase 3 Plan 2: Cross-Version Validation Outputs Summary

**3-way cross-version comparison across 224 mappings producing 16 mapping tables, consistency report with zero unexplained discrepancies, 143 silver-tier promotions, and updated proto annotations**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-03T23:54:52Z
- **Completed:** 2026-03-03T23:57:52Z
- **Tasks:** 2
- **Files modified:** 367

## Accomplishments
- Ran full 3-way cross-version comparison (15.9/16.1/16.2) across 224 mappings: 220 consistent, 4 with explained discrepancies
- Generated 16 per-category mapping tables and consistency report in docs/cross-version/
- Promoted 143 audit sidecars from bronze to silver with cross_version evidence
- Re-annotated all 223 proto files: 143 silver, 13 bronze, 67 unverified

## Task Commits

Each task was committed atomically:

1. **Task 1: Run cross-version checker and generate all outputs** - `5cb8b49` (feat)
2. **Task 2: Update proto confidence annotations to reflect silver tier** - `63db78d` (feat)

## Files Created/Modified
- `docs/cross-version/*.md` (17 files) - Per-category mapping tables and consistency report
- `analysis/tools/proto_schema_validator/mapping.py` - Fixed get_apk_enum_values for missing proto_enum_classes table
- `oaa/**/*.audit.yaml` (143 files) - Promoted from bronze to silver with cross_version evidence
- `oaa/**/*.proto` (223 files) - Re-annotated with updated confidence tiers

## Decisions Made
- **Discrepancy classification:** All 4 flagged mappings (DriverPosition, HapticFeedbackType, SensorErrorStatus, CarLocalMediaPlayback) are false positives from 16.1 DB lacking proto_enum_classes table. Manually verified identical enum values between 15.9 and 16.2.
- **Promotion count:** 143 of 220 eligible. The 77 gap is expected: some mappings lack sidecar files (enum-only or unmapped types).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed get_apk_enum_values crash on missing proto_enum_classes table**
- **Found during:** Task 1 (running cross-version checker)
- **Issue:** The 16.1 APK index DB does not have a `proto_enum_classes` table, causing sqlite3.OperationalError
- **Fix:** Wrapped the fallback query in try/except sqlite3.OperationalError, returning None when table is missing
- **Files modified:** analysis/tools/proto_schema_validator/mapping.py
- **Verification:** Tool runs successfully across all 3 DBs
- **Committed in:** 5cb8b49 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Essential for tool to function with heterogeneous DB schemas across versions. No scope creep.

## Issues Encountered
None beyond the auto-fixed bug above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 3 complete: all cross-version validation outputs produced
- 143 silver-tier sidecars available for Phase 4 (feature channel docs)
- Mapping tables in docs/cross-version/ provide reference for developers
- Proto annotations reflect current evidence state across all 223 files

---
*Phase: 03-cross-version-validation*
*Completed: 2026-03-03*
