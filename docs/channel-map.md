# Android Auto Channel Map

Android Auto multiplexes all communication over a single TCP connection using channel IDs. Each channel handles a specific domain of the protocol.

> **Note:** Channel IDs below are GAL service type numbers from the SDP `ChannelDescriptor`. The actual multiplexed channel number on the wire may differ — it's assigned dynamically per-session based on the SDP response order. The GAL type is the stable identifier.

## Channel ID Table

| GAL Type | Channel | Category | Description |
|---------:|---------|----------|-------------|
| 0 | Control | `control` | Session lifecycle, service discovery, auth, ping, shutdown, focus |
| 1 | Input | `input` | Touch events, button presses, rotary, touchpad, haptic feedback |
| 7 | Sensor | `sensor` | GPS, vehicle sensors, driving status |
| 3 | Video | `video` | H.264/H.265/VP9/AV1 encoded video stream |
| 4 | Media Audio | `audio` | Music/podcast PCM/AAC audio stream |
| 5 | Speech Audio | `audio` | Navigation prompts, assistant voice |
| 6 | Phone Audio | `audio` | Voice call audio (bidirectional) |
| 9 | Bluetooth | `bluetooth` | BT pairing coordination |
| 17 | WiFi Projection | `wifi` | WiFi credential delivery (GAL, 1 msg) |
| 10 | Navigation Status | `navigation` | Turn-by-turn guidance, maneuvers, ETA, instrument cluster |
| 11 | Media Info | `media` | Now-playing metadata and playback state |
| 13 | Phone Status | `phone` | Call state, phone input |
| 15 | Radio | `radio` | AM/FM/DAB radio program info, tuning, favorites |
| 19 | Car Control | `carcontrol` | HVAC, seat temp, door locks, mirror heat via VHAL |
| 20 | Car Local Media | `media` | Local media (car's own source) status/metadata |

## Channel Details

### Channel 0: Control (GAL type 0)

Session-level messages. All use `MessageType::Control`. Handles service discovery, auth, focus negotiation, and channel lifecycle.

| Message | Direction | Purpose |
|---------|-----------|---------|
| `ServiceDiscoveryRequest` | HU -> Phone | Advertise HU capabilities |
| `ServiceDiscoveryResponse` | Phone -> HU | Phone's available channels and configs |
| `ChannelOpenRequest` | HU -> Phone | Open a specific channel |
| `ChannelOpenResponse` | Phone -> HU | Accept/reject channel open |
| `PingRequest` | Bidirectional | Keepalive |
| `PingResponse` | Bidirectional | Keepalive reply |
| `BindingRequest` | Phone -> HU | Auth key exchange |
| `BindingResponse` | HU -> Phone | Auth key response |
| `AuthCompleteIndication` | Phone -> HU | Auth success |
| `NavigationFocusRequest` | Phone -> HU | Request nav display focus (msg 13) |
| `NavigationFocusResponse` | HU -> Phone | Grant/deny nav focus (msg 14) |
| `VoiceSessionRequest` | Phone -> HU | Initiate voice assistant (msg 17) |
| `CallAvailabilityStatus` | HU -> Phone | Whether phone calls are available (msg 24) |
| `ShutdownRequest` | Either | Initiate disconnect |
| `ShutdownResponse` | Either | Acknowledge disconnect |

### Channel 1: Input (GAL type 1)

All use `MessageType::Specific`.

| Message | Direction | Purpose |
|---------|-----------|---------|
| `InputEventIndication` | HU -> Phone | Touch, button, rotary, touchpad, absolute input |
| `InputBindingRequest` | Phone -> HU | Phone advertises supported keybindings |
| `InputBindingResponse` | HU -> Phone | HU acknowledges binding request |
| `InputBindingNotification` | Phone -> HU | Haptic feedback requests |

### Channel 7: Sensor (GAL type 7)

| Message | Direction | Purpose |
|---------|-----------|---------|
| `SensorRequest` | Phone -> HU | Subscribe to specific sensor types |
| `SensorStartResponse` | HU -> Phone | Acknowledge sensor subscription |
| `SensorEventIndication` | HU -> Phone | Sensor data payload (GPS, speed, RPM, etc.) |
| `SensorError` | HU -> Phone | Sensor error notification |

### Channel 3: Video (GAL type 3)

| Message | Direction | Purpose |
|---------|-----------|---------|
| `AVChannelSetupRequest` | Phone -> HU | Select video codec and resolution |
| `AVChannelSetupResponse` | HU -> Phone | Accept/reject setup |
| `AVChannelStartIndication` | Phone -> HU | Begin video stream |
| `AVChannelStopIndication` | Phone -> HU | Pause/stop video stream |
| `AVMediaAckIndication` | HU -> Phone | Flow control acknowledgment |
| `VideoFocusRequest` | HU -> Phone | Request video focus change |
| `VideoFocusIndication` | Phone -> HU | Grant/revoke video focus |
| `UpdateUiConfigRequest` | Bidirectional | Runtime UI config (theming, insets) |
| `UiConfigRequest` | HU -> Phone | Request UI configuration |
| (raw video frames) | Phone -> HU | Encoded H.264/H.265/VP9/AV1 data |

### Channels 4, 5, 6: Audio (GAL types 4, 5, 6)

Three audio channels share the same AV message types.

| Message | Direction | Purpose |
|---------|-----------|---------|
| `AVChannelSetupRequest` | Phone -> HU | Select audio codec and config |
| `AVChannelSetupResponse` | HU -> Phone | Accept/reject setup |
| `AVChannelStartIndication` | Bidirectional | Begin audio stream |
| `AVChannelStopIndication` | Phone -> HU | Stop audio stream |
| `AVMediaAckIndication` | HU -> Phone | Flow control acknowledgment |
| (raw audio frames) | Phone -> HU | PCM or AAC-LC audio data |

Audio focus is negotiated on the control channel, not on audio channels themselves. Channel 6 (phone audio) is bidirectional — the HU also sends microphone audio to the phone.

### Mic Input (GAL type 8)

| Message | Direction | Purpose |
|---------|-----------|---------|
| `MicrophoneOpenResponse` | HU -> Phone | Mic session config (status, sample rate) |
| (raw audio frames) | Bidirectional | PCM audio: 0x0000 HU→Phone, 0x0001 Phone→HU |

### Channel 9: Bluetooth (GAL type 9)

| Message | Direction | Purpose |
|---------|-----------|---------|
| `BluetoothPairingRequest` | HU -> Phone | Request BT pairing |
| `BluetoothPairingResponse` | HU -> Phone | Pairing result (status via ProtocolStatus) |
| `BluetoothAuthenticationData` | HU -> Phone | Auth data (string) |
| `BluetoothAuthenticationResult` | Phone -> HU | Auth result (status) |

### Channel 17: WiFi Projection (GAL type 17)

Only 1 GAL message. Most WiFi setup happens over BT RFCOMM, not on this channel.

| Message | Direction | Purpose |
|---------|-----------|---------|
| `WifiCredentialsResponse` | HU -> Phone | WiFi credentials (SSID, passphrase, security, BSSID) |

### Channel 10: Navigation Status (GAL type 10)

| Message | Direction | Purpose |
|---------|-----------|---------|
| `InstrumentClusterStart` | HU -> Phone | Signal cluster display is ready |
| `InstrumentClusterStop` | HU -> Phone | Signal cluster session ended |
| `NavigationState` | Phone -> HU | Navigation active/inactive/rerouting |
| `LegacyNavigationTurnEvent` | Phone -> HU | Simplified turn data (legacy HUs, PDK < 1.6) |
| `NavigationNotification` | Phone -> HU | Rich turn-by-turn with steps, lanes, destinations |
| `NavigationNextTurnDistanceEvent` | Phone -> HU | Distance to next maneuver |
| `VehicleEnergyForecast` | Phone -> HU | EV energy/range forecast (PDK >= 5.1) |

### Channel 11: Media Info (GAL type 11)

| Message | Direction | Purpose |
|---------|-----------|---------|
| `MediaPlaybackStatus` | Phone -> HU | Play/pause/stop state, position, duration |
| `MediaPlaybackStatusEvent` | HU -> Phone | Playback input action |
| `MediaPlaybackMetadata` | Phone -> HU | Track title, artist, album, art |

Media playback controls (play, pause, next, previous) are sent as button events on the **input channel**, not here.

### Channel 13: Phone Status (GAL type 13)

| Message | Direction | Purpose |
|---------|-----------|---------|
| `PhoneStatusUpdate` | Phone -> HU | Call state, phone call details |
| `PhoneStatusInput` | HU -> Phone | Input action for phone status display |

Note: `CallAvailabilityStatus` and `VoiceSessionRequest` are on the **control channel** (msgs 24 and 17), not here.

### Channel 15: Radio (GAL type 15)

| Message | Direction | Purpose |
|---------|-----------|---------|
| `RadioProgramListNotification` | HU -> Phone | Full program list |
| `RadioProgramInfoNotification` | HU -> Phone | Current station info |
| `RadioMuteRequest` | Phone -> HU | Mute/unmute radio |
| `RadioMuteResponse` | HU -> Phone | Mute status |
| `RadioTuneRequest` | Phone -> HU | Tune to station |
| `RadioTuneResponse` | HU -> Phone | Tune result |
| `RadioFavoriteListNotification` | HU -> Phone | Favorite stations |
| `RadioFavoriteToggleRequest` | Phone -> HU | Add/remove favorite |
| `RadioTuneDirectionRequest` | Phone -> HU | Seek up/down |
| `RadioSearchRequest` | Phone -> HU | Search radio (new in 16.2) |

### Channel 19: Car Control (GAL type 19)

| Message | Direction | Purpose |
|---------|-----------|---------|
| `SetCarPropertyValueRequest` | HU -> Phone | Set a VHAL property |
| `SetCarPropertyValueResponse` | Phone -> HU | Property set result |
| `RegisterCarPropertyListenersRequest` | HU -> Phone | Subscribe to property changes |
| `RegisterCarPropertyListenersResponse` | Phone -> HU | Per-property registration results |
| `CarPropertyChangeEvent` | Phone -> HU | Property value changed |
| `CarActionNotification` | HU -> Phone | App launch action (HVAC, media, etc.) |
| `CarControlGroupUpdate` | Phone -> HU | Updated control group layout |

### Channel 20: Car Local Media (GAL type 20)

| Message | Direction | Purpose |
|---------|-----------|---------|
| `CarLocalMediaPlaybackStatus` | HU -> Phone | Local media playback state |
| `CarLocalMediaPlaybackMetadata` | HU -> Phone | Local media track info |
| `CarLocalMediaPlaybackRequest` | Phone -> HU | Request playback action |

> **Capture evidence boundary:** The VW capture cannot validate claims about this surface.
> The on-phone hook lives inside the AA framing layer; `channel_id`, `flags`, and outer
> frame header semantics are below the hook's observation point. See
> [06-capture-non-claim-boundary.md](verification/06-capture-non-claim-boundary.md).
