# Android Auto 17.3.662804-release Static Proto Schema Matches

This report is generated from protobuf-lite `RawMessageInfo` metadata and
static service/semantic dispatch evidence, and curated cross-version class
lineage. It does not use a live Android Auto session.

## Provenance

- APK SHA-256: `1db7ce995aa52b2cde47a01abfb0364220fb57fc60217de3ec714e3034795344`
- Canonical messages: 376
- Decoded APK messages: 1957
- Canonical enums: 112
- Decoded APK enums: 134
- Canonical message-reference edges: 223
- APK field-linked reference edges: 1273

## Summary

- Resolved mappings: 175
- High confidence (dispatch or confirmed lineage): 39
- Medium confidence (unique structure): 136
- Static dispatch observations considered: 129
- Cross-version lineage anchors considered: 6
- Legacy canonical identities invalidated: 6
- Explicit service/log dispatch schema conflicts: 0
- Globally unique enum numeric-domain mappings: 13
- Direct child-schema conflicts described: 0
- Resolved-parent child schema differences: 1

## Cross-version class-lineage anchors

Lineage continuity identifies which obfuscated class survived each release.
An `invalidated` disposition means call-site semantics prove that the legacy
canonical name came from an unrelated bundled-library protobuf; it is not a
17.3 protocol mapping.

| Canonical identity | 16.2 → 16.4 → 17.3 | Disposition | Rejected local candidates | Reason |
|---|---|---|---|---|
| `oaa.proto.data.CapabilityConnectionEntry` | `aafl` → `aayi` → `abud` | invalidated | `abum` | The historical class lineage belongs to Google authentication data, while the same-shape 17.3 candidate abum belongs to a separate auth telemetry lineage; neither supports the capability-negotiation name. |
| `oaa.proto.data.CapabilityEntry` | `aagb` → `aayy` → `abut` | invalidated | `abut` | This stable class is a Google Surveys client-capability entry, not an Android Auto phone capability entry. |
| `oaa.proto.data.HandwritingInputModelConfig` | `aago` → `aazl` → `abvg` | invalidated | `abvg` | The five-field lineage is a Google Surveys request-context message; field 2 is the survey client-capability object, not an input-model descriptor. |
| `oaa.proto.data.PhoneCapabilities` | `aafx` → `aayu` → `abup` | invalidated | `abup` | The six-field lineage is Google Surveys client context, not the Android Auto ServiceDiscoveryRequest phone-capabilities message. |
| `oaa.proto.data.TransportSecurityDetail` | `aajh` → `abce` → `abxz` | invalidated | `abrb`, `akef`, `sxq` | The historical four-level child graph survives as Google authentication credential data, not Android Auto transport-security configuration; the three local candidates are unrelated two-way oneofs. |
| `oaa.proto.data.WifiDirectConfig` | `was` → `wtf` → `xla` | invalidated | `xla` | The six-field lineage is radio song metadata, not Wi-Fi Direct connection configuration. |

## Dispatch-resolved mappings

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

| Canonical message | APK class | Initial candidates | Graph evidence |
|---|---|---:|---|
| `oaa.proto.data.AbsoluteInputEvent` | `xes` | 2 | trusted_parent `oaa.proto.data.AbsoluteInputEvents:1` → `oaa.proto.data.AbsoluteInputEvent` (`xet` → `xes`) |
| `oaa.proto.data.AbsoluteInputEvents` | `xet` | 24 | trusted_parent `oaa.proto.messages.InputEventIndication:5` → `oaa.proto.data.AbsoluteInputEvents` (`xhp` → `xet`); compatible_child `oaa.proto.data.AbsoluteInputEvents:1` → `oaa.proto.data.AbsoluteInputEvent` (`xet` → `xes`) |
| `oaa.proto.data.Accel` | `xeu` | 11 | trusted_parent `oaa.proto.messages.SensorEventIndication:19` → `oaa.proto.data.Accel` (`xln` → `xeu`) |
| `oaa.proto.data.AudioConfig` | `xfb` | 2 | trusted_parent `oaa.proto.data.AVChannel:3` → `oaa.proto.data.AudioConfig` (`xik` → `xfb`); trusted_parent `oaa.proto.data.AVInputChannel:2` → `oaa.proto.data.AudioConfig` (`xil` → `xfb`) |
| `oaa.proto.data.BlendedUIConfig` | `xfi` | 3 | trusted_parent `oaa.proto.data.AdditionalVideoConfig:8` → `oaa.proto.data.BlendedUIConfig` (`xml` → `xfi`); compatible_child `oaa.proto.data.BlendedUIConfig:1` → `oaa.proto.data.DisplayCornerRadii` (`xfi` → `xgs`); compatible_child `oaa.proto.data.BlendedUIConfig:2` → `oaa.proto.data.NativeUIElement` (`xfi` → `xir`) |
| `oaa.proto.data.ButtonEvents` | `xib` | 24 | trusted_parent `oaa.proto.messages.InputEventIndication:4` → `oaa.proto.data.ButtonEvents` (`xhp` → `xib`); compatible_child `oaa.proto.data.ButtonEvents:1` → `oaa.proto.data.ButtonEvent` (`xib` → `xia`) |
| `oaa.proto.data.CarControlChannel` | `xgb` | 1 | trusted_parent `oaa.proto.data.ChannelDescriptor:15` → `oaa.proto.data.CarControlChannel` (`xlv` → `xgb`); compatible_child `oaa.proto.data.CarControlChannel:1` → `oaa.proto.messages.CarPropertyConfig` (`xgb` → `xeg`); compatible_child `oaa.proto.data.CarControlChannel:2` → `oaa.proto.messages.CarControl` (`xgb` → `xfy`) |
| `oaa.proto.data.DeviceInfo` | `xen` | 1 | trusted_parent `oaa.proto.messages.WifiVersionRequest:5` → `oaa.proto.data.DeviceInfo` (`xnv` → `xen`) |
| `oaa.proto.data.Diagnostics` | `xgx` | 6 | trusted_parent `oaa.proto.messages.SensorEventIndication:9` → `oaa.proto.data.Diagnostics` (`xln` → `xgx`) |
| `oaa.proto.data.DisplayCornerRadii` | `xgs` | 4 | trusted_parent `oaa.proto.data.BlendedUIConfig:1` → `oaa.proto.data.DisplayCornerRadii` (`xfi` → `xgs`) |
| `oaa.proto.data.DrivingStatus` | `xhb` | 4 | trusted_parent `oaa.proto.messages.SensorEventIndication:13` → `oaa.proto.data.DrivingStatus` (`xln` → `xhb`) |
| `oaa.proto.data.Environment` | `xhc` | 11 | trusted_parent `oaa.proto.messages.SensorEventIndication:11` → `oaa.proto.data.Environment` (`xln` → `xhc`) |
| `oaa.proto.data.FuelLevel` | `xhf` | 1 | trusted_parent `oaa.proto.messages.SensorEventIndication:6` → `oaa.proto.data.FuelLevel` (`xln` → `xhf`) |
| `oaa.proto.data.Gear` | `xhh` | 11 | trusted_parent `oaa.proto.messages.SensorEventIndication:8` → `oaa.proto.data.Gear` (`xln` → `xhh`) |
| `oaa.proto.data.Gyro` | `xhl` | 11 | trusted_parent `oaa.proto.messages.SensorEventIndication:20` → `oaa.proto.data.Gyro` (`xln` → `xhl`) |
| `oaa.proto.data.HVAC` | `xhn` | 8 | trusted_parent `oaa.proto.messages.SensorEventIndication:12` → `oaa.proto.data.HVAC` (`xln` → `xhn`) |
| `oaa.proto.data.HeadUnitInfo` | `xen` | 1 | trusted_parent `oaa.proto.messages.ServiceDiscoveryResponse:17` → `oaa.proto.data.HeadUnitInfo` (`xlx` → `xen`) |
| `oaa.proto.data.NativeUIElement` | `xir` | 2 | trusted_parent `oaa.proto.data.BlendedUIConfig:2` → `oaa.proto.data.NativeUIElement` (`xfi` → `xir`); compatible_child `oaa.proto.data.NativeUIElement:1` → `oaa.proto.data.UIElementPosition` (`xir` → `xlh`) |
| `oaa.proto.data.NavigationImageOptions` | `xji` | 3 | trusted_parent `oaa.proto.data.NavigationChannel:3` → `oaa.proto.data.NavigationImageOptions` (`xjk` → `xji`) |
| `oaa.proto.data.NightMode` | `xjp` | 11 | trusted_parent `oaa.proto.messages.SensorEventIndication:10` → `oaa.proto.data.NightMode` (`xln` → `xjp`) |
| `oaa.proto.data.Odometer` | `xjq` | 2 | trusted_parent `oaa.proto.messages.SensorEventIndication:5` → `oaa.proto.data.Odometer` (`xln` → `xjq`) |
| `oaa.proto.data.ParkingBrake` | `xju` | 2 | trusted_parent `oaa.proto.messages.SensorEventIndication:7` → `oaa.proto.data.ParkingBrake` (`xln` → `xju`) |
| `oaa.proto.data.Passenger` | `xjv` | 11 | trusted_parent `oaa.proto.messages.SensorEventIndication:15` → `oaa.proto.data.Passenger` (`xln` → `xjv`) |
| `oaa.proto.data.PingConfiguration` | `abmh` | 2 | trusted_parent `oaa.proto.messages.AVChannelMediaConfig:1` → `oaa.proto.data.PingConfiguration` (`xig` → `abmh`); trusted_parent `oaa.proto.messages.AVChannelMediaConfig:3` → `oaa.proto.data.PingConfiguration` (`xig` → `abmh`); trusted_parent `oaa.proto.messages.AVChannelMediaConfig:4` → `oaa.proto.data.PingConfiguration` (`xig` → `abmh`) |
| `oaa.proto.data.RPM` | `xlm` | 4 | trusted_parent `oaa.proto.messages.SensorEventIndication:4` → `oaa.proto.data.RPM` (`xln` → `xlm`) |
| `oaa.proto.data.RadioBands` | `xkj` | 24 | trusted_parent `oaa.proto.data.RadioChannelConfig:2` → `oaa.proto.data.RadioBands` (`xkx` → `xkj`); compatible_child `oaa.proto.data.RadioBands:1` → `oaa.proto.data.RadioBandGroup` (`xkj` → `xki`) |
| `oaa.proto.data.RadioChannelConfig` | `xkx` | 10 | trusted_parent `oaa.proto.data.ChannelDescriptor:7` → `oaa.proto.data.RadioChannelConfig` (`xlv` → `xkx`); compatible_child `oaa.proto.data.RadioChannelConfig:2` → `oaa.proto.data.RadioBands` (`xkx` → `xkj`) |
| `oaa.proto.data.RawEvTripSettings` | `xle` | 6 | trusted_parent `oaa.proto.messages.SensorEventIndication:26` → `oaa.proto.data.RawEvTripSettings` (`xln` → `xle`) |
| `oaa.proto.data.RawVehicleEnergyModel` | `xlg` | 6 | trusted_parent `oaa.proto.messages.SensorEventIndication:25` → `oaa.proto.data.RawVehicleEnergyModel` (`xln` → `xlg`) |
| `oaa.proto.data.RelativeInputEvent` | `xlk` | 2 | trusted_parent `oaa.proto.data.RelativeInputEvents:1` → `oaa.proto.data.RelativeInputEvent` (`xll` → `xlk`) |
| `oaa.proto.data.RelativeInputEvents` | `xll` | 24 | trusted_parent `oaa.proto.messages.InputEventIndication:6` → `oaa.proto.data.RelativeInputEvents` (`xhp` → `xll`); compatible_child `oaa.proto.data.RelativeInputEvents:1` → `oaa.proto.data.RelativeInputEvent` (`xll` → `xlk`) |
| `oaa.proto.data.SensorChannel` | `xlt` | 1 | trusted_parent `oaa.proto.data.ChannelDescriptor:2` → `oaa.proto.data.SensorChannel` (`xlv` → `xlt`); compatible_child `oaa.proto.data.SensorChannel:1` → `oaa.proto.data.SensorTypeEntry` (`xlt` → `xls`) |
| `oaa.proto.data.SensorChannelConfig` | `xlt` | 1 | compatible_child `oaa.proto.data.SensorChannelConfig:1` → `oaa.proto.data.SensorTypeEntry` (`xlt` → `xls`) |
| `oaa.proto.data.SensorTypeEntry` | `xls` | 11 | trusted_parent `oaa.proto.data.SensorChannel:1` → `oaa.proto.data.SensorTypeEntry` (`xlt` → `xls`); trusted_parent `oaa.proto.data.SensorChannelConfig:1` → `oaa.proto.data.SensorTypeEntry` (`xlt` → `xls`); compatible_enum `oaa.proto.data.SensorTypeEntry:1` → `oaa.proto.enums.SensorType.Enum` (`xls` → `xlu`) |
| `oaa.proto.data.SessionInfo` | `xeo` | 1 | trusted_parent `oaa.proto.messages.ServiceDiscoveryRequest:6` → `oaa.proto.data.SessionInfo` (`xlw` → `xeo`) |
| `oaa.proto.data.SteeringWheel` | `xgw` | 2 | trusted_parent `oaa.proto.messages.SensorEventIndication:14` → `oaa.proto.data.SteeringWheel` (`xln` → `xgw`) |
| `oaa.proto.data.TirePressure` | `xmf` | 2 | trusted_parent `oaa.proto.messages.SensorEventIndication:18` → `oaa.proto.data.TirePressure` (`xln` → `xmf`) |
| `oaa.proto.data.TollCardData` | `xmg` | 2 | trusted_parent `oaa.proto.messages.SensorEventIndication:22` → `oaa.proto.data.TollCardData` (`xln` → `xmg`) |
| `oaa.proto.data.TouchLocation` | `xmh` | 2 | trusted_parent `oaa.proto.data.TouchEvent:1` → `oaa.proto.data.TouchLocation` (`xmi` → `xmh`) |
| `oaa.proto.data.TrailerData` | `xmj` | 270 | trusted_parent `oaa.proto.messages.SensorEventIndication:24` → `oaa.proto.data.TrailerData` (`xln` → `xmj`) |
| `oaa.proto.data.UIElementPosition` | `xlh` | 4 | trusted_parent `oaa.proto.data.NativeUIElement:1` → `oaa.proto.data.UIElementPosition` (`xir` → `xlh`); trusted_parent `oaa.proto.data.VideoMarginConfig:1` → `oaa.proto.data.UIElementPosition` (`xgv` → `xlh`) |
| `oaa.proto.data.VehicleEnergyModelData` | `xeq` | 88 | trusted_parent `oaa.proto.messages.SensorEventIndication:23` → `oaa.proto.data.VehicleEnergyModelData` (`xln` → `xeq`); compatible_child `oaa.proto.data.VehicleEnergyModelData:1` → `oaa.proto.data.VehicleEnergyInfo` (`xeq` → `xer`) |
| `oaa.proto.data.VehicleEnergyValue` | `xep` | 6 | trusted_parent `oaa.proto.data.VehicleEnergyInfo:3` → `oaa.proto.data.VehicleEnergyValue` (`xer` → `xep`); trusted_parent `oaa.proto.data.VehicleEnergyInfo:4` → `oaa.proto.data.VehicleEnergyValue` (`xer` → `xep`) |
| `oaa.proto.data.VersionFeatureFlags` | `xnq` | 5 | trusted_parent `oaa.proto.messages.WifiVersionRequest:6` → `oaa.proto.data.VersionFeatureFlags` (`xnv` → `xnq`) |
| `oaa.proto.data.VideoInsets` | `xht` | 4 | trusted_parent `oaa.proto.data.AdditionalVideoConfig:1` → `oaa.proto.data.VideoInsets` (`xml` → `xht`); trusted_parent `oaa.proto.data.AdditionalVideoConfig:2` → `oaa.proto.data.VideoInsets` (`xml` → `xht`); trusted_parent `oaa.proto.data.AdditionalVideoConfig:3` → `oaa.proto.data.VideoInsets` (`xml` → `xht`) |
| `oaa.proto.data.VideoMarginConfig` | `xgv` | 30 | trusted_parent `oaa.proto.data.AdditionalVideoConfig:7` → `oaa.proto.data.VideoMarginConfig` (`xml` → `xgv`); compatible_child `oaa.proto.data.VideoMarginConfig:1` → `oaa.proto.data.UIElementPosition` (`xgv` → `xlh`) |
| `oaa.proto.data.VideoResizeAction` | `xew` | 15 | trusted_parent `oaa.proto.data.AdditionalVideoConfig:6` → `oaa.proto.data.VideoResizeAction` (`xml` → `xew`); compatible_enum `oaa.proto.data.VideoResizeAction:1` → `oaa.proto.data.ResizeActionType` (`xew` → `xey`) |
| `oaa.proto.data.WifiChannel` | `xnh` | 6 | trusted_parent `oaa.proto.data.ChannelDescriptor:14` → `oaa.proto.data.WifiChannel` (`xlv` → `xnh`) |
| `oaa.proto.messages.CarAction` | `xdw` | 9 | trusted_parent `oaa.proto.messages.CarActionControl:1` → `oaa.proto.messages.CarAction` (`xfv` → `xdw`); trusted_parent `oaa.proto.messages.CarActionEntry:1` → `oaa.proto.messages.CarAction` (`xdx` → `xdw`); trusted_parent `oaa.proto.messages.CarPropertyControl:2` → `oaa.proto.messages.CarAction` (`xeh` → `xdw`) |
| `oaa.proto.messages.CarActionControl` | `xfv` | 30 | trusted_parent `oaa.proto.messages.CarControl:2` → `oaa.proto.messages.CarActionControl` (`xfy` → `xfv`); compatible_child `oaa.proto.messages.CarActionControl:1` → `oaa.proto.messages.CarAction` (`xfv` → `xdw`) |
| `oaa.proto.messages.CarActionEntry` | `xdx` | 88 | trusted_parent `oaa.proto.data.CarControlChannel:3` → `oaa.proto.messages.CarActionEntry` (`xgb` → `xdx`); trusted_parent `oaa.proto.messages.CarControlChannelDescriptor:3` → `oaa.proto.messages.CarActionEntry` (`xgb` → `xdx`); compatible_child `oaa.proto.messages.CarActionEntry:1` → `oaa.proto.messages.CarAction` (`xdx` → `xdw`) |
| `oaa.proto.messages.CarControlChannelDescriptor` | `xgb` | 1 | compatible_child `oaa.proto.messages.CarControlChannelDescriptor:1` → `oaa.proto.messages.CarPropertyConfig` (`xgb` → `xeg`); compatible_child `oaa.proto.messages.CarControlChannelDescriptor:2` → `oaa.proto.messages.CarControl` (`xgb` → `xfy`); compatible_child `oaa.proto.messages.CarControlChannelDescriptor:3` → `oaa.proto.messages.CarActionEntry` (`xgb` → `xdx`) |
| `oaa.proto.messages.CarProperty` | `xee` | 3 | trusted_parent `oaa.proto.messages.CarPropertyChangeEvent:1` → `oaa.proto.messages.CarProperty` (`xgj` → `xee`); trusted_parent `oaa.proto.messages.CarPropertyControl:1` → `oaa.proto.messages.CarProperty` (`xeh` → `xee`); trusted_parent `oaa.proto.messages.CarPropertyControl:3` → `oaa.proto.messages.CarProperty` (`xeh` → `xee`) |
| `oaa.proto.messages.CarPropertyAreaConfig` | `xdv` | 5 | trusted_parent `oaa.proto.messages.CarPropertyConfig:7` → `oaa.proto.messages.CarPropertyAreaConfig` (`xeg` → `xdv`); compatible_child `oaa.proto.messages.CarPropertyAreaConfig:1` → `oaa.proto.messages.CarAreaId` (`xdv` → `xef`); compatible_child `oaa.proto.messages.CarPropertyAreaConfig:2` → `oaa.proto.messages.CarPropertyValue` (`xdv` → `xem`) |
| `oaa.proto.messages.CarPropertyControl` | `xeh` | 5 | trusted_parent `oaa.proto.messages.CarControl:1` → `oaa.proto.messages.CarPropertyControl` (`xfy` → `xeh`); compatible_child `oaa.proto.messages.CarPropertyControl:1` → `oaa.proto.messages.CarProperty` (`xeh` → `xee`); compatible_child `oaa.proto.messages.CarPropertyControl:2` → `oaa.proto.messages.CarAction` (`xeh` → `xdw`) |
| `oaa.proto.messages.ChargingStationDetails` | `xgo` | 11 | trusted_parent `oaa.proto.messages.NavigationDestination:2` → `oaa.proto.messages.ChargingStationDetails` (`xix` → `xgo`) |
| `oaa.proto.messages.IntValues` | `xek` | 4 | trusted_parent `oaa.proto.messages.CarPropertyValue:6` → `oaa.proto.messages.IntValues` (`xem` → `xek`) |
| `oaa.proto.messages.NavigationDestination` | `xix` | 2 | trusted_parent `oaa.proto.messages.NavigationNotification:2` → `oaa.proto.messages.NavigationDestination` (`xjg` → `xix`); compatible_child `oaa.proto.messages.NavigationDestination:2` → `oaa.proto.messages.ChargingStationDetails` (`xix` → `xgo`) |
| `oaa.proto.messages.NavigationLane` | `xjb` | 24 | trusted_parent `oaa.proto.messages.NavigationStep:3` → `oaa.proto.messages.NavigationLane` (`xjn` → `xjb`); compatible_child `oaa.proto.messages.NavigationLane:1` → `oaa.proto.messages.NavigationLaneDirection` (`xjb` → `xja`) |
| `oaa.proto.messages.NavigationLaneDirection` | `xja` | 2 | trusted_parent `oaa.proto.messages.NavigationLane:1` → `oaa.proto.messages.NavigationLaneDirection` (`xjb` → `xja`) |
| `oaa.proto.messages.NavigationManeuver` | `xjc` | 1 | trusted_parent `oaa.proto.messages.NavigationStep:1` → `oaa.proto.messages.NavigationManeuver` (`xjn` → `xjc`) |
| `oaa.proto.messages.NavigationNotification` | `xjg` | 3 | compatible_child `oaa.proto.messages.NavigationNotification:1` → `oaa.proto.messages.NavigationStep` (`xjg` → `xjn`); compatible_child `oaa.proto.messages.NavigationNotification:2` → `oaa.proto.messages.NavigationDestination` (`xjg` → `xix`) |
| `oaa.proto.messages.NavigationRemainingDistance` | `xjo` | 2 | compatible_child `oaa.proto.messages.NavigationRemainingDistance:1` → `oaa.proto.messages.NavigationTurnDistance` (`xjo` → `xiz`) |
| `oaa.proto.messages.NavigationRoadInfo` | `xiv` | 5 | trusted_parent `oaa.proto.messages.NavigationStep:4` → `oaa.proto.messages.NavigationRoadInfo` (`xjn` → `xiv`) |
| `oaa.proto.messages.NavigationStepDistance` | `xjo` | 2 | trusted_parent `oaa.proto.messages.NavigationNextTurnDistanceEvent:1` → `oaa.proto.messages.NavigationStepDistance` (`xiw` → `xjo`); compatible_child `oaa.proto.messages.NavigationStepDistance:1` → `oaa.proto.messages.NavigationTurnDistance` (`xjo` → `xiz`) |
| `oaa.proto.messages.NavigationText` | `xjf` | 6 | trusted_parent `oaa.proto.messages.NavigationNextTurnDistanceEvent:3` → `oaa.proto.messages.NavigationText` (`xiw` → `xjf`); trusted_parent `oaa.proto.messages.NavigationStep:2` → `oaa.proto.messages.NavigationText` (`xjn` → `xjf`) |
| `oaa.proto.messages.PhoneInputType` | `xhu` | 11 | trusted_parent `oaa.proto.messages.PhoneStatusInput:1` → `oaa.proto.messages.PhoneInputType` (`xka` → `xhu`) |
| `oaa.proto.messages.RadioImage` | `xkm` | 6 | trusted_parent `oaa.proto.messages.RadioMetadata:5` → `oaa.proto.messages.RadioImage` (`xkn` → `xkm`); trusted_parent `oaa.proto.messages.RadioSongMetadata:5` → `oaa.proto.messages.RadioImage` (`xla` → `xkm`) |
| `oaa.proto.messages.RadioProgramInfo` | `xks` | 8 | trusted_parent `oaa.proto.messages.RadioFavoriteListNotification:1` → `oaa.proto.messages.RadioProgramInfo` (`xkl` → `xks`); trusted_parent `oaa.proto.messages.RadioProgramInfoNotification:1` → `oaa.proto.messages.RadioProgramInfo` (`xkt` → `xks`); trusted_parent `oaa.proto.messages.RadioProgramListNotification:1` → `oaa.proto.messages.RadioProgramInfo` (`xku` → `xks`) |
| `oaa.proto.messages.RadioProgramSelector` | `xkv` | 3 | trusted_parent `oaa.proto.messages.RadioProgramInfo:1` → `oaa.proto.messages.RadioProgramSelector` (`xks` → `xkv`); compatible_child `oaa.proto.messages.RadioProgramSelector:1` → `oaa.proto.messages.RadioProgramIdentifier` (`xkv` → `xkr`); compatible_child `oaa.proto.messages.RadioProgramSelector:2` → `oaa.proto.messages.RadioProgramIdentifier` (`xkv` → `xkr`) |
| `oaa.proto.messages.SetCarPropertyListenerResult` | `xgk` | 2 | trusted_parent `oaa.proto.messages.RegisterCarPropertyListenersResponse:1` → `oaa.proto.messages.SetCarPropertyListenerResult` (`xlj` → `xgk`); compatible_child `oaa.proto.messages.SetCarPropertyListenerResult:1` → `oaa.proto.messages.CarProperty` (`xgk` → `xee`); compatible_enum `oaa.proto.messages.SetCarPropertyListenerResult:2` → `oaa.proto.enums.Status.Enum` (`xgk` → `xin`) |
| `oaa.proto.messages.UiConfigData` | `xmn` | 3 | compatible_child `oaa.proto.messages.UiConfigData:1` → `oaa.proto.messages.UiConfigEntry` (`xmn` → `xmp`); compatible_child `oaa.proto.messages.UiConfigData:2` → `oaa.proto.messages.UiConfigEntry` (`xmn` → `xmp`) |
| `oaa.proto.messages.WifiProjectionEndpoint` | `xnq` | 5 | trusted_parent `oaa.proto.messages.WifiSetupInfo:4` → `oaa.proto.messages.WifiProjectionEndpoint` (`xns` → `xnq`) |

## Unique structural mappings

These mappings have one exact APK schema candidate but no dispatch anchor yet.

| Canonical message | APK class | Fields |
|---|---|---:|
| `oaa.proto.data.AVChannel` | `xik` | 8 |
| `oaa.proto.data.AVInputChannel` | `xil` | 2 |
| `oaa.proto.data.AdditionalVideoConfig` | `xml` | 8 |
| `oaa.proto.data.AssistantFeatureFlags` | `opi` | 14 |
| `oaa.proto.data.BluetoothChannel` | `xfp` | 2 |
| `oaa.proto.data.ButtonEvent` | `xia` | 4 |
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
| `oaa.proto.data.VehicleEnergyInfo` | `xer` | 5 |
| `oaa.proto.data.VendorExtensionChannel` | `xmv` | 3 |
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
| `oaa.proto.messages.RadioSongMetadata` | `xla` | 6 |
| `oaa.proto.messages.SensorError` | `xlo` | 2 |
| `oaa.proto.messages.StatsEntry` | `xfa` | 4 |
| `oaa.proto.messages.UiConfigEntry` | `xmp` | 2 |
| `oaa.proto.messages.UiConfigValue` | `xmo` | 1 |
| `oaa.proto.messages.UserSwitchRequest` | `syl` | 1 |
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

## Resolved-parent child schema differences

A dispatch/lineage-backed parent, or one linked from a trusted parent,
identifies the APK child at this field, but the child schema differs
from the current canonical definition. These are
version-delta or stale-schema candidates, not accepted mappings.

| Canonical parent | APK parent | Field | Canonical child | APK child | Local schema difference |
|---|---|---:|---|---|---|
| `oaa.proto.data.AVChannel` | `xik` | 4 | `oaa.proto.data.VideoConfig` | `xmz` | missing f7 uint32 |

## Dispatch/schema conflicts

Explicit service or message-name evidence identifies an APK class, but its
17.3 local schema differs from the current canonical definition.

| Canonical message | APK class | Context | Local schema difference | Evidence |
|---|---|---|---|---|

None.

## Hard-anchor edge conflicts

Identity is supported by exact local shape and an unambiguous dispatch or
confirmed lineage anchor,
but at least one recovered child edge disagrees with the canonical graph.

| Canonical message | APK class |
|---|---|

## Constraint conflicts

These schemas matched locally, but all candidates contradicted at least one
known message-reference edge. They are retained as follow-up evidence rather
than silently accepted or discarded.

| Canonical message | Initial APK candidates |
|---|---|

### Direct child-schema differences

These are first-order edge disagreements where the APK child class does
not have the local shape of any candidate for the canonical child type.

| Canonical parent | APK parent | Field | Canonical child | APK child |
|---|---|---:|---|---|

## Limitations

- Unique structure is evidence of identity, not proof of original Google naming.
- Class continuity across releases is not semantic proof; bundled Google libraries can preserve unrelated schemas for years.
- Empty and small messages remain highly ambiguous until graph or dispatch constraints apply.
- Field references are recovered where the `RawMessageInfo` object-array cursor and JADX field declarations are complete.
- Canonical corrections describe 17.3; consumers supporting older releases should preserve version-compatibility policy at their API boundary.
- Runtime behavior, timing, and state-machine semantics remain outside schema matching.
