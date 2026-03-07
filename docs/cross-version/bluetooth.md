# Bluetooth - Cross-Version Mapping

**Mappings:** 3 | **Versions:** 15.9, 16.1, 16.2

| Proto Name | 15.9 | 16.1 | 16.2 | Fields (15.9/16.1/16.2) |
|---|---|---|---|---|
| BluetoothChannel | `vok` | `vwc` | `vvo` | 2/2/2 |
| BluetoothPairingRequest | `juf` | `kay` | `kba` | 3/3/3 |
| BluetoothPairingResponse | `wyp` | `xgq` | `vvn` | 3/3/2 |

> **CORRECTED (2026-03-07):** 16.2 class is `vvn`, not `xgb` (xgb is an unrelated sub-message). Fields reduced from 3 to 2 (field 3 removed). 16.1 class `kba` was originally listed as `kay` (which is PairingRequest) — `kba` is the correct 16.2 PairingRequest class.
