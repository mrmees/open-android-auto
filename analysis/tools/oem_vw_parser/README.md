# OEM VW Parser

VW MIB3 OI capture parser — fragment classification, SDP extraction, coverage manifesting, OEM-only candidate diff.

## Quick run

```bash
PYTHONPATH=. pytest analysis/tools/oem_vw_parser/tests -v
```

## End-to-end CLI

```bash
python3 -m analysis.tools.oem_vw_parser.run \
    --vw captures/oem-vw-mib3oi-2026-04-06 \
    --dhu captures/general \
    --dhu captures/idle-baseline \
    --dhu captures/music-playback \
    --dhu captures/active-navigation \
    --out analysis/reports/oem-vw/
```

See `.planning/phases/07-vw-capture-analysis/07-CONTEXT.md` for the locked design contract.
