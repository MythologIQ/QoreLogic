## Phase 14 — Shadow Attribution (dual Process Shadow Genome)

**change_class**: feature
**Status**: Active
**Author**: QorLogic Governor
**Date**: 2026-04-15
**Branch**: `phase/14-shadow-attribution`

## Open Questions

None. Design validated in dialogue: (c) dual-file schema; new doctrine file for attribution; scope limited to `PROCESS_SHADOW_GENOME.md` (the collector's target); narrative `SHADOW_GENOME.md` unchanged.

## Context

The cross-repo collector (`qor/scripts/collect_shadow_genomes.py:39`) reads `docs/PROCESS_SHADOW_GENOME.md` from every consumer and pools unaddressed events. Today it pools everything — including failures attributable to the consumer's own codebase or LLM-intrinsic behavior, not to Qor-logic artifacts. This repo should only receive events Qor-logic can act on: prompt text, doctrine rules, gate/bundle logic, or helper behavior.

## Track A — Attribution doctrine + upstream file

### Affected Files

- `qor/references/doctrine-shadow-attribution.md` (new) — classification criteria
- `docs/PROCESS_SHADOW_GENOME_UPSTREAM.md` (new, empty starter with frontmatter comment)

### Changes

`doctrine-shadow-attribution.md` (5 sections):

1. **Purpose** — why two files exist; collector reads upstream only.
2. **UPSTREAM classification** — failure implicates a Qor-logic artifact: skill prompt text, doctrine rule, gate/bundle logic, helper script behavior, reference pattern. Worked example: "agent produced an orphan file because qor-implement Step 4 didn't check entry-point import chain."
3. **LOCAL classification** — failure implicates consumer codebase, LLM-intrinsic behavior (hallucination, context loss), or integration-site wiring. Worked example: "agent misspelled a project-specific variable name; not attributable to Qor-logic skill text."
4. **Ambiguity tiebreak** — if unclear, default LOCAL; re-classify only if Qor-logic artifact change would have prevented the failure.
5. **File routing** — UPSTREAM → `docs/PROCESS_SHADOW_GENOME_UPSTREAM.md`; LOCAL → `docs/PROCESS_SHADOW_GENOME.md`.

Starter `PROCESS_SHADOW_GENOME_UPSTREAM.md`: header + frontmatter comment noting purpose and link to doctrine.

## Track B — Skill wiring

### Affected Files

- `qor/skills/governance/qor-shadow-process/SKILL.md` — attribution step added before file write
- `qor/skills/governance/qor-audit/SKILL.md` — Step 6 Shadow Genome branch (narrative still goes to `SHADOW_GENOME.md`; noted for clarity — no behavior change for narrative file)

### Changes

`qor-shadow-process/SKILL.md` gains a classification step:

> Before appending the event, classify attribution per `qor/references/doctrine-shadow-attribution.md`. UPSTREAM → `docs/PROCESS_SHADOW_GENOME_UPSTREAM.md`. LOCAL → `docs/PROCESS_SHADOW_GENOME.md`. When in doubt, LOCAL.

Frontmatter `gate_writes` widened: `docs/PROCESS_SHADOW_GENOME.md (append-only) OR docs/PROCESS_SHADOW_GENOME_UPSTREAM.md (append-only)`.

`qor-audit/SKILL.md` Step 6 gains one line noting narrative `SHADOW_GENOME.md` entries are out of scope for collector (narrative, not structured); no file change to Step 6 behavior.

## Track C — Collector filter

### Affected Files

- `qor/scripts/collect_shadow_genomes.py` — read upstream file, not local

### Changes

Change constant `SHADOW_LOG_REL = "docs/PROCESS_SHADOW_GENOME.md"` → `SHADOW_LOG_REL = "docs/PROCESS_SHADOW_GENOME_UPSTREAM.md"`. Single-line edit. Consumer repos without upstream file produce zero events (graceful); collector skips missing files.

Add fallback read of legacy `PROCESS_SHADOW_GENOME.md` only if upstream file is missing AND legacy has entries → warn operator that classification is pending. Simple conditional; no silent data loss during rollout.

## Track D — Tests

### `tests/test_shadow_attribution.py` (new, 5 tests)

- `test_doctrine_shadow_attribution_exists` — file exists at `qor/references/doctrine-shadow-attribution.md`.
- `test_doctrine_shadow_attribution_defines_both_classes` — body contains literal substrings `UPSTREAM` and `LOCAL` (uppercase as defined in doctrine).
- `test_doctrine_shadow_attribution_has_worked_examples` — body contains at least two occurrences of the substring `Worked example` (one per class).
- `test_collector_reads_upstream_file` — `collect_shadow_genomes.py` contains the string `PROCESS_SHADOW_GENOME_UPSTREAM.md`.
- `test_upstream_file_exists` — `docs/PROCESS_SHADOW_GENOME_UPSTREAM.md` exists.

### `tests/test_skill_doctrine.py` (2 tests added)

- `test_shadow_process_skill_documents_attribution` — `qor-shadow-process/SKILL.md` body references `doctrine-shadow-attribution.md` or the word `UPSTREAM`.
- `test_shadow_process_skill_documents_both_log_files` — `qor-shadow-process/SKILL.md` body references both `PROCESS_SHADOW_GENOME.md` and `PROCESS_SHADOW_GENOME_UPSTREAM.md`.

## Affected Files

### Track A (2 new)
- `qor/references/doctrine-shadow-attribution.md`
- `docs/PROCESS_SHADOW_GENOME_UPSTREAM.md`

### Track B (2 modified)
- `qor/skills/governance/qor-shadow-process/SKILL.md`
- `qor/skills/governance/qor-audit/SKILL.md`

### Track C (1 modified)
- `qor/scripts/collect_shadow_genomes.py`

### Track D (1 new + 1 modified)
- `tests/test_shadow_attribution.py` (5 tests)
- `tests/test_skill_doctrine.py` (2 new tests)

## Constraints

- **No breaking change to narrative `docs/SHADOW_GENOME.md`** (out of scope).
- **Tests before code** for `test_shadow_attribution.py`.
- **Reliability check**: pytest 2x consecutive identical results before commit.
- **W-1 discipline** (Phase 13 carryover): doctrine literal strings must match test substrings verbatim.
- **Rule 4 compliance**: collector filter change = new rule (only upstream-attributed events flow); test `test_collector_reads_upstream_file` enforces it.

## Success Criteria

- [ ] `qor/references/doctrine-shadow-attribution.md` exists with 5 sections; body contains `UPSTREAM`, `LOCAL`, and ≥2 `Worked example` occurrences.
- [ ] `docs/PROCESS_SHADOW_GENOME_UPSTREAM.md` exists as empty starter.
- [ ] `qor-shadow-process/SKILL.md` documents attribution classification + both log file paths.
- [ ] `qor-audit/SKILL.md` Step 6 clarifies scope (narrative vs. structured).
- [ ] `collect_shadow_genomes.py` reads `PROCESS_SHADOW_GENOME_UPSTREAM.md`; graceful fallback warning when only legacy file present.
- [ ] `tests/test_shadow_attribution.py` 5 tests passing.
- [ ] `tests/test_skill_doctrine.py` 2 new tests passing.
- [ ] Full suite: **209 passing + 6 skipped** (baseline 202 + 5 + 2 = 209).
- [ ] `check_variant_drift.py` clean (variants regenerated).
- [ ] `ledger_hash.py verify` chain valid.
- [ ] Substantiation: `0.3.0 → 0.4.0` + annotated tag `v0.4.0`.

## CI Commands

```bash
python -m pytest tests/test_shadow_attribution.py tests/test_skill_doctrine.py -v
python -m pytest tests/
python qor/scripts/check_variant_drift.py
python qor/scripts/ledger_hash.py verify docs/META_LEDGER.md
git tag --list 'v*' | tail -3
```
