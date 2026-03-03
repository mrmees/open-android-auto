# Wifi - Cross-Version Mapping

**Mappings:** 14 | **Versions:** 15.9, 16.1, 16.2

| Proto Name | 15.9 | 16.1 | 16.2 | Fields (15.9/16.1/16.2) |
|---|---|---|---|---|
| WiFiProjectionChannel | -- | `wdh` | -- | 0/1/0 |
| WifiChannel | -- | `wdh` | -- | 0/1/0 |
| WifiConnectStatus | `vvr` | `wdj` | `wcz` | 2/2/2 |
| WifiConnectionRejection | `vvs` | `wdk` | `wda` | 1/1/1 |
| WifiDirectConfig | `vtj` | `wbb` | `was` | 6/6/6 |
| WifiInfoRequest | -- | `wdl` | `wdb` | 0/0/0 |
| WifiInfoResponse | `vvu` | `wdm` | `wdc` | 5/5/5 |
| WifiNetworkInfo | `vvq` | `wdi` | `wcy` | 5/5/5 |
| WifiSecurityResponse | -- | `wan` | `waf` | 0/13/13 |
| WifiSetupInfo | `vwa` | `wds` | `wdi` | 5/5/5 |
| WifiSetupMessage | `vvv` | `wdn` | `wdd` | 0/0/0 |
| WifiStartResponse | `vwc` | `wdu` | `wdk` | 3/3/3 |
| WifiVersionRequest | `vwd` | `wdv` | `wdl` | 6/6/6 |
| WifiVersionResponse | `vwe` | `wdw` | `wdm` | 7/7/7 |
