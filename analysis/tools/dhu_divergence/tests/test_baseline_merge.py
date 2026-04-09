from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from analysis.tools.dhu_divergence.baseline_merge import (
    load_dhu_baseline,
    merge_baselines,
)


def test_union_merge(descriptor_bundle, repo_root: Path) -> None:
    """Merging two real DHU baselines produces a union of their channel kinds."""
    fixtures = repo_root / "analysis/tools/dhu_divergence/tests/fixtures"
    # `load_dhu_baseline` expects a directory — create a tmp structure where the
    # fixture .bin is placed as `sdp_response.bin` under a directory.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        dir_a = tmp_path / "baseline_a"
        dir_b = tmp_path / "baseline_b"
        dir_a.mkdir()
        dir_b.mkdir()
        shutil.copy(fixtures / "dhu_sdp_a.bin", dir_a / "sdp_response.bin")
        shutil.copy(fixtures / "dhu_sdp_b.bin", dir_b / "sdp_response.bin")

        bl_a = load_dhu_baseline(descriptor_bundle, "baseline_a", dir_a)
        bl_b = load_dhu_baseline(descriptor_bundle, "baseline_b", dir_b)

        assert len(bl_a.channels) > 0, "Baseline A has no channels — load failed"
        assert len(bl_b.channels) > 0, "Baseline B has no channels — load failed"

        merged = merge_baselines([bl_a, bl_b])

        # Every kind in either baseline must be in the merge.
        kinds_a = {c["channel_kind"] for c in bl_a.channels}
        kinds_b = {c["channel_kind"] for c in bl_b.channels}
        expected_kinds = kinds_a | kinds_b
        assert set(merged.kinds_to_baselines.keys()) == expected_kinds

        # Every kind has a non-empty baselines_matched list, and the list is sorted.
        for kind, baseline_names in merged.kinds_to_baselines.items():
            assert len(baseline_names) >= 1
            assert baseline_names == sorted(baseline_names)

        # Every kind has a representative channel.
        for kind in expected_kinds:
            assert kind in merged.representative_channels
