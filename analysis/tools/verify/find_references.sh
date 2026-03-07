#!/bin/bash
# Find all references to a class in the decompiled APK source.
# Usage: ./find_references.sh <class_name> [context_lines]
#
# Searches for the class name as: type references, instantiations,
# field declarations, method parameters, and casts.

set -euo pipefail

JADX_DIR="$(dirname "$0")/../../aa-16.2/jadx-output/sources"
CLASS="${1:?Usage: find_references.sh <class_name> [context_lines]}"
CTX="${2:-3}"

if [ ! -d "$JADX_DIR" ]; then
    echo "ERROR: jadx output not found at $JADX_DIR" >&2
    exit 1
fi

echo "=== References to '$CLASS' in jadx output ==="
echo ""

# Find files that reference this class (excluding its own definition)
FILES=$(grep -rl --include="*.java" "\b${CLASS}\b" "$JADX_DIR" 2>/dev/null | grep -v "/${CLASS}\.java$" || true)

if [ -z "$FILES" ]; then
    echo "No external references found."
    exit 0
fi

COUNT=$(echo "$FILES" | wc -l)
echo "Found in $COUNT file(s):"
echo ""

for f in $FILES; do
    BASENAME=$(basename "$f" .java)
    echo "--- $BASENAME ($f) ---"
    grep -n -C "$CTX" "\b${CLASS}\b" "$f" | head -60
    echo ""
done
