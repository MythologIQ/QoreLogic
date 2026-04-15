# Research Brief: /qor-audit

**Date**: 2026-04-15
**Analyst**: QorLogic Analyst (research mode)
**Target**: `qor/skills/governance/qor-audit/SKILL.md` + references + cross-references in governance docs
**Scope**: Identify gaps, redundancy, ambiguous instructions, missing tool references, workflow inconsistencies.

---

## Executive Summary

`/qor-audit` is functionally complete for human-driven invocation but has **23 issues** spanning 4 categories. Most consequential: **Gap #1** (skill declares `gate_writes: audit` but no step actually writes the gate artifact at `.qor/gates/<session>/audit.json`) and **Gap #15** (legacy `.agent/staging/` output path coexists with newer `.qor/gates/` chain location with no reconciliation). 4 critical, 10 medium, 9 cosmetic.

## Findings

### Critical gaps (action required)

#### Gap #1 — `gate_writes: audit` declared but never executed

**Location**: `qor/skills/governance/qor-audit/SKILL.md:13` (frontmatter), Step 4 line 188
**Severity**: CRITICAL

Frontmatter declares `gate_writes: audit`, meaning downstream phases (`/qor-implement`) call `gate_chain.check_prior_artifact("implement")` expecting `.qor/gates/<session>/audit.json`. Step 4 only instructs writing the prose `.agent/staging/AUDIT_REPORT.md`. The gate artifact is never written; downstream gates always see "missing prior" and require override.

**Action**: Step 4 must instruct writing the structured gate artifact via `validate_gate_artifact.write_artifact("audit", {...})` in addition to the prose report. Add to `qor_audit_runtime.py` a `write_audit_artifact(verdict, target, violations, risk_grade)` helper that wraps the schema-conforming write.

#### Gap #2 — Adversarial-mode reference is a ghost handler

**Location**: SKILL.md:69
**Severity**: CRITICAL

Step 1.a references `qor/skills/governance/qor-audit/references/adversarial-mode.md`. Verified: file does NOT exist (only `qor-audit-templates.md` is in `references/`). Marked "TBD" inline but a reader following the link hits a 404.

**Action**: Either author a stub `adversarial-mode.md` documenting the contract (input/output schemas already exist in `qor/gates/schema/audit.schema.json`), or remove the reference and inline the contract sketch.

#### Gap #3 — Stale source path in metadata

**Location**: SKILL.md:10
**Severity**: MEDIUM

Frontmatter `source.path: processed/skills-output/qor-audit` references `processed/` directory which was deleted in the Phase 7 SSoT migration cutover (Ledger Entry #19). Path no longer resolves.

**Action**: Update to `qor/skills/governance/qor-audit` to match the SSoT canonical location.

#### Gap #4 — Wrong category in metadata

**Location**: SKILL.md:6
**Severity**: MEDIUM

Frontmatter `metadata.category: development`. The skill lives at `qor/skills/governance/` and is conceptually a governance skill (Judge persona, gate tribunal). Inconsistent with sibling governance skills.

**Action**: Change to `governance`.

### Workflow inconsistencies

#### Issue #5 — Two output destinations, one documented

**Location**: SKILL.md skill-block line 21 + Step 4 + Phase 3/7 wiring
**Severity**: HIGH

Skill output declared as `.agent/staging/AUDIT_REPORT.md` (line 21) — predates the SSoT migration. The Phase 3 gate chain expects structured output at `.qor/gates/<session_id>/audit.json` per `qor/gates/chain.md:28`. Skill currently produces only the legacy prose; gate artifact is missing (see Gap #1).

**Action**: Document both outputs explicitly. Prose report at `.agent/staging/AUDIT_REPORT.md` (or migrate to `docs/audit-reports/<date>.md`); structured artifact at `.qor/gates/<session>/audit.json`. The two are distinct deliverables; skill must produce both.

#### Issue #6 — Conflated shadow logs

**Location**: SKILL.md:198 (Step 6)
**Severity**: HIGH

"If verdict is VETO, document in `docs/SHADOW_GENOME.md`" — correct file (audit-verdict records). But `docs/PROCESS_SHADOW_GENOME.md` exists separately for process failures. Skill text does NOT disambiguate, and a Step 0 override emits to PROCESS_SHADOW_GENOME (correctly). A reader could miswrite.

**Action**: Step 6 explicit clarification: "audit verdict failures land in `docs/SHADOW_GENOME.md`; process-level overrides during this audit (e.g., gate skip) land in `docs/PROCESS_SHADOW_GENOME.md` via `runtime.emit_gate_override` (already done in Step 0)."

#### Issue #7 — `<phase>GATE</phase>` vs `phase: audit` mismatch

**Location**: SKILL.md skill block line 19 vs frontmatter line 11
**Severity**: LOW

Skill block uses descriptive `GATE`; frontmatter uses canonical `audit`. Tools that read frontmatter (gate_chain) work correctly; tools that read the skill block (display) show inconsistent labels.

**Action**: Either align (use `audit` in both) or document that skill-block phase is descriptive while frontmatter is canonical.

#### Issue #8 — Missing Delegation section (inconsistent with Phase 9 Track A)

**Severity**: MEDIUM

Phase 9 added `## Delegation` sections to `qor-research`, `qor-plan`, `qor-implement`, `qor-refactor`, `qor-validate` per delegation-table doctrine. `qor-audit` got handoff lines inline in Step 3 instead — useful but inconsistent doc structure.

**Action**: Add `## Delegation` section before `## Constraints`, citing `qor/gates/delegation-table.md` and naming the same handoffs (Razor → /qor-refactor; Orphan/Macro → /qor-organize; PASS → /qor-implement; L3 security → /qor-debug). The inline references in Step 3 can stay — they're contextual reminders.

### Missing tool references

#### Issue #9 — No reference to `ledger_hash.py`

**Location**: SKILL.md Step 5 (line 192)
**Severity**: MEDIUM

"Edit `docs/META_LEDGER.md` — add GATE TRIBUNAL entry with verdict, content hash, chain hash" — instructs hash computation but doesn't name `qor/scripts/ledger_hash.py` which provides `hash` and `chain` subcommands.

**Action**: "Use `python qor/scripts/ledger_hash.py hash <report>` for content hash and `... chain <content> <prev>` for the chain hash."

#### Issue #10 — No reference to `validate_gate_artifact.py`

**Severity**: MEDIUM

Audit produces `audit.json` (per Gap #1 fix); should validate it before considering the audit complete. `qor/scripts/validate_gate_artifact.py audit <path>` exists for exactly this.

**Action**: New step or subsection: "Validate output: `python qor/scripts/validate_gate_artifact.py audit .qor/gates/<sid>/audit.json` exits 0".

#### Issue #11 — No reference to `check_shadow_threshold.py` post-VETO

**Severity**: LOW

After a VETO emits a shadow event, the threshold checker is implied but never invoked. Periodic threshold breach is the trigger for `/qor-remediate` (per chain.md/delegation-table). Skill could nudge: "After this VETO, consider `python qor/scripts/check_shadow_threshold.py` to see if accumulated process drift now warrants `/qor-remediate`."

**Action**: Add as a soft recommendation in Step 6 or Final Report.

### Ambiguity

#### Issue #12 — "Estimate" without methodology

**Location**: SKILL.md:130-133 (Razor Pass table)
**Severity**: MEDIUM

Razor table columns: "Limit | Blueprint Proposes | Status". Tells auditor to fill in `[estimate]` but doesn't say HOW (read which files? extract from plan? grep for line counts?). For an LLM following this protocol, "estimate" is interpretation-dependent.

**Action**: Add a sub-bullet: "Estimate by reading the plan's affected-files list and using `wc -l` on existing files OR by inspecting proposed function/file scope statements."

#### Issue #13 — Risk Grade rubric absent

**Location**: SKILL.md (and templates)
**Severity**: MEDIUM

L1/L2/L3 used throughout but no rubric defines when to assign which. Audit report template has `Risk Grade: [L1 / L2 / L3]` with no guidance. Different auditors will assign inconsistently.

**Action**: Add a rubric to `references/qor-audit-templates.md` or to `qor/references/`. Suggest: L1=cosmetic/scope-limited, L2=structural, L3=security-critical.

#### Issue #14 — Missing JSON template

**Location**: `references/qor-audit-templates.md`
**Severity**: MEDIUM

Templates file has prose AUDIT_REPORT, ledger entry, shadow genome entry templates but NO JSON template matching `audit.schema.json`. Auditors writing the gate artifact (Gap #1) have no reference shape.

**Action**: Append an "Audit Gate Artifact JSON Template" section to `references/qor-audit-templates.md`.

### Redundancy

#### Issue #15 — Repeated template references

**Location**: SKILL.md Steps 4, 5, 6, 7
**Severity**: COSMETIC

`Template: references/qor-audit-templates.md` appears 4 times. Could consolidate into a single "All output formats use `references/qor-audit-templates.md` templates — see that file for §AUDIT_REPORT, §LEDGER ENTRY, §SHADOW GENOME ENTRY, §FINAL REPORT, and §AUDIT JSON (when added)."

#### Issue #16 — "QL Audit Templates" header (Qore-sweep miss)

**Location**: `references/qor-audit-templates.md:1`
**Severity**: COSMETIC

Heading: `# QL Audit Templates` — pre-rename leftover. Phase 7 sweep didn't catch this because "QL" (uppercase, no hyphen) wasn't in the rule set.

**Action**: Update to `# QorLogic Audit Templates`. Also surface the broader gap — the Phase 7 rename rules missed standalone "QL" tokens. Worth a separate sweep.

#### Issue #17 — Constraints section incomplete

**Location**: SKILL.md:204-211
**Severity**: MEDIUM

Constraints don't reference the new infra introduced in Phases 3/7/9: no rule about "ALWAYS write audit.json", "ALWAYS validate via schema", "ALWAYS reference delegation-table for handoffs".

**Action**: Add 3-4 constraint lines covering gate artifact write, schema validation, delegation-table compliance.

#### Issue #18 — Success Criteria incomplete

**Location**: SKILL.md:215-223
**Severity**: MEDIUM

Doesn't include: "[ ] Gate artifact `.qor/gates/<session>/audit.json` written and validates against `audit.schema.json`".

**Action**: Add corresponding criterion.

### Other observations

- **Issue #19**: SKILL.md line 184 — "On PASS verdict overall: next phase is `/qor-implement`" appears at the end of Orphan Detection rather than in Step 4 (Generate Verdict) or Step 7 (Final Report). Logically misplaced.
- **Issue #20**: Step 0 → Step 1.a Python continuity is implicit. The pseudocode reads as one Python flow but spans markdown headers; could confuse.
- **Issue #21**: Skill block duplicates info already in frontmatter (`<phase>`, `<persona>`). Either is the canonical source — pick one and refactor the other to a display-only role.
- **Issue #22**: No test coverage for the audit skill's runtime wiring beyond `test_qor_audit_runtime.py` (11 tests). No test verifies that the documented Step 4 "write gate artifact" instruction actually exists in the skill text. Would be a good docstring-style integration test.
- **Issue #23**: Workflow-bundle perspective — `qor-deep-audit-recon` ends at RESEARCH_BRIEF, then `qor-deep-audit-remediate` invokes `/qor-plan` → `/qor-audit`. The audit step inside a bundle has different expectations (auditing a remediation plan, not original feature work). SKILL.md doesn't acknowledge this context-specific use.

## Blueprint Alignment

| Claim | Reality | Status |
|---|---|---|
| `gate_writes: audit` (frontmatter) | No step writes `.qor/gates/<sid>/audit.json` | **DRIFT** |
| References `adversarial-mode.md` | File does not exist | **DRIFT** |
| Source path `processed/skills-output/qor-audit` | `processed/` deleted in Phase 7 cutover | **DRIFT** |
| Category `development` | Skill is in `governance/` dir, sibling skills are `governance` | **DRIFT** |
| Output `.agent/staging/AUDIT_REPORT.md` | Predates SSoT; co-exists with .qor/gates/ structured artifact | **DRIFT** (coexistence undocumented) |
| Step 6 writes to `docs/SHADOW_GENOME.md` | Correct file, but conflation risk with PROCESS_SHADOW_GENOME | MATCH (with ambiguity) |
| Phase 7/9 wiring complete | Step 0 + Step 1.a present, but no `## Delegation` section like sibling skills | **PARTIAL** |
| Token-efficiency doctrine | Skill body is terse; templates duplicated 4x | MATCH (minor cleanup) |

## Recommendations

Sorted by severity:

1. **CRITICAL** — Add gate-artifact write step (Gap #1). Add `write_audit_artifact` helper to `qor_audit_runtime.py`. Add criterion to Success Criteria.
2. **CRITICAL** — Resolve adversarial-mode.md ghost (Gap #2). Author the stub or remove the reference.
3. **MEDIUM** — Update frontmatter: `category: governance`, `source.path: qor/skills/governance/qor-audit` (Gaps #3, #4).
4. **MEDIUM** — Document both output destinations explicitly (Issue #5).
5. **MEDIUM** — Add `## Delegation` section per Phase 9 doctrine consistency (Issue #8).
6. **MEDIUM** — Reference `ledger_hash.py`, `validate_gate_artifact.py`, optionally `check_shadow_threshold.py` (Issues #9, #10, #11).
7. **MEDIUM** — Add JSON template to `qor-audit-templates.md` (Issue #14). Include Risk Grade rubric (Issue #13).
8. **MEDIUM** — Define methodology for Razor "estimate" (Issue #12).
9. **MEDIUM** — Augment Constraints + Success Criteria with new infra references (Issues #17, #18).
10. **LOW/COSMETIC** — Disambiguate shadow logs (#6), align phase labels (#7), consolidate template refs (#15), fix "QL" leftover (#16), reposition PASS-next-action prose (#19).
11. **TECH-DEBT** — Reconcile skill-block + frontmatter duplication doctrine (Issue #21). Add documentation-integration test (Issue #22).
12. **DOCTRINE EXTENSION** — Document bundle-context expectations (Issue #23).

## Updated Knowledge

The Phase 7 rename sweep missed standalone "QL" tokens (uppercase, no hyphen). Worth a follow-up minor sweep covering: `QL`, `qore` (lowercase, non-prefix). Add to the next rename phase if scope warrants.

The pattern of "gate_writes declared but never executed" likely applies to other skills too — should be checked across `qor-research`, `qor-plan`, `qor-implement`, `qor-substantiate`, `qor-validate`. This is **systemic gap #1** and may be the most important Phase 11 finding.

---

_Research advisory. Findings inform the next `/qor-plan` invocation to remediate. No ledger entry written; remediation plan will reference this brief and emit its own ledger entry per chain protocol._
