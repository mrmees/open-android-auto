from __future__ import annotations

import json
from pathlib import Path

from analysis.tools.dhu_divergence.baseline_merge import (
    DhuBaseline,
    merge_baselines,
)
from analysis.tools.dhu_divergence.divergence import (
    compute_divergences,
    load_vw_channels,
    services_only_in_dhu,
    services_only_in_vw,
)


def _build_vw_from_fixture(repo_root: Path) -> list[dict]:
    fixtures = repo_root / "analysis/tools/dhu_divergence/tests/fixtures"
    vw_data = json.loads((fixtures / "vw_sdp_mini.json").read_text())
    return load_vw_channels(vw_data)


def _build_fake_dhu_merge() -> object:
    """Build a fake MergedDhu carrying only an av_channel and a
    vendor_extension_channel, so the divergence calc has a known DHU side
    regardless of real-fixture SDP decoding."""
    bl = DhuBaseline(
        name="fake",
        path=Path("/dev/null"),
        channels=[
            {"channel_id": 0, "channel_kind": "av_channel", "config": {}},
            {
                "channel_id": 1,
                "channel_kind": "vendor_extension_channel",
                "config": {"flag": "dhu"},
            },
        ],
    )
    return merge_baselines([bl])


def test_vw_only_services(repo_root: Path) -> None:
    """Services present in VW but not in merged DHU get flagged as service_only_in_vw."""
    vw_channels = _build_vw_from_fixture(repo_root)
    merged = _build_fake_dhu_merge()
    divergences = compute_divergences(vw_channels, merged)

    vw_only = services_only_in_vw(divergences)
    # VW fixture has bluetooth_channel, wifi_channel, sensor_channel, input_channel
    # Fake DHU has av_channel, vendor_extension_channel
    # So VW-only should include [bluetooth_channel, input_channel, sensor_channel, wifi_channel]
    assert "bluetooth_channel" in vw_only
    assert "wifi_channel" in vw_only
    # Sorted alphabetically.
    assert vw_only == sorted(vw_only)
    # av_channel is in BOTH — must NOT appear as vw_only.
    assert "av_channel" not in vw_only


def test_dhu_only_services(repo_root: Path) -> None:
    """Services present in merged DHU but not in VW get flagged as service_only_in_dhu."""
    vw_channels = _build_vw_from_fixture(repo_root)
    merged = _build_fake_dhu_merge()
    divergences = compute_divergences(vw_channels, merged)

    dhu_only = services_only_in_dhu(divergences)
    assert "vendor_extension_channel" in dhu_only
    # baselines_matched is populated for DHU-only entries.
    ve_divs = [d for d in divergences if d.service == "vendor_extension_channel"]
    assert len(ve_divs) == 1
    assert ve_divs[0].baselines_matched == ["fake"]
