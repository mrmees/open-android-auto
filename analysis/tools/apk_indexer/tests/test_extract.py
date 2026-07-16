import re

from analysis.tools.apk_indexer.extract import (
    _decode_field_references,
    _detect_proto_names,
    _extract_proto_enum_from_text,
    extract_signals,
)


def test_proto_enum_excludes_generated_unrecognized_sentinel(tmp_path):
    source = tmp_path / "xed.java"
    text = """
    public enum xed implements abnb {
        FIRST(0),
        SECOND(1),
        UNRECOGNIZED(-1);
    }
    """

    row = _extract_proto_enum_from_text(
        source,
        text,
        enum_interface_re=re.compile(r"implements\s+abnb"),
    )

    assert row is not None
    assert '"name": "UNRECOGNIZED"' not in row["values"]
    assert row["value_count"] == 2


def test_extract_uuid(tmp_path):
    sample = tmp_path / "A.java"
    sample.write_text('String u = "4de17a00-52cb-11e6-bdf4-0800200c9a66";\n')

    result = extract_signals(tmp_path)

    assert result["uuids"][0]["value"] == "4de17a00-52cb-11e6-bdf4-0800200c9a66"


def test_extract_constant_hex(tmp_path):
    sample = tmp_path / "B.java"
    sample.write_text("int channel = 0x1A2B;\n")

    result = extract_signals(tmp_path)

    assert result["constants"][0]["value"] == "0x1A2B"


def test_extract_proto_access_setter(tmp_path):
    sample = tmp_path / "C.java"
    sample.write_text("builder.setChannelId(3);\n")

    result = extract_signals(tmp_path)

    assert result["proto_accesses"][0]["accessor"] == "setChannelId"


def test_extract_call_edge_like_invocation(tmp_path):
    sample = tmp_path / "D.java"
    sample.write_text("transport.sendMessage(frame);\n")

    result = extract_signals(tmp_path)

    assert result["call_edges"][0]["target"] == "transport.sendMessage"


def test_extract_proto_write_patterns(tmp_path):
    sample = tmp_path / "E.java"
    sample.write_text(
        "xhqVar.b |= 16;\n"
        "xhqVar.g = i7;\n"
        "if (!o.b.H()) { o.t(); }\n"
        "defpackage.xhq xhqVar6 = (defpackage.xhq) o.q();\n"
    )

    result = extract_signals(tmp_path)

    ops = {(row["target"], row["op"]) for row in result["proto_writes"]}
    assert ("xhqVar.b", "|=") in ops
    assert ("xhqVar.g", "=") in ops


def test_extract_projection_scope_filters_non_projection(tmp_path):
    projection = tmp_path / "sources" / "com" / "google" / "android" / "projection" / "A.java"
    projection.parent.mkdir(parents=True)
    projection.write_text('String u = "4de17a00-52cb-11e6-bdf4-0800200c9a66";\n')

    non_projection = tmp_path / "sources" / "androidx" / "B.java"
    non_projection.parent.mkdir(parents=True)
    non_projection.write_text('String u = "669a0c20-0008-f4bd-e611-cb52007ae14d";\n')

    result = extract_signals(tmp_path, scope="projection")

    assert len(result["uuids"]) == 1
    assert result["uuids"][0]["value"] == "4de17a00-52cb-11e6-bdf4-0800200c9a66"


def test_extract_enum_maps(tmp_path):
    sample = tmp_path / "vyn.java"
    sample.write_text(
        "public enum vyn {\n"
        "  MEDIA_CODEC_AUDIO_PCM(1),\n"
        "  MEDIA_CODEC_AUDIO_AAC_LC(2);\n"
        "  public static vyn b(int i2) {\n"
        "    switch (i2) {\n"
        "      case 1:\n"
        "        return MEDIA_CODEC_AUDIO_PCM;\n"
        "      case 2:\n"
        "        return MEDIA_CODEC_AUDIO_AAC_LC;\n"
        "      default:\n"
        "        return null;\n"
        "    }\n"
        "  }\n"
        "}\n"
    )

    result = extract_signals(tmp_path)

    rows = {(r["enum_class"], r["int_value"], r["enum_name"]) for r in result["enum_maps"]}
    assert ("vyn", 1, "MEDIA_CODEC_AUDIO_PCM") in rows
    assert ("vyn", 2, "MEDIA_CODEC_AUDIO_AAC_LC") in rows


def test_extract_switch_maps(tmp_path):
    sample = tmp_path / "Dispatch.java"
    sample.write_text(
        "switch (messageId) {\n"
        "  case 7:\n"
        "    handler.handleAudio(msg);\n"
        "    break;\n"
        "  case 9:\n"
        "    return codec.select(h);\n"
        "  default:\n"
        "    return null;\n"
        "}\n"
    )

    result = extract_signals(tmp_path)

    rows = {(r["switch_expr"], r["case_value"], r["target"]) for r in result["switch_maps"]}
    assert ("messageId", "7", "handler.handleAudio") in rows
    assert ("messageId", "9", "codec.select") in rows


def test_detect_descriptor_by_raw_message_info_shape_not_total_new_count(tmp_path):
    obfuscated = tmp_path / "sources" / "defpackage"
    obfuscated.mkdir(parents=True)

    (obfuscated / "signals.java").write_text(
        "\n".join(
            ["final class Message extends abmx {}"] * 501
            + ['Object info = new aboi(a, "\\u0001\\u0000", null);'] * 501
            + ['Object helper = new yxw(1, "VALUE");'] * 600
            + ["enum Value implements abnb { VALUE }"] * 51
        )
    )

    assert _detect_proto_names(tmp_path) == (
        "defpackage",
        "abmx",
        "aboi",
        "abnb",
    )


def test_decode_raw_message_info_field_references():
    decoded = {
        "syntax": "proto2",
        "oneof_count": 0,
        "hasbits_count": 1,
        "fields": [
            {
                "field_number": 1,
                "type_id": 9,
                "base_type": "message",
                "is_oneof": False,
                "enum_closed": False,
            },
            {
                "field_number": 2,
                "type_id": 27,
                "base_type": "message",
                "is_oneof": False,
                "enum_closed": False,
            },
            {
                "field_number": 3,
                "type_id": 12,
                "base_type": "enum",
                "is_oneof": False,
                "enum_closed": True,
            },
        ],
    }

    references = _decode_field_references(
        decoded,
        ['"bitField0_"', '"child_"', '"children_"', "abc.class", '"state_"', "xyz.a"],
        [
            {"name": "child_", "type": "defpackage.abc"},
            {"name": "children_", "type": "abna"},
            {"name": "state_", "type": "int"},
        ],
    )

    assert [(item["field_number"], item["target_class"]) for item in references] == [
        (1, "abc"),
        (2, "abc"),
        (3, "xyz"),
    ]
