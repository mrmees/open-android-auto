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


# ---------------------------------------------------------------------------
# 07-02 end-to-end tests: OEM-only diff, candidate labeling, JSON sidecar views
# ---------------------------------------------------------------------------


def test_oem_only_diff(tmp_path, bundle, vw_micro_path, dhu_micro_path):
    """The OEM-only candidate list is a set difference filtered through
    fragment classification.

    Fixture composition guarantee (07-01 Task 1): `dhu_micro.jsonl` does NOT
    contain msg_type=0x8004. The vw_micro fixture DOES contain msg_type=0x8004
    records (the dominant Tier B sensor stream). This guarantees the diff is
    non-empty so this test isn't vacuous.
    """
    from analysis.tools.oem_vw_parser.io import load_vw_capture
    from analysis.tools.oem_vw_parser.normalize import normalize_dhu_direction
    from analysis.tools.oem_vw_parser.tier_classifier import classify_capture

    vw = list(load_vw_capture(vw_micro_path, capture_id="vw_micro"))
    vw_classified, _ = classify_capture(vw, bundle)

    # Build vw key set (msg_type, direction), excluding garbage.
    vw_keys = {
        (cr.record.msg_type, cr.record.direction)
        for cr in vw_classified
        if cr.label != "continuation_or_garbage"
    }

    dhu_pairs = []
    for line in open(dhu_micro_path):
        if line.strip():
            r = json.loads(line)
            dhu_pairs.append((int(r["msg_type"]), r.get("direction", "dhu")))
    dhu_keys = {
        (mt, normalize_dhu_direction(d) if d in ("dhu", "phone") else d)
        for mt, d in dhu_pairs
    }

    diff = vw_keys - dhu_keys

    # Positive check: diff MUST be non-empty given the fixture composition rule.
    assert len(diff) >= 1, (
        "Expected at least one VW-only candidate from fixtures. "
        "Either dhu_micro.jsonl was modified to include msg_type=0x8004 "
        "(violating 07-01 Task 1 composition rule) or vw_micro.jsonl is missing "
        "the 0x8004 records."
    )
    assert (32772, "in") in diff, (
        f"Expected (0x8004='in') in diff, got: {sorted(diff)}"
    )

    # No purely-garbage candidate leaked. The diff is keyed by
    # (msg_type, direction); multiple records can share a key. The contract
    # is that EVERY key in the diff must have AT LEAST ONE non-garbage
    # underlying record — purely-garbage keys are filtered before the diff
    # via the `if cr.label != "continuation_or_garbage"` guard above. Records
    # that share a key with a non-garbage sibling are allowed to coexist;
    # they will not contribute to the candidate counts in run.py because
    # the candidate accumulator iterates classified records and skips garbage
    # via the same guard.
    cr_by_key: dict[tuple[int, str], list] = {}
    for cr in vw_classified:
        cr_by_key.setdefault((cr.record.msg_type, cr.record.direction), []).append(cr)
    for key in diff:
        assert key in cr_by_key, f"diff key {key} has no underlying classified record"
        # At least one non-garbage record must exist for this key.
        non_garbage = [
            cr for cr in cr_by_key[key] if cr.label != "continuation_or_garbage"
        ]
        assert len(non_garbage) >= 1, (
            f"diff key {key} has only continuation_or_garbage records — "
            f"the pre-diff filter should have excluded it"
        )
        # And that non-garbage record must be Tier A/B with a standalone/
        # probable_first label.
        for cr in non_garbage:
            assert cr.tier in {"A", "B"}, f"Tier C record leaked into diff: {key}"
            assert cr.label in {"standalone", "probable_first"}, (
                f"Garbage label leaked into diff: {key} → {cr.label}"
            )


def test_candidate_labels(tmp_path):
    """Every surviving candidate is labeled 'candidate', never 'confirmed'."""
    from analysis.tools.oem_vw_parser.manifests import emit_candidate_json

    candidates_by_mt = {42: {"count": 1, "tier": "B"}}
    candidates_by_mt_dir = {(42, "in"): {"count": 1, "tier": "B"}}
    out = tmp_path / "candidates.json"
    emit_candidate_json(candidates_by_mt, candidates_by_mt_dir, out)

    text = out.read_text()
    data = json.loads(text)
    assert data["label"] == "candidate"
    # Ensure no "confirmed" anywhere in the file.
    assert "confirmed" not in text


def test_candidate_views(tmp_path):
    """Both candidates_by_msg_type and candidates_by_msg_type_direction emit."""
    from analysis.tools.oem_vw_parser.manifests import emit_candidate_json

    emit_candidate_json(
        {1: {"count": 2}, 2: {"count": 3}},
        {(1, "in"): {"count": 2}, (2, "out"): {"count": 3}},
        tmp_path / "c.json",
    )
    data = json.loads((tmp_path / "c.json").read_text())
    assert "candidates_by_msg_type" in data
    assert "candidates_by_msg_type_direction" in data
    assert len(data["candidates_by_msg_type"]) == 2
    assert len(data["candidates_by_msg_type_direction"]) == 2
