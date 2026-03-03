# Interaction Specs Design

**Date:** 2026-03-02
**Status:** Approved

## Goal

Create modular, step-by-step interaction specifications for the AA/Phone protocol. Each doc covers one phase of the session lifecycle with exact wire formats, protobuf payloads, error handling, and implementation notes. Living documents — updated as new findings emerge.

## Documents

| Doc | Phase | Scope |
|-----|-------|-------|
| `01-transport-setup.md` | Physical → TCP | BT discovery, RFCOMM handshake, WiFi credential exchange, TCP connect. Also covers USB AOA wired path. References `wireless-bluetooth-setup.md` for BT/SDP details. |
| `02-version-ssl-auth.md` | TCP → Authenticated | Binary version exchange, app-layer TLS 1.2 handshake, auth/binding. Starts at "TCP socket is open." |
| `03-service-discovery.md` | Authenticated → Configured | ServiceDiscoveryRequest/Response, capability negotiation, what the phone expects and what the HU must advertise. |
| `04-channel-lifecycle.md` | Configured → Streaming | Channel open/close, per-channel AV setup (video, audio, sensor, input), flow control, focus management. |

## Document Template

Each doc follows:
1. **Overview** — 2-3 sentences
2. **Prerequisites** — what must be true before this phase
3. **Sequence Diagram** — ASCII, HU↔Phone
4. **Step-by-Step** — per-message detail: direction, wire format, fields, expected response, timing
5. **Error Handling** — failure modes, detection, recovery
6. **Log Tags** — logcat tags for this phase
7. **Implementation Notes** — gotchas, version-gated behavior
8. **References** — proto files, APK source, other docs

## Approach

- Start with doc 2 (version/SSL/auth) — doc 1 is largely covered by existing `wireless-bluetooth-setup.md`
- Draw from: `phone-side-debug.md` captures, APK decompilation, `gal-protocol-reference.md`, aasdk source knowledge, firmware analyses
- Include real captured values (cert subjects, version bytes, timing) alongside the spec
- Each doc ends with the exact postcondition that the next doc's prerequisite expects

## Source Material

- Captured session in `phone-side-debug.md` (Samsung S25 Ultra → Pi 4, wireless)
- APK v16.2 decompiled at `analysis/aa-16.2/jadx-output/`
- GAL reference from DHU 2.1 at `analysis/gal-protocol-reference.md`
- Existing proto files in `oaa/`
- Firmware analyses in `docs/decompiled_headunit_firmware/`
