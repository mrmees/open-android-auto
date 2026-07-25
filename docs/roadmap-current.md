# Roadmap (Current)

## v1.0 Milestone — Complete (2026-03-04)

- APK v16.1 and v16.2 protobuf catalogs finalized with reproducible indexing workflow.
- GAL gap coverage complete — all 14 channel handler types have proto definitions and documentation.
- GAL proto verification complete — 194 Gold protos across all 14 channels, 29 retractions, 75 schema fixes.
- SDP proto verification complete — 112 Gold protos, full ChannelDescriptor tree verified.
- 234 `.proto` files across 17 categories in the `oaa/` tree.
- Non-media capture-based protobuf regression validation (`proto_stream_validator`) operational with locked baselines.
- Cross-version comparison tooling (v16.1 vs v16.2) built and producing diff reports.
- Channel documentation written for all major channels (`docs/channels/`).
- Session lifecycle interaction specs completed (`docs/interactions/`).
- Wire capture TLS decryption pipeline working (Frida-based master secret extraction).
- Verification framework with confidence tiers and audit trail (`docs/verification/`).

## Now

- Recover the aggregate `analysis/tools` verification contract before merging
  `dev/android-auto-17.3-analysis` into `main`: remove ignored-asset
  requirements from the default gate, synchronize generated confidence
  comments with canonical audit sidecars, restore protobuf 4.21 compatibility,
  and make one clean-checkout verification command authoritative.
- Android Auto 17.3 Task 13 evidence-policy reconciliation is complete:
  confidence tiers now derive from one executable policy, MATCH-08-only SDP
  bindings remain central-report evidence rather than message promotions, and
  audits, OEM reports, coverage, and video documentation share that boundary.
- Consolidate remaining session-specific notes into permanent docs.
- Publish a minimal `dist` branch for downstream proto consumers without the research archive.
- Android Auto 17.3 static schema-matching baseline operational: 175 mappings resolved without a live session, including 39 dispatch-backed and 73 graph-resolved mappings, plus 13 unique enum-domain mappings. Every graph-resolved row now records its exact parent/field evidence.
- Six residual conflict families have exact 16.2 → 16.4 → 17.3 class lineages; five unrelated proto files (49 messages and 6 enums) are excluded from the active graph after call sites tied them to Surveys, GoogleAuth, or radio metadata.
- The capture-backed `WifiSecurityResponse` is reduced to fields 1-5; removing its false radio-metadata extension unlocked `RadioSongMetadata -> xla` as a unique structural mapping.
- Trusted-parent propagation recovered 24 additional identities and the 17.3 blended-UI subtree (`xml`/`xfi`/`xgs`/`xir`/`xlh`); the only remaining trusted-parent schema delta is `VideoConfig` field 7, which disappeared in 17.3 but remains in the proto for 16.x compatibility.
- Android Auto 17.3 multi-display analysis now has a durable local APK/JADX
  provenance chain and source-level confirmation of per-display IDs, surfaces,
  video endpoints, focus state, and input binding; findings are preserved in
  `analysis/reports/multi-display/android-auto-17.3.md`.

## Next

- Run Task 14's final release gate over the full proto tree, analysis tools,
  manifest commands, links, matcher immutability, and exact publication scope;
  do not reopen the reconciled Task 13 evidence boundaries without new direct
  message/field evidence.
- Reconstruct any real protocol-facing capability or connection schemas only from trusted service/channel parents or wire evidence; do not reuse the retracted bundled-library names.
- Trace the remaining 149 structural collisions from cross-version parents or semantic call sites; do not promote globally unique local shapes without contextual evidence.
- Add verifier recovery for enum multiplexers whose switch bodies JADX could not decompile.
- Expand wire capture coverage to underexplored channels (car control, radio, phone).
- VideoConfigData field 11: confirm UiConfig sub-message structure via wire capture.
- Improve evidence coverage for proto definitions — promote Bronze→Silver where wire capture data exists.
- Capture a live MAIN + CLUSTER + AUXILIARY session to confirm concurrent channel
  IDs, AV handshakes, media streams, and independent focus behavior against the
  17.3 static display model.

## Later

- Protocol change tracking for catalog-level semantic updates across future Android Auto versions.
- Automated stale path/reference detection in docs.
- Community contribution workflow for new implementations and proto discoveries.

## Focus Guardrails

- This repo is not an app runtime project; avoid UI/runtime feature work here.
- Prioritize protocol definitions, protocol docs, and analysis tooling only.
- Defer cross-repo product planning to the primary application repository.

Last Updated: 2026-07-25
