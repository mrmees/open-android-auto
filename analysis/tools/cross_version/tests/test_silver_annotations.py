"""Phase 3 test: silver-tier sidecars have matching silver annotations in proto files.

Gap 3 (TOOL-02): Phase 2 tests check annotation-sidecar consistency but were written
when everything was bronze. This test specifically verifies that silver-tier sidecars
have matching `// confidence: silver` annotations in their corresponding proto files.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from analysis.tools.seed_import.annotate import (
    format_confidence,
    render_annotated_content,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
OAA_ROOT = REPO_ROOT / "oaa"

_DOCUMENTATION_ONLY_SILVER_PROTOS = {
    "oaa/audio/AudioFocusStateMessage.proto",
    "oaa/audio/AudioStreamTypeMessage.proto",
    "oaa/control/GalPingRequestMessage.proto",
    "oaa/control/GalPingResponseMessage.proto",
    "oaa/input/InputChannelData.proto",
    "oaa/input/KeyEventData.proto",
    "oaa/input/TouchConfigData.proto",
    "oaa/input/TouchCoordinateData.proto",
    "oaa/navigation/NavigationFocusIndicationMessage.proto",
}


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
def test_silver_proto_annotation_matches_canonical_confidence_comment(
    sidecar_path: Path, proto_path: Path
):
    """Silver proto annotations must include the comment derived from their sidecar."""
    if not proto_path.exists():
        pytest.skip(f"Proto file {proto_path} does not exist")

    sidecar_data = yaml.safe_load(sidecar_path.read_text(encoding="utf-8"))
    expected_comment = format_confidence(
        sidecar_data["confidence"],
        sidecar_data.get("evidence", []),
    )
    content = proto_path.read_text(encoding="utf-8")
    _, stats = render_annotated_content(content, sidecar_data)
    if not any(stats.values()):
        try:
            relative_proto = proto_path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            relative_proto = proto_path.as_posix()
        assert relative_proto in _DOCUMENTATION_ONLY_SILVER_PROTOS, (
            f"unexpected zero-target silver proto: {relative_proto}"
        )
        return

    assert expected_comment in content, (
        f"{proto_path.name}: silver annotation does not match its sidecar.\n"
        f"  Expected comment: {expected_comment!r}\n"
        f"  Sidecar: {sidecar_path}"
    )


def test_zero_target_silver_protos_match_documentation_only_cohort():
    """Only the named documentation/retraction cohort may have no render targets."""
    discovered = set()
    for sidecar_path, proto_path in _SILVER_PAIRS:
        sidecar_data = yaml.safe_load(sidecar_path.read_text(encoding="utf-8"))
        content = proto_path.read_text(encoding="utf-8")
        _, stats = render_annotated_content(content, sidecar_data)
        if not any(stats.values()):
            discovered.add(proto_path.relative_to(REPO_ROOT).as_posix())

    assert discovered == _DOCUMENTATION_ONLY_SILVER_PROTOS


def test_unexpected_zero_target_silver_proto_is_rejected(tmp_path: Path):
    """A new empty silver proto must not inherit the documentation-only exemption."""
    proto_path = tmp_path / "UnexpectedEmpty.proto"
    proto_path.write_text(
        'syntax = "proto2";\npackage unexpected;\n',
        encoding="utf-8",
    )
    sidecar_path = tmp_path / "UnexpectedEmpty.audit.yaml"
    sidecar_path.write_text(
        "proto: oaa/unexpected/UnexpectedEmpty.proto\n"
        "confidence: silver\n"
        "evidence:\n"
        "- type: apk_static\n",
        encoding="utf-8",
    )

    with pytest.raises(AssertionError, match="unexpected zero-target silver proto"):
        test_silver_proto_annotation_matches_canonical_confidence_comment(
            sidecar_path,
            proto_path,
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
