from __future__ import annotations


def classify_candidates(
    candidates: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    accepted: list[dict[str, object]] = []
    unknown: list[dict[str, object]] = []

    for row in candidates:
        sources = set(str(v) for v in row.get("evidence_sources", []))
        if len(sources) >= 2 and "descriptor" in sources:
            accepted.append({**row, "confidence": "high"})
        else:
            unknown.append({**row, "reason": "insufficient_evidence"})

    return accepted, unknown
