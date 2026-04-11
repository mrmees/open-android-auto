from __future__ import annotations
import json
from pathlib import Path


REGEN_CMD = "PYTHONPATH=. python3 -m analysis.tools.promotion_walker.run"


def _load_report(repo_root: Path) -> dict:
    p = repo_root / "analysis/reports/oem-vw/promotion-walk.json"
    assert p.exists(), f"{p} not found -- run walker first: {REGEN_CMD}"
    return json.loads(p.read_text())


def test_main_report_emitted(repo_root: Path) -> None:
    assert (repo_root / "analysis/reports/oem-vw/promotion-walk.md").exists(), \
        f"main report missing. Regenerate with: {REGEN_CMD}"
    assert (repo_root / "analysis/reports/oem-vw/promotion-walk.json").exists(), \
        f"main report JSON missing. Regenerate with: {REGEN_CMD}"


def test_worklist_emitted(repo_root: Path) -> None:
    assert (repo_root / "analysis/reports/oem-vw/oem-match-pending-gold-worklist.md").exists(), \
        f"worklist markdown missing. Regenerate with: {REGEN_CMD}"
    assert (repo_root / "analysis/reports/oem-vw/oem-match-pending-gold-worklist.json").exists(), \
        f"worklist JSON missing. Regenerate with: {REGEN_CMD}"


def test_live_promotion_count(repo_root: Path) -> None:
    report = _load_report(repo_root)
    n = len(report["platinum_promotions"])
    assert n == 2, (
        f"expected 2 Platinum promotions (MediaPlaybackStatusMessage + MediaPlaybackMetadataMessage), "
        f"got {n}. Regenerate: {REGEN_CMD}"
    )


def test_live_pending_count(repo_root: Path) -> None:
    report = _load_report(repo_root)
    n = len(report["pending_gold_flags"])
    assert n == 21, (
        f"expected 21 oem_match_pending_gold flags (11 av + 5 audio_silver + 2 audio_bronze + 3 video), "
        f"got {n}. Regenerate: {REGEN_CMD}"
    )


def test_live_already_platinum_skip(repo_root: Path) -> None:
    report = _load_report(repo_root)
    skipped = report["skipped_sidecars"]
    already = [s for s in skipped if s["verdict_kind"] == "skip_already_platinum"]
    assert len(already) == 1, (
        f"expected exactly 1 skip_already_platinum (VideoFocusRequestMessage), "
        f"got {len(already)}. Regenerate: {REGEN_CMD}"
    )
    assert "VideoFocusRequestMessage" in already[0]["sidecar_path"]


def test_live_out_of_sdp_count(repo_root: Path) -> None:
    report = _load_report(repo_root)
    skipped = report["skipped_sidecars"]
    oos = [s for s in skipped if s["verdict_kind"] == "skip_out_of_sdp_scope"]
    # 3 CarLocalMediaPlayback* sidecars
    assert len(oos) == 3, (
        f"expected 3 skip_out_of_sdp_scope (CarLocalMediaPlayback*), got {len(oos)}. "
        f"Regenerate: {REGEN_CMD}"
    )
    for entry in oos:
        assert "CarLocalMediaPlayback" in entry["sidecar_path"] or \
               "car_local_media" in (entry.get("skip_reason") or "")
