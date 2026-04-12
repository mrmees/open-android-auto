from __future__ import annotations

from analysis.tools.coverage_dashboard.scanner import ScanResult


def render_markdown(result: ScanResult) -> str:
    """Format ScanResult into markdown report with 6 locked sections."""
    raise NotImplementedError("render_markdown not yet implemented")


def render_json(result: ScanResult) -> str:
    """Format ScanResult into JSON sidecar with top-level keys matching sections."""
    raise NotImplementedError("render_json not yet implemented")
