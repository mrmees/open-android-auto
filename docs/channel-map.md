# Android Auto Channel Map

Android Auto multiplexes all communication over a single TCP connection using channel IDs. Each channel handles a specific domain of the protocol.

## Channel ID Table

| ID | Channel | Category | Description |
|---:|---------|----------|-------------|
| 0 | Control | `control` | Session lifecycle, service discovery, auth, ping, shutdown |
| 1 | Input | `input` | Touch events, button presses, haptic feedback |
| 2 | Sensor | `sensor` | GPS, vehicle sensors, driving status |
| 3 | Video | `video` | H.264/H.265/VP9/AV1 encoded video stream |
| 4 | Media Audio | `audio` | Music/podcast PCM audio stream |
| 5 | Speech Audio | `audio` | Navigation prompts, assistant voice |
| 6 | Phone Audio | `audio` | Voice call audio (bidirectional) |
| 7 | Bluetooth | `bluetooth` | BT pairing coordination |
| 8 | WiFi Projection | `wifi` | WiFi connection setup and management |
| 9 | Notification | `notification` | Phone notification mirroring |
| 10 | Media Status | `media` | Now-playing metadata and playback state |
| 11 | Navigation Status | `navigation` | Turn-by-turn guidance, maneuvers, ETA |
| 12 | Phone Status | `phone` | Call state, phone capabilities |

## Channel Details

### Channel 0: Control

Session-level messages. All use `MessageType::Control`.

| Message | Direction | Purpose |
|---------|-----------|---------|
| `ServiceDiscoveryRequest` | HU -> Phone | Advertise HU capabilities, request phone services |
| `ServiceDiscoveryResponse` | Phone -> HU | Phone's available channels and configs |
| `ChannelOpenRequest` | HU -> Phone | Open a specific channel |
| `ChannelOpenResponse` | Phone -> HU | Accept/reject channel open |
| `PingRequest` | HU -> Phone | Keepalive |
| `PingResponse` | Phone -> HU | Keepalive reply |
| `BindingRequest` | HU -> Phone | Auth key exchange |
| `BindingResponse` | Phone -> HU | Auth key response |
| `AuthCompleteIndication` | Phone -> HU | Auth success |
| `ShutdownRequest` | Either | Initiate disconnect |
| `ShutdownResponse` | Either | Acknowledge disconnect |

### Channel 1: Input

All use `MessageType::Specific`.

| Message | Direction | Purpose |
|---------|-----------|---------|
| `InputEventIndication` | HU -> Phone | Touch, button, or relative input events |

Touch events contain arrays of `TouchEvent` with pointer tracking. Button events use Android `KeyEvent` codes.

### Channel 2: Sensor

| Message | Direction | Purpose |
|---------|-----------|---------|
| `SensorStartRequest` | Phone -> HU | Request specific sensor data |
| `SensorStartResponse` | HU -> Phone | Acknowledge sensor subscription |
| `SensorEventIndication` | HU -> Phone | Sensor data payload (GPS, speed, RPM, etc.) |

The phone requests which sensors it wants. The HU sends periodic updates for subscribed sensors.

### Channel 3: Video

| Message | Direction | Purpose |
|---------|-----------|---------|
| `AVChannelSetupRequest` | Phone -> HU | Select video codec and resolution |
| `AVChannelSetupResponse` | HU -> Phone | Accept/reject setup |
| `AVChannelStartIndication` | Phone -> HU | Begin video stream |
| `AVChannelStopIndication` | Phone -> HU | Pause/stop video stream |
| `AVMediaAckIndication` | HU -> Phone | Flow control acknowledgment |
| `VideoFocusRequest` | Phone -> HU | Request video focus change |
| `VideoFocusIndication` | HU -> Phone | Grant/revoke video focus |
| (raw video frames) | Phone -> HU | Encoded H.264/H.265/VP9/AV1 data |

### Channels 4, 5, 6: Audio

Three audio channels share the same message types from the `av` and `audio` categories.

| Message | Direction | Purpose |
|---------|-----------|---------|
| `AVChannelSetupRequest` | Phone -> HU | Select audio codec and config |
| `AVChannelSetupResponse` | HU -> Phone | Accept/reject setup |
| `AVChannelStartIndication` | Phone -> HU | Begin audio stream |
| `AVChannelStopIndication` | Phone -> HU | Stop audio stream |
| `AudioFocusRequest` | Phone -> HU | Request audio focus (gain, transient, duck) |
| `AudioFocusResponse` | HU -> Phone | Grant/deny audio focus |
| (raw audio frames) | Phone -> HU | PCM audio data |

Channel 6 (phone audio) is bidirectional -- the HU also sends microphone audio to the phone.

### Channel 7: Bluetooth

| Message | Direction | Purpose |
|---------|-----------|---------|
| `BluetoothPairingRequest` | Phone -> HU | Request BT pairing |
| `BluetoothPairingResponse` | HU -> Phone | Pairing result |

### Channel 8: WiFi Projection

| Message | Direction | Purpose |
|---------|-----------|---------|
| `WifiVersionRequest` | Either | Protocol version negotiation |
| `WifiVersionResponse` | Either | Version response |
| `WifiSecurityRequest` | Phone -> HU | Request WiFi security params |
| `WifiSecurityResponse` | HU -> Phone | WiFi credentials (SSID, password, BSSID) |
| `WifiStartRequest` | Phone -> HU | Begin WiFi projection |
| `WifiStartResponse` | HU -> Phone | Accept/reject WiFi start |
| `WifiInfoRequest` | Either | WiFi status query |
| `WifiInfoResponse` | Either | WiFi status response |

### Channel 9: Notification

| Message | Direction | Purpose |
|---------|-----------|---------|
| (notification data) | Phone -> HU | Phone notification content |

Phone-to-HU only. The HU does not send notifications to the phone.

### Channel 10: Media Status

| Message | Direction | Purpose |
|---------|-----------|---------|
| `MediaPlaybackStatus` | Phone -> HU | Play/pause/stop state, position, duration |
| `MediaPlaybackMetadata` | Phone -> HU | Track title, artist, album, art |

### Channel 11: Navigation Status

| Message | Direction | Purpose |
|---------|-----------|---------|
| `NavigationTurnEvent` | Phone -> HU | Next turn info, maneuver type, road name |
| `NavigationDistance` | Phone -> HU | Distance to next maneuver |
| `NavigationState` | Phone -> HU | Active/inactive navigation state |
| `NavigationNotification` | Phone -> HU | ETA, traffic info |
| `NavigationFocusRequest` | Phone -> HU | Request nav display focus |
| `NavigationFocusResponse` | HU -> Phone | Grant/deny nav focus |

### Channel 12: Phone Status

| Message | Direction | Purpose |
|---------|-----------|---------|
| `PhoneStatus` | Phone -> HU | Call state (idle, ringing, active), signal strength |
| `CallAvailability` | Phone -> HU | Whether phone calls are available |
| `VoiceSessionRequest` | HU -> Phone | Initiate voice assistant |
