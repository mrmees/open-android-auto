from __future__ import annotations

import json
from pathlib import Path

from analysis.tools.dhu_divergence.attribution import classify_divergence
from analysis.tools.dhu_divergence.divergence import Divergence


def _load_mini_delta(repo_root: Path) -> dict:
    return json.loads(
        (
            repo_root
            / "analysis/tools/dhu_divergence/tests/fixtures/delta_report_mini.json"
        ).read_text()
    )


def test_vw_only_defaults_oem(repo_root: Path) -> None:
    """A service_only_in_vw not listed in new_in_16_4 defaults to attribution: oem."""
    delta = _load_mini_delta(repo_root)
    div = Divergence(
        kind="service_only_in_vw",
        service="bluetooth_channel",
        vw_config={},
        dhu_configs=[],
        baselines_matched=[],
    )
    result = classify_divergence(div, delta)
    assert result.attribution == "oem"
    assert "new_in_16_4" in result.attribution_reason


def test_vw_only_version_attribution(repo_root: Path) -> None:
    """A service_only_in_vw whose proto IS in new_in_16_4 returns attribution: version."""
    delta = _load_mini_delta(repo_root)
    # Fixture's new_in_16_4 contains VersionAttributedFixtureMessage — use a service
    # string that substring-matches it.
    div = Divergence(
        kind="service_only_in_vw",
        service="versionattributedfixture",
        vw_config={},
        dhu_configs=[],
        baselines_matched=[],
    )
    result = classify_divergence(div, delta)
    assert result.attribution == "version"


def test_dhu_only_defaults_ambiguous(repo_root: Path) -> None:
    """A service_only_in_dhu not listed in removed_in_16_4 defaults to attribution: ambiguous."""
    delta = _load_mini_delta(repo_root)
    div = Divergence(
        kind="service_only_in_dhu",
        service="vendor_extension_channel",
        vw_config=None,
        dhu_configs=[{}],
        baselines_matched=["general"],
    )
    result = classify_divergence(div, delta)
    assert result.attribution == "ambiguous"
