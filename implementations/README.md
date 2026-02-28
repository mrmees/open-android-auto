# Implementations

This directory is for community-contributed Android Auto protocol implementations.

In this repository, an implementation is a library that uses the shared `.proto` definitions in `oaa/` to conduct an Android Auto session end-to-end: connection setup, handshake, encryption, channel multiplexing, and message dispatch.

## Expected Coverage for a Complete Implementation

A complete implementation should cover:

- TCP transport
- SSL/TLS handshake and authenticated session setup
- Message framing (frame header encode/decode)
- Encryption handling (AES-128-GCM after authentication)
- Channel open/close lifecycle
- Service discovery
- Channel handlers (video, audio, input, sensor, navigation, and other services)

## Contribution Structure

Each implementation should live in its own subdirectory, for example:

```text
implementations/
|- qt/
|  `- README.md
`- rust/
   `- README.md
```

Each implementation directory should include a `README.md` with dependencies, build steps, usage examples, and current coverage status.

## Current Implementation Baseline

| Implementation | Status | Notes |
|----------------|--------|-------|
| `qt` | Bootstrapped in this repo | Runtime framework currently lives in `openauto-prodigy`; this repo tracks protocol-facing scope and contribution flow in `implementations/qt/README.md`. |

## Partial Implementations Are Welcome

Contributions do not need to be complete to be accepted. Partial implementations are welcome if scope and limitations are documented clearly.
