## Phase 17a — Doctrine Completion (SG-036, SG-037, unanchored-test sweep)

**change_class**: feature
**Status**: Active
**Author**: QorLogic Governor
**Date**: 2026-04-16
**Branch**: `phase/17a-doctrine-completion`

## Open Questions

None. Two failure patterns logged in prior-phase Shadow Genome narrative need codification in the load-bearing doctrine. Sweep scope confirmed via inline grounding (12 unanchored hits in `test_skill_doctrine.py`, most legitimate narrow-keyword checks).

## Context

Grounded 2026-04-16:
- SG-036 (doctrine adoption grace period) logged in `docs/SHADOW_GENOME.md:319` during Entry #40 but absent from `qor/references/doctrine-shadow-genome-countermeasures.md` (69 lines). Narrative-only → not load-bearing.
- SG-037 (knowledge-surface drift) surfaced during Phase 16 implementation when `test_plan_skill_documents_branch_creation` broke after Track C moved content to `step-extensions.md`. Fix applied in `tests/test_skill_doctrine.py` but pattern not codified.
- `tests/test_skill_doctrine.py` (295 lines) contains 12 `in text`/`in body` checks. Most are narrow-keyword substantive checks (filenames, function names) unlikely to drift; sweep confirms or fixes each.

## Track A — Add SG-036 and SG-037 to doctrine

### Affected Files

- `qor/references/doctrine-shadow-genome-countermeasures.md` — two new sections at end

### Changes

Append two sections following the existing SG entry pattern (grounded against existing SG-032, SG-033 structure):

**SG-036: doctrine adoption grace period**. A doctrine codified in phase N does not become automatically load-bearing in phase N+1 unless the author treats it as active. "I'll verify during implementation" is a deferral, not compliance. The Grounding Protocol requires inline citation at plan-authoring time, not implementation time. **Countermeasure**: treat newly codified doctrine as active immediately; run all grep/read verifications inline with date-stamped provenance. **Verification hint**: plan body contains phrases like "grounded via `wc -l`" or "verified 2026-MM-DD" for every file-size/phrase-location claim. Source incident: Phase 16 v1 (Entry #40 V-1).

**SG-037: knowledge-surface drift**. Doctrine tests anchored to a single file produce false negatives when refactoring moves knowledge across files. The test asserts `"phase/" in SKILL_A.read_text()`; refactor extracts the content to `SKILL_A_references.md`; test fails on a refactor that preserved the knowledge surface. **Countermeasure**: doctrine tests must check the combined knowledge surface, not a single file. Read both the canonical skill and its declared companion references. **Verification hint**: test reads `skill_body + extensions_body` (or equivalent combined surface) before asserting. Source incident: Phase 16 Track C refactor (Entry #42 implementation note).

Net delta: +~20 lines. File size transition: 69 → ~89. Well under Razor 250.

## Track B — Doctrine-content tests for SG-036 and SG-037

### Affected Files

- `tests/test_shadow_genome_doctrine.py` — update existing + add proximity anchors

### Changes

Update `test_doctrine_lists_all_sg_ids` to include both new IDs:

```python
for sg in ("SG-016", "SG-017", "SG-019", "SG-020", "SG-021",
          "SG-032", "SG-033", "SG-036", "SG-037"):
    assert sg in body, f"Doctrine must contain {sg}"
```

(Note: SG-034 and SG-035 were added to the doctrine in Phase 15 v2's implementation of Track A. The existing `test_doctrine_lists_all_sg_ids` covers 016/017/019/020/021/032/033 only per Phase 15 v1 plan — this is a gap. Judge-grounded 2026-04-16: the file contains all 9 entries but the test covers only 7. Correcting to cover all 9 existing + 2 new = 11 IDs.)

Add two proximity-anchored tests:

- `test_doctrine_documents_sg036_grace_period` — regex `SG-036.{0,500}(grace period|deferral|inline)` matches within 500-char window of the ID.
- `test_doctrine_documents_sg037_surface_drift` — regex `SG-037.{0,500}(surface|moves|combined)` matches within 500-char window.

Grounded keyword choices: SG-036's narrative entry (`SHADOW_GENOME.md:319`) uses literal phrases "no grace period", "deferral", "inline citation" — any of these work as anchor keywords. SG-037's surface-drift language uses "surface", "moves across files", "combined knowledge surface" — similarly anchored.

## Track C — Sweep `test_skill_doctrine.py` for unanchored checks

### Affected Files

- `tests/test_skill_doctrine.py` (potentially; sweep is read-only unless violations found)

### Changes

Grounded 2026-04-16 via `grep -n "in text\|in body" tests/test_skill_doctrine.py`: 12 hits. Categorization:

| Line | Check | Category | Action |
|---|---|---|---|
| 75-77 | `".qor/gates/" in body` OR `"write_artifact"` OR `"write_gate_artifact"` | Narrow keywords, substantive | No action |
| 119 | `if "processed/skills-output" in text` | Positive conditional, not assertion | No action |
| 202 | `missing = sorted(s for s in expected if s not in text)` | Negative iteration | No action |
| 212 | `if "tools/reliability/" in text` | Absence check (audit) | No action |
| 239 | `"bump_version" in text or "create_seal_tag" in text` | Narrow function names | No action |
| 265 | `for keyword in (...): assert keyword in text` | 4 governance-specific keywords | Consider anchoring (SG-035 risk) |
| 279 | `"doctrine-shadow-attribution.md" in text or "UPSTREAM" in text` | File reference + keyword | No action |
| 286-287 | log file filename checks | Narrow | No action |
| 293 | `"doctrine-shadow-attribution.md" in text` | File reference | No action |

**Finding**: line 265's governance-doctrine keywords (`issue label`, `pr description`, `branch name`, `tag annotation`) are section-specific but not proximity-anchored. Phase 15 W-1 discipline mandates anchoring to prevent SG-035 drift. Fix by replacing the loop with proximity regex:

```python
def test_governance_doctrine_documents_github_hygiene():
    text = GOV_DOCTRINE.read_text(encoding="utf-8").lower()
    # Anchor each keyword to "github hygiene" section header (or document root)
    import re
    for keyword in ("issue label", "pr description", "branch name", "tag annotation"):
        assert re.search(rf"github hygiene.{{0,1500}}{re.escape(keyword)}", text, re.DOTALL), (
            f"doctrine-governance-enforcement.md 'GitHub hygiene' section must contain: {keyword!r}"
        )
```

Grounded: `doctrine-governance-enforcement.md` contains a "GitHub hygiene" section (verified 2026-04-16). The 1500-char window accommodates a longer section than the 500-char doctrine sections.

All other unanchored checks are narrow enough that SG-035 risk is minimal (specific function names, filenames). Documented as "reviewed, safe" — no action.

## Affected Files (summary)

### New
None.

### Modified (3)
- `qor/references/doctrine-shadow-genome-countermeasures.md` (+~20 lines: SG-036 + SG-037 sections)
- `tests/test_shadow_genome_doctrine.py` (+2 tests + 1 updated test; +~15 lines)
- `tests/test_skill_doctrine.py` (Track C fix for line 265 — 1 test replaced with anchored version)

## Constraints

- **Inline grounding**: every file-size, line count, and keyword-location claim cites the grep/read that verified it (SG-016 + SG-036 active).
- **Tests before code** for Track B new tests.
- **W-1 literal-keyword discipline**: doctrine body contains literal SG IDs and countermeasure keywords matched verbatim by proximity regex.
- **Reliability**: pytest 2x consecutive identical results before commit.
- **No behavior changes**: Tracks A/B/C add/strengthen tests; no skill protocol edits.

## Success Criteria

- [ ] Doctrine file contains SG-036 and SG-037 sections with proximity-anchorable keywords.
- [ ] `test_doctrine_lists_all_sg_ids` covers all 11 SG IDs (016, 017, 019, 020, 021, 032, 033, 034, 035, 036, 037).
- [ ] `test_doctrine_documents_sg036_grace_period` and `test_doctrine_documents_sg037_surface_drift` green.
- [ ] `test_governance_doctrine_documents_github_hygiene` rewritten with proximity anchor, still green.
- [ ] Tests: +2 new + 1 updated (doctrine lists) + 1 rewritten (governance hygiene) = effectively +3. Baseline 231 → **234 passing**, skipped unchanged.
- [ ] `check_variant_drift.py` clean after `BUILD_REGEN=1` (doctrine file changed).
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
