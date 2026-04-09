from __future__ import annotations

import json
from pathlib import Path


def test_live_divergence_snapshot(repo_root: Path) -> None:
    """The live divergence report exists and has non-empty summary.

    Empirical snapshot — regenerate with the command in the report's
    `baseline_reproduction.command` field if this fails.
    """
    report_path = repo_root / "analysis/reports/oem-vw/dhu-divergence.json"
    assert report_path.exists(), (
        f"Live divergence report missing at {report_path}. "
        f"Regenerate with: PYTHONPATH=. python3 -m analysis.tools.dhu_divergence.run "
        f"--vw-sdp-json analysis/reports/oem-vw/sdp-values.json "
        f"--dhu captures/general --dhu captures/idle-baseline "
        f"--dhu captures/music-playback --dhu captures/active-navigation "
        f"--delta-report analysis/reports/cross-version/16-4-delta-report.json "
        f"--out analysis/reports/oem-vw/ --repo-root ."
    )
    data = json.loads(report_path.read_text())
    assert "summary" in data
    assert "by_attribution" in data["summary"]
    # Non-empty — Phase 9 research preview guarantees >= 3 divergences.
    assert data["summary"]["total_divergences"] >= 1, (
        "Live report has 0 divergences — expected bluetooth_channel + wifi_channel VW-only "
        "and vendor_extension_channel DHU-only per 09-RESEARCH.md § Live divergence preview."
    )


def test_live_expected_vw_only(repo_root: Path) -> None:
    """Live report MUST contain bluetooth_channel and wifi_channel as VW-only services.

    Empirical snapshot — locked to the 2026-04-08 research preview. If Phase 7's
    SDP parser or the live VW SDP bytes change, this test will fail loudly and
    point at the regeneration command.
    """
    report_path = repo_root / "analysis/reports/oem-vw/dhu-divergence.json"
    data = json.loads(report_path.read_text())
    vw_only = set(data["services_in_vw_but_not_dhu"])
    expected = {"bluetooth_channel", "wifi_channel"}
    assert expected.issubset(vw_only), (
        f"Expected {expected} subset of services_in_vw_but_not_dhu, "
        f"got {vw_only}. Baseline: analysis/reports/oem-vw/sdp-values.json + 4 DHU SDP files. "
        f"Run date: see report metadata. Regeneration command: in the report's "
        f"baseline_reproduction.command field."
    )


def test_live_expected_dhu_only(repo_root: Path) -> None:
    """Live report MUST contain vendor_extension_channel as a DHU-only service.

    Empirical snapshot — locked to the 2026-04-08 research preview.
    """
    report_path = repo_root / "analysis/reports/oem-vw/dhu-divergence.json"
    data = json.loads(report_path.read_text())
    dhu_only = set(data["services_in_dhu_but_not_vw"])
    assert "vendor_extension_channel" in dhu_only, (
        f"Expected 'vendor_extension_channel' in services_in_dhu_but_not_vw, "
        f"got {dhu_only}. Baseline: 4 DHU SDP files in captures/. "
        f"Run date: see report metadata. Regeneration command: in the report's "
        f"baseline_reproduction.command field."
    )
