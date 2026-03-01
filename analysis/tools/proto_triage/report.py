"""Markdown report generation for proto triage results."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from analysis.tools.proto_triage.score import TriageCategory, TriageResult


def generate_report(
    results: list[TriageResult],
    seed_count: int,
    universe_count: int,
) -> str:
    """Generate the full markdown triage report."""
    lines: list[str] = []

    # --- Summary ---
    by_cat: dict[TriageCategory, list[TriageResult]] = defaultdict(list)
    for r in results:
        by_cat[r.category].append(r)

    lines.append("# Proto Class Triage Report\n")
    lines.append("## Summary\n")
    lines.append("| Category | Count |")
    lines.append("|---|---|")
    lines.append(f"| Already mapped | {seed_count} |")
    for cat in TriageCategory:
        lines.append(f"| {cat.value} | {len(by_cat[cat])} |")
    lines.append(f"| **Total in APK** | **{universe_count}** |")
    lines.append("")

    # --- Wire Protocol Candidates ---
    wire_cats = [TriageCategory.WIRE_HIGH, TriageCategory.WIRE_MEDIUM, TriageCategory.WIRE_LOW]
    wire_results = [r for cat in wire_cats for r in by_cat[cat]]

    if wire_results:
        lines.append("## Wire Protocol Candidates\n")

        # Group by service, then by category
        by_service: dict[str, list[TriageResult]] = defaultdict(list)
        for r in wire_results:
            by_service[r.service_label].append(r)

        for service in sorted(by_service.keys()):
            svc_results = by_service[service]
            lines.append(f"### {service}\n")
            lines.append("| Class | Cat | Conf | Syntax | Fields | Sub-refs | Signals |")
            lines.append("|---|---|---|---|---|---|---|")
            for r in svc_results:
                sig_str = ", ".join(r.signals)
                lines.append(
                    f"| `{r.class_name}` | {r.category.value} | {r.confidence:.2f} "
                    f"| {r.proto_syntax or '(empty)'} | {r.field_count} "
                    f"| {r.sub_ref_count} | {sig_str} |"
                )
            lines.append("")

    # --- Internal Classifications ---
    internal = by_cat[TriageCategory.INTERNAL]
    if internal:
        lines.append("## Internal Classifications\n")
        lines.append("| Class | Conf | Syntax | Fields | Evidence |")
        lines.append("|---|---|---|---|---|")
        for r in internal:
            sig_str = ", ".join(r.signals)
            lines.append(
                f"| `{r.class_name}` | {r.confidence:.2f} "
                f"| {r.proto_syntax or '(empty)'} | {r.field_count} "
                f"| {sig_str} |"
            )
        lines.append("")

    # --- Utility ---
    utility = by_cat[TriageCategory.UTILITY]
    if utility:
        lines.append("## Utility / Framework Classes\n")
        lines.append("| Class | Conf | Syntax | Fields | Signals |")
        lines.append("|---|---|---|---|---|")
        for r in utility:
            sig_str = ", ".join(r.signals)
            lines.append(
                f"| `{r.class_name}` | {r.confidence:.2f} "
                f"| {r.proto_syntax or '(empty)'} | {r.field_count} "
                f"| {sig_str} |"
            )
        lines.append("")

    # --- Unknown — Manual Review ---
    unknown = by_cat[TriageCategory.UNKNOWN]
    if unknown:
        lines.append("## Unknown — Manual Review Needed\n")
        # Proto2 unknowns first (higher priority)
        proto2_unknown = [r for r in unknown if r.proto_syntax == "proto2"]
        proto3_unknown = [r for r in unknown if r.proto_syntax != "proto2"]

        if proto2_unknown:
            lines.append("### Proto2 (higher priority)\n")
            lines.append("| Class | Conf | Fields | Sub-refs | Signals |")
            lines.append("|---|---|---|---|---|")
            for r in proto2_unknown:
                sig_str = ", ".join(r.signals)
                lines.append(
                    f"| `{r.class_name}` | {r.confidence:.2f} "
                    f"| {r.field_count} | {r.sub_ref_count} "
                    f"| {sig_str} |"
                )
            lines.append("")

        if proto3_unknown:
            lines.append("### Proto3 (lower priority)\n")
            lines.append("| Class | Conf | Fields | Sub-refs | Signals |")
            lines.append("|---|---|---|---|---|")
            for r in proto3_unknown:
                sig_str = ", ".join(r.signals)
                lines.append(
                    f"| `{r.class_name}` | {r.confidence:.2f} "
                    f"| {r.field_count} | {r.sub_ref_count} "
                    f"| {sig_str} |"
                )
            lines.append("")

    return "\n".join(lines)


def write_report(report: str, output: Path) -> None:
    """Write report to file, creating parent dirs as needed."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
