# Android Auto 17.3.662804-release Static Proto Schema Matches

This report is generated from protobuf-lite `RawMessageInfo` metadata and
static service/semantic dispatch evidence. It does not use a live Android Auto session.

## Provenance

- APK SHA-256: `1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344`
- Canonical messages: 422
- Decoded APK messages: 1957
- Canonical enums: 117
- Decoded APK enums: 134
- Canonical message-reference edges: 278
- APK field-linked reference edges: 1273

## Summary

- Resolved mappings: 155
- High confidence (structure + dispatch): 39
- Medium confidence (unique structure): 116
- Static dispatch observations considered: 129
- Explicit service/log dispatch schema conflicts: 0
- Globally unique enum numeric-domain mappings: 13
- Direct child-schema conflicts described: 19

## Dispatch-resolved and confirmed mappings

| Canonical message | APK class | Status | Evidence |
|---|---|---|---|
| `oaa.proto.messages.AudioFocusResponse` | `xfc` | unique_structural_dispatch_confirmed | control ID `0x0013` at `defpackage/iyk.java:288`; control ID `0x0013` at `defpackage/rjn.java:86`; control ID `0x0013` at `defpackage/rri.java:226` |
| `oaa.proto.messages.AuthCompleteIndication` | `xfg` | dispatch_resolved | control ID `0x0004` at `defpackage/iyk.java:473`; control ID `0x0004` at `defpackage/rjn.java:142`; control ID `0x0004` at `defpackage/rri.java:382` |
| `oaa.proto.messages.BluetoothAuthenticationData` | `xfj` | unique_structural_dispatch_confirmed | bluetooth ID `0x8003` at `defpackage/rqj.java:80`; named_log ID `0x8003` at `defpackage/rqj.java:116` |
| `oaa.proto.messages.BluetoothAuthenticationResult` | `xfk` | dispatch_resolved | canonical_log ID `0x8004` at `defpackage/rfi.java:178`; canonical_log ID `0x8004` at `defpackage/rfi.java:191` |
| `oaa.proto.messages.BluetoothPairingResponse` | `xfn` | unique_structural_dispatch_confirmed | bluetooth ID `0x8002` at `defpackage/rqj.java:23`; named_log ID `0x8002` at `defpackage/rqj.java:35` |
| `oaa.proto.messages.ByeByeResponse` | `xft` | dispatch_resolved | canonical_log ID `0x0010` at `defpackage/iyk.java:737`; canonical_log ID `0x0010` at `defpackage/iyk.java:759`; canonical_log ID `0x0010` at `defpackage/rri.java:625` |
| `oaa.proto.messages.CallAvailabilityStatus` | `xfu` | dispatch_resolved | control ID `0x0018` at `defpackage/iyk.java:338`; control ID `0x0018` at `defpackage/rri.java:273` |
| `oaa.proto.messages.CarControlGroupUpdate` | `xga` | dispatch_resolved | car_control ID `0x8007` at `defpackage/ixb.java:163` |
| `oaa.proto.messages.CarLocalMediaPlaybackMetadata` | `xgf` | unique_structural_dispatch_confirmed | car_local_media ID `0x8002` at `defpackage/ixi.java:83` |
| `oaa.proto.messages.CarLocalMediaPlaybackRequest` | `xgg` | dispatch_resolved | canonical_log ID `0x0000` at `defpackage/iiy.java:138` |
| `oaa.proto.messages.CarPropertyChangeEvent` | `xgj` | unique_structural_dispatch_confirmed | car_control ID `0x8005` at `defpackage/ixb.java:132` |
| `oaa.proto.messages.InputBindingRequest` | `xhx` | dispatch_resolved | input_source ID `0x8002` at `defpackage/rjq.java:118` |
| `oaa.proto.messages.InputBindingResponse` | `xhy` | dispatch_resolved | input_source ID `0x8003` at `defpackage/rjq.java:155` |
| `oaa.proto.messages.InputEventIndication` | `xhp` | unique_structural_dispatch_confirmed | input_source ID `0x8001` at `defpackage/rjq.java:81` |
| `oaa.proto.messages.InstrumentClusterStart` | `xjl` | dispatch_resolved | navigation ID `0x8001` at `defpackage/izq.java:68` |
| `oaa.proto.messages.InstrumentClusterStop` | `xjm` | dispatch_resolved | navigation ID `0x8002` at `defpackage/izq.java:27` |
| `oaa.proto.messages.NavigationFocusRequest` | `xit` | dispatch_resolved | control ID `0x000d` at `defpackage/rjn.java:331` |
| `oaa.proto.messages.PhoneStatusInput` | `xka` | unique_structural_dispatch_confirmed | phone_status ID `0x8002` at `defpackage/izw.java:23` |
| `oaa.proto.messages.PingRequest` | `xkd` | unique_structural_dispatch_confirmed | control ID `0x000b` at `defpackage/iyk.java:554`; control ID `0x000b` at `defpackage/rjn.java:257`; control ID `0x000b` at `defpackage/rri.java:442` |
| `oaa.proto.messages.PingResponse` | `xke` | unique_structural_dispatch_confirmed | control ID `0x000c` at `defpackage/iyk.java:591`; control ID `0x000c` at `defpackage/rjn.java:295`; control ID `0x000c` at `defpackage/rri.java:496` |
| `oaa.proto.messages.RadioFavoriteListNotification` | `xkl` | dispatch_resolved | radio ID `0x8020` at `defpackage/jai.java:188`; named_log ID `0x8020` at `defpackage/jai.java:199` |
| `oaa.proto.messages.RadioMuteResponse` | `xkp` | dispatch_resolved | radio ID `0x801d` at `defpackage/jai.java:112`; named_log ID `0x801d` at `defpackage/jai.java:123` |
| `oaa.proto.messages.RadioProgramInfoNotification` | `xkt` | unique_structural_dispatch_confirmed | radio ID `0x801b` at `defpackage/jai.java:64`; named_log ID `0x801b` at `defpackage/jai.java:75` |
| `oaa.proto.messages.RadioProgramListNotification` | `xku` | dispatch_resolved | radio ID `0x801a` at `defpackage/jai.java:26`; named_log ID `0x801a` at `defpackage/jai.java:37` |
| `oaa.proto.messages.RadioTuneResponse` | `xlc` | dispatch_resolved | radio ID `0x801f` at `defpackage/jai.java:150`; named_log ID `0x801f` at `defpackage/jai.java:161` |
| `oaa.proto.messages.RegisterCarPropertyListenersRequest` | `xli` | dispatch_resolved | canonical_log ID `0x0000` at `defpackage/iip.java:266` |
| `oaa.proto.messages.RegisterCarPropertyListenersResponse` | `xlj` | dispatch_resolved | car_control ID `0x8004` at `defpackage/ixb.java:101` |
| `oaa.proto.messages.SensorEventIndication` | `xln` | unique_structural_dispatch_confirmed | sensor_source ID `0x8003` at `defpackage/rjs.java:171` |
| `oaa.proto.messages.SensorRequest` | `xlq` | unique_structural_dispatch_confirmed | sensor_source ID `0x8001` at `defpackage/rjs.java:81` |
| `oaa.proto.messages.SensorStartResponseMessage` | `xlr` | dispatch_resolved | sensor_source ID `0x8002` at `defpackage/rjs.java:126` |
| `oaa.proto.messages.ServiceDiscoveryRequest` | `xlw` | unique_structural_dispatch_confirmed | control ID `0x0005` at `defpackage/rjn.java:179` |
| `oaa.proto.messages.ServiceDiscoveryResponse` | `xlx` | unique_structural_dispatch_confirmed | control ID `0x0006` at `defpackage/iyk.java:210`; control ID `0x0006` at `defpackage/rjn.java:220`; control ID `0x0006` at `defpackage/rri.java:182` |
| `oaa.proto.messages.SetCarPropertyValueRequest` | `xlz` | unique_structural_dispatch_confirmed | canonical_log ID `0x0000` at `defpackage/iip.java:933` |
| `oaa.proto.messages.SetCarPropertyValueResponse` | `xma` | unique_structural_dispatch_confirmed | car_control ID `0x8002` at `defpackage/ixb.java:32` |
| `oaa.proto.messages.ShutdownRequest` | `xfs` | dispatch_resolved | control ID `0x000f` at `defpackage/iyk.java:684`; control ID `0x000f` at `defpackage/rjn.java:411`; control ID `0x000f` at `defpackage/rri.java:576` |
| `oaa.proto.messages.UpdateUiConfigRequest` | `xms` | dispatch_resolved | canonical_log ID `0x0000` at `defpackage/jdc.java:125`; canonical_log ID `0x8009` at `defpackage/jdc.java:207`; canonical_log ID `0x8009` at `defpackage/jdc.java:213` |
| `oaa.proto.messages.VideoFocusIndication` | `xnb` | dispatch_resolved | media_sink ID `0x8008` at `defpackage/jdc.java:150`; media_sink ID `0x8008` at `defpackage/rjt.java:83` |
| `oaa.proto.messages.VideoFocusRequest` | `xnd` | unique_structural_dispatch_confirmed | media_sink ID `0x8007` at `defpackage/rjt.java:31` |
| `oaa.proto.messages.WifiCredentialsResponse` | `xng` | unique_structural_dispatch_confirmed | wifi_projection ID `0x8002` at `defpackage/jau.java:38`; named_log ID `0x8002` at `defpackage/jau.java:49` |

## Graph-resolved mappings

These mappings were ambiguous by local shape and became unique after
field-number-labelled message-edge constraint propagation.

| Canonical message | APK class | Initial candidates |
|---|---|---:|
| `oaa.proto.data.AbsoluteInputEvent` | `xes` | 2 |
| `oaa.proto.data.AbsoluteInputEvents` | `xet` | 24 |
| `oaa.proto.data.Accel` | `xeu` | 11 |
| `oaa.proto.data.ButtonEvents` | `xib` | 24 |
| `oaa.proto.data.CapabilityFlag` | `abuf` | 2 |
| `oaa.proto.data.CapabilityPair` | `abuq` | 5 |
| `oaa.proto.data.Diagnostics` | `xgx` | 6 |
| `oaa.proto.data.DrivingStatus` | `xhb` | 4 |
| `oaa.proto.data.Environment` | `xhc` | 11 |
| `oaa.proto.data.Gear` | `xhh` | 11 |
| `oaa.proto.data.Gyro` | `xhl` | 11 |
| `oaa.proto.data.HVAC` | `xhn` | 8 |
| `oaa.proto.data.InputModelDescriptor` | `abvb` | 3 |
| `oaa.proto.data.NavigationImageOptions` | `xji` | 3 |
| `oaa.proto.data.NightMode` | `xjp` | 11 |
| `oaa.proto.data.Odometer` | `xjq` | 2 |
| `oaa.proto.data.ParkingBrake` | `xju` | 2 |
| `oaa.proto.data.Passenger` | `xjv` | 11 |
| `oaa.proto.data.RPM` | `xlm` | 4 |
| `oaa.proto.data.RadioBands` | `xkj` | 24 |
| `oaa.proto.data.RadioChannelConfig` | `xkx` | 10 |
| `oaa.proto.data.RawEvTripSettings` | `xle` | 6 |
| `oaa.proto.data.RawVehicleEnergyModel` | `xlg` | 6 |
| `oaa.proto.data.RelativeInputEvent` | `xlk` | 2 |
| `oaa.proto.data.RelativeInputEvents` | `xll` | 24 |
| `oaa.proto.data.SteeringWheel` | `xgw` | 2 |
| `oaa.proto.data.TirePressure` | `xmf` | 2 |
| `oaa.proto.data.TollCardData` | `xmg` | 2 |
| `oaa.proto.data.TouchLocation` | `xmh` | 2 |
| `oaa.proto.data.TrailerData` | `xmj` | 270 |
| `oaa.proto.data.TransportCapabilityEntry` | `abxp` | 12 |
| `oaa.proto.data.VehicleEnergyModelData` | `xeq` | 88 |
| `oaa.proto.data.VehicleEnergyValue` | `xep` | 6 |
| `oaa.proto.data.VersionFeatureFlags` | `xnq` | 5 |
| `oaa.proto.data.WifiChannel` | `xnh` | 6 |
| `oaa.proto.messages.CarAction` | `xdw` | 9 |
| `oaa.proto.messages.CarActionControl` | `xfv` | 30 |
| `oaa.proto.messages.CarProperty` | `xee` | 3 |
| `oaa.proto.messages.CarPropertyAreaConfig` | `xdv` | 5 |
| `oaa.proto.messages.CarPropertyControl` | `xeh` | 5 |
| `oaa.proto.messages.IntValues` | `xek` | 4 |
| `oaa.proto.messages.NavigationDestination` | `xix` | 2 |
| `oaa.proto.messages.NavigationLane` | `xjb` | 24 |
| `oaa.proto.messages.NavigationNotification` | `xjg` | 3 |
| `oaa.proto.messages.NavigationRemainingDistance` | `xjo` | 2 |
| `oaa.proto.messages.NavigationRoadInfo` | `xiv` | 5 |
| `oaa.proto.messages.NavigationStepDistance` | `xjo` | 2 |
| `oaa.proto.messages.NavigationText` | `xjf` | 6 |
| `oaa.proto.messages.PhoneInputType` | `xhu` | 11 |
| `oaa.proto.messages.RadioImage` | `xkm` | 6 |
| `oaa.proto.messages.RadioProgramInfo` | `xks` | 8 |
| `oaa.proto.messages.RadioProgramSelector` | `xkv` | 3 |
| `oaa.proto.messages.SetCarPropertyListenerResult` | `xgk` | 2 |
| `oaa.proto.messages.UiConfigData` | `xmn` | 3 |
| `oaa.proto.messages.WifiProjectionEndpoint` | `xnq` | 5 |

## Unique structural mappings

These mappings have one exact APK schema candidate but no dispatch anchor yet.

| Canonical message | APK class | Fields |
|---|---|---:|
| `oaa.proto.data.AVChannel` | `xik` | 8 |
| `oaa.proto.data.AVInputChannel` | `xil` | 2 |
| `oaa.proto.data.AssistantFeatureFlags` | `opi` | 14 |
| `oaa.proto.data.BluetoothChannel` | `xfp` | 2 |
| `oaa.proto.data.ButtonEvent` | `xia` | 4 |
| `oaa.proto.data.CapConnModelList` | `vzh` | 2 |
| `oaa.proto.data.ChannelDescriptor` | `xlv` | 18 |
| `oaa.proto.data.Compass` | `xgp` | 3 |
| `oaa.proto.data.DistanceLabel` | `zad` | 4 |
| `oaa.proto.data.Door` | `xgz` | 3 |
| `oaa.proto.data.GPSLocation` | `xid` | 6 |
| `oaa.proto.data.GpsSatelliteData` | `xhk` | 3 |
| `oaa.proto.data.GpsSatelliteInfo` | `xhj` | 5 |
| `oaa.proto.data.InputChannelConfig` | `xhs` | 5 |
| `oaa.proto.data.Light` | `xic` | 3 |
| `oaa.proto.data.NavigationChannel` | `xjk` | 3 |
| `oaa.proto.data.NavigationDistanceValue` | `yzw` | 3 |
| `oaa.proto.data.RadioBandGroup` | `xki` | 4 |
| `oaa.proto.data.SensorEventFloat` | `xjt` | 1 |
| `oaa.proto.data.Speed` | `xmc` | 3 |
| `oaa.proto.data.TouchEvent` | `xmi` | 3 |
| `oaa.proto.data.TouchPadConfig` | `xhq` | 8 |
| `oaa.proto.data.TouchScreenConfig` | `xhr` | 3 |
| `oaa.proto.data.TransportCapabilities` | `abxq` | 2 |
| `oaa.proto.data.VehicleEnergyInfo` | `xer` | 5 |
| `oaa.proto.messages.AVChannelMediaConfig` | `xig` | 13 |
| `oaa.proto.messages.AVChannelMediaStats` | `xim` | 15 |
| `oaa.proto.messages.AVChannelSetupResponse` | `xgq` | 3 |
| `oaa.proto.messages.AVChannelStartIndication` | `xmd` | 4 |
| `oaa.proto.messages.AVMediaAckIndication` | `xev` | 3 |
| `oaa.proto.messages.CarAreaId` | `xef` | 6 |
| `oaa.proto.messages.CarControl` | `xfy` | 6 |
| `oaa.proto.messages.CarControlGroup` | `xfz` | 2 |
| `oaa.proto.messages.CarLocalMediaPlaybackStatus` | `xgh` | 4 |
| `oaa.proto.messages.CarPropertyConfig` | `xeg` | 7 |
| `oaa.proto.messages.CarPropertyValue` | `xem` | 8 |
| `oaa.proto.messages.ChannelOpenRequest` | `xgm` | 2 |
| `oaa.proto.messages.DestinationDistance` | `xiy` | 3 |
| `oaa.proto.messages.FloatValues` | `xej` | 1 |
| `oaa.proto.messages.LegacyActiveRadioNotification` | `ajdm` | 3 |
| `oaa.proto.messages.LegacyHdRadioComment` | `abrm` | 2 |
| `oaa.proto.messages.LongValues` | `xel` | 1 |
| `oaa.proto.messages.MediaPlaybackMetadata` | `xih` | 7 |
| `oaa.proto.messages.MediaPlaybackStatus` | `xii` | 6 |
| `oaa.proto.messages.NavigationDistance` | `zac` | 4 |
| `oaa.proto.messages.NavigationDistanceEntry` | `zag` | 3 |
| `oaa.proto.messages.NavigationNextTurnDistanceEvent` | `xiw` | 3 |
| `oaa.proto.messages.NavigationStep` | `xjn` | 4 |
| `oaa.proto.messages.NavigationTurnDistance` | `xiz` | 3 |
| `oaa.proto.messages.PhoneCall` | `xjx` | 6 |
| `oaa.proto.messages.PhoneStatusUpdate` | `xjz` | 2 |
| `oaa.proto.messages.RadioMetadata` | `xkn` | 13 |
| `oaa.proto.messages.RadioProgramIdentifier` | `xkr` | 2 |
| `oaa.proto.messages.RadioProgramType` | `xkw` | 2 |
| `oaa.proto.messages.SensorError` | `xlo` | 2 |
| `oaa.proto.messages.StatsEntry` | `xfa` | 4 |
| `oaa.proto.messages.UiConfigEntry` | `xmp` | 2 |
| `oaa.proto.messages.UiConfigValue` | `xmo` | 1 |
| `oaa.proto.messages.WifiNetworkInfo` | `xni` | 5 |
| `oaa.proto.messages.WifiSetupInfo` | `xns` | 5 |
| `oaa.proto.messages.WifiVersionRequest` | `xnv` | 6 |

## Unique enum numeric-domain mappings

These enum identities have a numeric value set unique in both the canonical
catalog and the decoded APK. Names alone are not used for matching.

| Canonical enum | APK enum | Distinct values |
|---|---|---:|
| `oaa.proto.enums.EVConnectorType.Enum` | `xhd` | 13 |
| `oaa.proto.enums.FuelType.Enum` | `xhg` | 13 |
| `oaa.proto.enums.NotificationType.Enum` | `yxp` | 35 |
| `oaa.proto.enums.SensorType.Enum` | `xlu` | 27 |
| `oaa.proto.enums.ShutdownReason.Enum` | `xfr` | 8 |
| `oaa.proto.enums.Status.Enum` | `xin` | 34 |
| `oaa.proto.messages.CarActionId` | `abec` | 5 |
| `oaa.proto.messages.CarPropertyType` | `abzs` | 11 |
| `oaa.proto.messages.VehicleAreaDoor` | `xdy` | 9 |
| `oaa.proto.messages.VehicleAreaMirror` | `xdz` | 4 |
| `oaa.proto.messages.VehicleAreaSeat` | `xea` | 9 |
| `oaa.proto.messages.VehicleAreaWheel` | `xeb` | 5 |
| `oaa.proto.messages.VehicleAreaWindow` | `xec` | 11 |

## Dispatch/schema conflicts

Explicit service or message-name evidence identifies an APK class, but its
17.3 local schema differs from the current canonical definition.

| Canonical message | APK class | Context | Local schema difference | Evidence |
|---|---|---|---|---|

None.

## Dispatch-backed edge conflicts

Identity is supported by exact local shape and unambiguous service dispatch,
but at least one recovered child edge disagrees with the canonical graph.

| Canonical message | APK class |
|---|---|

## Constraint conflicts

These schemas matched locally, but all candidates contradicted at least one
known message-reference edge. They are retained as follow-up evidence rather
than silently accepted or discarded.

| Canonical message | Initial APK candidates |
|---|---|
| `oaa.proto.data.CapabilityConnectionEntry` | `abum` |
| `oaa.proto.data.CapabilityEntry` | `abut` |
| `oaa.proto.data.HandwritingInputModelConfig` | `abvg` |
| `oaa.proto.data.PhoneCapabilities` | `abup` |
| `oaa.proto.data.TransportSecurityDetail` | `abrb`, `akef`, `sxq` |
| `oaa.proto.data.WifiDirectConfig` | `xla` |

### Direct child-schema differences

These are first-order edge disagreements where the APK child class does
not have the local shape of any candidate for the canonical child type.

| Canonical parent | APK parent | Field | Canonical child | APK child |
|---|---|---:|---|---|
| `oaa.proto.data.CapabilityConnectionEntry` | `abum` | 1 | `oaa.proto.data.CapConnValue` | `abui` |
| `oaa.proto.data.CapabilityConnectionEntry` | `abum` | 3 | `oaa.proto.data.CapConnValue` | `abul` |
| `oaa.proto.data.CapabilityConnectionEntry` | `abum` | 4 | `oaa.proto.data.CapConnBool` | `abuj` |
| `oaa.proto.data.CapabilityConnectionEntry` | `abum` | 5 | `oaa.proto.data.CapConnComplex` | `abuh` |
| `oaa.proto.data.CapabilityEntry` | `abut` | 4 | `oaa.proto.data.CapabilityValueMsg` | `abvc` |
| `oaa.proto.data.CapabilityEntry` | `abut` | 5 | `oaa.proto.data.CapabilityValueMsg` | `abun` |
| `oaa.proto.data.CapabilityEntry` | `abut` | 6 | `oaa.proto.data.CapabilityValueMsg` | `abuu` |
| `oaa.proto.data.CapabilityEntry` | `abut` | 7 | `oaa.proto.data.CapabilityValueMsg` | `abuo` |
| `oaa.proto.data.CapabilityEntry` | `abut` | 10 | `oaa.proto.data.CapabilityValueMsg` | `abvi` |
| `oaa.proto.data.HandwritingInputModelConfig` | `abvg` | 2 | `oaa.proto.data.InputModelDescriptor` | `abup` |
| `oaa.proto.data.PhoneCapabilities` | `abup` | 2 | `oaa.proto.data.DeviceInfo` | `abtq` |
| `oaa.proto.data.PhoneCapabilities` | `abup` | 3 | `oaa.proto.data.PhoneConnectionConfig` | `abts` |
| `oaa.proto.data.TransportSecurityDetail` | `abrb` | 1 | `oaa.proto.data.TransportSecurityCertChain` | `abqz` |
| `oaa.proto.data.TransportSecurityDetail` | `abrb` | 2 | `oaa.proto.data.TransportSecurityParams` | `abra` |
| `oaa.proto.data.TransportSecurityDetail` | `akef` | 1 | `oaa.proto.data.TransportSecurityCertChain` | `akee` |
| `oaa.proto.data.TransportSecurityDetail` | `akef` | 2 | `oaa.proto.data.TransportSecurityParams` | `tjw` |
| `oaa.proto.data.TransportSecurityDetail` | `sxq` | 1 | `oaa.proto.data.TransportSecurityCertChain` | `syj` |
| `oaa.proto.data.TransportSecurityDetail` | `sxq` | 2 | `oaa.proto.data.TransportSecurityParams` | `sxp` |
| `oaa.proto.data.WifiDirectConfig` | `xla` | 5 | `oaa.proto.data.GroupOwnerInfo` | `xkm` |

## Limitations

- Unique structure is evidence of identity, not proof of original Google naming.
- Empty and small messages remain highly ambiguous until graph or dispatch constraints apply.
- Field references are recovered where the `RawMessageInfo` object-array cursor and JADX field declarations are complete.
- Canonical corrections describe 17.3; consumers supporting older releases should preserve version-compatibility policy at their API boundary.
- Runtime behavior, timing, and state-machine semantics remain outside schema matching.
