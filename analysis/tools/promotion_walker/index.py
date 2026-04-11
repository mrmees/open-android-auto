from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

Index = dict[tuple[str, int, str], list[tuple[int, int]]]


def build_index(
    coverage_path: Path,
    messages_path: Path,
) -> Index:
    """Build (service, msg_type, direction) -> [(seq, ts_ms), ...] index.

    Source: coverage.json.per_msg_type for attribution (Phase 7 is source of truth),
    messages.jsonl for (seq, ts_ms) of each populated msg_type.
    Walker does NOT re-attribute msg_types -- Phase 7's taxonomy is final.
    """
    cov = json.loads(Path(coverage_path).read_text())

    # Step 1: build a "tracked" map of (msg_type, direction) -> service from coverage.json
    tracked: dict[tuple[int, str], str] = {}
    for entry in cov.get("per_msg_type", []):
        svc = entry.get("service")
        if svc is None or svc == "control":
            continue
        tracked[(int(entry["msg_type"]), str(entry["direction"]))] = svc

    # Step 2: scan messages.jsonl once, collect (seq, ts_ms) for each tracked entry
    index: dict[tuple[str, int, str], list[tuple[int, int]]] = defaultdict(list)
    for line in Path(messages_path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        key2 = (int(rec["msg_type"]), str(rec["direction"]))
        svc = tracked.get(key2)
        if svc is None:
            continue
        index[(svc, key2[0], key2[1])].append((int(rec["seq"]), int(rec["ts_ms"])))

    return dict(index)


def build_sdp_kinds(sdp_values_path: Path) -> set[str]:
    """Return the set of channel_kind strings declared in VW SDP response."""
    sdp = json.loads(Path(sdp_values_path).read_text())
    channels = sdp.get("response", {}).get("channels", [])
    return {ch["channel_kind"] for ch in channels if ch.get("channel_kind")}


def build_classification(classification_path: Path) -> dict[tuple[int, str], str]:
    """Return (msg_type, direction) -> label dict from msg-type-classification.json."""
    data = json.loads(Path(classification_path).read_text())
    out: dict[tuple[int, str], str] = {}
    for entry in data.get("entries", []):
        key = (int(entry["msg_type"]), str(entry["direction"]))
        out[key] = str(entry["label"])
    return out
