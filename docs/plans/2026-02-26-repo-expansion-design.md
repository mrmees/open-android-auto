# open-android-auto Repo Expansion Design

## Goal

Expand open-android-auto from a proto-only collection into the canonical open-source Android Auto protocol reference — covering protocol documentation, wireless Bluetooth setup, firmware analysis, and APK analysis tools.

## Audience

Developers building AA head units or clients.

## Repo Structure

```
open-android-auto/
├── proto/oaa/...                         (164 files, 13 categories — no change)
├── docs/
│   ├── protocol-overview.md              (exists)
│   ├── channel-map.md                    (exists)
│   ├── field-notes.md                    (exists)
│   ├── protocol-reference.md             (from openauto-prodigy)
│   ├── wireless-bluetooth-setup.md       (full BT wireless AA guide)
│   ├── video-resolution.md               (AA video resolution details)
│   ├── display-rendering.md              (display rendering/margins)
│   ├── phone-side-debug.md               (phone-side debugging)
│   ├── troubleshooting.md                (common issues runbook)
│   ├── protocol-cross-reference.md       (cross-reference)
│   └── decompiled_headunit_firmware/     (5 commercial HU analyses)
│       ├── alpine-halo9.md
│       ├── alpine-ilx-w650bt.md
│       ├── kenwood-dnx.md
│       ├── pioneer-dmh.md
│       └── sony-xav.md
├── analysis/
│   ├── README.md                         (disclaimer: personal dev tools, no current functionality)
│   ├── tools/                            (APK indexer scripts)
│   └── database/                         (pre-built SQLite DB)
├── research/                             (existing archive material — no change)
└── README.md                             (rewritten for expanded scope)
```

## Content Sources

| Destination | Source |
|-------------|--------|
| `docs/protocol-reference.md` | `openauto-prodigy/docs/aa-protocol-reference.md` |
| `docs/video-resolution.md` | `openauto-prodigy/docs/aa-video-resolution.md` |
| `docs/display-rendering.md` | `openauto-prodigy/docs/aa-display-rendering.md` |
| `docs/phone-side-debug.md` | `openauto-prodigy/docs/aa-phone-side-debug.md` |
| `docs/troubleshooting.md` | `openauto-prodigy/docs/aa-troubleshooting-runbook.md` |
| `docs/protocol-cross-reference.md` | `openauto-prodigy/docs/android-auto-protocol-cross-reference.md` |
| `docs/wireless-bluetooth-setup.md` | `openauto-prodigy/docs/OpenAutoPro_archive_information/bluetooth-wireless-aa-setup.md` |
| `docs/decompiled_headunit_firmware/*.md` | `openauto-prodigy/docs/OpenAutoPro_archive_information/firmware/*.md` |
| `analysis/tools/` | APK indexer scripts from openauto-prodigy analysis pipeline |
| `analysis/database/` | Pre-built SQLite database |

## What stays out

- openauto-prodigy-specific docs (design-philosophy, plugin-api, config-schema, roadmap)
- Pi deployment/installation docs
- Session handoffs, plans, baselines
- OAP disk image, extracted binaries, manual PDF

## README

Rewrite to reflect expanded scope: not just "proto files" but "the AA protocol reference." Link to all doc sections.
