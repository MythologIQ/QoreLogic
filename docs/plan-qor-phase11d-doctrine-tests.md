# Plan: Phase 11D — SKILL.md Doctrine Tests + Gap Closure

**Status**: Active (scope-limited)
**Author**: QorLogic Governor
**Date**: 2026-04-15
**Scope**: Add `tests/test_skill_doctrine.py` (8 static analyses over SKILL.md tree). Tests fail initially. Then fix gaps category-by-category until green. Ship as one phase so the tests prove the fixes.
**Triggered by**: `docs/research-brief-full-audit-2026-04-15.md` (V-5 missing meta-finding S-14)

## Open Questions

None. Decisions:
- Tests are static (grep / file-walks); no skill execution
- Tests fail at HEAD before fixes (proves they catch real defects)
- Fixes are mechanical sweeps + targeted authoring; no behavior change
- Phase 11D scope: S-1, S-2, S-3, S-5, S-6, S-7, S-9, S-10. Defer S-4 (full Delegation sections), S-8 (delegation-table additions), S-12 (agent cross-refs), S-11 (ledger_hash tests) to future phases.

## Test deliverables (`tests/test_skill_doctrine.py`)

| Test | Pattern | Catches |
|---|---|---|
| `test_gate_writes_implies_write_step` | every skill with non-empty `gate_writes` has `.qor/gates/` or `write_artifact` in body | S-1 |
| `test_no_dead_skill_references` | every `/qor-*` ref resolves to existing skill dir | S-9 |
| `test_no_stale_processed_paths` | no SKILL.md frontmatter cites `processed/skills-output/` | S-2 |
| `test_governance_skills_have_governance_category` | skills under `qor/skills/governance/` declare `category: governance` | S-3 |
| `test_skill_local_references_files_exist` | every `references/<file>.md` cited in body resolves locally | S-6 (local refs) |
| `test_qor_help_lists_every_skill` | every `qor-*` skill name appears in `qor-help/SKILL.md` | S-7 |
| `test_no_QL_uppercase_leftovers` | grep `\bQL\b` returns zero in active SKILL.md + references | S-5 |
| `test_no_tools_reliability_references` | no skill body references `tools/reliability/` (vestigial) | S-10 |

Tests use the existing `tests/bundle_runner.py`-style markdown-walk pattern.

## Fix order (matches test order)

### Fix S-1 — gate_writes execution

- Add `write_gate_artifact(phase: str, payload: dict, session_id: str | None = None) -> Path` to `qor/scripts/gate_chain.py` (wraps `validate_gate_artifact.write_artifact`)
- Append a `### Step N: Write Gate Artifact` snippet to each affected skill's protocol:
  ```python
  import gate_chain
  gate_chain.write_gate_artifact(
      phase="<phase>",
      payload={"phase": "<phase>", "ts": shadow_process.now_iso(), "session_id": sid, ...},
      session_id=sid,
  )
  ```
- Affected skills (verified count = 8): `qor-plan`, `qor-implement`, `qor-refactor`, `qor-substantiate`, `qor-validate`, `qor-repo-audit`, `qor-repo-release`, `qor-repo-scaffold`. Plus `qor-audit` (already noted in prior brief) — total 9 markdown edits.

### Fix S-9 — dead skill refs

- Replace `/qor-course-correct` → `/qor-remediate` in `qor-help/SKILL.md`. (Verified: only that one skill references it.)

### Fix S-2 — stale paths

- Sweep frontmatter: `processed/skills-output/<name>` → `qor/skills/<category>/<name>` (16 skills)

### Fix S-3 — governance category

- Set `category: governance` for `qor-audit`, `qor-substantiate`, `qor-validate`, `qor-governance-compliance`, `qor-shadow-process`

### Fix S-5 — QL leftovers

- Sweep `\bQL\b` → `QorLogic` in 5 reference files

### Fix S-6 — references paths

- `qor-deep-audit`, `qor-help`, `qor-onboard-codebase` body references to `references/doctrine-token-efficiency.md` change to `qor/references/doctrine-token-efficiency.md`
- Author `qor/skills/governance/qor-audit/references/adversarial-mode.md` stub (1-page doc with input/output schema sketch + "wiring deferred" note)

### Fix S-7 — qor-help completeness

- Add 4 missing skills under appropriate categories (governance: qor-governance-compliance; memory: qor-docs-technical-writing; meta: qor-meta-log-decision, qor-meta-track-shadow)

### Fix S-10 — vestigial refs

- Remove `tools/reliability/` deferred blocks from `qor-implement/SKILL.md` and `qor-substantiate/SKILL.md`

## Verification

All 8 doctrine tests must turn green. Full suite must remain at 154+ passing (no regression).

## Constraints

- **No new Python beyond `gate_chain.write_gate_artifact()`**
- **No SKILL.md behavior change** — only doctrine compliance + content correction
- **Tests written first**, then fixes — TDD enforces "the test catches the gap"
- **Honor token-efficiency** — doctrine tests are static greps, fast
- **Defer S-4, S-8, S-11, S-12 to later phases** — keep this scope tight

## Success Criteria

- [ ] `tests/test_skill_doctrine.py` exists with 8 tests
- [ ] All 8 tests fail at start of fix work (proves they catch gaps)
- [ ] All 8 tests pass after fixes
- [ ] `gate_chain.write_gate_artifact()` helper exists with at least 1 unit test
- [ ] 9 SKILL.md files updated with Step "Write Gate Artifact"
- [ ] 16 frontmatter source paths updated; 5 categories fixed; 1 dead ref fixed; 5 QL leftovers swept; 4 doctrine paths fixed; 4 skills added to qor-help; 2 tools/reliability blocks removed; 1 adversarial-mode stub authored
- [ ] Drift clean (dist regenerated)
- [ ] Full suite 162+/162+ passing (154 prior + 8 new)
- [ ] Ledger chain verify OK
- [ ] Committed + pushed

## CI Commands

```bash
python -m pytest tests/test_skill_doctrine.py -v
python -m pytest tests/
python qor/scripts/check_variant_drift.py
python qor/scripts/ledger_hash.py verify docs/META_LEDGER.md
```
