# Qor Skill Delegation Table

**Doctrine**: Skills name skills explicitly. When skill X detects condition Y, the legal next action is invoking skill Z — not reinventing Z's process inline.

This table is the single source of truth for cross-skill handoffs. Every `/qor-*` skill must consult this when emitting "next action" guidance.

## Delegation matrix

| Detector | Condition | Delegate to | Rationale |
|---|---|---|---|
| `qor-audit` | Section 4 Razor violation (functions >40 lines, files >250 lines, nesting >3, ternaries) | `/qor-refactor` | refactor owns file-internal logic shape |
| `qor-audit` | Orphan file detected | `/qor-organize` | organize owns project-level structure |
| `qor-audit` | Macro-level architecture breach (cyclic deps, mixed domains, layering reversal) | `/qor-organize` | structural concerns are organize's domain |
| `qor-audit` | PASS verdict | `/qor-implement` | next phase in chain |
| `qor-audit` | VETO with security L3 | `/qor-debug` (root cause) then `/qor-refactor` or `/qor-implement` | security findings need diagnosis before fix |
| `qor-research` | Research complete | `/qor-plan` | next phase in chain |
| `qor-research` | Project-structure questions surface | `/qor-organize` | restructuring is organize's domain, not plan's |
| `qor-plan` | Plan complete | `/qor-audit` | next phase in chain |
| `qor-plan` | Architectural restructuring needed | `/qor-organize` | organize owns directory topology |
| `qor-implement` | Implementation complete | `/qor-substantiate` | next phase in chain |
| `qor-implement` | Mid-implement Razor bloat detected | `/qor-refactor` | refactor enforces Section 4 |
| `qor-implement` | Regression / hallucination / degradation detected | `/qor-debug` | debug owns root-cause analysis |
| `qor-refactor` | File-internal refactor reveals project-level issue | `/qor-organize` | scope escalation; organize handles project shape |
| `qor-refactor` | Refactor complete | `/qor-audit` (re-audit) or `/qor-substantiate` (if mid-implement) | depends on entry point |
| `qor-substantiate` | Section 4 violation detected post-build | `/qor-refactor` | enforce Razor before sealing |
| `qor-substantiate` | Reality != Promise (missing files, broken tests) | `/qor-debug` (diagnose) then return to `/qor-implement` | diagnose root cause; don't reseal until fixed |
| `qor-substantiate` | PASS verdict | `/qor-validate` (if formal validation phase needed) or `/qor-repo-release` | sealed; ready for downstream |
| `qor-validate` | Repeat failure across cycles (3+ same root cause) | `/qor-remediate` | process-level concern, not code-level |
| `qor-debug` | Root cause is process gap (gate skipped, capability shortfall) | `/qor-remediate` | code is fine; the workflow needs adjustment |
| `qor-debug` | Root cause is code defect | `/qor-implement` (with fix scoped) or `/qor-refactor` | per defect class |
| any phase | Process Shadow Genome threshold (sev sum >= 10) | `/qor-remediate` | auto-triggered by `qor/scripts/check_shadow_threshold.py` |
| any phase | Capability shortfall (codex-plugin, agent-teams missing on host that supports them) | log via `qor_platform.is_available` + `shadow_process.append_event` | non-blocking; logged for trend analysis |

## Anti-patterns this prevents

- **Inline reinvention**: `qor-audit` says "fix the 60-line function" without naming `/qor-refactor`. Reader interprets this as "do it yourself" rather than invoking the dedicated skill.
- **Process invention in implementation**: `qor-implement` notices file is bloating, inlines its own Section 4 enforcement instead of pausing to `/qor-refactor`.
- **Code-level fix for process problem**: regression keeps recurring; team writes more tests when the actual issue is the gate sequence (skipped audit, missing capability). `/qor-remediate` is the right tool.
- **Scope creep within a skill**: `qor-refactor` notices the project is structurally a mess; instead of escalating to `/qor-organize`, it tries to do project-level reshaping inside a file-internal pass.

## Update protocol

When a new skill is added or an existing skill gains a new failure mode, update this table BEFORE wiring the new SKILL.md. Skills must reference this table; the table must not lag the skills.

## Verification

`grep -E "^\| .qor-" qor/gates/delegation-table.md` returns the matrix rows. CI gate (future): every chain skill's SKILL.md must reference at least one row from this table.
