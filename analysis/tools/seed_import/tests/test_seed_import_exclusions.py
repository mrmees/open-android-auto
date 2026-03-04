"""
TOOL-01 gap: verify the exclusion filtering logic in the seed import pipeline.

The import pipeline must exclude telemetry/noise classes (patterns defined in
run._is_excluded). Tests verify:
- Known telemetry/noise class names ARE excluded
- Known seed proto classes (e.g., NightMode, GearData) are NOT excluded
- The zyd utility class is excluded

Uses the _is_excluded function from run.py directly to test the filter logic.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
# Ensure the repo root is importable
sys.path.insert(0, str(REPO_ROOT))

from analysis.tools.proto_schema_validator.models import ProtoMapping
from analysis.tools.seed_import.run import _is_excluded


def _make_mapping(message: str, fqn: str = "", apk_classes: dict | None = None, confidence: str = "proto_comment") -> ProtoMapping:
    """Helper to create a ProtoMapping for testing exclusion logic."""
    return ProtoMapping(
        proto_message=message,
        proto_file=f"oaa/sensor/{message}.proto",
        proto_fqn=fqn or f"oaa.proto.data.{message}",
        apk_classes=apk_classes or {"16.1": "abc"},
        confidence=confidence,
    )


# ---------------------------------------------------------------------------
# Telemetry/noise classes that MUST be excluded
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("message,fqn", [
    ("TelemetryEvent", "oaa.proto.data.TelemetryEvent"),
    ("AnalyticsEvent", "oaa.proto.data.AnalyticsEvent"),
    ("FeedbackRequest", "oaa.proto.data.FeedbackRequest"),
    ("UserSurveyData", "oaa.proto.data.UserSurveyData"),
    ("CrashReport", "oaa.proto.data.CrashReport"),
    ("HatsServiceEvent", "oaa.proto.data.HatsServiceEvent"),
    ("ConnectivityEvent", "oaa.proto.data.ConnectivityEvent"),
    ("AudioDiagnosticsData", "oaa.proto.data.AudioDiagnosticsData"),
    ("DapperSpanData", "oaa.proto.data.DapperSpanData"),
    ("FailureInjectionConfig", "oaa.proto.data.FailureInjectionConfig"),
    ("AssistantConnectionInfo", "oaa.proto.data.AssistantConnectionInfo"),
    ("FirebaseEvent", "oaa.proto.data.FirebaseEvent"),
    ("BugReportData", "oaa.proto.data.BugReportData"),
    ("CarSetupServiceRequest", "oaa.proto.data.CarSetupServiceRequest"),
    ("PerformancePrimesMetric", "performance.primes.PerformancePrimesMetric"),
])
def test_telemetry_noise_class_is_excluded(message: str, fqn: str):
    """Telemetry and noise class names must be filtered out by the import pipeline."""
    mapping = _make_mapping(message, fqn)
    assert _is_excluded(mapping), (
        f"Expected '{message}' (fqn='{fqn}') to be excluded as telemetry/noise, "
        f"but _is_excluded() returned False. "
        f"Check _INTERNAL_PATTERNS and _TELEMETRY_ROOT_PATTERNS in run.py."
    )


# ---------------------------------------------------------------------------
# Seed classes that must NOT be excluded
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("message,fqn", [
    ("NightMode", "oaa.proto.data.NightMode"),
    ("GearData", "oaa.proto.data.GearData"),
    ("SpeedData", "oaa.proto.data.SpeedData"),
    ("FuelLevelData", "oaa.proto.data.FuelLevelData"),
    ("LocationData", "oaa.proto.data.LocationData"),
    ("AccelData", "oaa.proto.data.AccelData"),
    ("CompassData", "oaa.proto.data.CompassData"),
    ("AudioConfig", "oaa.proto.data.AudioConfig"),
    ("NavigationStatus", "oaa.proto.data.NavigationStatus"),
    ("MediaPlaybackData", "oaa.proto.data.MediaPlaybackData"),
])
def test_seed_class_is_not_excluded(message: str, fqn: str):
    """Known seed proto classes must pass the exclusion filter (not be excluded)."""
    mapping = _make_mapping(message, fqn)
    assert not _is_excluded(mapping), (
        f"Expected '{message}' (fqn='{fqn}') to NOT be excluded, "
        f"but _is_excluded() returned True. "
        f"This class is a legitimate seed mapping that must be imported."
    )


# ---------------------------------------------------------------------------
# Utility class exclusion
# ---------------------------------------------------------------------------

def test_zyd_utility_class_is_excluded():
    """The zyd class (PingConfiguration — generic Duration) must be excluded as a utility class."""
    mapping = ProtoMapping(
        proto_message="PingConfiguration",
        proto_file="oaa/common/PingConfigurationData.proto",
        proto_fqn="oaa.proto.data.PingConfiguration",
        apk_classes={"16.1": "zyd"},
        confidence="proto_comment",
    )
    assert _is_excluded(mapping), (
        "Expected PingConfiguration with APK class 'zyd' to be excluded as a utility class. "
        "Check _UTILITY_EXCLUSIONS in run.py."
    )


def test_non_utility_class_with_similar_name_not_excluded():
    """A class that happens to have a utility-like APK name but doesn't match exactly is not excluded."""
    mapping = ProtoMapping(
        proto_message="NightMode",
        proto_file="oaa/sensor/NightModeData.proto",
        proto_fqn="oaa.proto.data.NightMode",
        apk_classes={"16.1": "vzi"},  # real NightMode APK class — not 'zyd'
        confidence="enum_match",
    )
    assert not _is_excluded(mapping), (
        "NightMode with a non-utility APK class should not be excluded."
    )
