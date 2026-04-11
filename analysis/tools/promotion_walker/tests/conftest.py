from __future__ import annotations
import json
import shutil
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def schema() -> dict:
    return json.loads((REPO_ROOT / "docs/verification/audit-schema.json").read_text())


@pytest.fixture
def mock_coverage() -> dict:
    return json.loads((FIXTURES / "mock_coverage.json").read_text())


@pytest.fixture
def mock_sdp() -> dict:
    return json.loads((FIXTURES / "mock_sdp_values.json").read_text())


@pytest.fixture
def mock_messages_jsonl() -> Path:
    return FIXTURES / "mock_messages.jsonl"


@pytest.fixture
def temp_oaa_tree(tmp_path: Path) -> Path:
    """Copy the 8 fixture sidecars into a tmpdir structure mirroring oaa/{media,video,audio,av}/."""
    tree = tmp_path / "oaa"
    for subdir in ("av", "media", "video", "audio"):
        (tree / subdir).mkdir(parents=True)
    for name in (
        "sidecar_gold_clean.audit.yaml",
        "sidecar_gold_no_cv.audit.yaml",
        "sidecar_silver_clean.audit.yaml",
        "sidecar_bronze_clean.audit.yaml",
        "sidecar_retracted.audit.yaml",
        "sidecar_already_platinum.audit.yaml",
        "sidecar_schema_invalid_corrections.audit.yaml",
        "sidecar_out_of_sdp_scope.audit.yaml",
    ):
        src = FIXTURES / name
        if src.exists():
            shutil.copy(src, tree / "media" / name)
    return tree
