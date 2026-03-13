# Navigation - Cross-Version Mapping

**Mappings:** 31 | **Versions:** 15.9, 16.1, 16.2

| Proto Name | 15.9 | 16.1 | 16.2 | Fields (15.9/16.1/16.2) |
|---|---|---|---|---|
| ChargingStationDetails | `vph` | `vwz` | `vwl` | 3/3/3 |
| DestinationDistance | `vrn` | `vzf` | `vyr` | 3/3/3 |
| DistanceLabel | `xfb` | `xnc` | `xmn` | 4/4/4 |
| LaneShape | `vrp` | `vzh` | `vyt` | 0/0/0 |
| NavigationChannel | `agsu` | `ahdp` | `ahcm` | 3/3/3 |
| NavigationChannelConfig | `vrz` | `vzr` | `vzd` | 3/3/3 |
| NavigationDestination | `vrm` | `vze` | `vyq` | 2/2/2 |
| NavigationDistance | `xfa` | `xnb` | `xmm` | 4/4/4 |
| NavigationDistanceDisplay | `xfc` | `xnd` | `xmo` | 4/4/4 |
| NavigationDistanceEntry | `xfe` | `xnf` | `xmq` | 3/3/3 |
| NavigationDistanceInfo | `xff` | `xng` | `xmr` | 3/3/3 |
| NavigationDistanceOneof | `xfd` | `xne` | -- | 1/1/0 |
| NavigationDistanceValue | `xev` | `xmw` | `xmg` | 3/3/3 |
| ~~NavigationFocusIndication~~ | ~~`vto`~~ | ~~`wbg`~~ | ~~`waw`~~ | ~~1/1/1~~ | **RETRACTED** — wbg=SensorErrorStatus, waw=VehicleEnergyForecast in 16.2 |
| NavigationFocusRequest | `vri` | `vza` | `vyl` | 1/1/1 |
| NavigationFocusResponse | `vrh` | `vyz` | `vyk` | 1/1/1 |
| NavigationImageDimensions | `vry` | `vzq` | `vzc` | 3/3/3 |
| NavigationImageOptions | `vry` | `vzq` | `vzc` | 3/3/3 |
| NavigationLane | `vst` | `vzj` | `vyv` | 1/1/1 |
| NavigationLaneDirection | `vrq` | `vzi` | `vyu` | 2/2/2 |
| NavigationManeuver | `vrs` | `vzk` | `vyw` | 3/3/3 |
| NavigationNextTurnDistanceEvent | `vrl` | `vzd` | `vyp` | 3/3/3 |
| NavigationNotification | `vrw` | `vzo` | `vza` | 2/2/2 |
| NavigationRemainingDistance | `vsd` | `vzv` | `vzh` | 2/2/2 |
| NavigationRoadInfo | `xbx` | `vzc` | `vyo` | 1/1/1 |
| NavigationState | `vrx` | `vzp` | `vzb` | 1/1/1 |
| NavigationStep | `vsc` | `vzu` | `vzg` | 4/4/4 |
| NavigationStepDistance | `xeu` | `xmv` | `xmf` | 2/2/2 |
| NavigationText | -- | `vzn` | `vyz` | 0/1/1 |
| NavigationTurnDistance | `vro` | `vzg` | `vys` | 3/3/3 |
| NavigationTurnEvent | `vru` | `vzm` | `vyy` | 6/6/6 |

Note: `NavigationTurnEvent` still has a deprecated 16.2 class match (`vyy`), but source-backed nav sender tracing did not find a reachable native `0x8004` path in 16.2. Treat this row as class-shape continuity, not proof of an active 16.2 wire message.
