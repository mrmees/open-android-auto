# Android Auto 17.3 Protocol Update Dossier

- Version: `17.3.662804-release`
- APKM SHA-256: `1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344`
- base.apk SHA-256: `5557827f259898bdab97b489e1a0aef937fd6ec711d87361cf25d51af6f48619`
- Design: `docs/plans/2026-07-24-android-auto-17.3-update-design.md`
- Execution plan: `docs/plans/2026-07-24-android-auto-17.3-update-plan.md`

## Gate Status

| Gate | Status | Exit evidence |
|---|---|---|
| Baseline preservation | confirmed-static | Durable provenance and matcher smoke recorded in Task 1 handoff. |
| Direction and video-ID audit | confirmed-static | All video, car-control, sensor, and radio DIR rows are closed in `message-matrix.md`; the sole bounded video slot remains explicitly deferred. |
| Identity and compatibility | confirmed-static | All five ID rows are closed in `message-matrix.md`: AV/input identity is source-proven, field 18 is a compatible addition, and the unavailable 16.2 semantics for fields 16-17 are explicitly classified as insufficient evidence rather than inferred. |
| New services | confirmed-static | All CarIntent, CarLocalMedia, and BufferedMedia rows are closed in `services.md`. CarLocalMedia value 5 and BufferedMedia IDs 1-3/outbound paths remain explicitly deferred; 17.3 directly proves a gated service-type-21 parser for incoming ID 4, not runtime activation or a complete transfer protocol. |
| Runtime validation | open | `runtime-validation.md` RT rows |
| Canonical publication | open | `change-manifest.md` accepted rows |
| Final verification and handoff | open | final handoff entry |

## Resume Here

- Last completed task: Task 8, CarLocalMedia and BufferedMedia classification
- Next task: Task 9, focused runtime validation
- Next command: `adb devices -l`
