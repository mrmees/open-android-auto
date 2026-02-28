# Roadmap (Current)

## Now

- Finalize APK `v16.1` protobuf catalog contract in `analysis/tools/apk_indexer`.
- Keep high-confidence catalog and unknown queue split enforceable via tests.
- Maintain reproducible indexing workflow and query pack usability.

## Next

- Run manual triage on unknown queue entries to promote high-confidence definitions.
- Improve evidence coverage for accepted catalog entries.
- Establish canonical benchmark baseline for end-to-end indexing runtime.
- Add non-media capture-based protobuf regression validation (`validate`/`--bless`) for schema changes in `oaa/*.proto`.

## Later

- Add future-version compatibility hooks beyond canonical `v16.1`.
- Add protocol change tracking for catalog-level semantic updates.
- Expand automation around stale path/reference detection in docs.

## Focus Guardrails

- This repo is not an app runtime project; avoid UI/runtime feature work here.
- Prioritize protocol definitions, protocol docs, and analysis tooling only.
- Defer cross-repo product planning to the primary application repository.

Last Updated: 2026-02-28 (apk protobuf catalog implementation + stream validator planning)
