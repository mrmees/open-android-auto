# Video - Cross-Version Mapping

**Mappings:** 14 | **Versions:** 15.9, 16.1, 16.2, 16.4

| Proto Name | 15.9 | 16.1 | 16.2 | 16.4 | Fields (15.9/16.1/16.2/16.4) |
|---|---|---|---|---|---|
| AdditionalVideoConfig | `vuu` | `wcm` | `wcb` | `wuo` | 7/7/7/7 |
| UiConfigData | `vuw` | `wco` | `wce` | -- | 2/2/2/0 |
| UiConfigEntry | `vuy` | `wcq` | `wcg` | -- | 2/2/2/0 |
| UiConfigRequest | `vvb` | `wct` | `wcj` | -- | 1/1/1/0 |
| VideoConfig | `vvh` | `wcz` | `wcp` | `wvb` | 11/11/11/11 |
| VideoFocusIndication | `vvj` | `wdb` | `wcr` | -- | 2/2/2/0 |
| VideoFocusMode | `vvc` | `wcu` | `wck` | -- | 1/1/1/0 |
| VideoFocusNotification | `vqm` | `vye` | `vxq` | -- | 1/1/1/0 |
| VideoFocusRequest | `vvl` | `wdd` | `wct` | `wvf` | 2/2/2/2 |
| UIElementPosition | `vtq` | `wbi` | `way` | -- | 4/4/4/0 |
| VideoMarginConfig | `vpl` | `vxd` | `vwp` | -- | 1/1/1/0 |
| VideoMargins | `wzu` | `xhv` | `xhg` | -- | 3/3/3/0 |
| VideoResizeAction | `vnt` | `vvl` | `vux` | -- | 1/1/1/0 |
| VideoInsets | `vqj` | `vyb` | `vxn` | -- | 4/4/4/0 |

## Android Auto 17.3 endpoint corrections

The 17.3 phone endpoint resolves historical direction and shifted-name
conflicts without changing previously proven field tags or types:

| Wire ID | 17.3 name | 17.3 direction / schema boundary |
|---|---|---|
| 0x8007 | VideoFocusRequest | Phone -> HU |
| 0x8008 | VideoFocusIndication | HU -> Phone |
| 0x8009 | UpdateUiConfigRequest | HU -> Phone; AdditionalVideoConfig field 1 |
| 0x800A | UpdateUiConfigRequest | Phone -> HU; AdditionalVideoConfig field 1 |
| 0x800B | AudioUnderflow | HU -> Phone; no payload parsed |
| 0x800C | ActionTaken | Phone -> HU; enum field 1, with the public action enum unpublished |
| 0x800D | OverlayParameters | Phone -> HU; repeated overlay-options field 1, with nested overlay-option semantics unpublished |
| 0x800E | OverlayStart | HU -> Phone; int32 display-session ID field 1 |
| 0x800F | OverlayStop | HU -> Phone; empty payload |
| 0x8010 | reserved | Direction and payload unknown; publication deferred |
| 0x8011 | UiConfigRequest | Phone -> HU |
| 0x8012 | UpdateHuUiConfigResponse | HU -> Phone |
| 0x8013 | MediaStats | HU -> Phone |
| 0x8014 | MediaOptions | Phone -> HU |
| 0x8015 | CriticalUiNotification | Phone -> HU; critical-UI-focus enum field 1 |

The 0x8010 reservation is not permission to shift a later name into that slot.
