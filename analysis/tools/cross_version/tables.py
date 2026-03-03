"""Markdown mapping table generator.

Generates per-category markdown tables showing obfuscated class names
and field counts across APK versions.
"""
from __future__ import annotations

import sqlite3
from collections import defaultdict
from pathlib import Path

from analysis.tools.proto_schema_validator.models import ProtoMapping


def _field_count(db_path: Path, class_name: str | None) -> int:
    """Query field count for a class from the DB."""
    if not class_name:
        return 0
    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM proto_fields WHERE class_name = ?",
            (class_name,),
        ).fetchone()
    finally:
        conn.close()
    return row[0] if row else 0


def generate_tables(
    db_paths: dict[str, Path],
    mappings: list[ProtoMapping],
    output_dir: Path,
) -> list[Path]:
    """Generate markdown mapping tables grouped by oaa/ category.

    Args:
        db_paths: Maps version label to DB path.
        mappings: ProtoMapping list.
        output_dir: Directory to write markdown files to.

    Returns:
        List of created file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    versions = sorted(db_paths.keys())

    # Group mappings by category (first directory under oaa/)
    categories: dict[str, list[ProtoMapping]] = defaultdict(list)
    for m in mappings:
        parts = Path(m.proto_file).parts
        if len(parts) >= 2:
            category = parts[1]  # oaa/<category>/...
        else:
            category = "other"
        categories[category].append(m)

    created: list[Path] = []

    for category, entries in sorted(categories.items()):
        lines = [
            f"# {category.replace('_', ' ').title()} - Cross-Version Mapping\n",
            f"**Mappings:** {len(entries)} | **Versions:** {', '.join(versions)}\n",
        ]

        # Table header
        version_cols = " | ".join(versions)
        field_cols = "/".join(versions)
        lines.append(
            f"| Proto Name | {version_cols} | Fields ({field_cols}) |"
        )
        lines.append(
            f"|{'---|' * (len(versions) + 2)}"
        )

        for m in sorted(entries, key=lambda x: x.proto_message):
            class_cells = []
            field_counts = []
            for v in versions:
                cls = m.apk_classes.get(v)
                class_cells.append(f"`{cls}`" if cls else "--")
                field_counts.append(str(_field_count(db_paths[v], cls)))

            classes_str = " | ".join(class_cells)
            fields_str = "/".join(field_counts)
            lines.append(
                f"| {m.proto_message} | {classes_str} | {fields_str} |"
            )

        lines.append("")  # trailing newline

        out_path = output_dir / f"{category}.md"
        out_path.write_text("\n".join(lines), encoding="utf-8")
        created.append(out_path)

    return created
