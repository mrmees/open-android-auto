from __future__ import annotations

import json
import tempfile
from pathlib import Path

from analysis.tools.dhu_divergence.attribution import AttributedDivergence
from analysis.tools.dhu_divergence.baseline_merge import DhuBaseline, merge_baselines
from analysis.tools.dhu_divergence.divergence import Divergence
from analysis.tools.dhu_divergence.report import (
    SECTION_HEADERS,
    build_json,
    emit_markdown,
)


def _build_fake_data(repo_root: Path) -> dict:
    """Build a full data dict using fixture inputs, for report structure tests."""
    # Create a fake merged DHU with 1 baseline pointing at the real fixture.
    dhu_bin = repo_root / "analysis/tools/dhu_divergence/tests/fixtures/dhu_sdp_a.bin"
    bl = DhuBaseline(
        name="fake_baseline",
        path=dhu_bin,
        channels=[
            {"channel_id": 0, "channel_kind": "av_channel", "config": {}},
        ],
    )
    merged = merge_baselines([bl])

    vw_sdp = json.loads(
        (
            repo_root
            / "analysis/tools/dhu_divergence/tests/fixtures/vw_sdp_mini.json"
        ).read_text()
    )

    attributed = [
        AttributedDivergence(
            divergence=Divergence(
                kind="service_only_in_vw",
                service="bluetooth_channel",
                vw_config={},
                dhu_configs=[],
                baselines_matched=[],
            ),
            attribution="oem",
            attribution_reason="Test OEM reason",
            phase_8_delta_report_lookup={
                "new_in_16_4": None,
                "removed_in_16_4": None,
                "schema_changes": None,
            },
        ),
        AttributedDivergence(
            divergence=Divergence(
                kind="service_only_in_dhu",
                service="vendor_extension_channel",
                vw_config=None,
                dhu_configs=[{}],
                baselines_matched=["fake_baseline"],
            ),
            attribution="ambiguous",
            attribution_reason="Test ambiguous reason",
            phase_8_delta_report_lookup={
                "new_in_16_4": None,
                "removed_in_16_4": None,
                "schema_changes": None,
            },
        ),
    ]

    # delta_report_path — use the fixture mini report.
    delta_path = (
        repo_root
        / "analysis/tools/dhu_divergence/tests/fixtures/delta_report_mini.json"
    )

    return build_json(
        attributed=attributed,
        merged_dhu=merged,
        vw_sdp_values=vw_sdp,
        vw_capture_path="captures/oem-vw-mib3oi-2026-04-06/",
        delta_report_path=delta_path,
    )


def test_eight_sections(repo_root: Path) -> None:
    """Markdown report has all 8 locked section headers in order."""
    data = _build_fake_data(repo_root)
    with tempfile.TemporaryDirectory() as tmp:
        out_md = Path(tmp) / "report.md"
        emit_markdown(data, out_md)
        text = out_md.read_text()
        # All 8 headers appear.
        for header in SECTION_HEADERS:
            assert header in text, f"Missing section header: {header}"
        # In ORDER — find each and assert positions are monotonically increasing.
        positions = [text.index(h) for h in SECTION_HEADERS]
        assert positions == sorted(positions), (
            f"Section headers not in locked order — positions: {positions}"
        )


def test_json_structure(repo_root: Path) -> None:
    """JSON sidecar has the 9 locked top-level keys."""
    data = _build_fake_data(repo_root)
    required_keys = {
        "metadata",
        "summary",
        "version_attributed_divergences",
        "oem_attributed_divergences",
        "ambiguous_divergences",
        "services_in_vw_but_not_dhu",
        "services_in_dhu_but_not_vw",
        "per_baseline_observation_summary",
        "baseline_reproduction",
    }
    assert set(data.keys()) == required_keys
    # Summary has by_attribution with all 3 keys.
    assert set(data["summary"]["by_attribution"].keys()) == {
        "version",
        "oem",
        "ambiguous",
    }


def test_metadata_hashes(repo_root: Path) -> None:
    """Metadata block contains sha256 hashes for every DHU baseline and the delta report."""
    data = _build_fake_data(repo_root)
    meta = data["metadata"]
    assert "phase_8_delta_report_sha256" in meta
    assert len(meta["phase_8_delta_report_sha256"]) == 64  # sha256 hex
    assert meta["dhu_baselines"], "dhu_baselines list is empty"
    for b in meta["dhu_baselines"]:
        assert "sha256" in b
        assert len(b["sha256"]) == 64
