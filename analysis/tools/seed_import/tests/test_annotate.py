from pathlib import Path

from analysis.tools.seed_import import annotate


PROTO = '''syntax = "proto2";
package fixture;

// confidence: gold [stale]
message Example {
  optional string value = 1; // semantic note  // confidence: gold [stale]
}
'''

AUDIT = {
    "confidence": "bronze",
    "evidence": [{"type": "apk_static"}],
}


def test_render_uses_sidecar_tier_and_evidence_for_declaration():
    """Catches a renderer that ignores the supplied audit tier or evidence."""
    rendered, stats = annotate.render_annotated_content(PROTO, AUDIT)

    assert "// confidence: bronze [apk_static]\nmessage Example" in rendered
    assert stats == {"messages": 1, "fields": 1, "enums": 0}


def test_render_without_sidecar_replaces_stale_confidence_with_unverified():
    """Catches a renderer that retains confidence when no audit sidecar exists."""
    rendered, _ = annotate.render_annotated_content(PROTO, None)

    assert "gold [stale]" not in rendered
    assert rendered.count("// confidence: unverified") == 2


def test_render_uses_field_override_tier_and_evidence():
    """Catches field annotations that use file-level audit values despite overrides."""
    audit = {
        **AUDIT,
        "fields": {
            "value": {
                "confidence": "silver",
                "evidence": [{"type": "runtime_trace"}],
            }
        },
    }

    rendered, _ = annotate.render_annotated_content(PROTO, audit)

    assert "optional string value = 1; // semantic note  // confidence: silver [runtime_trace]" in rendered


def test_render_preserves_semantic_inline_comment_before_confidence():
    """Catches field rewriting that discards a pre-existing non-confidence comment."""
    rendered, _ = annotate.render_annotated_content(PROTO, AUDIT)

    assert "optional string value = 1; // semantic note  // confidence: bronze [apk_static]" in rendered


def test_rendering_rendered_content_is_byte_identical():
    """Catches non-idempotent annotation rendering that churns generated files."""
    rendered_once, _ = annotate.render_annotated_content(PROTO, AUDIT)
    rendered_twice, _ = annotate.render_annotated_content(rendered_once, AUDIT)

    assert rendered_twice == rendered_once


def test_check_mode_reports_drift_without_writing(tmp_path: Path):
    """Catches check mode that repairs a drifting proto instead of remaining read-only."""
    proto_path = tmp_path / "Example.proto"
    proto_path.write_text(PROTO)

    stats = annotate.annotate_proto(proto_path, AUDIT, check=True)

    assert stats["changed"] is True
    assert proto_path.read_text() == PROTO


def test_cli_check_prints_exact_drifting_path_and_returns_one(tmp_path: Path, capsys):
    """Catches a drift CLI that hides the affected proto path or exits successfully."""
    proto_path = tmp_path / "Example.proto"
    proto_path.write_text(PROTO)

    result = annotate.main(["--check", str(tmp_path)])

    assert result == 1
    assert f"DRIFT: {proto_path}" in capsys.readouterr().out


def test_repair_then_check_is_clean_and_second_repair_is_a_noop(tmp_path: Path):
    """Catches repair output that remains drifting or changes on a second repair."""
    proto_path = tmp_path / "Example.proto"
    proto_path.write_text(PROTO)

    first_repair = annotate.annotate_proto(proto_path, AUDIT)
    repaired = proto_path.read_text()
    check = annotate.annotate_proto(proto_path, AUDIT, check=True)
    second_repair = annotate.annotate_proto(proto_path, AUDIT)

    assert first_repair["changed"] is True
    assert check["changed"] is False
    assert second_repair["changed"] is False
    assert proto_path.read_text() == repaired
