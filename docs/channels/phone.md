# Phone Channel

## Proto Confidence Summary

| Message | Tier | Evidence | Audit File |
|---------|------|----------|------------|
| PhoneStatusUpdate | Silver | apk_static + cross_version | [PhoneStatusMessage.audit.yaml](../../oaa/phone/PhoneStatusMessage.audit.yaml) |
| PhoneCall | Silver | apk_static + cross_version | [PhoneStatusMessage.audit.yaml](../../oaa/phone/PhoneStatusMessage.audit.yaml) |
| CallAvailabilityStatus | Silver | apk_static + cross_version | [CallAvailabilityMessage.audit.yaml](../../oaa/phone/CallAvailabilityMessage.audit.yaml) |
| VoiceSessionRequest | Silver | apk_static + cross_version | [VoiceSessionRequestMessage.audit.yaml](../../oaa/phone/VoiceSessionRequestMessage.audit.yaml) |
| PhoneStatusInput | Silver | apk_static + cross_version | [PhoneStatusInputMessage.audit.yaml](../../oaa/phone/PhoneStatusInputMessage.audit.yaml) |
| PhoneCallState (enum) | Silver | apk_static + cross_version | [PhoneCallStateEnum.audit.yaml](../../oaa/phone/PhoneCallStateEnum.audit.yaml) |
| PhoneStatusChannel | Unverified | -- | -- |

## Overview

Channel 12 (`PHONE_STATUS`) carries call state and availability information from the phone to the head unit. This is a relatively thin channel -- the phone handles actual telephony, and this channel primarily notifies the HU about call state changes for UI display (incoming call banners, active call indicators, signal strength).

The channel has 6 proto files with 5 audit sidecars and 7 cross-version mappings. All message-level protos are Silver confidence. See [cross-version mapping table](../cross-version/phone.md) for version stability across 15.9, 16.1, and 16.2.

**Scope boundary:** DTMF tone input and contact synchronization are NOT part of this channel. These functions likely flow through Bluetooth HFP profile and Android's Contacts provider respectively, not the AA wire protocol. See [Evidence Gaps](#evidence-gaps) for details.

---

## Message Catalog

> Confidence: Silver [apk_static, cross_version] -- all messages Silver except PhoneStatusChannel (Unverified, empty config message)

| MsgID | Message | Direction | Purpose |
|-------|---------|-----------|---------|
| 0x8001 | PhoneStatusUpdate | Phone -> HU | Call state, signal strength, active calls |
| 0x8002 | PhoneStatusInput | Phone -> HU | D-pad input relayed from phone UI |
| -- | CallAvailabilityStatus | Phone -> HU | Whether phone calls are currently available |
| -- | VoiceSessionRequest | HU -> Phone | Trigger voice assistant activation |
| -- | PhoneStatusChannel | Service Discovery | Empty channel configuration message |

### PhoneStatusUpdate (0x8001)

The primary message on this channel. Contains a list of active calls and signal strength.

```protobuf
message PhoneStatusUpdate {
    repeated PhoneCall calls = 1;        // Active calls (empty = idle)
    optional uint32 signal_strength = 2; // Cellular signal level
}

message PhoneCall {
    optional PhoneCallState.Enum call_state = 1;   // UNKNOWN through MUTED
    optional uint32 call_duration_seconds = 2;      // Elapsed since connected
    optional string phone_number = 3;               // e.g. "+1 858-225-7702"
    optional string display_name = 4;               // e.g. "Spam Risk", contact name
    optional string contact_id = 5;                 // Empty for unknown contacts
    optional bytes contact_photo = 6;               // PNG image (sent with ACTIVE)
}
```

**PhoneCallState** values:

| Value | Name | Meaning |
|-------|------|---------|
| 0 | UNKNOWN | Default/unset |
| 1 | IN_CALL | Active voice call |
| 2 | ON_HOLD | Call placed on hold |
| 3 | INACTIVE | Call ended or not active |
| 4 | INCOMING | Ringing, not yet answered |
| 5 | CONFERENCED | Part of a conference call |
| 6 | MUTED | Call muted (microphone off) |

### CallAvailabilityStatus

Single boolean indicating whether the phone can make calls.

```protobuf
message CallAvailabilityStatus {
    optional bool call_available = 1;
}
```

This reflects cellular connectivity -- `false` when out of service, in airplane mode, or when the phone otherwise cannot place calls.

### VoiceSessionRequest

> Confidence: Silver [apk_static, cross_version] -- single enum field, straightforward

Triggers voice assistant activation on the phone. This is an HU-to-phone message -- the user presses a voice button on the HU, and this message tells the phone to start listening.

```protobuf
message VoiceSessionRequest {
    optional VoiceSessionType session_type = 1;
}

enum VoiceSessionType {
    VOICE_SESSION_START = 1;  // Open microphone, start assistant
    VOICE_SESSION_STOP = 2;   // End voice session
}
```

Note: `VoiceSessionType` value 0 is intentionally absent -- the APK throws null on value 0, indicating it is an invalid/unsupported state.

---

## State Machine

```
Phone                                    Head Unit
  |                                         |
  |  Incoming call                          |
  |                                         |
  |--- PhoneStatusUpdate ----------------->  |  calls[0].state = INCOMING
  |     call_state: INCOMING                |  phone_number, display_name set
  |     phone_number: "+1 555-1234"         |
  |     display_name: "John Smith"          |
  |                                         |
  |  User answers on HU (d-pad ENTER)       |
  |                                         |
  |<-- PhoneStatusInput -------------------  |  action: PHONE_INPUT_ENTER
  |                                         |
  |--- PhoneStatusUpdate ----------------->  |  calls[0].state = IN_CALL
  |     call_state: IN_CALL                 |  call_duration_seconds starts
  |     contact_photo: [PNG bytes]          |  contact_photo sent with ACTIVE
  |                                         |
  |  Call ends                              |
  |                                         |
  |--- PhoneStatusUpdate ----------------->  |  calls = [] (empty = idle)
  |                                         |
```

The phone drives all state transitions. PhoneStatusUpdate with an empty `calls` list indicates idle state (no active calls). Multiple concurrent calls appear as multiple entries in the `calls` repeated field.

---

## PhoneStatusInput and Instrument Cluster Connection

> Confidence: Silver [apk_static, cross_version] -- PhoneStatusInput is Silver; shared enum is structurally confirmed

PhoneStatusInput carries d-pad navigation events using the same 0-7 enum values as InstrumentClusterAction on the navigation channel:

```protobuf
message PhoneStatusInput {
    optional PhoneInputType input_type = 1;   // Wraps PhoneInputAction enum (0-7)
    optional string caller_id = 2;            // Phone number or identifier
    optional string display_name = 3;         // Contact display name
}
```

| Value | PhoneInputAction | InstrumentClusterAction |
|-------|-----------------|------------------------|
| 0 | PHONE_INPUT_UNKNOWN | CLUSTER_ACTION_UNKNOWN |
| 1 | PHONE_INPUT_UP | CLUSTER_ACTION_UP |
| 2 | PHONE_INPUT_DOWN | CLUSTER_ACTION_DOWN |
| 3 | PHONE_INPUT_LEFT | CLUSTER_ACTION_LEFT |
| 4 | PHONE_INPUT_RIGHT | CLUSTER_ACTION_RIGHT |
| 5 | PHONE_INPUT_ENTER | CLUSTER_ACTION_ENTER |
| 6 | PHONE_INPUT_BACK | CLUSTER_ACTION_BACK |
| 7 | PHONE_INPUT_CALL | CLUSTER_ACTION_CALL |

Both use the handler log tag `CAR.GAL.INST` and service log tag `CAR.INST`. This strongly suggests shared input handling infrastructure -- the phone status display on the instrument cluster uses the same d-pad navigation model as the main cluster display.

> **Gotcha:** PhoneStatusInput and InstrumentClusterInput share the same d-pad enum values (0-7) and the same APK handler infrastructure (`CAR.GAL.INST`). If you're implementing both the phone status display and the instrument cluster, you can share your input handling code -- but be aware they arrive on different channels (12 vs 11) with different message wrappers.

---

## Evidence Gaps

### DTMF Tone Input

No proto evidence exists for sending DTMF tones (touch-tone digits) through the AA wire protocol. DTMF during active calls almost certainly flows through the **Bluetooth HFP (Hands-Free Profile)** audio channel, which carries the voice call audio bidirectionally. The AA wire protocol manages call state display, not call audio control.

### Contact Synchronization

No proto evidence exists for contact list synchronization through the AA wire protocol. Contact data (names, photos, phone numbers) for caller ID likely comes through **Android's Contacts provider** via the Bluetooth PBAP (Phone Book Access Profile) or through the contact fields embedded in PhoneStatusUpdate itself (display_name, contact_id, contact_photo). There is no bulk contact sync mechanism in the phone channel protos.

These are not gaps in the documentation -- they reflect the actual protocol boundary. The AA wire protocol handles UI state notification, while Bluetooth profiles handle the underlying telephony and contact data transport.

---

## Implementation Guide

### Displaying Call State

A basic phone status implementation handles three UI states:

1. **Idle** -- `calls` is empty. No phone UI shown or show signal strength only.
2. **Incoming** -- `call_state = INCOMING`. Show incoming call banner with caller name/number. Provide accept/reject buttons mapped to PhoneStatusInput.
3. **Active** -- `call_state = IN_CALL`. Show active call card with caller info, duration counter, and mute/hold controls.

```c
void handle_phone_status(const PhoneStatusUpdate* status) {
    if (status->calls_size() == 0) {
        ui_hide_phone_card();
        if (status->has_signal_strength())
            ui_set_signal_bars(status->signal_strength());
        return;
    }

    const PhoneCall& call = status->calls(0);
    switch (call.call_state()) {
        case PhoneCallState::INCOMING:
            ui_show_incoming_call(call.display_name(),
                                 call.phone_number());
            break;
        case PhoneCallState::IN_CALL:
            ui_show_active_call(call.display_name(),
                                call.call_duration_seconds());
            if (call.has_contact_photo())
                ui_set_caller_photo(call.contact_photo().data(),
                                    call.contact_photo().size());
            break;
        case PhoneCallState::ON_HOLD:
            ui_show_hold_indicator();
            break;
        default:
            break;
    }
}
```

### Voice Assistant Button

Map a physical or on-screen microphone button to VoiceSessionRequest:

```c
void on_voice_button_press() {
    VoiceSessionRequest req;
    req.set_session_type(VOICE_SESSION_START);
    send_phone_channel(req);
}

void on_voice_button_release() {
    VoiceSessionRequest req;
    req.set_session_type(VOICE_SESSION_STOP);
    send_phone_channel(req);
}
```

---

## Gotchas

> **Gotcha:** DTMF tones are NOT sent through the AA wire protocol. If your HU has a dial pad for in-call DTMF, those tones must be sent through the Bluetooth HFP audio channel, not through PhoneStatusInput or any phone channel message. There is no DTMF proto message.

> **Gotcha:** The `contact_photo` field in PhoneCall is sent with the `IN_CALL` state, not with `INCOMING`. When the phone first reports an incoming call, the photo may not yet be present. Update your UI when the state transitions to IN_CALL and check for the photo field again.

> **Gotcha:** `signal_strength` is a uint32 on PhoneStatusUpdate, not on PhoneCall. It represents the phone's cellular signal level, not a per-call quality metric. The exact scale is not documented in the proto -- Android typically uses 0-4 bars, but the raw value may be a different range. Test with your target phone to calibrate your signal bar UI.

---

## References

### Proto Files
- [PhoneStatusMessage.proto](../../oaa/phone/PhoneStatusMessage.proto)
- [CallAvailabilityMessage.proto](../../oaa/phone/CallAvailabilityMessage.proto)
- [VoiceSessionRequestMessage.proto](../../oaa/phone/VoiceSessionRequestMessage.proto)
- [PhoneStatusInputMessage.proto](../../oaa/phone/PhoneStatusInputMessage.proto)
- [PhoneCallStateEnum.proto](../../oaa/phone/PhoneCallStateEnum.proto)
- [PhoneStatusChannelData.proto](../../oaa/phone/PhoneStatusChannelData.proto)

### Audit Sidecars
- [PhoneStatusMessage.audit.yaml](../../oaa/phone/PhoneStatusMessage.audit.yaml)
- [CallAvailabilityMessage.audit.yaml](../../oaa/phone/CallAvailabilityMessage.audit.yaml)
- [VoiceSessionRequestMessage.audit.yaml](../../oaa/phone/VoiceSessionRequestMessage.audit.yaml)
- [PhoneStatusInputMessage.audit.yaml](../../oaa/phone/PhoneStatusInputMessage.audit.yaml)
- [PhoneCallStateEnum.audit.yaml](../../oaa/phone/PhoneCallStateEnum.audit.yaml)

### Cross-References
- [Phone Cross-Version Mapping](../cross-version/phone.md) (7 mappings across v15.9, v16.1, v16.2)
- [Channel Map](../channel-map.md) (Channel 12: Phone Status)
- [Channel Lifecycle](../interactions/04-channel-lifecycle.md) (channel open/close flow)
- [Navigation Channel](nav.md) (InstrumentCluster shared enum reference)
- [Confidence Tiers](../verification/01-confidence-tiers.md) (tier definitions)
