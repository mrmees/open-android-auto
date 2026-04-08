"""Two-pass 16.4 class identity matcher.

Phase 8 XVER-01 — resolves 16.4 obfuscated class names for existing 16.2
mappings using only intrinsic structural features. No re-decompilation, no
log scraping, no human review in the inner loop.

Algorithm
---------
Pass 1: independent identity by structural fingerprint.
    - For enums: (int_value, enum_name) tuple from enum_maps (or
      proto_enum_classes fallback). If exactly one 16.4 class has the
      identical tuple -> commit.
    - For messages: (field_number, base_type) tuple from proto_fields.
      If exactly one 16.4 class has the identical tuple -> commit.
    - Anything not unique stays in the unresolved bucket.

Pass 2: anchored topology disambiguation.
    - For each unresolved ambiguous mapping, look up the source class's
      sub_message_refs. Map the known 16.2 sub-refs through Pass 1 anchors
      to a predicted 16.4 sub-ref set. Filter the candidate list to those
      whose 16.4 sub_message_refs superset the predicted set.
    - Commit if exactly one candidate remains.

Falls back to 16.1 / 15.9 fingerprints when 16.2 class is null
(per 08-RESEARCH.md Open Question 4).

Empirical targets (08-RESEARCH.md First-Pass Empirical Sanity Check):
    Pass 1 enum commits:        5  (all 5 enums)
    Pass 1 message commits:    78  (unique field-tuple)
    Pass 2 topology commits:   10  (anchored subref disambiguation)
    Total committable:         93 / 240 (38.8%)

Output
------
- Mutates analysis/tools/proto_schema_validator/class_mapping.yaml in place.
  Every mapping gets a '16.4' key, either a class name (committed) or None
  (ambiguous / no_candidate / no_source_class). NO inline comments —
  PyYAML strips them on round-trip (08-RESEARCH.md Correction #5).
- Writes analysis/reports/cross-version/16-4-mapping-candidates.md with
  every unresolved mapping and the reason for non-commit.
- Returns a stats dict for the snapshot test.

The matcher is idempotent: running twice on an already-populated YAML
produces the same output (same class_mapping.yaml, same candidates report,
same stats). No duplicate writes.

Usage
-----
    PYTHONPATH=. python3 -m analysis.tools.cross_version.match_16_4
    # -> prints stats JSON to stdout
"""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from analysis.tools.proto_schema_validator.mapping import (
    get_apk_enum_values,
    get_apk_fields,
    load_mapping,
)
from analysis.tools.proto_schema_validator.models import FieldDef, ProtoMapping

_REPO_ROOT = Path(__file__).resolve().parents[3]
MAPPING_YAML = _REPO_ROOT / "analysis" / "tools" / "proto_schema_validator" / "class_mapping.yaml"
CANDIDATES_MD = _REPO_ROOT / "analysis" / "reports" / "cross-version" / "16-4-mapping-candidates.md"

_SOURCE_VERSION_PRIORITY = ("16.2", "16.1", "15.9")


@dataclass
class MatchResult:
    """Outcome of attempting to match one mapping to a 16.4 class."""

    proto_message: str
    outcome: str
    # outcome ∈ {"pass1_enum", "pass1_message", "pass2_topology",
    #            "ambiguous", "no_candidate", "no_source_class"}
    source_class: str | None = None
    source_version: str = ""
    committed_to: str | None = None
    candidates: list[str] = field(default_factory=list)
    field_count: int | None = None
    reason: str = ""


def _load_16_4_index(db_164: Path) -> dict[str, Any]:
    """Build lookup indices from the 16.4 DB.

    Returns:
        dict with keys:
          "field_tuple_to_classes": (field_num, base_type, ...) -> [class_name]
          "enum_tuple_to_classes":  (value, name, ...) -> [class_name]
          "class_to_sub_refs":      class_name -> set(sub_class_name)
    """
    conn = sqlite3.connect(str(db_164))
    conn.row_factory = sqlite3.Row
    try:
        # Field tuples per class
        field_rows = conn.execute(
            "SELECT class_name, field_number, base_type FROM proto_fields "
            "ORDER BY class_name, field_number"
        ).fetchall()
        fields_by_class: dict[str, list[tuple[int, str]]] = defaultdict(list)
        for r in field_rows:
            fields_by_class[r["class_name"]].append((r["field_number"], r["base_type"]))

        field_tuple_to_classes: dict[tuple, list[str]] = defaultdict(list)
        for cls, fs in fields_by_class.items():
            tup = tuple(sorted(fs))
            field_tuple_to_classes[tup].append(cls)

        # Enum tuples: prefer enum_maps, fall back to proto_enum_classes
        enum_rows = conn.execute(
            "SELECT enum_class, int_value, enum_name FROM enum_maps "
            "ORDER BY enum_class, int_value"
        ).fetchall()
        enum_by_class: dict[str, list[tuple[int, str]]] = defaultdict(list)
        for r in enum_rows:
            enum_by_class[r["enum_class"]].append((r["int_value"], r["enum_name"]))

        # proto_enum_classes fallback (may or may not exist)
        try:
            pec_rows = conn.execute(
                'SELECT class_name, "values" FROM proto_enum_classes'
            ).fetchall()
            for r in pec_rows:
                if r["class_name"] in enum_by_class:
                    continue  # enum_maps already has it
                try:
                    values = json.loads(r["values"])
                    enum_by_class[r["class_name"]] = [
                        (v["int_value"], v["name"]) for v in values
                    ]
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
        except sqlite3.OperationalError:
            pass

        enum_tuple_to_classes: dict[tuple, list[str]] = defaultdict(list)
        for cls, vs in enum_by_class.items():
            tup = tuple(sorted(vs))
            enum_tuple_to_classes[tup].append(cls)

        # sub_message_refs per class
        class_to_sub_refs: dict[str, set[str]] = {}
        try:
            sub_rows = conn.execute(
                "SELECT class_name, sub_message_refs FROM proto_classes"
            ).fetchall()
            for r in sub_rows:
                refs_raw = r["sub_message_refs"]
                if not refs_raw:
                    class_to_sub_refs[r["class_name"]] = set()
                    continue
                try:
                    refs = json.loads(refs_raw)
                    class_to_sub_refs[r["class_name"]] = set(refs) if refs else set()
                except json.JSONDecodeError:
                    class_to_sub_refs[r["class_name"]] = set()
        except sqlite3.OperationalError:
            pass
    finally:
        conn.close()

    return {
        "field_tuple_to_classes": dict(field_tuple_to_classes),
        "enum_tuple_to_classes": dict(enum_tuple_to_classes),
        "class_to_sub_refs": class_to_sub_refs,
    }


def _source_class(mapping: ProtoMapping) -> tuple[str | None, str]:
    """Return (class_name, source_version). Prefer 16.2 > 16.1 > 15.9."""
    for v in _SOURCE_VERSION_PRIORITY:
        cls = mapping.apk_classes.get(v)
        if cls:
            return (cls, v)
    return (None, "")


def _field_tuple(db_path: Path, class_name: str) -> tuple[tuple[int, str], ...]:
    fields = get_apk_fields(db_path, class_name)
    return tuple(sorted((f.field_number, f.base_type) for f in fields))


def _enum_tuple(db_path: Path, class_name: str) -> tuple[tuple[int, str], ...]:
    values = get_apk_enum_values(db_path, class_name)
    if not values:
        return ()
    return tuple(sorted(values))


def _get_sub_refs(db: Path, cls: str) -> set[str]:
    """Query sub_message_refs for one class, return set of sub-class names."""
    conn = sqlite3.connect(str(db))
    try:
        row = conn.execute(
            "SELECT sub_message_refs FROM proto_classes WHERE class_name = ?",
            (cls,),
        ).fetchone()
    except sqlite3.OperationalError:
        return set()
    finally:
        conn.close()
    if row is None or not row[0]:
        return set()
    try:
        refs = json.loads(row[0])
    except json.JSONDecodeError:
        return set()
    return set(refs) if refs else set()


def run_matcher(
    db_paths_prior: dict[str, Path] | None = None,
    db_164: Path | None = None,
) -> dict[str, Any]:
    """Two-pass matcher. Mutates class_mapping.yaml in place. Returns summary stats."""
    from analysis.tools.cross_version.run import _find_db

    if db_paths_prior is None:
        db_paths_prior = {
            "15.9": _find_db("15.9"),
            "16.1": _find_db("16.1"),
            "16.2": _find_db("16.2"),
        }
    if db_164 is None:
        db_164 = _find_db("16.4")

    if db_164 is None:
        raise RuntimeError("16.4 DB not found — expected canonical build 661014")

    mappings = load_mapping()
    index_164 = _load_16_4_index(db_164)

    results: list[MatchResult] = []
    pass1_anchors: dict[str, str] = {}  # source_class_name -> 16.4_class_name

    # ---------- Pass 1: unique fingerprint matching ----------
    for m in mappings:
        src_class, src_version = _source_class(m)
        if not src_class:
            results.append(
                MatchResult(
                    proto_message=m.proto_message,
                    outcome="no_source_class",
                    reason="no non-null class in 15.9/16.1/16.2",
                )
            )
            m.apk_classes["16.4"] = None
            continue

        src_db = db_paths_prior.get(src_version)
        if src_db is None:
            results.append(
                MatchResult(
                    proto_message=m.proto_message,
                    outcome="no_source_class",
                    source_class=src_class,
                    source_version=src_version,
                    reason=f"source DB for {src_version} unavailable",
                )
            )
            m.apk_classes["16.4"] = None
            continue

        # Try enum fingerprint first
        enum_tup = _enum_tuple(src_db, src_class)
        if enum_tup:
            candidates = index_164["enum_tuple_to_classes"].get(enum_tup, [])
            if len(candidates) == 1:
                m.apk_classes["16.4"] = candidates[0]
                pass1_anchors[src_class] = candidates[0]
                results.append(
                    MatchResult(
                        proto_message=m.proto_message,
                        outcome="pass1_enum",
                        source_class=src_class,
                        source_version=src_version,
                        committed_to=candidates[0],
                        field_count=len(enum_tup),
                    )
                )
                continue
            elif len(candidates) > 1:
                results.append(
                    MatchResult(
                        proto_message=m.proto_message,
                        outcome="ambiguous",
                        source_class=src_class,
                        source_version=src_version,
                        candidates=list(candidates),
                        field_count=len(enum_tup),
                        reason=f"enum fingerprint has {len(candidates)} 16.4 matches",
                    )
                )
                m.apk_classes["16.4"] = None
                continue
            else:
                # enum fingerprint but no 16.4 match — fall through to message
                pass

        # Fall through to message fingerprint
        field_tup = _field_tuple(src_db, src_class)
        if not field_tup:
            # 0-field marker class OR truly absent — record and null
            results.append(
                MatchResult(
                    proto_message=m.proto_message,
                    outcome="no_candidate",
                    source_class=src_class,
                    source_version=src_version,
                    field_count=0,
                    reason="0-field marker class (no fields and no enum values)",
                )
            )
            m.apk_classes["16.4"] = None
            continue

        candidates = index_164["field_tuple_to_classes"].get(field_tup, [])
        if len(candidates) == 1:
            m.apk_classes["16.4"] = candidates[0]
            pass1_anchors[src_class] = candidates[0]
            results.append(
                MatchResult(
                    proto_message=m.proto_message,
                    outcome="pass1_message",
                    source_class=src_class,
                    source_version=src_version,
                    committed_to=candidates[0],
                    field_count=len(field_tup),
                )
            )
        elif len(candidates) > 1:
            results.append(
                MatchResult(
                    proto_message=m.proto_message,
                    outcome="ambiguous",
                    source_class=src_class,
                    source_version=src_version,
                    candidates=list(candidates),
                    field_count=len(field_tup),
                    reason=f"field-tuple has {len(candidates)} 16.4 matches",
                )
            )
            m.apk_classes["16.4"] = None
        else:
            results.append(
                MatchResult(
                    proto_message=m.proto_message,
                    outcome="no_candidate",
                    source_class=src_class,
                    source_version=src_version,
                    field_count=len(field_tup),
                    reason="no 16.4 class has matching field-tuple",
                )
            )
            m.apk_classes["16.4"] = None

    # ---------- Pass 2: topology disambiguation ----------
    for i, r in enumerate(results):
        if r.outcome != "ambiguous" or not r.candidates:
            continue
        m = mappings[i]
        src_class = r.source_class
        src_version = r.source_version
        if not src_class or not src_version:
            continue
        src_db = db_paths_prior.get(src_version)
        if src_db is None:
            continue

        src_subs = _get_sub_refs(src_db, src_class)
        # Map known 16.2 sub-refs through Pass 1 anchors -> predicted 16.4 sub-refs
        predicted = {pass1_anchors[s] for s in src_subs if s in pass1_anchors}
        if not predicted:
            continue  # no topology to leverage

        # Filter candidates whose 16.4 sub_message_refs superset the predicted set
        filtered = [
            c
            for c in r.candidates
            if predicted.issubset(index_164["class_to_sub_refs"].get(c, set()))
        ]
        if len(filtered) == 1:
            m.apk_classes["16.4"] = filtered[0]
            pass1_anchors[src_class] = filtered[0]
            results[i] = MatchResult(
                proto_message=r.proto_message,
                outcome="pass2_topology",
                source_class=src_class,
                source_version=src_version,
                committed_to=filtered[0],
                field_count=r.field_count,
            )

    # ---------- Write outputs ----------
    _write_mapping_yaml(mappings)
    _write_candidates_md(results)

    # Return stats (JSON-serializable for the snapshot test)
    pass1_enum = sum(1 for r in results if r.outcome == "pass1_enum")
    pass1_msg = sum(1 for r in results if r.outcome == "pass1_message")
    pass2 = sum(1 for r in results if r.outcome == "pass2_topology")
    total_committable = pass1_enum + pass1_msg + pass2
    unresolved = sum(
        1 for r in results if r.outcome in ("ambiguous", "no_candidate", "no_source_class")
    )
    return {
        "total_mappings": len(results),
        "pass1_enum_commits": pass1_enum,
        "pass1_message_commits": pass1_msg,
        "pass2_topology_commits": pass2,
        "total_committable": total_committable,
        "ambiguous_or_unmatched": unresolved,
        "generated_date": "2026-04-08",
        "note": "Generated by analysis/tools/cross_version/match_16_4.py against canonical 16.4.661014 APK DB.",
    }


def _mapping_to_dict(m: ProtoMapping) -> dict[str, Any]:
    """Serialize a ProtoMapping back to a YAML-friendly dict.

    Preserves the field ordering that load_mapping() produces:
      proto_message, proto_file, proto_fqn, apk_classes, confidence
    The apk_classes dict stays keyed by version string and is sorted
    deterministically (15.9, 16.1, 16.2, 16.4) so round-trips are stable.
    """
    apk = {}
    # Preserve deterministic ordering for reviewability
    for v in ("15.9", "16.1", "16.2", "16.4"):
        if v in m.apk_classes:
            apk[v] = m.apk_classes[v]
    # Any other versions (future-proof) go at the end, sorted
    for v in sorted(m.apk_classes.keys()):
        if v not in apk:
            apk[v] = m.apk_classes[v]
    out: dict[str, Any] = {
        "proto_message": m.proto_message,
        "proto_file": m.proto_file,
    }
    if m.proto_fqn:
        out["proto_fqn"] = m.proto_fqn
    out["apk_classes"] = apk
    if m.confidence:
        out["confidence"] = m.confidence
    return out


def _write_mapping_yaml(mappings: list[ProtoMapping]) -> None:
    """Serialize mappings back to class_mapping.yaml using PyYAML.

    Comments are NOT preserved — per 08-RESEARCH.md Correction #5, all
    ambiguous-match context lives in 16-4-mapping-candidates.md, not
    inline YAML comments.
    """
    data = {"mappings": [_mapping_to_dict(m) for m in mappings]}
    MAPPING_YAML.write_text(
        yaml.safe_dump(
            data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
    )


def _write_candidates_md(results: list[MatchResult]) -> None:
    CANDIDATES_MD.parent.mkdir(parents=True, exist_ok=True)
    unresolved = [
        r for r in results if r.outcome in ("ambiguous", "no_candidate", "no_source_class")
    ]
    lines = [
        "# 16.4 Mapping Candidates — Ambiguous Auto-Matcher Results",
        "",
        "Generated: 2026-04-08 by `analysis/tools/cross_version/match_16_4.py`",
        "",
        "This file lists every mapping the auto-matcher could NOT commit to a unique "
        "16.4 class. Ambiguous entries have multiple candidates with the same structural "
        "fingerprint; no_candidate entries have no 16.4 class sharing their fingerprint "
        "(usually 0-field marker classes); no_source_class entries have no non-null 15.9 / "
        "16.1 / 16.2 class to fingerprint from.",
        "",
        "Human review: spot-check ambiguous entries with ≥1 overlapping sub-message ref "
        "or field count within ±2 of the source.",
        "",
        f"**Total unresolved:** {len(unresolved)} / {len(results)}",
        "",
        "| Proto | Outcome | Source (ver / class) | Field count | Candidates | Reason |",
        "|-------|---------|----------------------|-------------|------------|--------|",
    ]
    for r in sorted(unresolved, key=lambda x: (x.outcome, x.proto_message)):
        src = (
            f"{r.source_version} / `{r.source_class}`"
            if r.source_class
            else "—"
        )
        cand_str = ", ".join(f"`{c}`" for c in r.candidates) if r.candidates else "—"
        fc = str(r.field_count) if r.field_count is not None else "—"
        lines.append(
            f"| `{r.proto_message}` | {r.outcome} | {src} | {fc} | {cand_str} | {r.reason} |"
        )
    CANDIDATES_MD.write_text("\n".join(lines) + "\n")


def main() -> None:
    stats = run_matcher()
    json.dump(stats, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
