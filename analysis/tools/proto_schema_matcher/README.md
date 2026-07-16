# Proto Schema Matcher

Statically matches canonical `oaa/**/*.proto` messages to obfuscated Android
Auto protobuf-lite classes. The matcher combines exact normalized schema shape
with conservative message-ID observations from control and explicitly identified
service handlers, plus message names recovered from nearby validation logs.
Proto files explicitly marked `confidence: retracted` are excluded from the
canonical graph.

Field-number-labelled message edges propagate in both directions from trusted
parents. Enum fields use resolved protobuf-lite verifier members and numeric
domains; generated `UNRECOGNIZED` constants and canonical proto3 zero sentinels
are normalized before matching.

It does not require a phone, head unit, emulator, or wire capture.

## Requirements

- `protoc` in `PATH`
- Python protobuf runtime (`google.protobuf`)
- A JADX output tree or an APK index `proto_classes.json`

## 17.3 smoke command

Run from the repository root:

```bash
PYTHONPATH=. python3 -m analysis.tools.proto_schema_matcher.run \
  --jadx-root /tmp/android-auto-17.3-jadx \
  --version 17.3.662804-release \
  --apk-sha256 1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344 \
  --output-json analysis/reports/cross-version/17-3-schema-match.json \
  --output-md analysis/reports/cross-version/17-3-schema-match.md
```

For a previously indexed APK, use `--proto-classes-json` instead. Dispatch
refinement is available only when `--jadx-root` is supplied.

## Confidence

- `high`: exact schema match plus a unique compatible static service/semantic dispatch observation
- `medium`: globally unique normalized schema shape, or a graph-resolved match
- `none`: no candidate or multiple structurally identical candidates remain

The tool never chooses arbitrarily among ambiguous candidates. When explicit
handler evidence identifies a class whose local schema differs, the JSON and
Markdown reports include a field-level structural delta rather than accepting it.
