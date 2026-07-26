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
    assert n == 0, f"MATCH-08-only service bindings cannot promote messages; got {n}"


def test_live_pending_count(repo_root: Path) -> None:
    report = _load_report(repo_root)
    n = len(report["pending_gold_flags"])
    assert n == 0, f"MATCH-08-only service bindings cannot create pending flags; got {n}"


def test_live_has_no_match08_only_platinum_skip(repo_root: Path) -> None:
    report = _load_report(repo_root)
    skipped = report["skipped_sidecars"]
    already = [s for s in skipped if s["verdict_kind"] == "skip_already_platinum"]
    assert already == [], "service-binding-only Platinum sidecars must be reconciled"


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
