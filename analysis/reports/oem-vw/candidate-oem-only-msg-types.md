# VW Capture: Candidate OEM-only msg_types

**Set difference**: `{(msg_type, direction) in VW} - `{(msg_type, direction) in any DHU baseline}`

**Filter**: every candidate was first filtered through the OEM-01 fragment classification pipeline — `continuation_or_garbage` records are NEVER listed here.

**Label**: every surviving entry is labeled `candidate` (NEVER `confirmed`) until repeat observation in a future capture, successful schema parse, or APK cross-reference.

## By (msg_type, direction)

| msg_type | hex | direction | count | tier | attribution | label |
|---------:|-----|-----------|------:|------|-------------|-------|
| 5 | 0x0005 | out | 1 | A | deterministic | candidate |
| 6 | 0x0006 | in | 1 | A | deterministic | candidate |
| 7 | 0x0007 | out | 11 | A | deterministic | candidate |
| 8 | 0x0008 | in | 11 | A | deterministic | candidate |
| 11 | 0x000B | in | 59 | A | deterministic | candidate |
| 12 | 0x000C | out | 59 | A | deterministic | candidate |
| 13 | 0x000D | out | 1 | A | deterministic | candidate |
| 14 | 0x000E | in | 1 | A | deterministic | candidate |
| 18 | 0x0012 | out | 2 | A | deterministic | candidate |
| 19 | 0x0013 | in | 1 | A | deterministic | candidate |
| 32768 | 0x8000 | out | 3 | B | sdp_candidates | candidate |
| 32772 | 0x8004 | in | 2752 | B | sdp_candidates | candidate |
| 32774 | 0x8006 | out | 46 | B | sdp_candidates | candidate |
| 32775 | 0x8007 | out | 46 | B | sdp_candidates | candidate |
| 32776 | 0x8008 | in | 2 | B | sdp_candidates | candidate |
| 32821 | 0x8035 | out | 1 | B | unattributed | candidate |
| 32865 | 0x8061 | out | 1 | B | sdp_narrowed | candidate |

## By msg_type only

| msg_type | hex | count | label |
|---------:|-----|------:|-------|
| 5 | 0x0005 | 1 | candidate |
| 6 | 0x0006 | 1 | candidate |
| 7 | 0x0007 | 11 | candidate |
| 8 | 0x0008 | 11 | candidate |
| 11 | 0x000B | 59 | candidate |
| 12 | 0x000C | 59 | candidate |
| 13 | 0x000D | 1 | candidate |
| 14 | 0x000E | 1 | candidate |
| 18 | 0x0012 | 2 | candidate |
| 19 | 0x0013 | 1 | candidate |
| 32768 | 0x8000 | 3 | candidate |
| 32772 | 0x8004 | 2752 | candidate |
| 32774 | 0x8006 | 46 | candidate |
| 32775 | 0x8007 | 46 | candidate |
| 32776 | 0x8008 | 2 | candidate |
| 32821 | 0x8035 | 1 | candidate |
| 32865 | 0x8061 | 1 | candidate |
