from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path

from .models import (
    DispatchObservation,
    EnumNode,
    FieldShape,
    LineageAnchor,
    MatchResult,
    MessageNode,
)


_STRUCTURAL_FIELD_ATTRIBUTES = (
    "base_type",
    "repeated",
    "packed",
    "oneof",
    "map",
    "required",
)


def _field_payload(field: FieldShape) -> dict[str, object]:
    return {
        "number": field.number,
        **{
            attribute: getattr(field, attribute)
            for attribute in _STRUCTURAL_FIELD_ATTRIBUTES
        },
    }


def describe_schema_difference(
    canonical: MessageNode,
    apk: MessageNode,
) -> dict[str, object]:
    """Describe the local structural delta without comparing obfuscated targets."""
    canonical_fields = {field.number: field for field in canonical.fields}
    apk_fields = {field.number: field for field in apk.fields}
    missing_numbers = sorted(canonical_fields.keys() - apk_fields.keys())
    extra_numbers = sorted(apk_fields.keys() - canonical_fields.keys())
    changed_fields = []
    for number in sorted(canonical_fields.keys() & apk_fields.keys()):
        canonical_field = canonical_fields[number]
        apk_field = apk_fields[number]
        changes = {
            attribute: {
                "canonical": getattr(canonical_field, attribute),
                "apk": getattr(apk_field, attribute),
            }
            for attribute in _STRUCTURAL_FIELD_ATTRIBUTES
            if getattr(canonical_field, attribute) != getattr(apk_field, attribute)
        }
        if changes:
            changed_fields.append({"number": number, "changes": changes})
    return {
        "syntax": (
            None
            if canonical.syntax == apk.syntax
            else {"canonical": canonical.syntax, "apk": apk.syntax}
        ),
        "missing_fields": [
            _field_payload(canonical_fields[number]) for number in missing_numbers
        ],
        "extra_fields": [_field_payload(apk_fields[number]) for number in extra_numbers],
        "changed_fields": changed_fields,
    }


def _format_field(field: dict[str, object]) -> str:
    modifiers = [
        attribute
        for attribute in _STRUCTURAL_FIELD_ATTRIBUTES[1:]
        if field.get(attribute)
    ]
    suffix = f" ({', '.join(modifiers)})" if modifiers else ""
    return f"f{field['number']} {field['base_type']}{suffix}"


def _format_schema_difference(difference: dict[str, object]) -> str:
    parts = []
    syntax = difference.get("syntax")
    if isinstance(syntax, dict):
        parts.append(f"syntax {syntax['canonical']}→{syntax['apk']}")
    for field in difference.get("missing_fields", []):
        parts.append(f"missing {_format_field(field)}")
    for field in difference.get("extra_fields", []):
        parts.append(f"extra {_format_field(field)}")
    for field in difference.get("changed_fields", []):
        changes = ", ".join(
            f"{attribute} {values['canonical']}→{values['apk']}"
            for attribute, values in field["changes"].items()
        )
        parts.append(f"f{field['number']} {changes}")
    return "; ".join(parts) or "no local structural delta"


def build_payload(
    *,
    version: str,
    apk_sha256: str,
    canonical_count: int,
    apk_count: int,
    canonical_edge_count: int,
    apk_edge_count: int,
    canonical_graph: dict[str, MessageNode],
    apk_graph: dict[str, MessageNode],
    canonical_enums: dict[str, EnumNode],
    apk_enums: dict[str, EnumNode],
    enum_matches: dict[str, list[str]],
    results: list[MatchResult],
    observations: list[DispatchObservation],
    lineage_anchors: list[LineageAnchor],
) -> dict[str, object]:
    status_counts = Counter(result.status for result in results)
    result_by_name = {result.canonical_name: result for result in results}
    dispatch_schema_conflicts = []
    for observation in observations:
        if (
            observation.service_type in {"control", "canonical_log"}
            or observation.canonical_name not in result_by_name
            or observation.apk_class
            in result_by_name[observation.canonical_name].structural_candidates
            or observation.canonical_name not in canonical_graph
            or observation.apk_class not in apk_graph
        ):
            continue
        conflict = asdict(observation)
        conflict["schema_difference"] = describe_schema_difference(
            canonical_graph[observation.canonical_name],
            apk_graph[observation.apk_class],
        )
        dispatch_schema_conflicts.append(conflict)
    enum_domain_mappings = [
        {
            "canonical_name": canonical_name,
            "apk_class": candidates[0],
            "value_count": len(canonical_enums[canonical_name].structural_key()),
        }
        for canonical_name, candidates in sorted(enum_matches.items())
        if len(candidates) == 1
        and sum(
            other_candidates == candidates
            for other_candidates in enum_matches.values()
        )
        == 1
    ]
    constraint_conflict_details = []
    for result in results:
        if result.status not in {
            "constraint_conflict",
            "dispatch_resolved_edge_conflict",
            "lineage_resolved_edge_conflict",
        }:
            continue
        canonical_node = canonical_graph[result.canonical_name]
        for apk_class in result.structural_candidates:
            apk_fields = {field.number: field for field in apk_graph[apk_class].fields}
            for canonical_field in canonical_node.fields:
                if (
                    canonical_field.base_type not in {"message", "group"}
                    or not canonical_field.target
                    or canonical_field.target not in result_by_name
                ):
                    continue
                apk_field = apk_fields.get(canonical_field.number)
                target_result = result_by_name[canonical_field.target]
                if (
                    apk_field is None
                    or apk_field.target is None
                    or not target_result.structural_candidates
                    or apk_field.target in target_result.structural_candidates
                ):
                    continue
                constraint_conflict_details.append(
                    {
                        "canonical_name": result.canonical_name,
                        "apk_class": apk_class,
                        "field_number": canonical_field.number,
                        "canonical_target": canonical_field.target,
                        "apk_target": apk_field.target,
                        "reason": "child local schema differs",
                    }
                )
    resolved_parent_child_schema_differences = []
    for result in results:
        has_trusted_parent_edge = any(
            evidence.relation == "trusted_parent"
            for evidence in result.graph_evidence
        )
        if result.resolved_apk_class is None or not (
            result.confidence == "high" or has_trusted_parent_edge
        ):
            continue
        canonical_parent = canonical_graph[result.canonical_name]
        apk_parent = apk_graph[result.resolved_apk_class]
        apk_fields = {field.number: field for field in apk_parent.fields}
        for canonical_field in canonical_parent.fields:
            if (
                canonical_field.base_type not in {"message", "group"}
                or not canonical_field.target
                or canonical_field.target not in result_by_name
            ):
                continue
            apk_field = apk_fields.get(canonical_field.number)
            if (
                apk_field is None
                or apk_field.target is None
                or apk_field.target not in apk_graph
            ):
                continue
            child_result = result_by_name[canonical_field.target]
            if apk_field.target in child_result.structural_candidates:
                continue
            resolved_parent_child_schema_differences.append(
                {
                    "canonical_parent": result.canonical_name,
                    "apk_parent": result.resolved_apk_class,
                    "field_number": canonical_field.number,
                    "canonical_child": canonical_field.target,
                    "apk_child": apk_field.target,
                    "canonical_child_status": child_result.status,
                    "schema_difference": describe_schema_difference(
                        canonical_graph[canonical_field.target],
                        apk_graph[apk_field.target],
                    ),
                }
            )
    match_payloads = []
    for result in results:
        item = asdict(result)
        del item["lineage_anchor"]
        match_payloads.append(item)
    return {
        "version": version,
        "apk_sha256": apk_sha256,
        "canonical_message_count": canonical_count,
        "apk_message_count": apk_count,
        "canonical_enum_count": len(canonical_enums),
        "apk_enum_count": len(apk_enums),
        "canonical_message_edge_count": canonical_edge_count,
        "apk_message_edge_count": apk_edge_count,
        "summary": {
            "resolved": sum(result.resolved_apk_class is not None for result in results),
            "high_confidence": sum(result.confidence == "high" for result in results),
            "medium_confidence": sum(result.confidence == "medium" for result in results),
            "dispatch_observations": len(observations),
            "lineage_anchors": len(lineage_anchors),
            "lineage_invalidations": sum(
                anchor.disposition == "invalidated" for anchor in lineage_anchors
            ),
            "dispatch_schema_conflicts": len(dispatch_schema_conflicts),
            "unique_enum_domains": len(enum_domain_mappings),
            "direct_child_schema_conflicts": len(constraint_conflict_details),
            "resolved_parent_child_schema_differences": len(
                resolved_parent_child_schema_differences
            ),
            "status_counts": dict(sorted(status_counts.items())),
        },
        "dispatch_schema_conflicts": dispatch_schema_conflicts,
        "enum_domain_mappings": enum_domain_mappings,
        "constraint_conflict_details": constraint_conflict_details,
        "resolved_parent_child_schema_differences": (
            resolved_parent_child_schema_differences
        ),
        "lineage_anchors": [asdict(anchor) for anchor in lineage_anchors],
        "matches": match_payloads,
    }


def write_json(payload: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_markdown(payload: dict[str, object]) -> str:
    summary = payload["summary"]
    assert isinstance(summary, dict)
    matches = payload["matches"]
    assert isinstance(matches, list)

    lines = [
        f"# Android Auto {payload['version']} Static Proto Schema Matches",
        "",
        "This report is generated from protobuf-lite `RawMessageInfo` metadata and",
        "static service/semantic dispatch evidence, and curated cross-version class",
        "lineage. It does not use a live Android Auto session.",
        "",
        "## Provenance",
        "",
        f"- APK SHA-256: `{payload['apk_sha256']}`",
        f"- Canonical messages: {payload['canonical_message_count']}",
        f"- Decoded APK messages: {payload['apk_message_count']}",
        f"- Canonical enums: {payload['canonical_enum_count']}",
        f"- Decoded APK enums: {payload['apk_enum_count']}",
        f"- Canonical message-reference edges: {payload['canonical_message_edge_count']}",
        f"- APK field-linked reference edges: {payload['apk_message_edge_count']}",
        "",
        "## Summary",
        "",
        f"- Resolved mappings: {summary['resolved']}",
        f"- High confidence (dispatch or confirmed lineage): {summary['high_confidence']}",
        f"- Medium confidence (unique structure): {summary['medium_confidence']}",
        f"- Static dispatch observations considered: {summary['dispatch_observations']}",
        f"- Cross-version lineage anchors considered: {summary['lineage_anchors']}",
        f"- Legacy canonical identities invalidated: {summary['lineage_invalidations']}",
        f"- Explicit service/log dispatch schema conflicts: {summary['dispatch_schema_conflicts']}",
        f"- Globally unique enum numeric-domain mappings: {summary['unique_enum_domains']}",
        f"- Direct child-schema conflicts described: {summary['direct_child_schema_conflicts']}",
        f"- Resolved-parent child schema differences: {summary['resolved_parent_child_schema_differences']}",
        "",
        "## Cross-version class-lineage anchors",
        "",
        "Lineage continuity identifies which obfuscated class survived each release.",
        "An `invalidated` disposition means call-site semantics prove that the legacy",
        "canonical name came from an unrelated bundled-library protobuf; it is not a",
        "17.3 protocol mapping.",
        "",
        "| Canonical identity | 16.2 → 16.4 → 17.3 | Disposition | Rejected local candidates | Reason |",
        "|---|---|---|---|---|",
    ]
    for anchor in payload.get("lineage_anchors") or []:
        chain = " → ".join(
            f"`{step['apk_class']}`" for step in anchor["lineage"]
        )
        rejected = ", ".join(
            f"`{candidate}`" for candidate in anchor["rejected_candidates"]
        ) or "—"
        lines.append(
            f"| `{anchor['canonical_name']}` | {chain} | {anchor['disposition']} | "
            f"{rejected} | {anchor['rationale']} |"
        )

    lines.extend(
        [
            "",
            "## Dispatch-resolved mappings",
            "",
            "| Canonical message | APK class | Status | Evidence |",
            "|---|---|---|---|",
        ]
    )

    dispatch_rows = [
        item
        for item in matches
        if str(item["status"]) in {
            "dispatch_resolved",
            "dispatch_resolved_edge_conflict",
            "unique_structural_dispatch_confirmed",
        }
    ]
    for item in dispatch_rows:
        evidence = item.get("dispatch_evidence") or []
        evidence_text = "; ".join(
            f"{entry['service_type']} ID `0x{entry['message_id']:04x}` at "
            f"`{entry['source']}:{entry['line']}`"
            for entry in evidence[:3]
        )
        lines.append(
            f"| `{item['canonical_name']}` | `{item['resolved_apk_class']}` | "
            f"{item['status']} | {evidence_text} |"
        )

    lines.extend(
        [
            "",
            "## Graph-resolved mappings",
            "",
            "These mappings were ambiguous by local shape and became unique after",
            "field-number-labelled message-edge constraint propagation.",
            "",
            "| Canonical message | APK class | Initial candidates | Graph evidence |",
            "|---|---|---:|---|",
        ]
    )
    for item in matches:
        if item["status"] == "graph_resolved":
            evidence = item.get("graph_evidence") or []
            evidence_text = "; ".join(
                f"{entry['relation']} `"
                f"{entry['canonical_parent']}:{entry['field_number']}` → `"
                f"{entry['canonical_target']}` (`{entry['apk_parent']}` → "
                f"`{entry['apk_target']}`)"
                for entry in evidence[:3]
            )
            lines.append(
                f"| `{item['canonical_name']}` | `{item['resolved_apk_class']}` | "
                f"{item['structural_candidate_count']} | {evidence_text} |"
            )

    lines.extend(
        [
            "",
            "## Unique structural mappings",
            "",
            "These mappings have one exact APK schema candidate but no dispatch anchor yet.",
            "",
            "| Canonical message | APK class | Fields |",
            "|---|---|---:|",
        ]
    )
    for item in matches:
        if item["status"] == "unique_structural":
            lines.append(
                f"| `{item['canonical_name']}` | `{item['resolved_apk_class']}` | "
                f"{item['field_count']} |"
            )

    lines.extend(
        [
            "",
            "## Unique enum numeric-domain mappings",
            "",
            "These enum identities have a numeric value set unique in both the canonical",
            "catalog and the decoded APK. Names alone are not used for matching.",
            "",
            "| Canonical enum | APK enum | Distinct values |",
            "|---|---|---:|",
        ]
    )
    for item in payload.get("enum_domain_mappings") or []:
        lines.append(
            f"| `{item['canonical_name']}` | `{item['apk_class']}` | "
            f"{item['value_count']} |"
        )

    lines.extend(
        [
            "",
            "## Resolved-parent child schema differences",
            "",
            "A dispatch/lineage-backed parent, or one linked from a trusted parent,",
            "identifies the APK child at this field, but the child schema differs",
            "from the current canonical definition. These are",
            "version-delta or stale-schema candidates, not accepted mappings.",
            "",
            "| Canonical parent | APK parent | Field | Canonical child | APK child | Local schema difference |",
            "|---|---|---:|---|---|---|",
        ]
    )
    parent_child_differences = (
        payload.get("resolved_parent_child_schema_differences") or []
    )
    if parent_child_differences:
        for item in parent_child_differences:
            lines.append(
                f"| `{item['canonical_parent']}` | `{item['apk_parent']}` | "
                f"{item['field_number']} | `{item['canonical_child']}` | "
                f"`{item['apk_child']}` | "
                f"{_format_schema_difference(item['schema_difference'])} |"
            )
    else:
        lines.extend(["", "None."])

    lines.extend(
        [
            "",
            "## Dispatch/schema conflicts",
            "",
            "Explicit service or message-name evidence identifies an APK class, but its",
            "17.3 local schema differs from the current canonical definition.",
            "",
            "| Canonical message | APK class | Context | Local schema difference | Evidence |",
            "|---|---|---|---|---|",
        ]
    )
    conflicts = payload.get("dispatch_schema_conflicts") or []
    if conflicts:
        for item in conflicts:
            lines.append(
                f"| `{item['canonical_name']}` | `{item['apk_class']}` | "
                f"{item['service_type']} `0x{item['message_id']:04x}` | "
                f"{_format_schema_difference(item['schema_difference'])} | "
                f"`{item['source']}:{item['line']}` |"
            )
    else:
        lines.extend(["", "None."])

    lines.extend(
        [
            "",
            "## Hard-anchor edge conflicts",
            "",
            "Identity is supported by exact local shape and an unambiguous dispatch or",
            "confirmed lineage anchor,",
            "but at least one recovered child edge disagrees with the canonical graph.",
            "",
            "| Canonical message | APK class |",
            "|---|---|",
        ]
    )
    for item in matches:
        if item["status"] in {
            "dispatch_resolved_edge_conflict",
            "lineage_resolved_edge_conflict",
        }:
            lines.append(
                f"| `{item['canonical_name']}` | `{item['resolved_apk_class']}` |"
            )

    lines.extend(
        [
            "",
            "## Constraint conflicts",
            "",
            "These schemas matched locally, but all candidates contradicted at least one",
            "known message-reference edge. They are retained as follow-up evidence rather",
            "than silently accepted or discarded.",
            "",
            "| Canonical message | Initial APK candidates |",
            "|---|---|",
        ]
    )
    for item in matches:
        if item["status"] == "constraint_conflict":
            candidate_text = ", ".join(
                f"`{candidate}`" for candidate in item["structural_candidates"]
            )
            lines.append(f"| `{item['canonical_name']}` | {candidate_text} |")

    lines.extend(
        [
            "",
            "### Direct child-schema differences",
            "",
            "These are first-order edge disagreements where the APK child class does",
            "not have the local shape of any candidate for the canonical child type.",
            "",
            "| Canonical parent | APK parent | Field | Canonical child | APK child |",
            "|---|---|---:|---|---|",
        ]
    )
    for item in payload.get("constraint_conflict_details") or []:
        lines.append(
            f"| `{item['canonical_name']}` | `{item['apk_class']}` | "
            f"{item['field_number']} | `{item['canonical_target']}` | "
            f"`{item['apk_target']}` |"
        )

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Unique structure is evidence of identity, not proof of original Google naming.",
            "- Class continuity across releases is not semantic proof; bundled Google libraries can preserve unrelated schemas for years.",
            "- Empty and small messages remain highly ambiguous until graph or dispatch constraints apply.",
            "- Field references are recovered where the `RawMessageInfo` object-array cursor and JADX field declarations are complete.",
            "- Canonical corrections describe 17.3; consumers supporting older releases should preserve version-compatibility policy at their API boundary.",
            "- Runtime behavior, timing, and state-machine semantics remain outside schema matching.",
            "",
        ]
    )
    return "\n".join(lines)


def write_markdown(payload: dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(payload), encoding="utf-8")
