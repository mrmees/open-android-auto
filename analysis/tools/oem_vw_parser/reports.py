from __future__ import annotations

from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path

from .models import ClassifiedRecord, FrequencyProfile


HEURISTIC_CAVEAT = (
    "> **Loud caveat:** This is a heuristic stack over a lossy capture format. The on-phone\n"
    "> hook lives inside the AA framing layer — `channel_id`, `flags`, and frame boundaries are\n"
    "> not visible. Continuation fragments inside multi-frame messages are interpreted as\n"
    "> standalone records by the wire format and must be filtered by the three-tier\n"
    "> plausibility gate. Real ground truth requires the framing-hook capture work tracked as\n"
    "> v2 CAP-01. Residual misclassifications will be visible in aggregate stats.\n"
)


def emit_classification_report(
    classified: list[ClassifiedRecord],
    profile: FrequencyProfile,
    out_path: Path,
    capture_id: str,
    capture_window_s: float,
    total_records: int,
) -> None:
    """Write the per-msg_type classification markdown report.

    Three sections: Tier Distribution, Label Distribution (5 atomic buckets),
    and Per-msg_type Classification table sorted by count desc. The
    HEURISTIC_CAVEAT block is rendered prominently near the top so naïve
    readers cannot mistake fragment classification rows for verified protocol
    messages.
    """
    buf = StringIO()
    buf.write("# VW Capture: Per-msg_type Classification\n\n")
    buf.write(f"**Capture:** `captures/{capture_id}/`\n")
    buf.write("**Capture version:** 5 (`native_interceptor_regnatives`)\n")
    buf.write(f"**Records:** {total_records:,} ({capture_window_s:.1f}s window)\n")
    buf.write(f"**Frequency threshold (empirical):** {profile.threshold}\n\n")
    buf.write(HEURISTIC_CAVEAT + "\n")

    # Tier distribution
    by_tier: Counter[str] = Counter(cr.tier for cr in classified)
    buf.write("## Tier Distribution\n\n")
    buf.write("| Tier | Records | % |\n|------|--------:|--:|\n")
    for tier in ("A", "B", "C"):
        count = by_tier.get(tier, 0)
        pct = (count / total_records * 100) if total_records else 0
        buf.write(f"| {tier} | {count:,} | {pct:.1f}% |\n")
    buf.write("\n")

    # Label distribution
    by_label: Counter[str] = Counter(cr.label for cr in classified)
    buf.write("## Label Distribution (5 buckets — atomic)\n\n")
    buf.write("| Label | Records |\n|-------|--------:|\n")
    for label in (
        "standalone",
        "probable_first",
        "continuation_or_garbage",
        "reassembled",
        "unattributed",
    ):
        buf.write(f"| {label} | {by_label.get(label, 0):,} |\n")
    buf.write("\n")
    buf.write("_`reassembled` is intentionally empty in Phase 7 — see 07-CONTEXT.md decisions._\n\n")
    buf.write("_`unattributed` is reserved for the attribution pipeline in plan 07-02._\n\n")

    # Per-msg_type table
    buf.write("## Per-msg_type Classification\n\n")
    buf.write("| msg_type | hex | tier | direction | count | label | notes |\n")
    buf.write("|---------:|-----|-----|-----------|------:|-------|-------|\n")
    grouped: dict[tuple[int, str, str, str], list[ClassifiedRecord]] = defaultdict(list)
    for cr in classified:
        key = (cr.record.msg_type, cr.record.direction, cr.tier, cr.label)
        grouped[key].append(cr)
    for (mt, direction, tier, label), records in sorted(
        grouped.items(), key=lambda k: -len(k[1])
    ):
        notes_sample = ",".join(records[0].notes) if records[0].notes else "—"
        buf.write(
            f"| {mt} | 0x{mt:04X} | {tier} | {direction} | "
            f"{len(records):,} | {label} | {notes_sample} |\n"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(buf.getvalue(), encoding="utf-8")
