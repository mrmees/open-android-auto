# Cross-Version Consistency Report

## Summary

- **Total mappings compared:** 224
- **Consistent (no suspicious divergence):** 220
- **With discrepancies:** 4
- **Expected additions (newer versions):** 0
- **Suspicious issues (type changes/removals):** 34
- **Sidecars promoted:** 0

## Discrepancies

| Mapping | Version Pair | Issue | Field | Detail |
|---|---|---|---|---|
| DriverPosition | vpq -> vxi | field_removed | 0 | field 0 (enum_value) present in v1 but removed in v2 |
| DriverPosition | vpq -> vxi | field_removed | 1 | field 1 (enum_value) present in v1 but removed in v2 |
| DriverPosition | vpq -> vxi | field_removed | 2 | field 2 (enum_value) present in v1 but removed in v2 |
| DriverPosition | vpq -> vxi | field_removed | 3 | field 3 (enum_value) present in v1 but removed in v2 |
| DriverPosition | vpq -> vwu | field_removed | 0 | field 0 (enum_value) present in v1 but removed in v2 |
| DriverPosition | vpq -> vwu | field_removed | 1 | field 1 (enum_value) present in v1 but removed in v2 |
| DriverPosition | vpq -> vwu | field_removed | 2 | field 2 (enum_value) present in v1 but removed in v2 |
| DriverPosition | vpq -> vwu | field_removed | 3 | field 3 (enum_value) present in v1 but removed in v2 |
| HapticFeedbackType | vpu -> vxm | field_removed | 1 | field 1 (enum_value) present in v1 but removed in v2 |
| HapticFeedbackType | vpu -> vxm | field_removed | 2 | field 2 (enum_value) present in v1 but removed in v2 |
| HapticFeedbackType | vpu -> vxm | field_removed | 3 | field 3 (enum_value) present in v1 but removed in v2 |
| HapticFeedbackType | vpu -> vxm | field_removed | 4 | field 4 (enum_value) present in v1 but removed in v2 |
| HapticFeedbackType | vpu -> vxm | field_removed | 5 | field 5 (enum_value) present in v1 but removed in v2 |
| HapticFeedbackType | vpu -> vwy | field_removed | 1 | field 1 (enum_value) present in v1 but removed in v2 |
| HapticFeedbackType | vpu -> vwy | field_removed | 2 | field 2 (enum_value) present in v1 but removed in v2 |
| HapticFeedbackType | vpu -> vwy | field_removed | 3 | field 3 (enum_value) present in v1 but removed in v2 |
| HapticFeedbackType | vpu -> vwy | field_removed | 4 | field 4 (enum_value) present in v1 but removed in v2 |
| HapticFeedbackType | vpu -> vwy | field_removed | 5 | field 5 (enum_value) present in v1 but removed in v2 |
| SensorErrorStatus | vty -> wbq | field_removed | 1 | field 1 (enum_value) present in v1 but removed in v2 |
| SensorErrorStatus | vty -> wbq | field_removed | 2 | field 2 (enum_value) present in v1 but removed in v2 |
| SensorErrorStatus | vty -> wbq | field_removed | 3 | field 3 (enum_value) present in v1 but removed in v2 |
| SensorErrorStatus | vty -> wbg | field_removed | 1 | field 1 (enum_value) present in v1 but removed in v2 |
| SensorErrorStatus | vty -> wbg | field_removed | 2 | field 2 (enum_value) present in v1 but removed in v2 |
| SensorErrorStatus | vty -> wbg | field_removed | 3 | field 3 (enum_value) present in v1 but removed in v2 |
| CarLocalMediaPlayback | vox -> vwp | field_removed | 0 | field 0 (enum_value) present in v1 but removed in v2 |
| CarLocalMediaPlayback | vox -> vwp | field_removed | 1 | field 1 (enum_value) present in v1 but removed in v2 |
| CarLocalMediaPlayback | vox -> vwp | field_removed | 2 | field 2 (enum_value) present in v1 but removed in v2 |
| CarLocalMediaPlayback | vox -> vwp | field_removed | 3 | field 3 (enum_value) present in v1 but removed in v2 |
| CarLocalMediaPlayback | vox -> vwp | field_removed | 4 | field 4 (enum_value) present in v1 but removed in v2 |
| CarLocalMediaPlayback | vox -> vwb | field_removed | 0 | field 0 (enum_value) present in v1 but removed in v2 |
| CarLocalMediaPlayback | vox -> vwb | field_removed | 1 | field 1 (enum_value) present in v1 but removed in v2 |
| CarLocalMediaPlayback | vox -> vwb | field_removed | 2 | field 2 (enum_value) present in v1 but removed in v2 |
| CarLocalMediaPlayback | vox -> vwb | field_removed | 3 | field 3 (enum_value) present in v1 but removed in v2 |
| CarLocalMediaPlayback | vox -> vwb | field_removed | 4 | field 4 (enum_value) present in v1 but removed in v2 |

## Expected Evolution (Field Additions)

No field additions detected across versions.

## Promotion Summary

- Consistent mappings eligible for promotion: 220
- Sidecars actually promoted: 0
