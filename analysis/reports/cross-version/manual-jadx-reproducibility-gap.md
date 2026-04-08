# Manual-JADX Reproducibility Gap — 16.4.661034 Salvaged Classes

**Scope:** 5 manually-recovered class files under
`analysis/aa_apk_16.4.661034_apkm/manual-jadx/defpackage/`:
`rcn.java`, `rco.java`, `rcp.java`, `rdt.java`, `red.java`.

**Purpose:** This document states explicitly what CANNOT be concluded from
these salvaged classes. Their recovery history is documented separately in
[`PROVENANCE.md`](../../aa_apk_16.4.661034_apkm/manual-jadx/PROVENANCE.md) —
this document focuses on the limits that history creates.

The canonical 16.4 analysis for Phase 8 runs against the indexed
`16.4.661014` build (see [`16-4-delta-report.md`](./16-4-delta-report.md)). The
5 files discussed here come from `16.4.661034`, a different build, recovered
under conditions that cannot be reproduced.

## Non-Claims — What the 5 Salvaged Classes CANNOT Support

The following claims CANNOT be made from `rcn.java`, `rco.java`, `rcp.java`,
`rdt.java`, or `red.java` in `analysis/aa_apk_16.4.661034_apkm/manual-jadx/defpackage/`:

1. **No cross-version structural comparison.** The bulk JADX tree stubs these
   classes with `UnsupportedOperationException`. The manual single-class
   recoveries cannot be compared field-by-field against 15.9/16.1/16.2 equivalents
   because the bulk tree would have to be re-decompiled for a fair comparison,
   and the argv that produced the stronger recoveries is unresolved.

2. **No byte-match reproducibility.** Fresh JADX runs with both minimal
   `--single-class` and `--show-bad-code --comments-level debug --decompilation-mode simple`
   flags do not reproduce the preserved files. Without the exact argv, the
   recoveries are not independently verifiable.

3. **No confidence tier promotion.** These classes MUST NOT be cited as evidence
   for Bronze→Silver or Silver→Gold promotion in any sidecar. Any sidecar whose
   only 16.4 evidence comes from these salvaged classes stays at its prior tier.

4. **No methodology validation.** The salvaged classes cannot be used to
   validate or contradict the cross-version checker's methodology, because the
   input data itself is unrepeatable.

5. **No build-number claim.** The manual-jadx files come from 16.4.661034.
   The canonical 16.4 for Phase 8 and all downstream cross-version analysis is
   16.4.661014. Claims about "16.4 behavior" from these 5 classes are implicitly
   claims about 661034, not the canonical build.

## References

- **Recovery history:** [`analysis/aa_apk_16.4.661034_apkm/manual-jadx/PROVENANCE.md`](../../aa_apk_16.4.661034_apkm/manual-jadx/PROVENANCE.md) — documents
  the 2026-03-29 salvage session, the unresolved JADX argv, and what each
  of the 5 classes covers (transport/framing for `rcn`/`rco`/`rcp`, TLS /
  security helpers for `red`, path-stability inclusion for `rdt`).
- **Canonical 16.4 analysis (661014 build):** [`16-4-delta-report.md`](./16-4-delta-report.md) — the
  structural delta report for Phase 8. Every cross-version conclusion about
  16.4 comes from there, not from the 5 salvaged classes.
- **Phase 8 requirement:** XVER-05 in [`.planning/REQUIREMENTS.md`](../../../.planning/REQUIREMENTS.md).
- **Related honesty deliverables:** Phase 7's TIER-05 non-claim boundary (VW
  OEM capture framing-layer limits) applies the same spirit to a different
  evidence gap — "we have the files, but here is explicitly what they can't
  support." Consistent framing across the project.

## Why This Doc Exists

XVER-05 is an honesty deliverable. The 5 files exist in the repo — nothing
stops a future reader from citing them as evidence. This document makes doing
so structurally impossible without tripping an explicit non-claim.

Any sidecar entry, report, or downstream claim that would rely on these files
as evidence must first reconcile with the 5 non-claims above. If the claim
cannot survive those constraints, it cannot cite the salvaged classes.

The rule is simple: these 5 files are archeological artifacts. Treat them as
unrepeatable reference material, never as evidence that passes a confidence
tier bar.
