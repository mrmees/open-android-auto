# Wifi - Cross-Version Mapping

**Mappings:** 14 | **Versions:** 15.9, 16.1, 16.2, 16.4

| Proto Name | 15.9 | 16.1 | 16.2 | 16.4 | Fields (15.9/16.1/16.2/16.4) |
|---|---|---|---|---|---|
| WiFiProjectionChannel | -- | `wdh` | -- | -- | 0/1/0/0 |
| WifiChannel | -- | `wdh` | -- | -- | 0/1/0/0 |
| WifiConnectStatus | `vvr` | `wdj` | `wcz` | -- | 2/2/2/0 |
| WifiConnectionRejection | `vvs` | `wdk` | `wda` | -- | 1/1/1/0 |
| WifiDirectConfig | `vtj` | `wbb` | `was` | `wtf` | 6/6/6/6 |
| WifiInfoRequest | -- | `wdl` | `wdb` | -- | 0/0/0/0 |
| WifiInfoResponse | `vvu` | `wdm` | `wdc` | `wvp` | 5/5/5/5 |
| WifiNetworkInfo | `vvq` | `wdi` | `wcy` | `wvl` | 5/5/5/5 |
| WifiSecurityResponse | -- | `wan` | `waf` | `wss` | 0/13/13/13 |
| WifiSetupInfo | `vwa` | `wds` | `wdi` | `wvv` | 5/5/5/5 |
| WifiSetupMessage | `vvv` | `wdn` | `wdd` | `wvq` | 0/0/0/0 |
| WifiStartResponse | `vwc` | `wdu` | `wdk` | -- | 3/3/3/0 |
| WifiVersionRequest | `vwd` | `wdv` | `wdl` | `wvy` | 6/6/6/6 |
| WifiVersionResponse | `vwe` | `wdw` | `wdm` | `wvz` | 7/7/7/7 |
