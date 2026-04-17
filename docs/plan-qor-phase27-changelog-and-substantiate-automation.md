# Plan: Phase 27 -- CHANGELOG.md + substantiate-time automation

**change_class**: feature

## Open Questions

- **Date source for backfill**: `git log -1 --format=%ad --date=short <tag>` (commit date) vs ledger entry timestamp. Plan uses **commit date** because the ledger timestamp was inconsistently recorded in early entries and the git tag date is the canonical "shipped at" moment. Adjust if a different source is authoritative.
- **Keep a Changelog categories to use**: plan uses the standard six (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`). `Deprecated` and `Removed` are likely unused for most past versions; plan only emits sections that have at least one bullet.
- **Historical Phase 23 gap**: v0.14.0 shipped without a ledger seal (the gap documented by Entry #84 BACKFILL). Plan treats v0.14.0 as a first-class CHANGELOG entry derived from the git commit + plan file + backfill narrative. No "missing" annotation in the CHANGELOG body itself; PyPI readers see a normal entry.

## Goal

Two capabilities:

1. **Author `CHANGELOG.md` with full history (v0.3.0 -> v0.17.0)**. Keep-a-Changelog format. Per-version sections derived from seal ledger entries + plan change_class + commit messages. Hand-authored (not parser-generated) for the one-time backfill to avoid over-engineering a one-shot operation.
2. **Automate forward entries via `/qor-substantiate`**. New pure module `qor/scripts/changelog_stamp.py` provides `stamp_unreleased(changelog_text, version, date) -> text` that renames the `## [Unreleased]` section to `## [X.Y.Z] - YYYY-MM-DD` and inserts a fresh empty `[Unreleased]` above it. Authors populate `Unreleased` bullets during `/qor-implement`; seal stamps the version mechanically.

## Design summary

- **CHANGELOG is a user-facing narrative, ledger is an auditor-facing evidence chain.** Two artifacts, two audiences. The CHANGELOG references the ledger (Merkle seal hash per version) but does not embed it or duplicate it. Format: Keep a Changelog 1.1.0 + SemVer.
- **Backfill is hand-authored, not auto-generated.** A one-time task produces ~15 version sections from existing material (ledger seal entries, plan change_class declarations, commit messages). Parser automation for the backfill would couple CHANGELOG format to ledger markup, a Simple-Made-Easy anti-pattern; the backfill runs once.
- **Forward automation is minimal.** `changelog_stamp.py` does one thing: rename the `Unreleased` header on seal. That's it. No content generation. Authors are responsible for populating `Unreleased` during implementation phases, matching upstream Keep-a-Changelog convention.
- **Enforcement is tag coverage + structure.** Lint test asserts every git tag has a CHANGELOG section; a second lint validates Keep-a-Changelog structure (required headers, date format, section ordering). Missing tag entry fails CI on future releases.
- **Doctrine cites policy, not mechanism.** `doctrine-changelog.md` states the rule (every release has a CHANGELOG section, bullets describe user-facing changes not implementation details, security-relevant changes get the `Security` category). The mechanism (stamp + lint) lives in code.

## CI validation

```
pytest -q
```

New lint tests run in the default pytest suite. No new dependencies introduced.

---

## Phase 1: Author CHANGELOG.md with v0.3.0 -> v0.17.0 backfill

### Affected files

- `tests/test_changelog_format.py` (new) -- Keep-a-Changelog structural lint
- `tests/test_changelog_tag_coverage.py` (new) -- every git tag has a section; no orphan sections
- `CHANGELOG.md` (new) -- repo-root CHANGELOG with full history

### Unit Tests (write FIRST)

- `tests/test_changelog_format.py`
  - **Parser policy**: plain string + `re` only. No YAML. No eval.
  - Asserts `CHANGELOG.md` exists at repo root.
  - Asserts header matches `# Changelog\n\n`.
  - Asserts the `Keep a Changelog` link is present in the intro.
  - Asserts the `Semantic Versioning` link is present in the intro.
  - Asserts exactly one `## [Unreleased]` section exists (canonical header).
  - For every `## [X.Y.Z] - YYYY-MM-DD` header: version matches SemVer regex, date matches `\d{4}-\d{2}-\d{2}`.
  - Version order: sections appear newest-first (v0.17.0 before v0.16.0, etc.). `Unreleased` is first.
  - Allowed subsection headers: `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, `### Security`. Any `###` that is not in this set fails.
  - Within each version section: each non-header line is either blank or begins with `- ` (bullet).
  - Fixture-based positive controls: `tests/fixtures/changelog_good.md` passes; `tests/fixtures/changelog_bad_date.md` + `tests/fixtures/changelog_bad_category.md` both fail with clear per-rule errors.
- `tests/test_changelog_tag_coverage.py`
  - Walks `git tag -l "v*"` output (captured via `subprocess.run` with `check=True`, argv list form -- no `shell=True` per SG A03 discipline).
  - For each tag, asserts the CHANGELOG has a corresponding `## [X.Y.Z] -` section.
  - For each CHANGELOG version section, asserts a corresponding git tag exists.
  - Skips `pre-qor-migration` (non-SemVer historical tag).
  - Failure message names every tag without a CHANGELOG entry AND every CHANGELOG entry without a tag.

### Changes

- `CHANGELOG.md` (at repo root):
  - Header: `# Changelog`, intro paragraph with Keep-a-Changelog + SemVer links.
  - `## [Unreleased]` section, empty (will be populated during Phase 27 implementation itself; Phase 28+ populate during their own implement phases).
  - Per-version sections for v0.17.0, v0.16.0, v0.15.0, v0.14.0, v0.13.0, v0.12.0, v0.11.0, v0.10.0, v0.9.0, v0.8.0, v0.7.0, v0.6.0, v0.5.0, v0.4.0, v0.3.0 in that order (newest first).
  - Each section: 2-5 bullets under `### Added` / `### Changed` / `### Fixed` / `### Security` as applicable. Bullets describe USER-facing changes (new commands, behavior changes, security posture shifts). NOT internal refactors or ledger entry numbers.
  - Content is derived from ledger seal entries (`### Entry #N: SESSION SEAL`), plan files (`docs/plan-qor-phase*.md` for each phase's goal), and git commit messages for that tag. Authored by hand; no parser involvement.
  - Footer (after the oldest version): one-line pointer `Earlier versions (< v0.3.0) shipped internally before the repo went public; see git history for migration pedigree.`
- `tests/fixtures/changelog_good.md`, `tests/fixtures/changelog_bad_date.md`, `tests/fixtures/changelog_bad_category.md`:
  - Minimal fixtures (~20 lines each). The good one passes the format lint; the two bad ones violate exactly one rule each (date format, disallowed subsection header).

---

## Phase 2: `changelog_stamp.py` + `/qor-substantiate` wiring

### Affected files

- `tests/test_changelog_stamp.py` (new) -- pure-function unit tests for the stamp module
- `qor/scripts/changelog_stamp.py` (new) -- single-purpose pure module
- `qor/skills/governance/qor-substantiate/SKILL.md` -- add Step 7.6 (or similar) calling the stamp after the version bump

### Unit Tests (write FIRST)

- `tests/test_changelog_stamp.py`
  - `stamp_unreleased(text, version="0.18.0", date="2026-05-01")` takes a CHANGELOG fragment with `## [Unreleased]` and a non-empty body, returns a new text where:
    - `## [Unreleased]` is followed by a freshly-empty section.
    - Below the new Unreleased section, a `## [0.18.0] - 2026-05-01` header appears with the body that was previously under Unreleased.
    - The rest of the CHANGELOG (older versions) is unchanged byte-for-byte.
  - Idempotent on already-stamped CHANGELOG: if the target version already has a section, raise `ValueError` naming the collision (never silently overwrite).
  - Empty-Unreleased edge: `stamp_unreleased(text, ...)` where Unreleased has no bullets returns unchanged text with a warning string (no new empty version entry).
  - Missing-Unreleased edge: raises `ValueError` naming the expected header.
  - SemVer validation: invalid version string raises `ValueError` citing the regex.
  - Date validation: invalid date string raises `ValueError`.
  - `stamp_unreleased` is pure -- no file I/O. A separate wrapper `apply_stamp(path, version, date)` handles the read/write, tested in the integration test (Phase 3).

### Changes

- `qor/scripts/changelog_stamp.py`:
  - Module-level constants `_SEMVER_RE`, `_DATE_RE`, `_UNRELEASED_HEADER = "## [Unreleased]"`, `_NEW_EMPTY_UNRELEASED = "## [Unreleased]\n\n"`.
  - `validate_version(version)` -- raises on non-SemVer.
  - `validate_date(date)` -- raises on non-ISO.
  - `stamp_unreleased(text, version, date) -> str` -- pure, <30 lines, uses plain string slicing to locate headers (no regex-based structural parsing).
  - `apply_stamp(path, version, date, *, dry_run=False) -> str` -- reads, stamps, writes atomically (temp-file + rename), returns the written path. Raises if path missing.
- `qor/skills/governance/qor-substantiate/SKILL.md`:
  - New step "Step 7.6: Stamp CHANGELOG" invoking `qor/scripts/changelog_stamp.py apply_stamp(CHANGELOG.md, new_version, today_iso)`. Runs AFTER Step 7.5 version bump, BEFORE Step 8 cleanup. On `ValueError` (missing Unreleased, empty Unreleased, version collision), PAUSE with a clear operator message; do not silently ship an unchanged CHANGELOG.
  - **Step 9.5 (Stage Artifacts)** auto-stage list updated: append `git add CHANGELOG.md` to the staging block. Without this, the stamped CHANGELOG is not committed by the seal ceremony -- the stamp modifies the file in place but the operator's `git add` block must also pick it up.

---

## Phase 3: Lint integration + doctrine

### Affected files

- `tests/test_substantiate_changelog_integration.py` (new) -- end-to-end: fixture CHANGELOG + synthetic substantiate run
- `qor/references/doctrine-changelog.md` (new) -- CHANGELOG policy doctrine
- `qor/scripts/changelog_stamp.py` -- no changes beyond Phase 2

### Unit Tests (write FIRST)

- `tests/test_substantiate_changelog_integration.py`
  - Stages a fixture CHANGELOG with a populated `Unreleased` section containing bullets under `### Added`.
  - Calls `apply_stamp(fixture_path, "0.18.0", "2026-05-01")`.
  - Reads back the stamped CHANGELOG and asserts:
    - `## [Unreleased]` still exists (empty body).
    - `## [0.18.0] - 2026-05-01` exists with the original bullets.
    - Byte-equal below the new entry (older versions untouched).
  - Negative: a second `apply_stamp` on the same fixture with the same `0.18.0` raises `ValueError("version [0.18.0] already present")`.
  - **Staging assertion**: after `apply_stamp` modifies a fixture CHANGELOG inside a `git init` tmp_path workspace, a simulated `git add` block that mirrors Step 9.5's auto-stage list (including the new `git add CHANGELOG.md` line) must leave `git diff --cached --name-only` containing `CHANGELOG.md`. The test proves the plan's Step 9.5 update actually stages the stamped file; catches drift if the auto-stage list regresses.
- `tests/test_changelog_doctrine.py`
  - Asserts `qor/references/doctrine-changelog.md` exists.
  - Asserts it contains the phrases `Keep a Changelog`, `Unreleased`, `Semantic Versioning`.
  - Asserts it names `qor/scripts/changelog_stamp.py` as the canonical automation.
  - Asserts it names `tests/test_changelog_format.py` and `tests/test_changelog_tag_coverage.py` as the enforcement surface.

### Changes

- `qor/references/doctrine-changelog.md`:
  - Policy: every release adds a dated section; `Unreleased` grows during implementation; bullets describe user-facing changes; security posture changes go in `Security`.
  - Mechanism: `changelog_stamp.py` handles the Unreleased -> version rename on seal.
  - Enforcement: two lint tests (format + tag coverage).
  - Exception: the initial backfill in Phase 27 Phase 1 is hand-authored; from v0.18.0 onward the Unreleased convention + stamp automation is the canonical path.

---

## Delegation

- Plan complete -> `/qor-audit`.
- Phase 1 is content authoring + structural lint. Phase 2 is a small pure module + skill wiring. Phase 3 is doctrine + integration test. No module restructuring; `/qor-organize` not required.
- If the audit flags the substantiate SKILL.md additions as changing its semantic contract (beyond appending one step), escalate to `/qor-refactor`.
