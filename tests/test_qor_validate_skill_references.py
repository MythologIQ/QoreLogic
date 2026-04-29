"""Phase 41 (issue #13): lint the shipped qor-validate SKILL for stale references.

The pre-Phase-41 SKILL.md pointed at `.claude/commands/scripts/validate-ledger.py`,
a path that `qorlogic install` does not produce. Canonical references are
`qor.scripts.ledger_hash` (module) and `qorlogic verify-ledger` (CLI).
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

STALE_PATH = ".claude/commands/scripts/validate-ledger.py"
CANONICAL_MARKERS = ("qor/scripts/ledger_hash.py", "qor.scripts.ledger_hash", "qor-logic verify-ledger")

SOURCE_SKILL = REPO_ROOT / "qor" / "skills" / "governance" / "qor-validate" / "SKILL.md"
VARIANT_DIST_SKILLS = list(
    (REPO_ROOT / "qor" / "dist" / "variants").glob("*/skills/qor-validate/SKILL.md")
)


def _all_skill_paths() -> list[Path]:
    paths = [SOURCE_SKILL, *VARIANT_DIST_SKILLS]
    return [p for p in paths if p.exists()]


def test_qor_validate_skill_has_no_stale_path():
    """Neither the source SKILL nor any shipped variant may contain the pre-Phase-41 stub path."""
    paths = _all_skill_paths()
    assert SOURCE_SKILL in paths, "source qor-validate SKILL.md missing"
    for p in paths:
        text = p.read_text(encoding="utf-8")
        assert STALE_PATH not in text, f"{p.relative_to(REPO_ROOT)} still references stale {STALE_PATH!r}"


def test_qor_validate_skill_references_canonical_path():
    """Each SKILL must reference the canonical module or CLI entrypoint."""
    paths = _all_skill_paths()
    for p in paths:
        text = p.read_text(encoding="utf-8")
        assert any(m in text for m in CANONICAL_MARKERS), (
            f"{p.relative_to(REPO_ROOT)} does not reference any canonical marker "
            f"(expected one of {CANONICAL_MARKERS})"
        )
