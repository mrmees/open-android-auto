from analysis.tools.apk_indexer.catalog import build_catalog


def test_build_catalog_splits_accepted_and_unknown():
    signals = {
        "proto_classes": [
            {
                "file": "sources/defpackage/vvh.java",
                "class_name": "vvh",
                "descriptor": "....",
                "field_count": 3,
            }
        ],
        "proto_writes": [{"file": "A.java", "line": 5, "target": "vvhVar.b", "op": "|=", "value": "16"}],
        "class_references": [],
    }

    out = build_catalog(signals, apk_version="16.1")

    assert len(out["proto_catalog"]) == 1
    assert len(out["proto_unknowns"]) == 0
    assert out["proto_catalog"][0]["class_name"] == "vvh"
    assert out["proto_catalog"][0]["confidence"] == "high"


def test_build_catalog_routes_weak_evidence_to_unknown():
    signals = {
        "proto_classes": [
            {
                "file": "sources/defpackage/x1a.java",
                "class_name": "x1a",
                "descriptor": "",
                "field_count": 0,
            }
        ],
        "proto_writes": [],
        "class_references": [],
    }

    out = build_catalog(signals, apk_version="16.1")

    assert len(out["proto_catalog"]) == 0
    assert len(out["proto_unknowns"]) == 1
    assert out["proto_unknowns"][0]["class_name"] == "x1a"
    assert out["proto_unknowns"][0]["reason"] == "insufficient_evidence"
