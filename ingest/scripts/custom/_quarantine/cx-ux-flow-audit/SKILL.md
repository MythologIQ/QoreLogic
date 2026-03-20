---
name: cx-ux-flow-audit
description: Audit customer and user experience flows with multi-perspective journey mapping and friction detection. Use when asked to review UX/CX flows, identify awkward or unnatural experiences, map end-to-end navigation, assess onboarding/task completion/retention flows, or produce a journey map and friction log with remediation guidance.
---

# Cx Ux Flow Audit

## Overview

Create a multi-perspective journey map and a friction log that pinpoints awkward or unnatural experiences, explains why they deter users, and proposes feasible fixes.

## Quick Intake

Ask only what is missing after autonomous discovery. Do not ask the user to define success; propose it.

- Identify product, target personas, and primary outcomes if unclear.
- Clarify entry points, surfaces, and environments (web, desktop, mobile, offline, admin) if not discoverable.
- Request missing artifacts only if needed to validate a claim.
- Confirm constraints only when a fix would otherwise be infeasible.

## Autonomous Discovery (Do Before Questions)

Use local context and available tools to gather evidence first.

1. Scan the repo for entry points and flows (routes, nav, auth, onboarding, dashboards).
2. Read relevant screens, components, and copy; note flow transitions and state changes.
3. Look for analytics or telemetry events that imply critical steps.
4. Check for E2E or UI tests (for example Playwright) to infer canonical flows.
5. Use existing screenshots or run-view tooling if available; otherwise infer from code.
6. Capture citations with file paths and line references as "receipts."

If the repo or artifacts are unavailable, state that constraint explicitly and proceed with a best-effort audit.

## Success Definition (Provide, Do Not Ask)

Define success criteria up front and validate later:

- Time-to-first-value: users complete the first meaningful task quickly.
- Clarity: each step is self-explanatory with visible feedback.
- Low rework: errors are recoverable without restarting.
- Consistency: language, layout, and behavior are predictable.
- Cognitive load: steps are chunked and low-friction.
- Retention support: returning users resume without re-learning.

## Workflow

1. Define the journey stages and critical tasks (onboarding, activation, repeat use, recovery, offboarding).
2. Map steps for at least three perspectives: first-time user, returning user, power user or admin.
3. For each step, capture user intent, system response, and expectations.
4. Rate each step on clarity, effort, time cost, error risk, and emotional tone.
5. Flag awkward or unnatural moments:
   - Surprising transitions or hidden state changes
   - Forced context switches or unnecessary steps
   - Inconsistent language, placement, or feedback
   - Unclear permissions, unclear ownership, or missing affordances
6. Describe deterrents and likely drop-off points with evidence or rationale.
7. Propose fixes with feasibility, scope, and expected impact.
8. Summarize quick wins and deeper structural changes.

## Output Format

Produce both a journey map and a friction log.

### Scales

Use consistent, lightweight scoring:

- Effort: `1` (low) to `5` (high)
- Risk: `1` (low) to `5` (high)
- Emotion: `-2` (negative) to `+2` (positive)
- Expectation Match: `Miss`, `Partial`, `Match`

### Journey Map

Use a compact table with columns:

- Stage
- Step
- User Goal
- System Response
- Expectation Match
- Effort
- Emotion
- Risk
- Notes

### Friction Log

Use a compact table with columns:

- ID
- Step
- Friction / Awkwardness
- Why It Deters
- Affected Personas
- Evidence or Hypothesis
- Recommended Fix
- Priority

### Recommendations

- Quick wins (low effort, high impact)
- Structural fixes (high effort, high impact)
- Open questions and unknowns

### Evidence Appendix (Receipts)

List the key evidence used to justify findings:

- File paths with line references
- Copy strings or UI labels
- Test specs or selectors
- Screenshots or artifacts (if available)

### Sample Output Template

```text
Journey Map
Stage | Step | User Goal | System Response | Expectation Match | Effort | Emotion | Risk | Notes
----- | ---- | --------- | --------------- | ----------------- | ------ | ------- | ---- | -----
[ ]   | [ ]  | [ ]       | [ ]             | [ ]               | [ ]    | [ ]     | [ ]  | [ ]

Friction Log
ID | Step | Friction / Awkwardness | Why It Deters | Affected Personas | Evidence or Hypothesis | Recommended Fix | Priority
-- | ---- | ---------------------- | ------------ | ----------------- | ---------------------- | -------------- | --------
[ ]| [ ]  | [ ]                    | [ ]          | [ ]               | [ ]                    | [ ]            | [ ]

Recommendations
Quick wins: [ ]
Structural fixes: [ ]
Open questions: [ ]
```

## Handoff to Dopamine Engagement Review

End the audit by asking:

"Do you want to perform a Dopamine Engagement Review to evaluate neurodiverse productivity supports and reward systems?"

If yes, pass these artifacts into the next skill:

- Journey map
- Friction log
- Target personas and constraints
- Success metrics

## Scope Boundary

**In scope**
- End-to-end journey mapping, friction analysis, and flow remediation.

**Out of scope**
- Pure accessibility/design-standards compliance checklists (use `web-design-guidelines`).
- Motivation/reward-loop analysis as primary lens (use `dopamine-engagement-review`).
