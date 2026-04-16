# Shadow Attribution Doctrine

Classification criteria for Process Shadow Genome events.

## 1. Purpose

Two structured log files exist for process shadow events:

- `docs/PROCESS_SHADOW_GENOME_UPSTREAM.md` — events attributable to Qor-logic artifacts.
- `docs/PROCESS_SHADOW_GENOME.md` — events attributable to consumer codebase or LLM-intrinsic behavior.

The cross-repo collector reads UPSTREAM only. LOCAL events are the consumer's responsibility.

## 2. UPSTREAM classification

A failure is UPSTREAM when it implicates a Qor-logic artifact: skill prompt text, doctrine rule, gate/bundle logic, helper script behavior, or reference pattern.

Worked example: "Agent produced an orphan file because `qor-implement` Step 4 did not check entry-point import chain."

## 3. LOCAL classification

A failure is LOCAL when it implicates consumer codebase, LLM-intrinsic behavior (hallucination, context loss), or integration-site wiring.

Worked example: "Agent misspelled a project-specific variable name; not attributable to Qor-logic skill text."

## 4. Ambiguity tiebreak

If unclear, default LOCAL. Re-classify to UPSTREAM only if a Qor-logic artifact change would have prevented the failure.

## 5. File routing

- UPSTREAM events go to `docs/PROCESS_SHADOW_GENOME_UPSTREAM.md`.
- LOCAL events go to `docs/PROCESS_SHADOW_GENOME.md`.

## 6. Out of scope

`docs/SHADOW_GENOME.md` (the narrative VETO failure-pattern log) is unchanged and not subject to attribution classification. It records audit failure patterns, not structured process events.
