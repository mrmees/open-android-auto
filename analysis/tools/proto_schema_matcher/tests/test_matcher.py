from analysis.tools.proto_schema_matcher.matcher import match_enum_domains, match_graphs
from analysis.tools.proto_schema_matcher.models import (
    DispatchObservation,
    EnumNode,
    FieldShape,
    MessageNode,
)


def _node(name: str, *fields: FieldShape) -> MessageNode:
    return MessageNode(name=name, syntax="proto2", fields=tuple(fields))


def test_unique_structure_resolves_with_medium_confidence():
    shape = FieldShape(1, "int32", required=True)

    result = match_graphs(
        {"oaa.proto.messages.Request": _node("oaa.proto.messages.Request", shape)},
        {"abc": _node("abc", shape)},
    )[0]

    assert result.status == "unique_structural"
    assert result.confidence == "medium"
    assert result.resolved_apk_class == "abc"


def test_dispatch_resolves_structural_collision():
    shape = FieldShape(1, "int64")
    canonical_name = "oaa.proto.messages.PingRequest"

    result = match_graphs(
        {canonical_name: _node(canonical_name, shape)},
        {
            "aaa": _node("aaa", shape),
            "xkd": _node("xkd", shape),
        },
        [DispatchObservation(canonical_name, 11, "xkd", "Handler.java", 42)],
    )[0]

    assert result.status == "dispatch_resolved"
    assert result.confidence == "high"
    assert result.resolved_apk_class == "xkd"
    assert result.structural_candidate_count == 2


def test_canonical_aliases_are_not_treated_as_unique():
    shape = FieldShape(1, "string")

    results = match_graphs(
        {
            "oaa.proto.data.DeviceInfo": _node("oaa.proto.data.DeviceInfo", shape),
            "oaa.proto.data.HeadUnitInfo": _node("oaa.proto.data.HeadUnitInfo", shape),
        },
        {"xen": _node("xen", shape)},
    )

    assert {result.status for result in results} == {"ambiguous_structural"}
    assert {result.canonical_shape_count for result in results} == {2}
    assert all(result.resolved_apk_class is None for result in results)


def test_message_edge_constraint_resolves_parent_collision():
    child_name = "oaa.proto.data.Child"
    parent_name = "oaa.proto.messages.Parent"
    child_shape = FieldShape(1, "string")
    parent_shape = FieldShape(1, "message", target=child_name)

    results = match_graphs(
        {
            child_name: _node(child_name, child_shape),
            parent_name: _node(parent_name, parent_shape),
        },
        {
            "bbb": _node("bbb", child_shape),
            "p1": _node("p1", FieldShape(1, "message", target="bbb")),
            "p2": _node("p2", FieldShape(1, "message", target="ccc")),
        },
    )
    parent = next(result for result in results if result.canonical_name == parent_name)

    assert parent.status == "graph_resolved"
    assert parent.resolved_apk_class == "p1"
    assert parent.structural_candidate_count == 2
    assert parent.refined_candidate_count == 1


def test_dispatch_parent_resolves_child_collision_backwards():
    child_name = "oaa.proto.data.Child"
    parent_name = "oaa.proto.messages.Parent"

    results = match_graphs(
        {
            child_name: _node(child_name, FieldShape(1, "int32")),
            parent_name: _node(
                parent_name,
                FieldShape(1, "message", target=child_name),
            ),
        },
        {
            "child1": _node("child1", FieldShape(1, "int32")),
            "child2": _node("child2", FieldShape(1, "int32")),
            "parent": _node(
                "parent",
                FieldShape(1, "message", target="child2"),
            ),
        },
        [DispatchObservation(parent_name, 0x8001, "parent", "handler.java", 10)],
    )
    child = next(result for result in results if result.canonical_name == child_name)

    assert child.status == "graph_resolved"
    assert child.resolved_apk_class == "child2"


def test_dispatch_identity_survives_message_edge_conflict():
    child_name = "oaa.proto.data.Child"
    parent_name = "oaa.proto.messages.Parent"
    parent_shape = FieldShape(1, "message", target=child_name)

    results = match_graphs(
        {
            child_name: _node(child_name, FieldShape(1, "string")),
            parent_name: _node(parent_name, parent_shape),
        },
        {
            "bbb": _node("bbb", FieldShape(1, "string")),
            "parent": _node("parent", FieldShape(1, "message", target="wrong")),
        },
        [DispatchObservation(parent_name, 0x8003, "parent", "handler.java", 10)],
    )
    parent = next(result for result in results if result.canonical_name == parent_name)

    assert parent.status == "dispatch_resolved_edge_conflict"
    assert parent.confidence == "high"
    assert parent.resolved_apk_class == "parent"
    assert parent.edge_constraint_conflict is True


def test_incompatible_dispatch_observation_is_not_used():
    canonical_name = "oaa.proto.messages.PingRequest"

    result = match_graphs(
        {canonical_name: _node(canonical_name, FieldShape(1, "int64"))},
        {
            "aaa": _node("aaa", FieldShape(1, "int64")),
            "xkd": _node("xkd", FieldShape(1, "string")),
        },
        [DispatchObservation(canonical_name, 11, "xkd", "Handler.java", 42)],
    )[0]

    assert result.status == "unique_structural"
    assert result.resolved_apk_class == "aaa"
    assert result.dispatch_evidence == []


def test_enum_domain_edge_resolves_message_collision():
    first_name = "oaa.proto.messages.First"
    second_name = "oaa.proto.messages.Second"
    first_enum = "oaa.proto.enums.First.Enum"
    second_enum = "oaa.proto.enums.Second.Enum"

    results = match_graphs(
        {
            first_name: _node(first_name, FieldShape(1, "enum", target=first_enum)),
            second_name: _node(
                second_name,
                FieldShape(1, "enum", target=second_enum),
            ),
        },
        {
            "p1": _node("p1", FieldShape(1, "enum", target="e1")),
            "p2": _node("p2", FieldShape(1, "enum", target="e2")),
        },
        canonical_enums={
            first_enum: EnumNode(first_enum, (0, 1, 2)),
            second_enum: EnumNode(second_enum, (0, 10, 20)),
        },
        apk_enums={
            "e1": EnumNode("e1", (0, 1, 2)),
            "e2": EnumNode("e2", (0, 10, 20)),
        },
    )

    assert [(result.status, result.resolved_apk_class) for result in results] == [
        ("graph_resolved", "p1"),
        ("graph_resolved", "p2"),
    ]


def test_enum_domain_allows_canonical_proto3_zero_sentinel():
    matches = match_enum_domains(
        {"FocusMode": EnumNode("FocusMode", (0, 1, 2, 3, 4))},
        {"xna": EnumNode("xna", (1, 2, 3, 4))},
    )

    assert matches == {"FocusMode": ["xna"]}


def test_unknown_enum_target_is_not_promoted_after_other_candidate_conflicts():
    name = "oaa.proto.messages.Response"
    enum_name = "oaa.proto.enums.Status.Enum"

    result = match_graphs(
        {name: _node(name, FieldShape(1, "enum", target=enum_name))},
        {
            "known_wrong": _node(
                "known_wrong",
                FieldShape(1, "enum", target="wrong_enum"),
            ),
            "unknown": _node("unknown", FieldShape(1, "enum", target="verifier")),
        },
        canonical_enums={enum_name: EnumNode(enum_name, (0, 1, 2))},
        apk_enums={"wrong_enum": EnumNode("wrong_enum", (0, 10, 20))},
    )[0]

    assert result.status == "ambiguous_structural"
    assert result.resolved_apk_class is None
