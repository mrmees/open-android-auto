from __future__ import annotations

from collections import Counter
from typing import Iterable, Literal

from analysis.tools.proto_stream_validator.decode import decode_payload
from analysis.tools.proto_stream_validator.descriptors import DescriptorBundle
from analysis.tools.proto_stream_validator.message_map import resolve_message_type

from .models import (
    ClassifiedRecord,
    FrequencyProfile,
    UnifiedRecord,
    WireWalkResult,
)
from .wire_walker import walk_proto


# Three-tier plausibility gate (07-CONTEXT.md decisions section).
TIER_A_CONTROL_PLANE = range(0x0000, 0x0020)
TIER_B_CHANNEL_SCOPED = range(0x8000, 0x8100)
TIER_B_EXTRA = frozenset({0xFFFF})

# msg_type=0 corroboration thresholds (07-CONTEXT.md gotcha #2, calibrated
# against the VW MIB3 OI 2026-04-06 histogram). Mic PCM frames have payload
# length ~200 bytes and frequency ~2,751; legitimate ServiceDiscoveryFeatureA
# control records have payload length 0 and frequency at most 1.
MSG_TYPE_ZERO_PAYLOAD_SIZE_THRESHOLD = 32
MSG_TYPE_ZERO_FREQ_THRESHOLD = 100

# Fallback frequency threshold when the empirical knee detector finds no
# clear knee in [2, 10]. Picked from the VW capture (see 07-RESEARCH.md
# Histogram Ground Truth) and validated against every DHU baseline.
DEFAULT_FREQUENCY_THRESHOLD = 3


Label = Literal[
    "standalone",
    "probable_first",
    "continuation_or_garbage",
    "reassembled",
    "unattributed",
]


def determine_tier(msg_type: int, in_descriptor_map: bool) -> Literal["A", "B", "C"]:
    """Three-tier plausibility gate. Tier A wins over the structural range:
    a known descriptor beats raw msg_type membership."""
    if in_descriptor_map:
        return "A"
    if (
        msg_type in TIER_A_CONTROL_PLANE
        or msg_type in TIER_B_CHANNEL_SCOPED
        or msg_type in TIER_B_EXTRA
    ):
        return "B"
    return "C"


def build_histogram(
    records: Iterable[UnifiedRecord],
) -> dict[tuple[int, str], int]:
    """Build a (msg_type, direction) → count histogram."""
    ctr: Counter[tuple[int, str]] = Counter()
    for r in records:
        ctr[(r.msg_type, r.direction)] += 1
    return dict(ctr)


def derive_frequency_threshold(
    histogram: dict[tuple[int, str], int],
) -> int:
    """Derive the empirical frequency threshold from the histogram distribution.

    Finds the "knee" of the per-freq-count curve: the smallest N >= 3 where
    the count of (msg_type, direction) pairs at freq == N drops below half
    the count at freq == N-1. Below the knee is repeated real signaling,
    near the knee is plausible-but-rare, and singletons (freq=1) are
    overwhelmingly fragment bytes.

    Why N starts at 3, not 2: freq=1 is dominated by Tier C garbage
    singletons (1,032 distinct values out of 1,046 records on the VW
    capture). The 1→2 transition almost always shows a steep drop because
    all the noise concentrates at freq=1; that drop is not the real
    signaling/garbage boundary. The true knee lives further into the
    distribution, where the count of distinct (msg_type, direction) pairs
    at freq N first becomes much smaller than at freq N-1 — i.e., the first
    place where the curve falls off after stabilising past the noise floor.

    Falls back to DEFAULT_FREQUENCY_THRESHOLD if no knee is found in [3, 10].
    """
    counts_by_freq: dict[int, int] = {}
    for freq in histogram.values():
        counts_by_freq[freq] = counts_by_freq.get(freq, 0) + 1
    # Start scanning from N=3 with prev = count at freq=2. Singletons are
    # treated as the noise floor and explicitly skipped for the knee search.
    prev = counts_by_freq.get(2, 0)
    for n in range(3, 11):
        curr = counts_by_freq.get(n, 0)
        if prev > 0 and curr < prev / 2:
            return n
        prev = curr
    return DEFAULT_FREQUENCY_THRESHOLD


def should_demote_msg_type_zero(record: UnifiedRecord, freq: int) -> bool:
    """msg_type=0 corroboration rule (07-CONTEXT.md gotcha #2).

    Demote a msg_type=0 record from Tier A to Tier C when its payload is
    larger than the legitimate ServiceDiscoveryFeatureA empty body. The
    rationale: real ServiceDiscoveryFeatureA control records have a 0-byte
    body, so any msg_type=0 record with > 32 bytes of payload cannot be
    that message and is overwhelmingly likely to be raw mic PCM bytes whose
    first two bytes happened to read as 0x0000 — verified on the VW MIB3 OI
    2026-04-06 capture (2,751 such records on channel 7, length ~200 bytes,
    16 kHz mono).

    The MSG_TYPE_ZERO_FREQ_THRESHOLD constant remains as a corroboration
    boost the report layer can cite: at session-scale, a freq >= 100 on
    msg_type=0 is a smoking-gun signature for a media stream rather than a
    sporadic singleton. Demotion fires on payload size alone because the
    size signal is already decisive — a non-empty msg_type=0 record cannot
    be ServiceDiscoveryFeatureA regardless of how many times it appears.
    """
    if record.msg_type != 0:
        return False
    if len(record.payload) > MSG_TYPE_ZERO_PAYLOAD_SIZE_THRESHOLD:
        return True
    # Belt-and-suspenders: if a small msg_type=0 record somehow appears at
    # mic-PCM-stream frequency, that's still corroborating evidence of a
    # media stream and not a singleton control message.
    if freq >= MSG_TYPE_ZERO_FREQ_THRESHOLD:
        return True
    return False


def _try_schema_decode(bundle: DescriptorBundle, record: UnifiedRecord) -> bool:
    """Tier A schema decode with rstrip-padding retry. Returns True iff the
    payload decoded under its resolved proto type."""
    try:
        fqn = resolve_message_type(
            direction=record.direction,
            channel_id=record.channel_id or 0,
            message_id=record.msg_type,
            message_name=None,
            service_type=record.service_type or None,
        )
    except KeyError:
        return False
    body = record.payload[2:]
    try:
        decode_payload(bundle, fqn, body)
        return True
    except ValueError:
        # Trailing zero padding retry — see 07-RESEARCH.md "Validator-style
        # adapter shim" and the wire walker's padding-bail rule.
        try:
            decode_payload(bundle, fqn, body.rstrip(b"\x00"))
            return True
        except ValueError:
            return False


def _is_in_descriptor_map(record: UnifiedRecord) -> bool:
    try:
        resolve_message_type(
            direction=record.direction,
            channel_id=record.channel_id or 0,
            message_id=record.msg_type,
            message_name=None,
            service_type=record.service_type or None,
        )
        return True
    except KeyError:
        return False


def classify_record(
    record: UnifiedRecord,
    tier: Literal["A", "B", "C"],
    wire_result: WireWalkResult | None,
    schema_ok: bool,
    freq: int,
    freq_threshold: int,
) -> tuple[Label, tuple[str, ...]]:
    """Map a (record, tier, walk evidence, freq) tuple to one of the three
    reachable atomic labels: standalone, probable_first, continuation_or_garbage.

    `reassembled` and `unattributed` are NEVER returned — they are reserved
    for the framing-hook capture work and the 07-02 attribution pipeline.
    """
    notes: list[str] = []
    if tier == "C":
        return ("continuation_or_garbage", ("tier_c",))

    walked_ok = wire_result is not None and (
        wire_result.clean_to_eob or wire_result.clean_with_padding
    )
    if schema_ok or walked_ok:
        if freq >= freq_threshold:
            return ("standalone", ("tier_" + tier.lower(),))
        # Low frequency — require a second positive signal
        notes.append("low_frequency")
        second_signal = schema_ok or (
            wire_result is not None and len(wire_result.fields) >= 2
        )
        if second_signal:
            notes.append("low_frequency_second_signal_passed")
            return ("standalone", tuple(notes))
        notes.append("low_frequency_second_signal_failed")
        return ("continuation_or_garbage", tuple(notes))

    if wire_result is not None and len(wire_result.fields) > 0:
        return ("probable_first", ("partial_walk",))
    return ("continuation_or_garbage", ("walk_failed",))


def classify_capture(
    records: list[UnifiedRecord],
    bundle: DescriptorBundle,
) -> tuple[list[ClassifiedRecord], FrequencyProfile]:
    """End-to-end per-capture classification pipeline.

    Order: histogram → derived threshold → per-record tier → msg_type=0
    demotion BEFORE any decode → schema decode (with rstrip-padding retry)
    → wire-walk fallback → atomic label assignment → demote note appending.
    """
    histogram = build_histogram(records)
    threshold = derive_frequency_threshold(histogram)
    profile = FrequencyProfile(
        threshold=threshold,
        histogram=histogram,
        source=(
            "empirical knee detection over per-session (msg_type, direction) "
            "histogram; falls back to "
            f"{DEFAULT_FREQUENCY_THRESHOLD} when no knee in [2,10]. "
            "Per 07-CONTEXT.md decisions section."
        ),
    )

    classified: list[ClassifiedRecord] = []
    for r in records:
        freq = histogram.get((r.msg_type, r.direction), 0)
        in_map = _is_in_descriptor_map(r)
        tier = determine_tier(r.msg_type, in_map)

        # msg_type=0 corroboration — demote BEFORE schema decode so we don't
        # waste time trying to decode mic PCM as ServiceDiscoveryFeatureA.
        demote_note: str | None = None
        if should_demote_msg_type_zero(r, freq):
            tier = "C"
            demote_note = "msg_type_zero_demoted_to_C"

        schema_ok = False
        wire_result: WireWalkResult | None = None
        if tier != "C":
            schema_ok = _try_schema_decode(bundle, r)
            if not schema_ok:
                wire_result = walk_proto(r.payload[2:])

        label, base_notes = classify_record(
            r, tier, wire_result, schema_ok, freq, threshold
        )
        notes = base_notes if demote_note is None else base_notes + (demote_note,)
        classified.append(
            ClassifiedRecord(
                record=r,
                tier=tier,
                label=label,
                walk_result=wire_result,
                schema_decoded=schema_ok,
                freq=freq,
                low_frequency=(freq < threshold),
                notes=notes,
            )
        )
    return classified, profile
