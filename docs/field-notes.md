# Field Notes

Hard-won protocol knowledge from implementing a working Android Auto head unit. These are things that aren't obvious from reading the protobuf definitions alone and will save you significant debugging time.

## Video

**Touch screen config dimensions must match video resolution, not display resolution.**
The `touch_screen_config` in `ServiceDiscoveryRequest` must be set to the video resolution (e.g., 1280x720 for 720p), NOT your physical display resolution (e.g., 1024x600). The phone interprets touch coordinates relative to `touch_screen_config`. If these don't match the video resolution, touch will be misaligned.

**Phone sends unexpected `config_index` in `AVChannelSetupRequest`.**
Your HU might advertise video configs at indices 0-1, but the phone may respond with `config_index=3`. This is the phone's internal reference ID, not an index into your config list. Don't reject it -- match on codec type and resolution instead.

**SPS/PPS arrives as `AV_MEDIA_INDICATION` with no timestamp.**
H.264/H.265 codec initialization data (SPS/PPS/VPS) is sent as a regular media indication but without a presentation timestamp. You must forward this to your decoder before any video frames will decode. Don't filter it out based on missing timestamps.

**H.264 data already has AnnexB start codes.**
Video data from the phone already includes AnnexB start codes (`00 00 00 01`). Do NOT prepend additional start codes or you'll corrupt the bitstream.

**`VideoConfig.margin_width/height` actually works.**
Setting margin values causes the phone to render AA UI in a centered sub-region with black bar margins. Useful for non-standard screen ratios (e.g., fitting 16:9 AA onto a wider display with sidebars). Margins are locked at session start -- they can't be changed mid-stream.

**FFmpeg `thread_count` must be 1 for real-time AA decode.**
Multi-threaded decoders (`thread_count=2+`) buffer frames internally, causing permanent `EAGAIN` returns on phones that send small P-frames. Use `thread_count=1` for AA.

**Some phones output `YUVJ420P` instead of `YUV420P`.**
JPEG full-range vs. limited-range YUV420. Your decoder pipeline must accept both pixel formats (`AV_PIX_FMT_YUV420P` and `AV_PIX_FMT_YUVJ420P`) or you'll get a black screen on certain phones. Observed: Moto G Play 2024 outputs YUVJ420P, Samsung S25 Ultra outputs YUV420P.

## Framing

**`MessageType::Control` vs `MessageType::Specific` -- the silent killer.**
Channel 0 (control) messages use `MessageType::Control` (0x00). ALL other service channel messages use `MessageType::Specific` (0x01). If you send a message on channel 1-12 with `MessageType::Control`, the phone silently ignores it. No error, no disconnect, just nothing happens. This is the single most common cause of "my messages aren't working."

**Never drop compressed video packets.**
Dropping ANY P-frame in an H.264/H.265 stream breaks the decoder's reference frame chain. Every subsequent frame will produce artifacts or fail to decode until the next keyframe. If you're overwhelmed, request a lower resolution -- don't drop frames.

## Touch Input

**Actions match Android `MotionEvent` constants:**
- `DOWN` = 0 -- First finger touches
- `UP` = 1 -- Last finger lifts
- `MOVE` = 2 -- Any finger moves
- `POINTER_DOWN` = 5 -- Additional finger touches (while another is already down)
- `POINTER_UP` = 6 -- One finger lifts (while others remain)

**ALL active pointers must be included in every touch message.**
Don't just send the changed finger. Every `InputEventIndication` must include the full list of all currently-touching pointers with their current positions. The phone uses the complete pointer array to track multi-touch state.

**`action_index` is the array index, not the pointer ID.**
`action_index` refers to the position within the pointers array in the current message, NOT the stable `pointer_id`. If you have pointers at array positions [0, 1, 2] and pointer at position 1 lifts, `action_index = 1`.

**For UP events, include the lifted finger.**
When sending a `POINTER_UP` or `UP` event, include the lifted finger in the pointer array at its last known position. The phone needs to know which finger was released.

## WiFi / Bluetooth

**BSSID encoding in protobuf.**
BSSID is protobuf field 3 with tag `0x1a`, encoded as a length-delimited string (not a varint). If you're constructing WiFi credential messages manually, this encoding detail matters.

**WiFi SSID/password must exactly match `hostapd.conf`.**
The values sent in `WifiSecurityResponse` must be character-for-character identical to your actual AP configuration. The phone connects using these credentials verbatim -- no trimming, no case folding.

**Android has a BlueZ SDP UUID size bug.**
BlueZ encodes 16-bit standard UUIDs as 128-bit UUIDs in SDP records. Android's SDP parser rejects records that mix 16-bit and 128-bit UUID sizes. Workaround: strip all standard BlueZ SDP records and register only the AA SDP record, ensuring consistent UUID encoding.

**HFP AG profile must be registered.**
Android Auto requires the HU to register an HFP Audio Gateway profile (`UUID 0000111f`) via BlueZ `ProfileManager1`. Without it, the phone may disconnect Bluetooth before the AA app has a chance to act on the connection.

## Audio

**Three independent audio streams with separate focus.**
Media (channel 4), speech/navigation (channel 5), and phone call (channel 6) each have their own audio focus lifecycle. Audio focus types map to Android's `AudioManager`:
- `GAIN` -- Exclusive audio (e.g., phone call)
- `GAIN_TRANSIENT` -- Short exclusive audio (e.g., navigation prompt)
- `GAIN_TRANSIENT_MAY_DUCK` -- Allow other audio to continue at reduced volume

**PipeWire playback: always output full periods.**
If you're using PipeWire, always write `chunk->size = maxSize` and silence-fill any gap. PipeWire's graph timing is fixed by quantum/rate; writing variable-size chunks causes tempo wobble and audio artifacts.

## Service Discovery

**`device_name` and `device_brand` matter.**
Some phones display the HU's device name in their AA app settings. Use a recognizable name.

**Phone icons are PNG images.**
The `phone_icon_small/medium/large` fields in `ServiceDiscoveryRequest` are 32x32, 64x64, and 128x128 PNG images respectively. They're sent as raw bytes, not base64 or any other encoding.

## General

**The phone is always right.**
When something doesn't work, assume your HU implementation is wrong, not the phone. The AA app has been tested against hundreds of HU implementations. If the phone ignores your messages, rejects your setup, or disconnects unexpectedly, the problem is almost certainly in your framing, message types, or field encoding.
