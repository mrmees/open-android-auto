# Audio - Cross-Version Mapping

**Mappings:** 7 | **Versions:** 15.9, 16.1, 16.2

| Proto Name | 15.9 | 16.1 | 16.2 | Fields (15.9/16.1/16.2) |
|---|---|---|---|---|
| AudioConfig | `vnx` | `vvp` | `vvb` | 3/3/3 |
| AudioFocusChannel | -- | `vxq` | `vxc` | 0/0/0 |
| AudioFocusRequest | `vnz` | `vvr` | `vvd` | 1/1/1 |
| AudioFocusResponse | `vny` | `vvq` | `vvc` | 2/2/2 |
| ~~AudioFocusState~~ | ~~`vth`~~ | ~~`waz`~~ | ~~`waq`~~ | ~~1/1/1~~ | **RETRACTED** — waq is RadioFavoriteToggleRequest (radio ch 15) |
| ~~AudioStreamType~~ | ~~`vti`~~ | ~~`wba`~~ | ~~`war`~~ | ~~1/1/1~~ | **RETRACTED** — war is RadioTuneDirectionRequest (radio ch 15) |
| ~~AudioStreamTypeEnum~~ | -- | -- | -- | 0/0/0 | **RETRACTED** — actually RadioTuneDirection enum (UP=1, DOWN=2) |
