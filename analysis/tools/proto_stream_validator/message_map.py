from __future__ import annotations


MessageKey = tuple[int, int]
ServiceKey = tuple[str, int]


# Channel-specific mappings (for captures without service_type, e.g. cleanbuild)
_MESSAGE_TYPE_BY_TUPLE: dict[MessageKey, str] = {
    # Control channel (always ch0)
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
}

# Service-type mappings (preferred when service_type is available)
_MESSAGE_TYPE_BY_SERVICE: dict[ServiceKey, str] = {
    # Control channel
    ("control", 0x0004): "oaa.proto.messages.AuthCompleteIndication",
    ("control", 0x0005): "oaa.proto.messages.ServiceDiscoveryRequest",
    ("control", 0x0006): "oaa.proto.messages.ServiceDiscoveryResponse",
    ("control", 0x0007): "oaa.proto.messages.ChannelOpenRequest",
    ("control", 0x0008): "oaa.proto.messages.ChannelOpenResponse",
    ("control", 0x000B): "oaa.proto.messages.PingRequest",
    ("control", 0x000C): "oaa.proto.messages.PingResponse",
    ("control", 0x000D): "oaa.proto.messages.NavigationFocusRequest",
    ("control", 0x000E): "oaa.proto.messages.NavigationFocusResponse",
    ("control", 0x000F): "oaa.proto.messages.ShutdownRequest",
    ("control", 0x0010): "oaa.proto.messages.ShutdownResponse",
    ("control", 0x0011): "oaa.proto.messages.VoiceSessionRequest",
    ("control", 0x0012): "oaa.proto.messages.AudioFocusRequest",
    ("control", 0x0013): "oaa.proto.messages.AudioFocusResponse",
    ("control", 0x0018): "oaa.proto.messages.CallAvailabilityStatus",
    # Input
    ("input_source", 0x8001): "oaa.proto.messages.InputEventIndication",
    ("input_source", 0x8002): "oaa.proto.messages.BindingRequest",
    ("input_source", 0x8003): "oaa.proto.messages.BindingResponse",
    # Sensor source
    ("sensor_source", 0x8001): "oaa.proto.messages.SensorStartRequestMessage",
    ("sensor_source", 0x8002): "oaa.proto.messages.SensorStartResponseMessage",
    ("sensor_source", 0x8003): "oaa.proto.messages.SensorEventIndication",
    # AV / media sink (video, audio, mic)
    ("media_sink", 0x8000): "oaa.proto.messages.AVChannelSetupRequest",
    ("media_sink", 0x8001): "oaa.proto.messages.AVChannelStartIndication",
    ("media_sink", 0x8002): "oaa.proto.messages.AVChannelStopIndication",
    ("media_sink", 0x8003): "oaa.proto.messages.AVChannelSetupResponse",
    ("media_sink", 0x8004): "oaa.proto.messages.AVMediaAckIndication",
    ("media_sink", 0x8005): "oaa.proto.messages.AVInputOpenRequest",
    ("media_sink", 0x8006): "oaa.proto.messages.AVInputOpenResponse",
    ("media_sink", 0x8007): "oaa.proto.messages.VideoFocusRequest",
    ("media_sink", 0x8008): "oaa.proto.messages.VideoFocusIndication",
    # Navigation / nav_status
    ("navigation", 0x8001): "oaa.proto.messages.InstrumentClusterStart",
    ("navigation", 0x8002): "oaa.proto.messages.InstrumentClusterStop",
    ("navigation", 0x8003): "oaa.proto.messages.NavigationState",
    ("navigation", 0x8006): "oaa.proto.messages.NavigationNotification",
    ("navigation", 0x8007): "oaa.proto.messages.NavigationNextTurnDistanceEvent",
    ("navigation", 0x8008): "oaa.proto.messages.VehicleEnergyForecast",
    ("nav_status", 0x8001): "oaa.proto.messages.InstrumentClusterStart",
    ("nav_status", 0x8002): "oaa.proto.messages.InstrumentClusterStop",
    ("nav_status", 0x8003): "oaa.proto.messages.NavigationState",
    ("nav_status", 0x8006): "oaa.proto.messages.NavigationNotification",
    ("nav_status", 0x8007): "oaa.proto.messages.NavigationNextTurnDistanceEvent",
    ("nav_status", 0x8008): "oaa.proto.messages.VehicleEnergyForecast",
    # Phone status
    ("phone_status", 0x8001): "oaa.proto.messages.PhoneStatusUpdate",
    ("phone_status", 0x8002): "oaa.proto.messages.PhoneStatusInput",
    # Media info
    ("media_info", 0x8001): "oaa.proto.messages.MediaPlaybackStatus",
    ("media_info", 0x8002): "oaa.proto.messages.MediaPlaybackStatusEvent",
    ("media_info", 0x8003): "oaa.proto.messages.MediaPlaybackMetadata",
    # Sensor (WiFi/BT)
    ("sensor", 0x8001): "oaa.proto.messages.WifiSecurityRequest",
    ("sensor", 0x8002): "oaa.proto.messages.WifiSecurityResponse",
}

# ChannelOpen appears on every channel (sent on the channel being opened)
_UNIVERSAL_MESSAGES: dict[int, str] = {
    0x0007: "oaa.proto.messages.ChannelOpenRequest",
    0x0008: "oaa.proto.messages.ChannelOpenResponse",
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
    service_type: str | None = None,
) -> str:
    """Resolve a stream tuple to protobuf fully-qualified message type.

    Resolution order:
    1. (service_type, message_id) if service_type is provided
    2. (channel_id, message_id) for legacy captures
    3. Universal messages (ChannelOpen on any channel)
    4. message_name fallback
    """
    del direction  # Kept for future disambiguation.

    if service_type:
        skey = (service_type, message_id)
        if skey in _MESSAGE_TYPE_BY_SERVICE:
            return _MESSAGE_TYPE_BY_SERVICE[skey]

    key = (channel_id, message_id)
    if key in _MESSAGE_TYPE_BY_TUPLE:
        return _MESSAGE_TYPE_BY_TUPLE[key]

    if message_id in _UNIVERSAL_MESSAGES:
        return _UNIVERSAL_MESSAGES[message_id]

    if message_name and message_name in _MESSAGE_TYPE_BY_NAME:
        return _MESSAGE_TYPE_BY_NAME[message_name]

    name_part = f", message_name={message_name}" if message_name else ""
    svc_part = f", service_type={service_type}" if service_type else ""
    raise KeyError(
        f"unmapped tuple: channel_id={channel_id}, message_id=0x{message_id:04x}{name_part}{svc_part}"
    )
