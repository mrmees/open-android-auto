# Radio Channel Verification Report

**Channel:** Radio (service 15, CAR.GAL.RADIO-EP)
**Handler:** ibf.java (16.2), extends iav directly (NO +1 msg ID offset)
**Service:** hlr.java (16.2), log tag: CAR.RADIO
**Verified:** 2026-03-07

## Message ID Table

| Msg ID | Direction | 16.2 Class | Proto Name | Confidence |
|--------|-----------|------------|------------|------------|
| 0x801A | HU→Phone | wam | RadioProgramListNotification | Gold |
| 0x801B | HU→Phone | wal | RadioProgramInfoNotification | Gold |
| 0x801C | Phone→HU | wag | RadioMuteRequest | Gold |
| 0x801D | HU→Phone | wah | RadioMuteResponse | Gold |
| 0x801E | Phone→HU | wat | RadioTuneRequest | Gold |
| 0x801F | HU→Phone | wau | RadioTuneResponse | Gold |
| 0x8020 | HU→Phone | wad | RadioFavoriteListNotification | Gold |
| 0x8021 | Phone→HU | waq | RadioFavoriteToggleRequest | Gold |
| 0x8022 | Phone→HU | war | RadioTuneDirectionRequest | Gold |
| 0x8023 | Phone→HU | wac | RadioSearchRequest | Gold |

Outgoing msg IDs confirmed in hlr.java: setMute→32796, tuneToProgram→32798, toggleFavorite→32801, tuneDirection→32802, search→32803.

## Verification Result

**All 10 top-level messages match proto definitions exactly. No field errors found.**

All sub-messages and enums also match. This channel was structurally correct from the initial analysis — only needed 16.2 class name updates and confidence upgrades.

## Sub-Messages (all Gold)

| Proto | 16.1 Class | 16.2 Class | Fields | Status |
|-------|-----------|-----------|--------|--------|
| RadioProgramInfo | was | wak | 1: message(wan), 2: message(waf) | MATCH |
| RadioProgramSelector | wav | wan | 1: message(waj), 2: repeated message(waj) | MATCH |
| RadioProgramIdentifier | war | waj | 1: enum(wai), 2: uint64 | MATCH |
| RadioMetadata | wan | waf | 13 fields | MATCH |
| RadioSongMetadata | wbb | was | 6 fields | MATCH |
| RadioImage | wam | wae | 1: bytes | MATCH |
| RadioProgramType | waw | wao | 1: enum, 2: uint32 | MATCH |

## Enums (all Gold)

| Enum | 16.2 Class | Values | Status |
|------|-----------|--------|--------|
| RadioIdentifierType | wai | 10 values (0-9) | MATCH |
| RadioTuneStatus | C0000a.m80bA | 5 values (0-4) | MATCH |
| RadioTuneDirection | vdp.m36490W | 3 values (0-2) | MATCH |
| RadioProgramTypeSchema | vdp.m36490W | 3 values (0-2) | MATCH |
| RadioBandType | vzz | 4 values (0-3) | MATCH |
| RadioCodecType | — | 6 values (0-5) | Silver (not in 16.2 SDP) |
| RadioRegion | — | 2 values (0-1) | Silver (not in 16.2 SDP) |

## Changes Applied

1. **16.2 class names updated** in all comments (sub-messages had 16.1 names)
2. **RadioIdentifierType comment fixed** — said `waq` (wrong), now `wai`
3. **All confidence upgraded** from silver to gold
4. **RadioCodecType and RadioRegion** remain silver — not referenced in 16.2 SDP config

## SDP Config Note

The 16.1 RadioStation structure (14 fields) has been restructured in 16.2 to a 3-level hierarchy:
- `wap` (RadioChannelConfig) → field 2: `wab` (RadioBands)
- `wab` (RadioBands) → field 1: repeated `waa` (RadioBandGroup)
- `waa` (RadioBandGroup) → field 1: repeated enum vzz (BandType), field 2: bool, field 3: string

The existing `oaa/control/RadioChannelData.proto` still has the 16.1 structure and needs a future update.
