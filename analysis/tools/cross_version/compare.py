"""3-way cross-version comparison orchestrator.

Compares proto class structures across multiple APK versions using
pairwise comparison from layer3_crossversion.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from analysis.tools.proto_schema_validator.mapping import (
    get_apk_fields,
    get_apk_enum_values,
    load_mapping,
)
from analysis.tools.proto_schema_validator.layer3_crossversion import (
    compare_class_fields,
)
from analysis.tools.proto_schema_validator.models import (
    DriftIssue,
    FieldDef,
    IssueKind,
    ProtoMapping,
    Severity,
)


@dataclass
class ComparisonResult:
    """Result of comparing one mapping across version pairs."""

    mapping: ProtoMapping
    pairs_compared: list[tuple[str, str]] = field(default_factory=list)
    issues: list[DriftIssue] = field(default_factory=list)

    @property
    def has_suspicious(self) -> bool:
        """True if any issue is FIELD_REMOVED or FIELD_TYPE_CHANGED."""
        return any(
            i.kind in (IssueKind.FIELD_REMOVED, IssueKind.FIELD_TYPE_CHANGED)
            for i in self.issues
        )

    @property
    def is_consistent(self) -> bool:
        """True if no suspicious divergences found."""
        return not self.has_suspicious

    @property
    def versions_matched(self) -> list[str]:
        """Unique versions that participated in comparison."""
        versions = set()
        for v1, v2 in self.pairs_compared:
            versions.add(v1)
            versions.add(v2)
        return sorted(versions)


def _get_fields_or_enum(db_path: Path, class_name: str) -> list[FieldDef]:
    """Get fields for a class, falling back to enum values as synthetic fields."""
    fields = get_apk_fields(db_path, class_name)
    if fields:
        return fields

    # Fallback: try enum values and convert to synthetic FieldDef entries
    enum_vals = get_apk_enum_values(db_path, class_name)
    if enum_vals:
        return [
            FieldDef(
                field_number=int_val,
                base_type="enum_value",
                name=name,
            )
            for int_val, name in enum_vals
        ]
    return []


def run_comparison(
    db_paths: dict[str, Path],
    mappings: list[ProtoMapping] | None = None,
) -> list[ComparisonResult]:
    """Run pairwise comparisons across all version pairs.

    Args:
        db_paths: Maps version label (e.g. "15.9", "16.1") to DB path.
        mappings: ProtoMapping list. If None, loads from class_mapping.yaml.

    Returns:
        List of ComparisonResult, one per mapping.
    """
    if mappings is None:
        mappings = load_mapping()

    versions = sorted(db_paths.keys())
    pairs = []
    for i, v1 in enumerate(versions):
        for v2 in versions[i + 1:]:
            pairs.append((v1, v2))

    results: list[ComparisonResult] = []

    for m in mappings:
        result = ComparisonResult(mapping=m)

        for v1, v2 in pairs:
            cls1 = m.apk_classes.get(v1)
            cls2 = m.apk_classes.get(v2)
            if not cls1 or not cls2:
                continue

            fields1 = _get_fields_or_enum(db_paths[v1], cls1)
            fields2 = _get_fields_or_enum(db_paths[v2], cls2)

            if not fields1 and not fields2:
                continue

            result.pairs_compared.append((v1, v2))
            issues = compare_class_fields(fields1, fields2, cls1, cls2)
            result.issues.extend(issues)

        if result.pairs_compared:
            results.append(result)

    return results
