# Research Archive

This repository is not only a `.proto` source tree, it also includes the reverse-engineering research used to build and validate those definitions.

Use [`archive/README.md`](archive/README.md) for a quick map of imported material.

If you want to build your own head unit implementation, start here:

1. Read protocol context and gotchas in [`../docs/`](../docs).
2. Use archived deep-dive docs in [`archive/openauto-prodigy/docs/`](archive/openauto-prodigy/docs).
3. Re-run or adapt analysis tooling in [`archive/openauto-prodigy/tools/`](archive/openauto-prodigy/tools).
4. Review capture summaries in [`archive/openauto-prodigy/captures/`](archive/openauto-prodigy/captures).
5. Pull older cross-vendor reverse-engineering context from [`archive/openauto-pro-community/docs/`](archive/openauto-pro-community/docs).
6. Inspect reproducible APK indexing tooling at [`archive/openauto-prodigy/analysis/tools/apk_indexer/`](archive/openauto-prodigy/analysis/tools/apk_indexer).
7. Inspect generated AA v16.1 index outputs at [`archive/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-index/`](archive/openauto-prodigy/analysis-projection/android_auto_16.1.660414-release_161660414/apk-index).

## What Is Included

- APK and protocol analysis docs (`aa-apk-deep-dive`, `apk-indexing`, `apk-proto-reference`, cross-reference docs)
- Proto validation reports and milestone writeups
- Descriptor decoding and proto comparison scripts
- Matching manifests and machine-readable validation output (`json`)
- Phase-A decode artifacts and matched/unmatched extracted proto outputs
- Capture findings/timelines for selected probes
- Legacy/adjacent OpenAuto community firmware analysis notes (Alpine/Kenwood/Pioneer/Sony)
- APK indexer implementation with tests
- Generated JSON index outputs for Android Auto APK v16.1 (`constants`, `proto_accesses`, `proto_writes`, `call_edges`, `enum_maps`, `switch_maps`, `uuids`)

## What Is Not Included

- Raw phone logcat captures from testing sessions are intentionally excluded from this archive copy.
- Large generated SQLite index databases are intentionally excluded; use included JSON outputs or regenerate locally.
- Full decompiled APK source trees are intentionally excluded from this public archive copy due copyright/licensing risk; regenerate privately if needed.
- This archive does not claim perfect completeness; unresolved/unknown fields remain marked as such in the source material.

## Usage Notes

- Paths in archived docs may still reference their original `openauto-prodigy` layout.
- Treat this archive as source material and implementation guidance, not a formal Google AA specification.
- Preserve attribution and license headers when reusing content.
