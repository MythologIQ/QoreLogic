"""Phase 27 Phase 1: every git tag has a CHANGELOG section and vice versa."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent
CHANGELOG = REPO / "CHANGELOG.md"
_VERSION_HEADER = re.compile(r"^## \[([0-9]+\.[0-9]+\.[0-9]+)\] -", re.MULTILINE)


def _git_tags() -> list[str]:
    """Return sorted SemVer-prefixed tags; skip non-SemVer historical tags."""
    try:
        result = subprocess.run(
            ["git", "tag", "-l", "v*"],
            check=True, capture_output=True, text=True, cwd=REPO,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("git not available; tag-coverage test skipped")
    tags = [t.strip() for t in result.stdout.splitlines() if t.strip()]
    # Keep only strict vMAJOR.MINOR.PATCH; drop migration/non-SemVer tags.
    return sorted(t for t in tags if re.match(r"^v[0-9]+\.[0-9]+\.[0-9]+$", t))


def _changelog_versions() -> set[str]:
    text = CHANGELOG.read_text(encoding="utf-8")
    return set(_VERSION_HEADER.findall(text))


def test_every_tag_has_changelog_section():
    tags = _git_tags()
    versions = _changelog_versions()
    missing_sections: list[str] = []
    for tag in tags:
        version = tag.lstrip("v")
        if version not in versions:
            missing_sections.append(tag)
    assert not missing_sections, (
        "Git tags without CHANGELOG entries:\n  " + "\n  ".join(missing_sections)
    )


def test_every_changelog_section_has_tag():
    tags = {t.lstrip("v") for t in _git_tags()}
    versions = _changelog_versions()
    orphan_sections = versions - tags
    assert not orphan_sections, (
        "CHANGELOG sections without git tags:\n  " + "\n  ".join(sorted(orphan_sections))
    )
