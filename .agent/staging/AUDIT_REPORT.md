# AUDIT REPORT — research-brief-full-audit-2026-04-15.md

**Tribunal Date**: 2026-04-15
**Target**: `docs/research-brief-full-audit-2026-04-15.md`
**Risk Grade**: L1 (precision + completeness defects; brief is substantively sound)
**Auditor**: The QorLogic Judge

---

## VERDICT: **VETO**

---

### Executive Summary

Brief surfaces a real and consequential systemic gap (S-1 — gate_writes never executed) and a coherent set of doc-rot patterns. Substantively correct on most claims. **VETO** is for precision defects: count over-claims, conflations of doctrine with gaps, and one missing meta-finding the user has independently surfaced ("tests passed"). Brief is salvageable with targeted edits, not rewrite.

### Audit Results

#### Security Pass
**Result**: PASS. No L3 violations (research doc, no auth/secrets surface).

#### Ghost UI Pass
**Result**: N/A (research doc).

#### Section 4 Razor Pass
**Result**: PASS. Brief is 233 lines; recommendations are scannable; no nested ternaries.

#### Dependency Pass
**Result**: PASS. No new code or deps proposed in scope.

#### Macro-Level Coherence Pass
**Result**: FAIL. See V-1 through V-3 below.

#### Orphan Pass (evidence backing each finding)
**Result**: FAIL. See V-4.

### Violations Found

| ID | Category | Location | Description |
|---|---|---|---|
| V-1 | Precision | brief §S-1 | Count claims 9 affected skills; verified actual count is **8**. `qor-shadow-process` declares `gate_writes: docs/PROCESS_SHADOW_GENOME.md(append-only)` — that's a free-form path to a JSONL log, not a `.qor/gates/<sid>/<phase>.json` artifact. Brief's filter swept it in incorrectly. |
| V-2 | Doctrine conflation | brief §S-8 | "16 skills missing from delegation-table" treats cross-cutting and bundle skills as gaps. Brief later acknowledges this ("Some legitimately don't have a fixed handoff") but the headline count remains misleading. The actual gap is "table doesn't acknowledge cross-cutting skills exist", not "16 missing rows". |
| V-3 | Doctrine over-claim | brief §S-12 | "Most agents have NO /qor-* refs" treats this as a defect. Whether agents should reference invoking skills is a doctrine choice, not a doctrine-violation. Brief should propose adopting the doctrine first; only then can absence be a gap. |
| V-4 | Evidence | brief throughout | qor-research protocol Step 4a mandates "file:line for every finding". Brief cites file:line for ~6 of 24 findings; the rest say "many skills" or "X skills". Without citations, future readers can't verify or act precisely. |
| V-5 | Missing meta-finding | brief omits | Tests pass with all these systemic gaps present — therefore test coverage doctrine doesn't include SKILL.md compliance. This is **Systemic Pattern S-14**: tests verify Python module behavior; nothing verifies SKILL.md doctrine compliance (no test asserts "if gate_writes declared, body contains write step"). User surfaced this independently; brief should have caught it. |
| V-6 | Factual | brief §"qor-deep-audit (and sub-bundles)" | Verified `grep "Invoking .qor-deep-audit. directly" qor/skills/meta/qor-deep-audit/SKILL.md` returns 0 matches. Brief implies the prose exists ("§Decomposition mentions sequencing"); the finding-as-stated is correct (sequencing prose IS missing) but the brief's framing under "specific findings" suggests it merely needs polish, not authoring. |

### Required Remediation

1. **V-1**: Recount S-1 to 8 skills; remove `qor-shadow-process` from the affected list.
2. **V-2**: Restructure S-8 — split "missing rows" (3-4 actual table additions: bundles, qor-organize, qor-shadow-process) from "doctrine extension" (cross-cutting acknowledgement section). Headline count drops from 16 to a real number.
3. **V-3**: Either drop S-12 or convert it to a doctrine proposal: "Propose: agents declare 'invoked by /qor-*' line at bottom; affects 13 agents." Without the doctrine, it's not a gap.
4. **V-4**: Add file:line citations for at least the systemic patterns. For S-1 cite one example file:line per affected skill (e.g., `qor-plan/SKILL.md:5`). Spot-check verified count, not full enumeration.
5. **V-5**: Add **Systemic Pattern S-14 — Test coverage doctrine doesn't include SKILL.md compliance**. Recommend new test category: doctrine-compliance tests that grep SKILL.md bodies for required patterns based on frontmatter declarations. Recommendation slots into Phase 11D as item #6.
6. **V-6**: Reword the deep-audit finding to clearly state: "Sequencing prose is absent (verified)." Move from "Specific findings" to either S-class systemic if it applies to other bundles, or keep as specific with the verification noted.

### Verdict Hash

(computed at ledger entry — see Entry #21)

---
_This verdict is binding._
