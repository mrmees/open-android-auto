# Contributing

Contributions to expand and improve these protocol buffer definitions are welcome. This document covers the conventions used in the repository.

## Adding New Messages

1. Identify the correct category directory under `oaa/`. See the [README](README.md) for category descriptions.
2. Create your `.proto` file with the appropriate naming convention (see below).
3. Use the correct package namespace based on file type.
4. Add inline comments documenting observed field values and behavior.
5. Ensure the file compiles cleanly: `protoc --proto_path=. --cpp_out=/tmp oaa/<category>/YourFile.proto`

## File Naming

Files follow a suffix convention that determines their package:

| Suffix | Package | Example |
|--------|---------|---------|
| `*Message.proto` | `oaa.proto.messages` | `PingRequestMessage.proto` |
| `*Data.proto` | `oaa.proto.data` | `VideoConfigData.proto` |
| `*Enum.proto` | `oaa.proto.enums` | `StatusEnum.proto` |
| `*IdsEnum.proto` | `oaa.proto.ids` | `ControlMessageIdsEnum.proto` |

## Import Conventions

Use the `oaa/<category>/File.proto` import path:

```protobuf
import "oaa/common/StatusEnum.proto";
import "oaa/video/VideoConfigData.proto";
```

Do not use relative paths. The proto root is the repository root.

## Package Declarations

Every file must declare its package matching the suffix convention:

```protobuf
syntax = "proto3";

import "oaa/common/StatusEnum.proto";

package oaa.proto.messages;

message MyNewRequest {
    // fields
}
```

## Documenting Fields

Inline comments are the primary documentation method. Include:

- **Observed values** from live captures or APK analysis
- **Behavioral notes** (what happens if a field is missing, wrong, etc.)
- **Source references** (APK class names, firmware versions where observed)

Example:

```protobuf
message ServiceDiscoveryRequest {
    // APK class: wbx.java (AA v16.1)
    // Confirmed as PNG images via live capture (Samsung S25 Ultra, 2026-02-24)
    optional bytes phone_icon_small = 1;   // 32x32 PNG
    optional bytes phone_icon_medium = 2;  // 64x64 PNG
    optional bytes phone_icon_large = 3;   // 128x128 PNG

    optional string device_name = 4;
    optional string device_brand = 5;
}
```

## Verification Framework

Every `.proto` file in this repo has a corresponding `.audit.yaml` sidecar that tracks **how we know** each message and field is correct. If you add or modify a proto, you must update (or create) the matching sidecar.

### Confidence Tiers

| Tier | Evidence Required | Meaning |
|------|-------------------|---------|
| **Gold** | OEM wire capture | Production-confirmed |
| **Silver** | 2+ distinct evidence types | Corroborated independently |
| **Bronze** | Any single evidence source | Directionally correct |
| **Unverified** | None yet | Known to exist, not confirmed |

Tiers are computed deterministically from evidence — see [`docs/verification/01-confidence-tiers.md`](docs/verification/01-confidence-tiers.md).

### Audit Sidecars (`.audit.yaml`)

Each proto file gets a co-located sidecar with the same basename:

```
oaa/sensor/NightModeData.proto       ← proto definition
oaa/sensor/NightModeData.audit.yaml  ← evidence + confidence
```

When adding a new proto:
1. Create the `.audit.yaml` alongside it
2. Record at least one evidence entry (APK analysis, DHU observation, etc.)
3. Run `annotate.py` to sync confidence comments into the proto file

Sidecar format and schema: [`docs/verification/02-audit-trail-format.md`](docs/verification/02-audit-trail-format.md)

### Annotation Tool

After creating or updating sidecars, refresh the inline confidence comments in proto files:

```bash
python -m analysis.tools.seed_import.annotate oaa/<category>
```

This reads `.audit.yaml` files and adds/updates confidence comments above each message and on each field line. The cross-version promotion tool (`analysis/tools/cross_version/run.py --promote`) runs this automatically after promoting sidecars.

### Verification Procedures

Step-by-step procedures for gathering each evidence type are documented in [`docs/verification/03-verification-procedures.md`](docs/verification/03-verification-procedures.md).

## Proto Syntax

All definitions use **proto3**. The original aasdk used proto2; these have been migrated.

Use `optional` for fields where absence is meaningful (proto3 tracks presence for `optional` fields). Use bare field declarations where zero-value and absent are equivalent.

## Pull Requests

1. Fork the repository and create a feature branch.
2. Ensure all proto files compile without errors.
3. Include context in your PR description: how were the new fields/messages discovered? Live capture, APK decompilation, binary analysis?
4. One logical change per PR. Adding a new channel's messages is one PR; fixing field comments across multiple files is another.

## Capture-Based Proto Validation

When changing protobuf schemas that are used in stream decoding, run the
non-media capture validator and include results in your PR:

```bash
PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py \
  --capture analysis/captures/non_media/<capture>.jsonl \
  --baseline analysis/baselines/non_media/<capture>.normalized.json
```

If your schema change is intentional and changes decoded output, update the
baseline explicitly with rationale:

```bash
PYTHONPATH=. python3 analysis/tools/proto_stream_validator/run.py \
  --capture analysis/captures/non_media/<capture>.jsonl \
  --baseline analysis/baselines/non_media/<capture>.normalized.json \
  --bless \
  --reason "intentional proto update for <message>"
```

## License

All contributions must be compatible with **GPLv3**. By submitting a pull request, you agree that your contributions are licensed under GPLv3.

See [LICENSE](LICENSE) for the full text.
