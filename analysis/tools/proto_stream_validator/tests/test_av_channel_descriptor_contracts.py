from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("google.protobuf")

from google.protobuf.descriptor import FieldDescriptor

from analysis.tools.proto_stream_validator.descriptors import (
    build_descriptor_bundle,
)

REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture(scope="module")
def descriptor_bundle(tmp_path_factory):
    return build_descriptor_bundle(
        repo_root=REPO_ROOT,
        out_dir=tmp_path_factory.mktemp("av-codec-descriptors"),
    )


@pytest.mark.parametrize(
    "message_name",
    [
        "oaa.proto.data.AVChannel",
        "oaa.proto.data.AVInputChannel",
    ],
    ids=["AVChannel", "AVInputChannel"],
)
def test_stream_type_uses_media_codec_enum(descriptor_bundle, message_name):
    message = descriptor_bundle.pool.FindMessageTypeByName(message_name)
    field = message.fields_by_number[1]

    assert field.type == FieldDescriptor.TYPE_ENUM
    assert field.enum_type.full_name == "oaa.proto.enums.MediaCodecType.Enum"
