# Analysis

Tools and indexed data from reverse engineering the Android Auto protocol via APK decompilation and wire captures.

## Indexed APK Data

| Directory | Version | Contents |
|-----------|---------|----------|
| `android_auto_16.2.660604-release_162660604/` | v16.2 | JSON + SQLite index (current) |
| `database/apk_index.db` | v16.1 | SQLite database (155MB, projection-scope) |

### Key tables in apk_index.db

- `uuids` — Service and characteristic UUIDs
- `constants` — Named constants and their values
- `proto_accesses` — Protobuf field read/write locations
- `proto_writes` — Protobuf message construction sites
- `enum_maps` — Enum value mappings
- `switch_maps` — Switch statement case mappings
- `call_edges` — Method call graph edges

Query example:
```sql
SELECT * FROM constants WHERE name LIKE '%CHANNEL%';
```

## Tools

### tools/apk_indexer/

Extracts and indexes protocol-relevant data from decompiled Android Auto APKs: UUIDs, constants, protobuf field accesses, enum mappings, switch maps, and call edges. Outputs JSON and SQLite.

See `tools/apk_indexer/README.md` for usage.

### tools/proto_stream_validator/

Schema regression checker for protobuf definitions against recorded non-media AA wire captures. Compares decoded output against locked baselines and supports explicit bless updates (`--bless --reason ...`) for intentional schema changes.

See `tools/proto_stream_validator/README.md` for capture format and commands.

### tools/proto_triage/

Scores and prioritizes unidentified proto classes from the APK index using BFS graph traversal, hub-file analysis, package proximity, and structural signals.

### tools/seed_import/

Imports proto seed definitions from APK analysis into the `oaa/` proto tree. Includes `annotate.py` which syncs `.audit.yaml` confidence comments into proto files.

### tools/cross_version/

Compares proto definitions across APK versions (v16.1 vs v16.2). Generates diff reports and promotes audit sidecars when fields are confirmed stable across versions.

### tools/proto_schema_validator/

Validates proto schema definitions against APK class mappings. Two-layer approach: structural schema validation and wire-format verification.

### tools/interaction_docs/

Generates the session lifecycle documentation in `docs/interactions/` from protocol analysis.

## Captures

Wire captures from AA sessions are stored in `captures/` (top-level) and `captures/non_media/` (analysis-scoped). See `baselines/non_media/` for locked regression baselines.
