from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class FieldShape:
    number: int
    base_type: str
    repeated: bool = False
    packed: bool = False
    oneof: bool = False
    map: bool = False
    required: bool = False
    target: str | None = field(default=None, compare=False)

    def structural_key(self) -> tuple[object, ...]:
        return (
            self.number,
            self.base_type,
            self.repeated,
            self.packed,
            self.oneof,
            self.map,
            self.required,
        )


@dataclass(frozen=True)
class MessageNode:
    name: str
    syntax: str
    fields: tuple[FieldShape, ...]
    source: str = ""

    def structural_key(self) -> tuple[object, ...]:
        return (self.syntax, tuple(field.structural_key() for field in self.fields))


@dataclass(frozen=True)
class EnumNode:
    name: str
    values: tuple[int, ...]
    source: str = ""

    def structural_key(self) -> tuple[int, ...]:
        return tuple(sorted(set(self.values)))


@dataclass(frozen=True)
class DispatchObservation:
    canonical_name: str
    message_id: int
    apk_class: str
    source: str
    line: int
    service_type: str = "control"


@dataclass(frozen=True, order=True)
class GraphEvidence:
    canonical_parent: str
    apk_parent: str
    field_number: int
    canonical_target: str
    apk_target: str
    relation: str


@dataclass(frozen=True)
class LineageStep:
    version: str
    apk_class: str


@dataclass(frozen=True)
class LineageAnchor:
    canonical_name: str
    current_class: str
    disposition: str
    lineage: tuple[LineageStep, ...]
    rejected_candidates: tuple[str, ...]
    rationale: str
    evidence: tuple[str, ...]
    source: str


@dataclass
class MatchResult:
    canonical_name: str
    source: str
    field_count: int
    status: str
    confidence: str
    candidates: list[str]
    structural_candidates: list[str]
    structural_candidate_count: int
    refined_candidate_count: int
    canonical_shape_count: int
    resolved_apk_class: str | None = None
    edge_constraint_conflict: bool = False
    dispatch_evidence: list[DispatchObservation] = field(default_factory=list)
    graph_evidence: list[GraphEvidence] = field(default_factory=list)
    lineage_anchor: LineageAnchor | None = None
