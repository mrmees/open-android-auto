from __future__ import annotations

from pathlib import Path

import yaml

from .models import LineageAnchor, LineageStep


_DISPOSITIONS = {"confirmed", "invalidated"}


def _required_text(item: dict[str, object], key: str, source: Path) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{source}: anchor field {key!r} must be non-empty text")
    return value.strip()


def load_lineage_anchors(path: Path) -> list[LineageAnchor]:
    """Load curated cross-version identities and semantic invalidations."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("anchors"), list):
        raise ValueError(f"{path}: expected a mapping with an anchors list")

    anchors: list[LineageAnchor] = []
    seen_names: set[str] = set()
    for raw_anchor in raw["anchors"]:
        if not isinstance(raw_anchor, dict):
            raise ValueError(f"{path}: every anchor must be a mapping")
        canonical_name = _required_text(raw_anchor, "canonical_name", path)
        current_class = _required_text(raw_anchor, "current_class", path)
        disposition = _required_text(raw_anchor, "disposition", path)
        if disposition not in _DISPOSITIONS:
            raise ValueError(
                f"{path}: {canonical_name} disposition must be one of "
                f"{sorted(_DISPOSITIONS)}"
            )
        if canonical_name in seen_names:
            raise ValueError(f"{path}: duplicate anchor for {canonical_name}")
        seen_names.add(canonical_name)

        raw_lineage = raw_anchor.get("lineage")
        if not isinstance(raw_lineage, list) or len(raw_lineage) < 2:
            raise ValueError(
                f"{path}: {canonical_name} lineage must contain at least two steps"
            )
        lineage: list[LineageStep] = []
        for raw_step in raw_lineage:
            if not isinstance(raw_step, dict):
                raise ValueError(f"{path}: {canonical_name} has a non-mapping step")
            lineage.append(
                LineageStep(
                    version=_required_text(raw_step, "version", path),
                    apk_class=_required_text(raw_step, "apk_class", path),
                )
            )
        if lineage[-1].apk_class != current_class:
            raise ValueError(
                f"{path}: {canonical_name} current_class must equal the last lineage step"
            )

        rejected = raw_anchor.get("rejected_candidates", [])
        evidence = raw_anchor.get("evidence")
        if not isinstance(rejected, list) or not all(
            isinstance(value, str) and value for value in rejected
        ):
            raise ValueError(
                f"{path}: {canonical_name} rejected_candidates must be text values"
            )
        if not isinstance(evidence, list) or not evidence or not all(
            isinstance(value, str) and value.strip() for value in evidence
        ):
            raise ValueError(
                f"{path}: {canonical_name} evidence must contain non-empty text"
            )

        anchors.append(
            LineageAnchor(
                canonical_name=canonical_name,
                current_class=current_class,
                disposition=disposition,
                lineage=tuple(lineage),
                rejected_candidates=tuple(sorted(set(rejected))),
                rationale=_required_text(raw_anchor, "rationale", path),
                evidence=tuple(value.strip() for value in evidence),
                source=str(path),
            )
        )
    return anchors
