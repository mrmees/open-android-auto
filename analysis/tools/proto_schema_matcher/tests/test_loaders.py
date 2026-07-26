import json

from analysis.tools.proto_schema_matcher.loaders import (
    _load_verifier_enum_targets,
    load_apk_graph,
)


def test_load_apk_graph_from_index_json(tmp_path):
    source = tmp_path / "proto_classes.json"
    source.write_text(
        json.dumps(
            [
                {
                    "class_name": "xkd",
                    "proto_syntax": "proto2",
                    "file": "defpackage/xkd.java",
                    "decoded_fields": json.dumps(
                        [
                            {
                                "field_number": 1,
                                "base_type": "int64",
                                "is_repeated": False,
                                "is_packed": False,
                                "is_oneof": False,
                                "is_map": False,
                                "required": False,
                            }
                        ]
                    ),
                }
            ]
        )
    )

    graph = load_apk_graph(proto_classes_json=source)

    assert set(graph) == {"xkd"}
    assert graph["xkd"].fields[0].structural_key() == (
        1,
        "int64",
        False,
        False,
        False,
        False,
        False,
    )


def test_resolves_multiplexed_enum_verifier_member(tmp_path):
    source = tmp_path / "sources" / "defpackage" / "xjj.java"
    source.parent.mkdir(parents=True)
    source.write_text(
        """
        final class xjj {
          static final abnd c = new xjj(2);
          boolean a(int i) {
            switch (this.kind) {
              case 2:
                return xlu.b(i) != null;
              default:
                return false;
            }
          }
        }
        """
    )

    targets = _load_verifier_enum_targets(tmp_path, {"xlu"})

    assert targets == {"xjj.c": "xlu"}
