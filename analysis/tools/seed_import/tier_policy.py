"""Canonical executable confidence policy for audit sidecars."""

from __future__ import annotations

import re
from pathlib import Path

_VERSION = r"(?P<version>\d+\.\d+(?:\.\d+)?)"
_CLASS = r"(?P<class>[a-z][a-z0-9_$]{0,31})(?![a-z0-9_$])"

_VERSION_CLASS_PATTERNS = (
    re.compile(
        rf"\bv?{_VERSION}\s*[:=]\s*{_CLASS}",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b(?:APK|Android Auto)\s+v?{_VERSION}"
        rf"\s*\(\s*(?:(?:class)\s+|jadx:\s*)?{_CLASS}\s*\)",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b(?:APK|Android Auto)\s+v?{_VERSION}"
        rf"\s+(?:(?:class)\s+|jadx:\s*){_CLASS}",
        re.IGNORECASE,
    ),
)


def has_retraction_record(audit: dict) -> bool:
    """Return whether the sidecar independently records a retraction."""
    return bool(
        audit.get("retracted") is True
        or audit.get("retraction")
        or audit.get("retraction_reason")
        or audit.get("replaced_by")
    )


def has_primary_deep_trace(evidence: list[dict]) -> bool:
    """Require a decompiled-source handler anchor, not an internal report."""
    for entry in evidence:
        if entry.get("type") not in {"deep_trace", "apk_deep_trace"}:
            continue
        source = str(entry.get("source", ""))
        if ".java" not in source or source.startswith("analysis/reports/"):
            continue
        if re.search(r"\b(?:JADX|handler|line\s+\d+)\b|:\d|->|\bm(?:o)?\d", source):
            return True
    return False


def version_class_pairs(entry: dict) -> set[tuple[str, str]]:
    """Extract exact APK-version/obfuscated-class pairs from one entry."""
    detail = " ".join(
        str(entry.get(key, "")) for key in ("source", "method", "description")
    )
    pairs: set[tuple[str, str]] = set()
    for pattern in _VERSION_CLASS_PATTERNS:
        pairs.update(
            (match.group("version"), match.group("class").lower())
            for match in pattern.finditer(detail)
        )
    return pairs


def is_supportive_evidence(entry: dict) -> bool:
    """Return whether an entry positively supports the audited claim."""
    return entry.get("status") in {None, "consistent"}


def has_reproducible_cross_version(evidence: list[dict]) -> bool:
    """Require one cross-version entry with exact classes for 2+ APK versions."""
    for entry in evidence:
        if entry.get("type") != "cross_version" or not is_supportive_evidence(entry):
            continue
        pairs = version_class_pairs(entry)
        if len({version for version, _ in pairs}) >= 2:
            return True
    return False


def has_gold_prerequisites(evidence: list[dict]) -> bool:
    return has_primary_deep_trace(evidence) and has_reproducible_cross_version(evidence)


def qualifying_platinum_entry(entry: dict, repo_root: Path | None = None) -> bool:
    """Validate scoped message/field OEM evidence, excluding MATCH-08 alone."""
    if entry.get("type") not in {"platinum_evidence", "oem_capture"}:
        return False
    required = {
        "capture_path", "vehicle_metadata", "msg_seq", "ts_ms",
        "message_completeness", "attribution_method", "oem_scope",
        "applicability", "match_rules",
    }
    if not required <= entry.keys():
        return False
    if not entry.get("msg_seq") or not entry.get("ts_ms") or not entry.get("match_rules"):
        return False
    if set(entry["match_rules"]) == {"MATCH-08"}:
        return False
    if entry.get("applicability") == "fields" and not entry.get("fields"):
        return False
    if entry.get("applicability") == "message" and "fields" in entry:
        return False
    metadata = entry.get("vehicle_metadata")
    if not isinstance(metadata, dict) or not {
        "make", "model", "year", "aa_version"
    } <= metadata.keys():
        return False
    if repo_root is not None and not (repo_root / entry["capture_path"]).exists():
        return False
    return True


def expected_tier(audit: dict, repo_root: Path | None = None) -> str:
    """Derive a tier without consulting the sidecar's stated confidence."""
    if has_retraction_record(audit):
        return "retracted"
    evidence = audit.get("evidence") or []
    types = {
        entry.get("type")
        for entry in evidence
        if entry.get("type") and is_supportive_evidence(entry)
    }
    gold = has_gold_prerequisites(evidence)
    platinum = any(qualifying_platinum_entry(entry, repo_root) for entry in evidence)
    if gold and platinum:
        return "platinum"
    if gold:
        return "gold"
    if len(types) >= 2:
        return "silver"
    if types:
        return "bronze"
    return "unverified"


def pending_gold_violations(audit: dict, repo_root: Path | None = None) -> list[str]:
    """Return strict no-skip worklist violations without reading confidence."""
    if "oem_match_pending_gold" not in audit:
        if "pending_platinum_evidence" in audit:
            return ["pending_platinum_evidence requires oem_match_pending_gold: true"]
        return []
    violations: list[str] = []
    if audit["oem_match_pending_gold"] is not True:
        violations.append("oem_match_pending_gold must be true when present")
    tier = expected_tier(audit, repo_root)
    if tier not in {"bronze", "silver"}:
        violations.append(f"pending-Gold is Bronze/Silver-only, not {tier}")
    if "platinum_scope" in audit:
        violations.append("pending-Gold cannot carry platinum_scope")
    if any(
        entry.get("type") in {"platinum_evidence", "oem_capture"}
        for entry in audit.get("evidence") or []
    ):
        violations.append("pending OEM evidence belongs outside evidence[]")
    pending = audit.get("pending_platinum_evidence") or []
    if not pending or not all(qualifying_platinum_entry(e, repo_root) for e in pending):
        violations.append("pending-Gold requires qualifying pending OEM evidence")
    return violations
