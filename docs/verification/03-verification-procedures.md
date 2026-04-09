# 03 -- Verification Procedures

Step-by-step procedures for gathering each of the four evidence types. A contributor should be able to follow these instructions to verify any proto field or message and produce a valid evidence entry for an [audit trail file](02-audit-trail-format.md).

For evidence type definitions and promotion logic, see [01-confidence-tiers.md](01-confidence-tiers.md). For which sources are valid and excluded, see [04-source-provenance.md](04-source-provenance.md).

---

## 1. APK Static Analysis (`apk_static`)

### Prerequisites

- **jadx** (1.5.1 or later) for APK decompilation
- Decompiled APK source in the `analysis/` directory (currently available: 15.9, 16.1, 16.2)
- apk_indexer SQLite database (at `analysis/android_auto_<version>/apk-index/sqlite/apk_index.db`)

### Procedure

1. **Identify the target.** Determine which proto message or field you are verifying. Find the `.proto` file in the `oaa/` directory.

2. **Look up the obfuscated class.** Query the apk_indexer database to find the obfuscated class name that corresponds to your proto message:

   ```sql
   SELECT * FROM proto_classes WHERE proto_name LIKE '%YourMessageName%';
   ```

   Note: obfuscated class names differ between APK versions. Always record which version you are analyzing.

3. **Choose your analysis method.** Select the technique that best fits what you are verifying:

   - **`bfs_trace`** -- Follow field references from a known entry point through the call graph. Use when verifying message-to-field mappings (e.g., "field 10 of SensorEventIndication maps to NightMode"). Trace through the apk_indexer `call_edges` and `class_references` tables, or manually through jadx decompiled source.

   - **`enum_match`** -- Match enum constant values between decompiled code and proto enum definitions. Use when verifying enum fields. Look for switch maps (`switch_maps` table) and constant values (`constants` table) in the apk_indexer database.

   - **`string_const`** -- Find string constants that name or reference proto messages or fields. Use when proto names appear in log tags, error messages, or annotations. Query the `constants` table for string values matching message or field names.

   - **`proto_access`** -- Trace proto read/write patterns (e.g., `message.getField()`, `message.setField()`) to confirm field types and usage. Use the `proto_accesses` and `proto_writes` tables in the apk_indexer database.

   - **`call_graph`** -- Analyze call edges to understand how a message is constructed, sent, or processed. Use the `call_edges` table to trace execution flow through obfuscated methods.

   - **`switch_map`** -- Analyze switch map tables that dispatch on enum or field values. Use when verifying how enum values map to behavior. Query the `switch_maps` table.

4. **Perform the analysis.** Follow the method through the decompiled source or database queries. Record:
   - The obfuscated class name(s) examined
   - The APK version analyzed
   - The specific code location (class, method, line if available)
   - What the analysis revealed about the proto structure

5. **Create the evidence entry:**

   ```yaml
   - type: apk_static
     method: bfs_trace  # or enum_match, string_const, proto_access, etc.
     source: "APK 16.1 (jadx: wbo.java field 10 -> NightMode)"
     date: 2026-02-28
     description: "Field 10 of SensorEventIndication maps to NightMode message via BFS trace through obfuscated class wbo"
   ```

### Tips

- When in doubt about the obfuscated class mapping, check `proto_evidence` in the apk_indexer database for previously identified mappings.
- Multiple `apk_static` entries with different methods still count as **one evidence type** for tier promotion. To reach Silver, you need a different evidence type entirely.

---

## 2. DHU Observation (`dhu_observation`)

### Prerequisites

- Android phone with Android Auto installed
- Google Desktop Head Unit (DHU) version 2.1, available in the Android SDK at `extras/google/auto/`
- ADB access to the phone (wireless ADB recommended for simultaneous USB AA connection)
- DHU configuration file (e.g., `kitchen_sink.ini` for full sensor/input support)

### Procedure

1. **Set up the DHU.** Configure with the appropriate `.ini` file. The `kitchen_sink.ini` config enables all inputs, sensors, cluster display, and media playback at 720p. DHU configs are typically at `<android-sdk>/extras/google/auto/config/`.

2. **Connect the phone.** Connect via USB (AOA mode) or WiFi. The phone should launch Android Auto and connect to the DHU.

3. **Enable logcat capture.** On the phone, set up logcat capture via wireless ADB:

   ```bash
   adb connect <phone-ip>:5555
   adb logcat -v time > capture.log
   ```

   For targeted capture, filter by known tags:
   ```bash
   adb logcat -v time CAR.SENSOR.LITE:V CAR.GAL.*:V GH.*:V CAR.SYS:V CAR.WM:V *:S
   ```

4. **Trigger the behavior.** Depending on what you are verifying:
   - **Sensors:** Use DHU CLI commands (e.g., `night_mode true`, `fuel 0.75`)
   - **Navigation:** Start navigation on the phone and observe cluster/nav data
   - **Media:** Play media and observe metadata flow
   - **Input:** Use touchpad, rotary, or button inputs from the DHU

5. **Capture and analyze logcat output.** Look for relevant log tags:
   - `CAR.SENSOR.LITE` -- Raw sensor events
   - `CAR.GAL.RADIO-EP` -- Radio channel endpoint
   - `CAR.GAL.VIDEO` -- Video stream channel
   - `CAR.GAL.CAR_CONTROL` -- Car control channel
   - `GH.Radio` / `CAR.RADIO` -- Radio MediaBrowserService
   - `GH.MediaActiveContrConn` -- MediaBrowserService controller
   - `GH.NDirector` -- Navigation director

6. **Trace the message flow.** Follow the processing pipeline from raw event through to final handling. Document each stage observed in the logs.

7. **Create the evidence entry:**

   ```yaml
   - type: dhu_observation
     method: logcat_trace  # or cli_injection, behavioral_test
     source: "DHU 2.1 kitchen_sink.ini, logcat tag CAR.SENSOR.LITE"
     date: 2026-02-28
     description: "Injected night_mode=true via DHU CLI. Full pipeline traced: CAR.SENSOR.LITE -> getDayNightModeUserSetting -> updateDayNightMode(source=SENSOR) -> CAR.SYS -> CAR.WM"
   ```

### Method Tags

- **`logcat_trace`** -- Full pipeline trace via logcat tag filtering. The most detailed method -- captures the entire message processing chain.
- **`cli_injection`** -- Direct injection via DHU CLI commands. Confirms that the AA app processes the injected value, but may not reveal the full pipeline.
- **`behavioral_test`** -- Observed behavioral change (e.g., UI theme update, cluster data display) in response to a protocol event. Useful when logcat is silent but the effect is visible.

### Important Notes

- DHU observations are valid for Bronze and Silver but **never sufficient for Gold**. The DHU is a test harness, not a production environment.
- Some sensors are "silent" in logcat -- they are processed successfully but do not emit log messages. Speed (3), location (1), and fuel (6) fall into this category. For these, use `cli_injection` or `behavioral_test` methods.
- The `aa-logcat` capture tool has known issues on Android 13+ (logcat access is gated by foreground approval). Manual ADB logcat may be needed until Shizuku integration is complete.

---

## 3. OEM Wire Capture (`oem_capture`)

### Prerequisites

- Production OEM Android Auto head unit (NOT the DHU)
- Capture setup: USB sniffer (e.g., USB protocol analyzer) or network capture tool for wireless AA
- Android phone with Android Auto installed
- Proto definitions from `oaa/` directory for decoding captured messages

### Procedure

1. **Set up packet capture.** Position a capture device between the phone and the OEM head unit:
   - **Wired AA (USB):** Use a USB protocol analyzer or man-in-the-middle proxy
   - **Wireless AA (WiFi):** Use network packet capture (e.g., Wireshark on a monitoring interface)

2. **Connect and trigger behavior.** Connect the phone to the head unit normally. Trigger the specific behavior you want to verify (e.g., send a night mode change, start navigation, play media).

3. **Extract proto messages.** From the captured traffic:
   - Identify AA protocol frames (they follow the AA framing format)
   - Extract the proto payload from each frame
   - Identify the channel and message type from the frame header

4. **Decode the payload.** Use the `.proto` definitions from `oaa/` to decode the captured proto messages:

   ```bash
   protoc --decode=oaa.proto.data.NightMode oaa/sensor/NightModeData.proto < captured_payload.bin
   ```

5. **Compare against definitions.** Verify that:
   - Field numbers match the proto definition
   - Field types match (e.g., bool, int32, enum)
   - Enum values match defined values
   - Message nesting matches the expected structure

6. **Document the capture:**
   - OEM head unit make and model
   - Capture method and tools used
   - Raw capture file reference (if shareable; redact personal data)
   - Specific fields and values observed

7. **Create the evidence entry:**

   ```yaml
   - type: oem_capture
     source: "OEM [make/model], USB capture via [tool]"
     date: 2026-03-15
     description: "Captured NightMode message on sensor channel. Field 1 (is_night) observed as bool, value true when headlights activated. Field number and type match proto definition."
   ```

### Current Status

**No OEM captures are available yet in this project.** This procedure is documented for when they become available. Contributors with access to OEM head units are encouraged to capture and contribute wire data.

See the project roadmap for planned capture tooling (TOOL-03).

### Important Notes

- OEM capture is the **only evidence type** that can directly promote a claim to Gold tier. A single OEM capture is sufficient.
- Always redact personal information (GPS coordinates, contact names, etc.) from captures before sharing.
- Document the head unit model specifically -- different OEM implementations may behave differently.

---

## 4. Cross-Version Comparison (`cross_version`)

### Prerequisites

- apk_indexer SQLite databases for multiple APK versions (currently available: 15.9, 16.1, 16.2)
- Understanding that obfuscated class names differ between versions -- you cannot simply grep for the same class name

### Procedure

1. **Identify the proto structure in one version.** Start with the version where you have the strongest existing evidence (usually the one with an `apk_static` entry already). Note the obfuscated class name and the proto field structure.

2. **Map to other versions using enum fingerprinting.** Obfuscated class names change between APK versions. To find the equivalent class:

   - **`enum_fingerprint`** -- Extract the enum constant values from the known class. Search for classes in other versions with matching enum value sets. Enum values are stable across obfuscation because they are part of the proto wire format.

     ```sql
     -- Find enum values for known class in version A
     SELECT * FROM constants WHERE class_name = 'wbo' AND type = 'int';

     -- Search for matching pattern in version B's database
     SELECT class_name, value FROM constants
     WHERE type = 'int' AND value IN (1, 2, 3, 10, 11)
     GROUP BY class_name HAVING COUNT(*) >= 3;
     ```

   - **`package_trace`** -- Trace the package/module structure across versions. Even though class names change, the import patterns and package organization often remain similar.

3. **Compare proto structure.** Once you have the equivalent classes across versions, compare:
   - Field numbers (should be identical for stable proto fields)
   - Field types (bool, int32, string, enum, nested message, etc.)
   - Field names (if available in string constants or annotations)
   - Message nesting structure
   - Enum value definitions

4. **Document differences.** If structures differ between versions:
   - Record which versions were compared
   - Note specific differences (added fields, removed fields, type changes)
   - These differences are valuable -- they reveal proto evolution over time

5. **Assess stability.** Identical structure across 3 versions is strong corroborating evidence that the proto definition is correct and stable. Structural differences should be documented as version-specific annotations.

   - **`structure_match`** -- Use this method tag when the proto structure is confirmed identical across versions.

6. **Create the evidence entry:**

   ```yaml
   - type: cross_version
     method: enum_fingerprint
     source: "APK 15.9 (class abc), APK 16.1 (class wbo), APK 16.2 (class xyz)"
     date: 2026-03-01
     description: "NightMode message structure identical across 3 versions. Field 1 (is_night, bool) present in all. Mapped via enum fingerprint on SensorType values."
   ```

### Method Tags

- **`enum_fingerprint`** -- Matched classes across versions by enum value patterns. The most reliable cross-version mapping technique.
- **`structure_match`** -- Compared field numbers and types across versions and found them identical.
- **`package_trace`** -- Traced package/module structure across versions to identify equivalent classes.

### Important Notes

- `cross_version` counts as a **separate evidence type** from `apk_static`. Even though both derive from APK analysis, cross-version stability is a distinct signal from single-version static analysis.
- Always record which specific versions were compared and the obfuscated class name in each version.
- The apk_indexer databases for different versions are in separate directories under `analysis/`.

---

## General Notes

### Method Tags Are Open Vocabulary

The method tags listed above are conventions, not a closed set. Contributors may define new method tags as analysis techniques evolve. When introducing a new method tag:

- Choose a descriptive, lowercase, underscore-separated name
- Document what the method does in the evidence entry's `description` field
- Consider adding it to this document in a future PR if it becomes commonly used

### Evidence Entries Should Be Self-Contained

Each evidence entry should be understandable on its own. A reader should be able to understand:

- What source material was examined
- What analysis technique was applied
- What was found
- Why it supports the proto definition

Do not assume the reader has access to your local environment, tools, or prior context.

### When in Doubt

- **Is my evidence valid?** Check the source against [04-source-provenance.md](04-source-provenance.md).
- **What tier does my evidence produce?** Apply the promotion logic from [01-confidence-tiers.md](01-confidence-tiers.md).
- **How do I record it?** Follow the YAML format in [02-audit-trail-format.md](02-audit-trail-format.md).
- **Still unsure?** Raise the question in your PR. It is better to ask than to introduce ambiguity.

---

## 5. Platinum Evidence

Platinum evidence is OEM wire capture confirmation applied to a sidecar that
already has Gold prerequisites (deep-trace APK + cross-version). See
[01-confidence-tiers.md](01-confidence-tiers.md) for the tier ladder and
[05-oem-match-policy.md](05-oem-match-policy.md) for the `MATCH-*` rule IDs
this procedure cites. See
[06-capture-non-claim-boundary.md](06-capture-non-claim-boundary.md) for the
5 surfaces Platinum evidence CANNOT validate.

### Prerequisites

A proto MUST be at `confidence: gold` BEFORE it can receive a
`platinum_evidence` entry and be promoted to `confidence: platinum`. The
promotion ladder is strict: Bronze → Silver → Gold → Platinum. Bronze/Silver
protos that get matched in an OEM capture but lack Gold prerequisites
receive the sidecar-level flag `oem_match_pending_gold: true` and wait for
deep-trace analysis to land first.

The walker that consumes the `oem_match_pending_gold` worklist lives in
Phase 10.

### Procedure

1. **Verify the proto is already Gold.** Read the sidecar's `confidence:`
   field. If it is `silver` or `bronze`, set `oem_match_pending_gold: true`
   at the sidecar top level and stop — this proto is not eligible for
   Platinum promotion yet.

2. **Locate the proto in the OEM capture.** Use
   `analysis/reports/oem-vw/coverage.json` and
   `analysis/reports/oem-vw/msg-type-classification.json` to find the
   `msg_seq` indices (positions in `messages.jsonl`) and OEM-01 labels for
   the proto's messages.

3. **Classify the observation per OEM-01.** Record the
   `message_completeness` value from the OEM-01 taxonomy:
   - `standalone` full payload → enables `MATCH-02`
   - `reassembled` multi-fragment → enables `MATCH-03` (zero usage in v1.5)
   - `continuation_or_garbage` → triggers `NOMATCH-04` instead; do NOT
     promote
   - `probable_first` / `unattributed` → insufficient for Platinum; stay at
     Gold

4. **Determine applicability.** Set `applicability: message` if the whole
   message shape is confirmed, OR `applicability: fields` if only specific
   fields were verified. `applicability: fields` requires a populated
   `fields` list of field numbers or names; `applicability: message`
   requires the `fields` key to be OMITTED (the schema enforces this).

5. **Enumerate the satisfied MATCH rules.** Cross-reference
   [05-oem-match-policy.md](05-oem-match-policy.md) and cite EVERY rule that
   the observation satisfies. Cherry-picking a subset is not allowed. The
   minimum honest citation when only SDP-level evidence is available is
   `match_rules: [MATCH-08]`.

6. **Add the `platinum_evidence` entry.** Append a new entry to the
   sidecar's `evidence:` array. Required fields: `capture_path`,
   `vehicle_metadata` (`make`/`model`/`year`/`aa_version`), `msg_seq`,
   `ts_ms`, `message_completeness`, `attribution_method`, `oem_scope`,
   `applicability`, and `match_rules`. If `applicability == fields`, include
   the `fields` list. Do NOT modify or remove existing evidence entries —
   the Platinum entry sits alongside the pre-existing Gold evidence.

7. **Set the sidecar tier fields.** Change `confidence:` from `gold` to
   `platinum` and add `platinum_scope: single_oem` at the sidecar top level.
   Update `last_updated:` to today's date.

8. **Validate against the schema.** Run
   `jsonschema.validate(data, audit-schema)` against
   `docs/verification/audit-schema.json`. The schema enforces: `confidence:
   platinum` requires `platinum_scope`; `type: platinum_evidence` requires
   all 10 scope fields; `applicability: fields` requires the `fields` list;
   `applicability: message` forbids the `fields` list; `match_rules` rejects
   unknown IDs, duplicates, and empty lists.

### Worked examples

Worked examples land in Phase 10 after the first batch of real Platinum
promotions are produced. See `.planning/phases/10-gold-tier-promotion-walk/`
for the Phase 10 plan artifacts. Phase 9 Plan 01 committed one reference
example: `oaa/video/VideoFocusRequestMessage.audit.yaml`, promoted from
Gold to Platinum with a single-OEM `MATCH-08` (SDP descriptor match)
citation. Phase 10 will extend that entry with the real `msg_seq` /
`ts_ms` indices after deep inspection of `messages.jsonl`.
