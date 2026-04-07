from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_vw_histogram_snapshot(histogram_snapshot_path, bundle):
    """Empirical snapshot with loosened conservation-law assertions.

    Asserts conservation laws and lower bounds rather than exact counts so
    the test doesn't false-fail on ±1 boundary cases. Will fail loudly if
    the capture file is replaced or the msg_type=0 mic PCM rule is
    misfiring.
    """
    from analysis.tools.oem_vw_parser.io import load_vw_capture
    from analysis.tools.oem_vw_parser.tier_classifier import classify_capture

    snapshot = json.loads(histogram_snapshot_path.read_text())
    capture_path = REPO_ROOT / snapshot["capture_path"] / "messages.jsonl"
    if not capture_path.exists():
        pytest.skip(f"full VW capture not present at {capture_path}")

    records = list(
        load_vw_capture(capture_path, capture_id="oem-vw-mib3oi-2026-04-06")
    )

    # Conservation: total record count must match exactly. msg_type=0
    # demotion only moves records between tiers; it never creates or
    # destroys them.
    assert len(records) == snapshot["total_records"], (
        f"Capture record count drifted: expected {snapshot['total_records']}, "
        f"got {len(records)}. Update {histogram_snapshot_path} if intentional."
    )

    classified, profile = classify_capture(records, bundle)

    tier_counts = Counter(cr.tier for cr in classified)

    # Conservation: tiers sum to total
    assert sum(tier_counts.values()) == snapshot["total_records"]

    # Tier B is NOT affected by msg_type=0 demotion (only Tier A → C moves
    # happen). Allow a tiny absolute slack for boundary cases at the Tier
    # A/B descriptor map edges (a record that resolves through the message
    # map at one revision but not another shifts between A and B).
    expected_b = snapshot["tier_counts_pre_demotion"]["B"]
    assert abs(tier_counts["B"] - expected_b) <= 2, (
        f"Tier B drifted: expected {expected_b}, got {tier_counts['B']}"
    )

    # msg_type=0 demotion count: snapshot recorded 2,751 on 2026-04-07.
    # Allow ±5% slack for boundary cases at exactly payload_len == 32.
    demoted = [
        cr
        for cr in classified
        if cr.record.msg_type == 0 and "msg_type_zero_demoted_to_C" in cr.notes
    ]
    assert 2600 <= len(demoted) <= 2800, (
        f"Expected 2600-2800 msg_type=0 demotions, got {len(demoted)}. "
        f"Either the mic PCM rule is misfiring or the capture file changed. "
        f"Snapshot recorded 2751 demotions on 2026-04-07."
    )

    # Overall post-demotion totals match within 1% slack for boundary cases.
    for tier in ("A", "C"):
        expected = snapshot["tier_counts_post_demotion"][tier]
        actual = tier_counts[tier]
        assert abs(actual - expected) <= max(1, int(0.01 * expected)), (
            f"Tier {tier} drift > 1%: expected {expected}, got {actual}"
        )

    # The empirical threshold derivation should still land at the recorded
    # value.
    assert profile.threshold == snapshot["freq_threshold_derived"]


def test_classification_report_shape(tmp_path, bundle, vw_micro_path):
    """End-to-end on the micro fixture: produces a markdown and JSON
    report with the expected shape."""
    from analysis.tools.oem_vw_parser.io import load_vw_capture
    from analysis.tools.oem_vw_parser.manifests import emit_classification_json
    from analysis.tools.oem_vw_parser.reports import emit_classification_report
    from analysis.tools.oem_vw_parser.tier_classifier import classify_capture

    records = list(load_vw_capture(vw_micro_path, capture_id="vw_micro"))
    classified, profile = classify_capture(records, bundle)

    md_path = tmp_path / "msg-type-classification.md"
    json_path = tmp_path / "msg-type-classification.json"
    emit_classification_report(
        classified, profile, md_path, "vw_micro", 60.0, len(records)
    )
    emit_classification_json(
        classified, profile, json_path, "vw_micro", len(records)
    )

    md = md_path.read_text()
    assert "# VW Capture: Per-msg_type Classification" in md
    assert "Loud caveat" in md
    assert "reassembled" in md
    assert "intentionally empty" in md

    data = json.loads(json_path.read_text())
    assert data["label_counts"]["reassembled"] == 0
    assert data["label_counts"]["unattributed"] == 0
    assert "entries" in data
    assert "tier_counts" in data
