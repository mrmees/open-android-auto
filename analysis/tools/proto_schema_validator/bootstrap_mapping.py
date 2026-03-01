"""Seed class_mapping.yaml from existing sources.

Sources:
1. ``// APK class: xyz`` comments in oaa/**/*.proto files (16.1 names)
2. ``apk_protos.json`` matches from prior analysis (16.1 names)

Run directly:
    python -m analysis.tools.proto_schema_validator.bootstrap_mapping
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import yaml


_REPO_ROOT = Path(__file__).resolve().parents[3]
_OAA_DIR = _REPO_ROOT / "oaa"
_APK_PROTOS_JSON = (
    _REPO_ROOT
    / "research"
    / "archive"
    / "openauto-prodigy"
    / "tools"
    / "proto_decode_output"
    / "apk_protos.json"
)
_OUTPUT = Path(__file__).resolve().parent / "class_mapping.yaml"

# Matches: ``// APK class: vxn`` or ``* APK class: vxo.java (AA v16.1)``
_APK_COMMENT_RE = re.compile(
    r"[/*]+\s*APK class:\s*([a-zA-Z]\w*)(?:\.java)?\b"
)
_MESSAGE_RE = re.compile(r"^message\s+(\w+)")


def _parse_proto_comments(oaa_dir: Path) -> dict[str, list[dict]]:
    """Parse APK class comments from proto files.

    Returns mapping of proto_file (relative to repo root) -> list of
    {message, apk_class} dicts.
    """
    results: dict[str, list[dict]] = {}

    for proto_path in sorted(oaa_dir.rglob("*.proto")):
        lines = proto_path.read_text(encoding="utf-8").splitlines()
        rel = str(proto_path.relative_to(oaa_dir.parent))

        pending_apk_classes: list[str] = []
        last_message: str | None = None
        entries: list[dict] = []

        for line in lines:
            stripped = line.strip()

            # Collect APK class comments
            m = _APK_COMMENT_RE.search(stripped)
            if m:
                pending_apk_classes.append(m.group(1))
                continue

            # Match message declarations
            m = _MESSAGE_RE.match(stripped)
            if m:
                last_message = m.group(1)
                # Associate pending APK comments with this message
                if pending_apk_classes:
                    for apk_cls in pending_apk_classes:
                        entries.append({
                            "message": last_message,
                            "apk_class": apk_cls,
                        })
                    pending_apk_classes = []

        if entries:
            results[rel] = entries

    return results


def _load_apk_protos_json(path: Path) -> list[dict]:
    """Load matches from apk_protos.json, filtering collisions."""
    with open(path) as f:
        data = json.load(f)

    matches = data.get("matches", [])
    # Count how many our_messages map to each apk_class
    apk_counts = Counter(m["apk_class"] for m in matches)

    results = []
    for m in matches:
        collision_count = apk_counts[m["apk_class"]]
        results.append({
            "our_message": m["our_message"],
            "our_proto": m["our_proto"],
            "apk_class": m["apk_class"],
            "score": m["score"],
            "collision_count": collision_count,
        })
    return results


def _find_proto_file(message_name: str, proto_filename: str, oaa_dir: Path) -> str | None:
    """Find the proto file path for a message name."""
    # Try matching by proto filename first
    candidates = list(oaa_dir.rglob(f"{proto_filename}.proto"))
    if len(candidates) == 1:
        return str(candidates[0].relative_to(oaa_dir.parent))

    # Try matching by message name
    for proto_path in oaa_dir.rglob("*.proto"):
        text = proto_path.read_text(encoding="utf-8")
        if re.search(rf"^message\s+{re.escape(message_name)}\b", text, re.MULTILINE):
            return str(proto_path.relative_to(oaa_dir.parent))

    return None


def _get_package_for_file(proto_path: Path, repo_root: Path) -> str:
    """Extract the package declaration from a proto file."""
    full = repo_root / proto_path
    if not full.exists():
        return ""
    for line in full.read_text(encoding="utf-8").splitlines():
        line = line.strip().rstrip(";")
        if line.startswith("package "):
            return line[8:].strip()
    return ""


def bootstrap(output: Path | None = None) -> Path:
    """Generate class_mapping.yaml from all available sources."""
    output = output or _OUTPUT

    # Source 1: Proto file comments
    comment_mappings = _parse_proto_comments(_OAA_DIR)

    # Source 2: apk_protos.json
    json_matches = _load_apk_protos_json(_APK_PROTOS_JSON) if _APK_PROTOS_JSON.exists() else []

    # Build unified mapping keyed by (proto_file, message_name)
    seen: dict[tuple[str, str], dict] = {}

    # Process comment mappings first (direct evidence)
    for proto_file, entries in comment_mappings.items():
        for entry in entries:
            key = (proto_file, entry["message"])
            if key not in seen:
                pkg = _get_package_for_file(Path(proto_file), _REPO_ROOT)
                fqn = f"{pkg}.{entry['message']}" if pkg else entry["message"]
                seen[key] = {
                    "proto_message": entry["message"],
                    "proto_file": proto_file,
                    "proto_fqn": fqn,
                    "apk_classes": {"16.1": entry["apk_class"], "16.2": None},
                    "confidence": "proto_comment",
                }
            else:
                # Additional APK class from another comment — could be sub-message
                existing = seen[key]
                if existing["apk_classes"]["16.1"] != entry["apk_class"]:
                    # First one wins for the top-level; note this case
                    pass

    # Process JSON matches
    for m in json_matches:
        proto_file = _find_proto_file(m["our_message"], m["our_proto"], _OAA_DIR)
        if not proto_file:
            continue

        key = (proto_file, m["our_message"])
        confidence = "apk_protos_json"
        if m["collision_count"] > 1:
            confidence = f"apk_protos_json_collision_{m['collision_count']}"

        if key not in seen:
            pkg = _get_package_for_file(Path(proto_file), _REPO_ROOT)
            fqn = f"{pkg}.{m['our_message']}" if pkg else m["our_message"]
            seen[key] = {
                "proto_message": m["our_message"],
                "proto_file": proto_file,
                "proto_fqn": fqn,
                "apk_classes": {"16.1": m["apk_class"], "16.2": None},
                "confidence": confidence,
            }
        else:
            # Comment already provided a mapping; JSON is supplementary
            existing = seen[key]
            if existing["apk_classes"]["16.1"] is None:
                existing["apk_classes"]["16.1"] = m["apk_class"]
                existing["confidence"] = confidence

    # Sort by proto file then message name
    mappings = sorted(seen.values(), key=lambda x: (x["proto_file"], x["proto_message"]))

    doc = {"mappings": mappings}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        yaml.dump(doc, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    return output


if __name__ == "__main__":
    out = bootstrap()
    print(f"Wrote {out}")
    with open(out) as f:
        data = yaml.safe_load(f)
    mappings = data["mappings"]
    print(f"  Total mappings: {len(mappings)}")
    sources = Counter(m["confidence"] for m in mappings)
    for src, cnt in sources.most_common():
        print(f"  {src}: {cnt}")
