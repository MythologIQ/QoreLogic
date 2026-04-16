# qor-plan Step Extensions

Extracted prose for Steps 0.5 and 1.a of `qor/skills/sdlc/qor-plan/SKILL.md` (Phase 16 refactor — keeps SKILL.md under Section 4 Razor).

## Step 0.5: Phase branch creation (Phase 13 wiring)

Before authoring a plan, cut a per-phase branch. Dirty tree blocks checkout; operator chooses stash / commit / abandon.

```python
# Phase 13 wiring: dirty-tree check + per-phase branch
import subprocess, sys
sys.path.insert(0, 'qor/scripts')
import governance_helpers as gh

result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
if result.stdout.strip():
    raise gh.InterdictionError(
        "Working tree dirty; operator must choose stash/commit/abandon before plan branch"
    )

phase_num, slug = gh.derive_phase_metadata(plan_path)  # raises on letter-suffix legacy plans
subprocess.run(["git", "checkout", "-b", f"phase/{phase_num:02d}-{slug}"], check=True)
```

Plan header MUST declare `**change_class**: hotfix | feature | breaking` (bold — V-2). Doctrine test `test_plans_declare_change_class` enforces.

## Step 1.a — Capability check (agent-teams parallel mode, Phase 8 wiring)

```python
import qor_platform as qplat
import shadow_process

if qplat.is_available("agent-teams"):
    # Fan out specialist tracks (frontend/backend/infra) in parallel via TeamCreate;
    # synthesize results in this skill.
    mode = "teams"
else:
    state = qplat.current() or {}
    if state.get("detected", {}).get("host") == "claude-code":
        # claude-code host but agent-teams not declared -> log capability_shortfall
        shadow_process.append_event({
            "ts": shadow_process.now_iso(), "skill": "qor-plan", "session_id": sid,
            "event_type": "capability_shortfall", "severity": 2,
            "details": {"capability": "agent-teams"},
            "addressed": False, "issue_url": None, "addressed_ts": None,
            "addressed_reason": None, "source_entry_id": None,
        })
    mode = "sequential"
```

Contract for `teams` mode (reserved for future harness wiring): `TeamCreate(<spec>) -> [{track, deliverable}, ...]`. Skill synthesizes the track outputs into a single artifact.
