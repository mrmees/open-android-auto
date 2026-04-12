from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest


@pytest.fixture
def mock_oaa_tree(tmp_path: Path) -> Path:
    """Build a synthetic oaa/ subtree with all tier types, evidence, missing, and orphan cases."""
    oaa = tmp_path / "oaa"

    # --- audio: 1 bronze sidecar + 1 proto without sidecar (missing) ---
    audio = oaa / "audio"
    audio.mkdir(parents=True)

    (audio / "FakeAudioMessage.proto").write_text('syntax = "proto3";\n')
    (audio / "FakeAudioMessage.audit.yaml").write_text(dedent("""\
        proto_file: oaa/audio/FakeAudioMessage.proto
        confidence: bronze
        evidence:
          - type: apk_static
            source: jadx
            description: Static APK analysis
        last_updated: "2026-01-01"
    """))

    (audio / "OrphanlessProto.proto").write_text('syntax = "proto3";\n')
    # No sidecar for OrphanlessProto -> missing

    # --- video: 1 silver sidecar with evidence + oem_match_pending_gold + pending_platinum_evidence ---
    video = oaa / "video"
    video.mkdir(parents=True)

    (video / "FakeVideoMessage.proto").write_text('syntax = "proto3";\n')
    (video / "FakeVideoMessage.audit.yaml").write_text(dedent("""\
        proto_file: oaa/video/FakeVideoMessage.proto
        confidence: silver
        oem_match_pending_gold: true
        evidence:
          - type: cross_version
            source: cross_version_analysis
            description: Cross-version comparison
          - type: apk_static
            source: jadx
            description: Static APK analysis
        pending_platinum_evidence:
          - type: platinum_evidence
            source: vw_capture
            description: VW MIB3 OI capture evidence
        last_updated: "2026-01-01"
    """))

    # --- control: 1 retracted + 1 superseded ---
    control = oaa / "control"
    control.mkdir(parents=True)

    (control / "RetractedMessage.proto").write_text('syntax = "proto3";\n')
    (control / "RetractedMessage.audit.yaml").write_text(dedent("""\
        proto_file: oaa/control/RetractedMessage.proto
        confidence: retracted
        evidence:
          - type: apk_static
            source: jadx
            description: Static APK analysis
        last_updated: "2026-01-01"
    """))

    (control / "SupersededMessage.proto").write_text('syntax = "proto3";\n')
    (control / "SupersededMessage.audit.yaml").write_text(dedent("""\
        proto_file: oaa/control/SupersededMessage.proto
        confidence: superseded
        evidence:
          - type: deep_trace
            source: jadx_deep
            description: Deep trace analysis
        last_updated: "2026-01-01"
    """))

    # --- sensor: 1 orphan sidecar (no matching .proto) ---
    sensor = oaa / "sensor"
    sensor.mkdir(parents=True)

    (sensor / "OrphanSidecar.audit.yaml").write_text(dedent("""\
        proto_file: oaa/sensor/OrphanSidecar.proto
        confidence: bronze
        evidence:
          - type: apk_static
            source: jadx
            description: Static APK analysis
        last_updated: "2026-01-01"
    """))
    # No OrphanSidecar.proto -> orphan

    return tmp_path
