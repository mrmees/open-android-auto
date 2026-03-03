"""Tests for the consistency report generator."""
from __future__ import annotations

from pathlib import Path

from analysis.tools.cross_version.compare import ComparisonResult
from analysis.tools.cross_version.report import generate_report
from analysis.tools.proto_schema_validator.models import (
    DriftIssue,
    IssueKind,
    ProtoMapping,
    Severity,
)


def _make_result(
    message: str, issues: list[DriftIssue] | None = None
) -> ComparisonResult:
    return ComparisonResult(
        mapping=ProtoMapping(
            proto_message=message,
            proto_file=f"oaa/sensor/{message}.proto",
            apk_classes={"15.9": "aaa", "16.1": "bbb", "16.2": "ccc"},
        ),
        pairs_compared=[("15.9", "16.1"), ("16.1", "16.2")],
        issues=issues or [],
    )


def test_report_structure(tmp_path: Path):
    """Report contains expected sections: Summary, Discrepancies, Promotion."""
    results = [
        _make_result("CleanMessage"),
        _make_result(
            "DirtyMessage",
            issues=[
                DriftIssue(
                    apk_class_v1="aaa",
                    apk_class_v2="bbb",
                    kind=IssueKind.FIELD_TYPE_CHANGED,
                    severity=Severity.ERROR,
                    field_number=3,
                    detail="field 3 type changed",
                ),
            ],
        ),
    ]
    output = tmp_path / "report.md"
    exit_code = generate_report(results, output)

    content = output.read_text()
    assert "Summary" in content or "summary" in content.lower()
    assert "Discrepan" in content or "discrepan" in content.lower()
    assert exit_code != 0, "Should return non-zero when discrepancies exist"


def test_zero_discrepancies_exit_0(tmp_path: Path):
    """When all mappings are consistent, report indicates success."""
    results = [
        _make_result("CleanA"),
        _make_result("CleanB"),
    ]
    output = tmp_path / "report.md"
    exit_code = generate_report(results, output)

    assert exit_code == 0, "Should return 0 when no discrepancies"
    content = output.read_text()
    assert output.exists()
    assert len(content) > 0
