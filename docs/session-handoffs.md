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
