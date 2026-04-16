## Phase 20 v3 — Import Migration (Sprint 2 of 4, remediation of Entry #61 VETO)

**change_class**: feature
**Status**: Active
**Author**: QorLogic Governor
**Date**: 2026-04-16
**Branch**: `phase/20-import-migration`
**Supersedes**: `docs/plan-qor-phase20-v2-import-migration.md` (VETO'd — Entry #61)
**Derived from**: `docs/RESEARCH_BRIEF.md` Sprint 2
**Closes gaps**: GAP-IMP-01, GAP-IMP-02, GAP-IMP-03, GAP-IMP-05 (**4 of 18**; 7 open after this phase)

## Open Questions

None. Entry #61 V-1 has a verbatim prescribed fix (option (a) `addopts`).

## Delta from v2

Single fix to close Entry #61 V-1 (integration test skip mechanism unspecified).

**V-1 closure (audit-prescribed option (a))**: add `addopts = "-m 'not integration'"` to `[tool.pytest.ini_options]` in `pyproject.toml`. Global default excludes integration marker; CI install-smoke job explicitly opts in via `-m integration`. Matches pytest convention; single line change.

**Propagation**: pyproject.toml becomes a modified file. Updates:
- Affected Files "Modified (20)" → **"Modified (21)"**
- New sub-group or extend "CI" to include pyproject — adopting "Config (1)" as new sub-group for clarity: pyproject.toml
- Success Criteria adds: `[tool.pytest.ini_options].addopts = "-m 'not integration'"` declared

No other scope changes. All v2 design (resources.py, workdir.py, import migration, REPO_ROOT split, hardcoded path cleanup, install-smoke CI job) carries forward unchanged.

## Scope (unchanged from v2)

All four IMP gaps close in one phase. Non-SDLC scope respected.

Out of scope:
- Sprint 3 (Phase 21): `qorlogic install/uninstall/list/info/compile/verify-ledger`, host resolver, MANIFEST emitter, `--profile` selector
- Sprint 4 (Phase 22): `.gitignore` build artifacts, `compile.py` rename, drift/ledger CI wiring, TestPyPI rehearsal, macOS in matrix, plan-linter test (SG-038 mechanical mitigation per SHADOW_GENOME Entry #17)

## Grounded state (2026-04-16 via `grep -n` / `wc -l` / `find`)

- `sys.path.insert` sites in production: **9** files
- Bare sibling imports: **13** across 9 files
- `REPO_ROOT = Path(__file__).resolve().parent.parent.parent` sites: **13 total** (11 `qor/scripts/` + 2 `qor/reliability/`)
- Hardcoded runtime path strings: **8** (4 in `calculate-session-seal.py`, 4 in `collect_shadow_genomes.py`)
- `sys.path.insert` in tests: **3** (`tests/conftest.py:6,7`, `tests/test_governance_helpers.py:15`)
- Current test count: 278 passed (post-Phase 19, commit `c57a821`)
- `[tool.pytest.ini_options]` in pyproject.toml: declares `testpaths`, `markers` (lines 57-62 post-Phase 19); **no `addopts` currently configured** (verified via `grep "addopts" pyproject.toml` → empty).

## Track A — New module: `qor/resources.py` (unchanged from v2)

See v2 Track A. ~25 lines, 3 functions under 5 lines each.

## Track B — New module: `qor/workdir.py` (unchanged from v2)

See v2 Track B. ~45 lines, `$QOR_ROOT` → `Path.cwd()` anchor chain, optional `detect_git_root()` SDLC helper.

## Track C — Migrate 13 sibling imports (IMP-01, unchanged from v2)

9 files in `qor/scripts/` updated: `validate_gate_artifact.py`, `remediate_read_context.py`, `remediate_mark_addressed.py`, `qor_audit_runtime.py`, `gate_chain.py`, `create_shadow_issue.py`, `collect_shadow_genomes.py`, `check_variant_drift.py`, `check_shadow_threshold.py`. Delete `sys.path.insert`; rewrite sibling imports as `from qor.scripts import X`.

## Track D — REPO_ROOT split (IMP-02, unchanged from v2)

13 files touched: 11 in `qor/scripts/` + 2 in `qor/reliability/`. Delete every `REPO_ROOT = parent.parent.parent`; route to `qor.resources` (packaged) or `qor.workdir` (consumer state).

## Track E — Hardcoded path cleanup (IMP-03, unchanged from v2)

2 files: `calculate-session-seal.py` (4 paths) + `collect_shadow_genomes.py` (4: scripts + logs). Route through `qor.workdir` or `python -m qor.scripts.X`.

## Track F — Test infrastructure + CI smoke test + pytest config (IMP-05, v3 extended)

### Affected Files
- `tests/conftest.py` (remove `sys.path.insert`)
- `tests/test_governance_helpers.py` (remove `sys.path.insert`)
- `tests/test_packaging_install.py` (new, 4 integration tests)
- `pyproject.toml` (**v3**: add `addopts = "-m 'not integration'"` to `[tool.pytest.ini_options]`)
- `.github/workflows/ci.yml` (append install-smoke job)

### Changes

**`pyproject.toml`** (v3 addition) — extend `[tool.pytest.ini_options]`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-m 'not integration'"
markers = [
    "integration: live environment probes; opt-in via '-m integration'",
]
```

Default `pytest tests/` now excludes `@pytest.mark.integration` tests. Install-smoke CI job opts in via `-m integration` explicitly (already specified).

**`tests/test_packaging_install.py`** (new, ~40 lines, 4 tests with `@pytest.mark.integration`):
- `test_installed_wheel_imports_package`
- `test_installed_wheel_ships_schemas`
- `test_installed_wheel_ships_skills`
- `test_cli_entry_point_runs`

**`tests/conftest.py`** + **`tests/test_governance_helpers.py`** — remove `sys.path.insert` blocks.

**`.github/workflows/ci.yml`** — append install-smoke job using `${{ runner.temp }}` for cross-platform temp; explicit `-m integration` to opt in.

## Track G — Test expectations (v3 verified achievable)

- Baseline: 278 passed + 0 skipped (post-Phase 19).
- **+4 new** integration tests; skipped by default via `addopts` filter.
- Default target: 278 → **278 passed + 4 skipped** (skip reason: "not integration" marker excluded by `addopts`).
- Integration target: **282 passing** when `-m integration` opts in (CI install-smoke job).

## Affected Files (summary)

### New (3)
- `qor/resources.py`
- `qor/workdir.py`
- `tests/test_packaging_install.py`

### Modified (21)

Scripts (15):
- `qor/scripts/shadow_process.py`
- `qor/scripts/validate_gate_artifact.py`
- `qor/scripts/session.py`
- `qor/scripts/remediate_read_context.py`
- `qor/scripts/remediate_mark_addressed.py`
- `qor/scripts/remediate_emit_gate.py`
- `qor/scripts/qor_audit_runtime.py`
- `qor/scripts/qor_platform.py`
- `qor/scripts/gate_chain.py`
- `qor/scripts/create_shadow_issue.py`
- `qor/scripts/collect_shadow_genomes.py`
- `qor/scripts/compile.py`
- `qor/scripts/check_variant_drift.py`
- `qor/scripts/check_shadow_threshold.py`
- `qor/scripts/calculate-session-seal.py`

Reliability (2):
- `qor/reliability/intent-lock.py`
- `qor/reliability/skill-admission.py`

Tests (2):
- `tests/conftest.py`
- `tests/test_governance_helpers.py`

Config (1):
- `pyproject.toml` (v3: add `addopts`)

CI (1):
- `.github/workflows/ci.yml`

Total: 3 new + **21 modified** = 24 files.

## Constraints

- **Inline grounding**: every count cites `grep` / `wc -l` / `find` with date 2026-04-16.
- **Tests before code** for `test_packaging_install.py`.
- **SG-038 lockstep**: prose + enumerations + success criteria cite **4 gap IDs, 3 new, 21 modified, +4 new tests, 0.10.0 → 0.11.0, 7 remaining after**.
- **Non-SDLC scope**: `qor/workdir.py` uses `$QOR_ROOT` → `Path.cwd()` only.
- **No new runtime dependencies**: stdlib only.
- **Reliability**: pytest 2x deterministic before commit.

## Success Criteria

- [ ] `qor/resources.py` + `qor/workdir.py` created; both under 50 lines.
- [ ] 13 sibling imports converted to `from qor.scripts import X`.
- [ ] 13 `REPO_ROOT = parent.parent.parent` declarations removed.
- [ ] 9 `sys.path.insert` sites in `qor/scripts/` removed.
- [ ] 8 hardcoded path strings routed through `qor.workdir` or `python -m`.
- [ ] 3 `sys.path.insert` sites in tests removed.
- [ ] `tests/test_packaging_install.py` with 4 integration tests.
- [ ] `pyproject.toml` `[tool.pytest.ini_options].addopts = "-m 'not integration'"` declared.
- [ ] `.github/workflows/ci.yml` install-smoke job added (explicit `-m integration`).
- [ ] Tests default: **278 passed + 4 skipped** (skip reason: addopts filter).
- [ ] Tests integration: 282 passing in CI smoke.
- [ ] `python -m build` builds cleanly at 0.11.0.
- [ ] `check_variant_drift.py` clean.
- [ ] `ledger_hash.py verify` chain valid.
- [ ] Substantiation: `0.10.0 → 0.11.0`; annotated tag `v0.11.0`.
- [ ] **4 gaps closed** (IMP-01/02/03/05); **7 remaining in RESEARCH_BRIEF.md**.

## CI Commands

```bash
python -m pytest tests/ -v                   # 278 passed + 4 skipped via addopts
python -m pytest tests/ -m integration -v    # 4 integration tests opt in
BUILD_REGEN=1 python qor/scripts/check_variant_drift.py
python qor/scripts/ledger_hash.py verify docs/META_LEDGER.md
python -m build
git tag --list 'v*' | tail -5
```
