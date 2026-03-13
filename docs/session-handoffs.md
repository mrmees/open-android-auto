# Session Handoffs

Append-only log for cross-session continuity.

Historical entries (2026-02-27 through 2026-03-04) have been archived to [session-handoffs-archive.md](session-handoffs-archive.md). Key findings from those sessions are now captured in channel docs (`docs/channels/`), MEMORY.md, and the verification framework.

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

## 2026-03-07 — Doc cleanup, proto compilation, wire capture validation

Date / Session: 2026-03-07 / doc-cleanup-wire-validation

What Changed:
- Completed doc cleanup tasks 4-8 (analysis README, roadmap, sub-READMEs, final sweep)
- Fixed all protoc compilation errors across 234 protos (broken imports, duplicates, missing syntax)
- Created sensor.md (639 lines) and video.md (666 lines) channel docs
- Cleaned up untracked files (temp/, tools.yaml, gitignored android_auto_unknown_unknown/)
- Pushed 35 commits, tagged v1.1
- Re-blessed existing baseline (188 diffs, all expected from proto fixes)
- Converted 4 scenario captures (general, idle-baseline, music-playback, active-navigation) to validator format
- Ran all 4 through proto_stream_validator — 15,242 frames, ~1,302 decoded successfully

Status:
- v1.1 tagged and pushed
- All 234 protos compile cleanly with protoc
- 4 agents independently modified message_map.py, filtering.py, and run.py — changes CONFLICT
- Converter script at analysis/tools/proto_stream_validator/convert_capture.py works but doesn't strip 2-byte msg ID prefix from payload
- 4 new baselines created but not committed yet (general, idle-baseline, music-playback, active-navigation)

Key Findings from Wire Validation:
- All enum values resolve to names — proto schemas confirmed correct
- SDP decodes perfectly across all captures (14-channel descriptor trees)
- Audio focus lifecycle, video focus, bluetooth pairing, nav focus all decode correctly
- MESSAGE MAP TOO NARROW: only maps msgs on specific channel IDs (AV on ch3 only, ChannelOpen on ch0 only). ~78% of frames unmapped because same message types appear on channels 1-14
- PAYLOAD PREFIX: converted captures embed 2-byte BE msg ID in payload_hex — needs stripping in converter or decoder
- InputEventIndication only shows timestamp, no touch/key data (possible proto gap at field 2)
- SensorEventIndication decodes as {} in all captures (may be initial "no data" response)
- 805 mic channel frames misidentified as AVChannelStartIndication (raw audio data, not proto)

Next Steps:
1. DISCARD agent changes to message_map.py, filtering.py, run.py (they conflict)
2. Fix convert_capture.py to strip 2-byte msg ID prefix from payload_hex
3. Expand message_map.py: make ChannelOpen and AV control messages channel-agnostic
4. Update filtering.py: skip raw media data (0x0000/0x0001) on all AV channels, skip high msg IDs on video channels (H.264 NAL units)
5. Add nav channel messages to map: StatusChange (0x8003), DistanceEvent (0x8006), TurnEvent (0x8007)
6. Add phone status (ch11 0x8001), media info (ch12 0x8001) to map
7. Re-run all 5 captures, bless baselines, commit
8. Investigate InputEventIndication field 2 gap (display channel ID?)

Verification:
- `PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py --capture analysis/captures/non_media/2026-02-28-s25-cleanbuild.jsonl --baseline analysis/baselines/non_media/2026-02-28-s25-cleanbuild.normalized.json` -> validation passed
- `find oaa -name '*.proto' | sort | xargs protoc --proto_path=. --cpp_out=/tmp/oaa_verify` -> clean (0 errors, 0 warnings)

## 2026-03-13 — Nav image evidence design and execution plan

Date / Session: 2026-03-13 / nav-image-evidence-planning

What Changed:
- Added [docs/plans/2026-03-13-nav-image-evidence-design.md](plans/2026-03-13-nav-image-evidence-design.md), an approved design for a source-first, version-paired investigation of native nav-channel image delivery
- Added [docs/plans/2026-03-13-nav-image-evidence-plan.md](plans/2026-03-13-nav-image-evidence-plan.md), a crash-tolerant execution plan with explicit checkpoints, `Resume Here` state, and per-task handoff requirements
- Captured the crucial evidence-source split in the plan: 16.2 source lives in this repo, while the full 16.1 decompiled source currently lives in the sibling `openauto-prodigy/analysis-projection` tree and must be treated as primary evidence during execution

Why:
- The nav-image investigation is getting interrupted by compaction/session crashes, so chat-only continuity is not reliable enough
- The open question is not "what do our docs say" but "what do the 16.1 and 16.2 APKs actually serialize on the native nav wire", especially around `turnImage`, `lanesImage`, `junctionImage`, and `NEXT_TURN_IMAGE`
- A durable plan is needed so the next recovery session can restart from repo files alone instead of re-deriving context from memory

Status:
- Planning complete; execution has not started yet
- The design explicitly keeps scope limited to protocol/evidence work
- The first execution task is to reconfirm the 16.1 dual-send structure (`32774` semantic + `32772` image-bearing) from source and start recording exact citations in the plan ledger

Next Steps:
1. Execute Task 1 from [docs/plans/2026-03-13-nav-image-evidence-plan.md](plans/2026-03-13-nav-image-evidence-plan.md) using `executing-plans`
2. After each meaningful claim closure, update the plan's `Resume Here` block and append a fresh handoff entry before moving on
3. Do not update canonical nav docs/proto comments until the 16.1/16.2 delta matrix closes the relevant evidence questions

Verification:
- `test -f docs/plans/2026-03-13-nav-image-evidence-design.md && echo design_present` -> `design_present`
- `test -f docs/plans/2026-03-13-nav-image-evidence-plan.md && echo plan_present` -> `plan_present`
- `test -d /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources && echo ext_16_1_source_present` -> `ext_16_1_source_present`
- `rg -n "Evidence Ledger|Resume Here|NEXT_TURN_IMAGE|32772|32774" docs/plans/2026-03-13-nav-image-evidence-design.md docs/plans/2026-03-13-nav-image-evidence-plan.md` -> expected investigation/checkpoint markers present
- `git diff --check` -> clean

## 2026-03-13 — 16.1 semantic nav sender checkpoint

Date / Session: 2026-03-13 / nav-image-evidence-task1

What Changed:
- Reconfirmed from 16.1 source that `hkx.h(...)` takes the semantic rich-nav branch under `y(r)`, builds `vzu` step entries from maneuver, lane, text, and road-info data, appends destination entries, and emits `this.k.k(32774, (vzo) o.q())`
- Reconfirmed from the 16.1 message classes that `vzo` only contains repeated `vzu` step entries plus repeated `vze` destinations, while `vzu` exposes maneuver/text/lanes/road-info fields and no raw image-bytes field
- Updated [docs/plans/2026-03-13-nav-image-evidence-plan.md](plans/2026-03-13-nav-image-evidence-plan.md) so recovery now resumes at Task 2 and the app-side image-byte origin question

Why:
- The semantic half of the 16.1 dual-send claim needed exact source citations before the investigation could safely talk about whether images are sent separately or embedded in the rich payload

Status:
- Task 1 complete
- `Q1` now has exact citations for the semantic `32774` half of the claim
- The legacy/image-bearing `32772` half is still the next thing to re-verify from source

Next Steps:
1. Verify that 16.1 `NavigationStep` stores app-provided turn-image bytes in `byte[] c` and parcels them as field `5`
2. Verify that the legacy sender path in `hkx.java` passes `navigationStep2.c` into the image-bearing serializer
3. Verify that `vzm` contains the on-wire bytes field before tightening `Q1`/`Q2`

Verification:
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java | sed -n '302,578p'` -> `y(r)` rich-nav gate, `vzu`/`vzo` builders, destination append, and `this.k.k(32774, (vzo) o.q())` at line `578`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/vzo.java | sed -n '7,30p'` -> descriptor only exposes repeated `vzu` (`b`) and repeated `vze` (`c`)
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/vzu.java | sed -n '7,30p'` -> fields are `vzk`, `vzn`, repeated `vzj`, and `vzc`; no bytes field present

## 2026-03-13 — 16.1 legacy image-bearing nav path checkpoint

Date / Session: 2026-03-13 / nav-image-evidence-task2

What Changed:
- Reconfirmed from 16.1 source that `NavigationStep` stores app-provided turn-image bytes in `byte[] c` and writes them to parcel field `5`
- Reconfirmed that the legacy path in `hkx.java` reads `navigationStep2.c`, substitutes fallback `bArr` when the step image is null, and passes the resulting bytes into `n(...)`
- Reconfirmed inside `hkx.n(...)` plus `vzm.java` that non-null bytes are serialized into `vzm.f` and the legacy nav payload is emitted on `32772`
- Updated [docs/plans/2026-03-13-nav-image-evidence-plan.md](plans/2026-03-13-nav-image-evidence-plan.md) so recovery now resumes at Task 3 and the fallback-image generation question

Why:
- The dual-send claim needed exact source evidence that the legacy path carries raw image bytes from the app-side model all the way into the wire serializer, not just a vague "image-bearing" label

Status:
- Task 2 complete
- `Q1` now has exact citations for both the semantic `32774` path and the legacy/image-bearing `32772` path
- `Q2` now has the fallback input boundary (`NavigationStep.c` or `bArr`), but the exact local synthesis of `bArr` remains the next source trace

Next Steps:
1. Trace `hkx.n(...)` through the fallback branch to identify the local resource-based turn-image synthesis
2. Update `Q2` with exact fallback-generation citations and refresh `Resume Here`
3. Commit the fallback-image checkpoint from Task 3

Verification:
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/com/google/android/gms/car/navigation/NavigationStep.java | sed -n '4,66p'` -> `byte[] c` at line `8`, assignment at line `24`, parcel write `defpackage.rjc.y(parcel, 5, this.c)` at line `65`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java | sed -n '748,756p'` -> legacy caller prefers `navigationStep2.c` and falls back to `bArr` before calling `n(...)`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java | sed -n '1023,1033p'` -> `n(...)` writes non-null bytes into `vzm.f` and sends `32772`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/vzm.java | sed -n '13,34p'` -> `vzm` exposes `zxq f` as the bytes field in its 6-field descriptor

## 2026-03-13 — 16.1 fallback turn-image generation checkpoint

Date / Session: 2026-03-13 / nav-image-evidence-task3

What Changed:
- Reconfirmed from 16.1 source that `hkx.n(...)` clears incoming image bytes when `!this.g.bp()`, then synthesizes fallback bytes locally when `bArr` is null and `this.l` (`hwl`) is available
- Captured the concrete resource-selection logic: `da_turn_depart`, `da_turn_straight`, turn-side variants such as `da_turn_right`/`da_turn_ramp_right`/`da_turn_fork_right`, roundabout assets `da_turn_roundabout_1` through `_8`, `da_turn_uturn`, `da_turn_generic_merge`, `da_turn_ferry`, `da_turn_arrive`, plus generic `hwl.b()` fallback
- Updated [docs/plans/2026-03-13-nav-image-evidence-plan.md](plans/2026-03-13-nav-image-evidence-plan.md) so recovery now resumes at Task 4 and the 16.1 capability-gate question

Why:
- `Q2` needed a source-backed mechanism, not just a claim that some fallback image "must exist"; the exact asset-selection branch is what makes the legacy behavior defensible

Status:
- Task 3 complete
- `Q2` now has exact source citations for local fallback turn-image generation
- The next open 16.1 question is the capability gating that decides when semantic and legacy paths are emitted

Next Steps:
1. Trace the `y(r)` and `z(carInfo)` gates in `hkx.java`
2. Inspect any helper context needed to explain those gates without overstating what they mean
3. Update `Q7`, refresh `Resume Here`, and commit the Task 4 checkpoint

Verification:
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java | sed -n '843,967p'` -> null-image fallback selects concrete `da_turn_*` assets or `hwl.b()` generic bytes
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java | sed -n '1023,1033p'` -> synthesized bytes are serialized into `vzm.f` and sent on `32772`

## 2026-03-13 — 16.1 nav delivery gates checkpoint

Date / Session: 2026-03-13 / nav-image-evidence-task4

What Changed:
- Reconfirmed that the 16.1 semantic nav path is gated by `y(carInfo)` while the legacy image-bearing path is gated by `z(carInfo)` inside `hkx.h(...)`
- Closed the 16.1 threshold itself from source: `CarInfo.e` / `f` are the head-unit protocol major/minor version fields, and `hkx.x(carInfo)` treats HU protocol `>= 1.6` as modern
- Traced the non-version override: `hkx` constructor field `this.e` is populated from clustersim vendor-extension bit `poe.b`, so older HUs can still enter the semantic branch when that override is true
- Checked [docs/plans/2026-03-13-nav-image-evidence-plan.md](plans/2026-03-13-nav-image-evidence-plan.md) forward so recovery now resumes at Task 5 and the 16.2 semantic sender re-verification

Why:
- The earlier "dual-send structure" evidence was real but incomplete; this task pins down when 16.1 sends semantic only, legacy only, or both, which is necessary before comparing 16.2 behavior without overstating compatibility claims

Status:
- Task 4 complete
- `Q7` is now `Needs better evidence`: the 16.1 gate logic is source-backed, but the exact meaning of clustersim override bit `poe.b` and the 16.2 gate equivalents are still open
- `hzy.java` did not add new gating logic; it handles nav lifecycle/control messages and emits `32773`, so the semantic-vs-legacy decision remains in `hkx.java`

Next Steps:
1. Reconfirm the 16.2 semantic native sender in `hlj.mo18762h(...)`
2. Verify the 16.2 message classes are still image-free on the semantic path
3. Update `Q3`, refresh `Resume Here`, and commit the Task 5 checkpoint

Verification:
- `grep -n "if (y(r))" /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java` -> semantic gate occurrences at lines `159` and `304`
- `grep -n "if (z(carInfo))" /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java` -> legacy gate occurrence at line `586`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java | sed -n '47,60p'` -> `x(carInfo)` encodes HU protocol threshold `>1` or `1.6+`; `y(carInfo)` is `this.e || x(carInfo)`; `z(carInfo)` is `!x(carInfo)`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java | sed -n '304,308p'` -> semantic `32774` path is entered under `if (y(r))`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java | sed -n '586,592p'` -> legacy/image path is entered under `if (z(carInfo))`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/ijk.java | sed -n '59,59p'` -> `CarInfo.e` / `f` are populated from `headUnitProtocolMajorVersionNumber` / `headUnitProtocolMinorVersionNumber`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/iny.java | sed -n '323,333p'` -> `hkx` receives constructor boolean from clustersim vendor-extension field `poeVar.b`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hlw.java | sed -n '8,37p'` -> `hlw` parses clustersim vendor-extension payload into `poe`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hzy.java | sed -n '15,135p'` -> no semantic/legacy gate logic; file handles `32769`/`32770` receive path and emits `32773`

## 2026-03-13 — 16.2 semantic nav sender checkpoint

Date / Session: 2026-03-13 / nav-image-evidence-task5

What Changed:
- Reconfirmed from 16.2 source that `hlj.mo18762h(...)` still builds the semantic native nav payload and emits it on `32774`
- Reconfirmed that the semantic payload remains image-free: `vza` only contains repeated step + destination entries, and `vzg` only contains maneuver, text, lane, and road-info fields
- Updated [docs/plans/2026-03-13-nav-image-evidence-plan.md](plans/2026-03-13-nav-image-evidence-plan.md) so recovery now resumes at Task 6 and the 16.2 app-side turn-image question
- Recorded the source-location workaround: this worktree has the 16.2 `apk-index` tree but not the decompiled `apk-source`, so Task 5 used the main checkout's read-only `analysis/.../apk-source` path as evidence

Why:
- `Q3` was already believed to be true, but this investigation only counts what the actual sender and message classes still do in 16.2, with line-backed proof instead of inherited assumptions

Status:
- Task 5 complete
- `Q3` now has exact 16.2 citations for the semantic sender and its image-free wire shape
- The next open question is whether 16.2 still routes `NavigationStep.turnImage` bytes into any native sender path

Next Steps:
1. Verify that 16.2 `NavigationStep` still carries app-side `turnImage` bytes
2. Check whether `hlj`'s semantic path ignores those bytes while any legacy helper still accepts them
3. Update `Q4`, refresh `Resume Here`, and commit the Task 6 checkpoint

Verification:
- `sed -n '360,620p' /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java` -> semantic builder populates maneuver, text, lanes, road info, destinations, then continues toward `32774`
- `sed -n '1,220p' /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/vza.java` -> descriptor only exposes repeated `vzg` step entries and repeated `vyq` destinations
- `sed -n '1,220p' /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/vzg.java` -> fields are `vyw`, `vyz`, repeated `vyv`, and `vyo`; no bytes field present
- `rg -n "32774|m18758y\\(|if \\(m18758y\\(mo19019r\\)\\)" /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java` -> semantic gate occurrences at lines `215` and `361`; `32774` send at line `635`
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java | sed -n '96,110p'` -> 16.2 still uses `m18758y(carInfo) = this.f34211e || m18757x(carInfo)` with the same protocol-threshold helper structure
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java | sed -n '375,635p'` -> semantic sender builds `vzg` entries from maneuver/text/lanes/road-info and adds destinations before `m20106k(32774, ...)`
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/vza.java | sed -n '12,40p'` -> `vza` is repeated `vzg` + repeated `vyq`
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/vzg.java | sed -n '13,45p'` -> `vzg` fields remain maneuver, text, repeated lanes, and road-info only

## 2026-03-13 — 16.2 app-side turn-image path checkpoint

Date / Session: 2026-03-13 / nav-image-evidence-task6

What Changed:
- Reconfirmed from 16.2 source that `NavigationStep` still carries app-provided `turnImage` bytes in `byte[] f20729c` and parcels them as field `5`
- Reconfirmed that the semantic `32774` sender path in `hlj.mo18762h(...)` does not read `f20729c`; it only serializes maneuver, text, lane, and road-info data into `vzg`
- Reconfirmed that the legacy branch under `m18759z(carInfo)` still reads `navigationStep2.f20729c`, falls back to `bArr` when null, and passes the bytes into `mo18767n(...)`
- Updated [docs/plans/2026-03-13-nav-image-evidence-plan.md](plans/2026-03-13-nav-image-evidence-plan.md) so recovery now resumes at Task 7 and the explicit `NEXT_TURN_IMAGE` / image-negotiation search

Why:
- This task separates two claims that are easy to blur together: "the app model still has turn-image bytes" versus "16.2 still has a reachable native image-bearing wire sender." The source only proves the first claim cleanly and leaves the second open.

Status:
- Task 6 complete
- `Q4` is now `Needs better evidence`: retained legacy byte plumbing exists, but the image-bearing sender graph is not closed because `mo18767n(...)` is not decompiled in this source dump
- The next open question is whether explicit `NEXT_TURN_IMAGE` / image-negotiation references expose a reachable sender or just dead-end leftovers

Next Steps:
1. Search 16.2 `p000/*.java` for `NEXT_TURN_IMAGE`, `NavigationImageOptions`, `turnImage`, and related image-negotiation symbols
2. Search the 16.2 nav stack for message IDs around the old image-bearing path
3. Update `Q4` / `Q5`, refresh `Resume Here`, and commit the Task 7 checkpoint

Verification:
- `sed -n '1,90p' /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/com/google/android/gms/car/navigation/NavigationStep.java` -> `NavigationStep` still defines `byte[] f20729c` and parcels it as field `5`
- `sed -n '360,545p' /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java` -> semantic path builds `vzg` from maneuver/text/lanes/road-info only
- `sed -n '790,815p' /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java` -> legacy branch forwards `navigationStep2.f20729c` or fallback `bArr` into `mo18767n(...)`
- `rg -n "f20729c|mo18767n\\(|m18759z\\(|32772|32773|32774" /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/com/google/android/gms/car/navigation/NavigationStep.java` -> `f20729c` appears only in `NavigationStep` and the legacy `hlj` branch; semantic `32774` send remains separate
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/com/google/android/gms/car/navigation/NavigationStep.java | sed -n '24,88p'` -> `f20729c` assignment, `turnImage` stringification, and parcel field `5`
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java | sed -n '361,545p'` -> semantic sender consumes maneuver/text/lanes/road-info fields and never references `f20729c`
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java | sed -n '643,815p'` -> legacy branch is gated by `m18759z(carInfo)` and passes `navigationStep2.f20729c` into `mo18767n(...)`
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java | sed -n '929,934p'` -> `mo18767n(...)` exists with a `byte[]` parameter, but its body is unavailable in this decompiled source dump
