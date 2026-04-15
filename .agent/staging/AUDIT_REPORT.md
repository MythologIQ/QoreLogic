# AUDIT REPORT — plan-qor-phase13-v2.md

**Tribunal Date**: 2026-04-15
**Target**: `docs/plan-qor-phase13-v2.md`
**Risk Grade**: L1 (architecture decision + spec gaps; substantive direction sound)
**Auditor**: The QorLogic Judge

---

## VERDICT: **VETO**

---

### Executive Summary

v2 addresses all 10 v1 V-* items. **VETO** is for one architecture-altering finding driven by operator's GitHub-hygiene hint (V-1, demands rework of Track A.3 + D.3) plus 6 specification gaps. Plan substantively sound; remediation reduces scope, doesn't expand it.

### Audit Results

#### Security/Ghost UI/Razor/Dependency Passes
**Result**: PASS.

#### Macro-Level Pass
**Result**: FAIL — see V-1 (architecture: parallel infrastructure to GitHub-native).

#### Orphan Pass
**Result**: PASS at file level; conditional on V-1 resolution.

### Violations Found

| ID | Category | Location | Description |
|---|---|---|---|
| V-1 | YAGNI / parallel infrastructure | plan §A.3 (`docs/PHASE_HISTORY.md`) + §C.1 `append_phase_history_row()` + §D.3 `test_phase_history_lists_every_plan` | Operator hint: "Good GitHub hygiene also solves for this — issues updated with branches labeled, documentation/notes in the PR." Hint is correct: GitHub already provides phase indexing via labeled issues + branch metadata + PR descriptions + commit history + tags. Building a parallel `PHASE_HISTORY.md` duplicates this machinery. The doctrine doc should describe the *GitHub hygiene practice* (issue per phase, labels for phase number + change class, branch named `phase/<NN>-<slug>`, PR description templates, tag annotation) — not author a separate index. **Drop A.3, drop helper `append_phase_history_row`, drop D.3 test.** Replace with §A.3-revised: `docs/PHASE_HYGIENE.md` or new section in governance doctrine specifying the GitHub conventions. |
| V-2 | Format ambiguity | §C.1 `parse_change_class()` looks for `**change_class**: <class>` but doctrine doesn't declare canonical syntax | Plan v2 header writes `**change_class**: feature` (bold markdown). Plan v1 (verbatim recall) wrote it without bold. Test would need to handle both, OR plan must mandate one. Recommend canonical: `**change_class**: <class>` (bold, consistent with `**Status**:` etc. in plan headers). Doctrine and parser agree on one; doctrine test rejects the other. |
| V-3 | Test count mismatch (V-9 recurrence) | §D.2 header says "8 tests per V-3"; body lists 9 | `test_derive_phase_metadata_from_digit_filename`, `test_derive_phase_metadata_rejects_letter_suffix`, 4× `test_parse_change_class_*`, 3× `test_bump_version_*` = 9. Plan §D.2 header inconsistent. Update count. |
| V-4 | Undefined exception | §B.1 `raise InterdictionError(...)` | `InterdictionError` is not defined anywhere in the repo. Either define in `governance_helpers.py`, or use stdlib (e.g., `RuntimeError`), or specify the exception class in the plan. |
| V-5 | Spec gap | §C.1 `current_phase_plan_path()` says "picks most recent by mtime when v1/v2 exist" | Implicit rule. What about v3, v4, ...? mtime-based works but is filesystem-dependent (CI may not preserve mtime via git). Better: lexicographic order on filename suffix (`-v2.md` > `governance-enforcement.md`), with explicit tiebreak rule documented. |
| V-6 | Citation inaccuracy | §A.4 Rule 4 "Verified instances: Phase 11D S-1 ... Phase 13 V-1" | Phase 11D S-1 was surfaced in `docs/research-brief-full-audit-2026-04-15.md`, not in a phase audit. The citation should be `docs/research-brief-full-audit-2026-04-15.md §S-1` or just `Phase 11D doctrine-test introduction`. Per /qor-plan grounding protocol, named mechanisms must be cited with verified path. |
| V-7 | Risk of fabrication | §A.3 `docs/PHASE_HISTORY.md` historical rows (genesis through 12) | If V-1 (above) is accepted, this becomes moot. If V-1 is REJECTED and we keep PHASE_HISTORY.md, the historical rows would be hand-typed from imperfect memory. Genesis is dated 2026-03-19 (pre-conversation). No canonical record exists for several entries. Risk: invented data presented as historical fact. Either accept V-1, or constrain history rows to phases with verifiable ledger entries (#17, #18, #19, #20, #21, #22, #23, #24, #25 — and only those). |

### Required Remediation

1. **V-1 (CRITICAL)**: Drop `docs/PHASE_HISTORY.md`, `append_phase_history_row()` helper, and `test_phase_history_lists_every_plan` doctrine test. Replace with `docs/PHASE_HYGIENE.md` (or section in `doctrine-governance-enforcement.md`) specifying GitHub conventions:
   - One issue per phase (title: `Phase {NN}: {slug}`)
   - Issue labels: `phase:NN`, `class:hotfix|feature|breaking`
   - Branch named per the existing rule (`phase/<NN>-<slug>`)
   - PR descriptions cite the plan file + ledger entry + Merkle seal
   - Annotated tag at substantiation links back to the PR or commit
   - Doctrine test (replacement): `test_governance_doctrine_documents_github_hygiene` — verifies `doctrine-governance-enforcement.md` contains the keywords (issue label, PR description, branch name, tag annotation)
2. **V-2**: Mandate canonical `**change_class**: <class>` (bold). Update `parse_change_class()` regex to enforce. Update doctrine test to reject non-bold variant.
3. **V-3**: Update §D.2 header from "8 tests" to "9 tests".
4. **V-4**: Either define `InterdictionError` in `governance_helpers.py` (`class InterdictionError(RuntimeError): pass`) or use `RuntimeError` directly. Plan must state which.
5. **V-5**: Replace mtime tiebreak with lexicographic-suffix rule. Document: "When multiple plans match `phase<NN>*.md`, the one with the highest sortable suffix wins (`-v3.md` > `-v2.md` > base filename). Tiebreak deterministic across CI/local."
6. **V-6**: Update §A.4 citation from "Phase 11D S-1" to `docs/research-brief-full-audit-2026-04-15.md §S-1` (verified file).
7. **V-7**: Resolves automatically if V-1 accepted. If V-1 rejected, restrict history rows to phases with ledger-entry citations only (no fabricated genesis-era rows).

### Verdict Hash

(computed at ledger entry — see Entry #26)

---
_This verdict is binding._
