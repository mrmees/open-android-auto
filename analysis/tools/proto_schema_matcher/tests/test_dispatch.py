from analysis.tools.proto_schema_matcher.dispatch import (
    extract_canonical_name_logs,
    extract_control_dispatch,
    extract_named_dispatch,
    extract_service_dispatch,
)


def test_extract_control_dispatch_observation(tmp_path):
    sources = tmp_path / "sources" / "defpackage"
    sources.mkdir(parents=True)
    (sources / "handler.java").write_text(
        "void receive(int i) {\n"
        "  if (i == 11) {\n"
        "    xkd xkdVar = xkd.a;\n"
        "  }\n"
        "}\n"
    )

    observations = extract_control_dispatch(tmp_path, {"xkd"})

    assert len(observations) == 1
    assert observations[0].canonical_name == "oaa.proto.messages.PingRequest"
    assert observations[0].message_id == 11
    assert observations[0].apk_class == "xkd"
    assert observations[0].source == "defpackage/handler.java"
    assert observations[0].line == 3
    assert observations[0].service_type == "control"


def test_extract_control_dispatch_ignores_non_proto_default_instance(tmp_path):
    sources = tmp_path / "sources" / "defpackage"
    sources.mkdir(parents=True)
    (sources / "handler.java").write_text(
        "switch (i) {\n"
        "  case 12:\n"
        "    helper helperVar = helper.a;\n"
        "}\n"
    )

    assert extract_control_dispatch(tmp_path, {"xke"}) == []


def test_extract_explicit_sensor_service_dispatch(tmp_path):
    sources = tmp_path / "sources" / "defpackage"
    sources.mkdir(parents=True)
    (sources / "sensor_handler.java").write_text(
        "String service = rpq.SENSOR_SOURCE.name();\n"
        "switch (messageId) {\n"
        "  case 32771:\n"
        "    xln xlnVar = xln.a;\n"
        "}\n"
    )

    observations = extract_service_dispatch(tmp_path, {"xln"})

    assert len(observations) == 1
    assert observations[0].canonical_name == "oaa.proto.messages.SensorEventIndication"
    assert observations[0].message_id == 0x8003
    assert observations[0].apk_class == "xln"
    assert observations[0].service_type == "sensor_source"


def test_extracts_numeric_superclass_service_context(tmp_path):
    sources = tmp_path / "sources" / "defpackage"
    sources.mkdir(parents=True)
    (sources / "bluetooth_handler.java").write_text(
        "class Handler extends Endpoint {\n"
        "  Handler() { super(9, callback, transport, 0); }\n"
        "  void receive(int messageId) {\n"
        "    if (messageId == 32770) {\n"
        "      xfn xfnVar = xfn.a;\n"
        "    }\n"
        "  }\n"
        "}\n"
    )

    observations = extract_service_dispatch(tmp_path, {"xfn"})

    assert len(observations) == 1
    assert observations[0].canonical_name.endswith(".BluetoothPairingResponse")
    assert observations[0].service_type == "bluetooth"


def test_nested_inequality_guards_do_not_cross_assign_classes(tmp_path):
    sources = tmp_path / "sources" / "defpackage"
    sources.mkdir(parents=True)
    (sources / "navigation_handler.java").write_text(
        "class Handler extends Endpoint {\n"
        "  Handler() { super(10, callback, transport); }\n"
        "  void receive(int messageId) {\n"
        "    if (messageId != 32769) {\n"
        "      if (messageId != 32770) { throw fail(); }\n"
        "      xjm xjmVar = xjm.a;\n"
        "      return;\n"
        "    }\n"
        "    xjl xjlVar = xjl.a;\n"
        "  }\n"
        "}\n"
    )

    observations = extract_service_dispatch(tmp_path, {"xjl", "xjm"})

    assert [(item.message_id, item.apk_class) for item in observations] == [
        (0x8001, "xjl"),
        (0x8002, "xjm"),
    ]


def test_service_dispatch_skips_files_with_mixed_context(tmp_path):
    sources = tmp_path / "sources" / "defpackage"
    sources.mkdir(parents=True)
    (sources / "mixed.java").write_text(
        "Object a = rpq.SENSOR_SOURCE;\n"
        "Object b = rpq.INPUT_SOURCE;\n"
        "if (messageId == 32771) {\n"
        "  xln xlnVar = xln.a;\n"
        "}\n"
    )

    assert extract_service_dispatch(tmp_path, {"xln"}) == []


def test_extract_message_identity_from_validation_log(tmp_path):
    sources = tmp_path / "sources" / "defpackage"
    sources.mkdir(parents=True)
    (sources / "bluetooth.java").write_text(
        "if (messageId == 32770) {\n"
        "  xfn xfnVar = xfn.a;\n"
        "  parse(xfnVar);\n"
        '  log("Wrong BluetoothPairingResponse message");\n'
        "}\n"
    )

    observations = extract_named_dispatch(tmp_path, {"xfn"})

    assert len(observations) == 1
    assert observations[0].canonical_name == (
        "oaa.proto.messages.BluetoothPairingResponse"
    )
    assert observations[0].message_id == 0x8002
    assert observations[0].apk_class == "xfn"
    assert observations[0].service_type == "named_log"


def test_extract_case_id_for_named_validation_log(tmp_path):
    sources = tmp_path / "sources" / "defpackage"
    sources.mkdir(parents=True)
    (sources / "pairing.java").write_text(
        "switch (messageId) {\n"
        "  case 0x8002:\n"
        "    xfn xfnVar = xfn.a;\n"
        '    log("Wrong BluetoothPairingResponse message");\n'
        "    break;\n"
        "}\n"
    )

    observations = extract_named_dispatch(tmp_path, {"xfn"})

    assert len(observations) == 1
    assert observations[0].message_id == 0x8002


def test_extracts_canonical_send_log_with_known_alias(tmp_path):
    sources = tmp_path / "sources" / "defpackage"
    sources.mkdir(parents=True)
    (sources / "bluetooth_sender.java").write_text(
        'log("sendAuthenticationResult: result=%s");\n'
        "abmr builder = xfk.a.o();\n"
        "channel.send(32772, builder.q());\n"
    )

    observations = extract_canonical_name_logs(
        tmp_path,
        {"xfk"},
        {"oaa.proto.messages.BluetoothAuthenticationResult"},
    )

    assert len(observations) == 1
    assert observations[0].canonical_name.endswith(".BluetoothAuthenticationResult")
    assert observations[0].apk_class == "xfk"
    assert observations[0].message_id == 0x8004
    assert observations[0].service_type == "canonical_log"
