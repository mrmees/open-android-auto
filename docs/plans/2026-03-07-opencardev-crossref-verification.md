# opencardev/aasdk Cross-Reference Verification Plan

**Created:** 2026-03-07
**Status:** Ready for execution
**Prerequisite:** Read `analysis/reports/proto-verification/PROGRESS.md` for methodology context

## Background

We imported protos from the opencardev/aasdk project (GPLv3) into four new areas. All are currently at `bronze [external_reference]` confidence. This plan verifies each against the 16.2 APK using the same agent-driven methodology that took our original 14 channels to Gold.

**Commit:** `f520156` — `feat(protos): add cross-referenced protos from opencardev/aasdk`

## What Changed

| Area | Files | Current Confidence | Notes |
|------|-------|-------------------|-------|
| Media Browser | `oaa/mediabrowser/` (2 files) | bronze | Dead channel in 16.1+ — verify SDP stub is truly empty |
| Control extras | `oaa/common/` (4 new), `oaa/control/` (1 new, 1 upgraded) | bronze/silver | Enums + data messages, some may have APK evidence |
| Legacy Radio v1 | `oaa/radio/LegacyRadioMessages.proto` | bronze | Different API generation — verify msg IDs don't conflict with v2 |
| GAL Verification | `oaa/verification/` (2 files) | bronze | DHU test channel — may not exist in phone APK at all |

## Verification Approach

Same 6-check methodology as previous verification waves:
1. **Channel binding** — which handler/service class owns this?
2. **Message ID** — confirmed in handler switch or enum?
3. **Direction** — Phone→HU or HU→Phone?
4. **Field schema** — field numbers, types, names match APK class?
5. **Cross-references** — sub-messages, imports, enums consistent?
6. **Enum values** — all values present, none missing?

### Key Resources
- **DB:** `analysis/android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db`
- **jadx:** `analysis/aa-16.2/jadx-output/sources/p000/`
- **Existing protos:** `oaa/` (all directories)
- **Existing verification reports:** `analysis/reports/proto-verification/`

## Wave 1: Media Browser Channel (type 12)

**Goal:** Confirm channel is dead, verify SDP stub, check if any msg IDs or handler code exists.

### Agent Tasks

**Agent 1A: Media Browser SDP & Handler Search**
- Verify `MediaBrowserChannel` (vxy in 16.2) is truly empty (0 fields)
- Search for ANY handler class registered for service type 12 / MEDIA_BROWSER
- Check `qkn.java` (service type enum) — confirm MEDIA_BROWSER=12 exists
- Search DB for classes referencing media browser message IDs (0x8001-0x8006 in the context of channel type 12)
- Check if `ChannelDescriptor` field 11 is ever populated in any code path
- Look for log tags: `MediaBrowser`, `CAR.GAL.MEDIA_BROWSER`

**Expected outcome:** Confirm dead channel. If ANY handler exists, escalate — that means we have real messages to verify.

**If dead (expected):** Upgrade MediaBrowserMessages.proto header to note "confirmed dead in 16.2" and upgrade confidence to `silver [cross_referenced, apk_confirmed_dead]`.

## Wave 2: Control Channel Extras

**Goal:** Verify the 5 new common/control protos against APK evidence.

### Agent Tasks

**Agent 2A: ChannelCloseNotification (msg 0x0009)**
- Find handler for msg ID 9 (0x0009) in `hzh.java` (control channel handler)
- Confirm it's an empty message (no deserialization)
- Check direction (HU→Phone or bidirectional?)
- Search for log strings mentioning "channel close" or "close notification"

**Agent 2B: LocationCharacterization enum**
- Search DB for bitmask values: 1, 2, 4, 8, 16, 32, 64, 128, 256
- Look in `HeadUnitInfo` / `SensorChannel` config for location characterization field
- Check if this is referenced by GPS/location sensor setup code
- Verify our enum values match what the APK uses

**Agent 2C: SessionConfiguration enum**
- Search DB for bitmask values related to UI hiding: 1, 2, 4, 8
- Look in `HeadUnitInfo` (wbl/HeadUnitInfoData.proto) for session config field
- Check ServiceDiscoveryResponse handling for these flags
- Find APK code that checks "hide clock", "hide signal", "hide battery"

**Agent 2D: FragInfo enum**
- Search for fragmentation-related code — frame assembly, continuation flags
- Check if this maps to the flags byte in the wire frame header
- Look for enum with values 0-3 related to FIRST/CONTINUATION/LAST/UNFRAGMENTED
- NOTE: May be in native code (C/JNI) rather than Java — if so, note that

**Agent 2E: WirelessTcpConfiguration**
- Search for socket buffer configuration: SO_RCVBUF, SO_SNDBUF, SO_TIMEOUT
- Look in WiFi projection connection setup code
- Check if referenced by `ConnectionConfiguration` or transport config
- Search for class with 3 uint32 fields related to socket/TCP config

## Wave 3: Legacy Radio v1 Cross-Check

**Goal:** NOT full verification (these are legacy messages). Just confirm:
1. Message IDs 0x8001-0x8019 are NOT used by the current radio handler (ibf.java)
2. No conflict between legacy v1 and current v2 msg ID ranges
3. Check if any v1 structures (RadioType enum, RdsData, etc.) still exist in APK as dead code

### Agent Tasks

**Agent 3A: Radio Message ID Range Check**
- Read ibf.java handler switch cases — confirm only 0x801A-0x8023
- Search for any references to msg IDs in 0x8001-0x8019 range on radio channel
- Check if `RadioType` enum (AM=0, FM=1, AM_HD=2, FM_HD=3, DAB=4, XM=5) exists anywhere
- Look for `RdsData`, `HdRadioStationInfo`, `StationPreset` class equivalents
- Check if `RadioProperties` (14-field tuner capability message) exists

**Expected outcome:** Confirm no conflicts. v1 IDs should be completely absent from 16.2. Some structures (RadioType?) might persist as dead code.

## Wave 4: GAL Verification & Diagnostics

**Goal:** Check if verification vendor extension exists in the phone APK at all.

### Agent Tasks

**Agent 4A: GAL Verification Channel Search**
- Search for `GalVerification` or `gal_verification` references
- Look for vendor extension message IDs 0x8001-0x800B in non-radio/non-media-browser contexts
- Check `kaz.java` (known vendor extension handler) for any structured message handling
- Search for "verification", "inject input", "screen capture" in APK strings
- Look for `SetSensor`, `MediaSinkStatus`, `VideoFocus`, `AudioFocus` in test/verification context

**Agent 4B: Google Diagnostics Search**
- Search for `Diagnostics`, `bug_report`, `BugReport` in APK
- Look for message IDs 1 and 2 on any vendor extension channel
- Check for token-based request/response patterns related to diagnostics

**Expected outcome:** These are likely DHU-side only (not in the phone APK). If confirmed absent, upgrade to `silver [cross_referenced, dhu_only]`. If found, upgrade to gold with full verification.

## Wave 5: ConnectedDevices Upgrade Attempt

**Goal:** Try to push ConnectedDevices from silver to gold.

### Agent Tasks

**Agent 5A: ConnectedDevices Deep Trace**
- Re-examine msg IDs 0x0014, 0x0015, 0x0016, 0x0019 in `hzh.java`
- Previous verification found "no handler implementation" — retry with more thorough search
- Check if these are handled by a different class (not hzh.java)
- Look for `ConnectedDevice`, `UserSwitch`, `user_switch` in DB
- Search for the `UserSwitchStatus` error codes (-1 through -9 or equivalent)
- Check if multi-device is a GMS-only feature (like vendor extension)

## Execution Notes

### Agent Prompt Template
Each agent should receive:
1. The specific proto file content being verified
2. The 6-check verification methodology
3. Key paths (DB, jadx, existing protos)
4. Known pitfalls from PROGRESS.md (obfuscated name reuse, +1 msg ID offset on AV channels, etc.)
5. Instructions to REPORT findings only — do NOT modify files

### Parallelization
- Wave 1 (1 agent) can run alone — quick check
- Wave 2 (5 agents) can all run in parallel — independent searches
- Wave 3 (1 agent) can run in parallel with Wave 2
- Wave 4 (2 agents) can run in parallel with everything
- Wave 5 (1 agent) can run in parallel with everything

**Max parallel: 10 agents** (all waves at once if context allows)
**Recommended: 2-3 waves at a time** to review findings between batches

### After Each Wave
1. Review agent findings
2. Apply changes (upgrade confidence, fix schemas, add notes)
3. Commit with wave number in message
4. Update this doc with results

## Expected Outcomes

| Area | Likely Result |
|------|--------------|
| Media Browser | Confirmed dead → silver |
| ChannelCloseNotification | Likely found in hzh.java → gold |
| LocationCharacterization | May find in HeadUnitInfo → silver or gold |
| SessionConfiguration | May find in HeadUnitInfo → silver or gold |
| FragInfo | May be native/JNI → stays bronze |
| WirelessTcpConfiguration | May find in WiFi setup → silver or gold |
| Legacy Radio v1 | Confirmed no conflicts → stays bronze (legacy reference) |
| GAL Verification | Likely DHU-only → silver |
| Google Diagnostics | Likely DHU-only → silver |
| ConnectedDevices | Possible upgrade to gold if handler found |
