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
| Direction and video-ID audit | open | Video rows closed by Task 3; car-control, sensor, and radio DIR rows remain open in `message-matrix.md`. |
| Identity and compatibility | open | `message-matrix.md` ID rows |
| New services | open | `services.md` SVC rows |
| Runtime validation | open | `runtime-validation.md` RT rows |
| Canonical publication | open | `change-manifest.md` accepted rows |
| Final verification and handoff | open | final handoff entry |

## Resume Here

- Last completed task: Task 3, video message direction and ID audit
- Next task: Task 4, car-control direction matrix
- Next command: `rg -n 'case 3276|case 3277|Received unexpected car control|\.q\(\)' analysis/aa_apk_17.3.662804_apkm/jadx-output/sources/defpackage/ixb.java`
