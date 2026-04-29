"""Phase 48: doctrine §138 must cover both qor/scripts/ and qor/reliability/.

Pre-Phase-48 wording covered only qor/reliability/. The same `python -m`
discipline applies to both dirs; lock the symmetric form.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCTRINE = REPO_ROOT / "qor" / "references" / "doctrine-governance-enforcement.md"


def _read() -> str:
    return DOCTRINE.read_text(encoding="utf-8")


def _section_138_window(body: str, span: int = 3000) -> str:
    # §138 is the second numbered rule under a known surrounding section. The
    # rule starts with "2. **Snake_case ...**" (or similar bold lead). Locate it
    # by the unique phrase "Snake_case" + "python -m" — the rule's signature.
    m = re.search(r"^\d+\.\s+\*\*Snake_case", body, re.MULTILINE)
    if not m:
        return ""
    return body[m.start(): m.start() + span]


def test_section_138_covers_both_scripts_and_reliability():
    body = _read()
    window = _section_138_window(body)
    assert window, "doctrine must contain a 'Snake_case' rule (§138)"
    assert "qor/reliability/" in window, "§138 must mention qor/reliability/"
    assert "qor/scripts/" in window, "§138 must mention qor/scripts/"
    assert "python -m qor.scripts." in window, (
        "§138 must specify the canonical 'python -m qor.scripts.<name>' invocation"
    )
    assert "python -m qor.reliability." in window, (
        "§138 must specify the canonical 'python -m qor.reliability.<name>' invocation"
    )


def test_section_138_negative_path_strip():
    body = _read()
    # Mutate by removing the Snake_case lead from the doctrine in-memory.
    mutated = re.sub(
        r"^\d+\.\s+\*\*Snake_case.*?(?=^\d+\.\s+\*\*|\Z)",
        "(rule stripped)\n",
        body,
        count=1,
        flags=re.MULTILINE | re.DOTALL,
    )
    window = _section_138_window(mutated)
    # After strip, the Snake_case lead is gone so window is empty / fails.
    assert not window or "qor/reliability/" not in window, (
        "negative path: stripped doctrine must not satisfy the positive check"
    )


def test_doctrine_line_92_uses_module_form():
    """Prose example at ~line 92 cites 'manual session rotation'. The example
    must use module form, not path form."""
    body = _read()
    # Find the prose example mentioning 'session rotation' near 'qor/scripts/session'.
    m = re.search(r"manual session rotation.*?qor[./]scripts[./]session.*?[`\)]", body, re.DOTALL | re.IGNORECASE)
    assert m, "doctrine must contain a 'manual session rotation' prose example"
    citation = m.group(0)
    assert "python -m qor.scripts.session" in citation, (
        f"session-rotation prose example must use module form 'python -m qor.scripts.session'; "
        f"found: {citation!r}"
    )
    assert "python qor/scripts/session.py" not in citation, (
        f"session-rotation prose example must not use path form; found: {citation!r}"
    )
