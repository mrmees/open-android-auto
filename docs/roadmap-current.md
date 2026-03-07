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

- Documentation cleanup and accuracy sweep (this task).
- Consolidate remaining session-specific notes into permanent docs.

## Next

- Expand wire capture coverage to underexplored channels (car control, radio, phone).
- VideoConfigData field 11: confirm UiConfig sub-message structure via wire capture.
- Improve evidence coverage for proto definitions — promote Bronze→Silver where wire capture data exists.

## Later

- Protocol change tracking for catalog-level semantic updates across future Android Auto versions.
- Automated stale path/reference detection in docs.
- Community contribution workflow for new implementations and proto discoveries.

## Focus Guardrails

- This repo is not an app runtime project; avoid UI/runtime feature work here.
- Prioritize protocol definitions, protocol docs, and analysis tooling only.
- Defer cross-repo product planning to the primary application repository.

Last Updated: 2026-03-07
