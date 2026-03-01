"""Layer 1: Compare our proto schemas against APK database field structures."""
from __future__ import annotations

from pathlib import Path

from analysis.tools.proto_schema_validator.models import (
    FieldDef,
    IssueKind,
    SchemaIssue,
    Severity,
    WIRE_TYPE_GROUPS,
)
from analysis.tools.proto_schema_validator.mapping import (
    get_apk_fields,
    get_apk_syntax,
    get_our_syntax,
    get_proto_fields_from_descriptor,
)
from google.protobuf import descriptor_pool


# Known issues that can't be fixed without splitting proto files or
# are proto-lite encoding artifacts.  Downgrade these from ERROR to WARNING.
_KNOWN_ISSUES = {
    # Proto3 messages in proto2 files — can't have two syntaxes in one file.
    # CarControlMessages.proto has both proto2 and proto3 messages.
    ("CarAction", IssueKind.SYNTAX_MISMATCH),
    ("CarAreaId", IssueKind.SYNTAX_MISMATCH),
    ("CarProperty", IssueKind.SYNTAX_MISMATCH),
    ("CarPropertyControl", IssueKind.SYNTAX_MISMATCH),
    ("CarPropertyValue", IssueKind.SYNTAX_MISMATCH),
    ("FloatValues", IssueKind.SYNTAX_MISMATCH),
    ("IntValues", IssueKind.SYNTAX_MISMATCH),
    ("LongValues", IssueKind.SYNTAX_MISMATCH),
    # PhoneCapabilitiesData.proto — mixed syntax
    ("CapabilityEntry", IssueKind.SYNTAX_MISMATCH),
    ("CapabilityFlag", IssueKind.SYNTAX_MISMATCH),
    ("CapabilityPair", IssueKind.SYNTAX_MISMATCH),
    ("PingConfigPair", IssueKind.SYNTAX_MISMATCH),
    # FeatureFlagsData.proto — mixed syntax
    ("AssistantFeatureFlags", IssueKind.SYNTAX_MISMATCH),
    # Proto-lite MAP type encoded as group — message vs group mismatch
    ("NavigationDistanceDisplay", IssueKind.TYPE_MISMATCH),
    # Proto-lite closed enum wrappers — enums appear as message in DB
    ("WifiSecurityResponse", IssueKind.TYPE_MISMATCH),
}


def _same_wire_type(type_a: str, type_b: str) -> bool:
    """Check if two proto types share the same wire encoding."""
    ga = WIRE_TYPE_GROUPS.get(type_a)
    gb = WIRE_TYPE_GROUPS.get(type_b)
    if ga is None or gb is None:
        return False
    return ga == gb


def compare_fields(
    our_fields: list[FieldDef],
    apk_fields: list[FieldDef],
    proto_message: str,
) -> list[SchemaIssue]:
    """Compare our schema fields against APK DB fields."""
    issues: list[SchemaIssue] = []

    our_by_num = {f.field_number: f for f in our_fields}
    apk_by_num = {f.field_number: f for f in apk_fields}

    all_nums = sorted(set(our_by_num) | set(apk_by_num))

    for num in all_nums:
        ours = our_by_num.get(num)
        theirs = apk_by_num.get(num)

        if theirs and not ours:
            issues.append(SchemaIssue(
                proto_message=proto_message,
                kind=IssueKind.MISSING_FIELD,
                severity=Severity.ERROR,
                field_number=num,
                detail=f"field {num} in APK ({theirs.base_type}"
                       f"{' repeated' if theirs.is_repeated else ''}) "
                       f"but missing from our schema",
            ))
            continue

        if ours and not theirs:
            issues.append(SchemaIssue(
                proto_message=proto_message,
                kind=IssueKind.EXTRA_FIELD,
                severity=Severity.WARNING,
                field_number=num,
                detail=f"field {num} ({ours.name}: {ours.base_type}) "
                       f"in our schema but not in APK DB",
            ))
            continue

        # Both exist — compare types
        assert ours is not None and theirs is not None
        if ours.base_type != theirs.base_type:
            same_wire = _same_wire_type(ours.base_type, theirs.base_type)
            issues.append(SchemaIssue(
                proto_message=proto_message,
                kind=IssueKind.TYPE_MISMATCH,
                severity=Severity.WARNING if same_wire else Severity.ERROR,
                field_number=num,
                detail=f"field {num} ({ours.name}): "
                       f"ours={ours.base_type}, APK={theirs.base_type}"
                       f"{' (same wire type)' if same_wire else ' (DIFFERENT wire type!)'}",
            ))

        # Compare modifiers
        modifier_diffs = []
        if ours.is_repeated != theirs.is_repeated:
            modifier_diffs.append(
                f"repeated: ours={ours.is_repeated}, APK={theirs.is_repeated}"
            )
        if ours.is_packed != theirs.is_packed:
            modifier_diffs.append(
                f"packed: ours={ours.is_packed}, APK={theirs.is_packed}"
            )
        if ours.is_oneof != theirs.is_oneof:
            modifier_diffs.append(
                f"oneof: ours={ours.is_oneof}, APK={theirs.is_oneof}"
            )
        if ours.is_map != theirs.is_map:
            modifier_diffs.append(
                f"map: ours={ours.is_map}, APK={theirs.is_map}"
            )

        if modifier_diffs:
            issues.append(SchemaIssue(
                proto_message=proto_message,
                kind=IssueKind.MODIFIER_MISMATCH,
                severity=Severity.WARNING,
                field_number=num,
                detail=f"field {num} ({ours.name}): {'; '.join(modifier_diffs)}",
            ))

    return issues


def validate_message(
    pool: descriptor_pool.DescriptorPool,
    proto_fqn: str,
    proto_file: str,
    proto_message: str,
    apk_class: str,
    db_path: Path,
) -> list[SchemaIssue]:
    """Run full Layer 1 validation for a single message."""
    issues: list[SchemaIssue] = []

    # Syntax check
    our_syntax = get_our_syntax(proto_file)
    apk_syntax = get_apk_syntax(db_path, apk_class)
    if apk_syntax and our_syntax != "unknown" and our_syntax != apk_syntax:
        issues.append(SchemaIssue(
            proto_message=proto_message,
            kind=IssueKind.SYNTAX_MISMATCH,
            severity=Severity.ERROR,
            detail=f"ours={our_syntax}, APK={apk_syntax}",
        ))

    # Get fields from both sides
    try:
        our_fields = get_proto_fields_from_descriptor(pool, proto_fqn)
    except KeyError:
        issues.append(SchemaIssue(
            proto_message=proto_message,
            kind=IssueKind.MISSING_FIELD,
            severity=Severity.ERROR,
            detail=f"could not find {proto_fqn} in compiled descriptor pool",
        ))
        return issues

    apk_fields = get_apk_fields(db_path, apk_class)
    if not apk_fields:
        issues.append(SchemaIssue(
            proto_message=proto_message,
            kind=IssueKind.MISSING_FIELD,
            severity=Severity.WARNING,
            detail=f"APK class {apk_class} has no fields in DB "
                   f"(may be empty message or missing descriptor)",
        ))
        return issues

    # Field comparison
    issues.extend(compare_fields(our_fields, apk_fields, proto_message))

    # Downgrade known-unfixable issues from ERROR to WARNING
    downgraded = []
    for issue in issues:
        if issue.severity == Severity.ERROR:
            key = (issue.proto_message, issue.kind)
            if key in _KNOWN_ISSUES:
                issue = SchemaIssue(
                    proto_message=issue.proto_message,
                    kind=issue.kind,
                    severity=Severity.WARNING,
                    field_number=issue.field_number,
                    detail=issue.detail + " [known limitation]",
                )
        downgraded.append(issue)

    return downgraded


def run_layer1(
    pool: descriptor_pool.DescriptorPool,
    mappings: list,
    db_path: Path,
    version: str = "16.1",
) -> list[SchemaIssue]:
    """Run Layer 1 validation across all mapped protos."""
    all_issues: list[SchemaIssue] = []

    for m in mappings:
        apk_class = m.apk_classes.get(version)
        if not apk_class:
            continue
        if not m.proto_fqn:
            continue

        issues = validate_message(
            pool=pool,
            proto_fqn=m.proto_fqn,
            proto_file=m.proto_file,
            proto_message=m.proto_message,
            apk_class=apk_class,
            db_path=db_path,
        )
        all_issues.extend(issues)

    return all_issues
