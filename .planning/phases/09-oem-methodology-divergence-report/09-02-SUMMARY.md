---
phase: 09-oem-methodology-divergence-report
plan: 02
subsystem: oem-divergence-analysis
tags: [python, pytest, protobuf, sdp-divergence, attribution, phase-7-reuse, phase-8-reuse, oem-04]

requires:
  - phase: 07-vw-capture-analysis
    provides: "oem_vw_parser.sdp_decode (decode_sdp_response library function), sdp-values.json (VW SDP parsed shape), DeclaredService dataclass shape"
  - phase: 08-16-4-cross-version-validation
    provides: "16-4-delta-report.json (new_in_16_4 + removed_in_16_4 attribution source), schema migration precedent"
  - phase: 09-oem-methodology-divergence-report (Plan 09-01)
    provides: "dhu_divergence package skeleton, conftest.py with repo_root + schema fixtures, retracted sidecar backstop"
provides:
  - "analysis/tools/dhu_divergence/ — sibling package with 5 implementation modules importing oem_vw_parser as a library"
  - "baseline_merge.load_dhu_baseline + merge_baselines — DHU SDP loader + union merge with baselines_matched provenance"
  - "divergence.compute_divergences — channel_kind-granularity diff producing service_only_in_vw / service_only_in_dhu entries"
  - "attribution.classify_divergence — version | oem | ambiguous classifier using Phase 8 delta report substring lookup"
  - "report.build_json + emit_markdown + emit_json — 8-section markdown + JSON sidecar with locked top-level keys, deterministic output"
  - "run.py CLI — wires all 5 modules through a single PYTHONPATH=. python3 -m analysis.tools.dhu_divergence.run entry point"
  - "analysis/reports/oem-vw/dhu-divergence.md + dhu-divergence.json — live OEM-04 deliverable with sha256-locked provenance"
  - "12 Plan 09-02 tests (1 merge + 2 divergence + 3 attribution + 3 report + 3 live snapshot) all green"
affects: [phase-10-gold-promotion-walk, phase-11-channel-architecture-reference, phase-12-coverage-dashboard]

tech-stack:
  added: []
  patterns:
    - "Sibling-package import-not-fork discipline — dhu_divergence imports oem_vw_parser.sdp_decode as a library function and reshapes the returned SdpSnapshot.services tuple into Phase 7's channel-dict shape. Zero modifications to Phase 7's parser, verified via git status --porcelain."
    - "Loose substring matching for attribution lookup — service strings (channel_kind) and proto_message names don't line up 1:1 (e.g., bluetooth_channel vs BluetoothPairingResponse), so the matcher strips _channel + underscores and does case-insensitive substring containment. Lets version attribution fire when Phase 8 starts populating new_in_16_4 without code changes."
    - "Empirical snapshot test pattern with regeneration command in failure message — test_run.py asserts the live JSON contains specific empirical values (bluetooth_channel + wifi_channel VW-only, vendor_extension_channel DHU-only) and prints the regeneration CLI command in the failure message. Locked to 2026-04-08 research preview."

key-files:
  created:
    - analysis/tools/dhu_divergence/baseline_merge.py
    - analysis/tools/dhu_divergence/divergence.py
    - analysis/tools/dhu_divergence/attribution.py
    - analysis/tools/dhu_divergence/report.py
    - analysis/tools/dhu_divergence/run.py
    - analysis/tools/dhu_divergence/tests/fixtures/dhu_sdp_a.bin
    - analysis/tools/dhu_divergence/tests/fixtures/dhu_sdp_b.bin
    - analysis/tools/dhu_divergence/tests/fixtures/vw_sdp_mini.json
    - analysis/tools/dhu_divergence/tests/fixtures/delta_report_mini.json
    - analysis/tools/dhu_divergence/tests/fixtures/expected_divergence.json
    - analysis/reports/oem-vw/dhu-divergence.md
    - analysis/reports/oem-vw/dhu-divergence.json
  modified:
    - analysis/tools/dhu_divergence/tests/conftest.py
    - analysis/tools/dhu_divergence/tests/test_baseline_merge.py
    - analysis/tools/dhu_divergence/tests/test_divergence.py
    - analysis/tools/dhu_divergence/tests/test_attribution.py
    - analysis/tools/dhu_divergence/tests/test_report.py
    - analysis/tools/dhu_divergence/tests/test_run.py

key-decisions:
  - "All 4 DHU SDP baselines turned out to be byte-identical (sha256 a4f2bc3465b00efd6d2b3c420578272fb275d310b6c13c99a7d0ed42f90ee704, all 844 bytes). The merge logic handles this gracefully — kinds_to_baselines lists all 4 names for every kind. The empirical preview was correct: 14 channels / 8 distinct kinds across all 4 captures."
  - "load_dhu_baseline reshapes SdpSnapshot.services tuple into channel-dict shape — the plan called the field 'channels' but the actual oem_vw_parser dataclass field is 'services' (DeclaredService dataclasses). Rule 3 blocking fix: read the real dataclass and adapted the loader. No oem_vw_parser modification."
  - "Substring matching strips _channel suffix and underscores before lookup — service strings use channel_kind format (bluetooth_channel) while delta entries use proto names (BluetoothPairingResponse). Empty needle (after stripping) returns False to avoid spurious matches on degenerate inputs."
  - "Live attribution result matches research preview exactly: bluetooth_channel + wifi_channel attributed oem (not in new_in_16_4 — list is empty in live data); vendor_extension_channel attributed ambiguous (not in removed_in_16_4 even though the list has 143 entries — proto names don't substring-match the channel_kind)."
  - "vw_aa_version field reads head_unit_software_version from sdp-values.json which is '2756.04' (the HU's actual firmware build, not the AA app version 16.4.661034). Documented in the JSON metadata; downstream consumers can cross-reference both via the capture path."

patterns-established:
  - "Sibling package + library import: when reusing a Phase N parser in Phase N+M, create a new sibling package and import the parser's pure functions/dataclasses rather than extending the original. Verified via git status --porcelain analysis/tools/oem_vw_parser/ — empty after Plan 09-02 completes."
  - "Locked section header constant: report.py defines SECTION_HEADERS as a top-level constant (8 entries, locked) and references it by index in emit_markdown. Tests assert all 8 are present via SECTION_HEADERS iteration AND that file positions are monotonically increasing. Future contributors who edit the markdown layout cannot accidentally reorder sections without breaking test_eight_sections."
  - "Empirical snapshot tests carry their own regeneration command in the failure message — when DHU SDP bytes or VW SDP changes upstream, the test fails loudly with the exact CLI command needed to regenerate the artifact. No silent drift, no mystery failures."

requirements-completed: [OEM-04]

duration: 7min
completed: 2026-04-09
---

# Phase 9 Plan 02: VW-vs-DHU SDP Divergence Report Summary

**Sibling-package divergence tool that imports oem_vw_parser as a library, merges 4 byte-identical DHU SDP baselines, and emits an 8-section markdown + JSON report with the empirical preview locked: bluetooth_channel + wifi_channel attributed `oem`, vendor_extension_channel attributed `ambiguous`.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-04-09T12:20:29Z
- **Completed:** 2026-04-09T12:27:27Z
- **Tasks:** 4
- **Files created:** 12
- **Files modified:** 6
- **Tests added:** 12 (1 merge + 2 divergence + 3 attribution + 3 report + 3 live snapshot, all green)

## Accomplishments

- **Sibling-package OEM-04 deliverable shipped** without touching `analysis/tools/oem_vw_parser/`. The discipline locked into the success criteria (`git status --porcelain analysis/tools/oem_vw_parser/` is empty) holds end-to-end.
- **Live divergence report at `analysis/reports/oem-vw/dhu-divergence.{md,json}`** matches the Phase 9 research preview exactly:
  - `services_in_vw_but_not_dhu = ['bluetooth_channel', 'wifi_channel']` (both attributed `oem`)
  - `services_in_dhu_but_not_vw = ['vendor_extension_channel']` (attributed `ambiguous`)
  - `summary.by_attribution = {version: 0, oem: 2, ambiguous: 1}`
- **All 4 DHU SDP baselines confirmed byte-identical** (single sha256 `a4f2bc34...`, 844 bytes each). The merge logic correctly attributes every channel kind to all 4 baseline names. This is exactly what the research preview predicted.
- **8 locked markdown section headers** in the exact mandated order, verified by `test_eight_sections` (presence + monotonically-increasing position) and by an independent grep against the live report.
- **9 locked JSON top-level keys** including `metadata` with sha256 hashes for all 4 DHU SDP files AND the Phase 8 delta report (5 hashes total, each 64 hex chars).
- **Phase 8 backward-compat baseline preserved** at 334 passed / 1 pre-existing failure (NavigationDistanceMessage). Phase 9 Plan 02 introduced zero regressions.

## Task Commits

Each task was committed atomically:

1. **Task 1: Wave 0 fixtures + test stubs** — `d77f2c2` (chore)
2. **Task 2: baseline_merge + divergence modules + 3 unit tests** — `5c90582` (feat)
3. **Task 3: attribution + report emitters + 6 unit tests** — `4a1cb3b` (feat)
4. **Task 4: CLI + live dhu-divergence.{md,json} + 3 snapshot tests** — `a339e88` (feat)

## Live Divergence Report Headlines

```
total_divergences:    3
by_attribution:       {version: 0, oem: 2, ambiguous: 1}
by_service:           {bluetooth_channel: 1, wifi_channel: 1, vendor_extension_channel: 1}
services_in_vw_only:  [bluetooth_channel, wifi_channel]
services_in_dhu_only: [vendor_extension_channel]
```

**Per-baseline summary** (all 4 baselines identical):

| Baseline           | Channels | Distinct kinds |
|--------------------|----------|----------------|
| general            | 14       | 8              |
| idle-baseline      | 14       | 8              |
| music-playback     | 14       | 8              |
| active-navigation  | 14       | 8              |

**JSON metadata provenance:**

- 4 DHU SDP file sha256 hashes (all `a4f2bc3465b00efd6d2b3c420578272fb275d310b6c13c99a7d0ed42f90ee704`)
- Phase 8 delta report sha256 (64 hex chars)
- VW capture path: `captures/oem-vw-mib3oi-2026-04-06/`
- VW AA version: `2756.04` (from `head_unit_software_version`)
- VW make/model/year/headunit: Volkswagen / VW3363 / 2024 / LGE COCKPIT_MIB3OI_GP

## Attribution Logic Live Result

Phase 8's `new_in_16_4` is empty in live data (0 entries). `removed_in_16_4` has 143 entries but none substring-match `bluetooth`, `wifi`, or `vendorextension`. Result:

| Service                     | Direction | Attribution | Reason                                                                          |
|-----------------------------|-----------|-------------|--------------------------------------------------------------------------------|
| bluetooth_channel           | VW-only   | oem         | Not in new_in_16_4. Present in VW SDP, absent from all DHU baselines.          |
| wifi_channel                | VW-only   | oem         | Not in new_in_16_4. Present in VW SDP, absent from all DHU baselines.          |
| vendor_extension_channel    | DHU-only  | ambiguous   | Not in removed_in_16_4. Could be DHU test harness or version drift.            |

This is the locked empirical preview from `09-RESEARCH.md § Live divergence preview` — confirmed end-to-end by `test_live_expected_vw_only` and `test_live_expected_dhu_only`.

## Files Created/Modified

**Created (12 files):**

- `analysis/tools/dhu_divergence/baseline_merge.py` — DHU SDP loader + union merge
- `analysis/tools/dhu_divergence/divergence.py` — VW-vs-merged-DHU diff
- `analysis/tools/dhu_divergence/attribution.py` — version/oem/ambiguous classifier
- `analysis/tools/dhu_divergence/report.py` — 8-section markdown + JSON emitter
- `analysis/tools/dhu_divergence/run.py` — CLI entry point
- `analysis/tools/dhu_divergence/tests/fixtures/dhu_sdp_a.bin` — copy of `captures/general/sdp_response.bin`
- `analysis/tools/dhu_divergence/tests/fixtures/dhu_sdp_b.bin` — copy of `captures/active-navigation/sdp_response.bin`
- `analysis/tools/dhu_divergence/tests/fixtures/vw_sdp_mini.json` — minimal VW SDP fixture for divergence tests
- `analysis/tools/dhu_divergence/tests/fixtures/delta_report_mini.json` — synthetic Phase 8 delta covering attribution branches
- `analysis/tools/dhu_divergence/tests/fixtures/expected_divergence.json` — golden shape reference
- `analysis/reports/oem-vw/dhu-divergence.md` — live OEM-04 report (markdown)
- `analysis/reports/oem-vw/dhu-divergence.json` — live OEM-04 report (JSON sidecar)

**Modified (6 files):**

- `analysis/tools/dhu_divergence/tests/conftest.py` — added session-scoped `descriptor_bundle` fixture
- `analysis/tools/dhu_divergence/tests/test_baseline_merge.py` — replaced 1 stub with `test_union_merge`
- `analysis/tools/dhu_divergence/tests/test_divergence.py` — replaced 2 stubs (`test_vw_only_services`, `test_dhu_only_services`)
- `analysis/tools/dhu_divergence/tests/test_attribution.py` — replaced 3 stubs (`test_vw_only_defaults_oem`, `test_vw_only_version_attribution`, `test_dhu_only_defaults_ambiguous`)
- `analysis/tools/dhu_divergence/tests/test_report.py` — replaced 3 stubs (`test_eight_sections`, `test_json_structure`, `test_metadata_hashes`)
- `analysis/tools/dhu_divergence/tests/test_run.py` — replaced 3 stubs (`test_live_divergence_snapshot`, `test_live_expected_vw_only`, `test_live_expected_dhu_only`)

## Decisions Made

All captured in `key-decisions` frontmatter. Highlights:

- **`SdpSnapshot.services` not `.channels`** — the plan called the field `channels` but the actual `oem_vw_parser` dataclass uses `services` (a tuple of `DeclaredService`). The loader reshapes that into the channel-dict shape Phase 7 uses. Caught at the very first integration point; no oem_vw_parser modification needed.
- **Substring matching is the realistic attribution matcher** — service strings (channel_kind format) and delta entries (proto message names) do not line up 1:1, so the matcher strips `_channel` and underscores before substring containment. Empty needle short-circuits to False.
- **Byte-identical DHU baselines are the data, not a bug** — research predicted it, the merge handles it cleanly (every kind has all 4 baseline names listed in `kinds_to_baselines`), and the per-baseline summary shows it transparently.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Plan called the SdpSnapshot field `channels`, real field is `services`**

- **Found during:** Task 2 (baseline_merge.py implementation)
- **Issue:** The plan's `<interfaces>` block said `decode_sdp_response(...)` returns an `SdpSnapshot` with a `.channels` list. Reading `analysis/tools/oem_vw_parser/models.py` directly showed the dataclass field is `services: tuple[DeclaredService, ...]` (not `channels`). The plan's `getattr(snapshot, "channels", [])` would have silently returned an empty list because the attribute doesn't exist.
- **Fix:** Loader iterates `snapshot.services` directly (not `getattr`), accessing the `DeclaredService.channel_id`, `.channel_kind`, `.config` fields by name. Reshapes into the `{channel_id, channel_kind, config}` dict shape Phase 7's `sdp-values.json` uses, so both sides of the divergence computation share one structural view. No `oem_vw_parser` modification — the field rename is purely on the consuming side.
- **Files modified:** `analysis/tools/dhu_divergence/baseline_merge.py`
- **Verification:** `test_union_merge` passes against the real DHU SDP fixtures; live CLI run produces the empirical-preview-correct divergence (3 entries with the expected service names). Plan 09-01's `test_retracted_sidecars.py` and the Phase 8 baseline both still green.
- **Committed in:** `5c90582` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 Rule 3 blocking)
**Impact on plan:** A drop-in field-name correction caught at first integration. Without it, every `load_dhu_baseline` call would have returned a `DhuBaseline` with an empty channels list, causing the merge to find zero kinds and the divergence to report nothing — every test would have failed with an unhelpful "kinds set is empty" error. The fix was minimal (read the real dataclass, use the real field name) and preserved the import-not-fork discipline.

## Issues Encountered

None beyond the single field-name deviation. Each task committed atomically on first attempt after handling the deviation. No checkpoint was hit; the plan ran end-to-end autonomously in 7 minutes.

The CLI's first live run produced exactly the expected empirical preview output with no debugging needed — `bluetooth_channel`, `wifi_channel` VW-only and `vendor_extension_channel` DHU-only — because the field-name fix was the only real correctness bug in the entire pipeline.

## User Setup Required

None — no external service configuration needed for this plan's deliverables. All work is library imports, test fixtures, CLI scripting, and committed report files. Runs locally with the existing pytest + protobuf + jsonschema stack.

## Next Phase Readiness

**Phase 10 (Gold-tier promotion walk, TIER-04) is unblocked for OEM-04 consumption.** It has:

- `analysis/reports/oem-vw/dhu-divergence.json` — machine-consumable divergence report with `services_in_vw_but_not_dhu` (the OEM candidates Phase 10 will scope promotions to) and `oem_attributed_divergences` (the entries that justify Platinum claims for OEM-specific protos).
- `metadata.dhu_baselines[].sha256` and `metadata.phase_8_delta_report_sha256` — provenance hashes Phase 10's promotion walk can cite when it emits Platinum sidecars.
- Live attribution showing 0 version-attributed divergences (Phase 8's `new_in_16_4` is empty), so Phase 10's first promotion pass can treat every VW-only service as OEM-attributable until Phase 8 starts populating version data.

**Phase 11 (ARCH-04 channel architecture reference)** can cite the divergence report for VW-vs-DHU examples — specifically the bluetooth_channel and wifi_channel entries, which are the cleanest "VW exercises this, DHU does not" cases in the live data.

**Phase 12 (REPORT-01 dashboard)** reads `dhu-divergence.json` for divergence stats: by_attribution, by_service, per_baseline_observation_summary all map directly into dashboard widgets.

**Deferred for Phase 10+:** the divergence tool currently emits only service-level (channel_kind granularity) divergences. Field-level (`config_mismatch`) is reserved in the `DivergenceKind` literal but not yet emitted. Phase 10 may extend the divergence calc to emit per-field config mismatches once the promotion walk identifies which fields need OEM-vs-DHU comparison.

**Phase 9 itself is now COMPLETE** — both 09-01 (methodology surface) and 09-02 (divergence report) shipped. The full Phase 9 test sweep is 30 + 12 = 42 new tests passing across both plans, with the Phase 8 baseline of 334/1 preserved.

## Self-Check: PASSED

All 13 files referenced in this summary exist at their stated paths (verified via filesystem check). All 4 task commits exist in git history (verified via `git log --oneline --all | grep`). Plan 09-02 test suite runs 12 passed / 0 failed / 0 skipped. Phase 8 backward-compat baseline holds at 334 passed / 1 pre-existing failure (NavigationDistanceMessage). Live divergence report at `analysis/reports/oem-vw/dhu-divergence.{md,json}` carries the empirical preview locked: VW-only `[bluetooth_channel, wifi_channel]`, DHU-only `[vendor_extension_channel]`, summary `{version: 0, oem: 2, ambiguous: 1}`. `git status --porcelain analysis/tools/oem_vw_parser/` is empty — import-not-fork discipline preserved.

---
*Phase: 09-oem-methodology-divergence-report*
*Completed: 2026-04-09*
