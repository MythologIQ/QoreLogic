"""Phase 27 Phase 1: Keep-a-Changelog structural lint."""
from __future__ import annotations

import re
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
CHANGELOG = REPO / "CHANGELOG.md"
FIXTURES = Path(__file__).parent / "fixtures"

_VERSION_HEADER = re.compile(r"^## \[(?P<ver>[0-9]+\.[0-9]+\.[0-9]+)\] - (?P<date>\S.*)$")
_SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
_DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_SUBSECTION = re.compile(r"^### (?P<label>\S[^\n]*)$")
_ALLOWED_SUBSECTIONS = frozenset(
    {"Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"}
)


def _check(text: str) -> list[str]:
    errors: list[str] = []
    if not text.startswith("# Changelog\n\n"):
        errors.append("missing canonical header '# Changelog\\n\\n' at start")
    if "[Keep a Changelog]" not in text:
        errors.append("missing 'Keep a Changelog' link in intro")
    if "[Semantic Versioning]" not in text:
        errors.append("missing 'Semantic Versioning' link in intro")
    unreleased_count = text.count("## [Unreleased]")
    if unreleased_count != 1:
        errors.append(f"expected exactly one '## [Unreleased]' section, found {unreleased_count}")

    versions: list[tuple[str, int]] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        m = _VERSION_HEADER.match(line)
        if m:
            ver, date = m.group("ver"), m.group("date").strip()
            if not _SEMVER.match(ver):
                errors.append(f"line {idx+1}: version {ver!r} not SemVer")
            if not _DATE.match(date):
                errors.append(f"line {idx+1}: date {date!r} not YYYY-MM-DD")
            versions.append((ver, idx))

    # Unreleased must precede every versioned section.
    unreleased_line = next(
        (i for i, ln in enumerate(lines) if ln.strip() == "## [Unreleased]"), None
    )
    if unreleased_line is not None:
        for ver, pos in versions:
            if pos < unreleased_line:
                errors.append(f"version {ver} appears before Unreleased")

    # Versions ordered newest-first (lexicographic on SemVer tuple).
    def _key(v: str) -> tuple[int, ...]:
        return tuple(int(p) for p in v.split("."))

    for (a, _), (b, _) in zip(versions, versions[1:]):
        if _key(a) < _key(b):
            errors.append(f"version {a} listed before newer {b} (expected newest-first)")

    # Subsection headers must be in allowed set.
    for idx, line in enumerate(lines):
        m = _SUBSECTION.match(line)
        if m and m.group("label") not in _ALLOWED_SUBSECTIONS:
            errors.append(
                f"line {idx+1}: disallowed subsection {m.group('label')!r}; "
                f"allowed: {sorted(_ALLOWED_SUBSECTIONS)}"
            )
    return errors


def test_changelog_file_exists():
    assert CHANGELOG.exists(), f"missing repo-root CHANGELOG: {CHANGELOG}"


def test_canonical_changelog_passes_format_lint():
    errors = _check(CHANGELOG.read_text(encoding="utf-8"))
    assert not errors, "Changelog format violations:\n  " + "\n  ".join(errors)


def test_fixture_good_passes():
    errors = _check((FIXTURES / "changelog_good.md").read_text(encoding="utf-8"))
    assert errors == []


def test_fixture_bad_date_fails():
    errors = _check((FIXTURES / "changelog_bad_date.md").read_text(encoding="utf-8"))
    assert any("not YYYY-MM-DD" in e for e in errors), errors


def test_fixture_bad_category_fails():
    errors = _check((FIXTURES / "changelog_bad_category.md").read_text(encoding="utf-8"))
    assert any("disallowed subsection" in e for e in errors), errors
