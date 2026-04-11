---
phase: 10-gold-tier-promotion-walk
plan: 02
subsystem: verification-methodology
tags: [promotion-walker, platinum-tier, oem-evidence, match-rules, idempotency, sidecar-walker]

requires:
  - phase: 10-gold-tier-promotion-walk
    plan: 01
    provides: "audit-schema.json v4 with pending_platinum_evidence + corrections whitelist, ROADMAP terminology fix, promotion_walker package scaffold with 6 stubs + fixtures + conftest"

provides:
  - "analysis/tools/promotion_walker/ fully working package: index.py, verdict.py, rule_eval.py, report.py, run.py"
  - "42 tests passing (19 verdict/index/rule_eval + 5 report/idempotency/dry-run + 6 live snapshot + 8 schema migration + 4 roadmap terminology)"
  - "2 Gold->Platinum promotions: MediaPlaybackStatusMessage + MediaPlaybackMetadataMessage (both MATCH-08)"
  - "21 oem_match_pending_gold flags on Silver/Bronze sidecars in oaa/{av,audio,video}/"
  - "analysis/reports/oem-vw/promotion-walk.{md,json} with 8 locked section headers + 9 locked JSON keys"
  - "analysis/reports/oem-vw/oem-match-pending-gold-worklist.{md,json} with 21-entry deep-trace worklist"
  - "24 atomic git commits with conventional subjects citing MATCH-08 rule"

affects: [phase-11-channel-architecture-reference, phase-12-audit-report-generator]

tech-stack:
  added: []
  patterns: [directory-based-channel-binding-resolution, content-hash-idempotency-excluding-date, atomic-per-sidecar-commits-with-match-rule-citations]

key-files:
  created:
    - analysis/reports/oem-vw/promotion-walk.md
    - analysis/reports/oem-vw/promotion-walk.json
    - analysis/reports/oem-vw/oem-match-pending-gold-worklist.md
    - analysis/reports/oem-vw/oem-match-pending-gold-worklist.json
  modified:
    - analysis/tools/promotion_walker/index.py
    - analysis/tools/promotion_walker/verdict.py
    - analysis/tools/promotion_walker/rule_eval.py
    - analysis/tools/promotion_walker/report.py
    - analysis/tools/promotion_walker/run.py
    - analysis/tools/promotion_walker/tests/test_index.py
    - analysis/tools/promotion_walker/tests/test_verdict.py
    - analysis/tools/promotion_walker/tests/test_rule_eval.py
    - analysis/tools/promotion_walker/tests/test_walk_report.py
    - analysis/tools/promotion_walker/tests/test_idempotency.py
    - analysis/tools/promotion_walker/tests/test_dry_run.py
    - analysis/tools/promotion_walker/tests/test_live_walk_snapshot.py
    - oaa/media/MediaPlaybackStatusMessage.audit.yaml
    - oaa/media/MediaPlaybackMetadataMessage.audit.yaml

key-decisions:
  - "Channel-binding resolution uses directory-based inference (oaa/av/ -> av_channel, oaa/audio/ -> av_channel, oaa/video/ -> av_channel, oaa/media/ -> media_info_channel) with KNOWN_CAR_LOCAL_MEDIA_PROTOS override for the 3 CarLocalMedia* sidecars"
  - "Walker uses direct git add + git commit for atomic per-sidecar commits (gsd-tools commit skips when commit_docs=false)"
  - "MATCH-08 (SDP descriptor match) is the baseline rule for all in-scope sidecars; no wire-level msg_type matches in Phase 10 because Phase 7 coverage.json only attributes 2 msg_types to av_channel and neither maps to the in-scope proto message names"
  - "Idempotency verification run produced correct behavior: sidecar files unchanged (skip_already_platinum=3 on second run), only report files changed (walker_run_date updated)"
  - "validate_audit() from seed_import.generate is reused for pre-validation gate -- schema validation failure catches MediaPlaybackStatusEventMessage (notes field) and VideoFocusIndicationMessage (missing description) as expected"

patterns-established:
  - "Directory-based channel binding: walker resolves oaa/{subdir}/ to channel_kind without requiring per-sidecar channel metadata -- only CarLocalMedia* sidecars need the hard-coded override"
  - "Dual-pass idempotency: first pass applies verdicts + commits, second pass verifies content_hash dedupe prevents re-application -- sidecar sha256 stable across runs"
  - "Walker reports as snapshot artifacts: promotion-walk.json carries walker_run_date and capture_sha256 so downstream consumers know when the data was generated"

requirements-completed: [TIER-04]

duration: 8min
completed: 2026-04-11
---

# Phase 10 Plan 02: Promotion Walker Implementation Summary

**Promotion walker shipped: 2 Gold->Platinum promotions (MediaPlaybackStatus + MediaPlaybackMetadata via MATCH-08), 21 oem_match_pending_gold flags, 3 CarLocalMedia* out-of-SDP-scope skips, 42 tests all green, byte-idempotent on real oaa/ tree.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-11T15:43:35Z
- **Completed:** 2026-04-11T15:51:50Z
- **Tasks:** 2
- **Files created:** 4 (report files)
- **Files modified:** 35 (6 source modules + 7 test files + 2 promoted sidecars + 21 flagged sidecars - 1 already counted)

## Accomplishments

- **Walker core implemented** with 10-verdict routing logic. `walker_decide()` correctly routes all 36 in-scope sidecars: 2 promote, 21 flag, 3 out-of-SDP, 1 already-Platinum, 5 retracted, 1 superseded, 1 missing-prereq, 2 schema-invalid. MATCH-04/05 permanently excluded, NOMATCH-01 never emitted -- both enforced by defensive assertions + dedicated tests.

- **Live walker run produced exactly the predicted results.** Gold-counts delta: Gold 8->6, Platinum 1->3 (+2 promoted). All 21 Silver/Bronze in observed services got `oem_match_pending_gold: true` with `pending_platinum_evidence` draft entries citing MATCH-08. 24 atomic commits in git history with conventional subjects.

- **Walker is byte-idempotent on the real oaa/ tree.** Second run produces `git status --porcelain oaa/` empty. The 2 promoted sidecars route to `skip_already_platinum` on re-run. The 21 flagged sidecars route to idempotent skip via content_hash dedupe on `pending_platinum_evidence`. Report files regenerate with updated `walker_run_date` but sidecars are stable.

- **42 tests all green, zero skipped.** 8 schema migration (Plan 10-01) + 4 roadmap terminology + 19 walker core + 5 report/idempotency/dry-run + 6 live snapshot = 42 total. Phase 8 baseline preserved at 334 passed / 1 pre-existing failure.

## Task Commits

Each task was committed atomically:

1. **Task 1: Walker core (index, verdict, rule_eval) + 19 tests** -- `0904bde` (feat)
2. **Task 2: Walker runner (report, run) + 6 test files** -- `143ecbe` (feat)

**Walker atomic commits (24 total):**
- 2 `feat(10-02): promote X to Platinum (MATCH-08)` -- `da3f728`, `28732c6`
- 21 `chore(10-02): flag X for oem_match_pending_gold (MATCH-08)` -- `f7577e1`..`da76b2d`
- 1 `docs(10-02): write promotion walk report + worklist + Gold-counts delta` -- `0f4c15a`

## Live Walker Results

| Verdict | Count | Sidecars |
|---------|-------|----------|
| PROMOTE_TO_PLATINUM | 2 | MediaPlaybackStatusMessage, MediaPlaybackMetadataMessage |
| FLAG_PENDING_GOLD | 21 | 11 oaa/av/ + 3 oaa/video/ + 5 oaa/audio/ silver + 2 oaa/audio/ bronze |
| SKIP_OUT_OF_SDP_SCOPE | 3 | CarLocalMediaPlaybackStatus, CarLocalMediaPlaybackRequest, CarLocalMediaPlaybackMetadata |
| SKIP_ALREADY_PLATINUM | 1 | VideoFocusRequestMessage |
| SKIP_RETRACTED | 5 | MediaPlaybackCommand, MediaStatusList, MediaTrackIdentifier, VideoFocusMode, VideoFocusNotification |
| SKIP_SUPERSEDED | 1 | CarLocalMediaPlaybackEnum |
| SKIP_MISSING_GOLD_PREREQ | 1 | UiConfigRequestMessage |
| SKIP_SCHEMA_INVALID | 2 | MediaPlaybackStatusEventMessage, VideoFocusIndicationMessage |
| NOMATCH_OBSERVATION | 0 | (MATCH-08 baseline fires for all in-scope; no unmatched) |
| CONTRADICTION_REVIEW | 0 | (walker doesn't do field decoding) |
| **TOTAL** | **36** | |

**Gold-counts delta: Gold 8->6, Platinum 1->3 (+2 promoted)**

## Decisions Made

- **Channel-binding resolution is directory-based** with a hard-coded `KNOWN_CAR_LOCAL_MEDIA_PROTOS` override. No per-sidecar channel metadata was needed -- the directory path (`oaa/av/` -> av_channel, `oaa/media/` -> media_info_channel, etc.) plus the evidence description text scan for `car_local_media` catches all 36 sidecars correctly.

- **MATCH-08 is the only rule that fires in Phase 10.** No wire-level msg_type observations map to the in-scope proto message names in Phase 7's coverage.json (the 2 attributed msg_types are 0x8003/out and 0x8061/out which don't correspond to any sidecar's wire_msg_id). All promotions and flags cite MATCH-08 alone.

- **Direct git commands used instead of gsd-tools commit.** The `commit_docs: false` config causes gsd-tools to skip commits, so the walker uses `git add` + `git commit` directly for the atomic per-sidecar commits. This matches the Phase 8/9 precedent.

## Deviations from Plan

None -- plan executed exactly as written. All 36 verdicts match the predicted counts from 10-RESEARCH.md. Both tasks committed on first attempt. No auto-fixes needed.

## Issues Encountered

None. The dry-run output matched predictions exactly, confirming the implementation was correct before the live run.

## User Setup Required

None -- all work is Python implementation + YAML sidecar edits running locally with existing stack.

## Next Phase Readiness

**Phase 11 (channel architecture reference, ARCH-04) is unblocked.** It reads `promotion-walk.json` for VW-vs-DHU examples of which channels were observed and promoted.

**Phase 12 (audit dashboard, REPORT-01) is unblocked.** It reads `promotion-walk.json` for Gold/Platinum counts by channel -- the `gold_counts_delta` key provides the headline metric.

**Consumer pointers for downstream phases:**
- `promotion-walk.json` -> `gold_counts_delta.gold_before`, `gold_counts_delta.gold_after`, `gold_counts_delta.platinum_before`, `gold_counts_delta.platinum_after`
- `promotion-walk.json` -> `pending_gold_flags[]` for the 21 Silver/Bronze sidecars awaiting deep-trace
- `promotion-walk.json` -> `unobserved_services` for the per-directory count of sidecars in unobserved channels

**oem_vw_parser/ confirmed untouched** -- `git status --porcelain analysis/tools/oem_vw_parser/` returns empty. Import-not-fork discipline preserved.

## Self-Check: PASSED

All deliverable files verified:

- `analysis/tools/promotion_walker/index.py` -- FOUND, contains `build_index`, `build_sdp_kinds`, `build_classification`
- `analysis/tools/promotion_walker/verdict.py` -- FOUND, contains `walker_decide`, `content_hash`, `VerdictKind`(10)
- `analysis/tools/promotion_walker/rule_eval.py` -- FOUND, contains `eval_match_rules`, `eval_nomatch_rules`
- `analysis/tools/promotion_walker/report.py` -- FOUND, contains `build_walk_report`, `emit_md`, `emit_json`, `build_worklist`
- `analysis/tools/promotion_walker/run.py` -- FOUND, contains `main` with `--dry-run` flag
- `analysis/reports/oem-vw/promotion-walk.md` -- FOUND, 8 section headers present
- `analysis/reports/oem-vw/promotion-walk.json` -- FOUND, 9 top-level keys present
- `analysis/reports/oem-vw/oem-match-pending-gold-worklist.md` -- FOUND
- `analysis/reports/oem-vw/oem-match-pending-gold-worklist.json` -- FOUND, 21 entries
- Task commits `0904bde` and `143ecbe` -- FOUND in git log
- 42 tests pass, 0 skipped, 0 failures
- Phase 8 baseline: 334 passed / 1 failed
- oem_vw_parser: untouched

---
*Phase: 10-gold-tier-promotion-walk*
*Completed: 2026-04-11*
