"""Whole-repository tests for the canonical audit confidence policy."""

from pathlib import Path

import pytest
import yaml

from analysis.tools.seed_import.tier_policy import (
    expected_tier,
    pending_gold_violations,
    version_class_pairs,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
OAA_ROOT = REPO_ROOT / "oaa"
CLASS_MAPPING_PATH = (
    REPO_ROOT / "analysis" / "tools" / "proto_schema_validator" / "class_mapping.yaml"
)


def _find_audit_files() -> list[Path]:
    return sorted(OAA_ROOT.rglob("*.audit.yaml")) if OAA_ROOT.exists() else []


def _canonical_mapping_index(mappings: list[dict]) -> dict[str, dict[str, str | None]]:
    """Merge canonical mappings deterministically and reject contradictions."""
    index: dict[str, dict[str, str | None]] = {}
    ordered = sorted(
        mappings,
        key=lambda entry: (
            str(entry.get("proto_message", "")),
            str(entry.get("proto_file", "")),
            str(entry.get("proto_fqn", "")),
            tuple(
                sorted(
                    (str(version), "" if apk_class is None else str(apk_class).lower())
                    for version, apk_class in (entry.get("apk_classes") or {}).items()
                )
            ),
        ),
    )
    for entry in ordered:
        message = entry.get("proto_message")
        if not isinstance(message, str) or not message:
            raise AssertionError("canonical mapping entry requires proto_message")
        versions = index.setdefault(message, {})
        for version, apk_class in sorted((entry.get("apk_classes") or {}).items()):
            normalized = apk_class.lower() if isinstance(apk_class, str) else apk_class
            if version in versions and versions[version] != normalized:
                raise AssertionError(
                    f"contradictory canonical mapping for {message} {version}: "
                    f"{versions[version]!r} vs {normalized!r}"
                )
            versions[version] = normalized
    return index


def _canonical_pair_violations(
    audit: dict, canonical: dict[str, dict[str, str | None]]
) -> list[str]:
    message = audit.get("message")
    expected_by_version = canonical.get(message, {})
    violations: list[str] = []
    for entry in audit.get("evidence") or []:
        if entry.get("type") != "cross_version":
            continue
        for version, apk_class in sorted(version_class_pairs(entry)):
            if version not in expected_by_version:
                continue
            expected = expected_by_version[version]
            if expected is not None and apk_class != expected:
                violations.append(
                    f"{message} {version}: parsed {apk_class!r}, canonical {expected!r}"
                )
    return violations


def _platinum(tmp_path: Path, rules: list[str] | None = None) -> dict:
    capture = tmp_path / "captures" / "sample" / "messages.jsonl"
    capture.parent.mkdir(parents=True, exist_ok=True)
    capture.write_text("{}\n")
    return {
        "type": "platinum_evidence",
        "capture_path": "captures/sample/messages.jsonl",
        "vehicle_metadata": {
            "make": "Example", "model": "HU", "year": "2026", "aa_version": "16.4"
        },
        "msg_seq": [1], "ts_ms": [10], "message_completeness": "full",
        "attribution_method": "msg_type_fingerprint", "oem_scope": "single",
        "applicability": "message", "match_rules": rules or ["MATCH-02"],
    }


def _gold_evidence() -> list[dict]:
    return [
        {"type": "deep_trace", "source": "APK 16.2 ied.java:73 handler"},
        {"type": "cross_version", "source": "v15.9:vvj / v16.2:wcr"},
    ]


def test_no_evidence_yields_unverified():
    assert expected_tier({"evidence": []}) == "unverified"


def test_one_evidence_type_yields_bronze():
    assert expected_tier({"evidence": [{"type": "apk_static"}]}) == "bronze"


def test_same_type_duplication_does_not_reach_silver():
    audit = {"evidence": [{"type": "apk_static"}, {"type": "apk_static"}]}
    assert expected_tier(audit) == "bronze"


def test_two_distinct_types_yield_silver():
    audit = {"evidence": [{"type": "apk_static"}, {"type": "cross_version"}]}
    assert expected_tier(audit) == "silver"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("v15.9:vra", {("15.9", "vra")}),
        ("15.9 = abc$1", {("15.9", "abc$1")}),
        ("APK 16.2 (wcr)", {("16.2", "wcr")}),
        ("APK v16.2 (class wcr$2)", {("16.2", "wcr$2")}),
        ("Android Auto 17.3 (jadx: Xnd2)", {("17.3", "xnd2")}),
        ("Android Auto 17.3 class xnd$Inner1", {("17.3", "xnd$inner1")}),
        ("v1.0:a", {("1.0", "a")}),
        (f"v1.0:{'a' * 32}", {("1.0", "a" * 32)}),
    ],
)
def test_version_class_pairs_accept_only_explicit_supported_syntax(source, expected):
    assert version_class_pairs({"source": source}) == expected


@pytest.mark.parametrize(
    "source",
    [
        "Android Auto 17.3 endpoint trace; 16.4 confirms the direction",
        "17.3 canonical descriptor compared with 16.2 baseline",
        "cross-version checker (15.9, 16.1, 16.2, 16.4)",
        f"v1.0:{'a' * 33}",
    ],
)
def test_version_class_pairs_reject_prose_and_out_of_bounds_tokens(source):
    assert version_class_pairs({"source": source}) == set()


def test_canonical_mapping_index_merges_duplicate_messages_deterministically():
    first = {
        "proto_message": "Message",
        "proto_file": "z.proto",
        "apk_classes": {"16.2": "Abc"},
    }
    second = {
        "proto_message": "Message",
        "proto_file": "a.proto",
        "apk_classes": {"16.1": "Def"},
    }
    expected = {"Message": {"16.1": "def", "16.2": "abc"}}
    assert _canonical_mapping_index([first, second]) == expected
    assert _canonical_mapping_index([second, first]) == expected


@pytest.mark.parametrize(
    "mappings",
    [
        [
            {"proto_message": "Message", "apk_classes": {"16.1": "abc"}},
            {"proto_message": "Message", "apk_classes": {"16.1": "def"}},
        ],
        [
            {"proto_message": "Message", "apk_classes": {"16.1": "def"}},
            {"proto_message": "Message", "apk_classes": {"16.1": "abc"}},
        ],
    ],
)
def test_canonical_mapping_index_rejects_contradictory_duplicate_messages(
    mappings,
):
    with pytest.raises(
        AssertionError,
        match="contradictory canonical mapping for Message 16.1: 'abc' vs 'def'",
    ):
        _canonical_mapping_index(mappings)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "v16.1:wcm / v16.2:wci / v17.3:xms",
            ["UpdateUiConfigRequest 16.1: parsed 'wcm', canonical 'wcs'"],
        ),
        ("v16.1:wcs / v16.2:wci / v17.3:xms", []),
    ],
)
def test_update_ui_config_request_pairs_match_independent_canonical_map(
    source, expected
):
    canonical = {
        "UpdateUiConfigRequest": {"16.1": "wcs", "16.2": "wci"}
    }
    audit = {
        "message": "UpdateUiConfigRequest",
        "evidence": [{"type": "cross_version", "source": source}],
    }
    assert _canonical_pair_violations(audit, canonical) == expected


@pytest.mark.parametrize(
    "status",
    ["unmappable_16_4", "unmappable_marker", "drift_detected", "unknown_status"],
)
def test_negative_or_unknown_evidence_status_is_not_supportive(status):
    audit = {"evidence": [{"type": "cross_version", "status": status}]}
    assert expected_tier(audit) == "unverified"


@pytest.mark.parametrize("status", [None, "consistent"])
def test_absent_or_consistent_evidence_status_is_supportive(status):
    entry = {"type": "cross_version"}
    if status is not None:
        entry["status"] = status
    assert expected_tier({"evidence": [entry]}) == "bronze"


@pytest.mark.parametrize(
    "status", ["unmappable_16_4", "unmappable_marker", "drift_detected"]
)
def test_negative_cross_version_status_supports_neither_silver_nor_gold(status):
    bronze_audit = {
        "evidence": [
            {"type": "apk_static"},
            {
                "type": "cross_version",
                "source": "v15.9:vvj / v16.2:wcr",
                "status": status,
            },
        ]
    }
    silver_audit = {
        "evidence": [
            *bronze_audit["evidence"],
            {"type": "deep_trace", "source": "APK 16.2 ied.java:73 handler"},
        ]
    }
    assert expected_tier(bronze_audit) == "bronze"
    assert expected_tier(silver_audit) == "silver"


def test_same_type_supportive_evidence_does_not_promote_to_silver():
    audit = {
        "evidence": [
            {"type": "apk_static"},
            {"type": "apk_static", "status": "consistent"},
            {"type": "cross_version", "status": "unmappable_16_4"},
        ]
    }
    assert expected_tier(audit) == "bronze"


def test_gold_requires_primary_handler_and_exact_cross_version_anchors():
    assert expected_tier({"evidence": _gold_evidence()}) == "gold"


@pytest.mark.parametrize(
    "evidence",
    [
        [
            {"type": "apk_deep_trace", "source": "internal verification report"},
            {"type": "cross_version", "source": "v15.9:vvj / v16.2:wcr"},
        ],
        [
            {
                "type": "apk_deep_trace",
                "source": "analysis/reports/proto-verification/video.md",
                "description": "The summary cites handler ied.java:73.",
            },
            {"type": "cross_version", "source": "v15.9:vvj / v16.2:wcr"},
        ],
        [
            {"type": "apk_deep_trace", "source": "JADX ied.java:73 handler"},
            {"type": "cross_version", "source": "cross-version checker (15.9, 16.2)"},
        ],
    ],
)
def test_gold_stays_silver_when_a_prerequisite_is_not_reproducible(evidence):
    assert expected_tier({"evidence": evidence}) == "silver"


def test_platinum_requires_gold_and_scoped_message_evidence(tmp_path):
    assert expected_tier(
        {"evidence": [*_gold_evidence(), _platinum(tmp_path)]}, tmp_path
    ) == "platinum"


def test_platinum_cannot_skip_gold(tmp_path):
    audit = {"evidence": [{"type": "apk_static"}, _platinum(tmp_path)]}
    assert expected_tier(audit, tmp_path) == "silver"


def test_match08_service_binding_alone_is_not_message_platinum(tmp_path):
    audit = {"evidence": [*_gold_evidence(), _platinum(tmp_path, ["MATCH-08"])]}
    assert expected_tier(audit, tmp_path) == "gold"


def test_retracted_is_non_ordinal_and_ignores_stated_confidence():
    audit = {"confidence": "gold", "retracted": True, "evidence": _gold_evidence()}
    assert expected_tier(audit) == "retracted"


@pytest.mark.parametrize(
    "audit",
    [
        {"oem_match_pending_gold": False, "evidence": [{"type": "apk_static"}]},
        {"oem_match_pending_gold": True, "evidence": _gold_evidence()},
        {"oem_match_pending_gold": True, "evidence": [{"type": "apk_static"}]},
    ],
)
def test_invalid_pending_gold_flags_are_rejected(audit):
    assert pending_gold_violations(audit, REPO_ROOT)


AUDIT_FILES = _find_audit_files()
CLASS_MAPPING = yaml.safe_load(CLASS_MAPPING_PATH.read_text())
CANONICAL_MAPPING_INDEX = _canonical_mapping_index(CLASS_MAPPING["mappings"])


@pytest.mark.skipif(not AUDIT_FILES, reason="No .audit.yaml files found under oaa/")
@pytest.mark.parametrize("audit_path", AUDIT_FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_each_audit_yaml_matches_canonical_confidence_policy(audit_path):
    audit = yaml.safe_load(audit_path.read_text())
    assert isinstance(audit, dict), f"{audit_path}: expected a YAML mapping"
    stated = audit.get("confidence")
    expected = expected_tier(audit, REPO_ROOT)
    assert stated == expected, (
        f"{audit_path.relative_to(REPO_ROOT)}: confidence is {stated!r}, "
        f"independent evidence policy yields {expected!r}"
    )
    if stated == "platinum":
        assert audit.get("platinum_scope") in {"single_oem", "multi_oem"}
    else:
        assert "platinum_scope" not in audit
    assert not pending_gold_violations(audit, REPO_ROOT), (
        f"{audit_path.relative_to(REPO_ROOT)}: "
        f"{pending_gold_violations(audit, REPO_ROOT)}"
    )


@pytest.mark.skipif(not AUDIT_FILES, reason="No .audit.yaml files found under oaa/")
@pytest.mark.parametrize("audit_path", AUDIT_FILES, ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_cross_version_pairs_match_canonical_class_mapping(audit_path):
    audit = yaml.safe_load(audit_path.read_text())
    violations = _canonical_pair_violations(audit, CANONICAL_MAPPING_INDEX)
    assert not violations, (
        f"{audit_path.relative_to(REPO_ROOT)}: " + "; ".join(violations)
    )
