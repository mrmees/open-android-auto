#!/bin/bash
# Extract message ID constants from a channel handler file.
# Usage: ./extract_msg_ids.sh <path_to_handler.java>
#
# Looks for numeric constants in the 0x8000+ range (32768+)
# and lower control message IDs, plus switch/if patterns.

set -euo pipefail

FILE="${1:?Usage: extract_msg_ids.sh <path_to_handler.java>}"

if [ ! -f "$FILE" ]; then
    echo "ERROR: File not found: $FILE" >&2
    exit 1
fi

BASENAME=$(basename "$FILE" .java)
echo "=== Message IDs in $BASENAME ==="
echo ""

echo "--- Decimal constants in 0x8000+ range (32768-33023) ---"
grep -n -oP '\b(327[6-9]\d|328[0-9]\d|329[0-9]\d|3[3-9]\d{3})\b' "$FILE" 2>/dev/null | sort -t: -k2 -n -u || echo "(none)"
echo ""

echo "--- Hex constants (0x8xxx or 0x000x) ---"
grep -n -oP '0x[89a-fA-F][0-9a-fA-F]{3}|0x000[0-9a-fA-F]' "$FILE" 2>/dev/null | sort -u || echo "(none)"
echo ""

echo "--- Lines with comparison/switch on message type ---"
grep -n -P '(==\s*327|==\s*0x8|case\s+327|case\s+0x8|!=\s*327|!=\s*0x8)' "$FILE" 2>/dev/null || echo "(none)"
echo ""

echo "--- Send/write calls with numeric ID ---"
grep -n -P '(send|write|m\d+.*l)\(.*\b(327[6-9]\d|0x8)' "$FILE" 2>/dev/null || echo "(none)"
echo ""

echo "--- All lines with 3276x or 3277x or 3278x ---"
grep -n -P '\b3276[89]|3277[0-9]|3278[0-9]\b' "$FILE" 2>/dev/null || echo "(none)"
