# Sensor - Cross-Version Mapping

**Mappings:** 38 | **Versions:** 15.9, 16.1, 16.2, 16.4

| Proto Name | 15.9 | 16.1 | 16.2 | 16.4 | Fields (15.9/16.1/16.2/16.4) |
|---|---|---|---|---|---|
| Accel | `vnr` | `vvj` | `vuv` | -- | 3/3/3/0 |
| Compass | `vpi` | `vxa` | `vwm` | -- | 3/3/3/0 |
| Door | `vpp` | `vxh` | `vwt` | -- | 3/3/3/0 |
| DrivingStatus | `vpr` | `vxj` | `vwv` | -- | 1/1/1/0 |
| EVConnectorType | `vpt` | `vxl` | `vwx` | `wpj` | 0/0/0/0 |
| Environment | `vps` | `vxk` | `vww` | -- | 3/3/3/0 |
| FuelLevel | `vpv` | `vxn` | `vwz` | `wpl` | 3/3/3/3 |
| FuelType | `vpw` | `vxo` | `vxa` | `wpm` | 0/0/0/0 |
| GPSLocation | `vqt` | `vyl` | `vxx` | `wqj` | 6/6/6/6 |
| Gear | `vpx` | `vxp` | `vxb` | -- | 1/1/1/0 |
| GpsSatelliteData | `vqa` | `vxs` | `vxe` | -- | 3/3/3/0 |
| Gyro | `vqb` | `vxt` | `vxf` | -- | 3/3/3/0 |
| HVAC | `vqd` | `vxv` | `vxh` | -- | 2/2/2/0 |
| Light | `vqs` | `vyk` | `vxw` | `wqi` | 3/3/3/3 |
| NightMode | `vse` | `vzw` | `vzi` | -- | 1/1/1/0 |
| Odometer | `vsf` | `vzx` | `vzj` | -- | 2/2/2/0 |
| ParkingBrake | `vsj` | `wab` | `vzn` | -- | 1/1/1/0 |
| Passenger | `vsk` | `wac` | `vzo` | -- | 1/1/1/0 |
| RPM | `vtv` | `wbn` | `wbd` | -- | 1/1/1/0 |
| RawEvTripSettings | `vtn` | `wbf` | `wav` | -- | 1/1/1/0 |
| RawVehicleEnergyModel | `vtp` | `wbh` | `wax` | -- | 1/1/1/0 |
| Sensor | `vub` | `wbt` | `wbj` | -- | 1/1/1/0 |
| SensorChannel | `vuc` | `wbu` | `wbk` | `wtx` | 4/4/4/4 |
| SensorChannelConfig | `vuc` | `wbu` | `wbk` | `wtx` | 4/4/4/4 |
| SensorError | `vtx` | `wbp` | `wbf` | -- | 2/2/2/0 |
| SensorErrorStatus | `vty` | `wbq` | `wbg` | -- | 0/0/0/0 |
| SensorEventFloat | `vsi` | `waa` | `vzm` | -- | 1/1/1/0 |
| SensorEventIndication | `vtw` | `wbo` | `wbe` | `wtr` | 26/26/26/26 |
| SensorRequest | `vtz` | `wbr` | `wbh` | `wtu` | 2/2/2/2 |
| SensorStartRequestMessage | `vsz` | `war` | `waj` | `wsw` | 2/2/2/2 |
| SensorStartResponseMessage | `vua` | `wbs` | `wbi` | -- | 1/1/1/0 |
| SensorTypeEntry | `vub` | `wbt` | `wbj` | -- | 1/1/1/0 |
| Speed | `vul` | `wcd` | `wbt` | `wug` | 3/3/3/3 |
| SteeringWheel | `vpm` | `vxe` | `vwq` | -- | 2/2/2/0 |
| TirePressure | `vuo` | `wcg` | `wbw` | -- | 1/1/1/0 |
| TollCardData | `vup` | `wch` | `wbx` | -- | 1/1/1/0 |
| TrailerData | -- | `wcl` | `wca` | -- | 0/0/0/0 |
| VehicleEnergyModelData | `zuz` | `vvg` | `vus` | -- | 0/0/0/0 |
