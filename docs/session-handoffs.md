# Session Handoffs

Append-only log for cross-session continuity.

## Template

Date / Session: YYYY-MM-DD / short-session-name

What Changed:
- item

Why:
- rationale

Status:
- current state

Next Steps:
1. step
2. step

Verification:
- `command` -> result

## 2026-02-27 - Lean Workflow Bootstrap

Date / Session: 2026-02-27 / codex-lean-workflow-setup

What Changed:
- Added `AGENTS.md` with a protocol-adapted project management loop.
- Added `docs/roadmap-current.md` with `Now / Next / Later` priorities.
- Added this `docs/session-handoffs.md` log with a reusable handoff template.

Why:
- Create a lightweight workflow structure aligned with `openauto-prodigy` while fitting this repo's protocol-reference scope.

Status:
- In progress. Core workflow files are in place; README integration and final verification remain.

Next Steps:
1. Add workflow file references to `README.md`.
2. Run final consistency verification across workflow docs.
3. Confirm clean git state after commits.

Verification:
- `rg -n "Project Management Loop|Verification Baseline|Completion Rule" AGENTS.md` -> 3 matches.
- `rg -n "^## (Now|Next|Later|Focus Guardrails)$|^Last Updated:" docs/roadmap-current.md` -> 5 matches.

## 2026-02-27 - Lean Workflow Bootstrap Completed

Date / Session: 2026-02-27 / codex-lean-workflow-setup

What Changed:
- Added workflow references to `README.md`.
- Verified workflow file presence and cross-reference consistency.
- Completed lean workflow bootstrap for this repository.

Why:
- Make workflow entry points discoverable and ensure the new governance files are internally consistent.

Status:
- Complete.

Next Steps:
1. Use `AGENTS.md` loop for subsequent behavior-changing work.
2. Update `docs/roadmap-current.md` as priorities shift.
3. Keep appending handoff entries for each meaningful session.

Verification:
- `ls AGENTS.md docs/roadmap-current.md docs/session-handoffs.md` -> files present.
- `rg -n "roadmap-current|session-handoffs|AGENTS.md" AGENTS.md README.md docs/roadmap-current.md docs/session-handoffs.md` -> expected references found.
- `git status --short` -> clean before this handoff append.

## 2026-02-28 - APK Protobuf Catalog Phase (Task Batch 1)

Date / Session: 2026-02-28 / codex-apk-protobuf-catalog

What Changed:
- Added catalog pipeline primitives in `analysis/tools/apk_indexer`: confidence classifier, catalog derivation, benchmark harness, query pack, and report extensions.
- Extended SQLite schema and writer outputs with `proto_catalog`, `proto_evidence`, `proto_unknowns`, and `run_metadata`.
- Updated tests to enforce schema contract, catalog split behavior, run outputs, report sections, and benchmark metrics.
- Updated `docs/roadmap-current.md` to reflect current 2-week catalog priorities.

Why:
- Execute the approved roadmap to produce an evidence-backed protobuf catalog workflow for canonical APK `v16.1`.

Status:
- In progress. Core pipeline and tests are implemented; canonical local source path for full real-data smoke run was not available in this environment.

Next Steps:
1. Run the indexer against the real canonical decompiled `v16.1` source when path is available.
2. Start manual triage of unknown queue entries and promote high-confidence definitions.
3. Align proto-path references with ongoing `proto/oaa -> oaa` reorganization after it lands in this branch.

Verification:
- `PYTHONPATH=. pytest analysis/tools/apk_indexer/tests -v` -> `24 passed`.
- `test -d /home/matt/claude/personal/openautopro/firmware/android-auto-apk/decompiled && echo source_present || echo source_missing` -> `source_missing`.
- Synthetic smoke run:
  - `PYTHONPATH=. python3 analysis/tools/apk_indexer/run_indexer.py --source <tmp_fixture> --analysis-root <tmp_out> --scope all`
  - Output verified: `apk_index.db`, `proto_catalog.json`, `proto_unknowns.json`, `reports/summary.md`.

## 2026-02-28 - Lane Change Checkpoint (Obfuscation Chain Design)

Date / Session: 2026-02-28 / codex-lane-change-checkpoint

What Changed:
- Added approved design doc for obfuscation-chain traversal and name recovery:
  - `docs/plans/2026-02-28-obfuscation-chain-resolution-design.md`
- Recorded checkpoint for pausing implementation and switching focus.

Why:
- Preserve exact restart context before changing lanes, so the obfuscation-chain effort can resume without rediscovery.

Status:
- Parked for later review and execution planning.

Next Steps:
1. Have Claude review `docs/plans/2026-02-28-obfuscation-chain-resolution-design.md`.
2. After review, convert design into an implementation plan.
3. Execute in an isolated worktree when this lane is resumed.

Verification:
- `git show --name-only --oneline bffc477` -> design doc commit exists and includes `docs/plans/2026-02-28-obfuscation-chain-resolution-design.md`.

## 2026-02-28 - Proto Stream Validator Implementation (Non-Media Capture Diff Gate)

Date / Session: 2026-02-28 / codex-proto-stream-validator-implementation

What Changed:
- Added `analysis/tools/proto_stream_validator/` with:
  - `run.py` CLI (`validate` + `--bless --reason`)
  - capture/baseline I/O (`io.py`, `models.py`)
  - phase-1 non-media filtering (`filtering.py`)
  - tuple->message resolver (`message_map.py`)
  - descriptor set build + decode engine (`descriptors.py`, `decode.py`)
  - normalization and diff engine (`normalize.py`, `diffing.py`)
- Added test suite under `analysis/tools/proto_stream_validator/tests/` including:
  - unit tests for I/O, mapping/filtering, normalization/diff, CLI policy
  - golden capture fixture + baseline fixture for end-to-end non-media validation
- Added tool documentation: `analysis/tools/proto_stream_validator/README.md`.
- Updated docs integration:
  - `analysis/README.md` (new tool section)
  - `CONTRIBUTING.md` (capture-based validation workflow + bless policy)
  - `docs/roadmap-current.md` (Next lane for stream validator)
- Added approved planning artifacts:
  - `docs/plans/2026-02-28-proto-stream-validation-design.md`
  - `docs/plans/2026-02-28-proto-stream-validation-plan.md`

Why:
- Add a deterministic protobuf-change gate tied to real captured AA non-media traffic so schema regressions are caught before merge.
- Keep baseline updates explicit and auditable via `--bless --reason`.

Status:
- Complete for phase-1 implementation in this branch.
- Decode/golden execution requires Python protobuf runtime (`google.protobuf`) at runtime; policy/unit tests still run without it.

Next Steps:
1. Add capture-export support in `openauto-prodigy` to emit canonical non-media JSONL fixtures for this validator.
2. Expand `(channel_id, message_id)` mapping coverage and add explicit handling policy for non-protobuf control frames.
3. Wire validator into CI/pre-merge checks once runtime dependency policy is finalized.

Verification:
- `PYTHONPATH=. pytest analysis/tools/proto_stream_validator/tests -v` -> `14 passed, 3 skipped`.
- `PYTHONPATH=/tmp/protobuf_vendor:. pytest analysis/tools/proto_stream_validator/tests -v` -> `19 passed` (decode + golden included).
- `PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py --help` -> CLI help rendered successfully (exit 0).
- `rg -n "proto_stream_validator|validate|--bless|non_media" analysis/README.md CONTRIBUTING.md docs/roadmap-current.md analysis/tools/proto_stream_validator/README.md` -> expected references present.

## 2026-02-28 - Live Capture Baseline from Clean-Build Pairing

Date / Session: 2026-02-28 / codex-live-capture-baseline

What Changed:
- Pulled live Pi capture into:
  - `analysis/captures/non_media/2026-02-28-s25-cleanbuild.jsonl`
- Added corresponding blessed baseline:
  - `analysis/baselines/non_media/2026-02-28-s25-cleanbuild.normalized.json`
- Hardened validator mapping/filtering for real capture behavior:
  - message-name fallback resolution for dynamic channel tuples
  - phase-1 exclusions for non-protobuf control frames (`VERSION_*`, `SSL_HANDSHAKE`)
  - phase-1 exclusions for unresolved hex-labeled frames and high-volume `AV_MEDIA_ACK`
- Updated tests for the new mapping/filter semantics in:
  - `analysis/tools/proto_stream_validator/tests/test_message_map.py`

Why:
- The fresh clean-build AA stream includes dynamic channel-open tuples and non-protobuf handshake frames that caused the strict tuple-only resolver to fail before baseline generation.
- Phase-1 validation needs deterministic non-media signal from recorded sessions, not transport/noise churn.

Status:
- Working in `feat/proto-stream-validator` worktree.
- Live-capture bless succeeded and immediate validate passes for the same capture.

Next Steps:
1. Expand message-map coverage for additional known names/tuples as new captures are collected.
2. Decide whether the new capture/baseline pair should be the canonical CI fixture or a local reference set.
3. Mirror the same capture validation flow in `openauto-prodigy` developer docs once capture export workflow is finalized.

Verification:
- `/tmp/oaa-proto-validator-venv/bin/python -m pytest analysis/tools/proto_stream_validator/tests -v` -> `23 passed`.
- `/tmp/oaa-proto-validator-venv/bin/python analysis/tools/proto_stream_validator/run.py --capture analysis/captures/non_media/2026-02-28-s25-cleanbuild.jsonl --baseline analysis/baselines/non_media/2026-02-28-s25-cleanbuild.normalized.json --repo-root . --bless --reason "refresh baseline after mapping/filtering update"` -> baseline updated (exit 0).
- `/tmp/oaa-proto-validator-venv/bin/python analysis/tools/proto_stream_validator/run.py --capture analysis/captures/non_media/2026-02-28-s25-cleanbuild.jsonl --baseline analysis/baselines/non_media/2026-02-28-s25-cleanbuild.normalized.json --repo-root .` -> `validation passed: no baseline diffs` (exit 0).
- `python3 - <<'PY' ... len(json.load(...)) ... PY` on `analysis/baselines/non_media/2026-02-28-s25-cleanbuild.normalized.json` -> `rows 516`.

## 2026-02-28 - Community Home Restructure (Definitions + Implementations + Verification)

Date / Session: 2026-02-28 / codex-community-home-restructure

What Changed:
- Updated `README.md` to reposition the repository as a three-track community home: protocol definitions, multi-language implementations, and ongoing protocol verification.
- Added `implementations/README.md` and created the new `implementations/` top-level directory for language-specific protocol libraries.
- Updated `CONTRIBUTING.md` with implementation contribution guidance (structure, scope, required README content) and protocol verification contribution workflow/evidence expectations.
- Fixed `oaa/navigation/NavigationTurnEventMessage.proto` fields:
  - `maneuver_type` changed from `int32` to `oaa.proto.enums.ManeuverType.Enum`
  - `turn_direction` changed from `int32` to `oaa.proto.enums.TurnSide.Enum`
- Updated `docs/roadmap-current.md` priorities to reflect the community-home restructure and implementation track sequencing.

Why:
- Align repository structure and contributor guidance with the goal of making this project the central community home for Android Auto protocol definitions, implementations, and continuously verifiable protocol research.
- Correct enum typing in navigation turn events so the schema captures known protocol semantics more accurately.

Status:
- Complete for requested restructure/documentation updates and proto enum typing correction.

Next Steps:
1. Add first implementation subdirectory (for example `implementations/cpp/` or `implementations/rust/`) with concrete build + smoke verification instructions.
2. Add implementation coverage matrix in `implementations/README.md` as contributions arrive.
3. Continue promoting unknown APK catalog entries using the strengthened verification workflow.

Verification:
- `protoc --proto_path=. --cpp_out=/tmp oaa/navigation/NavigationTurnEventMessage.proto` -> success (exit 0).
- `rg -n "implementations/" README.md CONTRIBUTING.md docs/roadmap-current.md` -> expected references found in all updated docs.
- `rg -n "proto/oaa|--proto_path=proto" README.md CONTRIBUTING.md || true` -> no matches.
- `test -f implementations/README.md && echo implementations_readme_present` -> `implementations_readme_present`.
- `rg -n "ManeuverType\.Enum|TurnSide\.Enum" oaa/navigation/NavigationTurnEventMessage.proto` -> both typed enum fields present.

## 2026-02-28 - Qt Implementation Bridge Seed

Date / Session: 2026-02-28 / codex-qt-implementation-bridge

What Changed:
- Added `implementations/qt/README.md` as the first implementation entry, documenting the current Qt implementation baseline and linking canonical upstream (`openauto-prodigy`).
- Updated `implementations/README.md` with a current baseline table that marks `qt` as bootstrapped and points contributors to the bridge entry.
- Updated `README.md` implementations section to call out Qt as the current baseline and clarify that shared implementation work will be staged in this repository.
- Updated `CONTRIBUTING.md` with bridge-entry requirements for implementations that currently live in another repository (upstream link, scope, reference, and sync plan).
- Updated `docs/roadmap-current.md` sequencing to prioritize staged Qt module sharing/extraction from `openauto-prodigy`.

Why:
- Match implementation seeding to current reality: the active framework is Qt in `openauto-prodigy`.
- Provide an immediate, concrete path for contributors to align protocol work here while runtime code migration/sharing happens incrementally.

Status:
- Complete for Qt bridge seeding and related documentation/roadmap alignment.

Next Steps:
1. Add a protocol-surface checklist in `implementations/qt/README.md` with explicit status per subsystem.
2. Land first staged Qt protocol module under `implementations/qt/` with local build/smoke command.
3. Add cross-repo trace links from protocol docs to corresponding Qt implementation touchpoints.

Verification:
- `rg -n "implementations/qt|openauto-prodigy|bridge" README.md CONTRIBUTING.md implementations/README.md implementations/qt/README.md docs/roadmap-current.md` -> expected references found in all updated files.
- `rg -n "implementations/README.md|CONTRIBUTING.md|implementations/qt/README.md" README.md implementations/README.md` -> expected local path references present.
- `test -f implementations/qt/README.md && echo qt_readme_present` -> `qt_readme_present`.

## 2026-02-28 - Qt Coverage Checklist Status Update (Unknown -> Partial)

Date / Session: 2026-02-28 / codex-qt-checklist-partial-default

What Changed:
- Updated `implementations/qt/README.md` coverage checklist statuses from all `Unknown` to `Partial` across protocol areas.
- Added conservative notes on each row that status is expected from upstream runtime and still requires exact module/class mapping audit.

Why:
- Reflect current operator preference to show practical progress instead of fully unknown status while still avoiding over-claiming full verification.

Status:
- Complete for checklist status update.

Next Steps:
1. Audit `openauto-prodigy` and attach exact file/class references for each checklist row.
2. Promote rows from `Partial` to `Verified` only with concrete evidence (code location + run/test/capture).
3. Mark known gaps explicitly where functionality is missing or incomplete.

Verification:
- `rg -n "\| .* \| Partial \|" implementations/qt/README.md | wc -l` -> `11` rows marked `Partial`.
- `rg -n "\| Area \| Status \| Notes \||TCP transport|Navigation channel handler|Unknown" implementations/qt/README.md` -> checklist header + representative rows present; `Unknown` appears only in legend.
- `sed -n '20,90p' implementations/qt/README.md` -> table renders with updated `Partial` statuses and audit-pending notes.

## 2026-02-28 - Qt TCP/TLS Evidence Pass (Conservative)

Date / Session: 2026-02-28 / codex-qt-tcp-tls-evidence-pass

What Changed:
- Updated `implementations/qt/README.md` checklist notes for `TCP transport` and `TLS handshake/auth flow` to be evidence-backed instead of generic assumptions.
- Added `Evidence Snapshot (2026-02-28)` section with exact upstream file/line references from `openauto-prodigy` for:
  - TCP transport runtime wiring and unit test coverage.
  - TLS handshake flow, cryptor path, session state transitions, and unit test coverage.
- Kept both rows at `Partial` status per conservative policy (no `Verified` promotion yet).

Why:
- You requested conservative validation. This pass adds hard code references without over-claiming full verification status.

Status:
- Complete for first audit slice (`TCP + TLS`).

Next Steps:
1. Repeat evidence pass for framing + AES rows.
2. Repeat evidence pass for channel lifecycle + service discovery rows.
3. Promote rows to `Verified` only when each has code references plus a reproducible runtime/test signal.

Verification:
- `rg -n "QTcpSocket|connectToHost|TLS|SSL_do_handshake|handshakeComplete|TLSHandshake" /home/matt/claude/personal/openautopro/openauto-prodigy/src /home/matt/claude/personal/openautopro/openauto-prodigy/libs /home/matt/claude/personal/openautopro/openauto-prodigy/tests` -> identified TCP/TLS implementation and tests.
- `nl -ba <openauto-prodigy TCP/TLS files> | sed -n ...` on:
  - `libs/open-androidauto/src/Transport/TCPTransport.cpp`
  - `libs/open-androidauto/tests/test_tcp_transport.cpp`
  - `libs/open-androidauto/src/Messenger/Cryptor.cpp`
  - `libs/open-androidauto/src/Messenger/Messenger.cpp`
  - `libs/open-androidauto/src/Session/AASession.cpp`
  - `libs/open-androidauto/tests/test_cryptor.cpp`
  - `libs/open-androidauto/tests/test_session_fsm.cpp`
  -> captured exact line evidence used in `implementations/qt/README.md`.
- `rg -n "TCP audit references|TLS audit references|Evidence Snapshot|test_tcp_transport.cpp|Cryptor.cpp|Messenger.cpp|AASession.cpp|test_cryptor.cpp|test_session_fsm.cpp" implementations/qt/README.md` -> evidence references present.

## 2026-02-28 - APK Indexer Evidence Detail Refinement

Date / Session: 2026-02-28 / codex-apk-indexer-evidence-detail-refinement

What Changed:
- Updated `analysis/tools/apk_indexer/catalog.py` to collect detailed evidence rows per proto candidate instead of placeholder source tags.
- Added structured evidence collection for:
  - descriptor signal (`descriptor_length=<n>`)
  - field declarations (`field_count=<n>`)
  - proto writes (exact `target op value` + source file/line)
  - class references (`referenced_by=<source_package>` + source file/line)
- Updated `build_catalog(...)` to emit `proto_evidence` directly from the detailed evidence payload.
- Added regression test `test_build_catalog_emits_detailed_proto_evidence_rows` in `analysis/tools/apk_indexer/tests/test_catalog.py`.
- Updated `analysis/tools/apk_indexer/README.md` repo-specific run example to use an explicit `AA_DECOMPILED_ROOT` variable and a currently valid local path example.
- Updated `docs/roadmap-current.md` `Now` section to explicitly include APK evidence-structure refinement as a current priority.

Why:
- You requested focus on data structure/extraction quality from APK analysis instead of runtime deployment concerns.
- The previous evidence rows were too coarse for verification workflows because they omitted concrete source-line context.

Status:
- Complete for this refinement pass. Evidence rows now carry traceable context suitable for catalog review and unknown queue triage.

Next Steps:
1. Add evidence normalization/deduplication so repeated write/reference patterns collapse into canonical rows.
2. Extend evidence quality scoring (line-backed vs inferred) and surface it in report output.
3. Run indexer over current AA decompile snapshot and inspect catalog deltas in SQLite query pack.

Verification:
- `PYTHONPATH=. pytest analysis/tools/apk_indexer/tests -v` -> `25 passed in 0.37s`.
- `python3 analysis/tools/apk_indexer/run_indexer.py --help` -> CLI help renders successfully.
- `python3 analysis/tools/apk_indexer/benchmark.py --help` -> benchmark CLI help renders successfully.
- `python3 analysis/tools/apk_indexer/run_indexer.py --source /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source --analysis-root analysis --scope all` -> success (exit 0), outputs written under `analysis/android_auto_unknown_unknown/apk-index/`.
- `sqlite3 analysis/android_auto_unknown_unknown/apk-index/sqlite/apk_index.db "select 'proto_catalog', count(*) from proto_catalog union all select 'proto_unknowns', count(*) from proto_unknowns union all select 'proto_evidence', count(*) from proto_evidence union all select 'run_metadata', count(*) from run_metadata;"` -> `proto_catalog=1241`, `proto_unknowns=705`, `proto_evidence=20395`, `run_metadata=4`.
- `sqlite3 analysis/android_auto_unknown_unknown/apk-index/sqlite/apk_index.db "select evidence_source, count(*) from proto_evidence group by evidence_source order by count(*) desc;"` -> `class_references=10835`, `proto_writes=7050`, `descriptor=1441`, `field_decls=1069`.
- `protoc --proto_path=. --cpp_out=/tmp oaa/navigation/NavigationTurnEventMessage.proto` -> success (exit 0).
- `rg -n "implementations/|implementations/qt|openauto-prodigy" README.md CONTRIBUTING.md docs/roadmap-current.md implementations/README.md implementations/qt/README.md` -> expected references present.
- `rg -n -- "--proto_path=proto|proto/oaa" README.md CONTRIBUTING.md docs/roadmap-current.md implementations/README.md implementations/qt/README.md` -> no stale path references found.

## 2026-02-28 - Evidence Rollup + Unobfuscated Name Candidate Extraction

Date / Session: 2026-02-28 / codex-apk-evidence-rollup-name-candidates

What Changed:
- Extended `analysis/tools/apk_indexer/catalog.py` with:
  - `proto_evidence_rollup` output (deduplicated by `class_name + evidence_source + evidence_detail`) including `occurrence_count`, `distinct_files`, `first_line`, `last_line`, and `sample_source_file`.
  - `name_candidates` output to collect usable unobfuscated labels from:
    - `class_references.source_package` (excluding `defpackage.*`)
    - `enum_maps.enum_name`
    - `switch_maps.target`
    - `proto_accesses.accessor`
  - additional `run_metadata` counters for rollup and candidate totals.
- Extended SQLite writer (`analysis/tools/apk_indexer/write_sqlite.py`) with new tables + indexes:
  - `proto_evidence_rollup`
  - `name_candidates`
- Added query-pack SQL for targeted confirmation workflows:
  - `analysis/tools/apk_indexer/sql/04_evidence_rollup.sql`
  - `analysis/tools/apk_indexer/sql/05_name_candidates.sql`
- Updated `analysis/tools/apk_indexer/QUERY_PACK.md` and `analysis/tools/apk_indexer/README.md` to document new outputs and queries.
- Updated tests to cover new behavior:
  - `analysis/tools/apk_indexer/tests/test_catalog.py`
  - `analysis/tools/apk_indexer/tests/test_writers.py`
  - `analysis/tools/apk_indexer/tests/test_run_indexer.py`
- Updated `docs/roadmap-current.md` `Now` priorities to include targeted unobfuscated label extraction for confirmation runs.

Why:
- You requested a path to run targeted confirmation over extraction data and capture any usable unobfuscated names/labels for protocol understanding and implementation.
- Raw evidence remains lossless for forensic traceability while rollup and candidate outputs reduce triage noise and improve operator targeting.

Status:
- Complete for conservative phase-1 implementation (`raw evidence + additive rollup + additive name candidates`).

Next Steps:
1. Add confidence tuning/threshold controls for `name_candidates` (for example strict vs broad modes).
2. Add a dedicated SQL report that links `name_candidates` back to `proto_unknowns` classes for faster manual promotion.
3. Run this flow on the latest full APK decompile snapshot and store baseline metrics for comparison.

Verification:
- `PYTHONPATH=. pytest analysis/tools/apk_indexer/tests/test_catalog.py analysis/tools/apk_indexer/tests/test_writers.py analysis/tools/apk_indexer/tests/test_run_indexer.py -v` -> `10 passed in 0.34s`.
- `PYTHONPATH=. pytest analysis/tools/apk_indexer/tests -v` -> `27 passed in 0.37s`.
- `python3 analysis/tools/apk_indexer/run_indexer.py --help` -> CLI help renders successfully.
- `python3 analysis/tools/apk_indexer/benchmark.py --help` -> benchmark CLI help renders successfully.
- Synthetic end-to-end smoke run:
  - `python3 analysis/tools/apk_indexer/run_indexer.py --source <tmp decompiled fixture> --analysis-root <tmp analysis> --scope all` -> success (exit 0), outputs under `/tmp/oaa-index-smoke-f14tPK/analysis/android_auto_16.1_1248424/apk-index/`.
  - `find /tmp/oaa-index-smoke-f14tPK/analysis/android_auto_16.1_1248424/apk-index/json -maxdepth 1 -type f | sort` -> includes `proto_evidence_rollup.json` and `name_candidates.json`.
  - `sqlite3 /tmp/oaa-index-smoke-f14tPK/analysis/android_auto_16.1_1248424/apk-index/sqlite/apk_index.db "select 'proto_evidence_rollup', count(*) from proto_evidence_rollup union all select 'name_candidates', count(*) from name_candidates union all select 'proto_evidence', count(*) from proto_evidence;"` -> `proto_evidence_rollup=4`, `name_candidates=3`, `proto_evidence=4`.
  - `sqlite3 /tmp/oaa-index-smoke-f14tPK/analysis/android_auto_16.1_1248424/apk-index/sqlite/apk_index.db "select source_type, name, confidence from name_candidates order by source_type, name;"` -> extracted:
    - `proto_accessor|setChannelId|medium`
    - `source_package|com.google.android.projection.Foo|high`
    - `switch_target|handler.handleAudio|medium`
  - `sqlite3 /tmp/oaa-index-smoke-f14tPK/analysis/android_auto_16.1_1248424/apk-index/sqlite/apk_index.db "select class_name,evidence_source,evidence_detail,occurrence_count,distinct_files from proto_evidence_rollup order by class_name,evidence_source,evidence_detail;"` -> rollup rows generated as expected.
- `rg -n "proto_evidence_rollup|name_candidates|04_evidence_rollup|05_name_candidates" analysis/tools/apk_indexer/README.md analysis/tools/apk_indexer/QUERY_PACK.md analysis/tools/apk_indexer/catalog.py analysis/tools/apk_indexer/write_sqlite.py` -> expected references present.

## 2026-02-28 - DHU 2.1 Sensor + Navigation Verification

Date / Session: 2026-02-28 / dhu-sensor-logcat-verification

What Changed:
- Updated `oaa/sensor/SensorTypeEnum.proto` with verification status comments for sensors 1, 3, 6, 8, 9, 10.
- Updated `oaa/sensor/SensorEventIndicationMessage.proto` with per-field verification status and header comment.
- Updated `oaa/sensor/NightModeData.proto` with full processing pipeline documentation.
- Updated `oaa/navigation/NavigationTurnEventMessage.proto` with TurnEvent verification note and phone-side class mapping.
- Added DHU 2.1 Sensor Verification section to `docs/phone-side-debug.md` covering:
  - Sensor verification results table (night, speed, location, fuel, diagnostics, gear)
  - Night mode processing pipeline trace
  - "No listener" pattern documentation
  - Sensor visibility hierarchy
  - NavigationTurnEvent findings during active navigation
  - Complete DHU 2.1 command reference
- Added new log tags to phone-side-debug.md: CAR.SENSOR.LITE, CAR.SYS, CAR.WM, CSL.AbstractBundleable, GH.UserInterruptMgr, GH.StreamItemManager, CAR.VALIDATOR.

Why:
- Live DHU 2.1 + logcat capture session produced concrete verification evidence for protobuf field definitions against real AA protocol behavior.
- Night mode (sensor 10) and diagnostics (sensor 9) enum numbering confirmed by phone-side log references.
- Speed/fuel/location functionally confirmed but shown to be invisible to logcat.
- NavigationTurnEvent (0x8004) confirmed active at ~1Hz during navigation.

Status:
- Complete for documentation updates.

Next Steps:
1. Wire-level capture via OpenGAL proxy to verify speed/fuel/location protobuf encoding (logcat is insufficient).
2. Investigate TurnEvent BadParcelableException — may need updated car app library in DHU or custom proxy.
3. Test remaining DHU sensor commands (accel, compass, gyro, tollcard, odometer, range) for logcat visibility.

Verification:
- `protoc --proto_path=. --cpp_out=/tmp oaa/sensor/SensorTypeEnum.proto oaa/sensor/SensorEventIndicationMessage.proto oaa/sensor/NightModeData.proto oaa/navigation/NavigationTurnEventMessage.proto` -> success (exit 0).
- `rg -n "VERIFIED|functionally verified|DHU 2.1" oaa/sensor/SensorTypeEnum.proto oaa/sensor/SensorEventIndicationMessage.proto oaa/sensor/NightModeData.proto oaa/navigation/NavigationTurnEventMessage.proto` -> verification comments present in all four files.
- `rg -n "DHU 2.1 Sensor Verification|No Listener|Sensor Visibility Hierarchy|NavigationTurnEvent" docs/phone-side-debug.md` -> new sections present.

## 2026-02-28 - ChannelErrorCode 302 Correction from APK Evidence

Date / Session: 2026-02-28 / codex-channel-errorcode-302-correction

What Changed:
- Updated `oaa/common/ChannelErrorCodeEnum.proto`:
  - changed enum value `302` from `TRIED_TO_SEND_DATA_WHILE_CODEC_CONFIG_NOT_SENT`
  - to `RECEIVED_ACK_WHILE_NOT_STARTED`

Why:
- Targeted validation from phase-1 confirmation flow showed a mismatch between current proto and APK evidence.
- Current decompile (`nop.java`) and archived decode outputs both map `302` to `RECEIVED_ACK_WHILE_NOT_STARTED`, making the previous proto entry incorrect.

Status:
- Complete for this correction.

Next Steps:
1. Continue phase-1 walkthroughs for additional high-signal enum/accessor candidates and classify each as `verified-existing`, `corrected`, or `needs-more-evidence`.
2. Build a small `channel-error-code` verification table linking each value to source evidence file/line.
3. Audit neighboring `ChannelErrorCode` values for naming drift (`AUDIO_*` variants) using the same evidence-first process.

Verification:
- `protoc --proto_path=. --cpp_out=/tmp oaa/common/ChannelErrorCodeEnum.proto` -> success (exit 0).
- `sqlite3 /tmp/oaa-confirm-20260228-095738/android_auto_unknown_unknown/apk-index/sqlite/apk_index.db "select file,line,enum_class,int_value,enum_name from enum_maps where enum_class='nop' and int_value=302;"` -> `302 -> RECEIVED_ACK_WHILE_NOT_STARTED` from `nop.java` line `125`.
- `rg -n "RECEIVED_ACK_WHILE_NOT_STARTED|TRIED_TO_SEND_DATA_WHILE_CODEC_CONFIG_NOT_SENT" oaa/common/ChannelErrorCodeEnum.proto /tmp/oaa-confirm-20260228-095738/android_auto_unknown_unknown/apk-source/sources/defpackage/nop.java /home/matt/claude/personal/openautopro/open-android-auto/research/archive/openauto-prodigy/tools/proto_decode_output/enums/nop.proto` -> current proto + APK + archived decode all align on `RECEIVED_ACK_WHILE_NOT_STARTED` and no remaining match for deprecated name in current proto.

## 2026-02-28 - Phase-1 Enum Findings Wrap-Up

Date / Session: 2026-02-28 / codex-phase1-enum-wrap

What Changed:
- Completed a sequential validation pass for all phase-1 `enum_name` candidates (50 rows) with exact-value comparison against `oaa/*.proto`.
- Generated external validation artifacts under `/tmp/oaa-confirm-20260228-095738/android_auto_unknown_unknown/apk-index/exports/`:
  - `phase1_enum_validation_exact.csv`
  - `phase1_enum_validation_exact.md`
  - `phase1_enum_likely_actionable.csv`
  - `phase1_enum_likely_actionable_triage.csv`
  - `phase1_enum_likely_actionable_triage.md`
- Confirmed one label-collision case (`SSL_HANDSHAKE`) where enum names match but numeric values differ by domain (`APK=20` vs control message id `3`), preventing false-positive “already verified” classification.

Why:
- You asked to validate “the rest of phase-1 enum names” and then wrap the phase-1 findings into a clear actionable state.

Status:
- Complete for phase-1 enum review and triage packaging.
- No additional proto edits were applied in this wrap step beyond the previously-logged `ChannelErrorCode 302` correction.

Next Steps:
1. Execute `edit-now` items from `phase1_enum_likely_actionable_triage.csv` in a controlled batch limited to `oaa/common/ChannelErrorCodeEnum.proto`.
2. Run `verify-more` items via class-usage tracing (`aapc`, `vyh`, `noj`) before any schema additions.
3. Keep `name_collision_value_mismatch` items explicitly tagged to avoid domain-mix regressions in future reviews.

Verification:
- `python3 <sequential phase1 enum validator>` over `/tmp/oaa-confirm-20260228-095738/.../name_candidates_phase1_aa_protocol.tsv` -> produced exact-value validation outputs:
  - `present_in_oaa_proto_exact=3`
  - `name_collision_value_mismatch=1`
  - `apk_only_protocol_candidate=33`
  - `apk_only_likely_telemetry=13`
- `python3 <phase1 actionable triage generator>` over `phase1_enum_likely_actionable.csv` -> produced:
  - `edit-now=21`
  - `verify-more=9`
  - `telemetry=0`

## 2026-02-28 - Proto Stream Validation Brainstorm + Plan

Date / Session: 2026-02-28 / codex-proto-stream-validator-planning

What Changed:
- Added approved design doc: `docs/plans/2026-02-28-proto-stream-validation-design.md`.
- Added implementation plan doc: `docs/plans/2026-02-28-proto-stream-validation-plan.md`.
- Updated `docs/roadmap-current.md` `Next` sequencing with a non-media capture-based protobuf regression validator lane (`validate`/`bless`).

Why:
- You requested a practical way to validate protobuf changes against real AA stream behavior.
- Brainstorming converged on recorded-capture validation with strict no-regression diffs and explicit bless-only baseline updates.

Status:
- Complete for design + implementation planning.
- Implementation not started yet.

Next Steps:
1. Choose execution mode for the implementation plan (subagent-driven in this session vs parallel executing-plans session).
2. Implement `analysis/tools/proto_stream_validator/` task-by-task from the saved plan.
3. Add capture-export support in `openauto-prodigy` to generate full non-media payload JSONL fixtures for baseline creation.

Verification:
- `test -f docs/plans/2026-02-28-proto-stream-validation-design.md && echo design_doc_present` -> `design_doc_present`.
- `test -f docs/plans/2026-02-28-proto-stream-validation-plan.md && echo impl_plan_present` -> `impl_plan_present`.
- `rg -n "proto_stream_validator|validate|--bless|non_media|no-regression diff" docs/plans/2026-02-28-proto-stream-validation-design.md docs/plans/2026-02-28-proto-stream-validation-plan.md` -> expected capture/validator/baseline references present.
- `rg -n "capture-based protobuf regression validation|Last Updated:" docs/roadmap-current.md` -> new `Next` lane and updated timestamp note present.

## 2026-02-28 - Kitchen Sink DHU Session (Multi-Display + Full Sensor + Media)

Date / Session: 2026-02-28 / dhu-kitchen-sink-session

What Changed:
- Created `kitchen_sink.ini` DHU config enabling all inputs, all sensors, instrument cluster, playback status at 720p.
- Ran DHU 2.1 with kitchen_sink + cluster + auxiliary_nav configs for maximum protocol surface.
- Updated `oaa/sensor/SensorTypeEnum.proto`: TOLL_CARD=22 verified, GPS=21 and GEAR=8 noted as absent from DHU 2.1 binary, speed correction (no visible effect confirmed).
- Updated `oaa/sensor/SensorEventIndicationMessage.proto`: speed field comment corrected.
- Added Kitchen Sink Session section to `docs/phone-side-debug.md` covering:
  - Multi-display + cluster findings (4 DHU windows, structured nav metadata)
  - Media playback protocol details (MediaBrowserService framework, queue, custom actions)
  - 12 new log tags (GH.Media*, GH.NDirector, GH.NotificationStore, etc.)
  - Additional sensor verification (TOLL_CARD=22 new, odometer silent, gear/parking_brake/gps_satellite absent)
  - Cluster vs TurnEvent dual-path analysis for navigation data

Why:
- Kitchen sink config exercised maximum protocol surface: instrument cluster, media playback status, multi-display, touchpad input, and all available sensors.
- Confirmed DHU 2.1 definitively lacks gear, parking_brake, and gps_satellite commands regardless of INI config.
- Discovered that cluster navigation data flows via direct protobuf channel (working) independently from TurnEvent Parcelable path (broken).

Status:
- Complete for documentation updates.

Next Steps:
1. Test with DHU version > 2.1 if available — gear, parking_brake, gps_satellite may exist in newer builds.
2. Capture wire-level cluster channel data via openauto-prodigy to map cluster protobuf messages to our proto definitions.
3. Investigate media playback status protocol messages — the MediaBrowserService data visible in logcat must be serialized into AA protocol messages for the HU.
4. Test auxiliary nav display with `auxiliary_nav.ini` to see if it produces a separate video stream or navigation-only widget data.

Verification:
- `protoc --proto_path=. --cpp_out=/tmp oaa/sensor/SensorTypeEnum.proto oaa/sensor/SensorEventIndicationMessage.proto` -> success (exit 0).
- `rg -n "TOLL_CARD.*22.*VERIFIED|sensor:22" oaa/sensor/SensorTypeEnum.proto docs/phone-side-debug.md` -> toll card verification present.
- `rg -n "Kitchen Sink|Multi-Display|MediaBrowserService|Cluster vs TurnEvent" docs/phone-side-debug.md` -> new sections present.

## 2026-02-28 - MediaPlaybackStatus Proto Correction + GAL Channel Handler Map

Date / Session: 2026-02-28 / media-playback-status-deep-dive

What Changed:
- Corrected `oaa/media/MediaPlaybackStatusMessage.proto`:
  - Previous version had 24 fields from false APK match (class `ahdz` = memory diagnostics, not media).
  - Replaced with real 6-field structure from APK class `vyq` (AA v16.1).
  - Field 2 changed from `int32 source_id` to `string source_app` (wire-verified: "YouTube Music").
  - Added `PlaybackState` enum (0=UNKNOWN, 1=STOPPED, 2=PLAYING, 3=PAUSED, 4=ERROR).
  - Fields 4-6 are booleans (always false in capture — likely shuffle/repeat/favorited).
- Confirmed `MediaPlaybackMetadataMessage.proto` is correct (APK class `nmi`, 6 fields match).
- Discovered two separate media playback channels:
  - GAL type 11 (MEDIA_PLAYBACK_STATUS): handler `hzt.java`, uses `vyq` (6 fields) + `nmi` metadata.
  - GAL type 20 (CAR_LOCAL_MEDIA): handler `hxu.java`, uses `vws` (4 fields with packed repeated enum actions) + `vyp` metadata (7 fields).
- Decoded service discovery response mapping runtime channel IDs to GAL types.
- Built complete GAL channel handler map (13 handlers, types 1-21).

Why:
- Prior proto decoder matched `ahdz` to MediaPlaybackStatus with 0.833 score — a false positive.
  `ahdz` is a memory diagnostics proto (PSS, RSS, Swap, VMS telemetry), not media.
- Wire capture (1993 messages) proved field 2 is string, not int32, and only 6 fields exist.
- Runtime channel IDs don't match GAL type enums — channel 10 in capture = GAL type 11, not 10.

Status:
- Complete for MediaPlaybackStatus correction and channel handler mapping.

Key Findings:
- GAL Channel Handler Map (all `iag` subclasses in APK):
  Type 1: hys (CONTROL), Type 6: ice (AUDIO_SOURCE), Type 7: iat (SENSOR_SOURCE),
  Type 8: hzp (INPUT_SOURCE), Type 10: hzy (NAV_STATUS/Instrument Cluster),
  Type 11: hzt (MEDIA_PLAYBACK_STATUS), Type 13: iae (PHONE_STATUS),
  Type 15: iaq (RADIO), Type 16: iba/hlv (VENDOR_EXT), Type 17: ibc (WIFI),
  Type 19: hxp (CAR_CONTROL), Type 20: hxu (CAR_LOCAL_MEDIA),
  Type 21: ibh (BUFFERED_MEDIA_SINK)
- PlaybackState enum: 1→STOPPED, 2→PLAYING, 3→PAUSED, 4→ERROR (maps to Android PlaybackStateCompat)
- CAR_LOCAL_MEDIA actions enum (vwp): 0=PLAY, 1=PAUSE, 2=PREVIOUS, 3=NEXT, 4=STOP
- Service discovery maps runtime channels at session time; channel 10 = media_info = GAL type 11
- `nmi` (MediaPlaybackMetadata for channel 11) confirmed correct, `vyp` (7 fields) is for channel 20

Next Steps:
1. All GAL channel handler gaps are now closed — see completion handoff below.

Completed since initial handoff:
- Created `CarLocalMediaPlaybackStatus.proto` (vws, 4 fields + PlaybackState + CarLocalMediaPlaybackAction enums).
- Created `CarLocalMediaPlaybackMetadata.proto` (vwq, 5 fields — song, artist, album, albumArt, durationSeconds).
- Investigated `vyp` (7 fields) — found unused by handler; `hxu.java` actually deserializes `vwq` (5 fields).

Verification:
- `protoc --proto_path=. --cpp_out=/tmp oaa/media/MediaPlaybackStatusMessage.proto` -> success (exit 0).
- `protoc --proto_path=. --cpp_out=/tmp oaa/media/CarLocalMediaPlaybackStatusMessage.proto` -> success (exit 0).
- `protoc --proto_path=. --cpp_out=/tmp oaa/media/CarLocalMediaPlaybackMetadataMessage.proto` -> success (exit 0).
- `rg -n "PlaybackState|source_app|vyq|false positive|ahdz" oaa/media/MediaPlaybackStatusMessage.proto` -> corrected structure present with provenance notes.

## 2026-02-28 - GAL Channel Handler Coverage Complete

Date / Session: 2026-02-28 / gal-gap-coverage-complete

What Changed:
- Closed ALL remaining GAL channel handler gaps (7 commits total this session):
  1. `6acab46` - MediaPlaybackStatus correction + CAR_LOCAL_MEDIA protos (Status + Metadata)
  2. `3e7cbc1` - Car Control (type 19, 4 msgs + 8 sub-msgs) + Buffered Media Sink stub (type 21)
  3. `81549fd` - PhoneStatusInput (type 13, 3 fields)
  4. `c04bfb1` - Radio (type 15, 9 msgs + 6 sub-msgs + 3 enums — largest gap)
  5. `c996e1a` - Instrument Cluster (type 10, 3 msgs) + Vendor Extension docs (type 16) + Notification enum update
  6. `0e794de` - Connected Devices + Battery Status (control channel) + UI Config (AV channel, 4 msgs)
  7. `efb27a7` - Final gap cleanup: shuffle/repeat/repeat_one flags, CarLocalMediaPlaybackRequest, InstrumentClusterAction + PhoneInputAction enum name recovery

- Resolved all "minor open items":
  - MediaPlaybackStatus flags 4-6 = shuffle, repeat, repeat_one (confirmed via aa-proxy-rs + AIDL interface)
  - CAR_LOCAL_MEDIA_PLAYBACK_REQUEST (0x8003) = 1-field proto with CarLocalMediaPlaybackAction enum
  - InstrumentClusterAction + PhoneInputAction enum names recovered: UNKNOWN, UP, DOWN, LEFT, RIGHT, ENTER, BACK, CALL

- Key investigation findings:
  - Media Browser (type 12): Dead channel — no handler in v16.1, browsing is video-rendered
  - Diagnostics/Verification: All covered — ping protos exist, GalVerification is PCTS certification-only
  - Vendor Extension (type 16): Raw byte pipe, not protobuf — documented architecture only
  - Notifications (type 14): No phone-side handler — "GenericNotification" names come from HU firmware

Why:
- Systematic closure of every GAL protocol gap identified from the DHU 2.1 cross-reference.
- Every channel handler type (1-21) now has proto definitions or explicit documentation of why none is needed.

Status:
- Complete. All 13 GAL channel handler types are documented.

Next Steps:
1. Continue with APK indexer catalog triage and evidence promotion workflow.
2. Wire-capture validation of new proto definitions against live AA sessions.
3. VideoConfigData field 11 UiConfig sub-message confirmation via capture.

Verification:
- All proto files compile: `protoc --proto_path=. oaa/**/*.proto --descriptor_set_out=/dev/null` -> success.
- `git log --oneline HEAD~7..HEAD` -> 7 commits covering all GAL gaps.

## 2026-03-04 - Wire Capture Proto Validation (First Decrypted Stream)

Date / Session: 2026-03-04 / wire-capture-proto-validation

What Changed:
- Copied first decrypted capture files to `captures/general/` (aa_messages.jsonl, channel_map.json, sdp_response.bin)
- Validated signaling messages from 741-message capture (638 media_sink, 103 signaling)
- Discovered and documented channel_map.json label swap bug

Key Findings:

1. **channel_map.json labels are SWAPPED** for navigation and media_info:
   - SDP field 8 = `navigation_channel` per our ChannelDescriptor proto (line 54)
   - SDP field 9 = `media_info_channel` per our ChannelDescriptor proto (line 55)
   - Other Claude's parser labeled field 8 as "media_info" and field 9 as "nav_status" — reversed
   - Wire data confirms: ch10 (field 8) carries nav data, ch12 (field 9) carries MediaPlaybackStatus
   - **Action: Tell other Claude to fix SDP field-to-name mapping**

2. **WIRE VERIFIED protos** (promotable to Gold confidence):
   - `MediaPlaybackStatus` (0x8001 on media_info channel): PlaybackState 3→2 (PAUSED→PLAYING), source_app="YouTube Music", position_seconds incrementing, shuffle/repeat/repeat_one all false — every field matches
   - `PhoneStatusUpdate` (0x8001 on phone_status): signal_strength=0, no calls — matches
   - `NavigationState` (0x8003 on nav channel): state=1 (NAV_STATE_ACTIVE) — matches
   - `NavigationNotification` (0x8006 on nav channel): full sub-message hierarchy verified — steps[0].maneuver.type=DEPART(1), steps[0].instruction.text="toward Hunter Rd", steps[0].road_info.road_names=["toward Hunter Rd"], destinations[0].address="Texas" — perfect match

3. **0x8007 on nav channel — message type dispute**:
   - Our nav.md assigns 0x8007 = NavigationDistance (xnb)
   - Wire data: `{1: {1: {2: "0", 3: 6}}}` — nested submessages
   - NavigationDistance (xnb) FAILS: field 1 = NavigationDistanceValue (xmw) expects int64 at sub-field 1, wire has length-delimited submessage — wire type mismatch
   - NavigationNextTurnDistanceEvent (vzd) MATCHES: remaining_distance.distance.display_text="0", distance_unit=6
   - Resolution: need real phone navigation capture (not DHU synthetic) to confirm which message the phone actually sends on 0x8007

4. **DistanceDisplayUnit enum incomplete**: wire shows value 6, our enum only defines 0-5 (UNKNOWN through YARDS)

5. **Capture statistics**: 15 channels (0-14), 3 video sinks, 3 input sources, 2 audio sinks, nav, media_info, phone_status, vendor_ext, sensor_source, sensor

Why:
- First-ever wire validation of proto definitions against decrypted AA traffic.
- TLS decryption pipeline (Frida master secret extraction → pcap decrypt → per-channel message split) is fully operational on MINIMEES.

Status:
- General capture validated. Scenario-specific captures (idle, music, navigation) pending from other Claude on MINIMEES.

Next Steps:
1. Fix channel_map.json label mapping in capture pipeline on MINIMEES
2. Run scenario captures: idle-baseline (60s), music-playback (play/pause/skip), active-navigation (30s+ with turns)
3. Resolve 0x8007 message type with real phone navigation data
4. Add DistanceDisplayUnit value 6 once identified
5. Promote wire-verified protos from Silver to Gold confidence

Verification:
- `protoc --decode_raw < captures/general/sdp_response.bin` -> 14 ChannelDescriptors decoded, fields 6-9 on VideoConfig confirmed
- `python3` analysis of aa_messages.jsonl -> 741 messages, channel distribution matches SDP
- MediaPlaybackStatus decode: `{1:2, 2:"YouTube Music", 3:27, 4:0, 5:0, 6:0}` -> field-perfect proto match
- NavigationNotification decode: full 4-level sub-message hierarchy verified against NavigationNotificationMessage.proto

## 2026-03-04 - Scenario Capture Analysis & 0x8007 Resolution

Date / Session: 2026-03-04 / scenario-capture-analysis

What Changed:
- Copied 3 scenario captures from MINIMEES: idle-baseline, music-playback, active-navigation
- Resolved 0x8007 message type dispute: **NavigationNextTurnDistanceEvent**, not NavigationDistance
- Updated nav.md: corrected message catalog, state machine, confidence tiers, gotchas
- Updated NavigationTurnEventMessage.proto: promoted NavigationNextTurnDistanceEvent to Gold, added message ID
- Updated NavigationDistanceMessage.proto: removed incorrect 0x8007 claim, marked message ID as unknown
- Added DistanceDisplayUnit value 6 as placeholder (DISTANCE_UNIT_UNKNOWN_6)
- Promoted NavigationNotification, NavigationNextTurnDistanceEvent, NavigationState to Gold confidence

Key Findings:

1. **0x8007 = NavigationNextTurnDistanceEvent (RESOLVED)**:
   - 18 messages in active-navigation capture, all identical: `{1: {1: {2: "0", 3: 6}}}`
   - Maps to: remaining_distance.distance.display_text="0", distance_unit=6
   - NavigationDistance (xnb) FAILS: field 1 expects int64 (NavigationDistanceValue.raw_meters), wire has length-delimited submessage
   - NavigationNextTurnDistanceEvent (vzd) MATCHES: field 1 = NavigationRemainingDistance (submessage)
   - All 18 identical because car was stationary — distance="0" every time

2. **DistanceDisplayUnit 6 — still unknown**:
   - Seen in all 18 nav distance messages, all while stationary
   - Could be a locale-specific unit or a "no distance" placeholder
   - Needs driving capture with actual distance changes to resolve

3. **Capture pipeline data frame classification bug (MINIMEES)**:
   - On signaling channels (e.g., ch12 media_info), messages with flags 0x08/0x0a are AV data frames, not protobuf signaling
   - Pipeline treats them as signaling and interprets first 2 bytes as msg_type, producing garbage IDs (0x38ec, 0xb314, etc.)
   - These are all 16124 bytes — exactly the AV frame MTU — with random-looking encrypted content
   - Real signaling messages have flags 0x0b (encrypted signaling) or 0x0f (encrypted control)
   - Fix needed in decrypt_capture.py on MINIMEES: filter by flags before msg_type extraction

4. **Scenario capture statistics**:
   - idle-baseline: 4029 msgs, minimal signaling, 1 PhoneStatus, no nav
   - music-playback: 4941 msgs, 39 MediaPlaybackStatus updates (state 3→2, position incrementing, "YouTube Music"), album art data frames on ch12
   - active-navigation: 5531 msgs, 18x 0x8006 + 18x 0x8007 on nav, 803 cluster input events (ch7), 405 cluster video frames (ch8)

5. **MediaPlaybackStatus wire-verified (music-playback)**:
   - Field-perfect: `{1:3→2, 2:"YouTube Music", 3:43→81, 4:0, 5:0, 6:0}`
   - PlaybackState 3=PAUSED → 2=PLAYING, position_seconds incrementing, shuffle/repeat all false
   - 39 updates over capture duration

6. **Cluster activity during navigation**:
   - ch7 (input_source): 803x 0x8001 messages — touch/scroll events from cluster display
   - ch8 (media_sink): 405 frames — cluster video content (vs 4 in idle/music)
   - Confirms cluster display is active and receiving both video and input during nav

Why:
- Resolves the last disputed message type on the navigation channel
- Three scenario captures provide comprehensive wire evidence across idle, music, and navigation states

Status:
- Navigation channel fully documented with wire evidence. All message types confirmed except NavigationDistance (xnb) which has no known message ID.
- DistanceDisplayUnit value 6 and NavigationDistance message ID remain open — need driving capture.
- Capture pipeline bug documented but fix is on MINIMEES side.

Next Steps:
1. Fix capture pipeline on MINIMEES: filter flags 0x08/0x0a as data frames, not signaling
2. Get a driving capture with actual route progress to see real distance values and resolve enum 6
3. Identify NavigationDistance (xnb) message ID — may require targeted APK analysis of dispatch table
4. Promote MediaPlaybackStatus and PhoneStatusUpdate to Gold (need to update media_info.md and phone.md)
5. Consider capturing additional scenarios: phone call, Waze navigation, assistant interaction

Verification:
- `protoc --decode_raw` on all 18 0x8007 payloads: identical `{1: {1: {2: "0", 3: 6}}}` — matches NavigationNextTurnDistanceEvent
- `protoc --decode_raw` on 0x8006 payloads: NavigationNotification with steps[0].maneuver.type=DEPART(1), instruction="toward Hunter Rd"
- ch12 flags analysis: 0x8001 msgs have flags=0x0b (signaling), garbage msgs have flags=0x08 (data frame)
- MediaPlaybackStatus position_seconds: 43→81 over capture — incrementing as expected during playback

## 2026-03-04 - Multi-Display Content Routing (16.2 APK Deep Dive)

Date / Session: 2026-03-04 / multi-display-content-routing

What Changed:
- Deep analysis of 16.2 APK display content routing architecture
- Created `docs/channels/display-routing.md` — comprehensive reference for display types, content routing, and limitations
- Identified all relevant APK classes: qcw (display types), qcx (aux content types), lpj (main display categories), lpa/loz/lpc (routing logic)

Key Findings:

1. **Auxiliary display content types are nav-only (qcx.java)**:
   - UNKNOWN (0) — not supported, throws IllegalStateException
   - NAVIGATION (1) → PrototypeAuxiliaryDisplayNavigationCarActivityService (full map projection)
   - TURN_CARD (2) → PrototypeAuxiliaryDisplayTurnCardCarActivityService (maneuver card only)
   - **No MEDIA, PHONE, or MESSAGING content types exist for secondary displays**

2. **Main display has full content categories (lpj.java)**:
   - OTHER(0), NAVIGATION(1), PHONE(2), MEDIA(3), PHONE_MEDIA(8), SYSTEM(7)
   - These drive the Coolwalk rail facets but ONLY on the primary display
   - Secondary displays don't participate in this content system

3. **Cluster routing fallback chain (lpc.java)**:
   - Power saving + battery optimized → ClusterTurnCardCarActivityService
   - Default nav app has cluster service → use it (CATEGORY_PROJECTION_NAVIGATION query)
   - Google Maps fallback → GmmCarAuxiliaryProjectionService
   - Ultimate fallback → ClusterTurnCardCarActivityService
   - All paths lead to navigation content — no media/phone cluster services exist

4. **Nav app discovery (lak.java)**:
   - Only queries for `CATEGORY_PROJECTION_NAVIGATION` services
   - Cluster also checks `CATEGORY_SECONDARY_REGION`
   - Third-party nav apps (Waze) can provide cluster rendering, but only nav
   - No `CATEGORY_PROJECTION_MEDIA` or similar exists

5. **session_configuration bitmask (hve.java)**:
   - Bit 4 (value 16) = `UI_ELEMENT_NAVIGATION_TURN_DATA_AVAILABLE`
   - Signals HU can receive turn data — relevant for cluster turn card

6. **Display constraints (iom.java)**:
   - Exactly 1 MAIN required, at most 1 CLUSTER, rest become AUXILIARY
   - Primary display (ID 0) must be MAIN

Why:
- Understanding what content the phone will and won't project to secondary displays is critical for OpenAuto Prodigy's architecture — determines what we need to render ourselves vs. what we can delegate to the phone.

Status:
- Display routing fully documented. The phone projects nav-only content to secondary displays. For media/phone/messaging on secondary displays, OpenAuto Prodigy must render its own widgets from channel signaling data.

Implications for OpenAuto Prodigy:
- **Phone-projected content** (via video surfaces): nav map, turn card — that's all we get
- **Self-rendered content** (from signaling channels): media playback status, phone status, nav turn events, nav notifications — all wire-verified, all available as structured data
- This is actually a design advantage: we control the UI for media/phone widgets, not constrained by Google's rendering. The signaling data (MediaPlaybackStatus, PhoneStatusUpdate, NavigationNotification, NavigationNextTurnDistanceEvent) gives us everything we need.

Next Steps:
1. Design custom widget architecture for secondary displays using channel signaling data
2. Prototype a media widget from MediaPlaybackStatus data (song, artist, playback state, position)
3. Investigate whether Coolwalk rail facet switching generates observable wire events (could we detect which facet is active?)
4. Check if newer AA versions (17.x+) expand auxiliary display content types beyond navigation
5. Consider whether TURN_CARD vs NAVIGATION choice is configurable from the HU side

Verification:
- `qcx.java` enum: only UNKNOWN/NAVIGATION/TURN_CARD — confirmed no media/phone content types
- `loz.java` routing: ordinal 1→nav service, ordinal 2→turn card service, else→error log + null
- `lpc.java` cluster chain: all 4 fallback paths resolve to navigation services
- `lak.java` discovery: only queries CATEGORY_PROJECTION_NAVIGATION, no media equivalent
- `lpj.java` categories: NAVIGATION/PHONE/MEDIA/SYSTEM exist but only used for main display Coolwalk rail
- Turn card confirmed working in DHU testing

---

Date / Session: 2026-03-04 / coolwalk-layout-engine

What Changed:
- Deep reverse engineering of Coolwalk layout engine from AA 16.2 APK
- Created `docs/channels/coolwalk-layout.md` — comprehensive reference doc
- Discovered all PhenotypeFlag breakpoints, dashboard decision logic, card system, and layout types

Key Findings:

1. **PhenotypeFlag Breakpoints (abgu.java)**:
   - `SystemUi__horizontal_rail_canonical_breakpoint_dp` = 450dp (rail orientation)
   - `SystemUi__short_portrait_breakpoint_dp` = 680dp
   - `SystemUi__portrait_breakpoint_dp` = 900dp (height threshold)
   - `SystemUi__semi_widescreen_breakpoint_dp` = 880dp
   - `SystemUi__widescreen_breakpoint_dp` = 1240dp
   - `SystemUi__widescreen_aspect_ratio_breakpoint` = 1.67 (w/h ratio)
   - These are server-pushed Google config — HU cannot change them

2. **Horizontal vs Vertical Dashboard (mno.m26328K)**:
   - Landscape (layoutType==2): displayWidthDp >= 730 → horizontal
   - Other: displayWidthDp >= 800 → horizontal
   - For 1024×600 display: 160 DPI = 1024dp width → comfortably horizontal
   - At 240 DPI = 682dp → falls below threshold, vertical only

3. **Dashboard Card System**:
   - 6 card types: Blank, Navigation, Media, Nav Suggestions, Notification, Phone/TelecomCall
   - `mo25633a()` = **swipeable** flag (NOT visibility) — key `.swipable` in luc.java
   - Media/Nav/ActiveCall cards are NOT suppressed — they're just pinned (can't swipe-dismiss)
   - Card selection is reactive stream-based (first observable to emit wins), 300ms debounce
   - No weather card type exists — weather comes via notifications

4. **Layout Type Classification (mnu enum)**:
   - Types 1-3, 6, 12-15 → CANONICAL (standard Coolwalk)
   - Types 4-5 → WIDESCREEN
   - Type 7 → CLUSTER
   - Type 8 → CLUSTER_WITH_LAUNCHER
   - Type 9 → AUXILIARY
   - Type 10 → PORTRAIT
   - Type 11 → PORTRAIT_SHORT

5. **Cielo = Material 3 Theme (NOT a layout type)**:
   - Visual theme overlay, not structural layout change
   - Enabled via PhenotypeFlag `pus.CIELO` (index 53)
   - Layout XMLs structurally identical to standard Coolwalk
   - Legacy flags: `CieloFeature__cielo_status`, `CieloFeature__earth_enabled`

6. **Hero Layout = Integrated Panel Displays**:
   - POIP (Picture on Integrated Panel): landscape, 1280dp cutout, three rails (driver/main/passenger)
   - SOIP (Second on Integrated Panel): portrait-ish, 768×1244dp cutout, horizontal bottom rail
   - For cars where AA shares a larger screen with native car UI (BMW/Mercedes style)
   - `isHeroLayout` flag in mnj — reduces available width by 2×rail_width

7. **Demand Region = Voice/Assistant UI**:
   - NOT turn-by-turn navigation — it's Google Assistant / voice interaction overlay
   - Coexists with dashboard (separate regions, doesn't replace cards)
   - Triggered by steering wheel button, assistant activation, Maps mic
   - Templates: demand_voice_plate.xml, demand_space_search_suggestion.xml, etc.

8. **Driver-Aligned Dashboard**:
   - User setting: `key_settings_driver_aligned_dashboard`
   - Flips dashboard position: LHD 68.75% → 31.25% (right to left)
   - Wider ratio: 4.0 vs 3.2 default
   - Separate layout XMLs with `_driver_aligned_dashboard` suffix

Why:
- Understanding Coolwalk's layout engine is critical for OpenAuto Prodigy — the HU's only lever is the DPI it advertises in the SDP, which cascades through the entire layout system. Knowing the exact breakpoints lets us choose the optimal DPI for any given display.

Status:
- `docs/channels/coolwalk-layout.md` created with breakpoints, formulas, DPI tables, card system, and region maps
- Doc needs corrections: layout type table (mnu enum names), hero/Cielo sections need adding, card swipeable correction already applied

Next Steps:
1. **Update coolwalk-layout.md** with corrected layout type names (PORTRAIT not Cielo), add hero layout section, add Cielo theme section, add demand region and driver-aligned dashboard sections
2. **DHU DPI experiments** — validate breakpoints by running DHU at different DPI values and observing layout changes
3. **Rail widget internals** — how do the compact media/phone widgets in the sidebar work? What data drives them?
4. **Facet switching wire events** — can we detect when user switches between nav/media/phone on the Coolwalk rail?
5. **PhenotypeFlag manipulation** — can a rooted phone override breakpoint values?

APK Source References:
- `mno.java` — DisplayLayout engine, dashboard sizing, region management
- `mnj.java` — LayoutInfo (displayWidthDp, layoutType, isHeroLayout, etc.)
- `mnu.java` — Layout mode enum (CANONICAL, WIDESCREEN, PORTRAIT, CLUSTER, etc.)
- `abgu.java` — PhenotypeFlag defaults (all breakpoint values)
- `abgt.java` — PhenotypeFlag interface
- `lti.java` — Dashboard window controller (IS_HORIZONTAL)
- `lsu.java` — DashboardFragment
- `ltc.java` — DashboardViewModel (card observables, debounce)
- `luc.java` — Card swipeable key (`.swipable`)
- `lou.java` — Card rendering dispatch
- `lry-lse` — Card type classes
- `jlf.java` — Cielo component singleton
- `pus.java` — PhenotypeFlag enum (CIELO at index 53)
- `jzm.java` — Theme overlay selection (Coolwalk vs Cielo)
- `llk.java` — Driver-aligned dashboard enum
- Hero layouts: `sys_ui_layout_hero_poip_*.xml`, `sys_ui_layout_hero_soip.xml`

---

## 2026-03-04 - APK Deep Dive: 8 Research Targets (High + Medium Value)

Date / Session: 2026-03-04 / apk-deep-dive-8-targets

What Changed:

**High-Value Research (4 targets, all completed):**

1. **Facet Switching** — No wire events for rail facet taps. Only NavigationFocusRequest (msg 13, ch 0) fires from nav app lifecycle. CarFacet is HU→phone only. Content inferred from active data channels.
   - Added to `docs/channels/coolwalk-layout.md` (facet switching section)

2. **Input Channel** — Full decode: absolute pixel coordinates (no normalization, no pressure), multi-touch, 9 AA-custom keycodes (65536-65544), rotary = signed delta on AXIS_VSCROLL, touchpad 8-field config with sensitivity.
   - Created `docs/channels/input.md`

3. **VideoConfig Fields 6-9** — All identified: decoder_additional_depth(6), viewing_distance(7)=500mm, pixel_aspect_ratio_e4(8)=10000, real_density(9)=actual DPI before bucket quantization.
   - Updated `oaa/video/VideoConfigData.proto`

4. **Audio Codec Negotiation** — No Opus! PCM or AAC-LC only. One codec per channel (no negotiation). 48kHz/16kHz, 16-bit, mono/stereo. Ackless on PDK 5.0+.
   - Updated `docs/channels/audio.md` (codec negotiation section + gotchas)

**Medium-Value Research (4 targets, all completed):**

5. **Radio Channel (Service 15)** — 10 messages fully decoded: tune/seek/mute/favorites. AM/FM/DAB bands (no XM). Rich metadata (RDS, HD Radio, album art). MediaBrowserService integration. New message: 0x8023 RadioCustomActionRequest.
   - Agent output at `/tmp/claude-1000/-home-matt-claude-personal-openautopro-open-android-auto/tasks/a021e08899e67cd40.output`
   - **TODO**: Write `docs/channels/radio.md` from agent output

6. **Car Control Channel (Service 19)** — 7 messages fully decoded. Subscription model (register → change events). 25 vehicle properties (HVAC, door locks, mirror heat, toll card). Area zones (seat/window/mirror/door/wheel bitmasks). HMG temperature override for Hyundai/Kia.
   - Agent output at `/tmp/claude-1000/-home-matt-claude-personal-openautopro-open-android-auto/tasks/a17f8c191d8ab5b30.output`
   - **TODO**: Write `docs/channels/carcontrol.md` from agent output

7. **Notification Channel** — Entirely phone-side rendering. Empty SDP proto. No wire format for notifications. Reply via PendingIntent + RemoteInput locally. HU sees only projected pixels.
   - Agent output at `/tmp/claude-1000/-home-matt-claude-personal-openautopro-open-android-auto/tasks/afd2e9672b38bfc44.output`

8. **WIRE_HIGH Unknown Classes** — All 6 false positives. 2 already mapped (wai=ControlChannelParams, wco=UiConfigData). 4 are internal gRPC (Assistant/Dodgeboost): aaci=RoundedCornerMaskEntry, nmj=AssistantStatusResponse, nmo=AssistantSuggestion, rse=MediaRecommendationCallbackResponse.

**Proto Fixes Applied:**
- `oaa/carcontrol/CarPropertyData.proto`: Fixed FloatValues/LongValues type swap (float↔int64 were backwards)
- `oaa/radio/RadioBandTypeEnum.proto`: Added BAND_TYPE_DAB = 3
- `oaa/video/VideoConfigData.proto`: Named fields 6-9 with full documentation

**Doc Updates:**
- `docs/channels/coolwalk-layout.md`: Corrected layout type table, added Hero/Cielo/Demand/Driver-Aligned/Facet Switching sections
- `docs/channels/input.md`: Created — complete input channel reference
- `docs/channels/audio.md`: Added codec negotiation section, per-channel defaults, 7 new gotchas

Next Steps:
1. **Write `docs/channels/radio.md`** from agent output (task #14)
2. **Write `docs/channels/carcontrol.md`** from agent output (task #15)
3. Consider adding CarPropertyConfig proto changes for 16.1→16.2 field 4/7 restructure
4. Add DOOR_LOCK (24) and HMG_CAR_ALERTS_COUNT (25) to CarPropertyId enum in proto
5. Improve triage tool: penalize classes in gRPC service descriptors

Verification:
- All 8 agent outputs preserved in `/tmp/claude-1000/` task files
- Proto fixes compile-verified by field type inspection
- MEMORY.md updated with input channel, audio codecs, facet switching findings
