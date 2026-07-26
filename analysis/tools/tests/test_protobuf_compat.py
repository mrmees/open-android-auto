from types import SimpleNamespace

from analysis.tools import protobuf_compat


def test_message_class_uses_modern_module_api(monkeypatch):
    descriptor = object()
    expected = type("ModernMessage", (), {})
    fake_module = SimpleNamespace(GetMessageClass=lambda value: expected if value is descriptor else None)
    monkeypatch.setattr(protobuf_compat, "message_factory", fake_module)
    monkeypatch.setattr(protobuf_compat, "_PROTOBUF_IMPORT_ERROR", None)

    assert protobuf_compat.message_class_for_descriptor(descriptor) is expected


def test_message_class_falls_back_to_legacy_factory(monkeypatch):
    descriptor = object()
    expected = type("LegacyMessage", (), {})

    class LegacyFactory:
        def GetPrototype(self, value):
            assert value is descriptor
            return expected

    fake_module = SimpleNamespace(MessageFactory=LegacyFactory)
    monkeypatch.setattr(protobuf_compat, "message_factory", fake_module)
    monkeypatch.setattr(protobuf_compat, "_PROTOBUF_IMPORT_ERROR", None)

    assert protobuf_compat.message_class_for_descriptor(descriptor) is expected
