from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from analysis.tools.promotion_walker.verdict import Verdict, VerdictKind

MAIN_REPORT_SECTION_HEADERS = (
    "## Summary",
    "## Platinum promotions",
    "## oem_match_pending_gold (Silver + Bronze flagged)",
    "## Explicitly unmatched (Silver in observed service, not seen)",
    "## Retraction review queue",
    "## Skipped sidecars",
    "## Unobserved services \u2014 no claim either way",
    "## Walker run metadata",
)

MAIN_REPORT_JSON_KEYS = (
    "metadata",
    "summary",
    "platinum_promotions",
    "pending_gold_flags",
    "nomatch_observations",
    "retraction_review_queue",
    "skipped_sidecars",
    "unobserved_services",
    "gold_counts_delta",
)


def _verdict_to_dict(v: Verdict) -> dict[str, Any]:
    return {
        "sidecar_path": v.sidecar_path,
        "proto_message": v.proto_message,
        "current_tier": v.current_tier,
        "verdict_kind": v.kind.value,
        "matched_rules": list(v.matched_rules),
        "nomatch_rules": list(v.nomatch_rules),
        "msg_seq": list(v.msg_seq),
        "ts_ms": list(v.ts_ms),
        "message_completeness": v.message_completeness,
        "channel_kind": v.channel_kind,
        "skip_reason": v.skip_reason,
        "contradiction_summary": v.contradiction_summary,
    }


def build_walk_report(
    verdicts: list[Verdict],
    run_date: str,
    metadata: dict[str, Any],
    unobserved_counts: dict[str, dict[str, int]],
    gold_before: int,
    platinum_before: int,
) -> dict[str, Any]:
    """Aggregate verdicts into a report dict with the 9 locked top-level keys."""

    kind_buckets: dict[VerdictKind, list[Verdict]] = defaultdict(list)
    for v in verdicts:
        kind_buckets[v.kind].append(v)

    promoted = [_verdict_to_dict(v) for v in kind_buckets[VerdictKind.PROMOTE_TO_PLATINUM]]
    pending = [_verdict_to_dict(v) for v in kind_buckets[VerdictKind.FLAG_PENDING_GOLD]]
    nomatch = [_verdict_to_dict(v) for v in kind_buckets[VerdictKind.NOMATCH_OBSERVATION]]
    contradicted = [_verdict_to_dict(v) for v in kind_buckets[VerdictKind.CONTRADICTION_REVIEW]]
    skipped = []
    for k in (
        VerdictKind.SKIP_RETRACTED, VerdictKind.SKIP_SUPERSEDED,
        VerdictKind.SKIP_ALREADY_PLATINUM, VerdictKind.SKIP_SCHEMA_INVALID,
        VerdictKind.SKIP_MISSING_GOLD_PREREQ, VerdictKind.SKIP_OUT_OF_SDP_SCOPE,
    ):
        skipped.extend(_verdict_to_dict(v) for v in kind_buckets[k])

    gold_after = gold_before - len(promoted)
    platinum_after = platinum_before + len(promoted)

    summary = {
        "total_verdicts": len(verdicts),
        "by_kind": {k.value: len(kind_buckets[k]) for k in VerdictKind},
        "gold_counts_delta": {
            "gold_before": gold_before,
            "gold_after": gold_after,
            "platinum_before": platinum_before,
            "platinum_after": platinum_after,
            "promotion_count": len(promoted),
        },
        "pending_gold_flag_count": len(pending),
        "skipped_count": len(skipped),
    }

    return {
        "metadata": metadata,
        "summary": summary,
        "platinum_promotions": sorted(promoted, key=lambda d: d["sidecar_path"]),
        "pending_gold_flags": sorted(pending, key=lambda d: d["sidecar_path"]),
        "nomatch_observations": sorted(nomatch, key=lambda d: d["sidecar_path"]),
        "retraction_review_queue": sorted(contradicted, key=lambda d: d["sidecar_path"]),
        "skipped_sidecars": sorted(skipped, key=lambda d: d["sidecar_path"]),
        "unobserved_services": unobserved_counts,
        "gold_counts_delta": summary["gold_counts_delta"],
    }


def emit_md(report: dict[str, Any], out_path: Path) -> None:
    """Write the markdown version with all 8 locked section headers in order."""
    lines: list[str] = []
    lines.append("# Phase 10 Promotion Walk Report")
    lines.append("")
    lines.append(f"**Walker run date:** {report['metadata'].get('walker_run_date', 'unknown')}")
    lines.append(f"**Capture:** {report['metadata'].get('capture_path', 'unknown')}")
    lines.append(f"**Capture sha256:** `{report['metadata'].get('capture_sha256', 'unknown')}`")
    lines.append("")

    # Section 1: Summary
    lines.append(MAIN_REPORT_SECTION_HEADERS[0])  # "## Summary"
    s = report["summary"]
    gcd = s["gold_counts_delta"]
    lines.append("")
    lines.append(f"- **Gold-counts delta (in scope):** Gold {gcd['gold_before']} \u2192 {gcd['gold_after']}; Platinum {gcd['platinum_before']} \u2192 {gcd['platinum_after']} (+{gcd['promotion_count']} promoted)")
    lines.append(f"- **Total verdicts:** {s['total_verdicts']}")
    lines.append(f"- **Platinum promotions:** {len(report['platinum_promotions'])}")
    lines.append(f"- **oem_match_pending_gold flags:** {s['pending_gold_flag_count']}")
    lines.append(f"- **Skipped sidecars:** {s['skipped_count']}")
    lines.append("")
    lines.append("**Single-OEM trap reminder:** All promotions in this walk cite single-OEM VW MIB3 OI 2024 evidence. Every Platinum badge renders as `Platinum / single-OEM` per TIER-02. Multi-OEM corroboration is a v2 problem.")
    lines.append("")

    # Section 2: Platinum promotions
    lines.append(MAIN_REPORT_SECTION_HEADERS[1])
    lines.append("")
    if report["platinum_promotions"]:
        lines.append("| Sidecar | Previous tier | Matched rules | msg_seq count |")
        lines.append("|---------|---------------|---------------|---------------|")
        for p in report["platinum_promotions"]:
            rules = ", ".join(p["matched_rules"])
            lines.append(f"| `{p['sidecar_path']}` | {p['current_tier']} | {rules} | {len(p['msg_seq'])} |")
    else:
        lines.append("_No promotions in this walk._")
    lines.append("")

    # Section 3: oem_match_pending_gold
    lines.append(MAIN_REPORT_SECTION_HEADERS[2])
    lines.append("")
    if report["pending_gold_flags"]:
        lines.append("See the companion worklist at `oem-match-pending-gold-worklist.md` for the full deep-trace guidance.")
        lines.append("")
        lines.append("| Sidecar | Tier | Rules |")
        lines.append("|---------|------|-------|")
        for p in report["pending_gold_flags"]:
            rules = ", ".join(p["matched_rules"])
            lines.append(f"| `{p['sidecar_path']}` | {p['current_tier']} | {rules} |")
    else:
        lines.append("_No Silver/Bronze flagged for deep-trace in this walk._")
    lines.append("")

    # Section 4: Explicitly unmatched
    lines.append(MAIN_REPORT_SECTION_HEADERS[3])
    lines.append("")
    if report["nomatch_observations"]:
        for p in report["nomatch_observations"]:
            rules = ", ".join(p["nomatch_rules"])
            lines.append(f"- `{p['sidecar_path']}` \u2014 {rules}")
    else:
        lines.append("_No explicitly unmatched entries in this walk._")
    lines.append("")

    # Section 5: Retraction review queue
    lines.append(MAIN_REPORT_SECTION_HEADERS[4])
    lines.append("")
    if report["retraction_review_queue"]:
        for p in report["retraction_review_queue"]:
            lines.append(f"- `{p['sidecar_path']}` \u2014 {p['contradiction_summary'] or 'contradiction surfaced'}")
    else:
        lines.append("_No contradictions surfaced in this walk._")
    lines.append("")

    # Section 6: Skipped sidecars
    lines.append(MAIN_REPORT_SECTION_HEADERS[5])
    lines.append("")
    if report["skipped_sidecars"]:
        lines.append("| Sidecar | Verdict | Reason |")
        lines.append("|---------|---------|--------|")
        for p in report["skipped_sidecars"]:
            reason = (p["skip_reason"] or "").replace("|", "\\|")
            lines.append(f"| `{p['sidecar_path']}` | {p['verdict_kind']} | {reason} |")
    else:
        lines.append("_No sidecars skipped in this walk._")
    lines.append("")

    # Section 7: Unobserved services
    lines.append(MAIN_REPORT_SECTION_HEADERS[6])
    lines.append("")
    unobs = report["unobserved_services"]
    if unobs:
        lines.append("| Directory | Count | Breakdown |")
        lines.append("|-----------|-------|-----------|")
        for directory, counts in sorted(unobs.items()):
            total = counts.get("total", sum(v for k, v in counts.items() if k != "total"))
            breakdown = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()) if k != "total")
            lines.append(f"| `{directory}` | {total} | {breakdown} |")
    else:
        lines.append("_All in-scope services were observed._")
    lines.append("")

    # Section 8: Walker run metadata
    lines.append(MAIN_REPORT_SECTION_HEADERS[7])
    lines.append("")
    md = report["metadata"]
    for k in sorted(md.keys()):
        lines.append(f"- **{k}:** `{md[k]}`")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def emit_json(report: dict[str, Any], out_path: Path) -> None:
    """Write the JSON sidecar with sorted keys + trailing newline."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def build_worklist(
    pending_verdicts: list[Verdict],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Build the worklist dict for oem-match-pending-gold sidecars."""
    by_dir: dict[str, int] = defaultdict(int)
    entries: list[dict[str, Any]] = []
    for v in pending_verdicts:
        if v.kind != VerdictKind.FLAG_PENDING_GOLD:
            continue
        directory = "/".join(v.sidecar_path.split("/")[:2])  # e.g. "oaa/av"
        by_dir[directory] += 1
        entries.append({
            "sidecar_path": v.sidecar_path,
            "proto_message": v.proto_message,
            "sidecar_tier": v.current_tier,
            "matched_rules": list(v.matched_rules),
            "msg_seq": list(v.msg_seq),
            "ts_ms": list(v.ts_ms),
            "reason_pending": "Silver/Bronze\u2192Platinum blocked by Gold prerequisite rule; needs deep-trace APK evidence",
        })
    return {
        "metadata": metadata,
        "summary": {
            "total": len(entries),
            "by_directory": dict(by_dir),
        },
        "pending_gold_entries": sorted(entries, key=lambda d: d["sidecar_path"]),
    }


def emit_worklist_md(worklist: dict[str, Any], out_path: Path) -> None:
    lines = ["# oem_match_pending_gold Worklist", ""]
    s = worklist["summary"]
    lines.append(f"**Total:** {s['total']} sidecars")
    lines.append("")
    lines.append("## Summary by directory")
    lines.append("")
    for d, n in sorted(s["by_directory"].items()):
        lines.append(f"- `{d}/`: {n}")
    lines.append("")
    lines.append("## Per-proto")
    lines.append("")
    lines.append("| Sidecar | Tier | Rules | Reason |")
    lines.append("|---------|------|-------|--------|")
    for e in worklist["pending_gold_entries"]:
        rules = ", ".join(e["matched_rules"])
        lines.append(f"| `{e['sidecar_path']}` | {e['sidecar_tier']} | {rules} | {e['reason_pending']} |")
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def emit_worklist_json(worklist: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(worklist, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
