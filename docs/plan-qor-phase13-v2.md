# Plan: Phase 13 v2 — Governance Enforcement (Remediation)

**change_class**: feature
**Status**: Active (post-VETO remediation; ratified Q1=(a), Q2=(a), Q3=(a) + phase-history doc requirement)
**Author**: QorLogic Governor
**Date**: 2026-04-15
**Supersedes**: `docs/plan-qor-phase13-governance-enforcement.md` (v1, VETO — Ledger #25)

## Open Questions

None.

## Audit remediation (V-1..V-10 from Entry #25, quoted verbatim)

| ID | Audit instruction | Plan §addressing |
|---|---|---|
| V-1 | "Add `test_plans_declare_change_class` to `tests/test_skill_doctrine.py`. Test parses every `docs/plan-qor-phase*.md` header for `change_class:` field; rejects missing or invalid values. Update plan §D.1 to list 3 new doctrine tests (was 2)." | §D.1 (3 new doctrine tests) |
| V-2 | "Specify the plan-discovery mechanism. Recommend: substantiate reads the most-recent `docs/plan-qor-phase*.md` matching the current branch name's phase number (`phase/13-...` → `plan-qor-phase13-*.md`). Document in §B.2." | §B.2 + §C.1 (`current_phase_plan_path`) |
| V-3 | "Add `parse_change_class(plan_path: Path) -> str` to §C.1 helper list. Add `test_parse_change_class_*` (3 tests: hotfix/feature/breaking) to §D.2. Update count to 8 helper tests." | §C.1 + §D.2 (8 helper tests) |
| V-4 | "Decide naming scheme. Recommend: digits-only from Phase 13 forward; older plans (11d, 12-v2) grandfathered. Parser regex: `r'plan-qor-phase(\d+)-([a-z0-9-]+)\.md'`." | §C.1 + §A.3 phase-history doc |
| V-5 | "Add to §B.1 plan-skill Step 0.5: 'If `git status --porcelain` shows uncommitted changes, abort with operator decision (stash / commit / abandon prior phase).'" | §B.1 |
| V-6 | "Reference and extend qor-substantiate's existing Step 2.5 version-validation interdiction in §B.2. New Step 7.5 must check 'Target Version > Current Tag' before bump." | §B.2 |
| V-7 | "Add `**change_class**: feature` to plan header (eat your own dogfood)." | Header above ✓ |
| V-8 | "Add tag-message template to §A.1: e.g., `'v{version}\n\nMerkle seal: {seal}\nLedger entry: #{n}\nPhase: {phase}\nClass: {class}'`." | §A.1 |
| V-9 | "Local-merge option must dry-run first: `git merge --no-commit --no-ff <branch>`; if conflicts, abort and prompt operator. Document in §A.1." | §A.1 |
| V-10 | "Quote the current Step 9.6 text of qor-substantiate/SKILL.md when authoring §B.2 replacement instruction." | §B.2 (quoted verbatim) |

## Track A — Doctrines + CLAUDE.md + Phase History

### A.1 `qor/references/doctrine-governance-enforcement.md` (new)

5 sections (behavior, branching, versioning, tag, push/merge), with V-8 + V-9 fixes:

- **Behavior**: agent does not offer continuation menus when work is sealable. Substantiate-and-commit auto on green; operator decides push/merge.
- **Branching**: per-phase, `phase/<NN>-<slug>` from main. Pre-checkout interdiction: `git status --porcelain` must be clean OR operator chooses (stash/commit/abandon).
- **Versioning**: plan header declares `change_class: hotfix|feature|breaking`. Substantiate bumps `pyproject.toml [project].version`:
  - hotfix → patch (0.2.0 → 0.2.1)
  - feature → minor (0.2.0 → 0.3.0)
  - breaking → major (0.2.0 → 1.0.0)
- **Tag** (V-8 template): annotated tag `v{X.Y.Z}` with message:
  ```
  v{version}

  Merkle seal: {seal_hash}
  Ledger entry: #{entry_number}
  Phase: {phase_number}
  Class: {change_class}
  ```
- **Push/merge optionality (V-9 safety)**: 4 operator options:
  1. push only (`git push origin <branch>`)
  2. push + open PR (`gh pr create`)
  3. merge to main locally — **dry-run first**: `git merge --no-commit --no-ff <branch>`; on conflict, abort with prompt
  4. hold local

### A.2 `CLAUDE.md` update

New "Governance flow" section (3 bullets):
- After substantiation passes, commit automatically; do not offer continuation
- Each `/qor-plan` starts a new `phase/<NN>-<slug>` branch (digit phase numbers)
- Each substantiation bumps version per plan-declared `change_class:` and creates `v{X.Y.Z}` tag

### A.3 `docs/PHASE_HISTORY.md` (new)

Append-only index of all phases, one row per phase. Maintained automatically by substantiate (Phase 13.5 wiring) and grandfathered to include all historical phases.

```markdown
# QorLogic Phase History

| # | Slug | Plan | Substantiate Entry | Tag | Class | Sealed |
|---|---|---|---|---|---|---|
| 0 | (genesis) | — | #1 | — | — | 2026-03-19 |
| 1 | qor-* migration | plan-qor-migration-*.md (4 iter) | #20 | — | — | 2026-04-15 |
| 2 | compile-pipeline | plan-qor-phase2-compile.md | (impl/sub merged) | — | feature | 2026-04-15 |
| ... | ... | ... | ... | ... | ... | ... |
| 11d | doctrine-tests | plan-qor-phase11d-doctrine-tests.md | (legacy filename — grandfathered) | — | feature | 2026-04-15 |
| 12 | budget-ledger-tests | plan-qor-phase12-v2.md | #24 | — | feature | 2026-04-15 |
| 13 | governance-enforcement | plan-qor-phase13-v2.md | (this seal) | v0.3.0 | feature | (TBD) |
```

Substantiate appends a row at seal time. Doctrine test enforces every plan file has a row.

### A.4 `qor/references/doctrine-test-discipline.md` Rule 4 (V-1 + Q3 elevation)

New Rule 4 added: **"Rule = Test"**

> When a plan introduces a new rule (a constraint, format, requirement, or convention), the same plan MUST add the doctrine test enforcing it. Rule without test = optional. Verified instances: Phase 11D S-1 (`gate_writes` declared without execution test); Phase 13 V-1 (`change_class:` declared without parser test).

## Track B — Skill wiring

### B.1 `qor/skills/sdlc/qor-plan/SKILL.md`

Add Step 0.5 (per V-5):

```python
# Phase 13 wiring: dirty-tree check + per-phase branch
import subprocess
result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
if result.stdout.strip():
    # Operator decision: stash | commit | abandon | abort
    raise InterdictionError("Working tree dirty; operator must choose stash/commit/abandon before plan branch")

# Derive phase metadata from filename (digits only forward; V-4)
import sys; sys.path.insert(0, 'qor/scripts')
import governance_helpers as gh
phase_num, slug = gh.derive_phase_metadata(plan_path)  # raises on letter-suffix legacy plans
subprocess.run(["git", "checkout", "-b", f"phase/{phase_num:02d}-{slug}"], check=True)
```

Plan header MUST declare `**change_class**: hotfix | feature | breaking`. Doctrine test V-1 enforces.

### B.2 `qor/skills/governance/qor-substantiate/SKILL.md`

**Verbatim current Step 9.6 (V-10 quote)**:
> "Prompt user with three options: (1) merge to main, (2) create PR, (3) stay on branch. If version changed, offer to create annotated tag."

**Replacement**: 4-option menu per Track A.1 (push only / push+PR / local-merge with dry-run / hold).

Add Step 7.5 (between Final Merkle Seal and Cleanup):

```python
# Phase 13 wiring: bump version + tag
import sys; sys.path.insert(0, 'qor/scripts')
import governance_helpers as gh

plan_path = gh.current_phase_plan_path()  # V-2: branch-name match
change_class = gh.parse_change_class(plan_path)  # V-3 helper

# V-6: integrate existing Step 2.5 interdiction
new_version = gh.bump_version(change_class)  # raises if Target <= Current Tag
tag = gh.create_seal_tag(new_version, merkle_seal, ledger_entry_num, phase_num, change_class)
gh.append_phase_history_row(phase_num, slug, plan_path, ledger_entry_num, tag, change_class)
```

Constraint update: "NEVER offer continuation menus when work is sealable; the next decision is push/merge, not 'what next phase'."

## Track C — Script helpers

### C.1 `qor/scripts/governance_helpers.py` (new)

8 functions:

- `current_branch() -> str` — `git rev-parse --abbrev-ref HEAD`
- `derive_phase_metadata(plan_path: Path) -> tuple[int, str]` — parses `plan-qor-phase(\d+)-([a-z0-9-]+)\.md` (V-4). Raises ValueError on letter-suffix legacy plans.
- `current_phase_plan_path() -> Path` — V-2: parses current branch (`phase/<NN>-...`); globs `docs/plan-qor-phase<NN>*.md`; picks most recent by mtime when v1/v2 exist
- `parse_change_class(plan_path: Path) -> str` — V-3: parses plan header line `**change_class**: <class>`. Returns one of {hotfix, feature, breaking}. Raises ValueError on missing/invalid.
- `bump_version(change_class: str, pyproject_path: Path = ...) -> str` — reads pyproject; computes new version per class; checks no existing `v<X.Y.Z>` tag; writes pyproject; returns new version. V-6: integrates tag-collision check.
- `create_seal_tag(version, seal, entry, phase, klass) -> str` — V-8: annotated tag with templated message
- `create_phase_branch(phase: int, slug: str) -> str` — V-5: pre-checks dirty tree; checks out
- `append_phase_history_row(...) -> None` — A.3: appends to `docs/PHASE_HISTORY.md`

All atomic; no in-place mutation if any step fails.

## Track D — Tests

### D.1 `tests/test_skill_doctrine.py` (extend with 3 new — V-1)

- `test_plan_skill_documents_branch_creation` — `qor-plan/SKILL.md` body contains `phase/` branch reference
- `test_substantiate_skill_documents_version_bump` — `qor-substantiate/SKILL.md` body references `bump_version` or `create_seal_tag`
- `test_plans_declare_change_class` — every `docs/plan-qor-phase*.md` (digits-only forward, grandfathering older) header contains `**change_class**: <hotfix|feature|breaking>`. Phases 11d/12-v2 explicitly excluded by filename pattern.

### D.2 `tests/test_governance_helpers.py` (new — 8 tests per V-3)

- `test_derive_phase_metadata_from_digit_filename` — `plan-qor-phase13-governance-enforcement.md` → `(13, "governance-enforcement")`
- `test_derive_phase_metadata_rejects_letter_suffix` — `plan-qor-phase11d-doctrine-tests.md` → ValueError (legacy grandfathered, not parsed)
- `test_parse_change_class_hotfix` — synthetic plan with `**change_class**: hotfix` → `"hotfix"`
- `test_parse_change_class_feature` — synthetic plan with `**change_class**: feature` → `"feature"`
- `test_parse_change_class_breaking` — synthetic plan with `**change_class**: breaking` → `"breaking"`
- `test_parse_change_class_invalid_raises` — `**change_class**: xyz` → ValueError
- `test_bump_version_hotfix` — 0.2.0 + hotfix → 0.2.1
- `test_bump_version_feature` — 0.2.0 + feature → 0.3.0
- `test_bump_version_breaking` — 0.2.0 + breaking → 1.0.0

(9 tests total — one extra; reconciled count below)

### D.3 `tests/test_skill_doctrine.py` extra (V-1 + Q3 meta-doctrine)

- `test_phase_history_lists_every_plan` — every `docs/plan-qor-phase*.md` has a row in `docs/PHASE_HISTORY.md` (matched by phase number)

(4 doctrine tests total in this phase; 1 helper test extra → reconcile counts in Success Criteria)

## Affected Files

### Track A (4 new + 1 modified)
- `qor/references/doctrine-governance-enforcement.md`
- `qor/references/doctrine-test-discipline.md` (modified — Rule 4 added)
- `docs/PHASE_HISTORY.md` (new)
- `CLAUDE.md` (modified — Governance flow section)

### Track B (2 modified)
- `qor/skills/sdlc/qor-plan/SKILL.md`
- `qor/skills/governance/qor-substantiate/SKILL.md`

### Track C (1 new)
- `qor/scripts/governance_helpers.py`

### Track D (1 new + 1 modified)
- `tests/test_governance_helpers.py` (9 tests)
- `tests/test_skill_doctrine.py` (4 new tests; total grows by 4)

## Constraints

- **No GitHub Actions workflows**
- **All atomic writes via os.replace**
- **Tests before code** for governance_helpers (per doctrine-test-discipline)
- **Reliability check mandatory**: pytest 2x consecutive identical results before commit
- **Plan eats its own dogfood**: header declares `change_class: feature` (V-7) ✓
- **Phase 13 implemented on `main` directly** (bootstrap exception); subsequent phases use new branching rule

## Success Criteria

- [ ] `qor/references/doctrine-governance-enforcement.md` exists with 5 sections including V-8 tag template + V-9 dry-run safety
- [ ] `qor/references/doctrine-test-discipline.md` Rule 4 "Rule = Test" added
- [ ] `docs/PHASE_HISTORY.md` exists with rows for all historical phases (genesis through 12) + Phase 13 row appended at seal
- [ ] `CLAUDE.md` Governance flow section added
- [ ] `qor-plan/SKILL.md` Step 0.5 documents dirty-tree check + branch creation + change_class requirement
- [ ] `qor-substantiate/SKILL.md` Step 7.5 documents bump+tag+history-append; Step 9.6 quotes existing text + provides 4-option replacement
- [ ] `qor/scripts/governance_helpers.py` exists with 8 functions
- [ ] `tests/test_governance_helpers.py` 9 tests passing
- [ ] `tests/test_skill_doctrine.py` 4 new tests passing
- [ ] Full suite 200 passing + 6 skipped (was 187 + 6; +9 helper +4 doctrine = 200)
- [ ] Drift clean
- [ ] Ledger chain verified
- [ ] Substantiation produces version 0.2.0 → 0.3.0 + tag `v0.3.0`
- [ ] Operator prompted with 4-option push/merge menu

## CI Commands

```bash
python -m pytest tests/test_skill_doctrine.py tests/test_governance_helpers.py -v
python -m pytest tests/
python qor/scripts/check_variant_drift.py
python qor/scripts/ledger_hash.py verify docs/META_LEDGER.md
git tag --list 'v*' | tail -3
```
