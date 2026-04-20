# Plan: Phase 38 — `ci_commands` schema slot (B22)

**change_class**: feature
**target_version**: v0.28.0
**doc_tier**: standard
**pass**: 1

**Scope**: B22 only. Add `ci_commands` as a required field in `plan.schema.json` + template section in `/qor-plan`. Grandfathering rule: phase number < 38.

**Rationale**: `/qor-plan` SKILL.md §Constraints already mandates "note CI commands needed to validate the plan." The constraint is prose-level; schema does not enforce. Phase 36 and 37 plans both carried `## CI Commands` sections but via convention, not contract. Phase 38 closes that gap — consumers reading plan gate artifacts can rely on the field being present.

**terms_introduced**:
- `ci_commands` — required plan-schema field; array of command strings operators run locally to validate the plan before substantiate. Home: `qor/gates/schema/plan.schema.json` + `/qor-plan` template.

**Source**: `docs/BACKLOG.md` B22; user-directed freeze line set at v0.28.0 for upstream consumer lockdown.

## Open Questions

None.

## Non-goals

- No migration of pre-Phase-38 plans (grandfathering via phase-number rule).
- No persona / context-discipline changes (Phase 39 deferred).

## Phase 1 — B22: `ci_commands` schema slot

### Affected Files

- `qor/gates/schema/plan.schema.json` — add `ci_commands: string[]` property with `minItems: 1`, `items.minLength: 1`; add to `required` only when `phase == "plan"` (it already is). Grandfathering handled at test layer via phase-number parse.
- `qor/skills/sdlc/qor-plan/SKILL.md` §Plan Structure — add `## CI Commands` section to the template.
- `tests/test_plan_schema_ci_commands.py` — NEW. Schema + grandfathering tests.

### Changes

`plan.schema.json` addition:
```json
"ci_commands": {
  "type": "array",
  "items": { "type": "string", "minLength": 1 },
  "minItems": 1,
  "description": "Commands the operator runs to validate the plan locally before substantiate. Must match CI for deterministic parity. Required for phase >= 38."
}
```

Add `ci_commands` to the top-level `required` array.

Grandfathering: enforced by `test_pre_phase_38_plans_grandfathered` via regex parsing plan filename. Plans with phase number `< 38` are skipped at validation time in the test; the schema itself remains strict (implementation note: existing plans in `docs/` may not validate; this is acceptable — the test asserts only Phase 38+ compliance).

Plan body template (in `qor-plan/SKILL.md` §Plan Structure) gains a new section after the Phase blocks, before any footer:

```markdown
## CI Commands

- `<command>` — <what it validates>
```

### Unit Tests (TDD — written first)

- `tests/test_plan_schema_ci_commands.py::test_plan_schema_requires_ci_commands_for_phase_38_plus` — NEW. Plan without `ci_commands` fails validation.
- `tests/test_plan_schema_ci_commands.py::test_plan_schema_rejects_empty_ci_commands` — NEW. `ci_commands: []` fails minItems validation.
- `tests/test_plan_schema_ci_commands.py::test_plan_schema_rejects_empty_command_string` — NEW. `ci_commands: [""]` fails minLength validation.
- `tests/test_plan_schema_ci_commands.py::test_plan_schema_accepts_valid_ci_commands` — NEW. Valid array passes.
- `tests/test_plan_schema_ci_commands.py::test_qor_plan_skill_template_has_ci_commands_section` — NEW. Skill prose declares the template section.
- `tests/test_plan_schema_ci_commands.py::test_pre_phase_38_plans_grandfathered` — NEW. Glob `docs/plan-qor-phase[0-9]+-*.md`; phase < 38 skipped; phase >= 38 must validate with `ci_commands`.

## CI Commands

- `pytest tests/test_plan_schema_ci_commands.py` — targeted
- `pytest` — full suite at seal
- `python -m qor.reliability.skill_admission qor-plan` — admission
- `python -m qor.reliability.gate_skill_matrix` — handoff integrity
- `python qor/scripts/doc_integrity_strict.py` — term home
