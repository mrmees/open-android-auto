from __future__ import annotations
from pathlib import Path
from typing import Any

# Type alias -- Plan 10-02 may refine
Index = dict[tuple[str, int, str], list[tuple[int, int]]]
# Keyed by (service, msg_type, direction) -> list of (seq, ts_ms)


def build_index(
    coverage_path: Path,
    messages_path: Path,
) -> Index:
    """Build in-memory index keyed by (service, msg_type, direction).

    Source: coverage.json.per_msg_type for attribution; messages.jsonl for
    (seq, ts_ms) indices. Plan 10-02 implements the full logic; see
    10-RESEARCH.md section Example 1.
    """
    raise NotImplementedError("Plan 10-02 implements build_index")


def build_sdp_kinds(sdp_values_path: Path) -> set[str]:
    """Return the set of channel_kind strings declared in VW SDP response.

    Plan 10-02 reads sdp-values.json.response.channels[*].channel_kind.
    """
    raise NotImplementedError("Plan 10-02 implements build_sdp_kinds")
