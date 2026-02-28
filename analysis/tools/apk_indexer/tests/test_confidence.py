from analysis.tools.apk_indexer.confidence import classify_candidates


def test_classify_accepts_high_confidence():
    accepted, unknown = classify_candidates(
        [
            {
                "class_name": "vvh",
                "evidence_sources": ["descriptor", "field_decls", "proto_writes"],
            }
        ]
    )
    assert len(accepted) == 1
    assert len(unknown) == 0
    assert accepted[0]["confidence"] == "high"


def test_classify_routes_low_confidence_to_unknown():
    accepted, unknown = classify_candidates(
        [{"class_name": "x1a", "evidence_sources": ["proto_writes"]}]
    )
    assert len(accepted) == 0
    assert len(unknown) == 1
    assert unknown[0]["reason"] == "insufficient_evidence"


def test_classify_routes_borderline_to_unknown():
    accepted, unknown = classify_candidates(
        [{"class_name": "vyk", "evidence_sources": ["descriptor"]}]
    )
    assert len(accepted) == 0
    assert len(unknown) == 1
    assert unknown[0]["reason"] == "insufficient_evidence"
