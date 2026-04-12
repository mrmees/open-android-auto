from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone

from analysis.tools.coverage_dashboard.scanner import ScanResult

_TOOL_VERSION = "1.0.0"

_TIER_ORDER = ("bronze", "silver", "gold", "platinum", "retracted", "superseded")
_TIER_DISPLAY = {
    "bronze": "Bronze",
    "silver": "Silver",
    "gold": "Gold",
    "platinum": "Platinum",
    "retracted": "Retracted",
    "superseded": "Superseded",
}


def _git_head() -> str:
    """Get the current git HEAD hash, or 'unknown' if unavailable."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return "unknown"


def _run_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def render_markdown(result: ScanResult) -> str:
    """Format ScanResult into markdown report with 6 locked sections."""
    lines: list[str] = []
    lines.append("# Coverage Dashboard")
    lines.append("")

    # --- Section 1: Summary ---
    lines.append("## Summary")
    lines.append("")

    total_active = sum(
        c.bronze + c.silver + c.gold + c.platinum
        for c in result.per_channel.values()
    )
    total_retracted = sum(c.retracted for c in result.per_channel.values())
    total_superseded = sum(c.superseded for c in result.per_channel.values())
    total_bronze = sum(c.bronze for c in result.per_channel.values())
    total_silver = sum(c.silver for c in result.per_channel.values())
    total_gold = sum(c.gold for c in result.per_channel.values())
    total_platinum = sum(c.platinum for c in result.per_channel.values())

    coverage_pct = round(result.total_sidecars / result.total_protos * 100) if result.total_protos else 0

    headline = (
        f"{result.total_sidecars} sidecars covering {result.total_protos} protos "
        f"({coverage_pct}% coverage). "
        f"{total_platinum} Platinum / single-OEM, {total_gold} Gold, "
        f"{total_silver} Silver, {total_bronze} Bronze."
    )
    lines.append(headline)
    lines.append("")

    if result.pending_gold_count > 0:
        lines.append(
            f"{result.pending_gold_count} protos awaiting deep-trace for Platinum promotion "
            f"(oem_match_pending_gold)."
        )
        lines.append("")

    # --- Section 2: Per-Channel Tier Counts ---
    lines.append("## Per-Channel Tier Counts")
    lines.append("")
    lines.append("| Channel | Bronze | Silver | Gold | Platinum (s-OEM) | Retracted | Superseded | Total |")
    lines.append("|---------|--------|--------|------|------------------|-----------|------------|-------|")

    grand_total = [0, 0, 0, 0, 0, 0, 0]  # bronze, silver, gold, platinum, retracted, superseded, total
    for channel in sorted(result.per_channel.keys()):
        c = result.per_channel[channel]
        row_total = c.bronze + c.silver + c.gold + c.platinum + c.retracted + c.superseded
        lines.append(
            f"| {channel} | {c.bronze} | {c.silver} | {c.gold} | {c.platinum} | "
            f"{c.retracted} | {c.superseded} | {row_total} |"
        )
        grand_total[0] += c.bronze
        grand_total[1] += c.silver
        grand_total[2] += c.gold
        grand_total[3] += c.platinum
        grand_total[4] += c.retracted
        grand_total[5] += c.superseded
        grand_total[6] += row_total

    lines.append(
        f"| **Total** | **{grand_total[0]}** | **{grand_total[1]}** | **{grand_total[2]}** | "
        f"**{grand_total[3]}** | **{grand_total[4]}** | **{grand_total[5]}** | **{grand_total[6]}** |"
    )
    lines.append("")

    # --- Section 3: Evidence Type Breakdown ---
    lines.append("## Evidence Type Breakdown")
    lines.append("")

    # Discover all evidence types dynamically
    all_ev_types: set[str] = set()
    for tier_ev in result.evidence_by_tier.values():
        all_ev_types.update(tier_ev.keys())

    # Filter out types where ALL tiers have zero
    active_ev_types = sorted(
        t for t in all_ev_types
        if any(result.evidence_by_tier.get(tier, {}).get(t, 0) > 0 for tier in _TIER_ORDER)
    )

    if active_ev_types:
        header = "| Tier | " + " | ".join(active_ev_types) + " | Total |"
        separator = "|------|" + "|".join("-" * (len(t) + 2) for t in active_ev_types) + "|-------|"
        lines.append(header)
        lines.append(separator)

        for tier in _TIER_ORDER:
            tier_ev = result.evidence_by_tier.get(tier, {})
            vals = [tier_ev.get(t, 0) for t in active_ev_types]
            row_total = sum(vals)
            if row_total == 0:
                continue
            cells = " | ".join(str(v) for v in vals)
            lines.append(f"| {_TIER_DISPLAY[tier]} | {cells} | {row_total} |")
    else:
        lines.append("No evidence entries found.")

    lines.append("")

    # --- Section 4: Missing Sidecars ---
    lines.append("## Missing Sidecars")
    lines.append("")

    total_missing = sum(len(v) for v in result.missing_sidecars.values())
    if total_missing > 0:
        lines.append(f"{total_missing} proto files without audit sidecars:")
        lines.append("")
        for dir_name in sorted(result.missing_sidecars.keys()):
            protos = result.missing_sidecars[dir_name]
            lines.append(f"### {dir_name} ({len(protos)} missing)")
            lines.append("")
            for p in sorted(protos):
                lines.append(f"- {p}")
            lines.append("")
    else:
        lines.append("All proto files have audit sidecars.")
        lines.append("")

    # --- Section 5: Orphan Sidecars ---
    lines.append("## Orphan Sidecars")
    lines.append("")

    total_orphan = sum(len(v) for v in result.orphan_sidecars.values())
    if total_orphan > 0:
        lines.append(f"{total_orphan} orphan sidecars found:")
        lines.append("")
        for dir_name in sorted(result.orphan_sidecars.keys()):
            sidecars = result.orphan_sidecars[dir_name]
            lines.append(f"### {dir_name} ({len(sidecars)} orphan)")
            lines.append("")
            for s in sorted(sidecars):
                lines.append(f"- {s}")
            lines.append("")
    else:
        lines.append("No orphan sidecars found.")
        lines.append("")

    # --- Section 6: Dashboard Metadata ---
    lines.append("## Dashboard Metadata")
    lines.append("")
    lines.append(f"- **Run date:** {_run_date()}")
    lines.append(f"- **Tool version:** {_TOOL_VERSION}")
    lines.append(f"- **Total protos:** {result.total_protos}")
    lines.append(f"- **Total sidecars:** {result.total_sidecars}")
    lines.append(f"- **Sidecar directory:** oaa/")
    lines.append(f"- **Git HEAD:** {_git_head()}")
    lines.append("")

    return "\n".join(lines)


def _extract_tier_table(md: str) -> str:
    """Extract just the per-channel tier count table from full markdown."""
    in_section = False
    table_lines: list[str] = []
    for line in md.splitlines():
        if line.startswith("## Per-Channel Tier Counts"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip():
            table_lines.append(line)
    return "\n".join(table_lines)


def render_json(result: ScanResult) -> str:
    """Format ScanResult into JSON sidecar with top-level keys matching sections."""
    total_bronze = sum(c.bronze for c in result.per_channel.values())
    total_silver = sum(c.silver for c in result.per_channel.values())
    total_gold = sum(c.gold for c in result.per_channel.values())
    total_platinum = sum(c.platinum for c in result.per_channel.values())
    total_retracted = sum(c.retracted for c in result.per_channel.values())
    total_superseded = sum(c.superseded for c in result.per_channel.values())

    coverage_pct = round(result.total_sidecars / result.total_protos * 100) if result.total_protos else 0

    data = {
        "summary": {
            "total_sidecars": result.total_sidecars,
            "total_protos": result.total_protos,
            "coverage_pct": coverage_pct,
            "tiers": {
                "bronze": total_bronze,
                "silver": total_silver,
                "gold": total_gold,
                "platinum": total_platinum,
                "retracted": total_retracted,
                "superseded": total_superseded,
            },
            "pending_gold_count": result.pending_gold_count,
        },
        "per_channel_tier_counts": {
            channel: {
                "bronze": c.bronze,
                "silver": c.silver,
                "gold": c.gold,
                "platinum": c.platinum,
                "retracted": c.retracted,
                "superseded": c.superseded,
                "total": c.bronze + c.silver + c.gold + c.platinum + c.retracted + c.superseded,
            }
            for channel, c in sorted(result.per_channel.items())
        },
        "evidence_type_breakdown": {
            tier: dict(sorted(result.evidence_by_tier.get(tier, {}).items()))
            for tier in _TIER_ORDER
            if result.evidence_by_tier.get(tier)
        },
        "missing_sidecars": {
            k: sorted(v)
            for k, v in sorted(result.missing_sidecars.items())
        },
        "orphan_sidecars": {
            k: sorted(v)
            for k, v in sorted(result.orphan_sidecars.items())
        },
        "metadata": {
            "run_date": _run_date(),
            "tool_version": _TOOL_VERSION,
            "total_protos": result.total_protos,
            "total_sidecars": result.total_sidecars,
            "sidecar_directory": "oaa/",
            "git_head": _git_head(),
        },
    }

    return json.dumps(data, indent=2, sort_keys=True)
