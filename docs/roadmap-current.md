# Roadmap (Current)

## Now

- Finalize APK `v16.1` protobuf catalog contract in `analysis/tools/apk_indexer`.
- Keep high-confidence catalog and unknown queue split enforceable via tests.
- Maintain reproducible indexing workflow and query pack usability.

## Next

- **GAL gap coverage — COMPLETE.** All 13 channel handler types now have proto definitions or documentation:
  - Type 1: Control (existing + ConnectedDevices, BatteryStatus, UserSwitch)
  - Type 6-8: Audio/Sensor/Input (existing)
  - Type 10: Instrument Cluster (InstrumentClusterMessages.proto)
  - Type 11: Media Playback Status (corrected MediaPlaybackStatusMessage.proto)
  - Type 12: Media Browser — dead channel, no handler in v16.1
  - Type 13: Phone Status (existing + PhoneStatusInputMessage.proto)
  - Type 15: Radio (RadioMessages.proto — 9 messages, 6 sub-messages, 3 enums)
  - Type 16: Vendor Extension (VendorExtensionChannel.proto — documentation, raw byte pipe)
  - Type 19: Car Control (CarControlMessages.proto — 4 messages, 8 sub-messages, 3 enums)
  - Type 20: CAR_LOCAL_MEDIA (Status + Metadata + Request protos)
  - Type 21: Buffered Media Sink (BufferedMediaSinkMessage.proto — stub)
  - AV channels: UiConfigMessages.proto (4 messages for theme/margins/insets)
- Run manual triage on unknown queue entries to promote high-confidence definitions.
- Improve evidence coverage for accepted catalog entries.
- Establish canonical benchmark baseline for end-to-end indexing runtime.
- Add non-media capture-based protobuf regression validation (`validate`/`--bless`) for schema changes in `oaa/*.proto`.

## Later

- Add future-version compatibility hooks beyond canonical `v16.1`.
- Add protocol change tracking for catalog-level semantic updates.
- Expand automation around stale path/reference detection in docs.
- VideoConfigData field 11: confirm UiConfig sub-message structure via wire capture.

## Focus Guardrails

- This repo is not an app runtime project; avoid UI/runtime feature work here.
- Prioritize protocol definitions, protocol docs, and analysis tooling only.
- Defer cross-repo product planning to the primary application repository.

Last Updated: 2026-02-28 (GAL gap coverage complete — all channel handlers documented)
