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
