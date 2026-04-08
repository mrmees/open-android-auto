# VW Capture: Service Discovery Values

**Capture:** `captures/oem-vw-mib3oi-2026-04-06/`
**Source bins:** `sdp_request.bin`, `sdp_response.bin`
**Verified directions** (determined by decode, NOT the README):

- `sdp_request.bin` → phone → HU (decodes as ServiceDiscoveryRequest)
- `sdp_response.bin` → HU → phone (decodes as ServiceDiscoveryResponse)

## SDP Request (phone → HU)

- device_name: `Android`
- device_brand: `Google Pixel 8`
- session_uuid: `ba64e7d4-6347-47cd-9234-fb3cc41c5249`
- phone_icon_small: present=True, size_bytes=152
- phone_icon_medium: present=True, size_bytes=240
- phone_icon_large: present=True, size_bytes=411

## SDP Response (HU → phone)

- head_unit_name: `Volkswagen`
- car_model: `VW3363`
- car_year: `2024`
- car_serial: `092f7b7ed5024eb0`
- headunit_manufacturer: `LGE`
- headunit_model: `COCKPIT_MIB3OI_GP`
- sw_build: `C sample`
- sw_version: `2756.04`
- session_configuration: `1`
- display_name: `Volkswagen`
- probe_for_support: `False`
- driver_position: `0`

### HeadUnitInfo (sub-message)

- head_unit_make: `LGE`
- head_unit_model: `COCKPIT_MIB3OI_GP`
- head_unit_software_build: `C sample`
- head_unit_software_version: `2756.04`
- make: `Volkswagen`
- model: `VW3363`
- vehicle_id: `092f7b7ed5024eb0`
- year: `2024`

### Channel Descriptors (13 channels declared)

| channel_id | channel_kind | config summary |
|---:|---|---|
| 1 | `av_channel` | channel_id, display_type, video_configs |
| 2 | `input_channel` | display_id, supported_keycodes, touch_screen_configs |
| 3 | `av_channel` | audio_configs, audio_type, stream_type |
| 4 | `av_channel` | audio_configs, audio_type, stream_type |
| 5 | `av_channel` | audio_configs, audio_type, stream_type |
| 6 | `av_channel` | audio_configs, audio_type, stream_type |
| 7 | `av_input_channel` | audio_config, stream_type |
| 8 | `sensor_channel` | fuel_types, location_characterization, sensors |
| 9 | `bluetooth_channel` | adapter_address, supported_pairing_methods |
| 10 | `media_info_channel` | (empty marker) |
| 11 | `phone_status_channel` | (empty marker) |
| 12 | `navigation_channel` | minimum_interval_ms, type |
| 13 | `wifi_channel` | bssid |

## Services NOT declared by VW

- `car_control_channel`
- `generic_notification_channel`
- `media_browser_channel`
- `notification_channel`
- `radio_channel`
- `vendor_extension_channel`
- `voice_channel`

_These services are part of the full ChannelDescriptor schema but are absent from VW's SDP advertisement. They are comparative gaps — potentially observable on other OEMs but not on this VW MIB3 OI._
