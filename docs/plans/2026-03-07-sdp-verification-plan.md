# SDP Layer Verification — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Verify all SDP protobuf schemas against the 16.2 APK to Gold confidence.

**Architecture:** Agent-based verification — dispatch Explore agents to research 16.2 APK classes, collect findings, apply proto changes in main context, commit per wave. Same proven approach from GAL verification (194 Gold protos).

**Tech Stack:** SQLite DB queries (apk-index), jadx decompiled Java source, protobuf schemas

---

## Key Paths

| Resource | Path |
|----------|------|
| 16.2 DB | `analysis/android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db` |
| jadx source | `analysis/aa-16.2/jadx-output/sources/p000/` |
| Proto files | `oaa/` |
| Verification reports | `analysis/reports/proto-verification/` |
| Progress tracker | `analysis/reports/proto-verification/PROGRESS.md` |
| Helper scripts | `analysis/tools/verify/` |
| Design doc | `docs/plans/2026-03-07-sdp-verification-design.md` |

## DB Query Reference

```sql
-- Find a class by obfuscated name
SELECT * FROM classes WHERE class_name LIKE '%wbo%';

-- Get all fields for a class
SELECT f.field_name, f.field_number, f.field_type, f.field_modifier
FROM fields f JOIN classes c ON f.class_id = c.id
WHERE c.class_name LIKE '%wbo%'
ORDER BY f.field_number;

-- Get enum values
SELECT e.enum_name, e.enum_value
FROM enum_values e JOIN classes c ON e.class_id = c.id
WHERE c.class_name LIKE '%vyh%'
ORDER BY e.enum_value;

-- Find classes referencing another class
SELECT DISTINCT c2.class_name, c2.source_file
FROM class_references cr
JOIN classes c1 ON cr.referenced_class_id = c1.id
JOIN classes c2 ON cr.referencing_class_id = c2.id
WHERE c1.class_name LIKE '%wbo%';
```

## Agent Prompt Template

Each wave dispatches 1-3 agents with this structure:

```
You are verifying Android Auto SDP protobuf schemas against the 16.2 APK.

**Your task:** Verify [PROTO_LIST] against their 16.2 APK classes.

**Resources:**
- DB: [DB_PATH]
- jadx source: [JADX_PATH] (classes under p000/)
- Current proto files: [list proto file contents]

**For each proto, perform these 6 checks:**
1. Channel binding — which SDP field or message carries this proto
2. 16.2 class mapping — find correct obfuscated class (16.1 names differ!)
3. Field schema — field numbers, types, required/optional, sub-messages
4. Cross-references — imports, enum refs, shared types
5. Enum values — complete value lists
6. Confidence assessment — evidence quality

**Known pitfalls:**
- Obfuscated names change between 16.1 and 16.2 — match by STRUCTURE not name
- 16.1 class comments in current protos may be WRONG for 16.2
- Some protos are proto2, some proto3 — check APK descriptor
- Empty placeholder messages may have gained fields in 16.2

**Output format:** For each proto, report:
- 16.2 class name (with evidence)
- Field-by-field comparison (current vs 16.2)
- Any discrepancies found
- Recommended changes
- Confidence: Gold / Silver / Bronze

Do NOT modify any files. Report findings only.
```

## Verification Checklist (per proto)

For every proto verified, these 6 checks must pass:

- [ ] Channel binding confirmed
- [ ] 16.2 class identified
- [ ] Field schema matches (numbers, types, modifiers)
- [ ] Cross-references checked
- [ ] Enum values complete
- [ ] Confidence upgraded with evidence

---

## Task 1: Create SDP Progress Tracker

**Files:**
- Create: `analysis/reports/proto-verification/sdp-progress.md`

**Step 1: Create the tracking file**

```markdown
# SDP Verification Progress

**Design:** `docs/plans/2026-03-07-sdp-verification-design.md`
**Started:** 2026-03-07

## Summary

| Status | Count |
|--------|-------|
| Already Gold (from GAL) | 8 |
| Verified (new Gold) | 0 |
| Schema Errors Found & Fixed | 0 |
| New Protos Discovered | 0 |
| Retracted / Removed | 0 |
| Pending | ~30 |

## Wave Status

| Wave | Scope | Status | Notes |
|------|-------|--------|-------|
| 1 | SDP Envelope (SDR, SDReq, ChannelDescriptor) | PENDING | |
| 2 | Phone Capabilities | PENDING | |
| 3 | AV + Video SDP Configs | PENDING | |
| 4 | Audio + Mic SDP Configs | PENDING | |
| 5 | Navigation + Sensor SDP | PENDING | |
| 6 | Radio SDP (full rewrite) | PENDING | |
| 7 | Bluetooth + WiFi SDP | PENDING | |
| 8 | CarControl + Remaining Channels | PENDING | |
| 9 | Connection Config + Common Protos | PENDING | |

## Resume Pointer

Start at Wave 1.
```

**Step 2: Commit**

```bash
git add analysis/reports/proto-verification/sdp-progress.md
git commit -m "docs(sdp): add SDP verification progress tracker"
```

---

## Task 2: Wave 1 — SDP Envelope Verification

**Files:**
- Verify: `oaa/control/ServiceDiscoveryResponseMessage.proto`
- Verify: `oaa/control/ServiceDiscoveryRequestMessage.proto`
- Verify: `oaa/control/ChannelDescriptorData.proto`

**Step 1: Dispatch envelope agent**

Dispatch 1 Explore agent to verify these 3 core protos:

- **ServiceDiscoveryResponse** (16.1: wby) — 17 fields including car identity, channel array, HU info. Also verify the 4 ServiceDiscoveryFeature placeholder messages.
- **ServiceDiscoveryRequest** (16.1: wbx) — 6 fields including phone icons, device name, session info.
- **ChannelDescriptor** (16.1: wbw) — 17 fields mapping field numbers to channel config sub-messages. This is the spine — every field number must be correct.

Agent must find the 16.2 class names for all three and compare field-by-field.

**Step 2: Review agent findings**

Check for:
- New fields added in 16.2 (fields 12, 16 noted as missing in SDR)
- Field type changes
- New ChannelDescriptor fields beyond 17
- ServiceDiscoveryFeature placeholders — still empty?

**Step 3: Apply proto changes**

Update proto files based on agent findings.

**Step 4: Update progress tracker**

Mark Wave 1 complete, record findings.

**Step 5: Commit**

```bash
git add oaa/control/ServiceDiscoveryResponseMessage.proto \
        oaa/control/ServiceDiscoveryRequestMessage.proto \
        oaa/control/ChannelDescriptorData.proto \
        analysis/reports/proto-verification/sdp-progress.md
git commit -m "feat(verify-sdp): Wave 1 — SDP envelope verified against 16.2"
```

---

## Task 3: Wave 2 — Phone Capabilities Verification

**Files:**
- Verify: `oaa/control/PhoneCapabilitiesMessage.proto`
- Verify: `oaa/control/PhoneCapabilitiesData.proto`
- Verify: `oaa/control/CapabilityData.proto`

**Step 1: Dispatch phone capabilities agent**

Verify all phone-side SDP protos:
- PhoneCapabilities (16.1: aagr) — 6 fields
- DeviceInfo (16.1: vve) — 9 fields (fields 5-8 unnamed)
- PhoneConnectionConfig (16.1: wdm) — 5 fields
- CapabilityFlag (16.1: aagh) — 2 fields
- CapabilityPair (16.1: aags) — 2 fields
- CapabilityEntry (16.1: aagv) — 10 fields with oneof
- PingConfigPair (16.1: aaft) + PingConfigEntry — 2+4 fields
- WifiSecurityMode enum (16.1: wdr) — 11 values
- WifiAccessPointType enum
- PhoneIdentifierType enum (placeholder)
- CapabilityEnum (placeholder)

This wave can run in **parallel with Wave 3** since it's the phone side (independent).

**Step 2-5: Same as Wave 1** (review, apply, update tracker, commit)

```bash
git commit -m "feat(verify-sdp): Wave 2 — Phone capabilities verified against 16.2"
```

---

## Task 4: Wave 3 — AV + Video SDP Config Verification

**Files:**
- Verify: `oaa/av/AVChannelData.proto`
- Verify: `oaa/video/VideoConfigData.proto`
- Verify: `oaa/video/AdditionalVideoConfigData.proto`
- Verify: `oaa/av/AVStreamTypeEnum.proto`

**Step 1: Dispatch AV/video agent**

Verify all AV and video SDP config protos:
- AVChannel (16.1: vys) — 9 fields. Key: stream_type, video configs, audio configs, display_type, channel_id, focus_reason, keycode
- VideoConfig — 11 fields. Key: resolution enum, fps, margins, DPI, codec, additional config
- AdditionalVideoConfig — ~6 fields. Extended params like density, viewing distance
- AVStreamType enum — video/audio/mic stream types
- VideoMargins sub-message

Include the already-Gold VideoResolution enum values from GAL verification for cross-reference.

**Step 2-5: Same pattern** (review, apply, update tracker, commit)

```bash
git commit -m "feat(verify-sdp): Wave 3 — AV + Video SDP configs verified against 16.2"
```

---

## Task 5: Wave 4 — Audio + Mic SDP Config Verification

**Files:**
- Verify: `oaa/av/AVInputChannelData.proto`
- Verify: `oaa/audio/AudioConfigData.proto`
- Verify: `oaa/audio/AudioFocusChannelData.proto`

**Step 1: Dispatch audio agent**

Small wave — 3 protos:
- AVInputChannel (16.1: vyt) — 3 fields (stream_type, audio_config)
- AudioConfig — 3 fields (sample_rate, bit_depth, channel_count)
- AudioFocusChannel — 0 fields (empty marker, verify still empty in 16.2)

**Step 2-5: Same pattern**

```bash
git commit -m "feat(verify-sdp): Wave 4 — Audio + Mic SDP configs verified against 16.2"
```

---

## Task 6: Wave 5 — Navigation + Sensor SDP Config Verification

**Files:**
- Verify: `oaa/navigation/NavigationChannelData.proto`
- Verify: `oaa/navigation/NavigationImageOptionsData.proto`
- Verify: `oaa/sensor/SensorChannelData.proto`

**Step 1: Dispatch nav/sensor agent**

Partially Gold already — verify the parent containers:
- NavigationChannel (16.1: vzr) — 3 fields (min_interval, type enum, image_options)
- NavigationImageOptions — sub-msg fields
- NavigationChannelConfig (if separate from NavigationChannel)
- SensorChannel (16.1: wbu) — 4 fields. Children already Gold, verify parent matches.

**Step 2-5: Same pattern**

```bash
git commit -m "feat(verify-sdp): Wave 5 — Navigation + Sensor SDP configs verified against 16.2"
```

---

## Task 7: Wave 6 — Radio SDP Rewrite

**Files:**
- Rewrite: `oaa/control/RadioChannelData.proto`

**Step 1: Dispatch radio SDP agent**

This is a **full rewrite**, not a tweak. The 16.1 structure (RadioChannel → RadioStation × 14 fields → RadioBand) was replaced in 16.2 with a new hierarchy:
- RadioChannelConfig (16.2: wap)
- RadioBands (16.2: wab)
- RadioBandGroup (16.2: waa)

Agent must:
1. Find wap/wab/waa in 16.2 DB and jadx
2. Extract complete field schemas for all three
3. Determine how they nest
4. Check if RadioCodecType, RadioBandType, RadioRegion enums are still used in SDP (or only in GAL messages)

**Step 2: Review and rewrite proto**

This will be a complete replacement of RadioChannelData.proto contents, not incremental edits.

**Step 3-5: Same pattern**

```bash
git commit -m "feat(verify-sdp): Wave 6 — Radio SDP rewritten for 16.2 structure"
```

---

## Task 8: Wave 7 — Bluetooth + WiFi SDP Confirmation

**Files:**
- Verify: `oaa/bluetooth/BluetoothChannelData.proto`
- Verify: `oaa/wifi/WifiChannelData.proto`

**Step 1: Dispatch BT/WiFi agent**

Quick confirmation wave — both are already Gold from GAL verification. Agent verifies:
- BluetoothChannel parent container matches (field numbers in ChannelDescriptor)
- WifiChannel parent container matches
- No new fields added in 16.2 beyond what was verified

**Step 2-5: Same pattern**

```bash
git commit -m "feat(verify-sdp): Wave 7 — Bluetooth + WiFi SDP confirmed against 16.2"
```

---

## Task 9: Wave 8 — CarControl + Remaining Channels

**Files:**
- Modify: `oaa/control/ChannelDescriptorData.proto` (inline placeholder messages)
- Verify: `oaa/control/VendorExtensionChannelData.proto`
- Verify: `oaa/notification/NotificationChannelData.proto`

**Step 1: Dispatch remaining channels agent**

- CarControlChannel — placeholder has 0 fields but vwo in 16.2 has 3. Fill in actual structure.
- VendorExtensionChannel — verify 3 fields against 16.2
- MediaBrowserChannel (vym) — verify still empty in 16.2
- NotificationChannel — verify still empty in 16.2
- GenericNotificationChannel (vwt) — verify still empty in 16.2
- VoiceChannel (vwd) — verify still empty in 16.2

**Step 2-5: Same pattern**

```bash
git commit -m "feat(verify-sdp): Wave 8 — CarControl filled, remaining channels verified"
```

---

## Task 10: Wave 9 — Connection Config + Common Protos

**Files:**
- Verify: `oaa/control/ConnectionConfigurationData.proto`
- Verify: `oaa/control/ControlChannelConfigMessage.proto`
- Verify: `oaa/control/ControlChannelConfigData.proto`
- Verify: `oaa/control/InputModelData.proto`
- Verify: `oaa/control/ConnectedDevicesMessages.proto`
- Verify: `oaa/common/PingConfigurationData.proto`
- Verify: `oaa/common/SessionInfoData.proto`
- Verify: `oaa/common/FeatureFlagsData.proto`
- Verify: `oaa/common/AssistantFeatureFlagsData.proto`

**Step 1: Dispatch connection config agent**

Largest wave — split into 2 agents if needed:

**Agent A — Connection config tree:**
- ConnectionConfiguration (16.1: aajk) — verify oneof structure, sub-message types
- ConnectionSecurityConfig, ConnectionTransportConfig, ConnectionFeatureFlags, ConnectionTuningConfig, ConnectionReservedConfig
- TransportMetadata, TransportCapabilities, TransportSecurityConfig
- ControlChannelConfigMessage (16.1: wcx, 16.2: wcn) — verify class reassignment
- ControlChannelConfigData — three-layer nesting

For placeholder sub-messages (TuningParamsA/B/C/D, TransportCapabilityEntry, etc.): verify they exist in 16.2, note field count, but mark internals as TODO.

**Agent B — Common protos + InputModel:**
- PingConfiguration (unverified, no audit file)
- SessionInfo (16.1: 4 string fields)
- FeatureFlags / VersionFeatureFlags
- AssistantFeatureFlags (14 bool fields)
- InputModelData messages (CapabilityConnectionConfig, InputModelDescriptor, InputModelEntry, HandwritingInputModelConfig)
- ConnectedDevicesMessages (Bronze, no implementation)

**Step 2-5: Same pattern**

```bash
git commit -m "feat(verify-sdp): Wave 9 — Connection config + common protos verified"
```

---

## Task 11: Final Report + Cleanup

**Files:**
- Create: `analysis/reports/proto-verification/sdp.md`
- Update: `analysis/reports/proto-verification/sdp-progress.md`
- Update: `analysis/reports/proto-verification/PROGRESS.md` (add SDP section)

**Step 1: Write SDP verification report**

Consolidate all wave findings into a single report covering:
- Total protos verified to Gold
- Schema errors found and fixed
- New protos or fields discovered
- Retractions
- TODO items (placeholder internals deferred)

**Step 2: Update main progress tracker**

Add SDP section to PROGRESS.md linking to the SDP report.

**Step 3: Final commit**

```bash
git add analysis/reports/proto-verification/sdp.md \
        analysis/reports/proto-verification/sdp-progress.md \
        analysis/reports/proto-verification/PROGRESS.md
git commit -m "docs(verify-sdp): final SDP verification report — all waves complete"
```

---

## Parallelization Notes

- **Wave 2 can run in parallel with Waves 3-5** (phone side is independent from HU side)
- **Wave 7 is a quick confirmation** — can potentially run alongside Wave 6 or 8
- **Wave 9 Agent A and Agent B** are independent and can run in parallel
- Each wave's commit depends on the previous wave's changes being applied first (proto files may overlap, especially ChannelDescriptorData.proto)
