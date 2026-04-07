from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from .models import ClassifiedRecord, FrequencyProfile


def emit_classification_json(
    classified: list[ClassifiedRecord],
    profile: FrequencyProfile,
    out_path: Path,
    capture_id: str,
    total_records: int,
) -> None:
    """Write the per-msg_type classification machine-readable manifest.

    Sorted entries by descending count then ascending msg_type. Stable JSON
    output (sort_keys=True, indent=2, trailing newline) so re-runs produce
    byte-identical files when the input hasn't changed.
    """
    by_tier: Counter[str] = Counter(cr.tier for cr in classified)
    by_label: Counter[str] = Counter(cr.label for cr in classified)
    grouped: dict[tuple[int, str, str, str], int] = defaultdict(int)
    for cr in classified:
        grouped[(cr.record.msg_type, cr.record.direction, cr.tier, cr.label)] += 1

    entries = []
    for (mt, direction, tier, label), count in sorted(
        grouped.items(), key=lambda k: (-k[1], k[0][0])
    ):
        entries.append(
            {
                "msg_type": mt,
                "msg_type_hex": f"0x{mt:04X}",
                "direction": direction,
                "tier": tier,
                "label": label,
                "count": count,
            }
        )

    payload = {
        "capture_id": capture_id,
        "total_records": total_records,
        "tier_counts": {k: by_tier.get(k, 0) for k in ("A", "B", "C")},
        "label_counts": {
            k: by_label.get(k, 0)
            for k in (
                "standalone",
                "probable_first",
                "continuation_or_garbage",
                "reassembled",
                "unattributed",
            )
        },
        "freq_threshold": profile.threshold,
        "freq_threshold_source": profile.source,
        "entries": entries,
        "notes": {
            "reassembled": "intentionally empty per Phase 7 CONTEXT.md",
            "unattributed": "reserved for plan 07-02 attribution pipeline",
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
