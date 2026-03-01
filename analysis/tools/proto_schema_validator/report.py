"""Generate markdown validation reports."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from analysis.tools.proto_schema_validator.models import (
    DriftIssue,
    IssueKind,
    SchemaIssue,
    Severity,
    WireIssue,
)


def _severity_icon(s: Severity) -> str:
    if s == Severity.ERROR:
        return "ERROR"
    if s == Severity.WARNING:
        return "WARN"
    return "INFO"


def _group_by_message(issues: list) -> dict[str, list]:
    grouped: dict[str, list] = {}
    for issue in issues:
        key = getattr(issue, "proto_message", None) or getattr(issue, "apk_class_v1", "unknown")
        grouped.setdefault(key, []).append(issue)
    return dict(sorted(grouped.items()))


def generate_report(
    schema_issues: list[SchemaIssue] | None = None,
    wire_issues: list[WireIssue] | None = None,
    drift_issues: list[DriftIssue] | None = None,
    mapping_count: int = 0,
    validated_count: int = 0,
    wire_stats: dict | None = None,
    drift_stats: dict | None = None,
) -> str:
    """Generate a full markdown validation report."""
    lines: list[str] = []
    lines.append("# Proto Schema Validation Report\n")

    # Summary
    lines.append("## Summary\n")
    lines.append(f"- **Mapped protos:** {mapping_count}")
    lines.append(f"- **Validated (with APK class):** {validated_count}")

    if schema_issues is not None:
        errs = sum(1 for i in schema_issues if i.severity == Severity.ERROR)
        warns = sum(1 for i in schema_issues if i.severity == Severity.WARNING)
        lines.append(f"- **Layer 1 (Schema vs APK):** {errs} errors, {warns} warnings")

    if wire_issues is not None:
        errs = sum(1 for i in wire_issues if i.severity == Severity.ERROR)
        warns = sum(1 for i in wire_issues if i.severity == Severity.WARNING)
        lines.append(f"- **Layer 2 (Wire capture):** {errs} errors, {warns} warnings")
        if wire_stats:
            lines.append(f"  - Frames decoded: {wire_stats.get('decoded', 0)}")
            lines.append(f"  - Frames failed: {wire_stats.get('failed', 0)}")
            lines.append(f"  - Frames unmapped: {wire_stats.get('unmapped', 0)}")

    if drift_issues is not None:
        lines.append(f"- **Layer 3 (Cross-version):** {len(drift_issues)} findings")
        if drift_stats:
            lines.append(f"  - Structural matches found: {drift_stats.get('matches', 0)}")

    lines.append("")

    # Layer 1 detail
    if schema_issues is not None:
        lines.append("## Layer 1: Schema vs APK Database\n")

        # Issue type breakdown
        kind_counts = Counter(i.kind.value for i in schema_issues)
        if kind_counts:
            lines.append("### Issue Breakdown\n")
            lines.append("| Issue Type | Count |")
            lines.append("|---|---|")
            for kind, cnt in kind_counts.most_common():
                lines.append(f"| {kind} | {cnt} |")
            lines.append("")

        # Per-message details
        grouped = _group_by_message(schema_issues)
        lines.append("### Per-Message Details\n")
        for msg, issues in grouped.items():
            errs = sum(1 for i in issues if i.severity == Severity.ERROR)
            warns = sum(1 for i in issues if i.severity == Severity.WARNING)
            lines.append(f"#### {msg} ({errs}E / {warns}W)\n")
            for issue in sorted(issues, key=lambda i: (i.field_number or 0)):
                icon = _severity_icon(issue.severity)
                lines.append(f"- **[{icon}]** `{issue.kind.value}`: {issue.detail}")
            lines.append("")

    # Layer 2 detail
    if wire_issues is not None:
        lines.append("## Layer 2: Wire Capture Validation\n")
        grouped = _group_by_message(wire_issues)
        for msg, issues in grouped.items():
            lines.append(f"#### {msg}\n")
            for issue in issues:
                icon = _severity_icon(issue.severity)
                frame_note = f" (frame {issue.frame_index})" if issue.frame_index is not None else ""
                lines.append(f"- **[{icon}]** `{issue.kind.value}`: {issue.detail}{frame_note}")
            lines.append("")

    # Layer 3 detail
    if drift_issues is not None:
        lines.append("## Layer 3: Cross-Version Drift\n")
        grouped: dict[str, list] = {}
        for issue in drift_issues:
            key = f"{issue.apk_class_v1} -> {issue.apk_class_v2 or '?'}"
            grouped.setdefault(key, []).append(issue)
        for key, issues in sorted(grouped.items()):
            lines.append(f"#### {key}\n")
            for issue in issues:
                icon = _severity_icon(issue.severity)
                lines.append(f"- **[{icon}]** `{issue.kind.value}`: {issue.detail}")
            lines.append("")

    return "\n".join(lines)


def write_report(report: str, output: Path) -> None:
    """Write report to file."""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
