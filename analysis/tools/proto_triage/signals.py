"""Four signal computations for proto class triage."""
from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass, field

from analysis.tools.proto_triage.db import ProtoInfo


# --- Signal Results ---

@dataclass
class BFSResult:
    """Result of sub-message graph BFS from known seeds."""
    # class_name → hop distance from nearest seed
    hop_distance: dict[str, int] = field(default_factory=dict)


@dataclass
class HubResult:
    """Result of hub-file co-reference analysis."""
    # class_name → number of hub files that reference it
    hub_file_count: dict[str, int] = field(default_factory=dict)
    # class_name → set of hub files referencing it
    hub_files: dict[str, set[str]] = field(default_factory=dict)


@dataclass
class PackageResult:
    """Result of named-package classification."""
    # class_name → "INTERNAL" or "WIRE"
    classification: dict[str, str] = field(default_factory=dict)
    # class_name → set of matching package patterns
    evidence: dict[str, set[str]] = field(default_factory=dict)


@dataclass
class StructuralResult:
    """Result of structural feature analysis."""
    # class_name → set of feature flags
    features: dict[str, set[str]] = field(default_factory=dict)


# --- Internal package patterns ---

_INTERNAL_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"analytics", re.IGNORECASE),
    re.compile(r"feedback", re.IGNORECASE),
    re.compile(r"survey", re.IGNORECASE),
    re.compile(r"crash", re.IGNORECASE),
    re.compile(r"telemetry", re.IGNORECASE),
    re.compile(r"firebase", re.IGNORECASE),
    re.compile(r"InstallReferrer", re.IGNORECASE),
    re.compile(r"bugreport", re.IGNORECASE),
    re.compile(r"clearcut", re.IGNORECASE),
    re.compile(r"ConnectivityEvent", re.IGNORECASE),
    re.compile(r"performance\.primes", re.IGNORECASE),
    re.compile(r"CarSetupService", re.IGNORECASE),
]

_WIRE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"projection\.gearhead\.(?:services|protocol)", re.IGNORECASE),
    re.compile(r"gearhead\.projection", re.IGNORECASE),
    re.compile(r"projection\.(?:common|media|input|sensor)", re.IGNORECASE),
]


# --- Telemetry cluster detection ---

# Patterns that identify telemetry/logging root classes when they appear
# as the ONLY named references for a proto class.
_TELEMETRY_ROOT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ConnectivityEvent", re.IGNORECASE),
    re.compile(r"clearcut", re.IGNORECASE),
    re.compile(r"performance\.primes", re.IGNORECASE),
    re.compile(r"[Tt]elemetry"),
    re.compile(r"CarSetupService", re.IGNORECASE),
]


def compute_telemetry_cluster(
    universe: dict[str, ProtoInfo],
    seeds: set[str],
    class_to_packages: dict[str, set[str]],
) -> set[str]:
    """Identify telemetry root classes and expand through sub_message_refs.

    A telemetry root is a non-seed class whose ONLY named (non-obfuscated)
    package references match telemetry patterns. We then BFS through
    sub_message_refs to find all sub-messages that belong exclusively to the
    telemetry tree (stopping at seeds, which are shared with wire protocol).

    Returns the set of class names in the telemetry cluster.
    """
    # Step 1: Find telemetry roots
    roots: set[str] = set()
    for cls, packages in class_to_packages.items():
        if cls in seeds:
            continue
        named = [
            p for p in packages
            if p.startswith(("com.", "android.", "org."))
            and not p.startswith("defpackage.")
        ]
        if not named:
            continue
        # ALL named references must match telemetry patterns
        all_telemetry = all(
            any(pat.search(p) for pat in _TELEMETRY_ROOT_PATTERNS)
            for p in named
        )
        if all_telemetry:
            roots.add(cls)

    # Step 2: BFS from roots through sub_message_refs (directed, not bidirectional)
    cluster: set[str] = set(roots)
    queue = deque(roots)
    while queue:
        cls = queue.popleft()
        info = universe.get(cls)
        if not info:
            continue
        for ref in info.sub_message_refs:
            if ref in seeds or ref in cluster or ref not in universe:
                continue
            cluster.add(ref)
            queue.append(ref)

    return cluster


# --- Signal 1: Sub-message graph BFS ---

def compute_bfs_signal(
    graph: dict[str, set[str]],
    seeds: set[str],
    max_hops: int = 5,
    excluded: set[str] | None = None,
) -> BFSResult:
    """BFS from known wire seeds through sub-message graph.

    Expands bidirectionally — if known A embeds unknown B, B gets a hop.
    If unknown C embeds known D, C gets a hop too (graph is bidirectional).

    Classes in ``excluded`` are treated as walls — BFS won't enter or
    traverse through them, preventing telemetry clusters from polluting
    wire-protocol results.
    """
    result = BFSResult()
    blocked = (excluded or set()) | seeds
    visited: set[str] = set(blocked)
    queue: deque[tuple[str, int]] = deque()

    # Seed the BFS with direct neighbors of known classes
    for seed in seeds:
        for neighbor in graph.get(seed, ()):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, 1))
                result.hop_distance[neighbor] = 1

    # Expand outward
    while queue:
        cls, dist = queue.popleft()
        if dist >= max_hops:
            continue
        for neighbor in graph.get(cls, ()):
            if neighbor not in visited:
                visited.add(neighbor)
                new_dist = dist + 1
                queue.append((neighbor, new_dist))
                result.hop_distance[neighbor] = new_dist

    return result


# --- Signal 2: Hub file co-reference ---

def compute_hub_signal(
    file_to_classes: dict[str, set[str]],
    seeds: set[str],
    min_known_refs: int = 3,
) -> HubResult:
    """Find hub files (files referencing 3+ known protos) and their unknown co-refs.

    A hub file is a source file that references `min_known_refs` or more known
    wire proto classes. Any unknown proto class also referenced from a hub file
    is likely wire-related.
    """
    result = HubResult()

    for file_path, classes in file_to_classes.items():
        known_in_file = classes & seeds
        if len(known_in_file) < min_known_refs:
            continue
        # This is a hub file — record unknown classes it references
        unknown_in_file = classes - seeds
        for cls in unknown_in_file:
            result.hub_file_count[cls] = result.hub_file_count.get(cls, 0) + 1
            result.hub_files.setdefault(cls, set()).add(file_path)

    return result


# --- Signal 3: Named package classification ---

def compute_package_signal(
    class_to_packages: dict[str, set[str]],
    seeds: set[str],
) -> PackageResult:
    """Classify proto classes based on the Java packages that reference them.

    Classes referenced ONLY from internal packages → INTERNAL.
    Classes referenced from wire-related packages → WIRE.
    """
    result = PackageResult()

    for cls, packages in class_to_packages.items():
        if cls in seeds:
            continue

        internal_matches: set[str] = set()
        wire_matches: set[str] = set()
        other_packages = False

        for pkg in packages:
            # Obfuscated default-package classes are neutral — skip them
            if pkg.startswith("defpackage.") or not pkg.startswith(("com.", "android.", "org.")):
                continue

            matched_internal = False
            for pat in _INTERNAL_PATTERNS:
                if pat.search(pkg):
                    internal_matches.add(pkg)
                    matched_internal = True
                    break
            if matched_internal:
                continue

            matched_wire = False
            for pat in _WIRE_PATTERNS:
                if pat.search(pkg):
                    wire_matches.add(pkg)
                    matched_wire = True
                    break
            if not matched_wire:
                other_packages = True

        # Only classify if we have a clear signal
        if wire_matches:
            result.classification[cls] = "WIRE"
            result.evidence[cls] = wire_matches
        elif internal_matches and not other_packages:
            # ONLY internal references, no other packages
            result.classification[cls] = "INTERNAL"
            result.evidence[cls] = internal_matches

    return result


# --- Signal 4: Structural features ---

def compute_structural_signal(
    universe: dict[str, ProtoInfo],
    seeds: set[str],
) -> StructuralResult:
    """Classify based on structural proto features."""
    result = StructuralResult()

    for cls, info in universe.items():
        if cls in seeds:
            continue

        features: set[str] = set()

        if not info.proto_syntax:
            features.add("empty_syntax")
        elif info.proto_syntax == "proto2":
            features.add("proto2")
        elif info.proto_syntax == "proto3":
            features.add("proto3")

        if info.field_count == 0:
            features.add("zero_fields")

        if info.sub_message_refs:
            features.add("has_sub_refs")

        if features:
            result.features[cls] = features

    return result
