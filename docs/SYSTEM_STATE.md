# Qorlogic System State

**Snapshot**: 2026-04-17
**Chain Status**: ACTIVE (88 entries, last seal: cdb77df120... at v0.18.0)
**Phase**: Phase 27 sealed. `CHANGELOG.md` authored (Keep-a-Changelog 1.1.0, v0.3.0-v0.17.0 backfill + Phase 27 entry). `/qor-substantiate` Step 7.6 stamps `## [Unreleased]` -> `## [X.Y.Z] - YYYY-MM-DD` on seal via `qor/scripts/changelog_stamp.py`; Step 9.5 auto-stage includes `CHANGELOG.md`. Format + tag-bijection + stamp + integration lint tests in `tests/test_changelog_*.py`. Doctrine at `qor/references/doctrine-changelog.md`.

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
