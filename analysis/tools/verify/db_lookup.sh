#!/bin/bash
# Look up a proto class in the APK index database.
# Usage: ./db_lookup.sh <class_name>
#
# Dumps: proto fields, enum values, evidence, and decoded fields.

set -euo pipefail

DB="$(dirname "$0")/../../android_auto_16.2.660604-release_162660604/apk-index/sqlite/apk_index.db"
CLASS="${1:?Usage: db_lookup.sh <class_name>}"

if [ ! -f "$DB" ]; then
    echo "ERROR: Database not found at $DB" >&2
    exit 1
fi

echo "=== Proto class: $CLASS ==="
echo ""

echo "--- Class info ---"
sqlite3 -header -column "$DB" \
    "SELECT class_name, field_count, proto_syntax, deprecated FROM proto_classes WHERE class_name='$CLASS';"
echo ""

echo "--- Fields ---"
sqlite3 -header -column "$DB" \
    "SELECT field_number, type_label, base_type, type_id, is_repeated, is_packed, optional, required, is_oneof, is_map, enum_closed FROM proto_fields WHERE class_name='$CLASS' ORDER BY field_number;"
echo ""

echo "--- Decoded fields (JSON) ---"
sqlite3 "$DB" \
    "SELECT decoded_fields FROM proto_classes WHERE class_name='$CLASS';"
echo ""

echo "--- Sub-message references ---"
sqlite3 "$DB" \
    "SELECT sub_message_refs FROM proto_classes WHERE class_name='$CLASS';"
echo ""

echo "--- Enum values (if enum class) ---"
sqlite3 -header -column "$DB" \
    "SELECT enum_class, enum_name, int_value FROM enum_maps WHERE enum_class='$CLASS' ORDER BY int_value;"
echo ""

echo "--- Evidence ---"
sqlite3 -header -column "$DB" \
    "SELECT evidence_source, evidence_detail, source_file, line FROM proto_evidence WHERE class_name='$CLASS';"
echo ""

echo "--- Referenced by (other protos with this class as sub_message_ref) ---"
sqlite3 -header -column "$DB" \
    "SELECT class_name, field_count, proto_syntax FROM proto_classes WHERE sub_message_refs LIKE '%$CLASS%';"
