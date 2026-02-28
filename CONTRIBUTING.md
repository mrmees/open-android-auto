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
