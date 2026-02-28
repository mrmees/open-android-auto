# Qt Implementation (Bridge Entry)

This directory tracks the Qt-based Android Auto protocol implementation currently maintained in the `openauto-prodigy` repository.

## Current Source of Truth

- Upstream repository: https://github.com/mrmees/openauto-prodigy
- Implementation stack: Qt-based Android Auto runtime/framework
- Role of this directory: protocol-home bridge for contributors working from the shared `oaa/` definitions in this repository

## Scope

The Qt implementation targets the standard Android Auto protocol session lifecycle:

- TCP transport
- TLS handshake/auth flow
- Message framing
- AES-128-GCM session encryption
- Channel lifecycle and service discovery
- Channel handlers (video, audio, input, sensor, navigation, and related services)

## Coverage Status

This bridge entry is documentation-first. Runtime code remains upstream in `openauto-prodigy` today.

Use this checklist to track verified protocol coverage in the Qt stack.

Status legend:
- `Verified`: confirmed working with evidence (code + run/test/capture)
- `Partial`: some pieces implemented, not complete yet
- `Unknown`: not audited yet

| Area | Status | Notes |
|------|--------|-------|
| TCP transport | Partial | Evidence-backed in upstream; see TCP audit references below. |
| TLS handshake/auth flow | Partial | Evidence-backed in upstream; see TLS audit references below. |
| Message framing (header encode/decode) | Partial | Expected in upstream runtime; exact class/module mapping audit still pending. |
| AES-128-GCM session encryption | Partial | Expected in upstream runtime; exact class/module mapping audit still pending. |
| Channel open/close lifecycle | Partial | Expected in upstream runtime; exact class/module mapping audit still pending. |
| Service discovery | Partial | Expected in upstream runtime; exact class/module mapping audit still pending. |
| Video channel handler | Partial | Expected in upstream runtime; exact class/module mapping audit still pending. |
| Audio channel handler | Partial | Expected in upstream runtime; exact class/module mapping audit still pending. |
| Input channel handler | Partial | Expected in upstream runtime; exact class/module mapping audit still pending. |
| Sensor channel handler | Partial | Expected in upstream runtime; exact class/module mapping audit still pending. |
| Navigation channel handler | Partial | Expected in upstream runtime; exact class/module mapping audit still pending. |

### Evidence Snapshot (2026-02-28)

TCP transport (`Partial`):
- `/openauto-prodigy/libs/open-androidauto/src/Transport/TCPTransport.cpp`:
  `connectToHost` wiring and socket creation (`18-25`), socket write path (`55-63`), signal wiring (`70-80`).
- `/openauto-prodigy/src/core/aa/AndroidAutoOrchestrator.cpp`:
  runtime injection of accepted `QTcpSocket` into `oaa::TCPTransport` (`218-220`), AA session startup (`437-439`).
- `/openauto-prodigy/libs/open-androidauto/tests/test_tcp_transport.cpp`:
  local connection/send/receive + disconnect unit coverage (`9-43`, `45-69`).

TLS handshake/auth flow (`Partial`):
- `/openauto-prodigy/libs/open-androidauto/src/Messenger/Cryptor.cpp`:
  TLS role method selection (`14-17`), handshake drive (`79-95`), encrypt/decrypt path (`115-148`).
- `/openauto-prodigy/libs/open-androidauto/src/Messenger/Messenger.cpp`:
  handshake start (`138-142`), SSL_HANDSHAKE message routing (`177-183`), handshake drive/output + completion signal (`195-207`).
- `/openauto-prodigy/libs/open-androidauto/src/Session/AASession.cpp`:
  transition into TLS handshake (`220-223`) and post-handshake AUTH_COMPLETE flow (`226-233`).
- `/openauto-prodigy/libs/open-androidauto/tests/test_cryptor.cpp`:
  handshake activation and encrypt/decrypt unit coverage (`28-53`).
- `/openauto-prodigy/libs/open-androidauto/tests/test_session_fsm.cpp`:
  version-match transition into `TLSHandshake` state (`126-139`).

When protocol-facing modules are moved or shared into this repository, keep this README updated with:

- exact copied/extracted paths
- supported protocol surface
- build/test commands for the local implementation

## Contribution Notes

- Protocol-alignment PRs are welcome (mapping updates, message compatibility notes, decompilation evidence links).
- If proposing code movement from `openauto-prodigy` into this repository, include a small staged migration plan in the PR description.
