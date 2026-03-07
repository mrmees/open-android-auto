# Proto Verification Pipeline — Design

**Date:** 2026-03-06
**Status:** Active
**Tracking:** `analysis/reports/proto-verification/PROGRESS.md`

## Problem

Proto definitions derived from DB structural matching can be semantically wrong — right shape, wrong identity. The MediaPlaybackCommand retraction (2026-03-06) proved this: a proto class (`vuy`) was structurally mapped as a media command but was actually `ActionTakenNotification` on the video channel. This was only discovered when the HU software failed at runtime.

We need a systematic way to verify every wire proto definition end-to-end in the decompiled APK source, not just trust DB-level pattern matching.

## Approach

**Channel-handler-first verification.** The GAL channel handler classes in the APK are ground truth — they contain the switch/if-else logic that dispatches incoming messages and the send calls for outgoing messages. We start from the handler, extract its complete msg ID table, then reconcile against our proto definitions.

This catches:
- **Phantom messages** (protos we defined that don't exist on the claimed channel)
- **Missing messages** (msg IDs in the handler we haven't documented)
- **Misidentified protos** (correct structure, wrong channel/msg ID/name)

## Scope

**Phase 1 (current):** Wire protocol messages — protos with claimed msg IDs on GAL channels (~50-60 messages across ~14 channels).

**Phase 2 (future):** SDP data structures, sub-message recursive verification, remaining internal protos.

## Per-Channel Verification Process

### Step 1: Identify the channel handler class

Query DB or grep jadx source for the GAL tag string (e.g., `"CAR.GAL.MEDIA"`). Find the class containing message dispatch logic.

Helper: `analysis/tools/verify/find_references.sh <class_name>`

### Step 2: Extract the complete msg ID table

Read the handler's switch/if-else chain for incoming messages and any outbound send calls with msg IDs. This is the channel's ground truth.

Helper: `analysis/tools/verify/extract_msg_ids.sh <handler_file>`

### Step 3: Verify each proto against 6 checks

For each msg ID found in the handler, and for each proto we claim lives on this channel:

| # | Check | What to verify | Catches |
|---|-------|----------------|---------|
| 1 | **Channel binding** | Proto class is referenced from the correct GAL handler | Wrong channel assignment |
| 2 | **Message ID** | Sent/received with the msg ID we claim | Wrong msg ID |
| 3 | **Direction** | Code serializes (outbound) or deserializes (inbound) as expected | Reversed direction |
| 4 | **Field schema** | Field numbers, types, and modifiers match our .proto file | Wrong field types/numbers |
| 5 | **Cross-references** | Check ALL references to the proto class across the entire APK | Proto used on different channel (misidentification) |
| 6 | **Enum values** | Enum constants in APK match our enum definitions | Right shape, wrong semantics |

Any check that fails is a "stop, investigate" signal.

### Step 4: Record results

- **Per-channel report** in `analysis/reports/proto-verification/<channel>.md`
  - Handler class identified
  - Complete msg ID table (ground truth)
  - Per-proto 6-check results
  - Gaps discovered (msg IDs with no proto)
  - Suspects (protos not found in handler)
- **Update `.audit.yaml`** files with results
- **Update `PROGRESS.md`** with channel status

## Channel Priority Order

| Priority | Channel | ID | Handler Tag | Why |
|----------|---------|----|-------------|-----|
| 1 | Media | 10 | CAR.GAL.MEDIA | Already has one retraction |
| 2 | Navigation | 8 | CAR.GAL.NAV | Complex, many msg IDs, NavigationDistance reclassified |
| 3 | Control | 0 | CAR.GAL.CONTROL | Session lifecycle, critical for HU |
| 4 | Input | 1 | CAR.GAL.INPUT | Touch/button |
| 5 | Phone | 12 | CAR.GAL.PHONE | Phone status |
| 6 | Video | 2 | CAR.GAL.VIDEO | Video sink |
| 7 | Audio | 3-4 | CAR.GAL.AUDIO | Audio sink channels |
| 8 | Sensor | 7 | CAR.SENSOR | Sensor data |
| 9+ | Remaining | varies | varies | BT, radio, car control, wifi, notification, vendor ext |

## Confidence Tiers

| Tier | Meaning | Criteria |
|------|---------|----------|
| **Gold** | APK deep-trace verified | All 6 checks pass, handler traced end-to-end |
| **Silver** | Structural + cross-version match | DB evidence + consistent across APK versions |
| **Bronze** | Single-version structural match | DB evidence only |
| **Retracted** | Proven incorrect | Handler trace disproved it |
| **Unverified** | No evidence yet | Placeholder definitions |

## Helper Scripts

Located in `analysis/tools/verify/`. These are grep wrappers to save repetitive typing — the actual verification is human/Claude judgment.

| Script | Purpose | Usage |
|--------|---------|-------|
| `find_references.sh` | Find all files referencing a class | `./find_references.sh vyc` |
| `extract_msg_ids.sh` | Extract msg ID constants from a handler file | `./extract_msg_ids.sh path/to/handler.java` |
| `db_lookup.sh` | Dump proto fields, enums, evidence from DB | `./db_lookup.sh vyc` |

## Session Continuity

Each new session:
1. Read `analysis/reports/proto-verification/PROGRESS.md`
2. See which channel is next or in-progress
3. Read the per-channel report if resuming mid-channel
4. Continue from the last completed check

## Not In Scope (Phase 1)

- Proto classes used only in SDP/service discovery (verified separately via wire captures)
- Internal/telemetry protos (not wire messages)
- Sub-message recursive deep-trace beyond one level
- Automated pass/fail tooling (if the process stabilizes, we can automate later)
