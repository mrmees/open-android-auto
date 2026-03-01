"""Aggregate signals into triage results with confidence and service labels."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum

from analysis.tools.proto_triage.db import ProtoInfo
from analysis.tools.proto_triage.signals import (
    BFSResult,
    HubResult,
    PackageResult,
    StructuralResult,
)


class TriageCategory(Enum):
    WIRE_HIGH = "WIRE_HIGH"
    WIRE_MEDIUM = "WIRE_MEDIUM"
    WIRE_LOW = "WIRE_LOW"
    INTERNAL = "INTERNAL"
    UTILITY = "UTILITY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class TriageResult:
    class_name: str
    category: TriageCategory
    confidence: float
    service_label: str
    signals: list[str]  # Human-readable signal descriptions
    proto_syntax: str
    field_count: int
    sub_ref_count: int


def score_all(
    universe: dict[str, ProtoInfo],
    seeds: set[str],
    bfs: BFSResult,
    hub: HubResult,
    pkg: PackageResult,
    structural: StructuralResult,
    seed_service_map: dict[str, str],
    hub_result: HubResult,
    file_to_classes: dict[str, set[str]],
    telemetry_cluster: set[str] | None = None,
) -> list[TriageResult]:
    """Score all non-seed proto classes and return triage results."""
    telemetry = telemetry_cluster or set()
    results: list[TriageResult] = []

    for cls, info in universe.items():
        if cls in seeds:
            continue

        result = _score_one(
            cls, info, bfs, hub, pkg, structural,
            seed_service_map, file_to_classes, seeds,
            telemetry=telemetry,
        )
        results.append(result)

    # Sort: WIRE_HIGH first, then WIRE_MEDIUM, etc.
    category_order = {
        TriageCategory.WIRE_HIGH: 0,
        TriageCategory.WIRE_MEDIUM: 1,
        TriageCategory.WIRE_LOW: 2,
        TriageCategory.INTERNAL: 3,
        TriageCategory.UTILITY: 4,
        TriageCategory.UNKNOWN: 5,
    }
    results.sort(key=lambda r: (category_order[r.category], -r.confidence, r.class_name))
    return results


def _score_one(
    cls: str,
    info: ProtoInfo,
    bfs: BFSResult,
    hub: HubResult,
    pkg: PackageResult,
    structural: StructuralResult,
    seed_service_map: dict[str, str],
    file_to_classes: dict[str, set[str]],
    seeds: set[str],
    telemetry: set[str] | None = None,
) -> TriageResult:
    """Apply scoring rules to a single class."""
    signals: list[str] = []
    hop = bfs.hop_distance.get(cls)
    hub_count = hub.hub_file_count.get(cls, 0)
    pkg_class = pkg.classification.get(cls)
    features = structural.features.get(cls, set())

    has_wire_graph = hop is not None
    has_hub = hub_count > 0
    in_telemetry = telemetry is not None and cls in telemetry

    if in_telemetry:
        signals.append("telemetry_cluster")
    if hop is not None:
        signals.append(f"BFS hop {hop}")
    if hub_count > 0:
        signals.append(f"hub_files={hub_count}")
    if pkg_class:
        signals.append(f"pkg={pkg_class}")
    for f in sorted(features):
        signals.append(f"struct:{f}")

    # --- Priority scoring rules ---

    # Rule 1.5: Telemetry cluster — always INTERNAL regardless of other signals
    if in_telemetry:
        return TriageResult(
            class_name=cls,
            category=TriageCategory.INTERNAL,
            confidence=0.85,
            service_label="Telemetry",
            signals=signals,
            proto_syntax=info.proto_syntax,
            field_count=info.field_count,
            sub_ref_count=len(info.sub_message_refs),
        )

    # Rule 2: Internal dominant, no wire signals
    if pkg_class == "INTERNAL" and not has_wire_graph and not has_hub:
        return TriageResult(
            class_name=cls,
            category=TriageCategory.INTERNAL,
            confidence=0.75,
            service_label="Internal",
            signals=signals,
            proto_syntax=info.proto_syntax,
            field_count=info.field_count,
            sub_ref_count=len(info.sub_message_refs),
        )

    # Rule 3: Empty proto_syntax → UTILITY
    if "empty_syntax" in features:
        return TriageResult(
            class_name=cls,
            category=TriageCategory.UTILITY,
            confidence=0.7,
            service_label="Utility",
            signals=signals,
            proto_syntax=info.proto_syntax,
            field_count=info.field_count,
            sub_ref_count=len(info.sub_message_refs),
        )

    # Rule 4: BFS hop 1 OR hub_file_count >= 5
    if (hop is not None and hop <= 1) or hub_count >= 5:
        conf = 0.9 if (hop == 1 and hub_count >= 5) else 0.85 if hop == 1 else 0.8
        svc = _infer_service(cls, hub, file_to_classes, seeds, seed_service_map)
        return TriageResult(
            class_name=cls,
            category=TriageCategory.WIRE_HIGH,
            confidence=conf,
            service_label=svc,
            signals=signals,
            proto_syntax=info.proto_syntax,
            field_count=info.field_count,
            sub_ref_count=len(info.sub_message_refs),
        )

    # Rule 5: BFS hop 2 OR hub_file_count >= 2
    if (hop is not None and hop <= 2) or hub_count >= 2:
        conf = 0.75 if (hop == 2 and hub_count >= 2) else 0.7 if hop == 2 else 0.65
        svc = _infer_service(cls, hub, file_to_classes, seeds, seed_service_map)
        return TriageResult(
            class_name=cls,
            category=TriageCategory.WIRE_MEDIUM,
            confidence=conf,
            service_label=svc,
            signals=signals,
            proto_syntax=info.proto_syntax,
            field_count=info.field_count,
            sub_ref_count=len(info.sub_message_refs),
        )

    # Rule 6: BFS hop 3-5 OR hub_file_count == 1
    if (hop is not None and hop <= 5) or hub_count == 1:
        conf = 0.5 if hop is not None else 0.4
        svc = _infer_service(cls, hub, file_to_classes, seeds, seed_service_map)
        return TriageResult(
            class_name=cls,
            category=TriageCategory.WIRE_LOW,
            confidence=conf,
            service_label=svc,
            signals=signals,
            proto_syntax=info.proto_syntax,
            field_count=info.field_count,
            sub_ref_count=len(info.sub_message_refs),
        )

    # Rule 7: zero fields, no wire signals → UTILITY
    if "zero_fields" in features and not has_wire_graph and not has_hub:
        return TriageResult(
            class_name=cls,
            category=TriageCategory.UTILITY,
            confidence=0.6,
            service_label="Utility",
            signals=signals,
            proto_syntax=info.proto_syntax,
            field_count=info.field_count,
            sub_ref_count=len(info.sub_message_refs),
        )

    # Rule 8/9: UNKNOWN — proto2 higher priority than proto3
    conf = 0.3 if "proto2" in features else 0.2
    return TriageResult(
        class_name=cls,
        category=TriageCategory.UNKNOWN,
        confidence=conf,
        service_label="Unknown",
        signals=signals,
        proto_syntax=info.proto_syntax,
        field_count=info.field_count,
        sub_ref_count=len(info.sub_message_refs),
    )


def _infer_service(
    cls: str,
    hub: HubResult,
    file_to_classes: dict[str, set[str]],
    seeds: set[str],
    seed_service_map: dict[str, str],
) -> str:
    """Infer service label from hub file co-references with known seeds."""
    hub_files = hub.hub_files.get(cls, set())
    if not hub_files:
        # Fall back: check BFS neighbors via sub_message_refs
        return "Unknown"

    # Collect service labels from known seeds in the same hub files
    label_votes: Counter[str] = Counter()
    for hf in hub_files:
        file_classes = file_to_classes.get(hf, set())
        for co_class in file_classes:
            if co_class in seeds and co_class in seed_service_map:
                label_votes[seed_service_map[co_class]] += 1

    if not label_votes:
        return "Unknown"

    top = label_votes.most_common(2)
    if len(top) == 1 or top[0][1] > top[1][1]:
        return top[0][0]
    return "Mixed/Control"
