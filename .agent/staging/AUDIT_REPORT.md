# AUDIT REPORT — plan-qor-phase14-shadow-attribution.md

**Tribunal Date**: 2026-04-15
**Target**: `docs/plan-qor-phase14-shadow-attribution.md`
**Risk Grade**: L1 (scope-incomplete; pipeline survey missing)
**Auditor**: The QorLogic Judge

---

## VERDICT: **VETO**

---

### Executive Summary

Design direction is sound (dual-file schema confirmed in dialogue). VETO issued because plan surveys only 1 of 5 shadow-pipeline scripts and 1 of 2 shadow-tracking skills — the other 4 scripts + 1 skill still read/write the legacy single-path model. Shipping Phase 14 as drafted leaves the pipeline internally inconsistent: collector reads upstream, threshold-checker and issue-updater write to legacy. This is an SG-021 pattern recurrence (multi-layer edit compressed into a single verb that hides which files need editing). Also 2 spec-level defects. Remediation reduces ambiguity and expands scope to the verified pipeline surface.

### Audit Results

#### Security / Ghost UI / Dependency Passes
**Result**: PASS. No new dependencies. No credentials or placeholder auth.

#### Section 4 Razor
Planned changes: doctrine markdown (one file, ~60 lines est.); collector single-constant edit + small fallback block (~10 lines est.); 2 SKILL.md edits (cosmetic). **Result**: PASS.

#### Macro-Level / Orphan Passes
**Result**: FAIL — see V-1 (pipeline scope incomplete).

### Violations Found

| ID | Category | Location | Description |
|---|---|---|---|
| V-1 | Scope-incomplete (SG-021 recurrence) | §Track C + §Affected Files | Plan changes `SHADOW_LOG_REL` in `collect_shadow_genomes.py` only. Grep confirms 5 scripts reference `PROCESS_SHADOW_GENOME`: `collect_shadow_genomes.py`, `check_shadow_threshold.py:2`, `shadow_process.py:20` (hardcoded `LOG_PATH = REPO_ROOT / "docs" / "PROCESS_SHADOW_GENOME.md"`), `create_shadow_issue.py:9` (updates events in-file), `gate_chain.py`. After the plan's edit, `collect_shadow_genomes.py` reads UPSTREAM but `shadow_process.py` still writes LEGACY only (its `LOG_PATH` is a fixed constant, not classification-aware). The `qor-shadow-process` SKILL.md will instruct routing to two files, but the Python helper it wraps cannot split writes. Pipeline is internally inconsistent. Required: plan must survey and disposition ALL 5 scripts. `shadow_process.py` needs a `log_path_for(attribution)` helper; `check_shadow_threshold.py` and `create_shadow_issue.py` need to know which file (or both files) to operate on. |
| V-2 | Scope-incomplete (skills) | §Affected Files | Plan modifies `qor-shadow-process/SKILL.md` + `qor-audit/SKILL.md`. Grep confirms 2 additional skill files reference shadow-genome paths: `qor/skills/memory/track-shadow-genome.md` + `qor/skills/meta/qor-meta-track-shadow/SKILL.md`. These are user-invocable skills that instruct agents where to log. Leaving them pointing at the single-file model leaves agents writing to the wrong file ~50% of the time. Required: audit both skills; update or explicitly disposition (out-of-scope with rationale). |
| V-3 | Self-contradiction | §Track C "Changes" | Plan says: "Single-line edit. Consumer repos without upstream file produce zero events (graceful); collector skips missing files." Immediately followed by: "Add fallback read of legacy `PROCESS_SHADOW_GENOME.md` only if upstream file is missing AND legacy has entries → warn operator..." Two sentences, contradictory specs. Either it's a single-line constant change OR it's a multi-line conditional with fallback + warning. Required: pick one; if fallback is wanted, describe the conditional explicitly and add a test (`test_collector_warns_on_legacy_only`). |
| V-4 | Doctrine scope omission | §Track A doctrine §5 | §5 "File routing: UPSTREAM → PROCESS_SHADOW_GENOME_UPSTREAM.md; LOCAL → PROCESS_SHADOW_GENOME.md." Does not mention narrative `docs/SHADOW_GENOME.md` (the VETO failure-pattern log written by `/qor-audit` Step 6). Plan text claims narrative file is "out of scope" but the doctrine itself should say so explicitly — otherwise an agent reading the doctrine may route VETO narrative entries into one of the two structured files. Required: add §6 "Out of scope" stating `docs/SHADOW_GENOME.md` (narrative) is unchanged and not subject to attribution classification. |
| V-5 | gate_writes frontmatter syntax | §Track B changes | Plan proposes: `gate_writes: docs/PROCESS_SHADOW_GENOME.md (append-only) OR docs/PROCESS_SHADOW_GENOME_UPSTREAM.md (append-only)`. The `OR` syntax is not an existing convention; grep `gate_writes:` across all SKILL.md files to confirm existing patterns use single path or comma-separated list. Required: verify the existing convention (likely comma-separated or a list in YAML frontmatter); use that. If YAML list, the frontmatter parser must tolerate it — verify `qor_audit_runtime.py` or whichever reads frontmatter. |

### Required Remediation

1. **V-1**: Add §Track C.1–C.5 with one subsection per script (`collect_shadow_genomes.py`, `shadow_process.py`, `check_shadow_threshold.py`, `create_shadow_issue.py`, `gate_chain.py`). Each states: current behavior, required change (or explicit no-op with rationale). `shadow_process.py` requires a classification-aware write path (e.g., `append_event(event: dict)` reads `event["attribution"]` and picks the file). Add corresponding tests.
2. **V-2**: Survey `qor/skills/memory/track-shadow-genome.md` and `qor/skills/meta/qor-meta-track-shadow/SKILL.md`. Either update both to reference the doctrine + dual files, OR explicitly disposition as out-of-scope with rationale. Add doctrine-test `test_shadow_tracking_skills_reference_attribution_doctrine`.
3. **V-3**: Resolve contradiction. Recommend: keep the fallback (graceful rollout matters). Rewrite Track C as explicit conditional: if upstream exists → use it; elif legacy has entries → emit a stderr warning + read legacy for this cycle; else → zero events. Add `test_collector_warns_on_legacy_only`.
4. **V-4**: Add doctrine §6 "Out of scope" declaring `docs/SHADOW_GENOME.md` narrative log unchanged. Add test `test_doctrine_declares_narrative_log_out_of_scope` (substring match on `out of scope` + narrative filename).
5. **V-5**: Grep existing `gate_writes:` syntax in repo; use established convention. If no multi-path convention exists, propose one explicitly and add a parser-tolerance test.

### Verdict Hash

**Content Hash**: `64e47b223beb7157f47a241b8f85837a55ce8ddc580f461ffec3aeadb74e9b9a`
**Previous Hash**: `8b2a94f300881845c097cacbebf00648da87fa8e427f8d77cea6e866102b63dd`
**Chain Hash**: `54ef6a4281b361dea2f5c704d5b962caf4d278a87272ba87654b3317674a7d1b`
(sealed as Entry #31)

---
_This verdict is binding._
