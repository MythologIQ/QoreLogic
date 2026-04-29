"""Phase 49: defensive wiring tests for /qor-substantiate Step 6.5 badge
currency check (G-4).

Proximity-anchored on the Step 6.5 prose; paired with strip-and-fail
negative-path tests per Phase 46 doctrine.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "qor" / "skills" / "governance" / "qor-substantiate" / "SKILL.md"

STEP_HEADER = r"^### Step 6\.5: Documentation Currency Check\b"


def _read() -> str:
    return SKILL.read_text(encoding="utf-8")


def _proximity(body: str, header_pattern: str, phrase_pattern: str, span: int = 2500) -> bool:
    m = re.search(header_pattern, body, re.MULTILINE)
    if not m:
        return False
    window = body[m.end(): m.end() + span]
    return re.search(phrase_pattern, window, re.IGNORECASE | re.DOTALL) is not None


def _strip_section(body: str, header_pattern: str, span: int = 4000) -> str:
    m = re.search(header_pattern, body, re.MULTILINE)
    if not m:
        return body
    start = m.end()
    end = min(len(body), start + span)
    filler = "\n# stripped\n" * ((end - start) // 12 + 1)
    return body[:start] + filler[: end - start] + body[end:]


def test_substantiate_step_6_5_invokes_badge_currency_check():
    body = _read()
    assert _proximity(body, STEP_HEADER, r"badge_currency", span=2500), (
        "Step 6.5 must reference qor.scripts.badge_currency module"
    )
    assert _proximity(body, STEP_HEADER, r"feature.*breaking|breaking.*feature", span=2500), (
        "Step 6.5 must scope the check to feature/breaking change_class"
    )


def test_substantiate_step_6_5_negative_path():
    body = _read()
    mutated = _strip_section(body, STEP_HEADER)
    assert not _proximity(mutated, STEP_HEADER, r"badge_currency", span=2500)


def test_substantiate_aborts_seal_on_badge_mismatch_for_release_changes():
    body = _read()
    assert _proximity(body, STEP_HEADER, r"ABORT|aborts? seal", span=2500), (
        "Step 6.5 must specify ABORT semantics on mismatch (not WARN-only)"
    )


def test_substantiate_aborts_negative_path():
    body = _read()
    mutated = _strip_section(body, STEP_HEADER)
    assert not _proximity(mutated, STEP_HEADER, r"ABORT", span=2500)


def test_substantiate_badge_check_exempts_hotfix():
    body = _read()
    assert _proximity(body, STEP_HEADER, r"hotfix", span=2500), (
        "Step 6.5 must explicitly exempt hotfix change_class"
    )
    assert _proximity(body, STEP_HEADER, r"exempt|skip|except", span=2500), (
        "hotfix exemption must be named (not implicit)"
    )


def test_substantiate_hotfix_exemption_negative_path():
    body = _read()
    mutated = _strip_section(body, STEP_HEADER)
    assert not _proximity(mutated, STEP_HEADER, r"hotfix", span=2500)
