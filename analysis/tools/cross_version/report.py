"""Consistency report generator.

Produces a markdown report summarizing cross-version comparison results.
"""
from __future__ import annotations

from pathlib import Path

from analysis.tools.cross_version.compare import ComparisonResult
from analysis.tools.proto_schema_validator.models import IssueKind, Severity


def generate_report(
    results: list[ComparisonResult],
    output_path: Path,
    promotion_count: int = 0,
) -> int:
    """Generate a consistency report from comparison results.

    Args:
        results: ComparisonResult list from run_comparison.
        output_path: Path to write the markdown report.
        promotion_count: Number of sidecars promoted (for reporting).

    Returns:
        Exit code: 0 if no suspicious discrepancies, 1 otherwise.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = len(results)
    consistent = sum(1 for r in results if r.is_consistent)
    discrepant = total - consistent

    # Classify issues across all results
    expected_issues: list[tuple[ComparisonResult, any]] = []
    suspicious_issues: list[tuple[ComparisonResult, any]] = []

    for r in results:
        for issue in r.issues:
            if issue.kind == IssueKind.FIELD_ADDED:
                expected_issues.append((r, issue))
            elif issue.kind in (
                IssueKind.FIELD_REMOVED,
                IssueKind.FIELD_TYPE_CHANGED,
            ):
                suspicious_issues.append((r, issue))

    # Count version-specific mappings (those with pairs skipped due to null classes)
    version_specific = sum(
        1
        for r in results
        if len(r.pairs_compared) < len(r.mapping.apk_classes) - 1
    )

    lines = [
        "# Cross-Version Consistency Report\n",
        "## Summary\n",
        f"- **Total mappings compared:** {total}",
        f"- **Consistent (no suspicious divergence):** {consistent}",
        f"- **With discrepancies:** {discrepant}",
        f"- **Expected additions (newer versions):** {len(expected_issues)}",
        f"- **Suspicious issues (type changes/removals):** {len(suspicious_issues)}",
        f"- **Sidecars promoted:** {promotion_count}",
        "",
    ]

    # Discrepancies section
    lines.append("## Discrepancies\n")
    if suspicious_issues:
        lines.append(
            "| Mapping | Version Pair | Issue | Field | Detail |"
        )
        lines.append("|---|---|---|---|---|")
        for r, issue in suspicious_issues:
            pair_str = f"{issue.apk_class_v1} -> {issue.apk_class_v2}"
            lines.append(
                f"| {r.mapping.proto_message} "
                f"| {pair_str} "
                f"| {issue.kind.value} "
                f"| {issue.field_number} "
                f"| {issue.detail} |"
            )
        lines.append("")
    else:
        lines.append("No suspicious discrepancies found.\n")

    # Expected evolution section
    lines.append("## Expected Evolution (Field Additions)\n")
    if expected_issues:
        lines.append("| Mapping | Version Pair | Field | Detail |")
        lines.append("|---|---|---|---|")
        for r, issue in expected_issues:
            pair_str = f"{issue.apk_class_v1} -> {issue.apk_class_v2}"
            lines.append(
                f"| {r.mapping.proto_message} "
                f"| {pair_str} "
                f"| {issue.field_number} "
                f"| {issue.detail} |"
            )
        lines.append("")
    else:
        lines.append("No field additions detected across versions.\n")

    # Promotion section
    lines.append("## Promotion Summary\n")
    lines.append(f"- Consistent mappings eligible for promotion: {consistent}")
    lines.append(f"- Sidecars actually promoted: {promotion_count}")
    if promotion_count > 0:
        lines.append("- Promotion: bronze -> silver (apk_static + cross_version)")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")

    return 1 if suspicious_issues else 0
