# Plan: Phase 8 — Tier-C Skill Wiring (SKILL.md-only)

**Status**: Active (scope-limited)
**Author**: QorLogic Governor
**Date**: 2026-04-15
**Scope**: Wire all remaining chain skills with Step 0 gate check + capability branches where applicable. SKILL.md edits only — no new Python (existing `gate_chain` library is current-phase-parameterized).
**Base spec**: `docs/plan-qor-migration-final.md` §Phase 8 (skill-wiring portion); `qor/gates/chain.md`

## Open Questions

None. Decisions settled:
- Pattern: each chain skill calls `gate_chain.check_prior_artifact("<phase>")` directly; no per-skill runtime modules
- Capability branches: agent-teams for plan/implement (contract-level only — host fan-out is harness-specific, deferred to actual integration)
- Memory/meta cross-cutting skills do NOT get gate checks (they are invokable anywhere)
- qor-audit already wired in Phase 7

## Affected Files (8 SKILL.md edits)

### Chain skills (Step 0 gate check + optional Step 1.a capability branch)

| Skill | Phase | Reads | Capability branch |
|---|---|---|---|
| `qor/skills/sdlc/qor-research/SKILL.md` | research | (chain start — note only) | — |
| `qor/skills/sdlc/qor-plan/SKILL.md` | plan | research | agent-teams (parallel research/specialist tracks) |
| `qor/skills/sdlc/qor-implement/SKILL.md` | implement | audit (must be PASS) | agent-teams (parallel specialist tracks) |
| `qor/skills/sdlc/qor-refactor/SKILL.md` | implement | audit | — |
| `qor/skills/sdlc/qor-debug/SKILL.md` | debug | (cross-cutting — note only) | — |
| `qor/skills/governance/qor-substantiate/SKILL.md` | substantiate | implement | — |
| `qor/skills/governance/qor-validate/SKILL.md` | validate | substantiate | — |
| `qor/skills/sdlc/qor-remediate/SKILL.md` | remediate | (reads `docs/PROCESS_SHADOW_GENOME.md`, not gate) | — |

### Step 0 template (insert before existing `### Step 1` or earlier)

```markdown
### Step 0: Gate Check (advisory)

Verify prior-phase artifact exists and is well-formed before proceeding.

```python
import sys; sys.path.insert(0, 'qor/scripts')
import gate_chain, session, shadow_process

sid = session.get_or_create()
result = gate_chain.check_prior_artifact("<phase>", session_id=sid)
if not result.found:
    # Prompt user to override; on confirm:
    gate_chain.emit_gate_override(
        current_phase="<phase>",
        prior_phase_name="<prior>",
        reason="user override: <prior>.json not found",
        session_id=sid,
    )
elif not result.valid:
    gate_chain.emit_gate_override(
        current_phase="<phase>",
        prior_phase_name="<prior>",
        reason=f"user override: {result.errors}",
        session_id=sid,
    )
```

Override is permitted (advisory gate) but logged as severity-1 event.
```

### Step 1.a template (for plan + implement; insert after Step 1 identity activation)

```markdown
### Step 1.a — Capability check (agent-teams parallel mode)

```python
import qor_platform as qplat
if qplat.is_available("agent-teams"):
    # Fan out specialist tracks (frontend/backend/infra) in parallel via TeamCreate;
    # synthesize results in this skill.
    mode = "teams"
else:
    # Sequential single-track. If host=claude-code but agent-teams not declared,
    # log capability_shortfall (sev 2) so it counts toward the shadow threshold.
    if qplat.current() and qplat.current()["detected"]["host"] == "claude-code":
        # Use shadow_process.append_event with event_type="capability_shortfall"
        ...
    mode = "sequential"
```

Contract for teams mode (reserved): `TeamCreate(<spec>) -> [{track, deliverable}, ...]`.
Actual harness wiring is future work.
```

### Cross-cutting skills (note only, no gate code)

`qor-research`, `qor-debug`, `qor-remediate` get a Step 0 informational note, not a gate check:

```markdown
### Step 0: Chain position

This skill is a chain-start (research) / cross-cutting (debug, remediate). No prior-phase gate artifact is required. The skill does write its own artifact (`<phase>.json`) for downstream phases.
```

## Constraints

- **No new Python code** — uses existing `gate_chain`, `qor_platform`, `session`, `shadow_process` libraries.
- **No tests added** — `gate_chain.check_prior_artifact` is exercised by `tests/test_gates.py`; capability checks by `tests/test_platform.py`; nothing skill-specific to test in markdown.
- **Audit body unchanged** — Step 0 + 1.a inserted before existing methodology; existing steps preserved verbatim.
- **Dist regenerated** — source edits propagate via `BUILD_REGEN=1 python qor/scripts/compile.py`.

## Success Criteria

- [ ] 8 SKILL.md files updated with Step 0 (5 with gate checks, 3 with chain-position notes)
- [ ] qor-plan + qor-implement also have Step 1.a agent-teams capability branch
- [ ] Dist regenerated; drift check exits 0
- [ ] Existing 108 tests still pass (no new tests added)
- [ ] Ledger chain verify OK (unchanged)
- [ ] Committed + pushed with `BUILD_REGEN=1`

## CI Commands

```bash
python -m pytest tests/ -v
python qor/scripts/check_variant_drift.py
python qor/scripts/ledger_hash.py verify docs/META_LEDGER.md
```
