---
name: dopamine-engagement-review
description: Evaluate engagement and reward systems for productivity-focused software with neurodiverse considerations. Use when asked to perform a dopamine engagement review, analyze motivation and reward loops, design professional engagement supports beyond gamification, or produce a heat map of stressors, reinforcers, and energy draw across a user journey.
---

# Dopamine Engagement Review

## Overview

Assess the mental energy cost and reward dynamics across a user journey, then propose professional, productivity-aligned interventions that reduce negative draw and increase sustainable engagement.

## Preconditions

Require a journey map and friction log. If missing, ask for them or recommend running `cx-ux-flow-audit` first.

## Workflow

1. Confirm objectives and guardrails:
   - Prioritize productivity and organizational outcomes over novelty or entertainment.
   - Remove or modify features that detract from focus or work quality.
2. Build an energy model for the journey:
   - Define a simple scale for energy draw or gain (for example `-2` to `+2`).
   - Track uncertainty, effort, autonomy, competence feedback, and predictability.
3. Analyze each step for neurodiverse support:
   - Reduce ambiguity and hidden state.
   - Minimize sensory overload and interruptions.
   - Support executive function with chunking, checkpoints, and clear next actions.
4. Identify stressors, reinforcers, and median experiences:
   - Stressors: cognitive overload, inconsistent feedback, time pressure, error penalties.
   - Reinforcers: clear progress, mastery feedback, autonomy, reliable recovery.
   - Median experiences: neutral steps that can be improved with low risk.
5. Propose interventions with feasibility checks:
   - Tighten feedback loops tied to task completion.
   - Provide meaningful progress indicators and milestone visibility.
   - Offer optional focus modes and predictable timing.
6. Eliminate detractors:
   - If a feature cannot be aligned to productivity, recommend removing it.
7. Define success measures and validation:
   - Engagement quality, completion rates, reduced drop-off, improved task throughput.

## Output Format

Produce a heat map plus an action plan.

### Scales

Use consistent, lightweight scoring:

- Energy Draw or Gain: `-2` (drain) to `+2` (gain)
- Stressor Intensity: `1` (low) to `3` (high)
- Reinforcer Strength: `1` (low) to `3` (high)

### Engagement Heat Map

Use a compact table with columns:

- Stage
- Step
- Energy Draw or Gain
- Stressors
- Reinforcers
- Median Experience (Y/N)
- Notes

### Enhancement Opportunities

List each opportunity with:

- Problem
- Proposed Change
- Expected Impact
- Feasibility
- Risk or Tradeoff

### Professional Safeguards

- Avoid medical diagnosis or therapeutic claims.
- Keep recommendations aligned with productivity and organizational value.

### Sample Output Template

```text
Engagement Heat Map
Stage | Step | Energy Draw or Gain | Stressors | Reinforcers | Median Experience (Y/N) | Notes
----- | ---- | ------------------- | --------- | ---------- | ----------------------- | -----
[ ]   | [ ]  | [ ]                 | [ ]       | [ ]        | [ ]                     | [ ]

Enhancement Opportunities
Problem | Proposed Change | Expected Impact | Feasibility | Risk or Tradeoff
------- | --------------- | --------------- | ----------- | ---------------
[ ]     | [ ]             | [ ]             | [ ]         | [ ]
```

## Scope Boundary

**In scope**
- Engagement, reinforcement, stressor/energy mapping, and neurodiverse motivation support.

**Out of scope**
- Baseline accessibility/UI standards audit (use `web-design-guidelines`).
- End-to-end interaction friction mapping without engagement lens (use `cx-ux-flow-audit`).
