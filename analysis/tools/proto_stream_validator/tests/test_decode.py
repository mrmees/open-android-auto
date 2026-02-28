from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("google.protobuf")

from analysis.tools.proto_stream_validator.decode import decode_payload  # type: ignore[attr-defined]
from analysis.tools.proto_stream_validator.descriptors import (  # type: ignore[attr-defined]
    build_descriptor_bundle,
)


def test_build_descriptor_bundle_writes_descriptor_set(tmp_path):
    bundle = build_descriptor_bundle(repo_root=Path.cwd(), out_dir=tmp_path)
    assert bundle.descriptor_set_path.exists()


def test_decode_payload_ping_request(tmp_path):
    bundle = build_descriptor_bundle(repo_root=Path.cwd(), out_dir=tmp_path)

    decoded = decode_payload(
        bundle,
        "oaa.proto.messages.PingRequest",
        bytes.fromhex("0801"),
    )

    assert decoded == {"timestamp": "1"}


def test_decode_payload_rejects_malformed_wire_bytes(tmp_path):
    bundle = build_descriptor_bundle(repo_root=Path.cwd(), out_dir=tmp_path)

    with pytest.raises(ValueError):
        decode_payload(bundle, "oaa.proto.messages.PingRequest", bytes.fromhex("08"))
