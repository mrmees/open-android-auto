---
gsd_state_version: 1.0
milestone: v1.5
milestone_name: milestone
status: Phase 9 COMPLETE. Both plans 09-01 (methodology surface) and 09-02 (dhu_divergence report, OEM-04) shipped. dhu-divergence.{md,json} live at analysis/reports/oem-vw/ with empirical preview locked: bluetooth+wifi VW-only attributed oem, vendor_extension DHU-only attributed ambiguous. 12 Plan 09-02 tests green (1 merge + 2 divergence + 3 attribution + 3 report + 3 live snapshot). Phase 8 baseline preserved at 334/1. oem_vw_parser/ untouched. Phase 10 (Gold promotion walk, TIER-04) is unblocked.
stopped_at: "Completed 09-02-PLAN.md -- Phase 9 COMPLETE; Plan 09-02 (dhu_divergence report) shipped: bluetooth+wifi VW-only attributed oem, vendor_extension DHU-only attributed ambiguous; 12 new tests green; oem_vw_parser untouched; Phase 10 unblocked"
last_updated: "2026-04-09T12:30:40.110Z"
last_activity: 2026-04-09 -- Phase 9 COMPLETE (both plans landed; OEM-04 dhu-divergence report shipped with empirical preview locked; oem_vw_parser untouched; Phase 10 unblocked)
progress:
  total_phases: 7
  completed_phases: 4
  total_plans: 12
  completed_plans: 7
  percent: 58
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-07)

**Core value:** Every published proto definition and protocol claim carries explicit verification evidence and confidence level
**Current focus:** Phase 7 COMPLETE (OEM-01/02/03/05 all satisfied); Phase 8 (cross-version analysis) is the next critical path; Phase 8 and Phase 9 are the remaining v1.5 work

## Current Position

Phase: 9 (OEM Methodology & Divergence Report) -- COMPLETE
Plan: 09-01 -- COMPLETE; 09-02 -- COMPLETE
Status: PHASE 9 COMPLETE. Plan 09-02 (VW-vs-DHU SDP divergence report, OEM-04) shipped: new sibling package analysis/tools/dhu_divergence/ with 5 implementation modules (baseline_merge, divergence, attribution, report, run) imports oem_vw_parser.sdp_decode as a library function and reshapes SdpSnapshot.services tuple into Phase 7 channel-dict shape. NO modifications to oem_vw_parser/ — import-not-fork discipline preserved (verified via git status --porcelain). Live divergence report at analysis/reports/oem-vw/dhu-divergence.{md,json} matches research preview exactly: services_in_vw_but_not_dhu = [bluetooth_channel, wifi_channel] (both attributed oem); services_in_dhu_but_not_vw = [vendor_extension_channel] (attributed ambiguous); summary by_attribution = {version: 0, oem: 2, ambiguous: 1}. All 4 DHU SDP baselines confirmed byte-identical (single sha256 a4f2bc3465..., 844 bytes each, 14 channels / 8 distinct kinds). 12 new tests all green (1 merge + 2 divergence + 3 attribution + 3 report + 3 live snapshot). Phase 8 baseline held at 334 passed / 1 pre-existing failure (NavigationDistanceMessage). 8 locked markdown section headers and 9 locked JSON top-level keys both verified. Metadata block carries sha256 hashes for all 4 DHU SDP files + Phase 8 delta report (5 hashes total). Phase 10 (Gold promotion walk, TIER-04) is unblocked: dhu-divergence.json gives it the OEM candidate scoping, the migrated schema accepts platinum_evidence entries, 05-oem-match-policy.md defines the rule IDs, and VideoFocusRequestMessage is the reference platinum-promotion shape.
Last activity: 2026-04-09 -- Phase 9 COMPLETE (both plans landed; OEM-04 dhu-divergence report shipped with empirical preview locked; oem_vw_parser untouched; Phase 10 unblocked)

Progress: [███████░░░] 58% (7/12 v1.5 plans complete)

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

Phase 7 plan 01 execution decisions (2026-04-07):
- msg_type=0 demotion fires on payload-size signal alone (>32 bytes), not the freq>=100 backstop, because the size signal is already decisive — a non-empty msg_type=0 record cannot be ServiceDiscoveryFeatureA regardless of how many times it appears
- Frequency threshold knee detection scans from N=3 instead of N=2 because freq=1 is the noise floor (1,032 distinct singletons on the live capture); the 1→2 drop is dominated by garbage and is not the real signaling boundary
- Wire walker treats `field_num==0` during tag decoding as a clean padding-bail sentinel rather than a wire-walk failure (verified on real PingRequest seq=58 from the VW capture: `000b08e7c9dccace6a100000`)
- `build_descriptor_bundle` is called with explicit `repo_root` + `out_dir` arguments in conftest.py to match the existing `proto_stream_validator/tests/test_decode.py` shape (the plan's no-arg snippet was wrong about the actual signature)
- Histogram snapshot test allows ±1 absolute slack on Tier B (and ±1% on Tier A/C) to tolerate descriptor-map edge boundary cases without false-failing on legitimate ±1 record drift
- Live capture results: 7,954 records → A=267, B=3,890, C=3,797; standalone=4,147, probable_first=3, continuation_or_garbage=3,804; reassembled=0, unattributed=0; msg_type=0 demoted=2,751; empirical freq threshold=3

Phase 8 plan 01 execution decisions (2026-04-08):
- Custom match_16_4.py module built from scratch — proto_triage has no per-mapping matching API (08-RESEARCH Correction #1). The locked "enum fingerprint + field count within ±1" rule was reworded to "structural fingerprint uniqueness" because it only covers 5 of 240 mappings literally; field-tuple matching is the dominant signal for the 206 message mappings.
- Pass 2 topology disambiguation reseeds its anchor map mid-pass — each Pass 2 commit becomes a new anchor for later Pass 2 iterations. Yields 13 commits vs the 10 research baseline. Still fully idempotent.
- class_mapping.yaml version keys written in deterministic order (15.9 → 16.1 → 16.2 → 16.4) for reviewable git diffs. PyYAML safe_dump; no ruamel.yaml dep. Ambiguous-match notes live in 16-4-mapping-candidates.md, not inline YAML comments (08-RESEARCH Correction #5).
- Spurious enum drift suppression is UNCONDITIONAL — all 4 locked names (DriverPosition, HapticFeedbackType, SensorErrorStatus, CarLocalMediaPlayback) appear in known_indexer_artifacts even if the current comparison didn't surface them. Ensures test_spurious_enum_suppression holds whether or not 16.1/16.2 DBs are re-indexed with proto_enum_classes.
- Wave 0 reframe: test_find_db_164 and test_four_version_pairs already pass without code change (run_comparison is already version-agnostic). Removed xfail markers in Wave 0 rather than artificially breaking them.
- Delta report summary.total reflects full class_mapping.yaml row count (240), not the ComparisonResult count — catches mappings that never enter run_comparison() because both source and target field lists are empty.
- Live matcher empirical: 5 enum + 78 msg + 13 topology = 96 / 240 committable (40%). Delta JSON sidecar shows 0 schema_changes after suppression, 0 drifted_silver_gold, 144 unmappable, 143 removed_in_16_4.
- Baseline reproduction block in delta report locks sha256 hashes for all 4 APK index DBs. Regeneration command is PYTHONPATH=. python3 -m analysis.tools.cross_version.run.
- Pre-existing test failures (170 total: 168 silver_annotations + 1 promoted_sidecars + 1 published_outputs) logged in deferred-items.md. Unrelated to the 16.4 pipeline; Plan 08-01 does not touch them.

Phase 7 plan 02 execution decisions (2026-04-08):
- Direction by decode (not by file name) — the SDP request/response direction resolver tries both proto types and picks the one that decodes non-trivially. Locks the corrected direction permanently; anyone who "fixes" the README and breaks the decoder fails test_direction_resolution.
- Pre-flight Prodigy range cross-check: all 4 hypotheses dropped for VW (radio + car_control inapplicable, sensor + navigation ambiguous due to per-channel namespace collisions). surviving_hints = []. Range matching is dormant for VW; SDP narrowing is the primary signal.
- Strict 5-row attribution taxonomy preserved despite making observed[] thin: most VW Tier B records get sdp_candidates (multiple shape predicates match) → service=None → not in observed[]. The records exist in per_msg_type with service=null. Documented as locked behavior, not a bug.
- Comparative gaps filter out service_type='control' as a universal service (every capture has it on channel_id 0; not a per-channel kind). Result: comparative gaps = ['vendor_extension'] only.
- _discover_dhu_files() handles both canonical (aa_messages.jsonl) and suffixed (aa_messages_<scenario>.jsonl) DHU baseline naming — only captures/general uses the canonical pair.
- _fix_capture_readme() uses defensive single+double-space variants for the swap literal — the plan snippet had double space but the actual README uses single space. Idempotent ('right variant already present' guard).
- test_oem_only_diff garbage check loosened to 'every key in diff has at least one non-garbage record' — the plan's strict check was contradictory (a single (msg_type, direction) key can map to both garbage and non-garbage classified records).
- Live coverage results: 5 observed channels (5 av_channels), 8 intrinsic gaps, 1 comparative gap (vendor_extension), 1 anomaly.unattributed (msg_type=0x8035 out, single record), 17 OEM-only candidates by msg_type, 1,061 per_msg_type entries, baseline_snapshot_hash=ffb074e4f1...
- [Phase 08-16-4-cross-version-validation]: Phase 8 Plan 02: audit-schema.json whitelists optional status + drift_issues (additionalProperties stays false); walker is append-only with content-hash dedupe excluding date; strict all-6-pairs-clean rule yields 0 Bronze promotions (expected); 120 sidecars updated with 48 consistent + 72 unmappable_16_4 entries; walker is bit-idempotent on the real oaa/ tree; 40 skipped sidecars logged (35 pre-existing schema, 7 orphan, 1 malformed)

Phase 8 plan 02 execution decisions (2026-04-08):
- Schema migration whitelists new fields explicitly rather than relaxing additionalProperties: false — preserves the audit-schema contract so future drift is caught loudly. Adding status and drift_issues as optional keeps pre-Phase-8 entries valid without retroactive edits.
- drift_issues.kind enum uses lowercase values (field_added / field_removed / field_type_changed) to match the Python IssueKind model — the plan snippet used uppercase spec text but the real Python enum values are lowercase. Schema now matches the code so cross-version evidence can be queried / serialized without translation.
- content_hash explicitly excludes the date field (signature: type, method, source, description, status, drift_issues). Without this exclusion, re-running the walker on a different day would create false "new" entries every day, breaking the locked idempotency contract (PITFALL #6 in 08-RESEARCH.md).
- promote_eligible reads current tier from disk (not from ProtoMapping.confidence). The 240 ProtoMapping.confidence fields in class_mapping.yaml are stale seed-import defaults; the real current tier lives in the sidecar's confidence: field on disk.
- test_live_promotion_snapshot filters to actually-Bronze sidecars (reads confidence from disk). An early test iteration classified every mapping as if it were Bronze and returned 80 "promoted" — because 80 Silver sidecars have clean all-6-pairs but the rule only promotes them if they're currently Bronze. Filtering to current_tier == "bronze" gives the real 0-promotions headline.
- Legacy 3-version generate_report now suppresses the 4 known spurious enum drifts (consistent with delta_report.py). Rule 2 auto-fix: without this, run.py --promote exits non-zero from the 4 spurious drifts and breaks the acceptance pipeline's && chain.
- Walker skips invalid sidecars rather than rewriting them. 35 pre-existing sidecars (changes_applied, class_15_9/16_1/16_2, msg_id, deep_trace method, superseded confidence) don't conform to the current schema. The walker logs them and moves on rather than (a) silently breaking the append-only contract with a rewrite or (b) halting the walk.
- All 10 Bronze sidecars classify as stayed_bronze_no_164 (not stayed_bronze_marker). The Research doc framed the gap as 0-field markers; the live result is that those 10 also happen to have null 16.4 entries, so they're flagged as unmappable rather than marker-class-trivial. Semantically the same outcome (stay Bronze), but the reason is slightly different. The stayed_bronze_marker outcome exists in the classifier for future cases but is currently empty.
- Walker end-to-end stats: 160 sidecars → 120 updated (75%), 40 skipped (25%). Of 120 updated: 48 status=consistent, 72 status=unmappable_16_4, 0 drift_detected, 0 unmappable_marker. Of 40 skipped: 35 schema_validation_failed (pre-existing), 7 orphan_no_mapping, 1 malformed.
- Test suite baseline improved slightly: 528 passed / 170 failed → 568 passed / 168 failed. The -2 is incidental (parametric test collection shifted slightly); no regressions introduced.
- [Phase 09-oem-methodology-divergence-report]: Tier ladder locked at unverified → bronze → silver → gold → platinum, retracted as non-ordinal state
- [Phase 09-oem-methodology-divergence-report]: Gold redefined as deep-trace APK + cross-version (matches existing 32 Gold sidecars, no migration required); Platinum strictly above Gold with OEM wire capture confirmation
- [Phase 09-oem-methodology-divergence-report]: Platinum badges ALWAYS render with scope qualifier (Platinum / single-OEM or Platinum / multi-OEM) — single-OEM trap named on badge, not in prose footnote
- [Phase 09-oem-methodology-divergence-report]: 8 MATCH + 4 NOMATCH rules as closed enum in audit-schema.json; cross-file integrity test asserts schema enum exactly equals 05-oem-match-policy.md doc headings
- [Phase 09-oem-methodology-divergence-report]: Rule 1 auto-fix: whitelisted 10 legacy top-level sidecar fields + 2 legacy evidence types (apk_deep_trace, deep_trace) so 6 retracted sidecars + VideoFocusRequestMessage validate; plan assumed only tier enum addition needed, reality required legacy whitelist too. additionalProperties: false preserved
- [Phase 09-oem-methodology-divergence-report]: Cross-link walker uses sentinel-substring idempotency + path-suffix self-exclusion; explicit 5-file WALKER_TARGETS list (not glob-discovered); walker is byte-idempotent on real docs tree
- [Phase 09-oem-methodology-divergence-report]: First Gold→Platinum promotion: VideoFocusRequestMessage citing MATCH-08 (SDP descriptor match); msg_seq/ts_ms placeholders [0]/[0] for Phase 10 to overwrite after deep wire inspection
- [Phase 09-oem-methodology-divergence-report]: Plan 09-02: dhu_divergence sibling package imports oem_vw_parser.sdp_decode as a library; SdpSnapshot field is .services not .channels (Rule 3 fix); reshape to {channel_id, channel_kind, config} dicts to share Phase 7 sdp-values.json shape; oem_vw_parser/ remains untouched (verified via git status --porcelain)
- [Phase 09-oem-methodology-divergence-report]: Plan 09-02: All 4 DHU SDP baselines are byte-identical (single sha256 a4f2bc3465..., 844 bytes each, 14 channels / 8 distinct kinds); merge logic handles the degenerate union gracefully — every kind gets all 4 baseline names in kinds_to_baselines provenance
- [Phase 09-oem-methodology-divergence-report]: Plan 09-02: Live attribution result matches research preview exactly — bluetooth_channel + wifi_channel attributed oem (new_in_16_4 empty); vendor_extension_channel attributed ambiguous (no removed_in_16_4 substring match); summary by_attribution = {version: 0, oem: 2, ambiguous: 1}; live empirical snapshot tests lock these against future drift
- [Phase 09-oem-methodology-divergence-report]: Plan 09-02: Substring matcher strips _channel suffix and underscores before delta lookup — service strings (channel_kind format) and delta entries (proto message names) don't line up 1:1, so loose substring containment is the realistic matcher; empty needle short-circuits to False; design lets version attribution fire automatically once Phase 8 starts populating new_in_16_4

### Pending Todos

- Phase 9 (divergence report) — REQUIRES BOTH Phase 7 and Phase 8 outputs. Reads analysis/reports/oem-vw/coverage.json + sdp-values.json + candidate-oem-only-msg-types.json from Phase 7 AND analysis/reports/cross-version/16-4-delta-report.json from Phase 8 (now with the populated promoted_bronze_to_silver key). Schema migration in Plan 08-02 lets Phase 9 add oem_evidence fields using the same "explicit whitelist under additionalProperties: false" pattern.
- Phase 10 (Gold promotion walk, TIER-04) — gated on Phase 9. Reads coverage.json.observed[] to scope which Silver protos can be promoted. Override mechanism enforced via coverage.validate_override(). Silver pool is unchanged at 111 after Phase 8 (expected — the headline 0-promotion result stands). The strict is_eligible_for_silver rule from Plan 08-02 is reusable as a template for is_eligible_for_gold.
- Housekeeping (deferred, not blocking): clean up 35 pre-existing schema-invalid sidecars under oaa/ (changes_applied, class_15_9/class_16_1/class_16_2, msg_id, deep_trace method, superseded confidence — logged to analysis/reports/cross-version/skipped-sidecars.md). Not in scope for Phase 9 or 10 unless the schema evolves to accept these fields.

### Blockers/Concerns

- aa-logcat tool has broken logcat capture on Android 13+ (Shizuku fix needed) — affects DHU observation evidence gathering, but not v1.5 critical path
- Single-OEM evidence only — Gold tier promotions off this capture are technically "VW MIB3 OI 2024 Gold," not generalized OEM Gold. Addressed in v1.5 via TIER-02 scope dimension; multi-OEM corroboration remains a v2 problem (MOEM-01..03)
- VW capture format has no `channel_id` (on-phone Frida hook lives inside AA framing layer) — addressed in v1.5 via TIER-05 non-claim boundary documentation
- VW runs AA 16.4, DHU baselines span older APKs — version-alignment required in OEM-04 divergence report (shaped the Phase 9 dependency on Phase 8)

## Session Continuity

Last session: 2026-04-09T12:30:22.155Z
Stopped at: Completed 09-02-PLAN.md -- Phase 9 COMPLETE; Plan 09-02 (dhu_divergence report) shipped: bluetooth+wifi VW-only attributed oem, vendor_extension DHU-only attributed ambiguous; 12 new tests green; oem_vw_parser untouched; Phase 10 unblocked
Resume file: None
