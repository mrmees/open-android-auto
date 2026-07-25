# Proto Schema Matcher

Statically matches canonical `oaa/**/*.proto` messages to obfuscated Android
Auto protobuf-lite classes. The matcher combines exact normalized schema shape
with conservative message-ID observations from control and explicitly identified
service handlers, plus message names recovered from nearby validation logs.
Curated class-lineage anchors can confirm an identity across releases or
invalidate a legacy canonical name when call sites identify an unrelated bundled
Google library.

Proto files explicitly marked `confidence: retracted` are excluded from the
canonical graph.

Field-number-labelled message edges propagate in both directions from trusted
parents. Enum fields use resolved protobuf-lite verifier members and numeric
domains; generated `UNRECOGNIZED` constants and canonical proto3 zero sentinels
are normalized before matching.

Graph-resolved rows include the exact canonical/APK parent, field number, and
target edge used for the deduction. The report also lists child schema deltas
identified by dispatch/lineage-backed parents, allowing version changes to be
recorded without forcing a false exact match.

It does not require a phone, head unit, emulator, or wire capture.

## Requirements

- `protoc` in `PATH`
- Python protobuf runtime (`google.protobuf`)
- A JADX output tree or an APK index `proto_classes.json`

## 17.3 smoke command

Run from the repository root:

```bash
PYTHONPATH=. python3 -m analysis.tools.proto_schema_matcher.run \
  --jadx-root analysis/aa_apk_17.3.662804_apkm/jadx-output \
  --version 17.3.662804-release \
  --apk-sha256 1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344 \
  --lineage-yaml analysis/lineage/android-auto-17.3.yaml \
  --output-json analysis/aa_apk_17.3.662804_apkm/validation/17-3-schema-match-fresh.json \
  --output-md analysis/aa_apk_17.3.662804_apkm/validation/17-3-schema-match-fresh.md
```

The versioned JADX directory is intentionally ignored by Git. Its local
`PROVENANCE.md` records the source bundle, checksums, decompiler version, and
regeneration command. If the local tree is unavailable, restore the bundle and
decompile it there before running this command.

The smoke command writes into the ignored local analysis tree deliberately.
Compare a fresh result with the committed cross-version report before promoting
it; different JADX completeness can recover extra dispatch or enum evidence.

For a previously indexed APK, use `--proto-classes-json` instead. Dispatch
refinement is available only when `--jadx-root` is supplied.

## Confidence

- `high`: exact schema plus unique static dispatch, or a curated confirmed lineage anchor (including an explicitly reported schema/edge conflict)
- `medium`: globally unique normalized schema shape, or a graph-resolved match
- `none`: no candidate or multiple structurally identical candidates remain

An `invalidated` lineage never resolves a mapping. It quarantines the canonical
identity and every same-shape candidate because the historical schema was shown
to come from non-protocol code. Class-name continuity alone is not semantic
evidence.

The tool never chooses arbitrarily among ambiguous candidates. When explicit
handler evidence identifies a class whose local schema differs, the JSON and
Markdown reports include a field-level structural delta rather than accepting it.
