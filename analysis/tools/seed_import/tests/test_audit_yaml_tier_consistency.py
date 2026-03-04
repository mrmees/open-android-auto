"""
VERI-01 gap: verify that the confidence tier in each .audit.yaml matches the
deterministic promotion logic defined in docs/verification/01-confidence-tiers.md.

Promotion logic (from the spec):
    if any evidence.type == "oem_capture":     tier = gold
    elif count(distinct evidence.type) >= 2:   tier = silver
    elif count(evidence) >= 1:                 tier = bronze
    else:                                      tier = unverified

Skips gracefully if no .audit.yaml files exist yet.
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
OAA_ROOT = REPO_ROOT / "oaa"


def _find_audit_files():
    if not OAA_ROOT.exists():
        return []
    return sorted(OAA_ROOT.rglob("*.audit.yaml"))


def _compute_expected_tier(evidence_list):
    """
    Deterministic promotion logic from 01-confidence-tiers.md.

    Returns one of: 'gold', 'silver', 'bronze', 'unverified'
    """
    if not evidence_list:
        return "unverified"

    types = {entry.get("type") for entry in evidence_list}

    if "oem_capture" in types:
        return "gold"
    elif len(types) >= 2:
        return "silver"
    else:
        return "bronze"


AUDIT_FILES = _find_audit_files()


# Unit tests for the promotion logic itself — these run regardless of whether
# real .audit.yaml files exist.

def test_promotion_logic_no_evidence_yields_unverified():
    assert _compute_expected_tier([]) == "unverified"


def test_promotion_logic_single_apk_static_yields_bronze():
    evidence = [{"type": "apk_static"}]
    assert _compute_expected_tier(evidence) == "bronze"


def test_promotion_logic_single_dhu_observation_yields_bronze():
    evidence = [{"type": "dhu_observation"}]
    assert _compute_expected_tier(evidence) == "bronze"


def test_promotion_logic_single_cross_version_yields_bronze():
    evidence = [{"type": "cross_version"}]
    assert _compute_expected_tier(evidence) == "bronze"


def test_promotion_logic_two_apk_static_same_type_still_yields_bronze():
    """Two entries of the same type do NOT count as 2 distinct types."""
    evidence = [{"type": "apk_static"}, {"type": "apk_static"}]
    assert _compute_expected_tier(evidence) == "bronze"


def test_promotion_logic_apk_static_plus_dhu_observation_yields_silver():
    evidence = [{"type": "apk_static"}, {"type": "dhu_observation"}]
    assert _compute_expected_tier(evidence) == "silver"


def test_promotion_logic_apk_static_plus_cross_version_yields_silver():
    evidence = [{"type": "apk_static"}, {"type": "cross_version"}]
    assert _compute_expected_tier(evidence) == "silver"


def test_promotion_logic_dhu_observation_plus_cross_version_yields_silver():
    evidence = [{"type": "dhu_observation"}, {"type": "cross_version"}]
    assert _compute_expected_tier(evidence) == "silver"


def test_promotion_logic_three_non_oem_types_still_yields_silver():
    """Three distinct non-OEM types top out at silver — Gold requires OEM capture."""
    evidence = [
        {"type": "apk_static"},
        {"type": "dhu_observation"},
        {"type": "cross_version"},
    ]
    assert _compute_expected_tier(evidence) == "silver"


def test_promotion_logic_oem_capture_alone_yields_gold():
    evidence = [{"type": "oem_capture"}]
    assert _compute_expected_tier(evidence) == "gold"


def test_promotion_logic_oem_capture_with_other_types_yields_gold():
    evidence = [{"type": "apk_static"}, {"type": "oem_capture"}]
    assert _compute_expected_tier(evidence) == "gold"


@pytest.mark.skipif(
    len(AUDIT_FILES) == 0,
    reason="No .audit.yaml files found under oaa/ — skipping file tier-consistency pass",
)
@pytest.mark.parametrize("audit_path", AUDIT_FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_each_audit_yaml_tier_matches_promotion_logic(audit_path):
    """
    The confidence field in every .audit.yaml must equal the tier computed by
    applying the canonical promotion logic to its evidence list.

    A mismatch means a contributor manually set a tier that contradicts the
    evidence — this violates the Confidence Consistency Rule in 02-audit-trail-format.md.
    """
    with open(audit_path) as fh:
        content = yaml.safe_load(fh)

    assert content is not None, f"{audit_path} is empty"
    assert isinstance(content, dict), f"{audit_path} must be a YAML mapping"

    stated_tier = content.get("confidence")
    assert stated_tier is not None, (
        f"{audit_path.relative_to(REPO_ROOT)}: missing 'confidence' field"
    )

    evidence_list = content.get("evidence") or []
    expected_tier = _compute_expected_tier(evidence_list)

    assert stated_tier == expected_tier, (
        f"{audit_path.relative_to(REPO_ROOT)}: "
        f"confidence field is '{stated_tier}' but promotion logic yields '{expected_tier}'. "
        f"Evidence types present: {sorted({e.get('type') for e in evidence_list})}. "
        f"Fix the 'confidence' field or add/remove evidence entries to match."
    )
