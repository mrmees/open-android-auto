# Video - Cross-Version Mapping

**Mappings:** 14 | **Versions:** 15.9, 16.1, 16.2

| Proto Name | 15.9 | 16.1 | 16.2 | Fields (15.9/16.1/16.2) |
|---|---|---|---|---|
| AdditionalVideoConfig | `vuu` | `wcm` | `wcb` | 7/7/7 |
| UiConfigData | `vuw` | `wco` | `wce` | 2/2/2 |
| UiConfigEntry | `vuy` | `wcq` | `wcg` | 2/2/2 |
| UiConfigRequest | `vvb` | `wct` | `wcj` | 1/1/1 |
| VideoConfig | `vvh` | `wcz` | `wcp` | 11/11/11 |
| VideoFocusIndication | `vvj` | `wdb` | `wcr` | 2/2/2 |
| ~~VideoFocusMode~~ → UpdateHuUiConfigResponse | `vvc` | `wcu` | `wck` | 1/1/1 | **RETRACTED** as VideoFocusModeMessage — actually UpdateHuUiConfigResponse |
| ~~VideoFocusNotification~~ | ~~`vqm`~~ | ~~`vye`~~ | `vxq` | 1/1/1 | **RETRACTED** — actually IntegratedOverlayStartNotification |
| VideoFocusRequest | `vvl` | `wdd` | `wct` | 2/2/2 |
| VideoInsets | `vtq` | `wbi` | `way` | 4/4/4 |
| VideoMarginConfig | `vpl` | `vxd` | `vwp` | 1/1/1 |
| VideoMargins | `wzu` | `xhv` | `xhg` | 3/3/3 |
| VideoResizeAction | `vnt` | `vvl` | `vux` | 1/1/1 |
| VideoResolutionRange | `vqj` | `vyb` | `vxn` | 4/4/4 |
