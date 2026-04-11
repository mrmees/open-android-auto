from __future__ import annotations
import hashlib
from pathlib import Path

import yaml

from analysis.tools.promotion_walker.verdict import walker_decide
from analysis.tools.promotion_walker.run import _apply_verdict


def test_dry_run_no_writes(temp_oaa_tree: Path, schema: dict, mock_sdp: dict) -> None:
    """dry_run=True must not modify any fixture file on disk."""
    sdp_kinds = {c["channel_kind"] for c in mock_sdp["response"]["channels"]}

    before = {str(fx.relative_to(temp_oaa_tree)): hashlib.sha256(fx.read_bytes()).hexdigest()
              for fx in sorted(temp_oaa_tree.rglob("*.audit.yaml"))}

    for fx in sorted(temp_oaa_tree.rglob("*.audit.yaml")):
        sc = yaml.safe_load(fx.read_text())
        verdict = walker_decide(sc, fx, {}, sdp_kinds, {}, schema)
        _apply_verdict(verdict, fx, "captures/fixture-capture", "2026-04-09", dry_run=True)

    after = {str(fx.relative_to(temp_oaa_tree)): hashlib.sha256(fx.read_bytes()).hexdigest()
             for fx in sorted(temp_oaa_tree.rglob("*.audit.yaml"))}

    assert before == after, "dry_run mode modified sidecars -- this is a bug"
