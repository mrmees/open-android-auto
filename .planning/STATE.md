---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: OEM Evidence & Gold-Tier Promotion
status: in_progress
stopped_at: Phase 6 complete -- v1.1-v1.4 entries appended to MILESTONES.md
last_updated: "2026-04-07"
last_activity: 2026-04-07 -- Phase 6 plan 01 complete (HIST-01 satisfied)
progress:
  total_phases: 7
  completed_phases: 1
  total_plans: 12
  completed_plans: 1
  percent: 8
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-07)

**Core value:** Every published proto definition and protocol claim carries explicit verification evidence and confidence level
**Current focus:** Phase 6 complete (HIST-01 satisfied); Phase 7 (VW Capture Analysis) is next

## Current Position

Phase: 6 (Historical Bookkeeping) -- COMPLETE
Plan: 06-01 -- COMPLETE
Status: Phase 6 done. Phase 7 (VW Capture Analysis, OEM-01..03/05) is the next actionable work.
Last activity: 2026-04-07 — appended v1.1-v1.4 entries to MILESTONES.md

Progress: [█░░░░░░░░░] 8% (1/12 v1.5 plans complete)

## Accumulated Context

### Decisions

All v1.0 decisions logged in PROJECT.md Key Decisions table (10 entries with outcomes evaluated).

v1.5 framing decisions (2026-04-07):
- Versioned as v1.5 (minor) not v2.0 — framed as continuation of protocol reference work, not a new capability era
- VW MIB3 OI capture analysis is Phase 7 — analysis-only scope; tooling decisions deferred until analysis tells us what's needed
- Post-v1.0 ad-hoc work (channel verification, SDP layer verification, validator overhaul, nav image evidence) recorded retroactively as v1.1–v1.4 patch entries rather than folded into v1.5 scope

v1.5 roadmap decisions (2026-04-07):
- Phase numbering continues from v1.0 — Phases 6 through 12 (v1.0 shipped Phases 1-5)
- Gold promotion walk (Phase 10, TIER-04) is the milestone's headline deliverable; all other phases support or run alongside it
- TIER-04 is gated on OEM-03 coverage manifest — "every Silver proto checked" means "every Silver proto in services the VW capture actually observed"
- OEM-05 candidate novel msg_types are filtered through OEM-01 fragment classification before being labeled novel (avoids the continuation-fragment trap)
- Gold tier gets a visible scope dimension (`Gold / single-OEM` vs `Gold / multi-OEM`) via TIER-02 rather than a buried prose caveat — addresses the single-OEM trap head-on
- Phase 7 and Phase 8 operate on independent evidence sources and could run in parallel if capacity allows, but Phase 9 requires both
- HIST-01 (v1.1–v1.4 retroactive entries) is Phase 6 warmup — independent, bookkeeping, clears ledger debt before real work begins
- Phase 12 (REPORT-01) is intentionally last — running a coverage dashboard before the promotion walk would just show pre-walk Silver counts

Phase 6 execution decisions (2026-04-07):
- v1.5 milestone ledger is now accurate — MILESTONES.md jumps cleanly from v1.0 → v1.1 → v1.2 → v1.3 → v1.4, then v1.5 work begins
- Mar 7 same-day work split between v1.2 (SDP) and v1.3 (validator) by commit-subject prefix to preserve distinct headline metrics
- Mar 22 dist-branch CI + late corrections folded into v1.4 rather than spawning a v1.4.1 (ROADMAP only enumerates v1.1–v1.4)
- Material You theming placed in v1.4 alongside nav image evidence (it's a discovery, not a channel verification) per ROADMAP success criteria
- Grouping proposal preserved at .planning/phases/06-historical-bookkeeping/grouping-proposal.md as decision trail

### Pending Todos

None at milestone level. Phase 7 (VW Capture Analysis) is the next actionable work.

### Blockers/Concerns

- aa-logcat tool has broken logcat capture on Android 13+ (Shizuku fix needed) — affects DHU observation evidence gathering, but not v1.5 critical path
- Single-OEM evidence only — Gold tier promotions off this capture are technically "VW MIB3 OI 2024 Gold," not generalized OEM Gold. Addressed in v1.5 via TIER-02 scope dimension; multi-OEM corroboration remains a v2 problem (MOEM-01..03)
- VW capture format has no `channel_id` (on-phone Frida hook lives inside AA framing layer) — addressed in v1.5 via TIER-05 non-claim boundary documentation
- VW runs AA 16.4, DHU baselines span older APKs — version-alignment required in OEM-04 divergence report (shaped the Phase 9 dependency on Phase 8)

## Session Continuity

Last session: 2026-04-07
Stopped at: Phase 6 plan 01 complete -- MILESTONES.md updated with v1.1-v1.4 retroactive entries
Resume file: None
