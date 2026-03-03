# 04 — Source Provenance

## Valid Sources

These are the only sources accepted as evidence for verification claims. Each maps to one or more evidence types defined in [01-confidence-tiers.md](01-confidence-tiers.md).

### APK (Any Available Version)

**Evidence types:** `apk_static`, `cross_version`

Decompiled Android Auto APKs obtained via jadx from publicly available APK distributions. Currently available versions: 15.9, 16.1, 16.2.

Provides proto structure, field names and numbers, enum values, string constants, call graphs, class references, and type relationships. Cross-version comparison of these artifacts produces `cross_version` evidence.

APK analysis is the primary source for proto schema discovery. Obfuscated class names differ between versions — matching is done by enum value fingerprints and structural patterns, not by name.

### DHU Observations

**Evidence type:** `dhu_observation`

Google's Desktop Head Unit test harness (version 2.1). Runtime observations including message flow, sensor processing pipelines, channel lifecycle, and logcat output.

Provides behavioral evidence that complements static analysis. However, the DHU is a test environment maintained by Google for development purposes. Its behavior may diverge from production OEM implementations. For this reason, DHU observations are valid for Bronze and Silver tiers but **never sufficient for Gold**.

### OEM Wire Captures

**Evidence type:** `oem_capture`

Packet captures from production OEM Android Auto head units. This is the highest-fidelity source — it captures the actual protocol behavior between a phone and a real head unit in a production environment.

OEM captures are the only evidence type that can directly promote a claim to Gold tier. A single OEM capture confirming a behavior is sufficient.

### Official Google Documentation

**Evidence types:** Treated as `apk_static` (published API contracts) or noted in evidence description.

Published Android Auto SDK documentation, protocol documentation, and developer guides from Google's official channels. While authoritative, official documentation is often incomplete — it covers the public API surface but not internal protocol details.

---

## Excluded Sources

The following sources are **explicitly excluded** from use as evidence. Each exclusion has a specific rationale.

### Third-Party Reverse Engineering Blogs and Articles

**Rationale:** Unverifiable methodology. Published analyses may contain errors, assumptions, or speculation presented as fact. These errors propagate through the community when cited without independent verification.

If a blog post points to something interesting, treat it as a **hint for where to look** — then verify independently from a valid source.

### Forum Posts (XDA, Reddit, etc.)

**Rationale:** Anecdotal evidence, often conflated with speculation. Forum posts lack the methodological rigor needed for protocol documentation. Claims are not independently verifiable and frequently mix observation with interpretation.

Same rule applies: use as hints, verify independently.

### aasdk Source Code (f1xpl/aasdk and All Forks)

**Rationale: Clean-room risk.** This is the most critical exclusion.

This project is licensed GPL-3.0. The aasdk project contains proto definitions and protocol implementations obtained through reverse engineering with unknown methodology and unclear provenance. Using aasdk as an evidence source creates legal exposure:

1. **Derivation chain is unclear.** We cannot verify how aasdk's proto definitions were obtained or whether they were derived from sources that would create licensing obligations incompatible with our project.
2. **Clean-room integrity.** Our protocol definitions must be independently derived from primary sources (APK analysis, DHU observation, OEM captures). If we cite aasdk as evidence, our "independent derivation" claim is compromised.
3. **Error propagation.** Any errors in aasdk's definitions would propagate into our reference if we treat it as a source. Independent derivation naturally avoids this.

**Do not read, reference, or cite aasdk source code when producing evidence entries.** If you happen to know something from aasdk, you must still derive the evidence independently from a valid source. The evidence entry must cite only the valid source.

### Unofficial Documentation

**Rationale:** Provenance unverifiable. Documentation not published through official Google channels may be outdated, speculative, or derived from excluded sources.

### Leaked Internal Documents

**Rationale:** Legal risk and provenance concerns. Internal documents obtained without authorization create legal exposure regardless of their accuracy. They may also be outdated or reflect internal states that never shipped.

---

## Why These Rules Exist

### Clean-Room Integrity

Every claim in this protocol reference must be independently verifiable from primary sources. A contributor should be able to follow the evidence trail from any proto field back to the raw source material and reproduce the finding. This is not just good practice — it is a legal requirement for a clean-room reverse engineering effort.

### Legal Protection

This project is GPL-3.0 licensed. Clean derivation from primary sources (publicly available APKs, runtime observations, wire captures, official docs) ensures that our protocol definitions stand on their own legal footing. Mixing in evidence from projects with unclear provenance (particularly aasdk) would undermine this.

### Reproducibility

Any contributor should be able to take the cited source, apply the described method, and arrive at the same conclusion. This is why evidence entries include both the source and the method — the combination must be reproducible.

### Trust

Head unit developers depending on this reference need confidence that the provenance is clean. They need to know that using our proto definitions does not create transitive legal obligations or embed unverified claims from unknown sources.

---

## For Contributors

### Citing Sources in Evidence Entries

Every evidence entry should include:

- **type** — One of the four evidence types (`apk_static`, `dhu_observation`, `oem_capture`, `cross_version`)
- **source** — Specific source (e.g., `APK 16.2`, `DHU 2.1`, `OEM [unit model]`)
- **method** — How the evidence was obtained (e.g., `bfs_trace`, `logcat capture`, `pcap analysis`)
- **detail** — What was observed and why it supports the claim

Example:

```yaml
evidence:
  - type: apk_static
    source: "APK 16.2 (jadx decompilation)"
    method: enum_match
    detail: "Field number 3 maps to SPEED in SensorType enum across classes vfn, wab, xcd"
  - type: dhu_observation
    source: "DHU 2.1 (kitchen_sink.ini config)"
    method: logcat
    detail: "CAR.SENSOR.LITE tag shows speed sensor events processed at 1Hz"
```

### When You Find Corroborating Information in an Excluded Source

You will inevitably encounter information in blog posts, forum threads, or aasdk that seems to confirm what you are finding. This is fine — and even expected. The rule is:

1. **You may use excluded sources as hints** for where to look in valid sources.
2. **Your evidence entry must cite only the valid source** where you independently confirmed the finding.
3. **Do not mention the excluded source** in the evidence entry. The evidence trail must stand on its own.

The distinction is between "I looked at aasdk and copied their field names" (not acceptable) and "I noticed aasdk uses field 3 for speed, so I checked APK 16.2 and independently confirmed field 3 maps to SPEED in the SensorType enum" (acceptable — but cite only the APK finding).

### When in Doubt

If you are unsure whether a source qualifies or how to cite evidence, raise the question in your PR. It is better to ask than to introduce provenance ambiguity into the reference.
