from __future__ import annotations

from analysis.tools.apk_indexer.confidence import classify_candidates


def _has_proto_write_for_class(
    class_name: str, proto_writes: list[dict[str, object]]
) -> bool:
    needle = class_name.lower()
    for row in proto_writes:
        target = str(row.get("target", "")).lower()
        if target.startswith(f"{needle}var.") or target.startswith(f"{needle}."):
            return True
        if f"{needle}var" in target:
            return True
    return False


def _has_class_reference(
    class_name: str, class_references: list[dict[str, object]]
) -> bool:
    for row in class_references:
        if str(row.get("target_class", "")) == class_name:
            return True
    return False


def _build_candidates(signals: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    proto_classes = signals.get("proto_classes", [])
    proto_writes = signals.get("proto_writes", [])
    class_references = signals.get("class_references", [])

    for row in proto_classes:
        class_name = str(row.get("class_name", ""))
        descriptor = str(row.get("descriptor", ""))
        field_count = int(row.get("field_count", 0))
        source_file = str(row.get("file", ""))

        evidence_sources: list[str] = []
        if descriptor:
            evidence_sources.append("descriptor")
        if field_count > 0:
            evidence_sources.append("field_decls")
        if _has_proto_write_for_class(class_name, proto_writes):
            evidence_sources.append("proto_writes")
        if _has_class_reference(class_name, class_references):
            evidence_sources.append("class_references")

        candidates.append(
            {
                "class_name": class_name,
                "source_file": source_file,
                "field_count": field_count,
                "descriptor": descriptor,
                "evidence_sources": evidence_sources,
            }
        )
    return candidates


def build_catalog(
    signals: dict[str, list[dict[str, object]]], apk_version: str
) -> dict[str, list[dict[str, object]]]:
    candidates = _build_candidates(signals)
    accepted, unknown = classify_candidates(candidates)

    proto_catalog = [
        {
            "class_name": str(row.get("class_name", "")),
            "apk_version": apk_version,
            "confidence": str(row.get("confidence", "high")),
            "field_count": int(row.get("field_count", 0)),
            "descriptor": str(row.get("descriptor", "")),
            "source_file": str(row.get("source_file", "")),
        }
        for row in accepted
    ]

    proto_unknowns = [
        {
            "class_name": str(row.get("class_name", "")),
            "reason": str(row.get("reason", "insufficient_evidence")),
            "evidence_count": len(row.get("evidence_sources", [])),
            "notes": "manual_review_required",
        }
        for row in unknown
    ]

    proto_evidence: list[dict[str, object]] = []
    for row in candidates:
        class_name = str(row.get("class_name", ""))
        source_file = str(row.get("source_file", ""))
        for source in row.get("evidence_sources", []):
            proto_evidence.append(
                {
                    "class_name": class_name,
                    "evidence_source": str(source),
                    "evidence_detail": str(source),
                    "source_file": source_file,
                    "line": 0,
                }
            )

    run_metadata = [
        {"key": "apk_version", "value": apk_version},
        {"key": "proto_candidates", "value": str(len(candidates))},
        {"key": "proto_catalog_count", "value": str(len(proto_catalog))},
        {"key": "proto_unknown_count", "value": str(len(proto_unknowns))},
    ]

    return {
        "proto_catalog": proto_catalog,
        "proto_evidence": proto_evidence,
        "proto_unknowns": proto_unknowns,
        "run_metadata": run_metadata,
    }
