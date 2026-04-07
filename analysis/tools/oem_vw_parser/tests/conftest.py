from __future__ import annotations

from pathlib import Path

import pytest

from analysis.tools.proto_stream_validator.descriptors import build_descriptor_bundle

FIXTURES = Path(__file__).parent / "fixtures"

# Repo root = .../open-android-auto (parents: tests -> oem_vw_parser -> tools -> analysis -> repo)
REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture(scope="session")
def bundle(tmp_path_factory):
    """Build the oaa/ descriptor bundle once per test session.

    Mirrors the call shape used by analysis/tools/proto_stream_validator/tests/test_decode.py:
    build_descriptor_bundle(repo_root=..., out_dir=...).
    """
    out_dir = tmp_path_factory.mktemp("oem_vw_parser_bundle")
    return build_descriptor_bundle(repo_root=REPO_ROOT, out_dir=out_dir)


@pytest.fixture
def vw_micro_path() -> Path:
    return FIXTURES / "vw_micro.jsonl"


@pytest.fixture
def dhu_micro_path() -> Path:
    return FIXTURES / "dhu_micro.jsonl"


@pytest.fixture
def dhu_channel_map_path() -> Path:
    """Real channel_map.json copied from captures/general/ during fixture setup.

    Used by tests that exercise the explicit-channel-map path of load_dhu_capture.
    """
    return FIXTURES / "dhu_channel_map.json"


@pytest.fixture
def sdp_request_path() -> Path:
    return FIXTURES / "sdp_request_vw.bin"


@pytest.fixture
def sdp_response_path() -> Path:
    return FIXTURES / "sdp_response_vw.bin"


@pytest.fixture
def padded_ping_hex() -> str:
    return (FIXTURES / "padded_ping.hex").read_text().strip()


@pytest.fixture
def histogram_snapshot_path() -> Path:
    return FIXTURES / "histogram_snapshot.json"
