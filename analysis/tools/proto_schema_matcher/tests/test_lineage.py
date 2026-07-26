from pathlib import Path

import pytest

from analysis.tools.proto_schema_matcher.lineage import load_lineage_anchors


def test_load_lineage_anchor(tmp_path: Path):
    path = tmp_path / "lineage.yaml"
    path.write_text(
        """
anchors:
  - canonical_name: oaa.proto.data.Example
    disposition: invalidated
    current_class: xyz
    lineage:
      - {version: '16.2', apk_class: abc}
      - {version: '17.3', apk_class: xyz}
    rejected_candidates: [xyz]
    rationale: Unrelated library message.
    evidence: [Call site names the library.]
""".lstrip(),
        encoding="utf-8",
    )

    anchor = load_lineage_anchors(path)[0]

    assert anchor.canonical_name == "oaa.proto.data.Example"
    assert anchor.current_class == "xyz"
    assert anchor.lineage[-1].version == "17.3"
    assert anchor.rejected_candidates == ("xyz",)


def test_lineage_current_class_must_match_last_step(tmp_path: Path):
    path = tmp_path / "lineage.yaml"
    path.write_text(
        """
anchors:
  - canonical_name: oaa.proto.data.Example
    disposition: confirmed
    current_class: xyz
    lineage:
      - {version: '16.2', apk_class: abc}
      - {version: '17.3', apk_class: wrong}
    rationale: Exact call site.
    evidence: [Call site.]
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="last lineage step"):
        load_lineage_anchors(path)
