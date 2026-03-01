from __future__ import annotations

from collections import Counter
from pathlib import Path
import json
import re


UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
)
HEX_RE = re.compile(r"\b0x[0-9A-Fa-f]{4,}\b")
PROTO_ACCESS_RE = re.compile(r"\b(set|get|has|clear)[A-Z][A-Za-z0-9_]*\s*\(")
CALL_EDGE_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(")
PROTO_WRITE_OR_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*)\s*(\|=)\s*([^;]+);"
)
PROTO_WRITE_ASSIGN_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*)\s*(?<![=!<>])=(?!=)\s*([^;]+);"
)
ENUM_CLASS_RE = re.compile(r"\b(?:public\s+)?enum\s+([A-Za-z_][A-Za-z0-9_]*)\b")
SWITCH_RE = re.compile(r"\bswitch\s*\(([^)]+)\)")
CASE_RE = re.compile(r"\bcase\s+([^:]+):")

# Proto-lite class patterns (base class detected dynamically by _detect_proto_names)
DEPRECATED_RE = re.compile(r"@Deprecated")
# Field declarations: public <type> <name>
FIELD_DECL_RE = re.compile(
    r"^\s+public\s+(?!static|final)(\S+)\s+([a-z][a-zA-Z0-9]*)\s*[;=]",
    re.MULTILINE,
)

# Obfuscated package directories produced by different jadx versions
_OBFUSCATED_DIRS = ("defpackage", "p000")

# Pattern to find "extends <classname>" in the obfuscated package
_EXTENDS_RE = re.compile(r"\bextends\s+(?:defpackage\.)?([a-z][a-z0-9]*)\b")


def _find_obfuscated_dir(root: Path) -> str | None:
    """Detect which obfuscated package dir this source tree uses."""
    sources = root / "sources"
    for dirname in _OBFUSCATED_DIRS:
        if (sources / dirname).is_dir():
            return dirname
    return None


def _detect_proto_names(root: Path) -> tuple[str | None, str | None, str | None]:
    """Auto-detect obfuscated proto-lite base class and descriptor class names.

    Returns (obfuscated_dir, base_class, descriptor_class).

    Strategy:
    - Proto base class: the most-extended class in the obfuscated package (1900+ hits)
    - Descriptor class: the most-instantiated class via `new <class>(` (2000+ hits)
    """
    obf_dir = _find_obfuscated_dir(root)
    if obf_dir is None:
        return None, None, None

    obf_path = root / "sources" / obf_dir
    extends_counts: Counter[str] = Counter()
    new_counts: Counter[str] = Counter()

    # Build patterns based on package style
    if obf_dir == "defpackage":
        extends_pat = re.compile(r"\bextends\s+defpackage\.([a-z][a-z0-9]*)\b")
        new_pat = re.compile(r"\bnew\s+defpackage\.([a-z][a-z0-9]*)\s*\(")
    else:
        extends_pat = re.compile(r"\bextends\s+([a-z][a-z0-9]*)\s")
        new_pat = re.compile(r"\bnew\s+([a-z][a-z0-9]*)\s*\(")

    for java_file in obf_path.glob("*.java"):
        try:
            text = java_file.read_text(errors="ignore")
        except OSError:
            continue
        for m in extends_pat.finditer(text):
            extends_counts[m.group(1)] += 1
        for m in new_pat.finditer(text):
            new_counts[m.group(1)] += 1

    # Proto base: most extended, should be 1500+ (proto-lite GeneratedMessageLite)
    base_class = None
    if extends_counts:
        top_class, top_count = extends_counts.most_common(1)[0]
        if top_count > 500:  # proto base is always dominant by a wide margin
            base_class = top_class

    # Descriptor class: most instantiated, should be 1500+
    descriptor_class = None
    if new_counts:
        top_class, top_count = new_counts.most_common(1)[0]
        if top_count > 500:
            descriptor_class = top_class

    return obf_dir, base_class, descriptor_class


def _in_scope(path: Path, root: Path, scope: str, obf_dir: str | None = None) -> bool:
    if scope == "all":
        return True
    rel = path.relative_to(root).as_posix()
    # Always include the obfuscated package — proto classes live there
    if obf_dir and rel.startswith(f"sources/{obf_dir}/"):
        return True
    if scope == "projection":
        return rel.startswith("sources/com/google/android/projection/")
    return True


def _iter_text_files(root: Path, scope: str, obf_dir: str | None = None):
    for path in root.rglob("*"):
        if path.is_file() and _in_scope(path, root, scope, obf_dir):
            yield path


def _extract_enum_maps_from_text(path: Path, text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    enum_match = ENUM_CLASS_RE.search(text)
    if not enum_match:
        return rows
    enum_class = enum_match.group(1)

    lines = text.splitlines()
    pending_case: tuple[int, int] | None = None
    for line_no, line in enumerate(lines, 1):
        case_match = CASE_RE.search(line)
        if case_match:
            value_raw = case_match.group(1).strip()
            if value_raw.isdigit():
                pending_case = (line_no, int(value_raw))
            else:
                pending_case = None
            continue
        if pending_case is None:
            continue

        return_match = re.search(r"\breturn\s+([A-Z][A-Z0-9_]+)\s*;", line)
        if return_match:
            rows.append(
                {
                    "file": str(path),
                    "line": pending_case[0],
                    "enum_class": enum_class,
                    "int_value": pending_case[1],
                    "enum_name": return_match.group(1),
                }
            )
            pending_case = None
    return rows


def _extract_switch_maps_from_text(path: Path, text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    lines = text.splitlines()
    current_switch: str | None = None
    current_case: tuple[int, str] | None = None

    for line_no, line in enumerate(lines, 1):
        switch_match = SWITCH_RE.search(line)
        if switch_match:
            current_switch = switch_match.group(1).strip()
            current_case = None
            continue
        if current_switch is None:
            continue
        case_match = CASE_RE.search(line)
        if case_match:
            current_case = (line_no, case_match.group(1).strip())
            continue
        if current_case is not None:
            target_match = CALL_EDGE_RE.search(line)
            if target_match:
                rows.append(
                    {
                        "file": str(path),
                        "line": current_case[0],
                        "switch_expr": current_switch,
                        "case_value": current_case[1],
                        "target": f"{target_match.group(1)}.{target_match.group(2)}",
                    }
                )
                current_case = None
                continue
        if line.strip() == "}":
            current_switch = None
            current_case = None
    return rows


def _extract_proto_class_from_text(
    path: Path, text: str,
    extends_re: re.Pattern | None = None,
    descriptor_re: re.Pattern | None = None,
) -> dict[str, object] | None:
    """Extract metadata from protobuf-lite classes.

    Uses dynamically-detected base class and descriptor class patterns.
    """
    if extends_re is None or not extends_re.search(text):
        return None

    class_name = path.stem  # e.g. "vvh" from "vvh.java"
    deprecated = bool(DEPRECATED_RE.search(text))

    # Extract field declarations (type + name)
    fields: list[dict[str, str]] = []
    for m in FIELD_DECL_RE.finditer(text):
        field_type = m.group(1)
        field_name = m.group(2)
        # Normalize package-qualified types to just the class name
        if field_type.startswith("defpackage."):
            field_type = field_type.replace("defpackage.", "")
        elif field_type.startswith("p000."):
            field_type = field_type.replace("p000.", "")
        elif field_type == "java.lang.String":
            field_type = "String"
        fields.append({"type": field_type, "name": field_name})

    # Extract descriptor string and field name array from RawMessageInfo constructor
    descriptor = ""
    field_names: list[str] = []
    if descriptor_re is not None:
        desc_match = descriptor_re.search(text)
        if desc_match:
            descriptor = desc_match.group(1)
            names_raw = desc_match.group(2) if desc_match.lastindex >= 2 else ""
            if names_raw:
                field_names = [
                    n.strip().strip('"')
                    for n in names_raw.split(",")
                    if n.strip().strip('"')
                ]

    # Extract sub-message type references from field declarations
    sub_message_refs: list[str] = []
    for f in fields:
        ft = f["type"]
        if ft not in ("int", "long", "boolean", "float", "double", "byte", "String",
                       "byte[]") and not ft.startswith("zz"):
            # Likely a sub-message reference (another proto class)
            sub_message_refs.append(ft)

    return {
        "file": str(path),
        "class_name": class_name,
        "deprecated": deprecated,
        "field_count": len(fields),
        "field_names": json.dumps(field_names),
        "field_types": json.dumps([f["type"] for f in fields]),
        "field_decls": json.dumps(fields),
        "sub_message_refs": json.dumps(sub_message_refs),
        "descriptor": descriptor,
    }


def _extract_class_references_from_text(
    path: Path, text: str, root: Path, obf_dir: str | None = None,
) -> list[dict[str, object]]:
    """Find references to obfuscated-package classes from all files."""
    rel = path.relative_to(root).as_posix()
    source_class = path.stem
    is_obfuscated = obf_dir is not None and f"{obf_dir}/" in rel

    # Build reference pattern based on package style
    if obf_dir == "defpackage":
        ref_re = re.compile(r"\bdefpackage\.([a-z][a-z0-9]*)\b")
    elif obf_dir == "p000":
        # p000 classes are referenced without prefix in same-package code,
        # but with "p000." prefix from other packages via imports
        ref_re = re.compile(r"\bp000\.([a-z][a-z0-9]*)\b")
    else:
        return []

    rows: list[dict[str, object]] = []
    seen: set[str] = set()  # Dedupe per file
    for line_no, line in enumerate(text.splitlines(), 1):
        for m in ref_re.finditer(line):
            target_class = m.group(1)
            # Skip self-references in obfuscated package files
            if is_obfuscated and target_class == source_class:
                continue
            if target_class not in seen:
                seen.add(target_class)
                if is_obfuscated:
                    source_pkg = f"{obf_dir}.{source_class}"
                else:
                    source_pkg = rel.replace("sources/", "").replace("/", ".").rsplit(".", 1)[0]
                rows.append({
                    "file": str(path),
                    "line": line_no,
                    "source_package": source_pkg,
                    "target_class": target_class,
                })
    return rows


def extract_signals(root: Path, scope: str = "all") -> dict[str, list[dict[str, object]]]:
    uuids: list[dict[str, object]] = []
    constants: list[dict[str, object]] = []
    proto_accesses: list[dict[str, object]] = []
    proto_writes: list[dict[str, object]] = []
    call_edges: list[dict[str, object]] = []
    enum_maps: list[dict[str, object]] = []
    switch_maps: list[dict[str, object]] = []
    proto_classes: list[dict[str, object]] = []
    class_references: list[dict[str, object]] = []

    # Auto-detect obfuscated proto class names for this APK version
    obf_dir, base_class, descriptor_class = _detect_proto_names(root)
    if base_class:
        print(f"  Proto-lite base class: {base_class} (in {obf_dir}/)")
        if obf_dir == "defpackage":
            extends_re = re.compile(rf"\bextends\s+defpackage\.{re.escape(base_class)}\b")
        else:
            extends_re = re.compile(rf"\bextends\s+{re.escape(base_class)}\s")
    else:
        print("  WARNING: Could not detect proto-lite base class")
        extends_re = None

    if descriptor_class:
        print(f"  Descriptor class: {descriptor_class}")
        # Match: new <class>(<instance>, "<descriptor>", new Object[]{...})
        # Also: new <class>(<instance>, "<descriptor>", null)
        if obf_dir == "defpackage":
            prefix = rf"defpackage\.{re.escape(descriptor_class)}"
        else:
            prefix = re.escape(descriptor_class)
        descriptor_re = re.compile(
            rf'new\s+{prefix}\s*\([^,]+,\s*"([^"]*?)"\s*'
            rf'(?:,\s*new\s+(?:java\.lang\.)?Object\[\]\s*\{{([^}}]*)\}}|,\s*null)\s*\)'
        )
    else:
        print("  WARNING: Could not detect descriptor class")
        descriptor_re = None

    for path in _iter_text_files(root, scope, obf_dir):
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        enum_maps.extend(_extract_enum_maps_from_text(path, text))
        switch_maps.extend(_extract_switch_maps_from_text(path, text))

        # Proto class metadata
        proto_meta = _extract_proto_class_from_text(
            path, text, extends_re=extends_re, descriptor_re=descriptor_re,
        )
        if proto_meta is not None:
            proto_classes.append(proto_meta)

        # Cross-references from named files to obfuscated-package classes
        class_references.extend(
            _extract_class_references_from_text(path, text, root, obf_dir)
        )

        for line_no, line in enumerate(text.splitlines(), 1):
            for match in UUID_RE.finditer(line):
                uuids.append(
                    {
                        "file": str(path),
                        "line": line_no,
                        "value": match.group(0),
                    }
                )
            for match in HEX_RE.finditer(line):
                constants.append(
                    {
                        "file": str(path),
                        "line": line_no,
                        "value": match.group(0),
                    }
                )
            for match in PROTO_ACCESS_RE.finditer(line):
                accessor = match.group(0).split("(", 1)[0].strip()
                proto_accesses.append(
                    {
                        "file": str(path),
                        "line": line_no,
                        "accessor": accessor,
                    }
                )
            for match in PROTO_WRITE_OR_RE.finditer(line):
                proto_writes.append(
                    {
                        "file": str(path),
                        "line": line_no,
                        "target": match.group(1),
                        "op": match.group(2),
                        "value": match.group(3).strip(),
                    }
                )
            for match in PROTO_WRITE_ASSIGN_RE.finditer(line):
                proto_writes.append(
                    {
                        "file": str(path),
                        "line": line_no,
                        "target": match.group(1),
                        "op": "=",
                        "value": match.group(2).strip(),
                    }
                )
            for match in CALL_EDGE_RE.finditer(line):
                target = f"{match.group(1)}.{match.group(2)}"
                call_edges.append(
                    {
                        "file": str(path),
                        "line": line_no,
                        "target": target,
                    }
                )

    return {
        "uuids": sorted(uuids, key=lambda row: (row["value"], row["file"], row["line"])),
        "constants": sorted(
            constants, key=lambda row: (row["value"], row["file"], row["line"])
        ),
        "proto_accesses": sorted(
            proto_accesses, key=lambda row: (row["accessor"], row["file"], row["line"])
        ),
        "proto_writes": sorted(
            proto_writes,
            key=lambda row: (row["target"], row["op"], row["file"], row["line"]),
        ),
        "enum_maps": sorted(
            enum_maps,
            key=lambda row: (row["enum_class"], row["int_value"], row["file"], row["line"]),
        ),
        "switch_maps": sorted(
            switch_maps,
            key=lambda row: (row["switch_expr"], row["case_value"], row["file"], row["line"]),
        ),
        "call_edges": sorted(
            call_edges, key=lambda row: (row["target"], row["file"], row["line"])
        ),
        "proto_classes": sorted(
            proto_classes, key=lambda row: (row["class_name"],)
        ),
        "class_references": sorted(
            class_references,
            key=lambda row: (row["target_class"], row["source_package"], row["file"]),
        ),
    }
