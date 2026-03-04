"""Phase 3 test: silver-tier sidecars have matching silver annotations in proto files.

Gap 3 (TOOL-02): Phase 2 tests check annotation-sidecar consistency but were written
when everything was bronze. This test specifically verifies that silver-tier sidecars
have matching `// confidence: silver` annotations in their corresponding proto files.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
OAA_ROOT = REPO_ROOT / "oaa"


def _silver_sidecars() -> list[tuple[Path, Path]]:
    """Return (sidecar_path, proto_path) pairs for all silver-tier sidecars."""
    pairs = []
    for sidecar in sorted(OAA_ROOT.rglob("*.audit.yaml")):
        data = yaml.safe_load(sidecar.read_text())
        if data and data.get("confidence") == "silver":
            proto_rel = data.get("proto", "")
            proto_path = REPO_ROOT / proto_rel
            pairs.append((sidecar, proto_path))
    return pairs


_SILVER_PAIRS = _silver_sidecars()


def test_silver_proto_pairs_exist():
    """At least one silver sidecar+proto pair must exist after Phase 3."""
    assert len(_SILVER_PAIRS) > 0, (
        "No silver-tier sidecar/proto pairs found. Phase 3 must have run."
    )


@pytest.mark.parametrize(
    "sidecar_path,proto_path",
    _SILVER_PAIRS,
    ids=lambda p: p.relative_to(OAA_ROOT).as_posix() if isinstance(p, Path) and OAA_ROOT in p.parents else p.name,
)
def test_silver_sidecar_has_matching_proto_file(sidecar_path: Path, proto_path: Path):
    """Each silver sidecar must reference a proto file that actually exists."""
    assert proto_path.exists(), (
        f"Silver sidecar {sidecar_path.name} references proto file "
        f"{proto_path} which does not exist"
    )


@pytest.mark.parametrize(
    "sidecar_path,proto_path",
    _SILVER_PAIRS,
    ids=lambda p: p.relative_to(OAA_ROOT).as_posix() if isinstance(p, Path) and OAA_ROOT in p.parents else p.name,
)
def test_silver_sidecar_has_silver_annotation_in_proto(sidecar_path: Path, proto_path: Path):
    """Proto files for silver-tier sidecars must have `// confidence: silver` annotation."""
    if not proto_path.exists():
        pytest.skip(f"Proto file {proto_path} does not exist -- covered by prior test")

    content = proto_path.read_text(encoding="utf-8")
    assert "confidence: silver" in content, (
        f"{proto_path.name}: silver-tier sidecar exists but proto lacks "
        f"'// confidence: silver' annotation.\n"
        f"  Sidecar: {sidecar_path}\n"
        f"  Proto: {proto_path}"
    )


@pytest.mark.parametrize(
    "sidecar_path,proto_path",
    _SILVER_PAIRS,
    ids=lambda p: p.relative_to(OAA_ROOT).as_posix() if isinstance(p, Path) and OAA_ROOT in p.parents else p.name,
)
def test_silver_proto_annotation_includes_cross_version_evidence_tag(
    sidecar_path: Path, proto_path: Path
):
    """Silver proto annotations must include [apk_static, cross_version] evidence tags."""
    if not proto_path.exists():
        pytest.skip(f"Proto file {proto_path} does not exist")

    content = proto_path.read_text(encoding="utf-8")
    # The annotation pattern is: // confidence: silver [apk_static, cross_version]
    assert "cross_version" in content, (
        f"{proto_path.name}: silver annotation is missing 'cross_version' evidence tag.\n"
        f"  Expected pattern: '// confidence: silver [apk_static, cross_version]'\n"
        f"  Sidecar: {sidecar_path}"
    )


def test_no_bronze_sidecar_has_silver_proto_annotation():
    """Proto files for bronze-tier sidecars must NOT have a silver annotation (no upgrade leak)."""
    violations = []
    for sidecar in sorted(OAA_ROOT.rglob("*.audit.yaml")):
        data = yaml.safe_load(sidecar.read_text())
        if not data or data.get("confidence") != "bronze":
            continue
        proto_rel = data.get("proto", "")
        proto_path = REPO_ROOT / proto_rel
        if not proto_path.exists():
            continue
        content = proto_path.read_text(encoding="utf-8")
        if "confidence: silver" in content:
            violations.append(f"{sidecar.name} (bronze) -> {proto_path.name} has silver annotation")

    assert not violations, (
        f"Bronze sidecars with silver proto annotations (tier mismatch):\n"
        + "\n".join(violations)
    )
