## Phase 17a v2 — Doctrine Completion (remediation of Entry #44 VETO)

**change_class**: feature
**Status**: Active
**Author**: QorLogic Governor
**Date**: 2026-04-16
**Branch**: `phase/17a-doctrine-completion`
**Supersedes**: `docs/plan-qor-phase17a-doctrine-completion.md` (VETO'd — Entry #44)

## Open Questions

None. Entry #44 surfaced SG-038 (prose-code mismatch in plans) — included in scope alongside SG-036/037 per "doctrine completion" theme.

## Delta from v1 (inline-grounded)

v2 fixes the two Entry #44 violations and expands scope to include SG-038.

### V-1 closure: Track B code block matches prose + adds SG-038

**Audit prescription** (verbatim): "Replace the Track B code block with the full 11-ID list".

v2 Track B code (now 12 IDs including SG-038):

```python
for sg in ("SG-016", "SG-017", "SG-019", "SG-020", "SG-021",
          "SG-032", "SG-033", "SG-034", "SG-035",
          "SG-036", "SG-037", "SG-038"):
    assert sg in body, f"Doctrine must contain {sg}"
```

Grounded 2026-04-16: doctrine currently contains 9 SG sections (`grep -c "SG-" qor/references/doctrine-shadow-genome-countermeasures.md` → 9 hits for the 016/017/019/020/021/032/033/034/035 set; SG-017 and SG-020 share a combined header). Track A adds 3 new sections (036, 037, 038) → 12 total.

### V-2 closure: arithmetic correction

**Audit prescription** (verbatim): "+2 new, baseline 231 → **233 passing**".

v2 Track B + Track C now add 3 proximity-anchored tests (036, 037, 038), not 2. Revised math:

- 3 new tests (sg036, sg037, sg038 proximity anchors)
- 1 updated test (`test_doctrine_lists_all_sg_ids` — same function name, expanded coverage, no count change)
- 1 rewritten test (`test_governance_doctrine_documents_github_hygiene` — same function name, new anchor, no count change)

**Net: +3 test functions. Baseline 231 → 234 passing.** Distinction between new vs. updated tests held explicit in success criteria.

## Track A — Add SG-036, SG-037, SG-038 to doctrine (v2: includes SG-038)

### Affected Files

- `qor/references/doctrine-shadow-genome-countermeasures.md` — three new sections at end

### Changes

Append three sections following the existing SG entry pattern:

**SG-036: doctrine adoption grace period**. A doctrine codified in phase N does not become automatically load-bearing in phase N+1 unless the author treats it as active. "I'll verify during implementation" is a deferral, not compliance. The Grounding Protocol requires inline citation at plan-authoring time, not implementation time. **Countermeasure**: treat newly codified doctrine as active immediately; run all grep/read verifications inline with date-stamped provenance. **Verification hint**: plan body contains phrases like "grounded via `wc -l`" or "verified 2026-MM-DD" for every file-size/phrase-location claim. Source incident: Phase 16 v1 (Entry #40 V-1).

**SG-037: knowledge-surface drift**. Doctrine tests anchored to a single file produce false negatives when refactoring moves knowledge across files. The test asserts `"phase/" in SKILL_A.read_text()`; refactor extracts the content to `SKILL_A_references.md`; test fails on a refactor that preserved the knowledge surface. **Countermeasure**: doctrine tests must check the combined knowledge surface, not a single file. Read both the canonical skill and its declared companion references. **Verification hint**: test reads `skill_body + extensions_body` (or equivalent combined surface) before asserting. Source incident: Phase 16 Track C refactor (Entry #42 implementation note).

**SG-038: prose-code mismatch in plans**. A plan document encodes the same spec in two places: prose descriptions and code blocks. These drift independently when the author edits mid-draft. Prose says "test covers 11 IDs"; code block lists 9; implementer following code produces partial coverage while prose claims full. **Countermeasure**: when a plan updates a list, enumeration, or count, grep the plan for every occurrence of that element and update all copies in lockstep. Prose + code + success criteria must cite the same values. **Verification hint**: Judge cross-checks prose claims against code blocks during audit (Track Verdict Verification); any mismatch is VETO-grade. Source incident: Phase 17a v1 (Entry #44 V-1).

Net delta: +~30 lines across three sections. File size transition: 69 → ~99. Well under Razor 250.

## Track B — Doctrine-content tests (v2 with full 12-ID coverage)

### Affected Files

- `tests/test_shadow_genome_doctrine.py` — update existing + add 3 proximity anchors

### Changes

Update `test_doctrine_lists_all_sg_ids`:

```python
for sg in ("SG-016", "SG-017", "SG-019", "SG-020", "SG-021",
          "SG-032", "SG-033", "SG-034", "SG-035",
          "SG-036", "SG-037", "SG-038"):
    assert sg in body, f"Doctrine must contain {sg}"
```

Add three proximity-anchored tests:

- `test_doctrine_documents_sg036_grace_period` — regex `SG-036.{0,500}(grace period|deferral|inline)` matches.
- `test_doctrine_documents_sg037_surface_drift` — regex `SG-037.{0,500}(surface|moves|combined)` matches.
- `test_doctrine_documents_sg038_prose_code_mismatch` — regex `SG-038.{0,500}(prose|code block|lockstep)` matches.

Anchor keyword grounding (verified against Track A draft text above):
- SG-036 section uses "grace period" (section header), "deferral" (body), "inline citation" (body). All three match.
- SG-037 section uses "surface" (multiple), "moves knowledge" (body), "combined knowledge surface" (body). All three match.
- SG-038 section uses "prose" (multiple), "code block" (multiple), "lockstep" (body). All three match.

## Track C — Sweep `test_skill_doctrine.py` (unchanged from v1)

### Affected Files

- `tests/test_skill_doctrine.py` — line 265 anchor fix

### Changes

Grounded 2026-04-16 via `grep -n "in text\|in body" tests/test_skill_doctrine.py` → 12 hits. Line 265 is the only one requiring fix:

```python
def test_governance_doctrine_documents_github_hygiene():
    text = GOV_DOCTRINE.read_text(encoding="utf-8").lower()
    import re
    for keyword in ("issue label", "pr description", "branch name", "tag annotation"):
        assert re.search(rf"github hygiene.{{0,1500}}{re.escape(keyword)}", text, re.DOTALL), (
            f"doctrine-governance-enforcement.md 'GitHub hygiene' section must contain: {keyword!r}"
        )
```

Grounded: `doctrine-governance-enforcement.md` contains a "GitHub hygiene" section header. 1500-char window accommodates longer section body than the 500-char proximity default used for SG sections.

Other 11 hits in `test_skill_doctrine.py` are narrow-keyword substantive checks (filenames, function names) — no action needed.

## Affected Files (summary)

### New
None.

### Modified (3)
- `qor/references/doctrine-shadow-genome-countermeasures.md` (+~30 lines: SG-036 + SG-037 + SG-038 sections)
- `tests/test_shadow_genome_doctrine.py` (+3 new tests + 1 updated test; +~22 lines)
- `tests/test_skill_doctrine.py` (line 265 anchored)

## Constraints

- **Inline grounding**: every file-size, line count, and keyword-location claim cites grep/read provenance (SG-016 + SG-036 active).
- **Tests before code** for the 3 new proximity-anchor tests.
- **W-1 literal-keyword discipline**: doctrine body contains SG IDs + anchor keywords matched verbatim by regex.
- **Prose-code lockstep**: plan prose, code blocks, and success criteria all cite the same 12-ID list (SG-038 dogfood: this v2 is the first plan authored under the SG-038 rule).
- **Reliability**: pytest 2x consecutive identical results before commit.

## Success Criteria

- [ ] Doctrine file contains SG-036, SG-037, SG-038 sections with proximity-anchorable keywords.
- [ ] `test_doctrine_lists_all_sg_ids` covers all 12 SG IDs (016, 017, 019, 020, 021, 032, 033, 034, 035, 036, 037, 038).
- [ ] `test_doctrine_documents_sg036_grace_period`, `test_doctrine_documents_sg037_surface_drift`, `test_doctrine_documents_sg038_prose_code_mismatch` all green.
- [ ] `test_governance_doctrine_documents_github_hygiene` rewritten with proximity anchor, still green.
- [ ] Tests: **+3 new** (sg036, sg037, sg038). Baseline 231 → **234 passing**, skipped unchanged.
- [ ] `check_variant_drift.py` clean after `BUILD_REGEN=1`.
- [ ] `ledger_hash.py verify` chain valid.
- [ ] Substantiation: `0.6.0 → 0.7.0`; annotated tag `v0.7.0`.

## CI Commands

```bash
python -m pytest tests/test_shadow_genome_doctrine.py tests/test_skill_doctrine.py -v
python -m pytest tests/
BUILD_REGEN=1 python qor/scripts/check_variant_drift.py
python qor/scripts/ledger_hash.py verify docs/META_LEDGER.md
git tag --list 'v*' | tail -3
```
