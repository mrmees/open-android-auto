# Roadmap (Current)

## Done (recently completed)

- APK v16.1 protobuf catalog finalized with reproducible indexing workflow.
- GAL gap coverage complete — all 13 channel handler types have proto definitions or documentation.
- Non-media capture-based protobuf regression validation (`proto_stream_validator`) operational with locked baselines.
- Cross-version comparison tooling (v16.1 vs v16.2) built and producing diff reports.
- Channel documentation written for all major channels (`docs/channels/`).
- Session lifecycle interaction specs completed (`docs/interactions/`).
- Wire capture TLS decryption pipeline working (Frida-based master secret extraction).

## Now

- Improve evidence coverage for proto definitions — promote Bronze→Silver where wire capture data exists.
- Continue v16.2 APK deep-dive analysis for new/changed message types.
- Validate remaining proto schemas against wire captures from scenario sessions (idle, music, navigation).

## Next

- Expand wire capture coverage to underexplored channels (car control, radio, phone).
- Cross-version audit sidecar promotion — confirm field stability across v16.1→v16.2.
- Document any v16.2-only message types or field changes discovered during analysis.

## Later

- Protocol change tracking for catalog-level semantic updates across future versions.
- VideoConfigData field 11: confirm UiConfig sub-message structure via wire capture.
- Automated stale path/reference detection in docs.

## Focus Guardrails

- This repo is not an app runtime project; avoid UI/runtime feature work here.
- Prioritize protocol definitions, protocol docs, and analysis tooling only.
- Defer cross-repo product planning to the primary application repository.

Last Updated: 2026-03-04
