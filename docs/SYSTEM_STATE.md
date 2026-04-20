# Qorlogic System State

**Snapshot**: 2026-04-20
**Chain Status**: ACTIVE (Phase 38 sealing at v0.28.0 — **procedural surface freeze line**)
**Phase**: Phase 33 sealed. Seal-tag timing bug (off-by-one across v0.19.0-v0.22.0) fixed — `governance_helpers.create_seal_tag` now takes a required `commit: str` positional; `/qor-substantiate` Step 7.5 reduced to `bump_version` only; new Step 9.5.5 captures the post-commit SHA via `git rev-parse HEAD` and tags it. Release-doc currency rule added (Phase 33 addition to Step 6.5): when `plan.change_class ∈ {feature, breaking}`, README.md and CHANGELOG.md must appear in `implement.files_touched`; hotfix exempt. SG-Phase33-A records the historical bug + countermeasure; META_LEDGER Entry #112 backfills the 4 affected-tag inventory (historical tags not retagged — rewriting published remote discouraged; no consumer depends on them). 636 tests passing on two consecutive runs (delta +14). First phase branch to start from a reconciliation-merge base (`git merge --no-ff v0.23.0` as Phase 33's first commit) to bring phase/32-amended content back into scope after the PR #4 auto-merge race published pre-amend content to main. Phase 32 prior -- Check Surface D + E are now LIVE STRICT at `/qor-substantiate` Step 4.7 -- any term-drift or cross-doc conflict ABORTs seal. Check Surface D + E are now LIVE STRICT at `/qor-substantiate` Step 4.7 -- any term-drift or cross-doc conflict ABORTs seal. Zero-drift baseline established in Phase 2 via `docs/*.md` archive-by-default scope-fence (only the 4 system-tier docs are living; README + CHANGELOG excluded as narrative entry points) plus broad `referenced_by:` adoption for high-usage terms. Install drift check (`qor/scripts/install_drift_check.py`) SHA256-compares source SKILL.md vs installed copies; invoked as CLI or at `/qor-plan` Step 0.2 as pre-phase WARN. Doctrine §8 Install Currency documents the contract. 622 tests passing on two consecutive runs (delta +20). Phase 32 is the first plan to substantiate under live strict-mode D/E and passed cleanly on first attempt -- the zero-drift baseline held. Previous phase --  Operationalization bundle closes 8 of the 10 items from the post-Phase-30 gap inventory. New machinery: `/qor-substantiate` Step 6.5 Documentation Currency Check (WARNs when doc-affecting changes ship without system-tier doc updates); Check Surface D/E scope-fence tuning (doctrine-peer + home-dir-peer + per-entry scope_exclude); `doc_integrity_drift_report.py` operator CLI; `pr_citation_lint.py` + `.github/workflows/pr-lint.yml` enforcing doctrine-governance-enforcement §6 on every PR; SHA256 install-sync test catching dist drift at CI time; session marker path unified (`MARKER_PATH` = `.qor/session/current`). Live drift triage artifact `docs/phase31-drift-triage-report.md` captures residual-known-drift state. Path-unification migration had a lossy moment at first Phase 31 substantiate attempt (old `.qor/current_session` vs new `.qor/session/current` marker files both exist with different contents; manual migration applied). 602 tests passing on two consecutive runs (delta +29). SG-Phase31-A (in-plan correction parallel to source instead of upstream fix) + SG-Phase31-B (plan self-modification post-audit) codified; both countermeasures applied live during pass-1 VETO -> pass-2 PASS amendment. First seal to exercise Step 6.5 against its own output -- caught 9 currency warnings, system-tier docs amended mid-substantiate.

## Authoritative source

All canonical Qor content lives under `qor/`. Variant outputs (`claude`, `kilo-code`, `codex`) are deferred until Phase 2 re-introduces the compile pipeline.

## File Tree

```
G:/MythologIQ/Qorlogic/
├── qor/                                   Single source of truth
│   ├── skills/
│   │   ├── governance/                    Gate & audit authority
│   │   │   ├── qor-audit/
│   │   │   ├── qor-validate/
│   │   │   ├── qor-substantiate/
│   │   │   ├── qor-shadow-process/        (stub — full impl deferred)
│   │   │   └── qor-governance-compliance/
│   │   ├── sdlc/                          Research → implement cycle
│   │   │   ├── qor-research/
│   │   │   ├── qor-plan/
│   │   │   ├── qor-implement/
│   │   │   ├── qor-refactor/
│   │   │   ├── qor-debug/
│   │   │   └── qor-remediate/             (stub — absorbs qor-course-correct)
│   │   ├── memory/                        State tracking & documentation
│   │   │   ├── qor-status/
│   │   │   ├── qor-document/
│   │   │   ├── qor-organize/
│   │   │   ├── log-decision.md
│   │   │   ├── track-shadow-genome.md
│   │   │   └── qor-docs-technical-writing/
│   │   ├── meta/                          Bootstrapping & repo management
│   │   │   ├── qor-bootstrap/
│   │   │   ├── qor-help/
│   │   │   ├── qor-repo-audit/
│   │   │   ├── qor-repo-release/
│   │   │   ├── qor-repo-scaffold/
│   │   │   ├── qor-meta-log-decision/
│   │   │   └── qor-meta-track-shadow/
│   │   └── custom/                        (reserved; empty until qor-scoped custom content identified)
│   │
│   ├── agents/
│   │   ├── governance/                    qor-governor, qor-judge
│   │   ├── sdlc/                          qor-specialist, qor-strategist, qor-fixer,
│   │   │                                  qor-ux-evaluator, project-planner
│   │   ├── memory/                        qor-technical-writer, documentation-scribe,
│   │   │                                  learning-capture
│   │   └── meta/                          agent-architect, system-architect, build-doctor
│   │
│   ├── vendor/
│   │   ├── agents/                        7 generic specialists + third-party/ (wshobson-agents)
│   │   └── skills/                        ~65 third-party skills (frameworks, integrations,
│   │                                      tauri/, chrome-devtools/, custom/, _system/, agents/)
│   │
│   ├── scripts/
│   │   ├── ledger_hash.py                 Content/chain hashing + manifest generation + verify
│   │   ├── calculate-session-seal.py      Session seal utility
│   │   ├── legacy/                        Pre-migration pipeline (process-skills.py,
│   │   │                                  compile-*.py, admit-skill.py, gate-skill-matrix.py,
│   │   │                                  intent-lock.py)
│   │   └── utilities/                     Assorted utility scripts
│   │
│   ├── references/                        Doctrine + patterns + qor-* examples
│   ├── experimental/                      Non-canonical research (tauri2-state, tauri-launcher, etc.)
│   └── templates/                         Doc templates (ARCHITECTURE_PLAN, CONCEPT, SYSTEM_STATE, etc.)
│
├── docs/
│   ├── META_LEDGER.md                     Hash-chained governance ledger (18 entries)
│   ├── SHADOW_GENOME.md                   Audit-verdict failure records (5 entries)
│   ├── PROCESS_SHADOW_GENOME.md           Process-level failure log (JSONL append-only)
│   ├── SYSTEM_STATE.md                    This file
│   ├── SKILL_REGISTRY.md                  Category-organized skill index
│   ├── ARCHITECTURE_PLAN.md
│   ├── BACKLOG.md
│   ├── CONCEPT.md
│   ├── SKILL_AUDIT_CHECKLIST.md
│   ├── Lessons-Learned/
│   ├── plan-qor-*.md                      Migration plan iterations (v1, v2, v3, final, minimal, deferred)
│   ├── migration-manifest-pre.json        Phase 1.5 pre-move manifest (2176 paths)
│   ├── migration-manifest-post.json       Phase 1.5 post-move manifest (1458 paths)
│   ├── MERKLE_ITERATION_GUIDE.md
│   ├── SHIELD_SELF_AUDIT.md
│   └── archive/2026-04-15/                Pre-migration snapshots (ingest, processed, compiled,
│                                          deployable_state, kilo-code)
│
├── .qor/                                  Runtime state (gitignored)
│   └── migration-discards.log             First-source-wins discard record
│
├── pyproject.toml                         Python 3.11+, pytest config, jsonschema runtime dep
├── .gitignore
└── README.md
```

## Ledger chain head

- Entry #83 SESSION SEAL — Phase 26 substantiated (v0.17.0)
- Chain hash: `047f2f79f636507473704a085d27baef6c087044175d354eadea922afc12feb4`
- Entry #84 BACKFILL — Phase 23 historical annotation (non-advancing; documents `8081422` at `v0.14.0`)
- Verification: `python qor/scripts/ledger_hash.py verify docs/META_LEDGER.md` → all sealable entries OK from #63 through #83

## Shipped tooling

Compile pipeline, gate chain runtime, shadow threshold automation, cross-repo collector, platform detect, and validation suite were all shipped across Phases 10-23. Current tooling surface is operational:

- CLI: `qorlogic install|uninstall|list|init|info|compile|verify-ledger|seed|compliance|policy`
- Python modules: `qor/seed.py`, `qor/tone.py`, `qor/install.py`, `qor/hosts.py`, `qor/scripts/veto_pattern.py`, `qor/scripts/gemini_variant.py`, `qor/scripts/dist_compile.py`, `qor/scripts/ledger_hash.py`, `qor/scripts/shadow_process.py`
- Tests: 462 passing (unit + integration + e2e + doctrine + bundle contract)
- Supported hosts: claude, kilo-code, codex, gemini (all with repo/global scope)
- Communication tiers: technical / standard / plain via `/qor-tone` or `qorlogic init --tone`
- Shadow Genome events: 7 structured `event_type` enum values (incl. `repeated_veto_pattern` from Phase 26)

## Advisory-gate overrides carried

One sev-1 `gate_override` event logged in `docs/PROCESS_SHADOW_GENOME.md` against the 5-round audit loop verdicts on the full plan. User-approved per `/qor-debug` analysis. Remaining violations (V-1..V-5) are addressed in `plan-qor-ssot-minimal.md` or explicitly carried as known risk.

## Phase 36 (v0.26.0 — 2026-04-20): two-stage addressed flip in /qor-remediate

Phase scoped to B19 only after a four-pass audit loop on the original Phase 36 plan (archived at `docs/plan-qor-phase36-planaudit-loop-countermeasures.archived.md`) surfaced V1-V10 across progressively deeper infrastructure-alignment mismatches. `/qor-remediate` Entry #122 proposal was accepted 2026-04-20; scope narrowed.

**Shipped**:
- Schema: `addressed_pending` optional field + `allOf` invariant (`shadow_event.schema.json`); `reviews_remediate_gate` optional field (`audit.schema.json`).
- Script: `remediate_mark_addressed.py` rewritten into two-stage API (`mark_addressed_pending` + `mark_addressed`) with `ReviewAttestationError`. 4 functions each under the Razor 40-line limit.
- Skills: `/qor-remediate` Step 4 calls pending variant; new Step 6 documents review-pass flip invoked from `/qor-audit`. `/qor-audit` Step 4.1 captures `reviews-remediate:<path>` operator arg; Step 4.2 invokes `mark_addressed` on PASS.
- Doctrine: §10.1 "Two-stage remediation flip," §10.2 "Narrative SG entry closure."
- Tests: `test_shadow_event_schema.py` NEW (5 tests); `test_remediate.py` +10 new + 3 existing updated to pending-stage API. 654 passed across 2 consecutive runs (delta +12).

**SG closures**:
- SG-PlanAuditLoop-A: partially closed. B19 ships the first countermeasure (advisory-until-reviewed enforced). C2-C4 (stall detection, cycle-count escalation, CI-command slot) deferred to Phase 37/38.
- SG-Phase36-A: active but not triggered in this phase (narrow B19 scope did not re-expose the specification-drift pattern).

**Deferred** (per BACKLOG post-Phase-35 queue):
- Phase 37: B20/B21 + gate artifact accumulation infrastructure. Plan authored at `docs/plan-qor-phase37-stall-detection-infrastructure.md` — unmerged, unreviewed.
- Phase 38: B22 `ci_commands` schema slot.
- Phase 39: context-discipline doctrine + persona context-prioritization reframe (research brief `.agent/staging/RESEARCH_BRIEF.md`; META_LEDGER #116).

## Phase 37 (v0.27.0 — 2026-04-20): stall-detection infrastructure (B20 + B21)

Closes C2-C4 countermeasures from SG-PlanAuditLoop-A. Phase 36 shipped B19 (two-stage addressed flip) as prerequisite; Phase 37 ships the full stall-detection machinery on append-only audit history.

**Shipped**:
- `qor/scripts/audit_history.py` NEW — append-only `.qor/gates/<sid>/audit_history.jsonl` alongside singleton. Solves V10 from original Phase 36 plan.
- `qor/scripts/findings_signature.py` NEW — 16-hex-char SHA256 prefix over sorted unique `findings_categories`; `"LEGACY"` sentinel for absent field; `UnmappedCategoryError` on non-enum.
- `qor/scripts/stall_walk.py` NEW — shared walker returning `(count, signature, first_match_ts)` for both escalator and classifier.
- `qor/scripts/cycle_count_escalator.py` NEW — K=3 orchestrator + session-scoped suppression marker.
- `qor/scripts/orchestration_override.py` NEW — severity-2 event + suppression marker.
- Schema: `audit.schema.json` `findings_categories` 12-value closed enum + `allOf` required-on-VETO; `shadow_event.schema.json` event_type +`plan-replay` +`orchestration_override`.
- Classifier: `remediate_pattern_match` gate-loop unions `gate_override | orchestration_override`; plan-replay pattern added with gate-loop dedup.
- Skills: `/qor-plan` Step 2c cycle-count hook; `/qor-audit` Step 0.5 cycle-count hook + new 7th Infrastructure Alignment Pass.
- Doctrine: §10.3 audit history + findings signature; §10.4 cycle-count escalation; §10.5 override + suppression; new `SG-InfrastructureMismatch` countermeasure in the catalog.
- Tests: 46 new across 8 new files + 5 new in `test_remediate` + 1 update in `test_audit_gate_artifact`. 705 passed x2.

**SG closures**:
- SG-PlanAuditLoop-A: **fully closed** (C1 Phase 36, C2-C4 Phase 37).
- SG-Phase36-A: active; authoring discipline held.
- SG-InfrastructureMismatch: codified in countermeasure catalog this phase.

**Procedural surface freeze line**: v0.28.0 (after Phase 38). Phase 39 (context-discipline / persona reshape) explicitly deferred pending upstream consumer lockdown.

## Phase 38 (v0.28.0 — 2026-04-20): ci_commands schema slot (B22) — **FREEZE LINE**

Trivial scope: one schema field + one skill template section + one 6-test file. Establishes v0.28.0 as the procedural-surface freeze line per user direction for upstream consumer lockdown.

**Shipped**:
- `qor/gates/schema/plan.schema.json` — `ci_commands` required array (minItems 1, item minLength 1).
- `qor/skills/sdlc/qor-plan/SKILL.md` §Plan Structure — new `## CI Commands` template section + Phase 38 contract note.
- `tests/test_plan_schema_ci_commands.py` NEW (6 tests covering required-field enforcement, empty-array rejection, empty-string rejection, valid-case acceptance, skill-prose lint, grandfathering for pre-Phase-38 markdown plans).
- 9 existing plan-payload test fixtures updated to include `ci_commands` (payloads represent Phase-38-era consumers).
- `CHANGELOG.md` v0.27.0 section authored (Phase 37 debt).

**Procedural surface frozen**:
- Skill protocols (qor-plan/audit/remediate/implement/substantiate) — stable
- Event-type enum (9 values) — stable
- Gate-artifact schemas (plan + ci_commands now required, audit + findings_categories/reviews_remediate_gate, shadow_event + addressed_pending) — stable
- Findings categories enum (12 values) — stable
- Delegation table (108 handoffs) — stable
- Doctrine §10.1-10.5 — stable

**Deferred beyond freeze**:
- Phase 39: context-discipline doctrine + persona reshape (~30 skill files, M4 A/B harness). Explicitly out of scope pending upstream consumer lockdown against v0.28.0.

## Phase 39 Phases 1+2 (v0.29.0 — 2026-04-20): context-discipline doctrine + A/B harness infrastructure

Partial phase seal. Phases 1 and 2 of the 4-phase plan ship in v0.29.0; Phases 3 (live A/B run) and 4 (persona sweep + conditional Identity Activation rewrites) deferred to a separate operator-driven cycle.

**Phase 1 shipped** — doctrine codification:
- `qor/references/doctrine-context-discipline.md` NEW. 5 sections: three-mechanism distinction (frontmatter tag vs Identity Activation prose vs subagent invocation), persona-as-context-prioritization-scaffold rule, stance directive discipline, subagent invocation rule (`general` by default; persona-typed requires evidence), verification protocol requiring `<persona-evidence>` pointers.
- `qor/references/doctrine-governance-enforcement.md` §11 cross-reference.
- `tests/test_doctrine_context_discipline.py` — 3 structural tests.

**Phase 2 shipped** — A/B harness infrastructure (Anthropic SDK):
- `qor/scripts/ab_harness.py` — pure library (5 public functions + helpers), mockable, never reads env. `load_manifest`, `load_variant`, `score_response`, `run(variant, skill, client, ...)`, `compare`, `aggregate_runs`.
- `qor/scripts/ab_live_run.py` — operator CLI. Reads `ANTHROPIC_API_KEY`; exits clearly if absent; builds real `anthropic.Anthropic()` client; runs 2 skills × 2 variants × 5 runs × 20 defects = 400 API calls.
- `tests/fixtures/ab_corpus/` — 20 seeded defects across 10 `findings_categories` (2 per category, omitting `coverage-gap` and `dependency-unjustified` per plan). Each fixture carries `# SEEDED TEST DEFECT — NOT EXECUTABLE` header. `MANIFEST.json` uses `line_start` + `line_end` fields for multi-line defect ranges.
- `tests/fixtures/ab_corpus/variants/` — 4 hand-authored Identity Activation variant files (`qor-audit.persona.md`, `qor-audit.stance.md`, `qor-substantiate.persona.md`, `qor-substantiate.stance.md`).
- `pyproject.toml` — `anthropic>=0.40,<1.0` under `[project.optional-dependencies].ab-harness`. Default installs do not pull this dependency.
- `tests/test_ab_harness.py` — 16 CI tests, all Anthropic calls mocked.

**Deferred (Phase 39b)**:
- Phase 3 (operator action): `ANTHROPIC_API_KEY=... python qor/scripts/ab_live_run.py` produces `docs/phase39-ab-results.md`. Cost ~$32 per full cycle at Opus 4.7 pricing (corrected from plan's earlier ~$4 estimate). ~10-15 min wall-time.
- Phase 4 (conditional on Phase 3 results): S3 persona sweep across 24 skills; R3 Identity Activation rewrites fire only if Phase 3 declares `winner: "stance"`; R4 (qor-debug → doctrine cross-reference); R5 (qor-document persona-vs-agent disambiguation).

**Cost awareness (corrected from Pass 2 audit O1)**: actual skill body sizes are ~4,000-4,500 tokens each, not the plan's original ~500-token per-call assumption. Real cost ~$32 per full A/B cycle at Opus 4.7 pricing. Codified in `ab_harness.py` module docstring.

## Phase 39b Phases 1+2 (v0.30.0 — 2026-04-20): Agent Team A/B + persona sweep

Supersedes the v0.29.0 anthropic-SDK approach. Ships:
- `/qor-ab-run` skill orchestrating A/B via parallel Task-tool subagent dispatch (20 concurrent calls, zero external dep, aligned with doctrine §4 subagent invocation rule).
- `qor/scripts/ab_aggregator.py` pure-Python reducer: brace-balanced JSON extraction, malformed-tolerant, mean+stddev, winner declaration (±5pp tie threshold), markdown rendering.
- Subagent prompt template with `{VARIANT_IDENTITY_ACTIVATION_BLOCK}` + `{FIXTURES_CONCATENATED}` placeholders.
- Delegation-table + `/qor-help` catalog entries.

**Persona sweep applied**:
- **S3**: 5 decorative `<persona>` tags removed (`qor-status`, `qor-help`, `qor-repo-scaffold`, `qor-bootstrap`, `qor-document`).
- **R4**: `qor-debug` line 108 subagent_type constraint cross-references `doctrine-context-discipline.md` §4.
- **R5**: `qor-document` splits Identity Activation stance (main thread) from subagent pairing (`Task` dispatch) citing doctrine §1.2/§1.3.
- **R3 pending**: test `test_identity_activation_matches_ab_winner_if_results_exist` enforces conditional rewrite when operator produces `docs/phase39-ab-results.md` via `/qor-ab-run`.
- **LOAD_BEARING_PENDING_EVIDENCE registry** (19 skills): documented transitional state awaiting A/B evidence.

**Tests**: 743 pytest green × 2. Admission: `qor-ab-run` admitted. Matrix: 29 skills, 112 handoffs, 0 broken.

**Naming note**: branch `phase/39b-*` + plan `plan-qor-phase39b-*.md` use letter-suffix convention not supported by `governance_helpers._BRANCH_PHASE_RE` + `_PHASE_FILENAME_RE` (digit-only). Version bump performed manually (0.29.0 → 0.30.0). Future sub-phases should use next digit (e.g., phase/41) to remain compatible with automated bump.
