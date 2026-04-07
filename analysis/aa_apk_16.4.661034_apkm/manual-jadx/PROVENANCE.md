# Manual JADX Provenance

This directory preserves single-class JADX recoveries for a small set of 16.4.661034 classes whose checked-in bulk decompile under `jadx-output/sources/` is incomplete or materially less useful.

## Why This Exists

The normal bulk tree at `analysis/aa_apk_16.4.661034_apkm/jadx-output/sources/` contains these classes already, but several key methods are stubbed with `UnsupportedOperationException` or reduced to partial warnings. The copies here preserve the more complete raw single-class recoveries so later analysis does not depend on transient `/tmp` output from a prior session.

## Scope

Recovered classes copied into `manual-jadx/defpackage/`:

- `rcp.java` from `classes2.dex`
- `rco.java` from `classes2.dex`
- `rdt.java` from `classes.dex`
- `red.java` from `classes.dex`
- `rcn.java` from `classes2.dex`

## Source APK Tree

- APK snapshot: `analysis/aa_apk_16.4.661034_apkm/`
- Decompiled resources:
  - `analysis/aa_apk_16.4.661034_apkm/jadx-output/resources/classes.dex`
  - `analysis/aa_apk_16.4.661034_apkm/jadx-output/resources/classes2.dex`
  - `analysis/aa_apk_16.4.661034_apkm/jadx-output/resources/classes3.dex`
  - `analysis/aa_apk_16.4.661034_apkm/jadx-output/resources/classes4.dex`

## Recovery Origin

These files were recovered during an interrupted 2026-03-29 session and first existed in temporary output directories:

- `/tmp/jadx-rcp/rcp.java`
- `/tmp/jadx-rco/rco.java`
- `/tmp/jadx-rdt/rdt.java`
- `/tmp/jadx-red/red.java`
- `/tmp/jadx-rcn/rcn.java`

They were copied here so the paths are stable and repo-local.

## Reproduction Status

The preserved `/tmp/jadx-*.log` files only record output paths:

- `INFO  - loading ...`
- `INFO  - Saving class 'defpackage.<class>' to file '/tmp/jadx-<class>/<class>.java'`
- `INFO  - done`

As of 2026-03-29, the exact JADX argv that produced these stronger recoveries is still unresolved. Fresh attempts with the current local JADX binary using both:

- minimal `jadx --single-class ... --single-class-output ...`
- and `jadx --show-bad-code --comments-level debug --decompilation-mode simple --single-class ...`

did not byte-match the preserved files. They produced weaker output for several classes, while the copies in this directory retain materially more decompiled method bodies.

The source dex files above are still the correct starting point for reproducing or improving this batch later.

## Interpretation Notes

- `rcp`, `rco`, and `rcn` recover transport/framing logic that is mostly opaque in the bulk tree.
- `red` recovers substantially more of the TLS/security helper than the bulk tree exposes.
- `rdt` is included for path stability with the same recovery batch even though its bulk-tree version is already more readable than the others.
