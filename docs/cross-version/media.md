# Media - Cross-Version Mapping

**Mappings:** 10 | **Versions:** 15.9, 16.1, 16.2

| Proto Name | 15.9 | 16.1 | 16.2 | Fields (15.9/16.1/16.2) |
|---|---|---|---|---|
| CarLocalMediaPlayback | `vox` | `vwp` | `vwb` | 0/0/0 |
| CarLocalMediaPlaybackMetadata | `voy` | `vwq` | `vwc` | 5/5/5 |
| CarLocalMediaPlaybackRequest | `voz` | `vwr` | `vwd` | 1/1/1 |
| CarLocalMediaPlaybackStatus | `vpa` | `vws` | `vwe` | 4/4/4 |
| ~~MediaEventIdWrapper~~ | ~~`xet`~~ | ~~`xmu`~~ | ~~`xme`~~ | ~~1/1/1~~ | **RETRACTED** — internal MediaBrowserService, not wire protocol |
| MediaPlaybackCommand | `vnu` | `vvm` | `vuy` | 1/1/1 |
| MediaPlaybackMetadata | `nej` | `nmi` | `nlt` | 6/6/6 |
| MediaPlaybackStatus | `vqy` | `vyq` | `vyc` | 6/6/6 |
| MediaStatusList | `vrr` | `vyd` | -- | 1/1/0 |
| ~~MediaTrackIdentifier~~ | ~~`xdz`~~ | ~~`xma`~~ | ~~`xll`~~ | ~~3/3/3~~ | **RETRACTED** — internal MediaBrowserService queue structure, not wire protocol |
