from __future__ import annotations
from pathlib import Path
from typing import Any

# Locked main report section headers (10-RESEARCH.md section Report shape).
# Tests in test_walk_report.py will assert these appear in this order.
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

# Locked JSON top-level keys for the machine-readable report.
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


def build_walk_report(verdicts: list, run_date: str) -> dict[str, Any]:
    """Aggregate verdicts into a report dict with MAIN_REPORT_JSON_KEYS shape.

    Plan 10-02 implements the full aggregation.
    """
    raise NotImplementedError("Plan 10-02 implements build_walk_report")


def emit_md(report: dict, out_path: Path) -> None:
    """Write the markdown version of the walk report.

    Plan 10-02 implements; sections MUST appear in MAIN_REPORT_SECTION_HEADERS order.
    """
    raise NotImplementedError("Plan 10-02 implements emit_md")


def emit_json(report: dict, out_path: Path) -> None:
    """Write the JSON sidecar version of the walk report.

    Use json.dumps(data, sort_keys=True, indent=2) + trailing newline.
    """
    raise NotImplementedError("Plan 10-02 implements emit_json")


def build_worklist(pending_flags: list) -> dict[str, Any]:
    """Build the oem-match-pending-gold worklist for deep-trace prioritization.

    Plan 10-02 implements.
    """
    raise NotImplementedError("Plan 10-02 implements build_worklist")
