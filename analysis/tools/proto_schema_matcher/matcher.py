from __future__ import annotations

from collections import defaultdict

from .models import (
    DispatchObservation,
    EnumNode,
    LineageAnchor,
    MatchResult,
    MessageNode,
)


def match_enum_domains(
    canonical_enums: dict[str, EnumNode],
    apk_enums: dict[str, EnumNode],
) -> dict[str, list[str]]:
    """Return compatible numeric-domain candidates for each canonical enum.

    Canonical proto3 wrappers sometimes add a zero sentinel that is absent from
    the generated APK enum. That documented representation difference is the
    only non-exact domain relation accepted here.
    """

    def compatible(canonical: EnumNode, apk: EnumNode) -> bool:
        canonical_values = set(canonical.values)
        apk_values = set(apk.values)
        return apk_values == canonical_values or (
            0 in canonical_values and apk_values == canonical_values - {0}
        )

    return {
        canonical_name: sorted(
            apk_name
            for apk_name, apk_node in apk_enums.items()
            if compatible(node, apk_node)
        )
        for canonical_name, node in canonical_enums.items()
    }


def match_graphs(
    canonical_graph: dict[str, MessageNode],
    apk_graph: dict[str, MessageNode],
    dispatch_observations: list[DispatchObservation] | None = None,
    canonical_enums: dict[str, EnumNode] | None = None,
    apk_enums: dict[str, EnumNode] | None = None,
    lineage_anchors: list[LineageAnchor] | None = None,
) -> list[MatchResult]:
    """Match canonical messages to APK classes with auditable constraints."""
    apk_by_shape: dict[tuple[object, ...], list[str]] = defaultdict(list)
    for apk_class, node in apk_graph.items():
        apk_by_shape[node.structural_key()].append(apk_class)

    canonical_by_shape: dict[tuple[object, ...], list[str]] = defaultdict(list)
    for canonical_name, node in canonical_graph.items():
        canonical_by_shape[node.structural_key()].append(canonical_name)

    dispatch_by_canonical: dict[str, list[DispatchObservation]] = defaultdict(list)
    for observation in dispatch_observations or []:
        dispatch_by_canonical[observation.canonical_name].append(observation)

    anchor_by_canonical: dict[str, LineageAnchor] = {}
    for anchor in lineage_anchors or []:
        if anchor.canonical_name not in canonical_graph:
            raise ValueError(
                f"lineage anchor names unknown canonical message {anchor.canonical_name}"
            )
        if anchor.current_class not in apk_graph:
            raise ValueError(
                f"lineage anchor for {anchor.canonical_name} names unknown APK class "
                f"{anchor.current_class}"
            )
        unknown_rejections = set(anchor.rejected_candidates) - set(apk_graph)
        if unknown_rejections:
            raise ValueError(
                f"lineage anchor for {anchor.canonical_name} rejects unknown APK "
                f"classes {sorted(unknown_rejections)}"
            )
        if anchor.canonical_name in anchor_by_canonical:
            raise ValueError(f"duplicate lineage anchor for {anchor.canonical_name}")
        anchor_by_canonical[anchor.canonical_name] = anchor

    enum_candidate_sets = match_enum_domains(
        canonical_enums or {},
        apk_enums or {},
    )

    initial_candidates = {
        canonical_name: set(apk_by_shape.get(node.structural_key(), []))
        for canonical_name, node in canonical_graph.items()
    }
    candidate_sets = {
        canonical_name: set(candidates)
        for canonical_name, candidates in initial_candidates.items()
    }
    confirmed_anchors = {
        name: anchor.current_class
        for name, anchor in anchor_by_canonical.items()
        if anchor.disposition == "confirmed"
    }
    invalidated_names = {
        name
        for name, anchor in anchor_by_canonical.items()
        if anchor.disposition == "invalidated"
    }
    for canonical_name, apk_class in confirmed_anchors.items():
        candidate_sets[canonical_name] = {apk_class}
    for canonical_name in invalidated_names:
        # An invalidated anchor means that the canonical schema itself came
        # from an unrelated bundled-library protobuf. No same-shape class is
        # eligible for protocol naming until independent protocol evidence
        # reconstructs the message.
        candidate_sets[canonical_name] = set()

    # Dispatch is a hard constraint only when all structurally compatible
    # observations agree on one APK class.
    dispatch_anchors: dict[str, str] = {}
    for canonical_name, evidence in dispatch_by_canonical.items():
        if canonical_name in anchor_by_canonical:
            continue
        compatible = {
            item.apk_class
            for item in evidence
            if item.apk_class in candidate_sets.get(canonical_name, set())
        }
        if len(compatible) == 1:
            candidate_sets[canonical_name] = compatible
            dispatch_anchors[canonical_name] = next(iter(compatible))

    trusted_parent_names = set(dispatch_anchors) | set(confirmed_anchors)
    trusted_parent_names.update(
        canonical_name
        for canonical_name, candidates in initial_candidates.items()
        if canonical_name not in invalidated_names
        if len(candidates) == 1
        and len(
            canonical_by_shape[
                canonical_graph[canonical_name].structural_key()
            ]
        )
        == 1
    )

    def candidate_edges_are_compatible(
        canonical_name: str,
        apk_class: str,
    ) -> bool:
        canonical_node = canonical_graph[canonical_name]
        apk_node = apk_graph[apk_class]
        apk_fields = {field.number: field for field in apk_node.fields}
        for canonical_field in canonical_node.fields:
            target_name = canonical_field.target
            apk_field = apk_fields.get(canonical_field.number)
            if (
                canonical_field.base_type == "enum"
                and target_name
                and target_name in enum_candidate_sets
            ):
                target_candidates = enum_candidate_sets[target_name]
                if (
                    target_candidates
                    and apk_field is not None
                    and apk_field.target in (apk_enums or {})
                    and apk_field.target not in target_candidates
                ):
                    return False
                continue
            if (
                canonical_field.base_type not in {"message", "group"}
                or not target_name
                or target_name not in candidate_sets
            ):
                continue
            target_candidates = candidate_sets[target_name]
            if (
                target_candidates
                and apk_field is not None
                and apk_field.target is not None
                and apk_field.target not in target_candidates
            ):
                return False
        return True

    def candidate_has_confirmed_edge(
        canonical_name: str,
        apk_class: str,
    ) -> bool:
        apk_fields = {field.number: field for field in apk_graph[apk_class].fields}
        for canonical_field in canonical_graph[canonical_name].fields:
            target_name = canonical_field.target
            apk_field = apk_fields.get(canonical_field.number)
            if apk_field is None or apk_field.target is None or not target_name:
                continue
            if canonical_field.base_type in {"message", "group"}:
                target_candidates = candidate_sets.get(target_name, set())
                if target_candidates and apk_field.target in target_candidates:
                    return True
            elif canonical_field.base_type == "enum":
                target_candidates = enum_candidate_sets.get(target_name, [])
                if (
                    apk_field.target in (apk_enums or {})
                    and apk_field.target in target_candidates
                ):
                    return True
        return False

    # Constraint propagation over field-number-labelled message edges.
    # Unknown APK targets are deliberately skipped instead of treated as a
    # mismatch, keeping partial decompiles conservative.
    changed = True
    backward_resolved: set[str] = set()
    while changed:
        changed = False
        # A trusted parent also constrains its children: once the parent class
        # is known, a field-number-linked APK child is direct identity evidence.
        for canonical_name in tuple(trusted_parent_names):
            parent_candidates = candidate_sets[canonical_name]
            if len(parent_candidates) != 1:
                continue
            apk_parent = apk_graph[next(iter(parent_candidates))]
            apk_fields = {field.number: field for field in apk_parent.fields}
            for canonical_field in canonical_graph[canonical_name].fields:
                target_name = canonical_field.target
                if (
                    canonical_field.base_type not in {"message", "group"}
                    or not target_name
                    or target_name not in candidate_sets
                    or target_name in dispatch_anchors
                ):
                    continue
                apk_field = apk_fields.get(canonical_field.number)
                if (
                    apk_field is None
                    or apk_field.target is None
                    or apk_field.target not in candidate_sets[target_name]
                ):
                    continue
                narrowed = {apk_field.target}
                if candidate_sets[target_name] != narrowed:
                    candidate_sets[target_name] = narrowed
                    backward_resolved.add(target_name)
                    trusted_parent_names.add(target_name)
                    changed = True
        for canonical_name in canonical_graph:
            current = candidate_sets[canonical_name]
            if not current:
                continue
            if (
                canonical_name in dispatch_anchors
                or canonical_name in confirmed_anchors
            ):
                # Preserve a structurally compatible, unambiguous dispatch
                # identity. Any edge disagreement is reported separately.
                continue
            retained: set[str] = set()
            for apk_class in current:
                if candidate_edges_are_compatible(canonical_name, apk_class):
                    retained.add(apk_class)
            if retained != current:
                candidate_sets[canonical_name] = retained
                changed = True

    results: list[MatchResult] = []
    for canonical_name, node in sorted(canonical_graph.items()):
        structural_candidates = sorted(initial_candidates[canonical_name])
        candidates = sorted(candidate_sets[canonical_name])
        canonical_shape_count = len(canonical_by_shape[node.structural_key()])
        evidence = dispatch_by_canonical.get(canonical_name, [])
        lineage_anchor = anchor_by_canonical.get(canonical_name)
        dispatch_candidates = sorted(
            {
                item.apk_class
                for item in evidence
                if item.apk_class in initial_candidates[canonical_name]
            }
        )
        hard_anchor_class = dispatch_anchors.get(canonical_name) or confirmed_anchors.get(
            canonical_name
        )
        edge_constraint_conflict = (
            hard_anchor_class is not None
            and not candidate_edges_are_compatible(
                canonical_name,
                hard_anchor_class,
            )
        )

        if canonical_name in invalidated_names:
            status = "lineage_invalidated"
            confidence = "none"
            resolved = None
        elif canonical_name in confirmed_anchors:
            resolved = confirmed_anchors[canonical_name]
            if resolved not in initial_candidates[canonical_name]:
                status = "lineage_resolved_schema_conflict"
            elif edge_constraint_conflict:
                status = "lineage_resolved_edge_conflict"
            else:
                status = "lineage_resolved"
            confidence = "high"
        elif not structural_candidates:
            status = "not_found"
            confidence = "none"
            resolved = None
        elif not candidates:
            status = "constraint_conflict"
            confidence = "none"
            resolved = None
        elif len(dispatch_candidates) == 1:
            resolved = dispatch_candidates[0]
            if edge_constraint_conflict:
                status = "dispatch_resolved_edge_conflict"
            else:
                status = (
                    "unique_structural_dispatch_confirmed"
                    if len(structural_candidates) == 1
                    else "dispatch_resolved"
                )
            confidence = "high"
        elif (
            len(candidates) == 1
            and len(structural_candidates) == 1
            and canonical_shape_count == 1
        ):
            resolved = candidates[0]
            status = "unique_structural"
            confidence = "medium"
        elif (
            len(candidates) == 1
            and len(structural_candidates) > 1
            and (
                canonical_name in backward_resolved
                or candidate_has_confirmed_edge(canonical_name, candidates[0])
            )
        ):
            resolved = candidates[0]
            status = "graph_resolved"
            confidence = "medium"
        else:
            resolved = None
            status = "ambiguous_structural"
            confidence = "none"

        results.append(
            MatchResult(
                canonical_name=canonical_name,
                source=node.source,
                field_count=len(node.fields),
                status=status,
                confidence=confidence,
                candidates=candidates,
                structural_candidates=structural_candidates,
                structural_candidate_count=len(structural_candidates),
                refined_candidate_count=len(candidates),
                canonical_shape_count=canonical_shape_count,
                resolved_apk_class=resolved,
                edge_constraint_conflict=edge_constraint_conflict,
                dispatch_evidence=[
                    item
                    for item in evidence
                    if item.apk_class in initial_candidates[canonical_name]
                ],
                lineage_anchor=lineage_anchor,
            )
        )
    return results
