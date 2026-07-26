from __future__ import annotations

from typing import Any

try:
    from google.protobuf import json_format
    from google.protobuf import message
except ModuleNotFoundError as exc:  # pragma: no cover - exercised in dependency-limited envs
    json_format = None  # type: ignore[assignment]
    message = None  # type: ignore[assignment]
    _PROTOBUF_IMPORT_ERROR = exc
else:
    _PROTOBUF_IMPORT_ERROR = None

from analysis.tools.protobuf_compat import message_class_for_descriptor
from analysis.tools.proto_stream_validator.descriptors import DescriptorBundle


def _require_protobuf_runtime() -> None:
    if _PROTOBUF_IMPORT_ERROR is not None:
        raise RuntimeError(
            "python protobuf runtime is required (install package: protobuf)"
        ) from _PROTOBUF_IMPORT_ERROR


def decode_payload(
    bundle: DescriptorBundle,
    message_type: str,
    payload: bytes,
) -> dict[str, Any]:
    _require_protobuf_runtime()

    try:
        descriptor = bundle.pool.FindMessageTypeByName(message_type)
    except KeyError as exc:
        raise ValueError(f"unknown message type: {message_type}") from exc

    cls = message_class_for_descriptor(descriptor)
    msg = cls()

    try:
        msg.ParseFromString(payload)
    except message.DecodeError as exc:  # type: ignore[union-attr]
        raise ValueError(f"failed to decode {message_type}: {exc}") from exc

    return json_format.MessageToDict(  # type: ignore[union-attr]
        msg,
        preserving_proto_field_name=True,
    )
