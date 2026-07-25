# 02 -- Audit Trail Format

## Sidecar Convention

Each `.proto` file in `oaa/` gets a co-located `.audit.yaml` sidecar file with the same basename. The audit file records the current verification state and evidence trail for the proto definitions in that file.

```
oaa/sensor/NightModeData.proto        # Proto definition
oaa/sensor/NightModeData.audit.yaml   # Verification evidence
```

One audit file per proto file. The `message` field names the primary message defined in the proto file.

For proto files that define multiple messages, the top-level `message` and `confidence` apply to the primary message. Use the `fields` map to override confidence for individual fields, or add additional top-level entries in the same YAML file as separate documents (using `---` document separators) for secondary messages that need independent tracking.

In practice, most proto files define a single message. Keep it simple -- use `fields` overrides only when a specific field's confidence genuinely differs from the message-level tier.

---

## YAML Format Specification

### Top-Level Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `proto` | Yes | string | Relative path to the `.proto` file from the repo root. Must match pattern `oaa/*.proto`. |
| `message` | Yes | string | Primary message name defined in this proto file. |
| `confidence` | Yes | string | Current overall tier: `unverified`, `bronze`, `silver`, `gold`, `platinum`, or `retracted`. Lowercase. See [01-confidence-tiers.md](01-confidence-tiers.md) for the full tier ladder and retracted-state semantics. |
| `evidence` | No | list | Ordered list of evidence entries. Defaults to empty list `[]`. |
| `fields` | No | map | Per-field overrides. Keys are field names, values are override objects. |
| `platinum_scope` | Conditional | string | `single_oem` or `multi_oem`. REQUIRED when `confidence: platinum`; omitted otherwise. See [01-confidence-tiers.md](01-confidence-tiers.md) for the single-OEM trap explanation. |
| `oem_match_pending_gold` | No | bool | Phase 10 worklist flag — `true` only when a Silver/Bronze proto has qualifying message/field OEM evidence but lacks Gold prerequisites. MATCH-08-only service bindings do not qualify. |

### Evidence Entry Fields

Each entry in the `evidence` list has these fields:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `type` | Yes | string | One of: `apk_static`, `dhu_observation`, `oem_capture`, `cross_version`, `platinum_evidence`, `deep_trace`, `apk_deep_trace`. See [01-confidence-tiers.md](01-confidence-tiers.md) and [05-oem-match-policy.md](05-oem-match-policy.md) for Platinum/Gold evidence semantics. |
| `method` | No | string | Sub-method tag (free-form). See [03-verification-procedures.md](03-verification-procedures.md) for suggested values. |
| `source` | Yes | string | Human-readable source reference. Include enough detail to locate the raw material (APK version, tool, class name, DHU version, config, etc.). |
| `date` | Yes | string | ISO 8601 date (`YYYY-MM-DD`) when the evidence was gathered. |
| `description` | Yes | string | What was found and how. Should be self-contained -- a reader should understand the finding without needing external context. |

> **Platinum evidence entries** additionally carry 10 scope fields:
> `capture_path`, `vehicle_metadata`, `msg_seq`, `ts_ms`,
> `message_completeness`, `attribution_method`, `oem_scope`, `applicability`,
> optional `fields` list, and `match_rules` (closed enum of `MATCH-*` rule
> IDs). See [01-confidence-tiers.md](01-confidence-tiers.md) for the
> Platinum tier semantics and [05-oem-match-policy.md](05-oem-match-policy.md)
> for the rule IDs. Phase 9 added the retracted tier and the Platinum tier;
> [03-verification-procedures.md](03-verification-procedures.md) describes
> the platinum_evidence authoring procedure.

### Field Override Object

Each entry in the `fields` map has these fields:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `confidence` | Yes | string | Tier for this specific field: `unverified`, `bronze`, `silver`, `gold`, `platinum`, or `retracted`. |
| `evidence` | No | list | Evidence entries specific to this field (same structure as top-level evidence). |
| `notes` | No | string | Free-form notes about this field's verification status. |

---

## Worked Example: NightMode Sensor

This example shows the real progression of the `NightMode` message from initial seed import through verification. All data is drawn from actual project findings.

### Stage 1 -- Unverified (Phase 2 seed import)

When a proto file is first imported from Phase 2 schema extraction, its audit file starts empty:

```yaml
proto: oaa/sensor/NightModeData.proto
message: NightMode
confidence: unverified
evidence: []
```

This is the minimal valid audit file. The message is known to exist but no structured evidence has been recorded yet.

### Stage 2 -- Bronze (APK static analysis added)

A contributor traces the field mapping through decompiled APK code and records the finding:

```yaml
proto: oaa/sensor/NightModeData.proto
message: NightMode
confidence: bronze
evidence:
  - type: apk_static
    method: bfs_trace
    source: "APK 16.1 (jadx: wbo.java field 10 -> NightMode)"
    date: 2026-02-28
    description: "Field 10 of SensorEventIndication maps to NightMode message via BFS trace through obfuscated class wbo"
```

One evidence entry from one evidence type promotes the claim from Unverified to Bronze.

### Stage 3 -- Silver (DHU observation added)

A second contributor (or the same one, later) observes the behavior at runtime through the DHU:

```yaml
proto: oaa/sensor/NightModeData.proto
message: NightMode
confidence: silver
evidence:
  - type: apk_static
    method: bfs_trace
    source: "APK 16.1 (jadx: wbo.java field 10 -> NightMode)"
    date: 2026-02-28
    description: "Field 10 of SensorEventIndication maps to NightMode message via BFS trace through obfuscated class wbo"
  - type: dhu_observation
    method: logcat_trace
    source: "DHU 2.1 kitchen_sink.ini, logcat tag CAR.SENSOR.LITE"
    date: 2026-02-28
    description: "Injected night_mode=true via DHU CLI. Full pipeline traced: CAR.SENSOR.LITE -> getDayNightModeUserSetting -> updateDayNightMode(source=SENSOR) -> CAR.SYS -> CAR.WM"
```

Two distinct evidence types (`apk_static` + `dhu_observation`) promote the claim to Silver.

### What would it take to reach Gold?

Adding a reproducible `cross_version` entry with exact APK-version/class pairs
would still leave this claim at **Silver** until a primary handler/deep trace
also pins the message identity. Those two prerequisites promote it to Gold.
A qualifying message/field OEM capture can then promote the Gold-qualified
claim to scoped Platinum; OEM evidence does not skip Gold.

---

## Confidence Consistency Rule

The `confidence` field MUST match the promotion logic from
[01-confidence-tiers.md](01-confidence-tiers.md) applied independently to the
evidence list and retraction record:

- An explicit retraction record yields the non-ordinal `retracted` state.
- Gold requires both a primary handler/deep trace and one reproducible
  `cross_version` entry naming exact class mappings across 2+ APK versions.
- Platinum requires every Gold prerequisite, qualifying message/field OEM
  evidence, and `platinum_scope`.
- Otherwise, 2+ distinct evidence types yield Silver, one type yields Bronze,
  and no evidence yields Unverified. Duplicate entries of one type still count
  as one type.
- `oem_match_pending_gold` is valid only for Bronze/Silver sidecars with
  qualifying pending message/field OEM evidence; it is invalid for Gold,
  Platinum, Retracted, and MATCH-08-only service bindings.

If the `confidence` field and the evidence list disagree, the audit file is **invalid**. Future tooling will enforce this automatically. For now, contributors must self-verify before committing.

The same rule applies to per-field overrides in the `fields` map -- each field's `confidence` must be consistent with its own `evidence` list.

---

## Git History as Changelog

Audit files represent **current state only**. They do not contain history or changelog sections.

To see when a field was promoted from Bronze to Silver, or when a new evidence entry was added, use git history:

```bash
git log --follow oaa/sensor/NightModeData.audit.yaml
git blame oaa/sensor/NightModeData.audit.yaml
```

This keeps audit files clean and avoids duplication between the YAML content and git's built-in change tracking.

---

## Validation

Audit YAML files can be validated against the JSON Schema at [audit-schema.json](audit-schema.json). The schema enforces required fields, valid enum values, and structural constraints.

To validate manually:

```bash
# Using Python (jsonschema library)
pip install jsonschema pyyaml
python3 -c "
import yaml, json, jsonschema
schema = json.load(open('docs/verification/audit-schema.json'))
audit = yaml.safe_load(open('oaa/sensor/NightModeData.audit.yaml'))
jsonschema.validate(audit, schema)
print('Valid')
"
```

---

## See Also

- [01-confidence-tiers.md](01-confidence-tiers.md) -- Tier definitions and promotion logic
- [03-verification-procedures.md](03-verification-procedures.md) -- Step-by-step procedures for gathering each evidence type
- [04-source-provenance.md](04-source-provenance.md) -- Which sources are valid and excluded
- [audit-schema.json](audit-schema.json) -- JSON Schema for audit YAML validation
