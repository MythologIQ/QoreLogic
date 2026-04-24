# Plan: Phase 43 — intent-lock ancestry verify (unblock substantiate cycles)

**change_class**: hotfix
**target_version**: v0.28.3
**doc_tier**: minimal
**pass**: 2

**Pass 2 delta**: Added explicit scheduling-dependency declaration on PR #14 (Phase 42, v0.28.2) merging first, plus a Preflight section instructing operator to verify pyproject is at 0.28.2 before running `/qor-substantiate`. Addresses audit VETO V1 (plan-text / specification-drift) documented in `.agent/staging/AUDIT_REPORT.md` (Phase 43 Pass 1) and `docs/SHADOW_GENOME.md` Entry #31. Mirrors Phase 41 Pass 3's dependency-declaration pattern.

**Dependency**: target v0.28.3 reachable only after PR #14 (Phase 42, v0.28.2) merges to main and the v0.28.2 tag pushes to origin. Operator must rebase `phase/43-intent-lock-ancestry-verify` on the post-merge main (which advances pyproject to 0.28.2) before running `/qor-substantiate`. Without this rebase, `bump_version('hotfix')` computes 0.28.2 from the current pyproject baseline (0.28.1) and collides with the local v0.28.2 tag from Phase 42's pending seal — downgrade guard aborts.

**Scope**: Single-function fix in `qor/reliability/intent_lock.py`. Replace the strict HEAD-equality check in `verify()` with a `git merge-base --is-ancestor` ancestry check. Captured HEAD must be an ancestor of current HEAD; current HEAD may be any forward descendant. Plan-hash and audit-hash equality checks unchanged.

**Rationale**: Observed twice in the current session (Phase 41 substantiate, Phase 42 substantiate). The protocol is:

1. `/qor-implement` Step 5.5 captures intent-lock (plan_hash, audit_hash, HEAD_at_capture).
2. Implementation proceeds; the implement commit advances HEAD past HEAD_at_capture.
3. `/qor-substantiate` Step 4.6 calls `intent_lock.py verify`; HEAD inequality triggers `DRIFT: head`; substantiate aborts.

Current workaround: re-capture intent-lock between implement commit and substantiate. This works but defeats the lock's anti-drift purpose — re-capture is the first move after any legitimate implement, so the lock's HEAD component has devolved into noise the operator routes around.

The intent-lock's docstring states its purpose as "prevent silent plan drift between audit PASS and final seal." Plan and audit content drift are the real threats; HEAD equality was a secondary safety net whose over-triggering has made it a nuisance. An ancestry check preserves the real safety (catches history rewrites, resets, branch switches) while allowing legitimate forward commits (implement, post-implement amendments).

SG-Phase4x-A candidate: "Secondary safety checks that over-trigger in the happy path get routinely bypassed; route-around becomes SOP and the original anti-drift intent is lost." Countermeasure: relax the check to match actual-threat semantics, not operator-convenience semantics.

## Open Questions

None.

## Preflight note for substantiate

Before running `/qor-substantiate`, verify:

```bash
# 1. PR #14 is merged to main and v0.28.2 tag is on origin.
git ls-remote --tags origin | grep v0.28.2

# 2. Local branch is rebased on post-merge main (pyproject must read 0.28.2).
git checkout phase/43-intent-lock-ancestry-verify
git fetch origin main
git rebase origin/main
grep '^version' pyproject.toml  # must show: version = "0.28.2"
```

If any check fails, hold substantiate. `bump_version('hotfix')` will refuse the bump otherwise (downgrade guard against the existing local v0.28.2 tag).

## Phase 1 — ancestry-based HEAD verification

### Affected Files

- `tests/test_reliability_scripts.py` — NEW test cases (listed below) for the ancestry semantics. Tests written first; confirmed RED before patching.
- `qor/reliability/intent_lock.py` — replace the `_head_commit()` equality check in `verify()` with an ancestry check via `git merge-base --is-ancestor`. Preserve the plan-hash and audit-hash equality checks verbatim.

### Unit Tests

TDD order — new tests added and confirmed RED against the current strict-equality logic, then GREEN after the ancestry patch.

- `test_intent_lock_verify_allows_forward_head_advancement` — capture intent-lock at HEAD_A; create one or more commits (mimicking the implement commit); run `verify`; must exit 0. Current (strict-equality) logic exits 1 with `DRIFT: head`; patched logic exits 0 because capture-HEAD is an ancestor of current HEAD.
- `test_intent_lock_verify_detects_history_rewrite` — capture at HEAD_A; reset hard back to HEAD_A^ (rewriting history so HEAD_A is no longer reachable); create a new divergent commit; run `verify`; must exit 1 with `DRIFT: head` because capture-HEAD is not an ancestor of current HEAD.
- `test_intent_lock_verify_detects_branch_switch_to_divergent` — capture at HEAD_A on branch-1; create a second branch from a common ancestor with divergent history; switch to branch-2; run `verify`; must exit 1 because capture-HEAD is not an ancestor of branch-2's HEAD.
- `test_intent_lock_verify_still_detects_plan_drift_after_forward_head` — capture at HEAD_A; advance HEAD legitimately; mutate the plan file; run `verify`; must exit 1 with `DRIFT: plan` (plan-hash check fires before the ancestry check, so this is a test of correct ordering, not of the ancestry logic).
- `test_intent_lock_verify_still_detects_audit_drift_after_forward_head` — same pattern for audit file.
- `test_intent_lock_verify_ancestry_uses_subprocess_list_argv` — structural test: the `verify()` implementation must call `subprocess.run` with list-form argv (not `shell=True`) for the `merge-base` invocation. Guards against A03 injection drift.

All tests run in a `tmp_path` repo created via `subprocess.run(["git", "init"], ...)` with a deterministic commit chain. No coupling to the enclosing repo's live git state.

### Changes

In `qor/reliability/intent_lock.py`, replace the HEAD equality section of `verify()`:

```python
# Current (strict equality):
current_head = _head_commit(repo)
if current_head != data["head_commit"]:
    print("DRIFT: head", file=sys.stderr)
    return 1
```

with:

```python
# Phase 43: ancestry check instead of equality.
# Allows legitimate forward progress (implement commit advancing HEAD) while
# still catching history rewrites, resets, and branch switches to divergent
# histories. The capture HEAD must remain reachable from current HEAD.
captured_head = data["head_commit"]
result = subprocess.run(
    ["git", "merge-base", "--is-ancestor", captured_head, "HEAD"],
    cwd=str(repo),
    capture_output=True,
    text=True,
    check=False,
)
if result.returncode != 0:
    print("DRIFT: head", file=sys.stderr)
    return 1
```

`git merge-base --is-ancestor A B` exits 0 if A is an ancestor of B (including when A == B), non-zero otherwise. No shell interpolation; list-form argv.

The `_head_commit()` helper is no longer called from `verify()` (still used by `capture()`). Dead-code-free: keep `_head_commit()` since `capture()` still uses it.

## CI Commands

Operator must run locally before substantiate:

- `python -m pytest tests/test_reliability_scripts.py -v`
- `python -m pytest tests/ -v` (full suite — catch any doctrine-test coupling, esp. imports-discipline or skill-admission)

Determinism check: each new test runs twice in a row locally to confirm no flake. Tests use deterministic `subprocess` chains against throwaway `tmp_path` repos; no time/random/network coupling.
