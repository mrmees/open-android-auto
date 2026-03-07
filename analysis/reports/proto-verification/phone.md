# Phone Channel Verification Report

**Channel:** Phone Status (GAL type 13)
**Handler:** `iat.java` (16.2), tag `CAR.GAL.INST`
**Service:** `hll.java` (16.2), tag `CAR.INST`
**Date:** 2026-03-06
**Status:** COMPLETE — 2 Gold msgs, 1 Gold sub-msg, 2 Gold enums, 2 relocated, 1 removed

## Channel Overview

The phone channel is minimal — only 2 message types. The phone sends call state updates to the HU (0x8001), and the HU sends d-pad navigation input back (0x8002). Despite sharing the `CAR.GAL.INST` log tag with navigation, it's a distinct GAL type (13 vs 10).

## Verified Messages

### PhoneStatusUpdate (0x8001, Phone→HU)

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | vzr only used by hll.java (sender) on GAL type 13 |
| Message ID | PASS | 0x8001 (32769) at hll.java:188 via `m20106k` |
| Direction | FIXED | Phone→HU (was mislabeled as HU→Phone in proto comments) |
| Field schema | FIXED | PhoneCall fields 1-2 changed optional→required per DB + descriptor |
| Cross-references | PASS | Clean — only hll.java and vzr.java |
| Enum values | PASS | PhoneCallState: 7 values (0-6) confirmed via vzq.m37375b |

**16.2 classes:** vzr (PhoneStatusUpdate), vzp (PhoneCall), vzq (PhoneCallState)
**16.1 classes:** waf, wad, wae

### PhoneStatusInput (0x8002, HU→Phone)

| Check | Result | Details |
|-------|--------|---------|
| Channel binding | PASS | vzs only parsed in iat.java (GAL type 13) |
| Message ID | PASS | 0x8002 (32770) at iat.java:24 — the ONLY message this handler accepts |
| Direction | FIXED | HU→Phone (was mislabeled as Phone→HU in proto comments) |
| Field schema | PASS | 3 fields on vzs, 1 enum field on vxo — all match |
| Cross-references | PASS | Clean — only iat.java and vzs.java |
| Enum values | PASS | PhoneInputAction: 8 values (0-7) confirmed via C0000a.m128bw |

**16.2 classes:** vzs (PhoneStatusInput), vxo (PhoneInputType)
**16.1 classes:** wag, vyc

**Note:** vxo in 16.2 is PhoneInputType (phone channel), NOT MediaPlaybackStatusEvent (media channel, also 16.2 class vxo on INST/GAL type 11). These are different instances — the obfuscated name collision is between different channel contexts, but both are valid 16.2 mappings.

## Relocated Protos

| Proto | From | To | Msg ID | Channel | Evidence |
|-------|------|----|--------|---------|----------|
| CallAvailabilityStatus (vvt) | oaa/phone/ | oaa/control/ | 24 | Control (GAL 1) | hzh.java:361-407 handles msg 24, deserializes vvt |
| VoiceSessionRequest (wcu) | oaa/phone/ | oaa/control/ | 17 | Control (GAL 1) | hzh.java method mo20034f sends as msg 17 |

## Removed Protos

| Proto | Reason |
|-------|--------|
| PhoneStatusChannelData | Empty proto3 message with no fields. SDP ChannelDescriptor field 10 serves as marker only. |

## Schema Changes Applied

| File | Change |
|------|--------|
| PhoneStatusMessage.proto | Direction comment fixed (Phone→HU); PhoneCall fields 1-2 optional→required; confidence silver→gold; 16.2 class refs added |
| PhoneStatusInputMessage.proto | Direction comment fixed (HU→Phone); confidence silver→gold; 16.2 class refs added (vzs, vxo, iat.java) |
| PhoneCallStateEnum.proto | Confidence silver→gold; 16.2 class ref (vzq) added |
| CallAvailabilityMessage.proto | Moved to oaa/control/, updated header with control channel context |
| VoiceSessionRequestMessage.proto | Moved to oaa/control/, updated header with control channel context |
