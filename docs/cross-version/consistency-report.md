# Cross-Version Consistency Report

## Summary

- **Total mappings compared:** 224
- **Consistent (no suspicious divergence):** 220
- **With discrepancies:** 4 (all explained -- see analysis below)
- **Unexplained discrepancies:** 0
- **Expected additions (newer versions):** 17
- **Suspicious issues (type changes/removals):** 17
- **Sidecars promoted:** 143

## Discrepancy Analysis

All 4 discrepancies are **false positives** caused by the 16.1 APK index DB lacking the `proto_enum_classes` table. These 4 mappings are pure enum types with no `proto_fields` or `enum_maps` entries -- their values are only available via `proto_enum_classes`, which exists in 15.9 and 16.2 but not 16.1.

**Manual verification confirms all 4 enums are identical between 15.9 and 16.2:**

| Enum | 15.9 Values | 16.2 Values | Verdict |
|---|---|---|---|
| DriverPosition | LEFT(0), RIGHT(1), CENTER(2), UNKNOWN(3) | LEFT(0), RIGHT(1), CENTER(2), UNKNOWN(3) | Identical |
| HapticFeedbackType | SELECT(1), FOCUS_CHANGE(2), DRAG_SELECT(3), DRAG_START(4), DRAG_END(5) | SELECT(1), FOCUS_CHANGE(2), DRAG_SELECT(3), DRAG_START(4), DRAG_END(5) | Identical |
| SensorErrorStatus | OK(1), TRANSIENT(2), PERMANENT(3) | OK(1), TRANSIENT(2), PERMANENT(3) | Identical |
| CarLocalMediaPlayback | PLAY(0), PAUSE(1), PREVIOUS(2), NEXT(3), STOP(4) | PLAY(0), PAUSE(1), PREVIOUS(2), NEXT(3), STOP(4) | Identical |

**Root cause:** The 16.1 indexer run did not produce the `proto_enum_classes` table, so the comparison engine sees empty data for the 16.1 version of these classes, generating apparent "removed" (15.9->16.1) and "added" (16.1->16.2) issues.

**Classification: EXPLAINED -- data extraction gap, not structural change.**

## Raw Discrepancy Details

| Mapping | Version Pair | Issue | Field | Detail |
|---|---|---|---|---|
| DriverPosition | vpq -> vxi | field_removed | 0-3 | 16.1 DB lacks proto_enum_classes table |
| HapticFeedbackType | vpu -> vxm | field_removed | 1-5 | 16.1 DB lacks proto_enum_classes table |
| SensorErrorStatus | vty -> wbq | field_removed | 1-3 | 16.1 DB lacks proto_enum_classes table |
| CarLocalMediaPlayback | vox -> vwp | field_removed | 0-4 | 16.1 DB lacks proto_enum_classes table |

## Expected Evolution (Field Additions)

These are the mirror image of the discrepancies above -- enum values "appearing" in 16.2 that were actually present all along but invisible in 16.1 due to the missing table.

| Mapping | Version Pair | Fields | Detail |
|---|---|---|---|
| DriverPosition | vxi -> vwu | 0-3 | 16.1 data gap resolved in 16.2 |
| HapticFeedbackType | vxm -> vwy | 1-5 | 16.1 data gap resolved in 16.2 |
| SensorErrorStatus | wbq -> wbg | 1-3 | 16.1 data gap resolved in 16.2 |
| CarLocalMediaPlayback | vwp -> vwb | 0-4 | 16.1 data gap resolved in 16.2 |

## Promotion Summary

- Consistent mappings eligible for promotion: 220
- Sidecars actually promoted: 143
- Promotion: bronze -> silver (apk_static + cross_version)
- Not promoted: 77 mappings (no sidecar file, already promoted, or discrepancy-flagged)
