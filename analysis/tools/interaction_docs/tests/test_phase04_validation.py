"""
Phase 04 — Connection Lifecycle: Nyquist validation tests.

Gap coverage:
  gap-1: All 5 interaction docs (01-05) exist on disk
  gap-2: Confidence badge audit YAML links resolve to real files
  gap-3: Document chain links intact (01->02->03->04->05)
  gap-4: MVC checklist ("Minimum Viable Connection") exists in doc 04
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
DOCS_DIR = REPO_ROOT / "docs" / "interactions"

# All five interaction docs that must exist after phase 04
INTERACTION_DOCS = [
    "01-transport-setup.md",
    "02-version-ssl-auth.md",
    "03-service-discovery.md",
    "04-channel-lifecycle.md",
    "05-session-maintenance-teardown.md",
]

# Forward-chain: each doc must reference the next one
DOC_CHAIN = [
    ("01-transport-setup.md", "02-version-ssl-auth"),
    ("02-version-ssl-auth.md", "03-service-discovery"),
    ("03-service-discovery.md", "04-channel-lifecycle"),
    ("04-channel-lifecycle.md", "05-session-maintenance-teardown"),
]

# Regex: captures relative path in markdown link targeting a .audit.yaml file
# Matches: [SomeName.audit.yaml](../../oaa/path/SomeName.audit.yaml)
_AUDIT_LINK_RE = re.compile(r'\[([^\]]+\.audit\.yaml)\]\(([^)]+\.audit\.yaml)\)')


# ---------------------------------------------------------------------------
# Gap 1 — All 5 interaction docs exist
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("doc_name", INTERACTION_DOCS)
def test_interaction_doc_exists(doc_name):
    """All 5 connection lifecycle interaction docs must be present on disk."""
    doc_path = DOCS_DIR / doc_name
    assert doc_path.exists(), (
        f"Interaction doc missing: {doc_path}. "
        f"Phase 04 must produce all five docs (01-05) per DOCS-01 requirement."
    )


# ---------------------------------------------------------------------------
# Gap 2 — Confidence badge audit YAML links resolve to real files
# ---------------------------------------------------------------------------

def _collect_audit_yaml_refs(doc_name: str):
    """Return list of (link_text, relative_path, absolute_path) for all audit.yaml links in doc."""
    doc_path = DOCS_DIR / doc_name
    if not doc_path.exists():
        return []
    text = doc_path.read_text(encoding="utf-8")
    results = []
    for match in _AUDIT_LINK_RE.finditer(text):
        link_text = match.group(1)
        rel_path = match.group(2)
        # Resolve relative to the docs/interactions/ directory
        abs_path = (DOCS_DIR / rel_path).resolve()
        results.append((link_text, rel_path, abs_path))
    return results


@pytest.mark.parametrize("doc_name", INTERACTION_DOCS)
def test_audit_yaml_links_resolve(doc_name):
    """Every .audit.yaml link in a confidence badge must point to a file that exists."""
    refs = _collect_audit_yaml_refs(doc_name)

    # A doc with zero audit.yaml links is suspicious given phase 04 requirements,
    # but only fail if the doc itself exists (gap-1 covers missing docs).
    doc_path = DOCS_DIR / doc_name
    if not doc_path.exists():
        pytest.skip(f"{doc_name} does not exist — covered by gap-1 test.")

    missing = [
        (link_text, rel_path, str(abs_path))
        for link_text, rel_path, abs_path in refs
        if not abs_path.exists()
    ]

    assert not missing, (
        f"Broken audit.yaml links in {doc_name}:\n"
        + "\n".join(
            f"  [{lt}]({rp}) -> {ap} (NOT FOUND)"
            for lt, rp, ap in missing
        )
    )


@pytest.mark.parametrize("doc_name", INTERACTION_DOCS)
def test_doc_has_at_least_one_audit_yaml_link(doc_name):
    """Each enhanced doc must contain at least one audit.yaml confidence badge link."""
    doc_path = DOCS_DIR / doc_name
    if not doc_path.exists():
        pytest.skip(f"{doc_name} does not exist — covered by gap-1 test.")

    refs = _collect_audit_yaml_refs(doc_name)
    assert len(refs) > 0, (
        f"{doc_name} contains no audit.yaml confidence badge links. "
        "Phase 04 requires all docs to have inline confidence badges (DOCS-01)."
    )


# ---------------------------------------------------------------------------
# Gap 3 — Document chain links intact (01->02->03->04->05)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("source_doc,target_slug", DOC_CHAIN)
def test_document_chain_link_exists(source_doc, target_slug):
    """Each doc must contain a link referencing the next doc in the chain."""
    source_path = DOCS_DIR / source_doc
    if not source_path.exists():
        pytest.skip(f"{source_doc} does not exist — covered by gap-1 test.")

    text = source_path.read_text(encoding="utf-8")
    assert target_slug in text, (
        f"{source_doc} must contain a forward reference to '{target_slug}' "
        f"to maintain the connection lifecycle document chain (DOCS-01). "
        f"The link was not found anywhere in the document."
    )


# ---------------------------------------------------------------------------
# Gap 4 — MVC checklist in doc 04
# ---------------------------------------------------------------------------

def test_minimum_viable_connection_checklist_in_doc04():
    """Doc 04 must contain the Minimum Viable Connection checklist."""
    doc_path = DOCS_DIR / "04-channel-lifecycle.md"
    if not doc_path.exists():
        pytest.skip("04-channel-lifecycle.md does not exist — covered by gap-1 test.")

    text = doc_path.read_text(encoding="utf-8")
    found_mvc = "Minimum Viable Connection" in text or "MVC" in text
    assert found_mvc, (
        "04-channel-lifecycle.md must contain a 'Minimum Viable Connection' checklist. "
        "Per 04-01-PLAN.md: 'Doc 04 contains a Minimum Viable Connection checklist "
        "summarizing all steps from transport through channel open' (DOCS-01)."
    )


def test_minimum_viable_connection_is_section_heading():
    """The MVC checklist must be a proper section heading, not just inline mention."""
    doc_path = DOCS_DIR / "04-channel-lifecycle.md"
    if not doc_path.exists():
        pytest.skip("04-channel-lifecycle.md does not exist — covered by gap-1 test.")

    text = doc_path.read_text(encoding="utf-8")
    # Look for markdown heading containing "Minimum Viable Connection"
    heading_re = re.compile(r'^#{1,6}\s+.*Minimum Viable Connection', re.MULTILINE)
    assert heading_re.search(text), (
        "04-channel-lifecycle.md must have a markdown heading containing "
        "'Minimum Viable Connection', not just a mention in prose. "
        "The plan specifies it as a ## section."
    )
