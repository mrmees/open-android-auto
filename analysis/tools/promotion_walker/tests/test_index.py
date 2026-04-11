from __future__ import annotations
from pathlib import Path

from analysis.tools.promotion_walker.index import build_index, build_sdp_kinds


def test_build_index_from_mock_coverage(mock_messages_jsonl: Path, repo_root: Path) -> None:
    """build_index should find the attributed av_channel entry in mock_coverage.json."""
    fixtures_dir = repo_root / "analysis/tools/promotion_walker/tests/fixtures"
    cov_path = fixtures_dir / "mock_coverage.json"
    idx = build_index(cov_path, mock_messages_jsonl)

    # Expect at least one key: (av_channel, 32771, out)
    assert ("av_channel", 32771, "out") in idx, \
        f"expected av_channel/32771/out in index, got keys: {list(idx.keys())}"
    assert len(idx[("av_channel", 32771, "out")]) >= 1
    # Each entry is (seq, ts_ms) tuple
    seq, ts = idx[("av_channel", 32771, "out")][0]
    assert isinstance(seq, int) and isinstance(ts, int)


def test_build_sdp_kinds_from_mock_sdp(repo_root: Path) -> None:
    """build_sdp_kinds extracts the set of channel_kind strings from mock SDP."""
    sdp_path = repo_root / "analysis/tools/promotion_walker/tests/fixtures/mock_sdp_values.json"
    kinds = build_sdp_kinds(sdp_path)

    assert kinds == {"av_channel", "media_info_channel"}, \
        f"expected exactly av_channel + media_info_channel, got {kinds}"
