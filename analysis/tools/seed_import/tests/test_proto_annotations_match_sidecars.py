"""Verify that active proto confidence comments match the canonical renderer."""

import re
from pathlib import Path

import pytest

from analysis.tools.seed_import.annotate import (
    load_audit_yaml,
    render_annotated_content,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
OAA_ROOT = REPO_ROOT / "oaa"


def _find_proto_files():
    """Find every active proto under oaa/."""
    if not OAA_ROOT.exists():
        return []
    return sorted(OAA_ROOT.rglob("*.proto"))


PROTO_FILES = _find_proto_files()


@pytest.mark.skipif(
    len(PROTO_FILES) == 0,
    reason="No active .proto files found under oaa/ — skipping annotation check",
)
@pytest.mark.parametrize(
    "proto_path",
    PROTO_FILES,
    ids=lambda p: str(p.relative_to(REPO_ROOT)),
)
def test_proto_annotation_confidence_matches_sidecar(proto_path: Path):
    """Each stored confidence mirror must equal the canonical rendered content."""
    content = proto_path.read_text(encoding="utf-8")
    expected, _ = render_annotated_content(
        content,
        load_audit_yaml(proto_path),
    )

    assert content == expected, (
        f"{proto_path.relative_to(REPO_ROOT)}: confidence comments drift from "
        "the canonical audit-sidecar rendering"
    )


def test_protos_without_sidecars_have_only_unverified_confidence_labels():
    """A proto without canonical audit evidence must not claim a higher tier."""
    unsupported = []
    for proto_path in PROTO_FILES:
        if proto_path.with_suffix(".audit.yaml").exists():
            continue
        content = proto_path.read_text(encoding="utf-8")
        for match in re.finditer(
            r"\bconfidence\s*:\s*([a-z][a-z_-]*)",
            content,
            flags=re.IGNORECASE,
        ):
            tier = match.group(1).lower()
            if tier != "unverified":
                line = content.count("\n", 0, match.start()) + 1
                unsupported.append(
                    f"{proto_path.relative_to(REPO_ROOT)}:{line}: {tier}"
                )

    assert unsupported == [], (
        "protos without audit sidecars may only use confidence: unverified; "
        "unsupported labels:\n" + "\n".join(unsupported)
    )
