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

## 2026-03-13 — 16.2 NEXT_TURN_IMAGE search checkpoint

Date / Session: 2026-03-13 / nav-image-evidence-task7

What Changed:
- Searched the 16.2 `p000/*.java` tree for `NEXT_TURN_IMAGE`, `NavigationImageOptions`, `colour_depth`, `turnImage`, and `nextTurnImage`, then bounded the hits to the actual nav sender stack
- Reconfirmed that the visible 16.2 nav sender still exposes `32773` from `ian` and `32774` / `32775` / `32776` from `hlj`, with no named image-negotiation message or config path in source
- Updated [docs/plans/2026-03-13-nav-image-evidence-plan.md](plans/2026-03-13-nav-image-evidence-plan.md) so recovery now resumes at Task 8 and the projected-UI image asset question

Why:
- The investigation needed to stop hand-waving around `NEXT_TURN_IMAGE` and either find a real 16.2 sender path or kill that claim with an explicit, source-backed search trail

Status:
- Task 7 complete
- `Q5` is now `Rejected`: no reachable 16.2 `NEXT_TURN_IMAGE` / `NavigationImageOptions` path was found in source
- `Q4` stays `Needs better evidence`: the named successor path is gone, but the undecompiled `mo18767n(...)` body still prevents a full negative proof about any opaque legacy image send

Next Steps:
1. Verify that 16.2 `Maneuver.icon`, `Step.lanesImage`, and `RoutingInfo.junctionImage` exist as projected `CarIcon` fields
2. Verify that `jbl.java` consumes those images in projected UI rendering
3. Update `Q6`, refresh `Resume Here`, and commit the Task 8 checkpoint

Verification:
- `rg -n "NEXT_TURN_IMAGE|NavigationImageOptions|colour_depth|turnImage|nextTurnImage" /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000 -g '*.java'` -> only `turnImage` / `nextTurnImage` hits in `ggf.java`, `ggj.java`, and `ggo.java`; no `NEXT_TURN_IMAGE`, `NavigationImageOptions`, or `colour_depth` references
- `rg -n "32772|32773|32774|32775|32776|0x8004|0x8005|0x8006|0x8007|0x8008" /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000 -g '*.java'` -> nav-stack sender hits remain `hlj.java` and `ian.java`; extra `hlg.java` / `hlb.java` hits were investigated and excluded as input/control channels
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java | sed -n '96,110p;300,322p;635,645p;929,954p'` -> `m18758y(carInfo)` and `m18759z(carInfo)` remain the branch points; `hlj` visibly sends `32775`, `32774`, and `32776`, while `mo18767n(...)` stays undecompiled
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/ian.java | sed -n '118,148p'` -> `ian.m20073h(...)` emits `32773`
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/ggf.java | sed -n '1,60p'` -> `ExpandedTurnCardUiModel` carries `laneImage`, `turnImage`, `junctionImage`, and `nextTurnImage` as UI-model fields
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/ggj.java | sed -n '1,64p'` -> `MinimizedTurnCardUiModel` carries `laneImage` / `turnImage` UI-model fields
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/ggo.java | sed -n '71,77p'` -> `TurnCardStyle` still refers to `laneImageSize` / `turnImageSize` styling only
- `sed -n '1,220p' oaa/navigation/NavigationTypeEnum.proto` -> repo proto still defines `NEXT_TURN_IMAGE = 2`, but Task 7 found no 16.2 sender usage
- `sed -n '1,220p' oaa/navigation/NavigationImageOptionsData.proto` -> repo proto still defines `NavigationImageOptions`, but Task 7 found no 16.2 sender usage

## 2026-03-13 — Projected UI image assets vs native wire checkpoint

Date / Session: 2026-03-13 / nav-image-evidence-task8

What Changed:
- Reconfirmed from the 16.2 AndroidX projected navigation models that maneuver icons, lane images, and junction images exist as `CarIcon` fields on `Maneuver`, `Step`, and `RoutingInfo`
- Reconfirmed from `jbl.java` that those `CarIcon` assets are rendered into projected turn-card UI widgets rather than fed into the native nav sender
- Updated [docs/plans/2026-03-13-nav-image-evidence-plan.md](plans/2026-03-13-nav-image-evidence-plan.md) so recovery now resumes at Task 9 and the cross-version delta matrix

Why:
- `Q6` needed a clean split between "image exists in app-side projected UI models" and "image reaches the native nav wire"; without that split, it is too easy to mix projected templates with cluster/native transport claims

Status:
- Task 8 complete
- `Q6` is now `Rejected` for native transport: the source only proves projected-UI `CarIcon` usage for `junctionImage`, `lanesImage`, and maneuver icons
- The next step is to normalize the cross-version story in one matrix before touching canonical docs

Next Steps:
1. Add the 16.1 vs 16.2 matrix to the plan
2. Set final statuses for `Q1` through `Q8` without forcing weak closures
3. Refresh `Resume Here`, append the Task 9 handoff, and commit

Verification:
- `sed -n '55,120p' /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/Maneuver.java` -> `Maneuver` stores `CarIcon mIcon` and exposes it via `getIcon()`
- `sed -n '1,90p' /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/Step.java` -> `Step` stores `CarIcon mLanesImage` and exposes it via `getLanesImage()`
- `sed -n '1,80p' /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/RoutingInfo.java` -> `RoutingInfo` stores `CarIcon mJunctionImage` and exposes it via `getJunctionImage()`
- `sed -n '540,600p' /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/jbl.java` -> projected UI consumes `junctionImage`, maneuver icons, and `lanesImage` when rendering current/next steps
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/Maneuver.java | sed -n '60,101p'` -> exact `mIcon` field and getter lines
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/Step.java | sed -n '15,54p'` -> exact `mLanesImage` field/getter lines
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/androidx/car/app/navigation/model/RoutingInfo.java | sed -n '13,56p'` -> exact `mJunctionImage` field/getter lines
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/jbl.java | sed -n '548,606p'` -> projected renderer reads `getJunctionImage()`, `getIcon()`, and `getLanesImage()`

## 2026-03-13 — Cross-version nav image evidence matrix checkpoint

Date / Session: 2026-03-13 / nav-image-evidence-task9

What Changed:
- Added a 16.1 vs 16.2 matrix to [docs/plans/2026-03-13-nav-image-evidence-plan.md](plans/2026-03-13-nav-image-evidence-plan.md) covering app-side turn-image bytes, semantic senders, legacy image-bearing senders, fallback generation, `NEXT_TURN_IMAGE`, projected-only `CarIcon` assets, and native-wire image payloads
- Normalized the ledger so `Q1`-`Q8` now reflect the current evidence boundary: `Q5`/`Q6` rejected, `Q4`/`Q7` still bounded-but-open, and `Q8` confirmed as a workflow checkpoint
- Moved `Resume Here` forward to Task 10, where canonical docs/proto comments can now be updated minimally from the closed claims

Why:
- By Task 8 the raw evidence was there, but the repo still needed a single cross-version view that makes the remaining uncertainty obvious before any canonical docs are touched

Status:
- Task 9 complete
- The 16.1 vs 16.2 evidence story is now normalized enough for canonical doc updates
- Remaining uncertainty is intentionally narrow: the opaque 16.2 `mo18767n(...)` body and the exact meaning/provenance of the semantic override bit

Next Steps:
1. Search canonical nav docs/proto comments for the now-stale `NEXT_TURN_IMAGE` / image-payload claims
2. Apply only the source-backed claim changes
3. Run Task 10 verification and append the final handoff

Verification:
- `sed -n '34,95p' /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/plans/2026-03-13-nav-image-evidence-plan.md` -> ledger, `Resume Here`, and new `Cross-Version Matrix` section are all present and aligned
- `rg -n "Q[1-8] |Cross-Version Matrix|Task 9 - cross-version nav image evidence matrix|Task 10" /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/plans/2026-03-13-nav-image-evidence-plan.md` -> final statuses, matrix section, and Task 10 recovery target are present
- `rg -n "nav-image-evidence-task9|Q8|Task 10" /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/session-handoffs.md /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/plans/2026-03-13-nav-image-evidence-plan.md` -> handoff entry, confirmed `Q8`, and Task 10 `Resume Here` marker are present

## 2026-03-13 — Canonical nav image evidence update

Date / Session: 2026-03-13 / nav-image-evidence-task10

What Changed:
- Updated `docs/channels/nav.md` to bound `turn_icon` to the deprecated 16.1 `0x8004` / `32772` path, mark native `NavigationNotification` / `32774` as semantic-only, and call out `Maneuver.icon`, `Step.lanesImage`, and `RoutingInfo.junctionImage` as projected-UI-only evidence rather than native-wire payloads
- Updated `oaa/navigation/NavigationTurnEventMessage.proto`, `oaa/navigation/NavigationNotificationMessage.proto`, and `oaa/navigation/InstrumentClusterMessages.proto` comments to match the closed claims and stop presenting `NEXT_TURN_IMAGE` / `NavigationImageOptions` as a proven live 16.2 sender path
- Left the placeholder `NEXT_TURN_IMAGE` definitions in `oaa/navigation/NavigationChannelData.proto` and `oaa/navigation/NavigationTypeEnum.proto` untouched because Task 10 closed only the absence of a reachable 16.2 sender path, not the existence of those proto placeholders

Why:
- Task 9 finally bounded the evidence tightly enough to update canonical docs without smuggling in assumptions about the opaque `mo18767n(...)` path or the unresolved semantic override bit

Status:
- Task 10 complete
- Canonical docs now reflect the closed claims: `Q5` rejected, `Q6` rejected, `Q8` confirmed
- Still bounded: `Q4` needs better evidence because `mo18767n(...)` remains opaque; `Q7` needs better evidence because the semantic override bit meaning/provenance is not yet source-closed

Next Steps:
1. Recover or decompile the 16.2 `mo18767n(...)` body if you want to close whether any native legacy image sender survived beyond the visible `byte[]` plumbing
2. Trace the provenance and semantic meaning of 16.2 `f34211e` if you want the cross-version gate story fully closed
3. Revisit the placeholder `NEXT_TURN_IMAGE` proto definitions only if new source evidence shows they are live rather than dead-end config surfaces

Verification:
- `git -C /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313 diff --check` -> clean (no output)
- `rg -n "NEXT_TURN_IMAGE|turn_icon|junctionImage|lanesImage|32772|32774" /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/channels/nav.md /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/oaa/navigation` -> updated canonical docs show bounded `turn_icon` / `32772` / `32774` claims plus projected-only `junctionImage` / `lanesImage` notes; remaining `NEXT_TURN_IMAGE` hits are the untouched placeholder definitions in `NavigationChannelData.proto` and `NavigationTypeEnum.proto`
- `mkdir -p /tmp/oaa_nav_task10_verify && protoc --proto_path=. --cpp_out=/tmp/oaa_nav_task10_verify oaa/navigation/NavigationTurnEventMessage.proto oaa/navigation/NavigationNotificationMessage.proto oaa/navigation/InstrumentClusterMessages.proto` -> success

## 2026-03-13 — Nav mapping follow-up cleanup

Date / Session: 2026-03-13 / nav-image-evidence-followup-mappings

What Changed:
- Updated `docs/cross-version/navigation.md` so the 16.2 rows for `NavigationLane` and `NavigationText` now point to `vyv` and `vyz`, matching the semantic `32774` sender evidence
- Added a bounded note to the same cross-version table clarifying that the deprecated 16.2 `vyy` class is only class-shape continuity for `NavigationTurnEvent`, not proof of a reachable native `0x8004` sender path
- Updated `oaa/navigation/NavigationNotificationMessage.audit.yaml` and `oaa/navigation/NavigationTurnEventMessage.audit.yaml` to reflect those class mappings and the bounded 16.2 `vyy` status, and corrected the `TurnSideEnum.proto` header comment to reference NavigationTurnEvent field `3`

Why:
- Task 10 fixed the canonical nav docs, but a follow-up sweep found stale mapping/reference artifacts that now contradicted the source-backed evidence, especially around 16.2 semantic-nav submessages and the deprecated `vyy` class

Status:
- Follow-up reference cleanup complete
- Canonical nav docs, cross-version table, and the touched nav audit sidecars now agree on the bounded 16.2 story
- Still intentionally unresolved: whether undecompiled `mo18767n(...)` hides any native legacy image send, and what the 16.2 semantic override bit exactly means

Next Steps:
1. If you want a wider consistency pass, inspect historical/debug docs such as `docs/phone-side-debug.md` and any generated reference artifacts for pre-Task-10 TurnEvent assumptions
2. If you want to close `Q4`, recover or decompile the 16.2 `mo18767n(...)` body
3. If you want to close `Q7`, trace the provenance and semantic meaning of `f34211e`

Verification:
- `git -C /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313 diff --check` -> clean (no output)
- `rg -n "NavigationLane \\| .*vyv|NavigationText \\| .*vyz|NavigationTurnEvent \\| .*vyy|reachable native .*0x8004|Used in NavigationTurnEvent field 3|v16\\.2:vyv|v16\\.2:vyz" /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/cross-version/navigation.md /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/oaa/navigation/NavigationNotificationMessage.audit.yaml /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/oaa/navigation/NavigationTurnEventMessage.audit.yaml /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/oaa/navigation/TurnSideEnum.proto` -> expected updated mappings, bounded `vyy` note, and corrected field-number comment present
- `mkdir -p /tmp/oaa_nav_followup_verify && protoc --proto_path=. --cpp_out=/tmp/oaa_nav_followup_verify oaa/navigation/TurnSideEnum.proto oaa/navigation/NavigationTurnEventMessage.proto` -> success

## 2026-03-13 — Sony naming bridge cleanup

Date / Session: 2026-03-13 / nav-image-evidence-followup-sony-names

What Changed:
- Updated `docs/protocol-cross-reference.md` to keep the Sony-symbol `NavigationNextTurnEvent` terminology but explicitly bridge it to the canonical repo split between deprecated `NavigationTurnEvent`, `LegacyNavigationTurnEvent`, and `NavigationNextTurnDistanceEvent`
- Updated `docs/channels/coolwalk-layout.md` so the active-navigation inference note no longer implies `NavigationTurnEvent` is the modern default nav signal; it now points at `NavigationNotification` / `NavigationState` plus legacy flat turn-event fallbacks

Why:
- After the Task 10 and mapping follow-up fixes, these docs still mixed older Sony symbol names with canonical repo names in a way that could mislead readers about which modern nav messages are actually primary

Status:
- Naming-bridge cleanup complete
- The touched docs now preserve Sony/source terminology without fighting the bounded canonical nav evidence
- Remaining open questions are still the same bounded technical ones (`mo18767n(...)` and the override bit), not naming drift

Next Steps:
1. If you want a full historical consistency sweep, inspect the remaining Sony/Kenwood/Alpine firmware notes for places where symbol names should be explicitly bridged to canonical repo message names
2. If you want further evidence closure, continue on `Q4` or `Q7` rather than expanding doc cleanup indefinitely

Verification:
- `git -C /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313 diff --check` -> clean (no output)
- `rg -n "Sony-symbol terminology|NavigationNextTurnEvent \\| Sony-symbol family|Navigation status \\(10\\) \\| NavigationNextTurnEvent|Navigation active" /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/protocol-cross-reference.md /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/channels/coolwalk-layout.md` -> bridging note, updated Sony-name row, updated service summary row, and updated coolwalk navigation-activity note present

## 2026-03-13 — 16.2 legacy 0x8004 recovery correction

Date / Session: 2026-03-13 / nav-image-evidence-followup-q4-recovery

What Changed:
- Recovered `hlj.mo18767n(...)` from 16.2 `classes.dex` via fallback JADX and confirmed that the legacy `m18759z(carInfo)` branch still synthesizes `da_turn_*` fallback images, builds deprecated `vyy`, and sends native `32772` / `0x8004`
- Updated canonical/reference docs and proto comments that had been overstated after Task 10: `docs/channels/nav.md`, `oaa/navigation/NavigationTurnEventMessage.proto`, `oaa/navigation/NavigationNotificationMessage.proto`, `oaa/navigation/InstrumentClusterMessages.proto`, `docs/cross-version/navigation.md`, `oaa/navigation/NavigationTurnEventMessage.audit.yaml`, and `docs/protocol-cross-reference.md`
- Updated the nav-image design/plan artifacts so `Q4` is now confirmed, `Q5`/`Q6` stay rejected for the named successor / lane-junction cases, and the remaining live open question is the meaning of 16.2 override bit `f34211e`

Why:
- The previous post-Task-10 cleanup reasonably bounded the opaque `mo18767n(...)` method as unresolved, but once fallback JADX exposed the body, the stronger “0x8004 removed in 16.2” language became wrong and had to be corrected immediately

Status:
- `Q4` is now confirmed: 16.2 still has a native legacy image-bearing path on deprecated `32772` / `0x8004`
- `Q5` remains rejected: no named `NEXT_TURN_IMAGE` / `NavigationImageOptions` sender path was found; the live legacy send stays on deprecated `0x8004`
- `Q6` remains rejected for native lane/junction transport: recovered `mo18767n(...)` still only carries one optional turn-image bytes field
- `Q7` is now the primary remaining gap

Next Steps:
1. Trace the provenance and semantic meaning of `f34211e` to close the cross-version gate story
2. Decide whether any older historical/debug docs need explicit “superseded by fallback JADX recovery” notes, or whether the current canonical/reference corrections are enough

Verification:
- `git -C /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313 diff --check` -> clean (no output)
- `mkdir -p /tmp/oaa_nav_q4_verify && protoc --proto_path=. --cpp_out=/tmp/oaa_nav_q4_verify oaa/navigation/NavigationTurnEventMessage.proto oaa/navigation/NavigationNotificationMessage.proto oaa/navigation/InstrumentClusterMessages.proto` -> success
- `jadx --single-class defpackage.hlj --single-class-output /tmp/jadx_hlj_verify --decompilation-mode fallback --no-res /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/resources/classes.dex /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/resources/classes2.dex /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/resources/classes3.dex /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/resources/classes4.dex` -> success; wrote `/tmp/jadx_hlj_verify/hlj.java`
- `rg -n "bp\\(\\)|da_turn_|vyy|32772" /tmp/jadx_hlj_verify/hlj.java` -> recovered legacy helper clears bytes when image delivery is disabled, synthesizes concrete `da_turn_*` assets, builds `vyy`, and sends `32772`
- `rg -n "Q4 \\||Q5 \\||Q6 \\||Legacy image-bearing sender|Local fallback image generation|Native-wire lane/junction/turn image payloads|f34211e" /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/plans/2026-03-13-nav-image-evidence-plan.md /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/plans/2026-03-13-nav-image-evidence-design.md` -> plan/design artifacts now show `Q4` confirmed, `Q5`/`Q6` rejected, updated matrix rows, and `f34211e` as the next unanswered question
- `rg -n "legacy image-bearing|vyy @Deprecated|0x8004 / 32772|legacy image-bearing path still source-backed" /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/channels/nav.md /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/oaa/navigation/NavigationTurnEventMessage.proto /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/oaa/navigation/InstrumentClusterMessages.proto /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/cross-version/navigation.md /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/protocol-cross-reference.md` -> corrected canonical/reference docs now consistently describe deprecated but live legacy `0x8004` / `32772` in 16.2

## 2026-03-13 — Nav image evidence recovery rebaseline

Date / Session: 2026-03-13 / nav-image-evidence-recovery-rebaseline

What Changed:
- Rebased the recovery state after a crash review and confirmed the older "resume Task 10" prompt is stale relative to the branch head
- Verified the isolated worktree already contains Task 10 plus the later corrections through commit `00013e2` (`docs(nav): correct 16.2 legacy turn-event path`)
- Traced the remaining 16.2 override-bit provenance further: `hlj` receives `f34211e` from `pnl.f57495b`, `hmi` parses `pnl` from the `com.google.android.projection.clustersim` vendor extension, and `ilf` writes the same bit on the producer side during service-discovery munging
- Narrowed the remaining open question: `Q7` is no longer "where does the override bit come from?" so much as "what does that bit actually mean?"

Why:
- The previous restart prompt would have sent the next session backward into already-completed Task 10 work and pre-correction assumptions about `Q4`
- A fresh handoff needed to reflect the real branch state so the next session can focus only on the still-live `f34211e` semantics question

Status:
- Worktree is clean on branch `nav-image-evidence-20260313`
- Canonical nav docs and proto comments are already updated and corrected for the recovered 16.2 legacy `0x8004` / `32772` path
- `Q4` is confirmed, `Q5` and `Q6` remain rejected, and `Q7` is the only meaningful remaining investigation target
- Current source-backed provenance chain for `Q7`: `iom.java` -> `new hlj(..., pnlVar.f57495b)`; `hmi.java` parses `pnl`; `pnl.java` exposes a single boolean field; `ilf.java` writes that field from local variable `z5`; 16.1 mirrors the same shape via `iny.java` / `poe.b` / `iks.java`

Next Steps:
1. Trace how `z5` / `z3` are derived in `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/ilf.java` and compare that logic with `openauto-prodigy/.../defpackage/iks.java`
2. Inspect `analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/ile.java` and the 16.1 analog `openauto-prodigy/.../defpackage/ikr.java` to see whether the bit maps to a named pass-through/filtering behavior
3. If the producer-side semantics stay opaque, tighten `Q7` to "provenance closed, semantic meaning still unproven" rather than guessing

Verification:
- `git -C /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313 status --short --branch` -> clean branch `nav-image-evidence-20260313`
- `git -C /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313 log --oneline --decorate -10` -> head is `00013e2 docs(nav): correct 16.2 legacy turn-event path`; older Task 10 commit `0025f40` is already behind it
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/iom.java | sed -n '360,376p'` -> `hlj` constructed with `pnlVar.f57495b`
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hmi.java | sed -n '15,46p'` -> `hmi` parses `pnl` from `com.google.android.projection.clustersim`
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/pnl.java | sed -n '4,34p'` -> `pnl` carries boolean field `f57495b`
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/ilf.java | sed -n '377,383p'` -> producer-side service-discovery munger writes `((pnl) ...).f57495b = z5`
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/iks.java | sed -n '364,370p'` -> 16.1 producer-side path writes mirrored `poe.b = z5`

## 2026-03-13 — Q7 capability gate closure

Date / Session: 2026-03-13 / nav-image-evidence-q7-closure

What Changed:
- Closed `Q7` in the nav-image plan/design artifacts with a source-backed meaning for the 16.1 `poe.b` / 16.2 `pnl.f57495b` override bit
- Documented that the override becomes true only when the clustersim SDR munger has to inject a missing instrument-cluster descriptor (`wbw` / `wbm` bit `128` carrying `vzr` / `vzd` image options) and that `hkx` / `hlj` then use that bit to force the rich-semantic nav gate
- Refreshed the plan `Resume Here` block so the evidence ledger no longer points at a dead `f34211e` question

Why:
- `Q7` was the last live investigation target after Task 10 and the later nav-document corrections
- Direct APK source closed provenance but not the hidden branch in `iks` / `ilf`, so simple JADX recovery was needed to prove the bit's runtime meaning without guessing

Status:
- `Q7` is now confirmed
- The cross-version gate story is source-backed end-to-end: protocol `>= 1.6` still drives the default threshold, and the clustersim vendor bit is a synthetic-instrument-cluster override rather than a second HU-version field
- No canonical nav doc changes were needed in this pass; only the plan/design/handoff layer changed

Next Steps:
1. Optional: sweep historical/debug docs for stale text that still says the override-bit meaning is open
2. Otherwise this nav-image evidence track is ready for review

Verification:
- `git -C /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313 diff --check` -> clean (no output)
- `nl -ba /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/sources/p000/hlj.java | sed -n '116,152p'` -> `(wbmVar.f74994b & 128)` marks the instrument-cluster descriptor and `vzd` carries image-option data
- `nl -ba /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/sources/defpackage/hkx.java | sed -n '70,125p'` -> 16.1 mirrors the same `wbw.b & 128` instrument-cluster descriptor and `vzr` image-option handling
- `mkdir -p /tmp/jadx_ilf_verify && jadx --show-bad-code --comments-level debug --decompilation-mode simple --single-class defpackage.ilf --single-class-output /tmp/jadx_ilf_verify /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/resources/classes.dex` -> success; wrote `/tmp/jadx_ilf_verify/ilf.java`
- `rg -n "if \\(i2 >= 0\\)|wbmVar3\\.b \\|= 128|new ile|z5 = false" /tmp/jadx_ilf_verify/ilf.java` -> recovered branch injects missing `wbm.j` / bit-`128` descriptor, otherwise forces `z5 = false`, then passes `z5` into `new ile(...)`
- `mkdir -p /tmp/jadx_ile_verify && jadx --show-bad-code --comments-level debug --decompilation-mode simple --single-class defpackage.ile --single-class-output /tmp/jadx_ile_verify /home/matt/claude/personal/openautopro/open-android-auto/analysis/android_auto_16.2.660604-release_162660604/apk-source/resources/classes.dex` -> success; wrote `/tmp/jadx_ile_verify/ile.java`
- `rg -n "int\\[\\] iArr = \\{i\\}|iArr = new int\\[0\\]|if \\(this\\.e == false\\)|return null;" /tmp/jadx_ile_verify/ile.java` -> when the override is true, `ile` registers the synthetic channel and swallows returned nav messages (`return null`) instead of passing them through
- `mkdir -p /tmp/jadx_iks_verify && jadx --show-bad-code --comments-level debug --decompilation-mode simple --single-class defpackage.iks --single-class-output /tmp/jadx_iks_verify /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/resources/classes.dex` -> success; wrote `/tmp/jadx_iks_verify/iks.java`
- `rg -n "if \\(i2 >= 0\\)|wbwVar3\\.b \\|= 128|new ikr|z5 = false" /tmp/jadx_iks_verify/iks.java` -> 16.1 recovered branch matches 16.2: inject missing `wbw.j` / bit-`128` descriptor, otherwise force `z5 = false`, then pass `z5` into `new ikr(...)`
- `mkdir -p /tmp/jadx_ikr_verify && jadx --show-bad-code --comments-level debug --decompilation-mode simple --single-class defpackage.ikr --single-class-output /tmp/jadx_ikr_verify /home/matt/claude/personal/openautopro/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-source/resources/classes.dex` -> success; wrote `/tmp/jadx_ikr_verify/ikr.java`
- `rg -n "int\\[\\] iArr = \\{i\\}|iArr = new int\\[0\\]|if \\(this\\.e == false\\)|return null;" /tmp/jadx_ikr_verify/ikr.java` -> 16.1 `ikr` uses the same override-controlled synthetic-channel / swallow behavior as 16.2 `ile`
- `rg -n "Q7 \\| .*Confirmed|synthetic instrument-cluster descriptor|rich-nav capability override" /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/plans/2026-03-13-nav-image-evidence-plan.md /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/plans/2026-03-13-nav-image-evidence-design.md /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/nav-image-evidence-20260313/docs/session-handoffs.md` -> plan/design/handoff artifacts now show `Q7` confirmed and describe the override as synthetic instrument-cluster injection

## 2026-03-22 — Dist branch publication workflow

Date / Session: 2026-03-22 / dist-branch-publish

What Changed:
- Created and pushed an orphan `dist` branch containing only `README.md`, `LICENSE`, and `oaa/**/*.proto`
- Added [publish-dist.yml](../.github/workflows/publish-dist.yml) so release tags (`v*`) reconstruct and publish the `dist` branch from `main`
- Added planning docs at [docs/plans/2026-03-22-dist-branch-design.md](plans/2026-03-22-dist-branch-design.md) and [docs/plans/2026-03-22-dist-branch-publish.md](plans/2026-03-22-dist-branch-publish.md)
- Updated [docs/roadmap-current.md](roadmap-current.md) to reflect the downstream-consumer distribution cleanup

Why:
- Downstream consumers only need the canonical proto definitions and should not have to clone research archives and analysis artifacts from `main`
- An orphan `dist` branch provides a small, stable clone target while preserving `main` as the full protocol-reference branch
- Automating publication on release tags keeps `dist` synchronized without manual curation

Status:
- Remote branch `origin/dist` exists with only consumable deliverables
- Remote branch `origin/main` contains the workflow needed to refresh `dist` on future `v*` tags
- No files were removed from `main`

Next Steps:
1. Push the next release tag (`v*`) after proto updates so GitHub Actions republishes `dist`
2. Update downstream consumers to clone `-b dist` when they only need protobuf sources
3. Optionally delete the temporary local feature/dist worktrees after confirming no further edits are needed

Verification:
- `find oaa -name '*.proto' | sort | xargs protoc --proto_path=. --cpp_out=/tmp/oaa_baseline_verify` -> success in clean feature worktree
- `git -C /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/dist-output ls-tree -r --name-only dist | sed -n '1,20p'` -> only root metadata plus `oaa/*.proto` paths listed
- `find /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/dist-output/oaa -type f ! -name '*.proto'` -> no output
- `git -C /home/matt/claude/personal/openautopro/open-android-auto/.worktrees/dist-output push -u origin dist` -> success
- `GIT_TERMINAL_PROMPT=0 git -c credential.helper= ls-remote --heads https://github.com/mrmees/open-android-auto.git main dist` -> both remote heads resolved successfully
- `GIT_TERMINAL_PROMPT=0 timeout 180s git -c credential.helper= -c protocol.version=2 clone --single-branch --no-tags --depth 1 -b main https://github.com/mrmees/open-android-auto.git <tmp>` -> success; `in-pack: 2415`, `.git/objects: 57M`
- `GIT_TERMINAL_PROMPT=0 timeout 60s git -c credential.helper= -c protocol.version=2 clone --single-branch --no-tags --depth 1 -b dist https://github.com/mrmees/open-android-auto.git <tmp>` -> success; `in-pack: 269`, `.git/objects: 196K`

## 2026-03-22 — Presync salvage extraction

Date / Session: 2026-03-22 / salvage-presync-corrections

What Changed:
- Recovered the sensor direction corrections from the preserved `wip/root-main-presync-20260322` branch into current `main` lineage: `SensorRequest` is now documented as Phone -> HU, while `SensorStartResponse`, `SensorEventIndication`, and `SensorError` are documented as HU -> Phone in the canonical protos and docs
- Recovered the nav distance-unit correction slice: `DistanceDisplayUnit` now reflects the 0-7 mapping with `KILOMETERS_P1`, `MILES_P1`, `FEET`, and `YARDS`, and the checked-in non-media baselines no longer label value `6` as `DISTANCE_UNIT_UNKNOWN_6`
- Added [docs/plans/2026-03-22-salvage-presync-corrections.md](plans/2026-03-22-salvage-presync-corrections.md) to document the salvage plan and verification steps

Why:
- The preserved presync branch mixed a few valid corrections with several bad regressions, including deleting the live dist-publish workflow and rewinding later nav-image evidence conclusions
- Pulling that branch wholesale would have damaged current `main`; extracting the two defensible slices preserves the useful work without reintroducing stale conclusions

Status:
- Sensor-direction docs/proto comments are corrected on the salvage branch
- Nav distance-unit enum/docs/baselines are corrected on the salvage branch
- The broader presync branch remains intentionally unmerged because it also reverts current `main` truths

Next Steps:
1. Review the two salvage commits and fast-forward or cherry-pick them onto `main` if they still look right
2. Leave the rest of `wip/root-main-presync-20260322` unmerged unless a future pass identifies another narrowly extractable slice with fresh verification
3. If merged, consider deleting the `wip/root-main-presync-20260322` branch after confirming nothing else in it is needed

Verification:
- `mkdir -p /tmp/oaa_sensor_verify && protoc --proto_path=. --cpp_out=/tmp/oaa_sensor_verify oaa/sensor/SensorRequestMessage.proto oaa/sensor/SensorStartResponseMessage.proto oaa/sensor/SensorEventIndicationMessage.proto oaa/sensor/SensorErrorMessage.proto` -> success
- `rg -n "Sent by the phone to request sensor data|Sent by the head unit to acknowledge a sensor subscription request|Sent by the head unit to deliver sensor data to the phone|Direction: HU -> Phone\\.|SensorRequest \\| Phone -> HU|SensorStartResponse \\| HU -> Phone|SensorEventIndication \\| HU -> Phone|SensorError \\| HU -> Phone" oaa/sensor docs/channels/sensor.md docs/channel-map.md` -> corrected direction markers present
- `mkdir -p /tmp/oaa_nav_verify && protoc --proto_path=. --cpp_out=/tmp/oaa_nav_verify oaa/navigation/NavigationTurnEventMessage.proto oaa/navigation/InstrumentClusterMessages.proto` -> success
- `rg -n "DISTANCE_UNIT_UNKNOWN_6|7 values \\(0-6\\)" oaa/navigation docs/channels/nav.md analysis/baselines/non_media/{active-navigation,general}.normalized.json` -> no matches
- `rg -n "KILOMETERS_P1|MILES_P1|DISTANCE_UNIT_FEET|DISTANCE_UNIT_YARDS" oaa/navigation/NavigationTurnEventMessage.proto docs/channels/nav.md analysis/baselines/non_media/{active-navigation,general}.normalized.json` -> corrected names present

## 2026-03-29 — 16.4 manual JADX salvage checkpoint

Date / Session: 2026-03-29 / manual-jadx-16-4-salvage

What Changed:
- Created `analysis/aa_apk_16.4.661034_apkm/manual-jadx/`
- Copied recovered single-class decompiles for `rcp`, `rco`, `rdt`, `red`, and `rcn` into `analysis/aa_apk_16.4.661034_apkm/manual-jadx/defpackage/`
- Added `analysis/aa_apk_16.4.661034_apkm/manual-jadx/PROVENANCE.md` documenting the source APK tree, the interrupted-session `/tmp/jadx-*` origins, and the current reproduction gap

Why:
- The normal bulk tree under `analysis/aa_apk_16.4.661034_apkm/jadx-output/sources/defpackage/` leaves key methods stubbed or partially lost for these classes
- The stronger recoveries were sitting only in `/tmp`, which is not durable or repo-local
- Preserving them under a version-scoped path makes later protocol analysis reproducible enough to resume from the repo, even though the exact JADX argv is not yet closed

Status:
- Stable repo-local copies now exist for the recovered 16.4 classes
- The preserved files materially improve on the bulk checked-in JADX output for `rcp`, `rcn`, and `red`, and remove the bulk-tree method-dump stubs for `rcp`, `red`, `rcn`, and `rco.write(...)`
- Exact generator provenance is still incomplete: fresh local `jadx --single-class ...` attempts against the correct dex files did not byte-match these preserved copies

Next Steps:
1. If these classes become evidence-bearing for docs or proto work, cite the new `manual-jadx` paths instead of transient `/tmp` paths
2. If exact reproducibility matters, keep investigating which JADX mode/version produced the stronger `goto`-style recoveries
3. Consider whether any analysis notes should explicitly link to this salvage tree now that the paths are stable

Verification:
- `find analysis/aa_apk_16.4.661034_apkm/manual-jadx -maxdepth 2 -type f | sort` -> expected six files present (`PROVENANCE.md` plus five recovered classes)
- `rg -n "UnsupportedOperationException|Method dump skipped" analysis/aa_apk_16.4.661034_apkm/jadx-output/sources/defpackage/{rcp,rco,rdt,red,rcn}.java` -> bulk tree still shows skipped-method / stub evidence for all five classes
- `rg -n "UnsupportedOperationException|Method dump skipped" analysis/aa_apk_16.4.661034_apkm/manual-jadx/defpackage/{rcp,rco,rdt,red,rcn}.java` -> only expected `isOpen()` stub in `rco` plus the domain-level `Non-suspendable service` throw in `rdt`; recovered method-dump stubs are gone
- `git diff --check -- analysis/aa_apk_16.4.661034_apkm/manual-jadx` -> clean
- `jadx --single-class defpackage.red --single-class-output <tmp> analysis/aa_apk_16.4.661034_apkm/jadx-output/resources/classes.dex` -> completed, but output differed from preserved `manual-jadx/defpackage/red.java`
- `jadx --single-class defpackage.rcn --single-class-output <tmp> analysis/aa_apk_16.4.661034_apkm/jadx-output/resources/classes2.dex` -> completed, but output differed from preserved `manual-jadx/defpackage/rcn.java`
- `jadx --single-class defpackage.rdt --single-class-output <tmp> analysis/aa_apk_16.4.661034_apkm/jadx-output/resources/classes.dex` -> completed, but output differed from preserved `manual-jadx/defpackage/rdt.java`
- `jadx --show-bad-code --comments-level debug --decompilation-mode simple --single-class defpackage.red --single-class-output <tmp> analysis/aa_apk_16.4.661034_apkm/jadx-output/resources/classes.dex` -> completed, but output still differed from preserved `manual-jadx/defpackage/red.java`

## 2026-07-15 — Android Auto 17.3 protobuf metadata detection

Date / Session: 2026-07-15 / 17.3-static-protobuf-ingest

What Changed:
- Replaced frequency-only protobuf descriptor-class selection with detection of the stable `RawMessageInfo` constructor call shape: `(default instance, compact schema string, object array)`
- Retained the previous total-constructor-count heuristic only as a best-effort fallback for incomplete decompiles
- Added a regression that reproduces the 17.3 failure mode where an unrelated helper class has more total constructor calls than the real descriptor class
- Updated the roadmap with the 17.3 static-ingest, canonical schema-graph matching, and message-dispatch milestones

Why:
- Android Auto 17.3 instantiates the unrelated `yxw` helper 2,050 times and the real protobuf metadata class `aboi` 2,028 times, so the previous "most instantiated class" heuristic selected the wrong type
- Recognizing the semantic constructor shape recovers protobuf-lite metadata without requiring a running phone/head-unit session or wire capture

Status:
- The detector now identifies the 17.3 obfuscated protobuf runtime as base `abmx`, descriptor `aboi`, and enum interface `abnb`
- A full static scan of the local 17.3 JADX tree recovers 1,961 protobuf classes, 1,957 decoded descriptors, 134 protobuf enums, and 9,500 switch-map entries
- Canonical schema-graph matching and dispatch constraint propagation remain the next implementation increment

Next Steps:
1. Compile `oaa/**/*.proto` into a descriptor set and emit normalized canonical message signatures
2. Emit field-number-labelled APK message/enum reference edges from `RawMessageInfo` object arrays
3. Resolve ambiguous structural matches with channel, message-ID, direction, and cross-version anchors

Verification:
- `PYTHONPATH=. /tmp/open-android-auto-test-venv/bin/pytest analysis/tools/apk_indexer/tests/test_extract.py -q` -> 9 passed
- `PYTHONPATH=. /tmp/open-android-auto-test-venv/bin/pytest analysis/tools/apk_indexer/tests -q` -> 25 passed
- `_detect_proto_names(Path('/tmp/android-auto-17.3-jadx'))` -> `('defpackage', 'abmx', 'aboi', 'abnb')`
- `extract_signals(Path('/tmp/android-auto-17.3-jadx'), scope='all')` -> 1,961 protobuf classes, 1,957 decoded descriptors, 134 protobuf enums, and 9,500 switch-map entries

## 2026-07-15 — Android Auto 17.3 static schema-graph resolver

Date / Session: 2026-07-15 / 17.3-schema-graph-resolver

What Changed:
- Added `analysis/tools/proto_schema_matcher/`, which compiles the canonical `oaa/` descriptor graph and normalizes it against APK protobuf-lite schema metadata
- Added global structural uniqueness checks so duplicate canonical schemas are not incorrectly promoted as unique mappings
- Added conservative control-channel dispatch observations using the repository's existing message-ID map; observations become mappings only when the APK class is structurally compatible
- Decoded field-number-linked message/enum/map references from the `RawMessageInfo` object-array cursor and added iterative message-edge constraint propagation
- Generated machine-readable and Markdown Android Auto 17.3 reports under `analysis/reports/cross-version/17-3-schema-match.*`

Why:
- Local field tuples cannot distinguish empty, tiny, or deliberately parallel message schemas
- Global message-reference edges and dispatch IDs add independent constraints without requiring a phone, head unit, emulator, or capture session
- Explicit conflict reporting prevents incomplete decompilation or schema drift from being mistaken for a successful name recovery

Status:
- The 17.3 run compares 423 canonical messages with 1,957 decoded APK messages, 274 canonical message edges, and 1,273 recovered APK field-linked edges
- 77 mappings are resolved: 9 high-confidence dispatch-backed mappings and 68 medium-confidence mappings (61 globally unique structures plus 7 graph-resolved collisions)
- Graph resolution recovered `CarProperty`, `NavigationDestination`, `NavigationNotification`, `NavigationRemainingDistance`, `NavigationStepDistance`, `RadioProgramSelector`, and `UiConfigData`
- 13 constraint conflicts are retained in the report for drift/reference-parser triage; 259 messages remain structurally ambiguous and 74 have no exact 17.3 shape match

Next Steps:
1. Identify service/channel context around non-control handlers and reuse the existing service message-ID map for more dispatch anchors
2. Audit the 13 edge conflicts against raw JADX metadata, starting with canonical messages that had one local structural candidate
3. Add enum-domain edges and 16.2/16.4 cross-version anchors, then rerun fixed-point constraint propagation

Verification:
- `PYTHONPATH=. /tmp/open-android-auto-test-venv/bin/pytest analysis/tools/apk_indexer/tests analysis/tools/proto_schema_matcher/tests -q` -> 34 passed
- Documented `proto_schema_matcher` 17.3 smoke command -> success; 423 canonical messages, 1,957 APK messages, 60 static dispatch observations, 77 resolved mappings
- Generated report summary -> 9 high confidence, 68 medium confidence, 7 graph-resolved, 13 constraint conflicts, 259 ambiguous, 74 not found
- `UiConfigData` graph evidence -> local shape had 3 APK candidates and field targets narrowed it to `xmn`, whose fields 1 and 2 are repeated `xmp`

## 2026-07-15 — Android Auto 17.3 service-aware schema refinement

Date / Session: 2026-07-15 / 17.3-service-aware-schema-refinement

What Changed:
- Extended static dispatch extraction to handlers with an unambiguous `rpq` service token and to validation logs that spell out protobuf message names
- Added field-level schema differences for cases where explicit handler identity and the canonical local schema disagree
- Corrected input message IDs 0x8002/0x8003 to `InputBindingRequest`/`InputBindingResponse` and sensor message ID 0x8001 to the non-retracted `SensorRequest`
- Corrected `BluetoothPairingResponse.status` to the shared Status enum and recorded the 17.3-required `InputEventIndication.timestamp`
- Preserved a dispatch-backed identity when a recovered child edge conflicts, while retaining the disagreement as an explicit report status

Why:
- Service-local IDs are reusable across Android Auto channels, so a service token is required before they can safely identify a message
- The three initial dispatch/schema conflicts proved to be actionable catalog evidence: one stale retracted name, one enum declared as `int32`, and one 17.3 required-field change
- Named handler logs provide identity independently of schema shape and therefore resolve collisions without runtime testing

Status:
- The 17.3 run resolves 88 mappings: 25 high-confidence dispatch-backed mappings and 63 medium-confidence mappings
- Service and named-log extraction contributes input, sensor, video, Wi-Fi, Bluetooth, and radio anchors; radio case IDs are retained from switch branches
- All explicit dispatch/schema conflicts are reconciled; 12 graph-edge conflicts remain for separate reference/drift triage
- `BluetoothPairingResponse -> xfn`, `InputEventIndication -> xhp`, and `SensorRequest -> xlq` are now high-confidence mappings

Next Steps:
1. Audit the 12 remaining graph-edge conflicts against their raw object arrays and field declarations
2. Add canonical/APK enum-domain matching and use enum field references as graph constraints
3. Add 16.2/16.4 cross-version anchors for tiny and empty schemas that remain structurally ambiguous

Verification:
- `PYTHONPATH=. /tmp/open-android-auto-test-venv/bin/pytest analysis/tools/proto_schema_matcher/tests analysis/tools/proto_stream_validator/tests/test_message_map.py -q` -> 32 passed
- Documented 17.3 matcher smoke command -> success; 423 canonical messages, 1,957 APK messages, 80 static observations, 88 resolved mappings
- Generated report summary -> 25 high confidence, 63 medium confidence, 7 graph-resolved, 12 constraint conflicts, 251 ambiguous, 72 not found
- Dispatch/schema conflict count -> 0 after catalog corrections

## 2026-07-15 — Android Auto 17.3 conservative static extraction complete

Date / Session: 2026-07-15 / 17.3-conservative-static-extraction

What Changed:
- Added numeric superclass service-ID inference for Bluetooth, navigation, phone status, radio, Wi-Fi projection, car control, and car-local media handlers
- Added conservative canonical-name log anchors, including builder-to-literal-send correlation, while requiring structural compatibility before accepting identity
- Resolved multiplexed protobuf-lite enum verifier members to real enum classes, normalized generated `UNRECOGNIZED` values and proto3 zero sentinels, and matched enum numeric domains
- Added bidirectional field-edge propagation from dispatch-backed or globally unique parents and retained an evidence check so unknown enum targets cannot win by elimination
- Excluded explicitly retracted proto files from the canonical graph and emitted 30 direct parent/child schema differences for the remaining constraint conflicts
- Recovered the Android Auto 17.3 structured `VehicleEnergyModelData` schema from `xeq`/`xer`/`xep` metadata and the diagnostic formatter

Why:
- DEX protobuf-lite metadata contains field numbers, wire types, requiredness, oneofs, and message/enum references even though source names and descriptor strings are removed
- Explicit endpoint service IDs and semantic logs provide the independent identity anchors needed to turn structural candidates into names without a live session
- Parent-to-child propagation extracts otherwise ambiguous one-field and empty messages when their exact field position under a trusted parent is known
- The remaining unresolved set no longer has equivalent low-risk local evidence; it needs schema reconstruction, cross-version identity, stronger decompilation, or runtime traffic

Status:
- Active canonical graph: 421 messages and 117 enums after excluding retracted files
- Android Auto 17.3 graph: 1,957 decoded messages and 134 decoded enums
- 144 message mappings resolved: 39 high-confidence dispatch-backed and 105 medium-confidence mappings, including 50 graph-resolved mappings
- 13 globally unique enum numeric-domain mappings recovered
- 129 static dispatch observations were considered; explicit dispatch/schema conflict count is zero
- 12 parent constraint conflicts remain, described by 30 direct child-schema differences; 196 messages remain structurally ambiguous and 69 have no exact current-catalog shape

Notable 17.3 Catalog Corrections:
- `BluetoothPairingResponse.status`, `BluetoothAuthenticationResult.status`, and car-control response status fields now use the shared Status enum
- `InputEventIndication.timestamp`, `PhoneStatusInput.input_type`, and `PhoneInputType.action` are required in 17.3
- Sensor 0x8001 resolves to active `SensorRequest`, not retracted `SensorStartRequestMessage`
- `VehicleEnergyModelData` now contains battery level/capacity, HVAC status, external temperature, and battery temperature through recovered nested messages

Next Steps:
1. Reconstruct the 12 remaining schema-drift families from the generated direct child-edge table
2. Bring in 16.2/16.4 graph anchors for the 196 locally ambiguous messages
3. Re-decompile the unresolved multiplexed enum verifier switch bodies with a lower-level DEX tool where the extra enum edges justify the effort

Verification:
- `PYTHONPATH=. /tmp/open-android-auto-test-venv/bin/pytest analysis/tools/apk_indexer/tests analysis/tools/proto_schema_matcher/tests analysis/tools/proto_stream_validator/tests -q` -> 86 passed
- Documented 17.3 matcher smoke command -> success; 421 canonical messages, 117 canonical enums, 1,957 APK messages, 134 APK enums
- Generated report summary -> 144 resolved, 39 high confidence, 105 medium confidence, 50 graph-resolved, 13 unique enum domains
- Generated conflict audit -> 0 dispatch/schema conflicts, 12 parent constraint conflicts, 30 direct child-schema differences

## 2026-07-16 — Android Auto 17.3 protocol-facing schema-drift reconstruction

Date / Session: 2026-07-16 / 17.3-schema-drift-reconstruction

What Changed:
- Reconstructed `NavigationNextTurnDistanceEvent` directly from the 17.3
  `NavigationCurrentPosition` sender: step distance, repeated destination
  distances, and current-road text
- Reconstructed `WifiSetupInfo` from its RFCOMM logger/consumer: protocol
  version, setup token, WPP IP/port endpoint, and access-point info
- Corrected the required 17.3 `SensorTypeEntry` field and removed the duplicate
  `Sensor` child wrapper from `SensorChannel`
- Identified `xlv` as the 18-field 17.3 `ChannelDescriptor`, including required
  channel ID and the CarLocalMedia, BufferedMedia, and CarIntent service markers
- Reconstructed the nested 17.3 navigation and radio SDP configs from their
  service-discovery consumers and updated permanent channel/interaction docs
- Regenerated the 17.3 JSON and Markdown schema-match reports

Why:
- The outer protobuf schemas already matched, but stale nested types prevented
  graph propagation and hid current field semantics
- Direct construction/consumption sites expose semantic names that protobuf-lite
  metadata alone cannot recover
- Several remaining local-shape candidates are demonstrably unrelated telemetry
  or radio messages, so forcing them would reduce catalog accuracy

Status:
- Active canonical graph: 422 messages and 117 enums
- Android Auto 17.3 graph: 1,957 decoded messages and 134 decoded enums
- 155 mappings resolved: 39 high-confidence and 116 medium-confidence, including
  55 graph-resolved mappings
- Constraint-conflict parents fell from 12 to 6; direct child differences fell
  from 30 to 19; explicit dispatch/schema conflicts remain zero
- The six residual families are capability/phone, handwriting, transport
  security, and Wi-Fi Direct shapes without a trustworthy 17.3 identity anchor

Next Steps:
1. Use 16.2/16.4 class lineage or lower-level DEX references to identify the six
   remaining conflict families before changing their canonical schemas
2. Add cross-version anchors for the 194 locally ambiguous messages, prioritizing
   protocol-facing children of the now-resolved ChannelDescriptor tree
3. Treat the current 17.3 conflict candidates as hypotheses, not mappings; `xla`
   is already proven to be radio song metadata rather than Wi-Fi Direct config

Verification:
- `protoc --proto_path=. --descriptor_set_out=/tmp/oaa-proto-check/all.pb $(find oaa -name '*.proto' -print | sort)` -> success
- All `oaa/**/*.audit.yaml` files parse with PyYAML
- `PYTHONPATH=. /tmp/open-android-auto-test-venv/bin/pytest analysis/tools/apk_indexer/tests analysis/tools/proto_schema_matcher/tests analysis/tools/proto_stream_validator/tests -q` -> 86 passed
- Generated report summary -> 155 resolved, 39 high confidence, 116 medium confidence, 55 graph-resolved, 13 unique enum domains
- Generated conflict audit -> 0 dispatch/schema conflicts, 6 parent constraint conflicts, 19 direct child-schema differences

## 2026-07-16 — Android Auto 17.3 class-lineage invalidation anchors

Date / Session: 2026-07-16 / 17.3-class-lineage-anchors

What Changed:
- Added curated 16.2 → 16.4 → 17.3 lineage evidence for the six residual
  structural-conflict families under `analysis/lineage/`
- Extended `proto_schema_matcher` with confirmed and invalidated lineage anchors;
  invalidated identities quarantine every same-shape candidate instead of
  allowing graph propagation to assign a protocol name
- Regenerated the 17.3 JSON and Markdown reports with a dedicated lineage table
  and explicit invalidation counts

Why:
- Exact protobuf structure and stable obfuscated-class order establish class
  continuity, but they do not establish semantics when Android Auto bundles
  unrelated Google libraries
- Direct call sites identify the six historical mappings as Google Surveys
  request context, GoogleAuth data/telemetry, or radio song metadata
- Quarantining those identities also removes three child mappings that had been
  inferred only from the invalid parent graphs

Status:
- All six former constraint-conflict parents are now `lineage_invalidated`; no
  residual parent or direct-child constraint conflicts remain
- The conservative 17.3 baseline is 152 mappings: 39 high-confidence and 113
  medium-confidence, including 52 graph-resolved mappings
- `CapabilityFlag -> abuf`, `CapabilityPair -> abuq`, and
  `InputModelDescriptor -> abvb` were withdrawn because their only identity
  evidence came from invalidated Surveys parent messages
- The invalidated legacy lineages are:
  `aafl -> aayi -> abud`, `aagb -> aayy -> abut`,
  `aago -> aazl -> abvg`, `aafx -> aayu -> abup`,
  `aajh -> abce -> abxz`, and `was -> wtf -> xla`

Next Steps:
1. Quarantine/retract the affected canonical proto definitions and stale
   `class_mapping.yaml` entries so older tooling cannot consume the invalid names
2. Reconstruct real protocol-facing capability, transport-security, and Wi-Fi
   schemas only from trusted service/channel parents or wire evidence
3. Extend class-lineage anchoring to legitimate tiny/empty protocol collisions

Verification:
- `PYTHONPATH=. /tmp/open-android-auto-test-venv/bin/pytest analysis/tools/proto_schema_matcher/tests -q` -> 27 passed
- `PYTHONPATH=. /tmp/open-android-auto-test-venv/bin/pytest analysis/tools/apk_indexer/tests analysis/tools/proto_schema_matcher/tests analysis/tools/proto_stream_validator/tests -q` -> 91 passed
- New lineage YAML plus all 160 production `oaa/**/*.audit.yaml` files parse with PyYAML
- Documented 17.3 matcher smoke command with `--lineage-yaml` -> success; 422 canonical messages, 1,957 APK messages, 129 dispatch observations, and 6 lineage anchors
- Generated report summary -> 152 resolved, 39 high confidence, 113 medium confidence, 52 graph-resolved, 6 lineage invalidations
- Generated conflict audit -> 0 dispatch/schema conflicts, 0 parent constraint conflicts, 0 direct child-schema differences

## 2026-07-16 — Bundled-library proto quarantine and Wi-Fi correction

Date / Session: 2026-07-16 / bundled-library-proto-quarantine

What Changed:
- Retracted `CapabilityData`, `PhoneCapabilitiesMessage`, `InputModelData`,
  `ConnectionConfigurationData`, and `WifiDirectConfigData` at the audit-file
  boundary while retaining their source as research history
- Made the schema validator omit mappings whose proto audit is retracted
- Removed false fields 6-13 from `WifiSecurityResponse`; fields 1-5 remain
  capture-backed, and the stale `wan`/`waf`/`wss` mapping was cleared
- Corrected service-discovery, ping-maintenance, Wi-Fi, protocol-reference, and
  cross-version documentation that exposed the invalid schemas as protocol data
- Regenerated the 17.3 schema-match and 16.2 validation reports

Why:
- The exact lineages proved that these were stable protobufs, but their call
  sites place them in bundled GoogleAuth/Google Surveys rather than Android Auto
- `WifiSecurityResponse` is a real wire message, so retracting the whole message
  would discard useful data; only its radio-derived extension needed removal
- Keeping retracted mappings in active validation allowed structurally correct
  unrelated classes to continue contaminating reports and graph propagation

Status:
- The active canonical graph fell from 422 messages/117 enums to 373 messages/111
  enums by excluding 49 non-protocol messages and 6 enums
- The conservative 17.3 baseline is 151 mappings: 39 high-confidence and 112
  medium-confidence, including 51 graph-resolved mappings
- `RadioSongMetadata -> xla` is now a unique structural mapping; it had previously
  collided with the false `WifiDirectConfig` alias
- The 16.2 validator now loads 215 active mappings (203 mapped for 16.2) and no
  longer reports the retracted families or false `WifiSecurityResponse` APK class

Next Steps:
1. Trace legitimate unresolved children directly from dispatch-backed Android
   Auto service/channel parents, prioritizing the 166 structural collisions
2. Use captures or trusted RFCOMM handlers to determine whether
   `WifiSecurityResponse` has any real fields beyond the capture-backed 1-5
3. Regenerate the legacy protocol-reference document from active audited protos
   rather than continuing to patch its 16.1 auto-generated snapshot

Verification:
- `protoc --proto_path=. --descriptor_set_out=/tmp/oaa-proto-quarantine-check/all.pb $(find oaa -name '*.proto' -print | sort)` -> success
- `PYTHONPATH=. /tmp/open-android-auto-test-venv/bin/pytest analysis/tools/proto_schema_matcher/tests analysis/tools/proto_schema_validator/tests -q` -> 29 passed
- `PYTHONPATH=. /tmp/open-android-auto-test-venv/bin/pytest analysis/tools/apk_indexer/tests analysis/tools/proto_schema_matcher/tests analysis/tools/proto_schema_validator/tests analysis/tools/proto_stream_validator/tests -q` -> 93 passed
- All 6 changed audit sidecars validate against `docs/verification/audit-schema.json`
- Documented 17.3 matcher smoke command -> success; 373 canonical messages, 111 canonical enums, 1,957 APK messages, and 6 lineage anchors
- Generated 17.3 report -> 151 resolved, 39 high confidence, 112 medium confidence, 51 graph-resolved, and `RadioSongMetadata -> xla`
- 16.2 validator smoke -> 215 active mappings, 203 with a 16.2 class, 24 errors and 12 warnings after excluding retractions

## 2026-07-16 — Trusted-parent frontier and 17.3 blended UI recovery

Date / Session: 2026-07-16 / trusted-parent-class-lineage-frontier

What Changed:
- Fixed schema-matcher fixed-point propagation so a canonical alias with one
  APK candidate can inherit identity from a trusted parent, and graph-resolved
  parents can continue constraining their descendants
- Added machine-readable graph provenance (canonical/APK parent, field number,
  target edge, and relation) to every graph-resolved mapping and a separate
  report of child schema differences rooted in trusted parents
- Corrected `AudioConfig` fields 1-3 to proto2 `required`,
  `PingConfiguration` fields 1-2 to ordinary proto3 scalars, and
  `VendorExtensionChannel.name` to required in 17.3
- Recovered the 17.1/17.3 blended-UI subtree under
  `AdditionalVideoConfig`: display insets, corner radii, native UI elements,
  and their Rect-style positions; removed the false `VideoResolutionRange`
  identity and corrected the historical class mappings
- Recorded the one remaining trusted-parent version delta: 17.3 `VideoConfig`
  (`xmz`) omits field 7, while the optional field remains for 16.x wire
  compatibility

Why:
- Thirteen exact child identities were hidden because the matcher treated an
  already-single candidate as unresolved when its canonical shape had aliases
- Previous reports stated only that a mapping was graph-resolved; they did not
  preserve the edge that justified it, making independent review needlessly
  difficult
- Phone-side Rect construction in both 17.1 and 17.3 directly contradicts the
  old “minimum/maximum/preferred resolution” names for AdditionalVideoConfig
  fields 1-3 and exposes field 8 without a live projection session

Status:
- Active canonical graph: 376 messages and 112 enums; Android Auto 17.3 graph:
  1,957 decoded messages and 134 enums
- 175 mappings resolved: 39 high-confidence and 136 medium-confidence,
  including 73 graph-resolved mappings; 149 ambiguous structural mappings and
  52 not-found schemas remain
- Newly resolved protocol-facing identities include `CarControlChannel -> xgb`,
  `CarActionEntry -> xdx`, `SensorTypeEntry -> xls`, `AudioConfig -> xfb`,
  `AdditionalVideoConfig -> xml`, `BlendedUIConfig -> xfi`,
  `DisplayCornerRadii -> xgs`, `NativeUIElement -> xir`,
  `UIElementPosition -> xlh`, and `PingConfiguration -> abmh`
- No dispatch/schema, hard-edge, or constraint conflicts remain; the trusted
  parent child-delta report contains only the intentional VideoConfig field-7
  compatibility difference

Next Steps:
1. Trace the remaining 149 structural collisions from cross-version parent
   graphs or direct semantic consumers; do not promote context-free unique
   shapes as semantic proof
2. Recover the symbolic names for `NativeUIElementType` values 1-3 from an
   un-obfuscated API surface or wire/callback behavior
3. Decide whether downstream generated APIs need an explicit versioned
   `VideoConfig` view, rather than removing the backward-compatible field 7

Verification:
- `protoc --proto_path=. --descriptor_set_out=/tmp/oaa-proto-frontier-check/all.pb $(find oaa -name '*.proto' -print | sort)` -> success
- `PYTHONPATH=. /tmp/open-android-auto-test-venv/bin/pytest -q analysis/tools/apk_indexer/tests analysis/tools/proto_schema_matcher/tests analysis/tools/proto_schema_validator/tests analysis/tools/proto_stream_validator/tests` -> 94 passed
- All four changed audit sidecars validate against
  `docs/verification/audit-schema.json`
- Documented 17.3 matcher smoke command -> success; 376 canonical messages,
  1,957 APK messages, 129 dispatch observations, and 6 lineage anchors
- Generated report -> 175 resolved, 39 high confidence, 136 medium confidence,
  73 graph-resolved, 13 unique enum domains, and 1 intentional trusted-parent
  child schema delta
- 16.2 Layer-1 validator -> 215 active mappings, 203 with a 16.2 class, 24
  errors and 13 warnings; the added warning is expected because blended UI
  field 8 is new after 16.2

## 2026-07-24 — Android Auto 17.3 durable multi-display analysis

Date / Session: 2026-07-24 / 17.3-multi-display-durable-research

What Changed:
- Recovered the Android Auto `17.3.662804-release` APKM bundle from `/mnt/e/tmp`
  and copied it into the ignored, versioned local analysis directory
  `analysis/aa_apk_17.3.662804_apkm/`
- Extracted and preserved `base.apk`, recorded both SHA-256 identities, and
  generated a durable JADX 1.5.5 tree with 26,115 Java files
- Added local `PROVENANCE.md` covering bundle identity, tool versions,
  decompilation status, source anchors, and reproduction commands
- Added `analysis/reports/multi-display/android-auto-17.3.md` with exact 17.3
  source evidence for per-display `CarDisplayId`, `Surface`, video endpoint,
  configuration, encoder, focus, and input-binding state
- Updated the schema-matcher smoke command to use the durable local tree and to
  write fresh results into the ignored validation directory before promotion
- Updated the roadmap to make live MAIN + CLUSTER + AUXILIARY verification an
  explicit next step

Why:
- The previous 17.3 source lived under `/tmp`, so schema reports survived but
  source-level call-flow research depended on a transient decompile
- Multi-display implementation planning for OpenAuto Prodigy needs a durable,
  independently reviewable answer to whether AA uses separate displays or one
  cropped panoramic canvas
- Fresh 17.3 source proves that AA creates separate logical display/video
  instances; retaining the full ignored tree and a tracked evidence summary
  prevents that conclusion from being trapped in chat history

Status:
- The APKM hash is
  `1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344`,
  matching the existing 17.3 cross-version report; `base.apk` is
  `5557827f259898bdab97b489e1a0aef937fd6ec711d87361cf25d51af6f48619`
- 17.3 `itq` creates an `iti`/`itt` display/video pair for every video-capable
  `ChannelDescriptor`; `itt` owns the display's surface/config/encoder state,
  and `jdc` maps it to VIDEO, VIDEO_CLUSTER, or VIDEO_AUXILIARY
- 17.3 `jnb` enforces unique display IDs, display 0 as MAIN, exactly one MAIN,
  at most one CLUSTER, and exactly one matching input config per display
- The architecture conclusion is separate logical displays and media streams,
  not one HU-cropped mega-canvas; blended UI/insets are intra-display layout
- JADX completed with 57 errors, but all multi-display anchor classes used by
  the report are readable
- A fresh matcher run from the durable tree recovered 1,957 APK messages, 134
  enums, 135 observations, and 176 mappings (39 high, 137 medium). Its outputs
  are preserved under `validation/` and were not promoted because they differ
  from the committed 175/129 baseline at `BluetoothChannel`,
  `PhoneConnectionConfig`, and `WifiInfoResponse`

Next Steps:
1. Capture a live 17.3 MAIN + CLUSTER + AUXILIARY session and correlate distinct
   channel IDs, AV setup handshakes, media streams, focus changes, and logcat
   `CarDisplayId` activity launches
2. Review the three fresh-matcher delta rows before deciding whether the more
   complete JADX evidence should update the canonical 17.3 schema report
3. Translate the proven model into a Prodigy `DisplayRegistry` design with one
   video session/decoder/sink/input route per logical display, beginning with
   native semantic cluster widgets

Verification:
- Android reverse-engineering dependency check -> Java 21 and JADX 1.5.5 OK;
  optional Vineflower, dex2jar, and apktool absent
- Fingerprint of the APKM bundle -> native Android Java/Kotlin, Android Auto
  `17.3.662804-release`, suitable for JADX
- `sha256sum analysis/aa_apk_17.3.662804_apkm/input/android-auto-17.3.662804-release.apkm analysis/aa_apk_17.3.662804_apkm/input/base.apk` -> hashes match the values above
- JADX wrapper against the preserved `base.apk` -> usable partial success,
  26,115 Java files, 57 errors
- Durable-path `proto_schema_matcher` smoke command -> success; 376 canonical
  messages, 112 canonical enums, 1,957 APK messages, 134 APK enums, 135 static
  observations, 6 lineage anchors, and 176 resolved mappings
- Source-anchor existence checks for `jdc.java`, `itt.java`, `itq.java`,
  `iti.java`, `its.java`, and `jnb.java` -> all present
- `git diff --check` -> success
- Path/reference `rg` checks for the new durable path and report -> success; no
  active `/tmp/android-auto-17.3-jadx` smoke path remains

## 2026-07-24 — Prodigy multi-display maintainer handoff

Date / Session: 2026-07-24 / prodigy-multi-display-maintainer-handoff

What Changed:
- Added `analysis/reports/multi-display/prodigy-maintainer-handoff.md`, a
  standalone transfer document for the OpenAuto Prodigy maintainer
- Documented MAIN-only, MAIN + CLUSTER, MAIN + AUXILIARY, combined projected,
  single-display blended-UI, and native semantic-widget configurations
- Separated the multiplexed `ChannelDescriptor.channel_id` from the
  `CarDisplayId` carried in `AVChannel` field 6 and its matching
  `InputChannelConfig.display_id`
- Added a proposed Prodigy `DisplayRegistry`/`DisplaySession` model, archived
  integration seams, staged delivery order, acceptance tests, and failure modes
- Linked the handoff from `analysis/reports/multi-display/README.md`

Why:
- A Prodigy implementation can route and decode multiple streams incorrectly
  if it assumes one panoramic phone canvas or conflates a wire channel ID with
  a logical display ID
- The maintainer needs a self-contained document that preserves both the
  confirmed 17.3 evidence and the boundary between static proof, implementation
  recommendations, and unverified runtime behavior

Status:
- The maintainer handoff confirms separate logical display/video instances,
  surfaces, endpoints, focus state, and input matching in Android Auto 17.3
- Static topology support is distinguished from the still-missing simultaneous
  MAIN + CLUSTER + AUXILIARY wire capture
- No protobuf schema or Prodigy runtime code changed; the historical
  `AVChannel` field-6 name is recorded as a future API/naming decision only
- The current roadmap already prioritizes the required live multi-display
  capture, so this documentation pass did not change sequencing

Next Steps:
1. Give `analysis/reports/multi-display/prodigy-maintainer-handoff.md` to the
   Prodigy maintainer and map its responsibility-level seams to the current
   Prodigy source tree
2. Capture a live 17.3 MAIN + CLUSTER + AUXILIARY session to confirm concurrent
   channel lifecycle, stream separation, focus transitions, and content policy
3. Decide in a compatibility-focused proto/API pass whether `AVChannel` field 6
   should be renamed from `channel_id` to `display_id`

Verification:
- All 14 repository files linked by the maintainer handoff -> present
- Handoff evidence-anchor check -> all 14 cited 17.3 class/line spans present in
  the document
- Fresh JADX semantic check -> `xik.g` and `xik.h` are read before
  `new CarDisplayId(i4)` in `itq.java:213-220`
- Fresh JADX topology-message check -> unique display IDs, MAIN ID 0, MAIN type,
  one MAIN, at most one CLUSTER, and exactly one matched input all present in
  `jnb.java`
- `git diff --check` -> success

## 2026-07-24 — Preserve Android Auto 17.3 display evidence baseline

Date / Session: 2026-07-24 / android-auto-17.3-update-task-1

What Changed:
- Preserved the durable 17.3 APK/JADX provenance and source-cited multi-display
  reports as the committed evidence checkpoint for subsequent update work
- Documented the matcher smoke command against the ignored, version-scoped
  JADX tree and retained its fresh output only under the ignored `validation/`
  directory
- Reviewed the three fresh-matcher deltas without changing any canonical proto
  claims or replacing the committed cross-version report

Why:
- Later 17.3 analysis needs reproducible local source evidence while retaining
  the already reviewed 175-mapping/129-observation report as its stable
  comparison baseline
- The fresh output has more recovered evidence, but its three changed rows need
  deliberate review before it can affect canonical protocol documentation

Status:
- APKM SHA-256:
  `1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344`
- `base.apk` SHA-256:
  `5557827f259898bdab97b489e1a0aef937fd6ec711d87361cf25d51af6f48619`
- Durable JADX tree contains 26,115 Java files; all six required display
  anchors (`jdc`, `itt`, `itq`, `iti`, `its`, and `jnb`) are present
- Fresh matcher result: 1,957 APK messages, 134 APK enums, 135 dispatch
  observations, and 176 resolved mappings (39 high, 137 medium)
- Delta disposition: retain
  `analysis/reports/cross-version/17-3-schema-match.{json,md}` as canonical
  for this task and do not stage the fresh ignored output. Relative to that
  baseline, fresh `oaa.proto.data.BluetoothChannel` changes from
  `unique_structural` / `xfp` / `medium` to `constraint_conflict` / `-` /
  `none`; fresh `oaa.proto.data.PhoneConnectionConfig` changes from
  `ambiguous_structural` / `-` / `none` to `graph_resolved` / `xnm` /
  `medium`; and fresh `oaa.proto.messages.WifiInfoResponse` changes from
  `ambiguous_structural` / `-` / `none` to `graph_resolved` / `xnm` /
  `medium`

Next Steps:
1. Task 2: establish the 17.3 Release Dossier from this preserved evidence
   checkpoint
2. Review the three fresh-matcher delta rows before any report promotion or
   canonical proto claim
3. Capture a live MAIN + CLUSTER + AUXILIARY session to validate the static
   multi-display model at runtime

Verification:
- Durable artifact checksum and source-count commands -> expected two hashes
  and 26,115 Java files; all six anchor-file checks passed
- Documented durable-path matcher smoke command -> exit 0; 176 resolved
  mappings and 135 dispatch observations
- Three-row committed-versus-fresh `jq` comparison -> exact disposition
  recorded above; committed report retained as canonical
- Path/reference `rg` checks -> no active `/tmp/android-auto-17.3-jadx` smoke
  path; durable 17.3 paths and display concepts present
- `git diff --check` -> success

## 2026-07-24 — Establish Android Auto 17.3 release dossier

Date / Session: 2026-07-24 / android-auto-17.3-update-task-2

What Changed:
- Added the Android Auto 17.3 release dossier index at
  `analysis/reports/android-auto-17.3-update/README.md`
- Added stable message, service, and runtime-validation matrix contracts, plus
  an empty canonical change manifest
- Seeded the message matrix with DIR-VID, DIR-CC, DIR-SEN, DIR-RAD, and ID
  claim IDs; seeded the service and runtime matrices with their planned claim
  IDs, all at `open`

Why:
- Subsequent 17.3 tasks need one stable, evidence-gated place to update rows
  without creating competing report formats
- The fixed claim IDs and manifest rule preserve traceability from raw evidence
  through accepted canonical publication decisions

Status:
- Dossier layout established; baseline preservation remains `confirmed-static`
  and all later research/publication gates remain `open`
- Resume pointer is Task 3, video message direction and ID audit

Next Steps:
1. Task 3: trace and close the video-direction rows in `message-matrix.md`
2. Task 4: trace and close the car-control direction rows
3. Task 5: trace and close the sensor and radio direction rows

Verification:
- Dossier non-empty-file loop -> all five required dossier files present
- Required message, service, and runtime claim-ID `rg` checks -> all requested
  IDs present
- `git diff --check` -> success

## 2026-07-24 — Close Android Auto 17.3 video message matrix

Date / Session: 2026-07-24 / android-auto-17.3-update-task-3

What Changed:
- Replaced the nine seeded video placeholders with the complete fifteen-row
  `DIR-VID-8007` through `DIR-VID-8015` matrix, including the previously
  omitted hexadecimal `800A` through `800F` claim rows
- Traced every direct 17.3 phone send/receive branch through its complete
  builder/parser block and recorded the concrete protobuf-lite class,
  descriptor field layout, normalized direction, exact source anchors, 16.x
  conflict, status, and future canonical disposition
- Documented inherited raw-ID normalization through `wru.S(raw)` for received
  AudioUnderflow at raw `32779`/`0x800B` and MediaStats at raw
  `32787`/`0x8013`
- Added a bounded-search ledger for decimal IDs `32779`, `32784`, `32786`,
  `32787`, and `32788`, plus an exact old-versus-17.3 canonical conflict table
- Advanced the release dossier resume pointer to Task 4 without editing any
  canonical video proto or channel documentation

Why:
- The 16.x canonical sources mix raw wire IDs with the inherited AV handler's
  +1 internal dispatch values and repeatedly invert phone endpoint direction
- Android Auto 17.3 directly proves fourteen mappings; preserving those
  findings in the dossier gives Task 10 an evidence-ranked publication input
  while keeping the sole absent endpoint slot explicitly bounded

Status:
- Fourteen video rows are `confirmed-static`; no claim implies framed runtime
  observation
- `0x8007` VideoFocusRequest, `0x800A` UpdateUiConfigRequest, `0x800C`
  ActionTaken, `0x800D` IntegratedOverlayParameters, `0x8011` UiConfigRequest,
  `0x8014` MediaOptions, and `0x8015` CriticalUiNotification are Phone -> HU
- `0x8008` VideoFocusIndication, `0x8009` UpdateUiConfigRequest, `0x800B`
  AudioUnderflow, `0x800E` OverlayStart, `0x800F` OverlayStop, `0x8012`
  UpdateHuUiConfigResponse, and `0x8013` MediaStats are HU -> Phone
- Raw `0x8010`/`32784` is `unresolved-with-bounded-search` with status
  `deferred`: the bounded source search found only `wru.java` enum/offset
  bookkeeping, then `jdc` delegates and `jca` rejects internal `32785`; no
  17.3 send, parser, or payload class was found
- The exact numeric search root was
  `analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage` with
  `-g '*.java'`. Results were: `32779` only `wru.java:234,292-293`; `32784`
  only `wru.java:244,302-303`; `32786` `jdc.java:278` plus
  `wru.java:248,306-307`; `32787` only `wru.java:250,308-309`; and `32788`
  `jca.java:191,454`, `wru.java:252,310-311`, plus an unrelated negative
  constant substring at `kdv.java:160`

Next Steps:
1. Task 4: trace `ixb` phone receive branches and `iip` phone sends to close
   `DIR-CC-8001` through `DIR-CC-8007`
2. Task 10: publish the accepted video enum/name/direction corrections from
   this matrix; leave `0x8010` unnamed/reserved unless stronger evidence lands
3. Runtime validation: capture framed video-control traffic to supplement, not
   relabel, these static endpoint findings

Verification:
- Exact Task 3 open-row guard -> exit 0 with no `DIR-VID` open rows
- Exact required-decimal `rg` check -> all of `32775`, `32776`, `32777`,
  `32778`, `32780`, `32781`, `32782`, `32783`, `32785`, and `32789` present in
  `message-matrix.md`
- Video row/status count -> 15 rows: 14 `confirmed-static`, 1 `deferred`
- Resume-pointer `rg` -> Task 3 completed, Task 4 next, exact `ixb.java`
  extraction command present
- Source-anchor existence loop -> 15/15 referenced primary payload/endpoint
  files present
- `git diff --check` -> exit 0

## 2026-07-24 — Close Android Auto 17.3 car-control direction matrix

Date / Session: 2026-07-24 / android-auto-17.3-update-task-4

What Changed:
- Closed `DIR-CC-8001` through `DIR-CC-8007` with raw/decimal IDs, canonical
  names, Android Auto 17.3 payload classes, phone endpoint actions, normalized
  directions, exact source anchors, historical conflicts, static status, and
  canonical dispositions
- Traced the `ixb.java` phone receive branches and `iip.java` phone send
  builders through `xlz`, `xma`, `xli`, `xlj`, `xgj`, `xfw`, and `xga`, plus
  their nested protobuf-lite descriptor references
- Added a phone-endpoint normalization note that keeps the unexpected inbound
  `32771` and `32774` cases distinct from the direct phone-side sends
- Added an exact seven-row conflict ledger covering the inverted canonical
  proto comments, channel documentation, and prior Gold verification labels
- Advanced the dossier resume pointer to Task 5 without modifying canonical
  car-control protos/docs or changing roadmap sequencing

Why:
- The historical sources describe direction from the opposite endpoint
  perspective: Android Auto 17.3 directly sends `0x8001`, `0x8003`, and
  `0x8006` from the phone and directly parses `0x8002`, `0x8004`, `0x8005`,
  and `0x8007` on the phone
- Direct 17.3 endpoint and descriptor evidence outranks older comments and
  audit labels, while remaining explicitly static rather than runtime-captured

Status:
- `0x8001` `xlz` SetCarPropertyValueRequest, `0x8003` `xli`
  RegisterCarPropertyListenersRequest, and `0x8006` `xfw`
  CarActionNotification are `confirmed-static`, Phone -> HU
- `0x8002` `xma` SetCarPropertyValueResponse, `0x8004` `xlj`
  RegisterCarPropertyListenersResponse, `0x8005` `xgj`
  CarPropertyChangeEvent, and `0x8007` `xga` CarControlGroupUpdate are
  `confirmed-static`, HU -> Phone
- `ixb.java:95-99` explicitly rejects inbound `32771` and `32774`; those
  unexpected receive branches do not negate the sends at `iip.java:251-268`
  and `iip.java:568-591`
- No runtime traffic was captured or implied, and all canonical edits remain
  deferred to Task 10

Next Steps:
1. Task 5: trace `jal`, `jai`, and `iji` to close the sensor and radio direction
   rows
2. Task 10: publish the accepted car-control direction reversals from this
   conflict ledger without changing the evidence-ranked names or schemas
3. Runtime validation: capture framed car-control traffic to supplement these
   static phone-endpoint findings

Verification:
- Exact Task 4 receive extraction -> direct parsers for `32770`, `32772`,
  `32773`, and `32775`; explicit unexpected cases for `32771` and `32774`
- Exact Task 4 send extraction -> `ixb.k(...)` calls for `32769`, `32771`, and
  `32774` with complete `xlz`, `xli`, and `xfw` builders
- Exact canonical comparison -> all seven active directions are opposite the
  normalized Android Auto 17.3 phone-endpoint directions
- Exact Task 4 open-row guard -> exit 0 with no `DIR-CC` open rows
- Exact Task 4 direction `rg` -> all seven rows present with the required
  `Phone -> HU` or `HU -> Phone` direction
- Descriptor/source-anchor checks -> all referenced endpoint and protobuf-lite
  files and cited descriptor lines present
- Resume-pointer check -> Task 4 completed, Task 5 next, exact `jal.java`
  extraction command present
- `git diff --check` -> exit 0

## 2026-07-24 — Task 4 Fix Round 1: complete conflict-anchor inventory

Date / Session: 2026-07-24 / android-auto-17.3-update-task-4-fix-1

What Changed:
- Expanded every car-control conflict-ledger ID row to inventory the active
  stale direction and endpoint-perspective claims exposed by the bounded
  canonical search and their immediately surrounding narrative blocks
- Added the omitted proto handler comments, channel request/response prose,
  change-mode entries, complete lifecycle workflow, UUID-correlation note, and
  group-replacement note to their affected IDs
- Preserved all seven Android Auto 17.3 directions, payload classes, static
  classifications, canonical dispositions, and the Task 5 resume pointer

Why:
- Task 10 needs a complete stale-anchor inventory; representative table claims
  alone could leave contradictory overview, workflow, and gotcha prose behind

Status:
- The existing seven-row ledger is now exact for the bounded canonical search:
  each stale proto, channel-doc, and verification-report claim is mapped to one
  or more of `0x8001` through `0x8007`
- Canonical files remain unchanged in this evidence task

Next Steps:
1. Continue with Task 5 from the existing dossier resume pointer
2. In Task 10, use the expanded per-ID anchor inventory to update every stale
   car-control direction and endpoint-perspective statement together

Verification:
- Brief canonical-direction `rg` -> inventoried all stale matched claims and
  reviewed each matching narrative block; cross-version hits remain
  direction-free class mappings
- Matrix anchor `rg` -> omitted proto/channel anchors now present in their
  corresponding conflict rows
- Task 4 open-row guard -> exit 0; direction check -> all seven proven rows
  unchanged
- `git diff --check` -> exit 0

## 2026-07-24 — Close Android Auto 17.3 sensor and radio direction matrix

Date / Session: 2026-07-24 / android-auto-17.3-update-task-5

What Changed:
- Closed `DIR-SEN-8001` through `DIR-SEN-8004` and `DIR-RAD-801A` through
  `DIR-RAD-8023` with exact IDs, payload names/classes, phone endpoint actions,
  normalized directions, source anchors, version deltas, static status, and
  canonical dispositions
- Added complete top-level protobuf-lite descriptor inventories for all four
  sensor and ten radio payloads
- Recorded the exact four inverted sensor verification-report directions while
  preserving the already-correct sensor proto comments and channel catalog
- Recorded no canonical mapping change for all ten radio messages because the
  proto mapping, channel catalog, and verification table agree with 17.3; also
  inventoried the later radio channel prose that reverses endpoint ownership
- Advanced the dossier resume pointer and next command to Task 6 and marked the
  direction/video-ID audit gate `confirmed-static`

Why:
- Android Auto 17.3 directly sends SensorRequest plus five radio requests from
  the phone and directly parses the three sensor response/event/error messages
  plus five radio notifications/responses on the phone
- Separating the correct radio protocol mapping from contradictory narrative
  prose prevents Task 10 from reversing correct IDs while still ensuring the
  endpoint-ownership descriptions are repaired

Status:
- All 14 Task 5 rows are `confirmed-static`; no runtime capture is claimed
- Sensor: `0x8001` is Phone -> HU; `0x8002` through `0x8004` are HU -> Phone
- Radio: `0x801A`, `0x801B`, `0x801D`, `0x801F`, and `0x8020` are HU -> Phone;
  `0x801C`, `0x801E`, and `0x8021` through `0x8023` are Phone -> HU
- Radio remains an AA control/status bridge to HU-managed radio functionality;
  the static evidence does not establish phone-owned RF tuner implementation
  details or any backup-camera behavior

Next Steps:
1. Task 6: close display, transport-channel, service-type, input-binding, and
   descriptor fields 16-18 identity rows
2. Task 10: correct the four sensor verification rows and the inventoried radio
   narrative conflicts while preserving all ten radio mappings
3. Runtime validation: supplement these static findings with framed traffic;
   do not relabel the current evidence as runtime-captured

Verification:
- Exact Task 5 sensor extraction -> constants `32769` through `32772`, direct
  `xlq` send, and `xlr`/`xln`/`xlo` phone receive parsers found
- Exact Task 5 radio receive extraction -> phone parsers for `32794`, `32795`,
  `32797`, `32799`, and `32800`; `32796` and `32798` inbound copies unhandled
- Exact Task 5 radio send extraction -> `jai.k(...)` sends for `32796`, `32798`,
  and `32801` through `32803`
- Canonical comparison `rg` -> sensor proto/channel mapping agrees with 17.3,
  sensor verification rows 13-16 are inverted; radio proto/catalog/report
  mapping agrees for all ten, with contradictory channel prose inventoried
- Exact Task 5 open-row guard -> exit 0 with no `DIR-SEN` or `DIR-RAD` open rows
- Row/status counts -> 4 sensor plus 10 radio rows, all `confirmed-static`;
  radio `No canonical change` count 10
- Resume-pointer check -> Task 5 completed, Task 6 next, exact `itq.java`
  extraction command present
- Source-file existence check -> all 22 referenced endpoint/helper/descriptor
  Java files present
- `git diff --check` -> exit 0

## 2026-07-24 — Close Android Auto 17.3 display and descriptor identity matrix

Date / Session: 2026-07-24 / android-auto-17.3-update-task-6

What Changed:
- Closed `ID-AV-F6` by decoding `xik.g` as optional `uint32` field 6 and
  tracing it directly into `new CarDisplayId(...)`, the accepted per-display
  bridge, and the video endpoint construction path
- Closed `ID-INPUT-F5` by decoding `xhs.g` as optional `uint32` field 5 and
  tracing the exact equality match against each accepted AV `CarDisplayId`,
  including the zero/multiple-input topology failures
- Defined separate semantic domains for transport channel ID, GAL service
  type, logical display ID, and input-to-display binding ID
- Closed `ID-CD-F16` through `ID-CD-F18` with direct 17.3 descriptor-member,
  presence-bit, service-factory, and endpoint service-type chains
- Compared the 17.3 fields against the available 16.2 `wbm` index evidence:
  fields 16-17 retain source-proven 17.3 meanings but receive the conservative
  `insufficient evidence` cross-version disposition; optional field 18 is a
  `compatible addition/removal` relative to the 16.2 17-field descriptor
- Advanced the dossier resume pointer and identity gate to Task 7 without
  changing canonical protos, historical reports, or runtime claims

Why:
- `AVChannel` field 6 is a logical display ID, not the
  `ChannelDescriptor.channel_id` transport route, and input field 5 is the
  binding reference that joins an input service to that logical display
- The historical 16.2 `generic_notification` and `voice` labels do not have a
  trustworthy consumer or marker lineage in the preserved evidence, so
  classifying fields 16-17 as semantic reuse would overstate the record
- The 17.3 source directly ties descriptor fields 16-18 to CarLocalMedia,
  BufferedMedia, and CarIntent through bits `32768`, `65536`, and `131072` and
  endpoint service types 20, 21, and 22

Status:
- All five Task 6 ID rows are closed with exact source chains and canonical
  dispositions; the identity/compatibility gate is `confirmed-static`
- Accepted video-capable descriptors receive separate logical display and
  endpoint objects in the static construction path
- No framed simultaneous streams were observed; runtime concurrency remains
  unverified
- Canonical publication of the AV rename and descriptor version notes remains
  deferred to Task 10

Next Steps:
1. Task 7: reconstruct the bounded CarIntent service contract, starting with
   service type 22 and descriptor presence bit `131072`
2. Task 10: rename AV field 6 to `display_id` and publish only the supported
   fields 16-18 compatibility notes
3. Runtime validation: capture framed multi-display traffic before making any
   simultaneous-stream claim

Verification:
- Exact Task 6 source searches -> `xik.g` consumed by `new CarDisplayId`,
  `xhs.g` matched to that ID, and fields 16-18 tied to the three service bits
- Descriptor decoder -> `xik` field 6 and `xhs` field 5 are optional `uint32`;
  `xlv` contains optional message fields 16-18
- 16.2 index comparison -> `wbm` has 17 fields; fields 16-17 are messages;
  `vwf` and `vvp` remain `insufficient_evidence`; no field 18 is present
- Exact Task 6 open-row guard -> exit 0 with no open `ID-*` rows
- Terminology check -> transport channel ID, service type, display ID, and
  input-to-display binding language all present
- Identity table column check -> all five rows have the expected 11 columns
- Resume-pointer check -> Task 6 completed, Task 7 next, exact CarIntent
  extraction command present
- Owned-file and source-anchor checks -> only the three owned files changed;
  all cited 17.3 sources and 16.2 evidence files exist
- `git diff --check` -> exit 0

## 2026-07-24 — Task 6 Fix Round 1: correct descriptor source anchors

Date / Session: 2026-07-24 / android-auto-17.3-update-task-6-fix-1

What Changed:
- Corrected the `xik` RawMessageInfo citation from line 36 to line 38
- Corrected the `xhs` RawMessageInfo citation from line 36 to line 39
- Extended the `xgi`, `xfq`, and `xgd` marker ranges from lines 4-24 to 4-25
  so each range includes its empty RawMessageInfo descriptor call
- Preserved every Task 6 semantic conclusion, status, disposition, and resume
  pointer

Why:
- The former ranges ended immediately before the descriptor calls, making the
  otherwise-correct field and marker claims harder to reproduce exactly

Status:
- All five near-miss anchors in the Task 6 matrix now cite the exact descriptor
  lines
- The Task 6 identity rows remain closed and unchanged apart from citations

Next Steps:
1. Continue with Task 7 from the unchanged dossier resume pointer
2. Preserve the corrected anchors when publishing Task 6 conclusions in Task
   10

Verification:
- `nl -ba .../xik.java | sed -n '34,40p'` -> RawMessageInfo call at line 38
- `nl -ba .../xhs.java | sed -n '35,41p'` -> RawMessageInfo call at line 39
- `nl -ba .../{xgi,xfq,xgd}.java | sed -n '21,27p'` (run as a loop) -> each
  empty-marker RawMessageInfo call at line 25
- Focused anchor `rg` over all three owned files -> only corrected
  `xik.java:38`, `xhs.java:39`, and marker ranges `4-25` remain; the README and
  prior handoff contain no equivalent stale anchor
- Exact Task 6 open-row guard -> exit 0 with no open `ID-*` row
- `git diff --check` -> exit 0

## 2026-07-24 — Task 7: reconstruct the CarIntent service

Date / Session: 2026-07-24 / android-auto-17.3-update-task-7

What Changed:
- Closed all five `SVC-CI-*` rows with the descriptor, endpoint, raw-ID,
  payload-schema, and activation evidence boundaries
- Traced descriptor field 18 and presence bit `0x20000` through service type
  22 endpoint construction to the phone's incoming `xgc` parse and callback
  notification
- Decoded `xgc` as one optional field-2 string (wire type 2/tag `0x12`) and
  separated that wire fact from the consumer log's fixed NAVIGATE label
- Recorded the bounded raw-ID search as deferred and advanced the dossier
  resume pointer to Task 8

Why:
- The 17.3 sources prove a bounded HU -> Phone CarIntent payload contract, but
  no sender enum, dispatch comparison, or resource mapping proves its raw ID
- Publishing conventional `0x8001`, an intent-type enum, field 1 meaning, or
  acknowledgement would go beyond the available wire evidence
- The named `AdasRouteInfoFeature__car_intent_enabled` flag defaults false,
  while the actual decompiled factory path accepts or suppresses the service
  solely through descriptor field-18 presence

Status:
- `SVC-CI-DESCRIPTOR`, `SVC-CI-ENDPOINT`, `SVC-CI-SCHEMA`, and `SVC-CI-GATE`
  are `confirmed-static`
- `SVC-CI-ID` is `deferred`; the raw message ID remains unknown
- No canonical CarIntent proto or channel documentation was created before the
  Task 10 manifest gate
- Static evidence is not a runtime capture; live activation and framed traffic
  remain unverified

Next Steps:
1. Task 8: close CarLocalMedia state/flow and classify BufferedMedia
2. Task 10: publish only CarIntent rows accepted by the change manifest
3. Runtime validation: capture a framed CarIntent message to resolve its raw ID

Verification:
- Required descriptor/service search -> field-18 bit `131072`, service type
  22, and `CarIntentService` construction anchors found
- Required sender/dispatcher/resource searches -> no sender enum or raw-ID
  comparison; `SVC-CI-ID` remains deferred
- RawMessageInfo decoder -> proto2 optional field 2 `string`, wire type 2,
  encoded tag `0x12`
- Required activation search -> flag default false; no feature-name reference
  in `jnb` or `iix`; factory acceptance follows descriptor bit `0x20000`
- Exact Task 7 open-row guard -> exit 0 with no open `SVC-CI-*` rows
- Required contract-term check -> service type 22, field 2, HU -> Phone,
  NAVIGATE, and AdasRouteInfoFeature all present
- Owned-file scope check -> only the three Task 7 owned files changed
- `git diff --check` -> exit 0
