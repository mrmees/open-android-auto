from analysis.tools.proto_schema_matcher.models import FieldShape, MessageNode
from analysis.tools.proto_schema_matcher.report import describe_schema_difference


def _node(name: str, *fields: FieldShape) -> MessageNode:
    return MessageNode(name=name, syntax="proto2", fields=tuple(fields))


def test_schema_difference_reports_modifier_and_field_set_changes():
    difference = describe_schema_difference(
        _node(
            "canonical",
            FieldShape(1, "uint64"),
            FieldShape(2, "string"),
        ),
        _node(
            "apk",
            FieldShape(1, "uint64", required=True),
            FieldShape(3, "bytes"),
        ),
    )

    assert difference["changed_fields"] == [
        {
            "number": 1,
            "changes": {"required": {"canonical": False, "apk": True}},
        }
    ]
    assert difference["missing_fields"][0]["number"] == 2
    assert difference["extra_fields"][0]["number"] == 3
