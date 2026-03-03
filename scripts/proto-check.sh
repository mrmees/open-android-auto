#!/usr/bin/env bash
# proto-check.sh — Verify all published .proto files compile with protoc.
#
# Requires: protoc 3.12+ (tested with 3.21.12)
# Usage: bash scripts/proto-check.sh
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Find all .proto files under oaa/
mapfile -t PROTO_FILES < <(find "$REPO_ROOT/oaa" -name '*.proto' -type f | sort)

COUNT=${#PROTO_FILES[@]}

if [[ $COUNT -eq 0 ]]; then
    echo "ERROR: No .proto files found under oaa/"
    exit 2
fi

echo "Checking $COUNT proto files..."

if protoc --proto_path="$REPO_ROOT" --descriptor_set_out=/dev/null "${PROTO_FILES[@]}"; then
    echo "OK: All $COUNT proto files compile cleanly."
    exit 0
else
    echo "FAIL: protoc reported errors."
    exit 1
fi
