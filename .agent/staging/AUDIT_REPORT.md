# AUDIT REPORT — plan-qor-phase17a-doctrine-completion.md

**Tribunal Date**: 2026-04-16
**Target**: `docs/plan-qor-phase17a-doctrine-completion.md`
**Risk Grade**: L1
**Auditor**: The QorLogic Judge

---

## VERDICT: **VETO**

---

### Executive Summary

Plan is sound in intent — codify SG-036 + SG-037, expand `test_doctrine_lists_all_sg_ids` to cover all existing + new IDs, fix line 265's unanchored check. VETO issued for 2 defects. V-1 (critical): plan is self-inconsistent — prose + Success Criteria say "all 11 SG IDs" but the proposed code block in Track B lists only 9, missing SG-034 and SG-035. Implementer following the code literally would produce a test that still fails to cover the doctrine's actual content (the exact defect the plan claims to close). V-2: test count arithmetic is off by one (claims +3, actually +2). Minor, but a phase focused on rigor should get its own arithmetic right.

### Audit Results

#### Security Pass
**Result**: PASS.

#### Ghost UI Pass
**Result**: PASS.

#### Section 4 Razor Pass
**Result**: PASS. Doctrine 69 → ~89; test file deltas small. All under 250.

#### Dependency Pass
**Result**: PASS. No new deps (stdlib `re` + existing).

#### Orphan Pass
**Result**: PASS. All modified files tied to existing test/skill/doctrine chains.

#### Macro-Level Architecture Pass
**Result**: PASS. Doctrine remains single source of truth for SG inventory.

### Violations Found

| ID | Category | Location | Description |
|---|---|---|---|
| V-1 | Self-inconsistency (critical) | Track B code block vs. prose + Success Criteria | Plan's prose says "Correcting to cover all 9 existing + 2 new = 11 IDs" and Success Criteria says "covers all 11 SG IDs (016, 017, 019, 020, 021, 032, 033, 034, 035, 036, 037)". But the proposed code block lists only 9: `("SG-016", "SG-017", "SG-019", "SG-020", "SG-021", "SG-032", "SG-033", "SG-036", "SG-037")` — **missing SG-034 and SG-035**. Judge-grounded 2026-04-16: doctrine contains 9 SG sections (grep `^## SG-` → 8 headers because SG-017/020 share one section header, 9 IDs). An implementer following the code block verbatim would create a test that covers 9 IDs and still leaves SG-034 + SG-035 uncovered — precisely the gap Phase 17a claims to close. This is a case of prose promising X while code does Y (a pattern SG-033 warns about in a different domain). Required: fix the code block to list all 11 IDs as the prose claims. |
| V-2 | Test count arithmetic off by one | Track B + Success Criteria + Constraints | Plan says "+2 new + 1 updated (doctrine lists) + 1 rewritten (governance hygiene) = effectively +3. Baseline 231 → **234 passing**." Pytest counts test functions by name, not by assertion coverage. New test functions: `test_doctrine_documents_sg036_grace_period`, `test_doctrine_documents_sg037_surface_drift` = **2 new**. Updated test (`test_doctrine_lists_all_sg_ids`) keeps the same function name — no count change. Rewritten test (`test_governance_doctrine_documents_github_hygiene`) keeps the same function name — no count change. Actual net: +2. Baseline 231 → 233, not 234. Minor, but Phase 17a's thesis is grounding rigor; arithmetic errors undermine the thesis. |

### Required Remediation

1. **V-1**: Replace the Track B code block with the full 11-ID list:
   ```python
   for sg in ("SG-016", "SG-017", "SG-019", "SG-020", "SG-021",
             "SG-032", "SG-033", "SG-034", "SG-035",
             "SG-036", "SG-037"):
       assert sg in body, f"Doctrine must contain {sg}"
   ```
   Verify match against Success Criteria list.
2. **V-2**: Fix arithmetic. "+2 new, baseline 231 → **233 passing**". Update Success Criteria line accordingly. Keep the distinction between "new test" and "updated test coverage" visible in the explanatory prose, but do not treat updates as net-new tests in the count.

### Verdict Hash

**Content Hash**: `ebfd6293b6802ef60ca040bf2292ec217c2d105d2c2efdeb78dd238852973a7c`
**Previous Hash**: `fe327680d3fbf3dfce652905d9d424ced9738a9bebb031c21b69d07a459f2f2c`
**Chain Hash**: `933dc3773d5865defc272f700a5ef962d31f6ce8563ada4c2782515301f6a725`
(sealed as Entry #44)

---
_This verdict is binding._
