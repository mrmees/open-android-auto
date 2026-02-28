from __future__ import annotations


MessageKey = tuple[int, int]


_MESSAGE_TYPE_BY_TUPLE: dict[MessageKey, str] = {
    # Control channel
    (0, 0x0004): "oaa.proto.messages.AuthCompleteIndication",
    (0, 0x0005): "oaa.proto.messages.ServiceDiscoveryRequest",
    (0, 0x0006): "oaa.proto.messages.ServiceDiscoveryResponse",
    (0, 0x0007): "oaa.proto.messages.ChannelOpenRequest",
    (0, 0x0008): "oaa.proto.messages.ChannelOpenResponse",
    (0, 0x000B): "oaa.proto.messages.PingRequest",
    (0, 0x000C): "oaa.proto.messages.PingResponse",
    (0, 0x000D): "oaa.proto.messages.NavigationFocusRequest",
    (0, 0x000E): "oaa.proto.messages.NavigationFocusResponse",
    (0, 0x000F): "oaa.proto.messages.ShutdownRequest",
    (0, 0x0010): "oaa.proto.messages.ShutdownResponse",
    (0, 0x0011): "oaa.proto.messages.VoiceSessionRequest",
    (0, 0x0012): "oaa.proto.messages.AudioFocusRequest",
    (0, 0x0013): "oaa.proto.messages.AudioFocusResponse",
    (0, 0x0018): "oaa.proto.messages.CallAvailabilityStatus",
    # Input
    (1, 0x8001): "oaa.proto.messages.InputEventIndication",
    (1, 0x8002): "oaa.proto.messages.BindingRequest",
    (1, 0x8003): "oaa.proto.messages.BindingResponse",
    # Sensor
    (2, 0x8001): "oaa.proto.messages.SensorStartRequestMessage",
    (2, 0x8002): "oaa.proto.messages.SensorStartResponseMessage",
    (2, 0x8003): "oaa.proto.messages.SensorEventIndication",
    # AV channels (non-media control messages)
    (3, 0x8000): "oaa.proto.messages.AVChannelSetupRequest",
    (3, 0x8001): "oaa.proto.messages.AVChannelStartIndication",
    (3, 0x8002): "oaa.proto.messages.AVChannelStopIndication",
    (3, 0x8003): "oaa.proto.messages.AVChannelSetupResponse",
    (3, 0x8004): "oaa.proto.messages.AVMediaAckIndication",
    (3, 0x8007): "oaa.proto.messages.VideoFocusRequest",
    (3, 0x8008): "oaa.proto.messages.VideoFocusIndication",
    (7, 0x8005): "oaa.proto.messages.AVInputOpenRequest",
    (7, 0x8006): "oaa.proto.messages.AVInputOpenResponse",
    # Bluetooth
    (8, 0x8001): "oaa.proto.messages.BluetoothPairingRequest",
    (8, 0x8002): "oaa.proto.messages.BluetoothPairingResponse",
    # WiFi
    (14, 0x8001): "oaa.proto.messages.WifiSecurityRequest",
    (14, 0x8002): "oaa.proto.messages.WifiSecurityResponse",
}

_MESSAGE_TYPE_BY_NAME: dict[str, str] = {
    "AUTH_COMPLETE": "oaa.proto.messages.AuthCompleteIndication",
    "SERVICE_DISCOVERY_REQUEST": "oaa.proto.messages.ServiceDiscoveryRequest",
    "SERVICE_DISCOVERY_RESPONSE": "oaa.proto.messages.ServiceDiscoveryResponse",
    "CHANNEL_OPEN_REQUEST": "oaa.proto.messages.ChannelOpenRequest",
    "CHANNEL_OPEN_RESPONSE": "oaa.proto.messages.ChannelOpenResponse",
    "PING_REQUEST": "oaa.proto.messages.PingRequest",
    "PING_RESPONSE": "oaa.proto.messages.PingResponse",
    "NAVIGATION_FOCUS_REQUEST": "oaa.proto.messages.NavigationFocusRequest",
    "NAVIGATION_FOCUS_RESPONSE": "oaa.proto.messages.NavigationFocusResponse",
    "VOICE_SESSION_REQUEST": "oaa.proto.messages.VoiceSessionRequest",
    "AUDIO_FOCUS_REQUEST": "oaa.proto.messages.AudioFocusRequest",
    "AUDIO_FOCUS_RESPONSE": "oaa.proto.messages.AudioFocusResponse",
    "INPUT_EVENT_INDICATION": "oaa.proto.messages.InputEventIndication",
    "BINDING_REQUEST": "oaa.proto.messages.BindingRequest",
    "BINDING_RESPONSE": "oaa.proto.messages.BindingResponse",
    "SENSOR_START_REQUEST": "oaa.proto.messages.SensorStartRequestMessage",
    "SENSOR_START_RESPONSE": "oaa.proto.messages.SensorStartResponseMessage",
    "SENSOR_EVENT_INDICATION": "oaa.proto.messages.SensorEventIndication",
    "AV_SETUP_REQUEST": "oaa.proto.messages.AVChannelSetupRequest",
    "AV_SETUP_RESPONSE": "oaa.proto.messages.AVChannelSetupResponse",
    "AV_START_INDICATION": "oaa.proto.messages.AVChannelStartIndication",
    "AV_STOP_INDICATION": "oaa.proto.messages.AVChannelStopIndication",
    "AV_MEDIA_ACK": "oaa.proto.messages.AVMediaAckIndication",
    "VIDEO_FOCUS_REQUEST": "oaa.proto.messages.VideoFocusRequest",
    "VIDEO_FOCUS_INDICATION": "oaa.proto.messages.VideoFocusIndication",
    "AV_INPUT_OPEN_REQUEST": "oaa.proto.messages.AVInputOpenRequest",
    "AV_INPUT_OPEN_RESPONSE": "oaa.proto.messages.AVInputOpenResponse",
    "BT_PAIRING_REQUEST": "oaa.proto.messages.BluetoothPairingRequest",
    "BT_PAIRING_RESPONSE": "oaa.proto.messages.BluetoothPairingResponse",
    "WIFI_CREDENTIALS_REQUEST": "oaa.proto.messages.WifiSecurityRequest",
    "WIFI_CREDENTIALS_RESPONSE": "oaa.proto.messages.WifiSecurityResponse",
}


def resolve_message_type(
    direction: str,
    channel_id: int,
    message_id: int,
    message_name: str | None = None,
) -> str:
    """Resolve a stream tuple to protobuf fully-qualified message type."""
    del direction  # Direction is currently informational; kept for future disambiguation.

    key = (channel_id, message_id)
    if key in _MESSAGE_TYPE_BY_TUPLE:
        return _MESSAGE_TYPE_BY_TUPLE[key]

    if message_name and message_name in _MESSAGE_TYPE_BY_NAME:
        return _MESSAGE_TYPE_BY_NAME[message_name]

    name_part = f", message_name={message_name}" if message_name else ""
    raise KeyError(
        f"unmapped tuple: channel_id={channel_id}, message_id=0x{message_id:04x}{name_part}"
    )
