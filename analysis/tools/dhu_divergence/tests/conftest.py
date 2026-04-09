from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis.tools.proto_stream_validator.descriptors import build_descriptor_bundle

# Repo root = .../open-android-auto
# parents: tests -> dhu_divergence -> tools -> analysis -> repo
REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def schema(repo_root: Path) -> dict:
    return json.loads((repo_root / "docs/verification/audit-schema.json").read_text())


@pytest.fixture(scope="session")
def descriptor_bundle(repo_root: Path, tmp_path_factory):
    """Session-scoped protobuf descriptor bundle for SDP decoding.

    Mirrors the call shape used by `analysis/tools/oem_vw_parser/tests/conftest.py`:
    `build_descriptor_bundle(repo_root=..., out_dir=...)`.
    """
    out_dir = tmp_path_factory.mktemp("dhu_divergence_bundle")
    return build_descriptor_bundle(repo_root=repo_root, out_dir=out_dir)
