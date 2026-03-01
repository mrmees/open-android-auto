"""Layer 3: Cross-version structural drift between APK versions."""
from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path

from analysis.tools.proto_schema_validator.models import (
    DriftIssue,
    FieldDef,
    IssueKind,
    Severity,
)
from analysis.tools.proto_schema_validator.mapping import (
    get_all_apk_classes,
    get_apk_fields,
    get_apk_syntax,
)


def _structural_fingerprint(fields: list[FieldDef]) -> str:
    """Hash (field_number, base_type, is_repeated, is_packed) tuples."""
    parts = sorted(
        (f.field_number, f.base_type, f.is_repeated, f.is_packed)
        for f in fields
    )
    raw = str(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def compare_class_fields(
    fields_v1: list[FieldDef],
    fields_v2: list[FieldDef],
    class_v1: str,
    class_v2: str,
) -> list[DriftIssue]:
    """Compare fields between two APK versions of the same class."""
    issues: list[DriftIssue] = []

    v1_by_num = {f.field_number: f for f in fields_v1}
    v2_by_num = {f.field_number: f for f in fields_v2}

    all_nums = sorted(set(v1_by_num) | set(v2_by_num))

    for num in all_nums:
        f1 = v1_by_num.get(num)
        f2 = v2_by_num.get(num)

        if f1 and not f2:
            issues.append(DriftIssue(
                apk_class_v1=class_v1,
                apk_class_v2=class_v2,
                kind=IssueKind.FIELD_REMOVED,
                severity=Severity.WARNING,
                field_number=num,
                detail=f"field {num} ({f1.base_type}) present in v1 but removed in v2",
            ))
        elif f2 and not f1:
            issues.append(DriftIssue(
                apk_class_v1=class_v1,
                apk_class_v2=class_v2,
                kind=IssueKind.FIELD_ADDED,
                severity=Severity.INFO,
                field_number=num,
                detail=f"field {num} ({f2.base_type}) added in v2",
            ))
        elif f1 and f2 and f1.base_type != f2.base_type:
            issues.append(DriftIssue(
                apk_class_v1=class_v1,
                apk_class_v2=class_v2,
                kind=IssueKind.FIELD_TYPE_CHANGED,
                severity=Severity.ERROR,
                field_number=num,
                detail=f"field {num} type changed: v1={f1.base_type}, v2={f2.base_type}",
            ))

    return issues


def run_layer3(
    mappings: list,
    db_primary: Path,
    db_alt: Path,
    primary_version: str = "16.1",
) -> tuple[list[DriftIssue], dict]:
    """Run Layer 3 cross-version drift analysis.

    db_primary is the DB for primary_version, db_alt is the other version.
    """
    alt_version = "16.2" if primary_version == "16.1" else "16.1"

    all_issues: list[DriftIssue] = []
    stats = {"compared": 0, "matches": 0, "drift_found": 0}

    # Part 1: Direct comparison for classes with both versions mapped
    for m in mappings:
        cls_v1 = m.apk_classes.get(primary_version)
        cls_v2 = m.apk_classes.get(alt_version)
        if not cls_v1 or not cls_v2:
            continue

        fields_v1 = get_apk_fields(db_primary, cls_v1)
        fields_v2 = get_apk_fields(db_alt, cls_v2)

        if not fields_v1 or not fields_v2:
            continue

        stats["compared"] += 1
        issues = compare_class_fields(fields_v1, fields_v2, cls_v1, cls_v2)
        if issues:
            stats["drift_found"] += 1
        all_issues.extend(issues)

    # Part 2: Structural fingerprinting to find matches for unmapped classes
    # Build fingerprint -> class_name mapping for the alt DB
    alt_classes = get_all_apk_classes(db_alt)
    alt_fingerprints: dict[str, list[str]] = defaultdict(list)
    alt_field_cache: dict[str, list[FieldDef]] = {}

    for cls_name in alt_classes:
        fields = get_apk_fields(db_alt, cls_name)
        if not fields:
            continue
        alt_field_cache[cls_name] = fields
        fp = _structural_fingerprint(fields)
        alt_fingerprints[fp].append(cls_name)

    # For each primary-version-only mapping, try to find structural match
    for m in mappings:
        cls_v1 = m.apk_classes.get(primary_version)
        cls_v2 = m.apk_classes.get(alt_version)
        if not cls_v1 or cls_v2:
            continue  # Skip if already mapped or no primary class

        fields_v1 = get_apk_fields(db_primary, cls_v1)
        if not fields_v1:
            continue

        fp = _structural_fingerprint(fields_v1)
        matches = alt_fingerprints.get(fp, [])

        if len(matches) == 1:
            # Unique structural match
            matched_cls = matches[0]
            stats["matches"] += 1
            all_issues.append(DriftIssue(
                apk_class_v1=cls_v1,
                apk_class_v2=matched_cls,
                kind=IssueKind.STRUCTURAL_MATCH,
                severity=Severity.INFO,
                detail=f"unique structural match: {cls_v1} (v1) -> {matched_cls} (v2) "
                       f"[{len(fields_v1)} fields, fingerprint {fp}] "
                       f"(proto: {m.proto_message})",
            ))

            # Also do field comparison for structural matches
            fields_v2 = alt_field_cache.get(matched_cls, [])
            if fields_v2:
                drift = compare_class_fields(fields_v1, fields_v2, cls_v1, matched_cls)
                all_issues.extend(drift)

    return all_issues, stats
