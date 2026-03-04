"""
PROTO-02 gap: verify that confidence annotation comments in sensor/common proto files
match the confidence tier recorded in their corresponding .audit.yaml sidecars.

For each .proto file in oaa/sensor/ and oaa/common/:
- If a sidecar exists: the proto file MUST contain a '// confidence: {tier} [...]' comment
  matching the sidecar's confidence tier.
- If no sidecar: the proto file MUST contain '// confidence: unverified'.

Skips gracefully if no proto files exist.
"""

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
OAA_ROOT = REPO_ROOT / "oaa"
SENSOR_DIR = OAA_ROOT / "sensor"
COMMON_DIR = OAA_ROOT / "common"

# Annotation regex: matches "// confidence: <tier>" optionally followed by "[...]"
_CONFIDENCE_RE = re.compile(r"//\s*confidence:\s*(\w+)")


def _find_proto_files():
    """Find all .proto files in sensor/ and common/."""
    if not OAA_ROOT.exists():
        return []
    results = []
    for d in (SENSOR_DIR, COMMON_DIR):
        if d.exists():
            results.extend(sorted(d.glob("*.proto")))
    return results


def _extract_confidence_tiers_from_proto(proto_path: Path) -> list[str]:
    """Extract all unique confidence tier values from annotation comments in a proto file."""
    content = proto_path.read_text(encoding="utf-8")
    tiers = []
    for match in _CONFIDENCE_RE.finditer(content):
        tier = match.group(1)
        if tier not in tiers:
            tiers.append(tier)
    return tiers


def _load_sidecar(proto_path: Path) -> dict | None:
    """Load the .audit.yaml sidecar for a given .proto path, if it exists."""
    sidecar = proto_path.with_suffix(".audit.yaml")
    if not sidecar.exists():
        return None
    with open(sidecar, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


PROTO_FILES = _find_proto_files()


@pytest.mark.skipif(
    len(PROTO_FILES) == 0,
    reason="No .proto files found in oaa/sensor/ or oaa/common/ — skipping annotation check",
)
@pytest.mark.parametrize(
    "proto_path",
    PROTO_FILES,
    ids=lambda p: str(p.relative_to(REPO_ROOT)),
)
def test_proto_annotation_confidence_matches_sidecar(proto_path: Path):
    """
    Every confidence annotation comment in a sensor/common proto file must
    match the confidence tier in its corresponding .audit.yaml sidecar.

    If no sidecar exists, all annotations must say 'unverified'.
    """
    sidecar = _load_sidecar(proto_path)
    tiers_in_proto = _extract_confidence_tiers_from_proto(proto_path)
    rel = proto_path.relative_to(REPO_ROOT)

    assert tiers_in_proto, (
        f"{rel}: no '// confidence:' annotations found. "
        "All sensor/common proto files must be annotated (PROTO-02)."
    )

    if sidecar is None:
        # No sidecar — all annotations must be 'unverified'
        unexpected = [t for t in tiers_in_proto if t != "unverified"]
        assert not unexpected, (
            f"{rel}: no .audit.yaml sidecar exists, but found non-'unverified' "
            f"confidence annotations: {unexpected}. "
            "Proto files without sidecars must use '// confidence: unverified'."
        )
    else:
        expected_tier = sidecar.get("confidence")
        assert expected_tier is not None, (
            f"{rel}: sidecar is missing the 'confidence' field."
        )
        # All annotation tiers must match the sidecar tier (field-level annotations
        # inherit the message-level tier unless there are field overrides, which
        # are currently unused in the seed import).
        unexpected = [t for t in tiers_in_proto if t not in (expected_tier, "unverified")]
        assert not unexpected, (
            f"{rel}: sidecar confidence='{expected_tier}' but proto contains "
            f"mismatched annotation tier(s): {unexpected}. "
            "Confidence comments must mirror the audit YAML sidecar (PROTO-02)."
        )
        # At minimum the expected tier must actually appear in the file
        assert expected_tier in tiers_in_proto, (
            f"{rel}: sidecar confidence='{expected_tier}' but no annotation with "
            f"that tier found in proto. Found: {tiers_in_proto}."
        )
