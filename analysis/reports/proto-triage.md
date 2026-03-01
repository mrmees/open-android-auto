# Proto Class Triage Report

## Summary

| Category | Count |
|---|---|
| Already mapped | 156 |
| WIRE_HIGH | 38 |
| WIRE_MEDIUM | 60 |
| WIRE_LOW | 138 |
| INTERNAL | 79 |
| UTILITY | 449 |
| UNKNOWN | 1033 |
| **Total in APK** | **1946** |

## Wire Protocol Candidates

### AV

| Class | Cat | Conf | Syntax | Fields | Sub-refs | Signals |
|---|---|---|---|---|---|---|
| `vyu` | WIRE_HIGH | 0.85 | proto2 | 15 | 2 | BFS hop 1, hub_files=1, struct:has_sub_refs, struct:proto2 |
| `noo` | WIRE_MEDIUM | 0.65 | proto3 | 4 | 0 | hub_files=2, struct:proto3 |
| `noq` | WIRE_MEDIUM | 0.65 | proto3 | 6 | 4 | hub_files=3, struct:has_sub_refs, struct:proto3 |
| `wcf` | WIRE_LOW | 0.40 | proto2 | 0 | 0 | hub_files=1, struct:proto2, struct:zero_fields |

### Control

| Class | Cat | Conf | Syntax | Fields | Sub-refs | Signals |
|---|---|---|---|---|---|---|
| `aafu` | WIRE_HIGH | 0.85 | proto3 | 3 | 1 | BFS hop 1, hub_files=2, struct:has_sub_refs, struct:proto3 |
| `aagf` | WIRE_HIGH | 0.85 | proto3 | 6 | 1 | BFS hop 1, hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aagr` | WIRE_HIGH | 0.85 | proto3 | 6 | 4 | BFS hop 1, hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aaij` | WIRE_HIGH | 0.85 | proto3 | 2 | 2 | BFS hop 1, hub_files=2, struct:has_sub_refs, struct:proto3 |
| `aais` | WIRE_HIGH | 0.85 | proto3 | 3 | 3 | BFS hop 1, hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aaix` | WIRE_HIGH | 0.85 | proto3 | 2 | 1 | BFS hop 1, hub_files=2, struct:has_sub_refs, struct:proto3 |
| `aajt` | WIRE_HIGH | 0.85 | proto3 | 2 | 1 | BFS hop 1, hub_files=2, pkg=INTERNAL, struct:has_sub_refs, struct:proto3 |
| `aakd` | WIRE_HIGH | 0.85 | proto3 | 1 | 1 | BFS hop 1, hub_files=1, struct:has_sub_refs, struct:proto3 |
| `wbz` | WIRE_HIGH | 0.85 | proto2 | 1 | 1 | BFS hop 1, hub_files=3, struct:has_sub_refs, struct:proto2 |
| `aafs` | WIRE_MEDIUM | 0.75 | proto3 | 4 | 0 | BFS hop 2, hub_files=2, struct:proto3 |
| `aaiu` | WIRE_MEDIUM | 0.75 | proto3 | 2 | 2 | BFS hop 2, hub_files=2, struct:has_sub_refs, struct:proto3 |
| `aaiz` | WIRE_MEDIUM | 0.75 | proto3 | 3 | 1 | BFS hop 2, hub_files=2, pkg=INTERNAL, struct:has_sub_refs, struct:proto3 |
| `aake` | WIRE_MEDIUM | 0.75 | proto3 | 2 | 1 | BFS hop 2, hub_files=3, pkg=INTERNAL, struct:has_sub_refs, struct:proto3 |
| `aahf` | WIRE_MEDIUM | 0.70 | proto3 | 2 | 2 | BFS hop 2, hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aahi` | WIRE_MEDIUM | 0.70 | proto3 | 5 | 2 | BFS hop 2, hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aaiq` | WIRE_MEDIUM | 0.70 | proto3 | 2 | 0 | BFS hop 2, hub_files=1, struct:proto3 |
| `aair` | WIRE_MEDIUM | 0.70 | proto3 | 8 | 0 | BFS hop 2, hub_files=1, struct:proto3 |
| `aajs` | WIRE_MEDIUM | 0.70 | proto3 | 2 | 0 | BFS hop 2, hub_files=1, pkg=INTERNAL, struct:proto3 |
| `aakc` | WIRE_MEDIUM | 0.70 | proto3 | 1 | 1 | BFS hop 2, hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aafz` | WIRE_MEDIUM | 0.65 | proto3 | 3 | 0 | hub_files=2, struct:proto3 |
| `aagg` | WIRE_MEDIUM | 0.65 | proto3 | 4 | 0 | BFS hop 3, hub_files=2, struct:proto3 |
| `aahd` | WIRE_MEDIUM | 0.65 | proto3 | 2 | 1 | BFS hop 3, hub_files=2, struct:has_sub_refs, struct:proto3 |
| `aail` | WIRE_MEDIUM | 0.65 | proto3 | 2 | 2 | BFS hop 3, hub_files=2, struct:has_sub_refs, struct:proto3 |
| `aaim` | WIRE_MEDIUM | 0.65 | proto3 | 5 | 2 | BFS hop 3, hub_files=3, struct:has_sub_refs, struct:proto3 |
| `aajb` | WIRE_MEDIUM | 0.65 | proto3 | 1 | 0 | hub_files=3, struct:proto3 |
| `aajd` | WIRE_MEDIUM | 0.65 | proto3 | 1 | 1 | hub_files=2, struct:has_sub_refs, struct:proto3 |
| `aaje` | WIRE_MEDIUM | 0.65 | proto3 | 3 | 0 | hub_files=3, struct:proto3 |
| `aajf` | WIRE_MEDIUM | 0.65 | proto3 | 1 | 1 | hub_files=2, struct:has_sub_refs, struct:proto3 |
| `aajp` | WIRE_MEDIUM | 0.65 | proto3 | 7 | 5 | BFS hop 3, hub_files=2, pkg=INTERNAL, struct:has_sub_refs, struct:proto3 |
| `aaki` | WIRE_MEDIUM | 0.65 | proto3 | 3 | 0 | BFS hop 4, hub_files=2, struct:proto3 |
| `poe` | WIRE_MEDIUM | 0.65 | proto3 | 1 | 0 | hub_files=2, struct:proto3 |
| `vwg` | WIRE_MEDIUM | 0.65 | proto2 | 0 | 0 | hub_files=3, struct:proto2, struct:zero_fields |
| `vxz` | WIRE_MEDIUM | 0.65 | proto2 | 3 | 0 | hub_files=3, struct:proto2 |
| `waj` | WIRE_MEDIUM | 0.65 | proto2 | 3 | 1 | hub_files=3, struct:has_sub_refs, struct:proto2 |
| `wak` | WIRE_MEDIUM | 0.65 | proto2 | 2 | 1 | hub_files=3, struct:has_sub_refs, struct:proto2 |
| `wcw` | WIRE_MEDIUM | 0.65 | proto2 | 0 | 0 | hub_files=2, struct:proto2, struct:zero_fields |
| `zop` | WIRE_MEDIUM | 0.65 | proto2 | 12 | 1 | hub_files=2, struct:has_sub_refs, struct:proto2 |
| `aago` | WIRE_LOW | 0.50 | proto3 | 6 | 0 | BFS hop 3, hub_files=1, struct:proto3 |
| `aahn` | WIRE_LOW | 0.50 | proto3 | 2 | 0 | BFS hop 3, hub_files=1, struct:proto3 |
| `aait` | WIRE_LOW | 0.50 | proto3 | 4 | 0 | BFS hop 3, hub_files=1, struct:proto3 |
| `aaiw` | WIRE_LOW | 0.50 | proto3 | 4 | 0 | BFS hop 4, hub_files=1, pkg=INTERNAL, struct:proto3 |
| `aajl` | WIRE_LOW | 0.50 | proto3 | 2 | 0 | BFS hop 4, hub_files=1, pkg=INTERNAL, struct:proto3 |
| `aajq` | WIRE_LOW | 0.50 | proto3 | 2 | 0 | BFS hop 4, hub_files=1, struct:proto3 |
| `aajz` | WIRE_LOW | 0.50 | proto3 | 1 | 0 | BFS hop 4, hub_files=1, struct:proto3 |
| `aaka` | WIRE_LOW | 0.50 | proto3 | 5 | 0 | BFS hop 4, hub_files=1, struct:proto3 |
| `aakb` | WIRE_LOW | 0.50 | proto3 | 2 | 2 | BFS hop 3, hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aafl` | WIRE_LOW | 0.40 | proto3 | 4 | 0 | hub_files=1, struct:proto3 |
| `aafm` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `aafv` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `aafw` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `aafx` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `aafy` | WIRE_LOW | 0.40 | proto3 | 1 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aaga` | WIRE_LOW | 0.40 | proto3 | 1 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aagb` | WIRE_LOW | 0.40 | proto3 | 5 | 0 | hub_files=1, struct:proto3 |
| `aagc` | WIRE_LOW | 0.40 | proto3 | 2 | 2 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aagd` | WIRE_LOW | 0.40 | proto3 | 0 | 0 | hub_files=1, struct:proto3, struct:zero_fields |
| `aage` | WIRE_LOW | 0.40 | proto3 | 0 | 0 | hub_files=1, struct:proto3, struct:zero_fields |
| `aagn` | WIRE_LOW | 0.40 | proto3 | 3 | 0 | hub_files=1, struct:proto3 |
| `aagp` | WIRE_LOW | 0.40 | proto3 | 1 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aagq` | WIRE_LOW | 0.40 | proto3 | 2 | 0 | hub_files=1, struct:proto3 |
| `aagt` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `aagu` | WIRE_LOW | 0.40 | proto3 | 2 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aagw` | WIRE_LOW | 0.40 | proto3 | 5 | 0 | hub_files=1, struct:proto3 |
| `aagx` | WIRE_LOW | 0.40 | proto3 | 2 | 0 | hub_files=1, struct:proto3 |
| `aagy` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `aagz` | WIRE_LOW | 0.40 | proto3 | 5 | 0 | hub_files=1, struct:proto3 |
| `aaha` | WIRE_LOW | 0.40 | proto3 | 2 | 2 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aahb` | WIRE_LOW | 0.40 | proto3 | 1 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aahc` | WIRE_LOW | 0.40 | proto3 | 1 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aahe` | WIRE_LOW | 0.40 | proto3 | 2 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aahg` | WIRE_LOW | 0.40 | proto3 | 0 | 0 | hub_files=1, struct:proto3, struct:zero_fields |
| `aahh` | WIRE_LOW | 0.40 | proto3 | 1 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aahj` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `aahk` | WIRE_LOW | 0.40 | proto3 | 2 | 0 | hub_files=1, struct:proto3 |
| `aahl` | WIRE_LOW | 0.40 | proto3 | 3 | 0 | hub_files=1, struct:proto3 |
| `aaik` | WIRE_LOW | 0.40 | proto3 | 0 | 0 | hub_files=1, struct:proto3, struct:zero_fields |
| `aain` | WIRE_LOW | 0.40 | proto3 | 5 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aaio` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `aajc` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `aajn` | WIRE_LOW | 0.40 | proto3 | 1 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aajo` | WIRE_LOW | 0.40 | proto3 | 2 | 0 | hub_files=1, struct:proto3 |
| `aajv` | WIRE_LOW | 0.40 | proto3 | 11 | 1 | hub_files=1, pkg=INTERNAL, struct:has_sub_refs, struct:proto3 |
| `aajx` | WIRE_LOW | 0.40 | proto3 | 6 | 0 | hub_files=1, pkg=INTERNAL, struct:proto3 |
| `aajy` | WIRE_LOW | 0.40 | proto3 | 2 | 0 | hub_files=1, struct:proto3 |
| `aakf` | WIRE_LOW | 0.40 | proto3 | 2 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aakg` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `aakh` | WIRE_LOW | 0.40 | proto3 | 2 | 0 | hub_files=1, struct:proto3 |
| `aawf` | WIRE_LOW | 0.40 | proto3 | 2 | 0 | hub_files=1, pkg=INTERNAL, struct:proto3 |
| `aawg` | WIRE_LOW | 0.40 | proto3 | 1 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aawh` | WIRE_LOW | 0.40 | proto3 | 0 | 0 | hub_files=1, struct:proto3, struct:zero_fields |
| `aawi` | WIRE_LOW | 0.40 | proto3 | 0 | 0 | hub_files=1, struct:proto3, struct:zero_fields |
| `aawj` | WIRE_LOW | 0.40 | proto3 | 0 | 0 | hub_files=1, struct:proto3, struct:zero_fields |
| `aawk` | WIRE_LOW | 0.40 | proto3 | 0 | 0 | hub_files=1, struct:proto3, struct:zero_fields |
| `iar` | WIRE_LOW | 0.40 | proto3 | 12 | 0 | hub_files=1, struct:proto3 |
| `vxc` | WIRE_LOW | 0.40 | proto2 | 1 | 1 | hub_files=1, struct:has_sub_refs, struct:proto2 |
| `wcx` | WIRE_LOW | 0.40 | proto2 | 1 | 1 | hub_files=1, struct:has_sub_refs, struct:proto2 |
| `xiz` | WIRE_LOW | 0.40 | proto2 | 2 | 1 | hub_files=1, pkg=INTERNAL, struct:has_sub_refs, struct:proto2 |
| `zll` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `zlm` | WIRE_LOW | 0.40 | proto2 | 3 | 0 | hub_files=1, struct:proto2 |
| `znq` | WIRE_LOW | 0.40 | proto2 | 0 | 0 | hub_files=1, struct:proto2, struct:zero_fields |
| `zns` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `zpu` | WIRE_LOW | 0.40 | proto2 | 2 | 0 | hub_files=1, struct:proto2 |

### Input

| Class | Cat | Conf | Syntax | Fields | Sub-refs | Signals |
|---|---|---|---|---|---|---|
| `vvi` | WIRE_HIGH | 0.85 | proto2 | 1 | 0 | BFS hop 1, hub_files=2, struct:proto2 |
| `nnv` | WIRE_MEDIUM | 0.70 | proto3 | 16 | 3 | BFS hop 2, hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aacu` | WIRE_MEDIUM | 0.65 | proto2 | 1 | 0 | hub_files=3, struct:proto2 |
| `nnu` | WIRE_MEDIUM | 0.65 | proto3 | 6 | 2 | BFS hop 3, hub_files=2, struct:has_sub_refs, struct:proto3 |
| `vxy` | WIRE_MEDIUM | 0.65 | proto2 | 8 | 0 | hub_files=4, struct:proto2 |
| `vyf` | WIRE_MEDIUM | 0.65 | proto2 | 1 | 0 | hub_files=2, struct:proto2 |
| `vyg` | WIRE_MEDIUM | 0.65 | proto2 | 1 | 0 | hub_files=2, struct:proto2 |
| `noc` | WIRE_LOW | 0.50 | proto3 | 6 | 1 | BFS hop 3, hub_files=1, struct:has_sub_refs, struct:proto3 |
| `aadk` | WIRE_LOW | 0.40 | proto2 | 7 | 1 | hub_files=1, struct:has_sub_refs, struct:proto2 |
| `aadl` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `aadt` | WIRE_LOW | 0.40 | proto3 | 2 | 0 | hub_files=1, struct:proto3 |
| `aadu` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `aagl` | WIRE_LOW | 0.40 | proto3 | 4 | 0 | hub_files=1, pkg=INTERNAL, struct:proto3 |
| `aamq` | WIRE_LOW | 0.40 | proto2 | 4 | 1 | hub_files=1, struct:has_sub_refs, struct:proto2 |
| `aasq` | WIRE_LOW | 0.40 | proto3 | 3 | 0 | hub_files=1, struct:proto3 |
| `aasr` | WIRE_LOW | 0.40 | proto3 | 4 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `ahdm` | WIRE_LOW | 0.40 | proto2 | 3 | 1 | hub_files=1, struct:has_sub_refs, struct:proto2 |
| `ahfn` | WIRE_LOW | 0.40 | proto2 | 2 | 0 | hub_files=1, struct:proto2 |
| `ahfw` | WIRE_LOW | 0.40 | proto2 | 3 | 1 | hub_files=1, struct:has_sub_refs, struct:proto2 |
| `jpe` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `jpf` | WIRE_LOW | 0.40 | proto3 | 4 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `nfs` | WIRE_LOW | 0.40 | proto3 | 9 | 0 | hub_files=1, struct:proto3 |
| `nft` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `nok` | WIRE_LOW | 0.40 | proto3 | 5 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `ufe` | WIRE_LOW | 0.40 | proto3 | 4 | 0 | hub_files=1, struct:proto3 |
| `ufg` | WIRE_LOW | 0.40 | proto3 | 3 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `ufi` | WIRE_LOW | 0.40 | proto3 | 3 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `urq` | WIRE_LOW | 0.40 | proto3 | 2 | 0 | hub_files=1, struct:proto3 |
| `urt` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `vvh` | WIRE_LOW | 0.40 | proto2 | 2 | 0 | hub_files=1, struct:proto2 |
| `vxw` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `xgs` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `xgx` | WIRE_LOW | 0.40 | proto2 | 8 | 0 | hub_files=1, struct:proto2 |
| `xgz` | WIRE_LOW | 0.40 | proto2 | 21 | 2 | hub_files=1, struct:has_sub_refs, struct:proto2 |
| `xmd` | WIRE_LOW | 0.40 | proto2 | 3 | 0 | hub_files=1, struct:proto2 |
| `xmh` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `xss` | WIRE_LOW | 0.40 | proto2 | 3 | 1 | hub_files=1, struct:has_sub_refs, struct:proto2 |
| `ysu` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `zfp` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `zli` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `zlq` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `zlr` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `znc` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `znn` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `zrg` | WIRE_LOW | 0.40 | proto2 | 3 | 0 | hub_files=1, struct:proto2 |
| `zsr` | WIRE_LOW | 0.40 | proto3 | 6 | 3 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `zst` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `ztd` | WIRE_LOW | 0.40 | proto3 | 2 | 0 | hub_files=1, struct:proto3 |
| `ztq` | WIRE_LOW | 0.40 | proto3 | 1 | 0 | hub_files=1, struct:proto3 |
| `zts` | WIRE_LOW | 0.40 | proto3 | 3 | 1 | hub_files=1, struct:has_sub_refs, struct:proto3 |
| `zvm` | WIRE_LOW | 0.40 | proto2 | 3 | 1 | hub_files=1, struct:has_sub_refs, struct:proto2 |
| `zvs` | WIRE_LOW | 0.40 | proto2 | 4 | 0 | hub_files=1, struct:proto2 |

### Mixed/Control

| Class | Cat | Conf | Syntax | Fields | Sub-refs | Signals |
|---|---|---|---|---|---|---|
| `aacl` | WIRE_LOW | 0.40 | proto3 | 3 | 0 | hub_files=1, struct:proto3 |
| `vwd` | WIRE_LOW | 0.40 | proto2 | 0 | 0 | hub_files=1, struct:proto2, struct:zero_fields |
| `vwt` | WIRE_LOW | 0.40 | proto2 | 0 | 0 | hub_files=1, struct:proto2, struct:zero_fields |
| `vym` | WIRE_LOW | 0.40 | proto2 | 0 | 0 | hub_files=1, struct:proto2, struct:zero_fields |
| `vyr` | WIRE_LOW | 0.40 | proto2 | 0 | 0 | hub_files=1, struct:proto2, struct:zero_fields |

### Navigation

| Class | Cat | Conf | Syntax | Fields | Sub-refs | Signals |
|---|---|---|---|---|---|---|
| `vzd` | WIRE_HIGH | 0.85 | proto2 | 3 | 2 | BFS hop 1, hub_files=4, struct:has_sub_refs, struct:proto2 |
| `vzv` | WIRE_MEDIUM | 0.75 | proto2 | 2 | 1 | BFS hop 2, hub_files=2, struct:has_sub_refs, struct:proto2 |
| `vzg` | WIRE_MEDIUM | 0.65 | proto2 | 3 | 0 | BFS hop 3, hub_files=2, struct:proto2 |
| `vzf` | WIRE_LOW | 0.50 | proto2 | 3 | 1 | BFS hop 4, hub_files=1, struct:has_sub_refs, struct:proto2 |
| `non` | WIRE_LOW | 0.40 | proto3 | 12 | 0 | hub_files=1, struct:proto3 |
| `ujq` | WIRE_LOW | 0.40 | proto3 | 4 | 0 | hub_files=1, struct:proto3 |
| `wbg` | WIRE_LOW | 0.40 | proto2 | 1 | 1 | hub_files=1, struct:has_sub_refs, struct:proto2 |

### OAA

| Class | Cat | Conf | Syntax | Fields | Sub-refs | Signals |
|---|---|---|---|---|---|---|
| `vum` | WIRE_HIGH | 0.85 | proto3 | 3 | 2 | BFS hop 1, hub_files=2, struct:has_sub_refs, struct:proto3 |
| `vuo` | WIRE_HIGH | 0.85 | proto3 | 1 | 1 | BFS hop 1, hub_files=3, struct:has_sub_refs, struct:proto3 |
| `vwj` | WIRE_HIGH | 0.85 | proto2 | 1 | 1 | BFS hop 1, hub_files=2, struct:has_sub_refs, struct:proto2 |
| `vwo` | WIRE_HIGH | 0.85 | proto2 | 3 | 0 | BFS hop 1, hub_files=3, struct:proto2 |
| `vwu` | WIRE_HIGH | 0.85 | proto2 | 3 | 2 | BFS hop 1, hub_files=3, struct:has_sub_refs, struct:proto2 |
| `wca` | WIRE_HIGH | 0.85 | proto2 | 3 | 2 | BFS hop 1, hub_files=2, struct:has_sub_refs, struct:proto2 |
| `wcb` | WIRE_HIGH | 0.85 | proto2 | 4 | 1 | BFS hop 1, hub_files=2, struct:has_sub_refs, struct:proto2 |
| `wcm` | WIRE_HIGH | 0.85 | proto2 | 7 | 1 | BFS hop 1, hub_files=3, struct:has_sub_refs, struct:proto2 |
| `wcs` | WIRE_MEDIUM | 0.75 | proto2 | 1 | 1 | BFS hop 2, hub_files=2, struct:has_sub_refs, struct:proto2 |
| `vux` | WIRE_MEDIUM | 0.65 | proto3 | 7 | 0 | hub_files=3, struct:proto3 |
| `wbj` | WIRE_MEDIUM | 0.65 | proto2 | 1 | 0 | hub_files=2, struct:proto2 |
| `vye` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `vzy` | WIRE_LOW | 0.40 | proto2 | 4 | 0 | hub_files=1, struct:proto2 |
| `vzz` | WIRE_LOW | 0.40 | proto2 | 3 | 2 | hub_files=1, struct:has_sub_refs, struct:proto2 |
| `waa` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `wbk` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `wcu` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |

### Radio

| Class | Cat | Conf | Syntax | Fields | Sub-refs | Signals |
|---|---|---|---|---|---|---|
| `wbc` | WIRE_HIGH | 0.85 | proto2 | 1 | 1 | BFS hop 1, hub_files=1, struct:has_sub_refs, struct:proto2 |
| `wao` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `waz` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |
| `wba` | WIRE_LOW | 0.40 | proto2 | 1 | 0 | hub_files=1, struct:proto2 |

### Sensor

| Class | Cat | Conf | Syntax | Fields | Sub-refs | Signals |
|---|---|---|---|---|---|---|
| `vxs` | WIRE_HIGH | 0.80 | proto2 | 3 | 0 | hub_files=6, struct:proto2 |
| `wch` | WIRE_HIGH | 0.80 | proto2 | 1 | 0 | hub_files=5, struct:proto2 |
| `aacw` | WIRE_MEDIUM | 0.65 | proto2 | 1 | 0 | hub_files=2, struct:proto2 |
| `vvg` | WIRE_MEDIUM | 0.65 | proto3 | 0 | 0 | hub_files=4, struct:proto3, struct:zero_fields |
| `wbf` | WIRE_MEDIUM | 0.65 | proto2 | 1 | 1 | hub_files=3, struct:has_sub_refs, struct:proto2 |
| `wbh` | WIRE_MEDIUM | 0.65 | proto2 | 1 | 1 | hub_files=3, struct:has_sub_refs, struct:proto2 |
| `wbp` | WIRE_MEDIUM | 0.65 | proto2 | 2 | 0 | hub_files=2, struct:proto2 |
| `wbr` | WIRE_MEDIUM | 0.65 | proto2 | 2 | 0 | hub_files=2, struct:proto2 |
| `wcl` | WIRE_MEDIUM | 0.65 | proto2 | 0 | 0 | hub_files=4, struct:proto2, struct:zero_fields |
| `vxr` | WIRE_LOW | 0.40 | proto2 | 5 | 0 | hub_files=1, struct:proto2 |
| `ztb` | WIRE_LOW | 0.40 | proto3 | 28 | 2 | hub_files=1, struct:has_sub_refs, struct:proto3 |

### Unknown

| Class | Cat | Conf | Syntax | Fields | Sub-refs | Signals |
|---|---|---|---|---|---|---|
| `aaci` | WIRE_HIGH | 0.85 | proto3 | 2 | 1 | BFS hop 1, struct:has_sub_refs, struct:proto3 |
| `aafo` | WIRE_HIGH | 0.85 | proto3 | 2 | 2 | BFS hop 1, struct:has_sub_refs, struct:proto3 |
| `aafr` | WIRE_HIGH | 0.85 | proto3 | 4 | 4 | BFS hop 1, struct:has_sub_refs, struct:proto3 |
| `aheu` | WIRE_HIGH | 0.85 | proto2 | 5 | 1 | BFS hop 1, struct:has_sub_refs, struct:proto2 |
| `ahfy` | WIRE_HIGH | 0.85 | proto3 | 5 | 1 | BFS hop 1, struct:has_sub_refs, struct:proto3 |
| `nmj` | WIRE_HIGH | 0.85 | proto3 | 3 | 2 | BFS hop 1, struct:has_sub_refs, struct:proto3 |
| `nmo` | WIRE_HIGH | 0.85 | proto3 | 9 | 4 | BFS hop 1, struct:has_sub_refs, struct:proto3 |
| `noa` | WIRE_HIGH | 0.85 | proto3 | 6 | 1 | BFS hop 1, struct:has_sub_refs, struct:proto3 |
| `nvl` | WIRE_HIGH | 0.85 | proto3 | 3 | 1 | BFS hop 1, struct:has_sub_refs, struct:proto3 |
| `nvm` | WIRE_HIGH | 0.85 | proto3 | 2 | 1 | BFS hop 1, struct:has_sub_refs, struct:proto3 |
| `rse` | WIRE_HIGH | 0.85 | proto3 | 7 | 1 | BFS hop 1, struct:has_sub_refs, struct:proto3 |
| `vwn` | WIRE_HIGH | 0.85 | proto2 | 1 | 1 | BFS hop 1, struct:has_sub_refs, struct:proto2 |
| `wat` | WIRE_HIGH | 0.85 | proto2 | 3 | 1 | BFS hop 1, struct:has_sub_refs, struct:proto2 |
| `xmv` | WIRE_HIGH | 0.85 | proto2 | 2 | 1 | BFS hop 1, struct:has_sub_refs, struct:proto2 |
| `aafn` | WIRE_MEDIUM | 0.70 | proto3 | 6 | 0 | BFS hop 2, struct:proto3 |
| `aafq` | WIRE_MEDIUM | 0.70 | proto3 | 2 | 2 | BFS hop 2, struct:has_sub_refs, struct:proto3 |
| `aahm` | WIRE_MEDIUM | 0.70 | proto3 | 1 | 0 | BFS hop 2, struct:proto3 |
| `aaho` | WIRE_MEDIUM | 0.70 | proto3 | 5 | 4 | BFS hop 2, struct:has_sub_refs, struct:proto3 |
| `nmd` | WIRE_MEDIUM | 0.70 | proto3 | 3 | 0 | BFS hop 2, struct:proto3 |
| `nme` | WIRE_MEDIUM | 0.70 | proto3 | 5 | 3 | BFS hop 2, struct:has_sub_refs, struct:proto3 |
| `nmp` | WIRE_MEDIUM | 0.70 | proto3 | 3 | 0 | BFS hop 2, struct:proto3 |
| `nof` | WIRE_MEDIUM | 0.70 | proto3 | 10 | 4 | BFS hop 2, struct:has_sub_refs, struct:proto3 |
| `rsz` | WIRE_MEDIUM | 0.70 | proto3 | 2 | 1 | BFS hop 2, struct:has_sub_refs, struct:proto3 |
| `xma` | WIRE_MEDIUM | 0.70 | proto3 | 3 | 1 | BFS hop 2, struct:has_sub_refs, struct:proto3 |
| `xmu` | WIRE_MEDIUM | 0.70 | proto2 | 1 | 1 | BFS hop 2, struct:has_sub_refs, struct:proto2 |
| `aafp` | WIRE_LOW | 0.50 | proto3 | 4 | 0 | BFS hop 3, struct:proto3 |
| `aajm` | WIRE_LOW | 0.50 | proto3 | 3 | 0 | BFS hop 4, pkg=INTERNAL, struct:proto3 |
| `nmq` | WIRE_LOW | 0.50 | proto3 | 1 | 0 | BFS hop 3, struct:proto3 |
| `nnr` | WIRE_LOW | 0.50 | proto3 | 3 | 2 | BFS hop 3, struct:has_sub_refs, struct:proto3 |
| `nnx` | WIRE_LOW | 0.50 | proto3 | 3 | 0 | BFS hop 4, struct:proto3 |
| `nob` | WIRE_LOW | 0.50 | proto3 | 6 | 0 | BFS hop 3, struct:proto3 |

### WiFi

| Class | Cat | Conf | Syntax | Fields | Sub-refs | Signals |
|---|---|---|---|---|---|---|
| `wds` | WIRE_HIGH | 0.85 | proto2 | 5 | 3 | BFS hop 1, hub_files=4, struct:has_sub_refs, struct:proto2 |
| `wdt` | WIRE_MEDIUM | 0.65 | proto2 | 3 | 0 | hub_files=3, struct:proto2 |
| `nwf` | WIRE_LOW | 0.40 | proto3 | 2 | 0 | hub_files=1, struct:proto3 |

## Internal Classifications

| Class | Conf | Syntax | Fields | Evidence |
|---|---|---|---|---|
| `aaav` | 0.85 | proto3 | 2 | telemetry_cluster, struct:proto3 |
| `ahdg` | 0.85 | proto2 | 3 | telemetry_cluster, struct:has_sub_refs, struct:proto2 |
| `ahdh` | 0.85 | proto2 | 1 | telemetry_cluster, struct:proto2 |
| `ahdi` | 0.85 | proto2 | 10 | telemetry_cluster, hub_files=1, pkg=INTERNAL, struct:has_sub_refs, struct:proto2 |
| `ahdj` | 0.85 | proto2 | 1 | telemetry_cluster, hub_files=1, pkg=INTERNAL, struct:has_sub_refs, struct:proto2 |
| `ahdl` | 0.85 | proto2 | 2 | telemetry_cluster, struct:proto2 |
| `ahdq` | 0.85 | proto2 | 3 | telemetry_cluster, hub_files=1, struct:has_sub_refs, struct:proto2 |
| `ahdr` | 0.85 | proto2 | 63 | telemetry_cluster, hub_files=1, struct:has_sub_refs, struct:proto2 |
| `ahds` | 0.85 | proto2 | 5 | telemetry_cluster, struct:proto2 |
| `ahdu` | 0.85 | proto2 | 4 | telemetry_cluster, struct:has_sub_refs, struct:proto2 |
| `ahdz` | 0.85 | proto2 | 22 | telemetry_cluster, struct:proto2 |
| `ahea` | 0.85 | proto2 | 1 | telemetry_cluster, struct:proto2 |
| `aheb` | 0.85 | proto2 | 1 | telemetry_cluster, struct:has_sub_refs, struct:proto2 |
| `ahec` | 0.85 | proto2 | 5 | telemetry_cluster, struct:has_sub_refs, struct:proto2 |
| `ahed` | 0.85 | proto2 | 1 | telemetry_cluster, struct:proto2 |
| `ahef` | 0.85 | proto2 | 23 | telemetry_cluster, hub_files=1, pkg=INTERNAL, struct:has_sub_refs, struct:proto2 |
| `aheg` | 0.85 | proto2 | 2 | telemetry_cluster, hub_files=1, pkg=INTERNAL, struct:proto2 |
| `aheh` | 0.85 | proto2 | 1 | telemetry_cluster, struct:proto2 |
| `ahei` | 0.85 | proto2 | 2 | telemetry_cluster, hub_files=1, pkg=INTERNAL, struct:proto2 |
| `ahej` | 0.85 | proto2 | 5 | telemetry_cluster, hub_files=1, pkg=INTERNAL, struct:has_sub_refs, struct:proto2 |
| `ahel` | 0.85 | proto2 | 4 | telemetry_cluster, struct:proto2 |
| `ahen` | 0.85 | proto2 | 21 | telemetry_cluster, struct:has_sub_refs, struct:proto2 |
| `aheq` | 0.85 | proto2 | 5 | telemetry_cluster, struct:has_sub_refs, struct:proto2 |
| `ahev` | 0.85 | proto2 | 6 | telemetry_cluster, hub_files=1, struct:proto2 |
| `ahew` | 0.85 | proto2 | 1 | telemetry_cluster, hub_files=1, struct:has_sub_refs, struct:proto2 |
| `ahex` | 0.85 | proto2 | 2 | telemetry_cluster, struct:proto2 |
| `ahfa` | 0.85 | proto2 | 7 | telemetry_cluster, struct:proto2 |
| `ahfc` | 0.85 | proto2 | 2 | telemetry_cluster, struct:proto2 |
| `ahfd` | 0.85 | proto2 | 9 | telemetry_cluster, hub_files=2, pkg=INTERNAL, struct:has_sub_refs, struct:proto2 |
| `ahfe` | 0.85 | proto2 | 4 | telemetry_cluster, hub_files=1, struct:proto2 |
| `ahff` | 0.85 | proto2 | 2 | telemetry_cluster, hub_files=1, struct:has_sub_refs, struct:proto2 |
| `ahfg` | 0.85 | proto2 | 6 | telemetry_cluster, struct:proto2 |
| `ahfl` | 0.85 | proto2 | 2 | telemetry_cluster, hub_files=1, pkg=INTERNAL, struct:proto2 |
| `ahfm` | 0.85 | proto2 | 9 | telemetry_cluster, hub_files=1, pkg=INTERNAL, struct:proto2 |
| `ahfp` | 0.85 | proto2 | 3 | telemetry_cluster, struct:proto2 |
| `ahfq` | 0.85 | proto2 | 0 | telemetry_cluster, struct:proto2, struct:zero_fields |
| `ahfr` | 0.85 | proto2 | 28 | telemetry_cluster, hub_files=2, pkg=INTERNAL, struct:has_sub_refs, struct:proto2 |
| `ahfs` | 0.85 | proto2 | 2 | telemetry_cluster, struct:proto2 |
| `ahfz` | 0.85 | proto3 | 3 | telemetry_cluster, struct:has_sub_refs, struct:proto3 |
| `upd` | 0.85 | proto3 | 7 | telemetry_cluster, hub_files=2, pkg=INTERNAL, struct:proto3 |
| `xhl` | 0.85 | proto2 | 15 | telemetry_cluster, struct:proto2 |
| `xho` | 0.85 | proto2 | 8 | telemetry_cluster, struct:proto2 |
| `xhp` | 0.85 | proto2 | 2 | telemetry_cluster, struct:proto2 |
| `xhq` | 0.85 | proto2 | 5 | telemetry_cluster, hub_files=2, struct:proto2 |
| `xhs` | 0.85 | proto2 | 5 | telemetry_cluster, struct:proto2 |
| `xhw` | 0.85 | proto2 | 2 | telemetry_cluster, struct:proto2 |
| `xhx` | 0.85 | proto2 | 12 | telemetry_cluster, struct:proto2 |
| `xid` | 0.85 | proto2 | 58 | telemetry_cluster, hub_files=7, pkg=INTERNAL, struct:has_sub_refs, struct:proto2 |
| `xif` | 0.85 | proto2 | 4 | telemetry_cluster, struct:proto2 |
| `xih` | 0.85 | proto2 | 6 | telemetry_cluster, struct:proto2 |
| `xij` | 0.85 | proto2 | 8 | telemetry_cluster, struct:proto2 |
| `xis` | 0.85 | proto2 | 14 | telemetry_cluster, hub_files=1, struct:proto2 |
| `xit` | 0.85 | proto2 | 7 | telemetry_cluster, hub_files=1, struct:proto2 |
| `xiu` | 0.85 | proto2 | 3 | telemetry_cluster, struct:proto2 |
| `xiv` | 0.85 | proto2 | 7 | telemetry_cluster, hub_files=3, pkg=INTERNAL, struct:has_sub_refs, struct:proto2 |
| `xiw` | 0.85 | proto2 | 3 | telemetry_cluster, struct:proto2 |
| `xix` | 0.85 | proto2 | 2 | telemetry_cluster, struct:proto2 |
| `xjb` | 0.85 | proto2 | 1 | telemetry_cluster, struct:proto2 |
| `xjc` | 0.85 | proto2 | 2 | telemetry_cluster, struct:has_sub_refs, struct:proto2 |
| `xjf` | 0.85 | proto2 | 3 | telemetry_cluster, struct:proto2 |
| `xjn` | 0.85 | proto2 | 2 | telemetry_cluster, struct:proto2 |
| `xka` | 0.85 | proto2 | 18 | telemetry_cluster, struct:has_sub_refs, struct:proto2 |
| `xkb` | 0.85 | proto2 | 6 | telemetry_cluster, struct:proto2 |
| `xke` | 0.85 | proto2 | 4 | telemetry_cluster, struct:proto2 |
| `xkf` | 0.85 | proto2 | 4 | telemetry_cluster, struct:has_sub_refs, struct:proto2 |
| `xkg` | 0.85 | proto2 | 2 | telemetry_cluster, struct:proto2 |
| `xkj` | 0.85 | proto2 | 4 | telemetry_cluster, struct:proto2 |
| `xkm` | 0.85 | proto2 | 2 | telemetry_cluster, hub_files=1, struct:proto2 |
| `xkp` | 0.85 | proto2 | 4 | telemetry_cluster, hub_files=1, struct:proto2 |
| `xkt` | 0.85 | proto2 | 3 | telemetry_cluster, struct:proto2 |
| `xku` | 0.85 | proto2 | 3 | telemetry_cluster, struct:proto2 |
| `xkv` | 0.85 | proto2 | 2 | telemetry_cluster, struct:proto2 |
| `xlb` | 0.85 | proto2 | 49 | telemetry_cluster, hub_files=1, struct:has_sub_refs, struct:proto2 |
| `xlc` | 0.85 | proto2 | 5 | telemetry_cluster, struct:proto2 |
| `xle` | 0.85 | proto2 | 4 | telemetry_cluster, pkg=INTERNAL, struct:has_sub_refs, struct:proto2 |
| `xlf` | 0.85 | proto2 | 4 | telemetry_cluster, struct:proto2 |
| `aaip` | 0.75 | proto3 | 2 | pkg=INTERNAL, struct:proto3 |
| `aajr` | 0.75 | proto3 | 2 | pkg=INTERNAL, struct:proto3 |
| `aaju` | 0.75 | proto3 | 2 | pkg=INTERNAL, struct:has_sub_refs, struct:proto3 |

## Utility / Framework Classes

| Class | Conf | Syntax | Fields | Signals |
|---|---|---|---|---|
| `zyn` | 0.70 | (empty) | 1 | hub_files=51, struct:empty_syntax, struct:has_sub_refs |
| `zyq` | 0.70 | (empty) | 1 | struct:empty_syntax, struct:has_sub_refs |
| `zyt` | 0.70 | (empty) | 1 | hub_files=51, struct:empty_syntax |
| `Proxy` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `ProxyOptions` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `RequestContextConfigOptions` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aacx` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aacy` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aacz` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aadd` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aadg` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aadh` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aadj` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aafh` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aagi` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aagj` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aagk` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aagm` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aahw` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aama` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamb` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamc` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamd` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamg` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamh` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aami` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamj` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamk` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamn` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamt` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamu` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamv` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamy` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aamz` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aana` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aanb` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aand` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aane` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aanf` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aank` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aanl` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aanm` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aanq` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aanr` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aans` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aant` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aanu` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aanv` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aanw` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aany` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aanz` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaoa` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaoe` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaog` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaol` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaou` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaov` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaow` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaox` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaoy` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaoz` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aapb` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aapf` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aapg` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaph` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aapi` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aapj` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aapk` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aapm` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aapn` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aapp` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aapq` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aapr` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaps` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aapy` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaqd` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaqg` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaqi` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaqj` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaqk` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaqm` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaqo` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaqs` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaqt` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaqu` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaqv` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aare` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aarf` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aarg` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aarj` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aarm` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaro` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aarp` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aarq` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aarr` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aart` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaru` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aarv` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aarw` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aarx` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aary` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aarz` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aasc` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aasd` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aasf` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aasm` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aasn` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aasv` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aats` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `aaul` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aaum` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `ahdn` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `ahdy` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aheo` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `aher` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `ahes` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `ahet` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `nmk` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `nmw` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `nmx` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `nnc` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `nnd` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `nnf` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `nng` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `nnh` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `nnn` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `nvk` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `piq` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `piu` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `piv` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `pja` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `rsf` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `rsh` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `rsk` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `rsn` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `rss` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `rsu` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `rta` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `rtk` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `rtl` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `ubj` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `uob` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `vww` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `vxu` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `vzs` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `vzt` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `wdf` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `xgy` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `xhb` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `xhc` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `xlk` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xlt` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xlu` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `xly` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `xnj` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `xty` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xtz` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xua` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xuh` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `xup` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xuq` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xuv` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `xvo` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xvq` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xvr` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xvs` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xvt` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xvu` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xvv` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xvz` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwc` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwd` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwe` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwf` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwg` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwh` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwi` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwj` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwk` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwl` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwm` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwn` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwo` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwp` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwq` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwr` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xws` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwt` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwu` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xww` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xwz` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxa` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxb` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxd` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxf` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxg` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxh` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxi` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxj` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxl` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxm` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxn` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxq` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxs` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxt` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxu` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxv` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxw` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxx` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xxz` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xya` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `xyf` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `yae` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `yag` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `yap` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `yar` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `yau` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `yay` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `ybe` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `ybf` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `ybg` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `ybl` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `ybq` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `ytg` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `ytn` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `ytr` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `ytu` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `yyj` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `yzg` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `yzw` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zaw` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zbx` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zby` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zbz` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zca` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zcb` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcc` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcd` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zce` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcg` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zch` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zci` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcj` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zck` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcl` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcm` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zcn` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zco` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcp` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcq` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcr` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcs` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zct` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcu` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcv` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcw` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zcx` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zcy` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zcz` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zda` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdb` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdc` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdf` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdj` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdn` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdo` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zdp` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdq` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdr` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zds` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdt` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zdu` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdv` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdw` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdx` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zdy` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zdz` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zee` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zef` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zeg` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zeh` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zei` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zej` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zek` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zel` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zem` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zen` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zeo` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zep` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zeq` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zer` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zet` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zev` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zfc` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zfd` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zfe` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zff` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zfn` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zfo` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zfq` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zfz` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zga` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgb` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgc` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgd` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zge` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgf` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgg` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgh` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgj` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zgk` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgl` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zgm` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zgn` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgo` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgp` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgq` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgr` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgs` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgt` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgu` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zgv` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zgw` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zgx` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zgy` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zgz` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zha` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zhb` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zhe` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zhf` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zhh` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zhi` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhj` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhk` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhl` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhm` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhn` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zho` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhp` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhq` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhr` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhs` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zht` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhu` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhv` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhw` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhx` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhy` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zhz` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zia` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zib` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zic` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zid` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zie` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zif` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zig` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zih` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zii` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zik` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zil` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zim` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zin` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zio` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zip` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `ziq` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zir` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zis` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zit` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `ziv` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `ziw` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zix` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjb` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zjc` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zjd` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zje` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zjf` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjg` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zjh` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zji` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjj` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjk` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjl` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjm` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zjn` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjr` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjs` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjt` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zju` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zjv` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjw` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjx` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjy` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zjz` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zka` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zkb` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zkc` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zkd` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zke` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zkf` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zkg` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zkl` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zkn` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zks` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zkt` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zky` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zle` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zlf` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zlg` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zmb` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zmk` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zml` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zmm` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `znd` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zne` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zng` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `znv` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zoa` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zod` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zof` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zok` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zor` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zos` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zpc` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zpe` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zpf` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zpg` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zqm` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zrl` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zse` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zsj` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zsk` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zth` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `ztt` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zuo` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zuq` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zur` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zuw` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zux` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zva` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zvc` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zvg` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zvi` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zvj` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zvk` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zwc` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zwo` | 0.60 | proto2 | 0 | struct:proto2, struct:zero_fields |
| `zwu` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zwv` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |
| `zye` | 0.60 | proto3 | 0 | struct:proto3, struct:zero_fields |

## Unknown — Manual Review Needed

### Proto2 (higher priority)

| Class | Conf | Fields | Sub-refs | Signals |
|---|---|---|---|---|
| `aacv` | 0.30 | 1 | 0 | struct:proto2 |
| `aadi` | 0.30 | 2 | 0 | struct:proto2 |
| `aadm` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `aadn` | 0.30 | 2 | 0 | struct:proto2 |
| `aado` | 0.30 | 2 | 0 | struct:proto2 |
| `aadp` | 0.30 | 3 | 0 | struct:proto2 |
| `aadq` | 0.30 | 9 | 1 | struct:has_sub_refs, struct:proto2 |
| `aadr` | 0.30 | 2 | 0 | struct:proto2 |
| `aads` | 0.30 | 1 | 0 | struct:proto2 |
| `aafe` | 0.30 | 1 | 0 | struct:proto2 |
| `aaff` | 0.30 | 1 | 1 | struct:has_sub_refs, struct:proto2 |
| `aafi` | 0.30 | 1 | 0 | struct:proto2 |
| `aafj` | 0.30 | 1 | 0 | struct:proto2 |
| `aafk` | 0.30 | 1 | 0 | struct:proto2 |
| `aahv` | 0.30 | 1 | 0 | struct:proto2 |
| `aako` | 0.30 | 3 | 0 | struct:proto2 |
| `aala` | 0.30 | 2 | 0 | struct:proto2 |
| `aalv` | 0.30 | 2 | 0 | struct:proto2 |
| `aalw` | 0.30 | 3 | 0 | struct:proto2 |
| `aalx` | 0.30 | 3 | 1 | struct:has_sub_refs, struct:proto2 |
| `aame` | 0.30 | 1 | 0 | struct:proto2 |
| `aamm` | 0.30 | 1 | 0 | struct:proto2 |
| `aamo` | 0.30 | 14 | 3 | struct:has_sub_refs, struct:proto2 |
| `aamp` | 0.30 | 5 | 2 | struct:has_sub_refs, struct:proto2 |
| `aamr` | 0.30 | 34 | 1 | struct:has_sub_refs, struct:proto2 |
| `aams` | 0.30 | 9 | 3 | struct:has_sub_refs, struct:proto2 |
| `aamw` | 0.30 | 2 | 0 | struct:proto2 |
| `aanc` | 0.30 | 2 | 0 | struct:proto2 |
| `aanh` | 0.30 | 1 | 0 | struct:proto2 |
| `aanj` | 0.30 | 2 | 0 | struct:proto2 |
| `aanx` | 0.30 | 3 | 0 | struct:proto2 |
| `aaof` | 0.30 | 1 | 0 | struct:proto2 |
| `aaom` | 0.30 | 2 | 2 | struct:has_sub_refs, struct:proto2 |
| `aaon` | 0.30 | 2 | 0 | struct:proto2 |
| `aaoq` | 0.30 | 4 | 0 | struct:proto2 |
| `aaos` | 0.30 | 44 | 0 | struct:proto2 |
| `aaot` | 0.30 | 1 | 0 | struct:proto2 |
| `aapd` | 0.30 | 287 | 0 | struct:proto2 |
| `aaqh` | 0.30 | 1 | 0 | struct:proto2 |
| `aaql` | 0.30 | 1 | 0 | struct:proto2 |
| `aaqp` | 0.30 | 8 | 0 | struct:proto2 |
| `aaqy` | 0.30 | 1 | 0 | struct:proto2 |
| `aara` | 0.30 | 2 | 0 | struct:proto2 |
| `aarb` | 0.30 | 2 | 0 | struct:proto2 |
| `aarc` | 0.30 | 3 | 0 | struct:proto2 |
| `aard` | 0.30 | 3 | 0 | struct:proto2 |
| `aari` | 0.30 | 3 | 0 | struct:proto2 |
| `aasg` | 0.30 | 4 | 0 | struct:proto2 |
| `aasl` | 0.30 | 10 | 1 | struct:has_sub_refs, struct:proto2 |
| `aasu` | 0.30 | 6 | 0 | struct:proto2 |
| `aasw` | 0.30 | 2 | 0 | struct:proto2 |
| `aasx` | 0.30 | 4 | 1 | struct:has_sub_refs, struct:proto2 |
| `aasy` | 0.30 | 4 | 1 | struct:has_sub_refs, struct:proto2 |
| `aasz` | 0.30 | 2 | 0 | struct:proto2 |
| `aata` | 0.30 | 3 | 0 | struct:proto2 |
| `aaug` | 0.30 | 3 | 0 | struct:proto2 |
| `aauh` | 0.30 | 1 | 0 | struct:proto2 |
| `aaui` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `aauj` | 0.30 | 1 | 0 | struct:proto2 |
| `aauk` | 0.30 | 5 | 0 | struct:proto2 |
| `ahdd` | 0.30 | 3 | 0 | struct:proto2 |
| `ahdf` | 0.30 | 14 | 5 | struct:has_sub_refs, struct:proto2 |
| `ahdk` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `ahdo` | 0.30 | 7 | 1 | struct:has_sub_refs, struct:proto2 |
| `ahep` | 0.30 | 3 | 0 | struct:proto2 |
| `ahez` | 0.30 | 1 | 0 | struct:proto2 |
| `ahfb` | 0.30 | 1 | 0 | struct:proto2 |
| `ahfh` | 0.30 | 2 | 0 | struct:proto2 |
| `ahfi` | 0.30 | 3 | 0 | struct:proto2 |
| `ahfk` | 0.30 | 6 | 1 | struct:has_sub_refs, struct:proto2 |
| `ahfo` | 0.30 | 1 | 0 | struct:proto2 |
| `ahfu` | 0.30 | 3 | 1 | struct:has_sub_refs, struct:proto2 |
| `ahfv` | 0.30 | 1 | 0 | struct:proto2 |
| `ahfx` | 0.30 | 4 | 0 | struct:proto2 |
| `ahzu` | 0.30 | 8 | 0 | struct:proto2 |
| `ahzv` | 0.30 | 1 | 0 | struct:proto2 |
| `ahzx` | 0.30 | 1 | 0 | struct:proto2 |
| `oxi` | 0.30 | 1 | 0 | struct:proto2 |
| `oxj` | 0.30 | 2 | 0 | struct:proto2 |
| `vvm` | 0.30 | 1 | 0 | struct:proto2 |
| `vvw` | 0.30 | 3 | 0 | struct:proto2 |
| `vvx` | 0.30 | 1 | 0 | struct:proto2 |
| `vvy` | 0.30 | 1 | 0 | struct:proto2 |
| `vwa` | 0.30 | 2 | 0 | struct:proto2 |
| `vyd` | 0.30 | 1 | 0 | struct:proto2 |
| `vyp` | 0.30 | 7 | 1 | struct:has_sub_refs, struct:proto2 |
| `vzl` | 0.30 | 4 | 0 | struct:proto2 |
| `wai` | 0.30 | 4 | 0 | struct:proto2 |
| `wal` | 0.30 | 1 | 0 | struct:proto2 |
| `wap` | 0.30 | 1 | 0 | struct:proto2 |
| `wau` | 0.30 | 1 | 0 | struct:proto2 |
| `wbd` | 0.30 | 1 | 0 | struct:proto2 |
| `wco` | 0.30 | 2 | 0 | struct:proto2 |
| `wcp` | 0.30 | 1 | 0 | struct:proto2 |
| `wcq` | 0.30 | 2 | 0 | struct:proto2 |
| `wct` | 0.30 | 1 | 1 | struct:has_sub_refs, struct:proto2 |
| `wdg` | 0.30 | 4 | 0 | struct:proto2 |
| `wgf` | 0.30 | 1 | 0 | struct:proto2 |
| `wgh` | 0.30 | 1 | 0 | struct:proto2 |
| `xgh` | 0.30 | 7 | 0 | struct:proto2 |
| `xgm` | 0.30 | 1 | 0 | struct:proto2 |
| `xgn` | 0.30 | 1 | 0 | struct:proto2 |
| `xgr` | 0.30 | 1 | 0 | struct:proto2 |
| `xgt` | 0.30 | 2 | 0 | struct:proto2 |
| `xgu` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `xgw` | 0.30 | 2 | 0 | struct:proto2 |
| `xha` | 0.30 | 2 | 0 | struct:proto2 |
| `xhg` | 0.30 | 1 | 0 | struct:proto2 |
| `xhh` | 0.30 | 1 | 0 | struct:proto2 |
| `xhk` | 0.30 | 5 | 0 | struct:proto2 |
| `xhr` | 0.30 | 31 | 1 | struct:has_sub_refs, struct:proto2 |
| `xht` | 0.30 | 2 | 0 | struct:proto2 |
| `xhv` | 0.30 | 3 | 0 | struct:proto2 |
| `xhy` | 0.30 | 2 | 0 | struct:proto2 |
| `xhz` | 0.30 | 2 | 0 | struct:proto2 |
| `xib` | 0.30 | 3 | 0 | struct:proto2 |
| `xic` | 0.30 | 2 | 0 | struct:proto2 |
| `xig` | 0.30 | 7 | 0 | struct:proto2 |
| `xii` | 0.30 | 1 | 0 | struct:proto2 |
| `xin` | 0.30 | 6 | 0 | struct:proto2 |
| `xio` | 0.30 | 6 | 1 | struct:has_sub_refs, struct:proto2 |
| `xir` | 0.30 | 8 | 0 | struct:proto2 |
| `xiy` | 0.30 | 4 | 0 | struct:proto2 |
| `xjg` | 0.30 | 3 | 0 | struct:proto2 |
| `xji` | 0.30 | 3 | 0 | struct:proto2 |
| `xjj` | 0.30 | 6 | 0 | struct:proto2 |
| `xjl` | 0.30 | 3 | 0 | struct:proto2 |
| `xjo` | 0.30 | 3 | 0 | struct:proto2 |
| `xjp` | 0.30 | 4 | 0 | struct:proto2 |
| `xjq` | 0.30 | 4 | 0 | struct:proto2 |
| `xjr` | 0.30 | 4 | 1 | struct:has_sub_refs, struct:proto2 |
| `xjs` | 0.30 | 3 | 0 | struct:proto2 |
| `xjt` | 0.30 | 3 | 0 | struct:proto2 |
| `xju` | 0.30 | 2 | 0 | struct:proto2 |
| `xjv` | 0.30 | 3 | 0 | struct:proto2 |
| `xjy` | 0.30 | 1 | 0 | struct:proto2 |
| `xjz` | 0.30 | 4 | 0 | struct:proto2 |
| `xkc` | 0.30 | 2 | 0 | struct:proto2 |
| `xkk` | 0.30 | 1 | 1 | struct:has_sub_refs, struct:proto2 |
| `xkl` | 0.30 | 19 | 1 | struct:has_sub_refs, struct:proto2 |
| `xkq` | 0.30 | 4 | 0 | struct:proto2 |
| `xld` | 0.30 | 5 | 0 | struct:proto2 |
| `xls` | 0.30 | 3 | 0 | struct:proto2 |
| `xlv` | 0.30 | 2 | 0 | struct:proto2 |
| `xlx` | 0.30 | 3 | 0 | struct:proto2 |
| `xmb` | 0.30 | 7 | 1 | struct:has_sub_refs, struct:proto2 |
| `xmc` | 0.30 | 1 | 0 | struct:proto2 |
| `xme` | 0.30 | 1 | 0 | struct:proto2 |
| `xmr` | 0.30 | 4 | 0 | struct:proto2 |
| `xms` | 0.30 | 2 | 0 | struct:proto2 |
| `xmt` | 0.30 | 1 | 0 | struct:proto2 |
| `xmx` | 0.30 | 7 | 0 | struct:proto2 |
| `xmy` | 0.30 | 8 | 0 | struct:proto2 |
| `xmz` | 0.30 | 13 | 4 | struct:has_sub_refs, struct:proto2 |
| `xna` | 0.30 | 1 | 0 | struct:proto2 |
| `xnh` | 0.30 | 1 | 0 | struct:proto2 |
| `xni` | 0.30 | 7 | 0 | struct:proto2 |
| `xsr` | 0.30 | 1 | 0 | struct:proto2 |
| `xtr` | 0.30 | 1 | 0 | struct:proto2 |
| `xts` | 0.30 | 1 | 0 | struct:proto2 |
| `xtt` | 0.30 | 3 | 0 | struct:proto2 |
| `xtu` | 0.30 | 4 | 0 | struct:proto2 |
| `xtv` | 0.30 | 1 | 0 | struct:proto2 |
| `xui` | 0.30 | 1 | 0 | struct:proto2 |
| `xuk` | 0.30 | 1 | 0 | struct:proto2 |
| `xuw` | 0.30 | 1 | 0 | struct:proto2 |
| `xux` | 0.30 | 1 | 0 | struct:proto2 |
| `xuy` | 0.30 | 2 | 0 | struct:proto2 |
| `xuz` | 0.30 | 2 | 0 | struct:proto2 |
| `xva` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `xve` | 0.30 | 1 | 0 | struct:proto2 |
| `xvj` | 0.30 | 1 | 0 | struct:proto2 |
| `xvl` | 0.30 | 4 | 4 | struct:has_sub_refs, struct:proto2 |
| `xvn` | 0.30 | 3 | 0 | struct:proto2 |
| `xyk` | 0.30 | 1 | 0 | struct:proto2 |
| `xyl` | 0.30 | 1 | 0 | struct:proto2 |
| `xyo` | 0.30 | 2 | 0 | struct:proto2 |
| `xzv` | 0.30 | 8 | 0 | struct:proto2 |
| `yuw` | 0.30 | 1 | 0 | struct:proto2 |
| `yzq` | 0.30 | 1 | 0 | struct:proto2 |
| `yzr` | 0.30 | 1 | 0 | struct:proto2 |
| `zac` | 0.30 | 2 | 0 | struct:proto2 |
| `zae` | 0.30 | 2 | 0 | struct:proto2 |
| `zaf` | 0.30 | 2 | 0 | struct:proto2 |
| `zap` | 0.30 | 2 | 0 | struct:proto2 |
| `zar` | 0.30 | 1 | 0 | struct:proto2 |
| `zas` | 0.30 | 2 | 0 | struct:proto2 |
| `zat` | 0.30 | 2 | 0 | struct:proto2 |
| `zay` | 0.30 | 2 | 0 | struct:proto2 |
| `zbw` | 0.30 | 1 | 0 | struct:proto2 |
| `zcf` | 0.30 | 2 | 0 | struct:proto2 |
| `zdd` | 0.30 | 11 | 0 | struct:proto2 |
| `zdi` | 0.30 | 2 | 0 | struct:proto2 |
| `zdl` | 0.30 | 1 | 0 | struct:proto2 |
| `zdm` | 0.30 | 1 | 0 | struct:proto2 |
| `zeb` | 0.30 | 1 | 0 | struct:proto2 |
| `zec` | 0.30 | 1 | 0 | struct:proto2 |
| `zed` | 0.30 | 1 | 0 | struct:proto2 |
| `zes` | 0.30 | 2 | 0 | struct:proto2 |
| `zeu` | 0.30 | 2 | 0 | struct:proto2 |
| `zex` | 0.30 | 1 | 0 | struct:proto2 |
| `zez` | 0.30 | 1 | 0 | struct:proto2 |
| `zfb` | 0.30 | 1 | 0 | struct:proto2 |
| `zfg` | 0.30 | 13 | 0 | struct:proto2 |
| `zfh` | 0.30 | 1 | 0 | struct:proto2 |
| `zfk` | 0.30 | 1 | 0 | struct:proto2 |
| `zfl` | 0.30 | 1 | 0 | struct:proto2 |
| `zfm` | 0.30 | 1 | 0 | struct:proto2 |
| `zfr` | 0.30 | 1 | 0 | struct:proto2 |
| `zfs` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `zft` | 0.30 | 3 | 0 | struct:proto2 |
| `zfx` | 0.30 | 7 | 2 | struct:has_sub_refs, struct:proto2 |
| `zfy` | 0.30 | 3 | 1 | struct:has_sub_refs, struct:proto2 |
| `zgi` | 0.30 | 1 | 0 | struct:proto2 |
| `zij` | 0.30 | 16 | 0 | struct:proto2 |
| `ziz` | 0.30 | 1 | 0 | struct:proto2 |
| `zja` | 0.30 | 1 | 0 | struct:proto2 |
| `zjp` | 0.30 | 1 | 0 | struct:proto2 |
| `zjq` | 0.30 | 1 | 0 | struct:proto2 |
| `zkh` | 0.30 | 1 | 0 | struct:proto2 |
| `zkk` | 0.30 | 1 | 0 | struct:proto2 |
| `zlc` | 0.30 | 5 | 1 | struct:has_sub_refs, struct:proto2 |
| `zld` | 0.30 | 3 | 1 | struct:has_sub_refs, struct:proto2 |
| `zlh` | 0.30 | 3 | 2 | struct:has_sub_refs, struct:proto2 |
| `zlj` | 0.30 | 1 | 0 | struct:proto2 |
| `zlk` | 0.30 | 2 | 0 | struct:proto2 |
| `zln` | 0.30 | 2 | 0 | struct:proto2 |
| `zlp` | 0.30 | 2 | 0 | struct:proto2 |
| `zls` | 0.30 | 1 | 0 | struct:proto2 |
| `zlv` | 0.30 | 14 | 0 | struct:proto2 |
| `zlw` | 0.30 | 1 | 0 | struct:proto2 |
| `zlx` | 0.30 | 1 | 0 | struct:proto2 |
| `zmd` | 0.30 | 1 | 0 | struct:proto2 |
| `zme` | 0.30 | 6 | 0 | struct:proto2 |
| `zmf` | 0.30 | 3 | 0 | struct:proto2 |
| `zmg` | 0.30 | 2 | 0 | struct:proto2 |
| `zmh` | 0.30 | 4 | 0 | struct:proto2 |
| `zmi` | 0.30 | 2 | 0 | struct:proto2 |
| `zmj` | 0.30 | 4 | 1 | struct:has_sub_refs, struct:proto2 |
| `zmn` | 0.30 | 3 | 1 | struct:has_sub_refs, struct:proto2 |
| `zmo` | 0.30 | 5 | 0 | struct:proto2 |
| `zmr` | 0.30 | 6 | 1 | struct:has_sub_refs, struct:proto2 |
| `zms` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `zmt` | 0.30 | 9 | 1 | struct:has_sub_refs, struct:proto2 |
| `zmv` | 0.30 | 3 | 0 | struct:proto2 |
| `zmy` | 0.30 | 15 | 1 | struct:has_sub_refs, struct:proto2 |
| `zna` | 0.30 | 1 | 0 | struct:proto2 |
| `znb` | 0.30 | 6 | 4 | struct:has_sub_refs, struct:proto2 |
| `znj` | 0.30 | 2 | 0 | struct:proto2 |
| `znl` | 0.30 | 4 | 0 | struct:proto2 |
| `znp` | 0.30 | 21 | 4 | struct:has_sub_refs, struct:proto2 |
| `znr` | 0.30 | 2 | 0 | struct:proto2 |
| `znu` | 0.30 | 2 | 0 | struct:proto2 |
| `znz` | 0.30 | 11 | 0 | struct:proto2 |
| `zob` | 0.30 | 1 | 0 | struct:proto2 |
| `zoc` | 0.30 | 1 | 1 | struct:has_sub_refs, struct:proto2 |
| `zog` | 0.30 | 4 | 0 | struct:proto2 |
| `zoh` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `zoi` | 0.30 | 2 | 0 | struct:proto2 |
| `zon` | 0.30 | 1 | 0 | struct:proto2 |
| `zoo` | 0.30 | 5 | 0 | struct:proto2 |
| `zoq` | 0.30 | 5 | 1 | struct:has_sub_refs, struct:proto2 |
| `zot` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `zou` | 0.30 | 1 | 0 | struct:proto2 |
| `zox` | 0.30 | 3 | 0 | struct:proto2 |
| `zoz` | 0.30 | 3 | 0 | struct:proto2 |
| `zpa` | 0.30 | 1 | 0 | struct:proto2 |
| `zpb` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `zpd` | 0.30 | 1 | 0 | struct:proto2 |
| `zpi` | 0.30 | 10 | 1 | struct:has_sub_refs, struct:proto2 |
| `zpj` | 0.30 | 2 | 0 | struct:proto2 |
| `zpk` | 0.30 | 2 | 0 | struct:proto2 |
| `zpl` | 0.30 | 3 | 1 | struct:has_sub_refs, struct:proto2 |
| `zpm` | 0.30 | 18 | 0 | struct:proto2 |
| `zpn` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `zpo` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `zpp` | 0.30 | 2 | 0 | struct:proto2 |
| `zpr` | 0.30 | 1 | 0 | struct:proto2 |
| `zps` | 0.30 | 2 | 2 | struct:has_sub_refs, struct:proto2 |
| `zpt` | 0.30 | 3 | 0 | struct:proto2 |
| `zpw` | 0.30 | 1 | 0 | struct:proto2 |
| `zpx` | 0.30 | 10 | 0 | struct:proto2 |
| `zqo` | 0.30 | 5 | 1 | struct:has_sub_refs, struct:proto2 |
| `zqq` | 0.30 | 1 | 0 | struct:proto2 |
| `zqr` | 0.30 | 2 | 0 | struct:proto2 |
| `zqs` | 0.30 | 2 | 0 | struct:proto2 |
| `zqt` | 0.30 | 5 | 2 | struct:has_sub_refs, struct:proto2 |
| `zqu` | 0.30 | 1 | 0 | struct:proto2 |
| `zqw` | 0.30 | 2 | 0 | struct:proto2 |
| `zqz` | 0.30 | 19 | 1 | struct:has_sub_refs, struct:proto2 |
| `zre` | 0.30 | 9 | 2 | struct:has_sub_refs, struct:proto2 |
| `zrh` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `zrm` | 0.30 | 2 | 0 | struct:proto2 |
| `zrn` | 0.30 | 6 | 2 | struct:has_sub_refs, struct:proto2 |
| `zro` | 0.30 | 2 | 0 | struct:proto2 |
| `zrp` | 0.30 | 3 | 0 | struct:proto2 |
| `zrq` | 0.30 | 1 | 0 | struct:proto2 |
| `zrs` | 0.30 | 2 | 0 | struct:proto2 |
| `zrt` | 0.30 | 2 | 0 | struct:proto2 |
| `zrv` | 0.30 | 1 | 0 | struct:proto2 |
| `zrw` | 0.30 | 2 | 0 | struct:proto2 |
| `zvd` | 0.30 | 3 | 1 | struct:has_sub_refs, struct:proto2 |
| `zvl` | 0.30 | 1 | 0 | struct:proto2 |
| `zvn` | 0.30 | 5 | 0 | struct:proto2 |
| `zvo` | 0.30 | 1 | 0 | struct:proto2 |
| `zvp` | 0.30 | 1 | 0 | struct:proto2 |
| `zvr` | 0.30 | 2 | 1 | struct:has_sub_refs, struct:proto2 |
| `zvt` | 0.30 | 5 | 1 | struct:has_sub_refs, struct:proto2 |
| `zvu` | 0.30 | 2 | 0 | struct:proto2 |
| `zvv` | 0.30 | 1 | 0 | struct:proto2 |
| `zvw` | 0.30 | 2 | 0 | struct:proto2 |
| `zvy` | 0.30 | 1 | 0 | struct:proto2 |
| `zvz` | 0.30 | 1 | 0 | struct:proto2 |
| `zwa` | 0.30 | 1 | 0 | struct:proto2 |
| `zwb` | 0.30 | 1 | 0 | struct:proto2 |
| `zwe` | 0.30 | 1 | 0 | struct:proto2 |
| `zwg` | 0.30 | 1 | 0 | struct:proto2 |
| `zwh` | 0.30 | 2 | 0 | struct:proto2 |
| `zwi` | 0.30 | 1 | 0 | struct:proto2 |
| `zwj` | 0.30 | 2 | 0 | struct:proto2 |
| `zwm` | 0.30 | 1 | 0 | struct:proto2 |
| `zwn` | 0.30 | 1 | 1 | struct:has_sub_refs, struct:proto2 |
| `zwp` | 0.30 | 1 | 0 | struct:proto2 |
| `zwq` | 0.30 | 3 | 0 | struct:proto2 |
| `zws` | 0.30 | 1 | 0 | struct:proto2 |

### Proto3 (lower priority)

| Class | Conf | Fields | Sub-refs | Signals |
|---|---|---|---|---|
| `aacb` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `aacc` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `aace` | 0.20 | 1 | 0 | struct:proto3 |
| `aacf` | 0.20 | 2 | 0 | struct:proto3 |
| `aacg` | 0.20 | 1 | 0 | struct:proto3 |
| `aach` | 0.20 | 3 | 0 | struct:proto3 |
| `aacj` | 0.20 | 1 | 0 | struct:proto3 |
| `aacm` | 0.20 | 1 | 0 | struct:proto3 |
| `aacn` | 0.20 | 4 | 0 | struct:proto3 |
| `aaco` | 0.20 | 2 | 0 | struct:proto3 |
| `aacp` | 0.20 | 2 | 0 | struct:proto3 |
| `aacr` | 0.20 | 5 | 0 | struct:proto3 |
| `aacs` | 0.20 | 2 | 0 | struct:proto3 |
| `aada` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `aadb` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `aadc` | 0.20 | 1 | 0 | struct:proto3 |
| `aade` | 0.20 | 2 | 0 | struct:proto3 |
| `aadf` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `aadw` | 0.20 | 18 | 0 | struct:proto3 |
| `aadx` | 0.20 | 1 | 0 | struct:proto3 |
| `aady` | 0.20 | 1 | 0 | struct:proto3 |
| `aadz` | 0.20 | 2 | 0 | struct:proto3 |
| `aaea` | 0.20 | 1 | 0 | struct:proto3 |
| `aaeb` | 0.20 | 2 | 0 | struct:proto3 |
| `aaec` | 0.20 | 4 | 0 | struct:proto3 |
| `aaed` | 0.20 | 1 | 0 | struct:proto3 |
| `aaee` | 0.20 | 1 | 0 | struct:proto3 |
| `aaef` | 0.20 | 1 | 0 | struct:proto3 |
| `aaeh` | 0.20 | 2 | 0 | struct:proto3 |
| `aaei` | 0.20 | 1 | 0 | struct:proto3 |
| `aaej` | 0.20 | 1 | 0 | struct:proto3 |
| `aaek` | 0.20 | 1 | 0 | struct:proto3 |
| `aael` | 0.20 | 1 | 0 | struct:proto3 |
| `aaem` | 0.20 | 1 | 0 | struct:proto3 |
| `aaen` | 0.20 | 1 | 0 | struct:proto3 |
| `aaep` | 0.20 | 2 | 0 | struct:proto3 |
| `aaer` | 0.20 | 1 | 0 | struct:proto3 |
| `aaeu` | 0.20 | 1 | 0 | struct:proto3 |
| `aaev` | 0.20 | 2 | 0 | struct:proto3 |
| `aaew` | 0.20 | 1 | 0 | struct:proto3 |
| `aaex` | 0.20 | 1 | 0 | struct:proto3 |
| `aaey` | 0.20 | 4 | 0 | struct:proto3 |
| `aaez` | 0.20 | 1 | 0 | struct:proto3 |
| `aafa` | 0.20 | 1 | 0 | struct:proto3 |
| `aafb` | 0.20 | 1 | 0 | struct:proto3 |
| `aafc` | 0.20 | 1 | 0 | struct:proto3 |
| `aafd` | 0.20 | 1 | 0 | struct:proto3 |
| `aahy` | 0.20 | 13 | 5 | struct:has_sub_refs, struct:proto3 |
| `aaia` | 0.20 | 1 | 0 | struct:proto3 |
| `aaib` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `aaic` | 0.20 | 3 | 0 | struct:proto3 |
| `aaie` | 0.20 | 3 | 0 | struct:proto3 |
| `aaif` | 0.20 | 2 | 0 | struct:proto3 |
| `aaih` | 0.20 | 3 | 0 | struct:proto3 |
| `aaii` | 0.20 | 1 | 0 | struct:proto3 |
| `aajw` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `aakr` | 0.20 | 1 | 0 | struct:proto3 |
| `aaks` | 0.20 | 2 | 0 | struct:proto3 |
| `aakt` | 0.20 | 7 | 0 | struct:proto3 |
| `aaku` | 0.20 | 4 | 0 | struct:proto3 |
| `aakv` | 0.20 | 4 | 0 | struct:proto3 |
| `aakw` | 0.20 | 2 | 0 | struct:proto3 |
| `aakz` | 0.20 | 6 | 1 | struct:has_sub_refs, struct:proto3 |
| `aalp` | 0.20 | 5 | 0 | struct:proto3 |
| `aalq` | 0.20 | 2 | 0 | struct:proto3 |
| `aalr` | 0.20 | 4 | 2 | struct:has_sub_refs, struct:proto3 |
| `aaly` | 0.20 | 4 | 0 | struct:proto3 |
| `aalz` | 0.20 | 1 | 0 | struct:proto3 |
| `aamf` | 0.20 | 2 | 0 | struct:proto3 |
| `aang` | 0.20 | 12 | 0 | struct:proto3 |
| `aann` | 0.20 | 1 | 0 | struct:proto3 |
| `aano` | 0.20 | 1 | 0 | struct:proto3 |
| `aanp` | 0.20 | 1 | 0 | struct:proto3 |
| `aaod` | 0.20 | 15 | 1 | struct:has_sub_refs, struct:proto3 |
| `aaoh` | 0.20 | 2 | 0 | struct:proto3 |
| `aaoi` | 0.20 | 2 | 0 | struct:proto3 |
| `aaoj` | 0.20 | 1 | 0 | struct:proto3 |
| `aaok` | 0.20 | 2 | 0 | struct:proto3 |
| `aapa` | 0.20 | 1 | 0 | struct:proto3 |
| `aapl` | 0.20 | 2 | 0 | struct:proto3 |
| `aapo` | 0.20 | 1 | 0 | struct:proto3 |
| `aapt` | 0.20 | 1 | 0 | struct:proto3 |
| `aapu` | 0.20 | 1 | 0 | struct:proto3 |
| `aapw` | 0.20 | 1 | 0 | struct:proto3 |
| `aapx` | 0.20 | 1 | 0 | struct:proto3 |
| `aapz` | 0.20 | 4 | 2 | struct:has_sub_refs, struct:proto3 |
| `aaqa` | 0.20 | 3 | 0 | struct:proto3 |
| `aaqb` | 0.20 | 2 | 0 | struct:proto3 |
| `aaqc` | 0.20 | 1 | 0 | struct:proto3 |
| `aaqe` | 0.20 | 2 | 0 | struct:proto3 |
| `aaqf` | 0.20 | 2 | 0 | struct:proto3 |
| `aaqn` | 0.20 | 2 | 0 | struct:proto3 |
| `aaqq` | 0.20 | 1 | 0 | struct:proto3 |
| `aaqr` | 0.20 | 3 | 0 | struct:proto3 |
| `aaqw` | 0.20 | 2 | 0 | struct:proto3 |
| `aark` | 0.20 | 2 | 0 | struct:proto3 |
| `aarl` | 0.20 | 2 | 0 | struct:proto3 |
| `aarn` | 0.20 | 1 | 0 | struct:proto3 |
| `aars` | 0.20 | 2 | 0 | struct:proto3 |
| `aasa` | 0.20 | 1 | 0 | struct:proto3 |
| `aasb` | 0.20 | 1 | 0 | struct:proto3 |
| `aase` | 0.20 | 1 | 0 | struct:proto3 |
| `aaso` | 0.20 | 2 | 0 | struct:proto3 |
| `aass` | 0.20 | 4 | 0 | struct:proto3 |
| `aatb` | 0.20 | 3 | 0 | struct:proto3 |
| `aatc` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `aatd` | 0.20 | 1 | 0 | struct:proto3 |
| `aate` | 0.20 | 6 | 0 | struct:proto3 |
| `aatf` | 0.20 | 3 | 0 | struct:proto3 |
| `aatg` | 0.20 | 17 | 1 | struct:has_sub_refs, struct:proto3 |
| `aati` | 0.20 | 5 | 0 | struct:proto3 |
| `aatj` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `aatk` | 0.20 | 8 | 0 | struct:proto3 |
| `aatn` | 0.20 | 5 | 4 | struct:has_sub_refs, struct:proto3 |
| `aatp` | 0.20 | 3 | 0 | struct:proto3 |
| `aatu` | 0.20 | 3 | 0 | struct:proto3 |
| `aatv` | 0.20 | 3 | 0 | struct:proto3 |
| `aatw` | 0.20 | 4 | 1 | struct:has_sub_refs, struct:proto3 |
| `aatx` | 0.20 | 14 | 5 | struct:has_sub_refs, struct:proto3 |
| `aatz` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `aaua` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `aaub` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `aauc` | 0.20 | 4 | 1 | struct:has_sub_refs, struct:proto3 |
| `aaud` | 0.20 | 4 | 0 | struct:proto3 |
| `aaue` | 0.20 | 8 | 5 | struct:has_sub_refs, struct:proto3 |
| `aauf` | 0.20 | 1 | 0 | struct:proto3 |
| `aawl` | 0.20 | 1 | 0 | struct:proto3 |
| `abnf` | 0.20 | 2 | 0 | struct:proto3 |
| `abng` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `abnh` | 0.20 | 4 | 0 | struct:proto3 |
| `abni` | 0.20 | 1 | 0 | struct:proto3 |
| `abnv` | 0.20 | 3 | 0 | struct:proto3 |
| `abnw` | 0.20 | 3 | 0 | struct:proto3 |
| `ahdt` | 0.20 | 8 | 0 | struct:proto3 |
| `ahdv` | 0.20 | 3 | 0 | struct:proto3 |
| `ahdx` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `aied` | 0.20 | 2 | 0 | struct:proto3 |
| `aiee` | 0.20 | 2 | 0 | struct:proto3 |
| `aief` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `aieg` | 0.20 | 1 | 0 | struct:proto3 |
| `aieh` | 0.20 | 2 | 0 | struct:proto3 |
| `jma` | 0.20 | 7 | 0 | struct:proto3 |
| `jmb` | 0.20 | 1 | 0 | struct:proto3 |
| `jph` | 0.20 | 2 | 0 | struct:proto3 |
| `jxk` | 0.20 | 1 | 0 | struct:proto3 |
| `kaw` | 0.20 | 1 | 0 | struct:proto3 |
| `kbx` | 0.20 | 14 | 0 | struct:proto3 |
| `kby` | 0.20 | 2 | 0 | struct:proto3 |
| `kbz` | 0.20 | 2 | 0 | struct:proto3 |
| `lqm` | 0.20 | 1 | 0 | struct:proto3 |
| `lqo` | 0.20 | 1 | 0 | struct:proto3 |
| `lqq` | 0.20 | 4 | 0 | struct:proto3 |
| `nfr` | 0.20 | 2 | 0 | struct:proto3 |
| `nlm` | 0.20 | 2 | 0 | struct:proto3 |
| `nlp` | 0.20 | 7 | 1 | struct:has_sub_refs, struct:proto3 |
| `nlq` | 0.20 | 13 | 0 | struct:proto3 |
| `nlr` | 0.20 | 2 | 0 | struct:proto3 |
| `nls` | 0.20 | 13 | 1 | struct:has_sub_refs, struct:proto3 |
| `nlt` | 0.20 | 1 | 0 | struct:proto3 |
| `nlu` | 0.20 | 6 | 1 | struct:has_sub_refs, struct:proto3 |
| `nlv` | 0.20 | 1 | 0 | struct:proto3 |
| `nlw` | 0.20 | 1 | 0 | struct:proto3 |
| `nlx` | 0.20 | 2 | 0 | struct:proto3 |
| `nly` | 0.20 | 3 | 0 | struct:proto3 |
| `nlz` | 0.20 | 4 | 1 | struct:has_sub_refs, struct:proto3 |
| `nma` | 0.20 | 4 | 0 | struct:proto3 |
| `nmb` | 0.20 | 1 | 0 | struct:proto3 |
| `nmc` | 0.20 | 1 | 0 | struct:proto3 |
| `nmf` | 0.20 | 4 | 0 | struct:proto3 |
| `nmg` | 0.20 | 4 | 4 | struct:has_sub_refs, struct:proto3 |
| `nmh` | 0.20 | 2 | 0 | struct:proto3 |
| `nml` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `nmm` | 0.20 | 2 | 0 | struct:proto3 |
| `nmn` | 0.20 | 4 | 1 | struct:has_sub_refs, struct:proto3 |
| `nmr` | 0.20 | 4 | 0 | struct:proto3 |
| `nmu` | 0.20 | 2 | 0 | struct:proto3 |
| `nmv` | 0.20 | 11 | 1 | struct:has_sub_refs, struct:proto3 |
| `nmz` | 0.20 | 1 | 0 | struct:proto3 |
| `nnb` | 0.20 | 1 | 0 | struct:proto3 |
| `nne` | 0.20 | 3 | 0 | struct:proto3 |
| `nni` | 0.20 | 2 | 0 | struct:proto3 |
| `nnj` | 0.20 | 1 | 0 | struct:proto3 |
| `nnk` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `nnl` | 0.20 | 2 | 0 | struct:proto3 |
| `nnm` | 0.20 | 1 | 0 | struct:proto3 |
| `nnp` | 0.20 | 4 | 0 | struct:proto3 |
| `nnq` | 0.20 | 1 | 0 | struct:proto3 |
| `nns` | 0.20 | 2 | 0 | struct:proto3 |
| `nnz` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `noe` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `nol` | 0.20 | 14 | 0 | struct:proto3 |
| `ntp` | 0.20 | 7 | 0 | struct:proto3 |
| `nvf` | 0.20 | 2 | 0 | struct:proto3 |
| `nvi` | 0.20 | 2 | 0 | struct:proto3 |
| `nvj` | 0.20 | 4 | 1 | struct:has_sub_refs, struct:proto3 |
| `nvn` | 0.20 | 1 | 0 | struct:proto3 |
| `nvo` | 0.20 | 7 | 1 | struct:has_sub_refs, struct:proto3 |
| `nvp` | 0.20 | 1 | 0 | struct:proto3 |
| `nvq` | 0.20 | 2 | 0 | struct:proto3 |
| `nvy` | 0.20 | 2 | 0 | struct:proto3 |
| `nvz` | 0.20 | 3 | 0 | struct:proto3 |
| `nwa` | 0.20 | 5 | 0 | struct:proto3 |
| `nwe` | 0.20 | 3 | 0 | struct:proto3 |
| `oey` | 0.20 | 7 | 0 | struct:proto3 |
| `oez` | 0.20 | 5 | 0 | struct:proto3 |
| `ofa` | 0.20 | 2 | 2 | struct:has_sub_refs, struct:proto3 |
| `ofb` | 0.20 | 2 | 0 | struct:proto3 |
| `ofc` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `ofd` | 0.20 | 9 | 1 | struct:has_sub_refs, struct:proto3 |
| `ofe` | 0.20 | 2 | 2 | struct:has_sub_refs, struct:proto3 |
| `off` | 0.20 | 14 | 2 | struct:has_sub_refs, struct:proto3 |
| `ohd` | 0.20 | 4 | 1 | struct:has_sub_refs, struct:proto3 |
| `oqa` | 0.20 | 2 | 0 | struct:proto3 |
| `oqb` | 0.20 | 1 | 0 | struct:proto3 |
| `oqc` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `pim` | 0.20 | 5 | 0 | struct:proto3 |
| `pio` | 0.20 | 2 | 0 | struct:proto3 |
| `pip` | 0.20 | 2 | 0 | struct:proto3 |
| `pir` | 0.20 | 6 | 0 | struct:proto3 |
| `pis` | 0.20 | 2 | 0 | struct:proto3 |
| `pit` | 0.20 | 18 | 2 | struct:has_sub_refs, struct:proto3 |
| `piw` | 0.20 | 2 | 0 | struct:proto3 |
| `pix` | 0.20 | 4 | 0 | struct:proto3 |
| `piy` | 0.20 | 4 | 0 | struct:proto3 |
| `piz` | 0.20 | 5 | 0 | struct:proto3 |
| `pjb` | 0.20 | 11 | 0 | struct:proto3 |
| `pjc` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `pjd` | 0.20 | 1 | 0 | struct:proto3 |
| `poo` | 0.20 | 3 | 0 | struct:proto3 |
| `pop` | 0.20 | 7 | 1 | struct:has_sub_refs, struct:proto3 |
| `qbp` | 0.20 | 1 | 0 | struct:proto3 |
| `qkz` | 0.20 | 5 | 0 | struct:proto3 |
| `qla` | 0.20 | 10 | 1 | struct:has_sub_refs, struct:proto3 |
| `qlb` | 0.20 | 3 | 0 | struct:proto3 |
| `qlc` | 0.20 | 1 | 0 | struct:proto3 |
| `qld` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `qlg` | 0.20 | 2 | 0 | struct:proto3 |
| `rra` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `rrb` | 0.20 | 3 | 0 | struct:proto3 |
| `rrc` | 0.20 | 1 | 0 | struct:proto3 |
| `rsa` | 0.20 | 4 | 2 | struct:has_sub_refs, struct:proto3 |
| `rsb` | 0.20 | 2 | 0 | struct:proto3 |
| `rsg` | 0.20 | 2 | 0 | struct:proto3 |
| `rsi` | 0.20 | 1 | 0 | struct:proto3 |
| `rsj` | 0.20 | 2 | 0 | struct:proto3 |
| `rsl` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `rsm` | 0.20 | 3 | 0 | struct:proto3 |
| `rso` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `rsp` | 0.20 | 1 | 0 | struct:proto3 |
| `rsq` | 0.20 | 2 | 0 | struct:proto3 |
| `rsr` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `rst` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `rsv` | 0.20 | 1 | 0 | struct:proto3 |
| `rsw` | 0.20 | 1 | 0 | struct:proto3 |
| `rsx` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `rsy` | 0.20 | 2 | 0 | struct:proto3 |
| `rtb` | 0.20 | 1 | 0 | struct:proto3 |
| `rtc` | 0.20 | 4 | 0 | struct:proto3 |
| `rte` | 0.20 | 1 | 0 | struct:proto3 |
| `rtf` | 0.20 | 1 | 0 | struct:proto3 |
| `rtg` | 0.20 | 7 | 0 | struct:proto3 |
| `rth` | 0.20 | 2 | 0 | struct:proto3 |
| `rti` | 0.20 | 5 | 4 | struct:has_sub_refs, struct:proto3 |
| `rtj` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `rtm` | 0.20 | 6 | 0 | struct:proto3 |
| `rtn` | 0.20 | 4 | 0 | struct:proto3 |
| `rto` | 0.20 | 7 | 0 | struct:proto3 |
| `rtp` | 0.20 | 9 | 1 | struct:has_sub_refs, struct:proto3 |
| `rtr` | 0.20 | 12 | 2 | struct:has_sub_refs, struct:proto3 |
| `sdg` | 0.20 | 2 | 0 | struct:proto3 |
| `sdh` | 0.20 | 2 | 0 | struct:proto3 |
| `sdx` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `sdy` | 0.20 | 2 | 0 | struct:proto3 |
| `sdz` | 0.20 | 2 | 0 | struct:proto3 |
| `sea` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `sec` | 0.20 | 4 | 1 | struct:has_sub_refs, struct:proto3 |
| `sed` | 0.20 | 3 | 0 | struct:proto3 |
| `see` | 0.20 | 1 | 0 | struct:proto3 |
| `sef` | 0.20 | 1 | 0 | struct:proto3 |
| `seg` | 0.20 | 2 | 0 | struct:proto3 |
| `seh` | 0.20 | 3 | 0 | struct:proto3 |
| `sei` | 0.20 | 1 | 0 | struct:proto3 |
| `sek` | 0.20 | 2 | 0 | struct:proto3 |
| `sel` | 0.20 | 2 | 0 | struct:proto3 |
| `sen` | 0.20 | 2 | 0 | struct:proto3 |
| `seo` | 0.20 | 2 | 0 | struct:proto3 |
| `sep` | 0.20 | 1 | 0 | struct:proto3 |
| `seq` | 0.20 | 8 | 0 | struct:proto3 |
| `ses` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `sfa` | 0.20 | 2 | 0 | struct:proto3 |
| `sfu` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `sgp` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `sgt` | 0.20 | 2 | 0 | struct:proto3 |
| `sgu` | 0.20 | 1 | 0 | struct:proto3 |
| `sgv` | 0.20 | 2 | 0 | struct:proto3 |
| `shm` | 0.20 | 4 | 0 | struct:proto3 |
| `shn` | 0.20 | 2 | 0 | struct:proto3 |
| `sho` | 0.20 | 1 | 0 | struct:proto3 |
| `shp` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `shq` | 0.20 | 15 | 2 | struct:has_sub_refs, struct:proto3 |
| `shr` | 0.20 | 1 | 0 | struct:proto3 |
| `shs` | 0.20 | 2 | 0 | struct:proto3 |
| `sml` | 0.20 | 2 | 0 | struct:proto3 |
| `smm` | 0.20 | 6 | 2 | struct:has_sub_refs, struct:proto3 |
| `tez` | 0.20 | 5 | 0 | struct:proto3 |
| `tle` | 0.20 | 1 | 0 | struct:proto3 |
| `tta` | 0.20 | 6 | 6 | struct:has_sub_refs, struct:proto3 |
| `ttb` | 0.20 | 1 | 0 | struct:proto3 |
| `ttc` | 0.20 | 2 | 0 | struct:proto3 |
| `ttg` | 0.20 | 14 | 1 | struct:has_sub_refs, struct:proto3 |
| `tth` | 0.20 | 6 | 0 | struct:proto3 |
| `tti` | 0.20 | 9 | 0 | struct:proto3 |
| `ttj` | 0.20 | 1 | 0 | struct:proto3 |
| `tuk` | 0.20 | 3 | 0 | struct:proto3 |
| `tul` | 0.20 | 11 | 0 | struct:proto3 |
| `tum` | 0.20 | 4 | 0 | struct:proto3 |
| `tun` | 0.20 | 1 | 0 | struct:proto3 |
| `uff` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `ufh` | 0.20 | 4 | 0 | struct:proto3 |
| `uje` | 0.20 | 5 | 0 | struct:proto3 |
| `ujj` | 0.20 | 1 | 0 | struct:proto3 |
| `ujp` | 0.20 | 2 | 0 | struct:proto3 |
| `ulb` | 0.20 | 2 | 0 | struct:proto3 |
| `ulc` | 0.20 | 3 | 0 | struct:proto3 |
| `upr` | 0.20 | 9 | 2 | struct:has_sub_refs, struct:proto3 |
| `uqw` | 0.20 | 2 | 0 | struct:proto3 |
| `uqx` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `uqy` | 0.20 | 7 | 1 | struct:has_sub_refs, struct:proto3 |
| `uqz` | 0.20 | 6 | 0 | struct:proto3 |
| `ure` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `url` | 0.20 | 10 | 2 | struct:has_sub_refs, struct:proto3 |
| `urm` | 0.20 | 9 | 2 | struct:has_sub_refs, struct:proto3 |
| `urn` | 0.20 | 2 | 0 | struct:proto3 |
| `uro` | 0.20 | 2 | 2 | struct:has_sub_refs, struct:proto3 |
| `uss` | 0.20 | 1 | 0 | struct:proto3 |
| `usv` | 0.20 | 6 | 0 | struct:proto3 |
| `utj` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `utk` | 0.20 | 6 | 0 | struct:proto3 |
| `xgi` | 0.20 | 1 | 0 | struct:proto3 |
| `xhd` | 0.20 | 8 | 2 | struct:has_sub_refs, struct:proto3 |
| `xhe` | 0.20 | 1 | 0 | struct:proto3 |
| `xlg` | 0.20 | 1 | 0 | struct:proto3 |
| `xlh` | 0.20 | 1 | 0 | struct:proto3 |
| `xli` | 0.20 | 5 | 0 | struct:proto3 |
| `xlj` | 0.20 | 1 | 0 | struct:proto3 |
| `xlm` | 0.20 | 1 | 0 | struct:proto3 |
| `xln` | 0.20 | 3 | 0 | struct:proto3 |
| `xlp` | 0.20 | 2 | 0 | struct:proto3 |
| `xlq` | 0.20 | 6 | 0 | struct:proto3 |
| `xlr` | 0.20 | 4 | 0 | struct:proto3 |
| `xlw` | 0.20 | 2 | 0 | struct:proto3 |
| `xlz` | 0.20 | 1 | 0 | struct:proto3 |
| `xmg` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `xmo` | 0.20 | 6 | 0 | struct:proto3 |
| `xmq` | 0.20 | 2 | 0 | struct:proto3 |
| `xtx` | 0.20 | 1 | 0 | struct:proto3 |
| `xub` | 0.20 | 2 | 0 | struct:proto3 |
| `xud` | 0.20 | 1 | 0 | struct:proto3 |
| `xue` | 0.20 | 1 | 0 | struct:proto3 |
| `xuf` | 0.20 | 1 | 0 | struct:proto3 |
| `xuo` | 0.20 | 2 | 0 | struct:proto3 |
| `xus` | 0.20 | 2 | 0 | struct:proto3 |
| `xut` | 0.20 | 4 | 0 | struct:proto3 |
| `xuu` | 0.20 | 3 | 2 | struct:has_sub_refs, struct:proto3 |
| `xvp` | 0.20 | 1 | 0 | struct:proto3 |
| `xvw` | 0.20 | 1 | 0 | struct:proto3 |
| `xvx` | 0.20 | 2 | 0 | struct:proto3 |
| `xvy` | 0.20 | 2 | 0 | struct:proto3 |
| `xwa` | 0.20 | 1 | 0 | struct:proto3 |
| `xwb` | 0.20 | 1 | 0 | struct:proto3 |
| `xwv` | 0.20 | 1 | 0 | struct:proto3 |
| `xwx` | 0.20 | 1 | 0 | struct:proto3 |
| `xwy` | 0.20 | 1 | 0 | struct:proto3 |
| `xxc` | 0.20 | 1 | 0 | struct:proto3 |
| `xxk` | 0.20 | 1 | 0 | struct:proto3 |
| `xxo` | 0.20 | 2 | 0 | struct:proto3 |
| `xxp` | 0.20 | 1 | 0 | struct:proto3 |
| `xyb` | 0.20 | 1 | 0 | struct:proto3 |
| `xyc` | 0.20 | 5 | 2 | struct:has_sub_refs, struct:proto3 |
| `xyd` | 0.20 | 1 | 0 | struct:proto3 |
| `xye` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `xyg` | 0.20 | 1 | 0 | struct:proto3 |
| `xyh` | 0.20 | 1 | 0 | struct:proto3 |
| `xyv` | 0.20 | 5 | 0 | struct:proto3 |
| `xza` | 0.20 | 19 | 1 | struct:has_sub_refs, struct:proto3 |
| `xzb` | 0.20 | 1 | 0 | struct:proto3 |
| `xzc` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `xzw` | 0.20 | 2 | 0 | struct:proto3 |
| `xzx` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `xzy` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `xzz` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `yaa` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `yad` | 0.20 | 4 | 0 | struct:proto3 |
| `yaf` | 0.20 | 1 | 0 | struct:proto3 |
| `yai` | 0.20 | 1 | 0 | struct:proto3 |
| `yal` | 0.20 | 2 | 0 | struct:proto3 |
| `yam` | 0.20 | 1 | 0 | struct:proto3 |
| `yao` | 0.20 | 1 | 0 | struct:proto3 |
| `yaq` | 0.20 | 3 | 0 | struct:proto3 |
| `yat` | 0.20 | 1 | 0 | struct:proto3 |
| `yaw` | 0.20 | 1 | 0 | struct:proto3 |
| `yax` | 0.20 | 1 | 0 | struct:proto3 |
| `yaz` | 0.20 | 1 | 0 | struct:proto3 |
| `yba` | 0.20 | 1 | 0 | struct:proto3 |
| `ybb` | 0.20 | 6 | 0 | struct:proto3 |
| `ybd` | 0.20 | 3 | 0 | struct:proto3 |
| `ybi` | 0.20 | 2 | 0 | struct:proto3 |
| `ybj` | 0.20 | 1 | 0 | struct:proto3 |
| `ybk` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `ybn` | 0.20 | 2 | 0 | struct:proto3 |
| `ybo` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `ybp` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `ybr` | 0.20 | 1 | 0 | struct:proto3 |
| `ybs` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `ybt` | 0.20 | 1 | 0 | struct:proto3 |
| `ypz` | 0.20 | 2 | 0 | struct:proto3 |
| `ysx` | 0.20 | 1 | 0 | struct:proto3 |
| `ysy` | 0.20 | 3 | 0 | struct:proto3 |
| `ysz` | 0.20 | 1 | 0 | struct:proto3 |
| `yta` | 0.20 | 3 | 0 | struct:proto3 |
| `ytb` | 0.20 | 1 | 0 | struct:proto3 |
| `ytc` | 0.20 | 2 | 2 | struct:has_sub_refs, struct:proto3 |
| `ytd` | 0.20 | 2 | 2 | struct:has_sub_refs, struct:proto3 |
| `yte` | 0.20 | 6 | 2 | struct:has_sub_refs, struct:proto3 |
| `ytf` | 0.20 | 1 | 0 | struct:proto3 |
| `yth` | 0.20 | 5 | 4 | struct:has_sub_refs, struct:proto3 |
| `yti` | 0.20 | 3 | 0 | struct:proto3 |
| `ytj` | 0.20 | 2 | 0 | struct:proto3 |
| `ytk` | 0.20 | 3 | 0 | struct:proto3 |
| `ytl` | 0.20 | 2 | 0 | struct:proto3 |
| `ytm` | 0.20 | 2 | 0 | struct:proto3 |
| `yto` | 0.20 | 1 | 0 | struct:proto3 |
| `ytp` | 0.20 | 1 | 0 | struct:proto3 |
| `ytq` | 0.20 | 2 | 0 | struct:proto3 |
| `ytt` | 0.20 | 2 | 0 | struct:proto3 |
| `ytv` | 0.20 | 1 | 0 | struct:proto3 |
| `ytw` | 0.20 | 1 | 0 | struct:proto3 |
| `ytx` | 0.20 | 2 | 0 | struct:proto3 |
| `yty` | 0.20 | 1 | 0 | struct:proto3 |
| `ytz` | 0.20 | 2 | 0 | struct:proto3 |
| `yua` | 0.20 | 2 | 0 | struct:proto3 |
| `yub` | 0.20 | 2 | 0 | struct:proto3 |
| `yuc` | 0.20 | 2 | 0 | struct:proto3 |
| `yud` | 0.20 | 1 | 0 | struct:proto3 |
| `yue` | 0.20 | 2 | 0 | struct:proto3 |
| `yuf` | 0.20 | 1 | 0 | struct:proto3 |
| `yug` | 0.20 | 1 | 0 | struct:proto3 |
| `yuh` | 0.20 | 1 | 0 | struct:proto3 |
| `yui` | 0.20 | 2 | 0 | struct:proto3 |
| `yuj` | 0.20 | 2 | 0 | struct:proto3 |
| `yuk` | 0.20 | 1 | 0 | struct:proto3 |
| `yul` | 0.20 | 1 | 0 | struct:proto3 |
| `yum` | 0.20 | 2 | 0 | struct:proto3 |
| `yun` | 0.20 | 1 | 0 | struct:proto3 |
| `yuo` | 0.20 | 2 | 0 | struct:proto3 |
| `yup` | 0.20 | 1 | 0 | struct:proto3 |
| `yuq` | 0.20 | 2 | 0 | struct:proto3 |
| `yur` | 0.20 | 1 | 0 | struct:proto3 |
| `yus` | 0.20 | 2 | 0 | struct:proto3 |
| `yut` | 0.20 | 1 | 0 | struct:proto3 |
| `yuu` | 0.20 | 1 | 0 | struct:proto3 |
| `yuv` | 0.20 | 1 | 0 | struct:proto3 |
| `yux` | 0.20 | 2 | 0 | struct:proto3 |
| `yuy` | 0.20 | 1 | 0 | struct:proto3 |
| `yuz` | 0.20 | 2 | 0 | struct:proto3 |
| `yva` | 0.20 | 1 | 0 | struct:proto3 |
| `yvb` | 0.20 | 2 | 0 | struct:proto3 |
| `yvc` | 0.20 | 1 | 0 | struct:proto3 |
| `yvd` | 0.20 | 2 | 0 | struct:proto3 |
| `yve` | 0.20 | 2 | 0 | struct:proto3 |
| `yvf` | 0.20 | 1 | 0 | struct:proto3 |
| `yvg` | 0.20 | 2 | 0 | struct:proto3 |
| `yvh` | 0.20 | 1 | 0 | struct:proto3 |
| `yvi` | 0.20 | 1 | 0 | struct:proto3 |
| `yvj` | 0.20 | 1 | 0 | struct:proto3 |
| `yvk` | 0.20 | 1 | 0 | struct:proto3 |
| `yvl` | 0.20 | 2 | 0 | struct:proto3 |
| `yvm` | 0.20 | 1 | 0 | struct:proto3 |
| `yvn` | 0.20 | 1 | 0 | struct:proto3 |
| `yvo` | 0.20 | 1 | 0 | struct:proto3 |
| `yvp` | 0.20 | 1 | 0 | struct:proto3 |
| `yvq` | 0.20 | 1 | 0 | struct:proto3 |
| `yvr` | 0.20 | 1 | 0 | struct:proto3 |
| `yvs` | 0.20 | 1 | 0 | struct:proto3 |
| `yvt` | 0.20 | 1 | 0 | struct:proto3 |
| `yvu` | 0.20 | 2 | 0 | struct:proto3 |
| `yvv` | 0.20 | 2 | 0 | struct:proto3 |
| `yvw` | 0.20 | 1 | 0 | struct:proto3 |
| `yvx` | 0.20 | 1 | 0 | struct:proto3 |
| `yvy` | 0.20 | 1 | 0 | struct:proto3 |
| `yvz` | 0.20 | 1 | 0 | struct:proto3 |
| `ywa` | 0.20 | 1 | 0 | struct:proto3 |
| `ywb` | 0.20 | 2 | 0 | struct:proto3 |
| `ywc` | 0.20 | 1 | 0 | struct:proto3 |
| `ywd` | 0.20 | 1 | 0 | struct:proto3 |
| `ywe` | 0.20 | 2 | 0 | struct:proto3 |
| `ywf` | 0.20 | 2 | 0 | struct:proto3 |
| `ywg` | 0.20 | 1 | 0 | struct:proto3 |
| `ywh` | 0.20 | 1 | 0 | struct:proto3 |
| `ywi` | 0.20 | 2 | 0 | struct:proto3 |
| `ywj` | 0.20 | 2 | 0 | struct:proto3 |
| `ywk` | 0.20 | 2 | 0 | struct:proto3 |
| `ywl` | 0.20 | 2 | 0 | struct:proto3 |
| `ywm` | 0.20 | 2 | 0 | struct:proto3 |
| `ywn` | 0.20 | 2 | 0 | struct:proto3 |
| `ywo` | 0.20 | 2 | 0 | struct:proto3 |
| `ywp` | 0.20 | 1 | 0 | struct:proto3 |
| `ywq` | 0.20 | 1 | 0 | struct:proto3 |
| `ywr` | 0.20 | 1 | 0 | struct:proto3 |
| `yws` | 0.20 | 1 | 0 | struct:proto3 |
| `ywt` | 0.20 | 1 | 0 | struct:proto3 |
| `ywu` | 0.20 | 1 | 0 | struct:proto3 |
| `ywv` | 0.20 | 1 | 0 | struct:proto3 |
| `yww` | 0.20 | 1 | 0 | struct:proto3 |
| `ywx` | 0.20 | 2 | 0 | struct:proto3 |
| `ywy` | 0.20 | 2 | 0 | struct:proto3 |
| `ywz` | 0.20 | 1 | 0 | struct:proto3 |
| `yxa` | 0.20 | 1 | 0 | struct:proto3 |
| `yxb` | 0.20 | 1 | 0 | struct:proto3 |
| `yxc` | 0.20 | 2 | 0 | struct:proto3 |
| `yxd` | 0.20 | 2 | 0 | struct:proto3 |
| `yxe` | 0.20 | 1 | 0 | struct:proto3 |
| `yxf` | 0.20 | 1 | 0 | struct:proto3 |
| `yxg` | 0.20 | 2 | 0 | struct:proto3 |
| `yxh` | 0.20 | 2 | 0 | struct:proto3 |
| `yxi` | 0.20 | 2 | 0 | struct:proto3 |
| `yxj` | 0.20 | 2 | 0 | struct:proto3 |
| `yxk` | 0.20 | 2 | 0 | struct:proto3 |
| `yxl` | 0.20 | 1 | 0 | struct:proto3 |
| `yxm` | 0.20 | 2 | 0 | struct:proto3 |
| `yxn` | 0.20 | 2 | 0 | struct:proto3 |
| `yxo` | 0.20 | 2 | 0 | struct:proto3 |
| `yxp` | 0.20 | 2 | 0 | struct:proto3 |
| `yxq` | 0.20 | 2 | 0 | struct:proto3 |
| `yxr` | 0.20 | 2 | 0 | struct:proto3 |
| `yxs` | 0.20 | 1 | 0 | struct:proto3 |
| `yxt` | 0.20 | 1 | 0 | struct:proto3 |
| `yxu` | 0.20 | 2 | 0 | struct:proto3 |
| `yxv` | 0.20 | 1 | 0 | struct:proto3 |
| `yxw` | 0.20 | 1 | 0 | struct:proto3 |
| `yxx` | 0.20 | 2 | 0 | struct:proto3 |
| `yxy` | 0.20 | 1 | 0 | struct:proto3 |
| `yxz` | 0.20 | 1 | 0 | struct:proto3 |
| `yya` | 0.20 | 1 | 0 | struct:proto3 |
| `yyb` | 0.20 | 1 | 0 | struct:proto3 |
| `yyc` | 0.20 | 1 | 0 | struct:proto3 |
| `yyd` | 0.20 | 1 | 0 | struct:proto3 |
| `yye` | 0.20 | 2 | 0 | struct:proto3 |
| `yyf` | 0.20 | 1 | 0 | struct:proto3 |
| `yyg` | 0.20 | 1 | 0 | struct:proto3 |
| `yyh` | 0.20 | 1 | 0 | struct:proto3 |
| `yyi` | 0.20 | 1 | 0 | struct:proto3 |
| `yyk` | 0.20 | 2 | 0 | struct:proto3 |
| `yyn` | 0.20 | 2 | 0 | struct:proto3 |
| `yyo` | 0.20 | 2 | 0 | struct:proto3 |
| `yyp` | 0.20 | 2 | 0 | struct:proto3 |
| `yyq` | 0.20 | 2 | 0 | struct:proto3 |
| `yyr` | 0.20 | 3 | 0 | struct:proto3 |
| `yys` | 0.20 | 2 | 0 | struct:proto3 |
| `yyt` | 0.20 | 2 | 0 | struct:proto3 |
| `yyu` | 0.20 | 2 | 0 | struct:proto3 |
| `yyv` | 0.20 | 2 | 0 | struct:proto3 |
| `yyw` | 0.20 | 1 | 0 | struct:proto3 |
| `yyx` | 0.20 | 11 | 0 | struct:proto3 |
| `yyz` | 0.20 | 1 | 0 | struct:proto3 |
| `yza` | 0.20 | 3 | 0 | struct:proto3 |
| `yzb` | 0.20 | 2 | 0 | struct:proto3 |
| `yzc` | 0.20 | 2 | 0 | struct:proto3 |
| `yzd` | 0.20 | 2 | 0 | struct:proto3 |
| `yze` | 0.20 | 2 | 0 | struct:proto3 |
| `yzf` | 0.20 | 1 | 0 | struct:proto3 |
| `yzh` | 0.20 | 1 | 0 | struct:proto3 |
| `yzi` | 0.20 | 1 | 0 | struct:proto3 |
| `yzj` | 0.20 | 1 | 0 | struct:proto3 |
| `yzk` | 0.20 | 1 | 0 | struct:proto3 |
| `yzl` | 0.20 | 1 | 0 | struct:proto3 |
| `yzm` | 0.20 | 1 | 0 | struct:proto3 |
| `yzn` | 0.20 | 1 | 0 | struct:proto3 |
| `yzo` | 0.20 | 2 | 0 | struct:proto3 |
| `yzp` | 0.20 | 1 | 0 | struct:proto3 |
| `yzs` | 0.20 | 2 | 0 | struct:proto3 |
| `yzt` | 0.20 | 1 | 0 | struct:proto3 |
| `yzu` | 0.20 | 1 | 0 | struct:proto3 |
| `yzv` | 0.20 | 2 | 0 | struct:proto3 |
| `yzx` | 0.20 | 1 | 0 | struct:proto3 |
| `yzz` | 0.20 | 2 | 0 | struct:proto3 |
| `zaa` | 0.20 | 1 | 0 | struct:proto3 |
| `zab` | 0.20 | 2 | 0 | struct:proto3 |
| `zad` | 0.20 | 2 | 0 | struct:proto3 |
| `zag` | 0.20 | 1 | 0 | struct:proto3 |
| `zah` | 0.20 | 1 | 0 | struct:proto3 |
| `zai` | 0.20 | 2 | 0 | struct:proto3 |
| `zaj` | 0.20 | 2 | 0 | struct:proto3 |
| `zak` | 0.20 | 1 | 0 | struct:proto3 |
| `zal` | 0.20 | 2 | 0 | struct:proto3 |
| `zam` | 0.20 | 2 | 0 | struct:proto3 |
| `zao` | 0.20 | 3 | 0 | struct:proto3 |
| `zaq` | 0.20 | 2 | 0 | struct:proto3 |
| `zau` | 0.20 | 2 | 0 | struct:proto3 |
| `zav` | 0.20 | 1 | 0 | struct:proto3 |
| `zax` | 0.20 | 2 | 0 | struct:proto3 |
| `zaz` | 0.20 | 1 | 0 | struct:proto3 |
| `zba` | 0.20 | 1 | 0 | struct:proto3 |
| `zbb` | 0.20 | 1 | 0 | struct:proto3 |
| `zbc` | 0.20 | 1 | 0 | struct:proto3 |
| `zbd` | 0.20 | 1 | 0 | struct:proto3 |
| `zbe` | 0.20 | 2 | 0 | struct:proto3 |
| `zbf` | 0.20 | 1 | 0 | struct:proto3 |
| `zbg` | 0.20 | 2 | 0 | struct:proto3 |
| `zbh` | 0.20 | 1 | 0 | struct:proto3 |
| `zbi` | 0.20 | 1 | 0 | struct:proto3 |
| `zbj` | 0.20 | 1 | 0 | struct:proto3 |
| `zbk` | 0.20 | 2 | 0 | struct:proto3 |
| `zbl` | 0.20 | 2 | 0 | struct:proto3 |
| `zbm` | 0.20 | 2 | 0 | struct:proto3 |
| `zbn` | 0.20 | 1 | 0 | struct:proto3 |
| `zbo` | 0.20 | 2 | 0 | struct:proto3 |
| `zbp` | 0.20 | 2 | 0 | struct:proto3 |
| `zbq` | 0.20 | 2 | 0 | struct:proto3 |
| `zbr` | 0.20 | 1 | 0 | struct:proto3 |
| `zbs` | 0.20 | 1 | 0 | struct:proto3 |
| `zbt` | 0.20 | 2 | 0 | struct:proto3 |
| `zbu` | 0.20 | 2 | 0 | struct:proto3 |
| `zbv` | 0.20 | 1 | 0 | struct:proto3 |
| `zde` | 0.20 | 1 | 0 | struct:proto3 |
| `zhd` | 0.20 | 1 | 0 | struct:proto3 |
| `zhg` | 0.20 | 1 | 0 | struct:proto3 |
| `ziu` | 0.20 | 1 | 0 | struct:proto3 |
| `zki` | 0.20 | 1 | 0 | struct:proto3 |
| `zkm` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `zko` | 0.20 | 7 | 1 | struct:has_sub_refs, struct:proto3 |
| `zkp` | 0.20 | 2 | 0 | struct:proto3 |
| `zkq` | 0.20 | 1 | 0 | struct:proto3 |
| `zkr` | 0.20 | 2 | 0 | struct:proto3 |
| `zku` | 0.20 | 2 | 0 | struct:proto3 |
| `zkv` | 0.20 | 4 | 0 | struct:proto3 |
| `zkw` | 0.20 | 1 | 0 | struct:proto3 |
| `zkz` | 0.20 | 1 | 0 | struct:proto3 |
| `zla` | 0.20 | 1 | 0 | struct:proto3 |
| `znf` | 0.20 | 1 | 0 | struct:proto3 |
| `zol` | 0.20 | 1 | 0 | struct:proto3 |
| `zpq` | 0.20 | 1 | 0 | struct:proto3 |
| `zql` | 0.20 | 4 | 0 | struct:proto3 |
| `zqv` | 0.20 | 1 | 0 | struct:proto3 |
| `zqy` | 0.20 | 1 | 0 | struct:proto3 |
| `zra` | 0.20 | 1 | 0 | struct:proto3 |
| `zrx` | 0.20 | 1 | 0 | struct:proto3 |
| `zrz` | 0.20 | 1 | 0 | struct:proto3 |
| `zsb` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `zsf` | 0.20 | 1 | 0 | struct:proto3 |
| `zsg` | 0.20 | 2 | 0 | struct:proto3 |
| `zsh` | 0.20 | 2 | 0 | struct:proto3 |
| `zsi` | 0.20 | 12 | 1 | struct:has_sub_refs, struct:proto3 |
| `zsl` | 0.20 | 1 | 0 | struct:proto3 |
| `zsm` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `zsn` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `zso` | 0.20 | 2 | 0 | struct:proto3 |
| `zsp` | 0.20 | 2 | 0 | struct:proto3 |
| `zss` | 0.20 | 1 | 0 | struct:proto3 |
| `zsu` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `zsv` | 0.20 | 1 | 0 | struct:proto3 |
| `zsw` | 0.20 | 2 | 0 | struct:proto3 |
| `zsx` | 0.20 | 1 | 0 | struct:proto3 |
| `zsy` | 0.20 | 2 | 0 | struct:proto3 |
| `zsz` | 0.20 | 1 | 0 | struct:proto3 |
| `zta` | 0.20 | 8 | 3 | struct:has_sub_refs, struct:proto3 |
| `ztc` | 0.20 | 3 | 0 | struct:proto3 |
| `zte` | 0.20 | 24 | 0 | struct:proto3 |
| `ztf` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `ztg` | 0.20 | 1 | 0 | struct:proto3 |
| `zti` | 0.20 | 2 | 0 | struct:proto3 |
| `ztj` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `ztk` | 0.20 | 1 | 0 | struct:proto3 |
| `ztl` | 0.20 | 4 | 2 | struct:has_sub_refs, struct:proto3 |
| `ztm` | 0.20 | 2 | 1 | struct:has_sub_refs, struct:proto3 |
| `ztn` | 0.20 | 1 | 0 | struct:proto3 |
| `zto` | 0.20 | 1 | 0 | struct:proto3 |
| `ztp` | 0.20 | 2 | 0 | struct:proto3 |
| `ztr` | 0.20 | 3 | 0 | struct:proto3 |
| `ztu` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `ztv` | 0.20 | 11 | 2 | struct:has_sub_refs, struct:proto3 |
| `ztw` | 0.20 | 1 | 0 | struct:proto3 |
| `zty` | 0.20 | 1 | 0 | struct:proto3 |
| `ztz` | 0.20 | 9 | 1 | struct:has_sub_refs, struct:proto3 |
| `zua` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `zub` | 0.20 | 12 | 1 | struct:has_sub_refs, struct:proto3 |
| `zuc` | 0.20 | 1 | 0 | struct:proto3 |
| `zud` | 0.20 | 1 | 0 | struct:proto3 |
| `zuf` | 0.20 | 7 | 0 | struct:proto3 |
| `zug` | 0.20 | 1 | 0 | struct:proto3 |
| `zuh` | 0.20 | 2 | 0 | struct:proto3 |
| `zui` | 0.20 | 2 | 0 | struct:proto3 |
| `zuj` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `zuk` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `zul` | 0.20 | 3 | 0 | struct:proto3 |
| `zum` | 0.20 | 3 | 1 | struct:has_sub_refs, struct:proto3 |
| `zun` | 0.20 | 6 | 0 | struct:proto3 |
| `zup` | 0.20 | 1 | 0 | struct:proto3 |
| `zus` | 0.20 | 5 | 1 | struct:has_sub_refs, struct:proto3 |
| `zut` | 0.20 | 2 | 0 | struct:proto3 |
| `zuu` | 0.20 | 6 | 2 | struct:has_sub_refs, struct:proto3 |
| `zuv` | 0.20 | 2 | 0 | struct:proto3 |
| `zuy` | 0.20 | 1 | 0 | struct:proto3 |
| `zuz` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `zvb` | 0.20 | 1 | 1 | struct:has_sub_refs, struct:proto3 |
| `zvf` | 0.20 | 1 | 0 | struct:proto3 |
| `zvh` | 0.20 | 1 | 0 | struct:proto3 |
| `zww` | 0.20 | 3 | 0 | struct:proto3 |
