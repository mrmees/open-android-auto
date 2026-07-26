from __future__ import annotations

from typing import Any

try:
    from google.protobuf import message_factory
except ModuleNotFoundError as exc:
    message_factory = None  # type: ignore[assignment]
    _PROTOBUF_IMPORT_ERROR = exc
else:
    _PROTOBUF_IMPORT_ERROR = None


def message_class_for_descriptor(descriptor: object) -> type[Any]:
    """Return the dynamic message class on modern and protobuf 4.21 runtimes."""
    if _PROTOBUF_IMPORT_ERROR is not None:
        raise RuntimeError(
            "python protobuf runtime is required (install package: protobuf)"
        ) from _PROTOBUF_IMPORT_ERROR

    get_message_class = getattr(message_factory, "GetMessageClass", None)
    if callable(get_message_class):
        return get_message_class(descriptor)

    factory = message_factory.MessageFactory()  # type: ignore[union-attr]
    return factory.GetPrototype(descriptor)
