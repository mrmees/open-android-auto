from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from analysis.tools.proto_stream_validator.descriptors import build_descriptor_bundle

from .attribution import attribute_record
from .coverage import build_coverage_manifest
from .io import load_dhu_capture, load_session_json, load_vw_capture
from .manifests import (
    emit_candidate_json,
    emit_classification_json,
    emit_coverage_json,
    emit_sdp_values_json,
)
from .models import UnifiedRecord
from .reports import (
    emit_candidate_report,
    emit_classification_report,
    emit_coverage_report,
    emit_sdp_values_report,
)
from .sdp_decode import decode_sdp_request, decode_sdp_response
from .tier_classifier import classify_capture


def _discover_dhu_files(dhu_dir: Path) -> tuple[Path | None, Path | None]:
    """Find aa_messages*.jsonl + channel_map*.json in a DHU baseline directory.

    Some baselines use the canonical `aa_messages.jsonl` / `channel_map.json`
    pair (captures/general). Others use suffixed names like
    `aa_messages_idle-baseline.jsonl` / `channel_map_idle-baseline.json`
    (every other DHU baseline directory). This helper handles both.

    Returns (jsonl_path, channel_map_path), with either side as None if
    the file is missing. The channel map is optional — load_dhu_capture
    falls back to an empty map with a WARNING.
    """
    jsonl: Path | None = None
    channel_map: Path | None = None

    canonical_jsonl = dhu_dir / "aa_messages.jsonl"
    if canonical_jsonl.exists():
        jsonl = canonical_jsonl
    else:
        candidates = sorted(dhu_dir.glob("aa_messages*.jsonl"))
        if candidates:
            jsonl = candidates[0]

    canonical_map = dhu_dir / "channel_map.json"
    if canonical_map.exists():
        channel_map = canonical_map
    else:
        candidates = sorted(dhu_dir.glob("channel_map*.json"))
        if candidates:
            channel_map = candidates[0]

    return jsonl, channel_map


def _fix_capture_readme(readme: Path, out_dir: Path) -> None:
    """One-line direction-table swap + append 'Analysis Outputs' section.

    Idempotent: safe to re-run. The direction-table swap targets the EXACT
    wrong lines from the current README. The Analysis Outputs section is
    appended only if not already present.
    """
    if not readme.exists():
        return

    text = readme.read_text(encoding="utf-8")

    # Fix the swapped direction table. The actual README file uses single
    # spaces between cells (not the double space the plan snippet showed),
    # so the literals here MUST match the on-disk format byte-for-byte.
    # Both single- and double-space variants are handled defensively because
    # different editors may have normalized the whitespace.
    wrong_req_variants = (
        "| `sdp_request.bin` | 877 | Service Discovery Request from VW HU → phone |",
        "| `sdp_request.bin`  | 877 | Service Discovery Request from VW HU → phone |",
    )
    right_req_variants = (
        "| `sdp_request.bin` | 877 | Service Discovery Request from phone → VW HU |",
        "| `sdp_request.bin`  | 877 | Service Discovery Request from phone → VW HU |",
    )
    wrong_resp_variants = (
        "| `sdp_response.bin` | 610 | Service Discovery Response from phone → VW HU |",
        "| `sdp_response.bin`  | 610 | Service Discovery Response from phone → VW HU |",
    )
    right_resp_variants = (
        "| `sdp_response.bin` | 610 | Service Discovery Response from VW HU → phone |",
        "| `sdp_response.bin`  | 610 | Service Discovery Response from VW HU → phone |",
    )

    # Idempotent swap: only replace wrong → right if a right variant is not
    # already present. This guards against double-running on a partially-
    # fixed file.
    if not any(rv in text for rv in right_req_variants):
        for wv, rv in zip(wrong_req_variants, right_req_variants):
            if wv in text:
                text = text.replace(wv, rv)
                break
    if not any(rv in text for rv in right_resp_variants):
        for wv, rv in zip(wrong_resp_variants, right_resp_variants):
            if wv in text:
                text = text.replace(wv, rv)
                break

    # Append Analysis Outputs section if not already present.
    marker = "## Analysis Outputs"
    if marker not in text:
        # Build a relative path from the README's directory to the output dir.
        # captures/oem-vw-mib3oi-2026-04-06/README.md → ../../analysis/reports/oem-vw/
        try:
            rel = Path(
                "../../" + str(out_dir).lstrip("./").lstrip("/")
            )
        except Exception:
            rel = Path(out_dir)
        text += "\n\n## Analysis Outputs\n\n"
        text += f"Phase 7 analysis artifacts live under `{out_dir}/`:\n\n"
        text += (
            f"- [`sdp-values.md`]({rel}/sdp-values.md) — production SDP values "
            f"(HeadUnitInfo, 13 channels)\n"
        )
        text += f"- [`sdp-values.json`]({rel}/sdp-values.json) — machine-readable SDP values\n"
        text += (
            f"- [`msg-type-classification.md`]({rel}/msg-type-classification.md) — "
            f"per-msg-type fragment classification (from plan 07-01)\n"
        )
        text += (
            f"- [`msg-type-classification.json`]({rel}/msg-type-classification.json) — "
            f"machine-readable classification\n"
        )
        text += (
            f"- [`coverage-manifest.md`]({rel}/coverage-manifest.md) — VW session "
            f"coverage (observed / intrinsic gaps / comparative gaps / anomalies)\n"
        )
        text += (
            f"- [`coverage.json`]({rel}/coverage.json) — machine-readable coverage "
            f"manifest with `baseline_snapshot_hash`\n"
        )
        text += (
            f"- [`candidate-oem-only-msg-types.md`]({rel}/candidate-oem-only-msg-types.md) — "
            f"msg_types seen in VW but not DHU baselines (filtered through fragment "
            f"classification, labeled `candidate`)\n"
        )
        text += (
            f"- [`candidate-oem-only-msg-types.json`]({rel}/candidate-oem-only-msg-types.json) — "
            f"machine-readable candidate list\n\n"
        )
        text += (
            "**Correction applied 2026-04-07:** the SDP direction labels in the file "
            "table above were swapped. Plan 07-02 verified by direct decode that "
            "`sdp_request.bin` is phone→HU and `sdp_response.bin` is HU→phone, and "
            "fixed the table in a targeted one-line edit.\n"
        )

    readme.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the VW capture parser.

    Wires the full 07-01 + 07-02 pipeline:
        load → classify → SDP decode → attribute → coverage manifest →
        OEM-only diff → emit 8 reports → fix capture README.
    """
    parser = argparse.ArgumentParser(description="VW MIB3 OI capture parser")
    parser.add_argument(
        "--vw",
        type=Path,
        required=True,
        help="VW capture directory (must contain messages.jsonl and session.json)",
    )
    parser.add_argument(
        "--dhu",
        type=Path,
        action="append",
        default=[],
        help="DHU baseline capture directory (repeatable)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output report directory",
    )
    args = parser.parse_args(argv)

    # Validates capture_version is the JSON integer 5 (numeric, not string).
    load_session_json(args.vw / "session.json")

    # Load VW records.
    vw_records = list(
        load_vw_capture(args.vw / "messages.jsonl", capture_id=args.vw.name)
    )

    # Build descriptor bundle once.
    repo_root = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="oem_vw_parser_bundle_") as td:
        bundle = build_descriptor_bundle(repo_root=repo_root, out_dir=Path(td))

        # ---------------- 07-01: classification ----------------
        classified, profile = classify_capture(vw_records, bundle)

        # Compute capture window from record timestamps.
        ts_values = [r.ts_ms for r in vw_records]
        capture_window_s = (
            (max(ts_values) - min(ts_values)) / 1000.0 if ts_values else 0.0
        )

        emit_classification_report(
            classified,
            profile,
            args.out / "msg-type-classification.md",
            capture_id=args.vw.name,
            capture_window_s=capture_window_s,
            total_records=len(vw_records),
        )
        emit_classification_json(
            classified,
            profile,
            args.out / "msg-type-classification.json",
            capture_id=args.vw.name,
            total_records=len(vw_records),
        )

        # ---------------- 07-02: SDP extraction ----------------
        sdp = decode_sdp_response(bundle, args.vw / "sdp_response.bin")
        req = decode_sdp_request(bundle, args.vw / "sdp_request.bin")
        emit_sdp_values_report(sdp, req, args.out / "sdp-values.md")
        emit_sdp_values_json(sdp, req, args.out / "sdp-values.json")

        # ---------------- 07-02: Attribution ----------------
        attributed = [attribute_record(cr, sdp) for cr in classified]

        # ---------------- 07-02: Load DHU baselines ----------------
        dhu_records: list[UnifiedRecord] = []
        for dhu_dir in args.dhu:
            jsonl, channel_map = _discover_dhu_files(dhu_dir)
            if jsonl is not None:
                dhu_records.extend(
                    load_dhu_capture(
                        jsonl,
                        capture_id=dhu_dir.name,
                        channel_map_path=channel_map,
                    )
                )

        # ---------------- 07-02: Coverage manifest ----------------
        manifest = build_coverage_manifest(
            classified=classified,
            attributed=attributed,
            sdp=sdp,
            capture_duration_s=capture_window_s,
            dhu_baseline_paths=list(args.dhu),
            dhu_records=dhu_records,
            capture_id=args.vw.name,
        )
        emit_coverage_report(manifest, args.out / "coverage-manifest.md")
        emit_coverage_json(manifest, args.out / "coverage.json")

        # ---------------- 07-02: OEM-only candidate diff ----------------
        # Filter VW keys through fragment classification BEFORE the diff.
        vw_keys = {
            (cr.record.msg_type, cr.record.direction)
            for cr in classified
            if cr.label != "continuation_or_garbage"
        }
        dhu_keys = {(r.msg_type, r.direction) for r in dhu_records}
        oem_only = vw_keys - dhu_keys

        # Per-msg_type and per-(msg_type, direction) views.
        candidates_by_mt: dict[int, dict] = {}
        candidates_by_mt_dir: dict[tuple[int, str], dict] = {}
        ar_by_cr_id = {id(ar.classified): ar for ar in attributed}
        for cr in classified:
            key = (cr.record.msg_type, cr.record.direction)
            if key not in oem_only:
                continue
            ar = ar_by_cr_id.get(id(cr))
            attribution_method = ar.attribution_method if ar else "unattributed"

            existing = candidates_by_mt.get(
                cr.record.msg_type,
                {"count": 0, "tier": cr.tier, "attribution_method": attribution_method},
            )
            existing["count"] += 1
            existing["tier"] = cr.tier
            existing["attribution_method"] = attribution_method
            candidates_by_mt[cr.record.msg_type] = existing

            existing_pair = candidates_by_mt_dir.get(
                key,
                {"count": 0, "tier": cr.tier, "attribution_method": attribution_method},
            )
            existing_pair["count"] += 1
            existing_pair["tier"] = cr.tier
            existing_pair["attribution_method"] = attribution_method
            candidates_by_mt_dir[key] = existing_pair

        emit_candidate_report(
            candidates_by_mt,
            candidates_by_mt_dir,
            args.out / "candidate-oem-only-msg-types.md",
        )
        emit_candidate_json(
            candidates_by_mt,
            candidates_by_mt_dir,
            args.out / "candidate-oem-only-msg-types.json",
        )

        # ---------------- 07-02: README fix ----------------
        _fix_capture_readme(args.vw / "README.md", args.out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
