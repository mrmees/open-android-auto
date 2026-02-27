# Analysis Tools

These tools are included for personal development reference and have no current functionality as standalone utilities. They were used during reverse engineering of the Android Auto protocol and are provided as-is.

## Contents

### tools/apk_indexer/

Python scripts used to extract and index protocol-relevant data from the Android Auto APK (v16.1). Extracts UUIDs, constants, protobuf field accesses, enum mappings, switch maps, and call edges.

See `tools/apk_indexer/README.md` for usage details.

### database/apk_index.db

Pre-built SQLite database containing indexed data from Android Auto APK v16.1.660414-release. Key tables:

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
