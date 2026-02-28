# APK Indexer Query Pack

This pack contains ready-to-run SQL templates for catalog review after running
the indexer.

## Prerequisite

Build the index first:

```bash
python3 analysis/tools/apk_indexer/run_indexer.py \
  --source <decompiled-apk-root> \
  --analysis-root analysis \
  --scope all
```

Open the generated DB:

```bash
sqlite3 analysis/android_auto_<version>/apk-index/sqlite/apk_index.db
```

## Queries

1. `sql/01_catalog_overview.sql`  
   Shows accepted catalog totals by confidence tier.

2. `sql/02_proto_field_matrix.sql`  
   Shows accepted catalog entries sorted by field count.

3. `sql/03_unknown_queue.sql`  
   Shows unknown queue entries sorted for manual triage.

Run any query file from repo root:

```bash
sqlite3 analysis/android_auto_<version>/apk-index/sqlite/apk_index.db \
  < analysis/tools/apk_indexer/sql/01_catalog_overview.sql
```
