# AGENTS.md

## Scope Note

This repository is a protocol-reference and documentation project.
Behavior-changing work should stay scoped to protobuf definitions, protocol
documentation, and analysis tooling in this repository.

## Project Management Loop

For behavior-changing work in this repository:

1. Check alignment with the protocol-reference scope before implementation.
2. Update `docs/roadmap-current.md` when priorities or sequencing change.
3. Before claiming completion, run verification commands relevant to the files changed.
4. Append a handoff entry to `docs/session-handoffs.md` including:
   - what changed
   - why
   - status
   - next 1-3 steps
   - verification commands/results

## Verification Baseline

Use the smallest complete verification set that matches your changes:

- Proto changes:
  - `protoc --proto_path=proto --cpp_out=/tmp <changed-proto-files>`
- Documentation changes:
  - Run path/reference sanity checks (for example, `rg` checks for renamed or stale paths).
- `analysis/tools/*` changes:
  - Run the tool's documented smoke command from its local README or Makefile.

## Completion Rule

Do not claim work is complete without fresh verification evidence. Record
verification commands and outcomes in `docs/session-handoffs.md`.

## Workflow Priority

This file defines repository-specific workflow expectations. Platform-level
safety and skill instructions still apply.
