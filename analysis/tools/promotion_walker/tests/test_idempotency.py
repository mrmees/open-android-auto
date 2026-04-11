from __future__ import annotations
import hashlib
from pathlib import Path

import yaml

from analysis.tools.promotion_walker.verdict import walker_decide
from analysis.tools.promotion_walker.run import _apply_verdict


def _sha256_tree(root: Path) -> dict[str, str]:
    """Map of relative_path -> sha256 for every file under root."""
    out: dict[str, str] = {}
    for fx in sorted(root.rglob("*.audit.yaml")):
        rel = str(fx.relative_to(root))
        out[rel] = hashlib.sha256(fx.read_bytes()).hexdigest()
    return out


def test_walker_byte_idempotent(temp_oaa_tree: Path, schema: dict, mock_sdp: dict, tmp_path: Path) -> None:
    """Running _apply_verdict twice on the same sidecar produces byte-identical files."""
    sdp_kinds = {c["channel_kind"] for c in mock_sdp["response"]["channels"]}

    # First pass: apply verdicts
    for fx in sorted(temp_oaa_tree.rglob("*.audit.yaml")):
        sc = yaml.safe_load(fx.read_text())
        verdict = walker_decide(sc, fx, {}, sdp_kinds, {}, schema)
        _apply_verdict(verdict, fx, "captures/fixture-capture", "2026-04-09", dry_run=False)

    sha_after_first = _sha256_tree(temp_oaa_tree)

    # Second pass: same inputs (simulate re-run)
    for fx in sorted(temp_oaa_tree.rglob("*.audit.yaml")):
        sc = yaml.safe_load(fx.read_text())
        verdict = walker_decide(sc, fx, {}, sdp_kinds, {}, schema)
        _apply_verdict(verdict, fx, "captures/fixture-capture", "2026-04-09", dry_run=False)

    sha_after_second = _sha256_tree(temp_oaa_tree)
    assert sha_after_first == sha_after_second, \
        f"walker re-run produced drift: {set(sha_after_first.items()) ^ set(sha_after_second.items())}"
