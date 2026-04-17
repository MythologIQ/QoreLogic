"""Phase 27 Phase 2: changelog_stamp pure-function tests."""
from __future__ import annotations

import pytest


_UNRELEASED_WITH_BULLETS = """# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New tone tier selector
- Stamp automation

## [0.17.0] - 2026-04-17

### Added
- Earlier release entry.
"""

_UNRELEASED_EMPTY = """# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.17.0] - 2026-04-17

### Added
- Earlier release entry.
"""

_MISSING_UNRELEASED = """# Changelog

## [0.17.0] - 2026-04-17

### Added
- Earlier release entry.
"""


def test_stamp_unreleased_renames_and_inserts_fresh():
    from qor.scripts.changelog_stamp import stamp_unreleased
    out = stamp_unreleased(_UNRELEASED_WITH_BULLETS, "0.18.0", "2026-05-01")
    assert "## [Unreleased]" in out
    assert "## [0.18.0] - 2026-05-01" in out
    # The new version section contains the bullets that were under Unreleased.
    assert "New tone tier selector" in out
    assert "Stamp automation" in out
    # Older versions untouched.
    assert "## [0.17.0] - 2026-04-17" in out


def test_stamp_fresh_unreleased_empty_after_rename():
    from qor.scripts.changelog_stamp import stamp_unreleased
    out = stamp_unreleased(_UNRELEASED_WITH_BULLETS, "0.18.0", "2026-05-01")
    # The first Unreleased section should have no bullets between its header
    # and the newly-inserted 0.18.0 header.
    unreleased_idx = out.index("## [Unreleased]")
    version_idx = out.index("## [0.18.0]")
    between = out[unreleased_idx:version_idx]
    assert "- New tone tier selector" not in between
    assert "- Stamp automation" not in between


def test_stamp_empty_unreleased_raises():
    from qor.scripts.changelog_stamp import stamp_unreleased
    with pytest.raises(ValueError, match="empty|no bullets"):
        stamp_unreleased(_UNRELEASED_EMPTY, "0.18.0", "2026-05-01")


def test_stamp_missing_unreleased_raises():
    from qor.scripts.changelog_stamp import stamp_unreleased
    with pytest.raises(ValueError, match="Unreleased"):
        stamp_unreleased(_MISSING_UNRELEASED, "0.18.0", "2026-05-01")


def test_stamp_version_collision_raises():
    from qor.scripts.changelog_stamp import stamp_unreleased
    with pytest.raises(ValueError, match="0\\.17\\.0.*already"):
        stamp_unreleased(_UNRELEASED_WITH_BULLETS, "0.17.0", "2026-05-01")


def test_stamp_invalid_version_raises():
    from qor.scripts.changelog_stamp import stamp_unreleased
    with pytest.raises(ValueError, match="SemVer|version"):
        stamp_unreleased(_UNRELEASED_WITH_BULLETS, "0.18", "2026-05-01")


def test_stamp_invalid_date_raises():
    from qor.scripts.changelog_stamp import stamp_unreleased
    with pytest.raises(ValueError, match="date"):
        stamp_unreleased(_UNRELEASED_WITH_BULLETS, "0.18.0", "May 1 2026")


def test_apply_stamp_writes_atomically(tmp_path):
    from qor.scripts.changelog_stamp import apply_stamp
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text(_UNRELEASED_WITH_BULLETS, encoding="utf-8")
    result = apply_stamp(cl, "0.18.0", "2026-05-01")
    assert result == cl
    stamped = cl.read_text(encoding="utf-8")
    assert "## [0.18.0] - 2026-05-01" in stamped
    assert "## [Unreleased]" in stamped


def test_apply_stamp_missing_file_raises(tmp_path):
    from qor.scripts.changelog_stamp import apply_stamp
    with pytest.raises(FileNotFoundError):
        apply_stamp(tmp_path / "nope.md", "0.18.0", "2026-05-01")
