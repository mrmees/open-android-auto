from __future__ import annotations
from pathlib import Path

from analysis.tools.promotion_walker.report import (
    build_walk_report, build_worklist, emit_md, emit_json,
    MAIN_REPORT_SECTION_HEADERS, MAIN_REPORT_JSON_KEYS,
)
from analysis.tools.promotion_walker.verdict import Verdict, VerdictKind


def _synthetic_verdicts() -> list[Verdict]:
    return [
        Verdict("oaa/media/A.audit.yaml", "A", "gold", VerdictKind.PROMOTE_TO_PLATINUM,
                matched_rules=("MATCH-08",), channel_kind="media_info_channel"),
        Verdict("oaa/av/B.audit.yaml", "B", "silver", VerdictKind.FLAG_PENDING_GOLD,
                matched_rules=("MATCH-08",), channel_kind="av_channel"),
        Verdict("oaa/video/C.audit.yaml", "C", "platinum", VerdictKind.SKIP_ALREADY_PLATINUM,
                skip_reason="already_platinum"),
    ]


def test_locked_top_level_keys() -> None:
    verdicts = _synthetic_verdicts()
    report = build_walk_report(
        verdicts, "2026-04-09",
        metadata={"walker_run_date": "2026-04-09"},
        unobserved_counts={},
        gold_before=1, platinum_before=1,
    )
    assert tuple(sorted(report.keys())) == tuple(sorted(MAIN_REPORT_JSON_KEYS))


def test_locked_section_headers(tmp_path: Path) -> None:
    verdicts = _synthetic_verdicts()
    report = build_walk_report(
        verdicts, "2026-04-09",
        metadata={"walker_run_date": "2026-04-09", "capture_path": "x",
                  "capture_sha256": "x"},
        unobserved_counts={},
        gold_before=1, platinum_before=1,
    )
    out = tmp_path / "walk.md"
    emit_md(report, out)
    text = out.read_text()
    last_idx = -1
    for header in MAIN_REPORT_SECTION_HEADERS:
        idx = text.find(header)
        assert idx != -1, f"missing section header: {header}"
        assert idx > last_idx, f"section header out of order: {header}"
        last_idx = idx


def test_worklist_generated_from_pending_flags() -> None:
    verdicts = _synthetic_verdicts()
    worklist = build_worklist(verdicts, metadata={"walker_run_date": "2026-04-09"})
    assert worklist["summary"]["total"] == 1  # only 1 pending in synthetic
    assert "oaa/av" in worklist["summary"]["by_directory"]
    assert len(worklist["pending_gold_entries"]) == 1
